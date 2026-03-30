from dotenv import load_dotenv
from rag import load_rag_chain

load_dotenv()

def main():
    print("\n EnergyCo HR assistant")
    print("\n Type your question or 'exit' to quit")
    print("\n Loading RAG Chain...")
    chain = load_rag_chain()


    while True:
        question = input("You: ").strip()
        if not question:
            continue

        if question.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        print("Assistant: ", end="", flush=True)
        answer = chain.invoke(question)
        print(answer)
        print()
    
if __name__ == "__main__":
    main()