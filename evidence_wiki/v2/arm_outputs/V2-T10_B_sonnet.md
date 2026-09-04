# PROPOSAL V2-T10 (arm B)

## Hypothesis

A cross-domain "bridge-candidate" ranking built by scoring pairwise similarity of
per-object feature vectors across the four catalogs (hyperbolic knots, number fields,
elliptic curves, zero/spectral statistics) will, once passed through a density-matched
permutation null and a native-vocabulary complement, either (a) surface at least one
object-level correspondence that is not already recorded in the source databases and that
survives direct algebraic/numerical reconstruction, or (b) cleanly demonstrate that the
ranking signal is generic **feature-geometry** artifact (population density, scale,
formatting) rather than object-level coupling. Both outcomes are informative; the prior
runs of this program found (b) every time a formal null was applied. This revival treats
that as the base rate to beat, not a warm-up finding.

## Motivating evidence

The 2026-Q2 cross-domain coupling-tensor program (Aporia/Ergon/Harmonia, April-August
2026) built the direct predecessor of this idea and killed every concrete instantiation it
tried:

- The coupling tensor over NF/Artin/EC/MF/knots measured **feature geometry, not
  object-level coupling**, confirmed across all three scorers (C-8f20c74fa0cf).
- Re-encoding knots with the mathematically correct features (Mahler measure,
  root-of-unity evaluations) produced **no coupling signal** — feature correctness alone
  does not manufacture a bridge (C-1938a4759fd8).
- The one concrete bridge hypothesis in this space that was actually executed —
  McMullen's K3 Salem-field-to-knot-trace-field bridge — was killed by direct
  reverse-substitution: 245,280 evaluations, 0 hits at 10^-40 tolerance (C-534275646eeb).
- The NF "backbone" bond structure was killed by a permutation null: z = 0.0, proving the
  structure was distributional, not object-level (C-1f1a743fce1b).
- The tensor's own latent-rank claims (effective dim ≤5, SVT rank 12-16) were retracted:
  the SVT method's assumptions are violated by the sparse ordinal MNAR tensor, and ~52% of
  any rank-flavored signal is attributable to row/column density marginals alone
  (C-e0b3b4966385) — i.e. the instrument manufactures structure from population imbalance.
- Separately, on a different substrate: **generic** operators found zero relations over
  294,909,843 reachable elliptic-curve triples, while **one native verb** (quadratic
  twist) found 4,476 — but after class-level dedup, 100% of the sampled relations were
  already LMFDB-recorded, so none were discoveries (C-96a0e90f4eeb, C-a3744a88ea5e). A
  narrower binary-verb test (add/sub; hadamard structurally excluded) found H=0 over
  323,229,712 attainable triples, qualifying the positive result as vocabulary-specific,
  not a general native-operator win (C-6db5a537c0a5, retrieved as counterevidence to
  C-96a0e90f4eeb).
- A ranking-gain precedent directly on point for validation method: a state-conditioned
  ranking gain of D=+0.24395 at 70x its own SE was declared **VACUOUS** because the
  shuffled-label null scored 0.5903 against chance 0.5029 — the null failed to perturb the
  axis the statistic varies on, so the raw significance was disqualified outright
  (C-750f2b6fc3ac). This is the direct template for this proposal's mandatory null.
- Data-integrity caution: the elliptic-curve catalog's `object_id` column was NULL on
  1,984,167 of 2,009,089 rows from a desynced id sequence; `lmfdb_label` is the intact
  identity key, and the repair watermark is 134475 (C-948eae5cb70c). Any feature vector
  built off `object_id` today risks silently sampling the 24,922-row non-null subset.
- A stratification precedent: an abc/Szpiro decrease was first confounded by a
  prime-conductor selection effect at high N, then rescued by testing at fixed bad-prime
  count (C-4d867be1dc68) — the same conductor/discriminant-scale confound is expected to
  recur in any cross-catalog magnitude comparison.

`contradictions()` returned no item specific to this topic; the two live contradictions in
the wiki concern an unrelated Daedalus/Aporia substrate pair and a FAILS_TO_REPLICATE pair
with no rationale text, neither bearing on cross-catalog bridging. Repo search for the
2026-Q2 idea's literal origin also surfaced `apollo/cycles/type_bridge/` — read in full,
this is a *different* "bridge" (a genetic-programming blackboard data-flow op connecting
tiers of an evolutionary search substrate), not a catalog-similarity bridge; it did not
affect this design and is recorded as a false-lead in the operation log.

## Prospective predictions

1. A naive cosine/Euclidean similarity ranking over raw per-domain feature vectors
   (unnormalized, cross-domain z-scored only at the population level) will produce a
   top-K list dominated by scale/density artifacts — i.e. the top matches will cluster on
   whichever domain has the coarsest discretization or heaviest tail, mirroring the ~52%
   marginal-density attribution already measured on the predecessor tensor.
2. After density-marginal regression and a shuffled-label null, the surviving candidate
   count will be statistically indistinguishable from the null's false-discovery rate at
   the pre-registered top-K (i.e., most of the raw ranking's apparent structure will not
   survive) — consistent with every prior formal-null test in this program.
3. If any candidate survives the null, it will fail direct reconstruction (reverse
   substitution / exact algebraic check) at the McMullen precedent's tolerance (~10^-40 or
   domain-appropriate exactness), because similarity-in-feature-space has not previously
   implied object-level identity anywhere this program has checked.
4. A native-vocabulary complement arm (domain-native transforms, e.g. quadratic twist for
   EC, rather than generic feature coordinates) will outperform the generic similarity
   ranking on hit rate before dedup, replicating the native-verb-vs-generic-operator gap,
   but most native-verb hits will already be catalog-recorded (dedup rate near 100%),
   replicating C-96a0e90f4eeb.

## Experiment

**Catalogs and features** (four domains, held fixed for this cycle):
- Knots: hyperbolic knot trace fields / shape fields (12,963 roots at 3-13 crossings,
  per the McMullen precedent's census) — features: Mahler measure, root-of-unity
  evaluations, trace field discriminant, volume.
- Number fields: degree, discriminant, Galois group, Artin conductor, class number.
- Elliptic curves: conductor, rank, discriminant, j-invariant, trace-of-Frobenius
  sequence (first N primes) — keyed by `lmfdb_label`, never raw `object_id` (per
  C-948eae5cb70c; verify watermark 134475 before any bulk pull).
- Zeros: low-lying zero statistics / pair-correlation moments per L-function, keyed to
  the same conductor/discriminant scale as its source object.

**Pipeline:**
1. **Within-domain normalization first.** Rank-transform or z-score each feature within
   its own domain population before any cross-domain combination — never linearly combine
   heads trained on heterogeneous populations/scales (house rule; also the direct lesson
   of the density-marginal retraction).
2. **Stratify by conductor/discriminant decade** before computing any cross-domain
   similarity, to pre-empt the prime-conductor selection effect (C-4d867be1dc68).
3. Compute pairwise similarity (cosine, and separately a rank-correlation metric) within
   each conductor-matched stratum, cross-domain, using approximate nearest-neighbor
   indexing (not full brute force — see Compute estimate) to produce a top-K candidate
   list per domain pair (K pre-registered at 500 pairs/domain-pair before data is read).
4. **Density-marginal null:** regress out row/column marginal density (replicate the
   retracted-tensor diagnostic) and report the residual score; a candidate whose score
   drops below the null band after this step is marked ARTIFACT, not candidate.
5. **Shuffled-label null** on surviving candidates: relabel object identity within each
   domain (preserving within-domain feature marginals) B=10,000 times, recompute the
   top-K similarity statistic distribution, and report the empirical p-value AND the raw
   score against both chance and the null mean — modeled directly on the
   0.5903-vs-0.5029 disqualification precedent (never report the raw score alone).
6. **Native-vocabulary complement arm:** run one domain-native transform per catalog
   pair (e.g. quadratic twist family for EC, Dehn surgery family for knots) alongside the
   generic-feature arm, to separate "no bridge exists" from "the vocabulary is generic."
7. **Dedup against source databases** (LMFDB, etc.) for every surviving candidate before
   any discovery claim.
8. **Direct reconstruction** for every candidate surviving steps 4-7: exact
   algebraic/numerical verification (reverse substitution or equivalent), not a second
   similarity score.

## Controls

- **Density-marginal control:** row/column marginal-only null tensor (same
  method that attributed ~52% of the predecessor's rank signal to marginals alone).
- **Shuffled-label control:** B=10,000 within-domain relabelings, holding domain
  marginals fixed.
- **Uniform/random-pairing control:** candidates drawn uniformly across strata
  (ignoring conductor-matching) to isolate the effect of stratification itself.
- **Generic-vs-native control:** the same candidate space scored by (a) generic
  feature-vector similarity and (b) one domain-native operator, run on identical objects.
- **Instrument-verification control:** re-run the exact predecessor negative results
  (knot re-encoding null, McMullen reverse-substitution null) inside this pipeline as a
  positive-control-for-nullness check — if the pipeline reports a "hit" on a
  cell already established as H=0 / 0-hits, the pipeline is broken, not the hypothesis.

## Confound defenses

- **Object identity key:** verify `lmfdb_label` coverage and the `object_id` NULL
  watermark (134475) on the EC catalog before any feature pull; report row counts by
  identity-key validity.
- **Conductor/discriminant scale confound:** all cross-domain comparisons stratified by
  conductor/discriminant decade (per C-4d867be1dc68); no un-stratified comparison is
  reported as a discovery.
- **Prime-atmosphere confound:** given house evidence that 96%+ of cross-dataset
  structure across these catalogs traces to prime distribution, detrend against a
  prime-count/density covariate before computing similarity, and report the detrended and
  raw scores side by side.
- **MI/histogram bias:** if any mutual-information-style scorer is used alongside
  cosine similarity, it must be checked against a random-pairing null (sparse histograms
  bias MI upward) rather than reported raw.
- **Vocabulary confound:** never conclude "no bridge exists" from the generic-feature
  arm alone; the native-vocabulary complement arm is mandatory before any negative claim,
  per the native-verb-vs-generic-operator precedent.
- **No naive score combination:** the multi-domain composite score (if one is built) is
  never a linear combination of per-domain heads fit on different populations/scales;
  combination, if attempted, uses a rank-based or stratum-conditional method and is
  reported as a separate, clearly labeled analysis.

## Preregistered falsifiers (numeric thresholds)

A candidate bridge is **CANDIDATE_SUPPORTED** only if ALL of:
1. Density-marginal-regressed residual score retains ≥50% of the raw score's magnitude
   (i.e. the marginal null explains <50%, mirroring the ~52% retraction threshold as the
   line already shown to disqualify a result).
2. Shuffled-label null: empirical p < 0.001 (Holm-corrected across all top-K
   domain-pair candidates tested), AND the raw score exceeds the null's own mean by more
   than the null's standard deviation band used in the 0.5903-vs-0.5029 case is
   explicitly checked and reported — i.e. report both p-value and the null-vs-chance gap,
   and DISQUALIFY regardless of p-value if the null mean itself sits within 2 percentage
   points of chance on an unbounded-looking statistic (replicating the disqualification
   logic, not just its p-value).
3. Not already recorded in the source database under any known equivalence (exact dedup
   match rate must be 0/N for the candidate to be reportable as new; any nonzero dedup
   rate reclassifies the candidate as CONFIRMED_KNOWN, not discovery).
4. Direct reconstruction succeeds at domain-appropriate exactness (10^-40 numeric
   tolerance for the trace-field-style checks, replicating the McMullen precedent; exact
   symbolic match for algebraic identities).

**Falsified as VACUOUS** if any candidate meets (2)'s p-value but fails the null-gap
check in (2) — reported prominently, not filed silently, per house precedent.

**Program-level kill:** if, after testing all four domain-pair directions
(knot-NF, knot-EC, knot-zero, NF-EC, NF-zero, EC-zero) at the pre-registered K=500/pair,
zero candidates pass all four gates, the generic-feature-vector-similarity approach to
this bridging question is declared REFUTED for this catalog set and vocabulary, and the
native-vocabulary-only path (per C-96a0e90f4eeb) becomes the sole surviving track.

## Stopping rule

- Domain pairs, K=500 candidates/pair, and the B=10,000 null-resample count are fixed
  before any data is read; no post-hoc expansion of K or addition of domain pairs after
  seeing which candidates look promising.
- Multiplicity correction (Holm) is applied across the full pre-registered candidate set
  (6 domain-pairs x 500 = 3,000 candidates) before any single candidate is named a hit.
- The cycle stops at first full pass through all four gates on all six domain-pair
  directions; no re-running with adjusted thresholds after seeing the gate-1/gate-2
  pass rate. A second cycle, if run, is a new preregistration.
- Early stop permitted only in the negative direction: if the density-marginal control
  alone (step 4) already reduces the entire top-K list to below-null in every domain pair
  at the halfway point (3 of 6 pairs), the remaining 3 may be skipped and the whole cycle
  reported as REFUTED without running the shuffled-label null on them — this is a stop
  on futility, not a stop on a good result.

## Expected failure modes

1. **Feature-geometry recurrence (most likely, per C-8f20c74fa0cf and C-e0b3b4966385):**
   the ranking reproduces population density/scale structure and nothing survives the
   marginal-null gate. This is a clean, reportable negative, not an instrument failure.
2. **Null disqualification despite high raw significance** (per C-750f2b6fc3ac): a
   candidate clears p<0.001 by a wide margin but the null-vs-chance gap check fails —
   must be reported as VACUOUS, not as a discovery, however large the raw z-score.
3. **Dedup wipeout** (per C-96a0e90f4eeb): every candidate surviving the statistical
   gates turns out to already be catalog-recorded once cross-referenced against LMFDB —
   a statistically real but non-novel result.
4. **Object-identity corruption silently biasing the EC arm** (per C-948eae5cb70c) if
   the watermark/lmfdb_label check is skipped — would make any EC-side candidate
   unusable regardless of downstream gates.
5. **Conductor-confounded false positive** (per C-4d867be1dc68 pattern) if
   stratification is skipped or done at too coarse a decade resolution.
6. **Generic vocabulary blind spot:** the generic-feature arm reports REFUTED while a
   native-vocabulary transform (untested in this cycle for the remaining domain pairs)
   would have found something — this is why the native-vocabulary complement arm is
   mandatory and why the program-level kill in the falsifiers section is scoped to "for
   this vocabulary," not "no bridge exists."

## Compute estimate

- EC catalog: ~2,009,089 rows (900-curve subsets used in prior native-verb cycles ran
  ~294-323M reachable triples for binary/generic operators in hours-scale batch jobs; a
  pairwise all-vs-all similarity at full catalog scale is infeasible without indexing).
- Knot catalog: 12,963 hyperbolic knot shape-field roots (3-13 crossings), as used in the
  McMullen precedent (245,280 evaluations for a 5-polynomial x 12,963-root reverse
  substitution completed same-day on a single machine).
- Approximate nearest-neighbor indexing (e.g. FAISS/ball-tree on the normalized feature
  vectors) is required for any domain pair where both sides exceed ~10^4 objects;
  brute-force all-pairs at EC-scale (2M) x knot-scale (13K) = ~2.6x10^10 pairs is not
  attempted directly — indexing reduces the retrieval step to top-K per query, i.e.
  O(N log N) build + O(K) per query, estimated at single-machine hours, not days.
  If a domain pair still exceeds a 4-hour single-machine budget after indexing, that pair
  is stratum-subsampled (proportional to conductor-decade population) rather than
  silently dropped, and the subsampling is logged.
- Null resampling: B=10,000 shuffles x 6 domain pairs x top-500 candidates is the
  dominant cost after indexing; estimated at low-single-digit machine-hours total given
  the McMullen precedent's same-day 245K-evaluation runtime as a scale anchor.
- No GPU/LLM inference required; this is classical feature engineering + nearest-neighbor
  + permutation testing, within the existing local compute ceiling.

## Prior evidence that materially changed this design (or 'none found')

Materially changed (see next section for id-level mapping): the mandatory
density-marginal null, the mandatory shuffled-label null with an explicit null-vs-chance
gap check (not just p-value), the mandatory native-vocabulary complement arm, the
mandatory dedup-against-source-database step, the `lmfdb_label`-not-`object_id` identity
rule, and the conductor/discriminant stratification requirement were all added because of
specific prior kills in this exact program, not as generic best practice.

## Unresolved uncertainty

- Whether a domain-native transform exists for **all four** catalogs (a native op is
  documented for EC via quadratic twist; no equivalent native op is evidenced in the
  retrieved items for knots, NF, or zeros) — the native-vocabulary complement arm may
  therefore only be runnable on some domain pairs this cycle, leaving the "vocabulary vs.
  no-bridge" ambiguity only partially resolved for knot/NF/zero pairs.
  Non-EC domains are the residual uncertainty and are flagged, not silently defaulted to
  the generic arm.
- Whether the ~52% marginal-attribution figure (measured on the coupling-tensor's SVT
  rank claim, a different statistic) transfers as a threshold to a nearest-neighbor
  similarity ranking; it is used here as a precedent-consistent line, not a re-derived
  one, and should be recomputed on this pipeline's own null rather than assumed.
- The two items returned by `contradictions()` were both off-topic for this task (a
  Daedalus/Aporia substrate-ecology pair and an unattributed FAILS_TO_REPLICATE pair);
  this leaves open whether a topic-specific contradiction exists that the current
  contradiction index has not yet classified — worth a follow-up `contradictions()` call
  after this cycle's own findings are submitted.
- Zero/spectral-statistic catalog feature choice was not validated against any retrieved
  evidence item (no pack item or search hit addressed zero-statistics features
  specifically); the feature list in the Experiment section for that domain is a
  placeholder pending a dedicated evidence check before execution.

## Evidence Wiki consultation log (queries + object ids retrieved)

1. `search_evidence("cross-domain bridge feature vector similarity ranking validation", k=8)`
   -> C-01f913ae81af, C-8f20c74fa0cf, C-1938a4759fd8, C-534275646eeb, C-b037a49b641c,
   C-750f2b6fc3ac, C-94fc12c3e6af, C-e3c149ca4f7e
2. `get_counterevidence("C-96a0e90f4eeb")` [negative-evidence query]
   -> C-6db5a537c0a5 (QUALIFIES relation, binary-verb closure null H=0)
3. `contradictions()`
   -> R-e68c9331eca2 (C-3a1c49fa5a78 vs C-3d12c440f087, off-topic), R-2dc413ddca43
   (C-1d99d0adac44 vs C-7d559fe50c7a, off-topic)
4. `get_claim("C-6db5a537c0a5")` -> full claim/evidence record (binary native verbs,
   add/sub/hadamard, H=0 over 323,229,712 attainable triples, cycle 142-F KILL)

Additionally consulted the pre-built task pack `v2/packs/V2-T10_pack.json` (10 curated
items spanning C-8f20c74fa0cf, C-1938a4759fd8, C-534275646eeb, C-1f1a743fce1b,
C-e0b3b4966385, C-96a0e90f4eeb, C-a3744a88ea5e, C-750f2b6fc3ac, C-948eae5cb70c,
C-4d867be1dc68), which supplied most of the Motivating evidence section directly.

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)

- **C-8f20c74fa0cf** -> added the mandatory density-marginal-regression gate as the
  first filter before any candidate is called "candidate," not just "raw score."
- **C-1938a4759fd8** -> dropped "feature correctness" as a sufficient design criterion;
  the Experiment section does not treat improved features as a fix on its own, only as
  one input alongside the null gates.
- **C-534275646eeb** -> set the direct-reconstruction falsifier's numeric tolerance
  (10^-40) and made reverse-substitution-style verification a mandatory final gate
  rather than an optional check.
- **C-1f1a743fce1b** -> made the permutation/shuffled-label null on object identity a
  named, mandatory control (not left implicit).
- **C-e0b3b4966385** -> set the 50%-of-raw-score threshold in falsifier (1) and added
  the density-marginal control as a named, separate control from the shuffled-label null.
- **C-96a0e90f4eeb** + **C-6db5a537c0a5** -> added the native-vocabulary complement arm
  as mandatory (not optional), and scoped the program-level kill to "for this
  vocabulary" rather than "no bridge exists," because the native-verb result is itself
  vocabulary-specific (quadratic twist succeeded, add/sub/hadamard failed).
- **C-a3744a88ea5e** -> informed the compute estimate's brute-force infeasibility
  argument (294M reachable triples already required an engineered exhaustive scan;
  cross-catalog scale is larger still, hence the indexing requirement).
- **C-750f2b6fc3ac** -> the single most load-bearing item: added the explicit
  null-vs-chance gap check as a second, independent disqualifier alongside the p-value,
  and added the "VACUOUS despite high significance" category to both the falsifiers and
  expected-failure-modes sections.
- **C-948eae5cb70c** -> added the `lmfdb_label`-not-`object_id` identity rule and the
  watermark-134475 pre-check as a named confound defense.
- **C-4d867be1dc68** -> added mandatory conductor/discriminant-decade stratification
  before any cross-domain similarity computation, as a named confound defense.
- **Apollo `type_bridge` PREREGISTRATION.md** -> retrieved but did not affect design;
  it is a different "bridge" (evolutionary-search data-flow op), confirmed by full read,
  and excluded from all sections above.
- **contradictions() results (R-e68c9331eca2, R-2dc413ddca43)** -> retrieved but did not
  affect design; both are off-topic for cross-catalog bridging, noted in Unresolved
  uncertainty as a residual gap in the contradiction index rather than a design input.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Grep repo for `bridge` (case-insensitive, `*.md`) — file-list search, no document read.
2. Grep repo for `feature.vector.similarity|cross.domain bridge|bridges between` — file-list search, no document read.
3. Read `F:\Prometheus\evidence_wiki\v2\packs\V2-T10_pack.json` — document opened (1).
4. Bash: `ew.search_evidence("cross-domain bridge feature vector similarity ranking validation", k=8)` — wiki API call.
5. Bash: `ew.get_counterevidence("C-96a0e90f4eeb")` — wiki API call (negative-evidence query, satisfies required minimum).
6. Bash: `ew.contradictions()` — wiki API call (satisfies required minimum).
7. Bash: `ew.get_claim("C-6db5a537c0a5")` — wiki API call; document opened (2).
8. Read `F:\Prometheus\apollo\cycles\type_bridge\PREREGISTRATION.md` — document opened (3); confirmed off-topic, excluded from design.

**Ops used: 8 / 15. Documents opened: 3 / 12.** Early stop taken — the task pack plus the
three targeted wiki calls (search, counterevidence, contradictions) plus one disambiguating
repo read already covered every required consultation type and produced enough
load-bearing, id-traceable evidence to fully specify the falsifiers, controls, and confound
defenses above; further retrieval was judged likely to add volume, not decisions.
