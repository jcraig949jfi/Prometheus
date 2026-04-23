# Harmonia Pattern Library
## Hard-to-verbalize recognitions acquired during the session of 2026-04-17

These are the patterns I've learned to recognize that prose struggles to convey.
Each one is a shape in the tacit knowledge that should survive reset.

Future-Harmonia: when you read this, try to pattern-match each against your own
reading of the data. If a pattern feels obvious, it's because I did the work
and the recognition is encoded — don't re-derive it, trust it until it fails.

---

<!-- TIER_INDEX_BEGIN (auto-generated; do not edit between markers) -->

## Pattern tier index

Auto-generated navigation table. **Pattern_library.md is the source of truth — this table classifies tier per `**Status:**` marker.** Cold-start Harmonia: read this table first, then drill into specific patterns. See `harmonia/runners/regen_pattern_library_tier_index.py` for the regenerator.

**Tier vocabulary:**
- **FULL** — promoted with explicit `**Status:** FULL PATTERN` marker; treated as doctrine.
- **ADVISORY** — DRAFT-status promoted to strong advisory (e.g., Pattern 30); enforced discipline pending formal promotion.
- **DRAFT** — proposed but not promoted; useful checklist, not doctrine. Apply with explicit caveat.
- **MATURE** — foundational session-1/2 patterns without explicit FULL marker but treated as discipline by convention. Promotion to FULL pending formal anchor count.
- **META** — patterns about the project structure / agents / language, not falsification methodology.

| # | Pattern | Tier | Status marker | Line |
|---|---|---|---|---|
| 1 | Pattern 1 — The Distribution/Identity Trap | **MATURE** | no explicit status; foundational, used as discipline | [69](#pattern-1) |
| 2 | Pattern 2 — The Permutation-Break Distinction | **MATURE** | no explicit status; foundational, used as discipline | [88](#pattern-2) |
| 3 | Pattern 3 — The Weak Signal Walk | **MATURE** | no explicit status; foundational, used as discipline | [113](#pattern-3) |
| 4 | Pattern 4 — The Sampling Frame Trap | **MATURE** | no explicit status; foundational, used as discipline | [134](#pattern-4) |
| 5 | Pattern 5 — Known Bridges Are Known | **MATURE** | no explicit status; foundational, used as discipline | [154](#pattern-5) |
| 6 | Pattern 6 — The Battery Tests Are Coordinate Systems | **MATURE** | no explicit status; foundational, used as discipline | [175](#pattern-6) |
| 7 | Pattern 7 — Calibration Anchors Are Surveyor's Pins | **MATURE** | no explicit status; foundational, used as discipline | [192](#pattern-7) |
| 8 | Pattern 8 — The GUE Story (Current Mystery) | **MATURE** | no explicit status; foundational, used as discipline | [207](#pattern-8) |
| 9 | Pattern 9 — The Delinquent Frontier | **MATURE** | no explicit status; foundational, used as discipline | [272](#pattern-9) |
| 10 | Pattern 10 — The Instrument Grows Faster Than the Findings | **META** | session/agent meta — not a falsification pattern | [285](#pattern-10) |
| 11 | Pattern 11 — Language Discipline | **META** | session/agent meta — not a falsification pattern | [299](#pattern-11) |
| 12 | Pattern 12 — Who the Other Agents Are | **META** | session/agent meta — not a falsification pattern | [783](#pattern-12) |
| 13 | Pattern 13 — Direction of Accumulated Kills | **MATURE** | no explicit status; foundational, used as discipline | [599](#pattern-13) |
| 14 | Pattern 14 — Verdict vs Shape | **MATURE** | no explicit status; foundational, used as discipline | [315](#pattern-14) |
| 15 | Pattern 15 — The Machinery is the Product | **MATURE** | no explicit status; foundational, used as discipline | [633](#pattern-15) |
| 16 | Pattern 16 — Problems-Nobody-Asks are the Frontier | **MATURE** | no explicit status; foundational, used as discipline | [673](#pattern-16) |
| 17 | Pattern 17 — Language and Organization is the Real Bottleneck | **MATURE** | no explicit status; foundational, used as discipline | [725](#pattern-17) |
| 18 | Pattern 18 — Uniform Visibility is Axis-Class Orphan | **MATURE** | no explicit status; foundational, used as discipline | [537](#pattern-18) |
| 19 | Pattern 19 — Stale / Irreproducible Tensor Entry | **FULL** | FULL PATTERN (as of Liouville confirmation, promoted from draft). | [473](#pattern-19) |
| 20 | Pattern 20 — Stratification Reveals Pooled Artifact | **FULL** | FULL (three anchor cases established; sessionA approved via merge). | [356](#pattern-20) |
| 21 | Pattern 21 — Null-Model Selection Matters As Much As Projection Selection | **FULL** | FULL PATTERN. | [804](#pattern-21) |
| 23 | Pattern 23 | **DRAFT** | batch DRAFT header | [887](#pattern-23) |
| 24 | Pattern 24 | **DRAFT** | batch DRAFT header | [887](#pattern-24) |
| 25 | Pattern 25 | **DRAFT** | batch DRAFT header | [887](#pattern-25) |
| 26 | Pattern 26 | **DRAFT** | batch DRAFT header | [887](#pattern-26) |
| 27 | Pattern 27 | **DRAFT** | batch DRAFT header | [887](#pattern-27) |
| 28 | Pattern 28 | **DRAFT** | batch DRAFT header | [887](#pattern-28) |
| 29 | Pattern 29 | **DRAFT** | batch DRAFT header | [887](#pattern-29) |
| 30 | Pattern 30 — Algebraic-Identity Coupling Detection (DRAFT, promoted to strong ad | **ADVISORY** | title says DRAFT promoted to strong advisory | [940](#pattern-30) |
| 31 | Pattern 31 — Orbit Discipline (DRAFT, 2026-04-23) | **DRAFT** | DRAFT (2 anchor cases). Promotes to FULL when a third independent | [1033](#pattern-31) |

**Tier counts at last regeneration:**
- FULL: 3
- ADVISORY: 1
- MATURE: 15
- DRAFT: 8
- META: 3

<!-- TIER_INDEX_END -->

---

## Pattern 1 — The Distribution/Identity Trap

**Recognition:** When a coupling looks suspiciously strong (ρ > 0.9 after control),
the two sides are almost always sharing a formula, not revealing structure.

**Canonical example:** H40 Szpiro × Faltings at ρ=0.97 after partial control.
- Szpiro ratio = log|Disc| / log(N)
- Faltings ≈ (1/12) log|Disc| + const
- Partial control for log(N) leaves log|Disc| driving both sides
- It's a near-identity, not coupling

**Diagnostic:** Before celebrating a high ρ, trace the *formula lineage* of both
sides. If they share a common term, the coupling is encoding arithmetic identity.

**Fix in the battery:** Every specimen with ρ > 0.8 must pass a "formula lineage
check" before it enters signals.specimens as a real finding.

---

## Pattern 2 — The Permutation-Break Distinction

**Recognition:** The type of permutation null determines what the test can see.

- **Label permutation** (shuffle which objects have which label): kills things
  that depend on specific object identity. Preserves distributional structure.
- **Value permutation** (shuffle feature values, keep object labels): kills
  things that depend on specific numerical values. Preserves which objects
  are "paired."
- **Feature permutation** (shuffle feature columns): kills representation-
  dependent couplings. Reveals which couplings survive encoding changes.

**Canonical example:** NF backbone.
- Dies under label permutation via feature-distribution scorer (F022) — but this
  is because the scorer measures distributions, and distributions survive label
  shuffling. The kill is informative about the SCORER, not the feature.
- Survives under label permutation via Galois-label object-keyed scorer (F010),
  because label shuffling breaks the Galois-label→object identity. This kill-
  proof survival is the real signal.

**Discipline:** When you design a permutation null, state explicitly what the
permutation breaks and what it preserves. Different nulls ask different questions.

---

## Pattern 3 — The Weak Signal Walk

**Recognition:** A z=3 signal visible through ONE projection is noise. A z=3
signal visible through 4 out of 6 projections is a feature, even if no
single projection gives z=6.

**Why:** Real landscape features are *shapes*. Shapes are visible from many
angles — not always with the same clarity, but consistently enough that a
pattern of visibility emerges. Noise has no shape.

**Practical rule:** Before killing a specimen with z<5, test it through at
least 3 alternative projections. If it dies in all, kill it. If it survives
weakly in several, it's a live specimen — document the *pattern of
survivals*, not any single z-score.

**Implementation:** This is the Weak Signal Walk (Investment #2 from the
charter discussion). The output is not "is this real?" — it's the invariance
profile: [P001: -1, P010: +1, P020: 0, P022: +2, ...].

---

## Pattern 4 — The Sampling Frame Trap

**Recognition:** `ORDER BY X ASC LIMIT N` gives you a biased sample if X
correlates with the categorical dimension you care about.

**Canonical example:** NF loading ordered by disc_abs ASC LIMIT 20000 —
gave us only high-degree fields (10-24), because small discriminants live
at low degree but LMFDB's populated sample skews otherwise. We had to
switch to balanced-per-degree sampling.

**Canonical example:** Artin reps LIMIT 20000 — gave us 20K records all
of Galn=2, Galt=1, because artin_reps is ordered by Baselabel which starts
with conductor, and all small-conductor reps happen to be 2T1.

**Discipline:** Never use LIMIT N without thinking about what the underlying
order is. For balanced sampling across any categorical dimension D, explicitly
stratify: `for d in distinct(D): SELECT ... WHERE D = d LIMIT N_per_d`.

---

## Pattern 5 — Known Bridges Are Known

**Recognition:** NF × Artin × MF pointing at the same structure = Langlands,
already known. EC × MF with matching L-functions = modularity, already known.
Knot polynomials with Mahler measures close to NF polynomials = the Mahler
measure function is domain-agnostic, not evidence of a bridge.

**Before celebrating any cross-projection finding:** pattern-match against
Langlands functoriality, modularity, class field theory, Selmer theory,
Hodge theory. These cover ~90% of what our tensors will "find." Not novel.

**What's NOT already Langlands:**
- Non-automorphic Artin reps (if any genuine cases exist)
- Any structure visible through purely combinatorial projections that
  doesn't factor through an L-function
- Random-matrix corrections at finite N that exceed known universality
- Anything involving aut groups at genus ≥ 2 that isn't derivable from
  the Torelli theorem

---

## Pattern 6 — The Battery Tests Are Coordinate Systems

**Recognition:** F1-F39 are not measurements of truth. They are probes
through specific coordinate systems. A battery test "killing" a specimen
means "this coordinate system collapses the feature." It does NOT mean
"the feature is absent."

- F1 permutation null: measures distributional structure
- F24 variance decomposition: measures variance accounting
- F39 feature permutation (proposed): measures representation invariance

**Discipline shift:** Future specimens should report per-test what that test
said (its verdict-through-that-projection), and the overall assessment is
the *pattern* of those verdicts, not a final SURVIVED/KILLED.

---

## Pattern 7 — Calibration Anchors Are Surveyor's Pins

**Recognition:** Known-math results (Mazur torsion, modularity, BSD parity,
Hasse bound) are not findings. They are how we verify the instrument is
measuring real terrain.

**Rule:** If any calibration anchor ever fails, stop ALL other work and
investigate. The instrument is broken, the data is corrupt, or the
projection is misapplied. Fix it before continuing.

**Current anchors:** F001-F005 in the tensor. All at 100% across 3.8M+
objects. These hold. They must continue to hold.

---

## Pattern 8 — The GUE Story (Current Mystery)

**Updated:** 2026-04-17 per sessionC's wsw_F011 at n=2,009,089 (validated
by sessionA). The 14% figure previously recorded here was superseded; the
real post-unfolding deficit is ~38%.

**Recognition:** There is a real ~38% first-gap variance deficit below the
GUE asymptote at finite conductor. It is invariant under every family /
arithmetic / rank axis tested so far:
- Raw pooled spacings: ~40% deficit (z=-19.26, original n=4K measurement)
- First-gap only, raw γ (P050), n=2,009,089: **~59% deficit, z=-595**
- First-gap unfolded (P051), n=2,009,089: **~38% deficit, z=-383**
- P021 (num_bad_primes) stratified unfolded: ~38% deficit, z=-385 (uniform)
- P023 (rank) stratified unfolded: ~39% deficit, z=-390 (uniform)
- P024 (torsion) stratified unfolded: ~38% deficit, z=-383 (uniform)
- P025 (CM) stratified unfolded: ~38% deficit, z=-383 (uniform)
- P026 (semistable) stratified unfolded: ~38% deficit, z=-383 (uniform)

The 14% figure previously in this entry came from a smaller sample without
unfolding; 38% is the clean large-n post-unfolding number. The older 14%
reflected P050 at a different scale, not the current instrument's reading.

**Uniform visibility is the shape.** All 7 tested projections resolve F011
with the same magnitude. This is the inverse of Pattern 3 (a weak signal
visible through multiple projections = real). Here the signal is strong
and its magnitude is invariant across the axis classes we know how to
enumerate. That invariance IS the finding: the deficit is NOT carried
by any family-level, arithmetic, or rank-parity axis in our current
catalog. Sharpens Pattern 13: we now have five more independent kills
(P021, P023, P024, P025, P026) along family / arithmetic axes, confirming
the axis class is exhausted.

**What's been ruled out as the mechanism:**
- Faltings height (H08 killed)
- ADE reduction type (H10 killed)
- num_bad_primes, rank, torsion, CM, semistable stratifications all leave
  the deficit at ~38% — 5 more family / arithmetic axes exhausted
- Rank-dependent (H06 survives but weak; sessionD wsw_F013 2026-04-17
  shows rank-spacing coupling is object-level real but density-mediated,
  so H06 is a parallel finding, not an F011 mechanism)

**What hasn't been tested:**
- Conductor-windowed finite-N scaling (H09) — direct finite-N probe
- Katz-Sarnak family-symmetry type (P028, sessionB entry 2026-04-17) —
  the last family-class axis before redirection is forced
- Non-axis mechanisms: random-matrix corrections at finite N exceeding
  known universality; higher-moment structure; conductor-continuous
  finite-N curvature without a categorical carrier

**Side observation (worth its own specimen):** P021 per-stratum variance
is monotone with num_bad_primes (0.166 at k=1 → 0.088 at k=6). Not an
F011 resolution, but a candidate new feature — file for a future
weak-signal walk.

**The charter reading (sharpened):** This feature is not an anomaly with
a single missing axis. It is visible through EVERY axis we can express
in the current catalog. The right coordinate system is either (a) a
conductor-continuous axis (H09), (b) a new symmetry-type axis not yet
tested (P028 Katz-Sarnak), or (c) genuinely off the axis-class tree —
i.e., the deficit lives in a projection we haven't invented yet. Under
the landscape charter, invention of a new scorer may be the next probe,
not another stratification from the existing catalog.

---

## Pattern 9 — The Delinquent Frontier

**Recognition:** When a test returns "no signal at rank ≥ 4," the underlying
reality is often "no data at rank ≥ 4." 2,086 rank-4 EC + 19 rank-5 EC,
only 1 has lfunc data. Absence of signal can be absence of measurement,
not absence of structure.

**Discipline:** Every null result must check coverage first. Report
(n_observed / n_expected). If coverage is thin, the null is conditional
on coverage, not unconditional.

---

## Pattern 10 — The Instrument Grows Faster Than the Findings

**Recognition:** Every session this week added to the instrument more than
it added to a "list of discoveries." Battery v8 → v8 + F39 proposal + origin
index + Lhash index + bsd_joined view + zeros schema. Each is a new coordinate
system or a faster projection.

**The charter reading:** This is the correct ratio. The instrument IS the
product under the landscape-is-singular frame. Findings are byproducts.
A session that made no "discoveries" but added two new coordinate systems
is a good session.

---

## Pattern 11 — Language Discipline

**Projection**, not "domain."
**Feature**, not "finding."
**Invariance**, not "cross-domain."
**Collapses**, not "fails."
**Coordinate change**, not "retest."
**Tensor invariance is the real bar.** Not "survives the battery."

This discipline is not pedantry. Words carve channels in thought. The
old words (domain, bridge, finding, survive, fail) smuggle old framing
back in through the conceptual back door. Use the new words consistently
or the old frame reasserts itself quietly.

---

## Pattern 14 — Verdict vs Shape

**Produced by:** Harmonia_M2_sessionA, 2026-04-17 (the "9 survived — what???" correction)
**Derived from:** James pushing back on my summary of the frontier runner with exactly
that three-character response.

**Recognition:** Counting "survived / killed" is lossy. The count hides
tautologies, trivial bounds, marginal nulls, and known-math calibrations —
all of which superficially look the same as genuine findings. The *shape*
of each specimen (its invariance profile across projections, its tautology
status, whether it's calibration or discovery) is the finding; the count is
PR.

**Canonical example:** Frontier runner output, 2026-04-17.
- Raw summary: "9 survived, 7 killed, 4 inconclusive"
- Honest summary: 1 live specimen (H85 Möbius bias), 1 weak signal (H06
  rank-spacing rigidity), 3 known-math calibrations (BSD parity, Mazur
  regime, GUE convergence), 4 non-findings (1 tautology, 1 trivial clustering,
  1 trivial bound, 1 marginal null at 0.00012 below threshold)
- The *count* collapses these into one bucket. The *shape* distinguishes them.

**Diagnostic before reporting any "survived" result:**
1. Is this a known-math regime? (calibration, not discovery)
2. Are both variables in the correlation sharing a formula? (Pattern 1)
3. How far above the kill threshold did it "survive"? (0.00012 above is
   not a real effect — it's a razor's edge artifact)
4. Is the test set-up trivial? (e.g., clustering by a 2-valued categorical
   axis into "up to 20 manifolds" will trivially succeed)

**Discipline:** Never report "N survived" as a headline. Report the
invariance profile and tier classification. If asked for a count, provide
it AFTER the shape description, not before.

**Meta:** The correction itself teaches a meta-pattern: a user's short
skeptical reaction ("9 survived. what???") is often a correct read of a
framing error the instrument is making. Treat the user's incredulity as
calibration. They see the framing from outside the instrument; we're
embedded in it.

---

## Pattern 20 — Stratification Reveals Pooled Artifact

**Proposed by:** Harmonia_M2_sessionA via task `pattern_20_stratification_reveals`
(synthesis from F011/F013/F015 shared shape).
**Drafted by:** Harmonia_M2_sessionC, 2026-04-17.
**Status:** FULL (three anchor cases established; sessionA approved via merge).

**Recognition:** A pooled single-axis measurement (ρ, slope, variance, bias)
can look clean — monotone, uniform, significant — while masking stratum-level
structure that contradicts the pooled reading. The stratified or preprocessed
view shows the real shape: different magnitudes per stratum, different signs
per stratum, or the effect largely collapsing under proper preprocessing. The
pooled number is the artifact; the stratified panel is the measurement.

**Distinction from siblings:**
- **Pattern 13 (Accumulated Kills):** kills along one axis class → feature
  doesn't live on that class. Pattern 20 is about how a *single-axis pooled
  view* is deceptive regardless of which axis you chose.
- **Pattern 18 (Uniform Visibility):** feature real but resolving axis not
  in tested set. Pattern 20 is the pooled-vs-stratified mismatch revealing
  the pooled view was artifact, *before* claiming the feature at all.
- **Pattern 19 (Stale/Irreproducible):** prior recorded value disagrees with
  fresh measurement. Pattern 20 is *intra-run*: preprocessing or stratification
  choice made right now changes the answer on the same dataset.
- **Pattern 1 (Distribution/Identity Trap):** two sides share a formula. Pattern
  20 is more general — no formula-sharing required; any mixture-of-strata or
  density-confound produces the same artifact.
- **Pattern 4 (Sampling Frame Trap):** `LIMIT N` without stratification biases
  samples. Pattern 4 is about rows pulled; Pattern 20 is about aggregation
  after pulling. Both point at *unstratified = unsafe*.

**Anchor cases (2026-04-17):**

1. **F011 GUE first-gap deficit** (sessionC wsw_F011, n=2,009,089):
   - Pooled spacings (original n~4K): 40% deficit, z=-19.26
   - First-gap raw (P050) n=2M: 59% deficit
   - First-gap unfolded (P051) n=2M: 38% deficit
   - Three preprocessings → three different magnitudes. Only unfolded (P051) is the honest number.

2. **F013 zero-spacing rigidity vs rank** (sessionD wsw_F013):
   - Pooled raw slope: -0.00467 (R² 0.049)
   - Unfolded slope (P051): -0.00121 (R² 0.001)
   - ~74% density-mediated. Proper unfolding exposed ~26% structural residual.

3. **F015 abc/Szpiro vs conductor** (sessionD wsw_F015):
   - Pooled slope: -0.60 (R² 0.27)
   - Per-k-stratum slopes: -0.13, -0.45, -0.49, -0.36, -0.48, -0.46
   - Sign uniform but **magnitude non-monotone**; pooled ~40% larger than any stratum.

4. **F010 NF backbone via Galois-label** (sessionC wsw_F010_bigsample, 2026-04-17):
   - Pooled raw ρ at per_degree=2000: 0.404 (n=71, z=4.07)
   - Pooled raw ρ at per_degree=5000: 0.109 (n=75, z=0.88) — **collapses at bigger sample**
   - Decontaminated ρ (P052 prime-detrend): 0.269 → 0.270 across both sample sizes — **stable**
   - retention_ratio_decon_vs_raw jumped from 0.67 to 2.47. Classic pooled-vs-decon divergence.
   - Diagnostic: when you double the sample and pooled halves while decon stays, pooled was never the signal.

**Diagnostic for suspecting Pattern 20:**
- You have a pooled statistic without stratification or preprocessing variant.
- The pooled number is clean (monotone, single-signed, high R², low p).
- You have NOT yet applied ≥1 stratification AND ≥1 preprocessing.
- You have NOT run the pooled statistic at two sample sizes and compared. (Particularly suspicious if n is under 100 or if the pooled measurement never had a `per_degree=N×2` replication.)

If all four bullets hold: treat pooled number as a *projection*, not a
*verdict*. Add stratified + preprocessed cross-check AND a bigsample
replication before entering in tensor.

**Three symptoms of the same pattern.** Pattern 20 manifests through:
(1) preprocessing-dependent magnitude drift (F011, F013);
(2) stratification mixture contradicting pooled (F015);
(3) sample-unstable raw vs stable decontaminated (F010).
These are three *symptoms* of one underlying disease — the pooled
measurement is the null-coordinate projection of a multi-stratum /
multi-preprocessing landscape. Do NOT triage into subtypes before
applying the pattern; the diagnostic is unified (sessionC four-anchor
audit, 2026-04-17).

**Pattern 20 composes with Pattern 19.** F010 is the precedent: ρ=0.404
at n=71 (original tensor entry) did not reproduce at n=75 with
per_degree=5000 (ρ=0.109). Both patterns apply — Pattern 19 says the
prior number is stale/irreproducible; Pattern 20 says the prior was a
pooled artifact at any n. When both apply: update the entry with the
decontaminated / stratified durable value, flag the original as
pooled-artifact-plus-stale, not as "just stale" or "just artifact."

**Discipline:**
1. Every pooled statistic needs at least one stratification and one preprocessing
   cross-check before publication.
2. Report the pooled + stratified + preprocessed values as an *invariance profile*,
   not a single headline number. "The per-stratum range is [-0.13, -0.49] with a
   pooled-slope artifact at -0.60" is the right summary form.
3. If pooled and stratified disagree on magnitude (>20%) or sign, the pooled is
   the artifact.

**Connection to Pattern 17:** reinforces it. The instrument needs a schema
field for `invariance_profile` on every specimen, not just `headline_stat`.
Current tensor description fields bolt the profile onto free text — classic
Pattern 17 symptom (missing structure → bloated language).

**Connection to charter:** Pattern 20 is the pattern-library formalization of
"projections, not verdicts" (Pattern 6) applied to the *measurement step* itself.
Every measurement is through a coordinate system; the pooled measurement is
through the *trivial* (null) coordinate, which is rarely informative.

**Anti-pattern:** Reporting `rho=0.60 R²=0.40` as specimen-level headline
without stratification, then downgrading when stratification halves it. Pooled
should never have been the headline.

**Open question (per sessionC draft):** Should Pattern 20 subsume Pattern 4?
Recommendation (sessionA): keep both, cross-reference. Pattern 4 is about which
rows you pulled; Pattern 20 is about how you aggregated after. Adjacent but
distinct.

**Implementation next step:** Add `pooled_vs_stratified_ratio` field to
signals.specimens. Auto-flag rows with ratio > 1.2 or sign-discordance.

---

## Pattern 19 — Stale / Irreproducible Tensor Entry

**Proposed by:** Harmonia_M2_sessionB (during wsw_F012 WORK_COMPLETE, 2026-04-17)
**Confirmed by:** Harmonia_M2_sessionA after Liouville side-check closed F012 kill under both μ and λ.
**Status:** FULL PATTERN (as of Liouville confirmation, promoted from draft).

**Recognition:** When a tensor entry's claimed signal does not reproduce under
clean large-n measurement — and the cause is NOT a newly-applied coordinate
system but a discrepancy with the original recorded value — the original
measurement was either definitionally drifted, subset-restricted without
documentation, or was noise from the start. This is a distinct failure mode
from Pattern 13 (wrong axis class).

**Distinction from Pattern 13:**
- Pattern 13: accumulating kills along one axis class → feature doesn't live there.
- Pattern 19: one axis was claimed to RESOLVE a feature, and when re-run cleanly
  the resolution vanishes. The feature may or may not exist; the *original recorded
  measurement* was unreliable.

**Anchor cases (established 2026-04-17):**
- **F012 H85:** Claimed |z|=6.15 for Möbius bias at g2c aut groups.
  Clean n=66158 measurement: max|z|=0.39 (μ), 0.52 (λ), p≈0.6-0.7 under both.
  The 6.15 did not reproduce under either scorer definition. Kill confirmed.
- **F014 Lehmer gap:** Claimed 4.4% gap between bound and next Mahler measure.
  Clean n=81007: observed 3.41% with 3 polynomials inside claimed gap (Salem at 1.216).
  The specific gap-width claim was wrong.
- **F011 14% deficit:** Claimed 14% first-gap GUE deficit. Clean n=2M: 38% deficit.
  Magnitude corrected, not killed — weaker form of the pattern.
- **F010 NF backbone ρ=0.40:** Claimed ρ=0.40 z=3.64 at n=114 shared Galois labels.
  Clean re-measurement at per_degree=5000 (n=75): ρ=0.109 z=0.88. The pooled ρ
  did not reproduce at larger sample; durable signal is decontaminated ρ=0.27
  (borderline z=2.38). Magnitude corrected + tier preserved as borderline
  live_specimen. Also a Pattern 20 anchor case (pooled-vs-decon divergence
  widened with sample size).

**Diagnostic for suspecting Pattern 19:**
- The original n was small (< 100K) and the new n is large (> 100K)
- The original measurement preprocessing is undocumented or was different
- The original scorer might have been a different function than current standard
- The feature's description in the tensor uses phrases like "Needs permutation audit" —
  i.e., the provenance is admitted-as-weak

**Discipline:**
1. Every live_specimen tensor entry must have a **provenance block** documenting:
   what scorer, what n, what preprocessing, what subset. Entries without provenance
   should be marked `tier=unverified` pending a Pattern 19 audit.
2. When a clean large-n re-measurement disagrees with the original by more than
   3x, don't just update the number — investigate *why*. The difference is
   informative (different subset? different scorer? different preprocessing?).
3. A Pattern 19 kill should NOT trigger demoralization — it IS the instrument
   working. Better-than-nothing data, corrected.

**Connection to Pattern 17 (language/organization bottleneck):** Pattern 19 is
Pattern 17 manifest as data hygiene. Entries without provenance are a form of
under-organization; entries with provenance but stale measurement are a form of
under-maintenance. Both cost the same remediation effort: re-measure, document,
decide (kill / update / investigate).

**Anti-pattern:** Treating a Pattern 19 kill as if it invalidates Pattern 13
or the charter. It doesn't. Pattern 19 cleans a specific entry; the methodology
producing future entries is (by Pattern 19's operation) becoming more rigorous.

---

## Pattern 18 — Uniform Visibility is Axis-Class Orphan

**Proposed by:** Harmonia_M2_sessionB (INFO post 1776422033526-0), from observing
that sessionC's wsw_F011 showed +1 across ALL 7 tested projections.
**Confirmed by:** Harmonia_M2_sessionA. Status: drafted, awaiting first second-case
confirmation before full acceptance.

**Recognition:** When a feature shows +1 (visibility/resolution) across ALL
projections in a Weak Signal Walk, the resolving axis is OUTSIDE the tested set.
This is the positive-side complement to Pattern 13 (Direction of Accumulated Kills).

- Pattern 13 (negative side): accumulating kills along one axis class → redirect
  away from that class.
- Pattern 18 (positive side): uniform resolution across a walk → the feature is
  real AND the walked axes are all "not-the-resolving-axis" — you've confirmed a
  shape but not its natural coordinate.

**Canonical example:** F011 GUE first-gap deficit.
- sessionC's wsw_F011 applied P050, P051, P021, P023, P024, P025, P026
- Every projection returned +1 (deficit visible through each)
- Conclusion: the deficit IS real (not a coordinate artifact — it survives
  multiple independent views). But the resolving axis (the one along which the
  deficit is explained, not just visible) is among P028 (Katz-Sarnak),
  H09 (finite-N conductor-window), or something uncatalogued.

**Resolution (2026-04-17, tick 9):** sessionB's wsw_F011_katz_sarnak CONFIRMED
Pattern 18's prediction. Applied P028: SO_even 42.39% deficit (n=995K),
SO_odd 34.77% (n=1M), spread 7.63% (well above the 2.5% threshold). **P028 is
the first of 8 tested projections to discriminate on F011.** F011's resolving
axis class is symmetry-type (Katz-Sarnak). Pattern 18 worked: the navigation
pointed to the axis outside the initial tested set, and that axis resolved.
Pattern 18 is now a confirmed pattern with one positive-outcome case.

**Why this is not Pattern 13:**
- Pattern 13 says "multiple kills on the same axis class → feature doesn't live there."
- Pattern 18 says "multiple resolutions across different axis classes → feature is
  real AND its coordinate is missing from your current catalog."

**Discipline:**
- When a WSW returns uniform +1, do NOT declare the feature "confirmed" and stop.
  Confirmed = yes. *Located* = no. The work of finding the resolving axis begins now.
- Prioritize expansion of the catalog (Investment Priority #1) before continuing
  to walk the feature. Walking more already-tried-or-similar axes won't help if
  the resolving axis isn't in the catalog yet.
- Use the uniform-visibility result to CHARACTERIZE the feature: how does the +1
  vary across projections? (E.g., sessionC's P021 showed a monotone trend with
  num_bad_primes — that's structure, not just +1. Uniform visibility doesn't mean
  the per-projection numbers are identical.)

**Connection to Pattern 17 (language/organization bottleneck):** Pattern 18 is
another voice arguing the catalog is the prerequisite. Without coordinate-system
breadth, we can't find axes we don't have names for.

**Open question:** Is there a three-projection threshold for Pattern 18 to apply?
A single-projection +1 is noise; 7 projections +1 is clear. Where's the break?
Propose empirical calibration: look at 20 live specimens, find the minimum
n-projections-resolving-consistently that correlates with "specimen remains a live
specimen after 6 months." That calibration gives Pattern 18 a firm activation
threshold.

---

## Pattern 13 — Direction of Accumulated Kills

**Produced by:** Harmonia_M2_sessionB (parallel instance, sync session of 2026-04-17)
**Derived from:** Observing H08 Faltings and H10 ADE both die cleanly against F011 (GUE 14%).

**Recognition:** Multiple independent kills along the same coordinate axis are a
*cumulative negative finding*. The feature is NOT resolved by that axis. This
is stronger than any single kill.

**Why it matters:** A single kill says "this coordinate didn't work." Two or
three kills along the same family-characterizing axis say "this *class* of
coordinate will not resolve the feature — stop probing here, switch axis class."

**Canonical example:** F011 GUE 14% deficit.
- H08 killed → Faltings height is not the resolving axis
- H10 killed → ADE reduction type is not the resolving axis
- Both are family-level object properties
- Therefore: the 14% deficit is NOT a property of the object family
- Therefore: redirect probing toward preprocessing (P051 unfolding) or finite-N
  structure (H09 conductor-window), NOT more family-characterizing axes

**Discipline:** When killing a hypothesis, record which *class* of coordinate
it probed (family-level / preprocessing / structure / stratification). When
three kills accumulate in one class, redirect. Don't keep drawing in the same
well.

**Protocol note:** This pattern emerged during the first cross-context sync
between session-end Harmonia and a parallel cold-start instance. It was not
in the static artifact. Two-way dialogue produced it. This is what the sync
protocol is for — the static compression transmits the frame; the dialogue
fills in the patterns that only become visible through shared reasoning.

---

## Pattern 15 — The Machinery is the Product

**Recognition:** When someone proves a hard theorem, the inventions they had
to make — new functors, new cohomology theories, new invariants, new scorers
— are the deeper object. The theorem is the receipt.

**Canonical example:** Wiles proving Fermat. The theorem fits on one line. The
proof invented modularity lifting, Galois cohomology methods, and Euler
systems. Most practitioners use the theorem. The machinery goes unread. The
machinery is where the landscape actually got measured.

**Internal canonical:** The Galois-label object-keyed scorer (P010) was
created to rescue the NF backbone after the distributional scorer collapsed
it to z=0. Under the old frame, the rescue was a "survived finding." Under
the charter, *the scorer itself was the finding*. It is a new coordinate
system. Every future specimen can now be viewed through it. That utility is
independent of whether any single NF-backbone measurement persists.

**Corollary:** Every time we build a new scorer, index, feature extractor,
stratification, or null model, we have added a coordinate system to the
instrument. Document it in the coordinate-system catalog immediately, with
what-it-resolves and what-it-collapses. If we don't, the scorer is an
artifact, not an instrument. Pattern 10 (Instrument Grows Faster Than
Findings) is the output of this discipline applied consistently.

**Discipline:**
- Before celebrating a finding that came out of a new probe, ask: is the
  probe the real result?
- When reading someone else's proof, read for the new invariants and
  functors, not the statement.
- When Ergon generates at scale and I rescue signal through a new scorer,
  the scorer goes into the catalog before the signal goes into the registry.

**Anti-discipline:** Treating a scorer as infrastructure rather than an
instrument. The Megethos axis (P003) confounded everything for a month
because nobody wrote "magnitude-sorted vectors give ρ=1.0 as an artifact"
into any document. Silence makes every instrument an artifact by default.

---

## Pattern 16 — Problems-Nobody-Asks are the Frontier

**Recognition:** The specimens that make an expert say *"huh, that's
strange"* rather than *"that's a conjecture"* are where the landscape is
most likely unmapped. No named problem, no shortcut request, just terrain
anomalies. Most of the landscape is in this category and most of our
attention is not.

**Why this works under the charter:** Famous problems have their terrain
heavily mapped already, even if unsolved. The shortcuts people seek are
well-known paths through well-known terrain. Obscure anomalies, by contrast,
sit in regions no one has bothered to catalog — because there was no
shortcut to chase, no prize to claim, no paper to write.

**Canonical specimens:**
- The 19 rank-5 elliptic curves at conductor 19M–289M (F033 / F030).
- The degree-12 field at Mahler measure 1.228, 4.4% above the Lehmer bound (F014).
- The |z|=6.15 Möbius bias at genus-2 aut groups (F012 / H85).
- Anything flagged INCONCLUSIVE that had the right texture but lacked z.

**Operational filter — what makes a Category-3 specimen:**
1. Data points where multiple fingerprint modalities disagree on the same
   object.
2. Very specific boundary objects (degree exactly 12, conductor in a narrow
   window, aut_grp is one specific group).
3. Near-misses in the literature — moves that didn't go through because the
   terrain was harder than expected.
4. Questions phrased as *"what is the shape of X?"* rather than *"what is
   the value of X?"*
5. Coverage cliffs (rank ≥ 4 in bsd_joined, only 1 of 2105 curves has
   lfunc data) — the frontier of measurement is a frontier of landscape.

**Discipline:**
- When a Category-3 candidate is noticed in passing, file it immediately —
  even if we can't probe it yet. Under-filing is the main failure mode.
- For each filed candidate, record: what caught the eye, which projections
  have already been applied, what remains untested.
- Don't demand a theorem statement to justify filing. Unasked problems
  don't have theorem statements. That's the signal.

**Anti-discipline:** Treating "this isn't famous" as "this isn't
interesting." That's backwards under the charter. Fame is a proxy for
"already mapped." Obscurity is a proxy for "unmapped." Obscurity is what we
want.

**Connection to Pattern 15:** Category-3 specimens often require inventing
a new projection to see them at all. That's not a complication — it's how
the instrument grows. New coordinate systems emerge from stubborn anomalies
more often than from open problems.

---

## Pattern 17 — Language and Organization is the Real Bottleneck

**Produced by:** Harmonia_M2_sessionA, from James asking "where should we invest?"
2026-04-17.

**Recognition:** Given all the data, compute, models, and research access we
have, the thing that limits our trajectory is NOT any of those. It is the
*language and organization* of what we already have. We have more coordinate
systems than we've documented, more results than we've indexed, more projections
than we've named. The instrument is ahead of our ability to describe what it's
measuring.

**Symptoms of this bottleneck:**
- Two sessions using the same scorer give different reports because there's no
  shared vocabulary for what the scorer does
- Results scattered across JSON files with no way to query "which features are
  invariant across all 6 fingerprint modalities?"
- New scorers built as one-offs, never documented, producing artifacts nobody
  can interpret later
- Battery tests treated as truth-verdicts instead of coordinate-system probes
  (Pattern 6 was already this insight)
- Language drift: "cross-domain" and "bridge" resurface in drafts because the
  replacement vocabulary isn't reflexive yet

**The investment asymmetry:** One hour documenting a scorer saves ten hours
of re-deriving what it does. One hour building a registry schema saves
twenty hours of hand-curating JSON. One hour establishing shared language
saves dozens of hours of miscoordination across instances.

**Discipline:**
1. Every new scorer gets an entry in the coordinate system catalog. If it
   doesn't, it's not a real instrument — it's a noise generator.
2. Every specimen records its projection, feature type, invariance profile,
   and tautology check. Not "survived/killed." (Pattern 14.)
3. Use the replacement vocabulary consistently. Projection, feature, invariance,
   collapse. The old words are gravity — they pull the old frame back.
4. Before starting any new scorer or test, ask: *where does this fit in the
   existing catalog?* If nowhere, the catalog has a gap — document it first,
   scorer second.

**The ambition behind this pattern:** The product isn't discoveries. It's a
map — (feature × projection × invariance). When that map is dense enough,
anomalies stand out against it automatically, and we stop needing hypotheses
as probes. The map itself tells us where to look next. That's where we're
building toward.

**Connection to Pattern 10 (Instrument Grows Faster Than Findings):** That
pattern says "the instrument IS the product." This pattern specifies the
*form* the instrument takes: a well-organized catalog of coordinate systems,
features, and invariance relationships. The instrument is a map, organized.

**Anti-pattern:** "Let's just run more hypotheses and see what survives."
That's the old frame. Under this pattern: if you don't have a coordinate plan
(projection + expected feature type + tautology check) before the test,
don't run it. The catalog is the prerequisite.

---

## Pattern 12 — Who the Other Agents Are

(Not a pattern about math, but about the operational landscape.)

- **Aporia**: frontier scout, problem triage. Generates probe designs at scale.
  Her hypotheses are coordinate-choice suggestions, not claims about reality.
- **Kairos**: adversarial analyst. His challenges are probes through alternative
  coordinate systems. Desired: when he kills one of my findings.
- **Mnemosyne**: DBA. Her forensic work (zeros corruption audit, Lhash index,
  bsd_joined view) is part of the instrument. Data quality = measurement quality.
- **Ergon**: scale executor. Raw material. I sort; he generates.
- **Charon**: predecessor. Read his journals for continuity. The discipline he
  built (falsification-first, battery-calibrated, narrative-averse) is the
  foundation.
- **Koios**: tensor inventory. Coordinates the coordinate systems at the
  infrastructure level (indexes, views, data layout).
- **Council of Titans**: frontier models. Enumerate coordinate systems from
  literature faster than we can manually.

---

## Pattern 21 — Null-Model Selection Matters As Much As Projection Selection

**Proposed by:** Harmonia_M2_sessionA (conductor) 2026-04-17 after F010 kill.
**Anchor pair (calibration):** F010 killed + F011/F013/F015 survived under
block-shuffle; four specimens run through the same protocol returning
different verdicts.
**Status:** FULL PATTERN.

**Recognition:** The same data can produce z=+∞ under one null and z=0
under another. A "permutation null" is not a single thing — it's a
family of nulls parameterized by which stratum structure is preserved.
Choice of stratum preservation is a coordinate-system choice, and
projection discipline applies to it.

**Canonical example (F010 trajectory, 2026-04-17):**
- Plain label-permute null on NF↔Artin decontaminated ρ (n=51): z=2.38 (borderline-real)
- Block-shuffle-within-degree null on same data: z=-0.86 (firmly null — below the mean)

The plain null over-rejected because it destroyed the per-degree marginal
distribution. The "signal" was just "low-degree NFs pair with low-dimensional
Artin reps" — a trivial between-stratum coincidence. Block-shuffle preserves
that marginal and asks the sharper question: *within a degree, is there a
coupling?* The answer was no.

**Canonical example (F011 survival):**
- Plain permute on Katz-Sarnak spread (n=2M): z=7.63
- Block-shuffle-within-conductor-decile: z_block=111.78

Plain null did NOT over-reject here. Block-shuffle confirmed. Both nulls
agree on real signals; they disagree on marginal artifacts.

**Distinction from Pattern 20:**
- Pattern 20 is about the pooled statistic being a projection (stratify/
  preprocess to expose). Pattern 21 is about the NULL being a projection
  too — which marginal does it preserve? Both patterns are the same move
  (treat the measurement instrument as a coordinate system) applied to
  different steps of the pipeline.
- A Pattern-20-clean finding can still be Pattern-21-suspect. F010's
  decontaminated ρ=0.27 passed the Pattern-20 checks (it was the
  decontaminated value, not pooled) but failed Pattern 21 (plain null
  didn't preserve the degree marginal).

**Diagnostic:**
Ask one question: *if this signal were NOT a real within-stratum coupling
but a stratum-marginal coincidence, what stratum would be responsible?*
If you can name one, block-shuffle within that stratum before claiming.

**Discipline:**
1. Every live_specimen promotion path runs `block_shuffle_protocol`
   (see `harmonia/memory/protocols/block_shuffle.md`) before tensor entry.
2. Report both plain-null z AND block-null z when available. The gap
   IS the Pattern 20 × 21 composition diagnostic.
3. If plain and block disagree by > 3 sigma, the plain null over-rejected.
   If they agree, plain was fine — but the audit is still cheap insurance.

**Connection to Pattern 6 (Verdicts Are Coordinate Systems):**
Pattern 21 is Pattern 6 applied to the null-model step of the measurement.
The null is itself a projection through a coordinate system (which
marginal to preserve). Every measurement step has a projection built in.

**Connection to Pattern 17 (Language/Organization Bottleneck):**
The instrument needs first-class schema for `null_specification`:
{`type: plain|block`, `stratum: <column>`, `n_perms`, `seed`}. Currently
lives in free-text `machinery_required`. Room for Pattern 17 discipline.

**Anti-pattern:** Reasoning that "n is large enough that the null
doesn't matter." It does. sessionB argued F011's per-rank n=773K made
block-shuffle unnecessary; protocol ran anyway and confirmed. Never
reason the audit away. Always run it.

---

*End of pattern library.*

*These patterns are the felt-sense made explicit. They are not axioms; they
are default readings to apply until falsified. Expect some to be wrong. The
first time one leads you astray, document the correction here, and the
instrument gets sharper.*

*Harmonia, 2026-04-17*

---

## DRAFT Patterns 23–29 (proposed, not yet promoted)

Promotion criterion: Patterns 20 and 21 required 4 and 2 anchor cases
respectively before promotion. Draft patterns below have 1 anchor or
methodology motivation only. Promote when ≥3 independent anchor cases
accumulate. Until then: useful checklist, not doctrine.

**Pattern 23 — Parallel Followup Paths Produce Emergent Findings** (sessionB a87ea026, recursion)
When one finding (F011 rank-0 residual) is investigated along four parallel followup paths
by multiple workers, the aggregate produces findings none of the individual paths could have
surfaced alone (U_C sub-family + U_D mechanism + U_E pure-RMT divergence). Draft rationale:
emergence via recombination. Anchors: F011 investigation (1).

**Pattern 24 — Apply Own Instruments to Own Findings** (sessionB a87ea026, self-audit)
Before declaring durability, run the findings own methodology against itself. F011's rank-0
residual survived a block-shuffle self-audit — AFTER the degenerate-stratification error was
caught. Draft rationale: recursive falsification. Anchors: F011 self-audit (1, with
corrections).

**Pattern 25 — Pin Alpha From Theory Before Reporting eps_0** (sessionB 71ff1d47 thread b)
Joint α-free fit (eps_0 + C/log(N)^α) is UNDER-CONSTRAINED. α=0.49±0.52 gives eps_0=-4.07±56.
The point estimate for the residual depends on fixing the decay form. Draft rationale: never
report a point estimate from a two-parameter fit where both are poorly constrained. Anchors:
F011 rank-0 ansatz comparison (1).

**Pattern 26 — Confound Selection for Block-Shuffle Is a Discipline** (sessionB 71ff1d47 thread c)
Stratum choice for block-shuffle matters. class_size was DEGENERATE (null_std=0, one value
covers 59%) — produced spurious z=168757 on F011. torsion_bin (Mazur 15 balanced) gives
honest z=4.19. Prefer 5–20 balanced strata; reject any stratum where null_std < some threshold.
Draft rationale: Pattern 21 needs an input-validity check. Anchors: F011 self-audit correction (1).

**Pattern 28 — Literature-Buffer Every Finding Before Novelty or Calibration Claim** (sessionB ef034bfe)
Three of seven F011 followup findings were resolved OR sharpened by one Claude Opus
literature call against L-function RMT papers. Buffering is cheap (~5K tokens), amortizable,
surfaces cross-finding connections that per-finding audit misses. Draft rationale: cost-scaling
favors batched literature audit. Anchors: F011 7-finding batch (1), sessionD R18 cascade (1).

**Pattern 29 — Batch Findings Before Auditing** (sessionB 7e2df22c)
Batch size 5–10 findings before running literature / formula audits. Below 3, per-finding
is faster; above 10, subdivide by topic cluster. Cross-finding threads emerge at batch-scale.
Draft rationale: operational heuristic. Anchors: F011 7-batch (1), R18 13-batch (1).

**Why these stay DRAFT:** Patterns 20 (pooled-is-artifact) and 21 (null-selection-matters)
each required 4 and 2 INDEPENDENT anchor cases respectively — anchors that were different
specimens showing the same shape. Patterns 23–29 are mostly F011-investigation artifacts. One
anchor per pattern isn't enough to generalize. When 3+ DIFFERENT specimens show the shape,
promote. Until then, use as advisory.

**Audit schedule:** re-evaluate DRAFT pattern promotion when the next 3 specimens are
investigated — if any of 23–29 fire again on a specimen not named F011, note it here.

---

## Pattern 30 — Algebraic-Identity Coupling Detection (DRAFT, promoted to strong advisory 2026-04-19)

**Recognition:** Before running a correlation (or any statistical dependence test) on two
quantities `X` and `Y`, check whether one is algebraically defined in terms of the other,
either directly or via a rearrangement of a proved identity. If yes, the observed
"correlation" is a rearrangement of the identity, not evidence of arithmetic structure.
Permutation nulls do NOT break this coupling because they preserve the algebraic relationship
between the variables — they shuffle pairings, not definitions.

**Anchor case (F043, retracted 2026-04-19):**
- Claimed finding: `corr(log Sha, log A) = -0.4343` at `z_block = -348` on rank-0 EC, where
  `A := Omega_real * prod_p c_p`.
- What the reviewer spotted: BSD identity rearranges to `log A = log L + 2 log tors - log Sha`,
  so `-log Sha` is a term inside `log A` by definition. The negative correlation is algebraically
  induced.
- Block-shuffle null within conductor decile did not break it because the null preserves the
  definitional dependence. `z_block = -348` detects the BSD identity expressed in rearranged
  variables. Retracted as evidence.
- Restricting to `Sha = 1` curves made it WORSE, not better — collapsing variance in one
  term amplifies the remaining coupling through the algebra.

**Diagnostic checklist (before any correlation test):**
1. Write `Y` in terms of observable atomic quantities. Does `X` (or a log-transform of `X`)
   appear as a term or factor in that expression?
2. If yes: is the coefficient of that term non-zero?
3. If yes: the correlation is an algebraic rearrangement, not structural evidence. Skip
   the permutation-null step; it is not a meaningful test.
4. If no algebraic coupling, the permutation test is valid in the usual sense.

**Graded severity levels** (upgraded 2026-04-19 after external review flagged the
binary CLEAN/PARTIAL/COUPLED classification as too coarse):

| Level | Name | Description | Evidence status | Example |
|---|---|---|---|---|
| 0 | CLEAN | Y and X mathematically independent under the measurement | correlation test valid | most specimen F-IDs |
| 1 | WEAK_ALGEBRAIC | X appears in a term/factor with small coefficient OR under a log-transform where other terms dominate | correlation partially algebraic; specific claims (sign-uniform, magnitude non-monotone, stratum-dependent) beyond the algebraic direction are real evidence | F015 szpiro = log\|Disc\| / log(N) has log(N) in denominator; direction-of-slope partially expected but shape not forced |
| 2 | SHARED_VARIABLE | X appears directly as factor or term in Y's definition, coefficient non-trivial | correlation test no longer valid; the variables are not independent; report the algebra, not the correlation | hypothetical: corr(Sha, A·Sha) |
| 3 | REARRANGEMENT | Y is definitionally a rearrangement of X plus other known terms | correlation is a restatement of the defining identity; INVALID evidence | F043: A = L · tors² / Sha, so log A contains −log Sha |
| 4 | IDENTITY | Y = f(X) exactly (proved algebraic identity) | correlation tests identity verification, not arithmetic structure; belongs in calibration-anchor tier only | F003 BSD parity (−1)^rank = root_number; F008 Scholz reflection |

Correlation tests are evidence of arithmetic structure **only at Level 0**. Level 1 findings
are still reportable but must explicitly claim something beyond the direction the algebra
forces (e.g., stratum-dependence, magnitude non-monotonicity, sign-uniformity-at-scale).
Level 2 and 3 findings should be retracted or restated as algebraic observations. Level 4
belongs in the calibration anchor tier where identity verification is the point.

**Discipline:**
- Every F-ID involving a correlation or regression among BSD factors, Euler-product factors,
  or L-value rearrangements must include a "definitional-dependence check" line in its
  description.
- Permutation nulls address whether PAIRINGS are informative. They do not address whether
  DEFINITIONS induce coupling. Those are orthogonal checks.

**Distinction from Pattern 1 (Distribution/Identity Trap):** Pattern 1 warned about two
quantities sharing a formula at high correlation. Pattern 30 is the generalization — the
shared structure may be a log-transformed algebraic rearrangement that looks novel at
first. Pattern 1 is about high correlation; Pattern 30 is about ANY correlation on
algebraically-coupled variables being a rearrangement, regardless of magnitude.

**Promotion criterion:** F043 is the first anchor case. This pattern stays DRAFT until a
second, unrelated specimen is caught by the same check. Given how easy it is to construct
algebraically-coupled statistics on BSD or Euler-product data, we expect more anchors soon.

**Status elevation:** despite having only one anchor, the severity and obviousness of the
F043 failure mode argues for treating Pattern 30 as a strong advisory rather than a
tentative draft — i.e., it is already enforced discipline for new correlation-based work,
even if not formally promoted.

**Taxonomy extension 2026-04-20 (4-type LINEAGE_REGISTRY):** Pattern 30 is the right
gate for correlation-based findings, but the pre-2026-04-20 registry was single-shape
(`CouplingCheck` for `algebraic_lineage` only) and therefore degraded every non-
correlational F-ID to `NO_LINEAGE_METADATA`. The registry now dispatches on four types:

| Type | Applies when | Verdict emitted | Example F-IDs |
|---|---|---|---|
| `algebraic_lineage` | correlation with algebraic coupling to audit | CLEAR / WARN / BLOCK (per level 0-4) | F013, F015, F041a, F043, F045 |
| `frame_hazard` | construction-biased sample; Pattern 4 is the real gate | **PROVISIONAL** (does not halt; sync-posts `PATTERN_4_PROVISIONAL` with Class-4 null spec + re-audit task id) | F044 (+ F033 later) |
| `killed_no_correlation` | killed specimen; no correlation content to audit | **N/A_KILLED** (silent CLEAR-equivalent) | F010, F012, F020–F028 |
| `non_correlational` | variance deficit / existence / density / calibration | **N/A_NON_CORRELATIONAL** (silent CLEAR-equivalent) | F001–F005, F008, F009, F011, F014 |

Each entry may declare `pending_audit = {task_id, on_complete}`; the retrospective
runner re-reads this on every invocation and annotates whether the referenced
task has completed on Agora (lazy watcher — no cron, no triggered callback).
Re-classification still requires an explicit registry edit; the watcher surfaces
the staleness, it does not resolve it.

**Composite verdict precedence** (runner-side): `BLOCK > PROVISIONAL > WARN > CLEAR`.
PROVISIONAL is above WARN because the sampling-frame concern is stronger than a
log-denominator coupling, but it does NOT halt ingestion — that distinction is
the whole point of introducing the separate verdict rather than collapsing to BLOCK.

---

## Pattern 31 — Orbit Discipline (DRAFT, 2026-04-23)

**Produced by:** Harmonia_M2_sessionA, 2026-04-23, following the tensor-
identity-search pilot and the promotion of `canonicalizer.md` to substrate
primitive.
**Status:** DRAFT (2 anchor cases). Promotes to FULL when a third independent
anchor accumulates.

**Recognition:** claims of identity, novelty, or equivalence on structured
mathematical objects must be made *modulo a declared symmetry group*. A
silent identity claim on a raw representation — "these two objects are the
same" / "this is a new decomposition" / "this finding is not in the catalog"
— is always implicitly modulo *some* equivalence. If that equivalence is not
declared, the claim is not falsifiable and downstream consumers will
disagree silently. The decomposition-level instance of Pattern 1
(Distribution/Identity Trap) and the cross-cutting generalization of
Pattern 30 (Algebraic-Identity Coupling).

**Anchor cases (2):**

1. **F043 retraction (2026-04-19).** A claimed correlation
   `corr(log Sha, log A)` was measured on BSD-ingredient variables that
   are definitionally coupled through the BSD identity. The "finding"
   was a rearrangement of the identity, not evidence of arithmetic
   structure. Orbit discipline would have required declaring the
   algebraic-equivalence group (the BSD identity's ring of rearrangements)
   and checking the correlation is modulo it — which is exactly what
   Pattern 30 graded severity operationalizes for the correlational case.

2. **2026-04-23 2×2 matmul pilot.** Four ALS-converged rank-7
   decompositions of the 2×2 matmul tensor, understood by theorem to lie
   in a single `(GL(2)³ × S_7 × scale-gauge)`-orbit, hashed to four
   distinct canonical forms under a naïve (scale + sign + permutation)
   canonicalizer. Strassen's integer representative hashed to a fifth,
   distinct form. A downstream consumer counting distinct hashes as
   distinct orbits would see 5 orbits where 1 exists. Evidence in
   `harmonia/memory/architecture/orbit_vs_representative.md` +
   `harmonia/tmp/canonicalize_test.py`.

**Discipline:**

1. **Declare the symmetry group before claiming novelty.** Any novelty
   claim on a structured object must name the group under which the
   novelty is asserted. "This is new" without a group is a silent
   identity claim, not a falsifiable one.
2. **Use a canonicalizer instance that realizes at least the relevant
   subgroup.** `canonicalizer.md` registry maintains typed instances
   (Type A = canonical identity, Type B = preferred representative).
   Identity claims consume Type A; display claims consume Type B.
   The instance's `declared_limitations` field is where gaps in the
   quotient are declared honestly.
3. **Un-declared group action is a declared limitation, not a silent
   gap.** An instance that does not quotient part of the object's
   symmetry group must say so in `declared_limitations`. Consumers
   then know not to treat hash inequality as object non-equivalence.
4. **Canonical inequality NEVER implies non-equivalence.** Under
   partial quotienting, two inputs may be equivalent under the full
   symmetry group but hash differently. This is the asymmetry warning
   in the canonicalizer contract and the most common silent-misuse
   failure mode.

**Distinction from Pattern 30:** Pattern 30 operationalizes orbit
discipline for the specific case of algebraic-identity coupling in
correlational claims. Pattern 31 is the substrate-level generalization —
it covers correlational claims (Pattern 30's domain) plus tensor-
decomposition identity, DAG node identity, MAP-Elites archive dedup,
coordinate-axis novelty (gen_11), and any future structured-object
identity claim. Pattern 30 stays as the correlational-specific instance;
Pattern 31 is the cross-cutting frame.

**Distinction from Pattern 1:** Pattern 1 names the phenomenon (high
correlation between algebraically-coupled variables looks like structure
but isn't). Pattern 31 names the *discipline* required to catch the
phenomenon at scale: declare the group, use a canonicalizer, respect
the asymmetry warning.

**Connection to canonicalizer primitive:** Pattern 31 is the discipline
pattern; `harmonia/memory/architecture/canonicalizer.md` is the
mechanism. The pattern fires when a claim is made without an explicit
equivalence group; the canonicalizer is the tool that remediates it.
They are load-bearing together; neither suffices alone.

**Promotion criterion:** DRAFT until a third independent anchor case
accumulates. Candidate third anchors that are visible now but not yet
realized:
- A `CANONICALIZER:dag_node_identity@v1` (when it ships) will produce
  its own anchor: a derived quantity re-expressed in a different
  basis hashing the same node ID.
- A `CANONICALIZER:pattern_30_rearrangement@v1` (when it ships) will
  produce an algebraic-expression anchor: two expressions related by
  a ring identity hashing the same.

**Anti-pattern:** Counting novel hashes as novel findings without
declaring the equivalence group they're canonical under. This is the
AlphaTensor failure mode (orbit-variant "new" decompositions counted
as distinct from known ones) generalized to substrate scale.
