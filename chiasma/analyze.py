"""Summarize sweep rows: per (ratio, cap) medians by arm, and paired seed-wise
contrasts of O4 (and O4L) against named comparators.

Usage: python -B -m chiasma.analyze <rows.jsonl> [--vs O1,O2,O3,O0]
Integer arithmetic only; medians of an even count report the lower middle value.
"""
import argparse
import json
import sys
from collections import defaultdict

KEYS = ["bet_B", "err_CDE", "revise_DE", "collateral_CDE", "ydep_crit_CDE", "decoy_CDE",
        "unrel_CDE", "recovery_obs", "insert_F", "bytes_peak", "ops_total"]
LOWER_BETTER = KEYS


def med(vals):
    nums = sorted(v for v in vals if isinstance(v, int))
    nr = sum(1 for v in vals if not isinstance(v, int))
    if not nums:
        return "NR" * bool(nr)
    m = nums[(len(nums) - 1) // 2]
    return "{}{}".format(m, "+{}NR".format(nr) if nr else "")


def val(v, big=10 ** 9):
    return v if isinstance(v, int) else big    # NOT_RECOVERED ranks worst


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rows")
    ap.add_argument("--vs", default="O1,O2,O3,O0")
    ap.add_argument("--subjects", default="O4,O4L")
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(a.rows, encoding="utf-8")]
    by = defaultdict(list)
    for r in rows:
        by[(r["ratio"], r["cap"], r["arm"])].append(r)
    ceil = {(r["ratio"], r["seed"]): r for r in rows if r["arm"] == "CEIL"}
    ratios = sorted({r["ratio"] for r in rows})
    caps = sorted({r["cap"] for r in rows if r["cap"] != "NONE"})
    arms = sorted({r["arm"] for r in rows})
    for ratio in ratios:
        for cap in caps:
            print("\n== {} cap={} (medians over seeds; NR = NOT_RECOVERED)".format(ratio, cap))
            print("{:<5}".format("arm") + "".join("{:>15}".format(k[:15]) for k in KEYS))
            for arm in arms:
                rs = by.get((ratio, cap, arm)) or ([ceil[k] for k in ceil if k[0] == ratio] if arm == "CEIL" else [])
                if not rs:
                    continue
                print("{:<5}".format(arm) + "".join("{:>15}".format(med([r["endpoints"][k] for r in rs])) for k in KEYS))
            for subj in a.subjects.split(","):
                for comp in a.vs.split(","):
                    S = {r["seed"]: r for r in by.get((ratio, cap, subj), [])}
                    Cc = {r["seed"]: r for r in by.get((ratio, cap, comp), [])}
                    seeds = sorted(set(S) & set(Cc))
                    if not seeds:
                        continue
                    parts = []
                    for k in ("err_CDE", "revise_DE", "collateral_CDE", "recovery_obs", "bytes_peak", "ops_total"):
                        w = sum(1 for s in seeds if val(S[s]["endpoints"][k]) < val(Cc[s]["endpoints"][k]))
                        l = sum(1 for s in seeds if val(S[s]["endpoints"][k]) > val(Cc[s]["endpoints"][k]))
                        parts.append("{} {}W/{}L".format(k, w, l))
                    print("   {} vs {} (n={}): {}".format(subj, comp, len(seeds), "; ".join(parts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
