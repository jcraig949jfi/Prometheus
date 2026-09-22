"""Controls for atlas/harvest/frontier_runs_m2.py (Atlas-M2's receipt
collector). Pure: a fixture receipt tree under tmp_path, a Batch, no store.

positive  a receipt whose pointer Atlas already linked enriches THAT attempt
          (same key), flips the pointer to FS:M2 present=true, and yields
          the chunk segment on Atlas's segment key with the chunk file
          beside it as an FS:M2 pointer.
cheat     a receipt with NO linked pointer must never mint an attempt key
          from its times: the collector links it to the experiment and says
          so. The failure mode this guards: Atlas's attempt ids are RUN
          event times, one second off the receipt's finished_at for 8 of 42
          receipts on 2026-09-19; a minted key would be a second attempt.
negative  a malformed receipt is a failure_mode fact, never an entity.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from atlas.harvest import common as C  # noqa: E402
from atlas.harvest import frontier_runs_m2 as M  # noqa: E402

RECEIPT = {
    "schema": "archaeon.frontier.receipt.v1", "experiment_id": "B-scatter.T000.d_seed/2b4cbc221db3",
    "spec": {"budget": {"evaluations": 2000, "wall_s": 21600}, "spec_digest": "sha256:abc"},
    "status": "DONE", "started_at": "2026-09-19T02:02:30Z", "finished_at": "2026-09-19T02:04:04Z",
    "evaluations": 8000, "integrity": [{"chunk": 0, "replay_A": "SAME"}],
    "chunks": [{"chunk": 0, "g0": 0, "g1": 250, "status": "DONE", "spec_hash": "sha256:s", "out_digest": "sha256:o",
                "evaluations": 8000, "fired": {"behavioral_novelty": 3}, "unable": {"lineage_discontinuity": 1}}],
}


def _tree(tmp_path, spec_dir="B-scatter.T000.d_seed_2b4cbc221db3", receipt=RECEIPT, raw=None):
    d = tmp_path / "runs" / "B-scatter" / spec_dir
    d.mkdir(parents=True)
    (d / "RECEIPT.json").write_text(raw if raw is not None else json.dumps(receipt), encoding="utf-8")
    (d / "chunk_000.json.gz").write_bytes(b"\x1f\x8b not really gzip, never decompressed")
    return tmp_path / "runs"


def test_positive_linked_receipt_enriches_the_same_attempt_and_flips_the_pointer(tmp_path):
    root = _tree(tmp_path)
    xk = M.ekey("B-scatter.T000.d_seed/2b4cbc221db3")
    akey = C.attempt_key(xk, "at20260919T020405Z")          # the RUN event time: one second AFTER finished_at
    rel = "archaeon/frontier/runs/B-scatter/B-scatter.T000.d_seed_2b4cbc221db3/RECEIPT.json"
    b = C.Batch("frontier_runs_m2", M.VERSION, "Archaeon")
    stats = {"receipts": 0, "matched": 0, "unmatched": 0, "chunks": 0}
    M.collect(b, str(root), "M2", {rel: akey}, stats)
    assert stats == {"receipts": 1, "matched": 1, "unmatched": 0, "chunks": 1}
    assert list(b.t["attempt"]) == [akey]
    a = b.t["attempt"][akey]
    assert a["started_at"] == "2026-09-19T02:02:30Z" and a["finished_at"] == "2026-09-19T02:04:04Z"
    assert a["config_digest"] == "sha256:abc" and a["host_id"] == "M2"
    src = b.t["source"]["hostfile://M2/" + rel]
    assert src["visibility"] == "FS:M2" and src["present"] is True and src["path"] == rel
    assert src["file_sha256"] and src["size_bytes"] > 0
    sk = C.segment_key(akey, "chunk_000")
    assert sk in b.t["segment"] and b.t["segment"][sk]["digest"] == "sha256:o"
    chunk_uri = "hostfile://M2/archaeon/frontier/runs/B-scatter/B-scatter.T000.d_seed_2b4cbc221db3/chunk_000.json.gz"
    assert b.t["source"][chunk_uri]["visibility"] == "FS:M2"
    assert (chunk_uri, "segment", sk, "rows") in b.links
    names = {f["name"] for f in b.facts.values()}
    assert {"receipt.status", "receipt.evaluations", "receipt.fired.behavioral_novelty",
            "receipt.unable.lineage_discontinuity", "receipt.integrity"} <= names


def test_cheat_unlinked_receipt_never_mints_an_attempt(tmp_path):
    root = _tree(tmp_path)
    b = C.Batch("frontier_runs_m2", M.VERSION, "Archaeon")
    stats = {"receipts": 0, "matched": 0, "unmatched": 0, "chunks": 0}
    M.collect(b, str(root), "M2", {}, stats)                  # nothing linked: the RUN event is not indexed yet
    assert stats["unmatched"] == 1 and stats["matched"] == 0
    assert b.t["attempt"] == {} and b.t["segment"] == {}     # no key minted from the receipt's times
    xk = M.ekey("B-scatter.T000.d_seed/2b4cbc221db3")
    assert xk in b.t["experiment"]                            # keyed by the receipt's OWN declared experiment_id
    rel = "archaeon/frontier/runs/B-scatter/B-scatter.T000.d_seed_2b4cbc221db3/RECEIPT.json"
    assert ("hostfile://M2/" + rel, "experiment", xk, "receipt_unmatched") in b.links
    assert any(f["name"] == "receipt.present_no_run_event" and f["subject_key"] == xk for f in b.facts.values())
    # and the directory name was NOT used as identity (dir uses '_', the id uses '/')
    assert not any("d_seed_2b4cbc221db3" in k for k in b.t["experiment"])


def test_negative_malformed_receipt_is_a_failure_fact_not_an_entity(tmp_path):
    root = _tree(tmp_path, raw="{not json")
    b = C.Batch("frontier_runs_m2", M.VERSION, "Archaeon")
    M.collect(b, str(root), "M2", {})
    assert b.t["attempt"] == {} and b.t["experiment"] == {}
    assert any(f["name"] == "receipt.unreadable" and f["kind"] == "failure_mode" for f in b.facts.values())


def test_registry_lists_the_module_for_m2_only():
    from atlas import db
    hh = db.registry()["harvester_hosts"]
    assert hh["frontier_runs_m2"] == ["M2"]
    roots = [r for r in db.registry()["local_roots"] if r.get("mode") == M.REGISTRY_MODE]
    assert roots and all(r["host"] == "M2" for r in roots)


def test_cheat_chunk_only_dir_flips_known_pointers_and_mints_nothing(tmp_path):
    """/2: the old loop wrote chunks with no RECEIPT.json. A known URI is flipped
    to FS:M2; an unknown chunk-only dir yields no source and no entity."""
    d = tmp_path / "runs" / "LIN-2d4fd1c7" / "B-scatter.T000"
    d.mkdir(parents=True)
    (d / "chunk_000.json.gz").write_bytes(b"\x1f\x8b never decompressed")
    (d / "chunk_001.json.gz").write_bytes(b"\x1f\x8b never decompressed")
    known = {"hostfile://M2/archaeon/frontier/runs/LIN-2d4fd1c7/B-scatter.T000/chunk_001.json.gz"}
    b = C.Batch("frontier_runs_m2", M.VERSION, "Archaeon")
    stats = {"receipts": 0, "matched": 0, "unmatched": 0, "chunks": 0, "chunk_only_known": 0}
    M.collect(b, str(tmp_path / "runs"), "M2", {}, stats, known)
    assert stats["chunk_only_known"] == 1 and stats["receipts"] == 0
    assert set(b.t["source"]) == known                      # chunk_000 (unknown to the index) is NOT minted
    assert b.t["source"][next(iter(known))]["visibility"] == "FS:M2"
    assert b.t["attempt"] == {} and b.t["segment"] == {} and b.t["experiment"] == {} and b.links == []
