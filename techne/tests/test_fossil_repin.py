"""`harvest repin`: repair a record whose hash list was taken over a CRLF-converted and/or
build-dirtied body, from the byte-exact fetch rematerialize kept aside (2026-09-16; 11 of 121
records on M1 were of this kind).

Positive   a record with CRLF hashes + one residue file, origin serving LF -> rematerialize says
           DRIFT; repin REPINS: new list == fetch, old list kept as superseded-*, record carries
           hashes_superseded with reason + receipt, body installed, verify True.
Cheat      origin content REALLY differs (one line edited) under the same CRLF costume -> repin
           REFUSES (OTHER > 0); record, hash list, and the kept fetch are untouched.
Cheat 2    the fetch has a file the record lacks (ADDED) -> REFUSED.
Refusals   no upstream.drifted/ -> REFUSED; upstream/ already present -> REFUSED.
Nothing    a drift with no CRLF/residue explanation -> REFUSED ("nothing to repair").
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib
import tarfile

import pytest

from techne.fossils import harvest, record, vault

LF = b"int main(void) {\n  return 0;\n}\n"
CRLF = LF.replace(b"\n", b"\r\n")


def _tar_bytes(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for name, data in files.items():
            ti = tarfile.TarInfo(name); ti.size = len(data); ti.mtime = 0
            t.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


def _hash_list_lines(rows):
    return rows


@pytest.fixture
def m1_record(tmp_path, monkeypatch):
    """The origin serves LF bytes; the RECORD (as M1 wrote it) hashes a CRLF checkout of the
    same archive PLUS a build product. No archive sha256 pin (older records had none)."""
    monkeypatch.setenv("TECHNE_FOSSIL_VAULT", str(tmp_path / "vault"))
    monkeypatch.setattr(vault, "SPECIMENS", tmp_path / "specimens")
    origin = tmp_path / "origin"; origin.mkdir()
    archive = _tar_bytes({"x-1990/main.c": LF, "x-1990/README": b"readme\n"})
    (origin / "x.tar.gz").write_bytes(archive)
    sid = "synthetic-crlf-1990"
    # what M1's dirty checkout looked like: CRLF text + a .o that a build left behind
    dirty = tmp_path / "m1" / sid / "upstream"
    (dirty / "tree" / "x-1990").mkdir(parents=True)
    (dirty / "x.tar.gz").write_bytes(archive)
    (dirty / "tree" / "x-1990" / "main.c").write_bytes(CRLF)
    (dirty / "tree" / "x-1990" / "README").write_bytes(b"readme\r\n")
    (dirty / "tree" / "x-1990" / "main.o").write_bytes(b"\x7fELF residue")
    rows = vault.hash_tree(dirty)
    vault.write_hashes(sid, rows)
    rec = record.skeleton(sid, canonical_name="x", lineage="x", era="1990",
                          human_capability_summary={"built_to": "x", "pressure": "y", "success_means": "z"})
    rec["source_origin"] = {"artifacts": [{"kind": "url", "url": (origin / "x.tar.gz").as_uri(), "filename": "x.tar.gz"}]}
    rec["hashes"] = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows), "artifacts": [{"filename": "x.tar.gz"}]}
    record.save(rec)
    return {"sid": sid, "origin": origin, "old_tree": rec["hashes"]["tree_sha256"]}


def _tracked(sid):
    return {p.name: p.read_bytes() for p in vault.specimen_dir(sid).rglob("*") if p.is_file()}


def test_positive_crlf_and_residue_record_is_repinned(m1_record):
    sid = m1_record["sid"]
    r = harvest.rematerialize(sid)
    assert r["status"] == "DRIFT" and r["removed"] == ["tree/x-1990/main.o"]
    before = _tracked(sid)
    out = harvest.repin(sid, reason="test: record hashed a CRLF checkout with a .o in it")
    assert out["status"] == "REPINNED", out
    assert out["class_counts"] == {"SAME": 1, "RECORD_IS_CRLF": 2, "NOT_IN_ORIGIN": 1, "FETCH_IS_CRLF": 0, "OTHER": 0, "ADDED": 0}
    assert out["tree_sha256_old"] == m1_record["old_tree"] and out["tree_sha256_new"] != out["tree_sha256_old"]
    # body installed and verifies against the NEW list
    assert (vault.body_dir(sid) / "upstream" / "tree" / "x-1990" / "main.c").read_bytes() == LF
    assert not (vault.body_dir(sid) / "upstream.drifted").exists()
    assert harvest.verify(sid) is True
    # the old list is kept, annotated, byte-for-byte below its header
    sup = [p for p in vault.specimen_dir(sid).glob("UPSTREAM_HASHES.superseded-*.txt")]
    assert len(sup) == 1
    assert sup[0].read_text(encoding="utf-8").split("\n", 1)[1] == before["UPSTREAM_HASHES.txt"].decode("utf-8")
    rec = record.load(sid)
    assert rec["hashes"]["tree_sha256"] == out["tree_sha256_new"] and rec["hashes"]["n_files"] == 3
    assert rec["hashes_superseded"][0]["tree_sha256"] == m1_record["old_tree"]
    assert rec["hashes_superseded"][0]["reason"].startswith("test:")
    assert rec["hashes_superseded"][0]["receipt"] == "techne/fossils/specimens/%s/receipts/%s.json" % (sid, out["receipt_id"])
    assert (vault.specimen_dir(sid) / "receipts" / (out["receipt_id"] + ".json")).exists()
    # a second rematerialize on a fresh host would now MATCH: the record is upstream bytes
    harvest._rmtree(vault.body_dir(sid) / "upstream")
    assert harvest.rematerialize(sid)["status"] == "MATCH"


def test_cheat_real_content_change_under_crlf_costume_is_refused(m1_record):
    sid = m1_record["sid"]
    edited = _tar_bytes({"x-1990/main.c": LF.replace(b"return 0", b"return 1"), "x-1990/README": b"readme\n"})
    (m1_record["origin"] / "x.tar.gz").write_bytes(edited)
    assert harvest.rematerialize(sid)["status"] == "DRIFT"
    before = _tracked(sid)
    out = harvest.repin(sid, reason="should refuse")
    assert out["status"] == "REFUSED", out
    assert out["class_counts"]["OTHER"] >= 1
    assert _tracked(sid) == before
    assert (vault.body_dir(sid) / "upstream.drifted").exists() and not (vault.body_dir(sid) / "upstream").exists()
    assert record.load(sid).get("hashes_superseded") is None


def test_cheat_added_file_in_fetch_is_refused(m1_record):
    sid = m1_record["sid"]
    bigger = _tar_bytes({"x-1990/main.c": LF, "x-1990/README": b"readme\n", "x-1990/NEW": b"new\n"})
    (m1_record["origin"] / "x.tar.gz").write_bytes(bigger)
    harvest.rematerialize(sid)
    out = harvest.repin(sid, reason="should refuse")
    assert out["status"] == "REFUSED" and out["class_counts"]["ADDED"] == 1


def test_refuses_without_a_kept_fetch_and_with_a_body_present(m1_record):
    sid = m1_record["sid"]
    assert harvest.repin(sid, reason="x")["status"] == "REFUSED"
    harvest.rematerialize(sid); harvest.repin(sid, reason="first")
    assert (vault.body_dir(sid) / "upstream").exists()
    assert harvest.repin(sid, reason="again")["status"] == "REFUSED"
