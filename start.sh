#!/bin/bash

echo "Starting EnergyCo AI"

echo "Loading Ollama models"

docker exec energyco-ollama ollama pull mistral
docker exec energyco-ollama ollama pull nomic-embed-text

echo "Ingesting docs"
docker exec energyco-app python ingest.py --reset

echo "AI ready"
