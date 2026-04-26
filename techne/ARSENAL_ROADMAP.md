# Techne Arsenal Roadmap

**Long-term tracker for mathematical-software arsenal expansion.**

Updated: 2026-04-25 (initial) · Maintainer: Techne · Living document — never "done"

---

## Status legend

- 🟢 **OP** = operational; wrapped + tested + documented + accessible via `prometheus_math`
- 🟡 **WIP** = installed/available, partial wrap or not yet exposed via unified API
- 🔵 **READY** = installed but not yet wrapped
- 🟠 **GAP** = identified, not yet installed (decision pending or queued)
- 🔴 **BLOCK** = cannot install on current platform without WSL2 / native rebuild
- ⚫ **NOVEL** = doesn't exist; we'd build it

---

## Tier 1 — Already wrapped in Techne lib (operational)

These are the existing 21 Techne tools as of 2026-04-22. They become the
first-class implementations under `prometheus_math/`.

| Tool | Wraps | Category | Status |
|---|---|---|---|
| TOOL_MAHLER_MEASURE | numpy | NT | 🟢 OP |
| TOOL_GPD_TAIL_FIT | scipy | stats | 🟢 OP |
| TOOL_CF_EXPANSION | pure Python | NT | 🟢 OP |
| TOOL_SINGULARITY_CLASSIFIER | numpy | analytic comb | 🟢 OP |
| TOOL_HYPERBOLIC_VOLUME | snappy | TOP | 🟢 OP |
| TOOL_ROOT_NUMBER | cypari | EC | 🟢 OP |
| TOOL_CONDUCTOR | cypari | EC | 🟢 OP |
| TOOL_CLASS_NUMBER | cypari | NT | 🟢 OP |
| TOOL_REGULATOR | cypari | EC | 🟢 OP |
| TOOL_SMITH_NORMAL_FORM | sympy | algebra | 🟢 OP |
| TOOL_GALOIS_GROUP | cypari | NT | 🟢 OP |
| TOOL_LLL_REDUCTION | cypari | NT | 🟢 OP |
| TOOL_KNOT_SHAPE_FIELD | snappy + cypari | TOP | 🟢 OP |
| TOOL_HILBERT_CLASS_FIELD | cypari | NT | 🟢 OP |
| TOOL_ANALYTIC_SHA | cypari + Techne regulator | EC | 🟢 OP |
| TOOL_SELMER_RANK | cypari | EC | 🟢 OP |
| TOOL_FALTINGS_HEIGHT | cypari | EC | 🟢 OP |
| TOOL_ALEXANDER_POLYNOMIAL | knot_floer_homology | TOP | 🟢 OP |
| TOOL_FUNCTIONAL_EQ_CHECK | cypari | NT/L-fns | 🟢 OP |
| TOOL_TROPICAL_RANK | chipfiring | COMB | 🟢 OP |
| TOOL_CM_ORDER_DATA | cypari | NT | 🟢 OP |

---

## Tier 2 — Installed, ready to wrap into prometheus_math

Pip-installed already; just need facade work.

| Tool | Category | Why Prometheus needs it | Status |
|---|---|---|---|
| **sympy** | symbolic | Symbolic CAS; integration, simplification, polynomial ops | 🔵 READY |
| **mpmath** | high precision | Riemann zeta, PSLQ integer relations, special functions | 🔵 READY |
| **gmpy2** | high precision | GMP/MPFR/MPC bindings; arbitrary precision integer/float/complex | 🔵 READY |
| **python-flint** | NT primitives | Fast modular arithmetic, polynomial factoring | 🔵 READY |
| **z3-solver** | SMT | Theorem-proof scaffolding; SMT-decidable subsets | 🔵 READY |
| **pysat** | SAT | Combinatorial-to-SAT reductions | 🔵 READY |
| **pyscipopt** | OPT MIP | Open-source MIP for combinatorial optimization | 🔵 READY |
| **ortools / CP-SAT** | OPT CP | Google CP-SAT for combinatorial constraint solving | 🔵 READY |
| **highspy** | OPT LP | Fast LP/MIP backend | 🔵 READY |
| **pulp** | OPT modeling | Modeling layer over multiple OPT solvers | 🔵 READY |
| **cvxpy** | OPT convex | Convex optimization modeling | 🔵 READY |
| **gudhi** | TDA | Persistent homology, Mapper, witness complexes | 🔵 READY |
| **ripser** | TDA | Fast Vietoris-Rips persistence | 🔵 READY |
| **persim** | TDA | Persistence images, distances | 🔵 READY |
| **galois** | finite fields | GF(p^n) arithmetic, Reed-Solomon, BCH codes | 🔵 READY |
| **networkx** | combinatorics | Graph theory, routing, isomorphism (slow) | 🔵 READY |
| **chipfiring** | combinatorics | Graph divisor theory, Baker-Norine rank | 🔵 READY |

---

## Tier 3 — Heavy native installs (queued; install one at a time)

Native binaries on Windows; may install via installer or WSL2.

| Tool | Category | Install approach | Why we want it | Priority | Status |
|---|---|---|---|---|---|
| **GAP** | groups | Native Windows installer (~150 MB) | Finite group computation, character tables, ATLAS access; standard for group theory research | High | 🟠 GAP |
| **Macaulay2** | algebra/AG | Native Windows binary (~200 MB) | Commutative algebra, Gröbner bases, syzygies, sheaf cohomology | High | 🟠 GAP |
| **Lean 4 + Mathlib** | proof assistant | `elan` installer + `lake build` (~5 GB; first build slow) | Formal verification of research results; AI-prover integration; future-proof | High | 🟠 GAP |
| **Julia 1.10+** | language | Native Windows installer (~300 MB) | Modern numerical computing; gateway to OSCAR, Hecke, Nemo, HomotopyContinuation.jl | High | 🟠 GAP |
| **Singular** | algebra | Bundle with SageMath, or MSYS2 standalone | Polynomial-ring computation, fastest Gröbner basis | Medium | 🟡 WIP (subprocess wrapper shipped at `prometheus_math.algebraic_geometry`; gates on `_singular.is_installed()`; auto-activates when Singular reaches PATH/Cygwin/Sage-bundle) |
| **SageMath** | meta-CAS | Conda-forge `sagemath` or WSL2 (~3 GB) | Unified CAS; many specialized algorithms; backup for tools we'd otherwise miss | Medium | 🟠 GAP |
| **OSCAR.jl** | meta-CAS | Julia Pkg.add (after Julia installed; ~1 GB) | Modern Julia successor to Magma; closing Magma gap | Medium | 🟠 GAP |
| **PARI/GP standalone** | NT | Native Windows installer (~50 MB) | We have cypari already; standalone GP useful for `gp -q` scripts | Low | 🟠 GAP |
| **Maxima** | CAS | Native Windows installer (~70 MB) | Classic CAS; some algorithms not in SymPy | Low | 🟠 GAP |
| **R** | statistics | Native Windows installer (~150 MB) | Statistical inference, rare-event modeling; some pure-math stat work | Low | 🟠 GAP |

---

## Tier 4 — Linux-only / WSL2 required

Hard to install natively on Windows. Decision pending: stand up WSL2 or skip.

| Tool | Category | Why we want it | Priority | Status |
|---|---|---|---|---|
| **Regina** | TOP 3-mfd | Triangulation-based 3-manifold topology; complement to SnapPy | High | 🔴 BLOCK |
| **polymake** | polytopes / tropical | Convex polytopes, polyhedral combinatorics, tropical geometry | Medium | 🔴 BLOCK |
| **nauty / Traces** | combinatorics | Fastest practical graph isomorphism; or use `pynauty` pip on Linux | Medium | 🔴 BLOCK |
| **fpLLL** | NT lattice | Fastest LLL/BKZ; `cypari.qflll` is fallback | Medium | 🔴 BLOCK |
| **PHCpack** | NAG | Polyhedral homotopy continuation | Low | 🔴 BLOCK |
| **Bertini** | NAG | NAG (older but full-featured) | Low | 🔴 BLOCK |
| **CryptoMiniSat / Kissat** | SAT | Top-tier SAT solvers (PySAT bundles MiniSat-class only) | Low | 🔴 BLOCK |

---

## Tier 5 — Web service wrappers (mathematical databases)

Living public APIs. Wrappers to make queries first-class within
`prometheus_math`.

| Service | Category | Why we want it | Priority | Status |
|---|---|---|---|---|
| **LMFDB Postgres mirror** | DB | Direct SQL to L-functions, modular forms, EC, NF; already used heavily in Prometheus | Highest | 🟢 OP (`prometheus_math.databases.lmfdb`; 10/10 tests, 3.8M EC accessible) |
| **OEIS** | DB | Integer-sequence lookup; conjecture seeding | Highest | 🟢 OP (local mirror: 395K sequences, ~37 MB at `prometheus_data/oeis/`; resolves Cloudflare blocker via local-first dispatch; live API used as fallback when reachable) |
| **KnotInfo / LinkInfo** | DB | Knot/link census tables with invariants | High | 🟢 OP (`prometheus_math.databases.knotinfo`; via database_knotinfo pip; 12,966 knots + 4,188 links cached) |
| **ATLAS of Finite Groups** | DB | Finite simple group representations | Medium | 🟠 GAP (couples with GAP install) |
| **arXiv** | literature | Preprint search and download | Medium | 🟢 OP (`prometheus_math.databases.arxiv`; live API via arxiv pip pkg) |
| **zbMATH Open** | literature | Open-access math literature | Medium | 🟢 OP (`prometheus_math.databases.zbmath`; live API verified at api.zbmath.org/v1/document/_search; 8/8 tests pass) |
| **NumberFields.org / EC.org** | DB (Cremona) | Cremona's number-field and EC tables | Low | 🟠 GAP (LMFDB covers most; local mirror CSV optional — see whitepapers/local_dataset_strategy.md) |

---

## Tier 6 — AI/ML integrations

Modern AI tooling for math, both as backend and as workflow.

| System | Category | Why we want it | Priority | Status |
|---|---|---|---|---|
| **DeepSeek-Prover-V2** | AI prover | Open-weight Lean 4 prover; tactical proof generation | High | 🟠 GAP (needs Lean 4 first) |
| **Lean Copilot** | AI prover plugin | LLM-augmented tactic suggestion in Lean | High | 🟠 GAP (needs Lean 4 first) |
| **AlphaProof / AlphaGeometry** | AI prover | DeepMind's IMO-grade systems | — | 🔴 BLOCK (not publicly released) |
| **Mathlib LLM training** | corpus | Custom-finetune small models on Mathlib for our research domains | Medium | ⚫ NOVEL |
| **LLM-tactic-suggester** | AI prover | Local LLM (Llama 70B+) for proof tactic suggestion | Medium | ⚫ NOVEL |
| **Conjecture-from-LMFDB** | AI discovery | LLM-based pattern detection on LMFDB cross-joins | Medium | ⚫ NOVEL |

---

## Tier 7 — Reverse-engineer paywalled functionality

Specific Magma / Mathematica / Maple algorithms not yet open-source. Each
of these is a multi-week project.

| Target | Source | Why we want it | Priority | Status |
|---|---|---|---|---|
| **Magma `IsogenyClass`** | Magma | Higher-rank isogeny graph computation (NT critical) | High | 🟠 GAP |
| **Magma `pAdicLfunction`** | Magma | p-adic L-functions for higher-weight modular forms | High | 🟠 GAP |
| **Magma `SelmerGroup` (p > 2)** | Magma | p-Selmer for p > 2 (currently 2-Selmer only via PARI) | Medium | 🟠 GAP |
| **Mathematica `Integrate` quality** | Mathematica | Match Mathematica's integration engine for hard integrals | Medium | 🟠 GAP |
| **Maple ODE classifier** | Maple | Identify ODE class and applicable solution methods | Low | 🟠 GAP |
| **Mathematica special functions** | Mathematica | Curated special-function library beyond mpmath/sympy | Low | 🟠 GAP |

---

## Tier 8 — Novel tools (custom-built for Prometheus needs)

Tools that don't exist but our research has surfaced as needed. Add as
they emerge from agora streams or roadmap reviews.

| Tool | Why we need it | Priority | Status |
|---|---|---|---|
| **shape→iTrF substitution helper** | Aporia caveat (a) on H101: shape field vs invariant trace field | Low | ⚫ NOVEL (deferred per Aporia) |
| **Cross-database join engine** | LMFDB × OEIS × KnotInfo joins for void detection | Medium | ⚫ NOVEL |
| **Resumable-progress IO helper** | Long-running batch jobs with checkpoint/resume | Low | ⚫ NOVEL |
| **Khovanov homology pure-Python** | REQ-008; current options all Java/Perl heavy | Medium | ⚫ NOVEL |
| **Lehmer-degree-profile binner** | Charon's Mahler-measure scans need standard binning | Low | ⚫ NOVEL |
| **BSD audit batch** | Compose existing BSD chain over arbitrary curve set | Medium | ⚫ NOVEL |
| **CM-order × torsion stratifier** | F011-style cross-stratification helper | Low | ⚫ NOVEL |

---

## Tier 5b — Local dataset mirrors (complement to Tier 5 wrappers)

Each Tier-5 wrapper benefits from a local-mirror complement. See
`whitepapers/local_dataset_strategy.md` for the full strategy. Highest-
impact mirrors:

| Dataset | Size | Why we want it | Status |
|---|---|---|---|
| **OEIS stripped + names** | ~50 MB | Resolves Cloudflare blocker for `oeis.lookup()` | 🟢 OP (downloaded 2026-04-25 to `prometheus_data/oeis/`; 395,310 sequences; auto-loads on `prometheus_math` import) |
| **OEIS full dump (b-files, formulas, programs)** | ~1.5 GB | Full offline OEIS | 🟠 GAP |
| **Mossinghoff Mahler-measure tables** | ~5 MB | Lehmer/Salem cross-checks (Charon work) | 🟢 OP (`prometheus_math.databases.mahler`; 21 polynomials embedded; all M values cross-checked vs `techne.mahler_measure` to <1e-9; `lehmer_witness()`, `smallest_known(degree)`, `all_below(M)` etc.) |
| **Mathlib4 source + AST corpus** | 1.5–20 GB | Coupled with Lean 4 install; AI prover training | 🟠 GAP (depends Tier 3 Lean) |
| **ATLAS of Finite Groups (JSON export)** | ~50 MB | Finite group reference data | 🟠 GAP (depends Tier 3 GAP) |
| **Cremona EC CSV** | ~600 MB | Faster-than-SQL bulk EC scans; LMFDB live is sufficient meanwhile | 🟠 GAP (low priority) |
| **arXiv metadata snapshot** | ~2 GB | Bulk literature mining / ML training | 🟠 GAP (low priority) |

Architecture: `prometheus_math.databases._local` (planned) provides a
mirror-first lookup pattern with fallback to live API. New env var
`PROMETHEUS_DATA_DIR` configures the mirror root.

---

## Tier 9 — Continuously emerging (track, not yet decide)

New tools surface every quarter. Watch list:

- **Mathlib growth** — new theorems / new areas covered. Add wrappers as
  Lean integration becomes routine.
- **OSCAR releases** — every minor release adds Magma-replacement coverage.
- **DeepSeek-Prover successors** — AI-prover landscape moving fast.
- **PyPI math packages** — quarterly scan for new pip-installable tools.
- **Conference paper artifacts** — STOC/FOCS/ITCS/SODA / Algebraic
  Geometry / Number Theory conferences regularly publish code.

---

## Cycle protocol (how to drive this roadmap)

1. **At every Techne idle cycle**, if there's no agora research ask, pull
   the next-priority item from this roadmap and advance it.
2. **Status transitions** are visible in commits with messages like
   `prometheus_math: TOOL_X wrapped (was 🔵 READY → 🟢 OP)`.
3. **New entries** are added when:
   - A research ask surfaces a tool we don't have
   - An agora message mentions a tool we should track
   - A PyPI/conference scan finds a new candidate
   - A heavy install has a precondition met (e.g. Julia → OSCAR)
4. **Deprecation** is also tracked: tools that become unmaintained get
   marked, alternatives noted.

---

*Started 2026-04-25. Updated continuously. Years of work expected.*
