"""Offline package guardrails; no image builds, provider calls or credentials."""

import importlib.util
import json
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


def test_image_manifest_covers_runtime_critical_files_and_is_current():
    spec = importlib.util.spec_from_file_location("_image_manifest_test",
                                                   PACKAGE / "image_manifest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = module.build_manifest()
    # Every file actually shipped in the docker build context is covered,
    # plus pod_service.py and the controller-facing receipt schema (section
    # 9's "not only CPU oracle/GPU kernel/canary runner").
    docker_payload = {"aeth01_cpu_oracle.py", "aeth01_gpu_kernel.py",
                      "run_canary.py", "pod_service.py", "watchdog.sh"}
    assert docker_payload <= set(manifest["file_hashes_sha256"])
    assert {"pod_service.py", "receipt_schema.json", "Dockerfile"} <= set(
        manifest["file_hashes_sha256"])
    committed = json.loads((PACKAGE / "image_manifest.json").read_text())
    assert committed["file_hashes_sha256"] == manifest["file_hashes_sha256"]
    # Never claim build-verified identity that has not actually been checked.
    assert manifest["immutable_image_digest"] is None
    assert manifest["pinned_dependencies_build_verified"] is False


def test_linux_payload_files_are_lf_with_checkout_attributes():
    attrs = (PACKAGE / ".gitattributes").read_text()
    for glob in ("*.py", "*.sh", "*.json", "Dockerfile"):
        assert glob + " text eol=lf" in attrs
        for path in PACKAGE.glob(glob):
            assert b"\r" not in path.read_bytes(), path.name


def test_cleanup_operator_contract_matches_shared_policy_and_restart_requirements():
    text = (PACKAGE / "README.md").read_text()
    for phrase in ("CLEANUP_EVIDENCE_MODEL.md", "cleanup_evidence.py",
                   "Controller state schema 3 and reaper schema 2",
                   "KNOWN_OWNED_CLEANUP", "RECONCILIATION_WINDOW", "OPERATIONAL_CLEANUP",
                   "at least 361 healthy scans", "window credit does not",
                   "Repeated short", "CANNOT accumulate", "NOT that a scheduler is running"):
        assert phrase in text
    assert "Evidence accumulates across invocations" not in text
    for phrase in ("LIST_AND_KNOWN_GET_V1", "GET for every known reaper ID",
                   "post-window local seal", "run_dir=original_directory",
                   "authoritative_local_state=False", "Charge-reconciliation completion",
                   "forced-cleanup start/deadline", "cleanup_aeth01_oracle.py"):
        assert phrase in text