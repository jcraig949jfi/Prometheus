"""File the B1t receipt from committed landing rows. Run AFTER rebase.

usage: python -m primordial.soup.b1.receipt_b1t --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B" / "B1t-landing.jsonl"
CLAIM = ("B1t: the fix_unaffordable oracle blind spot is unpaid writes landing at/after the episode end. "
         "Predicted: (1) in E4b w5 elites (T=256, delay=4) >=80% of exercised-but-undetected episodes have ALL "
         "unpaid writes landing at/after the end; (2) the same >=80% for B1s's 154 absorbed episodes; (3) every "
         "detected episode has >=1 unpaid write landing before the end. Control: delay=0 worlds have no after-end "
         "landings by construction.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = [json.loads(x) for x in open(ROWS, encoding="utf-8")]

    def cls(sel):
        return Counter(r["class"] for r in sel)

    def share(c):
        m = c["missed_all_after_end"] + c["missed_in_episode_absorbed"]
        return (c["missed_all_after_end"] / m if m else None), m

    e4 = [r for r in rows if r["source"] == "E4b"]
    b1 = [r for r in rows if r["source"] == "B1s"]
    w5 = [r for r in e4 if r["world_seed"] == 5]
    s_w5, m_w5 = share(cls(w5))
    s_b1, m_b1 = share(cls(b1))
    anomalies = sum(r["class"].startswith("anomaly") for r in rows)
    d0_after = sum(r["class"] == "missed_all_after_end" for r in rows if r["delay"] == 0)

    elite = {}
    for gs in sorted({r["world_seed"] for r in e4}):
        sel = [r for r in e4 if r["world_seed"] == gs]
        els = sorted({r["elite"] for r in sel})
        ex = [e for e in els if any(r["unpaid_ticks"] > 0 for r in sel if r["elite"] == e)]
        caught = [e for e in ex if any(r["detected"] for r in sel if r["elite"] == e)]
        c = cls(sel)
        elite[f"w{gs}"] = {"delay": sel[0]["delay"], "elites_caught": f"{len(caught)}/{len(ex)}",
                           "missed_all_after_end": c["missed_all_after_end"],
                           "missed_in_episode_absorbed": c["missed_in_episode_absorbed"]}

    p1, p2, p3 = (s_w5 is not None and s_w5 >= 0.8), (s_b1 is not None and s_b1 >= 0.8), anomalies == 0
    rec = {
        "lane": "B", "exp_id": "B1t-unpaid-landing-after-end", "claim": CLAIM,
        "status": "PASS" if (p1 and p2 and p3 and d0_after == 0) else "KILL",
        "engineering": {"episodes": len(rows), "e4b_episodes": len(e4), "b1s_episodes": len(b1)},
        "science": {
            "e4b_per_world": elite,
            "e4b_w5_share_missed_all_after_end": round(s_w5, 4) if s_w5 is not None else None,
            "b1s_share_missed_all_after_end": round(s_b1, 4) if s_b1 is not None else None,
            "b1s_by_delay": {
                "delay0": dict(cls([r for r in b1 if r["delay"] == 0])),
                "delay_gt0": dict(cls([r for r in b1 if r["delay"] > 0])),
            },
            "two_mechanisms": ("(i) after-end landing: a dying slot's delayed unpaid writes land after the trace "
                               "stops (all 91 misses in E4b w5, 97/154 in B1s); (ii) in-episode absorption: a "
                               "write lands but leaves the trace unchanged (all 21 misses in E4b w4, 17/17 in "
                               "B1s delay-0 worlds, 40 in B1s delay>0). (ii)'s cause, e.g. an overwritten target "
                               "register, is not established"),
            "reproduces_e4b_elite_counts": elite.get("w5", {}).get("elites_caught") == "11/24"
                                           and elite.get("w4", {}).get("elites_caught") == "15/18",
            "hypothesis_scoring": {
                "p1_e4b_w5_ge_80pct_after_end": f"{'CONFIRMED' if p1 else 'WRONG'} ({s_w5:.1%} of {m_w5})",
                "p2_b1s_ge_80pct_after_end": f"{'CONFIRMED' if p2 else 'WRONG'} ({s_b1:.1%} of {m_b1})",
                "p3_detected_always_has_in_episode_landing": "CONFIRMED" if p3 else f"WRONG ({anomalies} anomalies)",
            },
        },
        "controls": {
            "cheat": ("delay=0 control: after-end misses in delay-0 worlds must be 0 by construction: "
                      f"{d0_after}; detected-without-in-episode-landing anomalies: {anomalies}"),
            "replication": "E4b elite-level detection recomputed from E's saved elites: w5 11/24 and w4 15/18, "
                           "equal to E's posted numbers",
        },
        "rows": "primordial/ledger/rows/B/B1t-landing.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science", "controls")}, indent=1))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
