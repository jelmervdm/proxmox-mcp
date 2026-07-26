# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.3] - 2026-07-26

### Fixed
- Redirected container entrypoint `echo` startup messages to `stderr` (`>&2`). Prevents non-JSON-RPC output on `stdout` which caused stdio MCP clients (such as Antigravity) to fail initialization with `invalid character 'S' looking for beginning of value`.

## [1.0.2] - 2026-07-24

### Added
- Integrated ContextForge Gateway natively into the Docker image.
- Added `ENABLE_CONTEXTFORGE_GATEWAY` environment variable to conditionally run the gateway.
- Made the Gateway port configurable via `GATEWAY_PORT` (defaults to 8000).

## [1.0.1] - 2026-07-24

### Fixed
- Fixed an import error in IBM ContextForge by removing a semicolon from the `create_vm` tool docstring.
- Added GitHub Actions workflow to publish the Docker image to GitHub Container Registry (GHCR).

## [0.1.0] - 2026-03-23

### Added

- Initial release with 286 MCP tools covering the full Proxmox VE API
- Node management (status, config, networking, services, tasks, disks, hardware)
- QEMU VM lifecycle (create, clone, migrate, snapshots, cloud-init, QEMU agent)
- LXC container management (create, clone, migrate, snapshots, templates)
- Storage management (datacenter config, volumes, LVM/ZFS/directory)
- Cluster operations (status, config, Ceph, replication, metrics, notifications)
- Access control (users, groups, roles, ACL, API tokens, auth domains)
- Backup management (vzdump, scheduled jobs, file restore)
- Firewall rules (cluster, node, VM, and container level)
- High Availability (resources, groups, migration)
- SDN (VNets, zones, controllers, IPAM)
- Resource pools and ACME certificate management
- Generic `proxmox_api_raw` escape-hatch tool for arbitrary API calls
- Docker support with docker-compose
- API token and password authentication
