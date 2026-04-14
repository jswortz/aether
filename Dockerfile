# Dockerfile for Aether Voice Swarm Gateway
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn websockets google-genai pydantic

# Copy the server code
COPY scripts/fastapi_voice_gateway.py /app/main.py

# Expose Cloud Run default port
EXPOSE 8080

# Start ASGI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
