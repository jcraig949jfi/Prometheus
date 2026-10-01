"""W2-H regression test for patches/b2_seed_key.diff (SEMANTIC, gated; default reproduces C1).
FAILS on current code (no b2_seed_v2 field), PASSES patched. Uses the recorded C1 rows read-only.
Run on a scratch copy: PYTHONPATH=<W2-H>/scratch python -m pytest -q tests/test_b2_seed_key_w2h.py"""
import collections
import gzip
import json
import os
import pathlib

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
RUN = pathlib.Path(__file__).resolve().parents[7] / "roles/Ananke/pte/c1_rows"


def _load():
    rows = [json.loads(l) for l in gzip.open(RUN / "cells.jsonl.gz", "rt")]
    cands = json.loads((RUN / "boundaries_B.json").read_text())
    return rows, cands


def test_default_reproduces_recorded_b2_seeds():
    from prometheus.ananke import campaign as C
    rows, cands = _load()
    B = [r for r in rows if r["wave"] == "B"]
    specs = C.wave_B2(C.CampaignConfig(), B, cands)
    rec = sorted(r["search_seed"] for r in rows if r["wave"] == "B2")
    assert sorted(s["search_seed"] for s in specs) == rec


def test_v2_seeds_not_shared_across_families_or_tracks():
    from prometheus.ananke import campaign as C
    rows, cands = _load()
    B = [r for r in rows if r["wave"] == "B"]
    old = collections.defaultdict(set)
    for s in C.wave_B2(C.CampaignConfig(), B, cands):
        old[s["search_seed"]].add((s["env"]["family"], s["extra"].get("track")))
    assert any(len(v) > 1 for v in old.values())        # the C1 defect is present under the default
    new = collections.defaultdict(set)
    for s in C.wave_B2(C.CampaignConfig(b2_seed_v2=True), B, cands):
        new[s["search_seed"]].add((s["env"]["family"], s["extra"].get("track")))
    assert all(len(v) == 1 for v in new.values())
