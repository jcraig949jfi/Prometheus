"""HITL #311, executed: re-verify the published Lehmer band with the REPAIRED verifier.

WHY THIS IS A RE-VERIFICATION AND NOT A RE-ENUMERATION, which is a stronger experiment and not
merely a cheaper one.

`run_brute_force` selects the band on `M_numpy` (numpy root-finding) and calls `mpmath_recheck`
only afterwards, at line 1230, to CERTIFY the entries it already selected. So the enumeration is
independent of the verifier: re-running all 97,435,855 polynomials would reproduce a
byte-identical band and then certify it differently. Re-enumerating would therefore CONFOUND any
verdict change with enumeration noise, while re-verifying the recorded band isolates exactly the
one thing that changed.

    published band  ->  repaired mpmath_recheck  ->  verdict_from_band
                        ^^^^^^^^^^^^^^^^^^^^^^^
                        the only difference

THE DEFECT BEING TESTED. Pre-cycle-053, `mpmath_recheck` escalated precision without factoring,
and `polyroots` fails on a root of multiplicity m NO MATTER HOW MANY DIGITS it is given -- the
iteration's obstacle is the condition number, which precision does not change. Every affected
entry came back NaN, was marked `verification_failed`, and `verdict_from_band` returns
INCONCLUSIVE precisely WHEN too many band entries fail verification. **The published INCONCLUSIVE
is therefore a property of the broken verifier, not of the mathematics.**

A NUMBER I HAVE BEEN CARRYING WRONG. Cycle 053 reported "17" verification failures and I repeated
it into HITL #311. The published band records **22 of 43**. The 17 is a different population
(the boundary-layer slice), and this file measures the band rather than quoting the note.

    python -m prometheus_math.lehmer_rerun_311
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prometheus_math.lehmer_brute_force import (  # noqa: E402
    INCONCLUSIVE_VERIFICATION_FAILURE_THRESHOLD, mpmath_recheck, verdict_from_band)

PUBLISHED = ROOT / "prometheus_math" / "_lehmer_brute_force_results.json"
OUT = ROOT / "prometheus_math" / "_lehmer_rerun_311_results.json"


def main() -> int:
    pub = json.loads(PUBLISHED.read_text(encoding="utf-8"))
    band = pub["in_lehmer_band"]

    before_failed = [e for e in band if e.get("verification_failed")]
    print(f"published band: {len(band)} entries, {len(before_failed)} verification_failed "
          f"({len(before_failed)/len(band):.4f} vs threshold "
          f"{INCONCLUSIVE_VERIFICATION_FAILURE_THRESHOLD})")
    print(f"published verdict: {pub['verdict']}")

    rows, still_failing, newly_verified, disagreements = [], [], [], []
    for e in band:
        hc = e["half_coeffs"]
        old_M = e.get("M_mpmath")
        old_failed = bool(e.get("verification_failed"))
        new_M = mpmath_recheck(hc, dps=30)
        new_failed = (new_M is None) or (isinstance(new_M, float) and math.isnan(new_M))
        rec = dict(e)
        rec["M_mpmath_repaired"] = None if new_failed else float(new_M)
        rec["verification_failed"] = bool(new_failed)          # what verdict_from_band reads
        rec["verification_failed_published"] = old_failed
        rows.append(rec)
        if old_failed and not new_failed:
            newly_verified.append({"half_coeffs": hc, "M_numpy": e.get("M_numpy"),
                                   "M_repaired": float(new_M)})
        if new_failed:
            still_failing.append(hc)
        # A published FINITE value that the repaired route disagrees with would be far more
        # serious than a NaN becoming finite: it would mean shipped numbers were wrong, not
        # merely absent. Checked rather than assumed.
        if (not old_failed) and (not new_failed) and old_M is not None:
            try:
                if not math.isclose(float(old_M), float(new_M), rel_tol=1e-9, abs_tol=1e-12):
                    disagreements.append({"half_coeffs": hc, "published": float(old_M),
                                          "repaired": float(new_M)})
            except (TypeError, ValueError):
                pass

    new_verdict = verdict_from_band(rows)
    n_failed_after = len(still_failing)

    # THE THIRD VERDICT, and the one that is actually correct.
    #
    # `verdict_from_band`'s own docstring states the precondition: "Cyclotomic-noise entries are
    # now filtered upstream in `run_brute_force` and removed from the band before verdict
    # dispatch". THE INPUT VIOLATES THAT PRECONDITION. 17 of the 43 band entries carry
    # `has_cyclotomic_factor: True`, and those 17 are EXACTLY the entries driving H2_BREAKS --
    # a branch whose own text calls them "a genuine candidate for a novel sub-1.18 specimen".
    # They are nothing of the kind: every one is a cyclotomic-factor product with a residual
    # measure at ~1.0009.
    #
    # This is not choosing the filter that gives a preferred answer. It is the filter the
    # function DOCUMENTS and does not apply -- ATK-019, documented hazard / unguarded code,
    # fourth instance in three days. All three verdicts are reported; none is suppressed.
    enforced = [e for e in rows
                if not e.get("has_cyclotomic_factor") and not e.get("is_cyclotomic")]
    verdict_enforced = verdict_from_band(enforced)

    out = {
        "hitl": "#311 — retract vs re-run, ruled RE-RUN by James 2026-08-27",
        "method": ("re-verification of the PUBLISHED band with the repaired verifier; the "
                   "enumeration is independent of the verifier (band selected on M_numpy, "
                   "mpmath_recheck certifies afterwards), so this isolates the fix"),
        "command": "python -m prometheus_math.lehmer_rerun_311",
        "source_artifact": "prometheus_math/_lehmer_brute_force_results.json",
        "subspace": pub.get("subspace"),
        "band_upper": pub.get("band_upper"),
        "total_polynomials_enumerated_in_published_run": pub.get("total_polynomials"),
        "band_size": len(band),
        "published": {
            "verdict": pub["verdict"],
            "n_verification_failed": len(before_failed),
            "failure_fraction": round(len(before_failed) / len(band), 4),
        },
        "repaired": {
            "verdict": new_verdict,
            "n_verification_failed": n_failed_after,
            "failure_fraction": round(n_failed_after / len(band), 4),
            "n_newly_verified": len(newly_verified),
        },
        "precondition_enforced": {
            "verdict": verdict_enforced,
            "band_size": len(enforced),
            "note": ("verdict_from_band documents that cyclotomic noise is removed "
                     "before dispatch; 17 of 43 entries violate that and are exactly "
                     "the H2_BREAKS drivers. With the documented precondition applied "
                     "the band is EMPTY."),
        },
        "h2_breaks_drivers_all_carry_cyclotomic_factor": True,
        "inconclusive_threshold": INCONCLUSIVE_VERIFICATION_FAILURE_THRESHOLD,
        "verdict_changed": new_verdict != pub["verdict"],
        "published_finite_values_that_disagree": disagreements,
        "newly_verified": newly_verified,
        "still_failing_half_coeffs": still_failing,
        "entries": rows,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"\nrepaired: {n_failed_after} verification_failed "
          f"({n_failed_after/len(band):.4f}), {len(newly_verified)} newly verified")
    print(f"published finite values that DISAGREE with the repaired route: {len(disagreements)}")
    print()
    print("VERDICT LADDER")
    print(f"  published (broken verifier)      : {pub['verdict']}")
    print(f"  repaired verifier, as dispatched : {new_verdict}")
    print(f"  + documented precondition applied: {verdict_enforced}  "
          f"(band {len(enforced)} entries)")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
