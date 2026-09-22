"""G-R5-1: explicit seed schema (runs_total / rng_family_count / runs_per_family), invariant, and the N x M lint."""
from __future__ import annotations

import json
import pathlib

import pytest

from primordial.metric import sample as SM

ROOT = pathlib.Path(__file__).resolve().parents[3]
R5_START_TS = 1789467179.0                   # round 5 P-BUILD start (Nestor-A brief, 2026-09-15 06:12:59 local)


def _runs(per):
    return [{"rng_family": f, "run_seed": i} for f, n in per.items() for i in range(n)]


def test_stamp_from_rows_is_explicit_and_holds_the_invariant():
    s = SM.stamp(_runs({4200: 8, 2101: 8, 3303: 8, 5501: 8}))
    assert {k: s[k] for k in SM.FIELDS} == {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8}
    assert s["families"] == [2101, 3303, 4200, 5501] and s["n_per_family"]["5501"] == 8 and "rng_families" not in s
    assert s["rng_family_count"] == len(s["families"]) and s["runs_total"] == sum(s["n_per_family"].values())
    assert s["runs_total"] == s["rng_family_count"] * s["runs_per_family"]
    unequal = SM.stamp(_runs({4200: 29, 2101: 1, 3303: 1, 5501: 1}))
    assert unequal["runs_total"] == 32 and unequal["runs_per_family"] is None
    with pytest.raises(ValueError, match="duplicate"):
        SM.stamp([{"rng_family": 4200, "run_seed": 0}, {"rng_family": 4200, "run_seed": 0}])


def test_invariant_refuses_inconsistent_stamps():
    ok = {"runs_total": 16, "rng_family_count": 2, "runs_per_family": 8, "families": [1, 2], "n_per_family": {"1": 8, "2": 8}}
    SM.check_invariant(ok)
    for bad in ({**ok, "runs_total": 32}, {**ok, "runs_per_family": 4}, {**ok, "rng_family_count": 4},
                {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 4},
                {**ok, "families": [1, 2, 3]}, {**ok, "families": [1, 3]}, {**ok, "rng_families": [1, 2]}):
        with pytest.raises(ValueError):
            SM.check_invariant(bad)


def test_meets_is_the_three_field_minimum():
    assert SM.meets(SM.from_counts({4200: 8, 2101: 8, 3303: 8, 5501: 8}))
    assert SM.meets(SM.from_counts({4200: 16, 2101: 8, 3303: 8, 5501: 8}))                 # unequal but every >= 8
    assert not SM.meets(SM.from_counts({4200: 29, 2101: 1, 3303: 1, 5501: 1}))             # 29+1+1+1
    assert not SM.meets(SM.from_counts({4200: 16, 2101: 16}))                             # 2 families
    assert not SM.meets(SM.from_counts({4200: 8, 2101: 8, 3303: 8, 5501: 7}))             # 31
    assert not SM.meets(dict(SM.PILOT_B2))                                                # the B2 pilot sample
    assert SM.meets(dict(SM.PILOT_B2), need=SM.PILOT_B2) and not SM.meets(None) and not SM.meets({"runs_total": 32})
    r = SM.refusal(SM.from_counts({4200: 16, 2101: 16}), "candidate")
    assert r["candidate_runs_total"] == 32 and r["candidate_rng_family_count"] == 2 and r["candidate_runs_per_family"] == 16
    assert r["need_runs_total"] == 32 and r["need_rng_family_count"] == 4 and r["need_runs_per_family"] == 8


@pytest.mark.parametrize("text", ["32 x 4 families", "8x4 runs", "32 runs x 4", "32 x 4 RNG families", "8 seeds x 4",
                                  "pooled 32x4 run seeds"])
def test_lint_flags_n_x_m_run_counts(text):
    assert SM.lint_text(text)


@pytest.mark.parametrize("text", ["800 x 128 genomes", "400x256 genomes", "runs_total 32, rng_family_count 4, runs_per_family 8",
                                  "a 4x4 grid", "T x S x W actions"])
def test_lint_leaves_budgets_and_the_explicit_form_alone(text):
    assert SM.lint_text(text) == []


def _new_receipts():
    for p in sorted((ROOT / "primordial" / "ledger").glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if isinstance(d, dict) and "exp_id" in d and float(d.get("ts") or 0) >= R5_START_TS:
                yield p.name, d


def _r5_tables():
    base = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld"
    return sorted(q for q in base.glob("*R5*.md")) + sorted(q for q in base.glob("*R5*.txt"))


def test_no_new_receipt_or_round5_table_prints_n_x_m_run_counts():
    hits = []
    for name, d in _new_receipts():
        text = json.dumps({k: v for k, v in d.items() if k not in ("engineering",)})
        hits += [(name, d["exp_id"], h) for h in SM.lint_text(text)]
    for q in _r5_tables():
        if q.name.startswith(("SWARM_R5", "BOOT_R5")):                    # plans quote operator text verbatim
            continue
        hits += [(q.name, None, h) for h in SM.lint_text(q.read_text(encoding="utf-8"))]
    assert hits == [], f"N x M run counts in new receipts/tables (use runs_total / rng_family_count / runs_per_family): {hits[:10]}"


def test_producers_stamp_the_explicit_three_fields_and_hold_the_invariant():
    """G-R5-1: every new summary / worlds stamp carries runs_total, rng_family_count, runs_per_family."""
    from primordial.metric import baseline as B
    from primordial.metric import eligibility as EL
    from primordial.metric import invariant as I
    from primordial.metric import r16 as R
    runs = [{"rng_family": f, "run_seed": i, "held64_per_seed": float(i), "readout": "top1_train", "world": "w1",
             "gen_seed": 1, "pressure": "p", "genome_bytes": 8, "budget_ok": True, "genomes": 1, "elites": ""}
            for f in (4200, 2101, 3303, 5501) for i in range(8)]
    for s in (B.pooled_stats(runs), B.pooled_summary(runs), I.pooled_summary(runs), R._stats(B.pooled_stats(runs))):
        assert {k: s[k] for k in SM.FIELDS} == {"runs_total": 32, "rng_family_count": 4, "runs_per_family": 8}
        assert "rng_families" not in s
        SM.check_invariant(s)
    e = EL.w13_eligibility()
    b = e["baseline"]
    assert (b["runs_total"], b["rng_family_count"], b["runs_per_family"]) == (32, 4, 8)
    assert b["rng_family_count"] == len(b["families"]) and b["runs_total"] == sum(b["n_per_family"].values())
