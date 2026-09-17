"""Operator 15 R15-1: one readout for the M2 baseline and every clause A candidate (primordial.metric.readout)."""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pytest

from primordial.metric import baseline as B
from primordial.metric import floors as F
from primordial.metric import readout as RO
from primordial.qd.archive import load_elites

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _planted():
    """20 elites, glen 4; train fit 100 - i for genome byte i, plus a tie at fit 100 with a larger genome."""
    el = [(100 - i, bytes([i, 0, 0, 0])) for i in range(20)] + [(100, bytes([9, 9, 0, 0]))]
    score = lambda raw, seeds: float(np.mean(200.0 - raw[:, 0].astype(float)))      # genome byte 0 -> 200
    return el, score


def test_planted_top1_differs_from_top16_mean_and_ties_break_on_genome_bytes():
    el, score = _planted()
    seen = []
    got = RO.read(el, 4, lambda raw, seeds: seen.append(np.asarray(seeds)) or score(raw, seeds))
    assert got["readout"] == RO.NAME == "top1_train" and got["held64_per_seed"] == 200.0 and got["train_fit"] == 100
    assert np.array_equal(seen[0], F.HELD64)
    legacy = score(B.top_raw(el, 4, n=16), F.HELD64)
    assert legacy != got["held64_per_seed"] and legacy < 200.0          # the planted top-16 mean is not top-1
    assert RO.select(list(reversed(el)))[0] == (100, bytes([0, 0, 0, 0]))  # order-free; the smaller genome wins the tie
    assert RO.select(el, 16) == [tuple(x) for x in sorted(el, key=lambda v: (-v[0], v[1]))[:16]]
    with pytest.raises(ValueError):
        RO.read([], 4, score)


def test_read_doc_matches_read_on_a_saved_elites_document():
    el, score = _planted()
    doc = {"glen": 4, "elites": [[c, f, g.hex(), ""] for c, (f, g) in enumerate(el)]}
    assert RO.read_doc(doc, score) == RO.read(el, 4, score)


def test_baseline_summary_carries_the_readout_and_refuses_mixed_rows():
    mk = lambda i, v, ro: {"run_seed": i, "held64_per_seed": float(v), "genome_bytes": 200, "budget_ok": True,
                           "genomes": 1, "world": "w13", "gen_seed": 13, "pressure": "p", "elites": f"e{i}",
                           **({"readout": ro} if ro else {})}
    assert B.summary([mk(i, 180 + i, RO.NAME) for i in range(8)])["readout"] == RO.NAME
    assert B.summary([mk(i, 180 + i, None) for i in range(8)])["readout"] == RO.LEGACY
    with pytest.raises(ValueError):
        B.summary([mk(i, 180 + i, RO.NAME if i else None) for i in range(8)])


def _w13():
    doc = json.loads((ROOT / "primordial/ledger/qd/worlds_r4.json").read_text(encoding="utf-8"))
    cell = next(c for c in doc["cells"] if c["world"] == "w13" and c["pressure"] == "train128_held64")
    d = [json.loads(x) for x in (ROOT / "primordial/ledger/rows/D/D-R4-4-readouts.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    arch = {r["run_seed"]: r for r in d if r.get("kind") == "archive" and r["world"] == "w13" and r["pressure"] == "train128_held64"}
    dcell = next(r for r in d if r.get("kind") == "cell" and r["world"] == "w13" and r["pressure"] == "train128_held64")
    return cell, arch, dcell


def test_w13_train128_baseline_reproduces_from_the_saved_archives():
    """Aimed at the claim: the shared reader over G's 8 saved M2 archives == D-R4-4's committed top1, exactly."""
    cell, arch, dcell = _w13()
    paths = {int(k): pathlib.Path(v) for k, v in cell["baseline"]["elites"].items()}
    if not all(p.exists() for p in paths.values()):
        pytest.skip("G's saved w13 archives are not on this host")
    got = {rs: B.reread(13, p) for rs, p in sorted(paths.items())}
    assert sorted(got) == sorted(arch) == list(range(8))
    for rs, g in got.items():
        assert g["readout"] == RO.NAME and g["held64_per_seed"] == arch[rs]["top1"], rs
    med = float(np.median([g["held64_per_seed"] for g in got.values()]))
    assert med == dcell["readouts"]["top1"]["median"] and round(med, 2) == 189.53
    assert med - cell["verdicts"]["gate_in|HOLD"]["floor"] == pytest.approx(23.0625)
