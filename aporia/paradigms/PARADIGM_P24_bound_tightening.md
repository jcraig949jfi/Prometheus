# PARADIGM P24 — Quantitative Bound-Tightening (worked example + decision tree + code skeleton)

Aporia P91, 2026-08-21. Source: taxonomy P24 (round-2; ternary-Goldbach/
Helfgott exemplar). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl.

**The move**: an analytic argument holds for n ≥ n₀; computation closes
[1, n₀); iterate on n₀ until the pincer meets (verb: TIGHTEN-THE-THRESHOLD;
payoff verb: CLOSE-THEOREMS-BY-PINCER).

## 1. Worked example — EXECUTED, a COMPLETE toy pincer
(`paradigm_p24_worked_example.py`)

Bertrand's postulate closed end-to-end by the Erdős machine:

- Three finite-range gates, each exact: the binomial lower bound
  C(2n,n) ≥ 4ⁿ/(2n+1) in integers (n ≤ 500); Erdős's key lemma (primes in
  (2n/3, n] never divide C(2n,n)) by direct factorization (n ≤ 500); the
  primorial bound ∏p ≤ 4ˣ to 10⁶ (max log-ratio 0.72), its inductive
  general case CITED as the analytic content.
- The threshold DERIVED, not assumed: the no-prime assumption self-destructs
  once 4^(n/3) > (2n+1)(2n)^√(2n) — computed **n₀ = 467**, the classical
  Erdős value ARRIVING from the inequality.
- Computational leg: a prime in (n, 2n] verified directly for every n ≤ 467.
- Convention flip caught at n=1: the postulate closes at 2n (p ≤ 2n); the
  strict interval excluded p=2 — the campaign's interval-convention doctrine
  firing once more, at the smallest possible case.
  Verdict: **PINCER-CLOSES**.

Honesty boundary (in the results file): the analytic half is a faithful
MINIATURE — its inductions are computationally gated on finite ranges and
cited beyond; kernel-formalizing them is the P10-bind escalation. The
paradigm at research scale (Helfgott's 90-year push) differs in effort, not
in shape.

## 2. Decision tree

- Q1: Is the statement PARAMETRIZED with an in-principle analytic argument
  for large parameters (sufficiently-large theorems, effective bounds)?
  — NO: nothing to tighten.
- Q1 YES — Q2: Is the current n₀ COMPUTABLE-RANGE or can any ingredient
  (zero-free region, explicit constant, inequality) be sharpened to bring
  it there? — NO: record the gap SIZE (n₀ vs compute ceiling) as typed
  residue — P24 programs are multi-decade and the gap number is the
  program's progress metric.
- Q2 YES — Q3: Are the analytic ingredients GATED (each inequality verified
  on its finite range, its general case cited or proven, its convention
  flips built in)? — NO: an ungated ingredient poisons the pincer at the
  seam; gate first.
- Q3 YES — EXECUTE: derive n₀ from the ingredients (never transcribe it),
  close [1, n₀] by computation, and state the honesty boundary between
  computed and cited — the pincer's seam is where errors hide.

## 3. Code skeleton

```python
def pincer_attack(ingredients, derive_threshold, verify_below, gate_ranges):
    """P24 template. Every ingredient gated on its finite range; the
    threshold derived; the seam stated."""
    for ing in ingredients:
        assert ing.verify_on(gate_ranges[ing.name]), f"{ing.name} gate FAILS"
    n0 = derive_threshold(ingredients)         # computed, never transcribed
    assert verify_below(n0), "computational leg has a hole"
    return {"n0": n0, "closed": True,
            "seam": [ing.name for ing in ingredients if ing.cited_beyond_gate]}
```

## 4. Catalog assignment

Primary: CAT-MATH-0057/0058 (Goldbach/twins ARE the paradigm's home range —
the exemplar's siblings), 0484 (explicit Mertens bounds are P24 ingredients),
0485/0479 (explicit-formula thresholds), 0370/0060 (zero-free regions are
THE research-scale ingredient). Secondary: 0136 (effective abc would be
P24's crown). The substrate note: every fire that tightens a numerical
threshold is a P24 step — the paradigm as progress metric. Anti-assignment:
0129/0154/0332 (nothing parametrized to tighten).

## Provenance and honesty

Bertrand-via-Erdős is a textbook proof; the content is the pincer executed
END-TO-END with every ingredient gated, the threshold arriving at the
classical 467 from in-code derivation, the n=1 convention catch, and the
explicitly drawn computed/cited seam — the exact discipline research-scale
P24 programs live or die by.
