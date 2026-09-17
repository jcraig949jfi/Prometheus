"""TECHNE-101 (2026-09-17, found on M3): the native runner must execute the bash it PROVED works.

Before this, tests skipped on shutil.which("bash") (PATH order: Git's bash) while _shell launched
["bash", ...] through CreateProcess, which searches System32 BEFORE PATH -- so on a Windows host
without a WSL distro the process that ran was C:\\Windows\\System32\\bash.exe, the WSL launcher,
which prints "no installed distributions" and exits 1. On M1/M2 the two resolutions agreed only
because there the System32 bash IS a distro. Label ("a bash exists") versus capability ("this
bash runs the recipe"), one layer below the gcc-shim finding (base role, 2026-09-11).

Controls:
  positive   a real bash passes the probe and is returned as an absolute path
  cheat 1    a "bash" that exits 0 but never prints BASH_VERSION is refused (exit code is a label)
  cheat 2    a "bash" that prints the WSL launcher's text and exits 1 is refused
  ordering   [cheat, real] -> real: the probe decides, not the position
  refusal    run() with no capable shell -> BLOCKED_PLATFORM / NATIVE_SHELL_UNAVAILABLE, NOT
             persisted to the record (a host fact is never written as a specimen fact)
"""
from __future__ import annotations

import json
import os
import pathlib
import stat

import pytest

from techne.fossils import harvest, record, vault

HELLO = b"hello from 1987\n"


def _fake_bash(tmp_path: pathlib.Path, name: str, stdout_text: str, exit_code: int) -> str:
    """An executable that answers the probe with `stdout_text` and `exit_code`."""
    if os.name == "nt":
        p = tmp_path / (name + ".cmd")
        body = "@echo off\r\n"
        if stdout_text:
            body += "echo %s\r\n" % stdout_text
        body += "exit /b %d\r\n" % exit_code
        p.write_text(body, encoding="ascii")
    else:
        p = tmp_path / name
        body = "#!/bin/sh\n"
        if stdout_text:
            body += "printf '%%s\\n' '%s'\n" % stdout_text
        body += "exit %d\n" % exit_code
        p.write_text(body, encoding="ascii")
        p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return str(p)


def test_probe_positive_real_bash_is_capable_and_absolute():
    sh = harvest.native_shell(refresh=True)
    if sh is None:
        pytest.skip("no capable bash on this host (the refusal path is tested below)")
    assert sh["capable"] is True
    assert sh["bash_version"]
    assert pathlib.Path(sh["path"]).is_absolute() and pathlib.Path(sh["path"]).is_file()


def test_cheat_exit_zero_without_bash_version_is_refused(tmp_path):
    fake = _fake_bash(tmp_path, "bash", "not a bash at all", 0)
    pr = harvest.probe_native_shell(fake)
    assert pr["exit"] == 0 and pr["capable"] is False and pr["bash_version"] is None
    assert harvest.native_shell(candidates=[fake]) is None


def test_cheat_wsl_launcher_text_is_refused(tmp_path):
    fake = _fake_bash(tmp_path, "bash", "Windows Subsystem for Linux has no installed distributions.", 1)
    pr = harvest.probe_native_shell(fake)
    assert pr["capable"] is False
    assert harvest.native_shell(candidates=[fake]) is None


def test_ordering_the_probe_decides_not_the_position(tmp_path):
    real = harvest.native_shell(refresh=True)
    if real is None:
        pytest.skip("no capable bash on this host")
    fake = _fake_bash(tmp_path, "bash", "", 0)
    chosen = harvest.native_shell(candidates=[fake, real["path"]])
    assert chosen is not None
    assert os.path.normcase(chosen["path"]) == os.path.normcase(real["path"])
    assert [p["path"] for p in chosen["probes"]][0] == fake      # the refused one is on the record


def test_candidates_are_absolute_existing_files_and_deduplicated():
    c = harvest.native_shell_candidates()
    assert all(pathlib.Path(p).is_absolute() and pathlib.Path(p).is_file() for p in c)
    assert len({os.path.normcase(os.path.abspath(p)) for p in c}) == len(c)


def _synthetic_specimen(tmp_path, monkeypatch, sid="synthetic-shell-1987"):
    monkeypatch.setenv("TECHNE_FOSSIL_VAULT", str(tmp_path / "vault"))
    monkeypatch.setattr(vault, "SPECIMENS", tmp_path / "specimens")
    up = vault.body_dir(sid) / "upstream"
    (up / "tree").mkdir(parents=True)
    (up / "tree" / "hello.txt").write_bytes(HELLO)
    rows = vault.hash_tree(up)
    vault.write_hashes(sid, rows)
    rec = record.skeleton(sid, canonical_name="synthetic", lineage="synthetic", era="1987",
                          human_capability_summary={"built_to": "x", "pressure": "y", "success_means": "z"})
    rec["hashes"] = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows)}
    record.save(rec)
    (vault.specimen_dir(sid) / "recipe.json").write_text(json.dumps(
        {"runner": "native", "workdir": "upstream/tree", "build": [],
         "runs": [{"name": "read", "cmd": "cat hello.txt", "expect": {"exit": 0, "stdout_contains": ["hello"]}}],
         "classification_if_ok": "RUNNABLE_NATIVE", "test_kind": "TECHNE"}), encoding="utf-8")
    return sid


def test_refusal_run_without_capable_shell_is_blocked_platform_and_not_persisted(tmp_path, monkeypatch):
    sid = _synthetic_specimen(tmp_path, monkeypatch)
    before = json.dumps(record.load(sid), sort_keys=True)
    monkeypatch.setattr(harvest, "native_shell", lambda *a, **k: None)
    r = harvest.run(sid, timeout=60)
    assert r["ok"] is False
    assert r["classification"] == "BLOCKED_PLATFORM"
    assert r["blocked_reason"] == "NATIVE_SHELL_UNAVAILABLE"
    assert r["persisted"] is False
    assert r["build"] == [] and r["runs"] == [] and r["tests"] == []      # nothing was attempted
    assert json.dumps(record.load(sid), sort_keys=True) == before          # the record is untouched
    assert not list((vault.specimen_dir(sid) / "receipts").glob("run-*.json")) if (vault.specimen_dir(sid) / "receipts").exists() else True


def test_receipt_records_the_shell_that_ran(tmp_path, monkeypatch):
    if harvest.native_shell(refresh=True) is None:
        pytest.skip("no capable bash on this host")
    sid = _synthetic_specimen(tmp_path, monkeypatch)
    r = harvest.run(sid, timeout=60)
    assert r["ok"] is True, r["runs"]
    assert r["native_shell"]["capable"] is True
    assert pathlib.Path(r["native_shell"]["path"]).is_absolute()
    assert r["native_shell"]["bash_version"]
