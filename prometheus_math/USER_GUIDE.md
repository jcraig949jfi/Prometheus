# prometheus_math — User Guide

**Researcher-facing introduction to the unified Prometheus mathematical-software API.**

Last updated: 2026-04-25 · Status: 31/38 backends available

---

## Welcome

`prometheus_math` (imported as `pm`) is a single Python entry point that
unifies a large, heterogeneous arsenal of mathematical software:
PARI/GP, FLINT, SnapPy, mpmath, GMP/MPFR, SymPy, Z3, SCIP, OR-Tools,
HiGHS, NetworkX, gudhi, Ripser, the Mossinghoff Mahler tables, the
ATLAS of Finite Groups, and live mirrors of LMFDB, OEIS, KnotInfo,
arXiv, and zbMATH. One import; one capability matrix; one place to
look up "how do I ask the *fastest available* tool for this answer?".

Three audiences:

- **Researchers** — you want `pm.elliptic_curves.analytic_sha(ainvs)`
  to just work, returning a number that can be cited or fed to the
  next step. You should rarely need to know which backend ran.
- **AI agents (Charon, Aporia, Ergon, Harmonia, Cartography, Techne)**
  — you want a stable, named API; deterministic return shapes;
  per-call backend overrides; and a registry to query before you
  attempt something an offline machine cannot do.
- **Contributors** — you want to add a new tool. The arsenal layout
  (categorical module + thin backend adapter + math-tdd test file)
  is documented in `prometheus_math/ARSENAL.md` and
  `techne/ARSENAL_ROADMAP.md`.

This guide is **Phase 1** of the documentation project. Phase 2 (the
recipe gallery: BSD audit, Galois census, knot-NF match, OEIS
conjecture check, and 6 more) is deferred and will land at
`prometheus_math/recipes/`.

---

## Installation

`prometheus_math` is part of the Prometheus monorepo. There is no
separate `pip install prometheus-math` package; you check out the
repo and add it to your `PYTHONPATH`, or run from the repo root.

### Pure-Python dependencies

Most of the arsenal is pure-Python. Install everything in one go:

```bash
pip install -r requirements.txt
```

(or, minimally for the core that this guide exercises:
`pip install numpy scipy sympy mpmath cypari python-flint snappy
networkx z3-solver pyscipopt highspy pulp ortools requests psycopg2`)

### Native binaries (optional, large)

Native math binaries unlock specific categories of operations and
must be installed separately:

| Backend | Use | Install hint |
|---|---|---|
| Singular | algebraic geometry — Groebner, primary decomposition | bundled with SageMath, or MSYS2 `pacman -S singular` |
| GAP | finite groups, character tables | `scripts/install_gap.md` |
| Macaulay2 | free resolutions, sheaf cohomology | upstream installer (~200 MB) |
| Lean 4 | proof assistant integration | `elan` |
| Julia | OSCAR / Hecke / Nemo gateway | upstream installer |

Until installed, the matching API surfaces (e.g.
`pm.algebraic_geometry.groebner_basis`) raise `ValueError` with the
install hint. The categorical module always imports successfully —
it's the *call* that gates on the binary.

### Local-mirror data (optional)

Several wrappers (OEIS, KnotInfo, Cremona) can run from a local data
directory, which both speeds up large scans and makes the pipeline
robust to Cloudflare / rate-limit failures. Set the environment
variable once:

```bash
# Linux / macOS
export PROMETHEUS_DATA_DIR=/path/to/big/disk/prometheus_data

# Windows (PowerShell)
$env:PROMETHEUS_DATA_DIR = "Z:\prometheus_data"
```

If unset, mirrors live under `<repo_root>/prometheus_data/` (created
on first use) or, as a final fallback, `~/.prometheus_data/`.

See [The local-mirror pattern](#the-local-mirror-pattern) below.

---

## First import + smoke test

```python
import prometheus_math as pm

print(pm.registry.summary())
# 31/38 backends available across 9 categories: AI, CAS, COMB, DB, NT, NUM, OPT, SAT, TOP
```

If this line prints a non-empty summary, you're ready. If it raises,
the most common culprits are:

- Missing pip dependency — read the traceback, `pip install` the package.
- PARI initialization failure — confirm `cypari` installed correctly
  (`python -c "import cypari; print(cypari.pari('2+2'))"`).
- Network probe timeout — `pm.registry` probes services on import;
  unreachable services are simply marked unavailable, never fatal.

The number of available backends is environment-dependent. The
**31/38** above is what a reasonably-equipped Windows research box
sees with the open-source stack installed; a fresh `pip install`
without optional native installs will see something like 25/38.

---

## Capability check

Three functions cover everything you need to know about what's
installed:

```python
import prometheus_math as pm

# Is a specific backend available?
pm.registry.is_available("snappy")      # True
pm.registry.is_available("singular")    # False on most boxes

# Full matrix, dict-of-dicts, sortable / filterable
matrix = pm.registry.installed()
sorted(name for name, info in matrix.items() if info["available"])
# ['arxiv', 'atlas', 'chipfiring', 'cremona', 'cvxpy', 'cypari', ...]

# One-line summary, suitable for logs / agent boot banners
pm.registry.summary()
# '31/38 backends available across 9 categories: AI, CAS, COMB, DB, NT, NUM, OPT, SAT, TOP'
```

The matrix entries have the shape:

```python
{
    "available": True,
    "version": "3.3.2",
    "kind": "python",          # 'python' | 'binary' | 'service' | 'data'
    "category": "TOP",
    "description": "3-manifolds, hyperbolic geometry",
    "error": None,
}
```

When `available=False`, `error` carries a one-line explanation
("not installed", "binary not on PATH", "service unreachable", ...).

---

## Per-category quickstart

Every category is a top-level submodule of `pm`. Pick the one that
matches your object of interest.

### `pm.number_theory` — number fields, polynomials, Mahler

```python
import prometheus_math as pm

# Class number of Q(sqrt(-5))
pm.number_theory.class_number("x^2+5")
# 2

# Galois group of x^4 - 2 over Q (the dihedral group D_4)
pm.number_theory.galois_group("x^4 - 2")
# {'name': 'D(4)', 'order': 8, 'transitive_id': (4, 3),
#  'parity': -1, 'is_abelian': False, 'degree': 4}

# Mahler measure of Lehmer's polynomial (small-Mahler witness)
pm.number_theory.mahler_measure(
    [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
)
# 1.1762808182599176
```

For Hilbert class fields and CM data:

```python
# H_K for K = Q(sqrt(-5)); H_K = K(i) absolutely
pm.number_fields.hilbert_class_field("x^2+5")
# {'abs_poly': 'x^4 + 3*x^2 + 1', 'rel_poly': 'x^2 + 1',
#  'degree_rel': 2, 'degree_abs': 4, 'disc': 400,
#  'class_number_K': 2, 'is_trivial': False}
```

### `pm.elliptic_curves` — E/Q

The full BSD chain on `11.a3` (the prototypical rank-0 curve with
`a-invariants = [0, -1, 1, 0, 0]`):

```python
import prometheus_math as pm

ainvs = [0, -1, 1, 0, 0]                       # 11.a3
pm.elliptic_curves.conductor(ainvs)            # 11
pm.elliptic_curves.bad_primes(ainvs)           # [11]
pm.elliptic_curves.root_number(ainvs)          # 1
pm.elliptic_curves.analytic_sha(ainvs)
# {'value': 1.0..., 'rounded': 1, 'rank': 0,
#  'L_r_over_fact': 0.2538..., 'Omega': 1.2692...,
#  'Reg': 1.0, 'tam': 5, 'tors': 5, 'disc_sign': -1}
```

For higher-rank curves, `analytic_sha` returns `'rank': r` and the
formula is BSD assuming the L-function order matches.

### `pm.number_fields` — NF-as-object

Splits naturally from `pm.number_theory`; same operations
(`class_number`, `class_group`, `regulator_nf`,
`hilbert_class_field`, `class_field_tower`, `cm_order_data`) but
imported as a focused namespace when you're doing pure NF research:

```python
import prometheus_math as pm

# CM order with discriminant -7 has class number 1; ring class
# polynomial has integer root j(tau) = -3375.
pm.number_fields.cm_order_data(-7)
# {'fundamental_disc': -7, 'cm_conductor': 1, 'class_number': 1,
#  'is_maximal': True, 'ring_class_polynomial': 'x + 3375', ...}
```

### `pm.topology` — knots, 3-manifolds, TDA

```python
import prometheus_math as pm

# Hyperbolic volume of the figure-eight knot 4_1
pm.topology.hyperbolic_volume("4_1")
# 2.029883212819307

# Same number to 20 digits (string)
pm.topology.hyperbolic_volume_hp("4_1", digits=20)
# '2.02988321281930725004'

# Alexander polynomial of 4_1: -1 + 3t - t^2 (signed convention)
pm.topology.alexander_polynomial("4_1")["coeffs"]
# [-1, 3, -1]

# Shape field of 5_2 — degree-3 NF with discriminant -23
pm.topology.knot_shape_field("5_2")["disc"]
# -23
```

### `pm.combinatorics` — graphs, divisors, integer matrices

```python
import prometheus_math as pm
import numpy as np

# Smith normal form of an integer matrix
M = np.array([[2, 4, 4],
              [-6, 6, 12],
              [10, -4, -16]])
pm.combinatorics.smith_normal_form(M).tolist()
# [[2, 0, 0], [0, 6, 0], [0, 0, 12]]

pm.combinatorics.invariant_factors(M)
# [2, 6, 12]

# Tropical (Baker-Norine) rank on a 4-cycle with chip distribution
# (2, 0, 0, 0)
A = np.array([[0, 1, 0, 1],
              [1, 0, 1, 0],
              [0, 1, 0, 1],
              [1, 0, 1, 0]])
pm.combinatorics.tropical_rank(A, [2, 0, 0, 0])
# 1
```

### `pm.algebraic_geometry` — Singular-gated

This module is gated on a Singular install. Always check first:

```python
import prometheus_math as pm

if pm.algebraic_geometry.installed():
    # Groebner basis of <x^2 - y, x*y - 1> in Q[x, y], lex order
    G = pm.algebraic_geometry.groebner_basis(
        ["x^2 - y", "x*y - 1"], variables=["x", "y"], order="lp"
    )
    print(G)
else:
    print("Singular not installed — use pm.symbolic.groebner_basis "
          "(SymPy fallback) for small examples.")
```

The SymPy fallback handles small inputs; Singular handles real ones.
See [Backend dispatch](#backend-dispatch) below for when each is
appropriate.

### `pm.optimization` — LP, MIP, SAT, SMT, convex

```python
import prometheus_math as pm

# Linear program: minimize -x - y s.t. x + y <= 4, x,y >= 0
out = pm.optimization.solve_lp(
    c=[-1, -1],
    A_ub=[[1, 1]], b_ub=[4],
    bounds=[(0, None), (0, None)],
)
out["fun"]              # -4.0
out["backend_used"]     # 'highspy' (or 'scipy' on a thin install)

# Mixed-integer: same problem, integer x, y
out = pm.optimization.solve_mip(
    c=[-1, -1],
    A_ub=[[1, 1]], b_ub=[4],
    integrality=[1, 1],
    bounds=[(0, None), (0, None)],
)
out["fun"], out["x"]    # -4.0, [4.0, 0.0] (or [0.0, 4.0])

# SAT: clauses (1 v 2), (~1 v 2), (1 v ~2) — both true is satisfying
pm.optimization.solve_sat([[1, 2], [-1, 2], [1, -2]])
# {'sat': True, 'model': [1, 2], 'backend_used': 'pysat'}
```

CP-SAT, SMT, and convex problems use `solve_cp`, `solve_smt`, and
`solve_convex` with a `model_fn(model)` builder pattern (see
`prometheus_math/optimization.py` docstrings).

### `pm.numerics` — arbitrary-precision, special functions

```python
import prometheus_math as pm

# Riemann zeta at the first non-trivial zero — should be ~0
z = pm.numerics.zeta(0.5 + 14.134725j, prec=80)
abs(z) < 1e-6           # True

# Bernoulli number as exact Fraction
pm.numerics.bernoulli(12)
# Fraction(-691, 2730)

# Integer relation finder (PSLQ)
import mpmath as mp
mp.mp.dps = 40
pm.numerics.pslq([mp.pi**2, mp.mpf(6) * mp.zeta(2)])
# [1, -1]   # records that pi^2 == 6 * zeta(2)
```

`set_precision(bits)` sets the global mpmath precision. For
heavy-precision work, use `mpmath.workprec(n)` as a context manager.

### `pm.symbolic` — CAS basics

```python
import prometheus_math as pm
from sympy import symbols
x = symbols("x")

pm.symbolic.factor("x^3 - 1")
# (x - 1)*(x**2 + x + 1)

pm.symbolic.integrate("sin(x)*x", x)
# -x*cos(x) + sin(x)

# Groebner basis (SymPy fallback for small examples)
y = symbols("y")
pm.symbolic.groebner_basis(["x^2 - y", "x*y - 1"], [x, y])
# [x - y**2, y**3 - 1]
```

### `pm.databases` — LMFDB, OEIS, KnotInfo, arXiv, zbMATH, Mahler, ATLAS

The database wrappers are categorically separate because they hit
the network (or an embedded snapshot) rather than computing locally.

```python
import prometheus_math as pm

# OEIS — Fibonacci by A-number (uses the local mirror first)
fib = pm.databases.oeis.lookup("A000045")
fib["data"][:8]
# [0, 1, 1, 2, 3, 5, 8, 13]

# LMFDB — elliptic curve by label
rows = pm.databases.lmfdb.elliptic_curves(label="11.a3")
rows[0]["ainvs"], rows[0]["conductor"]
# ([0, -1, 1, 0, 0], 11)

# KnotInfo — knot invariants
info = pm.databases.knotinfo.lookup("4_1")
info["determinant"], info["fibered"]
# (5, True)

# Mossinghoff small-Mahler tables — embedded, always available
pm.databases.mahler.lehmer_witness()["mahler_measure"]
# 1.1762808182599176

# ATLAS of Finite Groups — embedded snapshot, M11 has order 7920
pm.databases.atlas.lookup("M11")["order"]
# 7920
```

Each wrapper is independently available — you can `import
prometheus_math.databases.oeis` without touching LMFDB.

### `pm.research` — Prometheus research-thread primitives

These are reusable primitives extracted from active research threads
(Aporia, Charon, Ergon, Harmonia). They have a stable API and a
TDD test suite, but their interface is more ambitious than the
categorical modules — they often orchestrate many tools at once.

```python
import prometheus_math as pm

# BSD audit on one curve, with LMFDB cross-check
results = pm.research.bsd_audit.run(
    ["11.a3"],
    lmfdb_compare=True,
    timeout_s=60.0,
)
results[0]["all_consistent"]    # True
results[0]["rank"]               # 0
```

Other research entry points:

- `pm.research.spectral_gaps.scan(...)` — L-function spectral-gap-k
  vs random-matrix-ensemble null (used by Aporia's F011 work).
- `pm.research.vcm_scaling.regress_log_abs_d(...)` — V-CM-scaling
  stratifier per discriminant.
- `pm.research.identity_join.knot_to_nf(...)` — knot-NF identity
  matching against LMFDB.

---

## The local-mirror pattern

Several databases ship with (or grow on first contact) a local
mirror so research pipelines aren't held hostage by Cloudflare,
upstream rate limits, or transient network outages. The pattern is
shared across wrappers and worth understanding once.

### `PROMETHEUS_DATA_DIR`

The single environment variable that controls where mirrors live:

```bash
export PROMETHEUS_DATA_DIR=/path/to/big/disk/prometheus_data
```

Resolution order, when the variable is unset:

1. `$PROMETHEUS_DATA_DIR`
2. `<repo_root>/prometheus_data/` (if it already exists)
3. `~/.prometheus_data/`

The chosen directory is created if absent. Inspect at runtime:

```python
from prometheus_math.databases import _local
str(_local.data_dir())
# '/path/to/big/disk/prometheus_data'
```

### Per-database behavior

| Database | Mirror behavior |
|---|---|
| **OEIS** | `stripped` + `names` files, gzipped, ~50 MB. Auto-loaded if present. `oeis.update_mirror()` refreshes. Resolved Cloudflare blocks via stdlib `urllib` with a desktop-Chrome UA. |
| **KnotInfo** | Available via the `database_knotinfo` pip package (offline) or live CSV download (online). Whichever is installed lights up first. |
| **Cremona ecdata** | Opt-in 88 MB mirror under `<DATA_DIR>/cremona/`. Used as an LMFDB fallback when the Postgres mirror is unreachable. |
| **Mossinghoff** | Embedded snapshot in the package — *always* available, no download needed. |
| **ATLAS** | Embedded snapshot in the package — *always* available; auto-upgrades to GAP when GAP is installed. |
| **LMFDB** | No local mirror; uses the public Postgres mirror at `devmirror.lmfdb.xyz`. Use Cremona for the EC subset offline. |
| **arXiv / zbMATH** | No local mirror; live API only (rate-limited to <= 1 req/s). |

### Forcing local-first

For OEIS specifically:

```python
import prometheus_math as pm
pm.databases.oeis.has_local_mirror()       # True if mirrored
pm.databases.oeis.use_local_first(True)    # prefer local even if online
```

This is essential during long batch scans where the Cloudflare
challenge would interrupt every few hundred queries.

---

## Backend dispatch

For categories where multiple backends solve the same problem,
`prometheus_math` picks automatically based on what's installed and
what's known to be fast. The rule of thumb: **don't override unless
you have a reason**.

### When to override

The `backend=` keyword is supported on every dispatching function in
`pm.optimization`, `pm.symbolic.groebner_basis`, and (where multiple
NF backends exist) parts of `pm.number_theory`. Override when:

1. **You're benchmarking**. Force `backend="scipy"` and
   `backend="highspy"` separately to compare.
2. **You hit a backend-specific bug**. SCIP and HiGHS occasionally
   disagree on degenerate LPs; pin one until upstream lands a fix.
3. **You need a feature only one backend exposes**. Z3 has unique
   tactics; OR-Tools CP-SAT scales differently from PySAT on
   certain SAT instances.
4. **Reproducibility**. Pin the backend in published research code
   so a reader on a different install gets the same numbers.

### Example: forcing the LP solver

```python
import prometheus_math as pm

problem = dict(
    c=[-1, -1],
    A_ub=[[1, 1]], b_ub=[4],
    bounds=[(0, None), (0, None)],
)

# Default — auto-selected (highspy on a full install)
pm.optimization.solve_lp(**problem)["backend_used"]
# 'highspy'

# Forced
pm.optimization.solve_lp(**problem, backend="scipy")["backend_used"]
# 'scipy'

pm.optimization.solve_lp(**problem, backend="pulp")["backend_used"]
# 'pulp'
```

### What's available right now

```python
import prometheus_math as pm
pm.optimization.installed_solvers()
# {'LP':  ['highspy', 'scipy', 'pulp'],
#  'MIP': ['pyscipopt', 'ortools', 'highspy', 'pulp'],
#  'CP':  ['ortools'],
#  'SAT': ['pysat'],
#  'SMT': ['z3'],
#  'CONVEX': ['cvxpy']}
```

---

## Failure modes and how to read errors

The arsenal is opinionated about errors:

- **`ValueError` with an install hint** — a backend isn't installed.
  Most common for `pm.algebraic_geometry.*` (Singular) and
  `pm.groups.*` (GAP). The error message says exactly what to install.

- **`LMFDBConnectionError`** — the Postgres mirror is unreachable.
  Either your network blocks port 5432 outbound, the mirror is down
  (rare but happens), or your `connect_timeout` was too aggressive.
  Switch to `pm.databases.cremona` for the EC subset, or retry.

- **Returns `None` / `[]`** — for service wrappers like OEIS and
  arXiv, a network failure is a **non-fatal** condition: the
  function returns an empty result rather than raising. This is
  deliberate; pipelines shouldn't crash because Cloudflare hiccupped.
  Always check for `None` before indexing.

- **`<tool>_runtime_exceeded` in `warnings`** — `pm.research.*`
  audit functions enforce per-call timeouts (default 30 s). When a
  single tool blows past the cap, the field stays `None` and a
  warning string is appended; the rest of the audit continues.

- **`'all_consistent': False`** in BSD audit — *not* an error. It
  means at least one quantity disagreed beyond tolerance with LMFDB
  (or that LMFDB compare was skipped, in which case nothing to
  compare against). Inspect `delta_*` fields for the specifics.

When in doubt: `pm.registry.installed()[backend_name]["error"]`
carries the registration-time error. If a call is failing and the
registry says the backend is available, the error is in the call
itself, not the install.

---

## The math-tdd quality bar

Every operation in `prometheus_math` should be backed by a test file
scoring at least **A:1 P:2 E:2 C:1** on the math-tdd rubric:

- **A**uthority — published table or independently-implemented oracle
- **P**roperty — algebraic invariants (functorial / dimensional / sign)
- **E**dge — unit, zero, identity, degenerate inputs
- **C**omposition — at least one test where multiple operations chain

The full rubric, including how to backfill an existing untested
operation, lives at `.claude/skills/math-tdd/SKILL.md`. The audit
log of who scored what is `techne/TDD_LOG.md`.

If you contribute a new operation without an accompanying test file
that meets this bar, the math-tdd skill **will block the commit** in
review.

---

## Where to find more

- `prometheus_math/ARSENAL.md` — auto-generated, single-page API
  reference. Backend matrix, all operations, dependency graph.
  Re-run `pm.doc.arsenal()` to refresh after adding ops.
- `techne/ARSENAL_ROADMAP.md` — long-term tracker of tools we want
  to wrap but haven't yet.
- `techne/PROJECT_BACKLOG_1000.md` — full ranked work queue.
- `.claude/skills/math-tdd/SKILL.md` — the testing rubric.
- `prometheus_math/tests/` — categorical-module tests (see these
  for canonical usage patterns of every function).
- `prometheus_math/research/` — research-thread primitives and
  their test suites.

---

## Filing a tool request

Found a hole? Need an operation we don't expose? File a request in
the Techne queue:

```bash
echo '{"requested_at": "2026-04-25", "kind": "operation",
       "name": "pm.number_theory.iwasawa_invariants",
       "category": "C", "rationale": "Aporia F037 needs lambda/mu",
       "agent": "your-agent-name"}' >> techne/queue/requests.jsonl
```

Techne picks requests off this queue, slots them into the 1000-project
backlog with an effort estimate, and either forges them itself or
(for heavy native installs) escalates to a human operator.

---

*This guide is a single-file companion to `ARSENAL.md`. Keep it
short and runnable: every code block here is verified by
`prometheus_math/tests/test_user_guide_examples.py`.*
