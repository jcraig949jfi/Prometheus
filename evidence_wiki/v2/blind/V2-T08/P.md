# PROPOSAL V2-T08 (arm)

## Hypothesis

Fine-tuning a small local model (3-4B parameters, our stated VRAM ceiling) on the archive of
solved and failed attempt records will shift where the model sits within its EXISTING judgment
geometry — raising calibration and confidence-placement on attempts that resemble the training
distribution — but will NOT produce a structurally new discrimination capability for attempts
that are "plausible-shaped failures" (syntactically/formally correct-looking but wrong) drawn
from outside that distribution. Put as a single falsifiable claim: the post-FT judge's accuracy
gain will be measurably larger on near-distribution held-out attempts than on a matched set of
adversarially-plausible decoy attempts, and the between-family (near vs. decoy) gap will not
shrink relative to a prompted-baseline judge given the same records in-context.

This is a deliberate bet AGAINST the naive story ("more solved/failed examples make the judge
smarter at judging") and FOR the corpus-first finding already observed once in this program: fine
tuning on self-generated correct/corrected/unknown examples moved margins inside existing basins
without changing which basins exist (ignis/RESULTS.md, "Corpus-First Experiment", 2026-03-28).

## Motivating evidence

Three independent prior results in this repository bear directly on this design, all found via
ordinary search over F:\Prometheus (not evidence_wiki):

1. **ignis/RESULTS.md** ("Corpus-First Experiment", added 2026-03-28): supervised fine-tuning of
   Qwen-1.5B on 300 self-generated reasoning examples (74 correct, 181 corrected, 45 "unknown" —
   i.e. exactly a solved/failed/uncertain attempt archive) produced 0% change on Tier A/B accuracy
   but +9.5pp on far-transfer (Tier C), +21.4pp metacognition, +15.4pp self-correction, with the
   "ejection profile" (which answers survive internally) STRUCTURALLY UNCHANGED (26/30 alive
   before and after, median surviving layer unchanged at 26). Explicit conclusion in-file: "the
   basins are the ceiling... what moved is the model's position within the basins." This is the
   single closest prior instance of "fine-tune a small local model on solved/corrected attempt
   records" in the program, and it did not produce new discrimination — it produced better
   confidence placement on existing discrimination.

2. **aporia/docs/deep_research_reports/2026-05-23/00356_erg_02_substrate_alternatives_for_falsification_routing_lear.md**
   (Tier-2, unpinned to primary literature per `feedback_verify_upstream_attributions`): documents
   that Daedalus's Walk-1 substrate — an ML routing/judgment learner trained on ~5,000 mathlib4
   proof-trace records — hit an empirical scaling ceiling past ~2,000 records (+0.064 mean R² on
   kill-vector regression, +0.092 accuracy on 15-way next-macro classification, no further gain
   from more records or more trajectory context past 2-Markov). The report's central diagnosis:
   mathlib4 is "a repository of successful, heavily refactored proofs... a repository of
   survivorship bias. Training a falsification-routing Learner strictly on successful paths is
   akin to training a diagnostic classifier entirely on healthy patients." This is a direct,
   in-repo precedent for the exact task class in T08 (train a small model to judge/route proof
   attempts) hitting a low ceiling for a corpus-composition reason, not a scale reason.

3. **aporia/docs/EVIDENCE_2026-08-18_falsification_first_external.md** (Tier-2 synthesis, filed by
   Aporia, thread ERGON-FALS-MINE): reports frontier models solve ~48% of algorithmic problems but
   refute only <9% of subtly-incorrect solutions presented as correct — a ~5:1
   generation/verification asymmetry — and that 85-95% of model self-verification steps are
   CONFIRMATORY rather than corrective (independently matching this program's own
   promotion-confirms-by-assertion finding, M0.5, 2026-06-23). The same brief reports that
   contrastive success/fail PAIRED records on the same claim surface ("matched-twin doctrine")
   outperform isolated verdict labels for inducing falsification behavior in training.

Taken together: (a) this program has already run something close to this exact experiment once
(ignis) and got a calibration-not-discrimination result; (b) the nearest in-repo analogue of
training-a-judge-on-attempt-records (Daedalus Walk-1) hit a low ceiling attributable to
survivorship bias and flat/tabular record shape, not data volume; (c) any judge trained on
naively-labeled solved/failed records is at high prior risk of learning to be confirmatory
(rubber-stamp) rather than discriminating, because that is the dominant failure mode already
measured in this exact space.

## Prospective predictions

If the hypothesis is correct, we expect, ex ante:
- P1: FT-judge AUC-ROC on near-distribution held-out attempts > prompted-baseline-judge AUC-ROC
  on the same set, by a nontrivial margin (see falsifiers).
- P2: FT-judge AUC-ROC on the decoy set (plausible-but-wrong attempts, same claim surface as a
  real success — matched-twin construction) is NOT meaningfully better than prompted-baseline on
  the same decoy set — i.e. the near-vs-decoy AUC gap does not close after fine-tuning.
- P3: FT-judge's false-negative rate on decoys (calling a wrong attempt "will succeed") is at or
  above the ~91% miss rate observed for frontier models on subtly-incorrect solutions
  (EVIDENCE_2026-08-18) unless the training corpus is explicitly paired (kill+survive same
  surface) rather than pooled-and-shuffled.
- P4: Held-out accuracy vs. training-corpus size follows a curve that visibly bends before the
  full archive is exhausted (an in-repo analogue of the Walk-1 ~2,000-record ceiling), rather than
  monotonically improving with more records.
- P5 (the confound the hypothesis predicts we will NOT see, and which would falsify it if we did):
  a genuinely novel discrimination capability — FT-judge correctly flags decoy attempts that the
  prompted baseline, given the identical records in-context, cannot flag even with unlimited
  context budget.

## Experiment

**Corpus.** Assemble the archive of solved and failed attempt records available under
F:\Prometheus (excluding evidence_wiki). Candidate sources identified during search: Ergon's
admission/eviction attempt records (ergon/gen1b — per-artifact draw/credit/admission and eviction
logs with recorded outcomes) and Daedalus/Aporia proof-attempt traces (mathlib4-derived, per the
ERG-02 report). Each record must carry: (attempt features available BEFORE the outcome was known),
(outcome: solved / failed / abandoned), (failure-mode tag where available). Records must be
partitioned by TIME or by LINEAGE-of-origin, never shuffled across the solved/failed boundary,
to avoid leaking outcome-correlated identifiers into features (see Confound defenses).

**Model.** One small local instruction-tuned base in the 1.5B-4B range (matches ignis's
Qwen-1.5B precedent and this program's stated local ceiling), fine-tuned with LoRA (rank 4-8,
following the ignis recipe: targeted projections, not blanket rank-16, since blanket rank-16
collapsed performance in the ignis 1.7B run — 0.083 SR vs 0.417 for a 42x-smaller targeted
adapter).

**Task framing.** Binary/probabilistic judge: given an attempt's pre-outcome features, output
P(succeed). Trained via supervised fine-tuning on the archive, in TWO arms:
- Arm F-pooled: naive pooled solved/failed records, shuffled, standard SFT.
- Arm F-paired: matched-twin construction — wherever the archive permits, pair a killed attempt
  with a surviving attempt on the same claim surface (per the matched-twin doctrine in
  EVIDENCE_2026-08-18), contrastive-formatted.

**Held-out evaluation, three disjoint sets, none seen in training:**
- E-near: held-out attempts from the same task families as training (temporal or lineage
  split, never record-level shuffle-split).
- E-decoy: constructed plausible-but-wrong attempts on claim surfaces that DO have a real
  training-set success twin (AST-perturbation / hypothesis-softening in the style catalogued in
  EVIDENCE_2026-08-18 section 3) — i.e., attempts that look like a success shape but are not.
- E-far: attempts from a structurally different family not represented in training at all (the
  transfer test; analogous to Ignis's Tier C far-transfer split).

**Baselines, matched compute/exposure:**
- B-zero: same base model, zero-shot judge, no records.
- B-prompt: same base model, in-context with as many records as fit the context window (an
  exposure-matched, non-fine-tuned comparator — this is the "competence vs exposure" comparator
  required by `feedback_onpolicy_score_conflates_exposure_and_competence`).

**Metrics per (model, eval-set):** AUC-ROC, Brier score, calibration curve (10-bin), false
negative rate at the operating threshold that gives B-zero 50% precision (so all models are
compared at a threshold fixed BEFORE any model's outputs are seen).

**Seeds.** 5 independent fine-tuning seeds per arm (F-pooled, F-paired), per
`feedback_replicate_seeds`. Evaluation sets are fixed (not resampled per seed).

## Controls

- B-zero and B-prompt isolate how much of any observed gain is fine-tuning-specific versus just
  exposure to the records at inference time (in-context). This directly targets
  `feedback_onpolicy_score_conflates_exposure_and_competence`: an "improved judge" score is
  exposure x competence, and B-prompt is the same exposure without the weight update.
- A record-shuffled-history control (per ergon/gen1a's own "M1-shuffled-history" arm design,
  power_analysis_2026-09-01.json, which measured the ORDER component of accumulation as exactly
  zero, mean 0.0, sd 0.041): fine-tune on the same records in randomized temporal order, to check
  whether any gain is driven by content or by an artifact of presentation order.
- Decoy generation follows the four documented recipe classes in EVIDENCE_2026-08-18 §3 (AST
  perturbation, hypothesis-softening, citation-mimicry, prove-by-similarity) rather than
  ad hoc negatives, so failure types are typed and reproducible, not hand-picked to flatter the
  hypothesis.
- A held-out committee/independent-adjudicator check on a 10% sample of E-decoy outcome labels,
  since the labels themselves (solved/failed) must not be assigned by the same model family being
  judged (no same-model audit; `feedback_promotion_requires_independent_failure_mode`).

## Confound defenses

- **Leakage via record ordering / IDs.** Attempt records in this program frequently carry
  timestamp or lineage identifiers correlated with outcome (later lineages solve more, per the
  ergon gen1a accumulation effect, mean +0.11 vs no-library). Any feature the judge sees must be
  scrubbed of timestamp, lineage index, or run-id fields, or the judge will learn a
  temporal/lineage proxy instead of a content signal. Verified by checking that shuffling record
  IDs (holding content fixed) does not change judge accuracy.
- **Survivorship bias in the archive itself.** Per the ERG-02 report, if solved records
  dominate or are structurally cleaner than failed records (more refactored, shorter, better
  formatted), the judge may learn "looks like the clean corpus" rather than "will succeed." This
  is why E-decoy exists: decoys are constructed to be surface-clean but wrong, specifically to
  detect this confound. If FT-judge AUC on E-near improves but FN rate on E-decoy does not
  improve over B-zero, that is the survivorship-bias signature, not a discrimination gain.
  (`feedback_verify_signature_exists_before_controls`: confirm the "will this attempt succeed"
  signal is present and separable in the archive at all before trusting any FT delta.)
- **Confirmatory-bias / rubber-stamp collapse.** Per EVIDENCE_2026-08-18 (85-95% of
  self-verification is confirmatory), the FT-judge could trivially raise AUC-ROC/accuracy by
  learning to predict the training base rate (mostly "succeeds") rather than discriminating.
  Reported alongside AUC-ROC: the judge's overall predicted-success rate versus the true base
  rate in each eval set, and precision-recall (not accuracy alone), since accuracy on an imbalanced
  archive can be gamed by a constant-output judge.
- **Wrong population / mismatched difficulty.** E-near, E-decoy and E-far must be drawn from
  disjoint task families with their true difficulty distributions reported (not assumed equal),
  per `feedback_wrong_population_statistics` — a gain on E-near computed against an easier
  population than training would inflate the headline number.
- **Naive score combination.** AUC-ROC, Brier, and FN-rate at fixed threshold are reported
  SEPARATELY per eval set, never linearly averaged across E-near/E-decoy/E-far, since these are
  heterogeneous populations (`feedback_no_naive_score_combination`).

## Preregistered falsifiers (numeric thresholds)

Following this program's existing statistical convention (paired design, sign-flip permutation,
Holm-Bonferroni across the family of contrasts — ergon/gen1b/PREREG_GEN1_2026-09-01.txt):

- F1 (headline claim FAILS): ΔAUC-ROC(FT-paired vs B-prompt) on E-near, computed as the mean of
  5 paired seed-level deltas via two-sided sign-flip permutation (20,000 permutations), does not
  exceed 0.03 AUC at the Holm-corrected 0.05 level. Effect-size floor of 0.03 AUC is chosen to sit
  above the between-seed SD observed in the pilot batch of 5 seeds (computed before unblinding,
  analogous to the gen1a MDE convention of setting the bar above measurement SD —
  `feedback_gate_must_exceed_measurement_error`); if pilot SD makes 0.03 unreachable given n=5
  seeds, the run is declared underpowered rather than the bar lowered post hoc.
- F2 (survivorship-bias / confirmatory-collapse signature CONFIRMED, hypothesis's core prediction
  P2 upheld): ΔAUC-ROC(FT-paired vs B-prompt) on E-decoy is ≤ 0.01 AUC AND FN-rate on E-decoy for
  FT-paired is ≥ 0.70 (i.e., the judge still misses at least 70% of plausible-but-wrong attempts,
  anchored to the ~91% frontier-model miss rate reported in EVIDENCE_2026-08-18 as the regime this
  program already knows it is in).
- F3 (hypothesis FALSIFIED outright): if ΔAUC-ROC(FT-paired vs B-prompt) on E-decoy ≥ 0.05 AUC
  AND FN-rate on E-decoy drops below 0.50 — i.e., fine-tuning produces genuine new discrimination
  on adversarial decoys, not just calibration on near-distribution attempts — the hypothesis as
  stated is wrong and the corpus-first / basins-are-the-ceiling story does not generalize from
  Ignis's reasoning-trap domain to attempt-record judgment.
- F4 (order-vs-content control): the shuffled-history arm's ΔAUC-ROC vs FT-paired must be within
  ±0.02 AUC of zero (paired sign-flip test) for the ergon gen1a "order component measured zero"
  precedent to be corroborated in this domain; if shuffled-history matches or beats FT-paired,
  content in this archive is not doing the work.
- F5 (ceiling claim, P4): held-out AUC on E-near plotted against training-record count (5 log-
    spaced checkpoints: 20%, 40%, 60%, 80%, 100% of archive) must show a second-derivative sign
  change (visible bend) before 100% of records are used, mirroring the Walk-1 ~2,000-record
  ceiling; absence of any bend across the full archive falsifies the ceiling prediction (does not
  falsify P1/P2 on its own).

All five are frozen before any fine-tuning run begins. A contrast is called only if it survives
Holm-Bonferroni correction across F1, F2, F4 (the three formal significance tests); F3 and F5 are
directional/shape checks reported without a multiplicity correction, per the gen1b convention of
separating primary-scored contrasts from descriptive/exploratory measures.

## Stopping rule

Fixed-length run: 5 seeds x 2 arms (F-pooled, F-paired) x fixed eval sets, no interim look, no
optional stopping, no extension of seed count after seeing results — matching
ergon/gen1b/PREREG_GEN1_2026-09-01.txt §8. If the archive cannot supply enough matched-twin pairs
for a well-powered F-paired arm (assessed by a pre-run pairing-yield count, target ≥300 pairs,
following the R13 power-floor convention observed in ergon/probe/ledgers/campaign_log.jsonl,
where a campaign below its preregistered floor of 300 was declared "R13-POWER-FLOOR-UNMET" and
run only as a disclosed pipeline exercise, not a decisive run), this run is declared underpowered
and reported as a pipeline exercise, not a decisive result — never reinterpreted or waived
silently. If fine-tuning cannot complete for all 5 seeds x 2 arms, whatever seeds completed are
reported with their count and the primary analysis is declared underpowered rather than
reinterpreted.

## Expected failure modes

- The archive yields too few genuine failed-attempt records with pre-outcome features intact
  (most "failed" events in the probe/campaign logs inspected during search are infra-level
  events — timeouts, wall status — not content-level solution attempts), forcing either a smaller
  corpus than planned or substitution of a different attempt-record source; this must be disclosed,
  not patched over.
- Matched-twin pairing yield is low because most solved records in this program's corpora are,
  per the ERG-02 finding, "heavily refactored" survivors with no naturally occurring near-twin
  failure — forcing synthetic decoy construction to stand in for real paired failures, which
  weakens the paired-arm's ecological validity relative to F-pooled.
- The judge collapses to predicting the training base rate (the confirmatory-bias failure mode
  already measured at 85-95% elsewhere in this program) and every metric except FN-rate looks
  fine; this is why FN-rate and predicted-vs-true base rate are load-bearing reported numbers, not
  optional diagnostics.
- LoRA rank/target selection follows the ignis precedent (targeted, small rank beats blanket,
  larger rank) but this program has only one data point (Qwen-1.5B, reasoning-trap task) for that
  finding; it may not transfer to a classification/judgment head, and blanket-rank should be run
  as an unscored engineering check before committing compute to the targeted configuration.
- 5 seeds may be underpowered to detect a 0.03 AUC effect if between-seed SD in this domain is
  larger than the ergon/gen1a between-lineage SD (~0.03-0.06) used as the sizing anchor; a pilot
  SD estimate is required before the 0.03 threshold in F1 is treated as reachable.

## Compute estimate

Anchored to this program's only directly comparable local fine-tuning run (ignis, 2026-03-28):
Qwen-1.5B, 300 examples, 3 epochs, lr=5e-6, bf16, gradient checkpointing, on one RTX 5060 Ti
(16GB VRAM), reported as part of a sub-6-hour total experiment envelope. Scaling to this design:
2 arms x 5 seeds = 10 fine-tuning runs, each on an archive plausibly 1-2 orders of magnitude
larger than 300 records (Daedalus Walk-1 used up to ~5,000 records before its ceiling) — estimate
0.5-2 GPU-hours per run depending on final corpus size and LoRA rank, i.e., 5-20 GPU-hours total
for training. Evaluation (3 eval sets x ~3 model variants x 5 seeds, batched inference on a
1.5-4B model) is materially cheaper, estimated under 5 GPU-hours total. No cloud compute assumed,
consistent with this program's stated hardware ceiling (`feedback_vram_ceiling`: local ceiling
3-4B, 7B OOMs on the 17GB-class card) — the model choice for this experiment should not exceed
4B parameters for that reason, independent of the ignis precedent.

## Prior evidence that materially changed this design

- ignis/RESULTS.md's Corpus-First Experiment result (fine-tuning on solved/corrected/unknown
  records changed metacognition/calibration without changing the underlying correctness
  structure) is the direct reason the hypothesis is framed as a calibration-not-discrimination
  claim rather than a straightforward "fine-tuning will make the judge better" claim, and the
  direct reason E-decoy exists as a mandatory eval split rather than an optional stretch goal.
- The ERG-02 substrate-alternatives report's survivorship-bias diagnosis of Daedalus Walk-1
  (training a routing/judgment learner on a successful-only, tabular corpus hit a ~2,000-record
  ceiling) is the direct reason F5 (the ceiling falsifier) and the archive-composition confound
  defense exist, and the direct reason record features must be checked for survivorship-bias
  proxies before trusting any FT delta.
- EVIDENCE_2026-08-18's measured 91%-miss / 85-95%-confirmatory figures and its matched-twin
  corpus-format finding are the direct reason this design runs TWO training arms (pooled vs
  paired) rather than one, and the direct reason FN-rate on decoys, not aggregate accuracy, is
  the load-bearing falsifier metric.
- ergon/gen1b's preregistration and ergon/gen1a's power analysis supplied the concrete statistical
  machinery adopted here (paired seeds, sign-flip permutation, Holm-Bonferroni, MDE set above
  measurement SD, fixed-length stopping rule) — reused rather than reinvented because this program
  already has a working, audited convention for exactly this class of small-n paired-arm design.
- The R13-POWER-FLOOR-UNMET verdict found in ergon/probe/ledgers/campaign/campaign_log.jsonl
  supplied the concrete precedent and threshold-count convention (a floor of 300, waived only by
  an explicit, named waiver artifact) adopted in the Stopping rule section for the matched-twin
  pairing-yield check.

## Unresolved uncertainty

- Which concrete corpus in F:\Prometheus should serve as "the archive of solved and failed
  attempt records" was not resolved by this search: the probe/campaign ledgers found during
  search are predominantly infra-level (channel opens, timeouts, coverage), not content-level
  solve/fail records; the Daedalus/mathlib4 proof-trace corpus referenced in the ERG-02 report is
  the closest match found but was not directly opened to confirm its current size, location, or
  whether it postdates the ~2,000-record ceiling already identified. This must be resolved before
  the experiment can run and is the single largest open risk to the whole design.
- Whether the ignis LoRA-targeting result (v_proj-style targeted adapters beating blanket rank-16)
  transfers from a reasoning-trap generation task to a binary/probabilistic judgment head is
  untested; this design assumes it might, but treats it as an engineering check, not a
  preregistered claim.
- Whether 5 seeds gives adequate power for the 0.03 AUC threshold in F1 depends on a between-seed
  SD this search did not measure for a judgment-head task (only for the unrelated
  lineage-CFR and reasoning-trap domains); a pilot run is required before F1 can be treated as
  well-powered rather than provisional.
- Whether matched-twin (kill+survive same-surface) pairs exist in sufficient number in whatever
  archive is finally selected is unknown; this determines whether the paired arm (F-paired) can
  be run as designed or must fall back to synthetic decoys standing in for real twins throughout,
  which would weaken rather than merely limit the design.

