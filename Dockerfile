# ---------------------------------------------------------
# Stage 1: Dependency builder
# ---------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir \
        --prefix=/install \
        -r requirements.txt


# ---------------------------------------------------------
# Stage 2: Clean runtime image
# ---------------------------------------------------------
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only installed Python dependencies from builder.
COPY --from=builder /install /usr/local

# Runtime does not need setuptools/pip build tooling.
# Remove them to reduce attack surface and eliminate
# vulnerable vendored package metadata.
RUN python -m pip uninstall -y setuptools pip

# Copy application source code and MCP server definitions.
COPY src ./src
COPY mcp-servers ./mcp-servers

EXPOSE 8000

# Start the Enterprise Agentic DevOps REST API.
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]