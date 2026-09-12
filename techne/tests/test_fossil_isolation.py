"""The run-isolation and restore instruments of the fossil vault, with their controls.

Negative control  a recipe that writes nothing leaves the body verified under BOTH modes
                  (the detector does not hallucinate drift).
Positive control  an in-place run of a recipe that builds and edits DIRTIES the body and the
                  receipt says so (body_preserved False; drift names the rows) -- the detector
                  fires on the real failure mode that hit 23 of 57 bodies on 2026-09-12.
The fix           the same recipe under the default disposable copy leaves the body verified
                  while the build products exist in work/ and the run still passes.
Restore           the dirtied body goes back to its pin from its own archive by CONTENT;
                  a file no source holds is reported UNRECOVERABLE and the body stays unverified.
"""
from __future__ import annotations

import io
import json
import pathlib
import shutil
import tarfile

import pytest

from techne.fossils import harvest, record, vault

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="native runner needs bash")

HELLO = b"hello from 1987\n"
README = b"README of a specimen\n"


def _tar_bytes(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for name, data in files.items():
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


@pytest.fixture
def specimen(tmp_path, monkeypatch):
    """A synthetic specimen: tracked half under tmp/specimens, body under tmp/vault, the
    archive kept beside the extracted tree exactly as acquire() lays it out."""
    monkeypatch.setenv("TECHNE_FOSSIL_VAULT", str(tmp_path / "vault"))
    monkeypatch.setattr(vault, "SPECIMENS", tmp_path / "specimens")
    sid = "synthetic-1987"
    up = vault.body_dir(sid) / "upstream"
    (up / "tree").mkdir(parents=True)
    (up / "tree" / "hello.txt").write_bytes(HELLO)
    (up / "tree" / "README").write_bytes(README)
    (up / "synthetic.tar.gz").write_bytes(_tar_bytes({"synthetic-1987/hello.txt": HELLO, "synthetic-1987/README": README}))
    rows = vault.hash_tree(up)
    vault.write_hashes(sid, rows)
    rec = record.skeleton(sid, canonical_name="synthetic", lineage="synthetic", era="1987",
                          human_capability_summary={"built_to": "x", "pressure": "y", "success_means": "z"})
    rec["hashes"] = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows)}
    record.save(rec)
    return sid


def _recipe(sid, build, runs, **extra):
    r = {"runner": "native", "workdir": "upstream/tree", "build": build, "runs": runs,
         "classification_if_ok": "RUNNABLE_NATIVE", "test_kind": "TECHNE", **extra}
    (vault.specimen_dir(sid) / "recipe.json").write_text(json.dumps(r), encoding="utf-8")
    return r


CLEAN = ([], [{"name": "read", "cmd": "cat hello.txt", "expect": {"exit": 0, "stdout_contains": ["hello"]}}])
DIRTY = (["echo obj > product.o", "echo edited >> hello.txt"],
         [{"name": "read", "cmd": "cat hello.txt", "expect": {"exit": 0, "stdout_contains": ["hello"]}}])


def test_negative_control_clean_recipe_preserves_body_in_both_modes(specimen):
    _recipe(specimen, *CLEAN, in_place=True)
    r1 = harvest.run(specimen, timeout=60)
    assert r1["ok"] and r1["isolation"] == "in_place" and r1["body_preserved"] is True
    _recipe(specimen, *CLEAN)
    r2 = harvest.run(specimen, timeout=60)
    assert r2["ok"] and r2["isolation"] == "disposable_copy" and r2["body_preserved"] is True
    assert harvest.verify(specimen) is True


def test_positive_control_in_place_build_dirties_body_and_detector_fires(specimen):
    _recipe(specimen, *DIRTY, in_place=True)
    r = harvest.run(specimen, timeout=60)
    assert r["ok"] is True, "the run itself passes -- that is exactly why the label lied"
    assert r["body_preserved"] is False
    assert r["tree_sha256_after"] != r["tree_sha256_before"]
    d = harvest.drift(specimen)
    assert d["matches"] is False
    assert d["added"] == ["tree/product.o"]
    assert d["modified"] == ["tree/hello.txt"]
    assert d["removed"] == []
    assert harvest.verify(specimen) is False


def test_fix_disposable_copy_keeps_body_verified_while_build_products_exist(specimen):
    _recipe(specimen, *DIRTY)
    r = harvest.run(specimen, timeout=60)
    assert r["ok"] is True and r["isolation"] == "disposable_copy" and r["exec_root"] == "work"
    assert r["body_preserved"] is True
    work = vault.body_dir(specimen) / "work" / "upstream" / "tree"
    assert (work / "product.o").exists(), "the build really happened, in the copy"
    assert (work / "hello.txt").read_bytes() != HELLO
    assert (vault.body_dir(specimen) / "upstream" / "tree" / "hello.txt").read_bytes() == HELLO
    assert not (vault.body_dir(specimen) / "upstream" / "tree" / "product.o").exists()
    assert any(p["path"] == "product.o" for p in r["produced"]), "produced still tracks the build"
    assert harvest.verify(specimen) is True


def test_work_copy_is_fresh_per_run(specimen):
    _recipe(specimen, ["echo one > stale.o"], CLEAN[1])
    harvest.run(specimen, timeout=60)
    _recipe(specimen, [], CLEAN[1])
    harvest.run(specimen, timeout=60)
    assert not (vault.body_dir(specimen) / "work" / "upstream" / "tree" / "stale.o").exists()


def test_restore_recovers_dirtied_body_from_its_own_archive_by_content(specimen):
    _recipe(specimen, *DIRTY, in_place=True)
    harvest.run(specimen, timeout=60)
    assert harvest.verify(specimen) is False
    rep = harvest.restore(specimen)
    assert rep["deleted"] == ["tree/product.o"]
    assert rep["restored_from_archive"] == ["tree/hello.txt"]
    assert rep["restored_from_git"] == [] and rep["unrecoverable"] == []
    assert rep["verified"] is True and rep["after"]["matches"] is True
    assert harvest.verify(specimen) is True
    receipts = list((vault.specimen_dir(specimen) / "receipts").glob("restore-*.json"))
    assert len(receipts) == 1, "the rows ship with the verdict"
    assert json.loads(receipts[0].read_text(encoding="utf-8"))["verified"] is True


def test_restore_reports_unrecoverable_and_stays_unverified(specimen):
    up = vault.body_dir(specimen) / "upstream"
    (up / "synthetic.tar.gz").unlink()                       # no source of truth left beside the tree
    rows = vault.hash_tree(up)
    vault.write_hashes(specimen, rows)
    rec = record.load(specimen)
    rec["hashes"]["tree_sha256"] = vault.tree_hash_of(rows)
    record.save(rec)
    (up / "tree" / "hello.txt").write_bytes(b"corrupted\n")
    rep = harvest.restore(specimen)
    assert rep["unrecoverable"] == ["tree/hello.txt"]
    assert rep["verified"] is False
    assert (up / "tree" / "hello.txt").read_bytes() == b"corrupted\n", "nothing fabricated in its place"
    assert harvest.verify(specimen) is False


def test_restore_on_a_matching_body_is_a_noop(specimen):
    rep = harvest.restore(specimen)
    assert rep["verified"] is True and rep["deleted"] == []
    assert not list((vault.specimen_dir(specimen) / "receipts").glob("restore-*.json"))


def test_verify_all_census_counts_the_rows(specimen, tmp_path):
    _recipe(specimen, *DIRTY, in_place=True)
    harvest.run(specimen, timeout=60)
    out = tmp_path / "census.json"
    c = harvest.verify_all(str(out))
    assert c["specimens"] == 1 and c["differs"] == 1 and c["matches"] == 0
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["rows"][0]["added"] == ["tree/product.o"]
