from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os
from chat import detect_agent

load_dotenv()

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str
    agent: str = "general"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask_question(req: QuestionRequest):
    embeddings = OllamaEmbeddings(
        model=os.getenv("EMBEDDING_MODEL"),
        base_url=os.getenv("OLLAMA_BASE_URL")
    )
    vectorstore = Chroma(
        persist_directory=os.getenv("CHROMA_DB_PATH"),
        embedding_function=embeddings
    )
    llm = OllamaLLM(
        model=os.getenv("LLM_MODEL"),
        base_url=os.getenv("OLLAMA_BASE_URL")
    )
    agent = req.agent
    if agent == "auto" or agent == "general":
        agent = detect_agent(req.question, llm)

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3, "filter": {"agent": agent}})

    prompt = PromptTemplate.from_template("""You are an internal assistant for EnergyCo.
Answer using ONLY the context provided below.
If the answer is not in the context, say 'I don't have this information.'

Context:
{context}

Question:
{question}

Answer:""")

    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
    )

    answer = chain.invoke(req.question)
    return {"answer": answer, "agent": req.agent}