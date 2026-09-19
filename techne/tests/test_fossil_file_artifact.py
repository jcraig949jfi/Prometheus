"""Artifact kind 'file' (2026-09-19, directive 5 s6): a local hashed file becomes part of a body.
positive: copied and pinned; cheat: a pin that does not match the file is REFUSED and nothing is written;
negative: a missing source is a FileNotFoundError, not a silent skip."""
from __future__ import annotations

import hashlib
import pathlib

import pytest

from techne.fossils import harvest


def test_file_artifact_positive_copies_and_pins(tmp_path):
    src = tmp_path / "S9_1.npy"; src.write_bytes(b"\x93NUMPY fake bytes")
    up = tmp_path / "body" / "upstream"; body = tmp_path / "body"
    art = {"kind": "file", "source_path": str(src), "filename": "S9_1.npy"}
    fetched = harvest._fetch_artifacts([art], up, body)
    assert (up / "S9_1.npy").read_bytes() == src.read_bytes()
    assert art["sha256"] == hashlib.sha256(src.read_bytes()).hexdigest() and art["bytes"] == len(src.read_bytes())
    assert fetched[0]["sha256"] == art["sha256"]


def test_file_artifact_cheat_wrong_pin_is_refused(tmp_path):
    src = tmp_path / "x.npy"; src.write_bytes(b"real")
    up = tmp_path / "body" / "upstream"
    art = {"kind": "file", "source_path": str(src), "filename": "x.npy", "sha256": "0" * 64}
    with pytest.raises(RuntimeError, match="sha256 mismatch"):
        harvest._fetch_artifacts([art], up, tmp_path / "body")
    assert not (up / "x.npy").exists()


def test_file_artifact_missing_source_is_an_error(tmp_path):
    art = {"kind": "file", "source_path": str(tmp_path / "nope.npy"), "filename": "nope.npy"}
    with pytest.raises(FileNotFoundError):
        harvest._fetch_artifacts([art], tmp_path / "up", tmp_path)
