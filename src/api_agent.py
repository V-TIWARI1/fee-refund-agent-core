#uvicorn api_agent:app --reload
from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.schema import HumanMessage, AIMessage
import config.config as config
from tools.getCustomerContext import get_customer_context
from tools.getCustomerAccounts import get_customer_accounts
from tools.getTransactions import get_fee_charged_transactions
from tools.submitRefund import submit_refund
from rag.policy_rag import create_policy_retriever_tool_from_file
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Add this section to allow requests from React (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 👈 allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM setup
OPENAI_API_KEY = config.OPENAI_API_KEY
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    verbose=True
)

customer_data = get_customer_context()
policy_tool = create_policy_retriever_tool_from_file("policy.txt", OPENAI_API_KEY)

fee_refund_flow="""
For general inquiry related to fee charged. Agent can decide which function to call, agent can do all Inquiry related call to answer user question,but for fee refund follow below instruction
Fee Refund flow: whenever user ask for fee-refun/refund below is the standard flow.

1. Call get_customer_accounts with the customer ID to retrieve account details.
2. once you receiveed the list of account number,You must respond with the list of accounts, and ask the user to enter an account number.
3. once user have entered an account number, call get_fee_charged_transactions.
4. Show the list of fee transactions and ask the user for transaction IDs they want refund,if refund status is false it means it is eligible for fee refund and if its value is true it means it is already refunded.
5. once user has provided transaction ids, Call submit_refund for selected transaction IDs only to process the refund.
6. Display the refund status while display the status show total amount requested and total amount refunded.

Note-submit_refund can be called only for transaction Id user has provided. agent should not do fee refund with out user specifying transaction
"""

system_message = """
You are a bank fee refund assistant.
You should decide which function to call based on user input. If the user asks about something unrelated to refunds, answer accordingly.
You must remember the conversation context and decide which function to call based on the conversation history.
"""

# Session memory store
session_memory = {}

# Request schema
class ChatRequest(BaseModel):
    session_id: str
    user_input: str


def get_agent_and_memory(session_id: str):
    # If session does not exist, create new memory and agent
    if session_id not in session_memory:
        memory = ConversationBufferMemory(return_messages=True)
        agent_chain = initialize_agent(
            tools=[get_customer_accounts, get_fee_charged_transactions, submit_refund, policy_tool],
            llm=llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            system_message=system_message
        )

        # Generate and store welcome message
        welcome_prompt = (
            "Generate a short, friendly, and professional welcome message for the customer. "
            "Use their name, customer ID, and account opening date. Customer Id is mandatory. "
            "Ensure it's polite and ends with 'How can I assist you today?'\n\n"
            f"Customer Data: {json.dumps(customer_data)}"
        )
        welcome_response = agent_chain.invoke({"input": welcome_prompt})
        welcome_message = welcome_response["output"]
        memory.chat_memory.messages.append(AIMessage(content=welcome_message))

        session_memory[session_id] = {
            "agent": agent_chain,
            "memory": memory,
            "welcome_message": welcome_message
        }

    return session_memory[session_id]


@app.post("/chat")
async def chat_endpoint(chat: ChatRequest):
    session = get_agent_and_memory(chat.session_id)
    memory = session["memory"]
    agent_chain = session["agent"]

    # Format with conversation history
    past_messages = "\n".join(
        [f"User: {msg.content}" if isinstance(msg, HumanMessage) else f"Assistant: {msg.content}"
         for msg in memory.chat_memory.messages]
    )

    formatted_input = f"fee-refun-flow:{fee_refund_flow}\nPrevious conversation:\n{past_messages}\n\nUser: {chat.user_input}"

    response = agent_chain.invoke({"input": formatted_input})
    assistant_reply = response["output"]

    memory.chat_memory.messages.append(HumanMessage(content=chat.user_input))
    memory.chat_memory.messages.append(AIMessage(content=assistant_reply))

    return {"response": assistant_reply}


@app.get("/welcome/{session_id}")
async def get_welcome(session_id: str):
    session = get_agent_and_memory(session_id)
    return {"welcome_message": session["welcome_message"]}
