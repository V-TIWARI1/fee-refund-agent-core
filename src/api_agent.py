#uvicorn api_agent:app --reload --port 8081
#http://localhost:8081/welcome/1
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

fee_refund_flow = """
For general inquiries related to fees charged, the agent can autonomously decide which functions to call. The agent may use any inquiry-related functions to answer the user's questions. However, for fee refund requests, the following standard flow must be followed:

**Fee Refund Flow:**

1. Call `get_customer_accounts` with the customer ID to retrieve the list of customer accounts.
2. Once the list of account numbers is received, respond with the list and ask the user to select an account by entering the account number.
3. When the user provides an account number, call `get_fee_charged_transactions` for that account.
4. Display the list of fee-charged transactions. Ask the user to select the transaction IDs they want refunded.  
   - If `refund_status` is `false`, the transaction is eligible for a refund.  
   - If `refund_status` is `true`, the transaction has already been refunded.
5. Once the user selects transaction IDs, ask them to select a refund reason **for each transaction**.  
   - Valid refund reasons: `standard`, `hardship`, `disaster`
6. After the user provides the transaction IDs and reasons, call `submit_refund` with dict with list of transaction-id and reson of refund **only for the selected transaction IDs** to process the refund.
7. Display the refund status, including the **total amount requested** and the **total amount refunded**.

**Important Notes:**
- The `submit_refund` function must only be called for transaction IDs explicitly provided by the user.
- The agent must not initiate a refund without the user's input.
- If necessary to answer a user's query, the agent may call `get_fee_charged_transactions` for all accounts one by one.
"""

system_message = """
You are a bank fee refund assistant only can perfrom request related to fee refund only or genral inquiry.
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
