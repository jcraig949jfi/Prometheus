"""Adjudicate V0.4 against its matched nulls, per PREREG_V0_4.md sections 4 and 5.

Structural coordinates are read against NC5, the joint reversible manifest walk. Other
configuration coordinates against NC1B. Content and phenotype against NC4 (the length-matched
geometry reference), with the V0.3-preregistered NC3 comparison reported alongside for content.

Multiplicity uses holm_agree, which runs two independent Holm implementations and RAISES on
disagreement. No tolerance is introduced anywhere in this file.

    python proteus/v0_4/run_adjudicate.py
"""
from __future__ import annotations

import gzip
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.v0_4 import holm  # noqa: E402

STRUCTURAL_NC5 = ("genome_length", "config_log2_tape_words")
POP_COORDS = ("transcript_distinct", "transcript_top_share", "transcript_entropy_bits",
              "knockout_distinct", "knockout_top_share", "knockout_entropy_bits",
              "status_seq_distinct", "status_seq_top_share", "status_seq_entropy_bits")
CONTENT_PREFIXES = ("opcode_", "class_", "operand_")
CONTENT_EXACT = ("nop_share",)


def matched_null(coord: str) -> str:
    if coord in STRUCTURAL_NC5:
        return "NC5"
    if coord.startswith("config_"):
        return "NC1B"
    if coord in CONTENT_EXACT or any(coord.startswith(p) for p in CONTENT_PREFIXES):
        return "NC4"
    return "NC4"


def is_content(coord: str) -> bool:
    return coord in CONTENT_EXACT or any(coord.startswith(p) for p in CONTENT_PREFIXES)


def load(arm):
    p = os.path.join(HERE, f"RESULT_{arm}.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    with gzip.open(p + ".gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def series(res, cohort, coord, c):
    """Per-lineage values of one coordinate at one checkpoint, for any arm layout."""
    ck = res["cohorts"][cohort]["checkpoints"][str(c)]
    if res["arm"] == "NC5":
        if coord == "genome_length":
            return list(ck["genome_length"])
        if coord == "config_log2_tape_words":
            return [math.log2(t) for t in ck["tape_words"]]
        raise KeyError(coord)
    return [r[coord] for r in ck["per_lineage"]]


def drift(res, cohort, coord, a, b):
    x = series(res, cohort, coord, a)
    y = series(res, cohort, coord, b)
    return [q - p for p, q in zip(x, y)]


def mean(v):
    return sum(v) / len(v) if v else 0.0


def boot_diff(a, b, n_res, rng):
    na, nb = len(a), len(b)
    vals = []
    for _ in range(n_res):
        sa = sum(a[rng.randbelow(na)] for _ in range(na)) / na
        sb = sum(b[rng.randbelow(nb)] for _ in range(nb)) / nb
        vals.append(sa - sb)
    vals.sort()
    return vals[int(0.025 * n_res)], vals[int(0.975 * n_res) - 1]


def main():
    with open(os.path.join(HERE, "PREREG_V0_4.json"), encoding="utf-8") as f:
        pre = json.load(f)
    d = pre["crucible"]
    G = d["generations"]
    half = d["checkpoints"][len(d["checkpoints"]) // 2]
    n_res = d["bootstrap_resamples"]
    arms = {a: load(a) for a in pre["arms"]}
    v4 = arms["V0_4"]
    coords = sorted(v4["cohorts"]["32"]["checkpoints"]["0"]["per_lineage"][0].keys())
    rng = SplitMix64(seed_from("proteus.v0_4.adjudicate", pre["seed"]))
    report = {"prereg_id": pre["prereg_id"], "grammar_hash": pre["grammar_hash"],
              "generations": G, "second_half_from": half,
              "holm": "holm_agree (two independent implementations; disagreement aborts)",
              "cohorts": {}}

    for cohort in sorted(v4["cohorts"], key=int):
        rows = []
        for coord in coords:
            null_arm = matched_null(coord)
            nres = arms[null_arm]
            try:
                a_full = drift(v4, cohort, coord, 0, G)
                b_full = drift(nres, cohort, coord, 0, G)
                a_half = drift(v4, cohort, coord, half, G)
                b_half = drift(nres, cohort, coord, half, G)
            except (KeyError, TypeError):
                continue
            diff = mean(a_full) - mean(b_full)
            lo, hi = boot_diff(a_full, b_full, n_res, rng)
            dh = mean(a_half) - mean(b_half)
            hw = (hi - lo) / 2 or 1e-18
            row = {"coordinate": coord, "null_arm": null_arm,
                   "v0_4_drift": mean(a_full), "null_drift": mean(b_full),
                   "delta": diff, "ci95": [lo, hi], "delta_second_half": dh,
                   "excludes_zero": (lo > 0 and hi > 0) or (lo < 0 and hi < 0),
                   "sign_persists": (diff > 0 and dh > 0) or (diff < 0 and dh < 0),
                   "z": abs(diff) / hw * 1.959963985}
            if is_content(coord):
                b3 = drift(arms["NC3"], cohort, coord, 0, G)
                d3 = mean(a_full) - mean(b3)
                lo3, hi3 = boot_diff(a_full, b3, n_res, rng)
                row["nc3_reported_only"] = {
                    "null_drift": mean(b3), "delta": d3, "ci95": [lo3, hi3],
                    "excludes_zero": (lo3 > 0 and hi3 > 0) or (lo3 < 0 and hi3 < 0)}
            rows.append(row)
        for coord in POP_COORDS:
            a0 = v4["cohorts"][cohort]["checkpoints"]["0"]["population"][coord]
            aN = v4["cohorts"][cohort]["checkpoints"][str(G)]["population"][coord]
            b0 = arms["NC4"]["cohorts"][cohort]["checkpoints"]["0"]["population"][coord]
            bN = arms["NC4"]["cohorts"][cohort]["checkpoints"][str(G)]["population"][coord]
            rows.append({"coordinate": coord, "null_arm": "NC4",
                         "v0_4_drift": aN - a0, "null_drift": bN - b0,
                         "delta": (aN - a0) - (bN - b0), "ci95": None,
                         "delta_second_half": None, "excludes_zero": None,
                         "sign_persists": None, "z": 0.0,
                         "note": "population statistic; single realisation, no per-lineage CI"})
        testable = [(r["coordinate"], r["z"]) for r in rows if r["ci95"] is not None]
        hm = holm.holm_agree(testable)           # raises on disagreement; never a vote
        for r in rows:
            r["holm_significant"] = hm.get(r["coordinate"])
        raw = sum(1 for r in rows if r["excludes_zero"])
        both = [r["coordinate"] for r in rows
                if r.get("holm_significant") and r["sign_persists"] and r["excludes_zero"]]
        report["cohorts"][cohort] = {
            "n_coordinates_tested": len(testable),
            "raw_excluding_zero": raw,
            "expected_by_chance_at_95pct": 0.05 * len(testable),
            "holm_significant": sum(1 for r in rows if r.get("holm_significant")),
            "holm_significant_and_persistent": both,
            "coordinates": rows,
        }
        print(f"cohort {cohort:>3}: {len(testable)} coords | raw {raw} exclude zero "
              f"(chance {0.05*len(testable):.1f}) | Holm+persistent {len(both)}")
        for c in both:
            r = next(x for x in rows if x["coordinate"] == c)
            print(f"        {c:<32} v0.4 {r['v0_4_drift']:+9.4f}  null({r['null_arm']}) "
                  f"{r['null_drift']:+9.4f}  delta {r['delta']:+8.4f} "
                  f"[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}]")

    # structural coordinates always printed, significant or not (brief: report every coordinate)
    print("\nSTRUCTURAL COORDINATES vs NC5, every cohort:")
    for cohort in sorted(v4["cohorts"], key=int):
        for coord in STRUCTURAL_NC5:
            r = next((x for x in report["cohorts"][cohort]["coordinates"]
                      if x["coordinate"] == coord), None)
            if r:
                print(f"  {cohort:>4} {coord:<26} v0.4 {r['v0_4_drift']:+9.4f}  NC5 "
                      f"{r['null_drift']:+9.4f}  delta {r['delta']:+8.4f} "
                      f"[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] excl={r['excludes_zero']} "
                      f"holm={r['holm_significant']}")

    allp = sorted({c for coh in report["cohorts"].values()
                   for c in coh["holm_significant_and_persistent"]})
    report["union_persistent_holm"] = allp
    with open(os.path.join(HERE, "ADJUDICATION_V0_4.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1, sort_keys=True)
        f.write("\n")
    print("\nUNION of persistent Holm-significant coordinates:", len(allp), allp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
