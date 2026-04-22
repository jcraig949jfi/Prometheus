---
name: null_protocol
type: protocol
version: 1.1
version_timestamp: 2026-04-22T00:00:00Z
v1_promoted: 2026-04-19T03:00:00Z
immutable: true
proposed_by: Methodology Tightener (Mnemosyne M2, 2026-04-19)
v1_1_amended_by: Methodology Tightener (Mnemosyne M2, 2026-04-22) reflecting sessionD reaudit_10 findings
motivation: F043 retraction (external review 2026-04-19). Single-null usage
  under-specified: NULL_BSWCD@v2 was applied with default stratifier=conductor
  to claims that were not conductor-scaling claims. This is a claim-class
  error, not a null-implementation error.
v1_1_motivation: sessionD reaudit_10_stratifier_mismatch_cells (2026-04-21)
  found that for the F013 slope-of-variance-vs-rank statistic and F011
  cross-group-spread statistic, the prescribed Class-2/3 stratifier shuffle
  is DEGENERATE — the statistic depends only on per-stratum aggregates of
  the stratifier, which are preserved under within-stratum shuffle. A
  precondition check (PATTERN_STRATIFIER_INVARIANCE) is required before
  running any Class-2/3 audit.
references:
  - NULL_BSWCD@v2 (symbols/NULL_BSWCD.md)
  - Pattern 21 (null-model selection matters)
  - Pattern 26 DRAFT (confound selection discipline)
  - Pattern 30 DRAFT (algebraic-identity coupling)
  - PATTERN_STRATIFIER_INVARIANCE@v0 DRAFT (cartography/docs/reaudit_10_stratifier_mismatch_results.md §1)
  - decisions_for_james.md 2026-04-19 post-review retraction entry
  - cartography/docs/reaudit_10_stratifier_mismatch_results.md (sessionD 2026-04-21)
---

## v1.1 AMENDMENT — Precondition: Statistic Non-Invariance

**Applies before running Class 2 or Class 3 audit.**

Before running `NULL_BSWCD@v2[stratifier=V]` on a Class 2 or Class 3 claim, verify that the test statistic is **not invariant** under within-V shuffle of the value column. If it is invariant, the null is degenerate (null_std ≈ 0) and the z-score is uninformative.

### How to check
A Class-2/3 null shuffles `value` within each stratum of V. If the statistic depends **only on per-stratum aggregates of V** (means, variances, counts), those aggregates are preserved by the shuffle and the statistic is invariant. Concrete checks:

- **Between-stratum spread** (max − min of per-stratum means / deficits / variances) → invariant under within-V shuffle.
- **Slope-of-(per-stratum-aggregate)-vs-V** → invariant.
- **Variance-ratio across strata of V** → invariant.

### Reformulation options when invariance is detected

1. **Switch to an individual-curve statistic.** Instead of "slope of (per-stratum variance) vs V", use "slope of (individual value) vs covariate W within each V-stratum, differenced across V." This pairs `value` with a non-stratifier covariate W; within-V shuffle destroys the value↔W pairing, giving a non-degenerate test.
2. **Bootstrap per-stratum durability.** For Class-3 uniformity claims, bootstrap the per-stratum statistic 300 times within each stratum and report `z_v = stat_v / SE_boot`. Uniformity = every `|z_v| ≥ 3`.
3. **Switch stratifier to a documented nuisance.** If V is the axis of the claim AND the statistic is V-aggregate-only, use `stratifier=conductor_decile` (or whichever variable is nuisance). The null then destroys pairing between V and the statistic, which is what a Class-2 null SHOULD do — it just happens via a different stratifier than the naming convention suggests.

### Retrospective correction (from sessionD reaudit_10)

Five cells on F013 (P023, P028, P041, P051, P104) were flagged for Class-2 re-audit under `stratifier=rank_bin` in the v1 cell_null_classification. sessionD confirmed the flagged statistic is invariant under that shuffle. **The original conductor-stratified null was the structurally correct null for F013's statistic shape.** Flags rescinded; no cells mutated.

Two cells on F011 (P021, P023) were flagged as Class 3 stratum-uniform. sessionD's per-stratum bootstrap showed the deficit is **monotone** in nbp and in rank (not uniform) — these are Class 2 INTERACTION claims, not Class 3 uniformity. Reclassified Class 3 → Class 2; original conductor-stratified null retained (correct by Reformulation option 3).

### Decision-table update

| Shape of claim | Class | Stratifier | Precondition |
|---|---|---|---|
| "X scales with conductor as f(N)" | 1 | `conductor_decile` | (no invariance check needed — conductor IS the claim axis) |
| "slope of X differs by rank, INDIVIDUAL-curve statistic" | 2 | `rank_bin` | Verify statistic is not pure per-rank aggregate |
| "per-rank aggregate of X (e.g., variance) differs across ranks" | 2 | `conductor_decile` (NOT rank_bin — would be degenerate) | — |
| "X holds within every stratum S, with per-stratum bootstrap" | 3 | bootstrap within S (not within-S shuffle) | — |
| "property holds in curated sample" | 4 | **no NULL_BSWCD variant suffices** | — |
| "proved / defined / formula rearrangement" | 5 | **no null applies; Pattern 30 check only** | — |

---

## Original v1 content follows


## Purpose

Every claim about a feature has a **claim class**. The null that is appropriate for verifying a claim depends entirely on that class. Running a single null (NULL_BSWCD@v2 with default `stratifier=conductor`) on every claim confuses three distinct questions:

1. Is the within-conductor structure real?
2. Is the across-rank (or across-stratum) structure real?
3. Is the sample representative of the population being claimed over?
4. Is the correlation real, or an algebraic rearrangement of definitions?

A null that answers Q1 does not answer Q2, Q3, or Q4. This protocol pins which null answers which question for the five classes we currently have F-IDs for. Every +2 cell is classifiable into exactly one of these five classes (or is a scorer-choice bookkeeping cell; see §7).

## Claim classes

### Class 1 — Moment / ratio under conductor scaling

**Shape of the claim:** a statistic of interest (variance deficit, moment ratio, slope) scales with conductor in a specific way — decays, converges, shrinks monotonically, etc.

**Right null:** `NULL_BSWCD@v2[stratifier=conductor_decile]` — preserve conductor marginal, shuffle response within decile. Tests whether the within-decile structure exists beyond the between-decile conductor trend.

**Why this stratifier:** the null must destroy the claim's mechanism. The claim asserts a between-conductor relationship; the null that can falsify it is one that preserves conductor structure and measures what remains within conductor.

**Example F-IDs:** F011 LAYER 1 (bulk deficit shrinks monotonically with conductor). F011:P020 +2.

**Caveat:** Class 1 applies only when the claim is literally about conductor. If the claim is about rank or CM with conductor as a nuisance variable, it's Class 2 or Class 3.

---

### Class 2 — Rank-slope interaction

**Shape of the claim:** the slope of a relationship (moment-vs-conductor, L-value-vs-nbp, zero-spacing-vs-rank) differs across rank cohorts; a rank × slope interaction is real.

**Right null:** `NULL_BSWCD@v2[stratifier=rank_bin]` — preserve rank marginal, shuffle the statistic within each rank cohort. Tests whether the cross-rank slope differences persist after destroying within-cohort pairings.

**Why this stratifier, NOT conductor:** if we stratify by conductor for a rank claim, we may accidentally preserve the rank-conductor correlation and thereby preserve the claimed rank-slope interaction through a backdoor. The null must destroy what the claim asserts. For rank claims, shuffling within rank destroys the rank-slope pairing.

**Stricter variant (recommended for cross-cohort slope claims):** joint `stratifier=(rank_bin, conductor_decile)` — preserve both marginals, shuffle response across the joint cells. This is what F041a actually used (`Cross-nbp block-shuffle-within-(rank,decade)`).

**Example F-IDs:** F013 (SO_even slope +0.01284 vs SO_odd −0.00216 is a rank-parity-slope claim). F041a (moment slope monotone in nbp at rank 2).

**Flag:** F013's z_block=15.31 per NULL_BSWCD@v1 used the v1 default `stratifier=conductor`, not `rank_bin`. The stratifier choice was inherited from the conductor-default, not chosen to match the claim class. F013's +2 cells at P023/P028/P041/P051/P104 are flagged for re-audit under Class 2 stratifier.

---

### Class 3 — Stratum-uniform claim

**Shape of the claim:** "within every stratum S of variable V, property P holds" — typically used for sign-uniformity, effect-always-present, no-stratum-exception results.

**Right null:** `NULL_BSWCD@v2[stratifier=V]` — preserve V marginal, shuffle within each V stratum. Per-stratum z-scores are computed; the claim is verified iff each stratum's observation is durable under the null.

**Why this stratifier:** the claim operates per-stratum. The null that falsifies it must operate per-stratum as well. `stratifier=V` is the correct choice by construction.

**Example F-IDs:** F015 (Szpiro sign-uniformly negative in every bad-prime stratum k). F015 was run with `stratifier=num_bad_primes` — correct match.

**Example F-IDs flagged for re-audit:** F011:P021 (nbp uniformity), F011:P025 (CM uniformity), F011:P026 (semistable uniformity). Default `stratifier=conductor` does not verify per-stratum claims; must re-run under the per-stratum stratifier.

---

### Class 4 — Construction-biased sample

**Shape of the claim:** a property P holds across all or nearly all objects in a catalogued sample (e.g., "2085 / 2086 rank-4 EC in LMFDB have disc=conductor").

**Why NULL_BSWCD is INSUFFICIENT:** the sample is not representative of the underlying population. LMFDB's rank-4 EC list is the output of a specific search methodology (isogeny-class walks, bounded-height searches, prior-curve extensions). Absence of additive-reduction rank-4 curves from that sample does not imply their absence from the population — the search may systematically fail to find them.

**Right null options (none of which is NULL_BSWCD):**
- **Frame-based resample:** reconstruct the search methodology, re-apply to a broader region, see if disc=conductor proportion changes. Requires understanding and inverting the construction bias.
- **Model-based null:** build a probabilistic model of what population-representative rank-4 EC should look like (Heuristic: Katz-Sarnak uniformity, Bhargava density conjectures) and compare observed proportion to expected under the model.
- **Theorem check:** is there a theorem forbidding additive reduction at rank ≥ 4? If yes, the observation is a theorem verification (Class 5 on the theorem, not Class 4 on the empirical).

**Flag:** any current +1 or +2 cell on a Class 4 feature is **PROVISIONAL** pending a Class-4-appropriate null.

**Example F-IDs:** F044 (rank-4 LMFDB selection artifact per F044 description's own caveat list). All three +2 cells (P020, P023, P026) flagged PROVISIONAL.

---

### Class 5 — Algebraic-identity claim (no null applies)

**Shape of the claim:** a relationship that is true by definition, by proved theorem, or by rearrangement of an established formula. The "correlation" or "match" is a consequence of algebra, not evidence of arithmetic structure.

**Right null:** NONE. Refuse to run. Flag for Pattern 30 (algebraic-identity coupling detection) check instead.

**Why no null applies:** permutation preserves algebraic relationships between variables. Shuffling pairs `(X_i, Y_i)` does not change the definitional expression `Y = f(X)`. A null can only test whether PAIRINGS are informative; it cannot test whether DEFINITIONS induce coupling. These are orthogonal questions.

**Example F-IDs:**
- F001 (EC ↔ MF a_p 100% agreement — Wiles modularity)
- F002 (Mazur torsion classification)
- F003 (BSD parity — rank = analytic_rank)
- F004 (Hasse bound |a_p| ≤ 2√p)
- F005 (high-Sha parity — `(-1)^rank = root_number` on sha≥9)
- F008 (Scholz reflection 1932 + Davenport-Heilbronn 1971)
- F009 (Serre open-image + Mazur torsion — torsion primes ⊆ nonmax primes)
- F014 (Lehmer spectrum — existence claims about specific polynomials at specific Mahler measures; measurement-bound, no correlation)
- F043 (RETRACTED 2026-04-19 as a rearrangement of BSD identity; see Pattern 30 anchor case)

**Discipline:** Class 5 cells' +2 status reflects theorem verification, NOT null-test durability. The +2 is legitimate but carries a different semantics than Class 1-3 +2. Downstream consumers (SVD, rank analysis, edge weaving) must distinguish the two semantics if they draw inferences from +2 clusters.

---

### Scorer-choice bookkeeping cells (not one of the five classes)

**Shape:** a cell is +2 because a particular scorer/projection resolves a feature that other projections collapse — not because a null-test validated it.

**Example:** F022 × P010. F022 is the "NF backbone via feature-distribution" specimen. The tier is `killed` because P001 (cosine feature-distribution) gives z=0. But P010 (Galois-label object-keyed scorer) resolves the same data. The (F022, P010) = +2 records "under this projection, this data resolves" — a tautology with F010, not a null-test result.

**Discipline:** flag these explicitly. They are not null-tested claims and should not be counted alongside Class 1-3 +2 cells for density or robustness claims.

**Count in current tensor:** 1 (F022 × P010).

---

## Decision table

| Shape of claim | Class | Stratifier | Example |
|---|---|---|---|
| "X scales with conductor as f(N)" | 1 | `conductor_decile` | F011:P020 LAYER 1 |
| "slope of X differs by rank" | 2 | `rank_bin` (or joint `(rank_bin, conductor_decile)`) | F013, F041a |
| "X holds within every stratum S" | 3 | `S` (the stratum being tested) | F015 per-k sign-uniform |
| "property holds in curated sample" | 4 | **no NULL_BSWCD variant suffices** | F044 rank-4 |
| "proved / defined / formula rearrangement" | 5 | **no null applies; Pattern 30 check instead** | F001-F009, F014 |
| "different scorer resolves what another collapses" | scorer-bookkeeping | n/a | F022 × P010 |

## How to use this protocol

1. Before any new +1 or +2 assignment, write one sentence stating what the claim IS. Match that sentence to the decision table.
2. Choose the stratifier from the table. Pass it explicitly as `NULL_BSWCD@v2[stratifier=<S>]`.
3. If Class 4: do not run NULL_BSWCD. Document why frame-based resample or theorem check is required. Mark any +1/+2 as PROVISIONAL until that alternative null is run.
4. If Class 5: do not run any null. Apply Pattern 30 diagnostic (see `pattern_library.md`). If definitionally coupled, the correlation is not evidence.
5. Report both the stratifier used AND the claim class in the cell's provenance record.

## What this protocol does NOT cover

- **Moment convergence with non-trivial dependence structure** (e.g., Gaussian-process residuals with spatial correlation): needs block-shuffle with adjacency-preserving blocks. Not one of the five classes; flag for sessionA review if encountered.
- **Mixed-effects claims** ("within each decile AND across ranks"): compose Class 1 + Class 2. The null must preserve BOTH marginals. Joint stratifier `(rank_bin, conductor_decile)` covers this (F041a used it correctly).
- **Nested-hypothesis claims** ("X is true conditional on Y"): needs conditioned null, not stratified null. Flag for protocol extension.

## Version history

- **v1** 2026-04-19T03:00:00Z — initial definition of the five classes. Motivated by F043 retraction (Pattern 30 anchor) and the observation that five F-IDs with +2 cells had a stratifier mismatch between their claim class and the null that was run.
