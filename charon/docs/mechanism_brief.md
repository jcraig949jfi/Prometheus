# The Mechanism: Why Silent Primes Compress Zeros
## Charon Research Brief — April 5, 2026

---

## The Empirical Finding

Elliptic curves with more additive primes (Kodaira types II-IV*, where the
local L-factor L_p(s) = 1) show tighter zero spacing in the spectral tail:

| n_additive | Mean Cohen's d | Negative gaps |
|-----------|---------------|---------------|
| 0 (ref) | -- | -- |
| 1 | -0.036 | 14/15 |
| 2 | -0.101 | 15/15 |
| 3 | -0.207 | 15/15 |

Super-linear dose-response. The primes that contribute NOTHING to the
L-function's Euler product produce the STRONGEST gap compression.

---

## The Mechanism

### What additive primes do to the L-function

An additive prime p contributes:
1. **L_p(s) = 1** — no Euler factor. The prime is "silent" in the product.
2. **f_p >= 2** — the conductor exponent is at least 2 (vs 1 for multiplicative).
3. **a_{p^m} = 0 for all m** — zero contribution to the prime sum in the
   explicit formula.

### How this compresses zeros

The zero density at height T is approximately:
  n(T) ~ (1/2*pi) * log(N * T^2 / (4*pi^2))

Each additive prime inflates N by at least p^2, increasing n(T). More zeros
per unit height means the zeros must be packed more tightly.

Meanwhile, the explicit formula's prime sum loses a term:
  Sum_{p | N, additive} [contribution] = 0

Fewer oscillatory terms in the prime sum means less "repulsive force"
spreading the zeros apart. The GUE-like repulsion that creates the
canonical spacing comes from the interference of prime contributions.
Remove a prime's contribution, and one source of repulsion vanishes.

**Combined effect:** Higher density (more zeros) + fewer repulsive terms
(less spreading) = compression. Each additional silent prime compounds
both effects multiplicatively.

### Why RMT can't capture this

Random matrix theory models L-function zeros as eigenvalues of SO(2N)
matrices. The Vandermonde determinant produces uniform pairwise repulsion
between all eigenvalues. There is no concept of "missing interactions" —
every eigenangle repels every other eigenangle equally.

The real L-function has holes in its interaction pattern: additive primes
contribute no oscillatory terms, creating "gaps" in the repulsive force
field. These gaps produce asymmetric compression that the uniform-coupling
SO(2N) model can't represent.

This is why the sign inversion (rank-1 tighter instead of wider) exists:
the naive SO(2N) prediction assumes uniform coupling. The actual coupling
is non-uniform because some primes are silent.

---

## The Three Channels Unified

The Neron model at each bad prime p produces three invariants:

| Invariant | What it measures | Spectral channel |
|-----------|-----------------|-----------------|
| a_p / L_p(s) | Local L-factor (oscillation vs silence) | Gap compression via explicit formula |
| h_p(P) | Local height of MW generator | Regulator channel (within-class) |
| c_p | Component group order (Tamagawa) | Tamagawa fingerprint (two-hump) |

All three are determined by the Kodaira type — the structure of the
special fiber of the Neron model. The spectral tail reads this single
arithmetic-geometric object through three independent projections.

---

## The Additive Reduction Hierarchy

| Kodaira | Fiber | c_p | f_p | L_p | Effect |
|---------|-------|-----|-----|-----|--------|
| I_n (mult) | n-gon | n | 1 | (1-p^{-s})^{-1} | Oscillator present |
| II | cusp | 1 | >=2 | 1 | Silent, low f |
| III | tangent | 2 | >=2 | 1 | Silent, low f |
| IV | triple | 3 | >=2 | 1 | Silent, low f |
| I*_n | D_{n+4} | 2-4 | >=2 | 1 | Silent, high c |
| IV* | E_6 | 3 | >=2 | 1 | Silent, high c |
| III* | E_7 | 2 | >=2 | 1 | Silent, high c |
| II* | E_8 | 1 | >=2 | 1 | Silent, high c |

The starred types (I*, II*, III*, IV*) have the most complex special
fibers and the highest conductor contributions. They should drive the
strongest compression — testable by stratifying by Kodaira type directly.

---

## Testable Predictions

1. **Kodaira type stratification:** Curves with I* or starred additive
   types should show more compression than curves with simple additive
   types (II, III, IV), controlling for the number of bad primes.

2. **f_p dose-response:** Within additive primes, higher conductor
   exponent f_p should correlate with more compression (more density
   inflation per prime).

3. **Wild ramification:** At p = 2 and p = 3, wild ramification can
   push f_p to 6-8+. Curves with wild ramification at p = 2 should
   show extreme compression.

4. **Cross-family:** Genus-2 curves with bad reduction at more primes
   should show the same pattern. The mechanism is generic to all
   L-functions with Euler products.

---

## The Paper's Theoretical Section

The explicit formula provides the quantitative bridge:

  Sum_rho f_hat(gamma_rho) = [conductor term] - [prime sum]

The conductor term scales as log(N), increasing zero density.
The prime sum at bad additive primes is exactly zero.
The net effect: more zeros, less repulsion, tighter gaps.

This is derivable from first principles. A theorist could compute
the expected gap compression from the missing prime terms in the
explicit formula and compare to our measured d-values. If the
quantitative prediction matches, the mechanism is proven.

Key references:
- Mestre (1986): explicit formula for ECs
- Young (2006): 1-level density with bad-prime accounting
- Iwaniec & Kowalski Ch. 5: explicit formulae framework
- Silverman, Advanced Topics Ch. VI: Neron models, local heights
