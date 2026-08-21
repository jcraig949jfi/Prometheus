# PARADIGM P09 — Exhaustive Computation (worked example + decision tree + code skeleton)

Aporia P84, 2026-08-21. Source: taxonomy P09; no DR grounding in BACKCORPUS
(checked, not re-fired). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl.

**The move**: reduce to finitely many cases and verify each by machine — the
computer IS the proof (verb: ENUMERATE-COMPLETELY; payoff verb:
PROVE-BY-FINITE-CHECK).

## 1. Worked example — EXECUTED (`paradigm_p09_worked_example.py`)

A complete machine proof of **R(3,3) = 6**, both directions, full enumeration,
no sampling, no symmetry shortcuts (the exhaustion is the point):

- Instrument gate first: the all-red K5 must report C(5,3) = 10 monochromatic
  triangles — counter certified on an exact known before any enumeration.
- **LOWER**: all 1,024 colorings of K5 enumerated; **12** contain no
  monochromatic triangle → R(3,3) > 5. The raw count 12 is reported as an
  observable — it is exactly the classical pentagonal family (C5/C5-bar under
  rotation/reflection/swap), ARRIVING from the enumeration rather than assumed.
- **UPPER**: all 32,768 colorings of K6 enumerated; **0** lack a monochromatic
  triangle → R(3,3) ≤ 6. Zero exceptions over the full space is the theorem.

Verdict: **EXHAUSTION-PROVES**. This is the Four-Color/Kepler paradigm at toy
scale with every structural element present: finite reduction, certified
counter, complete enumeration, machine-checkable record.

## 2. Decision tree

- Q1: Can the statement be REDUCED to finitely many machine-checkable cases
  (directly, or via a reduction theorem bounding the search)? — NO: no
  exhaustion exists; P08 (probabilistic) or P07 (descent) may create the
  bound first.
- Q1 YES — Q2: Is the case count within compute budget (with SAT/MIP/symmetry
  reduction if needed)? — NO: record the exact gap (count vs budget) as a
  typed residue — exhaustions age well as hardware and solvers improve.
- Q2 YES — Q3: Is the per-case CHECKER certified on exact knowns (the checker
  is the proof's weakest link — a broken checker exhausts nothing)? — NO:
  gate it first, always.
- Q3 YES — EXECUTE: enumerate COMPLETELY, record totals and exceptional counts
  raw; any symmetry reduction used must itself be verified (orbit sizes sum
  to the full space) or the proof has a silent hole.
- Post-gate: the run's artifact must let a stranger re-verify without re-
  enumerating (counts, checksums, exceptional cases listed).

## 3. Code skeleton

```python
def exhaustive_attack(cases, checker, gates, expect_exceptions=0):
    """P09 template. Checker certified before enumeration; totals recorded
    raw; the artifact IS the proof, so it must be re-verifiable."""
    for known_case, known_value in gates:
        assert checker(known_case) == known_value, "checker gate FAILS — exhaust nothing"
    exceptions = [c for c in cases if not checker(c)]
    record = {"total": len(cases), "exceptions": len(exceptions),
              "exception_list": exceptions[:100]}
    record["verdict"] = ("PROVEN" if len(exceptions) == expect_exceptions
                         else "REFUTED-OR-ENCODING-FAULT")
    return record
```

## 4. Catalog assignment

Primary: CAT-MATH-0137 (the Agoh-Giuga conjunction battery IS this paradigm —
already executed P68), 0129/0154 (finite verifications), 0478 (archive-wide
simplicity census — **the natural batch-3 ROUTING candidate**: its spec is
exhaustive-computation shaped and its attack, once Elenchus clears the spec,
should be designed by walking THIS tree: Q1 finite rows yes, Q2 224k vectors
yes, Q3 gap-checker gated on a constructed near-degenerate pair). Secondary:
0057/0058/0479/0483/0485 (sieve verifications are bounded exhaustions).
Anti-assignment: 0060/0370 (RH-class — no finite reduction exists; Q1=NO and
THAT is the famous difficulty).

## Provenance and honesty

R(3,3)=6 dates to 1930; the pass's content is the complete, gated,
re-verifiable enumeration pattern at a scale where every structural element of
the big exhaustive proofs (certified checker, full-space coverage, raw
exceptional counts) is present and auditable in seconds. The 12 arriving as an
observable — not an assumption — is the pattern's bonus: exhaustion measures
structure it was not asked for.
