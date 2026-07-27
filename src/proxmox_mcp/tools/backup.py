"""Backup and vzdump tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register backup management tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_backup_jobs() -> str:
        """List all scheduled cluster backup jobs (vzdump).

        Use when reviewing automated backup schedules, retention policies, and targets.
        To view specific configuration for a single job, use get_backup_job instead.
        """
        return format_response(api_request("get", "/cluster/backup"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_backup_job(
        id: Annotated[str, Field(description="Backup job identifier (e.g., 'backup-100').")],
    ) -> str:
        """Get details, schedule, compression mode, and guest target list for a backup job.

        Use when inspecting settings for a specific scheduled backup task.
        To list all backup jobs, use list_backup_jobs instead.

        Args:
            id: Backup job ID.
        """
        return format_response(api_request("get", f"/cluster/backup/{id}"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_backup_job_included_volumes(
        id: Annotated[str, Field(description="Backup job ID.")],
    ) -> str:
        """Get list of virtual disks and volumes included in a backup job.

        Use when verifying volume selection before running automated backups.

        Args:
            id: Backup job ID.
        """
        return format_response(api_request("get", f"/cluster/backup/{id}/included_volumes"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_backup_job(
        storage: Annotated[str, Field(description="Target storage ID for backups (e.g., 'local', 'pbs-server').")],
        schedule: Annotated[str, Field(description="Calendar schedule string (e.g., 'daily', 'sat 02:00', 'mon..fri 23:00').")] = "daily",
        all_guests: Annotated[bool, Field(description="If True, include all cluster guests in backup.")] = True,
        vmid: Annotated[str, Field(description="Comma-separated VMIDs to back up if all_guests is False (e.g., '100,101').")] = "",
        node: Annotated[str, Field(description="Optional filter to only back up guests on a specific node.")] = "",
        mode: Annotated[str, Field(description="Backup execution mode: 'snapshot', 'suspend', or 'stop'.")] = "snapshot",
        compress: Annotated[str, Field(description="Compression algorithm: 'none', 'lzo', 'gzip', or 'zstd'.")] = "zstd",
        mailnotification: Annotated[str, Field(description="Mail notification trigger: 'always', 'failure', or 'never'.")] = "",
        mailto: Annotated[str, Field(description="Comma-separated notification recipient email addresses.")] = "",
        maxfiles: Annotated[int, Field(description="Max backup files to keep (deprecated; use prune_backups).")] = 0,
        prune_backups: Annotated[str, Field(description="Retention rules (e.g., 'keep-daily=7,keep-weekly=4,keep-monthly=12').")] = "",
        notes_template: Annotated[str, Field(description="Template for backup file notes.")] = "",
        enabled: Annotated[bool, Field(description="If True, enable the backup schedule upon creation.")] = True,
        comment: Annotated[str, Field(description="Optional description for the backup job.")] = "",
    ) -> str:
        """Create a scheduled vzdump backup job.

        Use when configuring recurring backup schedules across VMs or containers.
        To trigger an immediate one-off backup, use create_vzdump instead.

        Args:
            storage: Target storage ID for backups.
            schedule: Schedule in systemd calendar format (e.g. 'daily', 'weekly', '02:00').
            all_guests: Backup all guests.
            vmid: Comma-separated VMIDs to back up (if not all_guests).
            node: Only back up guests on this node.
            mode: Backup mode: 'snapshot', 'suspend', 'stop'.
            compress: Compression: 'none', 'lzo', 'gzip', 'zstd'.
            mailnotification: 'always' or 'failure'.
            mailto: Comma-separated email addresses.
            maxfiles: Max backup files to keep (0 = unlimited, deprecated - use prune_backups).
            prune_backups: Retention schedule (e.g. 'keep-daily=7,keep-weekly=4').
            notes_template: Template for backup notes.
            enabled: Enable the job.
            comment: Description.
        """
        params: dict = {"storage": storage, "schedule": schedule, "mode": mode, "compress": compress}
        if all_guests:
            params["all"] = 1
        if vmid:
            params["vmid"] = vmid
        if node:
            params["node"] = node
        if mailnotification:
            params["mailnotification"] = mailnotification
        if mailto:
            params["mailto"] = mailto
        if maxfiles:
            params["maxfiles"] = maxfiles
        if prune_backups:
            params["prune-backups"] = prune_backups
        if notes_template:
            params["notes-template"] = notes_template
        if not enabled:
            params["enabled"] = 0
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/backup", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_backup_job(
        id: Annotated[str, Field(description="Backup job ID to update.")],
        storage: Annotated[str, Field(description="New target storage ID.")] = "",
        schedule: Annotated[str, Field(description="New calendar schedule.")] = "",
        all_guests: Annotated[bool, Field(description="Include all guests.")] = False,
        vmid: Annotated[str, Field(description="Comma-separated VMIDs.")] = "",
        node: Annotated[str, Field(description="Node filter.")] = "",
        mode: Annotated[str, Field(description="Backup mode.")] = "",
        compress: Annotated[str, Field(description="Compression mode.")] = "",
        enabled: Annotated[bool, Field(description="Enable/disable schedule.")] = True,
        delete: Annotated[str, Field(description="Comma-separated properties to remove.")] = "",
    ) -> str:
        """Update settings for an existing scheduled backup job.

        Use when altering backup target storage, retention policies, or target guest lists.

        Args:
            id: Backup job ID.
            storage: Target storage ID.
            schedule: Schedule in systemd calendar format.
            all_guests: Backup all guests.
            vmid: Comma-separated VMIDs.
            node: Node filter.
            mode: Backup mode.
            compress: Compression.
            enabled: Enable/disable.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if storage:
            params["storage"] = storage
        if schedule:
            params["schedule"] = schedule
        if all_guests:
            params["all"] = 1
        if vmid:
            params["vmid"] = vmid
        if node:
            params["node"] = node
        if mode:
            params["mode"] = mode
        if compress:
            params["compress"] = compress
        if not enabled:
            params["enabled"] = 0
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/backup/{id}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_backup_job(
        id: Annotated[str, Field(description="Backup job ID to delete.")],
    ) -> str:
        """Delete a scheduled backup job configuration.

        Use when removing obsolete automated backup tasks. Note that existing backup files on storage are preserved.

        Args:
            id: Backup job ID.
        """
        return format_response(api_request("delete", f"/cluster/backup/{id}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_vzdump(
        node: Annotated[str, Field(description="Target PVE host node for the vzdump process.")],
        vmid: Annotated[str, Field(description="Comma-separated VM/CT IDs to back up (e.g., '100,101').")] = "",
        all_guests: Annotated[bool, Field(description="If True, back up all guests on the target node.")] = False,
        storage: Annotated[str, Field(description="Target storage ID (empty string uses default).")] = "",
        mode: Annotated[str, Field(description="Backup mode: 'snapshot', 'suspend', or 'stop'.")] = "snapshot",
        compress: Annotated[str, Field(description="Compression: 'none', 'lzo', 'gzip', or 'zstd'.")] = "zstd",
        stdout: Annotated[bool, Field(description="If True, stream output to stdout instead of file.")] = False,
    ) -> str:
        """Run an immediate one-off vzdump backup process.

        Use when taking on-demand backups before maintenance or upgrades.
        To schedule recurring backups, use create_backup_job instead.

        Args:
            node: The node to run the backup on.
            vmid: Comma-separated VMIDs (required if not all_guests).
            all_guests: Back up all guests on the node.
            storage: Target storage (empty = default).
            mode: Backup mode: 'snapshot', 'suspend', 'stop'.
            compress: Compression: 'none', 'lzo', 'gzip', 'zstd'.
            stdout: Write to stdout instead of storage.
        """
        params: dict = {"mode": mode, "compress": compress}
        if vmid:
            params["vmid"] = vmid
        if all_guests:
            params["all"] = 1
        if storage:
            params["storage"] = storage
        if stdout:
            params["stdout"] = 1
        return format_response(api_request("post", f"/nodes/{node}/vzdump", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vzdump_defaults(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """Get default vzdump backup configuration settings for a node.

        Use when auditing node-level default backup storage and compression settings.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/vzdump/defaults"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vzdump_extractconfig(
        node: Annotated[str, Field(description="Node name where volume resides.")],
        volume: Annotated[str, Field(description="Backup volume ID (e.g., 'local:backup/vzdump-qemu-100-2026_07_01.vma.zst').")],
    ) -> str:
        """Extract and view guest VM/CT configuration from a backup archive file.

        Use when inspecting VM configuration stored inside a backup file without performing full restore.

        Args:
            node: The node name.
            volume: Backup volume ID (e.g. 'local:backup/vzdump-qemu-100-2024_01_01-00_00_00.vma.zst').
        """
        return format_response(api_request("get", f"/nodes/{node}/vzdump/extractconfig", volume=volume))

    # ── Backup file restore ───────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_backup_file_restore(
        node: Annotated[str, Field(description="Node name where storage resides.")],
        storage: Annotated[str, Field(description="Storage ID containing the backup.")],
        volume: Annotated[str, Field(description="Backup file volume ID.")],
        filepath: Annotated[str, Field(description="Directory path inside the backup archive (defaults to '/').")] = "/",
    ) -> str:
        """Browse files inside a vzdump VM or CT backup for single-file recovery.

        Use when inspecting single files inside a backup archive before extracting.
        To download a specific file from the archive, use download_file_restore.

        Args:
            node: The node name.
            storage: Storage ID.
            volume: Backup volume ID.
            filepath: Path within the backup (default '/').
        """
        return format_response(
            api_request(
                "get",
                f"/nodes/{node}/storage/{storage}/file-restore/list",
                volume=volume,
                filepath=filepath,
            )
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def download_file_restore(
        node: Annotated[str, Field(description="Node name.")],
        storage: Annotated[str, Field(description="Storage ID.")],
        volume: Annotated[str, Field(description="Backup volume ID.")],
        filepath: Annotated[str, Field(description="Absolute path of file to extract from the backup archive.")],
    ) -> str:
        """Extract and download a single file from a guest backup archive.

        Use to perform granular single-file recovery without restoring the entire virtual machine.

        Args:
            node: The node name.
            storage: Storage ID.
            volume: Backup volume ID.
            filepath: Path of the file to download from the backup.
        """
        return format_response(
            api_request(
                "get",
                f"/nodes/{node}/storage/{storage}/file-restore/download",
                volume=volume,
                filepath=filepath,
            )
        )
