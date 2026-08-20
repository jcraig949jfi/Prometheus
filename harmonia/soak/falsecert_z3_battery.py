"""False-certification battery for the z3 backend (Harmonia-A soak P7).

test_verifier_z3.py pins that an undecidable universal returns "unknown" rather
than a fabricated verdict -- on a handful of hand-picked cases. This widens that
into a calibration battery whose pass criterion is the property that actually
matters for a selection-side instrument:

    z3 may abstain freely, but it must NEVER certify a falsehood as "proved",
    and every counterexample it supplies for "refuted" must actually falsify.

Every verdict is independently validated here:
  proved   -> brute-force search for a counterexample over a bounded range.
              A hit is a FALSE CERTIFICATION (the severe failure).
  refuted  -> evaluate the predicate at z3's own counterexample. If it does not
              falsify, the witness is FABRICATED.
  unknown  -> always acceptable; counted so that "0 false certifications" cannot
              be reported vacuously (P4/P5/P6 discipline: a clean result needs a
              decided-count beside it).

Ground truth is carried per case and is independently checkable, not asserted.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import z3
from harmonia.experiments.z3_backend import certify_universal

RANGE = range(-2000, 2001)

# (label, predicate_builder, python_pred, domain_builder, ground_truth)
CASES = [
    ("n^2 >= 0",                 lambda n: n*n >= 0,            lambda n: n*n >= 0,          None, True),
    ("n^2+n even",               lambda n: (n*n+n) % 2 == 0,    lambda n: (n*n+n) % 2 == 0,  None, True),
    ("2n even",                  lambda n: (2*n) % 2 == 0,      lambda n: (2*n) % 2 == 0,    None, True),
    ("n^2 >= n (all ints)",      lambda n: n*n >= n,            lambda n: n*n >= n,          None, True),
    ("(n+1)^2 = n^2+2n+1",       lambda n: (n+1)*(n+1) == n*n+2*n+1,
                                 lambda n: (n+1)**2 == n**2+2*n+1,                           None, True),
    ("n >= 0 (FALSE)",           lambda n: n >= 0,              lambda n: n >= 0,            None, False),
    ("n != 7 (FALSE)",           lambda n: n != 7,              lambda n: n != 7,            None, False),
    ("n^2 != 4 (FALSE)",         lambda n: n*n != 4,            lambda n: n*n != 4,          None, False),
    ("n^2 > n (FALSE at 0,1)",   lambda n: n*n > n,             lambda n: n*n > n,           None, False),
    ("3n != 6 (FALSE)",          lambda n: 3*n != 6,            lambda n: 3*n != 6,          None, False),
    ("n>=0 => n^2>=n",           lambda n: n*n >= n,            lambda n: n*n >= n,
                                 lambda n: n >= 0,                                            True),
    ("n>0 => n^2 >= 2n (FALSE)", lambda n: n*n >= 2*n,          lambda n: n*n >= 2*n,
                                 lambda n: n > 0,                                             False),
]

def brute_counterexample(pred, dom):
    for v in RANGE:
        if dom and not dom(v):
            continue
        try:
            if not pred(v):
                return v
        except Exception:
            continue
    return None

decided = abstained = 0
false_cert = []
fabricated = []
rows = []
for label, zb, pp, dbld, truth in CASES:
    res = certify_universal(zb, dbld)
    v = res["verdict"]
    note = ""
    if v == "unknown":
        abstained += 1
        note = "abstained (always acceptable)"
    else:
        decided += 1
        if v == "proved":
            cex = brute_counterexample(pp, dbld)
            if cex is not None:
                false_cert.append((label, cex)); note = f"FALSE CERTIFICATION: counterexample n={cex}"
            else:
                note = "no counterexample found in range — consistent"
        elif v == "refuted":
            c = res.get("counterexample")
            if c is None:
                note = "refuted without a witness"
            elif dbld is not None and not dbld(c):
                fabricated.append((label, c)); note = f"WITNESS OUT OF DOMAIN: n={c}"
            elif pp(c):
                fabricated.append((label, c)); note = f"FABRICATED WITNESS: n={c} does NOT falsify"
            else:
                note = f"witness n={c} validated"
    agree = "" if v == "unknown" else ("  [matches ground truth]" if (v == "proved") == truth else "  [DISAGREES with ground truth]")
    rows.append((label, v, note, agree))

for label, v, note, agree in rows:
    print(f"  {label:26s} {v:8s} {note}{agree}")
print(f"\nTRIAGE: {decided} decided, {abstained} abstained, {len(CASES)} total")
print(f"FALSE CERTIFICATIONS : {len(false_cert)}  {false_cert if false_cert else ''}")
print(f"FABRICATED WITNESSES : {len(fabricated)}  {fabricated if fabricated else ''}")
print(f"VERDICT: {'CLEAN' if not false_cert and not fabricated else 'INSTRUMENT FAILURE'}"
      f" (meaningful only because {decided} cases were actually decided)")
