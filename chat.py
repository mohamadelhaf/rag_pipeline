from dotenv import load_dotenv
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, chain
import os

load_dotenv()

store = {}

def get_session_history(session_id :str) -> BaseChatMessageHistory:
    if session_id  not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def load_chat_chain():
    embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), base_url = os.getenv("BASE_URL"))

    vectorstore = Chroma(persist_directory=os.getenv("CHROMA_DB_PATH"), embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k":3})
    llm = OllamaLLM(model=os.getenv("LLM_MODEL"), base_url=os.getenv("OLLAMA_BASE_URL"))
    prompt=ChatPromptTemplate.from_messages([("system", """You are an internal HR assistant for energyCo. Answer using ONLY the context provided below. If the answer is not in the context, say ' I don't have this information. '
                                              context:
                                              {context}"""),
                                              MessagesPlaceholder(variable_name="history"),
                                              ("human", "{question}")])
    chain = ({"context" :(lambda x: x["question"]) | retriever | format_docs, "question" : lambda x: x["question"], "history" : lambda x: x.get("history", [])} | prompt |llm | StrOutputParser())

    chain_with_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="question", history_messages_key="history")
    return chain_with_history
def main():
    print("EnergyCo HR Assistant Chat")
    print("Type your question or  'exit' or 'quit' or 'q' to quit")
    print("loading assistant...")
    chain = load_chat_chain()
    session_id= 'user_1'
    print("Assistant loaded. You can start asking questions.")
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("Exiting chat. Goodbye!")
            break

        print("Assistant ", end="", flush=True)
        answer = chain.invoke({"question": question}, config={"configurable": {"session_id": session_id}})
        print(f"{answer}")
        print()

if __name__ == "__main__":
    main()
             
