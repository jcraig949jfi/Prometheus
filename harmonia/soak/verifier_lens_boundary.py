"""Boundary case for verifier_lens (Harmonia-A soak P12).

The property that matters most for a selection-side verifier is not "does it get
representable cases right" but "what does it do with a claim it CANNOT represent".
Two outcomes are possible and they are opposites:

    valid=None   honest abstention -- "I cannot tell"
    valid=False  MIS-CERTIFICATION -- a TRUE claim declared WRONG (type-II)

Result: the fix has landed. verify() abstains on all five unregistered kinds probed.

But the suite's guard is
    assert r["valid"] in (False, None)
which accepts BOTH, so it cannot tell the correct behaviour from the exact failure
it exists to prevent. The regression is simulated below against that literal
expression rather than argued -- inspection is where this soak keeps getting burned
(see P10/P11), so the gap is measured.

Read-only. Touches no file outside harmonia/soak/.
"""
from collections import namedtuple

from harmonia.experiments.verifier_lens import _DISPATCH, verify

Probe = namedtuple("Probe", "pid family kind data answer")
UNREGISTERED = ["graph", "pigeonhole", "identity", "inequality", "linear_algebra"]


def classify(valid):
    if valid is None:
        return "ABSTAIN (correct)"
    if valid is False:
        return "MIS-CERTIFY (true claim declared wrong)"
    return "accept"


def probe_unregistered():
    print("registered kinds:", sorted(_DISPATCH.keys()))
    for kind in UNREGISTERED:
        r = verify(Probe("SOAK", "soak", kind, {"stmt": "a TRUE claim of this kind"}, None), True)
        print(f"  {kind:16s} valid={str(r['valid']):5s} kill={r['kill_pattern']:14s}"
              f" -> {classify(r['valid'])}")


def simulate_regression():
    """Evaluate the suite's ACTUAL assertion against both outcomes."""
    print("\nsuite guard: assert r['valid'] in (False, None)")
    for label, val in [("current behaviour (abstain)", None),
                       ("regression (mis-certify)", False)]:
        print(f"  {label:32s} valid={str(val):5s} -> assertion passes: {val in (False, None)}")
    print("  => a regression from None back to False leaves the suite GREEN")


if __name__ == "__main__":
    probe_unregistered()
    simulate_regression()
