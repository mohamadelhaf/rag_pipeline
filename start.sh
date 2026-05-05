#!/bin/bash
set -e

echo "Starting EnergyCo AI"

echo "Loading Ollama models..."
docker exec energyco-ollama ollama pull mistral
docker exec energyco-ollama ollama pull nomic-embed-text

echo "Ingesting documents..."
docker exec energyco-ingest python ingest.py --reset

echo "AI ready"
