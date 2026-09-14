"""File the B3g receipt (glue profile + correction of B2's speed conclusion). Run AFTER rebase.

usage: python -m primordial.soup.b3.receipt_glue --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B"
PROFILE = ROWS / "B3g-glue-profile.jsonl"
SETUP = ROWS / "B3g-glue-profile-setup.jsonl"
CLAIM = ("B3g: the 13-46% of the B2 graphblas form's wall time that B3 left unaccounted is Python glue in "
         "graphworld.py, not SuiteSparse. Predicted (in B3's journal as a guess, not a posted bar): run_gb's own "
         "Python (setdiff1d, row selection, dict/zip) dominates. Tested with cProfile tottime groups plus an "
         "UNPROFILED setup split (ticks=0 vs ticks=16), which also checks B2's speed claim.")


def _jsonl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    prof = _jsonl(PROFILE)
    setup = sorted(_jsonl(SETUP), key=lambda r: r["L"])
    crossover_ticks_only = next((r["entities"] for r in setup
                                 if r["gb_ent_ticks_per_s_ticks_only"] > r["ref_ent_ticks_per_s"]), None)
    below = [r["entities"] for r in setup if r["gb_ent_ticks_per_s_ticks_only"] <= r["ref_ent_ticks_per_s"]]
    crossover_with_setup = next((r["entities"] for r in setup
                                 if r["gb_ent_ticks_per_s_with_setup"] > r["ref_ent_ticks_per_s"]), None)
    big = [r for r in setup if r["entities"] >= 8192]
    b2_claim_holds = crossover_ticks_only is None or crossover_ticks_only >= 524288
    ref_setup_max = max(r["ref_setup_share"] for r in setup)
    method_ok = ref_setup_max <= 0.02
    rec = {
        "lane": "B", "exp_id": "B3g-graphblas-glue-and-b2-correction", "claim": CLAIM,
        # the self-refutation is the result: B2's speed conclusion does not hold per tick.
        # If the subtraction method fails its negative control, nothing is claimed.
        "status": ("INDETERMINATE" if not method_ok else "KILL" if not b2_claim_holds else "PASS"),
        "refutes": "B2-graphworld-toy: 'graphblas first beats the Python reference only at 524,288 entities'",
        "engineering": {
            "profile_share_by_group": {str(r["entities"]): r["share"] for r in prof},
            "profile_top_functions_largest": prof[-1]["top_functions"][:8],
            "setup_split_unprofiled": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}
                                       for r in setup],
            "caveats": ["cProfile inflates the 262k tiny step_cell calls, so profile shares are biased toward "
                        "py_glue; the unprofiled setup split is the number to trust",
                        "ticks=16 as in B2's bench, so setup is amortised over few ticks; setup is O(cells) "
                        "pure-Python static-relation construction (step_cell per cell per direction)",
                        "ref has no setup; gb ticks-only = (full - setup) wall"],
        },
        "science": {
            "where_the_unaccounted_time_goes": ("pure-Python static-relation construction inside run_gb "
                                                "(step_cell x 4 x cells) plus the per-tick trajectory string "
                                                "(genexpr + str.join); SuiteSparse kernels ~21% of profile at 8192"),
            "gb_setup_share_at_ge_8192_entities": [round(r["gb_setup_share"], 3) for r in big],
            "gb_overtakes_ref_ticks_only_at_entities": crossover_ticks_only,
            "gb_ticks_only_still_slower_at_entities": below,
            "gb_overtakes_ref_with_setup_at_entities": crossover_with_setup,
            "b2_correction": ("B2's receipt said graphblas beats the reference only at 524,288 entities (1.18x). "
                              "Per tick (setup excluded) graphblas already wins at "
                              f"{crossover_ticks_only} entities and above in this sweep; B2 measured setup+ticks "
                              "with ticks=16. B2's caveat said setup affects SMALL worlds; setup is "
                              f"{min(r['gb_setup_share'] for r in big):.0%}-{max(r['gb_setup_share'] for r in big):.0%} "
                              "at every size >= 8192 (computed from rows; the first filing hard-coded 41-46% from "
                              "a superseded run). The hash-equality result of B2 is unaffected."),
        },
        "controls": {
            "cheat": ("negative control RUN for the ticks=0 subtraction: the plain-Python reference has no "
                      "static-relation setup, so its ticks=0 share must be <= 2%: max "
                      f"{ref_setup_max:.2%} over {len(setup)} sizes "
                      f"({'passed' if method_ok else 'FAILED -> INDETERMINATE'})"),
            "same_process": "gb and ref timed back to back at every size with identical Specs and seeds",
            "b2_hash_unchanged": "no world code changed in B3g; B2's 50/50 oracle rows stand",
        },
        "rows": "primordial/ledger/rows/B/B3g-glue-profile.jsonl + B3g-glue-profile-setup.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "refutes", "science")}, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
