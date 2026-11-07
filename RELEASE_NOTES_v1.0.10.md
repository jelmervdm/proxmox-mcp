# Release v1.0.10: Complete ContextForge Gateway Credential Initialization

## Summary
Version 1.0.10 resolves `mcpgateway.config.SecurityConfigurationError: auth_encryption_secret: unset placeholder (__REPLACE_ME__) rejected` and associated password complexity/length validation failures when operating in ContextForge Gateway mode (`ENABLE_CONTEXTFORGE_GATEWAY=true`).

## Highlights
- **Comprehensive Secret Fallback**: `entrypoint.sh` now automatically generates ephemeral strong keys and passwords for all variables checked by `mcpgateway`:
  - `JWT_SECRET_KEY` (256-bit hex)
  - `AUTH_ENCRYPTION_SECRET` (256-bit hex)
  - `PLATFORM_ADMIN_PASSWORD` (URL-safe 24-char token)
  - `DEFAULT_USER_PASSWORD` (URL-safe 24-char token)
  - `BASIC_AUTH_PASSWORD` (URL-safe 24-char token)
- Prevents container crashes without requiring manual secret injection in deployments where ContextForge Gateway is used strictly as an SSE-to-stdio translation wrapper.

## Docker Container
Built automatically by GitHub Actions:
- `ghcr.io/jelmervdm/proxmox-mcp:v1.0.10`
- `ghcr.io/jelmervdm/proxmox-mcp:latest`

