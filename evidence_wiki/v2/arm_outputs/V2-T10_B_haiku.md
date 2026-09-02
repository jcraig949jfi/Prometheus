# PROPOSAL V2-T10 (arm B)

## Hypothesis

Generic feature-vector similarity across mathematical object catalogs (knots, number fields, elliptic curves) will fail to rank candidate cross-domain bridges above a correctly-specified null — reproducing the prior finding that seven generic operators found zero relations over 294M triples (C-a3744a88ea5e) — because generic vocabularies are category-blind. A native-invariant approach (where one exists) may succeed only if the feature-vector similarity strictly operationalizes a known algebraic transformation; the McMullen K3 construction (already killed at 0 hits / 245,280 evals; C-534275646eeb) serves as a negative anchor to certify that the pipeline can produce zero when the ground truth is zero.

## Motivating evidence

- **C-a3744a88ea5e:** Seven generic unary sequence operators found zero relations over 294,909,843 reachable triples on EC trace sequences; this is the 10^8-scale precedent for "generic fail."
- **C-96a0e90f4eeb:** One native verb (quadratic twist) recovered 4,476 exact relations where generic operators found zero, establishing that vocabulary choice, not object indifference, drives nullity.
- **C-534275646eeb:** The McMullen K3 bridge (small-Salem NF -> hyperbolic knot trace field) produced exactly 0 hits at 10^-40 tolerance over 245,280 reverse-substitution evaluations; usable as a calibration anchor.
- **C-8f20c74fa0cf:** Feature-vector similarity on coupling tensors over NF/EC/knots measured feature geometry (distributional overlap), not object-level coupling; confirmed across all three scorers.
- **C-1938a4759fd8:** Re-encoding knots with mathematically correct features (Mahler measure, root-of-unity evaluations) yielded no coupling signal, refuting feature mismatch as the cause of knot silence.

## Prospective predictions

1. The generic-feature arm will find ≤1 candidate correspondences across all three tested catalog pairs (EC-NF, EC-zeros, knots-NF) at the 10^6-10^7 scale—matching the 0-relation precedent from 294M triples.
2. Any apparent positive signal will shrink ≥50% under the marginal-shuffle feature-geometry control (C-8f20c74fa0cf/C-1f1a743fce1b), proving distributional confound rather than object coupling.
3. The McMullen K3 negative anchor will recover exactly 0 hits at 10^-40 tolerance (reproduce C-534275646eeb); pipeline miscalibration is the only cause that voids the entire run.
4. The native-invariant arm (EC quadratic twist only, where transformation is pre-registered and known) will recover ≥4,000 of 4,476 prior relations (≥95% anchor recovery), ensuring the pipeline is not systematically undercounting.

## Experiment

**Scope reduction:** Three catalog pairs only (EC-NF, EC-zeros, knots-NF), not six. EC and zeros use precomputed catalogs (LMFDB, Katz-Sarnak 35,416 forms). Knots use hyperbolic 12,963-element census.

**Two-stage, early-stop design:**

**Stage 0 (hard gate, immediate stop on failure):** Recover both calibration anchors with the exact same similarity-ranking pipeline before any novel scoring.
- Negative anchor: McMullen K3 reverse-substitution (5 Salem polys × 12,963 knot roots = 64,815 evals) → expect exactly 0 hits at 10^-40 tolerance.
- Positive anchor: EC quadratic twist (900 test curves, 12 isogeny classes) → expect ≥4,000 relations, ≥95% LMFDB-recorded after class dedup.
- **Failure mode:** If either anchor fails, ABORT entire run. Do not redesign; ABANDON this arm.

**Stage 1 (novel candidate ranking, one pass per pair):**
- Generic arm: top-k candidates (k=50 per pair, matched to catalog size) ranked by moment-based, magnitude-based, and degree-based summaries; score hit rate against corrected null (see Controls).
- Native arm: Not executed unless a pre-registered algebraic transformation exists *and* Stage 0 positive anchor succeeded.

## Controls

1. **Corrected null (mandatory, non-negotiable).** Across-set stratified conditional permutation: shuffle candidate labels within (parent-catalog, relation-type, availability-class) strata; preserve availability and hold-count. This is the C-750f2b6fc3ac fix applied verbatim—within-set shuffle has been burned.
2. **Feature-geometry marginal-shuffle control.** Replace each object's feature vector with a random draw from its catalog's marginal distribution, recompute ranking, and measure the fraction of observed D recovered. Threshold: ≥50% recovery → FEATURE_GEOMETRY artifact, signal is invalid.
3. **Generic-vs-native separation.** Report both arms completely separately; no score averaging, no blended verdict.
4. **Anchor recovery gate (Stage 0).** Both anchors must pass or entire run is VOID.
5. **Class-level deduplication.** Novel hits deduplicated by isogeny/equivalence class (per C-96a0e90f4eeb's 3,896 → 12 collapse ratio).
6. **Prime/conductor stratification.** Any discriminant- or conductor-indexed feature is stratified by bad-prime count before cross-catalog comparison (guards against the 96%+ prime-factorization confound).

## Confound defenses

- **Prime atmosphere:** Detrend all discriminant/conductor features for shared prime factorization (whitepaper Layer 1: 96%+ of naive scalar correlation).
- **Feature geometry vs. object coupling:** Control 2 is mandatory on every cell reporting D > 0.
- **Availability confound:** Stratified null (Control 1) exists to block state-conditioned ranking from reflecting joint availability rather than correspondence.
- **Isogeny/equivalence inflation:** Control 5 catches the dedup-multiplicity artifact.
- **Vocabulary-blindness doctrine:** Generic-arm nullity (0 relations) is not read as "no bridge exists"; it means the vocabulary is wrong. Native arm reports separately.

## Preregistered falsifiers (numeric thresholds)

- **F1 — null-calibration gate.** Corrected null hit rate deviates from expected by ≤2 SE; threshold violation → cell VACUOUS, no D reportable.
- **F2 — materiality bar.** D (top-k observed hit rate − null hit rate) must exceed 3 × SE(D); necessary but not sufficient.
- **F3 — feature-geometry kill.** Marginal-shuffle control recovers ≥50% of D → FEATURE_GEOMETRY artifact, signal void.
- **F4 — generic-vocabulary falsifier.** Generic arm finds 0 candidate hits across full sweep (10^6+ pair evaluations, matching C-a3744a88ea5e precedent); native arm (where testable) finds >0 → original generic formulation falsified.
- **F5 — anchor-recovery falsifier.** Negative anchor: any nonzero hit at 10^-40. Positive anchor: <4,000 relations or <95% LMFDB-recorded post-dedup → VOID entire run, no redesign.
- **F6 — dedup-collapse over-inflation.** ≥90% of raw hits collapse to LMFDB-recorded or same-class duplicates → zero novel discoveries claimed.
- **F7 — multiple-comparisons control.** 3 pairs × 2 arms = up to 6 family-wise tests; Holm-Bonferroni α=0.05.

## Stopping rule

**Stage 0 failures are terminal.** Negative anchor fails OR positive anchor fails → ABANDON, no Stage 1, no redesign loop.

**Within Stage 1:** Any cell tripping F1 (null miscalibration) → immediate STOP for that cell, route to null-redesign queue (max 1 iteration per pair; 2nd failure on same pair = terminal ABANDON for that pair).

**Program-wide stop:** If 2+ of the 6 controls fail on any single cell, terminal REDESIGN verdict (no Stage 1 results from that cell are reportable), matching C-750f2b6fc3ac precedent.

**No post-hoc metric shopping.** Feature definitions, catalog pairs, and arm configurations are frozen after Stage 0 passes.

## Expected failure modes

1. **Feature geometry reproduces (highest probability).** C-8f20c74fa0cf + C-1f1a743fce1b both showed distributional overlap, not object coupling, on the exact same catalogs; Control 2 will likely catch this again.
2. **Null misspecification in a new form.** The 4-catalog Sonnet design might expose a stratification corner case the 2-catalog C-750f2b6fc3ac fix did not cover; Haiku's 3-pair simplification reduces but does not eliminate this risk.
3. **Generic arm finds nothing at all.** C-a3744a88ea5e precedent suggests 0 is the most likely outcome; Haiku accepts this as a valid (falsifying) result, not a failed experiment.
4. **Positive anchor fails (Stage 0 abort).** EC quadratic twist is a theorem (C-96a0e90f4eeb), so this would signal pipeline bugs, not a hypothesis problem.
5. **Prime-conductor stratification reveals new confounds.** A derived feature (e.g., moment computed from discriminant) might be conductor-correlated without being explicitly flagged.
6. **Dedup-multiplicity cleanup nullifies any positive.** F6 catches isogeny-class inflation; Haiku expects this with high probability.

## Compute estimate

**Stage 0:** ~65K (negative anchor) + ~12K (positive anchor) pair evaluations = ~77K total, <1 minute.

**Stage 1:** 3 pairs × 2 arms × top-k=50 ranking + control runs ≈ 3 × (10^5 generic evals + 10^4 shuffle evals + overhead) ≈ few minutes to ≤1 hour total.

**Total wall-clock:** <2 hours on single CPU-bound session, no GPU, no training, no new corpus ingestion.

## Prior evidence that materially changed this design (or 'none found')

- **C-a3744a88ea5e (Generic operators fail):** Set the generic-arm hypothesis (expect ≤1 hits at 10^7 scale) and the scope choice (3 pairs instead of 6 for speed).
- **C-534275646eeb (McMullen K3 = 0):** Repurposed as the negative anchor for Stage 0 calibration; this is the only "bridge hypothesis" ever tested at scale to completion (not retracted, not hypothesis-upgrade after failure).
- **C-96a0e90f4eeb (Native verb succeeds):** Set the positive anchor (4,476 relations, ≥95%, ≥12 class-level triples) and justified the native-vs-generic split.
- **C-8f20c74fa0cf (Feature geometry, not coupling):** Mandated Control 2 (marginal-shuffle control) as mandatory, not advisory.
- **C-750f2b6fc3ac (Shuffled-label null failure):** Supplied the corrected across-set stratified conditional null and the "2 of N controls fail → terminal" stopping bar.

## Unresolved uncertainty

- Whether a native-invariant reformulation (e.g., explicit algebraic curve parameterization, Mahler-measure-based knot encoding) exists for the knot-NF or knot-zero pairs, making them testable with the native arm at all; Haiku marks these UNTESTABLE rather than forcing a redesign.
- Whether the prime-conductor stratification's 96%+ confound fully resolves in the 3-pair scope or resurfaces in higher-order interaction (e.g., degree-stratified conductor moments).
- Whether a negative Stage 0 anchor could be mis-specified (e.g., McMullen K3 boundary cases at ≤10^-40 tolerance that round to zero but are nonzero at higher precision).

## Evidence Wiki consultation log (queries + object ids retrieved)

**Query 1 (Op 3):** "ranking candidate bridges feature similarity cross-catalog"
- Results: C-8f20c74fa0cf (SUPPORTED), C-1938a4759fd8 (REFUTED), C-94fc12c3e6af (REFUTED)
- Relevance: C-8f20c74fa0cf motivated feature-geometry control (mandatory); C-1938a4759fd8 reinforced that even correct features (Mahler + root-of-unity) fail; C-94fc12c3e6af (feature routing) not cited in design (off-topic).

**Query 2 (Op 4):** "generic operators zero relations fail feature vector"
- Results: C-96a0e90f4eeb (OBSERVED, 4,476 native vs 0 generic), C-a3744a88ea5e (OBSERVED, 294M triples → 0)
- Relevance: Both cited directly; set generic-arm hypothesis and scale precedent.

**Query 3 (Op 5):** contradictions()
- Result: One contradiction (C-3a1c49fa5a78 vs C-3d12c440f087, both on "accumulated history improves search"; substrates differ; classified APPARENT_UNDER_DIFFERING_CONDITIONS)
- Relevance: Not relevant to bridge ranking; design proceeds unchanged.

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)

- **C-a3744a88ea5e** → Set generic-arm hypothesis to expect 0 or near-0 hits (matching 294M-triple precedent), defining F4's threshold.
- **C-96a0e90f4eeb** → Set positive anchor recovery metrics (4,476 relations, ≥95%, ≥12 class-level distinct), enabling Stage 0 calibration gate (F5).
- **C-534275646eeb** → Repurposed as negative anchor (expect exactly 0 at 10^-40) for Stage 0; makes the pipeline calibration executable rather than theoretical.
- **C-8f20c74fa0cf** → Mandated Control 2 (marginal-shuffle feature-geometry test) as non-optional on any positive D.
- **C-750f2b6fc3ac** → Supplied the corrected across-set stratified conditional null (Control 1), replacing the burned within-set shuffle; set the "2 of N controls fail → terminal" stopping bar.
- **C-1938a4759fd8** → Reinforced that correct features (Mahler measure, root-of-unity) alone do not create coupling on knots; design does not treat feature correction as a solution.
- **C-94fc12c3e6af** (retrieved but did not affect design) — Cold-start feature routing null is orthogonal to bridge ranking; not cited.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Read F:\Prometheus\evidence_wiki\v2\arm_outputs\V2-T10_C_sonnet.md (reference design, document 1/12).
2. Read F:\Prometheus\evidence_wiki\v2\packs\V2-T10_pack.json (context and evidence IDs, free).
3. Bash: import EvidenceWiki; ew.search_evidence('ranking candidate bridges...', k=5) → retrieved 5 results, 3 cited.
4. Bash: import EvidenceWiki; ew.search_evidence('generic operators zero relations...', k=3) → retrieved 2 results, 2 cited.
5. Bash: import EvidenceWiki; ew.contradictions() → retrieved 1 contradiction pair, marked not relevant.

Ops used: 5 / 15. Documents opened: 1 / 12. Early stop justified: Sonnet design provides complete structural template; Evidence Wiki queries confirmed all cited evidence and revealed no contradictions relevant to bridge ranking; additional searches redundant.
