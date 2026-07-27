"""High Availability (HA) management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register HA management tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ha_status() -> str:
        """Get High Availability manager status, quorum state, and active master node.

        Use when monitoring HA service state and cluster quorum status.
        To view detailed manager state details, use get_ha_manager_status instead.
        """
        return format_response(api_request("get", "/cluster/ha/status"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ha_manager_status() -> str:
        """Get detailed HA CRM and LRM daemon status and state machine details.

        Use when troubleshooting HA failover locks, fencing, or node election issues.
        """
        return format_response(api_request("get", "/cluster/ha/status/manager_status"))

    # ── HA Resources ──────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_ha_resources() -> str:
        """List all VMs and LXC containers managed under High Availability.

        Use when inspecting HA protection status for virtual machines and containers.
        To inspect configuration for a specific HA resource, use get_ha_resource instead.
        """
        return format_response(api_request("get", "/cluster/ha/resources"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ha_resource(
        sid: Annotated[str, Field(description="HA resource identifier formatted as 'type:vmid' (e.g., 'vm:100' or 'ct:101').")],
    ) -> str:
        """Get HA resource state, group assignment, restart limits, and relocation policies.

        Use when inspecting failover configuration for a single protected VM or container.
        To list all HA resources, use list_ha_resources instead.

        Args:
            sid: HA resource ID (format: 'type:vmid', e.g. 'vm:100' or 'ct:101').
        """
        return format_response(api_request("get", f"/cluster/ha/resources/{sid}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_ha_resource(
        sid: Annotated[str, Field(description="Resource ID formatted as 'type:vmid' (e.g., 'vm:100' or 'ct:101').")],
        group: Annotated[str, Field(description="Optional HA group identifier to assign resource to.")] = "",
        max_relocate: Annotated[int, Field(description="Maximum number of automatic relocation attempts on failure.")] = 1,
        max_restart: Annotated[int, Field(description="Maximum number of automatic restart attempts on failure.")] = 1,
        state: Annotated[str, Field(description="Target HA state: 'started', 'stopped', 'enabled', 'disabled', or 'ignored'.")] = "started",
        comment: Annotated[str, Field(description="Optional description or note for the HA resource.")] = "",
    ) -> str:
        """Add a virtual machine or container to Proxmox High Availability protection.

        Use when configuring failover protection for a VM or LXC container.
        To remove HA management from a resource, use delete_ha_resource.

        Args:
            sid: Resource ID (format: 'type:vmid', e.g. 'vm:100' or 'ct:101').
            group: HA group name.
            max_relocate: Max relocations on failure.
            max_restart: Max restarts on failure.
            state: Desired state: 'started', 'stopped', 'enabled', 'disabled', 'ignored'.
            comment: Description.
        """
        params: dict = {"sid": sid, "max_relocate": max_relocate, "max_restart": max_restart, "state": state}
        if group:
            params["group"] = group
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/ha/resources", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_ha_resource(
        sid: Annotated[str, Field(description="Target HA resource identifier ('type:vmid').")],
        group: Annotated[str, Field(description="New HA group identifier assignment.")] = "",
        max_relocate: Annotated[int, Field(description="Max relocate attempts (-1 to leave unchanged).")] = -1,
        max_restart: Annotated[int, Field(description="Max restart attempts (-1 to leave unchanged).")] = -1,
        state: Annotated[str, Field(description="Updated target HA state ('started', 'stopped', 'disabled', etc.).")] = "",
        comment: Annotated[str, Field(description="Updated comment or description.")] = "",
        delete: Annotated[str, Field(description="Comma-separated properties to remove from config.")] = "",
    ) -> str:
        """Update High Availability settings for a managed VM or container.

        Use when changing target states, failover policies, or group assignments.

        Args:
            sid: Resource ID.
            group: HA group name.
            max_relocate: Max relocations (-1 = don't change).
            max_restart: Max restarts (-1 = don't change).
            state: Desired state.
            comment: Description.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if group:
            params["group"] = group
        if max_relocate >= 0:
            params["max_relocate"] = max_relocate
        if max_restart >= 0:
            params["max_restart"] = max_restart
        if state:
            params["state"] = state
        if comment:
            params["comment"] = comment
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/ha/resources/{sid}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_ha_resource(
        sid: Annotated[str, Field(description="HA resource ID ('type:vmid') to remove from HA management.")],
    ) -> str:
        """Remove High Availability management from a VM or container.

        Use when disabling automatic HA failover monitoring for a resource without deleting the underlying VM.

        Args:
            sid: Resource ID (format: 'type:vmid').
        """
        return format_response(api_request("delete", f"/cluster/ha/resources/{sid}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def migrate_ha_resource(
        sid: Annotated[str, Field(description="HA resource ID ('type:vmid').")],
        node: Annotated[str, Field(description="Target host node for live migration.")],
    ) -> str:
        """Request live migration of an HA-managed resource to a target node.

        Use when triggering controlled live migration of protected VMs across cluster nodes.
        To perform non-live node relocation, use relocate_ha_resource instead.

        Args:
            sid: Resource ID.
            node: Target node.
        """
        return format_response(api_request("post", f"/cluster/ha/resources/{sid}/migrate", node=node))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def relocate_ha_resource(
        sid: Annotated[str, Field(description="HA resource ID ('type:vmid').")],
        node: Annotated[str, Field(description="Target node for resource relocation.")],
    ) -> str:
        """Request relocation of an HA resource to another node (may stop/start if offline).

        Use when moving HA resources during node maintenance.
        To perform live migration without downtime, use migrate_ha_resource instead.

        Args:
            sid: Resource ID.
            node: Target node.
        """
        return format_response(api_request("post", f"/cluster/ha/resources/{sid}/relocate", node=node))

    # ── HA Groups ─────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_ha_groups() -> str:
        """List configured HA node groups and their member priorities.

        Use when auditing node groups created for failover targeting.
        To view specific group configuration, use get_ha_group instead.
        """
        return format_response(api_request("get", "/cluster/ha/groups"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ha_group(
        group: Annotated[str, Field(description="HA group identifier.")],
    ) -> str:
        """Get node priority assignments and failback rules for an HA group.

        Use when inspecting node priority ordering for failover target groups.

        Args:
            group: Group ID.
        """
        return format_response(api_request("get", f"/cluster/ha/groups/{group}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_ha_group(
        group: Annotated[str, Field(description="Unique identifier for the new HA group.")],
        nodes: Annotated[
            str,
            Field(description="Node list with optional priorities (e.g., 'node1:2,node2:1' - higher is preferred)."),
        ],
        nofailback: Annotated[bool, Field(description="If True, do not automatically fail back to higher priority node on recovery.")] = False,
        restricted: Annotated[bool, Field(description="If True, strictly restrict resources to nodes in this group.")] = False,
        comment: Annotated[str, Field(description="Optional description or note for the group.")] = "",
    ) -> str:
        """Create an HA group defining node preferences and failover constraints.

        Use when establishing specific host node preferences for HA resource placement.

        Args:
            group: Group ID.
            nodes: Node list with optional priority (e.g. 'node1:2,node2:1' — higher = preferred).
            nofailback: If true, don't fail back to higher-priority nodes once recovered.
            restricted: Only run on nodes in this group (otherwise runs anywhere but prefers group nodes).
            comment: Description.
        """
        params: dict = {"group": group, "nodes": nodes}
        if nofailback:
            params["nofailback"] = 1
        if restricted:
            params["restricted"] = 1
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/ha/groups", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_ha_group(
        group: Annotated[str, Field(description="HA group identifier to update.")],
        nodes: Annotated[str, Field(description="Updated node list with priorities.")] = "",
        nofailback: Annotated[bool, Field(description="If True, disable automatic failback.")] = False,
        restricted: Annotated[bool, Field(description="If True, restrict execution to group nodes.")] = False,
        comment: Annotated[str, Field(description="Updated description.")] = "",
        delete: Annotated[str, Field(description="Comma-separated properties to delete.")] = "",
    ) -> str:
        """Update node priority lists or failback rules for an HA group.

        Use when adding nodes or modifying failover priorities for an HA group.

        Args:
            group: Group ID.
            nodes: Node list with optional priority.
            nofailback: Don't fail back.
            restricted: Only run on group nodes.
            comment: Description.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if nodes:
            params["nodes"] = nodes
        if nofailback:
            params["nofailback"] = 1
        if restricted:
            params["restricted"] = 1
        if comment:
            params["comment"] = comment
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/ha/groups/{group}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_ha_group(
        group: Annotated[str, Field(description="HA group identifier to delete.")],
    ) -> str:
        """Delete an HA group from Proxmox cluster configuration.

        Use when removing obsolete HA node preference groups.

        Args:
            group: Group ID.
        """
        return format_response(api_request("delete", f"/cluster/ha/groups/{group}"))
