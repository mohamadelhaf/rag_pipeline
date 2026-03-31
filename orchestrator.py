import os
from dotenv import load_dotenv
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.ollama.ollama_prompt_execution_settings import OllamaPromptExecutionSettings

load_dotenv()

async def create_kernel():
    kernel = Kernel()
    kernel.add_service(OllamaChatCompletion(service_id="mistral", ai_model_id=os.getenv("LLM_MODEL"), host=os.getenv("OLLAMA_BASE_URL")))
    return kernel


async def main():
    print("EnergyCo Orchestrator")
    print("\nType your question or  'exit' or 'quit' or 'q' to quit")

    print("Loading Orchestrator...")
    kernel = await create_kernel()

    async with (MCPStdioPlugin(name="hr", description="HR tools for employee info and leave balance", command="Python", args = ["mcp_servers/hr_server.py"]) as hr_plugin, MCPStdioPlugin(name="documents", description="Search company documents", command="Python", args=["mcp_servers/documents_server.py"] )as docs_plugin):
        kernel.add_plugin(hr_plugin)
        kernel.add_plugin(docs_plugin)

        settings = OllamaPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())

        history= ChatHistory()
        history.add_system_message("""You are an intelligent assistant for energyCo. You have access to the tools to search documents and get employee information. Always use the available tools to find accurate information before answering. If you don't have enough information, say so clearly """)

        print("\nready! Ask your question:")

        while True:
            question = input("\nYou:").strip()
            
            if not question:
                continue

            if question.lower() in ["exit", "quit", "q"]:
                print("Thank you Come Again!")
                break

            history.add_user_message(question)

            chat_service = kernel.get_service("mistral")
            response = await chat_service.get_chat_message_content(chat_history=history, settings=settings,kernel=kernel)

            print(f"\nOrchestrator: {response}\n")
            history.add_message(response)

if __name__ == "__main__":
    asyncio.run(main())
        