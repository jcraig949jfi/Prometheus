"""File the B5b receipt from committed split rows (C5 forward_fast swapped in). Run AFTER rebase.

usage: python -m primordial.soup.b5.receipt_b5b --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B"
FAST = ROWS / "B5b-rollout-split-c5.jsonl"
NUMPY = ROWS / "B5-rollout-split.jsonl"
CLAIM = ("B5b: with lane C's C5 tt_digits forward_fast(parallel) swapped into an exact copy of E5's rollout "
         "(E and C code read-only, P=128, seeds 9100..9107, worlds 1-5), B's world step + codebook gather + "
         "descriptor counters (world + act + books) are >= 50% of rollout wall in >= 4/5 worlds. Posted decision "
         "rule: >= 50% in >= 3/5 -> B builds the fused closed-loop kernel; < 30% in >= 3/5 -> not built. "
         "Controls: timed parts / loop wall within 5%; the fast copy's fitness == E5's numpy rollout 5/5.")


def _jsonl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = _jsonl(FAST)
    base = {r["world_seed"]: r for r in _jsonl(NUMPY)}
    assert all(r["forward"] == "fast" for r in rows), "B5b rows must come from the fast forward"
    glue = [r["glue_share"] for r in rows]
    ge50 = sum(x >= 0.5 for x in glue)
    lt30 = sum(x < 0.3 for x in glue)
    parts_ok = all(abs(r["parts_over_loop"] - 1) <= 0.05 for r in rows)
    fit_ok = all(r["fitness_equals_e5_rollout"] for r in rows)
    ctrl = parts_ok and fit_ok
    decision = ("build the fused closed-loop kernel" if ge50 >= 3 else
                "do NOT build" if lt30 >= 3 else "ambiguous: neither rule met")
    per = {}
    for r in rows:
        b = base.get(r["world_seed"])
        per[f"w{r['world_seed']}"] = {
            "share_fast": {k: round(v, 3) for k, v in r["share"].items()},
            "glue_share_fast": round(r["glue_share"], 3),
            "episode_steps_per_s_fast": round(r["episode_steps_per_s"]),
            "episode_steps_per_s_numpy_b5": round(b["episode_steps_per_s"]) if b else None,
            "rollout_speedup_vs_b5": round(r["episode_steps_per_s"] / b["episode_steps_per_s"], 2) if b else None,
            # Amdahl ceiling on what a fused kernel could still buy: glue -> 0
            "max_speedup_if_glue_were_free": round(1 / max(1 - r["glue_share"], 1e-9), 2),
        }
    rec = {
        "lane": "B", "exp_id": "B5b-rollout-split-after-c5", "claim": CLAIM,
        "status": "INDETERMINATE" if not ctrl else ("PASS" if ge50 >= 4 else "KILL"),
        "engineering": {"per_world": per,
                        "glue_share_range": [round(min(glue), 3), round(max(glue), 3)],
                        "note": "B5 rows (numpy forward) are the before; speedup_vs_b5 compares different runs "
                                "of the same loop, so it is indicative, not a controlled ratio"},
        "science": {
            "decision": decision,
            "hypothesis_scoring": {
                "glue_ge_50pct_in_ge_4_of_5": (f"{'CONFIRMED' if ge50 >= 4 else 'WRONG'} ({ge50}/5; "
                                               f"glue {min(glue):.0%}-{max(glue):.0%})"),
            },
        },
        "controls": {
            "cheat": (f"copy-faithfulness: fast copy fitness == E5 numpy rollout fitness "
                      f"{sum(r['fitness_equals_e5_rollout'] for r in rows)}/{len(rows)} worlds (a forward that "
                      "skipped work would change actions and fitness)"),
            "accounting": (f"timed parts / loop wall in [{min(r['parts_over_loop'] for r in rows):.3f}, "
                           f"{max(r['parts_over_loop'] for r in rows):.3f}] (bar: within 5%)"),
        },
        "rows": "primordial/ledger/rows/B/B5b-rollout-split-c5.jsonl (+ B5-rollout-split.jsonl as the before)",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science", "controls")}, indent=1))
    print(json.dumps(per, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
