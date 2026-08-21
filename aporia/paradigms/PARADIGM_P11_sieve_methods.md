# PARADIGM P11 — Sieve Methods (worked example + decision tree + code skeleton)

Aporia P85, 2026-08-21. Source: taxonomy P11; no DR grounding in BACKCORPUS
(checked). Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: filter a large set by local conditions; the structured residue is
the object (verb: SIEVE; payoff verb: COUNT-WHAT-SURVIVES-LOCAL-CONDITIONS).

## 1. Worked example — EXECUTED (`paradigm_p11_worked_example.py`)

The Legendre sieve — the ur-sieve — run EXACTLY and reconciled three ways at
three scales, integer-exact with zero tolerance:

- Identity (derived in-code): φ(N, primes ≤ √N) = π(N) − π(√N) + 1, computed
  by (a) inclusion-exclusion, (b) direct residue count, (c) the π-identity.
- Hand gate first: N=100 → **22 = 22 = 22**.
- N=1e4: **1,205** three ways. N=1e5: **9,528**. N=1e6: **78,331** — with 168
  sieving primes. Verdict: **SIEVE-EXACT**.

**Instrument-first catch (the pass's teaching)**: the first draft enumerated
ALL subsets of the sieving primes — 2^168 at N=1e6 — and hung; the d>N break
pruned products, not the enumeration. The fix is the RECURSIVE Legendre form
φ(x,a) = φ(x,a−1) − φ(x/pₐ,a−1), which IS the same inclusion-exclusion with
the pruning built into the recursion tree. The mathematical identity and the
feasible algorithm are different objects; sieve theory's whole history
(Brun's combinatorial truncations, Selberg's quadratic weights) is the
management of exactly this gap — our bug was the subject matter in miniature.

## 2. Decision tree

- Q1: Is the target a COUNT or DENSITY of elements avoiding local conditions
  (divisibility, congruence, reduction properties)? — NO: sieves count
  survivors; structural questions need other paradigms.
- Q1 YES — Q2: Are the local conditions INDEPENDENT-ish (density of the
  sieved set factors approximately over conditions)? — NO: strongly coupled
  conditions break sieve axioms; model the coupling first.
- Q2 YES — Q3: Is EXACT inclusion-exclusion feasible (few conditions, or a
  pruned recursion)? — YES: run it exact, reconcile against a direct count
  on a subrange (the three-way gate). — NO: TRUNCATE (Brun/Selberg class),
  and the truncation error becomes a stated term — never silently dropped;
  remember the parity barrier bounds what sieves alone can see.
- EXECUTE with the three-way reconciliation wherever a direct count is
  affordable; a sieve that has never been reconciled is a formula, not an
  instrument.

## 3. Code skeleton

```python
def sieve_attack(N, conditions, direct_count_fn=None):
    """P11 template. Exact pruned recursion where feasible; three-way
    reconciliation (recursion vs direct vs identity) on affordable ranges
    BEFORE trusting any truncated extension."""
    def phi(x, a):
        if a == 0 or x == 0:
            return x
        return phi(x, a - 1) - phi(x // conditions[a - 1], a - 1)
    survivors = phi(N, len(conditions))
    if direct_count_fn is not None:
        direct = direct_count_fn(N, conditions)
        assert survivors == direct, f"sieve unreconciled: {survivors} vs {direct}"
    return survivors
```

## 4. Catalog assignment

Primary: CAT-MATH-0057/0058 (Brun/Selberg territory — twin and Goldbach
counts), 0065 (gap statistics ride sieved sets), 0479/0483/0485 (race and
sign-change counts are sieved-set functionals), 0482 (form-representable
primes are a sieve residue — batch-4 native). Secondary: 0129/0151 (Chowla —
sieve-adjacent parity territory; the parity barrier is the WALL there, worth
naming in any 0151 attack). Anti-assignment: 0332/0334 (knot invariants —
no local divisibility structure; Q1=NO).

## Provenance and honesty

Legendre's identity is 1808-vintage; the content is the three-way exact
reconciliation pattern, the recursive-vs-naive lesson (the gap between
identity and algorithm IS sieve theory's subject), and the honest note that
everything here is the EXACT regime — the paradigm's power tools (Brun,
Selberg, Maynard) live in the truncated regime this example gates but does
not enter.
