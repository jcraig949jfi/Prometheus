"""File the B6b receipt from committed rows. Run AFTER rebase.

usage: python -m primordial.soup.b6.receipt_b6b --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B"
MAIN = ROWS / "B6b-fused-families.jsonl"
PROBE = ROWS / "B6b-probe-families.jsonl"
CLAIM = ("B6b: the fused closed-loop rollout extended to lane C's linear and tt_feat families (C's njit row "
         "kernels, read-only), judged against lane E7's own numpy rollout. Predicted: (H2) per-genome fitness AND "
         "descriptor cells == E7.rollout 128/128 on the train seeds AND on E6's 64 held-out seeds, worlds 4/1/3 x "
         "{linear, tt_feat}; (H1, reported not barred, host shared with E8) fused >= 5x E7 numpy rollout in >= 4/6 "
         "cells. Oracles: wforge replay 16/16; recorded action == argmax fam.ref_logits on clear rows. Cheats: "
         "skip_lin >= 14/16, brain stride 2 >= 30% of clear rows. Regression: tt_digits via the old E5 tuple API "
         "== E5.rollout.")


def _jsonl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")] if p.exists() else []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = _jsonl(MAIN)
    cells = [r for r in rows if r["kind"] == "cell"]
    regs = [r for r in rows if r["kind"] == "regression"]
    probe = _jsonl(PROBE)
    h2 = all(r[f"exact_fitness_{t}"] and r[f"exact_cells_{t}"] for r in cells for t in ("train", "held64"))
    sp = [r["speedup_vs_e7"] for r in cells]
    h1 = sum(x >= 5.0 for x in sp) >= 4
    world_ok = all(r["world_oracle_bad"] == 0 for r in cells)
    brain_ok = all(r["brain_mismatch"] == 0 and r["brain_clear_rows"] > 0 for r in cells)
    cheat_w = all(r["cheat_skip_lin_world_bad"] >= 14 for r in cells)
    cheat_b = all((r["cheat_brain_mismatch_share"] or 0) >= 0.30 for r in cells)
    reg_ok = bool(regs) and all(r["exact_fitness"] and r["exact_cells"] for r in regs)
    controls_ok = world_ok and brain_ok and cheat_w and cheat_b and reg_ok
    status = "INDETERMINATE" if not controls_ok else ("PASS" if h2 else "KILL")
    key = lambda r: f"w{r['world_seed']}_{r['family']}"
    rec = {
        "lane": "B", "exp_id": "B6b-fused-linear-tt-feat", "claim": CLAIM, "status": status,
        "engineering": {
            "per_cell": {key(r): {"speedup_vs_e7_numpy": round(r["speedup_vs_e7"], 2),
                                  "wall_e7_ms": round(r["wall_e7_numpy_s"] * 1e3, 1),
                                  "wall_fused_ms": round(r["wall_fused_s"] * 1e3, 2),
                                  "host_cpu_pct_before": r["host_cpu_pct_before"], "genome_bytes": r["genome_bytes"]}
                         for r in cells},
            "speedup_range": [round(min(sp), 2), round(max(sp), 2)] if sp else None,
            "caveat": "host shared with lane E's E8 run; speeds are same-process alternating medians but contended",
        },
        "science": {
            "hypothesis_scoring": {
                "h2_exact_train_and_held64": ("CONFIRMED (every world x family, both seed sets)" if h2 else
                                              "WRONG " + json.dumps({key(r): [r["fitness_mismatch_train"],
                                                                              r["cells_mismatch_train"],
                                                                              r["fitness_mismatch_held64"],
                                                                              r["cells_mismatch_held64"]]
                                                                     for r in cells})),
                "h1_ge_5x_in_ge_4_of_6_reported": (f"{'held' if h1 else 'missed'} "
                                                   f"({sum(x >= 5 for x in sp)}/{len(sp)}; "
                                                   f"{min(sp):.1f}x-{max(sp):.1f}x)") if sp else None,
            },
            "pre_build_probe": {f"w{r['world_seed']}_{r['family']}_m{r['mutate_steps']}":
                                f"{r['mismatches']}/{r['rows']}" for r in probe},
            "credit": "row kernels linear_act_row and tt_feat_act_row are lane C's (primordial/brain/genomes.py)",
        },
        "controls": {
            "cheat": ("skip_lin wforge replay mismatches "
                      + json.dumps({key(r): f"{r['cheat_skip_lin_world_bad']}/16" for r in cells})
                      + "; brain stride-2 mismatch share on clear rows "
                      + json.dumps({key(r): round(r["cheat_brain_mismatch_share"] or 0, 3) for r in cells})),
            "world_oracle": json.dumps({key(r): f"{16 - r['world_oracle_bad']}/16" for r in cells}),
            "brain_oracle": json.dumps({key(r): f"{r['brain_mismatch']}/{r['brain_clear_rows']}" for r in cells}),
            "regression_tt_digits_old_api": json.dumps(regs),
        },
        "rows": "primordial/ledger/rows/B/B6b-fused-families.jsonl + B6b-probe-families.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science", "controls")}, indent=1))
    print(json.dumps(rec["engineering"]["per_cell"], indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
