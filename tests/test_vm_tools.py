"""Tests for QEMU VM and LXC container tools."""

from proxmox_mcp.client import api_request


class TestQemuTools:
    def test_list_vms(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.get.return_value = [
            {"vmid": 100, "name": "webserver", "status": "running"},
            {"vmid": 101, "name": "database", "status": "stopped"},
        ]
        result = api_request("get", "/nodes/pve1/qemu")
        assert len(result) == 2
        assert result[0]["vmid"] == 100

    def test_get_vm_status(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").status.current.get.return_value = {
            "status": "running",
            "cpu": 0.12,
            "mem": 2147483648,
        }
        result = api_request("get", "/nodes/pve1/qemu/100/status/current")
        assert result is not None

    def test_create_vm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.post.return_value = "UPID:pve1:00001234"
        api_request("post", "/nodes/pve1/qemu", vmid=102, name="test-vm", memory=4096, cores=2)
        mock_proxmox_client.nodes.pve1.qemu.post.assert_called_once_with(vmid=102, name="test-vm", memory=4096, cores=2)

    def test_start_vm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").status.start.post.return_value = "UPID:..."
        result = api_request("post", "/nodes/pve1/qemu/100/status/start")
        assert result is not None

    def test_delete_vm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").delete.return_value = "UPID:..."
        result = api_request("delete", "/nodes/pve1/qemu/100")
        assert result is not None

    def test_clone_vm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").clone.post.return_value = "UPID:..."
        result = api_request("post", "/nodes/pve1/qemu/100/clone", newid=200, name="clone-vm")
        assert result is not None

    def test_unlink_vm_disk(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").unlink.put.return_value = "UPID:..."
        result = api_request("put", "/nodes/pve1/qemu/100/unlink", idlist="scsi0,scsi1", force=1)
        assert result is not None
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").unlink.put.assert_called_once_with(idlist="scsi0,scsi1", force=1)

    def test_stop_vm_overrule_shutdown(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").status.stop.post.return_value = "UPID:..."
        params = {"overrule-shutdown": 1, "skiplock": 1}
        result = api_request("post", "/nodes/pve1/qemu/100/status/stop", **params)
        assert result is not None
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").status.stop.post.assert_called_once_with(**params)

    def test_rollback_vm_snapshot_start(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").snapshot.__getattr__("snap1").rollback.post.return_value = "UPID:..."
        result = api_request("post", "/nodes/pve1/qemu/100/snapshot/snap1/rollback", start=1)
        assert result is not None
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").snapshot.__getattr__("snap1").rollback.post.assert_called_once_with(start=1)


class TestLxcTools:
    def test_list_containers(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.lxc.get.return_value = [
            {"vmid": 200, "name": "ct-web", "status": "running"},
        ]
        result = api_request("get", "/nodes/pve1/lxc")
        assert len(result) == 1
        assert result[0]["name"] == "ct-web"

    def test_create_container(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.lxc.post.return_value = "UPID:pve1:..."
        api_request(
            "post",
            "/nodes/pve1/lxc",
            vmid=201,
            hostname="test-ct",
            ostemplate="local:vztmpl/debian-12.tar.zst",
            memory=512,
            cores=1,
        )
        mock_proxmox_client.nodes.pve1.lxc.post.assert_called_once()

    def test_delete_container(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.lxc.__getattr__("200").delete.return_value = "UPID:..."
        result = api_request("delete", "/nodes/pve1/lxc/200")
        assert result is not None


class TestVmAgentExec:
    def test_vm_agent_exec_command_splitting_and_list(self, mock_proxmox_client):
        from mcp.server.fastmcp import FastMCP
        from proxmox_mcp.tools import qemu

        server = FastMCP("test")
        qemu.register(server)
        tool = server._tool_manager._tools["vm_agent_exec"]

        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").agent.exec.post.return_value = {"pid": 1234}

        # Test string command splitting
        res = tool.fn(node="pve1", vmid=100, command="uname -a")
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").agent.exec.post.assert_called_with(command=["uname", "-a"])
        assert "1234" in res

        # Test list command pass-through
        tool.fn(node="pve1", vmid=100, command=["echo", "test"])
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").agent.exec.post.assert_called_with(command=["echo", "test"])
