# zoo.diagnostics — Descriptor-Collapse Audit

**Status:** playground-tier; promoted to its own module in Phase 3 as the reusable core of the zoo instrument.
**Scope:** general — applies to any MAP-Elites or quality-diversity search that places individuals in a grid of behavior descriptors.

---

## What this module does

MAP-Elites archives look rich by construction: a 20×20 grid *looks* two-dimensional. The module checks whether the descriptors placing individuals in that grid are actually independent along the search path, or whether the apparent 2D structure is a 1D ridge wearing two costumes.

The core operation: compute pairwise Pearson correlations across all evaluated individuals for every pair of numeric descriptors. Flag pairs with |r| ≥ a threshold (default 0.9) as candidate dimensional collapse. Separately, correlate function-level (batch-level) descriptors across items to check whether the intrinsic axis predicts the observed compressibility.

**Why this is the real contribution of the zoo project.** The TT representation, MAP-Elites loop, and evolutionary operators are off-the-shelf pieces. The audit is what catches the failure mode where the map secretly collapses. External reviewer (2026-04-24) identified this as generalizable beyond TT approximation.

---

## API (current, Archive-coupled)

```python
from zoo.diagnostics.correlation import correlation_audit, cross_function_audit

# Per-archive correlation across evaluation history
result = correlation_audit(
    archive,                                  # zoo.map_elites.grid.Archive
    threshold=0.9,
    function_level_descriptors={"spectral_alpha": 1.83},  # function-level, logged only
)
# result["flagged"]: list of pairs above threshold
# result["matrix"]:  full correlation matrix
# result["warning"]: populated if any pair above threshold

# Cross-function: batch descriptors vs archive summaries
cross = cross_function_audit(archives_dict, function_descriptors_dict)
# cross["spectral_alpha_vs_log_min_error"]: correlation across functions
```

## Design intent: decouple from Archive (future work)

The current `correlation_audit(archive, ...)` binds to `zoo.map_elites.grid.Archive`, which is zoo-specific. A one-line generalization would accept any iterable of dicts with numeric descriptor keys:

```python
def correlation_audit_generic(
    items: list[dict[str, float]],
    threshold: float = 0.9,
    batch_descriptors: dict[str, float] | None = None,
) -> dict: ...
```

That's the clean version. We haven't made the cut yet because the zoo Archive carries slightly more (`ranks`, `cell`, `generation`) that the audit reports on. Once a second use site emerges, refactor.

---

## When to use this

Any time a search process explores individuals characterized by ≥2 numeric behavior descriptors and you want to know whether those descriptors are independent.

Failure mode this catches:
- **"Map looks 2D, trajectory is 1D."** Rank-perturbation in tensor trains, learning-rate sweeps in DL, hyperparameter GA, anything where a single knob is driving multiple derived metrics.

Failure modes this does NOT catch:
- Non-linear dependence (use mutual information for that).
- Dependence that emerges only in tails (use tail-conditional correlation).
- Dependence mediated by a third variable (use partial correlation).

The default Pearson audit is a first-line filter. It is cheap, interpretable, and catches the gross case. The zoo's Phase 2 `pairwise_tanh` result was gross: log_params ↔ log_error = −0.968.

---

## Discipline: reading a flagged result

When the audit flags a pair, three questions:

1. **Is it structurally forced?** `avg_rank ↔ log_params` always correlates because params is a polynomial in ranks. Not a real collapse. Maintain a list of tautological pairs to exclude.
2. **Is it saturation?** When one descriptor hits a floor (machine epsilon error, rank ceiling), the correlation becomes degenerate. Check ranges before interpreting.
3. **Is it genuine collapse?** If neither 1 nor 2 applies, the two axes are not independent along the search path actually taken. The grid is measuring 1D structure. Fix: add a rank-orthogonal descriptor and re-test.

---

## Relationship to the rest of zoo

- **Inputs:** `zoo.map_elites.grid.Archive` (current), will generalize.
- **Consumers:** `zoo.experiments.run_phase2`, `zoo.experiments.run_phase3` — both call into the audit at stage end.
- **Composes with:** any zoo descriptor (`zoo.descriptors.stability`, `zoo.descriptors.rank_profile`, `zoo.descriptors.spectral`) — the audit is descriptor-agnostic.

---

## Provenance

Introduced in zoo Phase 2 after explicit warning that MAP-Elites axes risk becoming proxies for reconstruction error. Fired on the one frontier function in the Phase 2 catalog. Promoted to its own module in Phase 3 per external review calling it "the real contribution" of the zoo project.
