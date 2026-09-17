"""File the B1u receipt from committed absorb rows. Run AFTER rebase.

usage: python -m primordial.soup.b1.receipt_b1u --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B" / "B1u-absorb.jsonl"
CLAIM = ("B1u: in-episode absorption (mechanism ii of B1t) is a landed unpaid write overwritten in the same tick "
         "before the trace line. Predicted: >=90% of absorbed episodes have EVERY unpaid write erased by a lin_op "
         "overwriting its target register within the tick; the rest are stoch-kick overwrites; 0 writes cancelling "
         "mod M. Control: every detected episode keeps the difference to a trace line.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = [json.loads(x) for x in open(ROWS, encoding="utf-8")]
    ab = [r for r in rows if r["b1t_class"] == "missed_in_episode_absorbed"]
    dt = [r for r in rows if r["b1t_class"] == "detected"]
    agg = Counter()
    for r in ab:
        agg.update(r["story_classes"])
    valid = all(r["replica_eq_wforge"] for r in rows)
    all_lin = sum(r["all_erased_by_lin_op"] for r in ab)
    share = all_lin / len(ab)
    other = {k: v for k, v in agg.items() if k not in ("erased_by_lin_op", "erased_by_stoch")}
    ab_leak = sum(r["replica_detected"] for r in ab)
    dt_ok = sum(r["replica_detected"] and r["any_survives_to_trace"] for r in dt)
    p1 = share >= 0.90
    p2 = not other            # everything not lin_op is a stoch overwrite; no cancellation / other class
    ctrl = valid and ab_leak == 0 and dt_ok == len(dt)
    rec = {
        "lane": "B", "exp_id": "B1u-in-episode-absorption", "claim": CLAIM,
        "status": ("INDETERMINATE" if not valid else "PASS" if (p1 and p2 and ctrl) else "KILL"),
        "engineering": {"episodes_replayed": len(rows), "absorbed": len(ab), "detected_sample": len(dt)},
        "science": {
            "absorbed_all_erased_by_lin_op": f"{all_lin}/{len(ab)}",
            "erase_events_over_all_ticks": dict(agg),
            "absorbed_any_read_before_erase": sum(r["any_read_before_erase"] for r in ab),
            "absorbed_by_source": dict(Counter(f"{r['source']}_w{r['world_seed']}" if r["source"] == "E4b"
                                               else r["source"] for r in ab)),
            "count_correction": "the pre-run bus post said 78 absorbed misses; B1t rows hold 81 "
                                "(E4b w1 3 + w4 21 + B1s 57); the post omitted w1",
            "hypothesis_scoring": {
                "ge_90pct_all_erased_by_lin_op": f"{'CONFIRMED' if p1 else 'WRONG'} ({share:.1%})",
                "rest_are_stoch_no_cancellation": "CONFIRMED" if p2 else f"WRONG (other classes {other})",
            },
            "consequence": ("the trace hash is structurally blind to any write whose target register a lin_op "
                            "overwrites in the same tick without reading it first; with (i) after-end landings this "
                            "accounts for every fix_unaffordable miss measured (B1t + B1u)"),
        },
        "controls": {
            "cheat": (f"replica validity: honest replica == wforge trace hash {sum(r['replica_eq_wforge'] for r in rows)}"
                      f"/{len(rows)}; absorbed episodes showing a trace difference in the replica (must be 0): {ab_leak}"),
            "positive": f"detected episodes whose difference survives to a trace line: {dt_ok}/{len(dt)}",
        },
        "rows": "primordial/ledger/rows/B/B1u-absorb.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science", "controls")}, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
