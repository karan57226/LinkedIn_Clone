#!/usr/bin/env python3
"""Dispatch the deployment script through SSM and wait for its real result."""
import base64
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

REGION = "us-west-1"
INSTANCES = {"frontend": "i-00bf665dad7167928", "backend": "i-0255cb08c63d77f5c"}


def aws(*args):
    return json.loads(subprocess.check_output(
        ["aws", "--region", REGION, "--output", "json", *args], text=True))


def dispatch(service, action, tag):
    source = base64.b64encode(Path(__file__).with_name("deploy_container.py").read_bytes()).decode()
    image = "488709146192.dkr.ecr.us-west-1.amazonaws.com/linkedin/" + service + ":" + tag
    args = ["flock", "-w", "30", "/var/lock/linkedin-deploy.lock", "python3", "-", action, service, image]
    # The payload contains code only, no database settings or credentials.
    command = "set -eu\nprintf '%s' " + shlex.quote(source) + " | base64 --decode | " + shlex.join(args)
    result = aws("ssm", "send-command", "--instance-ids", INSTANCES[service],
                 "--document-name", "AWS-RunShellScript", "--timeout-seconds", "120",
                 "--parameters", json.dumps({"commands": [command], "executionTimeout": ["900"]}),
                 "--comment", "LinkedIn " + action + " " + service)
    command_id = result["Command"]["CommandId"]
    print(service + ": SSM command " + command_id, flush=True)
    deadline = time.monotonic() + 1050
    while time.monotonic() < deadline:
        time.sleep(5)
        response = subprocess.run(
            ["aws", "--region", REGION, "--output", "json", "ssm", "get-command-invocation",
             "--command-id", command_id, "--instance-id", INSTANCES[service]],
            text=True, capture_output=True)
        if response.returncode:
            if "InvocationDoesNotExist" in response.stderr:
                continue
            raise RuntimeError("Could not read SSM result: " + response.stderr)
        invocation = json.loads(response.stdout)
        if invocation["Status"] in ("Pending", "InProgress", "Delayed", "Cancelling"):
            continue
        print(invocation.get("StandardOutputContent", ""))
        print(invocation.get("StandardErrorContent", ""), file=sys.stderr)
        if invocation["Status"] != "Success" or invocation["ResponseCode"] != 0:
            raise RuntimeError(service + ": SSM deployment " + invocation["Status"])
        return
    raise RuntimeError("SSM result timed out. Check command " + command_id + " before retrying.")


if __name__ == "__main__":
    dispatch(sys.argv[1], sys.argv[2], os.environ.get("GITHUB_SHA", "unused"))
