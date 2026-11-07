# Release v1.0.8: Host Lifecycle, Storage Replication CRUD, ZFS Management & Dynamic Hardware Config

## Summary
Version 1.0.8 expands the Proxmox MCP server from 286 to **297 registered tools** across 11 modules, introduces dynamic hardware configuration capabilities, and enhances routing ergonomics for AI client environments.

## Highlights

### 1. Dynamic Hardware Configuration (`extra_config`)
- Added `extra_config` parameter to `update_vm_config` (QEMU) and `update_container_config` (LXC) supporting JSON or comma-separated key=value strings.
- Allows direct configuration of virtual disks (`scsi0`–`scsi30`, `virtio0`–`virtio15`), I/O bandwidth/IOPS throttling (`mbps_wr`, `mbps_rd`, `iops_wr`, `iops_rd`), secondary network interfaces (`net1`, `net2`...), and LXC mount points (`mp0`).

### 2. Node Power Lifecycle
- **`reboot_node`**: Controlled graceful reboot of a Proxmox VE host node (`POST /nodes/{node}/status`, `command: "reboot"`).
- **`shutdown_node`**: Controlled power down of a Proxmox VE host node (`POST /nodes/{node}/status`, `command: "shutdown"`).

### 3. Storage Replication Lifecycle
- **`update_replication_job`**: Update replication schedule, rate limit, description, or toggle disabled state (`PUT /cluster/replication/{id}`).
- **`get_replication_log`**: Retrieve execution logs to diagnose ZFS snapshot synchronization and transfer errors (`GET /cluster/replication/{id}/log`).
- **`get_replication_status`**: Retrieve real-time operational status and failure metrics (`GET /cluster/replication/{id}/status`).

### 4. ZFS, LVM, and Directory Storage Management
- **`destroy_zfs_pool`**: Destroy a ZFS storage pool with optional partition cleanup (`DELETE /nodes/{node}/disks/zfs/{name}`).
- **`zfs_scrub`**: Start or cancel a ZFS pool data integrity scrub (`POST /nodes/{node}/disks/zfs/{name}`).
- **`delete_lvm`**: Destroy an LVM volume group (`DELETE /nodes/{node}/disks/lvm/{name}`).
- **`delete_lvmthin`**: Destroy an LVM thin pool (`DELETE /nodes/{node}/disks/lvmthin/{name}`).
- **`delete_directory_storage`**: Remove and unmount directory-backed storage mounts (`DELETE /nodes/{node}/disks/directory/{name}`).

### 5. VM Recovery & Lifecycle Enhancements
- **`unlink_vm_disk`**: Safely detach a virtual disk from a VM without deleting the volume data (`PUT /nodes/{node}/qemu/{vmid}/unlink`).
- **`stop_vm`**: Added `overrule_shutdown: bool` to cancel running shutdown tasks and force-stop locked/HA VMs.
- **`rollback_vm_snapshot`**: Added `start: bool` flag to automatically boot the VM following snapshot restoration.

### 6. Router Ergonomics
- Defaulted 19 core operational tools to direct visibility in routed mode (`TOOL_ROUTING=true`), eliminating multi-turn routing latency for routine management tasks.
- Fully configurable via the `ALWAYS_VISIBLE_TOOLS` environment variable.

## Docker Container
Built automatically by GitHub Actions:
- `ghcr.io/jelmervdm/proxmox-mcp:v1.0.8`
- `ghcr.io/jelmervdm/proxmox-mcp:latest`

