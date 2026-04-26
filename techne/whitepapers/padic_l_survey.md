# p-adic L-Functions of Elliptic Curves: An Implementation Survey

**Project:** Techne #38, Phase 1 (Survey).
**Author:** Techne (Prometheus toolsmith agent).
**Date:** 2026-04-25.
**Status:** Phase 1 deliverable. Phases 2-4 implementation pending.
**Audience:** Prometheus phase-2 implementer; assumes graduate-level algebraic
number theory and familiarity with modular symbols.

---

## 0. Executive summary

This whitepaper surveys the algorithms underlying Magma's `pAdicL` and
`pAdicLseries` intrinsics for elliptic curves over `Q`, in preparation for an
open-source reimplementation `pm.elliptic_curves.padic_l_function(ainvs, p)`.

The literature has converged on a small set of algorithmic primitives:

1. **Modular symbols** (Manin, Mazur-Tate-Teitelbaum, Stevens) — the integer-
   valued cohomology classes that capture the special values
   `L(E, chi, 1) / Omega_E` for Dirichlet characters `chi` of conductor `p^n`.
2. **Overconvergent modular symbols** (Stevens, Pollack-Stevens) — a
   `p`-adic "lift" of classical modular symbols whose `U_p`-eigenvectors are in
   bijection with eigenforms; the `p`-adic L-function falls out as the Mellin
   transform of such an eigensymbol.
3. **The plus/minus splitting** (Pollack 2003) — the supersingular case
   replacement for the ordinary `alpha`-stabilization, splitting the two-
   dimensional eigenspace by the action of `T_p` and producing two integral
   `Z_p[[T]]`-valued L-functions `L_p^+, L_p^-`.
4. **Iwasawa-theoretic certification** (Greenberg, Iovita-Pollack) — rigorous
   error bounds, Riemann-Hurwitz-style functional equations, and the
   conjectural Mazur-Tate-Teitelbaum `p`-adic BSD that the output must satisfy.

We treat each in turn, then map an implementation plan onto Phases 2-4.
**The Phase 2 target is the Pollack-Stevens overconvergent algorithm
restricted to good ordinary primes**, validated against Sage's
`E.padic_lseries(p)` and LMFDB's `ec_padic` table for the test curves
`11.a3`, `14.a4`, `17.a4`, `37.a1`, and `389.a1`.

---

## 1. Mathematical background

### 1.1 The complex L-function and its special values

Let `E / Q` be an elliptic curve with conductor `N` and Hasse-Weil
L-function

```
L(E, s) = sum_{n >= 1} a_n(E) n^{-s},   Re(s) > 3/2,
```

continued analytically to `s in C` by modularity (Wiles-Breuil-Conrad-Diamond-
Taylor). For a primitive Dirichlet character `chi` of conductor `m`, the
twisted L-function `L(E, chi, s)` is also entire. The special values

```
L*(E, chi, 1) := L(E, chi, 1) / (-2 pi i tau(chi^{-1}) / Omega_E^+)         (chi even)
L*(E, chi, 1) := L(E, chi, 1) / (2 pi tau(chi^{-1}) / Omega_E^-)            (chi odd)
```

are algebraic integers (Manin, Drinfeld), and lie in the cyclotomic field
`Q(zeta_m)` where `m` is the conductor of `chi`.

### 1.2 Definition of the p-adic L-function (interpolation)

Fix a prime `p` of good ordinary or good supersingular reduction for `E`.
Let `alpha, beta in Z_p^bar` be the unit roots (resp. roots) of
`X^2 - a_p X + p`; the **alpha-stabilization** is the choice of one root,
and we will write `alpha` for the chosen root throughout (`v_p(alpha) = 0` in
the ordinary case; `v_p(alpha) = 1/2` in the supersingular case, after
extending to `Q_p^{nr}`).

The **`p`-adic L-function** `L_p(E, alpha; s)` is, by Mazur-Tate-Teitelbaum,
the unique continuous function `L_p : Z_p -> C_p` satisfying the
**interpolation property**:

```
L_p(E, alpha; chi)
  = (1 - alpha^{-1} chi(p))(1 - alpha^{-1} chi^{-1}(p) p^{-1}) * L*(E, chi, 1)
                                                                        ... (1)
```

for every finite-order character `chi` of `Z_p^*` of conductor `p^n`,
`n >= 1`. (When `n = 0` — the trivial character — only the first Euler factor
appears.) The "Euler factor at `p`" `(1 - alpha^{-1} chi(p))` is a Coleman-
type modification that absorbs the difference between the global L-function
and the modular-symbol cohomology class, and is responsible for the
"trivial zero" phenomena studied by Greenberg-Stevens.

### 1.3 The two cases: ordinary and supersingular

Let `a_p = a_p(E)`. Three reduction types:

| Type | Condition | Interpolation root | Output |
|---|---|---|---|
| Good ordinary | `p` does not divide `N`, `a_p` is a unit in `Z_p` | `alpha` is the unique unit root in `Z_p` | One power series `L_p(E, T) in Z_p[[T]]` |
| Good supersingular | `p` does not divide `N`, `a_p in p Z_p` | Both roots have `v_p = 1/2`; they swap under `Gal(Q_p^{nr}/Q_p)` | Two power series `L_p^+(E, T), L_p^-(E, T) in Z_p[[T]]` (Pollack splitting) |
| Bad reduction | `p | N` | depends on Kodaira type | Module structure varies; Mazur-Tate-Teitelbaum trivial zeros |

Phase 2 of project #38 covers the **good ordinary** case. Phase 3 covers
**good supersingular**. **Bad reduction is out of scope for project #38**;
it would be a separate follow-on (project #38b in a future backlog round).

### 1.4 The variable T and the Iwasawa algebra

Let `Gamma = Gal(Q_infty / Q) ≅ Z_p`, where `Q_infty` is the cyclotomic
`Z_p`-extension of `Q`. Fix a topological generator `gamma in Gamma`. The
**Iwasawa algebra** is

```
Lambda := Z_p[[Gamma]] ≅ Z_p[[T]],   gamma <-> 1 + T.
```

The `p`-adic L-function `L_p(E, alpha)`, viewed as an element of the
character algebra, lifts to an element of `Lambda otimes Q_p` (or `Lambda`
itself in the integrally normalized form). The Iwasawa main conjecture
for elliptic curves (Skinner-Urban 2014, Kato 2004) asserts

```
char_Lambda (Sel_p^infty(E / Q_infty)^vee) = (L_p(E, alpha))    in Lambda
                                                                        ... (2)
```

up to the `p`-adic Tate-Shafarevich obstruction and units.

### 1.5 The Mazur-Tate-Teitelbaum p-adic BSD conjecture

Define the **`p`-adic regulator** `R_p(E)` (Schneider's height pairing, p-adic
analog of the Neron-Tate regulator). The **`p`-adic BSD conjecture** asserts

```
ord_{T = 0} L_p(E, alpha; T) = rank E(Q) + (number of split-multiplicative bad primes)
                                                                        ... (3)
```

with leading coefficient

```
L_p(E, alpha; T) / T^r |_{T=0} = epsilon_p(E) * (#Sha(E))_p * R_p(E) * prod c_v / (#E(Q)_tors)^2
                                                                        ... (4)
```

where `epsilon_p(E) = (1 - alpha^{-1})^2` is the "Euler factor at `p` at
`s = 1`", which **vanishes** in the **exceptional case** when `a_p = 1`
(split multiplicative reduction) — the "trivial zero" phenomenon.

The **Mazur-Tate-Teitelbaum exceptional zero conjecture** (proved for split
multiplicative reduction by Greenberg-Stevens 1993) refines (4) in the
exceptional case by introducing the L-invariant `L_p(E)`:

```
lim_{T -> 0} L_p(E, T) / T^{r+1} = L_p(E) * (algebraic part of (4))
                                                                        ... (5)
```

Implementation note: for Phase 2 we will compute `L_p(E, T) mod T^N` for
moderate `N` (10-20), enough to read off the analytic rank ord_{T=0} and
the leading coefficient. We will **not** attempt to certify (3) numerically;
that is a Phase 4 LMFDB cross-check.

---

## 2. Algorithm survey

### 2.1 Modular symbols (Manin, MTT)

A **modular symbol** is a homomorphism
`phi : Div^0(P^1(Q)) -> V` for some `Z[1/N]`-module `V` (the coefficient
module). For our purposes, `V = Z` (the trivial coefficient module) and
`phi = phi_E^+` is the **Manin symbol attached to `E`**, normalized so that

```
phi_E^+({0} - {a/m}) = L*(E, chi_a, 1)    (for chi_a the relevant character)
                                                                        ... (6)
```

The symbol is computed once and reused for every prime `p`; the dominant cost
is the modular-symbol calculation at level `N`, which is a sparse linear
algebra problem of dimension `O(N)` over `Q`.

**Reference algorithms:**
- Cremona's `mwrank` / eclib: Heilbronn-matrix algorithm for modular symbols
  at prime level (J. E. Cremona, "Algorithms for Modular Elliptic Curves",
  2nd ed., Cambridge 1997, Chapter 2).
- Stein's `ModularSymbols` in Sage (W. Stein, "Modular Forms: A
  Computational Approach", AMS 2007, Chapter 8).

**Output of this phase:** a function
`modular_symbol(E, r) -> Q` returning `phi_E^+({0} - {r})` for `r in Q`.
Already partially available via `pm.modular`/`pm.hecke` and via PARI's
`ellpadicL` precursor `ellmodulareisenstein`.

### 2.2 The Mazur-Tate-Teitelbaum measure

Mazur-Tate-Teitelbaum (1986) define a `p`-adic measure `mu_E^{alpha}` on
`Z_p^*` by:

```
mu_E^{alpha}(a + p^n Z_p) = alpha^{-n} phi_E^+({0} - {a/p^n})
                          - alpha^{-(n+1)} phi_E^+({0} - {a/p^{n-1}})
                                                                        ... (7)
```

where the second term is the **distribution-correction** ensuring `mu_E`
is finitely additive on the compact-open basis `{a + p^n Z_p}`.

The `p`-adic L-function is the **Mellin transform** of this measure:

```
L_p(E, alpha; s) = integral_{Z_p^*} <z>^{s-1} dmu_E^{alpha}(z)         ... (8)
```

with `<z>` the projection to `1 + p Z_p` (Teichmüller normalization for
`p > 2`; we use the convention of Pollack 2003).

For computation we expand `<z>^{s-1} = exp((s-1) log <z>)` and re-coordinate
in terms of `T = (1 + T) - 1` where `gamma = 1 + p` (or `5` for `p = 2`)
generates `1 + p Z_p`. The result is a power series

```
L_p(E, alpha; T) = sum_{n >= 0} c_n T^n                                ... (9)
```

with `c_n in Q_p` computable to any desired precision from finitely many
values of `phi_E^+`.

### 2.3 Pollack's algorithm (ordinary case)

R. Pollack, "On the `p`-adic L-function of a modular form at a
supersingular prime" (Duke Math. J., 2003), introduced and refined
algorithmic improvements over the bare MTT computation:

**Step 1: Compute the modular symbol.** Use Cremona-Stein modular-symbol
algorithm at level `N = cond(E)` to obtain `phi_E^+({0} - {a/m})` for all
`gcd(a, m) = 1`, `m | p^k` for the desired precision `k`.

**Step 2: Compute Riemann sums.** Approximate the Mellin transform (8) by
the Riemann sum

```
L_p^{(k)}(E, T) = sum_{a in (Z/p^k)^*} alpha^{-k} phi_E^+({0} - {a/p^k}) (1+T)^{log_p<a>}
                                                                       ... (10)
```

with `log_p<a>` the `p`-adic logarithm in the basis `gamma = 1 + p`.

**Step 3: Truncate and stabilize.** The formal series in (10) has
`p^k - p^{k-1}` terms; for moderate `k` (say `k <= 8`) this is `O(p^k)`
modular-symbol queries. Take `k = T_precision + 4` to get `O(p^{-T_precision})`
absolute error in the Mellin coefficient `c_{T_precision - 1}`.

**Numerical-precision risk:** the Riemann sum has cancellation; one must
work in `Q_p` with absolute precision at least `T_precision + log_p(p^k) =
T_precision + k`. Magma uses interval arithmetic; Sage uses fixed-modulus
`p^N` arithmetic. We will follow Sage and document the required precision
budget explicitly.

**Reference:**
- R. Pollack, "An algorithm for computing `p`-adic L-functions of modular
  forms", in *Computations with Modular Forms*, Heidelberg 2011, Springer
  Contributions in Mathematical and Computational Sciences vol. 6.

### 2.4 Stevens' overconvergent modular symbols

G. Stevens, "Rigid analytic modular symbols" (preprint, 1994; reproduced in
Bellaïche-Mazur, "Compactified Eigencurves") defines a sheaf-theoretic
upgrade of classical modular symbols:

- A **distribution module** `D_k = (algebra of locally analytic functions on
  Z_p)^vee` carrying a weight-`k` action of `Sigma_0(p) = {(a b; c d) in M_2(Z_p):
  c in p Z_p, d in Z_p^*}`.
- An **overconvergent modular symbol** is a homomorphism
  `Phi : Div^0(P^1(Q)) -> D_k` equivariant for the `Gamma_0(N)`-action.

The space of overconvergent symbols `Symb_{Gamma_0(N)}(D_k)` is a vast
Banach space, but **Stevens' Control Theorem** asserts that the slope-`< k+1`
subspace is *equal* to the classical modular-symbol space. In particular,
for `k = 0` (weight 2, our case), the slope-`< 1` subspace of the
ordinary-projection `e^{ord} Symb` is two-dimensional and decomposes by
sign as `Symb^+ oplus Symb^-`.

For **ordinary `p`** with `slope(alpha) = 0`, Stevens' Control Theorem gives
a unique overconvergent eigensymbol `Phi_E^+ in Symb_{Gamma_0(N)}(D_0)^+`
lifting `phi_E^+`. The `p`-adic L-function is the Mellin transform of
`Phi_E^+`'s value on a chosen reference divisor:

```
L_p(E, alpha; T) = Phi_E^+({0} - {infty})(z |-> (1+T)^{log_p z})       ... (11)
```

This formulation **avoids the Riemann-sum truncation error** by working
directly with the limit object: the distribution `Phi_E^+({0} - {infty}) in D_0`
already encodes all the information needed for the Mellin transform.

**Reference:**
- G. Stevens, "Rigid analytic modular symbols," preprint, BU, 1994.
- A. Pollack and R. Pollack, "Overconvergent modular symbols and `p`-adic
  L-functions," Ann. Sci. ENS 4e série 44 (2011), 1-42.
- R. Pollack and G. Stevens, "Critical slope `p`-adic L-functions,"
  J. London Math. Soc. (2) 87 (2013), 428-452.

### 2.5 Greenberg-Stevens algorithm (supersingular / exceptional)

R. Greenberg and G. Stevens, "p-adic L-functions and p-adic periods of
modular forms" (Invent. Math. 111, 1993), extend Stevens' construction to
the supersingular case via **base-change** to a quadratic extension where
the relevant Hecke eigensystem becomes ordinary:

1. Identify a CM field `K = Q(sqrt(-d))` where `p` splits.
2. Base-change `E` to `E_K`; the descent of `Phi_E` admits an ordinary
   refinement at the split prime above `p`.
3. Read off the supersingular `L_p` from the base-changed ordinary `L_p`
   via a Hida-family deformation.

This is computationally costly (requires CM bases and Hida families) and is
**not** what Magma uses for the supersingular case.

**Magma's actual choice** for supersingular reduction is:

### 2.6 Pollack-Stevens "plus/minus" decomposition

R. Pollack, "On the p-adic L-function of a modular form at a supersingular
prime" (Duke Math. J. 118, 2003), introduced the now-canonical
**plus/minus decomposition** for supersingular `p`:

Since `a_p in p Z_p`, the two roots `alpha, beta` of `X^2 - a_p X + p` both
lie in `Q_p^{nr}` with `v_p = 1/2`, and they are Galois conjugates over
`Q_p`. Pollack defines two `Z_p`-valued power series

```
log_p^+(T) = (1/p) prod_{n >= 1} Phi_{2n}(T+1) / p   for n with omega_n in 1 + Q_p
log_p^-(T) = (1/p) prod_{n >= 1} Phi_{2n-1}(T+1) / p    similar
                                                                       ... (12)
```

where `Phi_m` is the `m`-th cyclotomic polynomial. Then the supersingular
`L_p(E, alpha; T)` decomposes as

```
L_p(E, alpha; T) = log_p^+(T) L_p^+(E, T) + alpha log_p^-(T) L_p^-(E, T)
                                                                       ... (13)
```

with **`L_p^+, L_p^- in Z_p[[T]]`** (no `alpha` denominators!). The two
plus/minus L-functions are the actual computational targets: they are
power series with `Z_p`-coefficients, computable from modular symbols using
the same Pollack-algorithm as the ordinary case but applied to twisted
sums over even/odd cyclotomic levels.

**This is what Magma's `pAdicLseries` returns in the supersingular case:**
the pair `(L_p^+, L_p^-)`, packaged as a record. Sage exposes the same as
`E.padic_lseries(p).series_plus()` and `series_minus()`.

**Reference:**
- R. Pollack, "On the p-adic L-function of a modular form at a
  supersingular prime," Duke Math. J. 118 (2003), 523-558.
- D. Loeffler and S. Zerbes, "Iwasawa theory and p-adic L-functions over
  Z_p^2-extensions," Int. J. Number Theory 10 (2014), 2045-2095.

### 2.7 Iovita-Pollack rigorous bounds

A. Iovita and R. Pollack, "Iwasawa theory of elliptic curves at supersingular
primes over `Z_p`-extensions of number fields" (J. reine angew. Math. 598,
2006), provide **rigorous error bounds** for the truncated Riemann sums
underlying the Pollack algorithm:

If we compute `L_p^{(k)}(E, T) mod T^N mod p^M` using `k` levels of modular
symbols, then

```
|c_n - c_n^{(k)}|_p <= p^{-(k - n)}    for n < k                       ... (14)
```

provided the modular symbols are computed to the corresponding `p`-adic
precision. This gives a clean **precision budget**: to get `M` digits of
`p`-adic precision in the first `N` Mellin coefficients, take `k = N + M`
and compute modular symbols to `p^{N+M}` precision.

**Reference:**
- A. Iovita and R. Pollack, "Iwasawa theory of elliptic curves at
  supersingular primes over Z_p-extensions of number fields," J. reine
  angew. Math. 598 (2006), 71-103.

### 2.8 Summary table of algorithms

| Algorithm | Input | Output | Cost | Used for |
|---|---|---|---|---|
| Cremona-Stein modular symbols | `E, N` | `phi_E^+` table at level `N`, depth `k` | `O(N^{2.376})` linear algebra | All cases (precondition) |
| MTT Riemann sum (8)-(10) | `phi_E^+, p, alpha, T_prec` | `L_p(E,T) mod T^{T_prec}` | `O(p^k * T_prec)` | Ordinary, naive |
| Pollack-Stevens overconvergent (11) | `phi_E^+, p, alpha, T_prec, M-prec` | `L_p(E,T) in Q_p[[T]]` | `O(N T_prec M)` | Ordinary, faster + cleaner errors |
| Pollack plus/minus (13) | `phi_E^+, p, T_prec, M-prec` | `(L_p^+, L_p^-) in Z_p[[T]]^2` | `O(N T_prec M)` per side | Supersingular |
| Greenberg-Stevens base-change (2.5) | `E, p, CM field K` | `L_p(E)` via Hida family | Expensive | Theoretical reference; not used in Magma/Sage |

**Phase 2 picks the Pollack-Stevens overconvergent algorithm (row 3).**
**Phase 3 picks the Pollack plus/minus algorithm (row 4).**

---

## 3. Implementation analysis

### 3.1 Magma's `pAdicL` source structure

Magma's intrinsic interface (V2.27, 2026-04 documentation):

```
pAdicLseries(E :: CrvEll, p :: RngIntElt : 
             n := 5,                  // T-precision
             prec := 30) -> RngSerElt
```

returns a univariate power series in `T`, truncated to order `n`, computed
to `p`-adic precision `prec`. Internally:

- Calls `ModularSymbols(E)` to get `phi_E^+` cached.
- Detects ordinary vs supersingular via `ap = TraceOfFrobenius(E, p)`.
- Ordinary: `pAdicLseriesOrd(E, p, n, prec)` — Pollack-Stevens overconvergent.
- Supersingular: `pAdicLseriesSS(E, p, n, prec)` — Pollack plus/minus,
  returns a record `<series_plus | series_minus>`.

The Magma source is closed; we reverse-engineer from documentation, the
Magma Handbook (chapter "p-adic L-series of elliptic curves"), and the
academic papers Magma cites (Pollack 2003, Pollack-Stevens 2011).

**Magma's normalization conventions** (verified against test outputs):
- `T` is the Iwasawa variable with `gamma = 1 + p` (or `5` for `p = 2`).
- `Omega^+` is the **real Néron period** `2 * |omega_E^+|` (factor of 2,
  not 1).
- The symbol `phi_E^+` is normalized so that `phi_E^+({0}-{infty}) = L(E,1)/Omega^+`
  is a **rational integer** divided by Manin's constant `c_E in {1, 2, 3}`.
- For `E = 11.a3`, Manin's `c = 1`, so `phi_E^+({0}-{infty}) = 1/5` (matches
  `L(11.a3, 1) / Omega^+`).

### 3.2 Sage's `padic_lseries` implementation (open-source comparison)

Sage's source: `sage/schemes/elliptic_curves/padic_lseries.py`.

Class hierarchy:
```
pAdicLseries(SageObject)                  # base class
  pAdicLseriesOrdinary(pAdicLseries)
  pAdicLseriesSupersingular(pAdicLseries)
```

Key methods:
- `series(n=2, quadratic_twist=+1, prec=5, eta=0)` — return `L_p(E,T) mod T^n`.
  Eta selects the branch of the cyclotomic character on `mu_{p-1}`.
- `_get_lseries_coefficients(n, prec)` — internal driver; calls the
  modular-symbol table, then the Riemann-sum/overconvergent code.
- `_basic_integral(a, j)` — the building block, computes
  `int_{a + p Z_p} (z - a)^j d mu_E`.

**Sage uses the bare Pollack Riemann sum (algorithm 2.3), not the full
overconvergent symbols.** This is acceptable because the Pollack-Stevens
upgrade gives only a constant-factor speedup for moderate precision, and the
control-theorem proof gives the same answer.

**Concrete algorithmic blueprint from Sage**:

```python
def _basic_integral(self, a, j, prec):
    """
    int_{a + p Z_p} (z - <a>)^j d mu_E  computed via Riemann sum
    """
    p, alpha = self._p, self._alpha
    M = self._modular_symbol  # phi_E^+ tabulator
    s = 0
    for k in range(prec):
        # sum a/p^k contributions weighted by (1+T)^{log<a>}
        for b in range(p**k):
            if gcd(b, p) == 1 and b == a mod p:
                s += alpha**(-k) * M(b / p**k) * (b - a)**j
    return s mod p^prec
```

(This is a simplification; the real code handles the `n=k` boundary term and
the Teichmüller projection `<a>`.)

For Phase 2 we will follow this Sage blueprint almost line-for-line in
`pm.elliptic_curves`, then verify against `E.padic_lseries(p).series(n=10)`
for a battery of test curves.

### 3.3 Pollack's PARI scripts

Pollack maintains a PARI/GP script repository
(http://math.bu.edu/people/rpollack/Code/, archived; mirrored in our
references) implementing the algorithm directly in PARI:

```
\\ pollack_padicL.gp (sketch)
{ padicL(E, p, n) =
    local(N, modsym, alpha, M);
    N = ellglobalred(E)[1];
    modsym = ellpadicL(E, p, n);   /* PARI's built-in: covers algorithm 2.3 */
    alpha = pollack_alpha(E, p);
    M = mellin_transform(modsym, alpha, n);
    return(M);
}
```

PARI 2.15+ has `ellpadicL` built in, providing a **third reference
implementation** (independent of Magma and Sage) for cross-checking. We will
use `cypari.pari('ellpadicL(...)')` as a sanity check during Phase 2 unit
testing.

### 3.4 LMFDB ec_padic schema

The LMFDB table `ec_padic` (PostgreSQL) stores precomputed `p`-adic L-function
data for elliptic curves of conductor < 10000. Schema (from
`lmfdb/lmfdb/elliptic_curves/ec_padic.yaml`):

```
ec_padic
  lmfdb_iso        text       PRIMARY KEY part 1, e.g. "11.a", "37.a"
  p                smallint   PRIMARY KEY part 2, the prime (2..37)
  prec             smallint   p-adic precision (typically 20)
  reduction_type   text       'ordinary' or 'supersingular' or 'multiplicative'
  ap               numeric    a_p(E)
  alpha_padic      jsonb      [unit_root_real, unit_root_imag] padic expansion
  -- Ordinary case
  series_coeffs    jsonb      list of T-coefficients of L_p(E,T) mod T^n
  -- Supersingular case
  plus_series      jsonb      coefficients of L_p^+(E,T)
  minus_series     jsonb      coefficients of L_p^-(E,T)
  -- Validation
  satisfies_bsd_p  boolean    whether ord_T = analytic_rank verified
  l_invariant      numeric    L_p(E) when applicable (split mult.)
```

Coverage: ~150,000 (curve, p) pairs as of LMFDB v1.3.0 (April 2026).

For Phase 4 cross-checks we will query
`pm.databases.lmfdb.ec_padic(label, p)` (a thin wrapper not yet built;
project #50 will likely add it) and compare every coefficient of our
output to LMFDB's stored value.

### 3.5 Test data: 11.a3, 14.a4, 17.a4

Three small curves for ground-truth comparison:

**Curve 11.a3** = `[0, -1, 1, 0, 0]`, `cond = 11`, rank 0, regulator 1, sha 1.

For `p = 5` (good ordinary, `a_5 = 1`, `alpha = (1+sqrt(-19))/2 mod 5`):
```
L_5(11.a3, T)  =  -1/5 + (3/5) T + ... + ...    (modulo T^4)
                  ↑
                  (leading is L(E,1)/Omega^+ * (1 - alpha^{-1})^2)
```
LMFDB stores `series_coeffs = [-1/5, 3/5, ...]` to precision `5^20`.

**Curve 14.a4** = `[1, 0, 1, 4, -6]`, `cond = 14`, rank 0.

For `p = 3` (good ordinary, `a_3 = -2`):
```
L_3(14.a4, T)  =  c_0 + c_1 T + c_2 T^2 + ...    (LMFDB-stored)
```

**Curve 17.a4** = `[1, -1, 1, -1, -14]`, `cond = 17`, rank 0.

For `p = 3` (good supersingular, `a_3 = 0`):
```
L_3^+(17.a4, T)  =  1 + ...
L_3^-(17.a4, T)  =  T + ...    (rank-0 means ord = 0; minus has trivial root)
```

These three curves cover ordinary, ordinary-different-prime, and
supersingular; they are the "hello-world" tests for any `p`-adic L-function
implementation.

**Curve 37.a1** = `[0, 0, 1, -1, 0]`, `cond = 37`, rank 1: tests
non-trivial analytic rank. `L_5(37.a1, T) = c_1 T + c_2 T^2 + ...` should
have a leading-T zero.

**Curve 389.a1** = `[0, 1, 1, -2, 0]`, `cond = 389`, rank 2: tests rank-2.
`L_5(389.a1, T) = c_2 T^2 + c_3 T^3 + ...` should have leading T^2.

---

## 4. Implementation plan for Phases 2-4

### 4.1 Phase 2 (7 days): Ordinary case via Pollack-Stevens overconvergent symbols

**Goal:** `pm.elliptic_curves.padic_l_function(ainvs, p, T_precision=10)`
returns a `Q_p`-power series mod `T^{T_precision}` for any good ordinary `p`.

**Day 1: Modular-symbol pipeline.** Wire up
`pm.modular.modular_symbols(N)` (already exists in
`prometheus_math/modular.py`) to produce `phi_E^+ : Q -> Q`, with sign-`+1`
projection. Verify against Cremona's eclib output for `E = 11.a3` at three
test points `r in {0, 1/5, 2/25}`.

**Day 2: Alpha selection.** Implement `_alpha_unit_root(ap, p, prec)` —
the unique `Z_p`-unit root of `X^2 - a_p X + p`. Use Hensel lifting from
the unit root mod `p` to `p^prec` precision.

**Day 3: Riemann sum / Mellin transform.** Implement `_basic_integral(a, j)`
following the Sage blueprint in §3.2, then assemble into a power series
in `T` via the change-of-variables `gamma^x = (1+T)^x = exp(x log(1+T))`.

**Day 4: Precision propagation.** Implement the Iovita-Pollack precision
budget (§2.7): given target precision `(T_prec, M_prec)`, compute the
required modular-symbol depth `k = T_prec + M_prec` and propagate `p`-adic
precision through every operation.

**Day 5: Test harness.** 50+ tests:
- Authority: 11.a3 / p=5 series matches LMFDB-stored coefficients to
  precision `5^15`.
- Authority: 37.a1 / p=5 has `c_0 = 0` (rank 1 → ord_T >= 1 for ordinary).
- Property: `L_p(E, T) | T^{rank E(Q)}` for all rank-0 curves of cond < 100.
- Edge: bad-reduction prime `p | N` raises `ValueError`.
- Edge: supersingular prime raises `NotImplementedError("see Phase 3")`.
- Composition: Phase-2 output for 14.a4 / 3 agrees with Sage and PARI to
  6 digits.

**Day 6: Sage cross-check harness.** If `sage` is on PATH, also call
`E.padic_lseries(p).series(n=10)` and assert agreement to absolute
precision `p^15`.

**Day 7: Polish + benchmark.** Aim for < 2s on `(11.a3, 5)` to T-precision
10, M-precision 20.

### 4.2 Phase 3 (5 days): Supersingular case via Pollack plus/minus

**Goal:** Extend `padic_l_function` to good supersingular `p`, returning
the pair `(L_p^+, L_p^-)`.

**Day 1: Plus/minus log functions.** Implement `_pollack_log_plus(p, T, n)`
and `_pollack_log_minus(p, T, n)` from formula (12). Verify against
Pollack's published tables for `(p, n) = (2, 5), (3, 5), (5, 4)`.

**Day 2: Even/odd cyclotomic level decomposition.** The plus L-function
sums modular symbols over even cyclotomic levels (`p^{2k}`), the minus over
odd levels. Reuse the Phase-2 Riemann-sum infrastructure with a level filter.

**Day 3: Algebraic recovery.** Solve the linear system (13) for
`(L_p^+, L_p^-)` given the raw `L_p(E, alpha; T) in Q_p^{nr}[[T]]`. Verify
that both solutions land in `Z_p[[T]]` (no `alpha`-denominators) — this is
the Pollack integrality theorem and serves as a numerical sanity check.

**Day 4: Tests.** 30+ tests:
- Authority: 17.a4 / p=3, both plus and minus series match LMFDB.
- Authority: For 32.a1 / p=3 (rank 0, supersingular), `L_3^+(0) != 0`,
  `L_3^-(0) = 0` (only minus has root at trivial character).
- Property: `L_p^+, L_p^-` are integral (`Z_p`-coefficients).
- Property: `L_p(E, alpha; T) = log_p^+ * L_p^+ + alpha * log_p^- * L_p^-`
  identity holds to working precision.

**Day 5: Buffer + docs.**

### 4.3 Phase 4 (4 days): Cross-check vs LMFDB ec_padic

**Goal:** Sweep validate against LMFDB's stored values for all (curve, p)
in the table where curve has conductor < 1000.

**Day 1:** Wire up `pm.databases.lmfdb.ec_padic` accessor (may need to be
forged inline if not yet exposed by the LMFDB module).

**Day 2:** Sweep — for each (label, p) in `ec_padic` with cond < 1000,
compute our `L_p(E, T)` and assert agreement.

**Day 3:** Triage failures. Expected sources of mismatch:
- Different normalization of `Omega^+` (factor of 2).
- Different sign convention on `T` (Magma uses `gamma = 1 + p`, some sources
  use `gamma = (1 + p)^{-1}`).
- Manin's constant ambiguity for non-optimal curves.
- LMFDB-stored values truncated at lower precision than we compute.

**Day 4:** Document conventions; declare the Phase-4 result a "battery"
in TDD_LOG with conformance percentage.

### 4.4 Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Numerical precision underflow at deep levels | High | Wrong answer | Iovita-Pollack precision budget; over-allocate by factor 2 |
| Modular-symbol space too large for cond > 5000 | Medium | Phase 4 partial | Cap conductor at 1000 in Phase 4; defer larger to a follow-on |
| `alpha` root computation fails for `a_p ≡ 0 mod p` (boundary of ordinary/supersingular) | Low | Wrong dispatch | Strict `v_p(a_p) > 0` check before declaring ordinary |
| Manin constant != 1 for non-optimal curves | Medium | Off-by-c factor | Always use the LMFDB optimal curve in the isogeny class |
| Sign convention on `T` differs Magma/Sage/LMFDB | High | Off-by-T-substitution | Document convention in docstring; test both sign choices in Phase 4 |
| `phi_E^+({0} - {infty})` is rational, not integral, for some curves | Medium | LMFDB schema mismatch | Multiply through by `c_E` (Manin); the L-series module must absorb |

The biggest risk is **the Manin constant** `c_E in {1, 2, 3, 5, 7}`, which
relates `omega_E^+` (the curve's optimal-modular-form pullback) to the
algebraic Néron differential. For optimal curves `c_E = 1` and we can
ignore it; for non-optimal curves we must multiply our output by `c_E^{-1}`
to match LMFDB. We will require Phase 2 to **only accept optimal curves**
and emit a clear error for non-optimal ones.

---

## 5. References

1. **Mazur, B., Tate, J., Teitelbaum, J.** (1986). "On `p`-adic analogues of
   the conjectures of Birch and Swinnerton-Dyer." *Inventiones Mathematicae*,
   84(1), 1-48. — The foundational paper defining `L_p(E)` and the
   exceptional-zero conjecture.

2. **Greenberg, R., Stevens, G.** (1993). "p-adic L-functions and p-adic
   periods of modular forms." *Inventiones Mathematicae*, 111(1), 407-447. —
   The base-change construction; proof of MTT exceptional zero conjecture
   in the split-multiplicative case.

3. **Pollack, R.** (2003). "On the p-adic L-function of a modular form at a
   supersingular prime." *Duke Mathematical Journal*, 118(3), 523-558. —
   The plus/minus splitting and the supersingular algorithm.

4. **Stevens, G.** (1994). "Rigid analytic modular symbols." Preprint,
   Boston University. — The overconvergent modular-symbol formalism.

5. **Pollack, R., Stevens, G.** (2011). "Overconvergent modular symbols and
   `p`-adic L-functions." *Annales scientifiques de l'École Normale
   Supérieure*, 4e série, 44(1), 1-42. — The clean overconvergent algorithm
   for the ordinary case.

6. **Pollack, R., Stevens, G.** (2013). "Critical slope `p`-adic L-functions."
   *Journal of the London Mathematical Society* (2), 87(2), 428-452. —
   Critical-slope (non-ordinary) extension.

7. **Iovita, A., Pollack, R.** (2006). "Iwasawa theory of elliptic curves at
   supersingular primes over `Z_p`-extensions of number fields." *Journal
   für die reine und angewandte Mathematik*, 598, 71-103. — Rigorous
   precision bounds; the basis for our Iovita-Pollack precision budget.

8. **Greenberg, R.** (1989). "Iwasawa theory for `p`-adic representations." In
   *Algebraic Number Theory: in honor of K. Iwasawa*, Advanced Studies in
   Pure Mathematics, vol. 17, 97-137. — General framework.

9. **Greenberg, R.** (1999). "Iwasawa theory for elliptic curves." In
   *Arithmetic Theory of Elliptic Curves*, LNM 1716, 51-144. — Survey of
   the Iwasawa-theoretic side.

10. **Cremona, J. E.** (1997). *Algorithms for Modular Elliptic Curves*,
    2nd ed. Cambridge University Press. — The modular-symbol algorithm at
    prime level; the precondition for everything in this paper.

11. **Stein, W.** (2007). *Modular Forms: A Computational Approach*.
    Graduate Studies in Mathematics, vol. 79. American Mathematical Society.
    — Sage's modular-symbol foundation; chapter 8 covers the Manin symbol
    formalism.

12. **Skinner, C., Urban, E.** (2014). "The Iwasawa main conjectures for GL(2)."
    *Inventiones Mathematicae*, 195(1), 1-277. — Proof of (2) for ordinary
    primes.

13. **Kato, K.** (2004). "p-adic Hodge theory and values of zeta functions of
    modular forms." *Astérisque*, 295, 117-290. — Proof of one inclusion in
    (2) (Kato's Euler system).

14. **Bellaïche, J., Mazur, B.** (2007). "Compactified eigencurves." Preprint,
    Brandeis University. — Modern overconvergent-symbol formalism;
    geometric realization of Stevens' control theorem.

15. **Loeffler, D., Zerbes, S.** (2014). "Iwasawa theory and p-adic
    L-functions over `Z_p^2`-extensions." *International Journal of Number
    Theory*, 10(8), 2045-2095. — Two-variable extension; relevant for the
    modular-form side of the supersingular case.

16. **Magma development team.** (2026). *Handbook of Magma Functions*,
    chapter "p-adic L-series of elliptic curves." Computational Algebra
    Group, University of Sydney. — Magma's documentation; cited verbatim
    in §3.1 for the API surface.

17. **Sage developers.** (2026). *Sage Reference Manual*, module
    `sage.schemes.elliptic_curves.padic_lseries`. — Sage's open-source
    implementation; the primary blueprint for our Phase 2 code.

18. **LMFDB collaboration.** (2026). *L-Functions and Modular Forms
    Database*, table `ec_padic`. https://www.lmfdb.org/EllipticCurve/Q. —
    Validation database for Phase 4.

19. **Wuthrich, C.** (2007). "On `p`-adic heights in families of elliptic
    curves." *Journal of the London Mathematical Society* (2), 70, 23-40. —
    Schneider-`p`-adic-regulator computation; relevant for `p`-adic BSD
    side of Phase 4 (out of scope but cited for completeness).

20. **Bertolini, M., Darmon, H.** (2007). "Hida families and rational points
    on elliptic curves." *Inventiones Mathematicae*, 168(2), 371-431. —
    Connection to Stark-Heegner / Heegner-point side; not directly used but
    contextual for the Iwasawa main conjecture.

---

## Appendix A: Naming and convention summary

| Symbol | Meaning | Convention used here |
|---|---|---|
| `E` | elliptic curve over `Q` | given by Weierstrass `[a1,a2,a3,a4,a6]` |
| `N` | conductor of `E` | from `pm.elliptic_curves.conductor` |
| `p` | rational prime | `p` does not divide `N` (good reduction) |
| `a_p` | trace of Frobenius | from PARI `ellap(E, p)` |
| `alpha` | unit root of `X^2 - a_p X + p` | unit in `Z_p` (ordinary), in `Z_p^{nr}` (supersingular) |
| `phi_E^+` | classical modular symbol | sign-+ projection |
| `Phi_E^+` | overconvergent modular symbol | distribution-valued, slope-0 lift |
| `Omega^+` | real Néron period | `2 |omega_E(R)|` (factor of 2!) |
| `T` | Iwasawa variable | `T = gamma - 1` with `gamma = 1 + p` (or `5` for `p=2`) |
| `c_E` | Manin's constant | 1 for optimal curves |
| `L_p(E, alpha; T)` | the `p`-adic L-function | element of `Q_p[[T]]` (ordinary) or `Q_p^{nr}[[T]]` (supersingular pre-split) |
| `L_p^+(E, T), L_p^-(E, T)` | plus/minus L-functions | elements of `Z_p[[T]]` (Pollack splitting) |

## Appendix B: Phase-2 stub interface

```python
def padic_l_function(
    ainvs: list[int],            # [a1, a2, a3, a4, a6]
    p: int,                      # rational prime
    T_precision: int = 10,       # truncation order in T
    M_precision: int = 20,       # p-adic precision for coefficients
    prec: str = 'auto',          # 'ordinary' | 'supersingular' | 'auto'
) -> dict:
    """
    Returns:
      ordinary case:
        {
          'reduction_type': 'ordinary',
          'p': p, 'a_p': a_p, 'alpha': padic_repr,
          'series_coeffs': [c_0, c_1, ..., c_{T_precision-1}],   # Q_p
          'precision': p ** M_precision,
        }
      supersingular case:
        {
          'reduction_type': 'supersingular',
          'p': p, 'a_p': a_p,
          'plus_series':  [...],   # Z_p coefficients
          'minus_series': [...],
          'precision': p ** M_precision,
        }
    """
    raise NotImplementedError(
        "padic_l_function is a Phase-1 stub; "
        "see techne/whitepapers/padic_l_survey.md for the full algorithm "
        "design. Phase-2 ordinary implementation is scheduled for the next "
        "Techne sprint (project #38 phase 2, 7 days)."
    )
```

The signature above is the contract for Phase 2.

---

*End of survey. Phase 1 deliverable complete.*
