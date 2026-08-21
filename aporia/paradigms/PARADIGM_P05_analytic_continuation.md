# PARADIGM P05 — Analytic Continuation (worked example + decision tree + code skeleton)

Aporia P82, 2026-08-21. Source: taxonomy P05; no DR grounding in BACKCORPUS
(checked, not re-fired). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl.

**The move**: extend a function beyond its natural domain; the extension carries
global structure invisible in the defining data (verb: CONTINUE; payoff verb:
EVALUATE-WHERE-THE-SERIES-CANNOT).

## 1. Worked example — EXECUTED (`paradigm_p05_worked_example.py`)

Two legs, each certified by INDEPENDENT computational paths (no value from
memory):

- **A. Continuation values.** zeta(-1), zeta(-3), ..., zeta(-15): the defining
  series diverges at every point; mp.zeta (Riemann-Siegel/Euler-Maclaurin
  machinery) vs -B_2k/2k via mp.bernoulli (a separate recurrence). Worst
  relative disagreement across all 8 points: **1.5e-31** at dps=30.
  zeta(-1) = -1/12 arrives as a COMPUTED agreement of two algorithms, not a
  slogan.
- **B. Local-to-global glue.** Partial Euler products over sieved primes
  (nt_helpers) converge monotonically to the continued object's value
  zeta(2) = pi^2/6 (computed from mp.pi): |rel-1| = 1.3e-4 at X=1e3 down to
  5.9e-9 at X=1e7, monotone at every checkpoint.

Verdict: **CONTINUATION-EXACT**. The paradigm made operational: the continued
object is the ONLY thing that both exists where the series diverges and is
what the local factors glue to.

## 2. Decision tree

- Q1: Is your data LOCAL (finitely many coefficients, local factors, a
  function on part of its domain)? — NO: nothing to continue.
- Q1 YES — Q2: Does a continuation THEOREM exist for your object class
  (L-functions, theta-completion, Borel summability class)? — NO: numerical
  extrapolation (Pade, resurgence) may still act as a CONJECTURE GENERATOR,
  but its outputs are hypotheses, never values. Route accordingly.
- Q2 YES — Q3: Can you compute the continued values by TWO independent routes
  (functional equation vs series acceleration; two libraries; formula vs
  quadrature)? — NO: a single-path continued value is unauditable; treat as
  provisional and mark it.
- Q3 YES — EXECUTE: certify path agreement at working precision, THEN read
  global structure (zeros, poles, special values) from the continued object.

## 3. Code skeleton

```python
def continuation_attack(local_data, path_a, path_b, probe_points, tol=1e-25):
    """P05 template. Dual-path certification precedes any use of continued
    values; the agreement IS the certificate (independent-instruments rule)."""
    certified = []
    for s in probe_points:
        va, vb = path_a(local_data, s), path_b(local_data, s)
        rel = abs(va - vb) / max(abs(vb), 1e-300)
        assert rel < tol, f"paths disagree at {s}: {rel:.1e} — not certified"
        certified.append((s, va))
    return certified          # only now read global structure from these
```

## 4. Catalog assignment

Primary: CAT-MATH-0060/0370 (zeta continuation is the arena), 0165 (moments of
the continued object), 0063 (L(E,1) IS a continued value), 0260 (Artin
L-continuation), 0476/0477 (derivative at continued zeros). Secondary: 0057/0058
(circle-method generating functions). Anti-assignment: 0129/0154-class finite
combinatorics and 0316 (amicable pairs) — nothing infinite to continue (Q1=NO).

## Provenance and honesty

Both legs are settled mathematics; the certificate pattern (dual independent
paths, monotone glue) is the transferable content, plus the demonstrated fact
that our toolchain (mpmath + nt_helpers sieve) can certify continuations to
1e-31 — the precision budget future attacks can spend.
