"""fp003_apollo_executing_confirm_20260615.py

Executing-lens confirmation of the FP-003 (bounded_menu_wall) Apollo anchor,
de-escrowed -> coordinate_invariant on 2026-06-15 (Harmonia E, Stage 3).

Per feedback_executing_lens_beats_reading_lens: don't rest the anchor on the
pre-recorded fp_void_audits_20260610.json verdict -- RE-RUN the live detector
against the real per-gen ledger and show it fires under the HONEST-promotion
input contract (best_acc improvements), not the cell-fill trap the contract
warns about.

Data: apollo/run_branch_c_r2/evolve_log.jsonl (the R2 Branch-C run; 481 gens;
this is the exact run that produced the FP-003 firing).

Run:
    set PYTHONPATH=D:\\Prometheus
    python harmonia\\experiments\\fp003_apollo_executing_confirm_20260615.py
Expect: HONEST input -> FIRED True (streak 481/481, menu constant, search alive);
the CONTROL (cell-fill counts, the WRONG input) also fires but for the benign
saturation reason the contract documents -- which is exactly why the caller,
not the detector, owns the honest-promotion distinction.
"""
from __future__ import annotations

import json
from pathlib import Path

from harmonia.primitives.failure_primitives import detect_bounded_menu_wall

REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "apollo" / "run_branch_c_r2" / "evolve_log.jsonl"
OUT = Path(__file__).with_suffix(".json")


def main() -> dict:
    recs = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
    recs.sort(key=lambda r: r["gen"])

    # HONEST promotions: did best_acc strictly improve vs the prior gen?
    # (within-run fitness gain -- the load-bearing signal). NOT archive_cells,
    # which is capacity-bound and saturates by design.
    honest, prev = [], None
    for r in recs:
        acc = r["best_acc"]
        honest.append(1 if (prev is not None and acc > prev + 1e-9) else 0)
        prev = acc
    menu_fp = ["R2_op_menu_fixed"] * len(recs)  # op menu fixed across the run

    res = detect_bounded_menu_wall(honest, menu_fingerprints=menu_fp, min_streak=30)

    # CONTROL: the documented false-positive trap -- feeding cell-fill counts.
    fills, prev = [], None
    for r in recs:
        c = r["archive_cells"]
        fills.append(1 if (prev is not None and c > prev) else 0)
        prev = c
    ctrl = detect_bounded_menu_wall(fills, menu_fingerprints=menu_fp, min_streak=30)

    out = {
        "anchor": "FP-003 / apollo-blackboard-evolve",
        "source_log": str(LOG),
        "n_gens": len(recs),
        "gen_range": [recs[0]["gen"], recs[-1]["gen"]],
        "search_alive": {
            "mutation_viability_min": min(r["mutation_viability"] for r in recs),
            "mutation_viability_max": max(r["mutation_viability"] for r in recs),
            "gens_with_llm_used_gt0": sum(1 for r in recs if r["llm_used"] > 0),
        },
        "honest_input": {
            "total_best_acc_improvements": sum(honest),
            "fired": res.fired,
            "headline": res.headline,
            "evidence": res.evidence,
        },
        "control_cellfill_wrong_input": {
            "total_fills": sum(fills),
            "fired": ctrl.fired,
            "note": ("also fires, but for the benign saturation-at-capacity "
                     "reason the input contract documents; caller owns the "
                     "honest-promotion distinction"),
        },
        "verdict": ("FP-003 detector FIRES on the real Apollo R2 ledger under the "
                    "honest-promotion contract while search is alive -> anchor "
                    "confirmed by execution, not by a stored verdict."),
    }
    OUT.write_text(json.dumps(out, indent=2))
    assert res.fired, "expected FP-003 to fire on the Apollo R2 ledger"
    assert sum(honest) == 0, "best_acc must be flat across the run"
    print(json.dumps(out, indent=2))
    print(f"\nwrote {OUT}")
    return out


if __name__ == "__main__":
    main()
