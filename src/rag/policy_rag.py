import os
from langchain.tools import Tool
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

def create_policy_retriever_tool_from_file(file_name: str, openai_api_key: str, index_path: str = "policy_faiss_index") -> Tool:
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir_path, file_name)
    index_dir = os.path.join(dir_path, index_path)

    print(f"📁 Vector index path: {index_dir}")

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Check if FAISS index already exists
    if os.path.exists(os.path.join(index_dir, "index.faiss")):
        print("✅ Loading FAISS index from local disk...")
        vectorstore = FAISS.load_local(index_dir, embeddings,allow_dangerous_deserialization=True)
    else:
        print("🛠️  Building FAISS index from documents...")

        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(docs)

        vectorstore = FAISS.from_documents(split_docs, embeddings)
        
        os.makedirs(index_dir, exist_ok=True)  # Ensure directory exists
        vectorstore.save_local(index_dir)
        print("💾 FAISS index saved.")

    return Tool(
        name="policy_retriever",
        func=lambda q: "\n".join([doc.page_content for doc in vectorstore.similarity_search(q, k=3)]),
        description="Useful for answering questions about bank policy and general banking information."
    )
