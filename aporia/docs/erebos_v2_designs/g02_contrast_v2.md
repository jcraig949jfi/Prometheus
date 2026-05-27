# G02 Contrast — v2 design

**Date:** 2026-05-27
**Status:** v2 design proposal, informed by DR `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/02_g02_contrast_v2_design_audit.md`
**Predecessor:** v1 at `charon/agents/erebos/generators/g02_contrast.py`; loaders at `charon/agents/stygian/loaders/composition_g02_lehmer_salem.py`, `composition_g02_lehmer_smyth.py`, `composition_g02_lehmer_degree_parity.py`; shared kernel at `charon/agents/stygian/loaders/_mahler_composition_helpers.py`.

## 1. v1 state — what we have

- **Plugin tier:** R5 (DNA P10: causal moderation hypothesis), Tier-S feasibility, spec phase 1.
- **Cognitive move:** Take a REJECTED or UNVERIFIED Stygian row; split its parent dataset by a binary categorical (Salem/non-Salem, CM/non-CM, even/odd degree); claim that per-group survival rate diverges by `|surv_A - surv_B| > 0.10`.
- **Expected kill_pattern:** `permutation_null` (observed divergence indistinguishable from random label shuffle at 95th percentile, N=1000 shuffles).
- **Composition loader status:** three live variants (Salem, Smyth-extremal, degree-parity) sharing `_mahler_composition_helpers.run_binary_split_permutation_null`. All three loaders use a single hardcoded threshold (`M_LEHMER = 1.1762808`), a single random shuffle per permutation draw, and report a single `(observed_divergence, null_p95)` pair per emission.
- **Live substrate finding:** ITER-4 (`pivot/erebos_substrate_finding_iter4_salem_class_moderation_2026-05-26.md`): at `M = 1.30` (not `M_LEHMER`), Salem-vs-non-Salem fires PROMOTED with `observed_divergence = 0.997` vs `null_p95 = 0.024` — a 41.7× null ratio. The v1 baseline-threshold test at `M_LEHMER` rejected with divergence ≈ 0.0001. ITER-18 (`pivot/erebos_substrate_finding_iter18_g17_salem_phase_transition_2026-05-26.md`) further showed via G17's threshold sweep that the effect has a sharp phase transition at `M = 1.26`. The v1 plugin's single-threshold posture is therefore actively masking real moderation structure unless the loader happens to be parameterised inside the effect's narrow band.

## 2. DR-surfaced critical objections (top 3)

Each objection is anchored to the DR's primary-source citations (deep-research-pro-preview-12-2025, interaction `v1_Chdnb0VXYXF6T0xxSFJqTWNQdEtQT3FBMBIXZ29FV2Fxek9McUhSak1jUHRLUE9xQTA`, elapsed 304s).

- **Objection 1 — Single-shuffle permutation null is miscalibrated under latent confounding.** v1 uniformly shuffles the binary label across the pooled Mahler-measure list, but Salem-class is correlated with polynomial degree (Salem polynomials concentrate at small degree), so an apparent "Salem effect" can be a "degree effect" relabeled. The DR's three replacement nulls — Westfall-Young max-T, conditional permutation in the Berrett-et-al. style, and degree-stratified permutation — each catch a distinct failure mode the v1 null misses (FWER inflation across thresholds, latent confounding, Simpson's paradox / hub-bias respectively).
  - Source: Berrett et al. *The conditional permutation test for independence while controlling for confounders* (DR cite 4, MS-CRT advancement); Niu / Lai & Guan inverse conditional permutations (DR cite 5); Queme et al. 2026 degree-stratified permutation on hub-enriched networks (DR cites 7, 8); French et al. 2024 within-cluster exchangeability (DR cite 6). DR §1(a)–(c).
  - Failure mode it predicts: any binary that is *correlated with degree* (Salem, palindromic, cyclotomic-factor) will trigger PROMOTED at the right threshold *whether or not* it carries information beyond what degree alone carries. The v1 PROMOTED for Salem at `M = 1.30` is currently uninterpretable on this axis — we do not know whether Salem is the moderator or merely a proxy for low degree.

- **Objection 2 — Hardcoded threshold is a multiple-peeking trap, and the right threshold operates on the moderate-deviation scale.** v1 fixes `threshold = M_LEHMER` at module-import time. ITER-4 lifted that threshold to `M = 1.30` by hand, and ITER-18 then swept 11 thresholds in `[1.20, 1.40]`. Each of those moves is informal multiple-testing. The DR shows that (i) the maximum divergence over a threshold sweep is biased upward if the sweep is not embedded in a max-T null, and (ii) the *Bayes-optimal* threshold for the relevant 0/1 loss family does not sit on the CLT scale `O(1)` or the Bonferroni scale `O(log p)` but on the moderate-deviation scale `sqrt(log n / n)` with critical constant `t_crit = sqrt(log(π n / 2))` (Datta, Polson, Sokolov, Zantedeschi 2026; Naeini et al. 2025 BOLT loss).
  - Source: Datta, Polson, Sokolov, Zantedeschi 2026 *Bayes-optimal sparse testing on moderate-deviation scale* (DR cite 10, formula 11); Naeini et al. 2025 *Bayes Optimal Learning Threshold (BOLT)* (DR cite 12); Gupta et al. 2025 stability-selection for multi-omics threshold sweeps (DR cite 9). DR §2.
  - Failure mode it predicts: v1 at `M_LEHMER` permanently misses the Salem effect (Type II at the canonical anchor). Any v1.x patched to `M = 1.30` will report inflated significance because the threshold was picked after seeing the data. Both modes are present in the live substrate today.

- **Objection 3 — Three sibling binaries promoted via "report the strongest" without FDR control.** The Salem, Smyth-extremal, and degree-parity loaders are three correlated tests run on the same catalog; the swarm currently has no rule against expanding the binary registry indefinitely (BL-C-001 list is open). Selecting the maximum-divergence binary across `K` correlated structural flags inflates the family error rate; Bonferroni is then over-draconian for correlated flags, but absence of any correction is mathematically invalid. The DR commits to Benjamini-Hochberg FDR with the 2024 Rousseeuw-prize-cited framework, optionally upgraded to Jin (2024/2025) Weighted Conformal Selection for finite-sample FDR control under positive dependence.
  - Source: Benjamini-Hochberg via 2024 Rousseeuw Prize citation (DR cite 13); Temple et al. 2025 *FWER-vs-FDR for correlated selection scans* (DR cite 14); Jin 2024/2025 *Weighted Conformal Selection for biomedical discovery* (DR cite 15). DR §3.
  - Failure mode it predicts: as the substrate adds more `composition_g02_lehmer_*.py` siblings (palindromic, reciprocal, trace-parity, height-tertile…), false-PROMOTED frequency under the current naïve null will rise with `K` and the substrate will accumulate a backlog of unfalsifiable Salem-cluster lookalikes.

- **Objection 4 (secondary, retained to keep v2 honest about discarded Fisher information) — Binary discretization throws away the continuous structure of every Mossinghoff feature.** v1 forces every moderator into a `bool`. The DR §5 walks through three Mossinghoff-native cases where the right test is a continuous covariate: maximum root modulus `ρ = |α_max|`, log Galois-group size `log|G|`, and coefficient `L_1` norm. Each is mathematically continuous and is artificially binarized in v1 by an unspecified human cutoff. The Galois case is especially load-bearing because `|G|` spans `[d, d!]` over orders of magnitude and a binary "Symmetric vs. Non-Symmetric" split collapses every intermediate algebraic symmetry — exactly the substrate's interesting middle.
  - Source: DR §5 (continuous-covariate alternatives) drawing on logistic-regression formulations and distance correlation as continuous-test primitives (DR cites 9, 14 reused as methodology anchors).
  - Failure mode it predicts: v2 limited to binaries will miss any moderation effect whose true shape is a smooth gradient in `ρ`, `log|G|`, or coefficient height. The Salem-class binary will keep firing because the cluster has a sharp boundary, but the lesson — "moderation in the Mossinghoff catalog is generically *positional* in a continuous M-dependent feature" — will be invisible. v2 therefore reserves §3.6 to a continuous-covariate sibling rather than absorbing the continuous case into the binary kernel.

## 3. v2 architectural changes

Concrete code-level changes. Each change references (a) what v1 module changes, (b) what new module is added, (c) what tests are updated or added.

### 3.1 Replace the single-threshold-single-shuffle kernel with a Westfall-Young max-T sweep

The headline architectural change. The shared kernel becomes threshold-aware end-to-end.

- **What changes:** `_mahler_composition_helpers.run_binary_split_permutation_null` is superseded by a new `run_binary_split_maxt_sweep` that accepts a threshold *grid* and returns a single global p-value derived from the max-T null.
- **New module:** `charon/agents/stygian/loaders/_maxt_permutation.py` housing:
  - `sweep_divergences(group_a, group_b, thresholds) -> list[float]` (observed divergence at each grid point).
  - `maxt_permutation_null(pooled, n_a, thresholds, n_perm, seed) -> list[float]` returning `T_max^(b) = max_m D_m^(b)` per shuffle, i.e., the joint max-T null distribution.
  - `maxt_global_p(observed_max, null_max_dist) -> float` returning `(#{b : null_max[b] >= observed_max} + 1) / (n_perm + 1)`.
- **New constants** (calibrated against the ITER-18 G17 sweep so v2 baseline matches the live finding):
  - `MAXT_THRESHOLD_GRID = numpy.arange(1.18, 1.40 + 1e-9, 0.01)` (23 points covering ITER-18's `[1.20, 1.40]` plus the Lehmer anchor).
  - `MAXT_N_PERM = 2000` (up from 1000; the max-T null's tail needs more draws than a single-threshold null at a given resolution).
  - `MAXT_GLOBAL_P_THRESHOLD = 0.01` (DR §3 BH-compatible alpha, with the per-binary p-value entering BH at §3.3).
- **Test updates:** the v1 `run_binary_split_permutation_null` callers (the three live loaders) are migrated to the new kernel; the existing synthetic-control tests under `tests/charon/stygian/loaders/test_g02_*_synthetic.py` are re-baselined to expect a sweep-and-global-p result block; new test `test_maxt_kernel_recovers_iter4_salem.py` asserts that on the live Mossinghoff catalog the Salem binary's `maxt_global_p < 0.01` AND the argmax threshold lands in `[1.26, 1.34]` (the ITER-18 effect-detectable band).
- **Calibration note (Westfall-Young step-down vs. single-step):** the kernel implements the *single-step* max-T variant (compare each observed `D_m` to the global max-null distribution) for v2.0 because single-step yields a valid FWER bound across the threshold sweep without the order-dependence bookkeeping of the step-down variant. The step-down (Westfall-Young 1993 / Hothorn-Bretz 2008 modernisation) is strictly more powerful when many thresholds are nominally significant — a v2.1 upgrade if the substrate sees many emissions where multiple grid points pass `p < 0.05` after the global gate fails. Both variants share the same null-generation code, so the upgrade cost is small.

### 3.2 Add conditional / degree-stratified permutation as a second null channel

The max-T sweep controls the threshold-sweep multiplicity but does not address Objection 1's latent-degree-confounding. v2 adds a separate degree-stratified shuffle and reports *both* p-values.

- **What changes:** `_maxt_permutation.py` gains `maxt_permutation_null_stratified(pooled, labels, thresholds, n_perm, seed, strata_keyfn)` that shuffles labels *within* each stratum (default: polynomial degree). The loader output adds `null_global_p_unstratified` and `null_global_p_degree_stratified` side-by-side.
- **New module:** none; folded into `_maxt_permutation.py`.
- **New constants:** `STRATIFY_BY = "degree"` as default strata key in the kernel; loaders may override (e.g., `STRATIFY_BY = ("degree", "is_reciprocal")` for richer stratification once we have more flags).
- **Test updates:** a new synthetic `test_maxt_stratified_kills_degree_confound.py` constructs a synthetic catalog where the binary is a perfect function of degree; unstratified null should report `p < 0.01` (false positive); stratified null should report `p > 0.5` (correctly nulled out). The test pins the gap that v1 cannot diagnose.

### 3.3 Multi-binary BH-FDR controller across sibling loaders

v2 promotes the multi-binary discipline from "three loaders silently running independently" to a single FDR-controlled emission family.

- **What changes:** a new module reads the per-binary `(binary_id, maxt_global_p)` outputs from the live G02 sibling family within one Stygian executor tick and applies Benjamini-Hochberg.
- **New module:** `charon/agents/stygian/loaders/_g02_fdr_controller.py` exposing:
  - `register_binary_pvalue(binary_id, p_value, raw_result_blob)`.
  - `flush_fdr_decisions(alpha=0.05) -> dict[binary_id, {"q_value": float, "decision": "PROMOTED" | "REJECTED_fdr"}]` implementing the BH step-up procedure: sort p-values, find largest `i` with `p_(i) <= (i/K) * alpha`, mark all `<= p_(i)` as significant.
  - `STYGIAN_HOOK = "post_tick"`: the executor calls `flush_fdr_decisions` after each tick that contained ≥ 2 G02 emissions; each G02 loader's intermediate verdict becomes finalized at flush time.
- **New constants:** `FDR_ALPHA = 0.05` (BH level); `FDR_MIN_BINARIES_FOR_FLUSH = 2` (below 2, no FDR correction is meaningful and the controller passes through the raw max-T p-value).
- **Test updates:** `test_g02_fdr_controller.py` covering (i) three synthetic binaries with `p = [0.001, 0.02, 0.04]` and `K = 3, alpha = 0.05` — BH should promote all three; (ii) ten binaries with one true and nine null at `p ≈ 0.05` — BH should promote only the true; (iii) single-binary tick — controller passes through unchanged.

### 3.4 Effect-size reporting (Cohen's h, Hedges' g) replaces raw observed-divergence as the substrate-grade metric

Significance is not magnitude. With `n_salem = 8513` the v1 catalogue can trip nominally-significant divergences on differences that are mathematically trivial. v2 emits an effect size alongside every p-value and gates PROMOTED on it.

- **What changes:** the kernel returns the verdict dict augmented with:
  - `cohens_h = 2 * arcsin(sqrt(surv_a)) - 2 * arcsin(sqrt(surv_b))` (DR §4(c) formula).
  - `hedges_g` on the underlying M-distribution shift between groups (continuous form).
- **New module:** none; helper functions land in `_maxt_permutation.py`.
- **New constants:** `MIN_COHENS_H_FOR_PROMOTE = 0.20` (the DR's "trivial" cutoff is `< 0.10`; we keep a margin for a clean PROMOTE).
- **Test updates:** synthetic where the divergence is significant but Cohen's h ≈ 0.05 must REJECT with the new `trivial_effect_size` kill_pattern.

### 3.5 Continuous-covariate sibling channel (gated, opt-in per emission)

The DR's §5 Fisher-information critique is not absorbed into the binary kernel (that would conflate two distinct statistical questions); v2 instead ships a *sibling* continuous-covariate route that the plugin can opt into when a parent row's `claim_payload` exposes a continuous moderator handle.

- **What changes:** the kernel gains a `run_continuous_covariate_test(group_values, continuous_covariate_values, threshold_grid)` returning `(spearman_rho, distance_correlation, max_t_pvalue)` from a logistic-regression-of-survival-on-covariate at each threshold, with the same max-T permutation discipline as §3.1.
- **New module:** none; folded into `_maxt_permutation.py` as `continuous_covariate_maxt`.
- **New constants:** `CONTINUOUS_COVARIATE_KINDS = {"max_root_modulus", "log_galois_size", "coeff_l1_norm", "house"}` registered alongside `_binary_handles.py`.
- **When it activates:** loader runs continuous-covariate route *in parallel* with the binary route when `composition_payload["covariate_handle"]` is present and resolvable; the FDR controller treats binary p-value and continuous p-value as two separate family members.
- **Test updates:** `test_continuous_covariate_recovers_smooth_gradient.py` constructs a synthetic catalog with a smooth `ρ`-dependent survival gradient and asserts (i) the binary route REJECTs (no sharp threshold), (ii) the continuous route PROMOTEs.

### 3.6 Plugin-side: emit the threshold grid and the binary handle, not just text

v1 packs the binary as English. v2 makes the binary machine-routable so the FDR controller can group siblings and the kernel can run the right grid.

- **What changes:** `g02_contrast.py::_build_claim` extends `composition_payload` with:
  - `binary_handle = {"kind": "salem_class" | "is_smyth_extremal" | "degree_parity" | ..., "args": {...}}` drawn from a shared registry.
  - `threshold_grid = list(MAXT_THRESHOLD_GRID)` so the kernel and the loader agree on the sweep shape.
  - `fdr_family_id = "g02_lehmer_v2"` so the FDR controller can group sibling emissions in a single tick.
- **New module:** `charon/agents/erebos/generators/_binary_handles.py` (mirrors `_predicate_handles.py` from G01 v2) mapping a Stygian row's `claim_payload` onto one of N supported binary kinds.
- **Test updates:** extend `tests/charon/erebos/generators/test_g02_contrast.py` to assert (i) every emitted claim has a resolvable `binary_handle`, (ii) the `threshold_grid` matches the kernel default, (iii) `fdr_family_id` is populated.

## 4. New kill_patterns introduced

| kill_pattern | When it fires | Substrate-grade meaning |
|---|---|---|
| `maxt_global_null` | `maxt_global_p > 0.01` after the threshold sweep is folded into a max-T null. | Replaces v1 `permutation_null`. Substrate learns: the binary's apparent divergence at *any* threshold in the grid is consistent with chance once the threshold-search penalty is paid. Strictly stronger than v1's single-threshold null. |
| `degree_stratified_null` | `maxt_global_p_degree_stratified > 0.01` while `maxt_global_p_unstratified <= 0.01`. | The binary tracks the *degree* covariate, not the catalog's structural geometry. Substrate learns: the apparent moderation is a degree-distribution proxy; record the binary as a "degree-aliased" feature and de-prioritise sibling binaries that share that profile. |
| `fdr_rejected` | The binary's raw max-T p-value is below the conventional 0.05 threshold but does not pass Benjamini-Hochberg at `alpha = 0.05` given the K sibling binaries in this tick. | Substrate learns: this binary was a tick-mate's victim — the family contained enough nominally-significant tests that BH demoted it. Honest false-discovery accounting; the binary stays in the registry but the substrate does not promote a finding from it. |
| `trivial_effect_size` | `maxt_global_p <= 0.01` AND `cohens_h < 0.20`. | The binary is statistically distinguishable but mathematically uninteresting — the survival-fraction shift is below substrate-meaningful magnitude. Substrate learns: large-N over-power, not a real moderation. |
| `phase_transition_localized` | PROMOTE-positive PLUS argmax threshold satisfies `len(thresholds_with_individual_p < 0.05) <= 3` out of the 23-point grid (i.e., the effect is concentrated in a narrow window). | New positive substrate signal. The effect is real and *localised in M* — directly analogous to ITER-18's `M = 1.26` phase transition. Substrate learns: the binary is moderating a sharp boundary in the catalog, not a global trend; this is the right shape for cluster-edge phenomena and should be cross-referenced against G10 (Boundary) and G17 (Causal-Intervention). |
| `binary_covariate_dominated` | Continuous-covariate channel (§3.5) PROMOTEs at `p < 0.001` while the binary channel is killed by `maxt_global_null` OR demoted to `cohens_h < 0.20`. | The moderator is *continuous*, not categorical; the binary is a degraded representation. Substrate learns: route this composition target to a continuous-covariate-native plugin family (and demote the binary's place in the registry). Operationalises the DR §5 Fisher-information critique. |

The v1 `permutation_null` kill_pattern is retained as a legacy alias that maps to `maxt_global_null` for backward compatibility with the historical ledger; the executor's kill_pattern_registry rewrites old emissions on read.

## 5. Cross-plugin interactions

How v2 changes G02's relationship with neighboring plugins.

- **vs G17 Causal-Intervention (both Salem-class testing — argue *complementary*, not redundant):** G17 and G02 both interrogate the Salem-vs-non-Salem partition on the Mossinghoff catalog, but they are doing categorically different work after v2. G02 v2 asks *"is the joint over-threshold-grid divergence between two pre-existing labels distinguishable from a max-T null, controlling for degree, in the presence of K sibling binaries?"* — it is a Pearl-Rung-1 *observational* discrimination question with proper multiplicity discipline. G17 already asks *"if I intervene on the labels (shuffle them), does the parent correlation survive?"* — it is a Pearl-Rung-2 *interventional* question on a fixed pre-promoted correlation. The ITER-18 G17 multi-threshold sweep (the live finding doc cited above) revealed a sharp phase transition at `M = 1.26`; G02 v2's max-T grid will reproduce that transition as a *positional* feature (the argmax of `D_m`) and the FDR controller will calibrate its *significance*, but G02 will never test the interventional severability — that is irreducibly G17's job. The two are complementary along the Rung 1 → Rung 2 axis: G02 v2 establishes *where* and *how strongly* the categorical moderates on the static catalog; G17 establishes *whether* the moderation survives label-shuffling. The substrate gains from having both because each instrument's PROMOTED-without-the-other is a substrate-grade ambiguity: G02-PROMOTED + G17-severable means "real moderation but causally vulnerable" (probably proxy); G02-PROMOTED + G17-survives means "real moderation, causally robust" (probably structural). Cross-plugin rule added to Hecate: emit a `g02_g17_disagreement` flag whenever a binary appears as PROMOTED in one and REJECTED in the other at the same threshold band.

- **vs G04 Survivor-Tightening (closely paired in the live discovery chain):** ITER-4's PROMOTED Salem finding came from a *chained* G02-then-G04 composition (the loader name was `composition_g02_g04_lehmer_tightened`). G02 v2's threshold-grid absorbs the G04 tightening *into the G02 kernel itself* — G04 is no longer needed as a manual "now pick a tighter M" downstream step for this family. The cross-plugin re-balance is therefore: G04 v2 (separate v2 design) should drop its Mahler-band tightening loader as redundant with G02 v2's grid, and refocus on tightening operations that are genuinely orthogonal (e.g., conjunctive tightening: M-threshold + degree-cap + reciprocal-flag jointly). This is the right kind of v2-to-v2 specialization: G02 v2 owns the *one-dimensional threshold sweep*; G04 v2 owns *multi-dimensional conjunctive tightening*.

- **vs G10 Boundary (boundary-of-cluster detection):** G10 detects the *position* of a cluster boundary in a 1-D feature via a heteroskedasticity / smoothness-ratio test (ITER-10 finding doc). G02 v2's `phase_transition_localized` kill_vector tag flags when a binary moderator's effect is concentrated at the cluster boundary — the same boundary G10 finds via its independent route. Two-way agreement (G10-located boundary at `M ≈ 1.26` AND G02 v2 argmax in `[1.26, 1.34]`) is a substrate-grade triangulation; disagreement (G10 says boundary at one M but G02 v2 argmax lands at a different M) is a substrate-grade ambiguity worth a finding doc. Add Hecate rule: when both plugins fire on the same binary family within 5 ticks, emit `g02_g10_boundary_co_location` (positive) or `g02_g10_boundary_disagreement` (anomaly) per the argmax comparison.

- **vs G09 Projection-Collapse (degree-collapse instrument):** G09's role is to ablate a feature (collapse a dimension) and check whether the parent claim still survives. G02 v2's `degree_stratified_null` channel is a *partial* G09 — it runs the binary test as if the degree dimension were collapsed, but only as a null channel, not as a primary verdict. The interaction is: any G02 v2 emission that fires `degree_stratified_null` is a *positive trigger* for a G09 emission on the same binary, with the ablation axis = "degree". The Hecate ledger should auto-route the failed-binary into G09's input queue (this is the kind of downstream routing the substrate gains from having sibling plugins that look at the same data through different statistical lenses).

## 6. Refinement loop trigger

Conditions under which v2 should become v3:

- **Trigger A:** After ≥ 50 verdicted G02 v2 emissions, the kill_pattern distribution shows ≥ 70 % `degree_stratified_null` outcomes. That would indicate the substrate's binary registry is dominated by degree-correlated features and the stratification gate is doing most of the work; v3 should add *automatic* degree-residualization (project the divergence onto the orthogonal complement of degree before testing) rather than rely on the post-hoc stratified null.
- **Trigger B:** A frontier review identifies a substrate-grade alternative to the max-T sweep + BH-FDR stack — most plausibly the *arithmetic-heuristic null* (Cohen-Lenstra / random-matrix; DR §6) for any G02 binary that lifts into number-field or modular-form territory. Once the substrate has BL-C-002 BSD or BL-C-005-style L-function loaders, v3 must replace the exchangeability-assumption null with a structural one. The DR is explicit that for deterministic arithmetic objects, exchangeability is "an illusion" and the permutation null is "algebraically invalid."
- **Trigger C:** Any single PROMOTE survives v2 with `cohens_h > 0.20` but is later contradicted by a higher-precision Mossinghoff catalog re-pull (the substrate's downstream verification at greater M-precision overturns the survival fractions). That proves the v2 kernel was operating at insufficient catalog precision and the M-values themselves need a precision audit before the kernel runs.
- **Trigger D:** ITER-18's `M = 1.26` phase transition is not recovered by v2's max-T grid (i.e., the argmax falls outside `[1.26, 1.34]`). That would mean the max-T kernel is suppressing the very effect ITER-4 + ITER-18 are anchored on, and v3 must re-examine whether the max-T null is over-correcting in the Salem-cluster's narrow-band regime.

- **Trigger E:** The continuous-covariate channel (§3.5) fires `binary_covariate_dominated` on > 30 % of binary-PROMOTED emissions across the first 50 verdicted tick-cycles. That would mean the binary registry is systematically the wrong abstraction for this catalog, and v3 must promote the continuous channel to the *primary* verdict route with the binary as a degraded secondary. This is the DR §5 critique becoming substrate-empirical rather than substrate-hypothetical.

## 7. Falsification route specification

The exact battery shape an Erebos v2 G02 emission flows through:

```
queue_payload  →  loader.applicable()  →  loader.build_battery_input()  →  verdict  →  fdr_controller.flush
```

- **`applicable(queue_payload)`:**
  - Return True iff ALL of:
    - `queue_payload["source"] == "erebos"`.
    - `queue_payload["erebos_plugin_id"] == "g02_contrast"`.
    - `queue_payload["composition_payload"]["binary_handle"]` resolves via `_binary_handles.RESOLVERS[handle["kind"]]` (no `UnsupportedBinary`).
    - At least one of the binary kinds is in the Mahler-context family (`{"salem_class", "is_smyth_extremal", "degree_parity", "palindromic", "reciprocal"}`).
  - Otherwise REJECT-NOT-APPLICABLE (distinct from a kill).

- **`build_battery_input(queue_payload)`:**
  - `entries = load_non_cyclotomic_mahler_entries()` (existing shared helper).
  - `predicate = _binary_handles.resolve(handle)` returning `entry → bool`.
  - `parts = partition_by_predicate(entries, predicate)` returning `(group_a, group_b)` lists of M-values plus a parallel `degree_labels` list per group (needed by §3.2 stratified null).
  - Return `BatteryInput(entries, group_a, group_b, degree_labels, threshold_grid=MAXT_THRESHOLD_GRID)`.

- **`verdict(battery_input) → Verdict`:** (decision order matters — each gate short-circuits)
  1. If `len(group_a) < 10` or `len(group_b) < 10` → REJECT-NOT-APPLICABLE (insufficient sample; this is *not* a kill).
  2. Run `sweep_divergences` over `threshold_grid`; record `D_m = |surv_a(m) - surv_b(m)|` and the argmax threshold `m*`.
  3. Run `maxt_permutation_null` (unstratified, N=2000) on the pooled list; compute `maxt_global_p_unstratified`.
  4. Run `maxt_permutation_null_stratified` keyed by polynomial degree (N=2000) and compute `maxt_global_p_degree_stratified`.
  5. Compute `cohens_h(m*)` at the argmax threshold.
  6. Tentative verdict:
     - If `maxt_global_p_unstratified > 0.01` → KILL `maxt_global_null`.
     - Elif `maxt_global_p_degree_stratified > 0.01` → KILL `degree_stratified_null`.
     - Elif `cohens_h(m*) < 0.20` → KILL `trivial_effect_size`.
     - Else → TENTATIVE PROMOTE, recording all numerics including the per-threshold p-values for §3.5 localisation check.
  7. Emit the tentative verdict and the raw `maxt_global_p_unstratified` to the FDR controller via `register_binary_pvalue(fdr_family_id, p_value, blob)`.
  8. After the executor's tick completes, `flush_fdr_decisions(alpha=0.05)` finalises each tentative PROMOTE. Binaries that fail BH at this stage are demoted to KILL `fdr_rejected`.
  9. For surviving PROMOTEs, count `n_individual_significant_thresholds`; if `<= 3` of 23, additionally tag `phase_transition_localized` in `kill_vector` (positive signal, not a kill).
  10. If `composition_payload["covariate_handle"]` is present, additionally run `continuous_covariate_maxt` and register its p-value with the FDR controller under the same `fdr_family_id` but a distinct `binary_id = f"{handle.kind}_continuous"`. The two channels are scored independently by BH; cross-channel agreement / disagreement is logged in `kill_vector["channel_consistency"]`. If continuous PROMOTEs at `p < 0.001` while binary is killed → emit `binary_covariate_dominated`.

The full result blob attached to the kill_ledger row is therefore: `{verdict, kill_pattern, maxt_global_p_unstratified, maxt_global_p_degree_stratified, cohens_h, hedges_g, argmax_threshold, n_individual_significant_thresholds, per_threshold_divergence, per_threshold_p, n_group_a, n_group_b, threshold_grid, binary_handle, fdr_family_id, fdr_q_value, fdr_decision, channel_consistency, ...}`. This is a strict superset of v1's emission and the Stygian executor's row schema needs an additive migration only (no removals).

## 8. Anti-gravitational-well check

The DR exhibits several conventional gradients even while flagging the v1 problems. v2 explicitly rejects:

- **Conventional framing 1: "Replace the permutation null with a parametric Bayesian model on every binary" (DR §2 Bayes-optimal threshold subsection).** This is the LLM-default escalation: collapse a hard non-parametric problem into a parametric one by importing a likelihood. *Substrate alternative taken:* keep the null *non-parametric* (max-T permutation + degree-stratification) and *only* import the Bayes-optimal scaling result as a *threshold-grid spacing prescription* — the moderate-deviation scale `sqrt(log n / n)` tells us how dense the threshold grid should be near interesting M-values, not what prior to put on the divergence. This preserves the substrate's empirical posture: priors are a future v3+ direction if and when the substrate has a generative model of the catalog that justifies one. Honors `feedback_anti_gravitational_well` (don't import a formalism just because it has prestige) and `feedback_narrative_resistance` (don't let a Bayesian narrative replace the simplest mechanism check).

- **Conventional framing 2: "Move G02 to L-function / modular-form territory using Cohen-Lenstra / random-matrix nulls" (DR §6).** The DR builds a rich argument that for deterministic arithmetic structures, exchangeability collapses and structural-random-model nulls are required. *Substrate alternative taken:* v2 stays in Mahler-spectrum territory where the permutation null is *empirically calibratable* against the live ITER-4 + ITER-18 anchors. Cohen-Lenstra-style nulls are parked for v3+ via Refinement Trigger B, gated on the substrate first acquiring a BL-C-002 BSD or modular-form loader that *needs* them. Moving the v2 kernel into arithmetic-geometry territory before the substrate has a concrete L-function loader is a category error — we would be replacing a calibrated tool with a theoretically-prestigious tool that has no anchor against which to validate.

- **Conventional framing 3: "Add hierarchical Bayesian shrinkage across sibling binaries via a single common prior on the divergence parameter."** Frontier-model output on this kind of multi-test problem reliably suggests a hierarchical model. *Substrate alternative taken:* hierarchical shrinkage would require committing to a parametric form for "the divergence" *across categorically different binaries* (Salem vs. Smyth vs. parity) — which forces an apples-to-oranges comparison the substrate has no theoretical justification for. BH-FDR is the *non-parametric* sibling of hierarchical shrinkage and remains the disciplined choice until the substrate has a generative model that justifies tying the binaries together. The rejection here is the same anti-narrative move as framing 1: don't import statistical sophistication that has no anchor; ship the simplest discipline that catches the known failure modes (max-T + BH) and let the substrate's accumulated evidence decide whether more sophistication is warranted.

## 9. Open questions for frontier review

3–5 specific questions where v2 leaves a design choice ambiguous and frontier critique would be load-bearing.

- **Q1.** The `MAXT_THRESHOLD_GRID` is uniformly spaced at `0.01` in M across `[1.18, 1.40]`. The DR's Bayes-optimal `sqrt(log n / n)` result suggests non-uniform spacing — denser near the catalog's high-density region (close to Lehmer) and sparser at the tails. Should v2 ship with the uniform grid and adapt in v3, or should the kernel pre-compute a Bayes-spaced grid from `len(entries)` at module-load? The former is simpler and more comparable across loaders; the latter is the DR's explicit recommendation.

- **Q2.** Degree-stratified permutation handles one obvious confound. What is the right *next* stratification axis — `is_reciprocal`, `palindromic_flag`, `degree_band` (instead of exact degree)? Each adds substrate cost and forces narrower per-stratum sample sizes. Frontier review should rank the likely confounders by their predicted impact on PROMOTED rates given the existing live finding distribution.

- **Q3.** The FDR controller flushes per tick, but the executor's tick boundary is an arbitrary scheduling artifact, not a statistical unit. Should we instead flush per *fdr_family_id* on a rolling window (e.g., the most recent 20 emissions in that family), so the BH correction tracks the actual binary registry size rather than transient tick co-occurrence? The simpler tick-flush is easier to reason about; the rolling-window version is closer to what BH actually controls.

- **Q4.** `cohens_h < 0.20` is the trivial-effect-size cutoff. For Mahler-spectrum survival fractions, `0.20` corresponds to roughly a 10-percentage-point gap between the two groups' survival rates near `surv = 0.5` — already a sizable substantive effect. The ITER-4 Salem PROMOTED has `cohens_h ≈ 2.6` (massive). Is the cutoff too lenient and we should require `h >= 0.50` to call something substrate-grade? Frontier review should advise based on what magnitudes the substrate considers worth a finding doc.

- **Q5.** v2 is opinionated that G04 v2 should *drop* the Mahler-band tightening role (§5). If the G04 v2 author disagrees and ships an overlapping kernel anyway, what is the right disambiguation rule — purely architectural (G02 owns one-dim grid, G04 owns multi-dim conjunction) or empirical (whichever produces higher-resolution PROMOTEs on a shared synthetic battery)? Frontier review should call out whether the architectural split is durable or whether v2 is over-claiming territory.

- **Q6.** v2's `phase_transition_localized` tag is a *positive* substrate signal that fires alongside a PROMOTE, not a kill. Should the substrate treat this differently from a plain PROMOTE in downstream Hecate cross-gen analysis — e.g., does a localized phase transition deserve its own ledger column, its own kill_ledger sub-index, or its own finding-doc auto-trigger? Frontier review should call out whether this kind of "positive secondary signal" needs first-class infrastructure or whether it can live as a tag on the existing PROMOTE row.

- **Q7.** The legacy alias mapping `permutation_null → maxt_global_null` (§4 footer) preserves backward compatibility but also semantically *upgrades* historical rows that were never actually evaluated under a max-T null. Is the right discipline to (a) rewrite the historical kill_pattern on read with a flag indicating it was a v1 emission interpreted under v2 semantics, or (b) leave the historical rows untouched and gate the alias behind a per-query opt-in? Decision affects how the substrate counts kill_pattern frequencies during the v1 → v2 transition.

## 10. Implementation budget

Rough estimate in iterations (~1 iteration ≈ one Erebos working cycle, matching the substrate's existing iteration scale).

- v2 plugin update (`g02_contrast.py` payload extensions + `_binary_handles.py` registry): **1 iteration**.
- v2 kernel module (`_maxt_permutation.py` with max-T sweep, stratified null, effect-size helpers): **2 iterations** (one to scaffold + wire, one to calibrate against ITER-4 and ITER-18 anchors and confirm the kernel reproduces both findings).
- v2 FDR controller (`_g02_fdr_controller.py` + executor hook): **1 iteration** (small module but the executor wiring needs care to avoid double-flushing).
- Migration of the three live loaders (`composition_g02_lehmer_salem.py`, `*_smyth.py`, `*_degree_parity.py`) onto the new kernel + handle registry: **1 iteration**.
- Synthetic-control tests (max-T kernel, stratified null kills degree-confound, FDR controller across K binaries, trivial-effect-size synthetic, ITER-4 + ITER-18 anchor regression): **1 iteration**.
- Substrate finding doc (refines or supersedes ITER-4 / ITER-18 if v2 recovers them with stronger discipline): **1 iteration**, deferred until after first live v2 run on the Mossinghoff catalog.

**Total: 6–7 iterations** to ship v2 to substrate-live and verdicted, plus 1 follow-up iteration for the finding doc. Lower bound assumes the three loader migrations land cleanly under the new kernel; upper bound budgets for one round of threshold-grid recalibration if the kernel under- or over-detects the ITER-18 phase transition on first wire-up.

**Known risks (each is a v3-trigger candidate):**

- The max-T null with `N_PERM = 2000` and a 23-point grid costs `~46K` divergence computations per emission; if the Stygian executor's tick budget cannot absorb that for the larger sibling binary families being added in ITER-21+, v2 must either down-sample the grid or memoise the null (the null depends only on the pooled M-values plus `n_a`, both of which are stable across same-handle emissions in a given tick — a hash-keyed cache should cut cost by ≥ 10×).
- BH-FDR across tick co-occurrences is not a true family — different binaries genuinely belong to different scientific families, and the substrate currently has no way to declare those. v2 papers over this by using `fdr_family_id` as a string namespace; v3 will need a registered family taxonomy to avoid spurious cross-family demotions.
- The continuous-covariate channel (§3.5) doubles the loader's complexity and is the most likely source of bugs at the first wire-up. If implementation budget runs over, the continuous channel is the cleanest thing to gate behind a feature flag and ship in v2.1 rather than v2.0 — but the binary-only v2.0 must still emit the *placeholder* `binary_covariate_dominated` field as `null` so that the kill_ledger row schema is stable across the v2.0 → v2.1 transition.

**Ledger migration plan (v1 → v2):**

1. v1 rows are immutable; the migration is read-side only.
2. At read time, any v1 row with `kill_pattern == "permutation_null"` is annotated with `kill_pattern_v2_alias = "maxt_global_null"` and a `v1_legacy = True` flag — the substrate query layer reports both columns so historical statistics remain interpretable under v1 *and* v2 semantics.
3. A one-time backfill pass re-runs every v1 G02 emission through the v2 kernel (max-T + stratified + FDR) on the *current* Mossinghoff catalog, emitting parallel `_v2_replay` rows. This is `~3 hours` of compute on a typical executor (≈ 300 historical emissions × 30 s/emission).
4. The v1 → v2 replay diff (how many v1 PROMOTEDs survive v2 discipline, how many v1 REJECTEDs flip to PROMOTE under the wider grid) becomes a *substrate finding doc* in its own right — it is direct empirical evidence on how much the v1 statistical discipline was masking or fabricating moderation effects.
5. The replay diff is also the cleanest possible v2 calibration anchor: if v2 flips ITER-4's PROMOTED to a REJECTED, or fails to recover ITER-18's phase transition, the kernel needs another round of tuning *before* v2 goes live on new emissions. The replay is therefore both retrospective audit and prospective gate.
