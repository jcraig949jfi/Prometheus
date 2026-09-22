"""File the B1s receipt from committed rows (run AFTER rebase so `git` is final).

usage: python -m primordial.soup.b1.receipt_b1s --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B" / "B1s-sensitivity.jsonl"
CHEATS = ("fix_unaffordable", "no_regime_flip", "stoch_swap")
CLAIM = ("B1s: the trace-hash oracle detects >=95% of episodes in which a ONE-semantic cheat's semantic was "
         "exercised (fix_unaffordable, no_regime_flip, stoch_swap in the numpy form), with 0 detections where it "
         "was not exercised; fix_unaffordable predicted weakest.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    rows = [json.loads(x) for x in open(ROWS, encoding="utf-8")]
    per = {}
    for c in CHEATS:
        rc = [r for r in rows if r["cheat"] == c]
        ex = [r for r in rc if r["exercised"]]
        per[c] = {"episodes": len(rc), "exercised": len(ex),
                  "detected_exercised": sum(r["detected"] for r in ex),
                  "false_alarms": sum(r["detected"] for r in rc if not r["exercised"]),
                  "sensitivity": round(sum(r["detected"] for r in ex) / len(ex), 4) if ex else None}
    honest = sum(r["detected"] for r in rows if r["cheat"] is None)
    floor_met = all(v["sensitivity"] is not None and v["sensitivity"] >= 0.95 for v in per.values())
    rec = {
        "lane": "B", "exp_id": "B1s-oracle-sensitivity-floor", "claim": CLAIM,
        "status": "PASS" if floor_met else "KILL",
        "engineering": {"worlds": 60, "episodes_per_world": 16, "form": "np"},
        "science": {
            "per_cheat": per,
            "verdict": ("the >=95%% floor is KILLED by fix_unaffordable (sensitivity %.3f): an unpaid write "
                        "can be absorbed without changing the trace; stoch_swap and no_regime_flip detected in "
                        "every exercised episode; 0 false alarms in all three" % per["fix_unaffordable"]["sensitivity"]),
            "consequence": ("B1's 320/320 equality proves the forms agree on EXERCISED behaviour. A form wrong only "
                            "on the unaffordable-write semantic slips past ~20% of sampled episodes, so equality "
                            "claims need enough episodes that the semantic is exercised AND visible"),
            "undetected_mechanism": "not yet diagnosed (candidates: target overwritten by a lin op; landing after end)",
        },
        "controls": {
            "cheat": "three one-semantic cheats run; honest numpy form mismatches %d/960 (must be 0)" % honest,
            "negative": "detections on episodes where the semantic was NOT exercised: " +
                        json.dumps({c: per[c]["false_alarms"] for c in CHEATS}),
        },
        "rows": "primordial/ledger/rows/B/B1s-sensitivity.jsonl",
        "git": a.git,
    }
    print(json.dumps(rec["science"], indent=1), rec["status"])
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
