"""Offline package guardrails; no image builds, provider calls or credentials."""

from pathlib import Path
import re
import shutil
import subprocess

import pytest


PACKAGE = Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary"


@pytest.mark.parametrize("name", ["launch_pod.sh", "terminate_pod.sh"])
def test_legacy_shell_has_only_fail_closed_migration_commands(name):
    text = (PACKAGE / name).read_text(encoding="utf-8")
    # Quotes are explanatory messages, never shell commands or substitutions.
    assert "$(" not in text and "`" not in text
    lines = [line.strip() for line in text.splitlines()
             if line.strip() and not line.lstrip().startswith(("#", "'"))]
    assert lines == ["set -euo pipefail", "printf '%s\\n' " + chr(92), "exit 1"]


@pytest.mark.parametrize("name", ["launch_pod.sh", "terminate_pod.sh"])
def test_legacy_stubs_refuse_at_runtime(name, tmp_path):
    bash = shutil.which("bash")
    if bash is None or __import__("sys").platform != "linux":
        pytest.skip("Linux bash runtime; static fail-closed checks run everywhere")
    result = subprocess.run([bash, str(PACKAGE / name)], cwd=tmp_path,
                            env={"PATH": "/usr/bin:/bin"}, capture_output=True, timeout=5)
    assert result.returncode == 1 and result.stdout == b""
    assert b"DISABLED" in result.stderr and b"age_controller.py" in result.stderr


def test_docker_context_is_an_explicit_payload_only_allowlist():
    lines = [line.strip() for line in (PACKAGE / ".dockerignore").read_text().splitlines()
             if line.strip() and not line.startswith("#")]
    assert lines[0] == "*"
    included = {line[1:] for line in lines[1:]}
    assert all(line.startswith("!") for line in lines[1:])
    assert included == {"Dockerfile", ".dockerignore", "aeth01_cpu_oracle.py",
                        "aeth01_gpu_kernel.py", "run_canary.py", "pod_service.py", "watchdog.sh"}
    assert all((PACKAGE / name).is_file() for name in included)
    assert "age_controller.py" not in included and "runpod_api.py" not in included


def test_build_requires_explicit_tag_and_amd64_and_no_launch():
    text = (PACKAGE / "build_and_push.sh").read_text()
    assert "${IMAGE_TAG:?" in text and "${REGISTRY:?" in text
    assert "docker build --platform linux/amd64" in text
    assert "docker push" in text and "@sha256" in text
    assert not re.search(r"^\s*(runpodctl|python[0-9]*|curl|wget) ", text, re.MULTILINE)


def test_linux_payload_files_are_lf_with_checkout_attributes():
    attrs = (PACKAGE / ".gitattributes").read_text()
    for glob in ("*.py", "*.sh", "*.json", "Dockerfile"):
        assert glob + " text eol=lf" in attrs
        for path in PACKAGE.glob(glob):
            assert b"\r" not in path.read_bytes(), path.name