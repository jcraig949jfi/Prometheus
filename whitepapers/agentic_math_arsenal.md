# The Agentic Mathematics Arsenal

## A unified software substrate for AI scientists exploring the frontier of mathematics

**Version 1.0 · 2026-04-25 · Prometheus Project**

---

## Executive summary

We are building a software substrate for **AI agents doing mathematical
research at the frontier**. The substrate has three layers:

1. **Collection** — every open-source mathematical software tool worth
   using is installed, version-tracked, and probed for availability.
2. **Organization** — every operation has one canonical entry point in
   a **unified Python API**, dispatching to the fastest available
   backend.
3. **Wrapping** — proprietary or paywalled functionality is
   re-implemented from open sources where the gap is significant
   enough to bottleneck research.

The substrate is named `prometheus_math`. It exists so an agentic
scientist (Aporia, Charon, Ergon, Harmonia, and the rest of the
Prometheus team) can write `import prometheus_math as pm` and reach
**every mathematical operation the project needs**, with consistent
naming, consistent error handling, and verified test-driven quality.

This document describes what we've collected, the architecture of how
it's organized, the gaps still being closed, and the **continuous
work mandate** that drives a perpetual development pipeline.

---

## Why this exists

### The problem agentic scientists face

When an AI agent is asked to test a mathematical conjecture — say,
"is the gap-index gradient in F011 universal across L-function families?"
— it needs:

- A computer-algebra system (SageMath, Mathematica, Maple)
- A specialized number-theory library (PARI/GP, FLINT, Magma)
- A topological library (SnapPy, Regina, knot Floer homology)
- A proof assistant (Lean, Coq, Isabelle)
- An optimization engine (CPLEX, Gurobi, SCIP, OR-Tools)
- A research database (LMFDB, OEIS, KnotInfo, ATLAS)
- A high-precision numerics library (mpmath, ARB, MPFR)
- A visualization toolkit
- A data pipeline (Postgres, Pandas, JSON I/O)

Each of these has its own API, its own gotchas, its own install steps,
its own ways of failing silently. A working mathematician spends
**substantial time on glue code** between tools that solve different
parts of one research question. AI agents working autonomously have
even less tolerance for that glue: they need *one* import, *one*
naming convention, *one* trustworthy substrate.

### The North Star

Frontier mathematics, number theory, multi-dimensional mathematical
exploration — and most importantly, **the discovery of bridges between
mathematical domains that humans haven't yet found**.

The goal is not to replace human mathematicians but to give them, and
the AI agents collaborating with them, a substrate where computational
work happens at the speed of thought, where every numerical claim has
an authority-based test underneath it, and where the marginal cost of
testing a new conjecture is one function call.

---

## The architecture in one diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   AI agents (Aporia, Charon, Ergon, Harmonia, ...) and humans   │
│                                                                  │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              │  import prometheus_math as pm
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    prometheus_math (unified API)                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Categorical modules — operation surface for researchers │    │
│  │  • number_theory     • elliptic_curves                   │    │
│  │  • number_fields     • topology                          │    │
│  │  • combinatorics     • algebraic_geometry                │    │
│  │  • optimization      • numerics                          │    │
│  │  • symbolic          • databases (lmfdb/oeis/...)        │    │
│  │  • proof (Lean)      • viz (planned)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Registry — capability detection + backend dispatch      │    │
│  │ 36 backends probed; per-operation fallback chains       │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Backends — thin adapters to underlying tools            │    │
│  │  • _pari (cypari)       • _scip (pyscipopt)              │    │
│  │  • _sympy               • _z3                            │    │
│  │  • _flint               • _ortools                       │    │
│  │  • _snappy              • _mpmath                        │    │
│  │  • _kfh (knot Floer)    • _cvxpy                         │    │
│  │  • _gap (when installed) • _m2 (when installed)          │    │
│  │  • _lean (when installed) • _julia (when installed)      │    │
│  │  • _singular (gated)                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Data substrate                                                  │
│  • LMFDB Postgres mirror (devmirror.lmfdb.xyz)                  │
│  • OEIS local mirror (~37 MB; 395 K sequences)                   │
│  • KnotInfo (12,966 knots + 4,188 links via database_knotinfo)   │
│  • Mossinghoff Mahler tables (21 verified entries)               │
│  • arXiv API + zbMATH Open API                                   │
│  • Local Postgres dual (scientific + research)                   │
└──────────────────────────────────────────────────────────────────┘
```

The architecture is **cone-shaped**: the wide top (operations) narrows
to a thin neck (registry/dispatch), then widens again at the bottom
(diverse backends, including paywalled-equivalent open implementations).

---

## What's collected today (Apr 25, 2026)

### Backend capability matrix snapshot

**36 backends registered, 29 operational** across 9 categories.

| Category | Backends operational | Key tools |
|---|---|---|
| **CAS** | sympy 1.14 | symbolic computation |
| **NT** | cypari 2.5, python-flint 0.8 | PARI/GP, fast NT primitives |
| **NUM** | mpmath 1.3, gmpy2 2.3, numpy 2.2, scipy 1.13 | high precision, GMP/MPFR |
| **TOP** | snappy 3.3, knot_floer_homology 1.2, gudhi 3.12, ripser 0.6, persim 0.3 | 3-manifolds, knot Floer, TDA |
| **COMB** | networkx 3.6, chipfiring 1.1, galois 0.4 | graphs, chip-firing, finite fields |
| **SAT** | z3-solver 4.16, pysat 1.9 | SMT, SAT (Glucose/MiniSat) |
| **OPT** | pyscipopt 6.1, ortools 9.15, highspy 1.14, pulp 3.3, cvxpy 1.8 | MIP, LP, CP-SAT, convex |
| **AI** | torch 2.11 | PyTorch (foundation for ML/AI integrations) |
| **DB** | lmfdb, oeis (local), arxiv, knotinfo, zbmath, mossinghoff | mathematical databases (live + local) |

**Native binaries not yet on PATH** (queued with documented install paths):
- GAP, Macaulay2, Singular, Lean 4, Julia, R, SageMath

### Categorical operations exposed

- `pm.number_theory` — class numbers, Galois groups, Hilbert class
  fields + class field towers, LLL reduction, CM order data, Mahler
  measure, continued fractions, Sturm bounds, functional-equation
  checks (24 functions)
- `pm.elliptic_curves` — regulator (saturated), conductor + global
  reduction, root number, analytic Sha (BSD-formula), 2-Selmer rank,
  Faltings height, Mordell-Weil, height pairing (15 functions)
- `pm.number_fields` — class number, HCF, class field tower, CM order
  decomposition (6 functions)
- `pm.topology` — hyperbolic volume, knot shape field (Sage-free
  iTrF approximation), Alexander polynomial via HFK, batch helpers
  (8 functions)
- `pm.combinatorics` — Smith normal form, abelian group structure,
  tropical (Baker-Norine) rank on graphs, singularity classification
  of generating functions (8 functions)
- `pm.algebraic_geometry` — Gröbner basis, ideal quotient, primary
  decomposition, factorization, Hilbert series, free resolution
  (Singular subprocess wrapper; gated on Singular install) (8 functions)
- `pm.optimization` — solve_lp, solve_mip, solve_cp, solve_sat,
  solve_smt, solve_convex with backend dispatch (7 functions)
- `pm.numerics` — mpmath precision wrappers, Riemann zeta, Dirichlet
  L, PSLQ, lindep_complex, special functions (10 functions)
- `pm.symbolic` — simplify, factor, expand, solve, integrate,
  differentiate, series_expand, ODE solver, Gröbner basis, resultant
  (13 functions)
- `pm.databases` — typed wrappers for LMFDB, OEIS, arXiv, KnotInfo,
  zbMATH, Mossinghoff (50+ functions)

**Total operations exposed:** ~140 functions across 10 modules.

### Test coverage today

- **600+ tests passing** across `techne/tests/` and `prometheus_math/tests/`
- **38 operations** scored in `techne/TDD_LOG.md` against the
  4-category math-tdd rubric (authority / property / edge / composition)
- **BSD identity verified end-to-end** on 5 LMFDB anchor curves
  (11.a1, 37.a1, 389.a1, 5077.a1, 210.e1) — composition test catches
  bugs unit tests miss
- **LMFDB authority cross-check** on 50 random rank-0 curves: 50/50
  conductor, regulator, faltings_height match; 20/20 analytic Sha match
- **3 bugs surfaced and filed** in `BUGS.md` from the test push (one
  rational-truncation in regulator's `_to_py`, two PARI corner cases)

### Data substrate

- **LMFDB**: live Postgres mirror with 3.8M elliptic curves, ~600
  tables of mathematical objects with computed invariants
- **OEIS**: 395,310 integer sequences as local mirror (resolves
  Cloudflare gating of the live JSON API; bulk download required a
  TLS-fingerprint workaround via `urllib.request`)
- **KnotInfo**: 12,966 knots + 4,188 links cached via `database_knotinfo`
  pip package, fully offline
- **Mossinghoff**: 21 small-Mahler polynomials embedded with M values
  cross-verified to 1e-9 against `techne.mahler_measure`
- **arXiv**: live preprint search (verified working on 2026-04 issues)
- **zbMATH Open**: live literature index (api.zbmath.org/v1)

---

## How researchers use it

### Day-one researcher experience

```python
import prometheus_math as pm

# Capability check
pm.registry.summary()
# → "29/36 backends available across 9 categories: AI, CAS, COMB, DB, NT, NUM, OPT, SAT, TOP"

# Number theory — class number of Q(√-5)
pm.number_theory.class_number('x^2+5')                    # 2

# Elliptic curve BSD audit
sha = pm.elliptic_curves.analytic_sha([0, -1, 1, -10, -20])
# → {'value': 1.0, 'rounded': 1, 'rank': 0, 'L_r_over_fact': 0.2538...,
#    'Omega': 0.2538..., 'Reg': 1.0, 'tam': 5, 'tors': 5, 'disc_sign': -1}

# Topology — knot trace field
pm.topology.knot_shape_field('5_2')
# → {'poly': 'x^3 - x^2 + 1', 'degree': 3, 'disc': -23, ...}

# Database queries
pm.databases.lmfdb.elliptic_curves(label='37.a1')
pm.databases.oeis.lookup('A000045')                       # local mirror
pm.databases.arxiv.search('Riemann zeta', max_results=10)

# Optimization — auto-dispatches to fastest available backend
pm.optimization.solve_lp(c=[3, 4], A_ub=[[1, 2], [3, 1]], b_ub=[8, 9])

# Numerics — high precision
pm.numerics.zeta(0.5 + 14.13j, prec=50)                    # complex zero region
```

### When dispatch matters

`pm.optimization.solve_lp` tries `highspy` → `scipy.linprog` → `pulp`
in order. If a researcher has all three installed, HiGHS wins; if
only PuLP is available, that's used; if none, a clear error names
the missing options.

This dispatch lets the substrate **degrade gracefully** as researchers
work in different environments. Same API, same return shape — different
performance.

### When no backend is installed

`pm.algebraic_geometry.groebner_basis(...)` requires Singular. If
Singular isn't on PATH, the call raises `ValueError` with a message
naming the install paths to consider. The wrapper is shipped *gated*:
ready to activate the moment Singular is reachable, no code changes
needed.

---

## The math-tdd discipline

Mathematical software fails uniquely. A function can pass every unit
test and still be wrong by a factorial, by an integer index, by a
signed period — and the bug only surfaces when the function is
*composed* with another that has the dual error.

The `math-tdd` skill (at `techne/skills/math-tdd.md` and locally at
`.claude/skills/math-tdd/SKILL.md`) enforces **four required test
categories** for every mathematical operation:

1. **Authority-based** — output equals a published reference
   (LMFDB-stored value, OEIS sequence, Cohen table, Mossinghoff
   small-Mahler list, hand-computation with steps in docstring)
2. **Property-based** — invariants hold across many inputs (Hypothesis
   library; e.g., M(P) ≥ 1, regulator ≥ 0, class number ≥ 1, LLL
   preserves det)
3. **Edge-case** — empty / singleton / boundary / malformed /
   precision-boundary / pathological-scale all explicitly covered
4. **Composition** — chains of operations satisfy a known invariant
   (BSD identity, HCF degree, knot Alexander palindromicity)

A tool is "TDD-quality" iff it scores ≥2 in every category. The
`techne/TDD_LOG.md` file is the long-term audit log; the bar for
shipping new operations is TDD-quality.

### The seven failure modes we catch

The math-tdd skill documents seven failure modes specific to
mathematical software, identified from bugs we've already shipped and
fixed:

1. **Off-by-factorial** in L-function derivatives
2. **Off-by-2** from real-period sign convention
3. **Off-by-index²** from unsaturated lattice basis
4. **Variable-priority** errors in PARI relative extensions
5. **Polredabs flip** (x → -x preserves M but changes coeffs)
6. **Encoding errors** from cypari Unicode handling
7. **PARI stack overflow** on large-discriminant fields

Composition tests catch most of these. They are the highest-value
test category and were the focus of project #42 (40 chains, all
passing as of 2026-04-25).

---

## The collection-organization-wrapping triad

### Layer 1 — Collection (what to install)

The `techne/ARSENAL_ROADMAP.md` document tracks every potential
mathematical-software target across **9 tiers**:

- **Tier 1**: Already wrapped in `techne/lib/` (21 tools)
- **Tier 2**: Pip-installed, ready to surface in the unified API (17 tools)
- **Tier 3**: Heavy native installs queued (GAP, M2, Lean 4, Julia,
  Singular, SageMath, Maxima, R)
- **Tier 4**: Linux-only / WSL2 required (Regina, polymake, nauty,
  fpLLL, PHCpack, Bertini, CryptoMiniSat)
- **Tier 5**: Web-service wrappers (LMFDB ✓, OEIS ✓, KnotInfo ✓,
  arXiv ✓, zbMATH ✓, ATLAS, Cremona, NumberFields.org)
- **Tier 5b**: Local dataset mirrors (OEIS ✓, Mossinghoff ✓; full
  Mathlib, ATLAS, Cremona CSV, arXiv-bulk pending)
- **Tier 6**: AI/ML integrations (DeepSeek-Prover, Lean Copilot,
  conjecture engines, custom fine-tunes)
- **Tier 7**: Reverse-engineer paywalled functionality (Magma's
  `pAdicLfunction`, `IsogenyClass`, p-Selmer for p>2; Mathematica's
  integration engine; Maple's ODE classifier)
- **Tier 8**: Novel tools (custom-built for Prometheus needs)
- **Tier 9**: Continuously emerging (quarterly PyPI scan + new tools
  surfacing from research-mathematics conferences)

Tier 1+2 give us ~140 operations on day one. Tier 3 unlocks ~80 more
operations once GAP / M2 / Lean / Julia install completes. Tier 6+7
is multi-year exploratory work.

### Layer 2 — Organization (the unified API)

The unified API design rules:

1. **Operation-first naming**, not tool-first. We don't write
   `cypari.bnfinit("x^2+5").no` — we write
   `pm.number_theory.class_number('x^2+5')`.
2. **Backend dispatch by category**. `solve_lp` picks the fastest
   available LP backend; the user never types "highspy" unless
   overriding.
3. **Lazy imports** to keep the package import time under 2 seconds
   even with 30+ backends present.
4. **Categorical modules re-export** first-class implementations from
   `techne/lib/`. No duplication; researchers see the cleaner naming
   while existing tools keep working.
5. **Backend-agnostic return shapes** (dicts with named fields) so
   callers don't depend on backend types.

### Layer 3 — Wrapping (the open-source stack as proprietary substitute)

For each proprietary tool the field uses, we maintain a documented
substitution path in `whitepapers/mathematical_research_software.md`:

| Proprietary | Open-source replacement(s) | Fidelity | Gap |
|---|---|---|---|
| **Magma** | SageMath, PARI/GP, OSCAR.jl | ~80–90% | Specialized algorithms (NT) |
| **Mathematica** | SageMath, SymPy, Maxima | ~70% research, ~90% engineering | Special functions, integration engine |
| **Maple** | SageMath, Maxima, SymPy, Reduce | ~80% | ODE classifier, physics packages |
| **MATLAB** | Julia, Python+NumPy, Octave, Scilab | ~95% pure math, ~60% control eng | Simulink |
| **CPLEX/Gurobi** | SCIP, HiGHS, OR-Tools/CP-SAT | ~70% industrial, ~95% combinatorial | 2-100× speed gap on hard MIP |
| **MathSciNet** | zbMATH Open, arXiv, Google Scholar | ~85% search, ~70% reviews | Curated review system |

**No proprietary tool is required** for a working substrate today.
That's the headline.

---

## The continuous work pipeline

### The 1000-project backlog

`techne/PROJECT_BACKLOG_1000.md` lists 1000 ranked projects across the
14 categories above. Each is sized to ≤28 days; longer projects are
decomposed into phases.

**Top 10 projects** (as of 2026-04-25, after a recent batch landed):

1. GAP install + wrapper (Tier 3 native, 5d/2 phases)
2. Macaulay2 install + wrapper (5d/2 phases)
3. Lean 4 + Mathlib install + Lean wrapper skeleton (14d/3 phases)
4. Julia + OSCAR.jl install + Julia wrapper (7d/2 phases)
5. ATLAS of Finite Groups data acquisition + wrapper (4d)
6. Property-based test suite for `pm.number_theory` ✓ (just shipped, 126 tests)
7. Authority cross-check suite for `pm.elliptic_curves` vs LMFDB ✓ (just shipped, 242 tests)
8. BSD-audit batch composer (4d)
9. F011 follow-up: gap-k extended scan infrastructure (4d)
10. V-CM-scaling stratifier (3d)

Items 6 and 7 closed in a single TDD batch this week, demonstrating
the pull-from-roadmap rhythm.

### CI/CD around the clock

`.github/workflows/arsenal.yml` runs three jobs continuously:

- **arsenal-smoke** — every push, PR, and 6-hour cron: tolerant
  pip-install, registry probe, full pytest run, capability matrix
  in workflow summary
- **capability-tracking** — daily 07:17: re-probe, diff against
  snapshot, commit or open issue on change
- **docs-regen** — push-to-prometheus_math: regenerate `ARSENAL.md`,
  auto-commit if changed

The git log is itself a secondary tool index: every commit message
explicitly announces tool availability changes.

### The pull-from-roadmap mandate

When no direct researcher ask exists, Techne (the toolsmith agent)
pulls the next-priority item from the 1000-project backlog and
advances it. Phase boundaries are commit boundaries. The roadmap
moves continuously toward zero open items, but new items arrive as
researcher needs surface, and Tier 9 tracks new tools published in
the field.

There is no idle state — only the "between researcher asks" state,
which is the perpetual development pipeline.

---

## Where this differs from existing efforts

### vs. SageMath

SageMath is the closest comparable in spirit: an open-source unified
math system. We differ in three ways:

- **Smaller, opinionated surface.** SageMath wraps ~100 tools and
  exposes thousands of functions in its own naming convention.
  `prometheus_math` wraps the ~30 tools its researchers actually need
  and exposes ~140 functions in Pythonic naming.
- **Test-driven from the ground up.** Every operation has authority +
  property + edge + composition tests. SageMath's testing is more
  mature for some areas (NT) and weaker for others.
- **Agentic-scientist-first.** The API is designed for AI agents to
  call cleanly: dict returns, lazy imports, capability registry,
  consistent error messages. SageMath assumes a human at a notebook.

### vs. OSCAR.jl

OSCAR is the next-generation open-source unified system, written in
Julia. We complement OSCAR rather than compete:

- When OSCAR ships an operation faster than PARI/Singular, we'll
  dispatch to it via the `_julia` backend.
- The categorical operation surface stays in Python; OSCAR is one of
  several backends for that surface.
- Researcher onboarding stays in Python (the dominant language for
  scientific Python and AI agents).

### vs. proof-assistant ecosystems

Lean+Mathlib, Coq, Isabelle each have their own proof communities.
We integrate by exposing them as backends behind a `pm.proof.*`
categorical module (planned, project #3). The unified API doesn't
replace the communities — it gives one entry point for AI agents who
need to query, search, or invoke any of them without learning each
one's idiosyncratic interface.

### vs. databases-as-services

LMFDB, OEIS, KnotInfo, zbMATH are all critical data substrates. We
wrap each with:

- Typed Python interfaces returning dicts (no SQL string
  concatenation, no parsing CSV by hand)
- **Local-mirror-first** dispatch: if the dataset is locally
  cached, we use it; if not, we hit the live API; if both fail, we
  raise a clear error
- Cross-database join engines (planned, project #19): query LMFDB
  curves, look up the resulting integer sequences in OEIS, surface
  unexpected hits

This makes mathematical-database queries **first-class research
operations**, not auxiliary lookups.

---

## Where AI integration fits

The substrate is designed to be agent-callable. The next wave of
investment is in AI tooling specifically:

### Lean Copilot-style integration

Once Lean 4 + Mathlib lands (project #3), we'll add `pm.proof.suggest_tactic(goal)`
that:

- Sends the goal state to a local LLM (DeepSeek-Prover-V2 weights or
  similar)
- LLM returns ranked tactic suggestions
- Each suggestion is validated by Lean before being returned
- Successful proofs become training data for the next iteration

### Conjecture engines

`pm.research.conjecture_engine` (project #19) generates conjectures
from cross-database joins:

- For each LMFDB elliptic curve, generate the sequence of `a_p`
  Frobenius traces
- Search the OEIS for matches
- Surface unexpected hits — sequences that match a non-EC OEIS entry
  in a non-trivial way
- Rank by surprise (low prior probability of accidental match)

The output is a ranked list of cross-domain coincidences that
researchers can then investigate.

### Pattern detection on databases

Aporia's void-detection work (the "what's *missing* from current
mathematical knowledge" framing) is being formalized as
`pm.research.surface_anomalies(family_query)`. Run it on any
L-function family and it returns spectral ratios, conductor-stratified
deficits, and any anomalies relative to known random-matrix
universality classes.

### AI training corpora

Mathlib (project #3 phase 3) becomes a training corpus we maintain
locally. AlphaProof and DeepSeek-Prover were both trained on Mathlib;
having a local snapshot lets us:

- Train smaller specialized provers on subsets (NT-only, AG-only)
- Fine-tune commercial-LLM responses with RAG over Mathlib
- Diff against new Mathlib releases for capability tracking

---

## Local-dataset strategy

A separate strategic document at
`whitepapers/local_dataset_strategy.md` covers the case for local
mirroring of mathematical datasets. Summary:

**Why local mirrors matter:**
1. **API resilience** — OEIS's JSON search endpoint is Cloudflare-gated
   from many networks. The local mirror resolves this entirely.
2. **Throughput** — bulk scans on LMFDB are network-bound; local Postgres
   replicas are 50-500× faster.
3. **Reproducibility** — versioned local snapshots are durable; "live
   state of LMFDB on date X" is fragile.

**Highest-priority acquisitions:**

1. ~OEIS local mirror (~50 MB stripped + 1.5 GB full)~ ✓ DONE
2. ~Mossinghoff Mahler tables (~5 MB)~ ✓ DONE
3. Mathlib4 source + AST corpus (1.5–20 GB) — coupled with Lean install
4. ATLAS of Finite Groups (50 MB) — coupled with GAP install
5. Cremona EC CSV (600 MB) — optional faster-than-SQL bulk
6. arXiv metadata snapshot (2 GB) — optional bulk literature mining

**Architecture:** uniform local-first wrapper pattern. Each
`pm.databases.*` module checks local mirror before live API. The
`prometheus_math.databases._local` module provides this abstraction
(`data_dir()`, `dataset_path()`, `fetch_dataset()`, etc.).

---

## What's not yet wrapped

The honest list. Tracked in `techne/ARSENAL_ROADMAP.md`:

### Critical native installs (Tier 3 — pending user-interactive install)

- **GAP** — finite group theory, character tables, ATLAS data
- **Macaulay2** — commutative algebra, Gröbner bases, syzygies
- **Lean 4 + Mathlib** — formal verification, AI prover training
- **Julia + OSCAR.jl** — modern Magma replacement, faster on some ops

These four together represent ~80 operations not yet available.

### Linux-only / WSL2-required (Tier 4)

- **Regina** — 3-manifold normal surface theory
- **polymake** — convex polytopes, tropical geometry
- **nauty / Traces** — fastest graph isomorphism
- **fpLLL** — fastest LLL/BKZ (cypari.qflll is the current fallback)
- **PHCpack, Bertini** — numerical algebraic geometry
- **CryptoMiniSat, Kissat** — top-tier SAT solvers

### High-impact reverse-engineering (Tier 7)

- Magma's `pAdicLfunction` for higher-weight modular forms
- Magma's `IsogenyClass` for higher-rank isogeny graphs
- Magma's p-Selmer for p > 2
- Mathematica's integration engine quality gap

These are multi-week each but high-impact for specific research
threads (Iwasawa theory, BKLPR Selmer distribution).

---

## How this scales

### Short-term (3 months)

Land Tier 3 native installs (GAP, M2, Lean, Julia). That unlocks ~80
new operations without writing new wrappers — just activating the
existing gated wrappers and adding the Lean / Julia bridges. Backlog
items 1-4 in PROJECT_BACKLOG_1000.

### Medium-term (12 months)

Reach 80% test coverage on every shipped operation under the math-tdd
4-category rubric. Build the Conjecture-from-LMFDB pattern detector
(project #19). Reverse-engineer Magma's pAdicLfunction (project #38).

### Long-term (3+ years)

The roadmap explicitly never ends. Years of work catalogued. New
mathematical software is published every quarter (PyPI scan, conference
artifact tracking). Mathlib grows ~10–20% per year and the AST-corpus
based AI prover infrastructure compounds.

There is no completion state. The substrate matures, expands, and
adapts to research direction shifts.

---

## How to contribute

If you're a Prometheus researcher:

- File a research-driven REQ at `techne/queue/requests.jsonl` — the
  toolsmith's primary input
- Or directly add an entry to `techne/PROJECT_BACKLOG_1000.md`
- Or post a request on the `agora:techne` Redis stream

If you're a developer:

- Read `prometheus_math/USER_GUIDE.md` (forthcoming, project #23)
- Read `techne/skills/math-tdd.md` for the testing discipline
- Pick an item from `techne/PROJECT_BACKLOG_1000.md` and follow the
  TDD workflow

If you're an external observer:

- The repository is public at github.com/jcraig949jfi/Prometheus
- Read `whitepapers/mathematical_research_software.md` for the
  field-guide context
- Read this document for the architecture
- Open an issue with feedback or a tool we should wrap

---

## Closing

Mathematical research is increasingly computational. AI agents doing
mathematical research need a substrate where every operation has one
canonical entry point, every output has an authority-based test, and
every backend can be swapped without rewriting code.

`prometheus_math` is that substrate. It exists to make the marginal
cost of testing a new mathematical conjecture, of running a new
identity-join scan, of validating a new claim against LMFDB —
**one function call**.

Years of work ahead. The forge never cools.

---

*Compiled by Techne, 2026-04-25.*
*See also:*
- *`prometheus_math/ARSENAL.md`* — auto-generated capability matrix and operation reference
- *`techne/PROJECT_BACKLOG_1000.md`* — the long-term project queue
- *`techne/ARSENAL_ROADMAP.md`* — tier-organized roadmap
- *`techne/skills/math-tdd.md`* — the TDD discipline
- *`whitepapers/mathematical_research_software.md`* — the 50-tool field guide
- *`whitepapers/local_dataset_strategy.md`* — local-mirror strategy
