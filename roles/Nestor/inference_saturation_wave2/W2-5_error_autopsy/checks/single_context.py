"""Single-context-point ruler check.

Incidents: the self-state robustness ruler (rate_1 >= 0.25 * rate_0, read after ONE own
execution) labelled X-DD-SELFSTATE / X-P2-ENDOSTATE / X-P2-D0CHECK donors POISONED/ROBUST from a
single phase of carried register state that cycles (16000006 copies after k = 0, 2, 5 and fails
after 1, 3, 4). Same shape: X-POSITION read one randomized-victim draw order; B §7 A1: the H1
"competence" rested on a cached single 6-episode draw; R-05: 26/57 P-11 survivors rest on one
event passing exactly 2 of 3 draws.

    assay(context) -> float        (e.g. copy rate after k own executions, or under seed s)
    rule(value_at_context, reference) -> label

The check evaluates the label at the declared single point and at every other context and
reports whether the single-point label is representative.

Verdicts
    CONTEXT_UNSTABLE  the label flips across contexts; a single-point label is unreliable
    OK                the label is the same at every context tried
    NOT_VERIFIED      fewer than 2 contexts, or the assay raised
"""
from typing import Any, Callable, Sequence

from . import CheckResult, OK, NOT_VERIFIED

NAME = "single_context"


def check_context_stability(assay: Callable[[Any], float], contexts: Sequence,
                            rule: Callable[[float, float], str], reference_context: Any,
                            single_point: Any, min_agreement: float = 1.0) -> CheckResult:
    if len(contexts) < 2:
        return CheckResult(NAME, NOT_VERIFIED, "need >= 2 contexts to test stability")
    try:
        ref = assay(reference_context)
        vals = {c: assay(c) for c in contexts}
        single_val = vals[single_point] if single_point in vals else assay(single_point)
    except Exception as e:  # noqa: BLE001
        return CheckResult(NAME, NOT_VERIFIED, "assay raised %s: %s" % (type(e).__name__, e))
    labels = {c: rule(v, ref) for c, v in vals.items()}
    single_label = rule(single_val, ref)
    agree = sum(1 for l in labels.values() if l == single_label) / len(labels)
    details = {"single_point": single_point, "single_label": single_label, "labels": labels,
               "agreement_with_single_point": agree, "values": vals, "reference": ref}
    if agree < min_agreement:
        flips = [{"context": c, "label": l} for c, l in labels.items() if l != single_label]
        return CheckResult(NAME, "CONTEXT_UNSTABLE",
                           "single-point label %r agrees with only %.2f of contexts: use a "
                           "multi-context rule" % (single_label, agree), details, flips)
    return CheckResult(NAME, OK, "label stable across contexts", details)
