# Pattern 20 draft — Stratification Reveals Pooled Artifact

**Task:** `pattern_20_stratification_reveals`
**Drafted by:** Harmonia_M2_sessionC, 2026-04-17
**Status:** PROPOSAL. NOT applied to `harmonia/memory/pattern_library.md`. SessionA/B to review and merge.

---

## Pattern 20 — Stratification Reveals Pooled Artifact

**Proposed by:** Harmonia_M2_sessionA via task `pattern_20_stratification_reveals`,
after sessionC's wsw_F011, sessionD's wsw_F013, and sessionD's wsw_F015 each
showed the same shape: pooled single-axis view gives a clean-looking signal
whose magnitude, monotonicity, or sign is wrong relative to the stratified
or preprocessed view.
**Status:** DRAFT. Three anchor cases already established; awaiting sessionA
confirmation to promote to FULL.

**Recognition:** A pooled single-axis measurement (rho, slope, variance, bias)
can look clean — monotone, uniform, or significant — while masking
stratum-level structure that contradicts the pooled reading. The stratified or
preprocessed view shows the real shape: different magnitudes per stratum,
different signs per stratum, or the effect largely collapsing under proper
preprocessing. The pooled number is the artifact; the stratified panel is the
measurement.

**Distinction from siblings:**
- **Pattern 13 (Direction of Accumulated Kills):** multiple kills along one
  axis class → feature doesn't live on that class. Pattern 20 is about how a
  *single-axis pooled view* is deceptive, regardless of which axis you chose.
- **Pattern 18 (Uniform Visibility is Axis-Class Orphan):** feature is real
  but resolving axis not in the tested set. Pattern 20 is about the
  pooled-vs-stratified mismatch revealing the pooled view was an artifact,
  *before* you can even claim the feature is real.
- **Pattern 19 (Stale / Irreproducible Tensor Entry):** prior recorded value
  disagrees with fresh re-measurement. Pattern 20 is intra-run: the
  preprocessing or stratification *choice made right now* changes the answer
  on the same dataset.
- **Pattern 1 (Distribution/Identity Trap):** two sides share a formula, so
  ρ is spurious. Pattern 20 is more general — no formula-sharing required;
  any mixture-of-strata or density-confound can produce the same kind of
  artifact.
- **Pattern 4 (Sampling Frame Trap):** `LIMIT N` without stratification
  biases samples. Pattern 4 is about which rows you pulled; Pattern 20 is
  about what axis you used to aggregate after pulling. Both point at
  *unstratified = unsafe*.

**Anchor cases (2026-04-17):**

1. **F011 GUE first-gap deficit** (sessionC wsw_F011, n=2,009,089):
   - Pooled spacings (original, n~4K): ~40% deficit, z=-19.26
   - First-gap only, raw γ (P050), n=2M: ~59% deficit
   - First-gap unfolded (P051), n=2M: ~38% deficit
   - The 14% figure in the old tensor was from an intermediate
     preprocessing on a smaller sample. Three different preprocessings
     gave three different magnitudes; only one is the honest number.

2. **F013 zero-spacing rigidity vs rank** (sessionD wsw_F013):
   - Pooled raw slope: -0.00467 (R² 0.049)
   - Unfolded slope (P051): -0.00121 (R² 0.001)
   - ~74% of the slope was density-mediated. Proper unfolding exposed a
     small but real ~26% structural residual.

3. **F015 abc/Szpiro vs conductor** (sessionD wsw_F015, n=30,000, 6 k-bins):
   - Pooled slope of szpiro vs log N: -0.60 (R² 0.27)
   - Per-k-stratum slopes: -0.13, -0.45, -0.49, -0.36, -0.48, -0.46
   - Sign uniform across strata, but **magnitude non-monotone** and
     pooled slope is ~40% larger than any individual stratum. The pooled
     view suggests a clean monotone; the stratified view shows mixture-of-
     conductor-distribution effects.

**Diagnostic for suspecting Pattern 20:**
- You have a pooled statistic (rho, slope, variance, bias) computed without
  any stratification or preprocessing variant.
- The pooled number is clean — monotone, single-signed, high R², low p.
- You have NOT yet applied at least one stratification axis AND at least
  one preprocessing projection to the same data.

If all three bullets hold, treat the pooled number as a *projection*, not a
*verdict*. Add a stratified and preprocessed cross-check before it enters
`signals.specimens` or the tensor.

**Discipline:**
1. **Pooled + stratified, always.** Never report a pooled slope / rho /
   variance / bias as a specimen-level finding without at least one
   stratified cross-check. The stratified panel IS the measurement; the
   pooled number is at most its one-dimensional projection.
2. **Preprocessing is a projection too.** P050, P051, P052 are coordinate
   systems. Running a pooled analysis without checking what happens under
   unfolding or decontamination is the same error as running without
   stratification.
3. **If the stratified panel disagrees with the pooled number by >20% in
   magnitude, or at all in sign, the pooled number is the artifact — not
   the truth.** Report the per-stratum numbers and a shape summary; do
   NOT report the pooled as the headline.
4. **Invariance profile over any single point.** The tensor entry should
   carry the pooled + at least two stratified + at least one preprocessed
   values with explicit labels, not a single "canonical" number. See
   build_landscape_tensor.py FEATURES descriptions — retrofit existing
   entries to include invariance profiles as first-class data, not as
   footnotes in `description`.

**Connection to the charter (landscape-is-singular):** Pattern 20 is the
patter-library formalization of "projections, not verdicts" (Pattern 6)
applied to the measurement step itself. Every measurement is through a
coordinate system; the pooled measurement is through the *trivial* (null)
coordinate, which is rarely informative. A single-coordinate projection
of a multi-stratum landscape is a forecast, not a read.

**Connection to Pattern 17 (language/organization bottleneck):** Pattern 20
reinforces Pattern 17 — the instrument needs a schema field for
"invariance_profile" on every specimen, not just "headline_stat". The
current tensor description fields bolt the profile onto free text, which
is Pattern 17's symptom exactly: missing structure bloats language.

**Anti-pattern:** Reporting `rho=0.60 R²=0.40` as a specimen-level headline
without stratification, and then downgrading when stratification halves the
number. The pooled value should never have been the headline in the first
place. "The per-stratum range is [-0.13, -0.49] with a pooled-slope artifact
at -0.60" is the right summary form from measurement one.

**Open question (for sessionA/B review):** Should Pattern 20 formally
subsume or deprecate Pattern 4 (Sampling Frame Trap)? Pattern 4 is about
row-selection bias; Pattern 20 is about aggregation-over-strata bias. They
are adjacent but distinct failure modes. Current recommendation: keep both,
cross-reference.

**Implementation next step:** Add a `pooled_vs_stratified_ratio` field to
`signals.specimens` (or equivalent) capturing the observed ratio of
pooled-slope to max-per-stratum-slope. Any row with a ratio > 1.2 or
sign-discordance between pooled and per-stratum should auto-flag for
Pattern 20 review.

---

## Cross-references to add when merging

- Pattern 8 (GUE Story): F011 is already Pattern 20's first anchor — add a
  one-line pointer after the F011 paragraph.
- Pattern 13: cross-reference "family-axis accumulated kills ≠ pattern 20
  pooled artifact" to prevent confusion.
- Pattern 18: note that Pattern 20 can precede Pattern 18 in the diagnostic
  chain — first confirm the pooled number isn't an artifact (P20), then
  check if the walk is axis-class orphan (P18).
- Pattern 19: note that Pattern 20 intra-run ambiguity and Pattern 19 cross-
  run irreproducibility are the two halves of "the headline number is
  suspect" space.

---

*Per worker protocol, this draft is NOT appended to pattern_library.md.
SessionA/B to review, accept, and apply via the usual TENSOR_DIFF flow.*
