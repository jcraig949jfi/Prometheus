# Tensor Diagnostics

Tools that quantify the limits of what the (features × projections) tensor can support, NOT tools that make structural claims about it.

The distinction is load-bearing: every tool in this directory is a falsifier. The output of any diagnostic is a number plus caveats; that number alone is never sufficient to promote a structural claim about tensor geometry.

## Files

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
