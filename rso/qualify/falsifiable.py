"""Executable falsifiability checks for claim-critical controls (C-018-T012; directive 2026-10-12 s2B).

A control or baseline is evidence only if it could have come out the other way. Each function below checks one way that
it could not. They take plain callables and plain cases, so an engine adapter can call them on its own detectors before
it freezes. A finding is returned, not raised: qualification decides what a finding blocks (FALSIFIABILITY.md).

    cannot_emit(detector, inputs, classes)          classes the detector never outputs: it cannot discriminate them
    constant_passes(rule, cases, classes)           a constant answer that passes the rule: the rule tests nothing
    oracle_fails(rule, cases)                       even the true answers fail: the rule cannot be passed
    reads_answer(detector, cases, scrub)            output changes when only answer-bearing fields change: privileged access
    trusts_derived(analyzer, rows, tamper)          output unchanged when components contradict a derived field
    near_miss_rejected(detector, near_misses)       each registered near-miss / counterfeit is classed as its truth
    audit(...)                                      all of the above as one record

A case is (input, truth). `rule(predictions, truths) -> bool` is the registered pass rule.
"""


def _preds(detector, cases):
    return [detector(x) for x, _ in cases]


def cannot_emit(detector, inputs, classes):
    """Classes in `classes` that `detector` produces for none of `inputs` (Z80 b1/b2 had no ENV output)."""
    seen = {detector(x) for x in inputs}
    return sorted(c for c in classes if c not in seen)


def constant_passes(rule, cases, classes):
    """Constant answers that pass `rule` (Z80 Q2: 'always INSERTED' passed for every outcome the run could produce)."""
    truths = [t for _, t in cases]
    return sorted(c for c in classes if rule([c] * len(cases), truths))


def oracle_fails(rule, cases):
    """True if the rule rejects even the true answers: it cannot be passed, so a failure means nothing."""
    truths = [t for _, t in cases]
    return not rule(list(truths), truths)


def reads_answer(detector, cases, scrub):
    """Indices of cases whose output changes when `scrub(input)` removes or permutes only answer-bearing fields
    (arm name, recipe table key, stored label). A detector that changes is reading the answer (privileged access);
    the C-017 recipe LOOKUP TABLE is the canonical example."""
    return [i for i, (x, _) in enumerate(cases) if detector(x) != detector(scrub(x))]


def trusts_derived(analyzer, rows, tamper):
    """True if `analyzer(rows)` is unchanged after `tamper(rows)` makes the components contradict a derived field
    while leaving that field alone. C-013 D1's analyze.py counted row['discovery'] without re-deriving it."""
    return analyzer(rows) == analyzer(tamper(rows))


def near_miss_rejected(detector, near_misses):
    """Each near-miss is (input, truth, what_it_imitates). Returns the near-misses the detector gets WRONG. At least one
    near-miss per important inference is required (FALSIFIABILITY.md item 6); an empty list from an empty set is not a pass."""
    if not near_misses:
        raise ValueError("no near-miss registered: the inference has no demonstrated counterfeit")
    return [(t, imitates) for x, t, imitates in near_misses if detector(x) != t]


def audit(name, detector, rule, cases, classes, must_discriminate=(), scrub=None, near_misses=None):
    """One record per claim-critical control. ok is False if any check fires; cannot_emit blocks only for the classes
    the control is registered to discriminate (`must_discriminate`)."""
    rec = {"control": name,
           "cannot_emit": cannot_emit(detector, [x for x, _ in cases], classes),
           "constant_passes": constant_passes(rule, cases, classes),
           "oracle_fails": oracle_fails(rule, cases),
           "reads_answer": reads_answer(detector, cases, scrub) if scrub else None,
           "near_miss_wrong": near_miss_rejected(detector, near_misses) if near_misses is not None else None}
    rec["cannot_discriminate"] = [c for c in rec["cannot_emit"] if c in must_discriminate]
    rec["ok"] = (not rec["cannot_discriminate"] and not rec["constant_passes"] and not rec["oracle_fails"] and not rec["reads_answer"]
                 and not rec["near_miss_wrong"] and rec["near_miss_wrong"] is not None)
    return rec
