from dotenv import load_dotenv
import os
import sys
import glob
import shutil
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

load_dotenv()

AGENT_CONFIGS = {
    "HR" : {"chunk_size" :500 , "chunk_overlap":50},
    "Tech" : {"chunk_size" : 1000, "chunk_overlap":100},
    "compliance" : {"chunk_size" : 750, "chunk_overlap":75},
    "pm" : {"chunk_size" : 600, "chunk_overlap":60},
    "general": {"chunk_size" : 500, "chunk_overlap":50}
}

DEFAUILT_CHUNK_CONFIG = {"chunk_size" : 500, "chunk_overlap":50}

def get_agent_from_path(file_path):
    parts = file_path.replace("\\", "/").split("/")
    try:
        doc_index  = parts.index("documents")
        agent = parts[doc_index + 1]
        return agent
    except (ValueError, IndexError):
        return "general"
    

def load_and_chunk_file(file_path):
    filename = os.path.basename(file_path)
    agent = get_agent_from_path(file_path)
    config = AGENT_CONFIGS.get(agent, DEFAUILT_CHUNK_CONFIG)

    if filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif filename.endswith(".txt"):
        loader = TextLoader(file_path)
    else:
        print(f"Unsupported file type for {file_path}. Skipping.")
        return []
    
    documents = loader.load()

    for doc in documents:
        doc.metadata["agent"] = agent
        doc.metadata["filename"] = filename

    splitter = RecursiveCharacterTextSplitter(chunk_size=config["chunk_size"], chunk_overlap=config["chunk_overlap"])
    chunks = splitter.split_documents(documents)

    print(f"{filename} {len(chunks)} chunks  (agent: {agent}, chunk_size: {config['chunk_size']} with {config['chunk_overlap']}  overlap)")  

    return chunks



def ingest_docs(reset=False):

    chroma_path = os.getenv("CHROMA_DB_PATH")

    if reset and os.path.exists(chroma_path):
        print(f'Resetting ChromaFB at {chroma_path}')
        shutil.rmtree(chroma_path)
        print("Cleared existing ChromaDB")

    print("Loading documents")
    all_chunks = []

    all_files = (glob.glob("./data/documents/**/*.pdf", recursive=True) + glob.glob("./data/documents/**/*.txt", recursive=True))

    for file_path in all_files:
        print(f"Processing {file_path}")
        chunks = load_and_chunk_file(file_path)
        all_chunks.extend(chunks)

    print(f"Loaded and chunked {len(all_chunks)}")


    print("creating embeddings and storing in ChromaDB")
    embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), base_url=os.getenv("ollama_base_url"))
    vectorstore = Chroma.from_documents(documents=all_chunks, embedding=embeddings, persist_directory=chroma_path)
    print(f"stored {len(all_chunks)} chunks in ChromaDB")
    print("Ingestion complete")


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    ingest_docs(reset=reset)