"""Adjudicate the V0.3 crucible against its matched null controls, per PREREG_V0_3.md section 4.

No tolerance is introduced here. For every coordinate: drift = per-lineage change from checkpoint
0 to the final checkpoint; the same statistic is computed on the matched null; the reported
quantity is the DIFFERENCE, with a lineage-cluster bootstrap 95% interval. A coordinate is
declared to show a directional effect beyond null iff that interval excludes zero AND the sign
persists over the second half of the horizon. Holm correction is applied across all coordinates
within a cohort; both corrected and uncorrected counts are reported.

    python proteus/v0_3/run_adjudicate.py
"""
from __future__ import annotations

import gzip
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.v0_3 import nulls  # noqa: E402

# coordinate family -> matched null arm (PREREG section 3)
MATCH = {
    "genome_length": "NC1",
    "config_": "NC1B",
    "opcode_": "NC3", "class_": "NC3", "nop_share": "NC3", "operand_": "NC3",
    "executed_instruction_fraction": "NC4", "transcript_silent": "NC4",
    "status_": "NC4", "mutation_touches_executed": "NC4",
    "transcript_": "NC4", "knockout_": "NC4", "status_seq_": "NC4",
}
POP_COORDS = ("transcript_distinct", "transcript_top_share", "transcript_entropy_bits",
              "knockout_distinct", "knockout_top_share", "knockout_entropy_bits",
              "status_seq_distinct", "status_seq_top_share", "status_seq_entropy_bits")


def matched_null(coord: str) -> str:
    if coord in POP_COORDS:
        return "NC4"
    for pref, arm in MATCH.items():
        if coord == pref or (pref.endswith("_") and coord.startswith(pref)):
            return arm
    return "NC4"


def load(arm):
    p = os.path.join(HERE, f"RESULT_{arm}.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    with gzip.open(p + ".gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def per_lineage_drift(res, cohort, coord, c0, cN):
    ck = res["cohorts"][cohort]["checkpoints"]
    if arm_is_nc1(res):
        a, b = ck[str(c0)], ck[str(cN)]
        return [y - x for x, y in zip(a, b)]
    a = [r[coord] for r in ck[str(c0)]["per_lineage"]]
    b = [r[coord] for r in ck[str(cN)]["per_lineage"]]
    return [y - x for x, y in zip(a, b)]


def arm_is_nc1(res):
    return res["arm"] == "NC1"


def mean(v):
    return sum(v) / len(v) if v else 0.0


def boot_diff(a, b, n_res, rng):
    """Bootstrap the difference of means, resampling lineages independently in each arm."""
    na, nb = len(a), len(b)
    vals = []
    for _ in range(n_res):
        sa = sum(a[rng.randbelow(na)] for _ in range(na)) / na
        sb = sum(b[rng.randbelow(nb)] for _ in range(nb)) / nb
        vals.append(sa - sb)
    vals.sort()
    return vals[int(0.025 * n_res)], vals[int(0.975 * n_res) - 1]


def holm(pairs):
    """pairs: list of (name, excluded_zero, |effect|/half_width). Holm over the ranked evidence.

    We do not have p-values (bootstrap intervals only), so Holm is applied to the equivalent
    interval level: a coordinate survives correction iff its interval still excludes zero after
    widening by the Holm factor for its rank, using the standard normal quantile ratio.
    """
    import math
    ranked = sorted(pairs, key=lambda t: -t[2])
    m = len(ranked)
    out = {}
    stop = False
    for i, (name, excl, z) in enumerate(ranked):
        alpha = 0.05 / (m - i)
        crit = abs(_norm_ppf(1 - alpha / 2))     # compare z to z, not to a ratio
        ok = bool(excl and z >= crit) and not stop
        if not ok:
            stop = True                           # Holm is a step-down: stop at the first failure
        out[name] = ok
    return out


def _norm_ppf(p):
    import math
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p <= 1 - pl:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


def main():
    with open(os.path.join(HERE, "PREREG_V0_3.json"), encoding="utf-8") as f:
        pre = json.load(f)
    d = pre["crucible"]
    G = d["generations"]
    half = d["checkpoints"][len(d["checkpoints"]) // 2]
    n_res = d["bootstrap_resamples"]
    arms = {a: load(a) for a in ("V0_3", "NC1", "NC1B", "NC2", "NC3", "NC4")}
    v3 = arms["V0_3"]
    coords = sorted(v3["cohorts"]["32"]["checkpoints"]["0"]["per_lineage"][0].keys())
    rng = SplitMix64(seed_from("proteus.v0_3.adjudicate", pre["seed"]))
    report = {"prereg_id": pre["prereg_id"], "grammar_hash": pre["grammar_hash"],
              "generations": G, "second_half_from": half, "cohorts": {}}

    for cohort in sorted(v3["cohorts"], key=int):
        rows = []
        for coord in coords:
            null_arm = matched_null(coord)
            nres = arms[null_arm]
            if null_arm == "NC1" and coord != "genome_length":
                null_arm = "NC1B"
                nres = arms["NC1B"]
            # Content coordinates were preregistered against NC3, which FREEZES length. Where the
            # V0.3 arm changes length (cohorts 1, 8, 256) that comparison is confounded by length,
            # which is a wrong-population comparison. Discovered at adjudication. Rather than
            # silently switching the matching, BOTH are computed: NC3 as preregistered, and the
            # length-matched NC4. An effect is declared only if it survives against the
            # length-matched null; both numbers are reported.
            is_content = null_arm == "NC3"
            try:
                a_full = per_lineage_drift(v3, cohort, coord, 0, G)
                b_full = per_lineage_drift(nres, cohort, coord, 0, G)
                a_half = per_lineage_drift(v3, cohort, coord, half, G)
                b_half = per_lineage_drift(nres, cohort, coord, half, G)
                if is_content:
                    b4_full = per_lineage_drift(arms["NC4"], cohort, coord, 0, G)
                    b4_half = per_lineage_drift(arms["NC4"], cohort, coord, half, G)
            except (KeyError, TypeError):
                continue
            diff = mean(a_full) - mean(b_full)
            lo, hi = boot_diff(a_full, b_full, n_res, rng)
            diff_h = mean(a_half) - mean(b_half)
            excl = (lo > 0 and hi > 0) or (lo < 0 and hi < 0)
            persists = (diff > 0 and diff_h > 0) or (diff < 0 and diff_h < 0)
            hw = (hi - lo) / 2 or 1e-18
            row = {"coordinate": coord, "null_arm": null_arm,
                   "v0_3_drift": mean(a_full), "null_drift": mean(b_full),
                   "delta": diff, "ci95": [lo, hi],
                   "delta_second_half": diff_h,
                   "excludes_zero": excl, "sign_persists": persists,
                   "z_equivalent": abs(diff) / hw * 1.959963985}
            if is_content:
                d4 = mean(a_full) - mean(b4_full)
                lo4, hi4 = boot_diff(a_full, b4_full, n_res, rng)
                d4h = mean(a_half) - mean(b4_half)
                hw4 = (hi4 - lo4) / 2 or 1e-18
                excl4 = (lo4 > 0 and hi4 > 0) or (lo4 < 0 and hi4 < 0)
                row.update({"lengthmatched_null_arm": "NC4",
                            "lengthmatched_null_drift": mean(b4_full),
                            "lengthmatched_delta": d4, "lengthmatched_ci95": [lo4, hi4],
                            "lengthmatched_excludes_zero": excl4,
                            "lengthmatched_sign_persists": (d4 > 0 and d4h > 0) or (d4 < 0 and d4h < 0),
                            "lengthmatched_z": abs(d4) / hw4 * 1.959963985})
                # the decisive test uses the length-matched null
                row["excludes_zero"] = excl4
                row["sign_persists"] = row["lengthmatched_sign_persists"]
                row["z_equivalent"] = row["lengthmatched_z"]
            rows.append(row)
        # population-level coordinates, bootstrapped by resampling lineages and recomputing
        for coord in POP_COORDS:
            a0 = v3["cohorts"][cohort]["checkpoints"]["0"]["population"][coord]
            aN = v3["cohorts"][cohort]["checkpoints"][str(G)]["population"][coord]
            b0 = arms["NC4"]["cohorts"][cohort]["checkpoints"]["0"]["population"][coord]
            bN = arms["NC4"]["cohorts"][cohort]["checkpoints"][str(G)]["population"][coord]
            rows.append({"coordinate": coord, "null_arm": "NC4",
                         "v0_3_drift": aN - a0, "null_drift": bN - b0,
                         "delta": (aN - a0) - (bN - b0), "ci95": None,
                         "delta_second_half": None, "excludes_zero": None,
                         "sign_persists": None, "z_equivalent": 0.0,
                         "note": "population statistic; single realisation, no per-lineage CI"})
        testable = [(r["coordinate"], r["excludes_zero"], r["z_equivalent"])
                    for r in rows if r["ci95"] is not None]
        hm = holm(testable)
        for r in rows:
            r["holm_significant"] = hm.get(r["coordinate"])
        raw = sum(1 for r in rows if r["excludes_zero"])
        surv = sum(1 for r in rows if r.get("holm_significant"))
        both = [r["coordinate"] for r in rows if r.get("holm_significant") and r["sign_persists"]]
        report["cohorts"][cohort] = {
            "n_coordinates_tested": len(testable),
            "raw_excluding_zero": raw,
            "expected_by_chance_at_95pct": 0.05 * len(testable),
            "holm_significant": surv,
            "holm_significant_and_persistent": both,
            "coordinates": rows,
        }
        print(f"cohort {cohort:>3}: {len(testable)} coords | raw {raw} exclude zero "
              f"(chance {0.05*len(testable):.1f}) | Holm {surv} | persistent {len(both)}")
        for c in both:
            r = next(x for x in rows if x["coordinate"] == c)
            print(f"        {c:<34} v0.3 {r['v0_3_drift']:+.4f}  null({r['null_arm']}) "
                  f"{r['null_drift']:+.4f}  delta {r['delta']:+.4f} "
                  f"[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}]")
    with open(os.path.join(HERE, "ADJUDICATION_V0_3.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1, sort_keys=True)
        f.write("\n")
    allp = sorted({c for coh in report["cohorts"].values() for c in coh["holm_significant_and_persistent"]})
    print("\nUNION of persistent Holm-significant coordinates across cohorts:", len(allp))
    for c in allp:
        print("   ", c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
