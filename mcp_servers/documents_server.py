from fastmcp import FastMCP
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os

load_dotenv()

mcp = FastMCP('documents_server')

embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), base_url=os.getenv("OLLAMA_BASE_URL"))
vectorstore = Chroma(persist_directory=os.getenv("CHROMA_DB_PATH"), embedding_function=embeddings)

@mcp.tool()
def search_documents(query: str, agent:str = "general") -> str:
    results = vectorstore.similarity_search(query, k=3, filter={"agent":agent})

    if not results:
        return "No relevant documents found."
    
    formatted = []

    for i, doc in enumerate(results):
        source = doc.metadata.get("filename", "unknown")
        formatted.append(f"[source] : {source}\n{doc.page_content[:500]}")

    return "\n\n---\n\n".join(formatted)

@mcp.tool()
def list_available_agents() -> str:
    return ['hr','tech','compliance','pm','general']

if __name__ == "__main__":
    mcp.run()



