"""File the B6 receipt from committed rows. Run AFTER rebase.

usage: python -m primordial.soup.b6.receipt --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B" / "B6-fused-rollout.jsonl"
CLAIM = ("B6: lane E's closed-loop rollout fused into one numba call (prange over envs, all ticks; B world + "
         "observation + lane C's njit row kernel tt_digits_act_row + E's codebook and descriptor counters). "
         "Predicted: (H1) rollout wall >= 3x faster than the B5b fast path (numpy world + C5 forward_fast) in "
         ">= 4/5 worlds, alternating reps; (H2) EXACT: per-genome fitness AND descriptor cell == E5's own numpy "
         "rollout 128/128 in 5/5 worlds. Oracles: 16 recorded envs per world, trace hash + final charge == wforge "
         "replay 16/16; recorded action == argmax C ref_logits on clear rows, 0 mismatches. Cheats: skip_lin world "
         "fails wforge replay >= 14/16; skip-odd-cores brain mismatches >= 30% of clear rows.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = [json.loads(x) for x in open(ROWS, encoding="utf-8")]
    sp = [r["speedup_vs_fast"] for r in rows]
    h1 = sum(x >= 3.0 for x in sp) >= 4
    h2 = all(r["exact_fitness"] and r["exact_cells"] for r in rows)
    world_ok = all(r["world_oracle_bad"] == 0 for r in rows)
    brain_ok = all(r["brain_mismatch"] == 0 and r["brain_clear_rows"] > 0 for r in rows)
    cheat_world = all(r["cheat_skip_lin_world_bad"] >= 14 for r in rows)
    cheat_brain = all((r["cheat_brain_mismatch_share"] or 0) >= 0.30 for r in rows)
    oracles_ok = world_ok and brain_ok and cheat_world and cheat_brain
    status = ("INDETERMINATE" if not oracles_ok else
              "PASS" if (h1 and h2) else
              "KILL" if (h2 and not h1) else "FAIL")
    rec = {
        "lane": "B", "exp_id": "B6-fused-closed-loop-rollout", "claim": CLAIM, "status": status,
        "engineering": {
            "per_world": {f"w{r['world_seed']}": {
                "speedup_vs_b5b_fast": round(r["speedup_vs_fast"], 2),
                "wall_fast_loop_ms": round(r["wall_fast_loop_s"] * 1e3, 2),
                "wall_fused_ms": round(r["wall_fused_s"] * 1e3, 2),
                "episode_steps_per_s_fused": round(r["episode_steps_per_s_fused"]),
                "envs": r["envs"], "T": r["T"], "d_cores": r["d_cores"]} for r in rows},
            "speedup_range": [round(min(sp), 2), round(max(sp), 2)],
            "caveats": ["episode_steps_per_s_fused uses envs x horizon, not live steps (envs stop at done)",
                        "fused wall includes the Python wrapper (array prep, per-genome aggregation); "
                        "the fast-path loop excludes reset and cell computation, which favours the baseline",
                        "numba 3 threads for both paths; C5 forward_fast uses its own 24-chunk prange"],
        },
        "science": {
            "hypothesis_scoring": {
                "h1_ge_3x_in_ge_4_of_5": f"{'CONFIRMED' if h1 else 'WRONG'} ({sum(x >= 3 for x in sp)}/5; "
                                         f"{min(sp):.1f}x-{max(sp):.1f}x)",
                "h2_exact_fitness_and_cells": ("CONFIRMED (5/5 worlds, 0 genome mismatches)" if h2 else
                                               "WRONG " + json.dumps({f"w{r['world_seed']}":
                                                                      [r["fitness_mismatch_genomes"],
                                                                       r["cells_mismatch_genomes"]] for r in rows})),
            },
            "credit": "brain row kernel is lane C's genomes.tt_digits_act_row (commit 36dacd589); the "
                      "measure-first rule came from B5/B5b",
        },
        "controls": {
            "cheat": ("skip_lin world: wforge replay mismatches per world "
                      + json.dumps({f"w{r['world_seed']}": f"{r['cheat_skip_lin_world_bad']}/16" for r in rows})
                      + "; skip-odd-cores brain mismatch share on clear rows "
                      + json.dumps({f"w{r['world_seed']}": round(r["cheat_brain_mismatch_share"] or 0, 3)
                                    for r in rows})),
            "world_oracle": "honest fused trace hash + final charge vs wforge replay: "
                            + json.dumps({f"w{r['world_seed']}": f"{16 - r['world_oracle_bad']}/16" for r in rows}),
            "brain_oracle": "honest recorded action vs argmax C ref_logits on clear rows: "
                            + json.dumps({f"w{r['world_seed']}": f"{r['brain_mismatch']}/{r['brain_clear_rows']}"
                                          for r in rows}),
        },
        "rows": "primordial/ledger/rows/B/B6-fused-rollout.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science", "controls")}, indent=1))
    print(json.dumps(rec["engineering"]["per_world"], indent=1))
    if not a.dry:
        from primordial.bus import bus
        # no board score: episode_steps_per_s_fused counts envs x horizon, but envs stop at done,
        # so it overstates live steps; the rows do not record live step counts
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
