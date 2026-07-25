FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY entrypoint.sh .

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir '.[router]' mcp-contextforge-gateway --ignore-requires-python && \
    chmod +x entrypoint.sh && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
