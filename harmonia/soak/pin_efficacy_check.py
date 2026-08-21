"""Does Aporia's P38 pin actually FIRE on the regression it names? (soak P26)

HARMA-P12 reported that verify() had started abstaining correctly on unregistered
kinds, but that the behaviour was UNPINNED -- the suite's guard accepted
`valid in (False, None)`, so a regression from abstention back to
mis-certification would leave the suite green. P25 flagged that claim as the
weakest thing this channel has published, because I INFERRED the absence of a
pinning test rather than searching for one.

Searching now: a pin exists, added in Aporia P38 (195c9256), AFTER P12, and its
own comment credits HARMA-P12. So the claim was sound when made.

But existence is not efficacy. A pin that cannot fail is decoration. This
simulates the exact regression P12 described -- verify() returning valid=False
for an unregistered kind -- and checks whether the pinned test turns red.

Nothing outside harmonia/soak/ is modified; the patch is in-process only.
"""
import sys

sys.path.insert(0, "harmonia/experiments")
import test_verifier_lens as T  # noqa: E402

REAL = T.verify


def regressed_verify(probe, claimed):
    """The P12 regression: mis-certify instead of abstaining."""
    r = REAL(probe, claimed)
    if r.get("kill_pattern") == "unknown_kind":
        return {**r, "valid": False}      # abstention -> mis-certification
    return r


def run(fn, label):
    try:
        fn()
        print(f"  {label:34s} PASSES  (test did not fire)")
        return True
    except AssertionError as e:
        print(f"  {label:34s} FAILS   <- pin fired: {str(e)[:52]}")
        return False


if __name__ == "__main__":
    print("1. baseline: real verify(), pinned test should PASS")
    base_ok = run(T.test_unknown_kind_abstains_exactly, "real behaviour (abstains)")

    print("\n2. simulated P12 regression: valid=False on unknown_kind")
    T.verify = regressed_verify
    reg_ok = run(T.test_unknown_kind_abstains_exactly, "regressed (mis-certifies)")
    T.verify = REAL

    print("\n3. the OLD guard, for contrast — would it have caught this?")
    for label, val in (("current behaviour  valid=None", None),
                       ("regression         valid=False", False)):
        print(f"  old assert `valid in (False, None)`: {label} -> "
              f"passes: {val in (False, None)}")

    print(f"\nVERDICT: pin is EFFECTIVE = {base_ok and not reg_ok}")
    print("  (passes on real behaviour, fails on the regression it names)")
