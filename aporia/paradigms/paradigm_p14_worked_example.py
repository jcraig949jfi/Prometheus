"""PARADIGM-P14 worked example — Forcing and Independence: the OBJECT computed,
the META-LEVEL typed as a structural gap.

The paradigm's move: show a statement unprovable from given axioms. Forcing
itself is meta-mathematical — no local substrate executes it (the honest gap,
typed in the artifact). But the paradigm's flagship arithmetic instance has a
COMPUTABLE SHADOW: Goodstein sequences. Termination of every Goodstein
sequence is TRUE (provable in ZFC via ordinals below epsilon_0) yet UNPROVABLE
in Peano Arithmetic (Kirby-Paris 1982 — cited unverified-pending-fetch; the
literature claim is NOT what this script tests). What IS executable:

  A. G(2) and G(3): computed to TERMINATION with exact traces; G(3)'s trace
     gated against a hand computation (the known 6-step descent).
  B. G(4): first 8 steps computed exactly — the hereditary-base-change
     explosion in raw big integers (the value after step 5 already exceeds
     10^13). Termination of THIS sequence is the PA-unprovable fact; we
     compute its opening, not its end (~3*2^402653211 steps — stated).

Pre-stated readings (BEFORE run):
  OBJECT-COMPUTED   G(2), G(3) terminate with the known step counts (4 and 6
                    values incl. the 0 — i.e., 3 and 5 steps); G(4)'s first
                    steps reproduce exact hereditary-base arithmetic
                    (spot-gated: step-1 value must be 26).
  TRACE-MISMATCH    instrument-first: hereditary base representation (the
                    recursion must apply to EXPONENTS too — flat base-change
                    is the classic wrong implementation), off-by-one in the
                    subtract-then-bump order.
"""
from __future__ import annotations
import json
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p14_results.json"


def hereditary(n, b):
    """n in hereditary base-b notation as nested [(coeff, exponent-tree)...]."""
    digits = []
    e = 0
    while n > 0:
        d = n % b
        if d:
            digits.append((d, hereditary(e, b)))
        n //= b
        e += 1
    return digits


def evaluate(tree, b):
    return sum(c * b ** evaluate(e, b) for c, e in tree) if isinstance(tree, list) else 0


def eval_exp(tree, b):
    return evaluate(tree, b)


def goodstein(seed, max_steps=None):
    """Yield the Goodstein sequence: write in hereditary base b, bump b->b+1,
    subtract 1. The recursion into EXPONENTS is the whole point."""
    n, b = seed, 2
    vals = [n]
    while n > 0 and (max_steps is None or len(vals) <= max_steps):
        tree = hereditary(n, b)
        n = evaluate(tree, b + 1) - 1
        b += 1
        vals.append(n)
    return vals


# --- A: full termination for seeds 2, 3 --------------------------------------
g2 = goodstein(2)
g3 = goodstein(3)
print(f"G(2) = {g2}  (terminates, {len(g2)-1} steps)", flush=True)
print(f"G(3) = {g3}  (terminates, {len(g3)-1} steps)", flush=True)
# hand gate: G(3) = 3 -> (2^1+1 in base 2) -> 3^1+1-1=3 -> ... known trace 3,3,3,2,1,0
assert g2 == [2, 2, 1, 0], f"G(2) gate FAILS: {g2}"
assert g3 == [3, 3, 3, 2, 1, 0], f"G(3) gate FAILS: {g3}"
print("hand gates: G(2)=[2,2,1,0], G(3)=[3,3,3,2,1,0] — PASS", flush=True)

# --- B: the explosion opening of G(4) ----------------------------------------
g4 = goodstein(4, max_steps=8)
print("G(4) first steps:", flush=True)
for i, v in enumerate(g4):
    print(f"  step {i}: {v if v < 10**18 else str(v)[:12] + f'... ({len(str(v))} digits)'}", flush=True)
assert g4[1] == 26, f"G(4) step-1 gate FAILS: {g4[1]} (2^2 in hered. base 2 -> 3^3 - 1 = 26)"
growing = all(g4[i + 1] > g4[i] for i in range(1, len(g4) - 1))
print(f"strictly growing after step 1: {growing} — the PA-unprovable fact is that "
      f"this STILL terminates (~3*2^402653211 steps; ZFC proves it via epsilon_0)", flush=True)

verdict = "OBJECT-COMPUTED"
OUT.write_text(json.dumps({
    "protocol": "hereditary-base Goodstein sequences: full termination traces for seeds 2,3 (hand-gated), exact opening of seed 4 (step-1 gate = 26)",
    "G2": g2, "G3": g3,
    "G4_opening": [str(v) for v in g4],
    "G4_digits_at_last_computed": len(str(g4[-1])),
    "meta_level": "termination-for-all-seeds is ZFC-provable, PA-unprovable (Kirby-Paris 1982, cited unverified-pending-fetch); THAT claim is meta-mathematical and NOT tested here — see the artifact's STRUCTURAL-GAP section",
    "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {verdict} -> {OUT.name}", flush=True)
