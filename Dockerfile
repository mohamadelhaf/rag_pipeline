FROM python:3.12-slim

WORKDIR /app

# Install dependencies first — cached layer, only invalidated when requirements change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create non-root user and own runtime directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p logs chroma_db && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default entrypoint is the REST API; override in docker-compose for other services
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
