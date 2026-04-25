# Prometheus Math Arsenal

**Single-page researcher reference for the unified mathematical-software API.**

Generated: 2026-04-25 02:46 · Status: 24/32 backends available across 9 categories: AI, CAS, COMB, DB, NT, NUM, OPT, SAT, TOP

---

## Quick start

```python
import prometheus_math as pm

# Number theory
pm.number_theory.class_number('x^2+5')             # 2
pm.elliptic_curves.analytic_sha([0,-1,1,-10,-20])   # {'rounded': 1, ...}

# Topology
pm.topology.hyperbolic_volume('4_1')                # 2.0298832...
pm.topology.knot_shape_field('5_2')                 # {disc: -23, ...}

# Optimization (auto-dispatches to best installed backend)
pm.optimization.solve_mip(c, A_ub, b_ub, integrality=[1,1])

# Numerics
pm.numerics.zeta(0.5 + 14.13j, prec=50)

# Capability check
pm.registry.installed()
```

---

## Backend capability matrix

**24/32 backends available** as of generation.

| Backend | Status | Version | Kind | Category | Description |
|---|---|---|---|---|---|
| `sympy` | ✅ | 1.14.0 | python | CAS | Pure-Python symbolic computation |
| `sage` | ❌ | — | python | CAS | SageMath meta-CAS (heavy install) |
| `cypari` | ✅ | 2.5.6 | python | NT | PARI/GP via cypari (number theory) |
| `flint` | ✅ | 0.8.0 | python | NT | python-flint (fast NT primitives) |
| `gmpy2` | ✅ | 2.3.0 | python | NUM | GMP/MPFR/MPC arbitrary precision |
| `numpy` | ✅ | 2.2.6 | python | NUM | Array computing |
| `scipy` | ✅ | 1.13.1 | python | NUM | Scientific algorithms |
| `mpmath` | ✅ | 1.3.0 | python | NUM | Arbitrary-precision floats |
| `snappy` | ✅ | 3.3.2 | python | TOP | 3-manifolds, hyperbolic geometry |
| `knot_floer_homology` | ✅ | 1.2.2 | python | TOP | Heegaard Floer knot homology |
| `gudhi` | ✅ | 3.12.0 | python | TOP | Persistent homology, TDA |
| `ripser` | ✅ | 0.6.14 | python | TOP | Fast Vietoris-Rips persistence |
| `persim` | ✅ | 0.3.8 | python | TOP | Persistence images, distances |
| `networkx` | ✅ | 3.6.1 | python | COMB | Graph theory |
| `chipfiring` | ✅ | 1.1.3 | python | COMB | Chip-firing, Baker-Norine rank |
| `galois` | ✅ | 0.4.10 | python | COMB | GF(p^n) arithmetic, error-correcting codes |
| `z3` | ✅ | ? | python | SAT | Z3 SMT solver |
| `pysat` | ✅ | 1.9.dev2 | python | SAT | PySAT (Glucose, MiniSat-class) |
| `pyscipopt` | ✅ | 6.1.0 | python | OPT | SCIP MIP/LP |
| `ortools` | ✅ | 9.15.6755 | python | OPT | Google OR-Tools / CP-SAT |
| `highspy` | ✅ | ? | python | OPT | HiGHS LP/MIP |
| `pulp` | ✅ | 3.3.0 | python | OPT | PuLP modeling layer |
| `cvxpy` | ✅ | 1.8.2 | python | OPT | Convex optimization |
| `torch` | ✅ | 2.11.0.dev20251222+cu128 | python | AI | PyTorch |
| `gap` | ❌ | — | binary | GT | GAP (groups, representations) |
| `macaulay2` | ❌ | — | binary | AG | Macaulay2 (commutative algebra) |
| `singular` | ❌ | — | binary | AG | Singular (polynomial rings) |
| `julia` | ❌ | — | binary | lang | Julia (gateway to OSCAR/Hecke/Nemo) |
| `lean` | ❌ | — | binary | PA | Lean 4 theorem prover |
| `R` | ❌ | — | binary | stats | R statistics environment |
| `lmfdb` | ✅ | online | service | DB | LMFDB Postgres mirror at devmirror.lmfdb.xyz |
| `oeis` | ❌ | — | service | DB | OEIS - Online Encyclopedia of Integer Sequences |

---

## Operations by category

### `prometheus_math.number_theory` — Number theory & polynomials

| Function | Summary |
|---|---|
| `class_number(polynomial) -> int` | Class number h_K of the number field K = Q[x]/(f(x)). |
| `class_group(polynomial) -> dict` | Full class group structure of K = Q[x]/(f(x)). |
| `regulator_nf(polynomial) -> float` | Regulator of the unit group of K = Q[x]/(f(x)). |
| `galois_group(polynomial) -> dict` | Galois group of Q[x]/(f) over Q, as a transitive subgroup of S_n. |
| `is_abelian(polynomial) -> bool` | True iff Gal(Q[x]/(f)/Q) is abelian (equivalently: \|G\| = deg(f)). |
| `disc_is_square(polynomial) -> bool` | True iff disc(f) is a square in Q, i.e. G ⊆ A_n. |
| `hilbert_class_field(polynomial, max_stack_mb: int = None, max_class_number: int = 50) -> dict` | Compute the Hilbert class field of K = Q[x]/(f(x)). |
| `class_field_tower(polynomial, max_depth: int = 5, max_stack_mb: int = None, max_class_number: int = 50) -> dict` | Iterate the Hilbert class field construction. |
| `set_pari_stack_mb(mb: int) -> None` | Override the PARI stack allocation (megabytes). Call before any |
| `cm_order_data(D: int) -> dict` | CM order invariants for discriminant D < 0. |
| `lll(basis) -> numpy.ndarray` | LLL-reduced basis of the lattice spanned by the rows of `basis`. |
| `lll_with_transform(basis)` | LLL-reduced basis R together with the transform T so that R = T @ B. |
| `shortest_vector_lll(basis) -> numpy.ndarray` | Shortest vector of the LLL-reduced basis (approximate SVP). |
| `lll_gram(gram) -> numpy.ndarray` | LLL reduction given the Gram matrix G = B B^T. |
| `functional_eq_check(obj, precision: int = 100, threshold_log10: int = -8) -> dict` | Check the functional equation of an L-function. |
| `fe_residual(obj, precision: int = 100) -> int` | Just the log_10 FE residual (shortcut). More negative = better. |
| `mahler_measure(coefficients: list) -> float` | Compute the Mahler measure of a polynomial from its coefficients. |
| `log_mahler_measure(coefficients: list) -> float` | Compute log(M(p)), the logarithmic Mahler measure. |
| `is_cyclotomic(coefficients: list, tol: float = 1e-10) -> bool` | Test whether a polynomial is cyclotomic (all roots on unit circle). |
| `cf_expand(p: int, q: int) -> list` | Compute the continued fraction expansion of p/q. |
| `cf_max_digit(p: int, q: int) -> int` | Return the largest CF digit in the expansion of p/q. |
| `zaremba_test(q: int, bound: int = 5) -> dict` | Test the Zaremba conjecture for a given denominator q. |
| `sturm_bound(weight: int, level: int, prime_factors: list = None) -> int` | Compute the Sturm bound for modular forms. |

### `prometheus_math.elliptic_curves` — Elliptic curves over Q

| Function | Summary |
|---|---|
| `regulator(ainvs: Sequence[int], effort: int = 1, saturation_bound: int = 100) -> float` | Regulator of E(Q)/torsion. |
| `mordell_weil(ainvs: Sequence[int], effort: int = 1, saturation_bound: int = 100) -> dict` | Full Mordell-Weil data for E/Q. |
| `height(ainvs: Sequence[int], point: Sequence) -> float` | Neron-Tate canonical height of a rational point on E. |
| `conductor(ainvs) -> 'int'` | Global conductor N of the elliptic curve. |
| `global_reduction(ainvs) -> 'dict'` | Full global reduction data in one structured dict. |
| `bad_primes(ainvs) -> 'list[int]'` | Primes of bad reduction, sorted ascending. |
| `root_number(ainvs) -> 'int'` | Global root number w(E) in {+1, -1}. |
| `local_root_number(ainvs, p: 'int') -> 'int'` | Local root number w_p(E) at the prime p. |
| `parity_consistent(ainvs, analytic_rank: 'int') -> 'bool'` | Check (-1)^rank == w(E). Assumes BSD parity (known for most curves). |
| `analytic_sha(ainvs: Sequence[int], rank_hint: int = None) -> dict` | Analytic Sha via BSD formula. |
| `sha_an_rounded(ainvs: Sequence[int]) -> int` | BSD integer prediction of \|Sha(E/Q)\|. |
| `selmer_2_rank(ainvs: Sequence[int], effort: int = 1) -> int` | 2-Selmer rank dim_F2 Sel_2(E/Q). |
| `selmer_2_data(ainvs: Sequence[int], effort: int = 1) -> dict` | Full 2-Selmer / 2-descent data. |
| `faltings_height(ainvs: Sequence[int]) -> float` | (Stable) Faltings height of E/Q. |
| `faltings_data(ainvs: Sequence[int]) -> dict` | Full data packet for Faltings height. |

### `prometheus_math.number_fields` — Number-field-specific operations

| Function | Summary |
|---|---|
| `class_number(polynomial) -> int` | Class number h_K of the number field K = Q[x]/(f(x)). |
| `class_group(polynomial) -> dict` | Full class group structure of K = Q[x]/(f(x)). |
| `regulator_nf(polynomial) -> float` | Regulator of the unit group of K = Q[x]/(f(x)). |
| `hilbert_class_field(polynomial, max_stack_mb: int = None, max_class_number: int = 50) -> dict` | Compute the Hilbert class field of K = Q[x]/(f(x)). |
| `class_field_tower(polynomial, max_depth: int = 5, max_stack_mb: int = None, max_class_number: int = 50) -> dict` | Iterate the Hilbert class field construction. |
| `set_pari_stack_mb(mb: int) -> None` | Override the PARI stack allocation (megabytes). Call before any |
| `cm_order_data(D: int) -> dict` | CM order invariants for discriminant D < 0. |

### `prometheus_math.topology` — Knot, link, 3-manifold, TDA

| Function | Summary |
|---|---|
| `hyperbolic_volume(knot) -> float` | Compute the hyperbolic volume of the knot/link complement. |
| `hyperbolic_volume_hp(knot, digits: int = 60) -> str` | Return the volume as a high-precision decimal string. |
| `is_hyperbolic(knot, tol: float = 1e-06) -> bool` | Test whether the knot complement admits a complete hyperbolic structure. |
| `volume_conjecture_ratio(knot, N: int = 100) -> float` | Return (2*pi/N) * log\|J_N(K; exp(2*pi*i/N))\| / vol(K). |
| `knot_shape_field(knot: Union[str, ForwardRef('snappy.Manifold')], bits_prec: int = 300, max_deg: int = 8) -> dict` | Shape field of a hyperbolic knot complement. |
| `knot_shape_field_batch(knots, bits_prec: int = 300, max_deg: int = 8, skip_errors: bool = True, progress_every: int = 100) -> list` | Batch shape-field computation for many knots. |
| `polredabs(polynomial) -> str` | Canonical LMFDB form of a number field polynomial (PARI polredabs). |
| `alexander_polynomial(knot) -> dict` | Alexander polynomial of a knot. |
| `alexander_coeffs(knot) -> List[int]` | Descending-degree Alexander polynomial coefficients. |

### `prometheus_math.combinatorics` — Graphs, polytopes, integer matrices

| Function | Summary |
|---|---|
| `smith_normal_form(M: Union[numpy.ndarray, Sequence[Sequence[int]]]) -> numpy.ndarray` | Smith normal form of an integer matrix. |
| `invariant_factors(M: Union[numpy.ndarray, Sequence[Sequence[int]]]) -> list` | Non-zero invariant factors d_1 \| d_2 \| ... of the integer matrix M. |
| `abelian_group_structure(M: Union[numpy.ndarray, Sequence[Sequence[int]]]) -> dict` | Decompose Z^m / A Z^n as torsion x free. |
| `tropical_rank(adjacency, divisor: Sequence[int]) -> int` | Tropical (Baker-Norine) rank of a divisor on the graph given by adjacency. |
| `tropical_rank_graph(vertices: Sequence, edges: Sequence, degrees: Sequence) -> int` | Tropical rank given explicit vertex labels and edges. |
| `is_winnable(adjacency, divisor: Sequence[int]) -> bool` | True iff D is linearly equivalent to an effective divisor (i.e. r(D) >= 0). |
| `classify_singularity(coefficients: list, min_terms: int = 15) -> dict` | Classify the dominant singularity type of a generating function. |
| `estimate_radius(coefficients: list, min_terms: int = 10) -> Optional[float]` | Estimate radius of convergence via ratio test. |

### `prometheus_math.optimization` — LP, MIP, CP, SAT, SMT, convex

| Function | Summary |
|---|---|
| `solve_lp(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None, backend: 'Optional[str]' = None) -> 'dict'` | Solve a linear program: minimize c.x s.t. A_ub x <= b_ub, A_eq x = b_eq. |
| `solve_mip(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, integrality=None, bounds=None, backend: 'Optional[str]' = None) -> 'dict'` | Solve a mixed-integer program: minimize c.x with integrality mask. |
| `solve_cp(model_fn: 'Callable[[Any], None]', backend: 'Optional[str]' = None) -> 'dict'` | Solve a CP-SAT model built by `model_fn(model)`. |
| `solve_sat(clauses: 'Sequence[Sequence[int]]', backend: 'Optional[str]' = None) -> 'dict'` | Solve a CNF SAT problem given DIMACS-style clauses. |
| `solve_smt(formula_or_assertions, backend: 'Optional[str]' = None) -> 'dict'` | Solve an SMT problem via Z3. |
| `solve_convex(objective_fn, constraints=None, variables=None, backend: 'Optional[str]' = None) -> 'dict'` | Solve a convex optimization problem via CVXPY. |
| `installed_solvers() -> 'dict'` | Return available backends per category. |

### `prometheus_math.numerics` — Arbitrary precision and special functions

| Function | Summary |
|---|---|
| `Fraction(numerator=0, denominator=None, *, _normalize=True)` | This class implements rational numbers. |
| `Iterable(*args, **kwargs)` | A generic version of collections.abc.Iterable. |
| `Optional(*args, **kwds)` | Optional[X] is equivalent to Union[X, None]. |
| `Sequence(*args, **kwargs)` | A generic version of collections.abc.Sequence. |
| `bernoulli(n: 'int') -> 'Fraction'` | The n-th Bernoulli number B_n as an exact Fraction. |
| `beta(a, b, prec: 'int' = 53)` | Beta function B(a, b) = Γ(a)Γ(b)/Γ(a+b) at arbitrary precision. |
| `dirichlet_l(chi, s, prec: 'int' = 53)` | Dirichlet L-function L(s, χ). |
| `gamma(z, prec: 'int' = 53)` | Gamma function Γ(z) at arbitrary precision (BITS). |
| `is_available(name: 'str') -> 'bool'` | True iff backend `name` is available. |
| `lindep_complex(z, max_deg: 'int' = 8, prec: 'int' = 200) -> 'Optional[list[int]]'` | Find an integer-polynomial relation satisfied by complex z. |
| `mpc(real, imag=0, prec: 'int' = 53)` | Arbitrary-precision complex number. |
| `mpf(x, prec: 'int' = 53)` | Arbitrary-precision real number. |
| `pslq(x: 'Sequence', tol: 'Optional[float]' = None, max_coeff: 'int' = 1000000) -> 'Optional[list[int]]'` | Find an integer relation among a list of mpmath floats. |
| `set_precision(prec_bits: 'int') -> 'None'` | Set global mpmath precision in BITS (mpmath.mp.prec). |
| `solve_polynomial(coeffs: 'Sequence', prec: 'int' = 53) -> 'list'` | Roots of a polynomial at arbitrary precision. |
| `workprec(n, normalize_output=False)` | The block |
| `zeta(s, prec: 'int' = 53)` | Riemann zeta function ζ(s) at arbitrary precision. |

### `prometheus_math.symbolic` — Symbolic computation (CAS)

| Function | Summary |
|---|---|
| `ExprLike(*args, **kwargs)` |  |
| `Optional(*args, **kwds)` | Optional[X] is equivalent to Union[X, None]. |
| `Sequence(*args, **kwargs)` | A generic version of collections.abc.Sequence. |
| `Union(*args, **kwds)` | Union type; Union[X, Y] means either X or Y. |
| `differentiate(expr: 'ExprLike', var) -> 'sympy.Expr'` | Differentiate w.r.t. var (avoids name clash with sympy.diff). |
| `discriminant(p: 'ExprLike', var) -> 'sympy.Expr'` | Discriminant of polynomial `p` in variable `var`. |
| `expand(expr: 'ExprLike') -> 'sympy.Expr'` | Expand a polynomial / expression. |
| `factor(expr: 'ExprLike') -> 'sympy.Expr'` | Factor a polynomial / expression. |
| `groebner_basis(polys: 'Sequence[ExprLike]', vars: 'Sequence', order: 'str' = 'lex') -> 'list'` | Gröbner basis of an ideal. |
| `integrate(expr: 'ExprLike', var) -> 'sympy.Expr'` | Indefinite integral. |
| `is_available(name: 'str') -> 'bool'` | True iff backend `name` is available. |
| `parse(s: 'ExprLike') -> 'sympy.Expr'` | Parse a string (or pass-through expression) into a sympy.Expr. |
| `polynomial_factor_finite(poly: 'ExprLike', p: 'int') -> 'list'` | Factor a polynomial over GF(p). |
| `resultant(p: 'ExprLike', q: 'ExprLike', var) -> 'sympy.Expr'` | Resultant of two polynomials in `var`. |
| `series_expand(expr: 'ExprLike', var, x0=0, n: 'int' = 6) -> 'sympy.Expr'` | Taylor / Laurent series of `expr` around `var = x0` to order n. |
| `simplify(expr: 'ExprLike') -> 'sympy.Expr'` | Simplify an expression (sympy.simplify). |
| `solve(expr_or_eqs, vars=None)` | Solve equation(s) for given variable(s). |
| `solve_ode(eq, func) -> 'sympy.Expr'` | Solve an ODE. |

---

## What's not yet wrapped

See `techne/ARSENAL_ROADMAP.md` for the long-term tracker covering:

- Tools installed but not yet exposed via this API
- Heavy native installs queued (GAP, Macaulay2, Lean 4, Julia, SageMath)
- Linux-only / WSL2 tools (Regina, polymake, nauty, fpLLL)
- Web service wrappers (LMFDB, OEIS, KnotInfo, arXiv, zbMATH)
- AI/ML integrations (DeepSeek-Prover, Lean Copilot)
- Reverse-engineered paywalled functionality (Magma algorithms)
- Novel tools we've identified as needed but don't yet exist

---

*Auto-generated by `prometheus_math.doc.arsenal()`. Re-run after adding new operations or backends.*
