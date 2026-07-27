"""SDN (Software-Defined Networking) management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register SDN management tools."""

    # ── VNets ─────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_sdn_vnets() -> str:
        """List SDN virtual networks (VNets) configured on the cluster.

        Use when reviewing available software-defined network bridges.
        To view details for a specific VNet, use get_sdn_vnet instead.
        """
        return format_response(api_request("get", "/cluster/sdn/vnets"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_sdn_vnet(
        vnet: Annotated[str, Field(description="VNet identifier (e.g., 'vnet0').")],
    ) -> str:
        """Get SDN VNet configuration details.

        Use when inspecting VLAN tags, assigned zones, or bridge properties for a VNet.
        To list all virtual networks, use list_sdn_vnets instead.

        Args:
            vnet: VNet ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/vnets/{vnet}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_sdn_vnet(
        vnet: Annotated[str, Field(description="Name/ID for the new VNet.")],
        zone: Annotated[str, Field(description="Associated SDN zone ID (e.g., 'myzone').")],
        tag: Annotated[int, Field(description="Optional VLAN tag (0 for un-tagged).")] = 0,
        alias: Annotated[str, Field(description="Display alias or description for the VNet.")] = "",
        vlanaware: Annotated[bool, Field(description="If True, enable VLAN-aware bridge mode.")] = False,
    ) -> str:
        """Create a new SDN virtual network (VNet).

        Use when creating isolated or tagged virtual network segments for VMs and containers.
        To apply pending SDN changes to cluster nodes, use apply_sdn_changes.

        Args:
            vnet: VNet ID.
            zone: Zone ID.
            tag: VLAN tag.
            alias: Display alias.
            vlanaware: Enable VLAN-aware bridge.
        """
        params: dict = {"vnet": vnet, "zone": zone}
        if tag:
            params["tag"] = tag
        if alias:
            params["alias"] = alias
        if vlanaware:
            params["vlanaware"] = 1
        return format_response(api_request("post", "/cluster/sdn/vnets", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_sdn_vnet(
        vnet: Annotated[str, Field(description="VNet ID to update.")],
        zone: Annotated[str, Field(description="New associated zone ID.")] = "",
        tag: Annotated[int, Field(description="New VLAN tag (-1 to leave unchanged).")] = -1,
        alias: Annotated[str, Field(description="Updated display alias.")] = "",
        delete: Annotated[str, Field(description="Comma-separated properties to delete.")] = "",
    ) -> str:
        """Update configuration properties of an existing SDN VNet.

        Use when modifying zone associations, VLAN tags, or aliases.

        Args:
            vnet: VNet ID.
            zone: Zone ID.
            tag: VLAN tag (-1 = don't change).
            alias: Display alias.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if zone:
            params["zone"] = zone
        if tag >= 0:
            params["tag"] = tag
        if alias:
            params["alias"] = alias
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/sdn/vnets/{vnet}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_sdn_vnet(
        vnet: Annotated[str, Field(description="ID of the VNet to delete.")],
    ) -> str:
        """Delete an SDN virtual network.

        Use when removing unused SDN VNet definitions.

        Args:
            vnet: VNet ID.
        """
        return format_response(api_request("delete", f"/cluster/sdn/vnets/{vnet}"))

    # ── VNet Subnets ──────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_sdn_subnets(
        vnet: Annotated[str, Field(description="VNet ID for which to list subnets.")],
    ) -> str:
        """List IP subnets associated with an SDN VNet.

        Use when inspecting CIDRs, gateways, and SNAT rules for a VNet.

        Args:
            vnet: VNet ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/vnets/{vnet}/subnets"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_sdn_subnet(
        vnet: Annotated[str, Field(description="VNet ID to attach the subnet to.")],
        subnet: Annotated[str, Field(description="Subnet CIDR notation (e.g., '10.0.0.0/24').")],
        gateway: Annotated[str, Field(description="Gateway IP address (e.g., '10.0.0.1').")] = "",
        snat: Annotated[bool, Field(description="Enable Source Network Address Translation (SNAT).")] = False,
        dnszoneprefix: Annotated[str, Field(description="DNS zone prefix for IPAM automatic registration.")] = "",
    ) -> str:
        """Create an IP subnet inside an SDN VNet.

        Use when configuring IP ranges, default gateways, or SNAT for virtual networks.

        Args:
            vnet: VNet ID.
            subnet: Subnet CIDR (e.g. '10.0.0.0/24').
            gateway: Gateway IP.
            snat: Enable SNAT.
            dnszoneprefix: DNS zone prefix.
        """
        params: dict = {"subnet": subnet, "type": "subnet"}
        if gateway:
            params["gateway"] = gateway
        if snat:
            params["snat"] = 1
        if dnszoneprefix:
            params["dnszoneprefix"] = dnszoneprefix
        return format_response(api_request("post", f"/cluster/sdn/vnets/{vnet}/subnets", **params))

    # ── Zones ─────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_sdn_zones() -> str:
        """List SDN network zones (VLAN, VXLAN, EVPN, Simple).

        Use when auditing cluster networking zone topologies.
        To inspect a specific zone's configuration, use get_sdn_zone instead.
        """
        return format_response(api_request("get", "/cluster/sdn/zones"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_sdn_zone(
        zone: Annotated[str, Field(description="SDN Zone ID.")],
    ) -> str:
        """Get detailed configuration parameters for an SDN zone.

        Use when checking MTU, IPAM bindings, or host node membership for a zone.

        Args:
            zone: Zone ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/zones/{zone}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_sdn_zone(
        zone: Annotated[str, Field(description="Unique ID for the new zone.")],
        type: Annotated[str, Field(description="Zone technology type: 'simple', 'vlan', 'qinq', 'vxlan', or 'evpn'.")],
        nodes: Annotated[str, Field(description="Comma-separated node list to assign to this zone.")] = "",
        ipam: Annotated[str, Field(description="IPAM plugin identifier (e.g., 'pve').")] = "",
        dns: Annotated[str, Field(description="DNS plugin identifier.")] = "",
        bridge: Annotated[str, Field(description="Physical bridge interface (e.g., 'vmbr0').")] = "",
        mtu: Annotated[int, Field(description="Custom MTU size for zone interfaces.")] = 0,
    ) -> str:
        """Create a new SDN zone defining underlying network transport layer.

        Use when defining EVPN, VXLAN, or VLAN overlay boundaries.
        To apply pending SDN configurations to all nodes, use apply_sdn_changes.

        Args:
            zone: Zone ID.
            type: Zone type: 'simple', 'vlan', 'qinq', 'vxlan', 'evpn'.
            nodes: Comma-separated node list.
            ipam: IPAM plugin name.
            dns: DNS plugin name.
            bridge: Bridge name.
            mtu: MTU.
        """
        params: dict = {"zone": zone, "type": type}
        for key, val in [("nodes", nodes), ("ipam", ipam), ("dns", dns), ("bridge", bridge)]:
            if val:
                params[key] = val
        if mtu:
            params["mtu"] = mtu
        return format_response(api_request("post", "/cluster/sdn/zones", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_sdn_zone(
        zone: Annotated[str, Field(description="Zone ID to delete.")],
    ) -> str:
        """Delete an SDN zone from the cluster.

        Use when decommissioning a network zone. Note that associated VNets must be deleted first.

        Args:
            zone: Zone ID.
        """
        return format_response(api_request("delete", f"/cluster/sdn/zones/{zone}"))

    # ── Controllers ───────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_sdn_controllers() -> str:
        """List SDN control-plane controllers (e.g., BGP/EVPN controllers).

        Use when auditing SDN routing controller nodes.
        """
        return format_response(api_request("get", "/cluster/sdn/controllers"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_sdn_controller(
        controller: Annotated[str, Field(description="Controller ID.")],
    ) -> str:
        """Get configuration for a specific SDN controller.

        Use when inspecting controller AS numbers, peers, or routing options.

        Args:
            controller: Controller ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/controllers/{controller}"))

    # ── IPAM ──────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_sdn_ipams() -> str:
        """List configured IP Address Management (IPAM) plugins.

        Use when reviewing IPAM backends (e.g., PVE internal, NetBox, phpIPAM).
        """
        return format_response(api_request("get", "/cluster/sdn/ipams"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_sdn_ipam(
        ipam: Annotated[str, Field(description="IPAM plugin identifier.")],
    ) -> str:
        """Get configuration details for an IPAM plugin.

        Use when checking IPAM server endpoints or API credentials.

        Args:
            ipam: IPAM ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/ipams/{ipam}"))

    # ── DNS ───────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_sdn_dns() -> str:
        """List configured SDN DNS integration plugins.

        Use when auditing automatic DNS record registration backends.
        """
        return format_response(api_request("get", "/cluster/sdn/dns"))

    # ── Apply SDN Changes ─────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def apply_sdn_changes() -> str:
        """Reload and apply pending SDN configurations across all PVE cluster nodes.

        Use after adding, updating, or deleting VNets, subnets, or zones to push changes live.
        """
        return format_response(api_request("put", "/cluster/sdn"))
