"""RQ-4 (Rhadamanthus #245, 2026-09-14): every run receipt emits the interpreter version, a
pip-freeze hash and the NAMES (never values) of the environment variables read.

Positive control  a real fingerprint validates, and the hash MOVES when the package state moves
                  (the channel observes the thing it claims to observe).
Negative control  two fingerprints of one unchanged environment agree (no hallucinated drift).
Cheat controls    a schema/2 receipt with the block missing FAILS; a block that smuggles a VALUE
                  through env_vars_read ("NAME=value") FAILS; a hash that is not sha256 FAILS.
Legacy            a schema/1 receipt is reported as predating the field, never as defective.
Source discipline the fossils package reads os.environ only through vault.getenv, so the
                  names list cannot be silently incomplete.
End to end        a native run on a synthetic specimen writes a schema/2 receipt that carries
                  the block and names TECHNE_FOSSIL_VAULT among its reads.
"""
from __future__ import annotations

import io
import json
import pathlib
import re
import shutil
import tarfile

import pytest

from techne.fossils import harvest, record, vault

PKG = pathlib.Path(harvest.__file__).resolve().parent


def _fp(**over):
    e = harvest.environment_fingerprint(env_reads=["TECHNE_FOSSIL_VAULT"])
    e.update(over)
    return e


def _receipt(env, schema=harvest.RUN_RECEIPT_SCHEMA):
    return {"schema": schema, "host": {}, "tree_sha256_before": "x", "recipe_sha256": "y",
            "environment": env}


def test_positive_real_fingerprint_validates():
    assert harvest.validate_run_receipt(_receipt(_fp())) == []


def test_positive_hash_tracks_package_state(monkeypatch):
    before = harvest.environment_fingerprint(env_reads=[])["pip_freeze_sha256"]
    lines = harvest.pip_freeze_lines()
    monkeypatch.setattr(harvest, "pip_freeze_lines", lambda: lines + ["zz-planted==0.0.1"])
    after = harvest.environment_fingerprint(env_reads=[])["pip_freeze_sha256"]
    assert before != after, "a planted distribution must move the hash"


def test_negative_unchanged_environment_agrees():
    a = harvest.environment_fingerprint(env_reads=["A"])
    b = harvest.environment_fingerprint(env_reads=["A"])
    assert a == b


def test_cheat_missing_block_fails():
    r = _receipt(None)
    del r["environment"]
    assert harvest.validate_run_receipt(r) == ["environment block missing"]


def test_cheat_value_smuggled_through_names_fails():
    why = harvest.validate_run_receipt(_receipt(_fp(env_vars_read=["TECHNE_FOSSIL_VAULT=D:/somewhere"])))
    assert any("not a bare name" in w for w in why), why


def test_cheat_non_sha256_hash_fails():
    why = harvest.validate_run_receipt(_receipt(_fp(pip_freeze_sha256="deadbeef")))
    assert any("pip_freeze_sha256" in w for w in why), why


def test_cheat_interpreter_missing_fails():
    why = harvest.validate_run_receipt(_receipt(_fp(interpreter={})))
    assert any("interpreter" in w for w in why), why


def test_legacy_schema1_reported_not_failed():
    r = _receipt(None, schema="techne.fossil.run_receipt/1")
    del r["environment"]
    why = harvest.validate_run_receipt(r)
    assert len(why) == 1 and why[0].startswith("schema/1 receipt: predates")


def test_unknown_schema_fails():
    assert harvest.validate_run_receipt(_receipt(_fp(), schema="techne.fossil.run_receipt/9"))


def test_fossils_package_reads_environ_only_through_getenv():
    hits = []
    for py in sorted(PKG.glob("*.py")):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"os\.environ\b|os\.getenv\(", line) and not line.lstrip().startswith("#"):
                hits.append("%s:%d: %s" % (py.name, i, line.strip()))
    allowed = {"vault.py"}
    stray = [h for h in hits if h.split(":")[0] not in allowed]
    assert not stray, "unreceipted environment reads: %s" % stray
    assert any(h.startswith("vault.py") and "def getenv" not in h for h in hits), "getenv must itself read os.environ"


def test_receipt_census_over_tracked_receipts_has_no_defects():
    c = harvest.receipt_census()
    assert c["defective"] == 0
    assert c["n"] == c["carries_rq4"] + c["predates_rq4"]


# ---------------------------------------------------------------- end to end (native runner)

HELLO = b"hello from 1987\n"


def _tar_bytes(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for name, data in files.items():
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


@pytest.mark.skipif(shutil.which("bash") is None, reason="native runner needs bash")
def test_end_to_end_native_run_writes_schema2_receipt_with_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("TECHNE_FOSSIL_VAULT", str(tmp_path / "vault"))
    monkeypatch.setattr(vault, "SPECIMENS", tmp_path / "specimens")
    sid = "synthetic-env-1987"
    up = vault.body_dir(sid) / "upstream"
    (up / "tree").mkdir(parents=True)
    (up / "tree" / "hello.txt").write_bytes(HELLO)
    (up / "synthetic.tar.gz").write_bytes(_tar_bytes({"synthetic/hello.txt": HELLO}))
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
    r = harvest.run(sid, timeout=60)
    assert r["ok"] and r["schema"] == harvest.RUN_RECEIPT_SCHEMA
    assert harvest.validate_run_receipt(r) == []
    assert "TECHNE_FOSSIL_VAULT" in r["environment"]["env_vars_read"]
    assert all("=" not in n for n in r["environment"]["env_vars_read"])
    written = json.loads(next((vault.specimen_dir(sid) / "receipts").glob("run-*.json")).read_text(encoding="utf-8"))
    assert written["environment"] == r["environment"]
    # the value never reaches the receipt
    assert str(tmp_path) not in json.dumps(written["environment"])
