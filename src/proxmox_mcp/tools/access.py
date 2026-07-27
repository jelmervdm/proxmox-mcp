"""Access management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register access/authentication management tools."""

    # ── Users ─────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_users(
        enabled: Annotated[bool, Field(description="If True, only return enabled accounts.")] = False,
        full: Annotated[bool, Field(description="If True, include full group membership and token details.")] = True,
    ) -> str:
        """List user accounts configured in Proxmox access control.

        Use when reviewing registered cluster user accounts and active statuses.
        To inspect details for a specific user, use get_user instead.

        Args:
            enabled: Only show enabled users.
            full: Include detailed info (groups, tokens, etc.).
        """
        params: dict = {"full": int(full)}
        if enabled:
            params["enabled"] = 1
        return format_response(api_request("get", "/access/users", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_user(
        userid: Annotated[str, Field(description="User ID formatted as 'user@realm' (e.g., 'admin@pam' or 'john@pve').")],
    ) -> str:
        """Get user details, contact info, group memberships, and account expiration.

        Use when checking specific user privileges, group associations, or expiration dates.
        To list all users, use list_users instead.

        Args:
            userid: User ID (format: 'user@realm', e.g. 'admin@pam').
        """
        return format_response(api_request("get", f"/access/users/{userid}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_user(
        userid: Annotated[str, Field(description="User ID in 'user@realm' format (e.g., 'deploy@pve').")],
        password: Annotated[str, Field(description="Password (required for pve/pam realms).")] = "",
        email: Annotated[str, Field(description="User contact email address.")] = "",
        firstname: Annotated[str, Field(description="User first name.")] = "",
        lastname: Annotated[str, Field(description="User last name.")] = "",
        groups: Annotated[str, Field(description="Comma-separated group names.")] = "",
        comment: Annotated[str, Field(description="Optional comment or description.")] = "",
        enable: Annotated[bool, Field(description="If True, enable the account immediately.")] = True,
        expire: Annotated[int, Field(description="Account expiration timestamp (Unix epoch, 0 = never).")] = 0,
    ) -> str:
        """Create a new Proxmox user account.

        Use when provisioning local PVE or PAM authentication users.
        To delete a user account, use delete_user instead.

        Args:
            userid: User ID (format: 'user@realm', e.g. 'myuser@pve').
            password: Password (only for pve/pam realms).
            email: Email address.
            firstname: First name.
            lastname: Last name.
            groups: Comma-separated group list.
            comment: Description.
            enable: Enable user.
            expire: Account expiration (Unix epoch, 0 = never).
        """
        params: dict = {"userid": userid}
        if password:
            params["password"] = password
        for key, val in [
            ("email", email),
            ("firstname", firstname),
            ("lastname", lastname),
            ("groups", groups),
            ("comment", comment),
        ]:
            if val:
                params[key] = val
        if not enable:
            params["enable"] = 0
        if expire:
            params["expire"] = expire
        return format_response(api_request("post", "/access/users", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_user(
        userid: Annotated[str, Field(description="Target user ID ('user@realm').")],
        email: Annotated[str, Field(description="Updated email address.")] = "",
        firstname: Annotated[str, Field(description="Updated first name.")] = "",
        lastname: Annotated[str, Field(description="Updated last name.")] = "",
        groups: Annotated[str, Field(description="Comma-separated group names.")] = "",
        comment: Annotated[str, Field(description="Updated description.")] = "",
        enable: Annotated[bool, Field(description="Enable or disable the account.")] = True,
        expire: Annotated[int, Field(description="Account expiration epoch (-1 to leave unchanged).")] = -1,
        append: Annotated[bool, Field(description="If True, append groups instead of replacing.")] = False,
    ) -> str:
        """Update properties, groups, or account state of an existing user.

        Use when modifying user contact details, group memberships, or enabling/disabling access.

        Args:
            userid: User ID (format: 'user@realm').
            email: Email address.
            firstname: First name.
            lastname: Last name.
            groups: Comma-separated group list.
            comment: Description.
            enable: Enable/disable user.
            expire: Account expiration (Unix epoch, 0 = never, -1 = don't change).
            append: Append groups instead of replacing.
        """
        params: dict = {}
        for key, val in [
            ("email", email),
            ("firstname", firstname),
            ("lastname", lastname),
            ("groups", groups),
            ("comment", comment),
        ]:
            if val:
                params[key] = val
        if not enable:
            params["enable"] = 0
        if expire >= 0:
            params["expire"] = expire
        if append:
            params["append"] = 1
        return format_response(api_request("put", f"/access/users/{userid}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_user(
        userid: Annotated[str, Field(description="User ID ('user@realm') to delete.")],
    ) -> str:
        """Delete a user account and remove associated API tokens.

        Use when revoking user access permanently.

        Args:
            userid: User ID to delete (format: 'user@realm').
        """
        return format_response(api_request("delete", f"/access/users/{userid}"))

    # ── API Tokens ────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_user_tokens(
        userid: Annotated[str, Field(description="User ID ('user@realm').")],
    ) -> str:
        """List all API tokens created for a user.

        Use when auditing API key/token issuance for automated scripts.
        To view specific token configuration, use get_user_token instead.

        Args:
            userid: User ID (format: 'user@realm').
        """
        return format_response(api_request("get", f"/access/users/{userid}/token"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_user_token(
        userid: Annotated[str, Field(description="User ID ('user@realm').")],
        tokenid: Annotated[str, Field(description="Token ID (alphanumeric name).")],
    ) -> str:
        """Get details and privilege separation settings for an API token.

        Use when inspecting token expiration or privilege isolation settings.

        Args:
            userid: User ID (format: 'user@realm').
            tokenid: Token ID.
        """
        return format_response(api_request("get", f"/access/users/{userid}/token/{tokenid}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_user_token(
        userid: Annotated[str, Field(description="User ID ('user@realm') owner of the token.")],
        tokenid: Annotated[str, Field(description="Unique alphanumeric token name.")],
        comment: Annotated[str, Field(description="Optional token description.")] = "",
        privsep: Annotated[bool, Field(description="If True, enable privilege separation (token uses separate ACLs).")] = True,
        expire: Annotated[int, Field(description="Token expiration epoch (0 = never).")] = 0,
    ) -> str:
        """Create a new API token for automated API access. Returns the secret token value.

        Use when issuing credentials for automated CI/CD or API integration scripts.
        To revoke an API token, use delete_user_token.

        Args:
            userid: User ID (format: 'user@realm').
            tokenid: Token ID (alphanumeric).
            comment: Token description.
            privsep: Enable privilege separation (token has own permissions, not user's full permissions).
            expire: Expiration (Unix epoch, 0 = never).
        """
        params: dict = {}
        if comment:
            params["comment"] = comment
        if not privsep:
            params["privsep"] = 0
        if expire:
            params["expire"] = expire
        return format_response(api_request("post", f"/access/users/{userid}/token/{tokenid}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_user_token(
        userid: Annotated[str, Field(description="User ID ('user@realm').")],
        tokenid: Annotated[str, Field(description="Token ID to delete.")],
    ) -> str:
        """Delete an API token.

        Use when revoking an API key or script credential.

        Args:
            userid: User ID (format: 'user@realm').
            tokenid: Token ID.
        """
        return format_response(api_request("delete", f"/access/users/{userid}/token/{tokenid}"))

    # ── Groups ────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_groups() -> str:
        """List all user groups configured on the cluster.

        Use when inspecting organizational group definitions.
        To view specific group members and comments, use get_group instead.
        """
        return format_response(api_request("get", "/access/groups"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_group(
        groupid: Annotated[str, Field(description="Group ID.")],
    ) -> str:
        """Get details and comment for a specific group.

        Use when inspecting group settings.

        Args:
            groupid: Group ID.
        """
        return format_response(api_request("get", f"/access/groups/{groupid}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_group(
        groupid: Annotated[str, Field(description="Group name/ID to create.")],
        comment: Annotated[str, Field(description="Optional group description.")] = "",
    ) -> str:
        """Create a new user group for permission aggregation.

        Use when creating permission containers for users.
        To delete a group, use delete_group instead.

        Args:
            groupid: Group ID.
            comment: Description.
        """
        params: dict = {"groupid": groupid}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/access/groups", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_group(
        groupid: Annotated[str, Field(description="Group ID to update.")],
        comment: Annotated[str, Field(description="Updated description.")] = "",
    ) -> str:
        """Update description comment for a group.

        Use when updating metadata for a user group.

        Args:
            groupid: Group ID.
            comment: Description.
        """
        params: dict = {}
        if comment:
            params["comment"] = comment
        return format_response(api_request("put", f"/access/groups/{groupid}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_group(
        groupid: Annotated[str, Field(description="Group ID to delete.")],
    ) -> str:
        """Delete a user group.

        Use when removing obsolete groups.

        Args:
            groupid: Group ID.
        """
        return format_response(api_request("delete", f"/access/groups/{groupid}"))

    # ── Roles ─────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_roles() -> str:
        """List all RBAC roles (built-in and custom) configured on the cluster.

        Use when reviewing privilege packages available for assignment.
        To view specific privileges assigned to a role, use get_role instead.
        """
        return format_response(api_request("get", "/access/roles"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_role(
        roleid: Annotated[str, Field(description="Role ID (e.g., 'PVEAdmin', 'PVEVMUser', 'CustomRole').")],
    ) -> str:
        """Get privilege list assigned to a specific role.

        Use when checking exact permission flags for a role.

        Args:
            roleid: Role ID.
        """
        return format_response(api_request("get", f"/access/roles/{roleid}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_role(
        roleid: Annotated[str, Field(description="Unique custom role identifier.")],
        privs: Annotated[
            str,
            Field(description="Comma-separated privilege list (e.g., 'VM.Allocate,VM.Config.Disk,VM.PowerMgmt')."),
        ],
    ) -> str:
        """Create a custom RBAC role with defined fine-grained privileges.

        Use when creating custom permission roles for least-privilege access.
        To delete a custom role, use delete_role.

        Args:
            roleid: Role ID.
            privs: Comma-separated list of privileges (e.g. 'VM.Allocate,VM.Config.Disk,VM.PowerMgmt').
        """
        return format_response(api_request("post", "/access/roles", roleid=roleid, privs=privs))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_role(
        roleid: Annotated[str, Field(description="Role ID to update.")],
        privs: Annotated[str, Field(description="Comma-separated privilege list.")],
        append: Annotated[bool, Field(description="If True, append privileges instead of replacing.")] = False,
    ) -> str:
        """Update privileges assigned to a custom role.

        Use when extending or modifying privileges in custom roles.

        Args:
            roleid: Role ID.
            privs: Comma-separated list of privileges.
            append: Append privileges instead of replacing.
        """
        params: dict = {"privs": privs}
        if append:
            params["append"] = 1
        return format_response(api_request("put", f"/access/roles/{roleid}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_role(
        roleid: Annotated[str, Field(description="Custom role ID to delete.")],
    ) -> str:
        """Delete a custom role.

        Use when removing obsolete custom RBAC roles.

        Args:
            roleid: Role ID.
        """
        return format_response(api_request("delete", f"/access/roles/{roleid}"))

    # ── ACL (Access Control Lists) ────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_acl() -> str:
        """Get full cluster Access Control List (ACL) permission assignments.

        Use when inspecting path permissions assigned to users, groups, or API tokens.
        To modify access control assignments, use update_acl instead.
        """
        return format_response(api_request("get", "/access/acl"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_acl(
        path: Annotated[str, Field(description="Object path (e.g., '/', '/vms/100', '/storage/local', '/pool/mypool').")],
        roles: Annotated[str, Field(description="Comma-separated role IDs (e.g., 'PVEVMAdmin').")],
        users: Annotated[str, Field(description="Comma-separated user IDs ('user@realm').")] = "",
        groups: Annotated[str, Field(description="Comma-separated group IDs.")] = "",
        tokens: Annotated[str, Field(description="Comma-separated token IDs ('user@realm!tokenid').")] = "",
        propagate: Annotated[bool, Field(description="If True, propagate permissions down object hierarchy.")] = True,
        delete: Annotated[bool, Field(description="If True, remove the matching ACL entry.")] = False,
    ) -> str:
        """Add or remove ACL permission assignments on paths for users, groups, or tokens.

        Use when granting or revoking roles on Proxmox resource paths.

        Args:
            path: Object path (e.g. '/', '/vms/100', '/storage/local', '/pool/mypool').
            roles: Comma-separated role list.
            users: Comma-separated user list (format: 'user@realm').
            groups: Comma-separated group list.
            tokens: Comma-separated token list (format: 'user@realm!tokenid').
            propagate: Propagate permissions to child objects.
            delete: Remove the ACL entry instead of adding.
        """
        params: dict = {"path": path, "roles": roles}
        if users:
            params["users"] = users
        if groups:
            params["groups"] = groups
        if tokens:
            params["tokens"] = tokens
        if not propagate:
            params["propagate"] = 0
        if delete:
            params["delete"] = 1
        return format_response(api_request("put", "/access/acl", **params))

    # ── Auth Domains / Realms ─────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_auth_domains() -> str:
        """List configured authentication realms (PAM, PVE, LDAP, Active Directory, OpenID).

        Use when auditing cluster authentication backends.
        To view configuration for a specific realm, use get_auth_domain instead.
        """
        return format_response(api_request("get", "/access/domains"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_auth_domain(
        realm: Annotated[str, Field(description="Realm ID (e.g., 'pam', 'pve', 'my-ldap').")],
    ) -> str:
        """Get configuration properties for an authentication realm.

        Use when checking LDAP/AD base DN, server URLs, or OpenID client settings.

        Args:
            realm: Realm ID (e.g. 'pam', 'pve', 'my-ldap').
        """
        return format_response(api_request("get", f"/access/domains/{realm}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def sync_auth_domain(
        realm: Annotated[str, Field(description="Realm ID to synchronize.")],
        dry_run: Annotated[bool, Field(description="If True, only simulate sync without modifying users.")] = False,
        full: Annotated[bool, Field(description="If True, perform full sync instead of incremental.")] = False,
        enable_new: Annotated[bool, Field(description="If True, enable newly synchronized accounts.")] = True,
        remove_vanished: Annotated[str, Field(description="Comma-separated options for deleted directory objects ('entry', 'properties', 'acl').")] = "",
    ) -> str:
        """Synchronize users and groups from an external LDAP or Active Directory domain.

        Use when triggering user sync from directory services.

        Args:
            realm: Realm ID to sync.
            dry_run: Only show what would change.
            full: Full sync (not just incremental).
            enable_new: Enable newly synced users.
            remove_vanished: Comma-separated: 'entry' (remove users), 'properties' (clear), 'acl' (remove ACLs).
        """
        params: dict = {}
        if dry_run:
            params["dry-run"] = 1
        if full:
            params["full"] = 1
        if not enable_new:
            params["enable-new"] = 0
        if remove_vanished:
            params["remove-vanished"] = remove_vanished
        return format_response(api_request("post", f"/access/domains/{realm}/sync", **params))

    # ── TFA (Two-Factor Authentication) ───────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_tfa(
        userid: Annotated[str, Field(description="Optional user ID ('user@realm') filter. Empty string returns all users.")] = "",
    ) -> str:
        """List configured Two-Factor Authentication (TOTP, WebAuthn, Recovery Keys) entries.

        Use when auditing 2FA enforcement and enrolled keys for users.

        Args:
            userid: Filter by user ID (empty = all users).
        """
        if userid:
            return format_response(api_request("get", f"/access/tfa/{userid}"))
        return format_response(api_request("get", "/access/tfa"))

    # ── Permissions ───────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_permissions(
        userid: Annotated[str, Field(description="Target user ID to test (empty string tests authenticated API user).")] = "",
        path: Annotated[str, Field(description="Proxmox object path to evaluate (empty string tests root '/').")] = "",
    ) -> str:
        """Evaluate effective permissions for a user on a given Proxmox object path.

        Use when testing privilege calculations and ACL propagation.

        Args:
            userid: User to check (empty = current user).
            path: Object path to check (empty = root).
        """
        params: dict = {}
        if userid:
            params["userid"] = userid
        if path:
            params["path"] = path
        return format_response(api_request("get", "/access/permissions", **params))

    # ── Password ──────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def change_password(
        userid: Annotated[str, Field(description="User ID ('user@realm').")],
        password: Annotated[str, Field(description="New password.")],
    ) -> str:
        """Change password for a user on a local realm (PVE or PAM).

        Use when updating user authentication passwords.

        Args:
            userid: User ID (format: 'user@realm').
            password: New password.
        """
        return format_response(api_request("put", "/access/password", userid=userid, password=password))
