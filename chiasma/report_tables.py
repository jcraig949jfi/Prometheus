"""Render E1 report tables (markdown) from evaluation rows. Post-freeze helper: it
formats numbers, it decides nothing (the verdict is chiasma/verdict_e1.py).

Usage: python -B -m chiasma.report_tables <rows.jsonl> > tables.md
"""
import json
import sys
from collections import defaultdict

ARMS = ["O1", "O2", "O3", "O4", "O4L", "O0", "O3R", "O4R", "CEIL", "EMB"]
KEYS = ["bet_B", "err_CDE", "collateral_CDE", "ydep_crit_CDE", "decoy_CDE", "unrel_CDE",
        "recovery_obs", "insert_F", "bytes_peak", "ops_total"]


def med(vals):
    nums = sorted(v for v in vals if isinstance(v, int))
    nr = len(vals) - len(nums)
    if not nums:
        return "NR x{}".format(nr)
    m = nums[(len(nums) - 1) // 2]
    return "{}{}".format(m, " (+{} NR)".format(nr) if nr else "")


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    rows = [json.loads(l) for l in open(argv[0], encoding="utf-8")]
    by = defaultdict(list)
    for r in rows:
        by[(r["ratio"], r["cap"], r["arm"])].append(r)
    ratios = sorted({r["ratio"] for r in rows})
    caps = sorted({r["cap"] for r in rows if r["cap"] != "NONE"})
    print("Medians over 10 evaluation seeds (lower middle for even n). NR = NOT_RECOVERED.")
    print("CEIL is uncapped and repeated in every cap table.\n")
    for ratio in ratios:
        for cap in caps:
            print("### {} cap={}\n".format(ratio, cap))
            print("| arm | " + " | ".join(KEYS) + " |")
            print("|---|" + "---|" * len(KEYS))
            for arm in ARMS:
                rs = by.get((ratio, cap, arm)) or (by.get((ratio, "NONE", arm)) if arm == "CEIL" else None)
                if not rs:
                    continue
                print("| {} | ".format(arm) + " | ".join(med([r["endpoints"][k] for r in rs]) for k in KEYS) + " |")
            print()
    cpu = sum(r["cpu_ms"] for r in rows)
    print("Runs: {}. CPU: {} ms ({} core-hours, integer-rounded down).".format(len(rows), cpu, cpu // 3600000))
    return 0


if __name__ == "__main__":
    sys.exit(main())
