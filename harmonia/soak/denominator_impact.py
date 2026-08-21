"""Does an abstaining cid shift a reported score? (soak P36)

P35's falsifier, and the load-bearing assumption under FOUR passes (P32-P35), all
of which concluded "coverage loss, benign". That verdict holds only if abstentions
are excluded from the denominator rather than counted as misses.

Reading grading_oracle: `if vres.get("valid") is not None: n_verifiable += 1`, and
verified_rate = n_verified / n_verifiable. So abstentions are EXCLUDED, and
n_verifiable is REPORTED next to the rate.

Reading is not measuring (P26's lesson). This runs the real grader, then removes a
cid from the registry IN-PROCESS -- no file is touched -- and compares.

v1 mutated a duplicate z3_backend module object and reported 0% change on all
five removals. A uniform null across every case was the tell, same shape as
P27's 0/140 control.
"""
import sys

sys.path.insert(0, ".")
# MUST be the module grading_oracle resolves. A bare `import z3_backend` with
# harmonia/experiments on sys.path creates a SECOND module object with its own
# registry dict, and mutating that one changes nothing (HARMA-P36, self-caught).
from harmonia.experiments import z3_backend         # noqa: E402
from harmonia.services.grading_oracle import grade_reasoner  # noqa: E402


def perfect(p):
    """A reasoner that always answers correctly: isolates verifier behaviour."""
    return p.ground_truth, {}


def r6(res):
    t = res["per_tier"]["R6"]
    iv = t["independently_verified"]
    return t["n"], t["pass_rate"], iv["n_verifiable"], iv["n_verified"], iv["verified_rate"]


print("BASELINE (all 5 cids registered):")
n, pr, nv, nvd, vr = r6(grade_reasoner(perfect, tiers=["R6"]))
print(f"  n={n}  pass_rate={pr}   n_verifiable={nv}  n_verified={nvd}  verified_rate={vr}")

saved = dict(z3_backend.CONJECTURE_REGISTRY)
print(f"\nremoving ONE cid from the registry at a time (in-process; no file touched):")
print(f"  {'cid removed':26s} {'pass_rate':>10s} {'n_verifiable':>13s} {'verified_rate':>14s}  denom loss")
print("  " + "-" * 84)
try:
    for cid in list(saved):
        z3_backend.CONJECTURE_REGISTRY.clear()
        z3_backend.CONJECTURE_REGISTRY.update({k: v for k, v in saved.items() if k != cid})
        n2, pr2, nv2, nvd2, vr2 = r6(grade_reasoner(perfect, tiers=["R6"]))
        loss = nv - nv2
        print(f"  {cid:26s} {str(pr2):>10s} {nv2:>13d} {str(vr2):>14s}  -{loss} ({100*loss/nv:.0f}%)")
finally:
    z3_backend.CONJECTURE_REGISTRY.clear()
    z3_backend.CONJECTURE_REGISTRY.update(saved)

n3, pr3, nv3, nvd3, vr3 = r6(grade_reasoner(perfect, tiers=["R6"]))
print(f"\nregistry restored: n_verifiable={nv3} (baseline {nv}) -> {'OK' if nv3 == nv else 'MISMATCH'}")
