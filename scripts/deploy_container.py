#!/usr/bin/env python3
"""Run as root on EC2. Never print container environment values."""
import json
import subprocess
import sys
import time
import urllib.request


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE)


def inspect(name):
    return json.loads(run("docker", "inspect", name))[0]


def healthy(service):
    paths = ["http://127.0.0.1/"] if service == "frontend" else [
        "http://127.0.0.1:8000/health", "http://127.0.0.1:8000/api/feed"
    ]
    try:
        for url in paths:
            with urllib.request.urlopen(url, timeout=5) as response:
                body = response.read()
                if service == "backend":
                    data = json.loads(body)
                    if url.endswith("/health") and data.get("status") != "ok":
                        return False
                    if url.endswith("/api/feed") and not isinstance(data, list):
                        return False
        return True
    except Exception:
        return False


def wait_healthy(service):
    for _ in range(20):
        if inspect(service)["State"]["Running"] and healthy(service):
            return
        time.sleep(3)
    raise RuntimeError("Container health check failed")


def deploy(service, image):
    port = "80" if service == "frontend" else "8000"
    previous = service + "-previous"
    current = inspect(service)
    if current["Mounts"]:
        raise RuntimeError("Mounted storage requires a reviewed deployment configuration")
    bindings = current["HostConfig"]["PortBindings"]
    if set(bindings) != {port + "/tcp"} or any(
        item["HostPort"] != port or item["HostIp"] not in ("", "0.0.0.0", "::")
        for item in bindings[port + "/tcp"]
    ):
        raise RuntimeError("Unexpected port configuration")
    if current["HostConfig"]["NetworkMode"] not in ("default", "bridge"):
        raise RuntimeError("Custom Docker network requires a reviewed deployment configuration")
    if not current["State"]["Running"] or not healthy(service):
        raise RuntimeError("Existing container must be healthy before deployment")
    env = dict(item.split("=", 1) for item in current["Config"]["Env"])
    if service == "backend" and not env.get("DATABASE_URL", "").startswith(("postgresql://", "postgresql+psycopg://")):
        raise RuntimeError("Expected external PostgreSQL; refusing to risk local database loss")
    # Pull and verify before stopping the live container.
    registry = image.split("/", 1)[0]
    password = run("aws", "ecr", "get-login-password", "--region", "us-west-1")
    subprocess.run(["docker", "login", "--username", "AWS", "--password-stdin", registry],
                   input=password, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    run("docker", "pull", image)
    image_id = inspect(image)["Id"]
    if current["Image"] == image_id:
        print(service + ": already running requested image")
        return
    names = run("docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
    if previous in names:
        run("docker", "rm", previous)  # Refuses to remove a running container.
    run("docker", "rename", service, previous)
    try:
        run("docker", "stop", "--time", "30", previous)
        run("docker", "update", "--restart=no", previous)
        # Use a private temporary file, never expose settings in logs or arguments.
        settings = {key: env[key] for key in ("APP_ENV", "DATABASE_URL", "FRONTEND_ORIGIN") if key in env}
        if any("\n" in value or "\r" in value for value in settings.values()):
            raise RuntimeError("Multiline environment values are unsupported")
        import os
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", prefix="linkedin-env-") as config:
            os.chmod(config.name, 0o600)
            config.write("".join(key + "=" + value + "\n" for key, value in settings.items()))
            config.flush()
            run("docker", "run", "-d", "--name", service, "--restart", "always",
                "-p", port + ":" + port, "--env-file", config.name, image)
        wait_healthy(service)
    except Exception:
        names = run("docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
        if service in names:
            run("docker", "rm", "-f", service)
        run("docker", "rename", previous, service)
        run("docker", "update", "--restart=always", service)
        run("docker", "start", service)
        wait_healthy(service)
        raise RuntimeError("Deployment failed; previous container restored") from None
    print(service + ": deployment healthy; previous container retained")


def rollback(service):
    previous = service + "-previous"
    inspect(previous)  # Fail before changing anything if no backup exists.
    failed = service + "-rollback-current"
    run("docker", "rename", service, failed)
    try:
        run("docker", "stop", "--time", "30", failed)
        run("docker", "update", "--restart=no", failed)
        run("docker", "rename", previous, service)
        run("docker", "update", "--restart=always", service)
        run("docker", "start", service)
        wait_healthy(service)
    except Exception:
        names = run("docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
        if service in names:
            run("docker", "stop", "--time", "30", service)
            run("docker", "update", "--restart=no", service)
            run("docker", "rename", service, previous)
        run("docker", "rename", failed, service)
        run("docker", "update", "--restart=always", service)
        run("docker", "start", service)
        raise RuntimeError("Rollback failed; original container restarted") from None
    run("docker", "rename", failed, previous)
    print(service + ": previous release restored and healthy")


if __name__ == "__main__":
    try:
        action, service = sys.argv[1:3]
        if service not in ("frontend", "backend"):
            raise ValueError("Unknown service")
        if action == "deploy":
            expected = "488709146192.dkr.ecr.us-west-1.amazonaws.com/linkedin/" + service + ":"
            if not sys.argv[3].startswith(expected):
                raise ValueError("Unexpected image repository")
            deploy(service, sys.argv[3])
        elif action == "rollback":
            rollback(service)
        else:
            raise ValueError("Unknown action")
    except Exception as error:
        # subprocess errors can contain sensitive arguments or output: don't print them.
        print("Deployment unsuccessful: " + (str(error) if isinstance(error, (RuntimeError, ValueError)) else type(error).__name__), file=sys.stderr)
        sys.exit(1)
