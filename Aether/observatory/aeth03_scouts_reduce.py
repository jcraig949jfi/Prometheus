"""Apply PHYSICS_DESIGN_01 s5's preregistered KILL/JUSTIFY criteria to scout0.

Reads every `scout_<variant>_n<n>_s<k>.json` in a directory, averages each
metric over seeds, and evaluates the criteria exactly as written, against
v1 measured in the same battery. Thresholds are copied from the design
document, not tuned here; changing one requires changing the document.
"""

import argparse
import glob
import json
import os

KILL_ACTIVITY = 0.02            # K-a
KILL_ENDO_X = 2.0               # K-b: retained(+500) <= 2 x v1
KILL_SAT_FRACTION = 0.50        # K-c: differing sites >= 50% of lattice
KILL_SAT_J10 = 0.05             # K-c: and overlap lag 10 < 0.05
J1_ENDO_X = 5.0                 # J-1
J2_FOOT_X = 3.0                 # J-2
J2_REACH_MIN, J2_REACH_MAX = 2, 16
J3_J100 = 0.10                  # J-3


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def summarize(runs):
    n = runs[0]["n"]
    s = {
        "seeds": len(runs),
        "activity": mean([r["S0"]["activity_density"] for r in runs]),
        "energy_mean": mean([r["S0"]["energy_mean"] for r in runs]),
        "frozen_64": mean([r["S0"]["frozen_fraction_64"] for r in runs]),
        "retained_500": mean([r["S1"]["500"]["retained"] for r in runs]),
        "retained_100": mean([r["S1"]["100"]["retained"] for r in runs]),
        "change_on_500": mean([r["S1"]["500"]["on"] for r in runs]),
        "change_off_500": mean([r["S1"]["500"]["off"] for r in runs]),
        "j1": mean([r["S3"]["jaccard_lag1"] for r in runs]),
        "j10": mean([r["S3"]["jaccard_lag10"] for r in runs]),
        "j100": mean([r["S3"]["jaccard_lag100"] for r in runs]),
        "p_same_winner": mean([r["S4"]["p_same_winner"] for r in runs]),
        "p_rerolled": mean([r["S4"]["p_expected_if_rerolled"] for r in runs]),
    }
    for arm in ("perturbation_off", "perturbation_on"):
        for h in ("10", "100", "500"):
            rows = [r["S2"][arm]["by_horizon"][h] for r in runs]
            key = "%s_%s" % ("off" if arm.endswith("off") else "on", h)
            s["foot_" + key] = mean([x["footprint_per_origin"] for x in rows])
            s["reach_" + key] = mean([x["reach"] for x in rows])
            s["still_" + key] = mean([x["origins_still_differing"] for x in rows])
            s["diff_frac_" + key] = mean([
                (x["footprint_sites"] + r["S2"][arm]["origins"]
                 * x["origins_self_differing"]) / float(n * n)
                for x, r in zip(rows, runs)])
    return s


def judge(v, base):
    k_a = v["activity"] < KILL_ACTIVITY
    k_b = (v["retained_500"] <= KILL_ENDO_X * base["retained_500"]
           and v["foot_off_500"] <= base["foot_off_500"])
    k_c = (v["diff_frac_off_500"] >= KILL_SAT_FRACTION
           and (v["j10"] or 0.0) < KILL_SAT_J10)
    j_1 = v["retained_500"] >= J1_ENDO_X * base["retained_500"]
    j_2 = (v["foot_off_500"] >= J2_FOOT_X * max(base["foot_off_500"], 1e-9)
           and J2_REACH_MIN <= v["reach_off_500"] < J2_REACH_MAX)
    j_3 = (v["j100"] or 0.0) >= J3_J100
    killed = k_a or k_b or k_c
    justified = (not killed) and j_1 and j_2 and j_3
    return {"K-a": k_a, "K-b": k_b, "K-c": k_c, "J-1": j_1, "J-2": j_2,
            "J-3": j_3,
            "verdict": "KILLED" if killed else ("JUSTIFY_FOLLOW_UP" if justified
                                               else "UNRESOLVED")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir")
    a = ap.parse_args(argv)
    by_var = {}
    for p in sorted(glob.glob(os.path.join(a.dir, "scout_*_n*_s*.json"))):
        with open(p, encoding="utf-8") as fh:
            r = json.load(fh)
        by_var.setdefault(r["variant"], []).append(r)
    if "v1" not in by_var:
        raise SystemExit("no v1 baseline in %s" % a.dir)
    summary = {v: summarize(rs) for v, rs in by_var.items()}
    base = summary["v1"]
    verdicts = {v: judge(s, base) for v, s in summary.items() if v != "v1"}
    print(json.dumps({"summary": summary, "verdicts": verdicts}, indent=1,
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
