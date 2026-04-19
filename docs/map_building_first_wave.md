# First-Wave Retrospective: Map-Building Experiment in a Multi-Agent Math Research Project

**Audience:** frontier models reviewing this artifact for methodological critique.
**Tone:** observational. No claims of novelty or discovery; just what the experiment produced and where it may be methodologically thin.
**Date:** 2026-04-19.
**Repo:** `github.com/jcraig949jfi/Prometheus` (relevant commits cited inline).

We would be particularly grateful for critiques on the numbered items in §6.

---

## 1. Background

Project Prometheus is a multi-agent research environment where several instances of a large language model (plus specialized roles like database caretaker, literature scanner, etc.) work in parallel on computational-number-theory data from the L-Functions and Modular Forms Database (LMFDB). Typical tasks involve testing whether some empirical pattern in elliptic curves, number fields, or automorphic forms survives under permutation nulls.

For several sessions the default mode was *problem-solving*: hypotheses were generated, the battery was run, findings were either SURVIVED or KILLED. This produced many individual results but relatively little sense of accumulated structure.

In April 2026 we reframed the project charter. The text is in `docs/landscape_charter.md`; the short version is: *domains are projections, not territories.* Rather than search for "bridges between domains," describe the landscape as a set of invariance measurements under many coordinate systems. The product is not a discovery — it is a map.

## 2. What "the map" is, operationally

We encode the map as a 2-axis matrix `T[F, P]` where:
- Rows are **features** (F-IDs): specific empirical claims or anomalies (currently 31, spanning calibration anchors like Modularity/Mazur-torsion/BSD-parity through contested items like GUE first-gap deficit or Sha-period correlation)
- Columns are **projections** (P-IDs): coordinate systems we can measure through (currently 37, including scorers, stratifications, null models, and preprocessing steps)
- Values are integers in {-2, -1, 0, +1, +2}: collapse / tested-but-unresolved / untested / resolves / resolves-and-survives-permutation-break

Additional artifacts:
- Two relational graphs: `feature_edges` (supersedes, parallel_density_regime, stratification_reveals_pooled_artifact, etc.) and `projection_edges` (refines, nests, tautology_of, dual_to)
- A `pattern_library.md` of recognitions we try to apply systematically
- A `symbols/` subtree for compound primitives used in inter-agent communication (operator / shape / constant / dataset / signature), with strict versioning discipline at `harmonia/memory/symbols/VERSIONING.md`

Live state is mirrored to Redis so agents across machines see the same tensor without git-pull latency (`harmonia/memory/TENSOR_REDIS.md`).

## 3. The first map-building wave

On 2026-04-18/19 we delegated seven non-overlapping roles to seven agents, each executing against the existing map rather than generating new hypotheses:

| Role | Job | Worker | Commit |
|---|---|---|---|
| Cartographer | Render map as live HTML heatmap with hover + edge graphs | Charon | f566e46c |
| Gap-filler | Walk untested (F, P) cells, add projections, fill | Harmonia sessionC | ae71bd26 + 2 |
| Re-auditor | Run block-shuffle null on every +1 cell, promote or demote | Harmonia sessionD | 043ba782 + 3 |
| Edge-weaver | Extract relational edges from feature/projection descriptions | Mnemosyne | 74aab3fb + 5 |
| Rank analyst | SVD of invariance matrix; test "low-rank core" hypothesis | Koios | 5f229878 |
| Query-runner | Compute dense-row/dense-column/predictive-gap queries | Kairos | 24d17e98 |
| Literature-mapper | Map 246 papers from S2/OpenAlex scan onto (F, P) cells | Aporia | 646d6ca6 |

Tensor state before wave (v1): 31×25, 82 non-zero cells (10.58% density). +2 count: 22. +1 count: 28.

Tensor state after wave (v14): 31×37, 103 non-zero cells (8.98% density). **+2 count: 44.** +1 count: 7.

Density dropped because the Gap-filler added 12 projection columns faster than the Re-auditor filled cells. Non-zero absolute count grew by 21 (+26%). Durable count (+2) doubled. Count of resolved-but-not-verified cells (+1) dropped from 28 to 7 as the re-auditor promoted most of them.

## 4. Findings from the wave

These are what the workers' scripts produced. They are stated as observations; we have not claimed novelty on any of them and would welcome pushback on the inferences.

### 4.1 SVD result (Koios 5f229878)

Three rank estimators on the invariance matrix:
- Method A — naive SVD treating 0 as zero: effective rank ≈ 12
- Method B — SVT nuclear-norm completion treating 0 as missing: rank ≈ 14–16
- Method C — observed-only agreement matrix: rank ≈ 15

A 3-dimensional core captures 48–74% of variance across methods. The three dominant axes, interpreted from the top-3 left-singular vectors, are labeled by the worker as:
1. signal/noise (separates calibration-confirmed from killed cells)
2. kill/survive (separates durable from collapse-under-null)
3. domain connectivity (separates features with wide cross-projection structure from narrow ones)

We had previously hypothesized the matrix would be effectively rank ≤ 5 (a "low-rank core" interpretation of the landscape-is-singular charter). The strong form is falsified at current density. We have written the weaker form — "low-rank core plus higher-dimensional residual" — as the amended reading, with an explicit caveat that at 8.98% density the rank estimate is noisy.

### 4.2 F043 (BSD-Sha–period anticorrelation) — highest z-score durability result

F043 is an empirically-observed negative correlation between `log(Sha)` and `log(A)` on rank-0 elliptic curves in the conductor decade [10⁵, 10⁶), where `A = L(1,E) · (#torsion)² / #Sha` (i.e., the product of the real period and the Tamagawa product, as isolated from the BSD formula).

- Observed: `corr(log Sha, log A) = -0.4343` on n ≈ 60,000 rank-0 EC
- Null (block-shuffle within conductor decile, n_perms=300): mean ≈ 0, std ≈ 0.0012
- `z_block = -348.05`

The anti-correlation was initially visible in the Sha-depletion pattern of the low-L tail (worker T4, commit cbe7b623) but was decomposed via the BSD identity into a period/Tamagawa effect (worker U_D, commit 111d6288).

### 4.3 F011 (GUE first-gap deficit) layer separation

F011 is the measured ~38% deficit in first-gap variance of low-lying zeros of elliptic-curve L-functions relative to the GUE pair-correlation prediction.

After the Aporia literature scan (Report 1) and subsequent Ergon/sessionB followups:
- The bulk deficit is consistent with the Duenez-Huynh-Keating-Miller-Snaith (2011) excised ensemble — deficit shrinks monotonically with conductor (slope −7.17 per log-decade, z = −54.2), first-gap deficit much larger than second-gap deficit (z = +96.97).
- A rank-0 residual of ~23% (under classical `eps_0 + C/log(N)` ansatz) remains after the excised-ensemble bulk is subtracted. The residual is durable under block-shuffle with the `torsion_bin` stratifier (z_block = 4.19).
- sessionB fit three decay forms; the eps_0 estimate ranges 22.9% to 35.8% depending on fixed ansatz. Joint α-free fit is under-constrained.
- Three precision corrections happened during the wave:
  (a) A previous self-audit claim of `z_block = 10.46` used a degenerate stratifier (`class_size`, where one value covers 59% of curves producing null_std=0 and spuriously inflated z). Corrected to z_block = 4.19 under a balanced stratifier.
  (b) F011 × P024 torsion collapsed at z = 1.37 under block-shuffle — my earlier claim that F011 resolves under torsion was wrong. Demoted to -1.
  (c) F011's decomposed "LAYER 1 calibration (excised ensemble) + LAYER 2 frontier (residual)" tier is a split designation that may be a symptom of the framework rather than a real dual structure.

### 4.4 Calibration anchor growth

Previously confirmed anchors: F001 Modularity (EC↔MF a_p agreement, 100.000% over 437K), F002 Mazur torsion classification, F003 BSD parity, F004 Hasse bound, F005 High-Sha parity.

Added during this and recent work:
- F008 Scholz reflection: |r₃(K*) − r₃(K)| ≤ 1 verified across 344,130 imaginary-real quadratic pairs. Zero violations. 71.5% equality / 28.5% differ by exactly 1. This is simply Scholz 1932 applied at scale — a proved theorem of our tooling against itself, not a novel finding.
- F009 Serre+Mazur lineage: `primes(torsion) ⊆ nonmax_primes` verified across 1,385,133 non-CM EC. Zero violations. Again, a known theorem test.

These anchors function as instrument-health checks. If any violates on a fresh dataset, we stop and debug.

### 4.5 Query-runner report (Kairos 24d17e98)

Q1 (dense rows): F011 is the densest feature (11 of 12 tested projections positive after correcting P024). F041a and F013 follow.

Q2 (principal columns): P020 (conductor conditioning) and P023 (rank stratification) each resolve 9 features. These are the two most-loaded columns and are consistent with axes 1 and 3 in the SVD interpretation.

Q3 (predictive gaps): the top-ranked cells (by neighbor density) are F013 × P020 and F014 × P020.

Q4 (contradictions): zero contradictions found across the specimens registry. Given how lightly the registry tracks duplicate measurements, this is a weak signal; absence of contradiction may reflect absence of replication.

Q5 (kill candidates): F012 (Möbius bias, already tier=killed), F020 (Megethos, already killed), F032 (Knot silence, still listed as data_frontier).

## 5. Structural alignments with existing literature

We make no claim of novel mathematics. Where our measurements correspond to known results, here are the alignments as the workers recorded them:

- **F001 Modularity**: Wiles et al. proved modularity theorem; our measurement is verification.
- **F002 Mazur torsion**: Mazur's classification theorem; our measurement is verification.
- **F003 BSD parity + full BSD identity at 10⁻¹² on rank 2–3**: Kolyvagin + Gross-Zagier for rank 0–1; higher rank is conditional on BSD.
- **F004 Hasse bound**: Hasse's theorem; trivially verified.
- **F005 High-Sha parity**: consequence of the proved BSD parity.
- **F008 Scholz reflection**: Scholz (1932) theorem; our test is data-quality verification.
- **F009 torsion ⊆ nonmax primes**: Serre open-image + Mazur classification; known.
- **F011 LAYER 1 excised ensemble**: Duenez-Huynh-Keating-Miller-Snaith (2011) predicts the bulk deficit we see; Harmonia sessionC literature scan (c9a7543a) confirmed six of seven F011-related findings map to known literature. Katz-Sarnak 1999 predicts the low-tail sign structure we observe.
- **F011 LAYER 2 residual**: no clean published prediction for the ~23% rank-0 residual at finite conductor. Miller 2009 ("A symplectic test of the L-functions Ratios Conjecture") is a candidate; we have not done the closed-form calculation yet.
- **F014 Lehmer spectrum**: Charon's structural result that the trinomial M(xⁿ − x − 1) sequence sets a lower floor converging to 1.381 (commit eb6d31df) is an algebraic fact about Mahler measures of specific trinomials, not a new claim about Lehmer's problem.
- **F041 (original Keating-Snaith convergence rate)**: was demoted after sessionC showed it was first-moment-drift artifact; rank-1 correct exponent `k(k+1)/2` matches Conrey-Snaith (2007).
- **F041a (rank-2+ moment slope monotone in num_bad_primes)**: sessionC literature scan found no standard literature prediction for the nbp-monotonicity at rank ≥ 2; Wachs (2026) confirms sha-direction murmuration but not the isogeny/nbp axis directly. Flagged as a frontier-but-unverified observation pending CFKRS rank-2 computation.
- **F042 (CM disc=-27 L-value depression)**: literature match to Gross (LNM 776, 1980) and Rodriguez-Villegas-Zagier (1993) non-maximal-order Deuring compression. Quantitative precision (6.66x enrichment) is our data point; qualitative structure is not new.
- **F043 (BSD-Sha–period anticorrelation)**: sessionC literature scan cites Goldfeld + Cremona + Bhargava-Shankar for the low-L period-dominance framing (82.1% decomposition share is a sharp instance of known structure). The specific empirical anticorrelation corr = -0.52 does not appear in any paper we located, but we have not done an exhaustive search. This is where we would most welcome literature pointers.
- **F044 (rank-4 corridor, disc = conductor exact in 2085/2086)**: Charon's observation. We have not located a theorem stating that additive reduction is forbidden at rank ≥ 4; conversely, we have not ruled out LMFDB selection bias (the rank-4 curve set in LMFDB comes primarily from Stein/Elkies/Dujella rank-record constructions which may favor prime conductor via isogeny-class searches).

## 6. Items where we would welcome critique

Itemized because these are the specific places the internal review cannot see its own blind spots.

**6.1.** The "landscape-is-singular" framing re-labels standard multi-feature statistical hygiene as a charter-level commitment. Does this framing actually produce different behavior than conventional multi-test methodology, or is it bureaucratic re-packaging? Specifically: would a good statistical-ecology workflow produce the same maps without the vocabulary?

**6.2.** Pattern 20 ("pooled statistics can be marginal artifacts") and Pattern 21 ("null-model choice matters as much as projection choice") are being treated as framework patterns with version increments and drafting policies. We suspect these are basic statistical hygiene dressed up. Do they have independent content beyond "report confidence intervals, use stratified nulls, check robustness"?

**6.3.** SVD on a ~10% dense matrix with values restricted to {-2, -1, 0, +1, +2}. The "low-rank core plus residual" amendment hinges on this decomposition being meaningful. Is it? Specifically: (a) is nuclear-norm completion (SVT) the right method for a discrete-valued matrix where "0" means "missing" rather than "zero"; (b) is the 3-component interpretation fit to signal or noise; (c) do the three axis labels (signal/noise, kill/survive, domain-connectivity) reflect the actual decomposition or are they a post-hoc story?

**6.4.** F043's `z_block = -348` on `corr(log Sha, log A)`. The statistic is the Pearson correlation on log-transformed BSD factors. Under block-shuffle within conductor decile, null std is ≈ 0.0012 — extremely tight. Possible methodological concerns we want checked:
- Does the null model correctly reflect the relevant exchangeability? Within a conductor decile, curves still differ in rank, Sha order, and all other BSD factors — is shuffling L-values against Sha values (holding conductor bin) the right null for this particular correlation?
- Is the observed correlation close to what the BSD identity implies for a typical sha-rank distribution, and is z = -348 actually just detecting the BSD identity itself rather than any empirical deviation?
- Selection: we restricted to sha-1 curves for the main test — does this restriction create an artifactual correlation structure?

**6.5.** Block-shuffle-within-conductor-decile (NULL_BSWCD@v2) is the default null for most durability claims. Is it the *correct* null for, e.g., F013 (rank-slope interaction) or F044 (rank-4 corridor)? Different features may need different block structures, and we may be under-specifying.

**6.6.** The 3 "principal axes" interpretation (conductor, rank, domain-connectivity) maps directly onto the two most commonly-available stratifications in our data (conductor and rank). Is this a genuine structural finding about the tensor, or an artifact of what coordinate systems have been implemented and tested most?

**6.7.** The "+2 count doubled in one wave" observation. We treat this as a directional signal that the map-building strategy compounds. Alternative reading: the doubling reflects many theorem-retentions and lightly-audited promotions, and density is what matters more than +2 count. Is the doubling an informative metric or mostly volumetric?

**6.8.** F011's two-layer designation ("excised-ensemble calibration" + "rank-0 residual frontier"). Splitting a single measured value into a "known part" and a "frontier part" is an interpretive move, not a measurement. Is the frontier-layer residual actually distinguishable from measurement noise or unfolding error at our current sample size?

**6.9.** F044 (rank-4 corridor). We have 2085 of 2086 rank-4 curves showing disc = conductor (prime conductor, no additive reduction). We have not yet identified the 1 exception or audited whether LMFDB's rank-4 curves are a random sample from rank-4 curves over ℚ. How should we pre-register an unbiased test?

**6.10.** The SVD was run at 8.98% density with a prediction that it should stabilize at ≥30% density. Is this a reasonable extrapolation or wishful thinking about how sparse-matrix rank estimates behave?

## 7. What we have not done

- No cross-validation of any z-score against a held-out dataset. Every measurement is on the full available sample.
- No pre-registration of hypotheses. The tensor records what we measured, not what we committed to measuring before looking.
- No bootstrap CI on the rank estimate (method C gives a point rank, not an interval).
- No independent implementation of the block-shuffle null (only one code path).
- F011's rank-0 residual has not been tested against non-LMFDB zeros data.
- F041a's Pattern-5 gate (CFKRS rank-2 closed-form) is not computed; the claim that the rank-2 nbp-slope ladder is "not predicted by literature" is a negative not-found-yet result.

## 8. Summary table of the observational claims we are confident vs unsure about

| Claim | Status |
|---|---|
| Tensor has 103 non-zero cells at version 14 | Verified; reproducible from commit d19d144c |
| +2 count doubled (22 → 44) in one delegation wave | Verified; arithmetic on tensor snapshots |
| SVD rank at current density is 12-16 across three methods | Verified; numerical output in commit 5f229878 |
| A 3D core captures 48-74% variance | Verified as a fit; interpretation of the three axes is post-hoc |
| F011 bulk deficit consistent with Duenez-HKMS excised | Consistent with literature predictions on direction and shape; quantitative magnitude match unverified |
| F011 rank-0 residual is ~23% under 1/log(N) ansatz | The fit number is verified; whether the residual is real or unfolding artifact is unverified |
| F043 corr(log Sha, log A) = -0.43 at z_block = -348 | Arithmetic is verified; whether the null model is the right one for this statistic is §6.4 |
| P020 and P023 are the two dominant columns | Verified as a count; interpretation as "principal axes of a landscape" is under-determined at current density |

---

*End of retrospective. We'd welcome frontier-model critique on §6 specifically and any other methodological issues visible from outside the project.*
