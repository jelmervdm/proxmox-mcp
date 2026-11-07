#!/bin/bash
set -e

if [ "$ENABLE_CONTEXTFORGE_GATEWAY" = "true" ]; then
    PORT="${GATEWAY_PORT:-8000}"
    echo "Starting ContextForge Gateway (Port $PORT)..." >&2
    # Ensure ContextForge Gateway has valid secrets and passwords to satisfy security validator
    if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "__REPLACE_ME__" ]; then
        export JWT_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
    fi
    if [ -z "$AUTH_ENCRYPTION_SECRET" ] || [ "$AUTH_ENCRYPTION_SECRET" = "__REPLACE_ME__" ]; then
        export AUTH_ENCRYPTION_SECRET="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
    fi
    if [ -z "$PLATFORM_ADMIN_PASSWORD" ] || [ "$PLATFORM_ADMIN_PASSWORD" = "__REPLACE_ME__" ]; then
        export PLATFORM_ADMIN_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
    fi
    if [ -z "$DEFAULT_USER_PASSWORD" ] || [ "$DEFAULT_USER_PASSWORD" = "__REPLACE_ME__" ]; then
        export DEFAULT_USER_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
    fi
    if [ -z "$BASIC_AUTH_PASSWORD" ] || [ "$BASIC_AUTH_PASSWORD" = "__REPLACE_ME__" ]; then
        export BASIC_AUTH_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
    fi
    exec python3 -m mcpgateway.translate --stdio "proxmox-mcp-server" --expose-sse --port "$PORT" --host 0.0.0.0
else
    echo "Starting standard Proxmox MCP server..." >&2
    exec proxmox-mcp-server "$@"
fi

