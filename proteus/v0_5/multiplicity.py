"""Global multiplicity architecture for V0.5 (brief section 2). Frozen before any measurement.

V0.4 corrected multiplicity WITHIN each cohort while the qualification decision searched across
coordinates AND cohorts. That mismatch is what made a single-cohort survivor fireable. V0.5
resolves it prospectively:

    hypothesis cell = (coordinate, cohort)
    family          = every cell belonging to the qualification claim
    procedure       = ONE step-down Holm over that whole family

Two independent implementations, as in V0.4: one steps down on the z scale against normal
quantiles, the other on erfc-derived p-values. `global_holm_agree` runs both and raises on any
disagreement. Adjudication calls only that.

The within-cohort procedure is retained ONLY so the packet can show what it would have done. It
never decides anything in V0.5.
"""
from __future__ import annotations

from proteus.v0_4.holm import (ALPHA, HolmDisagreement, _norm_ppf, holm_by_p, holm_by_z,
                               two_sided_p)

__all__ = ["global_holm_by_z", "global_holm_by_p", "global_holm_agree", "within_cohort_holm",
           "FIXTURES", "HolmDisagreement"]


def _key(cell):
    return f"{cell[0]}@{cell[1]}"


def global_holm_by_z(cells, alpha: float = ALPHA) -> dict:
    """cells: [((coordinate, cohort), z)]. One step-down Holm over the whole family."""
    items = [(_key(c), z) for c, z in cells]
    return holm_by_z(items, alpha)


def global_holm_by_p(cells, alpha: float = ALPHA) -> dict:
    items = [(_key(c), z) for c, z in cells]
    return holm_by_p(items, alpha)


def global_holm_agree(cells, alpha: float = ALPHA) -> dict:
    a = global_holm_by_z(cells, alpha)
    b = global_holm_by_p(cells, alpha)
    if a != b:
        diff = sorted(k for k in a if a[k] != b[k])
        raise HolmDisagreement(f"global holm implementations disagree on {diff}")
    return a


def within_cohort_holm(cells, alpha: float = ALPHA) -> dict:
    """The V0.4 procedure. Retained for comparison only; it decides nothing in V0.5."""
    by_cohort = {}
    for (coord, cohort), z in cells:
        by_cohort.setdefault(cohort, []).append((coord, z))
    out = {}
    for cohort, items in by_cohort.items():
        res = holm_by_z(items, alpha)
        for coord, ok in res.items():
            out[_key((coord, cohort))] = ok
    return out


def confirmatory_test(z: float, expected_sign: int, observed_sign: int,
                      alpha: float) -> dict:
    """The single preregistered confirmatory test for a named discovery.

    One hypothesis, one dataset, one-sided in the DIRECTION THE DISCOVERY CLAIMED. A confirmation
    requires the same sign AND p <= alpha on that one-sided test. There is no multiplicity
    correction because there is exactly one confirmatory hypothesis.
    """
    same_sign = (expected_sign == observed_sign)
    p_two = two_sided_p(z)
    p_one = (p_two / 2.0) if same_sign else (1.0 - p_two / 2.0)
    return {"same_sign": same_sign, "z": z, "p_one_sided": p_one, "alpha": alpha,
            "confirmed": bool(same_sign and p_one <= alpha),
            "critical_z_one_sided": _norm_ppf(1.0 - alpha)}


# ------------------------------------------------------------------ frozen fixtures
# Cells are ((coordinate, cohort), z). Expected answers computed from the step-down thresholds,
# not guessed: for family size m the rank-i two-sided critical z is Phi^-1(1 - (alpha/(m-i))/2).
FIXTURES = {
    "zero_discoveries": {
        "cells": [(("a", 1), 1.5), (("b", 1), 1.9), (("a", 2), 0.4), (("b", 2), 2.1)],
        "expected": [],
    },
    "one_discovery": {
        # m=4 thresholds 2.4977 / 2.3940 / 2.2414 / 1.9600; 5.0 clears, then 2.3 fails rank 1
        "cells": [(("a", 1), 5.0), (("b", 1), 2.3), (("a", 2), 1.0), (("b", 2), 0.5)],
        "expected": ["a@1"],
    },
    "several_discoveries": {
        "cells": [(("a", 1), 6.0), (("b", 1), 5.0), (("a", 2), 4.0), (("b", 2), 0.2)],
        "expected": ["a@1", "a@2", "b@1"],
    },
    "discoveries_across_multiple_cohorts": {
        "cells": [(("a", 1), 6.5), (("a", 2), 6.0), (("a", 3), 5.5), (("b", 4), 5.0)],
        "expected": ["a@1", "a@2", "a@3", "b@4"],
    },
    "within_cohort_passes_but_global_does_not": {
        # Cohort 3 alone is a family of 2: thresholds 2.2414 / 1.9600, so z=2.4 is a discovery
        # WITHIN its cohort. Globally the family has 10 cells: the rank-0 threshold is 2.8070,
        # which 2.4 does not clear, so global correction rejects nothing.
        "cells": ([(("c%d" % i, 1), 0.5) for i in range(4)]
                  + [(("c%d" % i, 2), 0.5) for i in range(4)]
                  + [(("hit", 3), 2.4), (("other", 3), 0.3)]),
        "expected": [],
        "expected_within_cohort": ["hit@3"],
    },
}
