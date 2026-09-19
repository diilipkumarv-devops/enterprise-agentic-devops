# Enterprise Agentic DevOps API
# Python 3.11 slim runtime keeps the image smaller than the full Python image.
FROM python:3.11-slim

# Prevent Python from writing .pyc files and ensure logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Application directory inside the container.
WORKDIR /app

# Install Python dependencies first.
# Keeping this before application code improves Docker layer caching.
COPY requirements.txt .

RUN python -m pip install --no-cache-dir \
    --upgrade pip && \
    python -m pip install --no-cache-dir \
    -r requirements.txt

# Copy application source code and MCP server definitions.
COPY src ./src
COPY mcp-servers ./mcp-servers

# FastAPI/Uvicorn listens on port 8000.
EXPOSE 8000

# Start the Enterprise Agentic DevOps REST API.
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]