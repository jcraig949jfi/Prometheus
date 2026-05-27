# Erebos v3 — Phase 0 Implementation Plan (ITER-21 → ITER-30)

**Date:** 2026-05-27
**Purpose:** Operational plan for the 9 discipline primitives that v3 + DR amendment commit to before Sprint-1 can run meaningfully.
**Predecessor:** `pivot/erebos_v3_synthesis_2026-05-27.md` + `pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md`
**Phase:** Phase 0 of 3. Phase 1 ships architecture proofs; Phase 2 is Sprint-1 self-falsification.

---

## Phase 0 — discipline primitives that prevent loader implementations from defaulting back to v1 anti-patterns

Each ITER targets one primitive. Each iteration has: goals, files to touch, modules to add, test spec, smoke-test, commit message template, expected outcome.

### ITER-21 — `selection_discipline.py`

**DR anti-pattern addressed:** A (arbitrary-scalar selection).

**Goal:** A substrate-level module every loader's `build_battery_input()` must call when selecting from a candidate set with cardinality > 1. The module forbids lexicographically-first, modal, random, or aggregate-scalar selection without an explicit declared selection metric.

**New files:**
- `charon/agents/stygian/loaders/_selection_discipline.py` — the primitive.
- `charon/agents/stygian/tests/test_selection_discipline.py` — synthetic tests.

**Module signature:**
```python
class SelectionMetric(Enum):
    DISTANCE_MINIMIZING = "distance_minimizing"   # e.g., Wasserstein on persistence diagrams
    POSTERIOR_MAXIMIZING = "posterior_maximizing" # e.g., BOCPD posterior on change-points
    ATTRIBUTION_RANKED = "attribution_ranked"     # e.g., cc-Shapley on features
    PERCENTILE_BASED = "percentile_based"         # e.g., empirical-CDF push for adversarial
    EXHAUSTIVE = "exhaustive"                     # all candidates kept; no selection

class ArbitraryScalarSelectionError(Exception):
    """Raised when a loader picks first / random / argmax-scalar without declaring metric."""

def disciplined_select(
    candidates: list[Any],
    metric: SelectionMetric,
    metric_callable: Callable[[Any], float],
    *,
    data_type: str,                # for registry validation
    selection_provenance: dict,    # populated into emission's selection_provenance
) -> tuple[Any, dict]:
    """Select one candidate from > 1; record the chosen-and-rejected list.
    Raises ArbitraryScalarSelectionError if metric is None or metric_callable
    is incompatible with declared metric."""

def validate_metric_for_data_type(metric: SelectionMetric, data_type: str) -> bool:
    """Per the (data_type, valid_metric) registry. E.g., persistence_diagram
    accepts DISTANCE_MINIMIZING via Wasserstein but not POSTERIOR_MAXIMIZING."""
```

**Registry (initial population):**
```python
_VALID_METRIC_PAIRS = {
    "persistence_diagram": {SelectionMetric.DISTANCE_MINIMIZING},
    "survival_curve": {SelectionMetric.POSTERIOR_MAXIMIZING, SelectionMetric.PERCENTILE_BASED},
    "feature_vector": {SelectionMetric.ATTRIBUTION_RANKED, SelectionMetric.DISTANCE_MINIMIZING},
    "kill_pattern_set": {SelectionMetric.DISTANCE_MINIMIZING, SelectionMetric.EXHAUSTIVE},
    "ledger_row_set": {SelectionMetric.POSTERIOR_MAXIMIZING, SelectionMetric.EXHAUSTIVE},
}
```

**Test spec (10+ tests):**
- `test_select_distance_minimizing_on_persistence_diagram` — synthetic 3-candidate set; verifies smallest-distance returned.
- `test_select_attribution_ranked_on_feature_vector` — synthetic Shapley scores; verifies highest-attribution returned.
- `test_select_raises_on_undeclared_metric` — None metric → ArbitraryScalarSelectionError.
- `test_select_raises_on_incompatible_metric_data_type` — persistence_diagram + POSTERIOR_MAXIMIZING → error.
- `test_select_records_rejected_candidates_in_provenance` — selection_provenance carries all rejected.
- `test_select_with_single_candidate_skips_metric_check` — N=1 input passes through.
- `test_select_with_empty_candidates_raises` — explicit error.
- `test_select_metric_callable_must_be_finite` — NaN/Inf raises.
- `test_validate_metric_for_data_type_known_pairs`
- `test_validate_metric_for_data_type_unknown_data_type_returns_false`

**Smoke test:** import the module from an existing loader (g06_lehmer_*) and verify it can be plumbed.

**Commit template:**
```
Erebos v0.27 Phase 0 ITER-21: selection_discipline.py
Addresses DR Anti-Pattern A (arbitrary-scalar selection).
Forbids lexicographic-first / random / aggregate-scalar selection
at the loader-base-class contract. Registry: 5 SelectionMetric
values; 5 data_type validity pairs. 10 synthetic tests pass.
```

**Expected outcome:** infrastructure exists; no existing loader uses it yet (that's ITER-30's wrap work). The 6 loaders identified in DR Anti-Pattern A (G06, G09, G10, G11, G16, G18) become candidates for retrofit in Phase 1.

---

### ITER-22 — `catalog_profile.py`

**DR anti-pattern addressed:** B (local geometry ignored at thresholds).

**Goal:** A module that, given a catalog accessor, computes and caches local density / median pairwise gap / population percentiles / bootstrap CIs. Loaders that currently hardcode thresholds must reference `catalog_profile(domain).{property}` instead.

**New files:**
- `prometheus_math/databases/_catalog_profile.py` — primitive (lives in math layer so non-Stygian consumers can use it).
- `charon/agents/stygian/tests/test_catalog_profile.py` — tests.

**Module signature:**
```python
@dataclass(frozen=True)
class CatalogProfile:
    domain: str
    n_entries: int
    primary_axis_field: str        # e.g., "mahler_measure"
    density_kde: Callable[[float], float]  # KDE function
    median_pairwise_gap: float
    p05: float; p25: float; p50: float; p75: float; p95: float; p99: float
    bootstrap_ci: dict[str, tuple[float, float]]  # (lo, hi) per parameter
    computed_at: str  # ISO timestamp; cache invalidation key

class HardcodedThresholdError(Exception):
    """Raised when a loader uses a literal threshold without referencing catalog_profile."""

def catalog_profile(domain: str, *, refresh: bool = False) -> CatalogProfile:
    """Return cached profile for domain. Recompute if refresh=True or cache miss."""

def epsilon_band_for(domain: str, *, multiplier: float = 1.0) -> float:
    """Data-driven epsilon = multiplier * median_pairwise_gap."""

def percentile_threshold_for(domain: str, p: float) -> float:
    """Data-driven percentile pull from {p05, ..., p99}."""

def bootstrap_ci_for(domain: str, parameter_name: str) -> tuple[float, float]:
    """Data-driven CI for use as slope tolerance / chi² boundary / etc."""
```

**Cache strategy:** Pickle cache at `prometheus_math/databases/_catalog_profile_cache/<domain>.pkl`. Invalidate on catalog file mtime change.

**Test spec (8+ tests):**
- `test_catalog_profile_mahler_returns_valid_profile`
- `test_catalog_profile_cache_hits_on_second_call`
- `test_catalog_profile_refresh_invalidates_cache`
- `test_epsilon_band_for_mahler_with_default_multiplier`
- `test_percentile_threshold_for_known_values` (uses Mahler ground truth)
- `test_bootstrap_ci_for_returns_tuple_with_lo_lt_hi`
- `test_unknown_domain_raises`
- `test_density_kde_callable_returns_finite_value`

**Smoke test:**
```python
profile = catalog_profile("mahler")
eps = epsilon_band_for("mahler")
print(eps)  # expect ~ median pairwise M-gap in Mossinghoff
```

**Commit template:**
```
Erebos v0.28 Phase 0 ITER-22: catalog_profile.py
Addresses DR Anti-Pattern B (local geometry ignored at thresholds).
KDE density, median gap, p05-p99 percentiles, bootstrap CIs cached
per domain. Mahler profile populated; BSD/OEIS/NF stubs raise
UnknownDomain. 8 tests pass.
```

**Expected outcome:** future loader iterations replace hardcoded constants (G03 EPSILON_BAND, G10 SMOOTH_THRESHOLD, G11 CHI2_THRESHOLD, G23 DECAY_SLOPE_TOLERANCE) with `catalog_profile` calls.

---

### ITER-23 — `degeneracy_precondition.py`

**DR anti-pattern addressed:** C (triviality / degeneracy not gated upstream).

**Goal:** A module each loader's `applicable()` consults before returning True. Rejects emissions where the (data, inquiry) pair makes the test mathematically vacuous.

**New files:**
- `charon/agents/stygian/loaders/_degeneracy_precondition.py` — primitive.
- `charon/agents/stygian/tests/test_degeneracy_precondition.py` — tests.

**Module signature:**
```python
@dataclass(frozen=True)
class DegeneracyReport:
    is_degenerate: bool
    n_effective: int                # Kish formula
    feature_entropy_bits: float
    tail_concentration_index: float # max population fraction
    reason: Optional[str]           # which threshold tripped
    threshold_n_effective: int = 30
    threshold_entropy_bits: float = 0.5
    threshold_tail_index: float = 0.95

def degeneracy_report(
    data: Any,
    inquiry: dict,                  # the test the loader plans to run
    *,
    feature_extractor: Callable,    # which feature is "test-relevant"
) -> DegeneracyReport:
    """Compute the (data, inquiry) degeneracy report. Emitted as part of
    the loader's BatteryLoaderResult so downstream consumers can audit."""

def gate(report: DegeneracyReport) -> None:
    """Raise DegenerateInputError if report.is_degenerate."""

class DegenerateInputError(Exception):
    """Raised when a loader fires on degenerate input."""

def kish_effective_n(weights: list[float]) -> int:
    """(sum w)^2 / sum w^2"""

def entropy_bits(distribution: list[float]) -> float:
    """Shannon entropy in bits."""

def tail_concentration_index(distribution: list[float]) -> float:
    """max(distribution) / sum(distribution)."""
```

**Test spec (10+ tests):**
- `test_kish_effective_n_uniform_weights_equals_n`
- `test_kish_effective_n_concentrated_weights_drops`
- `test_entropy_bits_uniform_equals_log2_n`
- `test_entropy_bits_concentrated_drops_below_threshold`
- `test_tail_concentration_index_uniform_equals_one_over_n`
- `test_tail_concentration_index_concentrated_equals_one`
- `test_degeneracy_report_uniform_population_not_degenerate`
- `test_degeneracy_report_concentrated_population_is_degenerate`
- `test_degeneracy_report_small_sample_is_degenerate`
- `test_gate_raises_on_degenerate_report`
- `test_degeneracy_report_emitted_to_payload` (integration test)

**Smoke test:** simulate the G11 v1 tautology — feed Salem-bulk (99% one class) to the gate and verify it would reject.

**Commit template:**
```
Erebos v0.29 Phase 0 ITER-23: degeneracy_precondition.py
Addresses DR Anti-Pattern C (triviality not gated upstream).
Kish effective N + Shannon entropy + tail concentration index.
Pre-flight gate on (data, inquiry) pairs. Synthetic test confirms
the G11 v1 Salem-cluster tautology would have been rejected.
10 tests pass.
```

**Expected outcome:** future loader iterations call `degeneracy_report(...)` in `applicable()`. The 7 loaders identified in DR Anti-Pattern C become candidates for retrofit.

---

### ITER-24 — `SurvivalCurve` emission type

**DR anti-pattern addressed:** D (single-verdict instead of curve).

**Goal:** Add a new dataclass alongside `BatteryLoaderResult` that loaders operating over a parameter emit. Verdict-line becomes a derived feature of the curve, not the primary output.

**New files:**
- `charon/agents/stygian/loaders/_emission_types.py` — promotes existing dict-based emissions to typed dataclasses + adds `SurvivalCurve`.
- `charon/agents/stygian/tests/test_emission_types.py` — tests.

**Module signature:**
```python
@dataclass(frozen=True)
class SurvivalCurve:
    parameter_name: str
    parameter_values: list[float]
    observed_values: list[float]
    null_p05_values: list[float]
    null_p95_values: list[float]
    phase_transition_index: Optional[int]
    confidence_intervals: dict[str, tuple[float, float]]
    summary_verdict: str
    summary_kill_pattern: Optional[str]
    notes: str

    def detect_phase_transition(
        self,
        outcome_predicate: Callable[[int], bool]
    ) -> Optional[int]:
        """Return the first index where outcome predicate flips."""

    def to_battery_result(self) -> dict:
        """Convert to the legacy BatteryLoaderResult dict shape for
        backward compatibility with existing executor."""
```

**Test spec (8+ tests):**
- `test_survival_curve_dataclass_construction`
- `test_survival_curve_detect_phase_transition_monotone_severable_to_survives`
- `test_survival_curve_detect_phase_transition_no_transition`
- `test_survival_curve_to_battery_result_backward_compat`
- `test_survival_curve_confidence_intervals_lo_lt_hi`
- `test_survival_curve_parameter_values_monotone`
- `test_survival_curve_observed_and_nulls_same_length`
- `test_survival_curve_phase_transition_index_in_bounds`

**Smoke test:** retroactively wrap the ITER-18 G17 sweep result in a `SurvivalCurve` and verify `detect_phase_transition` recovers M=1.26.

**Commit template:**
```
Erebos v0.30 Phase 0 ITER-24: SurvivalCurve emission type
Addresses DR Anti-Pattern D (single-verdict instead of curve).
First-class typed alternative to dict-based BatteryLoaderResult.
phase_transition_index field; detect_phase_transition() helper.
Backward-compat via to_battery_result(). Smoke test: ITER-18 G17
sweep result correctly produces phase_transition_index = 3
(threshold M=1.26 boundary). 8 tests pass.
```

**Expected outcome:** future loaders operating over a parameter (G02, G04, G10, G16, G17, G23) emit SurvivalCurves.

---

### ITER-25 — `predicate_handle` field on `ComposedClaim`

**DR anti-pattern addressed:** E (symbolic / syntactic operations where math is structural).

**Goal:** Add a `predicate_handle` field to `ComposedClaim` that carries a machine-evaluable substrate alongside the claim text. M3 → M4 representation lift.

**New files:**
- `charon/agents/erebos/generators/_predicate_handles.py` — handle types.
- `charon/agents/erebos/tests/test_predicate_handles.py` — tests.

**Files to modify:**
- `charon/agents/erebos/generators/_base.py` — add `predicate_handle: Optional[PredicateHandle]` to `ComposedClaim`.

**Module signature:**
```python
class PredicateHandle(Protocol):
    """Discriminated union supertype."""
    handle_type: str   # one of: "lean_term", "smt_formula", "sympy_expr",
                       # "sage_object", "mahler_polynomial"
    def evaluate(self, point: Any) -> bool: ...
    def to_string(self) -> str: ...

@dataclass(frozen=True)
class MahlerPolynomialHandle:
    """Coefficient vector + algebraic-integer-class metadata."""
    handle_type: str = "mahler_polynomial"
    coeffs: list[int]
    is_palindromic: bool
    is_anti_palindromic: bool
    is_cyclotomic_extension: bool   # detected via M-equality
    mahler_measure: float
    degree: int
    salem_class: bool

    def evaluate(self, point: "MahlerPolynomialHandle") -> bool:
        """Default: structural equality."""

    def to_string(self) -> str:
        return f"M-poly deg={self.degree} M={self.mahler_measure}"

@dataclass(frozen=True)
class SmtFormulaHandle:
    handle_type: str = "smt_formula"
    sexpr: str           # z3-compatible s-expression
    variables: list[str]
    def evaluate(self, point: dict[str, Any]) -> bool: ...

# Lean / SymPy / Sage stubs raise NotImplementedError until ATP integration ships.
```

**Test spec (10+ tests):**
- `test_mahler_polynomial_handle_evaluate_self_equal`
- `test_mahler_polynomial_handle_to_string_format`
- `test_mahler_polynomial_handle_detect_palindromic`
- `test_mahler_polynomial_handle_detect_cyclotomic_extension`
- `test_smt_formula_handle_evaluate_simple_inequality` (mocked z3)
- `test_composed_claim_optional_predicate_handle_backward_compat`
- `test_composed_claim_with_mahler_handle_serializes_to_ledger`
- `test_lean_handle_stub_raises_not_implemented`
- `test_sympy_handle_stub_raises_not_implemented`
- `test_sage_handle_stub_raises_not_implemented`

**Smoke test:** retroactively wrap a G18 emission in a `MahlerPolynomialHandle` with the cyclotomic-extension filter; verify the false-positive Lehmer×Φ_16 case is correctly flagged via `is_cyclotomic_extension=True`.

**Commit template:**
```
Erebos v0.31 Phase 0 ITER-25: predicate_handle on ComposedClaim
Addresses DR Anti-Pattern E (syntactic ops where math is structural).
M3 -> M4 representation lift. MahlerPolynomialHandle fully
implemented (covers G03/G11/G18/G24 use cases); SmtFormulaHandle
basic implementation; Lean/SymPy/Sage handle stubs raise
NotImplementedError until ATP integration. 10 tests pass.
```

**Expected outcome:** plugins that currently regex-on-text (G03, G13) gain an alternate evaluation path. The G18 cyclotomic-extension filter becomes a property of the handle, not a one-off epsilon check.

---

### ITER-26 — `kill_pattern_registry.py`

**Goal:** Populate v3 §4.4's TBD registry with the 27-row routing table from v3 amendment §4.

**New files:**
- `charon/agents/erebos/_kill_pattern_registry.py` — primitive.
- `charon/agents/erebos/tests/test_kill_pattern_registry.py` — tests.

**Module signature:**
```python
@dataclass(frozen=True)
class KillPatternSpec:
    name: str
    repair_class: str       # F-axis: "F3" .. "F8"
    routing_action: str     # which plugin fires next (string ID for now;
                            # resolved to plugin instance later)
    confusion_class: list[str]  # other kill_patterns often confused with this
    observable_signature: str   # the exact loader-output condition that triggers
    assignment_provenance: str  # "human" | "loader" | "model_inferred" | "substrate_derived"

KILL_PATTERN_REGISTRY: dict[str, KillPatternSpec] = {
    "permutation_null": KillPatternSpec(
        name="permutation_null",
        repair_class="F3",
        routing_action="g02_with_westfall_young",
        confusion_class=["boundary_collapse"],
        observable_signature="observed_divergence <= null_p95",
        assignment_provenance="loader",
    ),
    # ... 26 more entries per v3 amendment §4 routing table
}

def routing_action_for(kp: str) -> Optional[str]:
    """Return the routing_action string for a kill_pattern, or None."""

def confusion_class_for(kp: str) -> list[str]:
    """Return the list of confusable kill_patterns."""

def repair_class_for(kp: str) -> str:
    """Return the F-axis repair class. Raises if kp unknown."""
```

**Test spec (8+ tests):**
- `test_registry_has_all_27_kill_patterns_from_v3_amendment`
- `test_routing_action_for_permutation_null`
- `test_routing_action_for_unknown_kill_pattern_returns_none`
- `test_confusion_class_for_boundary_collapse_includes_weakening_too_strict`
- `test_repair_class_for_all_entries_is_valid_F_axis`
- `test_assignment_provenance_for_all_entries_is_valid`
- `test_registry_keys_match_dataclass_name_field`
- `test_observable_signature_is_non_empty_for_all`

**Smoke test:** for each of the 14 directional kill_patterns currently in production, verify the registry has an entry.

**Commit template:**
```
Erebos v0.32 Phase 0 ITER-26: kill_pattern_registry.py
Populates v3 sec 4.4 TBD with 27-row routing table per v3 amendment
sec 4. Each kill_pattern carries: repair_class (F-axis), routing
_action, confusion_class, observable_signature, assignment_
provenance. Substrate now has machine-actionable failure gradients.
8 tests pass.
```

**Expected outcome:** future routing-layer work consults `routing_action_for(kp)` to decide the next plugin.

---

### ITER-27 — Cost-instrumentation layer

**Goal:** Every ComposedClaim emission gets four cost/value prices attached per v3 §4.5.

**Files to modify:**
- `charon/agents/erebos/generators/_base.py` — add cost fields to ComposedClaim.
- `charon/agents/erebos/daemon.py` — wrap plugin.generate() with timing; wrap loader execution with timing.
- `charon/agents/erebos/_value_metrics.py` — primitive for value_per_tick computation.

**New files:**
- `charon/agents/erebos/tests/test_value_metrics.py` — tests.

**Module signature additions to ComposedClaim:**
```python
@dataclass
class ComposedClaim:
    # ... existing fields ...
    generation_cost_seconds: float = 0.0
    falsification_cost_seconds: Optional[float] = None
    information_gain_nats: Optional[float] = None
    reuse_value_count: int = 0   # updated as downstream emissions reference
```

**`_value_metrics.py`:**
```python
def value_per_tick(
    ledger_rows: list[dict],
    *,
    window_days: int = 60,
) -> float:
    """Compute sum(info_gain * reuse_value) / sum(generation_cost +
    falsification_cost) over the rolling window."""

def information_gain_estimate(
    routing_distribution_before: dict[str, float],
    routing_distribution_after: dict[str, float],
) -> float:
    """KL divergence in nats between routing distributions."""

def update_reuse_value_counts(
    ledger_path: Path,
    window_days: int = 60,
) -> dict[str, int]:
    """For each row in the window, count downstream emissions that
    reference it via parent_record_ids. Returns {record_id: count}."""
```

**Test spec (6+ tests):**
- `test_value_per_tick_zero_for_empty_ledger`
- `test_value_per_tick_increases_with_information_gain`
- `test_value_per_tick_decreases_with_falsification_cost`
- `test_information_gain_zero_for_identical_distributions`
- `test_information_gain_positive_for_diverged_distributions`
- `test_update_reuse_value_counts_correct_on_synthetic_ledger`

**Commit template:**
```
Erebos v0.33 Phase 0 ITER-27: cost-instrumentation layer
v3 sec 4.5: every emission carries generation_cost_seconds,
falsification_cost_seconds, information_gain_nats, reuse_value_
count. value_per_tick = sum(info_gain * reuse_value) / sum(costs).
6 tests pass. Sprint-1 baseline measurable.
```

**Expected outcome:** the substrate has a value function. Phase 1 ablation experiments can measure against it.

---

### ITER-28 — Loader-debt budget enforcement

**Goal:** Hard-cap unfalsifiable emissions per v3 §4.8. Quarantine the 8 loaderless plugins.

**Files to modify:**
- `charon/agents/erebos/generators/__init__.py` — `applicable_plugins(state)` filters by quarantine status.
- `pivot/erebos_quarantine.md` — new file documenting quarantined plugins + unblock criteria.

**New files:**
- `charon/agents/erebos/_quarantine.py` — primitive.
- `charon/agents/erebos/tests/test_quarantine.py` — tests.

**Module signature:**
```python
@dataclass(frozen=True)
class QuarantineRule:
    plugin_id: str
    quarantined_since: str     # ISO date
    unblock_criterion: str     # "ship composition_g05_*.py" / etc.
    pending_emission_count: int

QUARANTINE_RULES: dict[str, QuarantineRule] = {
    "g05_confound_swap": QuarantineRule(
        plugin_id="g05_confound_swap",
        quarantined_since="2026-05-27",
        unblock_criterion="ship composition_g05_*.py loader",
        pending_emission_count=0,  # tracked at runtime
    ),
    # ... 7 more entries (G06, G12, G13, G14, G15? wait g15 has loader, G22 has loader... check)
}

def is_quarantined(plugin_id: str) -> bool: ...
def check_emission_cap(plugin_id: str, current_pending_count: int) -> None:
    """Raises LoaderDebtCapExceededError if pending > MAX_PENDING_EMISSIONS."""

MAX_PENDING_EMISSIONS = 200
MAX_QUARANTINE_DAYS = 30
```

**Test spec (6+ tests):**
- `test_is_quarantined_returns_true_for_listed_plugin`
- `test_is_quarantined_returns_false_for_unlisted_plugin`
- `test_check_emission_cap_raises_above_max`
- `test_check_emission_cap_passes_below_max`
- `test_applicable_plugins_excludes_quarantined`
- `test_quarantine_rule_unblock_criterion_required`

**Smoke test:** verify quarantined plugin's `applicable()` is short-circuited to False on production runs.

**Commit template:**
```
Erebos v0.34 Phase 0 ITER-28: loader-debt budget enforcement
v3 sec 4.8: 200-emission or 30-day hard cap on unfalsifiable
plugins. 8 loaderless plugins QUARANTINED with documented
unblock criteria. applicable_plugins(state) filters them out
of production runs. 6 tests pass. pivot/erebos_quarantine.md
shipped.
```

**Expected outcome:** the substrate stops inflating its "25/25 REGISTRY" framing. Quarantine documentation forces explicit unblock criteria.

---

### ITER-29 — Three-tier finding reclassification + whitepaper rewrite

**Goal:** v3 §4.10. Update the 9 substrate finding docs with reclassification. Rewrite whitepaper Section 5.

**Files to modify:**
- `pivot/erebos_whitepaper_v1_2026-05-27.md` — rewrite Section 5 + add reclassification appendix.
- Each of 9 substrate finding docs — add reclassification banner at top.

**New files:**
- `pivot/erebos_finding_reclassification_2026-05-27.md` — the reclassification doc with rationale per finding.

**Reclassification per v3 §4.10:**
- ITER-4 Salem moderation: catalog finding
- ITER-5 Salem band extension: catalog finding
- ITER-10 G10 Salem cluster detection: substrate finding
- ITER-13 G15 ledger MI: substrate finding
- ITER-13 G11 v2 degree-minima: catalog finding
- ITER-17 G23 1/log(N): catalog finding
- ITER-18 G17 phase transition M=1.26: catalog finding
- ITER-19 palindromic ≡ Salem: catalog finding
- Synthesis docs: meta (not findings; classification N/A)

Result: 2 substrate findings + 6 catalog findings + 0 mathematical + 0 literature-grade.

**Commit template:**
```
Erebos v0.35 Phase 0 ITER-29: three-tier finding reclassification
v3 sec 4.10: all 7 Mahler findings demoted to "catalog findings."
Only 2 of 8 substrate findings remain in "substrate" tier
(G10 Salem cluster detection + G15 ledger MI self-audit). Zero
mathematical findings; zero literature-grade. Whitepaper Section 5
rewritten. Reclassification rationale per finding documented at
pivot/erebos_finding_reclassification_2026-05-27.md. Substrate
evidence base is now calibration-honest.
```

**Expected outcome:** the whitepaper no longer over-credits the substrate. Public framing matches private epistemic state.

---

### ITER-30 — Phase 0 wrap

**Goal:** Run the full test suite; verify all Phase 0 commitments compose; write Phase 0 retrospective.

**Files to modify:**
- Various integration tests — verify the 5 new primitives compose (e.g., a loader using selection_discipline + catalog_profile + degeneracy_precondition + SurvivalCurve + predicate_handle in one ComposedClaim emission).

**New files:**
- `pivot/erebos_phase0_retrospective_2026-05-27.md` — Phase 0 retro.

**Test spec (5+ integration tests):**
- `test_loader_using_all_5_primitives_emits_valid_composed_claim`
- `test_quarantined_plugin_with_predicate_handle_still_blocked`
- `test_survival_curve_with_phase_transition_routes_via_kill_pattern_registry`
- `test_value_per_tick_baseline_computable_on_existing_ledger`
- `test_full_suite_passes_with_new_primitives_active`

**Commit template:**
```
Erebos v0.36 Phase 0 ITER-30: Phase 0 wrap + retrospective
All 9 Phase 0 commitments shipped. Integration tests verify 5
new primitives compose cleanly. 470 -> ~520 tests pass.
Substrate is ready for Phase 1 architecture proofs (ledger-memory
ablation harness, plugin degeneracy audit, earned-tier protocol,
BSD MVP loader). Phase 0 retrospective at pivot/erebos_phase0
_retrospective.md.
```

**Expected outcome:** Phase 0 complete; Phase 1 ready to begin at ITER-31.

---

## Sequencing dependencies

```
ITER-21 (selection_discipline) ──┐
ITER-22 (catalog_profile)      ──┤
ITER-23 (degeneracy_precond)   ──┤
ITER-24 (SurvivalCurve)        ──┤
ITER-25 (predicate_handle)     ──┤
ITER-26 (kill_pattern_registry)──┤
ITER-27 (cost-instrumentation) ──┤── all 9 independent of each other
ITER-28 (loader-debt budget)   ──┤   except ITER-30 (integration)
ITER-29 (reclassification doc) ──┤
ITER-30 (Phase 0 wrap)         ──┘── depends on all 9 above
```

The 9 primitives are independent and could be parallelized. They are sequenced one-per-iteration to enable disciplined commit history + per-iteration commit messages.

## Total Phase 0 budget

- **Code:** ~2500 lines (estimated; primitives are small, the discipline is in the contracts)
- **Tests:** ~60 new tests (estimated)
- **Documentation:** Phase 0 retrospective + reclassification rationale + quarantine doc
- **Substrate state at Phase 0 end:** 8 plugins quarantined; 14 of 17 still active; 5 primitives + cost layer in place; finding-reclassification public; ready for Phase 1.

## What's NOT in Phase 0

- Ablation experiments (Phase 2 / Sprint-1).
- Plugin degeneracy audit (Phase 1).
- Earned-tier protocol (Phase 1).
- BSD MVP loader (Phase 1).
- Per-plugin v3 implementations using DR outputs (Phase 3+; conditional on Sprint-1 pass).

---

**End Phase 0 implementation plan.** Beginning ITER-21 immediately.
