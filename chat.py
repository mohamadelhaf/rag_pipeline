from dotenv import load_dotenv
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
import os
from logger import log_interaction
import time
import subprocess
import chromadb



load_dotenv()

store = {}

AGENTS = ["hr", "tech", "compliance", "pm", "general"]


def ensure_ingested():
    chroma_path = os.getenv("CHROMA_DB_PATH")
    try:
        client = chromadb.PersistentClient(path=chroma_path)
        collections = client.list_collections()
        if not collections:
            print("No collections found in ChromaDB. Running ingestions ")
            subprocess.run(["python", "ingest.py"], check=True)
    except Exception:
        print("ChromaDB not ready. Running ingestions.")
        subprocess.run(["python", "ingest.py"], check=True)

def get_session_history(session_id :str) -> BaseChatMessageHistory:
    if session_id  not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def detect_agent(question: str, llm) -> str:
    prompt = PromptTemplate.from_template(
    "Classify this question into exactly one of these categories: " +
        f"{', '.join(AGENTS)}.\n\n" +
        "Rules:\n"
        "- hr: leave days, vacation, sick leave, onboarding, remote work, performance, CV, salary\n"
        "- tech: servers, code, systems, architecture, Linux, restart, deployment\n"
        "- compliance: GDPR, security, legal, regulations, data privacy\n"
        "- pm: projects, tasks, deadlines, meetings, planning\n"
        "- general: anything else\n\n"
        "Reply with ONLY one word from the list above. No explanation.\n\n"
        "Question: {question}\n"
        "Category:")

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": question}).strip().lower()

    if result not in AGENTS:
        return "general"
    return result             

def extract_question(x):
    if isinstance(x, dict):
        return x.get("question", "")
    return str(x)

def load_chat_chain(vectorstore, llm, agent_filter):
    retriever = vectorstore.as_retriever(search_kwargs={"k":3, "filter":{"agent" : agent_filter}})

    
    prompt=ChatPromptTemplate.from_messages([("system", """You are an internal  assistant for energyCo. Answer using ONLY the context provided below. If the answer is not in the context, say ' I don't have this information. '
                                              context:
                                              {context}"""),
                                              MessagesPlaceholder(variable_name="history"),
                                              ("human", "{question}")])
    chain = ({ "context": RunnableLambda(extract_question) | retriever | format_docs, "question": RunnableLambda(extract_question), "history": lambda x: x.get("history", []) if isinstance(x, dict) else []} | prompt |llm | StrOutputParser())

    chain_with_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="question", history_messages_key="history")
    return chain_with_history


def main():
    print("EnergyCo AI Assistant")
    print("Type your question or  'exit' or 'quit' or 'q' to quit")
    print("loading assistant...")
    ensure_ingested()
    embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), base_url = os.getenv("OLLAMA_BASE_URL"))
    vectorstore = Chroma(persist_directory=os.getenv("CHROMA_DB_PATH"), embedding_function=embeddings)
    llm = OllamaLLM(model=os.getenv("LLM_MODEL"), base_url=os.getenv("OLLAMA_BASE_URL"))
    session_id= 'user_1'
    print("Assistant loaded. You can start asking questions.")
    while True:
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() in ["exit", "quit", "q"]:
            print("Exiting chat. Goodbye!")
            break

        agent = detect_agent(question, llm)
        print(f"Routing to {agent} agent...")

        chain = load_chat_chain(vectorstore, llm, agent)

        chunks = vectorstore.similarity_search(question, k=3, filter={"agent":agent})
        start =time.time()


        print("Assistant ", end="", flush=True)
        answer = chain.invoke({"question": question}, config={"configurable": {"session_id": session_id}})
        duration_ms = int((time.time() - start) * 1000)
        print(f"{answer}")
        print()
        log_interaction(question, agent, chunks, answer, duration_ms)

if __name__ == "__main__":
    main()
             
