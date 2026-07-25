#!/bin/bash
set -e

if [ "$ENABLE_CONTEXTFORGE_GATEWAY" = "true" ]; then
    PORT="${GATEWAY_PORT:-8000}"
    echo "Starting ContextForge Gateway (Port $PORT)..."
    exec python3 -m mcpgateway.translate --stdio "proxmox-mcp-server" --expose-sse --port "$PORT" --host 0.0.0.0
else
    echo "Starting standard Proxmox MCP server..."
    exec proxmox-mcp-server "$@"
fi
