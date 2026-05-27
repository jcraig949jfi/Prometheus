# Erebos v3 Amendment — DR Synthesis

**Date:** 2026-05-27
**Author:** Charon
**Status:** Amendment to `pivot/erebos_v3_synthesis_2026-05-27.md`. Integrates cross-cutting findings from the 22-plugin Gemini Deep Research pass (`aporia/docs/deep_research_reports/erebos_v2_2026-05-27/`) and the five batch-syntheses (`aporia/docs/erebos_v3_dr_synthesis_batch{1..5}_*.md`).
**Reading order:** v3 synthesis first (architecture), then this amendment (per-plugin specifics that survive architectural redesign).

---

## 0. What this amendment adds to v3

v3 was synthesized from four frontier-model critiques of the v1 whitepaper. It identified 8 architectural themes and committed to 10 architectural changes + Sprint-1 ablation + 5 kill conditions.

The 22 plugin-specific DR outputs were already in hand when v3 was drafted but had not been read across-the-board. This amendment closes that gap. The DR convergence:

- **Confirms** five of v3's commitments at the per-plugin level (the DRs independently demand what v3 already commits to architecturally).
- **Sharpens** three v3 commitments with specific code-level demands the DRs raise.
- **Adds** four new architectural primitives that v3 did not anticipate. These are MANDATORY for the Sprint-1 ablation harness to be meaningful — they are the discipline layer that prevents loader implementations from defaulting back to the v1 anti-patterns the DRs all identified.
- **Re-prioritizes** the v3 §9 roadmap: two items move forward, two move back.

The amendment does NOT supersede v3 §6 kill conditions or §5 Sprint-1 ablation experiments. Those stand as-stated.

---

## 1. The DR meta-convergence — five cross-plugin anti-patterns

The 22 DRs were independently produced, one per plugin, but they converge on five anti-patterns that recur across the substrate. The convergence is too uniform to be reviewer noise — these are real architectural weaknesses inherited by every plugin that copied the v1 substrate's coding conventions.

### Anti-Pattern A — Arbitrary-scalar selection

**Where it appears:** G06 (alphabetical absentee from KP_UNIVERSE), G09 (random 50% Lehmer ablation), G10 (max/mean of first-diffs as smoothness ratio), G11 (degree_minimum flag as if it were the true argmin), G16 (10× as the adversarial multiplier), G18 (modal kill_pattern as predicted region).

**The pattern:** the v1 loader picks the first-lexicographic, random, or aggregate-scalar candidate from a structured mathematical space and treats that arbitrary choice as if it were geometrically meaningful.

**The fix the DRs converge on:** replace arbitrary scalars with distance-minimizing or posterior-maximizing or attribution-ranked selection that respects the underlying geometry.
- G06: Wasserstein-bottleneck on persistence diagrams (not alphabetical).
- G09: Shapley attribution per coordinate (not random ablation).
- G10: Bayesian online change-point posterior (not max/mean ratio).
- G11: directly computed argmin with cyclotomic-extension filter (not flag-based).
- G16: empirical-CDF percentile push (not 10× constant).
- G18: kill-density Voronoi cells (not modal kill_pattern).

**v3 integration:** the v3 §4.4 kill_pattern semantics layer is necessary but not sufficient. Selection discipline needs its own substrate-level guard. See §3.1 below (new architectural primitive).

### Anti-Pattern B — Local geometry ignored at the threshold layer

**Where it appears:** G02 (M=M_Lehmer threshold; effect actually lives at M=1.30), G03 (EPSILON_BAND=0.05 hardcoded), G04 (band [1.30, 1.50] hardcoded), G10 (SMOOTH_THRESHOLD=3.0 production-sweep-coupled), G11 (CHI2_THRESHOLD=10 or 50 hardcoded), G23 (DECAY_SLOPE_TOLERANCE=0.5).

**The pattern:** every threshold in the substrate is a hand-picked constant that worked for one calibration run, not a function of the local catalog density / scale / distribution.

**The fix:** every threshold becomes data-driven. Median pairwise gap → epsilon. Catalog density → smoothness threshold. Population skew → chi² boundary. Bootstrap CI → slope tolerance.

**v3 integration:** v3 §4.5 (epistemic economy) measures cost; it does not regulate thresholds. A new primitive — `CatalogProfile` — is mandated to expose per-catalog scale parameters that thresholds key off. See §3.2.

### Anti-Pattern C — Triviality / degeneracy not gated upstream

**Where it appears:** G02 (Salem ≈ 99% of catalog), G05 (argmax|value| picks high-magnitude noise), G09 (50% ablation when survival is already 100%), G11 (Salem-cluster bulk survival was tautological), G13 (weakening to trivially-true), G14 (strengthening to tautologically-false), G15 (control-flow rows dominate MI), G24 (catalog already passes by construction), G25 (passes any non-empty subset).

**The pattern:** plugins fire on inputs that make their test mathematically vacuous, and the result is reported as substrate-grade verdict.

**The fix the DRs converge on:** a uniform precondition layer that every plugin must pass before its verdict is admitted. The layer rejects emissions where the test is degenerate-by-construction.

**v3 integration:** v3 §4.2 (plugin degeneracy audit) addresses *which plugins are operational aliases*. It does NOT address *which emissions of any single plugin are individually degenerate*. The DRs demand the second discipline. See §3.3 (new architectural primitive).

### Anti-Pattern D — Single-verdict emission instead of curve/distribution

**Where it appears:** G02 (single threshold), G04 (single band), G10 (single smoothness ratio), G16 (single adversarial value), G17 (single intervention threshold pre-ITER-18), G23 (single power-law fit pre-ITER-17).

**The pattern:** loaders emit one verdict at one parameter setting, throwing away the gradient that surrounds the chosen point.

**The fix the DRs converge on:** every loader emits a *survival curve* or *phase diagram* over its operative parameter, with the verdict-line as a derived feature of the curve, not the primary output. ITER-17 (G23 multi-law fit) and ITER-18 (G17 phase-transition sweep) already prove the value of this discipline.

**v3 integration:** add a new substrate emission type — `SurvivalCurve` — that every loader can produce as a first-class artifact alongside the existing single-verdict `BatteryLoaderResult`. See §3.4.

### Anti-Pattern E — Symbolic / syntactic operations where the math is structural

**Where it appears:** G03 (regex on claim text), G07 (hardcoded dictionary), G12 (hardcoded similarity matrix), G13 (regex predicate lattice), G19 (ledger-string verdict transitivity), G24 (operates on coefficient list, not algebraic object).

**The pattern:** the plugin operates on the text/JSON representation of a claim rather than the underlying algebraic structure. Falsifications based on text manipulation are guaranteed to miss structural failures.

**The fix the DRs converge on:** every plugin emits machine-evaluable predicate handles alongside text. The loader operates on the handle (Lean term, SMT formula, sympy expression, sage object), not the text.

**v3 integration:** v3 §4.7 (composition-payload schema mobility) is in the right direction but not strict enough. The DRs demand a `predicate_handle` first-class field on every emission. See §3.5.

---

## 2. v3 commitments — confirmed, sharpened, or re-prioritized

For each of v3's 10 architectural changes, the DR convergence either confirms it, sharpens it, or moves it in priority.

| v3 commitment | DR status | Change |
|---|---|---|
| §4.1 Ledger-memory ablation harness | CONFIRMED | DRs across all batches assume but do not verify this primitive |
| §4.2 Plugin degeneracy audit | CONFIRMED | Multiple DRs independently identify pairs (G02/G04/G10/G17 "split and sweep"; G11/G18 "exception search") |
| §4.3 Earned-tier protocol | CONFIRMED | DRs note self-annotation across plugins; observed-vs-declared discipline is the same fix |
| §4.4 Kill_pattern semantics layer | SHARPENED | DRs demand the layer + 14 specific routing actions per kill_pattern (see §4 below) |
| §4.5 Epistemic economy | CONFIRMED | DRs assume cost instrumentation; without it, none of their proposed improvements are measurable |
| §4.6 Second-domain MVP | CONFIRMED + RE-PRIORITIZED EARLIER | The DRs (especially G07, G08, G21) make clear that single-domain v3 is structurally indefensible; ship BSD MVP loader BEFORE the §4.7 / §4.8 work |
| §4.7 Payload schema mobility | SHARPENED | DRs demand `predicate_handle` first-class field (Anti-Pattern E) |
| §4.8 Loader-debt budget | CONFIRMED | DRs implicitly assume quarantine; the 200-emission cap is the right number |
| §4.9 Learner integration spec | CONFIRMED + RE-PRIORITIZED LATER | The DRs do not require this for their proposed improvements; move spec writing AFTER §3.1-3.5 primitives ship |
| §4.10 Three-tier finding reclassification | CONFIRMED | DRs across all batches independently demote Mahler findings to "catalog findings" |

Two re-prioritization moves:
- **Move §4.6 (second-domain MVP) EARLIER** — to immediately after the cost instrumentation (§4.5). Sprint-1 ablation A8 cannot run without it.
- **Move §4.9 (Learner integration spec) LATER** — to after §3.1-3.5 primitives ship. Writing the spec before the DRs' demanded primitives exist would lock in the wrong loss-function shape.

---

## 3. Four new architectural primitives the DRs demand

These primitives are NOT in v3 §4. They are mandatory pre-requisites for v3's other commitments to mean what they're supposed to mean.

### 3.1 `selection_discipline.py` — forbid arbitrary-scalar candidate selection

**Addresses Anti-Pattern A.**

A new module that every loader's `build_battery_input()` must call before returning. The module:

- **Forbids** lexicographically-first, modal, random, or aggregate-scalar selection from a structured mathematical space when the size of that space is > 1.
- **Requires** that any selection from a candidate set declare its *selection metric*: distance-minimizing, posterior-maximizing, or attribution-ranked.
- **Validates** that the chosen metric is appropriate for the data type via a small registry of (data_type, valid_metric) pairs (e.g., persistence diagrams permit Wasserstein-bottleneck but not Euclidean).
- **Records** the rejected candidates in the emission's `selection_provenance` field so downstream plugins can audit the choice.

Loaders that pick first-alphabetical or random-sample without declaring their metric raise `ArbitraryScalarSelectionError`. Existing loaders are quarantined until they pass.

**Failure-shape this prevents:** the G06 "alphabetical absentee" pathology and the G16 "10× hardcoded" pathology that the DRs both surfaced as load-bearing.

**Estimated effort:** 2 iterations. This module ships BEFORE any v3 §4 commitment is implemented because every §4 commitment relies on plugins making non-arbitrary choices.

### 3.2 `catalog_profile.py` — expose local catalog density for threshold calibration

**Addresses Anti-Pattern B.**

A module that, given a catalog accessor (currently `prometheus_math.databases.mahler`; eventually BSD, OEIS, NF), computes and caches:

- **Density profile:** kernel density estimate over the primary measurement axis (M for Mahler, conductor for BSD, etc.).
- **Median pairwise gap:** the natural scale for ε-band thresholds.
- **Population percentiles:** {p05, p25, p50, p75, p95, p99} for use as percentile-based adversarial pushes (replaces G16's 10× constant).
- **Bootstrap CIs:** for any plugin that fits a parameter, the bootstrap CI bound becomes the slope tolerance / chi² threshold automatically.

Loaders that hardcode thresholds must instead reference `catalog_profile(domain).{property}` or raise `HardcodedThresholdError`.

**Failure-shape this prevents:** the G02 "wrong threshold" pathology, the G10 "production-sweep-coupled smoothness" pathology, the G23 "decay tolerance" pathology — all of which the DRs identify as the same underlying mistake.

**Estimated effort:** 3 iterations.

### 3.3 `degeneracy_precondition.py` — pre-flight gate on (data, inquiry) pairs

**Addresses Anti-Pattern C.**

A module each loader's `applicable()` consults before returning True. The module:

- **Computes** for the (data, inquiry) pair: effective sample size (Kish formula), entropy of the test-relevant feature distribution, tail concentration index.
- **Rejects** emissions where: effective sample size < 30, OR entropy < 0.5 bits, OR tail concentration index > 0.95 (one population class > 95% of mass).
- **Emits** a structured `DegeneracyReport` field on the emission's payload that downstream plugins (and the kill_pattern semantics layer) consume.

The G15 v2 "control-flow row filter" already discovered that filtering bookkeeping rows changes substrate verdicts. The DRs demand this discipline at the gate, not at the meta-analysis layer. The G11 v1 Salem-cluster tautology would have been caught here pre-firing.

**Failure-shape this prevents:** the G24 "tautological pass," the G25 "any non-empty subset passes," the G11 v1 "Salem-class bulk is Salem-class" tautology, and the G05 "argmax|value| picks noise" pathology.

**Estimated effort:** 2 iterations.

### 3.4 `SurvivalCurve` emission type — first-class alongside `BatteryLoaderResult`

**Addresses Anti-Pattern D.**

A new emission type in `charon/agents/stygian/loaders/_emission_types.py`:

```python
@dataclass
class SurvivalCurve:
    parameter_name: str       # e.g., "threshold_M"
    parameter_values: list[float]  # e.g., [1.20, 1.22, ..., 1.40]
    observed_values: list[float]
    null_p05_values: list[float]
    null_p95_values: list[float]
    phase_transition_index: Optional[int]  # where outcome flips
    confidence_intervals: dict
    summary_verdict: str       # derived feature, NOT primary output
    summary_kill_pattern: Optional[str]
```

Loaders that currently emit single-verdict `BatteryLoaderResult` are not deprecated — but loaders that operate over a parameter (G02, G04, G10, G16, G17, G23) MUST emit `SurvivalCurve` and let the kill_pattern semantics layer derive the verdict.

The ITER-17 (G23 multi-law) and ITER-18 (G17 phase-transition sweep) refinements both informally produced curves. This primitive promotes the discipline.

**Failure-shape this prevents:** the G17 v1 "single threshold M=M_Lehmer trivial" miss (which only surfaced when ITER-18 added the sweep) and the G23 v1 "single 1/N fit rejection" framing (which only surfaced 1/log(N) when ITER-17 added the multi-law fit).

**Estimated effort:** 2 iterations.

### 3.5 `predicate_handle` field — machine-evaluable substrate alongside claim text

**Addresses Anti-Pattern E.**

Add a new field to `ComposedClaim`:

```python
predicate_handle: Optional[PredicateHandle]
```

Where `PredicateHandle` is a discriminated union of:
- `LeanTermHandle` — pointer to a Lean 4 term + theorem context
- `SmtFormulaHandle` — z3.ExprRef or s-expression
- `SymPyExpressionHandle` — sympy expression with symbol table
- `SageObjectHandle` — SageMath object reference
- `MahlerPolynomialHandle` — coefficient vector + algebraic-integer-class metadata

Loaders that need to evaluate a claim semantically (not lexically) consult the handle. The existing text-based G03, G13, G24 implementations remain but are reduced to fallback paths when no handle is present.

This is the M3 → M4 move on the Reasoning Ladder. Without it, the substrate remains representation-locked.

**Failure-shape this prevents:** the G03 "regex on claim text" pathology (Anti-Pattern E) and the G13 "syntactic predicate weakening" pathology — both of which the DRs identify as load-bearing-wrong.

**Estimated effort:** 4 iterations (this is the biggest of the four primitives because it touches every plugin's `_build_claim()`).

---

## 4. The kill_pattern semantics layer — DR-derived specification

v3 §4.4 commits to the layer; the DRs provide the specific routing-action table. This section is the concrete spec.

### Per-kill_pattern routing actions

| kill_pattern | Repair class (F-axis) | Routing action | Confusion class |
|---|---|---|---|
| `permutation_null` | F3 local repair | Fire G02 with Westfall-Young max-T (Batch 1 DR convergence) | vs `boundary_collapse` (G03) |
| `boundary_collapse` | F4 global repair | Fire G03 with data-driven epsilon from `catalog_profile` | vs `weakening_too_strict` |
| `weakening_too_strict` | F5 strategy repair | Fire G13 with Z3 semantic weakening (Batch 3) | vs `boundary_collapse` |
| `strict_threshold_violation` | F4 global repair | Fire G04 with information-optimal band selection (Batch 1) | vs `permutation_null` |
| `complete_signal_collapse` | F6 ontology repair | Fire G05 with NOTEARS confounder discovery (Batch 1) | vs `permutation_null` |
| `universal_rejection` | F7 problem repair | Fire G06 with Wasserstein-distance void selection (Batch 2) | (none) |
| `metaphor_collapse` | F6 ontology repair | Fire G07 with cross-domain dataset accessor | (none — G07 is blocked) |
| `overfitting_goodharting` | F5 strategy repair | Fire G08 with Ergon ML held-out (currently blocked) | vs `residual_survival` |
| `residual_survival` | F3 local repair | Fire G09 with cc-Shapley attribution (Batch 2) | vs `overfitting_goodharting` |
| `smooth_degradation` | F3 local repair | (no action — claim survives sweep) | vs `sharp_boundary_detected` |
| `sharp_boundary_detected` | F6 ontology repair | Fire G10 with BOCPD posterior (Batch 2) | vs `smooth_degradation` |
| `out_of_sample_failure` | F5 strategy repair | Fire G11 with Monte Carlo permutation G-test (Batch 2) | vs `permutation_null` |
| `invariant_swap_collapses` | F6 ontology repair | Fire G12 with learned similarity matrix (Batch 2) | vs `metaphor_collapse` |
| `predicate_collapses_to_trivial` | F4 global repair | Fire G13 with Z3 semantic weakening (Batch 3) | vs `boundary_collapse` |
| `strengthening_breaks` | F5 strategy repair | Fire G14 with refinement-type witnesses (Batch 3) | vs `predicate_collapses_to_trivial` |
| `uncorrelated_residual_failures` | F3 local repair | Fire G15 v2 (real-verdict MI; already shipped) | (none) |
| `conjecture_survives_adversarial_attack` | F4 global repair | Fire G16 with percentile-based adversarial value (Batch 3) | vs `permutation_null` |
| `correlation_survives_intervention` | F6 ontology repair | Fire G17 with explicit do-operator graph surgery (Batch 3) | vs `conjecture_survives_adversarial_attack` |
| `region_R_exhausted_without_counterexample` | F5 strategy repair | Fire G18 with Voronoi-cell region prediction (Batch 4) | (none) |
| `sub_claim_falsified` | F3 local repair | Fire G19 v3 with Lean well-foundedness check (Batch 4) | (none) |
| `instrument_clash_detected` | F8 epistemic repair | Currently vacuous (G20); when Lethe v2 ships, fire G20 v2 | (none) |
| `functor_breaks` | F6 ontology repair | Fire G21 with per-domain morphism enumerator (currently blocked) | vs `metaphor_collapse` |
| `counterexample_breaks_master_unification` | F5 strategy repair | Fire G22 with Leiden + constant-Potts model (Batch 4) | (none) |
| `error_term_does_not_decay` | F4 global repair | Fire G23 with broken-power-law BIC (Batch 4) | vs `decay_faster_than_1_over_N` |
| `decay_faster_than_1_over_N` | F4 global repair | Fire G23 v2 multi-law (already shipped) | vs `error_term_does_not_decay` |
| `symmetry_breaking` | F8 epistemic repair | Fire G24 v3 with relational symmetry+invariant gate (Batch 5) | (none) |
| `tautological_pass` | F8 epistemic repair | Fire G25 v2 with (data, inquiry) precondition (Batch 5) | (none) |

This table replaces v3 §4.4's "TBD per kill_pattern" with concrete routing rules. The substrate now has machine-actionable failure gradients.

---

## 5. Prior-art commitments inherited from DR convergence

The DRs converged on a set of 2024-2027 methods that should become substrate-level dependencies, not per-plugin reinventions. Listed here for the architecture record.

### Substrate-level dependencies to add

- **`NOTEARS` / PC algorithm** for causal-discovery DAG construction (G05 confound, G17 intervention). Cited across Batches 1, 3.
- **Westfall-Young max-T permutation + Benjamini-Hochberg FDR** for multi-test family correction (G02, G04, G11). Cited across Batches 1, 2.
- **Empirical-Bernstein concentration bounds** for tightening (G04). Cited Batch 1.
- **Synthetic null engine / Knockoffs framework** (Barber-Candès 2025+) for calibrated permutation alternatives. Cited Batches 1, 4.
- **Bayesian Online Change-Point Detection (BOCPD)** for phase-transition / smoothness analysis (G10, G17). Cited Batches 2, 3.
- **Z3 SMT integration** for semantic predicate weakening / strengthening (G13, G14). Cited Batch 3.
- **Kohlenbach proof mining** for quantitative-from-qualitative weakening (G03, G13). Cited Batches 1, 3.
- **Leiden algorithm + constant Potts model** for community detection (G22). Cited Batch 4.
- **Refinement type theory** for safe strengthening witnesses (G14). Cited Batch 3.
- **cc-Shapley attribution** for projection-collapse correctness (G09). Cited Batch 2.
- **Wasserstein-bottleneck distance on persistence diagrams** for topological void selection (G06). Cited Batch 2.
- **Topos-theoretic causal models** as contrarian alternative to NOTEARS (G05 contrarian). Cited Batch 1.
- **Dirichlet-prior smoothed MI estimators** (Miller-Madow) for small-N joint distributions (G15). Cited Batch 3.

These dependencies are listed for v3.1+ implementation. Sprint-1 does not require them — Sprint-1 measures whether the v0 substrate has any value at all. v3.1 ships the dependencies that make the answer "yes."

---

## 6. Re-prioritized v3 roadmap

Combining v3 §9 with DR-convergence priorities:

**Phase 0 — Discipline primitives (ITER-21 → ITER-30, ~10 iterations):**
1. `selection_discipline.py` (§3.1) — forbid arbitrary scalar selection.
2. `catalog_profile.py` (§3.2) — expose local catalog density.
3. `degeneracy_precondition.py` (§3.3) — pre-flight gate.
4. `SurvivalCurve` emission type (§3.4) — first-class alongside BatteryLoaderResult.
5. `predicate_handle` field on ComposedClaim (§3.5) — M3 → M4 representation lift.
6. `kill_pattern_registry.py` populated per §4 routing table.
7. Cost-instrumentation layer (v3 §4.5) — pre-requisite for Sprint-1.
8. Loader-debt budget enforcement (v3 §4.8) — quarantine 8 loaderless plugins.
9. Three-tier finding reclassification (v3 §4.10) — rewrite whitepaper Section 5.

**Phase 1 — Architecture proofs (ITER-31 → ITER-40, ~10 iterations):**
10. Ledger-memory ablation harness (v3 §4.1) — first Sprint-1-style experiment.
11. Plugin degeneracy audit (v3 §4.2) — likely reduces 25 → 12-18 archetypes.
12. Earned-tier protocol (v3 §4.3) — replace self-annotation with behavioral observation.
13. BSD MVP loader (v3 §4.6) — second-domain proof. PROMOTED IN PRIORITY from Phase 2 because Sprint-1 A8 requires it.

**Phase 2 — Sprint-1 self-falsification (ITER-41 → ITER-50, ~10 iterations):**
14. All 10 ablation experiments per v3 §5.
15. Decision against v3 §6 kill conditions.

**Phase 3 — Conditional on Sprint-1 pass (ITER-51+):**
16. OEIS MVP loader (v3 §4.6 remaining).
17. NF MVP loader (v3 §4.6 remaining).
18. Composition-payload schema mobility deeper than `predicate_handle` (v3 §4.7).
19. Learner integration spec (v3 §4.9, DEMOTED IN PRIORITY because writing it before §3.5 ships would lock in wrong loss-function shape).
20. Per-plugin v3 reviews using the 22 DR outputs as inputs — only if architecture survives Sprint-1.

The total Phase 0 + Phase 1 + Phase 2 budget is ~30 iterations. Sprint-1 verdict at ITER-50.

---

## 7. Per-plugin DR-derived code-level demands (preserved for Phase 3+)

If Sprint-1 passes, the DRs surface 22 specific per-plugin code-level changes that should drive v3-grade plugin updates. Listed here as the work-queue for Phase 3+, NOT as commitments for Phase 0-2. The full per-plugin specifics live in the five batch synthesis docs:

- `aporia/docs/erebos_v3_dr_synthesis_batch1_g01_g05.md`
- `aporia/docs/erebos_v3_dr_synthesis_batch2_g06_g12.md`
- `aporia/docs/erebos_v3_dr_synthesis_batch3_g13_g17.md`
- `aporia/docs/erebos_v3_dr_synthesis_batch4_g18_g23.md`
- `aporia/docs/erebos_v3_dr_synthesis_batch5_g24_g25.md`

The work-queue is roughly the §4 routing table inverted into commits.

---

## 8. What the DR amendment does NOT change about v3

For honesty: the DR convergence reinforces v3's architecture but does NOT change:

1. **The 8 open questions in v3 §8** remain open. The DRs do not solve Goodhart-on-kill_patterns deepening, OEIS interestingness, compounding rot, ATP backend, Type E autonomous repair, or Lethe contamination. They sharpen the architecture; they do not transcend its limits.
2. **The 5 kill conditions in v3 §6** remain pre-committed. The DR convergence cannot be allowed to inflate confidence into "the substrate is now justified because the DRs are detailed." Sprint-1 is the verdict; the DRs are inputs to Sprint-1's design.
3. **The reclassification of 7 Mahler findings to "catalog findings"** stays. The DRs converge on the same demotion; none surface a finding that would qualify as "mathematical" or "literature-grade."
4. **The pause-or-shutdown disposition at ITER-50** stays. The DR convergence raises the bar for "what passing Sprint-1 means" — Sprint-1 must demonstrate that the substrate operating WITH the §3.1-§3.5 primitives and §4 routing table beats ablated baselines. If it doesn't, the substrate failed at the architecturally-strongest version of itself.

---

## 9. Acknowledgment of DR contribution

Per `feedback_take_a_stand`: the DRs did real work. The §3 primitives and §4 routing table did not exist in v3 because v3 was synthesized from frontier-model architectural critique, not from per-plugin literature review. The DR pass surfaced what the frontier critique missed: the loader-implementation patterns that re-introduce v1 anti-patterns at every plugin. The architectural commitments in v3 are necessary; the DR-derived primitives in §3 are what makes those commitments enforceable.

The combined v3 + DR-amendment is the substrate's most honest design statement to date. Sprint-1 is what determines whether the honesty was earned.

---

**End amendment.** Combined reading order for the v3 path:

1. `pivot/erebos_whitepaper_v1_2026-05-27.md` (the artifact the critique addresses)
2. `pivot/erebos_v3_synthesis_2026-05-27.md` (frontier-critique-driven architecture)
3. `pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md` (this document — DR-driven primitives)
4. `aporia/docs/erebos_v3_dr_synthesis_batch{1..5}_*.md` (per-batch DR extractions)
5. `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/*.md` (the 22 raw DR outputs)

Phase 0 begins at ITER-21.
