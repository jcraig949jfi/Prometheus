"""D-R7-6 (A 1789517336358-0; anomaly: the anti-prior arm PASSed in both rounds it has run): round 6's arm PASS was
explained by SATURATION (D-R7-1, receipt 1789511852981-0: held-out NK stops improving at ~80-100 generations, so a
1/5-CPU cut still reaches parity). Round 7's arm PASS, C-R7-AP-02 (codebook / nk_stub / byte_charge / falkordb_cypher /
metered_stream, receipt 1789517290895-0), has the same shape available: did its PRESSURE BIND ON THE READOUT'S OWN
WINNER, or did the cell reach parity because the winning genome pays almost nothing?

Zero QD: C's committed rows only (primordial/ledger/rows/C/C-R7-AP-02-codebook-nk-bytecharge-falkordb-metered.jsonl on
origin), cell and control paired on the same (family, run seed), 32 pairs, families 4200 / 2101 / 3303 / 5501 x run
seeds 0..7. Fields used: top1_program.functional_bytes, beta, train_nk_per_landscape_top1, held_per_landscape_top1,
held_delivered_share_top1, gens_done, oracles.ok, and the summary's held medians / bar / beta.

The pressure is byte_charge: selection fitness = sum TRAIN NK over the 8 train landscapes - BETA * functional bytes.
So the charge the WINNER actually paid, as a share of what it earned, is
    charge_share = beta * functional_bytes / (train_nk_per_landscape_top1 * N_TRAIN)
and the pressure binds only if that share is large enough to change which genome wins, which shows up as the charged
arm's winner being SMALLER than the uncharged control's winner on the same stream.

Rule (fixed before any value is read; pairs p = 1..32):
  s      = median over the 32 cell runs of charge_share
  small  = #pairs where the cell winner's functional_bytes < the control winner's
  same   = #pairs where they are equal
  PRESSURE_DID_NOT_BIND   s <= 0.01 and same >= 24   (the winner pays ~nothing and is no smaller: parity is free)
  PRESSURE_BOUND          s >= 0.05 and small >= 24  (the charge is material and it shrank the winner)
  MIXED                   otherwise
  INDETERMINATE if I1 or a planted control fails.
I1: 32 cell and 32 control runs, 8 per family, identical (family, run seed) key sets; every audited row's oracles.ok
true; beta equal to the summary's beta in every run; the recomputed held medians equal C's summary held_median_cell and
held_median_control to 0.01.
Planted controls (binding): planted_bound -- cell functional_bytes forced to control - 1 and charge_share forced to
0.10 must read PRESSURE_BOUND; planted_free -- cell functional_bytes equal to control and charge_share 0.001 must read
PRESSURE_DID_NOT_BIND.
Reported, not judged: held_delivered_share_top1 per arm (C's own AP-01 lesson: a meter that delivers every tick cannot
bind), functional_bytes / code_len / d distributions, gens_done, held and train medians, held_minus_random, and the
round 6 comparison (AP-01's mechanism was saturation, not non-binding pressure). The cross-round count (2 arm PASSes in
2 rounds) is recorded as descriptive only: n = 2 cannot separate a well-aimed arm from an ordinary draw, no hit rate is
computed and pm:prior:* is never read.

    worker.submit("D", "primordial.cohorts.d.r7_6_ap02_pressure_binding:job", EXP, ROWS, 300, envelope={...})
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import time

import numpy as np

EXP = "D-R7-6-ap02-pressure-binding"
PREDICATE_ID = EXP
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = f"primordial/ledger/rows/D/{EXP}.jsonl"
SRC_ROWS = "primordial/ledger/rows/C/C-R7-AP-02-codebook-nk-bytecharge-falkordb-metered.jsonl"
INTEGRATION = "origin/nestor/sidequest-graphworld-2026-09-14"
FAMILIES = (4200, 2101, 3303, 5501)
N_TRAIN = 8                       # C-R7-AP-02: train landscapes 9100..9107
FREE_SHARE, BOUND_SHARE = 0.01, 0.05
AGREE_PAIRS = 24
AP01 = {"exp": "C-R6-AP-01", "receipt": "1789488872310-0", "d_receipt": "1789511852981-0",
        "mechanism": "SATURATED: held-out NK plateaus by ~80-100 generations, so the 1/5-CPU cut reaches parity"}


def source_text(root=ROOT, integration: str = INTEGRATION) -> tuple[str, str]:
    """C's rows as committed on integration (fall back to the worktree copy); -> (text, provenance)."""
    q = subprocess.run(["git", "-C", str(root), "show", f"{integration}:{SRC_ROWS}"], capture_output=True, text=True,
                       encoding="utf-8")
    if q.returncode == 0 and q.stdout.strip():
        return q.stdout, integration
    return (root / SRC_ROWS).read_text(encoding="utf-8"), "worktree"


def load(text: str):
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    runs = {(x["arm"], int(x["family"]), int(x["run_seed"])): x for x in rows
            if x.get("kind") == "run" and x.get("arm") in ("cell", "control")}
    summ = [x for x in rows if x.get("kind") == "summary"]
    return runs, (summ[-1] if summ else {})


def pairs_of(runs) -> list[tuple[dict, dict]]:
    keys = sorted({(f, s) for (_, f, s) in runs}, key=lambda k: (FAMILIES.index(k[0]) if k[0] in FAMILIES else 9, k[1]))
    return [(runs[("cell", f, s)], runs[("control", f, s)]) for f, s in keys
            if ("cell", f, s) in runs and ("control", f, s) in runs]


def fb(row: dict) -> int:
    return int((row.get("top1_program") or {}).get("functional_bytes"))


def charge_share(row: dict) -> float:
    earned = float(row["train_nk_per_landscape_top1"]) * N_TRAIN
    return float(row["beta"]) * fb(row) / earned if earned else float("nan")


def counts(pp) -> tuple[int, int]:
    small = int(sum(fb(c) < fb(k) for c, k in pp))
    same = int(sum(fb(c) == fb(k) for c, k in pp))
    return small, same


def decide(i1: bool, controls_ok: bool, s: float, small: int, same: int) -> str:
    if not (i1 and controls_ok):
        return "INDETERMINATE"
    if s <= FREE_SHARE and same >= AGREE_PAIRS:
        return "PRESSURE_DID_NOT_BIND"
    if s >= BOUND_SHARE and small >= AGREE_PAIRS:
        return "PRESSURE_BOUND"
    return "MIXED"


def job(ctx, status: str = "record", exp: str = EXP, predicate_id: str = PREDICATE_ID):
    t0 = time.perf_counter()
    text, provenance = source_text()
    runs, summ = load(text)
    pp = pairs_of(runs)
    per_fam = {str(f): sum(int(c["family"]) == f for c, _ in pp) for f in FAMILIES}
    shares = [charge_share(c) for c, _ in pp]
    s = float(np.median(shares)) if shares else float("nan")
    small, same = counts(pp)
    cell_h = [float(c["held_per_landscape_top1"]) for c, _ in pp]
    ctrl_h = [float(k["held_per_landscape_top1"]) for _, k in pp]
    beta = summ.get("beta")
    i1 = {"pairs_32": len(pp) == 32, "per_family_8": all(v == 8 for v in per_fam.values()),
          "beta_consistent": all(float(x["beta"]) == float(beta) for x, _ in pp) if beta is not None else False,
          "oracles_ok_where_audited": all((x.get("oracles") or {}).get("ok", True) for pair in pp for x in pair),
          "median_cell_matches_summary": abs(float(np.median(cell_h)) - float(summ.get("held_median_cell", np.nan))) < 0.01,
          "median_control_matches_summary": abs(float(np.median(ctrl_h)) - float(summ.get("held_median_control", np.nan))) < 0.01}
    bound = decide(True, True, 0.10, AGREE_PAIRS, 0)
    free = decide(True, True, 0.001, 0, AGREE_PAIRS)
    controls = {"planted_bound": {"reads": bound, "ok": bound == "PRESSURE_BOUND"},
                "planted_free": {"reads": free, "ok": free == "PRESSURE_DID_NOT_BIND"}}
    ok = all(c["ok"] for c in controls.values())
    decision = decide(all(i1.values()), ok, s, small, same)
    d = lambda xs: {"median": float(np.median(xs)), "min": float(min(xs)), "max": float(max(xs))}
    ctx.emit({"kind": "summary", "exp": exp, "predicate_id": predicate_id, "status": status,
              "evidence_class": "VERDICT", "ts": round(time.time(), 3), "qd_runs": 0,
              "source_rows": SRC_ROWS, "source_provenance": provenance,
              "source_rows_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "runs_total": len(pp), "rng_family_count": len([f for f in per_fam if per_fam[f]]), "runs_per_family": 8,
              "families": list(FAMILIES), "n_per_family": per_fam, "beta": beta, "n_train_landscapes": N_TRAIN,
              "checks": {"I1": i1, "controls_ok": ok}, "controls": controls,
              "median_charge_share": s, "pairs_cell_winner_smaller": small, "pairs_equal_functional_bytes": same,
              "decision": decision,
              "reported_not_judged": {
                  "charge_share": d(shares),
                  "functional_bytes_cell": d([fb(c) for c, _ in pp]),
                  "functional_bytes_control": d([fb(k) for _, k in pp]),
                  "code_len_cell": d([int((c.get("top1_program") or {}).get("code_len")) for c, _ in pp]),
                  "d_cell": d([int((c.get("top1_program") or {}).get("d")) for c, _ in pp]),
                  "delivered_share_cell": d([float(c["held_delivered_share_top1"]) for c, _ in pp]),
                  "delivered_share_control": d([float(k["held_delivered_share_top1"]) for _, k in pp]),
                  "gens_done_cell": d([int(c["gens_done"]) for c, _ in pp]),
                  "held_median": {"cell": float(np.median(cell_h)), "control": float(np.median(ctrl_h)),
                                  "bar": summ.get("bar"), "primary": summ.get("primary")},
                  "held_minus_random_cell": d([float(c["held_minus_random"]) for c, _ in pp]),
                  "round6_comparison": AP01,
                  "cross_round_count": "2 anti-prior-arm PASSes in the 2 rounds the arm has run; DESCRIPTIVE ONLY -- "
                                       "n = 2 cannot separate a well-aimed arm from an ordinary draw, no hit rate is "
                                       "computed and pm:prior:* was not read"},
              "wall_s": round(time.perf_counter() - t0, 3)})
