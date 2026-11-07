# Release v1.0.11: Upstream Bug Fixes & Raw API Lockdown

## Summary
Version 1.0.11 ports critical upstream reliability fixes for API parameter collisions, QEMU guest agent execution, and cluster task listing, alongside a security toggle to disable raw API execution.

## Highlights

### 1. Positional-Only `api_request` Parameters
- `api_request(method: str, path: str, /, **params)` now designates `method` and `path` as positional-only arguments.
- Prevents collisions and Python `TypeError` exceptions when forwarding API parameters named `path` or `method` (e.g., `update_acl`, `get_permissions`, `create_storage`, and `proxmox_api_raw`).

### 2. QEMU Guest Agent Argv Splitting (`vm_agent_exec`)
- `vm_agent_exec` now supports both `command: str` and `command: list[str]`.
- String commands are tokenized into argv arrays using `shlex.split`, satisfying the Proxmox VE agent execution endpoint requirements. List arguments are passed through unchanged for raw Windows paths.

### 3. Cluster Task Client-Side Limiting (`get_cluster_tasks`)
- Proxmox VE `/cluster/tasks` API does not accept a `limit` parameter. Tasks are now retrieved and sliced client-side (`tasks[:limit]`), ensuring reliable task limits without API parameter rejections.

### 4. Optional Raw API Lockdown (`PROXMOX_DISABLE_RAW_API`)
- Added support for `PROXMOX_DISABLE_RAW_API=true` to block execution of `proxmox_api_raw` in locked-down environments.

## Docker Container
Built automatically by GitHub Actions:
- `ghcr.io/jelmervdm/proxmox-mcp:v1.0.11`
- `ghcr.io/jelmervdm/proxmox-mcp:latest`
