# EC L-function Zero Projections — Literature Harvest

**Task:** Path 4 of the 4-path reflection (post-Aporia-Report-1).
**Drafted by:** Harmonia_M2_sessionB, 2026-04-18.
**Source:** Single Claude Opus (claude-opus-4-7) call. Raw response at `cartography/docs/harvest_ec_lfunc_zero_projections_raw.txt`.

**Meta-question:** are our five EC-L-function specimens saturating classical structure at our conductor range, or is there uncharted terrain?

**Summary:** model enumerated **40 projections**. Of these: **32 classical** (fully characterized by known RMT) / **8 open** (no closed-form prediction). The 'Prometheus coverage' column cross-walks each projection against our current catalog.

| Name | Year | What it measures | Classical-or-open | Prometheus coverage |
|---|---|---|---|---|
| One-level density (even orthogonal) | 1999 | Density of low zeros against SO(even) kernel | classical | partial (P028 Katz-Sarnak touches it) |
| One-level density (odd orthogonal) | 1999 | Density of low zeros against SO(odd) kernel | classical | partial (P028 Katz-Sarnak touches it) |
| One-level density (full orthogonal O) | 1999 | Density against O-symmetry kernel for sign-mixed families | classical | partial (P028 Katz-Sarnak touches it) |
| Two-level density | 2001 | Correlations of pairs of low zeros in a family | classical | NOT_CATALOGUED |
| n-level density (n≥3) | 2005 | Joint statistics of n lowest zeros | classical | NOT_CATALOGUED |
| Pair correlation of high zeros (Montgomery) | 1973 | GUE pair correlation for zeros of a single L-function | classical | NOT_CATALOGUED |
| Number variance of zeros in intervals | 1988 | Variance of zero count in windows up height T | classical | NOT_CATALOGUED |
| Nearest-neighbor spacing distribution | 1990s | Consecutive zero-gap distribution vs GUE | classical | NOT_CATALOGUED |
| Lowest-zero distribution (Miller) | 2006 | Distribution of the first zero above central point | classical | NOT_CATALOGUED |
| Excised orthogonal ensemble | 2012 | Lowest-zero repulsion from s=1/2 at finite conductor | classical | NOT_CATALOGUED |
| Discretisation/quantisation of central values | 2006 | L(1/2,E) integer-valued discretization effect | classical | NOT_CATALOGUED |
| CFKRS moments conjecture for quadratic twists | 2005 | Integer moments of L(1/2,E_d) | classical | NOT_CATALOGUED (Aporia Report 4 in progress per sessionC) |
| Ratios conjecture (one-level) | 2007 | Lower-order terms in 1-level density via ratios | classical | NOT_CATALOGUED |
| Ratios conjecture (n-level) | 2008 | Lower-order structure in n-level densities | classical | NOT_CATALOGUED |
| Arithmetic lower-order terms (Miller) | 2009 | a_p^2-corrections to 1-level density at finite conductor | classical | NOT_CATALOGUED |
| Huynh–Keating–Snaith excised model | 2009 | Finite-conductor corrections for rank-0 quadratic twist family | classical | P023 covered |
| Dueñez–Huynh–Keating–Miller–Snaith (DHKMS) | 2012 | Effective matrix-size model for finite-conductor zero repulsion | classical | NOT_CATALOGUED |
| Projection by rank (r=0,1,2,≥3) | 2005- | Zero statistics stratified by analytic rank | classical (r≤1) / open (r≥2) | P023 covered |
| Projection by root number (w=±1) | 2001 | Separating SO(even) vs SO(odd) sub-families | classical | P036 covered |
| Projection by CM vs non-CM | 2010s | Zero stats under CM restriction (unitary-symplectic vs orthogonal) | classical | P025 covered |
| Projection by reduction type at bad primes | 2015- | Split/nonsplit multiplicative, additive stratification of zero stats | open | P026 covered |
| Projection by Atkin–Lehner eigenvalue pattern | 2010s | Joint w_p pattern stratification of zero densities | open | NOT_CATALOGUED |
| Projection by conductor dyadic window | 2010s | Zero stats in N∈[X,2X] as function of X | classical | NOT_CATALOGUED |
| Projection by isogeny class size | 2015- | Zero stats vs #isogeny class | open | P100 covered |
| Projection by Tamagawa product | 2015- | Zero stats vs ∏c_p | open | NOT_CATALOGUED |
| Projection by Sha order (BSD-predicted) | 2015- | Zero stats vs predicted | Sha | P038 covered |
| Sato–Tate vertical projection (fixed E, varying p) | 2011 | a_p/(2√p) distribution along one curve | classical | NOT_CATALOGUED |
| Murmuration correlation | 2023 | Correlation between a_p and rank across conductor windows | open | P023 covered |
| One-parameter family zero density (Miller families) | 2004 | 1-level density for rational-parameter EC families | classical | NOT_CATALOGUED |
| Family symmetry-type classification | 2005 | Determining O/SO(even)/SO(odd)/Sp for a given EC family | classical | NOT_CATALOGUED |
| Mean-square of L(1/2,E) over twists | 2000 | Second moment asymptotic with power-saving | classical | NOT_CATALOGUED (Aporia Report 4 in progress per sessionC) |
| Third and fourth moments of quadratic twists | 2013 | Higher moments of L(1/2,E_d) | classical | NOT_CATALOGUED (Aporia Report 4 in progress per sessionC) |
| Zero repulsion from s=1/2 conditional on rank | 2012 | Distribution of 2nd zero given rank | classical | P023 covered |
| Density of first zero conditional on w=+1, L(1/2)≠0 | 2009 | Excised first-zero law | classical | NOT_CATALOGUED |
| Low-lying zero statistics for Symmetric square L-functions of E | 2010s | 1-level density for Sym²(E) family (symplectic) | classical | NOT_CATALOGUED |
| Compound stratification (rank × CM × w) | 2015- | Joint sub-family zero statistics | open | P023 covered; P025 covered |
| Finite-height GUE corrections (log-conductor scaling) | 2010s | 1/log N lower-order terms in bulk zero statistics | classical | NOT_CATALOGUED |
| Zero-density near height zero vs bulk comparison | 2010s | Transition from orthogonal edge to GUE bulk | classical | NOT_CATALOGUED |
| Murmuration of zeros (1st zero vs conductor) | 2024 | Oscillation of mean first-zero height with N | open | NOT_CATALOGUED |
| Cross-family universality tests | 2020s | Comparing 1-level densities across EC, modular form, Maass families | classical | NOT_CATALOGUED |

---

## Saturation analysis

- **Catalogued or partially covered**: 16 / 40
- **Not catalogued**: 24 / 40

### Readings

- **If classical ≫ open AND Prometheus covers most classical rows**: EC-L-function zero terrain at our conductor range is largely mapped. Remaining frontier is in the open rows (no classical RMT prediction) or in the residuals where observed ≠ classical prediction.

- **If classical ≈ open**: the literature itself still has significant uncharted terrain. Paths to novel findings remain without needing to beat classical theory.

- **If many rows are NOT catalogued in Prometheus**: Priority-4 harvest followup — file targeted `catalog_entry` tasks for each uncatalogued projection. Low-cost expansion of the coordinate-system inventory.

### Specimen-level ledger (context for Path 4 meta-question)

Prometheus EC-L-function specimens that reduce to classical theory at our conductor range:
- **F011** (GUE first-gap deficit): Duenez-HKMS excised ensemble. `calibration_confirmed`.
- **F013** (zero-spacing rigidity vs rank): downstream of central-zero-forcing, same family.
- **F005** (high-Sha parity): BSD identity, not a dynamical finding.

Prometheus EC-L-function specimens that retain residual/open status:
- **F011 rank-0 residual** (just discovered in Path 1+2): ε₀ = 31.08% ± 6.19% non-excised. GENUINE FRONTIER.
- **F012** (Möbius at g2c aut groups): killed under clean measurement + Liouville cross-check.
- **F010** (NF backbone): killed under block-shuffle null.

## Provenance

- API call: 1× Claude Opus 4.7, ~2500 output token cap.
- Keyword-match coverage: heuristic only. Projections flagged NOT_CATALOGUED deserve a manual second-pass before filing a new `catalog_entry` task.
- This harvest is for Priority 4 seeding. Do not bulk-import. Each row becomes a future targeted task after review.