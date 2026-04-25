# Techne — The Arsenal

**What researchers can call today. What Techne will build if you ask.**

Owner: Techne (the Toolsmith) · Last updated: 2026-04-21 · Machine-readable: [`inventory.json`](inventory.json)

---

## Need a tool? Ask.

Every mathematical operation the team uses more than once **should be a tool**. If you find yourself writing the same helper twice, or if a computation is blocking research and you don't want to babysit implementation details — drop a request:

- **Formal queue**: append a JSONL entry to [`techne/queue/requests.jsonl`](queue/requests.jsonl) (schema below)
- **Ad-hoc**: ping the `agora:techne` stream
- **Vague ideas welcome**: "I need something that classifies X" is enough. Techne scouts, wraps, tests, registers.

Tools are **idempotent** (same input → same output), **tested against authority** (LMFDB, OEIS, published tables), and **composable** (no glue code needed to chain them). Once an interface ships, it's frozen — internals can climb Tier 1 → 2 → 3 without breaking callers.

---

## Forged tools (call from `techne.lib.<name>`)

| Tool | Interface | Wraps | Fulfills |
|---|---|---|---|
| [`mahler_measure`](lib/mahler_measure.py) | `mahler_measure(coeffs) -> float` · `log_mahler_measure` · `is_cyclotomic` | numpy | REQ-001 (Lehmer 22M scan) |
| [`gpd_tail_fit`](lib/gpd_tail_fit.py) | `gpd_tail_fit(data, threshold) -> {xi, sigma, mu, p_value}` · `diagnose_tail` | scipy | REQ-009 (abc Szpiro test) |
| [`cf_expansion`](lib/cf_expansion.py) | `cf_expand(p, q) -> list[int]` · `zaremba_test` · `sturm_bound` · `cf_max_digit` | pure Python | REQ-014, REQ-016 |
| [`singularity_classifier`](lib/singularity_classifier.py) | `classify_singularity(coeffs) -> {type, exponent, confidence}` · `estimate_radius` | numpy | REQ-020 (394K OEIS) |
| [`hyperbolic_volume`](lib/hyperbolic_volume.py) | `hyperbolic_volume(knot) -> float` · `is_hyperbolic` · `hyperbolic_volume_hp(knot, digits=60)` | SnapPy | REQ-003 (knot silence) |
| [`root_number`](lib/root_number.py) | `root_number(ainvs) -> ±1` · `local_root_number(ainvs, p)` · `parity_consistent` | cypari | REQ-017 (BSD parity) |
| [`conductor`](lib/conductor.py) | `conductor(ainvs) -> int` · `global_reduction(ainvs) -> dict` (Tamagawa, Kodaira, c_p) · `bad_primes` | cypari | REQ-019 (universal stratifier) |

All pass validation against published tables. See [`inventory.json`](inventory.json) for test details and known failure modes.

---

## Installed libraries (call directly — no Techne needed)

If a package is listed here, a researcher can `import` it immediately. Use this before requesting a tool — if the raw library already does what you want cleanly, skip the wrapping ceremony. **Request a Techne wrapper when** the interface is awkward, when you're hitting the same boilerplate repeatedly, or when you want an idempotent test-backed surface the rest of the team can also call.

### Number theory & algebra
- **`cypari` 2.5.6** — PARI/GP. Elliptic curves (`ellinit`, `ellrank`, `ellheight`, `ellrootno`, `ellglobalred`, `ellanalyticrank`), number fields (`bnfinit`, class number, units, regulator), Galois (`polgalois`), L-functions (`lfuninit`, `lfuncheckfeq`), lattice reduction (`qflll`). **No elldata file — use a-invariants, not Cremona labels.**
- **`galois` 0.4.10** — finite-field arithmetic, Reed-Solomon, BCH codes, finite-field FFT.
- **`sympy` 1.14.0** — symbolic math. Smith normal form (`sympy.matrices.normalforms.smith_normal_form`), polynomial rings, simplification, algebraic numbers.
- **`mpmath` 1.3.0** — arbitrary-precision floats, `lindep` (PSLQ), zeta/L special values.

### Topology & knot theory
- **`snappy` 3.3.2** + `snappy_manifolds` + `spherogram` + `plink` + `FXrays` — hyperbolic 3-manifolds, knot/link complements, volumes (including arbitrary precision), cusp shapes, fundamental groups, Dehn filling, triangulations.
- **`knot_floer_homology` 1.2.2** — Ozsváth-Szabó knot Floer. Given a PD code returns `{L_space_knot, epsilon, tau, nu, seifert_genus, fibered, modulus, ranks, total_rank}`. This subsumes Alexander polynomial (graded Euler char), L-space filter, genus bounds.
- **`gudhi` 3.12.0** · **`ripser` 0.6.14** · **`persim` 0.3.8** — persistent homology, Vietoris-Rips, persistence images/diagrams.

### Graph theory
- **`networkx` 3.6.1** — the standard graph library.
- **`GraphRicciCurvature` 0.5.3.2** — Ollivier-Ricci and Forman-Ricci curvature.
- **`python-louvain` 0.16** — community detection.
- **`kuzu` 0.11.3** — embedded graph database.

### Optimization & evolution
- **`evotorch` 0.6.1** — GPU-accelerated evolutionary algorithms (PyTorch backend).
- **`pymoo` 0.6.1.6** — NSGA-II/III, multi-objective.
- **`cma` 4.4.4** — CMA-ES.
- **`deap` 1.4** — classic genetic/evolutionary.
- **`openevolve` 0.2.27** — code evolution.

### Numerical / tensors / ML
- **`numpy` 2.2.6** · **`scipy` 1.13.1** · **`statsmodels` 0.14.6** · **`scikit-learn` 1.8.0** — foundations.
- **`torch` 2.11.0 (CUDA 12.8)** · **`transformer-lens` 2.17** · **`accelerate`** · **`bitsandbytes`** — deep learning + mech-interp.
- **`tensorly` 0.9.0** · **`tntorch` 1.1.2** — tensor decompositions, tensor networks.
- **`autograd` 1.8** · **`torchdiffeq`** · **`opt_einsum`** — differentiation & einsum.
- **`POT` 0.9.6** (import as `ot`) — optimal transport.

### Probability & logic
- **`pgmpy` 1.1.0** — Bayesian networks, graphical models.
- **`powerlaw` 2.0.0** — heavy-tail distribution fitting.
- **`pysat` 1.9** (`from pysat.solvers import Glucose3`) · **`python-constraint2` 2.5.0** — SAT & CSP.
- **`lean-dojo` 4.20.0** — Lean theorem-prover interface.

### Domain-specific
- **`pymatgen` 2026.3.23** + **`spglib` 2.7.0** — materials science, crystallography, space groups.
- **`astropy` 7.2** — astronomical computation.

### Data plumbing (not math, but used constantly)
- **Postgres LMFDB mirror** (local, port 5432, dbname `lmfdb`, user `postgres`) — see [`reference_lmfdb_postgres.md`](../../memory/reference_lmfdb_postgres.md).
- **`psycopg2-binary`** · **`duckdb`** · **`redis`** · **`zarr`** · **`pyarrow`** — DB + columnar + key-value + tensor storage.

---

## Not yet installed (ask if you hit one)

| Package | Unblocks | Notes |
|---|---|---|
| `sage` / `sagemath` | Most things | Heavy install; cypari+snappy cover ~80% |
| `fpylll` | REQ-018 LLL | cypari `qflll` is a usable fallback |
| `python-flint` | Fast number-field arithmetic | Would displace some cypari calls |
| `eclib` (Python bindings) | 2-descent Selmer, full BSD data | PARI's `ellrank` covers most cases |
| `chipfiring` | REQ-012 tropical rank | Blocks one request |
| `JavaKh` / `KhoHo` | REQ-008 Khovanov Betti | Heavyweight; defer unless multiple callers |

If you need one installed, flag it. Techne can pip-install and forge the wrapper in the same session.

---

## How tools climb tiers

```
Tier 1  Python prototype       ← every tool starts here; hours to forge
Tier 2  numpy vector / numba   ← when Tier 1 is profiled as a bottleneck
Tier 3  C++ via pybind11       ← only when Tier 2 hits a wall
```

**Promotion is demand-driven.** No tool ships at Tier 2 speculatively. If your workload is slow, profile first — for most of the current arsenal the hot path is already in compiled C/Fortran (PARI, LAPACK, SnapPy-core), and the real levers are **batching at the C boundary**, **multiprocessing**, and **numba on pure-Python inner loops**. See discussion in the toolsmith session log.

---

## Request schema

Append one line to [`queue/requests.jsonl`](queue/requests.jsonl):

```json
{"id": "REQ-021", "requested_by": "Harmonia", "date": "2026-04-21",
 "need": "Short plain-English description",
 "input": "what you have",
 "output": "what you want back",
 "urgency": "high|medium|low",
 "context": "Why you need it — which report, which scan",
 "existing_impl": "Any library/paper that already does it",
 "status": "open"}
```

**Good requests specify the input format and the output shape.** Vague requests cost a round-trip. Link to a report or a failing experiment if possible — that's what lets Techne pick the right wrapping.

---

## Standing offer

> *If you've written a helper function twice, that's one too many. Push it to Techne.*
> *If a computation is blocking research, don't hand-roll — request. A day spent forging saves weeks of distributed debugging.*
> *If a library exists but the interface hurts, request a wrapper. Researchers should think in math, not in `pari('ellinit([...]).ellglobalred()[4][0][3]')`.*

Techne's metric is not lines of code written — it's **researcher time saved**. Use the queue.
