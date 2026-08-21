# PARADIGM P10 — Formal Verification (worked example + decision tree + code skeleton)

Aporia P85, 2026-08-21. Source: taxonomy P10; no DR grounding in BACKCORPUS
(checked). Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: machine-check every inference step — the kernel is the verifier
(verb: KERNEL-CHECK; payoff verb: TRUST-A-PROOF-WITHOUT-TRUSTING-ITS-AUTHOR).

## 1. Worked example — EXECUTED via CROSS-CHANNEL BIND (`paradigm_p10_worked_example.py`)

**SYNERGY, called out per James's standing ask**: instead of building a second
Lean wrapper, this example binds to **Techne's forged proof-checker oracle**
(`prometheus_math/lean_oracle.py`, Techne cycle 015 — Lean 4.30.0 via elan,
three-valued PROVED/REFUTED/ERROR by design). The intentional overlap between
the loops, cashed: Aporia consumed the instrument the other channel forged.

Five claims through the real kernel, verdicts exact (**LANE-BINDS**):
- `(5*4*3)/(3*2*1) = 10` — P09's checker-gate value, kernel-certified (PROVED).
- `1^2+1^2+1^2 = 3*1*1*1` — P07's Markov base case (PROVED).
- `forall n : Nat, n + 0 = n` — an inference, not a computation (PROVED).
- `... = 11` — REFUTED (the lane has teeth).
- gibberish tactic — ERROR, not REFUTED (three-valued semantics honored).

The three-valued design proved itself TWICE: the deliberate gibberish case,
and a live one — the first draft used `Nat.choose`, which is Mathlib-only, and
the oracle returned ERROR ("Unknown constant"), never conflating cannot-tell
with false. Exactly the phantom-failure pathology Techne built the lane to
avoid, observed from the consumer side.

## 2. Decision tree

- Q1: Is there a PROOF (or proof sketch) whose correctness is the question?
  — NO: kernels check proofs, not truths; use P09 for finite facts.
- Q1 YES — Q2: Is the statement FORMALIZABLE in the available library scope
  (core vs Mathlib — probe the constant availability FIRST; the worked
  example's Nat.choose lesson)? — NO: autoformalization is a conjecture
  generator; route the gap as typed residue naming the missing library.
- Q2 YES — Q3: Is the proof effort bounded (decide/omega/rfl-class, or a
  known tactic path)? — NO: AI-prover escalation (the taxonomy's pipeline)
  or park; do not hand-fight the kernel in a loop pass.
- Q3 YES — EXECUTE: run the three-valued lane; PROVED is a certificate,
  REFUTED is a counterexample-backed kill, ERROR is a TOOLING fact — never
  read ERROR as either verdict.

## 3. Code skeleton

```python
def formal_attack(claims, oracle_check):
    """P10 template. Every claim set includes a mandatory known-REFUTED and a
    mandatory known-ERROR case: a lane that has never disagreed with you is
    an unverified lane (the can-fire invariant, kernel edition)."""
    results = {}
    teeth = errors = 0
    for name, stmt, proof, expected in claims:
        v = oracle_check(stmt, proof)
        results[name] = (v.status, expected, v.status == expected)
        teeth += (expected == "REFUTED")
        errors += (expected == "ERROR")
    assert teeth >= 1 and errors >= 1, "claim set lacks its teeth/error controls"
    return results
```

## 4. Catalog assignment

Primary: verdict-lane duty for ANY catalog attack producing a decidable
arithmetic identity (0129/0154 recursions, 0137 congruence facts, exact pins
in nt_helpers-class helpers — kernel-certify the pinned values). Secondary:
0332 (knot invariant identities are formalizable). Anti-assignment: all
distributional/statistical rows (0057-0062, 0165, 0175, 0348-class, 0478) —
kernels certify proofs, not p-values (Q1=NO).

## Provenance and honesty

The five facts are trivial; the content is the BIND (one channel consuming
another's forged instrument — the serendipity James is farming, realized), the
mandatory teeth/error controls in the template, and the live demonstration
that library scope (core vs Mathlib) is the first formalization gate. Techne's
oracle carries toolchain + source hash per verdict; provenance rides along.
