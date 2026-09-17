"""Judge the Q3b predicate (bus 1789427122926-0) from committed rows only.

usage: python -m primordial.nv.telemetry.judge_q3b primordial/ledger/rows/Q/Q3b-unpriv-features.jsonl
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict

OBS_BYTES = 4096 * 9 * 4


def judge(rows) -> dict:
    by = defaultdict(dict)
    for r in rows:
        by[r["rep"]][r["arm"]] = r
    reps = sorted(k for k, v in by.items() if {"honest", "cheat_sleep", "cheat_extra_copy"} <= set(v))
    c1 = c2 = 0
    for k in reps:
        h, s, c = by[k]["honest"], by[k]["cheat_sleep"], by[k]["cheat_extra_copy"]
        c1 += (c["h2d_bytes"] - h["h2d_bytes"] == OBS_BYTES) and c["d2h_bytes"] == h["d2h_bytes"]
        c2 += (s["wall_s"] - h["wall_s"] >= 0.045 and s["kernel_share"] < 0.5 * h["kernel_share"]
               and (s["h2d_bytes"], s["d2h_bytes"]) == (h["h2d_bytes"], h["d2h_bytes"]))
    shares = [by[k]["honest"]["kernel_share"] for k in reps]
    med = statistics.median(shares) if shares else 0.0
    false_stall = sum(x < 0.5 * med for x in shares)
    lost = sum(bool(r.get("lease_lost")) for r in rows)
    out = {"reps": len(reps), "copy_caught": c1, "sleep_caught": c2, "honest_share_median": med,
           "honest_false_stall": false_stall, "lease_lost_rows": lost}
    out["verdict"] = "PASS" if reps and c1 == c2 == len(reps) and false_stall == 0 and lost == 0 else "FAIL"
    return out


def main(argv=None) -> int:
    path = (argv or sys.argv[1:])[0]
    with open(path, encoding="utf-8") as fh:
        rows = [json.loads(x) for x in fh if x.strip()]
    print(json.dumps(judge(rows), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
