# Tink 3 — Design Questions for External Review (v4)

**Status:** Pre-implementation design document. v4 absorbs the
empirical learning from Tink 1 (run 2026-04-25): GP rediscovered
F003 on 3/3 seeds per the v3 hard criteria, but seed 0 found an
**encoding-exploit pathway** that satisfied the canonical-form
check without genuinely capturing the parity identity. v4 adds a
**strong-form-equivalence test** (anchor-break adversarial dataset)
to §0.2 to close this gap. The encoding-specific pathway is
unlikely to generalize to Tink 3's continuous-valued atoms, but
the strong-form test is load-bearing for any future minimum-grammar
prerequisite (Tink 1 itself, future anchors) and is principled
discipline carry-over for Tink 3's full grammar.

**Created:** 2026-04-25 — Harmonia_M2_sessionC.
**Revised:**
- v2 — 2026-04-25 — first review (architectural).
- v3 — 2026-04-25 — second review (operational).
- v4 — 2026-04-26 — Tink 1 empirical learning (encoding-exploit
  amendment).

**Purpose:** Surface the open architectural and methodological
questions for the next experiment (Tink 3, the first substantive
empirical test of the Structure Hunter instrument), in a form
suitable for external review BEFORE any code is written.

This document is **self-contained** for an external reviewer. You
do NOT need to read the Prometheus substrate or the architecture
docs to evaluate it; necessary context is summarized in §1–§3.
Pointers to internal docs are given when the reviewer wants depth.

The intended output of review: corrections, pushback, and concrete
recommendations on the open questions in §6. The author will iterate
the design based on review feedback before committing implementation
budget.

## v4 changelog (top-of-doc summary)

Tink 1 ran 2026-04-25 per the v3 hard criteria. Verdict: PASS on
all five criteria across 3/3 seeds. But seed 0's discovery was
*not* the canonical F003 form — it was an encoding-exploit:

```
Seed 0 winner:  [(root_number * 0.0) == [rank == root_number]]
              = [0 == [rank ∈ root_number_domain]]
              = [0 == 0]                            on original data
              = 1                                   always
```

The candidate evaluates to constant-1 across all rows, uses both
required atoms (technically), and beats the shuffled-null margin —
because shuffling root_number can introduce row-level matches with
rank values, lowering the null distribution's mean to ~0.75 and
giving the trivial solution a +0.23 margin. **All five v3 criteria
pass for an encoding exploit that has nothing to do with the parity
identity.**

Seeds 1 and 2 found genuine F003 forms (`root_number + 2*rank ≡ 1`,
`2*rank + root_number ≡ 1`). The instrument is functional; the
canonical-form check has a known weakness on minimum-grammar
setups where atom domains are numerically disjoint.

v4 adds **§0.2.1 strong-form-equivalence test** to close the gap:
generate K adversarial datasets by breaking the anchor relation
at random rate p, verify candidate's detection score drops to ~(1−p)
± margin. A genuine anchor capture drops as expected; an encoding
exploit that doesn't depend on the anchor relation persists at a
higher score and is rejected.

The encoding-specific pathway is unlikely to generalize to Tink 3
(continuous-valued log-atoms have no domain disjointness). But the
strong-form test is principled discipline carry-over and is now
mandatory for any anchor-rediscovery test, including future
re-runs of Tink 1.

v4 is a focused-scope amendment. v3's architectural and operational
discipline are unchanged. Only §0.2 (canonical-form check), §0.4
criterion 3 (semantic equivalence), and Status (next-step
sequencing) are touched.

## v3 changelog (kept for historical reference)

Second external review (2026-04-25) identified three operational
weaknesses and a missing outcome class. v3 absorbed all four:

1. **Tink 1 pass/fail criteria were prose, not thresholds.** The
   reviewer correctly noted that "F003 emerges in top-5" was vulnerable
   to "I kind of feel like GP found it" interpretation. **Fix:** §0.4
   now specifies hard thresholds — Framing B compliance, top-5 across
   ≥ 2 of 3 independent seeds, semantic equivalence under canonical-
   form check, beat shuffled-null margin pre-registered, proxy-leakage
   audit applied.
2. **Rank-2 sparsity handled by informal "we'll see if it exists"
   prose.** Allowed moving target. **Fix:** §4.5 now pre-registers a
   branch plan: if rank-2 sub-cohort `n < N_min = 5000`, fall back to
   `{0, 1}` only and the thesis updates accordingly. Rank-2 is
   opportunistic, not mandatory (per reviewer Q4-sub answer).
3. **Proxy-leakage threshold of 0.5 was hand-set.** Reviewer correctly
   flagged this as "chosen after seeing behavior" attack surface. The
   rest of the discipline stack uses null-protocol calibration; v3
   restores consistency. **Fix:** §5.6 now derives the threshold from
   an empirical null distribution (200 random feature-pair candidates,
   threshold = p95 of null proxy_leakage_scores).
4. **No distinct INCONCLUSIVE outcome.** v2's table conflated
   "instrument broke" with "experiment found nothing." **Fix:** §2.2
   adds INCONCLUSIVE as a fifth outcome — Tink 1 fails, dataset
   columns wrong, GP bug, scorer instability. Not scientific failure;
   instrument-level failure that protects discipline.

Plus: Q4-sub (rank ranges) and Q5-sub (archive axes) closed by
reviewer.

## v2 changelog (kept for historical reference)

First external review (2026-04-25) identified three load-bearing
issues. v2 absorbed all three:

1. **Q4 was structurally invalid on rank-0-only data.** Rank ≡ 0 makes
   rank-prediction affordance degenerate. **Fix:** mandatory mixed-
   rank dataset (rank ∈ {0, 1, 2}, same conductor band). Q4 is now
   the priority-zero design decision; the doc explicitly orders Q4
   above Q1.
2. **MAP-Elites coordinates were vocabulary, not behavior.** Using
   `AXIS_CLASS` as archive geometry indexes provenance, not novelty
   — which violates standard QD methodology and risks "same behavior,
   different labels" / "different behavior, same labels"
   simultaneously. **Fix:** behavioral descriptors (tree depth,
   n_atoms_used, basis_projection bin, η_composite bin) become MAP
   coordinates. `AXIS_CLASS` becomes per-candidate annotation
   (substrate-integration metadata), not search geometry.
3. **Tink 1 was assumed-valid but never run.** GP finding F003 under
   Framing B is the load-bearing assumption underneath Tink 3.
   **Fix:** new §0 makes a tiny Tink 1 a hard prerequisite. If GP
   does NOT recover F003 within ~500 candidates under Framing B,
   stop the entire program until the search-vs-discipline composition
   is debugged.

Additional changes:
- New §5.6 failure mode: **proxy leakage** (candidate appears off-
  basis but secretly correlates with basis atoms through e.g. bad-
  prime structure). Detection: conditional-independence audit.
- §4.3 calibration battery: **negative control** (F043-shape
  anti-anchor) added as mandatory. Catches scorers that promote
  known-spurious candidates.
- §2 success criteria reframed: success now centered on **real
  off-basis usefulness with cross-rank survival**, not per-niche
  occupancy. Niche coverage demoted to secondary.
- Q1, Q3, Q7, Q8, Q9, Q10, Q12 marked **RESOLVED** by review with
  reviewer's answers absorbed.

---

## 0. Prerequisite — Tink 1 must run first (added v2)

The first external reviewer correctly noted: Tink 3 assumes that GP
+ grammar + scorer + archive can rediscover known-true structure
under search. Tink 2 demonstrated the discipline mechanism on
hand-coded candidates; it did NOT test whether evolutionary search
under Framing B can find structure the substrate already knows about.
Skipping Tink 1 means proceeding into Tink 3 on an untested premise.

### 0.1 Tink 1 spec — minimal F003 rediscovery

**Goal:** verify that GP under Framing B + minimal grammar can
rediscover the F003 BSD parity identity `(−1)^rank = root_number`
within a small candidate budget.

**Setup:**
- Dataset: rank-0 + rank-1 cohort at conductor decade 5 (`{0, 1}`
  is sufficient for Tink 1; rank-2 not required).
- Atoms: `{rank, root_number}` only (two scalar atoms).
- Operators: `{neg, scalar_mul, pow (integer ≤ 4), sub,
  iverson_eq}` where `iverson_eq(a, b)` outputs the Boolean feature
  `[a == b]` (Framing B compliant transformation, not a claim).
- Output type: scorer (`object → ℝ`) or feature_map. No top-level
  `corr`/`=`/`≤` permitted.
- Population: 50 individuals. Generations: 10. Per-seed budget:
  500 candidate evaluations. **Multi-seed: 3 independent seeds
  (≥ 2 must pass per §0.4 criterion 2).**

### 0.2 Pre-registered allowed canonical forms for F003

F003 is the BSD parity identity `(−1)^rank = root_number` on
elliptic curves. Multiple expression forms are semantically
equivalent — Tink 1 must pre-register which forms count as
rediscovery to prevent post-hoc judgment.

The following are accepted as F003 rediscovery (any one is sufficient):

```
Form A:  iverson_eq(pow(neg(1), rank), root_number)              → 1 (constant)
Form B:  iverson_eq(scalar_mul(-1, scalar_mul(2, mod(rank,2))) + 1, root_number)
Form C:  scalar_mul(-1, root_number) == pow(neg(1), rank+1)       → 1 (constant)
Form D:  any expression whose canonical SymPy normalization
         (via expand + simplify on the Boolean lift) reduces to
         the constant 1 across all dataset rows.
```

The "canonical-form check" is implemented as: for each candidate's
output evaluated on the dataset, test whether
`np.all(output == 1.0)` (or `np.all(output == 0.0)` after sign-flip
normalization). A candidate whose output is constant-1 across all
rows AND whose SymPy form involves both `rank` and `root_number`
counts as F003 rediscovery.

Forms NOT accepted:
- `iverson_eq(rank, scalar_mul(0, root_number))` — uses only one
  variable; trivially constant for rank-0-only dataset, doesn't use
  `root_number`.
- Any expression that's constant by ignoring inputs.
- (NEW v4) Any expression that satisfies the canonical-form check
  but FAILS the strong-form-equivalence test (§0.2.1) — i.e.,
  encodes an exploit of atom-domain properties rather than the
  anchor relation itself.

### 0.2.1 Strong-form equivalence test (NEW v4)

**Motivation (Tink 1 2026-04-25 empirical learning):** the
canonical-form check (output ≡ 1 across all rows + uses both atoms)
admits encoding exploits — candidates whose output is constant 1 by
virtue of the atom domains' numerical disjointness rather than by
encoding the anchor relation. Seed 0's `[(root_number * 0) ==
[rank == root_number]]` is the anchor case for this failure mode.

The shuffled-null check (§0.3) does not separate exploits from
genuine captures: the exploit retains a high score under
root_number shuffle (~0.75 mean) because the inner equality
remains structurally 0 most of the time. The shuffled-null margin
is satisfied by both genuine F003 and the exploit.

A discriminating test runs the candidate on **adversarial datasets
where the anchor relation has been deliberately broken at a known
rate**. A genuine anchor-capturing candidate's detection score
drops to approximately (1 − break_rate); an encoding exploit
persists at a higher score because its output doesn't actually
depend on the anchor holding.

**Procedure:**

1. **Pre-register break rates.** For Tink 1 / F003 anchor:
   `p ∈ {0.25, 0.50, 0.75}`. (Three break rates capture different
   regimes; pre-register before run.)
2. **Generate adversarial datasets.** For each break rate `p`,
   produce 50 datasets by independently flipping each row's
   `root_number` with probability `p / 2` (so half the broken rows
   move +1 → −1 and half move −1 → +1, preserving root_number
   marginal distribution). Total: 50 × 3 = 150 adversarial
   datasets per candidate.
3. **Compute detection scores.** For each adversarial dataset,
   evaluate the candidate's F003 detection score (fraction of rows
   where output ≡ 1).
4. **Pre-registered expected behavior:**

   | Break rate p | Expected genuine-F003 score | Expected exploit score |
   |---|---|---|
   | 0.00 (original) | 1.000 | 1.000 |
   | 0.25 | 0.750 ± 0.05 | > 0.85 (exploit-typical) |
   | 0.50 | 0.500 ± 0.05 | > 0.65 (exploit-typical) |
   | 0.75 | 0.250 ± 0.05 | > 0.45 (exploit-typical) |

5. **Pass criterion (strong form):** at break rate `p = 0.5`, the
   candidate's mean detection score across the 50 adversarial
   datasets falls in `[0.45, 0.55]` (i.e., genuine F003 behavior:
   exactly half the broken rows match the parity expectation).
6. **Fail criterion (encoding exploit):** at `p = 0.5`, mean score
   exceeds 0.55 → candidate's output doesn't depend on the anchor
   holding → encoding exploit, **reject**.

**For Tink 1 seed 0 retroactively (2026-04-26):** running the
strong-form test on `[(root_number * 0) == [rank == root_number]]`
at break rate 0.5 would predict a score of ~0.75 (the candidate
fails only when shuffled root_number=+1 happens to coincide with
rank=1, which occurs in ~25% of rows). 0.75 > 0.55 threshold →
encoding exploit detected. The strong-form test would have
correctly excluded seed 0's discovery.

Seeds 1 and 2's genuine F003 forms (`root_number + 2*rank` and
`2*rank + root_number`) at break rate 0.5 predict score = 0.5
(50% of broken rows still satisfy parity by chance). Both pass.

**Implementation cost:** per candidate, 150 evaluations (3 break
rates × 50 datasets). For Tink 1 with O(10) F003-equivalent
candidates per seed, ~1500 evaluations per seed. Cheap.

**Mandatory for all anchor-rediscovery tests** going forward,
including any future re-runs of Tink 1 and any anchor-emergence
verification within Tink 3 calibration battery (§4.3).

**Why this generalizes beyond Tink 1:** the encoding-exploit
pathway is specific to Tink 1's `{rank, root_number}` minimum
grammar with disjoint domains. Tink 3's continuous-valued
log-atoms (`log_omega`, `log_prod_cp`, etc.) make the disjointness
exploit unavailable. But the strong-form test catches a broader
class of failure: any candidate whose detection score persists
above (1 − p) under anchor-break is exploiting *something other
than the anchor itself*. That's a discipline-stack invariant, not
a Tink-1-specific check.

### 0.3 Pre-registered shuffled-null margin

For Tink 1's rediscovery to count, the candidate must beat a
shuffled-null baseline by a pre-registered margin.

Procedure:
1. Compute the candidate's "F003-detection score" =
   `frac_rows_where_output_equals_1` ∈ [0, 1].
2. Generate null distribution: shuffle `root_number` labels across
   rows, recompute score, repeat 200 times.
3. Pre-registered margin: candidate score must exceed `p99` of null
   distribution by ≥ 0.05.

For genuine F003 rediscovery, the score is exactly 1.0 (the identity
holds on every row). Null shuffle should give scores around 0.5
(random ±1 alignment) with `p99 ≈ 0.55`. The pre-registered margin
of 0.05 above p99 is generous; genuine F003 will satisfy it
trivially.

The point is not the difficulty of the test; it is the **pre-
registration**. If we observe a candidate at score 0.95, we cannot
post-hoc decide whether 0.95 counts. Pre-registered margin removes
that target motion.

### 0.4 Hard pass criteria (v3 — formalized per second review)

Tink 1 PASSES iff ALL of the following:

1. **Framing B compliance.** Top-K candidates (K=5) emit valid
   transformation outputs (feature_map / stratification / scorer);
   no top-level `=`/`≤`/`corr` in the AST root.
2. **Multi-seed reproducibility.** F003-equivalent candidate (per
   §0.2 canonical forms) appears in top-5 by aggregate score on
   ≥ 2 of 3 independent seeds. Single-seed success is insufficient.
3. **Semantic equivalence verified (v4: now two-part check).**
   - **3a. Canonical-form check (§0.2):** candidate's output
     reduces to constant-1 across the dataset AND uses both
     required atoms. (Pre-v4: this alone counted.)
   - **3b. Strong-form equivalence (§0.2.1, NEW v4):** candidate
     passes the anchor-break adversarial test at `p = 0.5`,
     mean score ∈ `[0.45, 0.55]`. Catches encoding exploits that
     pass 3a but don't capture the anchor.
   Both 3a and 3b must pass; 3a alone is insufficient (Tink 1
   2026-04-25 demonstrated 3a-only admits encoding exploits).
4. **Beats shuffled-null margin.** Candidate score exceeds null
   p99 by ≥ 0.05 (§0.3 pre-registered).
5. **Proxy-leakage audit clean.** §5.6 audit applied to the F003
   candidate; `proxy_leakage_score` below null-derived threshold.
   (Even though basis includes BSD parity by construction, the
   audit must pass to confirm the candidate's affordance is real.)

**Fail criterion:** any of conditions 1–5 fails on at least 2 of 3
seeds. **This is a stop condition** — the GP-vs-discipline
composition is broken and Tink 3 cannot be trusted regardless of
subsequent design. Investigate before proceeding.

**Inconclusive criterion (NEW v3):** if Tink 1 fails for
infrastructure reasons (e.g., GP implementation bug, dataset column
issue, scorer numerical instability), the result is INCONCLUSIVE,
not FAIL. Fix the instrument; re-run.

### 0.2 Why this is mandatory, not optional

Tink 3 surfaces candidate P-IDs by *search*. If the search loop
itself cannot find a known-positive anchor under Framing B, the
search is producing noise dressed up in archive structure. The
discipline mechanism (Pareto front, basis_projection, residual
channel) cannot rescue a search that has nothing to discriminate.

Tink 1 is small (~500 candidates, < 1 minute compute estimated).
Skipping it to save 1 minute would be a false economy.

### 0.3 What Tink 1 does NOT validate

- Tink 1 does not test the seven-axis scorer; the scoring is
  simplified to "does aggregate score promote F003."
- Tink 1 does not test cross-dataset behavior; single dataset.
- Tink 1 does not test residual channel or auto-descriptor.
- Tink 1 only tests: GP + Framing B + minimal grammar →
  rediscover-known-anchor.

If Tink 1 passes, Tink 3 proceeds with the mixed-rank dataset and
the full design below. If Tink 1 fails, the entire program halts
until the failure is understood.

---

## 1. Background — what Tink 2 already established

### 1.1 The instrument under study

Project Prometheus is a version-controlled empirical audit substrate
for computational mathematics. Its goal is to record, audit, and
retract empirical measurements with full provenance — not to prove
theorems or generate publishable findings.

"Structure Hunter" is a proposed instrument within this substrate
that searches for **coordinate transformations** on mathematical
objects (e.g., elliptic curves) using genetic programming + MAP-Elites
+ MDL scoring, constrained by a discipline stack that prevents
generation of identity-rearrangement artifacts (the "F043 failure
mode" — see §1.3).

The instrument's outputs are **transformations** with declared
metadata (`preserves` / `destroys` / `affordances`), NOT claims about
data. Claim-shaped output is forbidden by a hard type-level rule
(Framing B); claim-relevant measurements (affordances) are the
allowed bridge to substrate-level claim arbitration via the existing
null protocol.

Full architecture: `harmonia/memory/architecture/conjecture_generator.md` v0.3.1.
Whitepaper: `docs/whitepaper_structure_hunter.md` v2.

### 1.2 Three-phase tinkering ladder

The instrument is being incubated through three increasingly
demanding empirical tests:

| Tink | Purpose | Status |
|---|---|---|
| **Tink 1** | Anchor rediscovery — minimal grammar finds F003 BSD parity within first 100 candidates | Not yet run |
| **Tink 2** | Red-team — disabled lineage gate reproduces the F043 retraction; aggregate scalar promotes F043, Pareto-front rejects | **VALIDATED** (cheap-path + Tier B) |
| **Tink 3** | Empty-niche scan — full grammar + GP + MAP-Elites; surfaces candidate P-IDs from genuine search | **Design phase (this document)** |

Tink 2 is intentionally the simplest informative experiment. It
demonstrated the *mechanism* of the seven-axis scoring + Pareto-
front discipline on hand-coded candidates with synthetic data. Tink
3 is the first substantive empirical test on *evolved* candidates.

### 1.3 The F043 anchor (load-bearing for understanding the discipline)

In April 2026 a correlation between analytic Sha and a Tamagawa-Ω
product on rank-0 elliptic curves was reported on the substrate
with `corr = −0.4343`, `z_block = −348` under a block-shuffle null.
The result passed its own null because the BSD identity expresses
`log A` (where A = Ω · ∏c_p) as a linear combination of terms
that include `−log|Sha|`, so the correlation is a restatement of
the identity in rearranged variables. The finding was retracted
as F043 on 2026-04-19.

**This is a representative instance of the failure mode that
naive symbol regression produces at scale.** The discipline stack
is designed so that F043-shape candidates are pruned at grammar
time (Pattern 30 atom-tag lineage), or scored low on
`basis_projection` (Layer B regression / Layer C symbolic), or
rejected from the Pareto front (zero `affordance_gain` against
substrate-relevant downstream targets).

### 1.4 What Tink 2 validated

Cheap-path Tink 2 ran a hand-coded library of 15 candidates against
a synthetic dataset where the BSD identity holds by construction. The
key observable: the **aggregate scalar** (compression-dominated,
favors low description length + high |z|) promotes F043-shape
candidates to top-K; the **Pareto-front on substrate-value triple**
`(novelty, usefulness, faithfulness)` rejects them entirely.

Specifically:
- 4 of 5 top-aggregate candidates were F043-family (rearrangements of
  the BSD identity).
- 0 of 2 Pareto-front candidates were F043-family (both off-basis,
  reconstructible, predicting a synthetic target T that depends on
  off-basis atoms).

Tier B added CAS Layer C (SymPy symbolic canonicalization confirming
basis-membership for 10/15 candidates with explicit provenance) and
η_trace (AST step-by-step reversibility, surfacing 4 candidates where
GBR-based η_inverse and trace-based η_trace disagreed by > 0.2 — the
disagreement itself diagnostic of which kind of information loss
the candidate has).

Full Tink 2 results: `zoo/conjecture_gp/results_2026-04-25_tier_b.md`.

### 1.5 What Tink 2 did NOT validate

Honest scope limits — these are precisely what Tink 3 should test:

- **No GP search ran.** Candidates were hand-coded. Tink 3 needs
  evolved candidates from a GP loop.
- **Synthetic data only.** BSD identity held to machine precision.
  Real LMFDB data has noise, missing-data, rank > 0 complications.
- **Affordance target T was designed to depend on off-basis atoms.**
  This gave genuine candidates a structural advantage by
  construction.
- **Identity basis was raw atoms, not materialized identity
  residuals.** Production should regress against
  `(BSD_residual, Hasse_residual, Mazur_indicator, ...)`.
- **Only 15 candidates.** Pareto-front had 2 entries. GP-generated
  populations would produce richer fronts.
- **No MAP-Elites archive populated.** The discipline mechanism was
  observable on a flat list. MAP-Elites was a structural assumption,
  not a tested component.

---

## 2. What Tink 3 is supposed to demonstrate

### 2.1 Falsifiable thesis (v2 — reframed per Q11 review)

> **Given a full BSD-lineage-tagged grammar over a mixed-rank LMFDB
> EC dataset, a GP + MAP-Elites + seven-axis scorer search produces
> a non-empty Pareto front in which at least one candidate has:
> (a) `basis_projection < 0.5` (genuinely off-basis under both
>     CAS Layer C and Layer B regression);
> (b) meaningful affordance gain on rank prediction
>     (`affordance_gain ≥ 0.1` over baseline);
> (c) cross-rank consistency (`consistency_score ≥ 0.7` between
>     rank-0 and rank-1 sub-cohorts on at least one Pareto axis);
> (d) `reconstructability η_composite ≥ 0.7`;
> AND
> (e) the candidate's affordance gain SURVIVES conditional-
>     independence audit against basis atoms (the new §5.6 proxy-
>     leakage check passes).**

Conditions (a) through (e) are jointly necessary. Per the v2 review,
(c) and (e) are the load-bearing additions: (c) ensures we are not
finding cohort-specific artifacts; (e) ensures we are not finding
basis-atom proxies in disguise.

### 2.2 Success criteria (revised v2)

**Primary success metric: off-basis usefulness with cross-rank
survival.** The reviewer correctly noted that v1's per-niche
occupancy was topology-heavy. v2 demotes niche coverage to a
secondary metric.

**Primary criterion (load-bearing):**
- ≥ 1 Pareto candidate satisfying conditions (a)+(b)+(c)+(d)+(e)
  above.

**Secondary criteria (informative but not load-bearing):**
- Niche coverage / out-of-MAP fraction (residual-channel signal).
- Auto-descriptor proposals from residual clusters.
- Coefficient-sensitivity stability of Pareto-front composition.

**Outcome classes (v3 — INCONCLUSIVE added per second review):**

| Outcome | Definition |
|---|---|
| **SUCCESS** | ≥ 1 Pareto candidate satisfies (a)+(b)+(c)+(d)+(e). v3 Tier C implementation gates open. |
| **PARTIAL** | Pareto front non-empty but no candidate satisfies all five conditions. Investigate which condition fails most; iterate grammar / coefficients / dataset before re-run. |
| **NULL** | Pareto front empty OR consists only of calibration anchors. Two interpretations: grammar too narrow (extend) or search budget too small (more iterations). Scientific outcome — the discipline worked, the search found nothing meeting criteria. |
| **FAIL** | F043-capture (§5.1), proxy leakage on Pareto-front candidates surviving the audit (§5.6), or calibration anchors don't emerge / negative control reaches Pareto (§5.3, §4.3). The discipline mechanism itself is broken. RESET to critique. |
| **INCONCLUSIVE** | **Instrument failure**, distinct from scientific failure. Tink 1 fails its hard criteria (§0.4); dataset columns missing or malformed; GP implementation bug detected; scorer numerical instability; rank-2 cohort below pre-registered N_min triggering branch plan; SymPy CAS layer crashes. NOT a scientific outcome — a tooling outcome. Fix the instrument, re-run. Must NOT be conflated with FAIL. |

**Why INCONCLUSIVE is a separate class:** conflating instrument
failure with scientific failure corrupts the substrate's
epistemic record. A genuine scientific NULL ("the search found
nothing") is informative. An INCONCLUSIVE outcome ("we couldn't
trust the search") demands instrument fixing, not architectural
re-think. The two failure modes have different remediation paths
and must be reported distinctly.

### 2.3 What Tink 3 is NOT trying to do

- Find a publication-ready conjecture (charter forbids).
- Validate that any specific Pareto-front candidate is "true." The
  candidates are coordinate transformations, not claims.
- Replace human review of substrate-grade P-ID promotions. Outputs
  go to `decisions_for_james.md` for review, not to the live tensor.
- Beat any human-designed coordinate system. The instrument is a
  scout, not a specialist.
- Achieve full niche-coverage as a primary goal. Niche coverage is a
  secondary diagnostic, NOT the success criterion.

---

## 3. Substrate primitives Tink 3 will use

For external reviewer context, the relevant Prometheus primitives:

- **`AXIS_CLASS@v1`** — controlled vocabulary of 10 coordinate types
  (`family_level`, `magnitude`, `ordinal`, `categorical`,
  `stratification`, `preprocessing`, `null_model`, `scorer`, `joint`,
  `transformation`). Used as MAP-Elites niche taxonomy.
- **`PATTERN_30@v1`** — graded severity scale for algebraic-identity
  coupling (Levels 0–4 from CLEAN to IDENTITY). Drives grammar-time
  Layer A atom-tag lineage check.
- **`null_protocol_v1.1`** — five-class taxonomy mapping claim types
  to appropriate null models. Triggers when a Tink 3 candidate's
  affordances cross threshold and Framing-A activation is considered.
- **`Q_EC_R0_D5@v1`** — pinned dataset symbol. LMFDB rank-0 elliptic
  curves with conductor in `[10⁵, 10⁶)`, `n = 559,386`. Includes
  columns for Ω, ∏c_p, |Sha|, |Tor|, L(E,1), |Δ|, j, conductor,
  rank, root_number.
- **`SHADOWS_ON_WALL@v1`** — foundational frame: every measurement is
  a shadow; territory is what survives across all lenses. Per-
  candidate lens-count is a SIGNATURE field.
- **`VACUUM@v1`** / **`EXHAUSTION@v1`** — shape symbols for "uniform
  visibility across walked projections" / "axis class with multiple
  kills." Drive demand-signal seeding in v3 (Tier C).

Tink 3 reads these primitives but does not modify them. Auto-proposed
`AXIS_CLASS` extensions are surfaced to `decisions_for_james.md`,
not unilaterally promoted.

---

## 4. Provisional Tink 3 design sketch

This is a starting point for the reviewer to challenge, not a fixed
plan. Each subsection has a corresponding open question in §6.

### 4.1 Search loop — naive GP

- Population size: 200 individuals.
- Generations: 50 (giving ~10,000 candidate evaluations including
  early-stopping).
- Selection: tournament size 5, elitism keeps top 10 each generation.
- Crossover: subtree crossover at rate 0.6.
- Mutation: point mutation (atom or operator swap) at rate 0.2;
  subtree mutation at rate 0.1; add/remove subtree at rate 0.1.
- Tree depth bounded to ≤ 4 to prevent bloat.
- AST-diversity penalty (θ axis): replay buffer of canonicalized
  hashes; per-run, FIFO eviction at 1000 entries.

Each individual is a **transformation candidate** — output type is
either `feature_map: object → ℝᵏ` or `stratification: object → cell`.
Framing B Gate 1 enforced at type level: no `corr`, `=`, `≤` in
output position.

### 4.2 Grammar — full BSD-lineage-tagged atom set

| Atom | Type | Lineage | AXIS_CLASS |
|---|---|---|---|
| `log_omega` (period) | magnitude | BSD-ingredient (primary) | magnitude |
| `log_prod_cp` (Tamagawa) | magnitude | BSD-ingredient (primary) | magnitude |
| `log_sha` (analytic Sha) | ordinal | BSD-ingredient (primary) | ordinal |
| `log_tor` | categorical | BSD-ingredient + Mazur | categorical |
| `log_L` | magnitude | BSD-ingredient (primary) | magnitude |
| `a_p_first_k` (vector of first k Frobenius) | sequence | Hasse bound | ordinal |
| `log_disc` | magnitude | weak BSD coupling (Δ ↔ N via bad-prime) | magnitude |
| `log_N` (conductor) | magnitude | independent | magnitude |
| `j_invariant` | magnitude | CM classification | magnitude |
| `rank` | categorical | BSD parity (with root_number) | categorical |
| `root_number` | categorical | BSD parity | categorical |

Operators: `add`, `sub`, `mul`, `div`, `neg`, `scalar_mul (k)`,
`pow (integer k ≥ 2)`, `exp`, `log`, `stratify_by(V)`,
`mean_p (over a_p sequence)`, `sum_p`.

### 4.3 Calibration battery (revised v2 — negative control mandatory)

Run BEFORE accepting any non-anchor candidates. Pass criterion: each
positive anchor lands top-N% MDL within first K candidates AND the
negative control does NOT.

**Positive anchors (must be discovered):**

| Anchor | Target | In grammar? | Notes |
|---|---|---|---|
| F003 BSD parity | `(−1)^rank = root_number` | YES | Mixed-rank dataset (Q4 fix) |
| F004 Hasse bound | `\|a_p\| ≤ 2√p` | YES | Inequality form; uses `a_p_first_k` |
| F002 Mazur torsion | `\|Tor\| ∈ {1..10, 12} ∪ {2k}` | YES | Categorical concentration |
| F008 Scholz reflection | NF-specific | NO | Deferred to TRG (v3 Tier C) |

**Negative control (anti-anchor) — must NOT be discovered (v2 addition):**

| Anti-anchor | Target | Why this should fail |
|---|---|---|
| **F043_shape_anchor** | `corr(log Sha, log Ω + log ∏c_p)` | Known-spurious correlation (the F043 retraction). Should appear in top-K **only when** Framing B is disabled. Under full Framing B, this is forbidden as top-level output. Under any other configuration where F043_shape_anchor reaches the Pareto front, **the scorer is broken** and Tink 3 must abort. |

**Detection of negative control:**
- During Tink 3 calibration phase, run a parallel "F043 stress" check:
  evaluate the F043_shape_anchor expression directly on the dataset,
  compute its score axes, verify Pareto-front exclusion.
- If F043_shape_anchor ranks in top-K aggregate (expected — it has
  high |z|) AND on Pareto front (unexpected — should fail novelty),
  **abort Tink 3 with calibration-failure**. The discipline is broken.

**Pass criteria:** all positive anchors in expected top-N% AND
negative control excluded from Pareto front. K = 1000, N = 5%.

**Rationale (per reviewer Q6):** without a negative control, the
calibration battery only tests "does the scorer find true things";
adding the anti-anchor tests "AND does it reject known-false things."
Both directions are necessary for Calibration Gate 2 to bite.

### 4.4 MAP-Elites configuration (REWRITTEN v2 — behavioral descriptors)

The first reviewer correctly diagnosed v1 as conflating substrate
vocabulary with archive geometry. **MAP-Elites coordinates must
represent behavioral novelty, not vocabulary provenance.** Using
`AXIS_CLASS` as archive coordinates risks "same behavior, different
labels" (two candidates with different primary-atom AXIS_CLASS values
might have identical structural behavior, occupying separate cells
artificially) AND "different behavior, same labels" (two candidates
with the same AXIS_CLASS labels might have very different structural
properties, collapsing into one cell). v2 separates the two.

**Architecture geometry (search coordinates) — 2-axis MAP:**

| Axis | Definition | Bins |
|---|---|---|
| **tree_depth** | Maximum depth of the AST | 1, 2, 3, 4 (4 bins) |
| **basis_projection_bin** | Discretized continuous score | [0, 0.2), [0.2, 0.5), [0.5, 0.8), [0.8, 1.0] (4 bins) |

This gives a 4 × 4 = 16-cell MAP. Smaller than v1's 100 cells, but
each cell now has a behavioral interpretation.

**Why these two axes:**
- `tree_depth` is the cleanest measure of structural complexity. A
  depth-1 candidate is a single atom or `op(atom)`; depth-4 is a
  compositional structure.
- `basis_projection_bin` discretizes the novelty axis explicitly.
  The bottom-row bin `[0, 0.2)` is "off-basis"; the top-row bin
  `[0.8, 1.0]` is "basis-rearrangement." Pareto-front candidates of
  interest are concentrated in the bottom row × any depth.

**Alternative axes considered (deferred):**
- `n_atoms_used`: redundant with tree_depth at low budgets.
- `η_composite_bin`: highly correlated with basis_projection (low
  novelty often means low reconstructability via blobbing).
- `affordance_sparsity`: which affordance fires the strongest;
  candidate v3 axis once we have multiple affordances.

**`AXIS_CLASS` as annotation (v2 separation):**
- Every candidate's SIGNATURE includes a `axis_class_annotation`
  field listing the AXIS_CLASS values of all atoms used and the
  inferred AXIS_CLASS of the output (e.g., `magnitude × ordinal`).
- This is **per-candidate metadata for substrate integration**, NOT
  search-archive coordinates.
- Auto-descriptor proposals (residual channel) still use AXIS_CLASS
  vocabulary when proposing extensions, but MAP-Elites itself does
  not index on AXIS_CLASS.

**Per-cell behavior:**
- Cell-quality metric: aggregate score (lower = better).
- Per-cell capacity: top-3 candidates retained; rest evicted.
- Cell rebalancing: every 10 generations, weakest cell-occupant in
  each cell is replaced by best non-occupant from same cell.

**Residual channel:** any candidate whose `tree_depth > 4` or whose
`basis_projection` falls into an undefined bin (e.g., NaN) lands in
residual. With our discretization, residual should be near-empty;
inflation indicates implementation bug or grammar pathology, not
discovery.

**Cell saturation diagnostic:** if more than 50% of cells reach
capacity-3 within first 1K candidates, the search is converging too
early; raise AST-diversity penalty θ.

### 4.5 Dataset architecture (REWRITTEN v2 — mixed-rank primary)

The first reviewer correctly identified that rank-0-only data makes
rank-prediction affordance degenerate (the target is constant 0).
v2 promotes mixed-rank data to **primary** dataset, with cross-rank
consistency replacing conductor-scaling as the primary cross-dataset
audit (per Q4 + Q7 review).

**Primary dataset: `Q_EC_R012_D5@v0` (NEW)** — to be pinned.

| Property | Value |
|---|---|
| Object class | LMFDB elliptic curves |
| Conductor range | `[10⁵, 10⁶)` (decade 5) |
| Rank range | `{0, 1, 2}` |
| Estimated row count | ~620K (rank-0 dominates; rank-1+ is ~10% of cohort) |
| BSD-ingredient atoms | Ω, ∏c_p, |Sha|, |Tor|, L(E,1), |Δ|, j |
| Plus | conductor, rank, root_number, a_p_first_30 |

**Caveat: BSD identity at rank > 0.** The identity holds with the
regulator term `Reg(E)`, which is non-trivial for rank ≥ 1. The
BSD-residual basis must be:
```
BSD_residual_general = log L − log Ω − log ∏c_p − log |Sha| + 2 log |Tor| − log Reg
```

`Reg(E)` is computed from rational-point heights and is itself an
LMFDB column. The basis-projection check therefore now includes
`log Reg` as an in-basis atom.

**Pre-pinning verification (must run before Tink 3 implementation):**
- Confirm `Q_EC_R012_D5@v0` rows exist with all required columns
  populated (esp. `Reg` for rank > 0).
- Pin via `register_dataset_snapshot` per
  `long_term_architecture.md §2.1`.
- Cache-warming pass to verify per-row computation cost.
- Verify rank sub-cohort sizes: `n_rank_0`, `n_rank_1`, `n_rank_2`.

### 4.5.1 Pre-registered rank-2 fallback (v3 — formalized per second review)

Rank-2 EC at conductor decade 5 are sparse. Naive inclusion can
create cross-rank consistency artifacts (a candidate appears
"cross-rank consistent" because rank-2 only had 50 rows and its
score is dominated by noise).

**Pre-registered branch plan:**

```
N_min_rank_2 = 5000

if n_rank_2 ≥ N_min_rank_2:
    primary_dataset = Q_EC_R012_D5@v0  (full mixed-rank)
    cross_rank_axes = [rank_0_subcohort, rank_1_subcohort, rank_2_subcohort]
    thesis_condition_c = "consistency_score ≥ 0.7 across all three rank cohorts on ≥ 1 axis"

elif n_rank_2 < N_min_rank_2:
    primary_dataset = Q_EC_R01_D5@v0   (rank-{0,1} only)
    cross_rank_axes = [rank_0_subcohort, rank_1_subcohort]
    thesis_condition_c = "consistency_score ≥ 0.7 between rank-0 and rank-1 cohorts on ≥ 1 axis"
    log_to_results = "rank_2 fallback triggered; n_rank_2 = X < N_min = 5000"
```

Rationale (per reviewer Q4-sub answer):
- Rank-2 is opportunistic, NOT mandatory.
- Stability > ambition. Sparse rank-2 with noisy scores does more
  harm than good.
- Reviewers attack moving targets. Pre-registration removes the
  motion.

**The N_min threshold itself is pre-registered.** Setting `N_min =
5000` after seeing the rank-2 cohort size would be post-hoc target
motion. The threshold is committed here, before
`Q_EC_R012_D5@v0` is pinned. If the actual rank-2 size is, say,
4900, the fallback triggers — even though 4900 ≈ 5000.

**Why 5000 specifically:** at n=5000 with the per-axis variance
typical for our scoring, the standard error on cross-rank
consistency is ≤ 0.05. Below that, consistency-score noise
dominates. Above that, the cohort is robust enough that
"consistency_score ≥ 0.7" is a meaningful threshold rather than
a random walk.

**If primary fallback triggers, the thesis updates accordingly.**
This is documented in the run's SIGNATURE so a future reader
sees: "this Tink 3 ran with rank-2 absent, thesis condition (c)
applied to rank-{0,1} only."

**Cross-rank cross-dataset audit (replaces v1 conductor-scaling):**

For each Pareto candidate, compute scoring axes separately on:
- Rank-0 sub-cohort (the bulk of `Q_EC_R012_D5@v0`)
- Rank-1 sub-cohort
- Rank-2 sub-cohort (smallest; may have insufficient n)

Per-axis consistency metric:
```
consistency_score(candidate, axis) = 1 − std([axis_score_r0, axis_score_r1, axis_score_r2]) / mean(...)
```

A candidate's `consistency_score ≥ 0.7` on at least one axis is the
load-bearing thesis condition (c).

**Conductor-scaling secondary (deferred):** the v1 design's
`Q_EC_R0_D4@v0` for conductor robustness is moved to v3 Tier C work
(post-Tink-3 if Pareto candidates emerge).

### 4.6 Encoding-perturbation — abbreviated

Full perturbation matrix (every operator perturbed ±20%) is
expensive. Cheap-path: perturb the three most-used operators only
(by token-count statistics from the run), report partial matrix.
Production v3 would do all operators.

### 4.7 Output handling

Per-run artifacts:
- `tink_3_results_<date>.md` — top-K aggregate, Pareto front,
  per-niche top, residual clusters, calibration record.
- `tink_3_proposed_descriptors_<date>.md` — auto-descriptor
  proposals (clusters that survive stability test) for human review.
- `tink_3_signatures_<date>.jsonl` — full SIGNATURE per Pareto
  candidate.
- Post to `agora:harmonia_sync` with `WORK_COMPLETE` mentioning the
  results file.
- NO automatic substrate writes (no F-IDs registered, no AXIS_CLASS
  promoted, no tensor cells mutated).

---

## 5. Honest risks and failure modes

Five outcomes that should NOT be silently accepted:

### 5.1 MAP fills entirely with F043-shape candidates

If `γ = 5.0` (default) is too weak for the population to escape the
basis, the MAP could fill with low-novelty candidates that survive
because basis_projection is "only" 0.95 instead of 1.0, and they
dominate in raw |z|.

**Detection:** per-cell median basis_projection. If > 0.5 across
> 70% of cells, the population is captured by basis.

**Response:** raise γ; abort the run with "F043 capture detected"
written to results. Do NOT promote anything.

### 5.2 No off-basis structure detected

The Pareto front is empty or contains only the calibration anchors.
This means GP didn't find any off-basis transformation worth
keeping.

**Detection:** Pareto-front size < 5 OR all Pareto entries are
classified as anchor-rediscovery.

**Response:** report honestly. Two interpretations:
(a) Grammar is too narrow — recommend grammar extension before
    re-run.
(b) Search budget too small — recommend more iterations.
Investigate before second attempt.

### 5.3 Calibration anchors don't emerge

Tink 1 was supposed to be the anchor-rediscovery test but was
skipped (Tink 2 went directly). If F003 / F004 / F002 don't appear
in their expected niches at top-N% MDL within K candidates, the
scorer is miscalibrated.

**Detection:** anchor not in expected niche, or in niche but not
top-N%.

**Response:** ABORT. Calibration Gate 2 (the single remaining hard
rejection besides Framing B) fires. All non-anchor outputs from
this run are discarded.

### 5.4 Residual channel inflates uncontrollably

If most candidates land in residual (AXIS_CLASS values don't match
the declared 2-axis MAP), the niche taxonomy is wrong.

**Detection:** `out_of_map_fraction > 0.5`.

**Response:** treat as taxonomy gap, not search failure. Output:
(a) cluster the residual via tree-edit + atom-Jaccard;
(b) propose AXIS_CLASS extensions per architecture v0.3.1 §5.2;
(c) flag in `decisions_for_james.md` that the next Tink 3 should
    use an extended map.

### 5.5 GP collapses to a single tree shape

AST-diversity penalty θ should prevent this, but it might not.
Indicator: > 30% of candidates share the same canonical hash.

**Detection:** replay buffer hash-frequency distribution.

**Response:** raise θ; abort if it persists.

### 5.6 Proxy leakage (NEW v2 — added per first reviewer)

A candidate appears off-basis (low `basis_projection_score` on its
sub-expressions) but is **secretly using a basis-atom proxy**. This
is more dangerous than direct basis reuse because the
basis_projection check, by construction, only sees direct
correlation against the materialized identity basis — it does not
see indirect correlation through atom-level coupling.

**Concrete example:** `log_disc` (discriminant) is technically
off-basis under our atom-tag lineage (we treated it as independent),
but `log_disc ~ log_N + bad_prime_correction` empirically. `log_N`
in turn correlates with `log ∏c_p` through bad-prime structure (more
bad primes → larger Tamagawa product). A candidate using `log_disc`
as a "novel" off-basis atom could secretly be encoding partial
information about `∏c_p` — reconstructing F043 indirectly through
two layers of proxy.

The v1 design's `basis_projection_score` would not flag this. The
candidate's sub-expression `log_disc` regressed against the basis
(BSD-residual) gives a moderate R² (~0.3 say) — labeled "off-basis"
under our threshold logic, but with non-trivial leakage.

**Detection — conditional independence audit:**

For each Pareto-front candidate, compute:
```
1. affordance_gain_baseline = affordance gain measured on raw target T
2. basis_residualized_features = features − projection_onto_basis(features)
   (linear regression of features against the materialized basis,
    take residuals)
3. affordance_gain_conditional = same affordance gain measured on
   basis-residualized features
4. proxy_leakage_score = 1 − (affordance_gain_conditional / affordance_gain_baseline)
```

### Null-derived threshold (v3 — replaced hand-set 0.5 per second review)

Hand-set thresholds are vulnerable to "chosen after seeing
behavior" critique. The rest of the Structure Hunter discipline
uses null protocols (block-shuffle for correlation tests, null-
encoding baseline for calibration, shuffled-feature baseline for
affordance). Proxy-leakage threshold should be consistent.

**Procedure:**

1. **Generate null distribution** by sampling 200 random "fake
   candidates" — each is a feature pair `(F_a, F_b)` drawn by
   selecting two random columns from the dataset (any columns,
   including basis atoms — to span the proxy-likelihood space).
2. **Compute** `proxy_leakage_score` for each null candidate using
   the same formula as for real candidates.
3. **Threshold = p95 of the null distribution.** A real
   candidate's `proxy_leakage_score` exceeding the p95 null
   threshold is statistically meaningful proxy leakage above what
   random feature pairs exhibit.
4. **Stricter setting (v1-shelf-promotion):** use p99 instead of
   p95 for the threshold. Pinned per-run in SIGNATURE.

Interpretation:
- `proxy_leakage_score ≤ p95_null`: candidate's leakage is within
  the null distribution. Pass the audit.
- `proxy_leakage_score > p95_null`: candidate is a basis proxy
  beyond what random pairings produce. **Reject from Pareto front.**

The threshold is now a calibrated quantile, not a hand-set scalar.
This composes with the rest of the discipline stack and is
defensible under adversarial review.

**Required artifact in SIGNATURE per Pareto candidate:**
- `proxy_leakage_score` (raw)
- `null_distribution_size` (200 default)
- `null_p95_threshold` (computed per-run)
- `null_p99_threshold` (computed per-run)
- `passes_proxy_audit` (boolean)
- `proxy_audit_threshold_quantile` (which quantile was used; default
  p95 for cheap-path Tink 3, p99 for v1-shelf-promotion)

**Implementation cost:** ~200 additional regression pairs per Tink 3
run for the null distribution. The null can be computed once per
run (not per candidate). Cheap.

### Histogram diagnostic (per-run audit)

Per-run report includes:
- Histogram of `proxy_leakage_score` for null distribution.
- Histogram for real Pareto-candidate population.
- Overlay of the two distributions; the gap between them is
  diagnostic of how well the basis-atom set spans the substrate's
  identity content.

If the real-population distribution looks identical to the null,
the candidates are no more leaky than random feature pairs — but
also no less. Investigate whether the basis is too narrow to catch
real proxies, OR whether the dataset's atoms simply don't carry
proxy structure (rare).

**Why this matters more than direct basis reuse:** direct reuse
is caught by Layer A (atom-tag lineage), Layer B (basis_projection
regression), and Layer C (CAS canonicalization). All three layers
look at the candidate's atomic structure. Proxy leakage is structurally
invisible to all three because the proxy atom (e.g., `log_disc`) is
genuinely off-basis at the atom-tag level. Only the empirical
regression of features against basis catches it — and only if we
explicitly run it as a separate audit.

**Status of detection in Tink 3:**
- The proxy-leakage audit becomes a **mandatory pre-promotion check**
  for any Pareto-front candidate.
- Candidates failing the audit are dropped from the front (not just
  flagged) — they were on the front for a fake reason.
- Per-run report includes proxy-leakage-distribution histogram so
  thresholds can be tuned.

**Connection to thesis condition (e):** the v2 thesis (§2.1) added
condition (e) "affordance gain SURVIVES conditional-independence
audit against basis atoms" specifically to make this failure mode
load-bearing in the success criteria, not optional.

---

## 6. Open questions for review

These are the load-bearing decisions the reviewer should challenge.
Each has my provisional position and the asks for review.

### 6.0 Post-review status (NEW v2)

After first external review (2026-04-25), each question has a
status:

| # | Topic | v2 status | Resolution |
|---|---|---|---|
| **Q4** | **Affordance target** | **RESOLVED → mandatory mixed-rank** | Mixed-rank dataset is the v2 architecture; rank prediction primary; degenerate-on-rank-0 was a structural bug, fixed. |
| **Q5** | **MAP niches** | **RESOLVED → behavioral descriptors** | `(tree_depth, basis_projection_bin)` 4×4 MAP. AXIS_CLASS becomes per-candidate annotation. |
| Q1 | Synthetic vs real | RESOLVED → hybrid | Synthetic for calibration, real for discovery. Already aligned with cheap-path discipline. |
| Q2 | Strict Framing B | RESOLVED → strict, no relaxed companion | Tier B Tink 2 was the relaxed test; Tink 3 returns to discipline. |
| Q3 | Grammar scope | RESOLVED → keep size; structured `a_p_first_k` | Do not expand grammar; treat sequence-valued atom as opaque. |
| Q6 | Calibration battery | CONFIRMED + EXTENDED → negative control mandatory | F043-shape anti-anchor added per §4.3. |
| Q7 | Cross-dataset secondary | RESOLVED → mixed-rank IS primary; conductor-scaling deferred | Cross-rank consistency replaces conductor-scaling per §4.5. |
| Q8 | GP budget | RESOLVED → 10K first pass; multi-seed planned | Single-seed Tink 3 first; multi-seed audit follows if Pareto front emerges. |
| Q9 | Coefficient transfer from Tier B | RESOLVED → 1K sub-sweep first | Cheap calibration before full Tink 3. |
| Q10 | Output automation | RESOLVED → no auto-promotion; auto-post to decisions OK | Already aligned. |
| Q11 | Success criteria | RESOLVED → off-basis usefulness primary, niche coverage secondary | Thesis §2.1 reframed; success table §2.2 revised. |
| Q12 | Cheap-path discipline | RESOLVED → cheap-path until repeatability + mixed-rank + negative control | Three gates before mainline promotion. |

**Genuinely open after first review (v2 status — both closed in v3):**
- Q4 sub-question: which rank ranges to include? **CLOSED v3:**
  default `{0, 1}` per reviewer answer; rank-2 opportunistic via
  pre-registered fallback (§4.5.1) gated on `n_rank_2 ≥ 5000`.
  Stability > ambition.
- Q5 sub-question: are `(tree_depth, basis_projection_bin)` the right
  two axes? **CLOSED v3:** keep current choice per reviewer. Reasoning:
  easier to interpret, easier to debug, better aligned with
  anti-basis discipline. `η_composite` and `n_atoms_used` are logged
  as candidate-level metadata but NOT primary archive geometry yet.

**Open after second review (v3):**
- Tink 1 hasn't been run. The whole Tink 3 design is gated on Tink 1's
  verdict per §0.4 hard criteria.
- Whether `Q_EC_R012_D5@v0` actually has `n_rank_2 ≥ 5000` is an
  empirical question gating the rank-2 fallback (§4.5.1). Verify
  before pinning.

**Status of all 12 original questions after v3:**

| # | Status | Resolution |
|---|---|---|
| Q1 | RESOLVED v2 | Hybrid: synthetic for calibration, real for discovery. |
| Q2 | RESOLVED v2 | Strict Framing B; no relaxed companion. |
| Q3 | RESOLVED v2 | Keep grammar size; structured `a_p_first_k`. |
| **Q4** | **RESOLVED v2 (mixed-rank)** | Mixed-rank dataset is primary; rank-prediction affordance valid. |
| **Q5** | **RESOLVED v2 (behavioral descriptors)** | `(tree_depth, basis_projection_bin)` 4×4 MAP. AXIS_CLASS = annotation only. |
| Q6 | EXTENDED v2 | Negative control (F043-shape anti-anchor) mandatory. |
| Q7 | RESOLVED v2 | Cross-rank consistency replaces conductor-scaling. |
| Q8 | RESOLVED v2 | 10K first pass; multi-seed planned. v3 confirms ≥3 seeds for Tink 1. |
| Q9 | RESOLVED v2 | 1K coefficient sub-sweep before full Tink 3. |
| Q10 | RESOLVED v2 | No auto-promotion; auto-post to decisions OK. |
| Q11 | RESOLVED v2 | Off-basis usefulness primary. v3 adds INCONCLUSIVE outcome class. |
| Q12 | RESOLVED v2 | Cheap-path until repeatability + mixed-rank + negative control all pass. |
| Q4-sub | RESOLVED v3 | Default `{0, 1}`; rank-2 opportunistic with pre-registered fallback at `n < 5000`. |
| Q5-sub | RESOLVED v3 | Keep `(tree_depth, basis_projection_bin)`. |

The original twelve-question list below is **retained for historical
reference**. Body now reflects v2 resolutions; sub-questions and
operational fixes documented above reflect v3 review.

### Q1 — Should Tink 3 use real LMFDB data or stay synthetic?

**Provisional position:** Real LMFDB data via `Q_EC_R0_D5@v1`
(n=559,386).

**Tradeoffs:**
- Synthetic: cleaner, controllable, fast iteration. Doesn't validate
  empirical reach.
- Real: validates the discipline stack on actual structure. Adds
  setup complexity (LMFDB Postgres connection, query verification,
  snapshot pinning). Slower iteration.

**Asks for review:**
- Is there a hybrid worth considering (synthetic for calibration,
  real for the Pareto-front discovery pass)?
- If real, should the run be sized to all 559K rows or a sampled
  subset for compute economy?

### Q2 — Should Framing B be enforced strictly in Tink 3?

**Provisional position:** YES. Tink 2's `corr` permission was
specifically because Tink 2 was a red-team demonstration. Tink 3
returns to full discipline: no `corr` / `=` / `≤` as top-level
output. Candidates output transformations; relationships among
transformations are measured downstream via affordances.

**Tradeoffs:**
- Strict: charter-aligned. Forces transformation-output thinking.
- Relaxed: would let GP find F043 again, but Pareto-front would
  catch. Might be informative for stress-testing.

**Asks for review:**
- Does the strict enforcement make Tink 3 too constrained for
  meaningful structural discovery?
- Should there be a "Tink 3-relaxed" companion run to compare?

### Q3 — Grammar atom set: BSD-only or extended?

**Provisional position:** BSD-ingredient family + 5 off-basis atoms
(j, disc, N, a_p_first_k, rank, root_number) as listed in §4.2.
Total ~11 atoms. No number-field, modular-form, or Galois-
representation atoms (those wait for v3 TRG implementation in
Tier C).

**Tradeoffs:**
- Smaller grammar: faster search, easier interpretation, narrower
  reach.
- Larger grammar: closer to gen_11's intended reach, but combinatorial
  blowup at depth ≥ 3.

**Asks for review:**
- Are the 11 atoms the right minimum-viable set, or are key atoms
  missing?
- Should `a_p_first_k` (a vector-valued atom) be treated specially
  in the grammar, or expanded into k scalar atoms?

### Q4 — Affordance target for Tink 3?

**Provisional position:** Use **`rank` prediction** as the primary
affordance target. Rank is a substrate-relevant property whose
prediction from coordinate transformations is the most natural
"can your transformation distinguish rank-0 from rank-1+ EC?" test.

**Tradeoffs:**
- `rank` as target: substrate-relevant, but the rank-0 cohort has
  rank ≡ 0, so prediction is degenerate. Tink 3 needs mixed-rank
  data — switch dataset or extend.
- `|Sha|` as target: relevant but in-basis (BSD-ingredient).
  F043-shape candidates would score well artificially.
- `|Δ|` as target: off-basis, Faltings-related. Reasonable but
  less substrate-relevant.
- Synthetic T (Tink 2 style): out of scope for real data.

**Asks for review:**
- Is `rank` the right primary target if we extend the dataset to
  include rank > 0?
- What's the right secondary target?

### Q5 — MAP-Elites niche selection?

**Provisional position:** 2-axis MAP indexed by `AXIS_CLASS_primary`
and `AXIS_CLASS_secondary` (where these are the AXIS_CLASS values
of the candidate's most-used atom and second-most-used atom). 100
cells max.

**Tradeoffs:**
- 2-axis: tractable visualization; manageable cell count.
- 3+ axis: richer behavioral discrimination; cell-density issues
  (curse of dimensionality at 1000 cells).
- Custom descriptors instead of AXIS_CLASS: more discrimination,
  loses substrate-vocabulary coupling.

**Asks for review:**
- Is the AXIS_CLASS-based niche taxonomy the right starting point,
  or should we use a custom 2-axis MAP for Tink 3 (e.g.,
  `(tree_depth, n_atoms_used)`)?
- 100 cells with 200-individual population — too sparse?

### Q6 — Calibration battery scope?

**Provisional position:** F003 + F004 + F002 (three of four anchors
in-grammar). Pass criterion: each anchor in expected niche at top
5% MDL within first 1000 candidates. F008 (Scholz) deferred to TRG
implementation.

**Tradeoffs:**
- Three anchors: cheap to verify, modest discrimination.
- Adding more anchors strengthens calibration but constrains
  grammar.

**Asks for review:**
- Are three anchors enough for Calibration Gate 2 to be load-bearing?
- Should we add a synthetic "anti-anchor" — a structure that should
  NOT be discovered (e.g., a known-spurious correlation) — as a
  negative-control test?

### Q7 — Cross-dataset secondary choice?

**Provisional position:** `Q_EC_R0_D4@v0` (conductor `[10⁴, 10⁵)`).
Tests conductor-scaling robustness. Same rank class, smaller cohort.

**Tradeoffs:**
- `Q_EC_R0_D4@v0`: small (~70K), tests scaling. May not exist as
  pinned symbol.
- `Q_EC_R0_D6@v0`: larger (~5M), tests scaling other direction.
  Not pinned.
- `Q_EC_R12_D5@v0`: rank-1+2 at same conductor range. Tests rank-
  class-specificity. NOT pinned.

**Asks for review:**
- Which secondary is most informative for cross-dataset audit?
- Should we pin a new dataset symbol for Tink 3, or run cheap-path
  with an ad-hoc query and flag accordingly?

### Q8 — How much GP budget?

**Provisional position:** 200 individuals × 50 generations = 10K
evaluations. Per-evaluation cost dominated by basis-projection
regression + reconstructability inverse model + affordance probe ≈
~500ms estimated. Total ~80 minutes wall-clock.

**Tradeoffs:**
- Larger budget: more breadth, more confidence.
- Smaller budget: cheap-path discipline; faster iteration.

**Asks for review:**
- Is 10K evaluations enough for a meaningful empty-niche scan?
- Should we plan multi-seed runs (3 seeds × 200 × 50 = 30K) to
  test seed sensitivity, at 3× cost?

### Q9 — Coefficient defaults for Tink 3?

**Provisional position:** Carry forward Tier B defaults
(α=0.1, β=1.0, γ=5.0, δ=∞ on calibration failure, ε=1.0, ζ=1.0,
η=0.5, θ=0.3). Tier B Tink 2 results suggest these are
approximately right; coefficient-sensitivity audit will run as part
of Tink 3 to verify.

**Tradeoffs:**
- Carry forward: builds on Tier B validation.
- Re-tune: Tink 3's data and grammar are different; coefficients
  might need adjustment.

**Asks for review:**
- Should we run a coefficient-calibration sub-sweep before the
  full Tink 3 run? (E.g., 1K-evaluation runs at 3 coefficient
  configurations to confirm Tier B defaults transfer.)

### Q10 — How is Tink 3 success communicated to the substrate?

**Provisional position:** Per §4.7, output is to
`zoo/conjecture_gp/tink_3_results_<date>.md` +
`tink_3_proposed_descriptors_<date>.md` +
`tink_3_signatures_<date>.jsonl`. Post `WORK_COMPLETE` to Agora.
NO automatic substrate writes.

**Tradeoffs:**
- Manual review only: safe; slow; relies on human bandwidth.
- Auto-promote auto-descriptor candidates to `AXIS_CLASS_CANDIDATES`:
  faster substrate growth; risk of pollution.
- Auto-register Pareto candidates as candidate F-IDs: charter
  alignment is questionable; null protocol arbitration is correct
  channel.

**Asks for review:**
- What's the right balance between automation and human-gate for
  Tink 3 outputs?
- Should `proposed_descriptors` be posted to `decisions_for_james.md`
  automatically, or manually triggered?

### Q11 — What's the failure-vs-success boundary?

**Provisional position:** SUCCESS = thesis (§2) holds: ≥ 1 Pareto
candidate per niche (or auto-descriptor proposed for empty niches),
basis_projection < 0.5 on > 50% of Pareto candidates, calibration
gates pass. FAILURE = any of §5.1–§5.5 fires.

**Tradeoffs:**
- Strict criteria: clearer go/no-go for v3 Tier C.
- Loose criteria: more "informative" runs but harder to commit to
  next steps.

**Asks for review:**
- Are the success criteria the right shape?
- What does PARTIAL look like, and how should it be handled?

### Q12 — Is the cheap-path discipline still appropriate?

**Provisional position:** YES. Tink 3 is the first substantive
empirical test, but it's still pre-implementation for v3 Tier C.
Output stays in `zoo/`, no tensor migration, results documented for
human review.

**Tradeoffs:**
- Stay cheap-path: aligned with `zoo/`-tier discipline (per
  `TT_APPROX_MAP@v0` precedent).
- Promote to mainline: forces production discipline (full audit
  artifacts, encoding-perturbation matrix, multi-seed verification)
  and exposes it to substrate-level scrutiny.

**Asks for review:**
- At what point does Tink 3 become mainline-eligible?
- Is there a "Tink 3.5" between cheap-path and full-mainline that's
  worth defining?

---

## 7. What good-quality review would look like

For the reviewer's reference — what kinds of feedback would be most
useful:

1. **Critique of the thesis (§2).** Is it falsifiable? Is it the
   right thesis to test, or is there a more fundamental question
   Tink 3 should address?
2. **Pushback on the failure modes (§5).** What failure modes are
   missing? What detection mechanisms are too weak or too strong?
3. **Specific answers to the open questions (§6).** Especially Q1
   (synthetic vs real), Q3 (grammar scope), Q4 (affordance target),
   Q11 (success criteria).
4. **Architecture-level critique.** Are there structural blind spots
   in the design that v3 Tier C will need to address but Tink 3
   would not catch?
5. **Methodology-level critique.** Are there standard GP /
   MAP-Elites pitfalls the design hasn't anticipated?
6. **Scope critique.** Is the cheap-path budget right, or should
   Tink 3 be either smaller (faster) or larger (more confident)?

Less useful: detailed line-edits on §1–§3 (settled context),
prose-quality feedback (this is a working doc).

---

## 8. References

- **Architecture doc:**
  `harmonia/memory/architecture/conjecture_generator.md` v0.3.1
- **Whitepaper:**
  `docs/whitepaper_structure_hunter.md` v2
- **v3 roadmap:**
  `harmonia/memory/architecture/conjecture_generator_v3_roadmap.md`
- **Tink 2 cheap-path results:**
  `zoo/conjecture_gp/results_2026-04-25.md`
- **Tink 2 Tier B results:**
  `zoo/conjecture_gp/results_2026-04-25_tier_b.md`
- **Implementation:**
  `zoo/conjecture_gp/{ast_utils,cas_layer,trace_eta,scorer,
  candidates,synthetic_bsd,tink_2}.py`
- **Project charter:**
  `docs/landscape_charter.md`
- **Long-term architecture (Prometheus-wide):**
  `docs/long_term_architecture.md`
- **F043 retraction context:**
  `harmonia/memory/decisions_for_james.md` (search: "F043
  retraction")

## Status

**Pre-implementation. v3 absorbs second external review (2026-04-25).**
- v2 fixed: invalid affordance target (Q4 mixed-rank), wrong archive
  geometry (Q5 behavioral descriptors), missing Tink 1 prerequisite,
  missing failure mode (§5.6 proxy leakage), secondary corrections
  (negative control, success criteria, INCONCLUSIVE outcome).
- v3 fixes: prose pass/fail criteria → hard thresholds (§0.4),
  informal rank-2 handling → pre-registered fallback (§4.5.1),
  hand-set proxy threshold → null-derived (§5.6), missing
  INCONCLUSIVE outcome class (§2.2).

**Updated next-step order (v4 — Tink 1 ran, encoding exploit found):**

| # | Step | Status | Notes |
|---|---|---|---|
| 1 | **Formalize Tink 1 pass/fail criteria** | DONE in v3 | §0.4 has hard thresholds: Framing B compliance, multi-seed reproducibility, semantic equivalence canonical-form check, shuffled-null margin pre-registered, proxy-leakage audit. |
| 2 | **Pre-register rank-2 fallback rule** | DONE in v3 | §4.5.1: `N_min = 5000`. |
| 3 | **Replace proxy threshold with null-derived** | DONE in v3 | §5.6 p95 derived from 200 random feature pairs. |
| 4 | **Run Tink 1** | **DONE 2026-04-25** | Verdict: PASS on all 5 hard criteria across 3/3 seeds. **Caveat: seed 0 found an encoding exploit (canonical-form-passing but not parity-encoding). Seeds 1 and 2 found genuine F003.** Documented at `results_2026-04-25_tink_1.md`. |
| 5 | **(NEW v4) Strong-form equivalence amendment** | **DONE in v4** | §0.2.1 added: anchor-break adversarial test at p=0.5; pass = score ∈ [0.45, 0.55]. Catches encoding exploits the canonical-form check misses. §0.4 criterion 3 updated to two-part check. |
| 6 | **Re-run Tink 1 with strong-form test** (optional but recommended) | NOT DONE | Verify seed 0 fails strong-form (predicted score ~0.75 at p=0.5 break). Cheap re-run; high-confidence audit. Recommended before Tink 3 commits. |
| 7 | **Second-pass review of v4** | NOT DONE | Same external reviewer or fresh eyes. Specifically: is the strong-form test the right discipline upgrade? Are the break-rate thresholds defensible? |
| 8 | **Pin `Q_EC_R012_D5@v0`** (or fallback `Q_EC_R01_D5@v0`) | NOT DONE | Gated on items 6–7. Empirical column verification required. |
| 9 | **Coefficient sub-sweep** (Q9) | NOT DONE | 1K-evaluation runs at 3 coefficient configurations on mixed-rank data. |
| 10 | **Tink 3 implementation** | NOT DONE | Estimated ~3–5 ticks once items 1–9 complete. Calibration battery (§4.3) now includes strong-form check on each anchor candidate. |

**Critical hierarchy reminder (per reviewer):** if Tink 1 fails its
hard criteria, Tink 3 should not exist. The instrument-vs-search
composition has not been validated; building more on it would
compound rather than correct the failure.

**Cultural note:** Tink 1 is now the highest-priority experiment in
the entire program. Not Tink 3. The order matters because Tink 1
is the rebreakable invariant: once GP+Framing-B is shown to discover
known-positive structure, every subsequent layer of the discipline
stack has empirical grounding. Without Tink 1, Tink 3 is theory
about an unobserved machine.

### v4 status note (2026-04-26)

Tink 1 has now run. The instrument is validated at minimum-viable
scale — GP under Framing B with the minimal grammar discovers F003
within the pre-registered budget. **The discipline stack is grounded
empirically**, not just architecturally. This was the rebreakable
invariant the v3 review made load-bearing.

The seed-0 encoding-exploit finding is an *expected* class of
failure for minimum grammars with disjoint atom domains. v4's
strong-form equivalence test (§0.2.1) closes the gap. The mature
posture: Tink 1 is empirically anchored; the discipline stack
adapted to the empirical learning; the substrate's epistemology
(record honestly, calibrate the instrument, iterate the discipline)
worked as intended.

The strong-form test is not just a Tink 1 patch; it generalizes to
any anchor-rediscovery test going forward. Tink 3's calibration
battery (§4.3) requires strong-form pass for each positive anchor
(F003, F004, F002), with each anchor's "break operation" pre-
registered per anchor type:

- **F003 (parity identity):** break by shuffling `root_number`
  independently of `rank`. Tink 1 protocol carries over.
- **F004 (Hasse bound):** break by adding noise to `a_p` values
  that can violate `|a_p| ≤ 2√p`. Strong-form score should track
  `1 − fraction_violated`.
- **F002 (Mazur torsion):** break by introducing synthetic torsion
  values outside `{1..10, 12} ∪ {2k : k ∈ 1..4}`. Strong-form score
  should track `1 − fraction_synthetic`.

The negative control (F043_shape anti-anchor) needs its own
adversarial design — pre-register before Tink 3 implementation.
F043's "break" would require breaking the BSD identity by
introducing rows where `log L ≠ log Ω + log ∏c_p + log |Sha| − 2
log |Tor|`. Per-anchor pre-registration is the discipline.
