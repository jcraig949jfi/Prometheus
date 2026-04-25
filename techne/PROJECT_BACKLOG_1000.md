# Prometheus Project Backlog — 1000 Projects

**Long-term ranked work queue for the Prometheus North Star.**

Maintainer: Techne · Initial draft: 2026-04-25 · Living document — never "done"

The Prometheus North Star is **frontier mathematics, number theory,
multi-dimensional mathematical exploration, and the discovery of bridges
between mathematical domains that humans haven't found**. This backlog
ranks 1000 candidate projects by their alignment to that goal.

## Methodology

Every project is sized to **≤ 28 days**. Larger work is decomposed into
phases and each phase counted as a separate project.

Each project has:
- **ID** (unique)
- **Title**
- **Category** (one of the 14 area codes below)
- **Priority** (rank 1–1000; lower = more important)
- **Effort** (estimated days, capped at 28)
- **Phases** (1 if single-phase; >1 if decomposed)
- **Deliverable** (one-line outcome)

Categories:
- **A** prometheus_math expansion (new operations, new backends, performance)
- **B** Testing infrastructure (property tests, authority cross-checks, regression suites)
- **C** Number theory specialty (L-functions, modular forms, p-adics, class field theory)
- **D** Algebraic geometry (Gröbner, schemes, tropical, moduli)
- **E** Topology & geometry (knots, 3- and 4-manifolds, persistent homology)
- **F** Combinatorics & graph theory (polytopes, designs, codes, enumeration)
- **G** Database expansion (new wrappers, local mirrors, cross-database joins)
- **H** AI / ML integrations (provers, conjecture generation, pattern detection)
- **I** Proof assistants (Lean, Coq, Isabelle integration)
- **J** Heavy native installs & wrappers (GAP, M2, Lean, Julia, SageMath)
- **K** Visualization & UI (notebooks, dashboards, interactive viz)
- **L** Reverse-engineering paywalled tools (Magma, Mathematica)
- **M** Documentation (tutorials, recipes, onboarding)
- **N** Research-specific (active Prometheus research threads)

## Prioritization rules

1. **Active-research blockers > arsenal coverage > novel exploration.**
   If Charon, Aporia, or Ergon currently can't proceed without a tool,
   that tool ranks high.
2. **Test-first projects rank above their target features.** The TDD
   skill (see `.claude/skills/math-tdd/SKILL.md`) means a research tool
   without authority-based tests is not shippable.
3. **Wrappers that unlock multiple downstream projects rank above
   single-purpose tools.** Lean 4 install enables ~80 other projects;
   GAP install enables ~40.
4. **Reverse-engineering paywalled tools is medium priority.** The
   open-source stack covers ~85% of needs; the missing 15% is
   genuine research compute.
5. **AI integrations rank high but only when foundational tools exist.**
   AlphaProof-style work needs Lean + Mathlib + a corpus first.

---

## TIER 1: Top 50 detailed projects

These are concrete, ready-to-execute projects with full specs. Each is
a self-contained ≤4-week deliverable. The Top 4 will be picked up
immediately by parallel TDD agents.

### #1 — GAP install + wrapper module

- **Category:** J (Heavy native installs)
- **Priority:** 1
- **Effort:** 5 days · Phases: 2
- **Phase 1 (2 days):** Native Windows install of GAP via the official
  installer (`scripts/install_gap.md` already documents the path).
  Verify `gap.exe` on PATH; registry probe lights up.
- **Phase 2 (3 days):** Build `prometheus_math/backends/_gap.py` (subprocess
  gateway, mirroring `_singular.py` pattern) and `prometheus_math/groups.py`
  (categorical facade). Operations: `character_table(name)`,
  `automorphism_group(generators)`, `composition_series`,
  `is_solvable`, `conjugacy_classes`, `irreducible_representations`,
  `centralizer`. Authority-based tests against published character
  tables for `S_n`, `A_n`, `M_11`, `M_12`. ATLAS-of-Finite-Groups
  cross-checks. 15+ tests.
- **Deliverable:** `pm.groups.character_table('S5')` returns the standard
  S₅ character table; tests green; ARSENAL.md regenerated.

### #2 — Macaulay2 install + wrapper module

- **Category:** J
- **Priority:** 2
- **Effort:** 5 days · Phases: 2
- **Phase 1 (2 days):** Native Windows install of Macaulay2 (~200 MB).
  Verify `M2.exe` on PATH.
- **Phase 2 (3 days):** Build `prometheus_math/backends/_m2.py`
  (subprocess gateway) extending `prometheus_math/algebraic_geometry.py`
  with M2-specific operations: `free_resolution`, `intersection_theory`,
  `sheaf_cohomology`, `chern_classes`, `koszul_complex`. Cross-checks
  vs published Macaulay2 textbook examples. 12+ tests.
- **Deliverable:** `pm.algebraic_geometry.free_resolution(I, ...)` works
  via M2 backend; tests green.

### #3 — Lean 4 + Mathlib install + Lean wrapper skeleton

- **Category:** J / I
- **Priority:** 3
- **Effort:** 14 days · Phases: 3
- **Phase 1 (2 days):** Install elan, lean stable toolchain (~2 GB),
  configure lake.
- **Phase 2 (5 days):** First Mathlib build (slow ~hours+); store
  `.olean` cache; document the multi-day first build.
- **Phase 3 (7 days):** Build `prometheus_math/proof.py` and
  `prometheus_math/backends/_lean.py` for goal/tactic invocation
  via Lean server. Operations: `parse_theorem`, `try_tactic`,
  `lemma_search`, `check_proof`. 8+ tests using Mathlib lemmas as
  authoritative refs.
- **Deliverable:** `pm.proof.try_tactic(goal, 'simp')` returns Lean's
  response; lemma_search by statement.

### #4 — Julia + OSCAR.jl install + Julia wrapper

- **Category:** J
- **Priority:** 4
- **Effort:** 7 days · Phases: 2
- **Phase 1 (1 day):** Install Julia 1.10+ (native Windows, ~300 MB).
- **Phase 2 (6 days):** Install OSCAR via `Pkg.add("Oscar")` (~1 GB).
  Build `prometheus_math/backends/_julia.py` using `juliacall` for
  subprocess + cross-language calls. Expose `pm.number_theory` and
  `pm.algebraic_geometry` operations to dispatch to OSCAR when faster
  than PARI/Singular. Authority cross-check: OSCAR's class-group
  computation must match `pm.number_theory.class_group(...)` output
  to bit equality.
- **Deliverable:** `pm.registry` shows `julia` + `oscar` available;
  cross-engine consistency tests pass.

### #5 — ATLAS of Finite Groups data acquisition + wrapper

- **Category:** G / J
- **Priority:** 5
- **Effort:** 4 days · Phases: 1
- Scrape or download (with permission/license check) the ATLAS data:
  character tables, generators, presentations, automorphism groups
  for finite simple groups. Build `prometheus_math/databases/atlas.py`.
  Hard-coded JSON snapshot (~50 MB) embedded; couples with GAP
  wrapper from #1. Test cross-checks against published Atlas tables.
- **Deliverable:** `pm.databases.atlas.character_table('M11')` returns
  the published character table.

### #6 — Property-based test suite for prometheus_math.number_theory

- **Category:** B
- **Priority:** 6
- **Effort:** 7 days · Phases: 1
- Adopt `hypothesis` library. Write property-based tests for every
  function in `pm.number_theory`. Properties: `class_number(K)` returns
  positive int; `mahler_measure(coeffs) >= 1`; `lll(B)` preserves
  determinant absolute value; `galois_group(f).order` divides `n!`
  where n = deg f; `cf_expand` round-trips through `cf_evaluate`. Add
  ~80 property tests across NT functions.
- **Deliverable:** `pytest --hypothesis-show-statistics` runs 80+
  property tests, all green; CI integrates Hypothesis.

### #7 — Authority cross-check suite for elliptic_curves vs LMFDB

- **Category:** B
- **Priority:** 7
- **Effort:** 5 days · Phases: 1
- For 1000 random curves from LMFDB, compute via `pm.elliptic_curves`:
  conductor, regulator, root_number, analytic_sha, faltings_height,
  selmer_2_rank. Compare to LMFDB stored values. Any discrepancy is
  a bug. Includes audit log + CI gate (any disagreement fails build).
- **Deliverable:** `prometheus_math/tests/audit/lmfdb_ec_audit.py`
  green on 1000-curve sample; CI runs nightly on a 100-curve subset.

### #8 — BSD-audit batch composer

- **Category:** N (Charon)
- **Priority:** 8
- **Effort:** 4 days · Phases: 1
- Build `prometheus_math/research/bsd_audit.py` composing
  `regulator + conductor + analytic_sha + selmer_2_rank + faltings_height`
  over a curve list (LMFDB query or CSV). Outputs full BSD consistency
  report per curve: predicted Sha, observed Sha (LMFDB), residual,
  rank parity check, Reg×Sha product. Used by Charon for Tier 2
  audits at scale.
- **Deliverable:** `pm.research.bsd_audit.run(label_list)` produces a
  CSV of consistency results; documented rerun pattern.

### #9 — F011 follow-up: gap-k extended scan infrastructure

- **Category:** N (Aporia, Ergon)
- **Priority:** 9
- **Effort:** 4 days · Phases: 1
- Generalize Ergon's gap-k scan to a reusable `pm.research.spectral_gaps`
  module: gap_k variance vs matched-GUE/CUE/USp(4) null across L-function
  families, with conductor/CM/torsion stratification, bootstrap CIs, and
  output as a paper-ready figure. Used by Aporia for paper-track
  Axis 3b extension.
- **Deliverable:** `pm.research.spectral_gaps.scan(family_query, k_max=24)`
  produces a JSON + 4-panel figure.

### #10 — V-CM-scaling stratifier

- **Category:** N (Aporia)
- **Priority:** 10
- **Effort:** 3 days · Phases: 1
- Build `pm.research.vcm_scaling` for the V-CM-scaling sub-void:
  given a sample of CM EC, compute (d_K, f, h(O_f), unit_group_order)
  per curve via TOOL_CM_ORDER_DATA, regress observed compression
  against these arithmetic invariants, output the per-disc residual
  table.
- **Deliverable:** Aporia's per-disc regression becomes a one-line call.

### #11 — OEIS local mirror weekly refresh CI job

- **Category:** B / G
- **Priority:** 11
- **Effort:** 2 days · Phases: 1
- Add a GitHub Actions workflow that downloads OEIS `stripped.gz` and
  `names.gz` weekly, compares to local cache, commits the snapshot
  date update. Tracks new sequences and removes any that were retired
  by Sloane.
- **Deliverable:** `.github/workflows/oeis-refresh.yml` runs weekly,
  commits cache update.

### #12 — KnotInfo local mirror via database_knotinfo with refresh

- **Category:** G
- **Priority:** 12
- **Effort:** 1 day · Phases: 1
- The `database_knotinfo` pip pkg already ships locally. Add explicit
  refresh logic in case knotinfo.math.indiana.edu publishes new csv
  exports. Backfill 14-crossing data when available.
- **Deliverable:** `pm.databases.knotinfo.update_mirror()` works.

### #13 — KnotInfo–LMFDB identity-join tooling

- **Category:** N (Aporia continuation)
- **Priority:** 13
- **Effort:** 5 days · Phases: 1
- Build `pm.research.identity_join.knot_to_nf(knots)` that for each
  knot in a list, computes shape field via TOOL_KNOT_SHAPE_FIELD, then
  queries LMFDB.nf_fields by (degree, abs_disc) to find matching number
  fields, returning a confidence score and the candidate matches.
- **Deliverable:** Aporia's knot→NF identity join is a single function call.

### #14 — Mossinghoff Mahler table extension to ~600 entries

- **Category:** G
- **Priority:** 14
- **Effort:** 7 days · Phases: 2
- **Phase 1 (4 days):** Source curated Mossinghoff data from published
  archives (Boyd, Mossinghoff, Smyth papers) and verify each M(P) via
  `techne.mahler_measure`. Extend embedded snapshot from 21 to ~600
  entries covering degrees 2–44.
- **Phase 2 (3 days):** Add `pm.databases.mahler.search_polynomial(M, deg)`
  for fuzzy lookup by measure within tolerance.
- **Deliverable:** Comprehensive small-Mahler reference for Charon's
  Lehmer/Salem research.

### #15 — Cremona EC dataset local CSV mirror

- **Category:** G
- **Priority:** 15
- **Effort:** 3 days · Phases: 1
- Download Cremona's EC tables from his GitHub (`ecdata`). Wire into
  `pm.databases.lmfdb.elliptic_curves` as local-first when local CSV
  present. Speeds up bulk EC scans 10–100×.
- **Deliverable:** `pm.databases.lmfdb.elliptic_curves(use_local=True)`
  is 50× faster on 10K-curve scans.

### #16 — Performance benchmark suite (Tier-2 promotion candidates)

- **Category:** A / B
- **Priority:** 16
- **Effort:** 4 days · Phases: 1
- Build `prometheus_math/benchmarks/` with timed runs of every
  operation against representative input sizes. Identify Tier-2
  promotion candidates (operations 10× slower than published baselines).
  Generate a report. Run in CI on schedule.
- **Deliverable:** `BENCHMARKS.md` auto-generated; promotion list
  ranked by impact.

### #17 — Hypothesis-based property tests for elliptic_curves

- **Category:** B
- **Priority:** 17
- **Effort:** 4 days · Phases: 1
- Property tests across all `pm.elliptic_curves`: rank ≥ 0; conductor
  > 0; |root_number| = 1; analytic_sha ≥ 1; faltings_height
  isogeny-invariance check across isogenous curves; selmer_2_rank ≥
  rank. ~50 properties.
- **Deliverable:** Hypothesis-driven property suite green; finds 0
  bugs in current implementation (or reports any it finds).

### #18 — arXiv full-text local cache for Lean-relevant papers

- **Category:** G / I
- **Priority:** 18
- **Effort:** 5 days · Phases: 1
- Download a curated set of ~500 arXiv papers tagged math.LO + math.NT
  with formal-verification angle. Build a search index. Used as
  retrieval base for AI tactic suggestion.
- **Deliverable:** `pm.databases.arxiv.local_search(query)` over the
  curated corpus.

### #19 — Conjecture engine: OEIS×LMFDB cross-join

- **Category:** N / H
- **Priority:** 19
- **Effort:** 7 days · Phases: 2
- **Phase 1 (3 days):** Define a "join schema": for each LMFDB EC,
  generate sequences (e.g., a_p coefficients), search OEIS for matches.
  Surface unexpected hits (a_p sequence matches a non-EC OEIS sequence).
- **Phase 2 (4 days):** Run at scale on 10K curves; dedupe; rank by
  surprise.
- **Deliverable:** `pm.research.conjecture_engine.cross_join(lmfdb_query, oeis)`
  produces a ranked list of cross-domain coincidences.

### #20 — Singular install (via SageMath dependency or MSYS2)

- **Category:** J
- **Priority:** 20
- **Effort:** 3 days · Phases: 1
- Singular wrapper at `prometheus_math/backends/_singular.py` already
  exists (gated). Install Singular via SageMath bundle path or MSYS2
  pacman. Activate the gated wrapper.
- **Deliverable:** `pm.algebraic_geometry.groebner_basis(...)` works;
  authority cross-checks vs published Singular textbook examples.

### #21 — fpLLL native-Windows install or replacement

- **Category:** J
- **Priority:** 21
- **Effort:** 4 days · Phases: 1
- Ergon's H101 work needed fpLLL; cypari.qflll is the fallback.
  Install fpLLL via WSL2 or document a working Cygwin path. Wire
  into `pm.number_theory.lll` as alternative backend. Performance
  benchmarks.
- **Deliverable:** fpLLL on PATH, registry lights up, `pm.number_theory.lll`
  dispatches to fpLLL when it beats PARI's qflll.

### #22 — Regina install via WSL2 + bridge

- **Category:** J / E
- **Priority:** 22
- **Effort:** 5 days · Phases: 1
- Install WSL2 Ubuntu, install Regina there, build a Windows-side
  bridge that calls Regina via `wsl.exe` for 3-manifold triangulation
  operations not in SnapPy. Add to `pm.topology`.
- **Deliverable:** `pm.topology.normal_surfaces(triangulation)` via
  Regina backend; 3-sphere recognition working.

### #23 — Documentation: prometheus_math user guide

- **Category:** M
- **Priority:** 23
- **Effort:** 7 days · Phases: 2
- **Phase 1 (3 days):** Write `prometheus_math/USER_GUIDE.md` covering
  installation, first import, capability check, basic usage in each
  category, the local-mirror pattern, when to override backend.
- **Phase 2 (4 days):** Write 10 cookbook recipes (BSD audit, knot-NF
  match, Galois group census, OEIS conjecture check, etc.) at
  `prometheus_math/recipes/`.
- **Deliverable:** Researcher-facing README + recipe gallery.

### #24 — Auto-generated dependency graph for ARSENAL.md

- **Category:** A / M
- **Priority:** 24
- **Effort:** 3 days · Phases: 1
- Extend `pm.doc.arsenal` to compute and render a directed graph of
  inter-module dependencies (e.g., `analytic_sha` depends on `regulator`).
  Embed as Mermaid diagram in ARSENAL.md.
- **Deliverable:** ARSENAL.md has a "Dependency graph" section
  auto-rendered.

### #25 — Galois representation tools (via PARI + Magma-replacement)

- **Category:** C
- **Priority:** 25
- **Effort:** 14 days · Phases: 3
- **Phase 1 (4 days):** `pm.galois.frobenius_traces(rep, primes)` for
  Artin reps via PARI.
- **Phase 2 (5 days):** `pm.galois.l_function(rep)` building the L-function
  from rep + applying functional equation check.
- **Phase 3 (5 days):** `pm.galois.is_modular(rep)` heuristic check via
  matching modular form q-coefficients (LMFDB cross-query).
- **Deliverable:** Aporia's Galois rep ↔ modular form work becomes
  a direct API.

### #26 — Iwasawa λ/μ invariant computation

- **Category:** C
- **Priority:** 26
- **Effort:** 7 days · Phases: 2
- **Phase 1 (3 days):** Implement λ_p, μ_p invariants via Iwasawa class
  group towers using PARI bnfinit + ZpL extensions.
- **Phase 2 (4 days):** Bulk-mode for systematic scan over Iwasawa-relevant
  curves; cross-check with LMFDB ec_iwasawa table.
- **Deliverable:** `pm.number_theory.iwasawa_invariants(K, p)` returns
  λ, μ.

### #27 — Modular forms: q-expansion computation at depth

- **Category:** C
- **Priority:** 27
- **Effort:** 7 days · Phases: 1
- `pm.modular.qexp(label, n_coeffs=1000)` compute first n q-coefficients
  for any LMFDB modular form via Hecke action, beyond what's in the
  current LMFDB stored coefficients.
- **Deliverable:** Extended q-expansions on demand.

### #28 — Hecke eigenvalue computation for arbitrary primes

- **Category:** C
- **Priority:** 28
- **Effort:** 5 days · Phases: 1
- For a modular form, compute Hecke eigenvalue at any prime via PARI's
  modsymbols. Cross-check with LMFDB stored eigenvalues for primes < 1000.
- **Deliverable:** `pm.modular.hecke_eigenvalue(form_label, p)`.

### #29 — Class field tower with Iwasawa-style p-extension

- **Category:** C
- **Priority:** 29
- **Effort:** 7 days · Phases: 2
- Extension of TOOL_HILBERT_CLASS_FIELD to compute the p-class field
  tower (p-Hilbert class field iterated). Tests against published
  Greenberg-conjecture-related results.
- **Deliverable:** `pm.number_fields.p_class_field_tower(K, p, max_depth)`.

### #30 — Lehmer-degree-profile binner

- **Category:** N (Charon)
- **Priority:** 30
- **Effort:** 2 days · Phases: 1
- Helper for Charon's Lehmer scans: given a list of polynomials with
  M(P), bin by degree and report (count, min M, max M, median M, Salem
  count) per bin. Standardized binning across scans.
- **Deliverable:** `pm.research.lehmer.degree_profile(scan_output)`.

### #31 — pyflint advanced operations exposure

- **Category:** A
- **Priority:** 31
- **Effort:** 3 days · Phases: 1
- python-flint is installed but only lightly used. Expose more of its
  surface: `fmpz_poly` factoring, modular polynomial computation,
  fast linear algebra modulo primes.
- **Deliverable:** `pm.numerics.flint_factor`, `pm.numerics.flint_polmodp`.

### #32 — Property-based tests for topology module

- **Category:** B
- **Priority:** 32
- **Effort:** 3 days · Phases: 1
- Hypothesis-based tests for `pm.topology`: knot-invariant orientability
  consistency, Alexander polynomial palindromicity, hyperbolic volume
  > 0 for hyperbolic, knot_shape_field discriminant divides the
  field's actual discriminant. ~30 properties.
- **Deliverable:** Topology Hypothesis suite green.

### #33 — Persistent-homology recipe gallery

- **Category:** M / E
- **Priority:** 33
- **Effort:** 4 days · Phases: 1
- 8–10 recipes at `prometheus_math/recipes/persistent_homology/`:
  Vietoris-Rips on point cloud, distance matrix → persistence diagram,
  bottleneck distance, persistence images for ML pipelines, time-series
  TDA.
- **Deliverable:** End-to-end recipes runnable from a clean install.

### #34 — Lean Copilot-style integration sketch

- **Category:** H / I
- **Priority:** 34
- **Effort:** 14 days · Phases: 3
- **Phase 1 (4 days):** After Lean 4 + Mathlib (project #3), sketch a
  Python wrapper for Lean tactic suggestion using local LLM (Llama
  or similar).
- **Phase 2 (5 days):** Build the suggestion-integration loop: send goal
  state to LLM, LLM returns tactics, validate via Lean.
- **Phase 3 (5 days):** Train a small classifier on Mathlib tactic uses
  to bootstrap suggestions.
- **Deliverable:** `pm.proof.suggest_tactic(goal)` returns ranked
  candidate tactics.

### #35 — DeepSeek-Prover-V2 integration

- **Category:** H / I
- **Priority:** 35
- **Effort:** 7 days · Phases: 2
- **Phase 1 (3 days):** Clone DeepSeek-Prover-V2 weights (open-weight,
  ~140 GB; defer if disk-budget exceeded).
- **Phase 2 (4 days):** Build `pm.proof.deepseek_prove(theorem)`
  wrapper invoking the model on Lean-formatted goals.
- **Deliverable:** `pm.proof.deepseek_prove(thm)` returns Lean proof
  candidate.

### #36 — Visualization: knot diagrams via SnapPy

- **Category:** K
- **Priority:** 36
- **Effort:** 3 days · Phases: 1
- Render knot diagrams as Matplotlib / SVG via SnapPy's plink. Helper
  `pm.viz.draw_knot('4_1')`.
- **Deliverable:** Notebook-ready knot rendering.

### #37 — Visualization: L-function zeros plot

- **Category:** K
- **Priority:** 37
- **Effort:** 2 days · Phases: 1
- `pm.viz.plot_zeros(label)` plots the first N zeros of an L-function
  with confidence bands.
- **Deliverable:** Researcher-friendly L-function visualization.

### #38 — Reverse-engineer: Magma's `pAdicL` for elliptic curves

- **Category:** L
- **Priority:** 38
- **Effort:** 21 days · Phases: 4
- **Phase 1 (5 days):** Survey Magma's p-adic L-function algorithms in
  literature (Pollack, Stevens, Greenberg).
- **Phase 2 (7 days):** Implement basic p-adic L for ordinary EC at p.
- **Phase 3 (5 days):** Extend to supersingular case.
- **Phase 4 (4 days):** Cross-check vs LMFDB's ec_padic table.
- **Deliverable:** `pm.elliptic_curves.padic_l_function(ainvs, p)`.

### #39 — Conjecture-from-data tool: random-matrix-ratio surfacing

- **Category:** N (Aporia)
- **Priority:** 39
- **Effort:** 5 days · Phases: 1
- Given a labeled L-function family (e.g., rank-0 EC), compute spectral
  ratios and compare to all known random-matrix universality classes.
  Surface anomalous ratios as conjecture candidates.
- **Deliverable:** `pm.research.surface_anomalies(family_query)`.

### #40 — Database freshness automation

- **Category:** B / G
- **Priority:** 40
- **Effort:** 3 days · Phases: 1
- CI workflow: weekly check of all upstream databases (LMFDB, OEIS,
  KnotInfo, arXiv, zbMATH); diff captured stats against snapshot;
  open issue if significant change.
- **Deliverable:** `.github/workflows/db-freshness.yml`.

### #41 — Edge-case test gallery

- **Category:** B
- **Priority:** 41
- **Effort:** 5 days · Phases: 1
- For each pm.* operation: test (a) empty input, (b) singleton, (c)
  malformed input, (d) extreme size (e.g., 10^6 coefficient polynomial),
  (e) numerical precision boundary. ~150 edge-case tests.
- **Deliverable:** Edge-case suite green; bugs surfaced and filed.

### #42 — Composition test gallery

- **Category:** B
- **Priority:** 42
- **Effort:** 4 days · Phases: 1
- Tests of operation chains: `regulator(C) * sha_an(C) ≈ L'(C,1)/Ω(C)`
  (BSD identity); `class_number(K) = degree(hilbert_class_field(K))`;
  knot Alexander roots inside knot trace field. ~40 composition tests.
- **Deliverable:** Composition suite catches BSD inconsistencies.

### #43 — pm.research.bootstrap helper

- **Category:** N
- **Priority:** 43
- **Effort:** 3 days · Phases: 1
- Reusable bootstrap-CI helper for the bootstrap operations Charon and
  Aporia run repeatedly. Wraps numpy/scipy + matched-null generation.
- **Deliverable:** `pm.research.bootstrap.matched_null_test(observation, null_fn, n=10000)`.

### #44 — pm.research.tensor cross-domain helpers

- **Category:** N (Harmonia)
- **Priority:** 44
- **Effort:** 7 days · Phases: 2
- Phase 1 (3 days): Helpers to build the cross-domain tensor that
  Harmonia uses (domain × phoneme × invariant).
- Phase 2 (4 days): Distributional and identity-join scorers as named
  operations.
- **Deliverable:** Tensor research becomes a first-class API.

### #45 — Symbolic computation: integration engine improvements

- **Category:** A / L
- **Priority:** 45
- **Effort:** 14 days · Phases: 3
- **Phase 1 (5 days):** Survey SymPy's integration vs Mathematica's:
  identify the worst-30 cases where SymPy fails.
- **Phase 2 (5 days):** Port the algorithms missing from SymPy
  (Risch-Bronstein, Trager).
- **Phase 3 (4 days):** Contribute upstream PR or maintain a fork.
- **Deliverable:** `pm.symbolic.integrate(...)` outperforms vanilla
  SymPy on a documented benchmark set.

### #46 — Mahler measure beyond Lehmer: random-polynomial scan

- **Category:** N (Charon continuation)
- **Priority:** 46
- **Effort:** 4 days · Phases: 1
- Beyond LMFDB-restricted scan, sample random reciprocal polynomials
  by degree and compute M(P) via TOOL_MAHLER_MEASURE. Look for
  sub-Lehmer specimens. Pure exploration.
- **Deliverable:** `pm.research.lehmer.random_scan(degrees, samples)`.

### #47 — `pm.databases.atlas` ATLAS of finite groups (without GAP)

- **Category:** G
- **Priority:** 47
- **Effort:** 4 days · Phases: 1
- Parse the public ATLAS of Finite Groups data into a JSON snapshot.
  Independent of GAP install. Enables group-theory queries before
  the GAP wrapper lands.
- **Deliverable:** Atlas data accessible in pm.databases.atlas before
  GAP install.

### #48 — pm.databases.zbmath MSC2020 full leaf-code expansion

- **Category:** G
- **Priority:** 48
- **Effort:** 3 days · Phases: 1
- Expand from ~200 anchor codes to full ~6500-leaf MSC2020 hierarchy.
- **Deliverable:** `pm.databases.zbmath.msc_codes()` returns all leaf
  codes with descriptions.

### #49 — pm.databases.lmfdb modular forms full extraction

- **Category:** G
- **Priority:** 49
- **Effort:** 5 days · Phases: 1
- Currently `pm.databases.lmfdb.modular_forms` has the basic MF table.
  Add Hecke eigenvalue tables, character orbits, dimension data,
  inner-twist info, mod-l Galois rep info.
- **Deliverable:** Full MF research accessible without writing SQL.

### #50 — Visualization: capability matrix dashboard

- **Category:** K / M
- **Priority:** 50
- **Effort:** 3 days · Phases: 1
- Web dashboard rendering `pm.registry.installed()` as a live grid.
  Hosted at `pm.viz.dashboard()`; refreshes from registry.
- **Deliverable:** Live capability dashboard accessible from local
  Jupyter or browser.

---

## TIER 2: Priority 51-250 (one-line entries grouped by category)

Concrete projects with brief specs. Each has full effort and category;
detail spec lives in commit messages when work begins.

### Category A — prometheus_math expansion (51-150)

51. **A** — Tier-2 numpy vectorization of `mahler_measure` for batch input · 3d
52. **A** — Tier-2 numba JIT for `cf_expand` over arrays of rationals · 2d
53. **A** — Add `pm.symbolic.tensor_decomposition` (CP, Tucker, Tensor-Train) · 5d
54. **A** — Add `pm.numerics.dft` arbitrary-precision FFT via mpmath · 4d
55. **A** — Add `pm.numerics.special.hurwitz_zeta` · 2d
56. **A** — Add `pm.numerics.special.dilogarithm` · 2d
57. **A** — Add `pm.numerics.special.q_pochhammer` · 3d
58. **A** — Add `pm.numerics.special.theta_functions` · 5d
59. **A** — Add `pm.numerics.special.eta_function` arbitrary tau · 3d
60. **A** — Lazy import refactor across all categorical modules · 4d
61. **A** — Add `pm.algebraic_geometry.hilbert_polynomial` (Singular-backend) · 3d
62. **A** — Add `pm.algebraic_geometry.normal_form` (Buchberger normal form) · 3d
63. **A** — Add `pm.combinatorics.partitions` (Young tableaux ops) · 5d
64. **A** — Add `pm.combinatorics.permutations` (Bruhat order, etc.) · 5d
65. **A** — Add `pm.combinatorics.posets` library · 7d (2 phases)
66. **A** — Add `pm.combinatorics.species` (combinatorial species algebra) · 14d (3 phases)
67. **A** — Add `pm.optimization.solve_sdp` (semidefinite programming via cvxpy) · 4d
68. **A** — Add `pm.optimization.solve_qp` (quadratic programming) · 3d
69. **A** — Add `pm.optimization.solve_socp` (second-order cone) · 3d
70. **A** — Add `pm.optimization.metaheuristics` (CMA-ES, GA via DEAP wrapper) · 5d
71. **A** — Add `pm.geometry.convex_hull` (qhull bindings) · 3d
72. **A** — Add `pm.geometry.delaunay` triangulation · 3d
73. **A** — Add `pm.geometry.voronoi` · 3d
74. **A** — Add `pm.statistics.distributions` (rich CDF/PDF/quantile) · 7d (2 phases)
75. **A** — Add `pm.statistics.bayesian` (PyMC integration) · 14d (3 phases)
76. **A** — Add `pm.dynamics.iterated_maps` (logistic, tent, etc.) · 3d
77. **A** — Add `pm.dynamics.ode_solvers` (high-order via mpmath) · 7d
78. **A** — Add `pm.physics.quantum.density_matrix` ops · 14d (3 phases)
79. **A** — Add `pm.physics.path_integral` numerical quadrature · 14d (3 phases)
80. **A** — Add `pm.physics.lie_groups` (matrix groups, Lie algebras) · 14d (3 phases)
81. **A** — Add `pm.crypto.primitives` (modular exp, RSA, ECDH) · 5d
82. **A** — Add `pm.crypto.lattice_based` (LWE/RLWE primitives) · 14d (3 phases)
83. **A** — Add `pm.crypto.isogeny_based` (CSIDH primitives) · 14d (3 phases)
84. **A** — Add `pm.crypto.signature_schemes` (ECDSA, Schnorr, Falcon) · 7d (2 phases)
85. **A** — Add `pm.coding.linear` (BCH, Reed-Solomon, Reed-Muller) · 7d
86. **A** — Add `pm.coding.lattice_codes` · 7d (2 phases)
87. **A** — Add `pm.coding.quantum_codes` · 14d (3 phases)
88. **A** — Add `pm.algebra.lie_algebras` (root systems, weights) · 14d (3 phases)
89. **A** — Add `pm.algebra.hopf_algebras` (combinatorial Hopf algebras) · 14d (3 phases)
90. **A** — Add `pm.algebra.cluster_algebras` (cluster mutation) · 14d (3 phases)
91. **A** — Add `pm.algebra.quantum_groups` (Uq(sl_n), R-matrices) · 21d (4 phases)
92. **A** — Add `pm.category_theory.basic` (functors, natural trans) · 7d (2 phases)
93. **A** — Add `pm.category_theory.operads` · 14d (3 phases)
94. **A** — Add `pm.algebraic_topology.fundamental_group` from CW complex · 7d (2 phases)
95. **A** — Add `pm.algebraic_topology.simplicial_sets` · 14d (3 phases)
96. **A** — Add `pm.algebraic_topology.spectral_sequences` (basic) · 14d (3 phases)
97. **A** — Add `pm.differential_geometry.manifolds` (charts, atlases) · 14d (3 phases)
98. **A** — Add `pm.differential_geometry.connections` (curvature, Christoffels) · 14d (3 phases)
99. **A** — Add `pm.geometry.projective` (projective coords, transforms) · 5d
100. **A** — Add `pm.geometry.hyperbolic_2d` (Möbius transformations) · 5d
101–150. **A** — _bulk:_ 50 more incremental additions across categorical modules covering smaller operations: pretty-printing utilities (5), input format validators (10), dimension constructors (5), specific named operations on number fields (10), specific named ops on EC (10), specific named ops on knots (10).

### Category B — Testing infrastructure (151-260)

151. **B** — Hypothesis property tests for combinatorics module · 3d
152. **B** — Hypothesis property tests for optimization module · 3d
153. **B** — Hypothesis property tests for symbolic module · 3d
154. **B** — Hypothesis property tests for numerics module · 3d
155. **B** — Hypothesis property tests for algebraic_geometry module · 3d
156. **B** — Hypothesis property tests for databases module · 3d
157. **B** — Hypothesis property tests for proof module (when Lean lands) · 3d
158. **B** — Coverage report integration in CI · 3d
159. **B** — Mutation testing via `mutmut` · 5d
160. **B** — Fuzzing via `atheris` for parser inputs (PARI strings, polynomial coeffs) · 5d
161. **B** — Authority cross-check: number_theory vs LMFDB nf_fields · 4d
162. **B** — Authority cross-check: modular_forms vs LMFDB mf_newforms · 5d
163. **B** — Authority cross-check: knot ops vs KnotInfo · 4d
164. **B** — Authority cross-check: integer relations vs OEIS · 3d
165. **B** — Authority cross-check: Mahler measures vs Mossinghoff tables · 3d
166. **B** — Authority cross-check: Galois groups vs LMFDB nf_fields · 3d
167. **B** — Regression test snapshot system for output stability · 4d
168. **B** — Performance benchmark CI integration · 3d
169. **B** — CI flakiness detector (re-run failed tests, report instability) · 3d
170. **B** — Documentation lint: every function has a working docstring example · 3d
171. **B** — Type stubs (PEP 561) for every public API · 7d
172. **B** — mypy strict-mode CI pass · 7d
173. **B** — pytest-xdist parallel CI for full-suite speedup · 2d
174. **B** — `pytest --collect-only` smoke for every commit · 1d
175. **B** — Doctest CI integration (run all docstring examples) · 3d
176. **B** — Cross-platform test matrix (Windows + Linux + Mac) · 5d
177. **B** — Integration test for the `_pari_util.safe_call` retry mechanism · 2d
178. **B** — Integration test for the OEIS local mirror auto-load · 2d
179. **B** — Integration test for backend fallback dispatch · 3d
180. **B** — Integration test for ARSENAL.md regeneration in CI · 1d
181. **B** — Random-input stress tests for every numerical routine (1M iters) · 5d
182. **B** — Memory-leak detection in long-running tools · 4d
183. **B** — Thread-safety tests for parallel use · 4d
184. **B** — Failure-mode tests for every documented failure case · 4d
185. **B** — Snapshot test of capability matrix on PR · 1d
186. **B** — Test of database connection retry/fallback logic · 2d
187. **B** — Test that LMFDB query results are stable over 24h · 2d
188. **B** — Test of encoding correctness (UTF-8, BOM) · 1d
189. **B** — Test for circular-import guards · 1d
190. **B** — Test that all imports in `prometheus_math/__init__.py` complete in <2s · 1d
191. **B** — Test for unused dependencies via `pip-audit` · 1d
192. **B** — Test for security vulnerabilities via `pip-audit` · 1d
193. **B** — Test that every test file has at least one test · 1d
194. **B** — Test that every function in `__all__` has at least one test · 2d
195. **B** — Test that ARSENAL.md never has broken markdown links · 1d
196. **B** — Test that Backend probe is < 100ms each · 1d
197. **B** — Test that registry.py is JSON-serializable · 1d
198. **B** — Test for namespace pollution (no leakage of imports) · 1d
199. **B** — Test for Python 3.11+ syntax compatibility · 1d
200. **B** — Test for Windows path-separator correctness (file IO) · 1d
201–260. **B** — _bulk:_ 60 more targeted tests covering specific code paths in each tool: `analytic_sha rank_hint=0` test (1d each), `hilbert_class_field` with each special signature (1d each), `cm_order_data` for non-imaginary-quadratic D (1d each), parser tests for every known input format (1d each), specific numerical-precision tests around `mpmath` workprec contexts (1d each).

### Category C — Number theory specialty (261-350)

261. **C** — `pm.modular.character_table_dirichlet(N)` Dirichlet characters mod N · 3d
262. **C** — `pm.modular.cusps(N)` cusps of Γ_0(N) · 3d
263. **C** — `pm.modular.atkin_lehner` operators · 5d
264. **C** — `pm.modular.fricke_involution` · 3d
265. **C** — `pm.modular.eisenstein_series_basis(N, k)` · 5d
266. **C** — `pm.modular.cuspidal_basis(N, k)` · 5d
267. **C** — `pm.modular.newforms(N, k)` (Atkin-Lehner-Li newform decomposition) · 7d (2 phases)
268. **C** — `pm.modular.theta_series` from quadratic form · 5d
269. **C** — `pm.modular.eta_products` · 5d
270. **C** — `pm.modular.modular_polynomial` Phi_n(j(τ)) · 5d
271. **C** — `pm.modular.j_invariant` arbitrary precision · 3d
272. **C** — `pm.modular.weierstrass_pe` (℘-function) · 3d
273. **C** — `pm.elliptic_curves.isogeny_graph(label)` complete isogeny class · 5d
274. **C** — `pm.elliptic_curves.heegner_point(K, label)` · 7d (2 phases)
275. **C** — `pm.elliptic_curves.kolyvagin_class(K, label)` · 14d (3 phases)
276. **C** — `pm.elliptic_curves.mordell_weil_basis_certified` · 7d (2 phases)
277. **C** — `pm.elliptic_curves.cm_period_lattice` · 5d
278. **C** — `pm.elliptic_curves.formal_group(ainvs)` formal group law to depth N · 5d
279. **C** — `pm.elliptic_curves.tate_module(ainvs, l)` Tate module mod l · 7d
280. **C** — `pm.elliptic_curves.galois_image(ainvs, l)` mod-l Galois rep image · 7d (2 phases)
281. **C** — `pm.elliptic_curves.serre_open_image_check` · 7d (2 phases)
282. **C** — `pm.elliptic_curves.height_pairing_matrix` Néron-Tate · 3d
283. **C** — `pm.elliptic_curves.minimal_disc_factorization` · 3d
284. **C** — `pm.elliptic_curves.tate_curve(ainvs, p)` for split mult red · 5d
285. **C** — `pm.number_fields.ray_class_field(K, modulus)` · 7d (2 phases)
286. **C** — `pm.number_fields.unit_group(K)` Dirichlet unit theorem realization · 5d
287. **C** — `pm.number_fields.regulator(K)` analytic class number formula · 3d
288. **C** — `pm.number_fields.ideal_factorization(K, ideal)` · 3d
289. **C** — `pm.number_fields.local_field_data(K, p)` ramification, inertia · 5d
290. **C** — `pm.number_fields.signature_via_galois` (real/complex places) · 3d
291. **C** — `pm.number_fields.zeta_function(K, s)` Dedekind zeta · 5d
292. **C** — `pm.number_fields.chebotarev_density(K, conjugacy_class)` · 5d
293. **C** — `pm.padic.local_l_function(E, p)` · 14d (3 phases)
294. **C** — `pm.padic.iwasawa_main_conjecture_lhs(E, p)` · 21d (4 phases)
295. **C** — `pm.padic.iwasawa_main_conjecture_rhs(E, p)` · 21d (4 phases)
296. **C** — `pm.padic.coleman_integration` · 21d (4 phases)
297. **C** — `pm.padic.berkovich_space_minimal` · 28d (4 phases)
298. **C** — `pm.l_functions.generic_zeros_to_precision(L, n, prec)` · 7d (2 phases)
299. **C** — `pm.l_functions.functional_equation_check_strict` · 3d
300. **C** — `pm.l_functions.mean_value_estimates` · 7d
301–350. **C** — _bulk:_ 50 more NT-specific operations: cyclotomic field special functions (10), Galois module structure ops (10), Brauer group computations (10), height-on-PEL-Shimura-varieties (10), specific Frobenius computations (10).

### Category D — Algebraic geometry (351-420)

351. **D** — `pm.algebraic_geometry.affine_variety_dim(I, vars)` · 3d
352. **D** — `pm.algebraic_geometry.projective_variety_dim` · 3d
353. **D** — `pm.algebraic_geometry.degree(I, vars)` · 3d
354. **D** — `pm.algebraic_geometry.ample_cone(toric_data)` · 7d (2 phases)
355. **D** — `pm.algebraic_geometry.toric_variety_from_fan(fan)` · 7d (2 phases)
356. **D** — `pm.algebraic_geometry.kahler_cone(toric_data)` · 5d
357. **D** — `pm.algebraic_geometry.birational_map_simplification` · 14d (3 phases)
358. **D** — `pm.algebraic_geometry.resolution_of_singularities_blowups` · 14d (3 phases)
359. **D** — `pm.algebraic_geometry.intersection_theory_chow_ring` · 21d (4 phases)
360. **D** — `pm.algebraic_geometry.schubert_calculus_grassmannian` · 14d (3 phases)
361. **D** — `pm.algebraic_geometry.sheaf_cohomology_via_serre_duality` · 21d (4 phases)
362. **D** — `pm.algebraic_geometry.hodge_diamond(variety)` · 14d (3 phases)
363. **D** — `pm.algebraic_geometry.k3_lattice_invariants` · 14d (3 phases)
364. **D** — `pm.algebraic_geometry.calabi_yau_topology` · 21d (4 phases)
365. **D** — `pm.algebraic_geometry.tropical_basis` · 7d (2 phases)
366. **D** — `pm.algebraic_geometry.tropical_curve_genus` · 5d
367. **D** — `pm.algebraic_geometry.tropical_jacobian` · 7d (2 phases)
368. **D** — `pm.algebraic_geometry.bezout_number` · 3d
369. **D** — `pm.algebraic_geometry.solve_polynomial_system_homotopy` · 7d (2 phases)
370. **D** — `pm.algebraic_geometry.witness_set` (NAG) · 14d (3 phases)
371. **D** — `pm.algebraic_geometry.numerical_irreducible_decomposition` · 14d (3 phases)
372. **D** — `pm.algebraic_geometry.elliptic_fibration_classifier` · 14d (3 phases)
373. **D** — `pm.algebraic_geometry.weighted_projective_space_ops` · 7d (2 phases)
374. **D** — `pm.algebraic_geometry.del_pezzo_surface_data` · 7d (2 phases)
375. **D** — `pm.algebraic_geometry.fano_variety_database_query` · 7d (2 phases)
376. **D** — `pm.algebraic_statistics.maximum_likelihood_degree` · 14d (3 phases)
377. **D** — `pm.algebraic_statistics.implicit_likelihood_inference` · 14d (3 phases)
378. **D** — `pm.algebraic_statistics.bayesian_network_geometry` · 14d (3 phases)
379. **D** — `pm.commutative_algebra.depth_codepth(M, R)` · 5d
380. **D** — `pm.commutative_algebra.koszul_homology` · 7d (2 phases)
381–420. **D** — _bulk:_ 40 more AG ops: specific named varieties (10), specific resolution algorithms (10), tropical-and-toric specific ops (10), specific named curves & surfaces (10).

### Category E — Topology & geometry (421-500)

421. **E** — `pm.topology.knot_signature_arf` · 3d
422. **E** — `pm.topology.knot_genus_4ball_smooth_topological` · 7d (2 phases)
423. **E** — `pm.topology.concordance_invariants` (tau, epsilon, etc.) · 5d
424. **E** — `pm.topology.lens_space_recognizer` · 7d (2 phases)
425. **E** — `pm.topology.surgery_invariants` · 14d (3 phases)
426. **E** — `pm.topology.kauffman_bracket` · 5d
427. **E** — `pm.topology.knot_group(name)` (Wirtinger presentation) · 5d
428. **E** — `pm.topology.knot_group_invariants` · 7d (2 phases)
429. **E** — `pm.topology.bridge_index` · 5d
430. **E** — `pm.topology.tunnel_number` · 7d (2 phases)
431. **E** — `pm.topology.crossing_number_lower_bound` · 5d
432. **E** — `pm.topology.alexander_polynomial_multivariate` (links) · 7d (2 phases)
433. **E** — `pm.topology.heegaard_genus` · 7d (2 phases)
434. **E** — `pm.topology.dehn_filling_volume_curve` · 7d (2 phases)
435. **E** — `pm.topology.borromean_rings_invariants` · 3d
436. **E** — `pm.topology.brunnian_links` · 5d
437. **E** — `pm.topology.colored_jones_polynomial` · 14d (3 phases)
438. **E** — `pm.topology.witten_reshetikhin_turaev_invariants` · 21d (4 phases)
439. **E** — `pm.topology.quantum_invariants_at_root_unity` · 14d (3 phases)
440. **E** — `pm.topology.4manifold_kirby_diagram_ops` · 21d (4 phases)
441. **E** — `pm.topology.symplectic_basis_links` · 7d
442. **E** — `pm.topology.pretzel_knot_family_props` · 5d
443. **E** — `pm.topology.cable_satellite_construction` · 5d
444. **E** — `pm.topology.handle_decomposition_3manifold` · 14d (3 phases)
445. **E** — `pm.topology.gauge_theory.flat_connections_count` · 21d (4 phases)
446. **E** — `pm.topology.persistent_homology_streaming` · 14d (3 phases)
447. **E** — `pm.topology.persistent_landscape` · 5d
448. **E** — `pm.topology.bottleneck_distance` · 3d
449. **E** — `pm.topology.wasserstein_distance_diagrams` · 3d
450. **E** — `pm.topology.morse_theory_critical_points` · 7d (2 phases)
451–500. **E** — _bulk:_ 50 more topology ops: specific 3-manifold census queries (10), specific knot invariants (10), specific persistent homology variants (10), differential geometry (10), specific geometric structures (10).

### Category F — Combinatorics & graph theory (501-560)

501. **F** — `pm.combinatorics.partition_count_to_n(N)` (Hardy-Ramanujan) · 3d
502. **F** — `pm.combinatorics.young_tableaux_enumeration(λ)` · 5d
503. **F** — `pm.combinatorics.RSK_correspondence` · 5d
504. **F** — `pm.combinatorics.symmetric_functions_basis_change` · 7d (2 phases)
505. **F** — `pm.combinatorics.macdonald_polynomials` · 14d (3 phases)
506. **F** — `pm.combinatorics.q_analog_basics` · 5d
507. **F** — `pm.combinatorics.lattice_paths_enumeration` · 5d
508. **F** — `pm.combinatorics.dyck_paths_basics` · 3d
509. **F** — `pm.combinatorics.polya_enumeration` · 5d
510. **F** — `pm.combinatorics.necklace_enumeration` · 3d
511. **F** — `pm.combinatorics.designs.steiner_systems` · 7d (2 phases)
512. **F** — `pm.combinatorics.designs.balanced_incomplete_block` · 7d (2 phases)
513. **F** — `pm.combinatorics.designs.latin_squares` · 5d
514. **F** — `pm.combinatorics.designs.hadamard_matrices` · 5d
515. **F** — `pm.combinatorics.codes.error_correcting_basics` · 7d (2 phases)
516. **F** — `pm.combinatorics.codes.bch_decode` · 5d
517. **F** — `pm.graph.canonical_label` (or wait for nauty wrapper) · 3d
518. **F** — `pm.graph.aut_group_size` · 5d
519. **F** — `pm.graph.spectral_invariants` (Laplacian, adjacency) · 3d
520. **F** — `pm.graph.cospectral_test` · 3d
521. **F** — `pm.graph.tree_isomorphism_fast` · 3d
522. **F** — `pm.graph.matching_polynomial` · 5d
523. **F** — `pm.graph.tutte_polynomial` · 7d (2 phases)
524. **F** — `pm.graph.chromatic_polynomial` · 5d
525. **F** — `pm.graph.expansion_constants` · 5d
526. **F** — `pm.polytopes.from_vertices` · 3d
527. **F** — `pm.polytopes.from_inequalities` · 3d
528. **F** — `pm.polytopes.f_vector` · 3d
529. **F** — `pm.polytopes.h_vector` · 3d
530. **F** — `pm.polytopes.ehrhart_polynomial` · 7d (2 phases)
531–560. **F** — _bulk:_ 30 more combinatorics ops: specific named graph families (10), specific named designs (5), specific code constructions (5), specific polytope ops (10).

### Category G — Database expansion (561-630)

561. **G** — `pm.databases.lmfdb.iwasawa` (ec_iwasawa) · 3d
562. **G** — `pm.databases.lmfdb.padic` (ec_padic) · 3d
563. **G** — `pm.databases.lmfdb.classical_modular_forms.bbl` · 3d
564. **G** — `pm.databases.lmfdb.maass_forms` · 4d
565. **G** — `pm.databases.lmfdb.hilbert_modular_forms` · 4d
566. **G** — `pm.databases.lmfdb.bianchi_modular_forms` · 4d
567. **G** — `pm.databases.lmfdb.siegel_modular_forms` · 4d
568. **G** — `pm.databases.lmfdb.artin_representations` · 4d
569. **G** — `pm.databases.lmfdb.galois_groups` · 3d
570. **G** — `pm.databases.lmfdb.belyi_maps` · 4d
571. **G** — `pm.databases.lmfdb.modular_curves` · 4d
572. **G** — `pm.databases.lmfdb.dirichlet_characters` · 3d
573. **G** — `pm.databases.lmfdb.hecke_algebras` · 4d
574. **G** — `pm.databases.lmfdb.hecke_orbits` · 4d
575. **G** — `pm.databases.lmfdb.lattice_database` · 4d
576. **G** — `pm.databases.lmfdb.local_fields` · 4d
577. **G** — `pm.databases.lmfdb.full_text_search` (cross-table) · 7d (2 phases)
578. **G** — `pm.databases.lmfdb.sample_random_object` (uniform sampling) · 5d
579. **G** — `pm.databases.lmfdb.bulk_export(table, csv)` · 3d
580. **G** — `pm.databases.cremona_ec_csv_local` · 5d
581. **G** — `pm.databases.scott_finite_groups_local` · 4d
582. **G** — `pm.databases.macaulay2_examples_local` · 3d
583. **G** — `pm.databases.gap_examples_local` · 3d
584. **G** — `pm.databases.sage_doc_local_search` · 5d
585. **G** — `pm.databases.mathlib_local_search` · 7d (2 phases)
586. **G** — `pm.databases.dlmf_search` (Digital Library of Math Functions) · 5d
587. **G** — `pm.databases.kaggle_arxiv_metadata_local` · 3d
588. **G** — `pm.databases.tang_kim_pari_data` · 4d
589. **G** — `pm.databases.brendan_mckay_graph_census` · 7d (2 phases)
590. **G** — `pm.databases.weeks_3manifold_census` · 7d (2 phases)
591. **G** — `pm.databases.mossinghoff_extension_full` · 7d
592. **G** — `pm.databases.boyd_salem_database` · 4d
593. **G** — `pm.databases.lmfdb_change_log_subscriber` · 5d
594. **G** — `pm.databases.cross_join_engine` · 14d (3 phases)
595. **G** — `pm.databases.local_pg_dual_setup` (scientific + research DBs) · 5d
596. **G** — `pm.databases.knot_concordance_genus_complete` · 5d
597. **G** — `pm.databases.lmfdb_search_widget_python_helper` · 5d
598. **G** — `pm.databases.openml_math_subset` · 7d (2 phases)
599. **G** — `pm.databases.huggingface_math_corpora` · 7d (2 phases)
600. **G** — `pm.databases.physics_supplements_pubchem_inspirehep` · 7d (2 phases)
601–630. **G** — _bulk:_ 30 more database wrappers/integrations: specific journal article databases (5), specific census enumerations (5), specific named tables (10), specific cross-references (10).

### Category H — AI / ML integrations (631-690)

631. **H** — Local LLM tactic suggester (Llama-70B local) · 14d (3 phases)
632. **H** — RAG over Mathlib for retrieval-augmented proof search · 14d (3 phases)
633. **H** — Conjecture-from-LMFDB pattern detector · 14d (3 phases)
634. **H** — OEIS-mining pattern detector for cross-domain coincidences · 7d (2 phases)
635. **H** — Auto-generated MSC-tag classifier for paper triage · 7d (2 phases)
636. **H** — Embedding-based theorem search over Mathlib · 7d (2 phases)
637. **H** — Sequence-to-formula model trained on OEIS · 14d (3 phases)
638. **H** — Knot-invariant prediction model · 14d (3 phases)
639. **H** — Modular form coefficient predictor · 14d (3 phases)
640. **H** — Diophantine equation solver via neural search · 21d (4 phases)
641. **H** — `pm.ai.suggest_property` (given a function, propose property tests) · 7d (2 phases)
642. **H** — `pm.ai.suggest_proof_outline` (given a theorem stmt) · 14d (3 phases)
643. **H** — `pm.ai.summarize_paper` · 5d
644. **H** — `pm.ai.match_paper_to_open_problem` · 7d (2 phases)
645. **H** — `pm.ai.bsd_consistency_explainer` · 5d
646. **H** — `pm.ai.knot_database_anomaly_detector` · 7d (2 phases)
647. **H** — `pm.ai.spectral_anomaly_detector` (for Aporia void detection) · 7d (2 phases)
648. **H** — `pm.ai.identity_join_scorer` · 5d
649. **H** — `pm.ai.formal_to_informal_translator` (Lean → English) · 7d (2 phases)
650. **H** — `pm.ai.informal_to_formal_translator` (English → Lean) · 14d (3 phases)
651–690. **H** — _bulk:_ 40 more AI integrations: specific RAG pipelines (10), specific predictors per family (10), specific fine-tuned classifiers (10), specific natural-language tools (10).

### Category I — Proof assistants (691-740)

691. **I** — Lean tactic snippet library (curated useful tactics) · 7d (2 phases)
692. **I** — Coq integration (after Coq install) · 14d (3 phases)
693. **I** — Isabelle integration (after Isabelle install) · 14d (3 phases)
694. **I** — HOL Light integration · 14d (3 phases)
695. **I** — Cross-system proof porting helpers · 21d (4 phases)
696. **I** — `pm.proof.search_lemma(statement, provers=['Lean','Coq','Isabelle'])` · 14d (3 phases)
697. **I** — Tactic recommender by goal-class · 14d (3 phases)
698. **I** — Lean theorem statement from natural language · 14d (3 phases)
699. **I** — Proof obligations splitter · 7d (2 phases)
700. **I** — Counterexample finder via SMT (when statement is false) · 14d (3 phases)
701–740. **I** — _bulk:_ 40 more PA integrations: domain-specific lemma libraries (10), term-rewriting tactics (10), proof term simplification (10), proof certification + checking (10).

### Category J — Heavy native installs & wrappers (741-790)

741. **J** — Sage install via WSL2 + Python bridge · 7d (2 phases)
742. **J** — OSCAR.jl extended ops post-install · 7d (2 phases)
743. **J** — Hecke.jl wrapper specialized for NF research · 7d (2 phases)
744. **J** — Nemo.jl wrapper for fast NT primitives · 5d
745. **J** — fpylll Windows native build (or WSL2) · 5d
746. **J** — Bertini install + wrapper · 7d (2 phases)
747. **J** — PHCpack install + wrapper · 7d (2 phases)
748. **J** — HomotopyContinuation.jl integration via Julia · 5d
749. **J** — `tensorly` advanced tensor decomposition exposure · 5d
750. **J** — Z3 SMT-LIB parser integration · 4d
751–790. **J** — _bulk:_ 40 more native install/wrapper projects: per-tool wrappers for specific math software (10), specific install automation (10), specific cross-language bridges (10), specific subprocess gateways (10).

### Category K — Visualization & UI (791-840)

791. **K** — `pm.viz.knot_diagram` · 5d
792. **K** — `pm.viz.modular_form_q_expansion_plot` · 3d
793. **K** — `pm.viz.lattice_visualization` · 5d
794. **K** — `pm.viz.polytope_3d` · 5d
795. **K** — `pm.viz.graph_layout_force_directed` · 3d
796. **K** — `pm.viz.persistence_diagram` · 3d
797. **K** — `pm.viz.dynamical_orbit` · 3d
798. **K** — `pm.viz.mandelbrot_julia_renderer` · 3d
799. **K** — `pm.viz.character_table_renderer` · 3d
800. **K** — `pm.viz.commutative_diagram_to_tikz` · 5d
801. **K** — `pm.viz.dashboard_jupyter_widget_for_arsenal` · 5d
802. **K** — Notebook kernel autocomplete for `pm.*` · 4d
803. **K** — Neovim/VSCode language server hints · 7d (2 phases)
804. **K** — `pm.viz.ecdsa_signature_visual` · 3d
805. **K** — `pm.viz.zeta_zeros_render` · 3d
806. **K** — `pm.viz.hyperbolic_plane_tiling` · 5d
807–840. **K** — _bulk:_ 34 more viz ops: specific named visualizations per category (e.g., Newton polygon, j-line plots, Riemann surface render).

### Category L — Reverse-engineer paywalled (841-890)

841. **L** — Mathematica special-function: missing 30 in SymPy · 14d (3 phases)
842. **L** — Mathematica integration test set (compare success rate) · 7d (2 phases)
843. **L** — Maple ODE solver feature parity gap analysis · 7d (2 phases)
844. **L** — Magma `EllipticCurveDatabase` open replication · 14d (3 phases)
845. **L** — Magma `pAdicLfunction` open implementation (project #38 detailed) · 21d (4 phases)
846. **L** — Magma `IsogenyClass` open implementation · 14d (3 phases)
847. **L** — Magma `SelmerGroup(p)` for p > 2 · 21d (4 phases)
848. **L** — Magma `HypergeometricMotive` open implementation · 21d (4 phases)
849. **L** — Magma `GalRep` Galois rep ops · 21d (4 phases)
850. **L** — CPLEX-quality MIP improvements in SCIP/HiGHS bench-driven · 14d (3 phases)
851. **L** — Mathematica integration engine: Risch+ feature port · 21d (4 phases)
852. **L** — Mathematica `Reduce` polynomial system solver port · 14d (3 phases)
853. **L** — Mathematica `RecurrenceTable` fast solver port · 7d (2 phases)
854. **L** — Maple `dsolve` enhancement to SymPy · 14d (3 phases)
855. **L** — Mathematica `FunctionExpand` for hypergeometrics · 14d (3 phases)
856. **L** — Magma `RamanujanGraph` open ops · 14d (3 phases)
857. **L** — Magma `LSeries` open implementation · 21d (4 phases)
858. **L** — Mathematica `WignerD` open improvement · 7d (2 phases)
859. **L** — Mathematica `ClebschGordan` open improvement · 7d (2 phases)
860. **L** — Mathematica special-function arbitrary-precision · 14d (3 phases)
861–890. **L** — _bulk:_ 30 more rev-eng targets: specific named Magma package ports (10), specific named Mathematica functions (10), specific Maple toolboxes (5), specific MathSciNet review-tool ports (5).

### Category M — Documentation (891-940)

891. **M** — `prometheus_math` quickstart for new researchers · 3d
892. **M** — Recipe: BSD audit on a single curve · 1d
893. **M** — Recipe: BSD audit on 1000 curves · 2d
894. **M** — Recipe: knot trace field → number field match · 1d
895. **M** — Recipe: OEIS conjecture check from new sequence · 1d
896. **M** — Recipe: spectral gap Test on L-function family · 2d
897. **M** — Recipe: Galois group census across NF · 1d
898. **M** — Recipe: Mahler measure scan · 1d
899. **M** — Recipe: persistent homology of point cloud · 1d
900. **M** — Recipe: Lean theorem search · 2d
901. **M** — Recipe: SCIP optimization model · 1d
902. **M** — Recipe: Z3 SMT formula · 1d
903. **M** — Recipe: arXiv recent-paper monitor · 1d
904. **M** — Researcher onboarding tutorial: 30-minute Aporia → Techne path · 3d
905. **M** — Researcher onboarding tutorial: 30-minute Charon → Techne path · 3d
906. **M** — Researcher onboarding tutorial: 30-minute Ergon → Techne path · 3d
907. **M** — Module-level docstrings audit (every module has summary) · 3d
908. **M** — Failure-modes catalog (every doc has known failure section) · 5d
909. **M** — Migration guide: Magma user → prometheus_math · 5d
910. **M** — Migration guide: Mathematica user → prometheus_math · 5d
911. **M** — Migration guide: Sage user → prometheus_math · 5d
912. **M** — TUTORIAL.md mathematical research workflow walkthrough · 5d
913. **M** — TROUBLESHOOTING.md common errors and fixes · 3d
914. **M** — CONTRIBUTING.md (how to add a new tool) · 2d
915. **M** — ARCHITECTURE.md (the overall design) · 3d
916. **M** — Update CLAUDE.md with prometheus_math conventions · 2d
917. **M** — Glossary of mathematical terms used in the codebase · 3d
918. **M** — Index of every public function in prometheus_math · 1d
919. **M** — Sphinx docs site (auto-generated) · 5d
920. **M** — ReadTheDocs hosting · 2d
921–940. **M** — _bulk:_ 20 more docs: per-tool tutorials (10), per-recipe galleries (5), per-module deep dives (5).

### Category N — Research-specific active threads (941-1000)

941. **N** — F011 follow-up: rank-1 EC compression scan via pm.research.spectral_gaps · 3d
942. **N** — F011 follow-up: rank-2 EC compression scan · 3d
943. **N** — F011 follow-up: CM curves Sato-Tate stratification · 5d
944. **N** — F011 follow-up: real vs complex Dirichlet splits · 3d
945. **N** — F011 follow-up: Maass GL3 extension to other GL_n · 7d (2 phases)
946. **N** — F011 follow-up: Hilbert modular form spectral test · 7d
947. **N** — F011 paper: figure-2 export via pm.research.figures · 3d
948. **N** — F011 paper: bibliography compiler via pm.databases.zbmath · 2d
949. **N** — F011 paper: methods section auto-gen from journal entries · 5d
950. **N** — F011 paper: appendices (statistical tables) generator · 3d
951. **N** — V-CM-scaling extension: order-conductor × torsion 2D matrix · 5d
952. **N** — V-CM-scaling: unit-group cardinality predictor (SEED 3) · 3d
953. **N** — V-CM-scaling: 200K-sample power study · 4d
954. **N** — V-GAMMA-SIXTH-ROOTS: Q(√-3)-specific deep analysis · 7d (2 phases)
955. **N** — H15 ADE tower-termination paper-grade rerun · 5d
956. **N** — H15 large-cn (cn > 50) extension · 7d
957. **N** — H80 Lehmer for L-function leading terms test · 5d
958. **N** — H85 Chowla at g2 66K scale-up · 5d
959. **N** — H101-style Salem-knot revisit at higher crossing census · 7d (2 phases)
960. **N** — V3 Strategy Disagreement: phoneme_equations × island_bridges scan · 7d (2 phases)
961. **N** — V5 Sleeping Beauty sweep production grade · 14d (3 phases)
962. **N** — Mossinghoff-LMFDB gap analysis (deg-14 specifically) · 3d
963. **N** — Aporia identity-join: ec_CM↔NF systematic · 5d
964. **N** — Aporia identity-join: artin↔NF systematic · 5d
965. **N** — Aporia identity-join: mf↔NF systematic · 5d
966. **N** — Aporia identity-join: bianchi↔K-Bianchi · 5d
967. **N** — Charon BSD-1646 large-N replication · 5d
968. **N** — Charon Lehmer scan extension to deg 15-20 · 7d (2 phases)
969. **N** — Ergon mechanism (a) full closure regression · 5d
970. **N** — Ergon mechanism (c) CM/torsion saturation completion · 5d
971. **N** — Harmonia null battery v2 expanded · 7d
972. **N** — Harmonia tensor coordinate system upgrade · 7d (2 phases)
973. **N** — Harmonia phoneme equations extension · 14d (3 phases)
974. **N** — Mnemosyne data-pillar architecture v2 · 14d (3 phases)
975. **N** — Mnemosyne LMFDB freshness pipeline · 5d
976. **N** — Pronoia constitutional verification audit · 7d (2 phases)
977. **N** — Kairos PATTERN catalog auto-population · 14d (3 phases)
978. **N** — Stoa predictions register: closing accuracy report · 3d
979. **N** — Stoa adversarial review queue UI · 7d (2 phases)
980. **N** — Aporia void detection v2 expanded coverage · 7d (2 phases)
981. **N** — Aporia paradigm gap matrix v3 · 7d (2 phases)
982. **N** — Cross-domain bridge atlas (ec ↔ knot ↔ modular form ↔ Galois rep) · 14d (3 phases)
983. **N** — Pattern 30 systematic search across all tensor cells · 7d (2 phases)
984. **N** — Pattern 31 (controllability rank) implementation · 7d (2 phases)
985. **N** — Pattern catalog: NULL_CONSTRAINT_MISMATCH detector · 5d
986. **N** — Pattern catalog: KILL_UNDER_CONSTRAINED detector · 5d
987. **N** — Pattern catalog: PREDICTION_LEVEL_MISMATCH detector · 5d
988. **N** — Pattern catalog: SUBFAMILY check enforcement · 5d
989. **N** — Pattern catalog: SELECTION_BIAS detector · 5d
990. **N** — Apollo v2 primitive routing DAG runner · 7d (2 phases)
991. **N** — Apollo evolution: ablation gate generalization · 7d (2 phases)
992. **N** — Apollo: 6D NSGA-II improvements · 7d (2 phases)
993. **N** — Cartography: 22-dimension tensor refresh · 7d (2 phases)
994. **N** — Cartography: search strategy upgrade · 7d (2 phases)
995. **N** — Octant-attack v3 (Aporia adversarial review extension) · 7d
996. **N** — F011-extension: USp(4) full census of g2c · 7d (2 phases)
997. **N** — F011-extension: U-class spectral residual study · 7d (2 phases)
998. **N** — F011-extension: paper revisions cycle · 5d
999. **N** — Master research tensor v3.4 → v4.0 redesign · 21d (4 phases)
1000. **N** — Pretzel knot family arithmetic-vs-topology study · 14d (3 phases)

---

## Maintenance protocol

- **Promotion:** items move up when a new researcher ask raises priority,
  when a precondition is met (e.g., GAP install unblocks ATLAS work), or
  when a precursor lands.
- **Demotion:** items move down when active research direction shifts,
  when an external tool ships the same capability, or when a related
  project covers the use case.
- **Closure:** completed projects move to `techne/COMPLETED.md` (created
  when first item closes); a one-liner per project with commit ref.
- **Addition:** new candidates added when researchers ask, when CI
  finds a coverage gap, or when a new tool emerges (Tier 9).

This document is intended to never reach 0 open items. It's the
research forge's perpetual queue.

---

*Initial draft 2026-04-25 by Techne. Numbers are rankings, not
prescriptions — the team can pull any item out of order if research
direction warrants.*
