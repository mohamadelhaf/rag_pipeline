from dotenv import load_dotenv
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def ingest_docs():
    print("loading documents")
    loader = DirectoryLoader("data/documents", glob="**/*.txt", show_progress=True, loader_cls=TextLoader)
    documents = loader.load()
    print(f"loaded {len(documents)} documents")

    print("splitting documents into chunks")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"created {len(chunks)} chunks")


    print("creating embeddings and storing in ChromaDB")
    embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), base_url=os.getenv("ollama_base_url"))
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=os.getenv("CHROMA_DB_PATH"))
    print(f"stored {len(chunks)} chunks in ChromaDB")
    print("Ingestion complete")


if __name__ == "__main__":
    ingest_docs()