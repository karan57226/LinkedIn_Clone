import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("deploy", Path(__file__).parents[1] / "scripts/deploy_container.py")
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.commands = []
        self.containers = {"backend": "old"}
        self.current = {
            "Mounts": [], "Image": "old", "State": {"Running": True},
            "Config": {"Env": ["APP_ENV=aws", "DATABASE_URL=postgresql+psycopg://secret"]},
            "HostConfig": {"NetworkMode": "default", "PortBindings": {
                "8000/tcp": [{"HostPort": "8000", "HostIp": ""}]}}
        }

    def command(self, *args):
        self.commands.append(args)
        if args[:3] == ("docker", "ps", "-a"):
            return "\n".join(self.containers)
        if args[:2] == ("docker", "rename"):
            self.containers[args[3]] = self.containers.pop(args[2])
        if args[:2] == ("docker", "rm"):
            self.containers.pop(args[-1])
        if args[:2] == ("docker", "run"):
            self.containers["backend"] = "new"
        return ""

    def exercise(self, check):
        with patch.object(deploy, "inspect", side_effect=lambda name: {"Id": "new"} if ":" in name else self.current), \
             patch.object(deploy, "run", side_effect=self.command), \
             patch.object(deploy, "healthy", return_value=True), \
             patch.object(deploy, "wait_healthy", side_effect=check), \
             patch.object(deploy.subprocess, "run"):
            deploy.deploy("backend", "registry/backend:commit")

    def test_success_retains_previous_container(self):
        self.exercise([None])
        self.assertEqual(self.containers, {"backend": "new", "backend-previous": "old"})

    def test_failed_health_restores_previous_and_fails_release(self):
        with self.assertRaisesRegex(RuntimeError, "previous container restored"):
            self.exercise([RuntimeError("unhealthy"), None])
        self.assertEqual(self.containers, {"backend": "old"})

    def test_mounts_block_deployment_before_changes(self):
        self.current["Mounts"] = [{"Type": "volume"}]
        with self.assertRaisesRegex(RuntimeError, "Mounted storage"):
            self.exercise([])
        self.assertEqual(self.commands, [])

    def test_sqlite_blocks_replacement(self):
        self.current["Config"]["Env"] = ["DATABASE_URL=sqlite:///./dev.db"]
        with self.assertRaisesRegex(RuntimeError, "PostgreSQL"):
            self.exercise([])
        self.assertEqual(self.commands, [])

    def test_manual_rollback_keeps_current_as_backup(self):
        self.containers["backend-previous"] = "older"
        with patch.object(deploy, "inspect", return_value=self.current), \
             patch.object(deploy, "run", side_effect=self.command), \
             patch.object(deploy, "wait_healthy"):
            deploy.rollback("backend")
        self.assertEqual(self.containers, {"backend": "older", "backend-previous": "old"})


if __name__ == "__main__":
    unittest.main()
