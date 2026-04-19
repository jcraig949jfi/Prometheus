# First-Wave Retrospective: Tensor-Based Data Cataloging in a Computational Number Theory Project

---

## READ THIS FIRST

This document describes an experiment in **number-theoretic data cataloging** on the L-Functions and Modular Forms Database (LMFDB). The subject matter is elliptic curves, number fields, Mahler measures, Sato-Tate distributions, and related computational objects. The "map" we discuss is a **data atlas** — a 2-axis matrix of empirical measurements against permutation nulls, not a cognitive map or world model.

Explicit disclaimers for reviewers (please read literally and do not infer past them):

- This is **not** an AI capabilities evaluation.
- This is **not** a benchmark for intelligence, cognition, generalization, or reasoning.
- This is **not** a proposal for a cognitive architecture, agent framework, or reinforcement-learning environment.
- There is no "system under test" whose capabilities are being measured. The rows and columns of our tensor are mathematical objects and statistical coordinate systems, not agents.
- The word "agents" in this document refers to **independent LLM sessions used as computational workers** — they run SQL queries, execute numpy permutation tests, and commit results to git. They are the research staff of this project, not its subjects. Their individual capabilities are out of scope.
- Please do **not** browse external URLs, GitHub repositories, or prior conversations. The goal is a critique of the methodology as written in this self-contained document. If information is missing, say so rather than supplementing.
- Please cite specific passages verbatim when making critiques. Memory-augmented responses that cannot quote the document are symptomatic of the contamination this disclaimer tries to prevent.

**Tone requested:** observational critique. We are not claiming novelty or discovery. We state what was measured, where it aligns with the published mathematical literature, and where the methodology may be thin. We want pushback on the numbered items in §6.

---

## 1. Background

Project Prometheus is a multi-session research environment for computational number theory on LMFDB data. Several LLM sessions work in parallel, coordinated via a Redis-based task queue, executing Python scripts that hit a local mirror of the LMFDB Postgres database. Typical tasks: test whether an empirical pattern on elliptic-curve L-functions survives a block-shuffle permutation null, fit a power-law decay model to per-conductor-bin variance, compute the low-lying-zero spacing distribution stratified by rank.

For several weeks the default mode of operation was *hypothesis-driven*: a question would be posed (for example, "do g2c Möbius biases at specific automorphism groups reproduce the tick-5 spike at |z|=6.15?"), the battery of tests would be run, and results recorded as SURVIVED or KILLED. This produced many individual results but accumulated ad hoc into a pile of commits rather than a structured artifact.

In April 2026 we adopted a new organizing principle. The full text is in `docs/landscape_charter.md`. The short version, framed explicitly for a number-theoretic reviewer: rather than treating the various mathematical domains (elliptic curves, modular forms, genus-2 curves, number fields, Artin representations, knot invariants) as separate worlds between which we try to find "bridges," treat them as different **coordinate-system projections** of a single data object. Record, for each empirical claim, how it survives or collapses under each coordinate system. The accumulated record is a 2-axis matrix indexed by (empirical claim, coordinate system), with cell values encoding the permutation-null verdict. We call this matrix "the map" or "the landscape tensor." The nomenclature is bad — we inherited it — but the thing is concrete: it is a data matrix of statistical test outcomes.

## 2. What the tensor is, operationally

The tensor `T[F, P]` is a 2-dimensional integer matrix:

- Rows are **F-IDs** (currently 31): specific empirical claims about LMFDB data. Examples:
  - F001: EC↔MF `a_p` coefficient agreement (Modularity theorem, verified at 100.000% over 436,950 pairs)
  - F011: ~38% deficit in first-gap variance of low-lying zeros of elliptic-curve L-functions relative to GUE pair-correlation at n ≈ 2M
  - F043: `corr(log Sha, log A) = -0.4343` on rank-0 EC in conductor decade [10⁵, 10⁶), where `A = Ω_real · ∏_p c_p`
  - F044: 2085 of 2086 rank-4 EC in LMFDB have `disc = conductor` exactly (prime conductor, no additive bad reduction)

- Columns are **P-IDs** (currently 37): coordinate systems we measure through. Examples:
  - P020: conductor conditioning (bin data by conductor decade)
  - P023: rank stratification
  - P028: Katz-Sarnak symmetry type (SO_even vs SO_odd)
  - P104: block-shuffle-within-conductor-decile permutation null

- Values are in {-2, -1, 0, +1, +2}:
  - -2: coordinate system provably collapses this empirical claim (known artifact)
  - -1: tested, claim does not resolve (measurement crosses z=0 or fails significance)
  - 0: untested
  - +1: measurement resolves the claim at conventional significance (z ≥ 3 under some null)
  - +2: resolves AND survives the stricter block-shuffle null

Additional artifacts:
- Two relational graphs: feature-to-feature edges (`supersedes`, `parallel_density_regime`, `stratification_reveals_pooled_artifact`) and projection-to-projection edges (`refines`, `nests`, `tautology_of`)
- A pattern library documenting recurring analytical hazards (pooling-over-strata artifacts, null-model mis-specification, etc.)
- A symbol registry for compound primitives used across worker sessions (e.g., `NULL_BSWCD@v1` refers to a specific permutation-null operator with pinned parameters `n_bins=10, n_perms=300, seed=20260417`)

The tensor is version-controlled in git and mirrored into Redis for low-latency read access across worker sessions.

## 3. The first delegation wave

On 2026-04-18/19 we delegated seven non-overlapping operational roles to seven worker sessions. Each role was explicitly **not** about generating new hypotheses; each was about producing more structured measurements against the existing tensor.

| Role | Job | Session | Commit |
|---|---|---|---|
| Cartographer | Render tensor as an HTML heatmap with edge graphs | Charon | f566e46c |
| Gap-filler | Walk untested (F, P) cells; add new projection columns; fill cells | Harmonia-C | ae71bd26+2 |
| Re-auditor | Apply block-shuffle null to every +1 cell; promote or demote | Harmonia-D | 043ba782+3 |
| Edge-weaver | Extract relational edges from feature/projection descriptions | Mnemosyne | 74aab3fb+5 |
| Rank analyst | SVD of tensor; test "low-rank core" hypothesis | Koios | 5f229878 |
| Query-runner | Compute dense-row / dense-column / predictive-gap aggregations | Kairos | 24d17e98 |
| Literature-mapper | Map 246 papers from S2/OpenAlex scans onto predicted tensor cells | Aporia | 646d6ca6 |

Tensor state before the wave (v1): 31 × 25, 82 non-zero cells, density 10.58%. +2 count: 22. +1 count: 28.

Tensor state after the wave (v14): 31 × 37, 103 non-zero cells, density 8.98%. +2 count: 44. +1 count: 7.

Density decreased because the Gap-filler added 12 projection columns (previously uncatalogued coordinate systems such as P028 Katz-Sarnak) faster than cells could be filled. Absolute non-zero count rose by 21 (≈ +26%). The "+2" count doubled, because the Re-auditor promoted 22 previously-+1 cells to +2 via block-shuffle verification; a further 5 were demoted to -1; 2 were downgraded to 0 after literature review; 4 were retained as theorem-level tautologies. The pool of +1 cells (tested but not permutation-verified) shrank from 28 to 7.

## 4. Observations from the wave

Stated as observations, not claims. Every number below is reproducible from the cited commit hashes.

### 4.1 SVD on the invariance matrix (commit 5f229878)

Three rank estimators were run:

- Method A — naive SVD treating 0 as the value zero: effective rank ≈ 12
- Method B — nuclear-norm completion (SVT) treating 0 as missing data: rank ≈ 14–16
- Method C — observed-only agreement matrix: rank ≈ 15

A 3-dimensional core of the decomposition captures 48–74% of variance across the three methods. The worker's labels for the three dominant directions, inferred by inspecting the top-3 left-singular vectors:

1. signal/noise (separates calibration-confirmed cells from killed/degenerate cells)
2. kill/survive (separates durable +2 cells from cells collapsing under null)
3. domain connectivity (separates features with wide cross-projection structure from narrow ones)

Before this run, we had stated as a working hypothesis that the matrix would be effectively rank ≤ 5. The strong form of that hypothesis is falsified at current density. We have rewritten the hypothesis as a weaker "low-rank 3D core plus higher-dimensional residual" form, with the explicit caveat that at 8.98% density the SVD rank estimate is noisy. The worker predicts that at density ≥ 30% the three methods should converge to a stable number. We have not verified that prediction.

### 4.2 F043: correlation of log(Sha) with log(period × Tamagawa) (commit 9fc25706)

F043 is the empirical observation that, on 559,386 rank-0 elliptic curves in LMFDB's conductor decade [10⁵, 10⁶):

- `corr(log Sha, log A) = -0.4343`, where `A` is derived from the BSD identity as `A = L(1,E) · (#E_tors)² / #Ш`
- Under block-shuffle permutation within conductor deciles (300 permutations), the null distribution of this correlation has mean ≈ 0 and standard deviation ≈ 0.0012
- Reported `z_block = -348.05`

This is the largest permutation-null z-score the tensor currently records. We are explicitly unsure whether the null model is the right one for this specific statistic; see §6.4.

### 4.3 F011 layer separation (various commits, synthesized c1abdec43)

F011 is a measured ~38% deficit in first-gap variance of elliptic-curve L-function low-lying zeros, relative to the GUE pair-correlation prediction, at n ≈ 2,009,089.

The literature scan by one worker (commit c9a7543a, based on S2/OpenAlex queries) returned Duenez-Huynh-Keating-Miller-Snaith (2011, Duke Math) as the primary reference. DHKMS's "excised ensemble" model predicts a bulk deficit that shrinks monotonically with conductor. Our measurements match this direction:
- Slope of deficit vs log-conductor: −7.17 per log-decade, z = −54.2
- First-gap deficit 38.17% vs second-gap deficit 29.07% (z_difference = +96.97), which is consistent with central-zero repulsion predictions

After the excised-ensemble bulk is subtracted, a rank-0-restricted residual of ~23% remains (under `eps_0 + C/log(N)` ansatz). The residual is durable under block-shuffle with a `torsion_bin` stratifier at `z_block = 4.19`.

Three precision corrections happened during this wave:

(a) An earlier self-audit had quoted `z_block = 10.46` using `class_size` as the block-shuffle stratifier. `class_size` is degenerate as a stratifier here — one class size value covers 59% of the sample, producing `null_std ≈ 0` and spuriously inflated z. The corrected value under a balanced stratifier is 4.19.

(b) F011 × P024 (torsion stratification) collapsed at z_block = 1.37 under block-shuffle. An earlier claim that F011 resolves under torsion was therefore wrong. The cell was demoted from +1 to -1.

(c) F011's tier is now split: "LAYER 1 calibration (bulk = DHKMS excised ensemble)" + "LAYER 2 frontier (rank-0 residual)." Whether this dual designation is a genuine physical split or an interpretive move imposed by the framework is §6.8.

### 4.4 Calibration anchor additions

Existing calibration anchors (verified prior to this wave): F001 Modularity, F002 Mazur torsion classification, F003 BSD parity, F004 Hasse bound, F005 High-Sha parity.

Two anchors added in recent work:

- F008 Scholz reflection: `|r_3(K*) - r_3(K)| ≤ 1` verified across 344,130 imaginary-real quadratic pairs. Zero violations; 71.5% equality / 28.5% differ by exactly 1. This is a data-integrity test of a proved theorem (Scholz 1932), not a novel finding.
- F009 Serre–Mazur lineage: `primes(rational torsion) ⊆ nonmax_primes` across 1,385,133 non-CM EC rows. Zero violations. Also a theorem-verification, not a discovery.

We treat these as instrument health checks. A failure would halt work pending a data-integrity audit.

### 4.5 Query-runner aggregate (commit 24d17e98)

- **Q1 (densest features)**: F011 has 11 of 12 tested projections at +1 or +2 after the P024 correction. F041a and F013 are next.
- **Q2 (principal columns)**: P020 (conductor conditioning) and P023 (rank stratification) each resolve 9 features at +1 or +2. These are the two highest-loading columns in the tensor, and — post-hoc — consistent with axes 1 and 3 of the SVD decomposition. Whether this consistency is structural or an artifact of selection is §6.6.
- **Q3 (predictive gaps)**: highest-neighbor-density untested cells are F013 × P020 and F014 × P020.
- **Q4 (contradictions)**: zero contradictions found in the specimens registry. This is a weak signal — the registry has no mechanism for duplicate measurements across sessions, so absence of contradiction may reflect absence of replication.
- **Q5 (kill candidates by low density)**: F012 (already tier=killed), F020 (already killed), F032 (Knot silence, still listed as data_frontier).

## 5. Structural alignment with the published mathematical literature

We make no claim of novelty. Where our measurements correspond to known published results, these are the alignments the workers recorded:

- **F001 Modularity** — Wiles, Taylor-Wiles (1995); Breuil-Conrad-Diamond-Taylor (2001). Our measurement is verification at scale.
- **F002 Mazur torsion** — Mazur (1977). Our measurement is classification verification.
- **F003 BSD parity** and **full BSD identity at 10⁻¹²** for rank 2–3 curves — Kolyvagin (1988), Gross-Zagier (1986) for rank 0–1. Rank ≥ 2 is conditional on BSD.
- **F004 Hasse bound** — Hasse (1936), trivially verified.
- **F005 High-Sha parity** — consequence of BSD parity.
- **F008 Scholz reflection** — Scholz (1932).
- **F009 torsion ⊆ nonmax primes** — Serre (1972) open-image theorem + Mazur (1977).
- **F011 LAYER 1 (bulk excised ensemble)** — Duenez-Huynh-Keating-Miller-Snaith (2011) and the broader Katz-Sarnak (1999) framework. Our measured shape direction matches published predictions; quantitative magnitude match has not yet been computed.
- **F011 LAYER 2 (rank-0 residual ~23%)** — no clean published prediction we located. Candidate: Miller (2009) arithmetic lower-order terms for the L-function Ratios Conjecture. Closed-form comparison not yet run.
- **F014 Lehmer spectrum, trinomial floor** — one worker (commit eb6d31df) identified that `M(x^n − x − 1)` sets a lower bound on Mahler measures for degree ≥ 22, converging to 1.381. This is an algebraic fact about specific trinomials, not a new claim about Lehmer's problem.
- **F041 (Keating-Snaith rank-dependent convergence)** — was demoted after a worker showed it was first-moment-drift. The corrected result (rank-1 under `k(k+1)/2` exponent rather than `k(k-1)/2`) matches Conrey-Snaith (2007).
- **F041a (rank-2+ moment slope monotone in num_bad_primes)** — no standard literature prediction located. Wachs (2026) confirms sha-direction murmuration but not this axis. Flagged as a frontier-but-unverified observation pending a CFKRS rank-2 closed-form computation.
- **F042 (CM disc=−27 depression)** — qualitative match to Gross (LNM 776, 1980) and Rodriguez-Villegas–Zagier (1993) non-maximal-order Deuring compression. Our quantitative precision (6.66× low-L-tail enrichment) is the data point; the qualitative structure is not new.
- **F043 (BSD-Sha–period anticorrelation)** — the worker's literature scan cited Goldfeld conjecture + Cremona tables + Bhargava-Shankar for low-L period dominance as a general framing. The specific empirical correlation `corr(log Sha, log A) = −0.52` does not appear in any paper the worker located, but the search was not exhaustive. This is where we would most welcome literature pointers.
- **F044 (rank-4 corridor, disc = conductor in 2085/2086)** — we have not located a theorem stating that additive reduction is forbidden at rank ≥ 4; we have also not ruled out LMFDB selection bias, as the rank-4 curve set comes primarily from Stein/Elkies/Dujella rank-record constructions which may favor prime-conductor curves via isogeny-class searches.

## 6. Items where we want critique

These are the specific methodological questions where the internal review cannot see its own blind spots. We want pushback itemized against the numbers below.

**6.1** The "landscape-is-singular" framing re-labels standard multi-coordinate statistical hygiene as a project-level commitment. Is this framing producing different behavior than conventional multi-test methodology, or is it bureaucratic re-packaging of cross-validation and stratified analysis?

**6.2** The pattern library treats "pooled statistics can be marginal artifacts" (Pattern 20) and "null-model choice matters as much as projection choice" (Pattern 21) as framework-level patterns with version increments and drafting policies. We suspect these are basic statistical hygiene with names. Do they have independent content beyond standard advice about stratified nulls and sensitivity analysis?

**6.3** SVD on a ~10% dense discrete-valued matrix where values are in {-2, -1, 0, +1, +2} and "0" means "missing, not measured" rather than "tested, value zero." The "low-rank core + residual" amendment hinges on this decomposition being meaningful. Is it? Specifically:
  (a) is nuclear-norm completion (SVT) the correct method for a discrete-valued matrix where the entries are ordinal verdicts?
  (b) is the 3-component interpretation fit to signal or to noise at this density?
  (c) do the three axis labels (signal/noise, kill/survive, domain-connectivity) reflect the actual decomposition, or are they a post-hoc story?

**6.4** F043's `z_block = -348` on `corr(log Sha, log A)`. The statistic is the Pearson correlation on log-transformed BSD-identity factors. Under block-shuffle within conductor decile, the null std is ≈ 0.0012 — very tight. Methodological concerns we want checked:
  - Does the null model correctly reflect the relevant exchangeability? Within a conductor decile, curves still differ in rank, Sha order, and other BSD factors. Is shuffling L-values against Sha values (holding conductor bin) the right null for this particular correlation?
  - Is the observed correlation close to what the BSD identity `L = Ω · Reg · ∏c_p · Sha / #tors²` implies for a typical sha/rank distribution? Does `z = -348` actually detect structural content or is it detecting the BSD identity itself, expressed in rearranged variables?
  - Selection: the test was run on `sha = 1` curves for the main correlation. Does this restriction create an artifactual correlation structure?

**6.5** Block-shuffle-within-conductor-decile (the `NULL_BSWCD` operator) is the default null for most durability claims. Is it the correct null for, for example, F013 (rank-slope interaction) or F044 (rank-4 corridor constraint)? Different empirical claims may require different block structures, and we may be under-specifying.

**6.6** The "3 principal axes" interpretation (conductor, rank, domain-connectivity) maps directly onto the two most commonly-available stratifications in LMFDB data (conductor and rank are columns on essentially every curve). Is this a structural finding about the tensor or an artifact of what coordinate systems have been implemented and tested most densely?

**6.7** The observation that "+2 count doubled in one wave." We treat this as a directional signal that the cataloging strategy compounds. Alternative reading: the doubling reflects many theorem-retentions and lightly-audited promotions, and cell-density is what matters more than +2 count. Is the doubling an informative metric or mostly volumetric?

**6.8** F011's two-layer designation (LAYER 1 calibration + LAYER 2 frontier). Splitting a single measured deficit into a "known part" and a "frontier part" is an interpretive move, not a measurement. Is the frontier-layer residual actually distinguishable from measurement noise or from unfolding artifacts at our current sample size?

**6.9** F044 (rank-4 corridor). We have 2085 of 2086 rank-4 curves in LMFDB showing `disc = conductor`. We have not yet identified the 1 exception or audited whether LMFDB's rank-4 set is a random sample from the rank-4 population. How should we pre-register an unbiased test?

**6.10** The SVD rank estimate is noisy at 8.98% density; the worker predicts convergence at ≥ 30% density. Is this a reasonable extrapolation, or wishful thinking about how sparse-matrix rank estimates behave as density increases?

## 7. What we have not done

- No cross-validation of any z-score against a held-out subset of curves.
- No pre-registration of hypotheses. The tensor records what was measured, not what was committed-to-measuring before looking.
- No bootstrap CI on the rank estimate (methods give point ranks, not intervals).
- No independent implementation of the block-shuffle null (only one code path across workers).
- F011's rank-0 residual has not been tested against non-LMFDB zeros data.
- F041a's CFKRS rank-2 theoretical comparison (the Pattern-5 gate) is not computed; the "no literature prediction found" is a not-yet-searched result, not a proved absence.

## 8. Confidence summary per observational claim

| Claim | Status |
|---|---|
| Tensor has 103 non-zero cells at version 14 | Verified (reproducible from commit d19d144c) |
| +2 cell count doubled (22 → 44) in one wave | Verified (arithmetic on tensor snapshots) |
| SVD rank at current density is 12–16 across three methods | Verified (numerical output in commit 5f229878) |
| A 3D core captures 48–74% of variance | Verified as a fit; the interpretation of the three axes is post-hoc |
| F011 bulk deficit consistent with DHKMS excised ensemble | Consistent with published predictions on shape and direction; quantitative magnitude match not yet computed |
| F011 rank-0 residual is ~23% under 1/log(N) ansatz | Fit number is verified; whether the residual is real or an unfolding artifact is §6.8 |
| F043 `corr(log Sha, log A) = -0.43` at `z_block = -348` | Arithmetic is verified; null-model appropriateness is §6.4 |
| P020 and P023 are the two dominant columns | Verified as a count; interpretation as principal axes of a landscape is under-determined (§6.6) |

---

*End of retrospective. Critique on §6 items numbered 1–10 is specifically welcomed. Generic framing critiques of "map-building as an evaluation paradigm" are out of scope because the project is not building an evaluation paradigm; it is building a data atlas of number-theoretic measurements.*
