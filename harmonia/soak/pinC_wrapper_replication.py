"""Replicate Pin C's mutation score by WRAPPING the real verify (soak P40).

Third replication mechanism of this soak, each chosen to fit what the mutation
actually changes:
  P38 checkpoint pin  -> SUBCLASS      (mutation changed a method body)
  P39 domain-skip pin -> INPUT SPACE   (mutation changed a value read from a spec field)
  P40 unknown_kind    -> WRAPPER       (mutation changed only the returned dict's fields)

Q1/Q2/Q3 rewrite fields of the dict the abstention branch returns, so a wrapper that
calls the REAL verify and rewrites those same fields is observably identical for an
unregistered kind. Q4 REMOVES the branch and changes control flow, so it is NOT
wrapper-reachable -- reported as partial coverage rather than claimed.

No file is edited; no bytecode is involved; the real verify does all the work.
"""
import os
import sys
from collections import namedtuple

sys.path.insert(0, os.path.abspath("."))
from harmonia.experiments.verifier_lens import verify as real_verify  # noqa: E402

P = namedtuple("P", "tier version kind data ground_truth")
PROBE = P("X", "clean", "totally_unknown_kind", {"stmt": "a true claim"}, None)


def wrap(field, value):
    """Rewrite `field` of the abstention branch's return — exactly what Q1-Q3 did."""
    def v(probe, claimed):
        r = dict(real_verify(probe, claimed))
        if r.get("kill_pattern") == "unknown_kind" or field == "kill_pattern":
            r[field] = value
        return r
    return v


VARIANTS = {
 "control (real verify)":       real_verify,
 "Q1 valid=False":              wrap("valid", False),
 "Q2 valid=True":               wrap("valid", True),
 "Q3 kill_pattern renamed":     wrap("kill_pattern", "dispatch_miss"),
}
PUBLISHED = {"Q1 valid=False": "CAUGHT", "Q2 valid=True": "CAUGHT",
             "Q3 kill_pattern renamed": "CAUGHT"}


def pin_assertions(vfn):
    """The pin transcribed from test_verifier_lens.py. None == pin PASSES."""
    r = vfn(PROBE, True)
    if r["valid"] is not None:
        return f"valid is {r['valid']!r}, expected None"
    if r["kill_pattern"] != "unknown_kind":
        return f"kill_pattern is {r['kill_pattern']!r}"
    return None


print(f"{'variant':30s} {'pin verdict':>12s} {'published':>10s}  agree?   first failure")
print("-" * 96)
agree = disagree = 0
for label, vfn in VARIANTS.items():
    fail = pin_assertions(vfn)
    verdict = "CAUGHT" if fail else "passes"
    if label in PUBLISHED:
        ok = verdict == PUBLISHED[label]
        agree += ok; disagree += not ok
        print(f"{label:30s} {verdict:>12s} {PUBLISHED[label]:>10s}  {'yes' if ok else '*** NO ***':8s} {str(fail)[:32]}")
    else:
        print(f"{label:30s} {verdict:>12s} {'(control)':>10s}  {'—':8s} {str(fail)[:32]}")

print("-" * 96)
print(f"agreements: {agree}/{len(PUBLISHED)}   disagreements: {disagree}")
print("Q4 (abstention branch REMOVED) changes control flow, not the returned dict,")
print("so it is not wrapper-reachable. Coverage here is 3 of the 4 published mutations.")

# What does the pin actually discriminate on? (the P38 decomposition, applied here)
print("\nDecomposition — does the pin CRASH or ASSERT on each mutation?")
for label, vfn in VARIANTS.items():
    if label == "control (real verify)":
        continue
    try:
        vfn(PROBE, True)
        how = "loads fine -> caught by ASSERTION"
    except Exception as e:
        how = f"RAISES {type(e).__name__} -> caught by crash"
    print(f"  {label:30s} {how}")
