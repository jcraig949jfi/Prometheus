"""techne.fossils.worlds: the world-rebuild census and the probe comparison, with controls.
Docker-dependent tests skip where docker is not reachable through WSL.

Cheat (build)     a Dockerfile asking for a package that does not exist -> BUILD_FAILED with the
                  apt error in error_tail; the census cannot report a failed build as BUILT.
Positive (build)  a trivial Dockerfile builds; the package manifest hash is a sha256 and is
                  IDENTICAL across two builds from the same base (the manifest measures the
                  image, not the build's clock).
Cheat (probe)     a receipt whose probe stdout claims a toolchain the image does not have ->
                  PROBE_DIFFERS naming the command; the same command's real output -> IDENTICAL.
Pure              _norm, _receipt_probe_text (truncated receipts are NOT comparable), the
                  recorded-worlds reference has 8 rows with Dockerfiles that exist.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from techne.fossils import vault, worlds

DOCKER = worlds.docker_available()
needs_docker = pytest.mark.skipif(not DOCKER, reason="docker not reachable through WSL on this host")


def test_recorded_worlds_reference_is_present_and_dockerfiles_exist():
    ws = worlds.recorded_worlds()
    assert len(ws) == 8
    for w in ws:
        assert (vault.REPO / w["dockerfile"]).exists(), w["dockerfile"]
        assert w["image_id"].startswith("sha256:")


def test_truncated_receipt_probe_is_not_comparable():
    assert worlds._receipt_probe_text({"stdout": {"head": "x", "tail": "y", "truncated": True}}) is None
    assert worlds._receipt_probe_text({"stdout": {"text": "gcc 12"}}) == "gcc 12"
    assert worlds._norm("a \r\n b  \n") == "a\n b"


@needs_docker
def test_cheat_nonexistent_package_is_build_failed(tmp_path):
    df = tmp_path / "bad.Dockerfile"
    df.write_text("FROM debian:bookworm-slim\nRUN apt-get update && apt-get install -y no-such-package-xyz-123\n", encoding="utf-8")
    row = _build_from(df, "prometheus-fossil-test-bad:ctl")
    assert row["status"] == "BUILD_FAILED", row
    assert "no-such-package-xyz-123" in (row["error_tail"] or "")
    assert row["image_id_rebuilt"] is None


def _build_from(df: pathlib.Path, tag: str):
    # build_world resolves dockerfile relative to the repo; point it at an absolute path instead
    row = {"image": tag, "dockerfile": str(df), "image_id": "sha256:000000000000"}
    orig = vault.REPO
    try:
        worlds.vault.REPO = pathlib.Path("/")  # so REPO / absolute == absolute
        return worlds.build_world(row, timeout=900)
    finally:
        worlds.vault.REPO = orig


@needs_docker
def test_positive_trivial_world_builds_and_manifest_is_stable(tmp_path):
    df = tmp_path / "ok.Dockerfile"
    df.write_text("FROM debian:bookworm-slim\nRUN true\n", encoding="utf-8")
    a = _build_from(df, "prometheus-fossil-test-ok:ctl")
    assert a["status"] == "BUILT" and a["image_id_rebuilt"].startswith("sha256:") and a["same_image_id"] is False
    assert len(a["package_manifest_sha256"]) == 64 and a["n_packages"] > 50
    b = _build_from(df, "prometheus-fossil-test-ok:ctl")
    assert b["package_manifest_sha256"] == a["package_manifest_sha256"]


@needs_docker
def test_probe_compare_cheat_and_positive(tmp_path, monkeypatch):
    monkeypatch.setenv("TECHNE_FOSSIL_VAULT", str(tmp_path / "vault"))
    monkeypatch.setattr(vault, "SPECIMENS", tmp_path / "specimens")
    sid = "synthetic-probe"
    (vault.body_dir(sid) / "upstream" / "tree").mkdir(parents=True)
    sd = vault.specimen_dir(sid); (sd / "receipts").mkdir(parents=True)
    (sd / "recipe.json").write_text(json.dumps({"runner": "docker", "image": "debian:bookworm-slim", "workdir": "upstream/tree",
                                               "probe": ["cat /etc/os-release | head -1"]}), encoding="utf-8")
    real = worlds.harvest._shell("docker", "cat /etc/os-release | head -1", vault.body_dir(sid), "upstream/tree", "debian:bookworm-slim", 120, readonly=True)["stdout"]
    assert "Debian" in real

    def receipt(text, name):
        (sd / "receipts" / name).write_text(json.dumps({"schema": "techne.fossil.run_receipt/1", "runner": "docker",
                                                        "probe": [{"cmd": "cat /etc/os-release | head -1", "exit": 0, "stdout": {"text": text}}]}), encoding="utf-8")

    receipt('PRETTY_NAME="Windows 3.1"', "run-synthetic-probe-20260101T000000Z.json")
    r = worlds.probe_compare_one(sid)
    assert r["status"] == "PROBE_DIFFERS" and r["differs"][0]["cmd"].startswith("cat /etc")
    receipt(real, "run-synthetic-probe-20260102T000000Z.json")   # newer receipt, real output
    r = worlds.probe_compare_one(sid)
    assert r["status"] == "PROBE_IDENTICAL" and r["identical"] == 1
