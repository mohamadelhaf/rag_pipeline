from dotenv import load_dotenv
import os
import sys
import glob
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def load_documents(directory):
    all_docs =[]

    for txt_file in glob.glob(f'{directory}/**/*.txt', recursive=True):
        loader = TextLoader(txt_file)
        all_docs.extend(loader.load())

    for pdf_file in glob.glob(f'{directory}/**/*.pdf', recursive=True):
        loader = PyPDFLoader(pdf_file)
        all_docs.extend(loader.load())

    return all_docs


def ingest_docs(reset=False):

    chroma_path = os.getenv("CHROMA_DB_PATH")

    if reset and os.path.exists(chroma_path):
        print(f'Resetting ChromaFB at {chroma_path}')
        shutil.rmtree(chroma_path)
        print("Cleared existing ChromaDB")

    print("Loading documents")
    documents = load_documents("data/documents")
    print(f"Loaded {len(documents)} documents")


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
    reset = "--reset" in sys.argv
    ingest_docs(reset=reset)