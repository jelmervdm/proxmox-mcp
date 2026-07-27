"""Firewall management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register firewall management tools."""

    # ── Cluster Firewall ──────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_firewall_options() -> str:
        """Get cluster-wide firewall options (enable status, default input/output policies, logging).

        Use when inspecting global Proxmox VE firewall security policies.
        To modify cluster firewall settings, use set_cluster_firewall_options instead.
        """
        return format_response(api_request("get", "/cluster/firewall/options"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def set_cluster_firewall_options(
        enable: Annotated[int, Field(description="1 to enable firewall globally, 0 to disable, -1 to leave unchanged.")] = -1,
        policy_in: Annotated[str, Field(description="Default ingress policy: 'ACCEPT', 'REJECT', or 'DROP'.")] = "",
        policy_out: Annotated[str, Field(description="Default egress policy: 'ACCEPT', 'REJECT', or 'DROP'.")] = "",
        log_ratelimit: Annotated[str, Field(description="Log rate limit spec (e.g., 'enable=1,rate=1/second,burst=5').")] = "",
        ebtables: Annotated[int, Field(description="1 to enable ebtables link-layer rules, 0 to disable, -1 to leave unchanged.")] = -1,
        delete: Annotated[str, Field(description="Comma-separated list of configuration keys to delete.")] = "",
    ) -> str:
        """Configure cluster-wide firewall defaults, default input/output policies, and rate limits.

        Use when modifying global ingress/egress filtering policies.

        Args:
            enable: 1 to enable, 0 to disable, -1 to not change.
            policy_in: Default input policy: 'ACCEPT', 'REJECT', 'DROP'.
            policy_out: Default output policy: 'ACCEPT', 'REJECT', 'DROP'.
            log_ratelimit: Log rate limit (e.g. 'enable=1,rate=1/second,burst=5').
            ebtables: 1 to enable ebtables rules, 0 to disable, -1 to not change.
            delete: Comma-separated options to delete.
        """
        params: dict = {}
        if enable >= 0:
            params["enable"] = enable
        if policy_in:
            params["policy_in"] = policy_in
        if policy_out:
            params["policy_out"] = policy_out
        if log_ratelimit:
            params["log_ratelimit"] = log_ratelimit
        if ebtables >= 0:
            params["ebtables"] = ebtables
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", "/cluster/firewall/options", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_cluster_firewall_rules() -> str:
        """List cluster-level firewall rules applied across all host nodes.

        Use when auditing datacenter firewall rule sequences.
        To view details for a specific rule position, use get_cluster_firewall_rule instead.
        """
        return format_response(api_request("get", "/cluster/firewall/rules"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_firewall_rule(
        pos: Annotated[int, Field(description="Rule sequence index position.")],
    ) -> str:
        """Get details for a specific cluster firewall rule by position index.

        Use when inspecting single cluster rule properties.

        Args:
            pos: Rule position number.
        """
        return format_response(api_request("get", f"/cluster/firewall/rules/{pos}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_cluster_firewall_rule(
        action: Annotated[str, Field(description="Action to take: 'ACCEPT', 'DROP', or 'REJECT'.")],
        type: Annotated[str, Field(description="Rule direction or group reference: 'in', 'out', or 'group'.")],
        enable: Annotated[int, Field(description="1 to enable rule, 0 to disable.")] = 1,
        source: Annotated[str, Field(description="Source address/range (CIDR, IP, or alias name).")] = "",
        dest: Annotated[str, Field(description="Destination address/range (CIDR, IP, or alias name).")] = "",
        proto: Annotated[str, Field(description="Transport protocol (e.g., 'tcp', 'udp', 'icmp').")] = "",
        sport: Annotated[str, Field(description="Source port or port range (e.g., '1024:65535').")] = "",
        dport: Annotated[str, Field(description="Destination port or port range (e.g., '22', '80,443').")] = "",
        iface: Annotated[str, Field(description="Target network interface (e.g., 'eth0').")] = "",
        macro: Annotated[str, Field(description="Predefined macro name (e.g., 'SSH', 'HTTP', 'HTTPS', 'Ping').")] = "",
        comment: Annotated[str, Field(description="Optional rule comment.")] = "",
        log: Annotated[str, Field(description="Log severity: 'emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug', 'nolog'.")] = "",
        pos: Annotated[int, Field(description="Rule sequence position (-1 to append at the end).")] = -1,
    ) -> str:
        """Create a cluster-level firewall rule.

        Use when enforcing global network access control rules across the cluster.
        To delete a rule position, use delete_cluster_firewall_rule.

        Args:
            action: 'ACCEPT', 'DROP', 'REJECT'.
            type: 'in', 'out', 'group'.
            enable: 1 = enabled, 0 = disabled.
            source: Source address/range (CIDR or alias).
            dest: Destination address/range.
            proto: Protocol (tcp, udp, icmp, etc.).
            sport: Source port(s).
            dport: Destination port(s).
            iface: Network interface.
            macro: Use predefined macro (e.g. 'SSH', 'HTTP', 'HTTPS', 'Ping').
            comment: Description.
            log: Log level: 'emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug', 'nolog'.
            pos: Rule position (-1 = append).
        """
        params: dict = {"action": action, "type": type, "enable": enable}
        for key, val in [
            ("source", source),
            ("dest", dest),
            ("proto", proto),
            ("sport", sport),
            ("dport", dport),
            ("iface", iface),
            ("macro", macro),
            ("comment", comment),
            ("log", log),
        ]:
            if val:
                params[key] = val
        if pos >= 0:
            params["pos"] = pos
        return format_response(api_request("post", "/cluster/firewall/rules", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_cluster_firewall_rule(
        pos: Annotated[int, Field(description="Rule sequence index to update.")],
        action: Annotated[str, Field(description="Updated action: 'ACCEPT', 'DROP', 'REJECT'.")] = "",
        enable: Annotated[int, Field(description="1 to enable, 0 to disable, -1 to leave unchanged.")] = -1,
        source: Annotated[str, Field(description="Updated source CIDR or alias.")] = "",
        dest: Annotated[str, Field(description="Updated destination CIDR or alias.")] = "",
        proto: Annotated[str, Field(description="Updated protocol.")] = "",
        sport: Annotated[str, Field(description="Updated source port(s).")] = "",
        dport: Annotated[str, Field(description="Updated destination port(s).")] = "",
        macro: Annotated[str, Field(description="Updated predefined macro.")] = "",
        comment: Annotated[str, Field(description="Updated description.")] = "",
        moveto: Annotated[int, Field(description="Move rule to new position index (-1 to leave position unchanged).")] = -1,
        delete: Annotated[str, Field(description="Comma-separated properties to delete from rule.")] = "",
    ) -> str:
        """Update or re-order an existing cluster-level firewall rule.

        Use when modifying ports, sources, or rule ordering in cluster firewall tables.

        Args:
            pos: Rule position to update.
            action: 'ACCEPT', 'DROP', 'REJECT'.
            enable: 1 = enabled, 0 = disabled, -1 = don't change.
            source: Source address/range.
            dest: Destination address/range.
            proto: Protocol.
            sport: Source port(s).
            dport: Destination port(s).
            macro: Predefined macro.
            comment: Description.
            moveto: Move rule to this position.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if action:
            params["action"] = action
        if enable >= 0:
            params["enable"] = enable
        for key, val in [
            ("source", source),
            ("dest", dest),
            ("proto", proto),
            ("sport", sport),
            ("dport", dport),
            ("macro", macro),
            ("comment", comment),
            ("delete", delete),
        ]:
            if val:
                params[key] = val
        if moveto >= 0:
            params["moveto"] = moveto
        return format_response(api_request("put", f"/cluster/firewall/rules/{pos}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_cluster_firewall_rule(
        pos: Annotated[int, Field(description="Rule sequence index to delete.")],
    ) -> str:
        """Delete a cluster-level firewall rule at specified position index.

        Use when removing obsolete cluster network filtering rules.

        Args:
            pos: Rule position to delete.
        """
        return format_response(api_request("delete", f"/cluster/firewall/rules/{pos}"))

    # ── Cluster Firewall Groups (Security Groups) ─────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_firewall_groups() -> str:
        """List all defined firewall security groups (reusable sets of firewall rules).

        Use when inspecting security groups reusable across VMs and containers.
        To view rules inside a specific group, use get_firewall_group_rules instead.
        """
        return format_response(api_request("get", "/cluster/firewall/groups"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_firewall_group_rules(
        group: Annotated[str, Field(description="Security group name.")],
    ) -> str:
        """List rules contained within a firewall security group.

        Use when reviewing rules assigned to a security group.

        Args:
            group: Security group name.
        """
        return format_response(api_request("get", f"/cluster/firewall/groups/{group}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_firewall_group(
        group: Annotated[str, Field(description="Unique security group name.")],
        comment: Annotated[str, Field(description="Optional description.")] = "",
    ) -> str:
        """Create a new firewall security group container.

        Use when defining reusable sets of firewall rules for application tiers.

        Args:
            group: Group name.
            comment: Description.
        """
        params: dict = {"group": group}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/firewall/groups", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_firewall_group_rule(
        group: Annotated[str, Field(description="Target security group name.")],
        action: Annotated[str, Field(description="Action: 'ACCEPT', 'DROP', 'REJECT'.")],
        type: Annotated[str, Field(description="Direction: 'in' or 'out'.")],
        enable: Annotated[int, Field(description="1 to enable rule, 0 to disable.")] = 1,
        source: Annotated[str, Field(description="Source address/range.")] = "",
        dest: Annotated[str, Field(description="Destination address/range.")] = "",
        proto: Annotated[str, Field(description="Transport protocol.")] = "",
        sport: Annotated[str, Field(description="Source port(s).")] = "",
        dport: Annotated[str, Field(description="Destination port(s).")] = "",
        macro: Annotated[str, Field(description="Predefined macro name.")] = "",
        comment: Annotated[str, Field(description="Optional rule description.")] = "",
    ) -> str:
        """Add a new firewall rule to an existing security group.

        Use when defining rules within a security group template.

        Args:
            group: Security group name.
            action: 'ACCEPT', 'DROP', 'REJECT'.
            type: 'in', 'out'.
            enable: 1 = enabled, 0 = disabled.
            source: Source address/range.
            dest: Destination address/range.
            proto: Protocol.
            sport: Source port(s).
            dport: Destination port(s).
            macro: Predefined macro.
            comment: Description.
        """
        params: dict = {"action": action, "type": type, "enable": enable}
        for key, val in [
            ("source", source),
            ("dest", dest),
            ("proto", proto),
            ("sport", sport),
            ("dport", dport),
            ("macro", macro),
            ("comment", comment),
        ]:
            if val:
                params[key] = val
        return format_response(api_request("post", f"/cluster/firewall/groups/{group}", **params))

    # ── Cluster Firewall Aliases & IPSets ─────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_firewall_aliases() -> str:
        """List cluster firewall IP aliases (symbolic names for IP addresses or CIDR ranges).

        Use when inspecting named network definitions.
        To create an alias, use create_firewall_alias instead.
        """
        return format_response(api_request("get", "/cluster/firewall/aliases"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_firewall_alias(
        name: Annotated[str, Field(description="Unique alias name.")],
        cidr: Annotated[str, Field(description="IP address or subnet CIDR (e.g., '10.0.0.0/24' or '192.168.1.1').")],
        comment: Annotated[str, Field(description="Optional comment.")] = "",
    ) -> str:
        """Create a cluster firewall IP alias for easy referencing in firewall rules.

        Use when defining human-readable labels for IP subnets or hosts.
        To delete an alias, use delete_firewall_alias.

        Args:
            name: Alias name.
            cidr: IP address or CIDR (e.g. '10.0.0.0/24' or '192.168.1.1').
            comment: Description.
        """
        params: dict = {"name": name, "cidr": cidr}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/firewall/aliases", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_firewall_alias(
        name: Annotated[str, Field(description="Alias name to delete.")],
    ) -> str:
        """Delete a cluster firewall IP alias.

        Use when removing obsolete named IP aliases.

        Args:
            name: Alias name.
        """
        return format_response(api_request("delete", f"/cluster/firewall/aliases/{name}"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_firewall_ipsets() -> str:
        """List cluster firewall IP sets (collections of IP subnets/addresses).

        Use when inspecting IP set groupings.
        To view entries in an IP set, use list_firewall_ipset_entries instead.
        """
        return format_response(api_request("get", "/cluster/firewall/ipset"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_firewall_ipset(
        name: Annotated[str, Field(description="Unique IP set name.")],
        comment: Annotated[str, Field(description="Optional description.")] = "",
    ) -> str:
        """Create a new firewall IP set container.

        Use when creating groups of IP addresses for bulk firewall matching.

        Args:
            name: IP set name.
            comment: Description.
        """
        params: dict = {"name": name}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/firewall/ipset", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_firewall_ipset_entries(
        name: Annotated[str, Field(description="IP set name.")],
    ) -> str:
        """List IP addresses and subnets contained in an IP set.

        Use when inspecting member IP ranges inside an IP set.

        Args:
            name: IP set name.
        """
        return format_response(api_request("get", f"/cluster/firewall/ipset/{name}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def add_firewall_ipset_entry(
        name: Annotated[str, Field(description="Target IP set name.")],
        cidr: Annotated[str, Field(description="IP address or CIDR range to add.")],
        comment: Annotated[str, Field(description="Optional comment.")] = "",
        nomatch: Annotated[bool, Field(description="If True, exclude this entry from matching.")] = False,
    ) -> str:
        """Add an IP address or CIDR range to an IP set.

        Use when populating IP sets with allowed or blocked subnets.

        Args:
            name: IP set name.
            cidr: IP address or CIDR.
            comment: Description.
            nomatch: Exclude this entry (nomatch).
        """
        params: dict = {"cidr": cidr}
        if comment:
            params["comment"] = comment
        if nomatch:
            params["nomatch"] = 1
        return format_response(api_request("post", f"/cluster/firewall/ipset/{name}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_firewall_ipset_entry(
        name: Annotated[str, Field(description="IP set name.")],
        cidr: Annotated[str, Field(description="IP address or CIDR range to remove.")],
    ) -> str:
        """Remove an IP address or CIDR range from an IP set.

        Use when removing IP entries from an IP set.

        Args:
            name: IP set name.
            cidr: IP address or CIDR to remove.
        """
        return format_response(api_request("delete", f"/cluster/firewall/ipset/{name}/{cidr}"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_firewall_macros() -> str:
        """List built-in Proxmox firewall macros (predefined rule templates like SSH, HTTP, MySQL).

        Use when discovering system macros to simplify rule creation.
        """
        return format_response(api_request("get", "/cluster/firewall/macros"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_firewall_refs() -> str:
        """Get all available firewall references (aliases, IP sets, macros) valid in rule parameters.

        Use when validating reference names prior to building complex firewall rules.
        """
        return format_response(api_request("get", "/cluster/firewall/refs"))

    # ── Node Firewall ─────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_firewall_options(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """Get host node firewall settings (enable status, log levels, conntrack max).

        Use when inspecting host-level firewall enforcement options.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/firewall/options"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def set_node_firewall_options(
        node: Annotated[str, Field(description="PVE host node name.")],
        enable: Annotated[int, Field(description="1 to enable firewall on node, 0 to disable, -1 to leave unchanged.")] = -1,
        log_level_in: Annotated[str, Field(description="Input log level ('emerg', 'notice', 'info', etc.).")] = "",
        log_level_out: Annotated[str, Field(description="Output log level.")] = "",
        ndp: Annotated[int, Field(description="1 to enable IPv6 NDP, 0 to disable, -1 to leave unchanged.")] = -1,
        nf_conntrack_max: Annotated[int, Field(description="Max conntrack table entries (0 to leave unchanged).")] = 0,
        delete: Annotated[str, Field(description="Comma-separated options to delete.")] = "",
    ) -> str:
        """Configure node firewall options, logging levels, and kernel conntrack limits.

        Use when adjusting host-specific firewall settings.

        Args:
            node: The node name.
            enable: 1 = enable, 0 = disable, -1 = don't change.
            log_level_in: Input log level.
            log_level_out: Output log level.
            ndp: 1 = enable NDP, 0 = disable, -1 = don't change.
            nf_conntrack_max: Max conntrack entries (0 = don't change).
            delete: Comma-separated options to delete.
        """
        params: dict = {}
        if enable >= 0:
            params["enable"] = enable
        if log_level_in:
            params["log_level_in"] = log_level_in
        if log_level_out:
            params["log_level_out"] = log_level_out
        if ndp >= 0:
            params["ndp"] = ndp
        if nf_conntrack_max:
            params["nf_conntrack_max"] = nf_conntrack_max
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/nodes/{node}/firewall/options", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_node_firewall_rules(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List firewall rules specific to a host node.

        Use when inspecting host-level ingress/egress filtering rules.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/firewall/rules"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_firewall_log(
        node: Annotated[str, Field(description="PVE host node name.")],
        limit: Annotated[int, Field(description="Max log lines to return.")] = 50,
    ) -> str:
        """Read recent firewall drop/accept logs for a host node.

        Use when diagnosing blocked network traffic on a host node.

        Args:
            node: The node name.
            limit: Max entries.
        """
        return format_response(api_request("get", f"/nodes/{node}/firewall/log", limit=limit))

    # ── VM/Container Firewall ─────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_firewall_options(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
    ) -> str:
        """Get firewall options for a specific QEMU virtual machine (enable, DHCP, IP filter, MAC filter).

        Use when auditing VM network security options.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/firewall/options"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def set_vm_firewall_options(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        enable: Annotated[int, Field(description="1 to enable VM firewall, 0 to disable, -1 to leave unchanged.")] = -1,
        dhcp: Annotated[int, Field(description="1 to enable DHCP filter, 0 to disable, -1 to leave unchanged.")] = -1,
        ipfilter: Annotated[int, Field(description="1 to enable IP anti-spoofing filter, 0 to disable.")] = -1,
        macfilter: Annotated[int, Field(description="1 to enable MAC anti-spoofing filter, 0 to disable.")] = -1,
        policy_in: Annotated[str, Field(description="Default input policy ('ACCEPT', 'REJECT', 'DROP').")] = "",
        policy_out: Annotated[str, Field(description="Default output policy.")] = "",
        delete: Annotated[str, Field(description="Comma-separated options to delete.")] = "",
    ) -> str:
        """Set firewall options, anti-spoofing filters, and default policies for a virtual machine.

        Use when enabling VM firewalling or configuring IP/MAC spoofing protections.

        Args:
            node: The node name.
            vmid: The VM ID.
            enable: 1 = enable, 0 = disable.
            dhcp: 1 = enable DHCP.
            ipfilter: 1 = enable IP filter.
            macfilter: 1 = enable MAC filter.
            policy_in: Input policy.
            policy_out: Output policy.
            delete: Comma-separated options to delete.
        """
        params: dict = {}
        if enable >= 0:
            params["enable"] = enable
        if dhcp >= 0:
            params["dhcp"] = dhcp
        if ipfilter >= 0:
            params["ipfilter"] = ipfilter
        if macfilter >= 0:
            params["macfilter"] = macfilter
        if policy_in:
            params["policy_in"] = policy_in
        if policy_out:
            params["policy_out"] = policy_out
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/firewall/options", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_vm_firewall_rules(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
    ) -> str:
        """List firewall rules configured for a QEMU virtual machine.

        Use when auditing network ingress/egress rules for a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/firewall/rules"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_vm_firewall_rule(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        action: Annotated[str, Field(description="Action: 'ACCEPT', 'DROP', or 'REJECT'.")],
        type: Annotated[str, Field(description="Rule type: 'in', 'out', or 'group'.")],
        enable: Annotated[int, Field(description="1 to enable rule, 0 to disable.")] = 1,
        source: Annotated[str, Field(description="Source address (CIDR, IP, or alias).")] = "",
        dest: Annotated[str, Field(description="Destination address (CIDR, IP, or alias).")] = "",
        proto: Annotated[str, Field(description="Transport protocol (e.g., 'tcp', 'udp').")] = "",
        dport: Annotated[str, Field(description="Destination port(s) (e.g., '80', '443').")] = "",
        macro: Annotated[str, Field(description="Predefined macro name.")] = "",
        comment: Annotated[str, Field(description="Optional comment.")] = "",
    ) -> str:
        """Create a firewall rule for a QEMU virtual machine.

        Use when granting or restricting network access to a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            action: 'ACCEPT', 'DROP', 'REJECT'.
            type: 'in', 'out', 'group'.
            enable: 1 = enabled, 0 = disabled.
            source: Source CIDR or alias.
            dest: Destination CIDR or alias.
            proto: Protocol.
            dport: Destination port(s).
            macro: Predefined macro.
            comment: Description.
        """
        params: dict = {"action": action, "type": type, "enable": enable}
        for key, val in [
            ("source", source),
            ("dest", dest),
            ("proto", proto),
            ("dport", dport),
            ("macro", macro),
            ("comment", comment),
        ]:
            if val:
                params[key] = val
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/firewall/rules", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_container_firewall_options(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
    ) -> str:
        """Get firewall options for an LXC container.

        Use when inspecting container firewall settings.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/firewall/options"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_container_firewall_rules(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
    ) -> str:
        """List firewall rules for an LXC container.

        Use when auditing container firewall rules.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/firewall/rules"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_container_firewall_rule(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
        action: Annotated[str, Field(description="Action: 'ACCEPT', 'DROP', or 'REJECT'.")],
        type: Annotated[str, Field(description="Rule type: 'in', 'out', or 'group'.")],
        enable: Annotated[int, Field(description="1 to enable rule, 0 to disable.")] = 1,
        source: Annotated[str, Field(description="Source address (CIDR, IP, or alias).")] = "",
        dest: Annotated[str, Field(description="Destination address (CIDR, IP, or alias).")] = "",
        proto: Annotated[str, Field(description="Transport protocol.")] = "",
        dport: Annotated[str, Field(description="Destination port(s).")] = "",
        macro: Annotated[str, Field(description="Predefined macro name.")] = "",
        comment: Annotated[str, Field(description="Optional comment.")] = "",
    ) -> str:
        """Create a firewall rule for an LXC container.

        Use when enforcing network access controls on a container.

        Args:
            node: The node name.
            vmid: The container ID.
            action: 'ACCEPT', 'DROP', 'REJECT'.
            type: 'in', 'out', 'group'.
            enable: 1 = enabled, 0 = disabled.
            source: Source CIDR or alias.
            dest: Destination CIDR or alias.
            proto: Protocol.
            dport: Destination port(s).
            macro: Predefined macro.
            comment: Description.
        """
        params: dict = {"action": action, "type": type, "enable": enable}
        for key, val in [
            ("source", source),
            ("dest", dest),
            ("proto", proto),
            ("dport", dport),
            ("macro", macro),
            ("comment", comment),
        ]:
            if val:
                params[key] = val
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/firewall/rules", **params))
