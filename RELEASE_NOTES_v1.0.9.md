# Release v1.0.9: ContextForge Gateway Secret Validation Fix

## Summary
Version 1.0.9 addresses startup failures when running in ContextForge Gateway mode (`ENABLE_CONTEXTFORGE_GATEWAY=true`) caused by strict secret validation in recent `mcp-contextforge-gateway` releases.

## Highlights

### 1. Automatic JWT Secret Generation Fallback
- `entrypoint.sh` now automatically detects if `JWT_SECRET_KEY` is undefined or set to the default placeholder `__REPLACE_ME__`.
- Generates a 256-bit cryptographically secure token (`secrets.token_hex(32)`) on the fly, preventing fatal `mcpgateway.config.SecurityConfigurationError` crashes while satisfying internal validation constraints.

### 2. Environment Configuration
- Added `JWT_SECRET_KEY` mapping to `docker-compose.yml`.
- Added `JWT_SECRET_KEY` example and instructions to `.env.example`.

## Docker Container
Built automatically by GitHub Actions:
- `ghcr.io/jelmervdm/proxmox-mcp:v1.0.9`
- `ghcr.io/jelmervdm/proxmox-mcp:latest`
