from dotenv import load_dotenv
import os 
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, chain
from langchain_core.prompts import PromptTemplate

load_dotenv()

def load_rag_chain():
    embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), base_url = os.getenv("BASE_URL"))
    vectorstore = Chroma(persist_directory=os.getenv("CHROMA_DB_PATH"),embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs = {"k": 3})
    llm = OllamaLLM(model=os.getenv("LLM_MODEL"), base_url=os.getenv("OLLAMA_BASE_URL"))
    prompt = PromptTemplate.from_template("""
    You are an internal HR assistant for energyCo.
Answer the question using ONLY the context provided below.
If the answer is not in the context, say " I don't Have this information."

Context:
{context}

Question:
{question}

Answer:
""")
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])
    
    chain = ({"context": retriever | format_docs, "question" : RunnablePassthrough()} | prompt | llm   | StrOutputParser())
    
    return chain


if __name__ == "__main__":
    chain = load_rag_chain()
    question = "How many days of paid leave do employees get?"
    print(f"Question: {question}")
    print(f"Answer: {chain.invoke(question)}")
    