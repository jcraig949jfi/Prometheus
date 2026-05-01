# Tensor Diagnostics

Tools that quantify the limits of what the (features × projections) tensor can support, NOT tools that make structural claims about it.

The distinction is load-bearing: every tool in this directory is a falsifier. The output of any diagnostic is a number plus caveats; that number alone is never sufficient to promote a structural claim about tensor geometry.

## Files

### `descriptor_collapse_audit.py`

**Purpose:** detect whether a set of named descriptors is collapsing onto a lower-dimensional manifold, with built-in null discipline and conditioning. Substrate-tier primitive callable from any session — the lift-and-generalize of the Zoo project's descriptor-collapse audit (Zoo closed at v3.4, 2026-04-26).

**Why this exists:** every Harmonia session that touches MAP-Elites, archive search, or any descriptor-pair structure should get this audit as an importable function rather than re-deriving it. Per `pivot/harmoniaD.md` §6 Move 1: industrialize what is already proven. The Zoo modules (`exploratory/zoo/diagnostics/{correlation,nonlinear}.py` + `exploratory/zoo/experiments/analyze_conditional_mi.py`) remain unchanged; this is the substrate-tier copy with generic API.

**What it does — five layers, in order:**

1. **Pearson correlation matrix** — pairwise; flags |r| ≥ `pearson_threshold` (default 0.9). Catches linear collapse only.
2. **Distance correlation** — Szekely-Rizzo-Bakirov; pairwise; flags dCor ≥ `dcor_threshold` (default 0.5). Zero iff independent (under finite-moment assumptions); positive under any dependence.
3. **KSG mutual information** — Kraskov-Stogbauer-Grassberger k-NN estimator; in nats; flags MI ≥ `mi_threshold_nats` (default 0.5 nats ~ 0.72 bits). Distribution-free.
4. **Shuffled null per pair** — empirical null distribution of MI and dCor by permuting one variable against the other; reports z-score and one-sided p-value. Auto-runs on any pair flagged at the shallow tier.
5. **Within-band conditional MI** — partitions by quantiles of one variable (or an explicit `condition_on` array) and recomputes MI within each band. If the global coupling collapses to baseline within bands, the dependence is boundary-explained; if it persists, the coupling is structural.

**Composite verdict (audit_summary):**

| Condition | Verdict |
|---|---|
| No shallow flags | `CLEAR` |
| Shallow flags exist but `deep_on_flagged=False` and no `deep_pairs` covered them | `SHALLOW_FLAGGED_DEEP_NOT_RUN` |
| Shallow flags exist; all deep-evaluated pairs not-above-null OR boundary-explained | `BOUNDARY_EXPLAINED` |
| ≥1 deep pair above-null AND not boundary-explained | `STRUCTURAL_COUPLING_SUSPECTED` |

**Run:**

```python
from harmonia.memory.diagnostics.descriptor_collapse_audit import descriptor_collapse_audit
import numpy as np

descs = {
    "log_params": np.array([...]),
    "log_error":  np.array([...]),
    "rank":       np.array([...]),
}
result = descriptor_collapse_audit(descs, rng_seed=0)
print(result["audit_summary"]["verdict"])
```

Validator (per discipline):

```bash
PYTHONPATH=. PYTHONIOENCODING=utf-8 \
python harmonia/memory/diagnostics/validate_descriptor_collapse_audit.py
```

Tests (23 cases — AC1 through AC4 plus per-layer unit tests):

```bash
PYTHONPATH=. PYTHONIOENCODING=utf-8 \
python -m pytest harmonia/memory/diagnostics/test_descriptor_collapse_audit.py -v
```

**Pass/fail interpretation:**

| Output | Meaning |
|---|---|
| `audit_summary.verdict == "CLEAR"` | No shallow flags. No evidence of collapse on any pair. Note this is a falsifier, not proof of independence. |
| `audit_summary.verdict == "BOUNDARY_EXPLAINED"` | ≥1 pair flagged shallow, but the within-band conditional MI dropped below the threshold-half heuristic. Coupling is consistent with a geometric/boundary effect. |
| `audit_summary.verdict == "STRUCTURAL_COUPLING_SUSPECTED"` | ≥1 pair has coupling above the shuffled null AND coupling persists within bands. NOT a positive finding — a flag for follow-up under proper null discipline (`NULL_BSWCD@v2`, `null_protocol_v1.md`) and Pattern 30. |
| `audit_summary.verdict == "SHALLOW_FLAGGED_DEEP_NOT_RUN"` | Shallow flags exist but no deep-tier evidence was collected for them (caller passed `deep_on_flagged=False` and no `deep_pairs`). The audit is refusing to assert boundary-explained without data; rerun with deep tier enabled or supply `deep_pairs`. |
| Any layer's `flagged` list non-empty alongside CLEAR verdict | Should never happen; would be a verdict-logic bug — file an issue. |

**What this tool does NOT do:**

- Does NOT prove independence. Even MI ≈ 0 has finite-sample noise; KSG can give small positive values for genuinely independent variables.
- Does NOT replace block-shuffle null discipline (`NULL_BSWCD@v2`) for any structural finding. This is a fast pre-flight check, not a final verdict.
- Does NOT detect Pattern 30 algebraic-identity coupling. Algebraically-coupled descriptors register as collapsed here (correct shallow signal), but the lineage diagnosis must come from `harmonia/sweeps/pattern_30.py`.
- Does NOT generalize to vector-valued descriptors. Each entry in the input dict must be 1-D. Multi-D extension is future work.

**Provenance:**

- Source: lifted from `exploratory/zoo/diagnostics/{correlation,nonlinear}.py` + `exploratory/zoo/experiments/analyze_conditional_mi.py` (Zoo project closed at v3.4, see `project_zoo_closed_at_v34.md`).
- Pivot directive: `pivot/harmoniaD.md` §6 Move 1.
- Proposal: `harmonia/memory/protocols/descriptor_collapse_audit_proposal.md` (sessionB, 2026-05-01).
- Tests: `harmonia/memory/diagnostics/test_descriptor_collapse_audit.py` (23 cases — AC1-AC4 plus per-layer units; all pass).
- Validator: `harmonia/memory/diagnostics/validate_descriptor_collapse_audit.py`.

**Known issues:**

- Within-band conditional MI uses KSG; KSG is biased on small n, so bands with `n < min_n_per_band` (default 20) are skipped. With small total n (< 80) and `n_bands=4`, the conditional layer may report `n_bands_valid=0` and `mean_within_band_mi=None`; in that case verdict falls through to whatever shallow flags exist with no boundary-explained downgrade available. Mitigation: bump n or reduce `n_bands`.
- The boundary-explained heuristic is `mean_within_band_mi < mi_threshold_nats / 2`. Inherited from the Zoo `analyze_conditional_mi.py` rule (`< 0.3` against threshold 0.5). Sound for moderate sample sizes; may need recalibration if used at very large n with very weak coupling.
- KSG MI threshold of 0.5 nats is moderate-tight; for descriptor pairs that are weakly but genuinely dependent (e.g. correlation ~ 0.3), Pearson and dCor may both fall below threshold while KSG also does — the audit will return CLEAR. This is the right behavior for collapse detection but means the tool is conservative on weak dependence.

### `missingness_confound_v01.py`

**Purpose:** quantify how much of any rank-flavored claim about the tensor is attributable to the MNAR observation pattern alone.

**Why this exists:** Geometry 1 (`harmonia/memory/geometries.md`) was retracted on 2026-04-19 because the original SVD/SVT estimates of "latent rank ~12–16, 3D core captures 48–74% of variance" were not defensible against the MNAR + 0-as-missing structure. This tool does NOT remediate that retraction — it makes it quantitative.

**What it does:**

1. Loads the tensor from `harmonia/memory/landscape_tensor.npz`.
2. Computes Φ = effective-rank from PSD-clamped pairwise-complete Pearson correlation matrix on column pairs with ≥5 overlapping observations. Auditor refinement 1 (PSD clamp) and refinement 2 (min_overlap=5) applied.
3. Compares Φ_observed against four null distributions (auditor refinement 4: both null-3 variants run):
   - **null_random** — fully random observation pattern + value permutation. Coarsest. Breaks both M's pattern and value-position binding.
   - **null_marginal** — Curveball-style degree-preserving swap on M, then permute values. Preserves both row and column marginal observation counts; breaks the joint.
   - **null_3a (within-rows)** — keep M exactly; permute values within each row's observed cells. Tests for cross-column structure beyond per-row marginals.
   - **null_3b (within-cols)** — keep M exactly; permute values within each column's observed cells. Tests for cross-row structure beyond per-col marginals.
4. Reports raw-phi gaps (primary) and σ gaps (secondary) for each null. Auditor refinement 3: explicit ratio thresholds rather than the original `≫` notation:
   - `pass_random_over_marginal` requires `|raw_phi_gap_random| / |raw_phi_gap_marginal| ≥ 2.0`
   - `pass_marginal_over_strictest` requires `|raw_phi_gap_marginal| / max(|gap_3a|, |gap_3b|) ≥ 1.5`
5. Reproducibility check: 5 seeds, gaps reported per seed; sd across seeds flagged if > 0.2σ.

**Why both raw-phi and σ gaps:** Empirically, `null_random` produces phi values that concentrate near full effective rank P with very small spread (sd as low as 1e-4). σ-gap = (phi_obs − null_mean) / null_sd then becomes unstable across seeds. Raw-phi gap is stable and interpretable in phi units; σ-gap is the secondary diagnostic.

**Run:**

```bash
AGORA_REDIS_HOST=... AGORA_REDIS_PASSWORD=...   # not required for this tool
cd D:/Prometheus
python harmonia/memory/diagnostics/missingness_confound_v01.py
```

Wall clock ~2m40s for 5 seeds × 1000 perms × 4 nulls. Output goes to `missingness_confound_v01_results.json` in the same directory.

**Pass/fail interpretation:**

| Condition | Meaning |
|---|---|
| `pass_overall=True` | Claim about column-correlation structure survives all four nulls at the configured ratio thresholds. |
| `pass_random_over_marginal=False` | Marginal-preserving null reproduces too much of the random-null effect. The observation pattern's row/col marginals already explain most of what looks like structure. **Geometry-1-retraction-style risk live.** |
| `pass_marginal_over_strictest=False` | Strict permutations within rows or cols already reproduce most of the marginal-null effect. The column-correlation structure beyond per-row/per-col marginals is small. |
| `within_0p2_sigma=False` (any null) | Across-seed gap variance exceeds 0.2σ. Bump n_perms or investigate distributional collapse (especially null_random). |

**What this tool does NOT do:**

- Does NOT estimate the tensor's latent rank. The current data does not support that claim under any method, period.
- Does NOT make any aggregate claim about the tensor as a whole. MNAR forbids that until controlled (F,P) sampling protocol is run (Geometry-1 retraction branch (b)).
- Does NOT replace SVT-on-ordinal-data done correctly. That's a separate project (probit/cumulative-link factorization with explicit attention model).
- Does NOT discharge the retraction. Promoting any rank claim requires the controlled-sampling protocol AND a properly-specified ordinal model AND cross-validation across worker cohorts AND survival on this diagnostic.

**Provenance:**

- Proposal: `harmonia/memory/protocols/missingness_confound_proposal.md` (sessionB, 2026-04-29 :13)
- Audit: Harmonia_M2_auditor `CONCUR_WITH_NOTES` 1777461099984-0, 4 refinements applied
- First implementation: sessionB, 2026-04-29 :23
- First audit-ready run: 2026-04-29 :33

**Known issues:**

- `null_random` σ-gap unstable: phi distribution concentrates near full rank P; σ-gap can blow up to ±10^4 when null sd is tiny. Mitigation: report raw-phi gap as primary; treat σ-gap as confirmatory only when null sd ≥ 1e-3.
- 31×37 tensor at 9% density gives small Φ-room (Φ_observed ≈ 36.28 vs P = 37 ceiling). All gap magnitudes are sub-unit in phi terms. The diagnostic is at the edge of sensitivity at this density. Investigation: alternative Φ choices that have more dynamic range at sparse densities.
- Curveball degree-preserving swap (`null_marginal`) uses 2000 swaps as default. Mixing time not validated. May need to be increased for tensors with stronger constraint structure.

## Discipline

Every tool in this directory MUST:

1. State explicitly what it does NOT support, in a CAVEATS block included in every output.
2. Be falsifiable on its own terms — i.e., have a reproducible pass/fail criterion, not just "did it run."
3. Have a proposal file in `harmonia/memory/protocols/` reviewed by at least one peer session before initial commit.
4. Reference the relevant null-discipline anchors (`PATTERN_21@v1`, `NULL_BSWCD@v2`, `NULL_PLAIN@v1`, etc.) explicitly in code comments where applicable.
