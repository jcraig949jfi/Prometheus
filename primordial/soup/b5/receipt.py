"""File the B5 receipt from committed split rows. Run AFTER rebase.

usage: python -m primordial.soup.b5.receipt --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B" / "B5-rollout-split.jsonl"
CLAIM = ("B5: in lane E's closed-loop rollout (E5 loop copied exactly, E code read-only, P=128, seeds 9100..9107, "
         "worlds 1-5) the B world step with observations is >= 50% of rollout wall in >= 3/5 worlds. Posted decision "
         "rule: world share < 30% in >= 3/5 -> B does NOT build a closed-loop numba world; >= 50% -> B builds it. "
         "Control: timed parts sum to the loop wall within 5%, and the copy's fitness equals E5's own rollout.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = [json.loads(x) for x in open(ROWS, encoding="utf-8")]
    ge50 = sum(r["share"]["world"] >= 0.5 for r in rows)
    lt30 = sum(r["share"]["world"] < 0.3 for r in rows)
    parts_ok = all(abs(r["parts_over_loop"] - 1) <= 0.05 for r in rows)
    fit_ok = all(r["fitness_equals_e5_rollout"] for r in rows)
    ctrl = parts_ok and fit_ok
    decision = ("build closed-loop numba world" if ge50 >= 3 else
                "do NOT build: the brain forward is the cost" if lt30 >= 3 else "ambiguous")
    brain = [r["share"]["brain"] for r in rows]
    world = [r["share"]["world"] for r in rows]
    # ceiling on what a faster world could buy E: world time -> 0 (Amdahl)
    max_speedup = [1 / (1 - r["share"]["world"]) for r in rows]
    rec = {
        "lane": "B", "exp_id": "B5-closed-loop-rollout-split", "claim": CLAIM,
        "status": "INDETERMINATE" if not ctrl else ("PASS" if ge50 >= 3 else "KILL"),
        "engineering": {
            "per_world": {f"w{r['world_seed']}": {"envs": r["envs"], "ticks": r["ticks_run"], "cores_d": r["d_cores"],
                                                   "share": {k: round(v, 3) for k, v in r["share"].items()},
                                                   "episode_steps_per_s": round(r["episode_steps_per_s"])}
                          for r in rows},
            "brain_share_range": [round(min(brain), 3), round(max(brain), 3)],
            "world_share_range": [round(min(world), 3), round(max(world), 3)],
            "max_rollout_speedup_if_world_were_free": [round(min(max_speedup), 3), round(max(max_speedup), 3)],
        },
        "science": {
            "decision": decision,
            "hypothesis_scoring": {
                "world_ge_50pct_in_ge_3_of_5": f"WRONG ({ge50}/5 worlds; world share {min(world):.0%}-{max(world):.0%})"
                if ge50 < 3 else f"CONFIRMED ({ge50}/5)",
            },
            "where_the_cost_is": (f"E's numpy TT brain forward is {min(brain):.0%}-{max(brain):.0%} of rollout wall "
                                  "(one gather G[gidx, core, digit] of [n, r, r] plus an einsum per core, d = 12-36 "
                                  "cores per tick); a free world would speed rollouts by at most "
                                  f"{min(max_speedup):.2f}-{max(max_speedup):.2f}x"),
            "not_established": "brain-forward optimisations were not tried; that is lane C/E code",
        },
        "controls": {
            "cheat": (f"copy-faithfulness: the timed copy's fitness equals E5's own rollout for the same brains in "
                      f"{sum(r['fitness_equals_e5_rollout'] for r in rows)}/{len(rows)} worlds (a copy that skipped "
                      "work to look fast would change fitness)"),
            "accounting": (f"timed parts / loop wall in [{min(r['parts_over_loop'] for r in rows):.3f}, "
                           f"{max(r['parts_over_loop'] for r in rows):.3f}] (bar: within 5%)"),
        },
        "rows": "primordial/ledger/rows/B/B5-rollout-split.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science", "controls")}, indent=1))
    print(json.dumps(rec["engineering"]["max_rollout_speedup_if_world_were_free"]))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
