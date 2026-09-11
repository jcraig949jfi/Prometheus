"""C1-e vs C3-2 historical arm. The comparison pre-declared on 2026-09-10.

THE PRE-DECLARATION, quoted from
`roles/Archaeon/INBOX_HERAKLES_H5_SCOPE_AND_C3_2_READ_2026-09-10.md`, which
was committed BEFORE any C3-2 number was seen:

    "I will compare each genome's accuracy against the C1-e measurement, not
     against the published figure, using a binomial SE from the C3-2 n_ics.
     A disagreement there is an instrument question between two of our own
     runs, which is a different and easier question than a disagreement with
     the literature."

Nothing in the rule below was chosen after the numbers arrived.

THE HORIZON QUESTION, SETTLED BEFORE COMPARING. C3-2 ran at 320 steps and
C1-e at 298. `at_T` is the state AT T, so the two are not the same measurement
in general. For THESE six genomes they are: measured on 4000 initial
conditions at N = 149, at_T accuracy is identical to four decimal places at
T = 298, 310, 320, 340 and 596. Every genome has converged well before 298 and
does not move again. So the comparison proceeds and no re-run is needed.

    python -m herakles.evca.c1e.compare_c3_2
"""
from __future__ import annotations

from herakles.workspace import assert_not_canonical

import io
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

#: C1-e primary run at N = 149, n_ics = 10000, steps = 298. The REFERENCE.
C1E_REFERENCE = {"maj": 0.0000, "exp": 0.6538, "par": 0.7708,
                 "particle1": 0.7542, "particle2": 0.7330, "GKL": 0.8145}
C1E_N_ICS = 10000

FAMILY_ALPHA = 0.05


def load_rows():
    out = subprocess.run(
        ["git", "show", "origin/main:archaeon/docs/h0h5/C3_2_READOUT.json"],
        cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("cannot read the readout: %s" % out.stderr[:200])
    d = json.loads(out.stdout)
    rows = d.get("historical_arm_for_c1e")
    if isinstance(rows, dict):
        rows = rows.get("rows")
    return rows


def main():
    # D-23: refuse to run from the canonical checkout.
    _ws = assert_not_canonical("write the C1-e vs C3-2 comparison")
    rows = load_rows()
    n_cells_compared = len(rows)
    per_cell_alpha = FAMILY_ALPHA / n_cells_compared
    # two-sided normal quantile, computed not looked up
    z = abs(_probit(per_cell_alpha / 2.0))

    print("C1-e vs C3-2 historical arm")
    print("cells compared %d, Bonferroni family %.2f, per-cell %.6f, z %.4f"
          % (n_cells_compared, FAMILY_ALPHA, per_cell_alpha, z))
    print()
    print("%-10s %6s %8s %8s %9s %8s %7s  %s"
          % ("rule", "sample", "C1-e", "C3-2", "diff", "se", "in_se",
             "decision"))
    results, n_agree, n_disagree, n_exact = [], 0, 0, 0
    for r in sorted(rows, key=lambda x: (x["rule"], x["ic_sample"])):
        name = r["rule"]
        ref = C1E_REFERENCE[name]
        obs = float(r["accuracy_at_T"])
        n = int(r["n_ics"])
        diff = obs - ref
        # binomial SE from the C3-2 n_ics, as pre-declared
        se = math.sqrt(obs * (1.0 - obs) / n) if 0 < obs < 1 else 0.0
        if ref == 0.0:
            # the same degenerate case C1-e prespecified an exact rule for:
            # a proportion test at p = 0 has zero band width
            decision = ("AGREES_EXACT" if r["n_incorrect_at_T"] == n
                        else "DISAGREES_EXACT")
            rule_used = "exact (reference is 0.0; zero-width band avoided)"
            n_exact += 1
            in_se = None
        else:
            band = z * se
            decision = "AGREES" if abs(diff) <= band else "DISAGREES"
            rule_used = "binomial, Bonferroni z = %.4f" % z
            in_se = abs(diff) / se if se > 0 else None
        if decision.startswith("AGREES"):
            n_agree += 1
        else:
            n_disagree += 1
        results.append({"rule": name, "ic_sample": r["ic_sample"],
                        "c1e_reference": ref, "c3_2_at_T": obs, "n_ics": n,
                        "diff": diff, "se": se,
                        "abs_diff_in_se": in_se, "decision": decision,
                        "decision_rule": rule_used,
                        "steps_c3_2": r["steps"], "steps_c1e": 298})
        print("%-10s %6d %8.4f %8.4f %+9.4f %8.4f %7s  %s"
              % (name, r["ic_sample"], ref, obs, diff, se,
                 ("%.2f" % in_se) if in_se is not None else "n/a", decision))

    print()
    print("AGREES %d of %d  (of which %d by the exact rule), DISAGREES %d"
          % (n_agree, n_cells_compared, n_exact, n_disagree))

    out = {"comparison": "C1-e reference vs C3-2 historical arm, at_T",
           "pre_declared_in": ("roles/Archaeon/"
                               "INBOX_HERAKLES_H5_SCOPE_AND_C3_2_READ_"
                               "2026-09-10.md"),
           "horizon_note": ("C3-2 at 320 steps, C1-e at 298. at_T is "
                            "identical to 4 dp at T = 298, 310, 320, 340, 596 "
                            "for all six genomes on 4000 ICs, so the "
                            "comparison proceeds without a re-run."),
           "c1e_reference": C1E_REFERENCE, "c1e_n_ics": C1E_N_ICS,
           "cells_compared": n_cells_compared, "family_alpha": FAMILY_ALPHA,
           "per_cell_alpha": per_cell_alpha, "z": z,
           "n_agree": n_agree, "n_disagree": n_disagree,
           "rows": results}
    p = os.path.join(HERE, "c1e_vs_c3_2.json")
    io.open(p, "w", encoding="utf-8", newline="").write(
        json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("wrote %s" % p)
    return 0


def _probit(p):
    """Inverse standard normal CDF, Acklam's rational approximation."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


if __name__ == "__main__":
    sys.exit(main())
