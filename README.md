# EDF-Mirror

Enterprise AI agent platform for a fictional energy company . Built to practice the full stack of an AI agent mission: RAG, MCP, orchestration, Copilot Studio, Power Automate, and LangChain.

## What this project does

the company has 5 departments (HR, Tech, Compliance, PM, General), each with its own documents and its own specialized agent. A user asks a question, the system figures out which agent should handle it, retrieves the relevant documents, and generates an answer.

The whole thing works end-to-end: you can ask questions through the CLI, through the API, or through a Copilot Studio agent connected via Power Automate.

## How it works

- User sends a question (CLI, API, or Copilot Studio)
- The system classifies the question and routes it to the right agent
- The agent searches its own documents in ChromaDB
- Mistral generates an answer based only on the retrieved context
- The interaction is logged for observability

For the Copilot Studio path, the flow is: Copilot Studio collects the question → Power Automate sends an HTTP POST to the FastAPI backend → backend runs the RAG pipeline → answer goes back through Power Automate → Copilot Studio displays it.

## Stack

- Python 3.12
- LangChain (LCEL) for the RAG pipeline
- ChromaDB for vector storage
- Ollama with Mistral (LLM) and nomic-embed-text (embeddings)
- FastMCP for MCP servers
- Semantic Kernel for the orchestrator
- FastAPI for the REST endpoint
- Docker + Docker Compose
- Microsoft Copilot Studio + Power Automate


## Setup

You need Python 3.12+, Ollama installed, and the models pulled:

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

Then:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=mistral
CHROMA_DB_PATH=./chroma_db
```

Generate the documents and ingest them:

```bash
python create_docs.py
python ingest.py --reset
```

Run the chat:

```bash
python chat.py
```

Or run the API:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

To expose the API for Copilot Studio, use ngrok:

```bash
ngrok http 8000
```

## What each file does

**ingest.py** — Loads documents from `data/documents/`, splits them into chunks (configurable per agent), adds metadata (agent name, filename), and stores embeddings in ChromaDB. The folder name determines which agent owns the document.

**chat.py** — Interactive chat loop. Classifies the question using the LLM, routes to the right agent, retrieves filtered chunks from ChromaDB, generates an answer with conversation memory, and logs everything.

**api.py** — FastAPI server with a `/ask` endpoint. Accepts a question and an optional agent parameter. If agent is "auto", it detects the right agent using the same classification logic as chat.py.

**rag.py** — Minimal RAG pipeline for quick testing. No memory, no routing, just query and answer.

**orchestrator.py** — Semantic Kernel based orchestrator that loads MCP plugins (HR and Documents) and lets the LLM decide which tools to call. Works best with models that support function calling (GPT-4o). Mistral understands the concept but doesn't reliably execute the tool calls.

**logger.py** — Writes each interaction to `logs/interactions.jsonl` with timestamp, question, agent, retrieved chunks, answer, and response time in ms.

**create_docs.py** — Generates fake policy documents for all 5 agents so you can test without real data.

**test_mcp.py** — Runs the HR and Documents MCP servers and calls their tools to verify they work.

## MCP servers

**hr_server.py** — Exposes tools for employee data: `get_employee_info(name)`, `check_leave_balance(name)`, `list_employees()`. Uses fake employee data.

**documents_server.py** — Exposes `search_documents(query, agent)` which runs a similarity search in ChromaDB filtered by agent. Also has `list_available_agents()`.

**calender_server.py** — Designed for Microsoft Graph API integration. Has tools for `get_events()`, `get_upcoming_events()`, and `create_event()`. Requires Azure AD app registration and M365 credentials.

## Copilot Studio + Power Automate

The Copilot Studio agent has two flows connected:

1. **Leave Request Flow** — A topic collects employee name, start date, end date, and reason through a conversation. It calls a Power Automate flow that sends an approval email via Outlook and responds with a confirmation message.

2. **RAG Query Flow** — A topic collects a question, calls a Power Automate flow that sends an HTTP POST to the FastAPI backend (via ngrok), and displays the AI-generated answer back to the user. The agent routing is dynamic — the API auto-detects which agent should handle the question.

## Chunking config

Each agent has its own chunk size and overlap to match the document type:

- HR: 500 / 50
- Tech: 1000 / 100
- Compliance: 750 / 75
- PM: 600 / 60
- General: 500 / 50

## Known limitations

- Mistral doesn't reliably execute Semantic Kernel function calls. The orchestrator architecture is correct but needs Azure OpenAI (GPT-4o) to work properly.
- The calendar server requires Azure AD credentials and a real M365 account.
- ngrok URLs change every time you restart (free tier). In production you'd deploy to Azure App Service or AKS.
- Agent classification with Mistral isn't always accurate. Works better with GPT-4o.

## What I'd change for production

- Swap Mistral for Azure OpenAI GPT-4o
- Replace ChromaDB with Azure AI Search
- Deploy the API to Azure App Service instead of ngrok
- Connect to real Active Directory for employee data
- Use Microsoft Graph API for real calendar/email integration
- Replace JSONL logging with Azure Monitor / Application Insights
- Add content filtering and guardrails

## Author

Mohamad Elhaf — Data & AI Engineer
