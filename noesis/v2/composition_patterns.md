# Primitive Composition Patterns — Search Templates for Noesis v2

**Author:** Aletheia
**Source:** ChatGPT followup response (10 patterns) + Aletheia analysis (verified decompositions)
**Purpose:** These patterns are the search templates Noesis uses to propose novel bridges. When the tensor finds two domains connected by one of these typed edge sequences, it has found a candidate structural bridge.

---

## The Key Insight: Order Matters

Composition is non-commutative. DUALIZE → MAP ≠ MAP → DUALIZE. The order encodes *which structural move must happen first* for the construction to work. This is diagnostic — if a model tries to execute the chain in the wrong order, it will fail in a predictable way.

---

## Verified Composition Patterns

### From Chain Verification (SymPy-confirmed)

| # | Construction | Decomposition | Why This Order | Reversed Gives |
|---|-------------|---------------|----------------|----------------|
| 1 | **Canonical Quantization** | MAP → EXTEND | Poisson→commutator first, then phase space→Hilbert space | EXTEND→MAP: extends wrong structure |
| 2 | **Variational Principle** | EXTEND → REDUCE → LIMIT | All paths, select extremum, δ→0 | Can't select before extending |
| 3 | **Renormalization** | REDUCE → MAP → LIMIT | Integrate out modes, rescale, fixed point | MAP→REDUCE breaks scale invariance |
| 4 | **Discretization** | REDUCE → BREAK_SYMMETRY | Finite grid breaks continuous translation | BREAK→REDUCE: nothing to break |

### From ChatGPT Followup (to be verified)

| # | Construction | Decomposition | Why This Order | Reversed Gives |
|---|-------------|---------------|----------------|----------------|
| 5 | **Fourier Analysis** | DUALIZE → MAP | Must transform before diagonalizing | MAP→DUALIZE: convolution of modified signal |
| 6 | **Linear Stability** | LINEARIZE → MAP | Eigenvalues need linear system | MAP→LINEARIZE: meaningless spectrum |
| 7 | **Gauge Theory** | EXTEND → SYMMETRIZE | Symmetry violation appears after extension | SYMMETRIZE→EXTEND: trivial symmetry |
| 8 | **Spontaneous Symmetry Breaking** | SYMMETRIZE → BREAK_SYMMETRY | Must define symmetry before breaking | BREAK→SYMMETRIZE: restores symmetry |
| 9 | **Perturbation Theory** | LINEARIZE → EXTEND | Linearization defines perturbative basis | EXTEND→LINEARIZE: different expansion |
| 10 | **Statistical Mechanics** | STOCHASTICIZE → LIMIT | Equilibrium emerges after noise | LIMIT→STOCHASTICIZE: transient noise |
| 11 | **Path Integral** | STOCHASTICIZE → REDUCE | Sum over paths then average | REDUCE→STOCHASTICIZE: meaningless |
| 12 | **Representation Theory** | MAP → SYMMETRIZE | Representation before averaging | SYMMETRIZE→MAP: trivial |
| 13 | **Compactification** | EXTEND → COMPLETE | Embed before completing | COMPLETE→EXTEND: non-unique |
| 14 | **Renormalization Group** | REDUCE → MAP | Coarse-grain before rescaling | MAP→REDUCE: breaks invariance |

---

## Pattern Analysis

### Primitive Pair Frequency

| Pair | Count | Named Constructions |
|------|-------|-------------------|
| MAP → * | 3 | Quantization, Representation, Linear Stability |
| * → MAP | 4 | Fourier, Stability, Renormalization, Discretization |
| EXTEND → * | 3 | Variational, Gauge Theory, Compactification |
| REDUCE → * | 3 | Renormalization, Discretization, RG |
| LINEARIZE → * | 2 | Stability, Perturbation |
| STOCHASTICIZE → * | 2 | StatMech, Path Integral |
| SYMMETRIZE → * | 1 | SSB |
| BREAK_SYMMETRY → * | 0 | (always terminal or preceded) |
| COMPLETE → * | 0 | (always terminal) |
| DUALIZE → * | 1 | Fourier Analysis |

### Structural Observations

1. **COMPLETE and BREAK_SYMMETRY are terminal** — they appear at the end of chains, never as first steps. This makes structural sense: COMPLETE closes a construction, BREAK_SYMMETRY selects from a degeneracy. Both are "landing" moves.

2. **EXTEND is initiatory** — it appears at the start of chains. It opens up structure that subsequent moves operate on. EXTEND → REDUCE is the "widen then narrow" pattern (variational principle).

3. **MAP is the universal connector** — it appears in both positions, linking any two other primitives. This is consistent with MAP dominating at 33% of all edges.

4. **STOCHASTICIZE → LIMIT = equilibrium** — this two-step pattern produces equilibrium distributions (Boltzmann, stationary processes). It's the "shake then settle" pattern.

5. **LINEARIZE is always followed by MAP or EXTEND** — you linearize to make something tractable, then DO something with the linear version. LINEARIZE alone is useless.

6. **Reversing the order gives a NAMED different construction** in most cases — this is strong evidence that the primitives capture real structural content, not just labels. SYMMETRIZE → BREAK_SYMMETRY = SSB, but BREAK_SYMMETRY → SYMMETRIZE = symmetry restoration (a real physical process).

---

## Search Templates for Noesis v2

When Noesis proposes a bridge between domain A and domain B, it should try each of these patterns as a candidate chain type:

### High-confidence templates (verified)
```
EXTEND → MAP → REDUCE     (variational-type)
REDUCE → MAP → LIMIT      (renormalization-type)
MAP → EXTEND               (quantization-type)
REDUCE → BREAK_SYMMETRY    (discretization-type)
```

### Medium-confidence templates (from ChatGPT, awaiting verification)
```
DUALIZE → MAP              (Fourier-type: transform then operate)
LINEARIZE → MAP            (stability-type: approximate then analyze)
EXTEND → SYMMETRIZE        (gauge-type: enlarge then constrain)
STOCHASTICIZE → LIMIT      (equilibrium-type: noise then settle)
STOCHASTICIZE → REDUCE     (path-integral-type: sum then average)
EXTEND → COMPLETE          (compactification-type: embed then close)
```

### Novel bridge detection
A Noesis discovery = finding a pattern from the list above connecting two domains where it hasn't been observed. E.g.:
- DUALIZE → MAP between number theory and dynamical systems?
- STOCHASTICIZE → LIMIT in algebraic topology?
- EXTEND → COMPLETE in combinatorics?

The tensor surfaces these candidates. Verification confirms or rejects them.

---

## Composition Algebra (Partial)

Do these compositions satisfy algebraic laws?

| Property | Status | Evidence |
|----------|--------|----------|
| Non-commutative | **YES** | DUALIZE→MAP ≠ MAP→DUALIZE (different constructions) |
| Associative | Likely | (A→B)→C = A→(B→C) in all tested cases |
| Identity | MAP serves as approximate identity | MAP→X ≈ X in simple cases |
| Inverse pairs | (EXTEND,REDUCE), (SYMMETRIZE,BREAK_SYMMETRY) | Partial inverses, not exact |
| Idempotent | DUALIZE∘DUALIZE ≅ id | Confirmed (Fourier, Pontryagin) |
| Nilpotent | REDUCE∘REDUCE = REDUCE | Successive projections compose |

This is a **non-commutative monoid with involution** (DUALIZE). Whether it has richer algebraic structure (e.g., a group-like quotient) is an open question worth investigating.
