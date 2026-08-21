# PARADIGM P23 — Recursive Self-Compression (worked example + decision tree + code skeleton)

Aporia P91, 2026-08-21. Source: taxonomy P23 (round-2; MIP*=RE exemplar).
Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: an instance simulates a strictly smaller instance of itself WITH
STRICT SAVINGS; iteration compounds the saving into qualitatively new power
(verb: SELF-DELEGATE-WITH-SAVINGS; payoff verb:
BOOTSTRAP-CAPABILITY-NO-SINGLE-LEVEL-HAS).

## 1. Worked example — EXECUTED (`paradigm_p23_worked_example.py`)

Strassen recursion as the bootstrapping engine at toy scale (tying to P15's
entrywise-verified rank-7):

- **A.** Recursive Strassen equals naive matmul EXACTLY on random integer
  matrices, n = 2..64 (integer arithmetic, six levels).
- **B.** Multiplication counts equal **7^k exactly** at every level — the
  strictly-decreasing-size lemma's ledger.
- **C.** The compounded exponent: log₂M(2^k)/k = **2.807354922 =
  log₂7 exactly** — an asymptotic capability NO single level possesses,
  created purely by self-delegation with a one-multiplication saving.
- **D.** DECLINE (derived): the identical recursion built on the naive
  8-multiplication block measures exponent **exactly 3** — iteration without
  strict saving bootstraps NOTHING. The decline value is derived (3) and
  direction-stated (equal to naive, not above).
  Verdict: **COMPRESSION-BOOTSTRAPS**.

Meta-note (typed): MIP*=RE-scale bootstrapping (protocols simulating
themselves down to halting-problem encoding) is proof engineering beyond a
pass; the executable ENGINE — strict per-level saving compounding into a new
exponent — is exactly what runs here.

## 2. Decision tree

- Q1: Does the system contain INSTANCES OF ITSELF at smaller size (recursive
  structure, self-similar protocols, self-applicable claims)? — NO: nothing
  to bootstrap; P07 descent handles mere reduction.
- Q1 YES — Q2: Does one level of self-delegation yield a STRICT saving
  (fewer resources than the direct method, provably)? — NO: iteration
  without strict saving compounds to nothing (the exponent-3 decline leg);
  find the saving or exit.
- Q2 YES — Q3: Does the saving COMPOSE under iteration (no per-level
  overhead swamping it; the recursion reaches a base case)? — NO: additive
  overheads can eat geometric savings; account them before claiming power.
- Q3 YES — EXECUTE: verify correctness at every level (two-route), audit the
  exact resource ledger against the derived law, measure the compound
  exponent against its derived value, AND run the no-saving decline leg.
- Distinction guard: P07 descends to DECIDE; P23 delegates to GAIN — if
  capability does not increase, you are doing descent, not compression.

## 3. Code skeleton

```python
def self_compression_attack(direct, delegated, sizes, saving_law, decline_variant):
    """P23 template. Correctness two-route per level; resource ledger exact
    against the derived law; the no-saving variant must bootstrap nothing."""
    for n in sizes:
        assert delegated(n).result == direct(n).result, f"delegation wrong at {n}"
        assert delegated(n).cost == saving_law(n), f"ledger off at {n}"
    gain = compound_exponent(delegated, sizes)
    null = compound_exponent(decline_variant, sizes)
    assert null == direct_exponent(), "decline leg gained power — accounting fault"
    return {"exponent": gain, "decline_exponent": null}
```

## 4. Catalog assignment

Primary: none at catalog level — a meta-paradigm (the taxonomy's own word);
its diagnostic target is Prometheus-internal: can a CLAIM evaluate a smaller
CLAIM (the substrate's P23 question, unprobed). Recast note: fast-arithmetic
kernels inside other attacks (FFT-based sieves) are P23 products consumed
silently. Anti-assignment: everything as a direct attack method; like P14,
the tree gates entry hard (sixth empty primary, ORGANIZING-LENSES family).

## Provenance and honesty

Strassen is 1969 and the exponent arithmetic is exact bookkeeping; the
content is the engine demonstrated with all four certificates (two-route
correctness, exact ledger, derived exponent, derived null) and the
distinction guard separating capability-gain from mere descent.
