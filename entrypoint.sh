#!/bin/bash
set -e

if [ "$ENABLE_CONTEXTFORGE_GATEWAY" = "true" ]; then
    echo "Starting ContextForge Gateway (Port 8000)..."
    exec python3 -m mcpgateway.translate --stdio "proxmox-mcp-server" --expose-sse --port 8000 --host 0.0.0.0
else
    echo "Starting standard Proxmox MCP server..."
    exec proxmox-mcp-server "$@"
fi
