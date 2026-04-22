# Generator #9 — Cross-Disciplinary Transplants (Information-Theoretic Projections)

**Status:** Tier 2 in pipeline doc, **promoted to Tier 1 execution (infra is small)**. Per James's 2026-04-20 conductor decision.
**Role:** Producer — imports three domain-agnostic projections from information theory, statistical physics, and algorithmic complexity.
**Qualification:** Harmonia session; familiarity with `symbols/VERSIONING.md`, `harmonia/memory/coordinate_system_catalog.md`, and the tensor schema.
**Estimated effort:** 2–4 ticks for first implementation; ongoing as new disciplines imported.

**Note on v1.0 re-scope:** the prior v0.1 DRAFT (vocabulary imports across four disciplines + hypothesis transplanter + Pattern 5 gate) was large-infra and blocked on three dependency gaps. v1.0 narrows the first-pass scope to **three concrete information-theoretic scorers** that ship as immediately-usable projections without requiring vocabulary manifests or the Pattern 5 hypothesis pipeline. The broader discipline-transplant framework from v0.1 remains a future direction; v1.0 gets measurable signal on the substrate in days, not weeks.

---

## Why this exists

Every projection currently on the substrate was authored from inside number theory. That means the coordinate system we use to see structure is the one the field already uses to see structure — which is exactly the coordinate system that failed to see whatever we are trying to find. MPA is construction, not discovery (`feedback_mpa_is_construction.md`): we have to build coordinates where structure becomes detectable, and the raw material for those coordinates lives in other disciplines.

Information theory, statistical physics, and algorithmic complexity all ship ready-made **projections that do not know about elliptic curves** and therefore cannot be accused of tautology with number-theoretic definitions. If any of them lights up non-trivially on our data, it is candidate structure — the projection was not built to find it.

This generator imports three such projections as v1:

1. **K̂ (Kolmogorov compressibility proxy)** — the algorithmic-complexity floor of each object's canonical fingerprint.
2. **Critical exponent** — the scaling-law exponent of any quantity against conductor (or any other scale axis), borrowed from critical-phenomena physics.
3. **Channel capacity** — the mutual information each projection P carries about a verdict, ranking the 42 existing projections by bits.

MDL and RG-flow are **Tier 2 deferred** within this same spec; free-energy is **explicitly deferred pending MDL**.

---

## Infrastructure to build

All three scorers ship in `harmonia/transplants/information_theoretic.py`. Each is a pure computation symbol per `long_term_architecture.md §2.1`, versioned per `VERSIONING.md`.

### Scorer 1 — `KOLMOGOROV_HAT@v1` (K̂ via zstd)

**Purpose:** a coarse, domain-agnostic proxy for Kolmogorov complexity. If two objects have very different K̂ under the same canonical fingerprint, they sit in different algorithmic-complexity regimes.

**Operator symbol:** `KOLMOGOROV_HAT@v1`
**Input signature:** `(object_id: str, fingerprint_spec: str = "a_p_sequence[p<=B]", B: int = 1000, zstd_level: int = 19)`
**Output shape:**

```json
{
  "object_id": "<ec_label>",
  "fingerprint_spec": "a_p_sequence[p<=1000]",
  "raw_len": <int bytes>,
  "compressed_len": <int bytes>,
  "ratio": <float in (0, 1]>,
  "zstd_level": 19,
  "scorer": "KOLMOGOROV_HAT@v1"
}
```

**Process:**

1. For each object (EC for first pass), canonicalize a fingerprint. The a_p sequence for p ≤ B is the natural choice for EC — it is the standard "Dirichlet coefficient" fingerprint, already domain-canonical, and it compresses meaningfully.
2. Serialize to a deterministic byte representation (fixed-width big-endian signed ints, no padding, no separators).
3. Compress with `zstd` at a pinned level (v1: level 19).
4. Record `ratio = len(compressed) / len(raw)`.

**First pass:** `Q_EC_R0_D5@v1` sample. Plot the ratio distribution; compare across conductor deciles. Claim-class at first pass: **Class 1 / 2** (finite-sample distributional claim).

### Scorer 2 — `CRITICAL_EXPONENT@v1` (scaling-law fit)

**Purpose:** borrow the critical-phenomena ansatz `f(N) = f_inf + C * N^(-alpha)` as a universal shape-fingerprint for any F-ID's conductor-dependence. Multiple F-IDs with matching `alpha` constitute a **universality class** — an invariance of a very different flavor from the ones we currently record.

**Operator symbol:** `CRITICAL_EXPONENT@v1`
**Input signature:** `(f_id: str, measurement_series: List[Tuple[int, float]], stratifier: str = "conductor_decile", ansatz: str = "power_law_plus_offset")`
**Output shape:**

```json
{
  "f_id": "F011",
  "ansatz": "f(N) = f_inf + C * N^(-alpha)",
  "stratifier": "conductor_decile",
  "n_strata": 10,
  "alpha": <float>,
  "alpha_sigma": <float>,
  "f_inf": <float>,
  "C": <float>,
  "fit_r2": <float>,
  "n_points": <int>,
  "scorer": "CRITICAL_EXPONENT@v1"
}
```

**Process:**

1. Stratify the dataset by conductor decile (or other scale axis declared in the stratifier).
2. For each stratum, compute the F-ID's measurement at that stratum's `N` (decile midpoint).
3. Nonlinear least-squares fit to the ansatz. Report `alpha ± sigma` via the covariance matrix.
4. Record `fit_r2` for diagnostic; low `fit_r2` (< 0.7) flags the ansatz as wrong for this F-ID (Pattern 25 warning).

**First pass:** F011, F015, F041a, F013. Any clustering in `alpha` across these four is the headline result. Alpha agreement within sigma across ≥ 2 F-IDs is a **universality-class candidate**, NOT a confirmation — Pattern 25 robustness under alternate ansatz is mandatory before any promotion.

### Scorer 3 — `CHANNEL_CAPACITY@v1` (mutual information per projection)

**Purpose:** each of our 42 projections is a lens; channel capacity measures **how many bits about the verdict that lens actually carries**. Projections with high capacity are the load-bearing ones. Projections with ≈ 0 capacity are unused — either dead lenses or lenses we haven't built verdicts for yet. Either way, the ranking surfaces what to prune and what to audit.

**Operator symbol:** `CHANNEL_CAPACITY@v1`
**Input signature:** `(p_id: str, dataset: str, verdict_spec: str, n_bins: int = 16, bin_strategy: str = "equal_quantile")`
**Output shape:**

```json
{
  "p_id": "P020",
  "dataset": "Q_EC_R0_D5@v1",
  "verdict_spec": "<verdict identifier>",
  "n_bins": 16,
  "bin_strategy": "equal_quantile",
  "mutual_information_bits": <float>,
  "mi_sigma": <float>,
  "n_objects": <int>,
  "scorer": "CHANNEL_CAPACITY@v1"
}
```

**Process:**

1. Pin a dataset (v1: `Q_EC_R0_D5@v1`).
2. For each projection P, extract the feature vector on every object.
3. Bin features and verdict via equal-quantile binning (v1: 16 bins each).
4. Compute `I(features; verdict) = H(verdict) - H(verdict | features)` in bits.
5. Bootstrap `mi_sigma` (1000 resamples).
6. Rank all 42 projections.

**First pass:** all 42 projections on `Q_EC_R0_D5@v1`. The ranking is the deliverable.

### Tier 2 deferred (within this spec)

- **MDL (minimum description length)** — formal two-part code length per projection. Deferred: needs a model-class declaration per P.
- **RG flow (renormalization-group)** — how each projection transforms under coarse-graining of conductor bins. Deferred: needs a coarse-graining operator.
- **Free energy** — **explicitly deferred pending MDL**. Cannot define a partition function without first pinning the MDL code.

---

## Process

1. Implement the three scorers as pure computation symbols in `harmonia/transplants/information_theoretic.py`.
2. Promote each to v1 per `VERSIONING.md`. Each gets a pinned seed (where stochastic), a pinned zstd level, a pinned binning strategy.
3. Reserve three new P-IDs via `reserve_p_id` — one per scorer — and register them in `harmonia/memory/coordinate_system_catalog.md`.
4. Run the three first-pass measurements declared above. Pipe each through the Pattern 30 gate (manual until `gen_06` auto-sweep lands per `project_harmonia_sessionA_20260420`); each scorer's output is a verdict that inherits full sweep discipline.
5. Append results to `harmonia/memory/transplant_results_log.md` with first-pass analysis.

---

## Outputs

- `harmonia/transplants/information_theoretic.py` — three scorer functions, each versioned, each with its pinned params.
- Three new P-IDs registered in `harmonia/memory/coordinate_system_catalog.md`.
- First K̂ pass on `Q_EC_R0_D5@v1` sample; ratio distribution plotted.
- First critical-exponent fit on F011, F015, F041a, F013 with `alpha ± sigma`.
- First channel-capacity audit ranking all 42 projections in bits.
- `harmonia/memory/transplant_results_log.md` — first-pass analysis + interpretation caveats.
- Promotion MDs for `KOLMOGOROV_HAT@v1`, `CRITICAL_EXPONENT@v1`, `CHANNEL_CAPACITY@v1`.

---

## Epistemic discipline

1. **K̂ via zstd is a coarse proxy; not true Kolmogorov complexity.** Zstd is a particular compressor with a particular dictionary and window size; a different compressor would give different ratios. The K̂ value is only meaningful **comparatively across objects under the same scorer version**, not as an absolute algorithmic complexity. Any claim phrased as "algorithmic-complexity finding" is overreach at v1.
2. **Channel capacity requires careful binning to avoid overfitting mutual information.** Equal-quantile binning with 16 bins is the v1 default; any claim must also report the MI under a halved and doubled binning to confirm it is not a binning artifact. Small-n strata (< 100 per bin) flag `FLAG_INCONCLUSIVE`.
3. **Critical-exponent extraction is under-constrained without fixing an ansatz (Pattern 25).** The v1 ansatz `f(N) = f_inf + C*N^(-alpha)` is one choice; a `log`-correction ansatz or a stretched-exponential ansatz would fit a different `alpha`. Low `fit_r2` is a Pattern 25 trigger; any cluster of alphas must be robustness-tested against an alternate ansatz before being called a universality class.
4. **None of these are tensor findings on their own.** They are **projections**, and every projection has to survive the full battery (null-family, Pattern 30 gate, stratified audit, Pattern 21 discordance) before being promoted to a tier. First-pass numbers are exploratory — `POSSIBLE` at best.
5. **Cross-disciplinary doesn't mean cross-validated.** A projection imported from physics / CS / stats is only domain-agnostic in provenance; its behavior on our data still needs the same epistemic discipline as any native projection. Pattern 5 (known bridges) still applies: e.g., zeta-function compressibility has literature; the gen_09 author must scan for prior art before claiming novelty on any pattern that lights up.

---

## Acceptance criteria

- [ ] `harmonia/transplants/information_theoretic.py` shipped with three scorer functions at v1.
- [ ] First K̂ pass on `Q_EC_R0_D5@v1` EC sample; ratio distribution plotted.
- [ ] First critical-exponent fit on F011, F015, F041a, F013 with `alpha ± sigma`.
- [ ] First channel-capacity audit ranking all 42 projections in bits.
- [ ] Three new P-IDs reserved via `reserve_p_id` and added to `coordinate_system_catalog.md`.
- [ ] `harmonia/memory/transplant_results_log.md` with first-pass analysis.
- [ ] Each scorer's first-pass output passes Pattern 30 gate (manual until `gen_06` auto-sweep lands).
- [ ] Commit cites this spec.

---

## Composes with

- **#6 pattern auto-sweeps** — all three scorers inherit the Pattern 30 gate; each scorer's output is a verdict that the auto-sweep will evaluate for algebraic coupling. Auto-sweep applies the moment `gen_06` ships; until then manual Pattern 30 review per `feedback_battery_calibration.md` and the sessionA 2026-04-20 handoff directive.
- **#2 null-family** — each scorer is itself a verdict that can be null-family-tested. K̂ ratio under label permutation, MI under stratified bootstrap, alpha under a parametric null — each becomes a `SIGNATURE@v2` entry once `gen_02` runners are available.
- **#10 composition enumeration** — critical-exponent × projection composes: any P with a well-defined scale-dependence can be fed to `CRITICAL_EXPONENT@v1` to produce a `(P, alpha)` pair. The composition catalog enumerates these, generating O(42) new paired measurements on first-pass.
- **#1 Map-Elites** (when live) — channel capacity becomes the occupancy score for projection cells. High-capacity cells are worth deeper audit; zero-capacity cells are audit-candidates for dead-lens removal.
- **External review** — these three scorers are exactly the kind of outside-the-field audits external reviewers keep asking for. Their outputs are review-facing.

---

## Claim instructions (paste-ready)

> Claim `gen_09_cross_disciplinary_transplants_seed` from Agora. Implement `KOLMOGOROV_HAT@v1`, `CRITICAL_EXPONENT@v1`, `CHANNEL_CAPACITY@v1` in `harmonia/transplants/information_theoretic.py` per `docs/prompts/gen_09_cross_disciplinary_transplants.md`. Run the three first-pass measurements. Reserve three P-IDs and register them in `coordinate_system_catalog.md`. Commit `transplant_results_log.md`. Post `WORK_COMPLETE` with ratio-distribution summary, alpha table, and top-5 / bottom-5 channel-capacity projections.

---

## Version

- **v1.0** — 2026-04-20 — first shippable spec; re-scoped from v0.1 DRAFT. Tier 2 in pipeline doc, promoted to Tier 1 execution per James's 2026-04-20 conductor decision (infra is small). Three information-theoretic scorers in scope; MDL and RG-flow deferred; free energy explicitly deferred pending MDL. Broader vocabulary-import / hypothesis-transplant framework from v0.1 DRAFT retained as future direction, not v1.0 deliverable.
- **v0.1 DRAFT** — 2026-04-20 — initial ambitious spec (vocabulary imports across four disciplines + hypothesis transplanter + Pattern 5 gate). Superseded by v1.0 for first-pass execution; retained in git history.
