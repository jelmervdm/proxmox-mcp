#!/bin/bash
set -e

if [ "$ENABLE_CONTEXTFORGE_GATEWAY" = "true" ]; then
    PORT="${GATEWAY_PORT:-8000}"
    echo "Starting ContextForge Gateway (Port $PORT)..." >&2
    # Ensure ContextForge Gateway has a valid JWT secret key to satisfy security validator
    if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "__REPLACE_ME__" ]; then
        export JWT_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
    fi
    exec python3 -m mcpgateway.translate --stdio "proxmox-mcp-server" --expose-sse --port "$PORT" --host 0.0.0.0
else
    echo "Starting standard Proxmox MCP server..." >&2
    exec proxmox-mcp-server "$@"
fi

