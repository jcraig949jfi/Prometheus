"""prometheus_math._metadata_table — central ArsenalMeta registration.

Side-effect-only module: importing it populates ``ARSENAL_REGISTRY``
with metadata for ~80 representative arsenal operations across 9
categories. The metadata is calibrated from one-shot profiling runs
(2026-04-29) on a Windows 11 / Ryzen 7 5700X / mpmath dps=15 host;
declared ``max_seconds`` are p95 * (~5x to 30x safety margin) so that
real EVAL ratios stay in the 0.05-0.5 range.

This file is the *only* place where arsenal callables are tagged.
Source modules in ``prometheus_math/`` and ``techne/lib/`` are not
decorated, which keeps merge surface clean for other agents.

Each registration is wrapped in ``try/except`` so that a missing backend
(e.g. snappy not installed → topology ops absent) does not break the
whole table.

Authority refs cite the same primary sources the math-tdd skill enforces
on commit (Cohen GTM 138 Tables 1.1-1.4, LMFDB labels, Mossinghoff
Mahler tables, Whittaker & Watson chapters, OEIS A-numbers, etc.).
Postconditions are *specific* invariants the math-tdd authority/property
tests assert; "output is correct" would fail review.
"""
from __future__ import annotations

from .arsenal_meta import ARSENAL_REGISTRY, ArsenalMeta


def _register(meta: ArsenalMeta) -> None:
    """Register one ArsenalMeta into the global registry."""
    ARSENAL_REGISTRY[meta.callable_ref] = meta


# ---------------------------------------------------------------------------
# numerics_special — special functions (calibrated p95 0.0-2.5ms; mostly
# mpmath wrappers, fast at default dps=15).
# ---------------------------------------------------------------------------

try:
    from . import numerics_special_dilogarithm  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_dilogarithm:dilogarithm",
        cost={"max_seconds": 5.1e-05, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 1.0772, "fit_r2": 0.75, "p95_seconds": 3e-06, "median_at_smallest_us": 1.0, "median_at_largest_us": 0.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "Li_2(0) == 0",
            "Li_2(1) == zeta(2) == pi^2/6",
            "Li_2(-1) == -pi^2/12",
            "real-valued for z in (-inf, 1]",
        ],
        authority_refs=[
            "Lewin 1981 (Polylogarithms and Associated Functions)",
            "Abramowitz & Stegun 27.7",
            "Basel: Li_2(1) = zeta(2) = pi^2/6",
        ],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Dilogarithm Li_2(z) via mpmath polylog; default dps=15.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_dilogarithm:polylogarithm",
        cost={"max_seconds": 0.003, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n^3)', "coefficient_us": 0.264, "fit_r2": 0.709, "p95_seconds": 0.000201, "median_at_smallest_us": 0.9, "median_at_largest_us": 65.7, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "Li_n(1) == zeta(n) for n >= 2",
            "Li_n(0) == 0",
            "Li_1(z) == -ln(1 - z)",
        ],
        authority_refs=["Lewin 1981 §1", "Abramowitz & Stegun 27.7"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Polylog Li_n(z) — n=1..10 cheap, n>=20 expensive at default dps.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_dilogarithm:bloch_wigner_dilog",
        cost={"max_seconds": 0.0078, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 377.6146, "fit_r2": 0.722, "p95_seconds": 0.00052, "median_at_smallest_us": 395.6, "median_at_largest_us": 513.0, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "real-valued output (BWD is single-valued real)",
            "D(z) == -D(1/z) (5-term identity component)",
            "D(0) == 0",
        ],
        authority_refs=["Bloch 1978 'Higher regulators...'", "Zagier 'The Bloch-Wigner-Ramakrishnan polylog'"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Bloch-Wigner dilogarithm; key for hyperbolic 3-volume of ideal tetrahedra.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_dilogarithm:clausen",
        cost={"max_seconds": 0.0059, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(log n)', "coefficient_us": 219.6768, "fit_r2": 0.964, "p95_seconds": 0.000391, "median_at_smallest_us": 213.8, "median_at_largest_us": 347.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "Cl_2(0) == 0",
            "Cl_2(pi) == 0",
            "Cl_2(theta + 2*pi) == Cl_2(theta) (periodic)",
        ],
        authority_refs=["Lewin 1981 §4", "Catalan's constant: Cl_2(pi/2) = G"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Clausen function Cl_2(theta) = Im(Li_2(e^{i*theta})).",
    ))
except ImportError:
    pass

try:
    from . import numerics_special_hurwitz  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_hurwitz:hurwitz_zeta",
        cost={"max_seconds": 6.2e-05, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 1.6126, "fit_r2": 1.0, "p95_seconds": 4e-06, "median_at_smallest_us": 1.5, "median_at_largest_us": 1.3, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "zeta(s, 1) == zeta(s) (Riemann zeta)",
            "zeta(s, 2) == zeta(s) - 1",
            "Re(a) > 0 required",
        ],
        authority_refs=["Apostol 'Introduction to Analytic Number Theory' §12", "Whittaker & Watson §13.13"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Hurwitz zeta zeta(s, a); generalises Riemann zeta.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_hurwitz:polygamma",
        cost={"max_seconds": 0.002, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 111.8905, "fit_r2": 1.0, "p95_seconds": 0.000131, "median_at_smallest_us": 16.2, "median_at_largest_us": 95.0, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "psi^(0)(1) == -gamma_em (Euler-Mascheroni)",
            "psi^(1)(1) == pi^2/6 == zeta(2)",
            "psi^(n)(x) == (-1)^(n+1) * n! * zeta(n+1, x)",
        ],
        authority_refs=["Abramowitz & Stegun 6.4", "Whittaker & Watson §12.32"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Polygamma psi^(n)(x); n=0 is digamma, n>=1 is derivative.",
    ))
except ImportError:
    pass

try:
    from . import numerics_special_theta  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_theta:theta_null_value",
        cost={"max_seconds": 0.00036, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 13.0222, "fit_r2": 0.946, "p95_seconds": 2.4e-05, "median_at_smallest_us": 13.1, "median_at_largest_us": 11.7, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "theta_3(0,q)^4 == theta_2(0,q)^4 + theta_4(0,q)^4 (Jacobi identity)",
            "theta_2(0,0) == 0",
            "theta_3(0,0) == 1",
            "theta_4(0,0) == 1",
        ],
        authority_refs=["Whittaker & Watson §21.41", "Mumford 'Tata Lectures on Theta'"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Jacobi nullwert theta_n(0, q); foundation of modular form theory.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_theta:jacobi_theta",
        cost={"max_seconds": 0.00024, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 11.6029, "fit_r2": 0.998, "p95_seconds": 1.6e-05, "median_at_smallest_us": 11.6, "median_at_largest_us": 11.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "theta_n(z + pi, q) follows quasi-periodicity formulas",
            "theta_2(0, q) == 2 q^(1/4) * sum_{k>=0} q^{k(k+1)}",
            "n in {1,2,3,4}",
        ],
        authority_refs=["Whittaker & Watson §21", "Tannery & Molk 'Elements de la theorie des fonctions elliptiques'"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Jacobi theta theta_n(z, q); n=1 is odd, others even.",
    ))
except ImportError:
    pass

try:
    from . import numerics_special_eta  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_eta:eta",
        cost={"max_seconds": 0.001, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 58.2386, "fit_r2": 0.979, "p95_seconds": 6.7e-05, "median_at_smallest_us": 59.5, "median_at_largest_us": 36.0, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "Im(tau) > 0 required",
            "eta(tau + 1) == exp(i*pi/12) * eta(tau) (T transformation)",
            "eta(-1/tau) == sqrt(-i*tau) * eta(tau) (S transformation, weight 1/2)",
        ],
        authority_refs=["Apostol 'Modular Functions and Dirichlet Series in Number Theory' §3"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Dedekind eta eta(tau) = q^{1/24} prod (1 - q^n).",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_eta:j_invariant",
        cost={"max_seconds": 0.001, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 59.3642, "fit_r2": 0.823, "p95_seconds": 6.9e-05, "median_at_smallest_us": 61.0, "median_at_largest_us": 49.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "j(i) == 1728",
            "j((-1+sqrt(-3))/2) == 0",
            "Im(tau) > 0 required",
            "j is SL_2(Z) invariant",
        ],
        authority_refs=["Silverman 'Advanced Topics in the Arithmetic of Elliptic Curves' §I", "j-invariant: SL2(Z)-invariant function on H"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Klein j-invariant j(tau); generates field of modular functions.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_eta:eta_quotient",
        cost={"max_seconds": 0.0013, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 82.8602, "fit_r2": 0.99, "p95_seconds": 8.8e-05, "median_at_smallest_us": 83.4, "median_at_largest_us": 66.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "all coefficients are integers",
            "Im(tau) > 0 required",
            "matches eta(tau)^a * eta(2*tau)^b * ... formula",
        ],
        authority_refs=["Ono 'Web of Modularity' §1", "Ligozat 1975 'Courbes modulaires de genre 1'"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="eta-quotient prod_d eta(d*tau)^{r_d}.",
    ))
except ImportError:
    pass

try:
    from . import numerics_special_q_pochhammer  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_q_pochhammer:euler_function",
        cost={"max_seconds": 0.00056, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 31.165, "fit_r2": 0.814, "p95_seconds": 3.7e-05, "median_at_smallest_us": 31.8, "median_at_largest_us": 36.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "euler_function(0) == 1",
            "|q| < 1 required",
            "phi(q) == prod_{k>=1} (1 - q^k)",
            "1/phi(q) == sum_{n>=0} p(n) q^n (Euler partition gen-fn)",
        ],
        authority_refs=["Whittaker & Watson §22", "Euler 1748 'Introductio in Analysin Infinitorum'"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Euler function phi(q) = (q;q)_inf.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_q_pochhammer:dedekind_eta",
        cost={"max_seconds": 0.00076, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 48.261, "fit_r2": 0.982, "p95_seconds": 5.1e-05, "median_at_smallest_us": 49.2, "median_at_largest_us": 29.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "Im(tau) > 0 required",
            "eta(tau) == q^{1/24} * phi(q) where q = exp(2*pi*i*tau)",
            "matches numerics_special_eta:eta to numerical precision",
        ],
        authority_refs=["Apostol 'Modular Functions and Dirichlet Series in Number Theory' §3"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="Dedekind eta via q-Pochhammer (alternative implementation).",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics_special_q_pochhammer:q_pochhammer",
        cost={"max_seconds": 0.0025, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 172.027, "fit_r2": 0.62, "p95_seconds": 0.000169, "median_at_smallest_us": 129.9, "median_at_largest_us": 37.5, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "(a;q)_0 == 1",
            "(a;q)_n == prod_{k=0}^{n-1} (1 - a*q^k)",
            "|q| < 1 for infinite case n=None",
        ],
        authority_refs=["Gasper & Rahman 'Basic Hypergeometric Series' §1.2"],
        equivalence_class="ideal_reduction",
        category="numerics_special",
        notes="q-Pochhammer (a;q)_n; n=None gives infinite product.",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# combinatorics — partitions / Young tableaux / RSK / posets.
# ---------------------------------------------------------------------------

try:
    from . import combinatorics_partitions  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.combinatorics_partitions:num_partitions",
        cost={"max_seconds": 0.00027, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 0.1001, "fit_r2": 1.0, "p95_seconds": 1.8e-05, "median_at_smallest_us": 0.1, "median_at_largest_us": 0.1, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "num_partitions(0) == 1",
            "num_partitions(n) > 0 for n >= 0",
            "p(100) == 190569292 (Hardy-Ramanujan)",
            "p(n) follows Euler pentagonal-number recurrence",
        ],
        authority_refs=["OEIS A000041", "Hardy & Ramanujan 1918 'Asymptotic formulae in combinatory analysis'", "Euler pentagonal-number theorem"],
        equivalence_class="partition_refinement",
        category="combinatorics",
        notes="Integer partition counting via Euler pentagonal recurrence.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.combinatorics_partitions:partitions_of",
        cost={"max_seconds": 0.0011, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n^3)', "coefficient_us": 0.0287, "fit_r2": 0.995, "p95_seconds": 7.2e-05, "median_at_smallest_us": 4.6, "median_at_largest_us": 71.4, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "partitions_of(0) == [()]",
            "len(partitions_of(n)) == num_partitions(n)",
            "each partition is weakly decreasing",
            "sum of each partition equals n",
        ],
        authority_refs=["Stanley EC2 §7.1", "Andrews 'The Theory of Partitions'"],
        equivalence_class="partition_refinement",
        category="combinatorics",
        notes="Enumerate all partitions of n; explodes for n > 60.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.combinatorics_partitions:conjugate",
        cost={"max_seconds": 0.00017, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 0.2257, "fit_r2": 0.991, "p95_seconds": 1.1e-05, "median_at_smallest_us": 1.9, "median_at_largest_us": 11.4, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "conjugate(conjugate(p)) == p (involution)",
            "len(conjugate(p)) == p[0] for non-empty p",
            "sum(conjugate(p)) == sum(p)",
        ],
        authority_refs=["Stanley EC2 §7.2", "Macdonald 'Symmetric Functions and Hall Polynomials' I.1"],
        equivalence_class="partition_refinement",
        category="combinatorics",
        notes="Transpose partition diagram (Young conjugation).",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.combinatorics_partitions:num_standard_young_tableaux",
        cost={"max_seconds": 0.00042, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n log n)', "coefficient_us": 0.7708, "fit_r2": 0.999, "p95_seconds": 2.8e-05, "median_at_smallest_us": 4.4, "median_at_largest_us": 20.6, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "f^{(n)} == 1 (single-row)",
            "f^{(1^n)} == 1 (single-column)",
            "matches Frame-Robinson-Thrall hook-length formula",
        ],
        authority_refs=["Frame, Robinson, Thrall 1954 'The hook graphs of the symmetric group'", "Stanley EC2 §7.21"],
        equivalence_class="partition_refinement",
        category="combinatorics",
        notes="f^lambda = n! / prod(hook lengths); dimension of irrep V_lambda of S_n.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.combinatorics_partitions:rsk",
        cost={"max_seconds": 7.5e-05, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 0.3745, "fit_r2": 0.944, "p95_seconds": 5e-06, "median_at_smallest_us": 1.4, "median_at_largest_us": 4.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "rsk yields shape(P) == shape(Q)",
            "P, Q are standard Young tableaux for permutations",
            "inverse_rsk(rsk(perm)) recovers perm",
        ],
        authority_refs=["Stanley EC2 §7.11", "Knuth 1970 'Permutations, matrices, and generalized Young tableaux'", "Schensted 1961"],
        equivalence_class="partition_refinement",
        category="combinatorics",
        notes="Robinson-Schensted-Knuth correspondence; permutation -> (P, Q) tableaux.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.combinatorics_partitions:hook_length_array",
        cost={"max_seconds": 0.0021, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n^2)', "coefficient_us": 0.2353, "fit_r2": 0.998, "p95_seconds": 0.00014, "median_at_smallest_us": 7.2, "median_at_largest_us": 133.2, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "all hook lengths are positive integers",
            "hook lengths satisfy h(i,j) = (lambda_i - j) + (lambda'_j - i) + 1",
        ],
        authority_refs=["Macdonald 'Symmetric Functions and Hall Polynomials' I.1"],
        equivalence_class="partition_refinement",
        category="combinatorics",
        notes="Hook lengths array for a Young diagram.",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# numerics — flint backend, mpmath FFT, classical numerics.
# ---------------------------------------------------------------------------

try:
    from . import numerics  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics:flint_factor",
        cost={"max_seconds": 0.0014, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 5.1523, "fit_r2": 0.998, "p95_seconds": 9.6e-05, "median_at_smallest_us": 18.9, "median_at_largest_us": 68.1, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "factor product equals input polynomial (up to leading sign)",
            "each factor is irreducible over Z",
            "exponents are positive integers",
        ],
        authority_refs=["Cohen GTM 138 §3.5 (Berlekamp-Zassenhaus)", "FLINT documentation 'fmpz_poly_factor'"],
        equivalence_class="ideal_reduction",
        category="numerics",
        notes="Integer polynomial factorization via FLINT.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics:flint_polmodp",
        cost={"max_seconds": 9.9e-05, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(log n)', "coefficient_us": 0.912, "fit_r2": 0.994, "p95_seconds": 7e-06, "median_at_smallest_us": 1.8, "median_at_largest_us": 3.5, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "all coefficients are in [0, p)",
            "p must be prime",
            "result represents same polynomial mod p as input",
        ],
        authority_refs=["Cohen GTM 138 §3.4", "FLINT 'nmod_poly'"],
        equivalence_class="ideal_reduction",
        category="numerics",
        notes="Reduce polynomial mod prime p via FLINT.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics:flint_matmul_modp",
        cost={"max_seconds": 0.0014, "max_memory_mb": 128, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n log n)', "coefficient_us": 1.0119, "fit_r2": 0.996, "p95_seconds": 9.5e-05, "median_at_smallest_us": 9.6, "median_at_largest_us": 87.5, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "all entries are in [0, p)",
            "(A @ B) mod p == result",
            "p must be prime",
        ],
        authority_refs=["FLINT 'nmod_mat_mul'"],
        equivalence_class="ideal_reduction",
        category="numerics",
        notes="Matrix multiplication mod p via FLINT.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics:mpdft",
        cost={"max_seconds": 0.0036, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 17.0674, "fit_r2": 0.987, "p95_seconds": 0.000242, "median_at_smallest_us": 60.2, "median_at_largest_us": 203.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "len(output) == len(input)",
            "Parseval: sum |X_k|^2 == N * sum |x_n|^2",
            "DFT(IDFT(x)) == x",
        ],
        authority_refs=["Cooley-Tukey 1965", "Numerical Recipes §12.2"],
        equivalence_class="ideal_reduction",
        category="numerics",
        notes="Arbitrary-precision DFT via mpmath; n need not be a power of 2.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics:mpfft",
        cost={"max_seconds": 0.0032, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 11.6831, "fit_r2": 1.0, "p95_seconds": 0.000217, "median_at_smallest_us": 47.8, "median_at_largest_us": 194.0, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "len(output) == len(input)",
            "len(input) must be a power of 2",
            "matches mpdft to working precision",
        ],
        authority_refs=["Cooley-Tukey 1965", "Numerical Recipes §12.2"],
        equivalence_class="ideal_reduction",
        category="numerics",
        notes="Radix-2 FFT in mpmath arbitrary precision.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics:bernoulli",
        cost={"max_seconds": 0.0073, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 1.1882, "fit_r2": 0.816, "p95_seconds": 0.000485, "median_at_smallest_us": 1.0, "median_at_largest_us": 0.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "B_0 == 1",
            "B_1 == -1/2 (or +1/2 by convention; this lib uses Bernoulli^- = -1/2)",
            "B_{2n+1} == 0 for n >= 1",
            "B_{2n} alternate sign with n",
        ],
        authority_refs=["Cohen GTM 240 §9.5", "Abramowitz & Stegun 23.1"],
        equivalence_class="ideal_reduction",
        category="numerics",
        notes="Bernoulli numbers as Fraction (exact rationals).",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.numerics:zeta",
        cost={"max_seconds": 0.00032, "max_memory_mb": 32, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 5.1446, "fit_r2": 0.879, "p95_seconds": 2.1e-05, "median_at_smallest_us": 4.5, "median_at_largest_us": 3.2, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "zeta(2) == pi^2 / 6 (Basel)",
            "zeta(4) == pi^4 / 90",
            "zeta(-1) == -1/12 (analytic continuation)",
            "zeta(0) == -1/2",
        ],
        authority_refs=["Riemann 1859", "Edwards 'Riemann's Zeta Function'"],
        equivalence_class="ideal_reduction",
        category="numerics",
        notes="Riemann zeta via mpmath (analytic continuation everywhere except s=1).",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# geometry — convex hull / Voronoi / Delaunay.
# ---------------------------------------------------------------------------

try:
    from . import geometry_convex_hull  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.geometry_convex_hull:convex_hull",
        cost={"max_seconds": 0.0058, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 304.6393, "fit_r2": 0.946, "p95_seconds": 0.000388, "median_at_smallest_us": 327.6, "median_at_largest_us": 364.5, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "all hull vertices are extreme points of input",
            "vertices are returned in CCW order in 2D",
            "volume is non-negative",
            "len(hull) >= d+1 for d-dim non-degenerate inputs",
        ],
        authority_refs=["Barber, Dobkin, Huhdanpaa 1996 'The Quickhull Algorithm'", "scipy.spatial.ConvexHull"],
        equivalence_class="variety_fingerprint",
        category="geometry",
        notes="Convex hull via QHull; 2D and higher.",
    ))
except ImportError:
    pass

try:
    from . import geometry_voronoi  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.geometry_voronoi:voronoi_diagram",
        cost={"max_seconds": 0.011, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(log n)', "coefficient_us": 242.7407, "fit_r2": 0.914, "p95_seconds": 0.000759, "median_at_smallest_us": 395.3, "median_at_largest_us": 707.1, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "every input point is a Voronoi seed",
            "cells partition the plane (modulo unbounded cells)",
            "Voronoi is the dual of Delaunay",
        ],
        authority_refs=["Voronoi 1908", "scipy.spatial.Voronoi (QHull)"],
        equivalence_class="variety_fingerprint",
        category="geometry",
        notes="Voronoi diagram of 2D point set; unbounded cells flagged.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.geometry_voronoi:lloyd_relaxation",
        cost={"max_seconds": 0.011, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(log n)', "coefficient_us": 242.7407, "fit_r2": 0.914, "p95_seconds": 0.000759, "median_at_smallest_us": 395.3, "median_at_largest_us": 707.1, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "len(output) == len(input)",
            "iterating to convergence yields a CVT (centroidal Voronoi tessellation)",
            "energy decreases monotonically",
        ],
        authority_refs=["Lloyd 1982 'Least squares quantization in PCM'", "Du, Faber, Gunzburger 1999 'Centroidal Voronoi Tessellations'"],
        equivalence_class="variety_fingerprint",
        category="geometry",
        notes="Lloyd's algorithm for centroidal Voronoi tessellation.",
    ))
except ImportError:
    pass

try:
    from . import geometry_delaunay  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.geometry_delaunay:delaunay_triangulation",
        cost={"max_seconds": 0.28, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 136.4203, "fit_r2": 0.641, "p95_seconds": 0.01859, "median_at_smallest_us": 1488.2, "median_at_largest_us": 17668.1, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "every input point is a vertex",
            "triangulation has empty-circumcircle property",
            "n_simplices == 2*n - 2 - h for 2D (h = #hull vertices)",
        ],
        authority_refs=["Delaunay 1934", "scipy.spatial.Delaunay (QHull)"],
        equivalence_class="variety_fingerprint",
        category="geometry",
        notes="Delaunay triangulation of d-dim point set.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.geometry_delaunay:circumcenter",
        cost={"max_seconds": 0.00027, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 9.8391, "fit_r2": 0.229, "p95_seconds": 1.8e-05, "median_at_smallest_us": 9.7, "median_at_largest_us": 9.5, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "all simplex points equidistant from circumcenter",
            "for triangle: lies at intersection of perpendicular bisectors",
        ],
        authority_refs=["Berg, Cheong, van Kreveld, Overmars 'Computational Geometry' §9"],
        equivalence_class="variety_fingerprint",
        category="geometry",
        notes="Circumcenter of d-simplex (d+1 points).",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# dynamics — iterated maps, Lyapunov.
# ---------------------------------------------------------------------------

try:
    from . import dynamics_iterated_maps  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.dynamics_iterated_maps:logistic_map",
        cost={"max_seconds": 0.00075, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 0.0978, "fit_r2": 0.999, "p95_seconds": 5e-05, "median_at_smallest_us": 3.8, "median_at_largest_us": 49.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "all orbit values in [0, 1] for r in [0, 4]",
            "r=4: chaotic, full unit interval coverage",
            "r in [0, 3]: orbit converges to fixed point",
        ],
        authority_refs=["May 1976 'Simple mathematical models with very complicated dynamics'", "Strogatz 'Nonlinear Dynamics and Chaos' §10"],
        equivalence_class="variety_fingerprint",
        category="dynamics",
        notes="Logistic map x_{n+1} = r * x_n * (1 - x_n).",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.dynamics_iterated_maps:lyapunov_exponent",
        cost={"max_seconds": 0.00075, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 0.0978, "fit_r2": 0.999, "p95_seconds": 5e-05, "median_at_smallest_us": 3.8, "median_at_largest_us": 49.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "lambda > 0 implies chaos",
            "lambda <= 0 implies regular (periodic or fixed)",
            "logistic at r=4: lambda = ln 2 ≈ 0.693",
        ],
        authority_refs=["Oseledec 1968 multiplicative ergodic theorem", "Strogatz 'Nonlinear Dynamics and Chaos' §10.5"],
        equivalence_class="variety_fingerprint",
        category="dynamics",
        notes="Maximum Lyapunov exponent of a 1-D map (analytic-derivative method).",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.dynamics_iterated_maps:tent_map",
        cost={"max_seconds": 0.00071, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 0.0947, "fit_r2": 0.998, "p95_seconds": 4.8e-05, "median_at_smallest_us": 3.5, "median_at_largest_us": 44.1, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "all orbit values in [0, 1]",
            "tent has lambda = ln 2 (always chaotic)",
        ],
        authority_refs=["Strogatz §10", "Devaney 'An Introduction to Chaotic Dynamical Systems' §1.7"],
        equivalence_class="variety_fingerprint",
        category="dynamics",
        notes="Tent map x_{n+1} = 2*min(x_n, 1 - x_n).",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# topology — knots, hyperbolic 3-manifolds.
# ---------------------------------------------------------------------------

try:
    from techne.lib import hyperbolic_volume  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.hyperbolic_volume:hyperbolic_volume",
        cost={"max_seconds": 0.00071, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 0.0947, "fit_r2": 0.998, "p95_seconds": 4.8e-05, "median_at_smallest_us": 3.5, "median_at_largest_us": 44.1, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "hyperbolic_volume('4_1') ≈ 2.0298832128 (figure-eight)",
            "hyperbolic_volume('5_2') ≈ 2.8281220883",
            "vol > 0 for hyperbolic knots",
            "raises if non-hyperbolic",
        ],
        authority_refs=["SnapPy", "Thurston 'The Geometry and Topology of 3-Manifolds'", "LMFDB knots"],
        equivalence_class="variety_fingerprint",
        category="topology",
        notes="Hyperbolic 3-volume of knot complement via SnapPy.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.hyperbolic_volume:is_hyperbolic",
        cost={"max_seconds": 0.02, "max_memory_mb": 64, "max_oracle_calls": 0},
        postconditions=[
            "True for figure-eight (4_1)",
            "False for unknot",
            "False for torus knots (Seifert-fibered)",
        ],
        authority_refs=["Thurston geometrization", "SnapPy"],
        equivalence_class="variety_fingerprint",
        category="topology",
        notes="Tests if knot complement admits hyperbolic structure.",
    ))
except ImportError:
    pass

try:
    from techne.lib import alexander_polynomial  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.alexander_polynomial:alexander_polynomial",
        cost={"max_seconds": 0.02, "max_memory_mb": 64, "max_oracle_calls": 0},
        postconditions=[
            "Delta_K(t) is a Laurent polynomial in t",
            "Delta_K(1) is +/- 1 for knots",
            "figure-eight 4_1: Delta = -t + 3 - 1/t",
            "unknot: Delta = 1",
        ],
        authority_refs=["Alexander 1928", "Rolfsen 'Knots and Links' §6", "LMFDB knots"],
        equivalence_class="variety_fingerprint",
        category="topology",
        notes="Alexander polynomial Delta_K(t) of a knot.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.alexander_polynomial:alexander_coeffs",
        cost={"max_seconds": 0.01, "max_memory_mb": 64, "max_oracle_calls": 0},
        postconditions=[
            "list of integer coefficients",
            "abs(Delta(1)) == 1 for knots",
            "palindromic (reciprocal) up to sign",
        ],
        authority_refs=["Alexander 1928", "Rolfsen 'Knots and Links' §6"],
        equivalence_class="variety_fingerprint",
        category="topology",
        notes="Integer coefficients of Alexander polynomial.",
    ))
except ImportError:
    pass

try:
    from techne.lib import knot_shape_field  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.knot_shape_field:polredabs",
        cost={"max_seconds": 0.02, "max_memory_mb": 64, "max_oracle_calls": 0},
        postconditions=[
            "output is monic integer polynomial",
            "minimal absolute discriminant in its NF isomorphism class",
            "deg(output) == deg(input)",
        ],
        authority_refs=["Cohen GTM 138 §4.4", "PARI 'polredabs'"],
        equivalence_class="ideal_reduction",
        category="topology",
        notes="Canonical defining polynomial for a number field (PARI polredabs).",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# number_theory / number_fields — class number, Galois group, LLL.
# ---------------------------------------------------------------------------

try:
    from techne.lib import class_number  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.class_number:class_number",
        cost={"max_seconds": 0.05, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "h(Q(sqrt(-1))) == 1",
            "h(Q(sqrt(-23))) == 3 (Cohen GTM 138 Table 1.1)",
            "h(Q(sqrt(-163))) == 1 (last imaginary quadratic with h=1)",
            "h(K) >= 1 always",
        ],
        authority_refs=["Cohen GTM 138 Table 1.1", "LMFDB number_field", "Stark-Heegner imaginary quadratic"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Class number h_K of a number field via PARI.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.class_number:class_group",
        cost={"max_seconds": 0.05, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "class_number == prod of class_group invariants",
            "trivial == True iff h == 1",
            "structure agrees with LMFDB",
        ],
        authority_refs=["Cohen GTM 138 Table 1.1, 1.2", "LMFDB number_field.class_group"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Class group structure (cyclic factors) of a number field.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.class_number:regulator_nf",
        cost={"max_seconds": 0.01, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "Reg(Q) = 1 for totally imaginary or unit-rank-0 fields",
            "Reg > 0 for totally real fields with rank >= 1",
            "Reg(Q(sqrt(2))) == log(1 + sqrt(2)) ≈ 0.8813735",
        ],
        authority_refs=["Cohen GTM 138 §4.9 / Tables 1.3, 1.4", "Dirichlet unit theorem"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Number-field regulator via PARI.",
    ))
except ImportError:
    pass

try:
    from techne.lib import galois_group  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.galois_group:galois_group",
        cost={"max_seconds": 0.005, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "Gal(x^2 - 2) is C_2",
            "Gal(x^3 - 2) is S_3",
            "Gal(x^5 - x - 1) is S_5",
            "order divides n!",
        ],
        authority_refs=["Cohen GTM 138 §6.3", "PARI 'polgalois'", "LMFDB nf.galois_group"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Galois group of irreducible polynomial via PARI polgalois.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.galois_group:is_abelian",
        cost={"max_seconds": 0.002, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "True for x^2 - d (any d)",
            "False for x^3 - 2 (S_3)",
            "True iff Galois group is abelian",
        ],
        authority_refs=["Cohen GTM 138 §6.3"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Test Galois-abelian via group structure.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.galois_group:disc_is_square",
        cost={"max_seconds": 0.002, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "True iff Galois group is contained in A_n",
            "matches sign-of-permutation criterion",
        ],
        authority_refs=["Cohen GTM 138 §6.3"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Test if disc(f) is a perfect square (Galois subset of A_n).",
    ))
except ImportError:
    pass

try:
    from techne.lib import hilbert_class_field  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.hilbert_class_field:hilbert_class_field",
        cost={"max_seconds": 0.1, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "[H:K] = h_K (class field theory)",
            "Gal(H/K) ≈ Cl(K) (Artin map)",
            "Q(sqrt(-23)): degree-3 extension",
        ],
        authority_refs=["Cohen 'Advanced Topics in Computational Number Theory' §6", "LMFDB nf.hilbert_class_field"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Hilbert class field H_K of a number field via PARI.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.hilbert_class_field:class_field_tower",
        cost={"max_seconds": 5.0, "max_memory_mb": 512, "max_oracle_calls": 0},
        postconditions=[
            "tower steps are abelian extensions",
            "Q(sqrt(-23)): tower terminates at depth 1 (h_H == 1)",
            "depth >= 0",
        ],
        authority_refs=["Furtwangler 1907", "Golod-Shafarevich 1964 (infinite towers exist)"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Iterated Hilbert class fields; can diverge (Golod-Shafarevich).",
    ))
except ImportError:
    pass

try:
    from techne.lib import p_class_field_tower  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.p_class_field_tower:p_hilbert_class_field",
        cost={"max_seconds": 1.0, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "Gal(H_p / K) is the p-part of Cl(K)",
            "p prime",
            "[H_p : K] divides h_K",
        ],
        authority_refs=["Iwasawa 'Local Class Field Theory' §V", "Cohen 'Advanced Topics' §6"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="p-part of the Hilbert class field; isolates p-class group.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.p_class_field_tower:p_class_field_tower",
        cost={"max_seconds": 10.0, "max_memory_mb": 1024, "max_oracle_calls": 0},
        postconditions=[
            "successively extends by p-class groups",
            "may terminate or diverge (Golod-Shafarevich p-tower)",
        ],
        authority_refs=["Golod-Shafarevich 1964", "Koch 'Galois Theory of p-Extensions'"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Iterated p-Hilbert class field tower.",
    ))
except ImportError:
    pass

try:
    from techne.lib import lll_reduction  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.lll_reduction:lll",
        cost={"max_seconds": 0.0018, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 3.094, "fit_r2": 0.967, "p95_seconds": 0.000117, "median_at_smallest_us": 12.9, "median_at_largest_us": 43.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "output is LLL-reduced basis (Lovasz condition with delta=3/4)",
            "abs(det(output)) == abs(det(input))",
            "first vector is short (within 2^{(n-1)/2} of shortest)",
        ],
        authority_refs=["Lenstra-Lenstra-Lovasz 1982", "Cohen GTM 138 §2.6"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="LLL lattice reduction via PARI qflll.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.lll_reduction:shortest_vector_lll",
        cost={"max_seconds": 0.0011, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 12.0077, "fit_r2": 0.683, "p95_seconds": 7.6e-05, "median_at_smallest_us": 27.1, "median_at_largest_us": 51.0, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "output is in lattice",
            "norm of output is short (LLL-approximation, not exact)",
        ],
        authority_refs=["LLL 1982", "Cohen GTM 138 §2.7"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="LLL-approximate shortest vector.",
    ))
except ImportError:
    pass

try:
    from techne.lib import smith_normal_form  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.smith_normal_form:smith_normal_form",
        cost={"max_seconds": 0.0053, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 47.2383, "fit_r2": 0.967, "p95_seconds": 0.000351, "median_at_smallest_us": 124.2, "median_at_largest_us": 284.6, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "output is diagonal",
            "diagonal entries d_1 | d_2 | ... | d_n (divisibility)",
            "abs(det(SNF)) == abs(det(input)) for square inputs",
        ],
        authority_refs=["Smith 1861", "Cohen GTM 138 §2.4"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Smith Normal Form for integer matrices.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.smith_normal_form:invariant_factors",
        cost={"max_seconds": 0.0046, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 36.4783, "fit_r2": 0.987, "p95_seconds": 0.000309, "median_at_smallest_us": 107.7, "median_at_largest_us": 276.5, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "list of positive integers",
            "each divides the next",
            "product equals abs(det) for square non-singular input",
        ],
        authority_refs=["Cohen GTM 138 §2.4"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Invariant factors (diagonal entries of SNF).",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.smith_normal_form:abelian_group_structure",
        cost={"max_seconds": 0.004, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 41.1556, "fit_r2": 0.996, "p95_seconds": 0.000265, "median_at_smallest_us": 109.2, "median_at_largest_us": 257.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "decomposes as Z^r x Z/d_1 x Z/d_2 x ... (d_i | d_{i+1})",
            "rank = number of zero invariant factors",
            "torsion order = product of nontrivial invariants",
        ],
        authority_refs=["Cohen GTM 138 §2.4", "Fundamental theorem of finitely generated abelian groups"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Abelian group structure from integer relation matrix.",
    ))
except ImportError:
    pass

try:
    from techne.lib import cm_order_data  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.cm_order_data:cm_order_data",
        cost={"max_seconds": 0.004, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 41.1556, "fit_r2": 0.996, "p95_seconds": 0.000265, "median_at_smallest_us": 109.2, "median_at_largest_us": 257.8, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "D < 0 (negative discriminant)",
            "class_number is a positive integer",
            "j_invariants list has length == class_number",
        ],
        authority_refs=["Cox 'Primes of the Form x^2 + ny^2' §7", "Cohen GTM 193 §5"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="CM order data for imaginary-quadratic discriminant D.",
    ))
except ImportError:
    pass

try:
    from techne.lib import mahler_measure  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.mahler_measure:mahler_measure",
        cost={"max_seconds": 0.0061, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n log n)', "coefficient_us": 1.2675, "fit_r2": 0.984, "p95_seconds": 0.000408, "median_at_smallest_us": 47.4, "median_at_largest_us": 399.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "M(P) >= 1 for non-zero integer polynomial",
            "M(cyclotomic) == 1 (Kronecker)",
            "M(Lehmer's) ≈ 1.17628081826 (smallest known > 1)",
            "M(P*Q) == M(P) * M(Q)",
        ],
        authority_refs=["Mossinghoff 'Lehmer's Problem'", "Lehmer 1933 'Factorization of certain cyclotomic functions'", "Smyth 1971 'On the product of conjugates outside the unit circle'"],
        equivalence_class="variety_fingerprint",
        category="research_lehmer",
        notes="Mahler measure M(P) of integer polynomial.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.mahler_measure:log_mahler_measure",
        cost={"max_seconds": 0.0061, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n log n)', "coefficient_us": 1.0706, "fit_r2": 0.989, "p95_seconds": 0.000405, "median_at_smallest_us": 44.3, "median_at_largest_us": 400.2, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "log_M(P) >= 0 for non-zero integer polynomial",
            "log_M(cyclotomic) == 0",
            "log_M(P*Q) == log_M(P) + log_M(Q)",
        ],
        authority_refs=["Mossinghoff 'Lehmer's Problem'", "Smyth 1971"],
        equivalence_class="variety_fingerprint",
        category="research_lehmer",
        notes="Logarithmic Mahler measure log M(P).",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.mahler_measure:is_cyclotomic",
        cost={"max_seconds": 0.0012, "max_memory_mb": 64, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n)', "coefficient_us": 6.0199, "fit_r2": 0.976, "p95_seconds": 8.1e-05, "median_at_smallest_us": 22.6, "median_at_largest_us": 80.1, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "True iff M(P) == 1 (Kronecker theorem)",
            "False if any root has |root| != 1",
            "agrees with palindromic-test for irreducible polys",
        ],
        authority_refs=["Kronecker 1857", "Mossinghoff 'Lehmer's Problem'"],
        equivalence_class="variety_fingerprint",
        category="research_lehmer",
        notes="Test: is integer polynomial a product of cyclotomics?",
    ))
except ImportError:
    pass

try:
    from techne.lib import cf_expansion  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.cf_expansion:cf_expand",
        cost={"max_seconds": 2.4e-05, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 0.4197, "fit_r2": 0.75, "p95_seconds": 2e-06, "median_at_smallest_us": 0.4, "median_at_largest_us": 0.3, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "cf_expand(22, 7) == [3, 7] (pi approximant)",
            "cf_expand(355, 113) == [3, 7, 16] (closer pi approximant)",
            "all entries except possibly the first are positive",
        ],
        authority_refs=["Khinchin 'Continued Fractions'", "Cohen GTM 138 §1.3"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Euclidean continued-fraction expansion of p/q.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.cf_expansion:cf_max_digit",
        cost={"max_seconds": 1.4e-05, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 0.4309, "fit_r2": 0.0, "p95_seconds": 1e-06, "median_at_smallest_us": 0.4, "median_at_largest_us": 0.4, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "max digit >= 1",
            "matches max(cf_expand(p, q))",
        ],
        authority_refs=["Zaremba 1972 'La methode des bons treillis pour le calcul des integrales multiples'"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Largest CF digit (Zaremba conjecture target).",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.cf_expansion:zaremba_test",
        cost={"max_seconds": 5e-05, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 0.4309, "fit_r2": 0.0, "p95_seconds": 1e-06, "median_at_smallest_us": 0.4, "median_at_largest_us": 0.4, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "returns dict with 'max_digit', 'witnesses' fields",
            "for q with bounded-CF representative: max_digit <= bound",
        ],
        authority_refs=["Zaremba 1972", "Bourgain-Kontorovich 2014 'On Zaremba's conjecture'"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Search representatives p/q with bounded CF digits (Zaremba conjecture).",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.cf_expansion:sturm_bound",
        cost={"max_seconds": 2.1e-05, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 1.4842, "fit_r2": 0.794, "p95_seconds": 1e-06, "median_at_smallest_us": 1.0, "median_at_largest_us": 0.5, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "sturm_bound(12, 11) == 12 (matches Stein 'Modular Forms: A Computational Approach' Th. 9.18)",
            "increases with weight and level",
            "bound is sharp for the modular forms space",
        ],
        authority_refs=["Sturm 1987 'On the congruence of modular forms'", "Stein 'Modular Forms: A Computational Approach' Theorem 9.18"],
        equivalence_class="ideal_reduction",
        category="number_theory",
        notes="Sturm bound: q-expansion coefficients needed to determine a modular form.",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# elliptic_curves — BSD audit chain.
# ---------------------------------------------------------------------------

try:
    from techne.lib import regulator  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="techne.lib.regulator:regulator",
        cost={"max_seconds": 5e-05, "max_memory_mb": 256, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 1.4842, "fit_r2": 0.794, "p95_seconds": 1e-06, "median_at_smallest_us": 1.0, "median_at_largest_us": 0.5, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "Reg(E) >= 0",
            "Reg(E) > 0 iff rank(E) >= 1",
            "rank-0 curves: Reg == 1 (empty product convention)",
            "37a1 (smallest rank-1): Reg matches LMFDB",
        ],
        authority_refs=["Cohen GTM 239 §8.4 (Heights and Néron-Tate)", "LMFDB ec.regulator"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="Néron-Tate regulator of an elliptic curve E/Q via PARI.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.regulator:mordell_weil",
        cost={"max_seconds": 0.1, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "rank in {0, 1, 2, ...}",
            "torsion subgroup is one of Mazur's 15 possibilities",
            "rank matches LMFDB for known curves",
        ],
        authority_refs=["Mordell 1922", "Mazur 1977 'Modular curves and the Eisenstein ideal'", "LMFDB ec.mw_data"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="Mordell-Weil group: (rank, torsion, generators) of E/Q.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.conductor:conductor",
        cost={"max_seconds": 0.00096, "max_memory_mb": 256, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n^2)', "coefficient_us": 5.7002, "fit_r2": 1.0, "p95_seconds": 6.4e-05, "median_at_smallest_us": 6.6, "median_at_largest_us": 21.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "N(E) is a positive integer",
            "primes dividing N == primes of bad reduction",
            "37a1: N == 37 (smallest rank-1)",
            "11a1: N == 11 (smallest rank-0, modular)",
        ],
        authority_refs=["Silverman 'Arithmetic of Elliptic Curves' §VII", "LMFDB ec.conductor"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="Conductor N(E) of E/Q via PARI ellglobalred.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.conductor:bad_primes",
        cost={"max_seconds": 0.00081, "max_memory_mb": 256, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n^2)', "coefficient_us": 6.8001, "fit_r2": 1.0, "p95_seconds": 5.4e-05, "median_at_smallest_us": 6.8, "median_at_largest_us": 22.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "list of primes",
            "each divides conductor N(E)",
            "for E good: empty list",
        ],
        authority_refs=["Silverman 'Arithmetic of Elliptic Curves' §VII"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="Primes of bad reduction for E/Q.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.root_number:root_number",
        cost={"max_seconds": 0.00042, "max_memory_mb": 256, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(n^2)', "coefficient_us": 5.0, "fit_r2": 1.0, "p95_seconds": 2.8e-05, "median_at_smallest_us": 5.3, "median_at_largest_us": 21.9, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "w(E) in {-1, +1}",
            "w(E) == (-1)^rank under BSD parity",
            "37a1: w == -1",
            "11a1: w == +1",
        ],
        authority_refs=["Birch-Stephens 1966", "LMFDB ec.root_number"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="Global root number w(E) of E/Q (sign of functional equation).",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.faltings_height:faltings_height",
        cost={"max_seconds": 0.0019, "max_memory_mb": 256, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 74.3, "fit_r2": 1.0, "p95_seconds": 0.000128, "median_at_smallest_us": 88.6, "median_at_largest_us": 80.3, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "real-valued",
            "h_F(E) tracks log of arithmetic complexity of E",
            "matches LMFDB faltings_height for known curves",
        ],
        authority_refs=["Faltings 1983 'Endlichkeitssatze fur abelsche Varietaten uber Zahlkorpern'", "LMFDB ec.faltings_height"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="Faltings height h_F(E) of an elliptic curve.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.analytic_sha:analytic_sha",
        cost={"max_seconds": 0.0019, "max_memory_mb": 256, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(1)', "coefficient_us": 74.3, "fit_r2": 1.0, "p95_seconds": 0.000128, "median_at_smallest_us": 88.6, "median_at_largest_us": 80.3, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "returns dict with 'sha_an', 'sha_an_rounded' fields",
            "sha_an_rounded is a positive integer",
            "BSD: |Sha(E)| should be perfect square; rounded value matches LMFDB",
            "37a1: sha_an_rounded == 1",
        ],
        authority_refs=["Birch-Swinnerton-Dyer 1965", "Cohen GTM 240 §8.6", "LMFDB ec.sha_an"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="Analytic Sha (Tate-Shafarevich) computed via BSD numerical formula.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.selmer_rank:selmer_2_rank",
        cost={"max_seconds": 0.05, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "non-negative integer",
            ">= rank(E) (Selmer bounds rank from above)",
            "for E with trivial 2-Sha: equals rank + dim(E[2](Q))",
        ],
        authority_refs=["Cremona 'Algorithms for Modular Elliptic Curves' §3", "LMFDB ec.selmer_rank"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="2-Selmer rank of E/Q via PARI ellrank.",
    ))
    _register(ArsenalMeta(
        callable_ref="techne.lib.functional_eq_check:functional_eq_check",
        cost={"max_seconds": 0.05, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'residual', 'pass' fields",
            "passes for known modular elliptic curves to threshold 1e-8",
            "37a1, 11a1: pass == True",
        ],
        authority_refs=["Wiles 1995 / Breuil-Conrad-Diamond-Taylor 2001 (modularity)", "Tunnell 'Functional equation' tests"],
        equivalence_class="variety_fingerprint",
        category="elliptic_curves",
        notes="Numerical functional-equation check on L(E, s).",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# research — Lehmer / bootstrap / anomaly_surface (frontier scaffolding).
# ---------------------------------------------------------------------------

try:
    from .research import lehmer  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.research.lehmer:identify_salem_class",
        cost={"max_seconds": 3.9e-05, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(log n)', "coefficient_us": 0.5208, "fit_r2": 0.984, "p95_seconds": 3e-06, "median_at_smallest_us": 0.8, "median_at_largest_us": 1.3, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "True iff polynomial is reciprocal with all roots on unit circle except one real > 1",
            "False for cyclotomic (all roots on circle)",
            "False for non-reciprocal",
        ],
        authority_refs=["Salem 1945 'Algebraic numbers and Fourier analysis'", "Smyth 'The Mahler measure of algebraic numbers: a survey'"],
        equivalence_class="variety_fingerprint",
        category="research_lehmer",
        notes="Test: is polynomial in Salem class (Pisot dual)?",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.research.lehmer:is_reciprocal",
        cost={"max_seconds": 3e-05, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(log n)', "coefficient_us": 0.2794, "fit_r2": 0.985, "p95_seconds": 2e-06, "median_at_smallest_us": 0.5, "median_at_largest_us": 1.0, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "True iff polynomial is palindromic (or anti-palindromic)",
            "True for cyclotomic, Lehmer's, all Salem classes",
        ],
        authority_refs=["Smyth 'The Mahler measure of algebraic numbers: a survey'"],
        equivalence_class="variety_fingerprint",
        category="research_lehmer",
        notes="Test polynomial reciprocity (palindromic coefficients).",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.research.lehmer:degree_profile",
        cost={"max_seconds": 5e-05, "max_memory_mb": 16, "max_oracle_calls": 0, "calibrated_cost": {"complexity": 'O(log n)', "coefficient_us": 0.2794, "fit_r2": 0.985, "p95_seconds": 2e-06, "median_at_smallest_us": 0.5, "median_at_largest_us": 1.0, "calibrated_2026_05_04": True, "host": "Skullport / Win11 / Py3.11.9 / Ryzen 7 5700X3D"}},
        postconditions=[
            "returns list of dicts keyed by degree",
            "each dict has 'count', 'min_M', 'examples'",
        ],
        authority_refs=["Mossinghoff Mahler tables (degree profiles)"],
        equivalence_class="variety_fingerprint",
        category="research_lehmer",
        notes="Degree-stratified profile of a Mahler-measure scan.",
    ))
except ImportError:
    pass

try:
    from .research import bootstrap  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.research.bootstrap:bootstrap_ci",
        cost={"max_seconds": 0.05, "max_memory_mb": 32, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'point', 'low', 'high', 'alpha'",
            "low <= point <= high",
            "alpha in (0, 1)",
            "n_resamples >= 100 for stable CI",
        ],
        authority_refs=["Efron 1979 'Bootstrap methods'", "Efron-Tibshirani 'An Introduction to the Bootstrap'"],
        equivalence_class="variety_fingerprint",
        category="research",
        notes="Percentile-bootstrap confidence interval.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.research.bootstrap:matched_null_test",
        cost={"max_seconds": 0.5, "max_memory_mb": 64, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'p_value', 'null_mean', 'null_std'",
            "p_value in [0, 1]",
            "two-tailed: clipped to [1/(n+1), 1]",
        ],
        authority_refs=["Efron-Tibshirani §16", "matched_null_test docstring (this lib)"],
        equivalence_class="variety_fingerprint",
        category="research",
        notes="Matched-null permutation test against user-supplied null sampler.",
    ))
except ImportError:
    pass

try:
    from .research import anomaly_surface  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.research.anomaly_surface:surface_anomalies",
        cost={"max_seconds": 5.0, "max_memory_mb": 256, "max_oracle_calls": 1},
        postconditions=[
            "returns dict with anomaly metrics per ensemble",
            "ensembles in {'GUE', 'GOE', 'GSE', 'Poisson'}",
            "ks_p_value in [0, 1]",
        ],
        authority_refs=["Mehta 'Random Matrices'", "Bohigas-Giannoni-Schmit 1984 conjecture"],
        equivalence_class="variety_fingerprint",
        category="research",
        notes="Spectral-ratio anomaly surface vs RMT canonical ensembles.",
    ))
except ImportError:
    pass


# ---------------------------------------------------------------------------
# optimization — QP / SOCP / SDP (CVXPY-backed).
# ---------------------------------------------------------------------------

try:
    from . import optimization_qp  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.optimization_qp:solve_qp",
        cost={"max_seconds": 0.1, "max_memory_mb": 128, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'x', 'value', 'status', 'solver'",
            "status in {'optimal', 'infeasible', 'unbounded', ...}",
            "P must be PSD (otherwise QP is non-convex)",
            "primal value matches dual value at optimum",
        ],
        authority_refs=["Boyd & Vandenberghe 'Convex Optimization' §4.4", "Nocedal & Wright 'Numerical Optimization' §16"],
        equivalence_class="variety_fingerprint",
        category="optimization",
        notes="Convex QP min 0.5 x'Px + q'x s.t. Gx<=h, A_eq x=b_eq.",
    ))
except ImportError:
    pass

try:
    from . import optimization_socp  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.optimization_socp:solve_socp",
        cost={"max_seconds": 0.5, "max_memory_mb": 128, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'x', 'optimal_value', 'status', 'solver_used'",
            "status in {'optimal', 'infeasible', 'unbounded'}",
            "respects ||A_i x + b_i||_2 <= c_i'x + d_i for each cone",
        ],
        authority_refs=["Lobo, Vandenberghe, Boyd, Lebret 1998 'Applications of Second-Order Cone Programming'"],
        equivalence_class="variety_fingerprint",
        category="optimization",
        notes="Second-Order Cone Program via CVXPY.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.optimization_socp:chebyshev_center",
        cost={"max_seconds": 0.05, "max_memory_mb": 64, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'center', 'radius'",
            "radius >= 0",
            "center is in interior of polytope when radius > 0",
            "ball B(center, radius) is inscribed in {x: A x <= b}",
        ],
        authority_refs=["Boyd & Vandenberghe 'Convex Optimization' §8.5"],
        equivalence_class="variety_fingerprint",
        category="optimization",
        notes="Chebyshev center of polytope (largest inscribed ball).",
    ))
except ImportError:
    pass

try:
    from . import optimization_sdp  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.optimization_sdp:solve_sdp",
        cost={"max_seconds": 1.0, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'X', 'value', 'status', 'solver_used'",
            "status in {'optimal', 'infeasible', 'unbounded'}",
            "X is PSD at optimum",
        ],
        authority_refs=["Vandenberghe & Boyd 1996 'Semidefinite Programming'"],
        equivalence_class="variety_fingerprint",
        category="optimization",
        notes="Semidefinite Program via CVXPY/SCS.",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.optimization_sdp:lovasz_theta",
        cost={"max_seconds": 0.5, "max_memory_mb": 128, "max_oracle_calls": 0},
        postconditions=[
            "alpha(G) <= theta(G) <= chi(G_complement) (sandwich)",
            "theta(C_5) ≈ sqrt(5) ≈ 2.236",
            "theta(K_n) == 1",
        ],
        authority_refs=["Lovasz 1979 'On the Shannon Capacity of a Graph'", "Knuth 1994 'The Sandwich Theorem'"],
        equivalence_class="variety_fingerprint",
        category="optimization",
        notes="Lovasz theta number of a graph (SDP relaxation of independence number).",
    ))
    _register(ArsenalMeta(
        callable_ref="prometheus_math.optimization_sdp:sdp_relaxation_max_cut",
        cost={"max_seconds": 1.0, "max_memory_mb": 256, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'X', 'sdp_value', 'cut_value', 'partition'",
            "cut_value <= sdp_value (relaxation)",
            "Goemans-Williamson: cut >= 0.878 * sdp_value (random hyperplane)",
        ],
        authority_refs=["Goemans-Williamson 1995 'Improved approximation algorithms for maximum cut'"],
        equivalence_class="variety_fingerprint",
        category="optimization",
        notes="Goemans-Williamson SDP relaxation of MAX-CUT.",
    ))
except ImportError:
    pass

try:
    from . import optimization  # noqa: F401

    _register(ArsenalMeta(
        callable_ref="prometheus_math.optimization:solve_lp",
        cost={"max_seconds": 0.05, "max_memory_mb": 64, "max_oracle_calls": 0},
        postconditions=[
            "returns dict with 'status', 'fun', 'x', 'success'",
            "status == 0 iff success at optimal",
            "solution satisfies A_ub x <= b_ub, A_eq x == b_eq",
        ],
        authority_refs=["Dantzig 1947 'Linear Programming'", "scipy.optimize.linprog (HiGHS)"],
        equivalence_class="variety_fingerprint",
        category="optimization",
        notes="Linear program via HiGHS/scipy/PuLP.",
    ))
except ImportError:
    pass
