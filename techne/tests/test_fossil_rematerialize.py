"""`harvest rematerialize`: a second host brings a body back from its recorded origin and proves
it is the same body, touching nothing tracked (2026-09-16, SFE ecosystem moves to M2 where the
vault holds 0 of 121 bodies).

Positive control  an origin still serving the preserved bytes -> MATCH, upstream/ installed,
                  `harvest verify` True, record.json and UPSTREAM_HASHES.txt byte-identical.
Cheat control     an origin serving DIFFERENT bytes under the same name -> DRIFT, NOT installed
                  as upstream/ (kept at upstream.drifted/ for forensics), tracked files untouched.
                  A rematerialize that installed whatever the origin served today would be the
                  false "reconstructible" the guarantee is about.
Negative control  an origin that no longer exists -> ORIGIN_UNREACHABLE, nothing installed,
                  no staging residue.
Idempotence       a second call on a MATCHed body fetches nothing (ALREADY_PRESENT_VERIFIED).
Acquire unchanged acquire() through the shared _fetch_artifacts still writes the pins.
Origins are file:// URLs so no network is touched.
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib
import tarfile

import pytest

from techne.fossils import harvest, record, vault

HELLO = b"hello from 1987\n"


def _tar_bytes(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for name, data in files.items():
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            ti.mtime = 0
            t.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


@pytest.fixture
def world(tmp_path, monkeypatch):
    """An 'origin' directory served over file://, a tracked half, and an EMPTY vault --
    the M2 situation. The record is what a first acquisition on another host would have
    written: pins (archive sha256) and the hash list over archive + extracted tree."""
    monkeypatch.setenv("TECHNE_FOSSIL_VAULT", str(tmp_path / "vault"))
    monkeypatch.setattr(vault, "SPECIMENS", tmp_path / "specimens")
    origin_dir = tmp_path / "origin"
    origin_dir.mkdir()
    archive = _tar_bytes({"synthetic-1987/hello.txt": HELLO})
    (origin_dir / "synthetic.tar.gz").write_bytes(archive)
    sid = "synthetic-remat-1987"
    # simulate the first host's acquisition in a scratch vault, then throw the body away
    first = tmp_path / "first_host_vault" / sid / "upstream"
    (first).mkdir(parents=True)
    (first / "synthetic.tar.gz").write_bytes(archive)
    vault.extract(first / "synthetic.tar.gz", first / "tree")
    rows = vault.hash_tree(first)
    vault.write_hashes(sid, rows)
    rec = record.skeleton(sid, canonical_name="synthetic", lineage="synthetic", era="1987",
                          human_capability_summary={"built_to": "x", "pressure": "y", "success_means": "z"})
    rec["source_origin"] = {"artifacts": [{"kind": "url", "url": (origin_dir / "synthetic.tar.gz").as_uri(),
                                           "filename": "synthetic.tar.gz",
                                           "sha256": hashlib.sha256(archive).hexdigest()}]}
    rec["hashes"] = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows)}
    record.save(rec)
    return {"sid": sid, "origin": origin_dir, "archive": archive,
            "tracked": _snapshot(sid)}


def _snapshot(sid):
    d = vault.specimen_dir(sid)
    return {p.name: p.read_bytes() for p in d.iterdir() if p.is_file()}


def test_positive_origin_still_serves_the_body(world):
    sid = world["sid"]
    assert not (vault.body_dir(sid) / "upstream").exists()
    r = harvest.rematerialize(sid)
    assert r["status"] == "MATCH", r
    assert r["tree_sha256_fetched"] == r["tree_sha256_recorded"]
    assert (vault.body_dir(sid) / "upstream" / "tree" / "synthetic-1987" / "hello.txt").read_bytes() == HELLO
    assert harvest.verify(sid) is True
    assert not (vault.body_dir(sid) / "rematerialize.tmp").exists()
    assert _snapshot(sid) == world["tracked"], "tracked files must be byte-identical"


def test_idempotent_second_call_fetches_nothing(world):
    sid = world["sid"]
    harvest.rematerialize(sid)
    (world["origin"] / "synthetic.tar.gz").unlink()   # origin gone AFTER the body is here
    r = harvest.rematerialize(sid)
    assert r["status"] == "ALREADY_PRESENT_VERIFIED"
    assert harvest.verify(sid) is True


def test_cheat_origin_serves_different_bytes_is_drift_and_not_installed(world):
    sid = world["sid"]
    swapped = _tar_bytes({"synthetic-1987/hello.txt": b"hello from 2026, same filename\n"})
    (world["origin"] / "synthetic.tar.gz").write_bytes(swapped)
    r = harvest.rematerialize(sid)
    # the archive pin catches it first: the record's sha256 for the archive no longer matches
    assert r["status"] in ("DRIFT", "ORIGIN_UNREACHABLE"), r
    assert not (vault.body_dir(sid) / "upstream").exists(), "a drifted origin must not become the body"
    assert harvest.drift(sid)["body_present"] is False
    assert _snapshot(sid) == world["tracked"]


def test_cheat_tree_drift_below_the_archive_pin(world):
    """Same archive bytes recorded WITHOUT an archive pin (older records), tree differs ->
    the hash list, not the pin, must catch it, and the drifted tree is kept for forensics."""
    sid = world["sid"]
    rec = record.load(sid)
    rec["source_origin"]["artifacts"][0].pop("sha256")
    record.save(rec)
    tracked = _snapshot(sid)
    (world["origin"] / "synthetic.tar.gz").write_bytes(_tar_bytes({"synthetic-1987/hello.txt": b"edited\n"}))
    r = harvest.rematerialize(sid)
    assert r["status"] == "DRIFT", r
    assert r["modified"] == ["tree/synthetic-1987/hello.txt"] or "synthetic.tar.gz" in r["modified"]
    assert not (vault.body_dir(sid) / "upstream").exists()
    assert (vault.body_dir(sid) / "upstream.drifted" / "tree" / "synthetic-1987" / "hello.txt").read_bytes() == b"edited\n"
    assert _snapshot(sid) == tracked


def test_negative_origin_gone_is_unreachable_and_leaves_nothing(world):
    sid = world["sid"]
    (world["origin"] / "synthetic.tar.gz").unlink()
    r = harvest.rematerialize(sid)
    assert r["status"] == "ORIGIN_UNREACHABLE" and r["error"], r
    assert not (vault.body_dir(sid) / "upstream").exists()
    assert not (vault.body_dir(sid) / "rematerialize.tmp").exists()
    assert _snapshot(sid) == world["tracked"]


def test_no_origin_recorded(world):
    sid = world["sid"]
    rec = record.load(sid)
    rec["source_origin"]["artifacts"] = []
    record.save(rec)
    assert harvest.rematerialize(sid)["status"] == "NO_ORIGIN"


def test_census_writes_after_every_row_and_counts(world, tmp_path):
    out = tmp_path / "census.json"
    c = harvest.rematerialize_all(str(out))
    assert c["complete"] is True and c["counts"] == {"MATCH": 1}
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert on_disk["schema"] == harvest.REMAT_SCHEMA and on_disk["rows"][0]["status"] == "MATCH"


def test_acquire_still_writes_pins_through_the_shared_fetcher(world):
    """acquire() is the FIRST-host tool and keeps mutating the record; the refactor must not
    have changed that (it is why rematerialize exists as a separate verb)."""
    sid = world["sid"]
    rec = record.load(sid)
    rec["source_origin"]["artifacts"][0].pop("sha256")
    record.save(rec)
    harvest.acquire(sid)
    rec2 = record.load(sid)
    assert rec2["source_origin"]["artifacts"][0]["sha256"] == hashlib.sha256(world["archive"]).hexdigest()
    originally = json.loads(world["tracked"]["record.json"])["hashes"]["tree_sha256"]
    assert rec2["hashes"]["tree_sha256"] == originally, "same bytes, same tree hash, on either host"
