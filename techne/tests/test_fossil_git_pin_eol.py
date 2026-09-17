"""vault.git_pin must give upstream BYTES whatever the host's core.autocrlf says (2026-09-16).

Found on M2 (global core.autocrlf=true) by `harvest rematerialize`: lapack-reference's pin is
not the default HEAD, so after the byte-exact clone the pin's checkout re-smudged the 70 files
that differ from HEAD to CRLF, while the index and the record held LF. The -c flags were bound
to `git clone` only.

Cheat control   with the host config forced to autocrlf=true, pinning a NON-HEAD commit whose
                files differ from HEAD yields LF bytes and a tree hash equal to a clone made
                with autocrlf=false (the defect would make them differ).
Positive        pinning HEAD itself was always LF; still is.
Persisted       the clone's own config says autocrlf=false, eol=lf, so any later git
                operation in it is byte-exact too.
"""
from __future__ import annotations

import pathlib
import subprocess

import pytest

from techne.fossils import vault

pytestmark = pytest.mark.skipif(subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
                                reason="needs git")

LF_TEXT_V1 = b"line one\nline two\n"
LF_TEXT_V2 = b"line one\nline two\nline three\n"


def _git(cwd, *args):
    return subprocess.run(["git", "-c", "core.autocrlf=false", *args], cwd=str(cwd), check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def upstream(tmp_path):
    """A bare 'origin' with two commits; the older one is the pin."""
    work = tmp_path / "work"
    work.mkdir()
    _git(work, "init", "-q", "-b", "main")
    _git(work, "config", "user.email", "t@t")
    _git(work, "config", "user.name", "t")
    (work / "a.txt").write_bytes(LF_TEXT_V1)
    (work / "b.txt").write_bytes(LF_TEXT_V1)
    _git(work, "add", "."); _git(work, "commit", "-q", "-m", "v1")
    v1 = _git(work, "rev-parse", "HEAD")
    (work / "a.txt").write_bytes(LF_TEXT_V2)
    _git(work, "add", "."); _git(work, "commit", "-q", "-m", "v2")
    bare = tmp_path / "origin.git"
    _git(tmp_path, "clone", "-q", "--bare", str(work), str(bare))
    return {"url": bare.as_uri(), "v1": v1, "v2": _git(work, "rev-parse", "HEAD")}


@pytest.fixture
def host_autocrlf_true(tmp_path, monkeypatch):
    cfg = tmp_path / "hostgitconfig"
    cfg.write_text("[core]\n\tautocrlf = true\n", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", str(tmp_path / "nosystem"))
    return cfg


def test_cheat_non_head_pin_under_autocrlf_true_is_byte_exact(upstream, host_autocrlf_true, tmp_path):
    dest = tmp_path / "pinned"
    g = vault.git_pin(upstream["url"], upstream["v1"], dest)
    assert g["commit"] == upstream["v1"]
    # a.txt is the file that DIFFERS from HEAD: the one the defect smudged
    assert (dest / "a.txt").read_bytes() == LF_TEXT_V1
    assert (dest / "b.txt").read_bytes() == LF_TEXT_V1
    assert b"\r" not in (dest / "a.txt").read_bytes()


def test_tree_hash_is_host_independent(upstream, tmp_path, monkeypatch):
    # reference: pinned with the host saying autocrlf=false
    cfg_false = tmp_path / "cfg_false"
    cfg_false.write_text("[core]\n\tautocrlf = false\n", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", str(tmp_path / "nosystem"))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg_false))
    vault.git_pin(upstream["url"], upstream["v1"], tmp_path / "ref")
    ref = vault.tree_hash_of(vault.hash_tree(tmp_path / "ref"))
    cfg_true = tmp_path / "cfg_true"
    cfg_true.write_text("[core]\n\tautocrlf = true\n", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg_true))
    vault.git_pin(upstream["url"], upstream["v1"], tmp_path / "host_true")
    assert vault.tree_hash_of(vault.hash_tree(tmp_path / "host_true")) == ref


def test_positive_head_pin_is_lf(upstream, host_autocrlf_true, tmp_path):
    dest = tmp_path / "head"
    vault.git_pin(upstream["url"], upstream["v2"], dest)
    assert (dest / "a.txt").read_bytes() == LF_TEXT_V2


def test_clone_config_is_persisted(upstream, host_autocrlf_true, tmp_path):
    dest = tmp_path / "persist"
    vault.git_pin(upstream["url"], upstream["v1"], dest)
    assert subprocess.run(["git", "-C", str(dest), "config", "--local", "core.autocrlf"],
                          capture_output=True, text=True).stdout.strip() == "false"
    assert subprocess.run(["git", "-C", str(dest), "config", "--local", "core.eol"],
                          capture_output=True, text=True).stdout.strip() == "lf"
