# PROPOSAL V2-T10 (arm)

## Hypothesis

Ranking candidate cross-domain "bridges" between object catalogs (knots, number
fields, elliptic curves, L-function/zeta zeros) by tiered feature-vector
similarity — exact discrete-invariant hashing (Tier 1) plus soft continuous
similarity (Tier 2: cosine/Euclidean/log-ratio) — will surface at most a small,
non-zero set of candidate pairs whose cross-domain correspondence survives a
pre-registered confound gauntlet (distributional, range, prime-mediated,
scaling-class, group-theoretic, spectral-universality, complexity-normalized
nulls). The informative claim is NOT "similarity ranking finds bridges" — a
near-identical pipeline was already built and run in this repository and its
measured yield was ~0 confirmed bridges out of 6 candidates, with the residual
signal explained as fingerprint collision rather than structural correspondence
(see Motivating evidence). The hypothesis under test here is narrower and more
skeptical: that adding a catalog largely absent from the prior run (L-function
zeros) and applying the full 7-layer filter as a pre-registered gate — instead
of ad hoc post-hoc killing — still yields zero bridges above the two already-
weak survivors, OR yields exactly one new structural (non-tautological,
non-fingerprint-collision) bridge, and that either outcome is diagnostic of
whether the transport-matrix "two-tier, no-signal-above-null" finding
generalizes to a fifth catalog.

## Motivating evidence

- `F:\Prometheus\cartography\shared\scripts\v2\layer2\signature_matcher.py` —
  an already-built tiered cross-domain bridge detector (Tier 1: operadic
  skeleton hash, Newton-polytope vertex hash, symmetry class, mod-p
  fingerprint; Tier 2: spectral cosine ≥ 0.92, convexity Euclidean ≤ 3.0,
  discriminant |log-ratio| ≤ 1.0; Tier 3: requires ≥1 Tier-1 hit AND ≥2 Tier-2
  hits) with a falsification-battery hook (`run_battery_on_bridges`) and a
  documented prior fix ("Kill #11": trivial/generic skeletons such as `V`,
  `eq(V,V)` were producing spurious cross-domain matches and had to be
  excluded). This is architecturally almost exactly the task's target design
  — it already exists and has already been iterated on for false positives.
- `F:\Prometheus\cartography\docs\cross_domain_falsification_protocol.md`
  (2026-04-12, council adversarial review) — measured that **67% of
  cross-domain overlap claims were false positives (4/6 killed by Benford +
  size audit)**; the two survivors (#58 PG-NF, #32 Iso-MF) are flagged
  SUSPECT, likely a group-theoretic tautology and an Eichler-Selberg
  rediscovery respectively. As of that report: **"Novel cross-domain bridges
  confirmed: 0. Novel cross-domain bridges pending: 2 (both likely
  rediscoveries)."** This protocol's 7-layer filter (distributional,
  range/size, prime-mediated, scaling-class, group-theoretic ancestry,
  spectral universality, information-density normalization) is the direct
  ancestor of the "Controls" section below.
- `F:\Prometheus\cartography\docs\all_findings_classified.md`, finding #13
  ("Cross-Domain Transport Matrix"): `{OEIS, EC, MF, Knots}` form a permeable
  core, `{Lattices, NF}` are impermeable, and **all pairwise z-scores are
  `|z| < 2`**, with the explicit interpretation "Transport is fingerprint
  collision, not structural bridge." This is a direct, already-measured
  negative result for the exact mechanism (feature-vector similarity ranking)
  this task proposes to revive.
- Same file, finding #6 ("Information-Theoretic Bottleneck Is Exactly
  log₂(p) Bits"): offers a candidate mechanistic explanation for why
  cross-domain bridges fail — a generating-function evaluation stage caps
  throughput at log₂(p) bits and "selectively destroys the features linking
  recurrence structure to arithmetic values." This is a falsifiable causal
  account this design should try to distinguish from pure fingerprint
  collision.
- `F:\Prometheus\cartography\shared\scripts\v2\moonshine_oeis_bridge.py` — a
  second, independent instance of the same idea (coefficient-subsequence
  matching between moonshine-adjacent OEIS sequences and the wider OEIS
  corpus). Its result file's kill/survive status was not retrieved within
  budget (unresolved — see Unresolved uncertainty).
- `F:\Prometheus\aporia\docs\deep_research_reports\2026-05-21\00074_isl_02_knot_theory_number_theory_bridges_2025.md`
  — establishes that the *theoretical* case for a knot↔number-field bridge
  is genuine and long-standing (the Mazur-Mumford dictionary: 3-manifolds ↔
  number fields, knots ↔ prime ideals, linking number ↔ Legendre symbol), and
  that 2024-2026 work (Bar-Natan/van der Veen's Θ invariant, arithmetic
  Chern-Simons/BF theory) is actively about *which* such bridges are
  computable. This matters for calibration: the domain pair is not a strawman
  — a real dictionary exists — but the existing empirical program in this
  repo already shows that naive feature-similarity mining over these
  particular catalogs (as opposed to the theoretically-motivated invariants
  the dictionary specifies) mostly reproduces false positives, not instances
  of that dictionary.
- `F:\Prometheus\cartography\v2\knot_bridge.py` — confirms the knot catalog
  in this repo carries crossing number, Jones polynomial span, and
  determinant per knot (2,977 knots per finding #78/#94), usable as
  off-the-shelf feature vectors; also a useful negative-lead reminder that
  "bridge" is overloaded (here: knot bridge *number*, an intra-domain
  invariant, unrelated to cross-domain bridges) — naming collisions of this
  kind should be guarded against in the pipeline's own vocabulary.

## Prospective predictions

1. Applying the existing Tier-1/Tier-2/Tier-3 pipeline to the four-catalog
   set {knots, number fields, elliptic curves, L-function zeros} will
   produce a Tier-3-confirmed bridge count in the same low regime as the
   prior run: 0-3 confirmed candidates out of the enumerated Tier-1
   cross-domain buckets, not a step-change increase from adding the zeros
   catalog.
2. Of any Tier-3-confirmed candidates, the majority (≥50%) will fail at
   Layer 1 (distributional) or Layer 2 (range/size) of the 7-layer filter,
   replicating the 4/6 (67%) false-positive rate already measured.
3. Any candidate that survives Layers 1-2 will disproportionately involve
   primes or prime-indexed features (zero counting function, prime ideal
   norms) and will be substantially weakened or killed by Layer 3
   (prime-mediated null), consistent with feedback that ~96% of
   cross-dataset structure traces to prime-atmosphere rather than
   catalog-specific structure.
4. If the log₂(p) information-bottleneck account (finding #6) is the correct
   mechanism, restricting comparisons to features computed *before* any
   modular/finite-field reduction step should raise the confirmed-bridge
   rate relative to features computed after such a step; if fingerprint
   collision (finding #13) is the correct account instead, no such
   before/after difference should appear.

## Experiment

1. **Catalog and feature inventory (enumeration, not sampling).** For each
   of the four catalogs, enumerate the full available feature set actually
   present in the repo's existing data files (not a themed subset) — e.g.
   knots: crossing number, determinant, Jones polynomial coefficients/span,
   signature (per `all_findings_classified.md` #78/#94); number fields:
   discriminant, degree, Galois group, class number; elliptic curves:
   conductor, rank, modular degree, regulator (per findings #69/#372);
   zeros: zero ordinate, counting-function residual, pair-correlation
   statistics. Record counts per catalog before any filtering — this is the
   inventory step required before any stratified sampling (per prior finding
   that alphabetical/prefix sampling silently hid most of a corpus).
2. **Reuse, don't rebuild, the Tier-1/2/3 pipeline.** Extend
   `signature_matcher.py`'s signature schema to admit zeros-catalog records
   (new `SIG_FILES` entries) rather than writing a parallel pipeline;
   preserve its existing Tier-1 hash types, Tier-2 thresholds (cosine ≥ 0.92,
   Euclidean ≤ 3.0, log-ratio ≤ 1.0) as the PRE-REGISTERED default — do not
   retune thresholds against the observed cross-domain hit rate.
3. **Run in `--dry-run` mode first** to get the raw Tier-1 cross-domain
   bucket count and Tier-3 confirmed count before invoking the falsification
   battery, exactly mirroring the existing script's two-stage design.
4. **Apply the 7-layer filter** from
   `cross_domain_falsification_protocol.md` to every Tier-3-confirmed
   candidate, in the documented order (distributional → range/size →
   prime-mediated → scaling-class → group-theoretic → spectral-universality
   → information-density normalization), stopping and recording the layer at
   which each candidate is killed.
5. **Held-out replication.** For any candidate surviving all 7 layers,
   partition each catalog by an orthogonal split (e.g. odd/even discriminant
   for number fields, odd/even crossing number for knots) and require the
   candidate similarity to replicate above threshold in BOTH halves
   independently before it is called anything stronger than PENDING.

## Controls

- **Uniform/Benford null (Layer 1):** compare observed Tier-1/Tier-2
  cross-domain hit rate to the rate expected if each catalog's feature
  values were drawn from its own marginal (Benford or empirical univariate)
  distribution independently — this is the control that killed 4/6 prior
  candidates and must be run first, not last.
- **Range-matched null (Layer 2):** re-run Tier-2 similarity after
  restricting both catalogs in a candidate pair to the same numeric window
  (e.g. same discriminant/conductor magnitude range), since the prior #34
  kill showed enrichment can be a pure artifact of both catalogs sampling
  small numbers.
- **Prime-conditioned null (Layer 3):** condition on prime-theoretic
  covariates (size, gap, residue class mod 6/12/30) before recomputing
  Tier-2 similarity, per the prime-atmosphere finding that most
  cross-dataset structure is prime-driven.
- **Permutation null on the similarity statistic itself:** shuffle catalog
  labels (not rows) across the union of both catalogs' feature vectors and
  recompute the Tier-2 cosine/Euclidean/log-ratio statistics 1,000 times to
  get an empirical null distribution; a candidate must exceed the 99th
  percentile of this null, not merely the fixed 0.92/3.0/1.0 thresholds, to
  be called Tier-3-confirmed. (Fixed thresholds alone reproduce exactly the
  same "fingerprint collision" pipeline finding #13 already measured — a
  permutation-calibrated threshold is the only way this design adds
  information beyond the existing run.)
- **Non-lineage control:** where a candidate pair's similarity could be
  explained by both objects being drawn from the same "genus"/generation
  process (e.g. both catalogs are down-stream of the same L-function used
  to define both a Galois representation and a zero set), exclude that pair
  from the confirmed set outright — this control is a hard exclusion, not a
  reweighting, per the standing rule that a control drawn from the
  treatment's own selection relation IS the treatment.

## Confound defenses

- **Verbs-must-be-native guard:** per the prior finding that 7 generic
  cross-domain operators found 0 relations among elliptic curves over 295M
  triples while 1 native verb (quadratic twist) found 4,476 on the same
  data, treat any Tier-1/Tier-2 similarity computed from *generic* numeric
  features (raw magnitude, raw count) as lower-priority evidence than
  similarity computed from features that are native invariants of both
  domains under the Mazur-Mumford dictionary specifically (e.g. linking
  number ↔ power residue symbol, not "both numbers are between 1 and 100").
- **Tautology/rediscovery guard:** any surviving candidate must be checked
  against known Langlands-program correspondences before being called
  "novel" — the prior program's two SUSPECT survivors (#58, #32) were
  flagged exactly because they likely rediscover an existing tautological
  or Eichler-Selberg identity rather than finding new structure.
- **Sampling-window guard:** enumerate the full feature inventory per
  catalog before selecting any subset for comparison (Experiment step 1);
  do not iterate catalogs in file-order or take `catalog[:N]`, since prefix
  sampling previously hid 137/141 relations and 5/8 edge-bearing generators
  in an unrelated corpus.
- **Threshold-vs-measurement-error guard:** before adopting any fixed
  Tier-2 threshold as a gate, compute the standard error of the underlying
  similarity statistic under the permutation null and confirm the threshold
  sits at least 3 SE away from the null mean; do not report a verdict where
  the gate is closer to the observed value than its own SE.
- **Naming-collision guard:** explicitly distinguish "bridge" as used here
  (a cross-domain feature-similarity correspondence) from "bridge number"
  (an intra-domain knot invariant already computed in
  `cartography/v2/knot_bridge.py`) in all output records and documentation,
  to prevent a downstream consumer from conflating the two.

## Preregistered falsifiers (numeric thresholds)

- **F1 (kills the revival):** if 0/N Tier-3-confirmed candidates survive all
  7 layers AND the permutation-calibrated exceedance test, for N ≥ 20
  Tier-1 cross-domain buckets examined, the hypothesis is falsified in the
  strong sense — the pipeline replicates finding #13 exactly and the
  "revival" adds nothing beyond what was already known on 2026-04-12.
- **F2 (kills the "new catalog helps" sub-claim):** if the L-function-zeros
  catalog contributes zero Tier-1 cross-domain buckets with any of the other
  three catalogs (i.e. it never appears in a cross-domain bucket at all),
  the sub-hypothesis that adding zeros would surface new bridges is
  falsified regardless of what happens with the other three catalogs.
- **F3 (kills the bottleneck-mechanism prediction):** if the
  before/after-modular-reduction confirmed-bridge rate differs by less than
  a factor of 1.5 in either direction (with 95% CI overlapping 1.0), the
  log₂(p) information-bottleneck account (finding #6) is not distinguished
  from the fingerprint-collision account (finding #13) by this experiment.
- **F4 (promotes a candidate beyond PENDING):** a candidate is promotable
  only if it (a) exceeds the 99th-percentile permutation null on ≥2 Tier-2
  metrics, (b) survives all 7 filter layers, (c) replicates in both halves
  of an orthogonal held-out split (Experiment step 5) at the same threshold,
  and (d) is not a known Langlands-program identity. Absent all four, no
  candidate may be reported as more than PENDING/SUSPECT, mirroring the
  existing #58/#32 status.

## Stopping rule

Run Tier-1/Tier-2/Tier-3 matching once on the full four-catalog inventory
(no iterative threshold retuning). Apply the 7-layer filter once, in fixed
order, to every Tier-3-confirmed candidate. Stop and report after: (a) every
candidate has been assigned a terminal status (KILLED-at-layer-k, PENDING,
or PROMOTED per F4), and (b) the held-out replication check (Experiment
step 5) has been run on every PENDING/PROMOTED candidate. Do not continue
searching with loosened thresholds if the initial run yields zero
candidates — a null result here is itself the deliverable (per F1), not a
reason to keep adjusting the pipeline until something clears the bar.

## Expected failure modes

- **Most likely outcome, per direct precedent:** near-total replication of
  the 2026-04-12 result — most or all candidates killed at Layers 1-2,
  yielding a null that confirms rather than revives the idea.
- **Prime-atmosphere masquerade:** any surviving candidate turns out to be
  mediated entirely by shared prime-indexed features, not a genuine
  structural bridge (Layer 3 / prediction 3 above).
- **ID-scheme mismatch silently dropping candidates:** `signature_matcher.py`
  already logs a warning class for this (OEIS `A######` IDs vs formula
  hex-hash IDs cannot be compared through Tier-1 exact matching); the same
  failure mode likely recurs for zeros (indexed by ordinate or index number)
  vs number-field IDs (indexed by discriminant/LMFDB label) — a genuine
  bridge could be invisible to Tier-1 purely because of ID-namespace
  mismatch, independent of whether it is real. This must be logged as a
  distinct "lost pairs" count, not silently absorbed into "0 bridges found."
- **Battery under-coverage:** the existing battery hook only tests bridges
  with directly comparable numeric arrays (mod-p signatures, discriminant
  numerics); structural matches (operadic/Newton/symmetry) fall through to
  a "REVIEW" verdict with no falsification test at all. A structural-match
  candidate reported as PENDING may really be untested, not "surviving
  scrutiny" — this must be labeled accordingly.
- **Overfitting the confound taxonomy to the 2026-04-12 candidate set:** the
  7 layers were derived to explain 6 specific historical false positives:
  they may not be an exhaustive basis for confounds specific to the
  zeros catalog, which introduces continuous (not discrete/algebraic)
  structure not represented in the original 6 cases.

## Compute estimate

- Feature/signature extraction for the zeros catalog (new): assume O(10⁴-10⁵)
  zeros with O(5-10) derived features each — CPU-only, minutes.
- Tier-1 hash indexing and Tier-2 pairwise scoring: existing pipeline is
  already O(catalog sizes); with 4 catalogs of order 10³-10⁵ records each,
  Tier-1 bucket construction is linear and Tier-2 pairwise scoring is
  restricted to within-bucket cross-domain pairs only (not all-pairs), so
  expect low-single-digit CPU-hours total, no GPU required.
- Permutation null (1,000 shuffles per candidate pair): trivial per-shuffle
  cost given the small number of surviving Tier-3 candidates expected
  (single-digit count per F1); total added cost is minutes, not hours.
- 7-layer filter application: mostly closed-form recomputation
  (conditioning, range restriction) on already-extracted features; no new
  data extraction required except where Layer 6 (spectral universality)
  requires generating RMT (GUE/GOE/Poisson) nulls per domain, which the
  protocol document already flags as "needs new infrastructure" (deferred
  item #10) — budget an explicit day of engineering time if Layer 6 is not
  to be skipped.
- Overall: this is a CPU-only, sub-day pipeline run once the zeros-catalog
  signature extractor exists; the dominant unknown cost is whether Layer 6
  (spectral universality null) needs to be built from scratch or can reuse
  existing RMT tooling elsewhere in the repo (not verified within this
  task's budget).

## Prior evidence that materially changed this design

The design changed substantially from a naive "run similarity ranking and
see what turns up" spec to the current one because of three findings
discovered during search, all inside this repository and none in
`evidence_wiki`:

1. The near-identical pipeline (`signature_matcher.py`) already exists and
   has already had at least one false-positive fix applied to it ("Kill
   #11", generic-skeleton exclusion) — this makes "revive the idea" mean
   "extend and re-gate an existing, already-once-burned pipeline," not
   "build one from scratch."
2. `cross_domain_falsification_protocol.md` reports a measured 67%
   false-positive rate and 0 confirmed novel bridges as of 2026-04-12, with
   an explicit 7-layer filter taxonomy already built from that experience.
   This directly supplied the Controls and Confound-defenses sections
   instead of a generic significance-testing plan.
3. `all_findings_classified.md` finding #13 ("Transport is fingerprint
   collision, not structural bridge," all |z| < 2 across the existing
   4-catalog transport matrix) reframed the hypothesis from a positive
   discovery claim into the current falsification-first framing (F1-F4),
   and directly motivated prediction 4 and falsifier F3 (distinguishing the
   fingerprint-collision account from the log₂(p) information-bottleneck
   account in finding #6).

## Unresolved uncertainty

- Whether `moonshine_oeis_bridge.py`'s coefficient-subsequence bridges (a
  structurally different bridge-detection method, exact 6-term window
  matching rather than tiered invariant similarity) were ever run through
  the 7-layer filter or the falsification battery — its output file
  (`moonshine_oeis_results.json`) was not opened within this task's
  retrieval budget, so its kill/survive status is unknown and should be
  checked before this design is executed, in case it already answers part
  of prediction 1-2 for the OEIS/modular-forms pair.
- Whether an L-function-zeros catalog with a stable, LMFDB-comparable ID
  scheme actually exists in this repo in a form the Tier-1 pipeline can
  index (the domain_map / catalog inventory that would answer this was
  found via search but not opened within budget) — if it does not exist in
  indexable form, Experiment step 1 (inventory) may reveal that the "zeros"
  catalog needs to be built before this spec can run at all, which would
  itself be a scope-changing finding.
- Whether Layer 6 (spectral universality / RMT null) has any existing
  reusable implementation elsewhere in the repo (e.g. under `techne/` or
  `aporia/`) — the falsification protocol document flags it as needing new
  infrastructure as of 2026-04-12, but nine months have passed and this was
  not re-checked here.
- Whether the two SUSPECT survivors (#58 PG-NF, #32 Iso-MF) have since been
  formally killed or promoted somewhere after 2026-04-12 — no later-dated
  status update for these two specific IDs was located within budget.

