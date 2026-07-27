"""Pool management and ACME certificate tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register pool and ACME tools."""

    # ── Pools ─────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_pools() -> str:
        """List all resource pools configured in the Proxmox cluster.

        Use when inspecting available resource pools and organizational boundaries.
        To view specific pool members and configuration, use get_pool instead.
        """
        return format_response(api_request("get", "/pools"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_pool(
        poolid: Annotated[str, Field(description="Unique identifier of the resource pool (e.g., 'production').")],
    ) -> str:
        """Get configuration, description, and list of VM/storage members for a specific pool.

        Use when inspecting members belonging to a resource pool.
        To list all available resource pools, use list_pools instead.

        Args:
            poolid: Pool ID.
        """
        return format_response(api_request("get", f"/pools/{poolid}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_pool(
        poolid: Annotated[str, Field(description="Unique ID for the new resource pool.")],
        comment: Annotated[str, Field(description="Optional description or notes for the pool.")] = "",
    ) -> str:
        """Create a new resource pool for grouping virtual machines and storage.

        Use when establishing new permission or resource boundaries.
        To modify existing pool memberships or comments, use update_pool instead.

        Args:
            poolid: Pool ID.
            comment: Description.
        """
        params: dict = {"poolid": poolid}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/pools", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_pool(
        poolid: Annotated[str, Field(description="Unique ID of the pool to update.")],
        comment: Annotated[str, Field(description="Updated description or comment for the pool.")] = "",
        vms: Annotated[str, Field(description="Comma-separated VM/CT IDs to add or remove (e.g., '100,101').")] = "",
        storage: Annotated[str, Field(description="Comma-separated storage identifiers to add or remove (e.g., 'local-lvm').")] = "",
        delete: Annotated[bool, Field(description="If True, remove specified VMs/storage from pool instead of adding.")] = False,
    ) -> str:
        """Update a resource pool's comment or add/remove VM and storage members.

        Use when managing resource pool assignments.
        To delete a pool completely, use delete_pool instead.

        Args:
            poolid: Pool ID.
            comment: Description.
            vms: Comma-separated VMIDs to add/remove.
            storage: Comma-separated storage IDs to add/remove.
            delete: If true, remove the specified vms/storage from the pool instead of adding.
        """
        params: dict = {}
        if comment:
            params["comment"] = comment
        if vms:
            params["vms"] = vms
        if storage:
            params["storage"] = storage
        if delete:
            params["delete"] = 1
        return format_response(api_request("put", f"/pools/{poolid}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_pool(
        poolid: Annotated[str, Field(description="Unique identifier of the resource pool to delete.")],
    ) -> str:
        """Delete an empty resource pool from Proxmox.

        Use when decommissioning a resource pool. Note that members should be removed prior to deletion.

        Args:
            poolid: Pool ID.
        """
        return format_response(api_request("delete", f"/pools/{poolid}"))

    # ── ACME (Let's Encrypt Certificates) ─────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_acme_accounts() -> str:
        """List configured ACME (Let's Encrypt) accounts on the cluster.

        Use when reviewing registered ACME accounts for automated SSL certificates.
        To inspect a specific ACME account's details, use get_acme_account instead.
        """
        return format_response(api_request("get", "/cluster/acme/account"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_acme_account(
        name: Annotated[str, Field(description="Name of the ACME account (defaults to 'default').")] = "default",
    ) -> str:
        """Get detailed account information and contact email for a specific ACME account.

        Use when checking ACME registration status and directory endpoints.
        To list all registered ACME accounts, use list_acme_accounts.

        Args:
            name: Account name (default: 'default').
        """
        return format_response(api_request("get", f"/cluster/acme/account/{name}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def register_acme_account(
        contact: Annotated[str, Field(description="Contact email address for ACME account registration.")],
        directory: Annotated[str, Field(description="ACME directory URL (empty string defaults to Let's Encrypt production).")] = "",
        name: Annotated[str, Field(description="Name to assign to the ACME account.")] = "default",
        tos_url: Annotated[str, Field(description="Terms of Service URL to accept.")] = "",
    ) -> str:
        """Register a new ACME (Let's Encrypt) account for cluster node certificates.

        Use when setting up automated SSL/TLS certificate issuing for cluster nodes.

        Args:
            contact: Contact email address.
            directory: ACME directory URL (empty = Let's Encrypt production).
            name: Account name.
            tos_url: Terms of service URL to accept.
        """
        params: dict = {"contact": contact, "name": name}
        if directory:
            params["directory"] = directory
        if tos_url:
            params["tos_url"] = tos_url
        return format_response(api_request("post", "/cluster/acme/account", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_acme_plugins() -> str:
        """List configured ACME DNS challenge plugins on the cluster.

        Use when auditing available ACME DNS validation plugins.
        To view configuration of a specific plugin, use get_acme_plugin instead.
        """
        return format_response(api_request("get", "/cluster/acme/plugins"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_acme_plugin(
        id: Annotated[str, Field(description="Unique ID of the ACME DNS challenge plugin.")],
    ) -> str:
        """Get configuration parameters for a specific ACME DNS plugin.

        Use when inspecting DNS challenge settings for ACME certificate validation.

        Args:
            id: Plugin ID.
        """
        return format_response(api_request("get", f"/cluster/acme/plugins/{id}"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_acme_directories() -> str:
        """List known ACME directory URLs (production, staging, Custom).

        Use when identifying ACME authority endpoints for account registration.
        """
        return format_response(api_request("get", "/cluster/acme/directories"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_acme_tos() -> str:
        """Get the current ACME Terms of Service URL.

        Use to retrieve the ToS link required during ACME account registration.
        """
        return format_response(api_request("get", "/cluster/acme/tos"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def order_node_certificate(
        node: Annotated[str, Field(description="Node name on which to order/renew ACME certificate.")],
        force: Annotated[bool, Field(description="If True, force renewal even if not close to expiration.")] = False,
    ) -> str:
        """Order or renew an ACME SSL certificate for a Proxmox node.

        Use when triggering SSL certificate issuance or renewal on a PVE host.
        To view current node certificate details, use get_node_certificates instead.

        Args:
            node: The node name.
            force: Force renewal even if not due.
        """
        params: dict = {}
        if force:
            params["force"] = 1
        return format_response(api_request("post", f"/nodes/{node}/certificates/acme/certificate", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_certificates(
        node: Annotated[str, Field(description="Target PVE node name.")],
    ) -> str:
        """Get active SSL certificate details (issuer, expiration, fingerprint) for a node.

        Use when auditing node TLS certificate validity and expiration dates.
        To trigger a renewal via ACME, use order_node_certificate instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/certificates/info"))
