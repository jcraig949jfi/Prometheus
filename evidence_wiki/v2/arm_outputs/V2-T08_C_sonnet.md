# PROPOSAL V2-T08 (arm C)

## Hypothesis
LoRA fine-tuning a small local model (≤4B params, within the measured ~3–4B local VRAM
ceiling) on our archive of solved-and-failed attempt records produces a judge whose
success/failure prediction on a NEW attempt beats (a) a behavioral heuristic floor built
from the same archive's base rates and (b) the base model's zero-shot judgment, AND that
this gain survives decomposition into format/prior/memorization components — i.e. a
non-trivial "genuine judgment" residual remains after those components are subtracted,
on both an entity-disjoint and a relation/domain-disjoint held-out split.

The competing (null) hypothesis, taken seriously because it is the modal outcome in this
archive's own history: the observed gain is ~entirely format-following + outcome base-rate
+ value memorization, with a genuine-judgment component statistically indistinguishable
from zero — the same decomposition previously found for a structurally identical
fine-tune-a-judge task.

## Motivating evidence
Two prior LoRA fine-tunes of a judge/classifier on this fleet's own attempt records
(`roles/Ergon/GREEDY_LORA_RESULT_2026-06-03.md`, `roles/Ergon/GREEDY_FOLLOWUP_FINDINGS_2026-06-07.md`)
found a large raw gain (Base 0.228 → LoRA 0.907, held-out n=1,200) that survived a
shuffled-label control (0.681) and an entity-disjoint holdout, but decomposed to genuine
reasoning ≈0.10 of the raw +0.68, dominated by format-following, a relation base-rate
prior (~0.67 oracle), and value memorization (~0.12); leave-one-source-out ablations
dropped performance to near-chance on three of the tested sources, and out-of-domain
transfer was ~+0.027 on n=600 (~1.3σ, not significant). This is the single most directly
on-task precedent and sets the default expectation for what "fine-tune a small model as a
success/failure judge" produces absent specific countermeasures.

A positive counter-precedent exists for learning from failure evidence alone: Incubation
v1's guard learner recovered a hostile world's exact designed trap boundary from failure
evidence with 0 false positives and out-of-sample prediction 0.9975–1.0 across seeds
(`incubation/DOCUMENTATION.md`) — but the same report records the boundary as bounded,
not repaired, at the task level (minimal solutions that avoid the hazard entirely are
unreachable by any state predicate). This is the ceiling case for what "learn a failure
boundary" can achieve, and it worked because the archive there had a clean
(state, predicate, outcome) structure — which the target archive is not yet shown to have.

Two routing evaluations on the same fleet's mined-failure/solve matrix
(`roles/Ergon/ROUTING_EVAL_2026-06-09.md`) show the signal is asymmetric by feature type:
collaborative/behavioral signal (which tool solved which problem) carries real navigable
structure beyond popularity (COLLAB AUC 0.829 vs POP 0.754, ΔAUC +0.075, P<0.0001,
survives an adversarial top-8 popularity drop), while concept/field metadata carries
none (FEATURE AUC 0.744 vs POP 0.753, real fields ≈ shuffled fields). This bears directly
on what features the judge should be trained on: attempt/outcome traces, not semantic
labels.

A retraction precedent (`aporia/docs/CYCLE_148L_TRANSFER_2026-08-24.md`) shows an
in-distribution positive result (147-K) reversing to anti-transfer on held-out relations
(D=-0.011, both models at or below the shuffled null) — memorization of 14 constants
masquerading as a learned relation. This is why relation/domain-disjoint transfer, not
just entity-disjoint holdout, is a mandatory split here.

Two archive-quality defects bear on whether the target archive is fit to train on at all:
(1) failed API/transport calls were loaded as fabricated prior-attempt residue,
byte-indistinguishable from legitimate empty-vocabulary records, at up to 24.4% of one
block (`ergon/probe/FINDING_transport_failures_as_residue_2026-08-25.md`); (2) a
structurally similar corpus (theseus/corpus) was closed for retrospective navigation
because none of its 8 edge-bearing generators recorded a usable (state, action, outcome)
triple (`aporia/docs/CYCLE_151O_CORPUS_CLOSED_2026-08-24.md`). A direct repo check this
session of a live local ledger (`ergon/probe/ledgers/campaign/campaign_log.jsonl`) found
only transport/channel-level events (`channel_open`, `channel_closed`, phase send/ok
counts) — not attempt-level (task, method, outcome) rows — confirming the same class of
gap is live in the artifact most likely to be reached for as "the archive" today.

A causal-inference caution: D6A's preregistered test of whether relational executable
history causally increases solver findability beyond the raw artifact hoard returned a
clean null (H3-H1 +0.010, p=0.4875, needed ≥+0.20; `SerendipityFoundry/D6A/REPORT_D6A.md`),
with even a designer-truth-seeded oracle upper bound moving dev-tier2 solves only
5/24→9/24. This licenses no claim that fine-tuning on archived history will causally
improve a general capability beyond this specific model's judgment on this specific task
distribution.

A calibration floor: a one-line non-LLM heuristic (count of five integers coprime to 30)
scored 0.5225 on fresh unseen tasks against a real solver's 0.4794
(`ergon/probe/FINDING_heuristic_floor_2026-08-24.md`) — the attainable-without-reasoning
floor in that probe band was far above chance. The judge here must clear an analogous
heuristic floor computed from the SAME archive (e.g. prior success rate by
method/agent/task-family), not chance.

Methodological precedent from a leakage-gate design in this fleet
(`ergon/probe/PREREG_adversarial_leakage_gate_2026-08-25.md`): a leakage/control test must
be two-sided (a below-null excursion is as informative as above-null and was, in that
campaign's own history, scored PASS on a live confirmed leak under a one-sided rule);
positive controls (a known-planted signal) must be run and shown detectable BEFORE a null
result is trusted; and splits must be grouped by the entity that could leak (there,
task uid; here, problem/task family) via GroupKFold-style assignment.

## Prospective predictions
1. Raw in-distribution AUC gain (fine-tuned judge vs. base model, same held-out split)
   will be positive and will replicate the 2026-06 magnitude range (expect a large raw
   gain, plausibly 0.4–0.7 AUC-equivalent, given the same fleet, similar archive scale).
2. That raw gain will decompose overwhelmingly into format-following + outcome
   base-rate + value memorization, mirroring the 2026-06 decomposition (reasoning share
   ≤0.15 of raw gain) UNLESS the archive audit (Phase 0) finds this archive has a richer,
   cleaner (context, method, outcome) structure than theseus/corpus or the campaign
   ledgers inspected this session — in which case a larger genuine-judgment residual is
   possible but not assumed.
3. Entity-disjoint holdout gain will be smaller than in-distribution gain but nonzero;
   relation/domain-disjoint holdout gain has a real chance of collapsing to or below the
   shuffled-label null (per the 148-L retraction precedent) — this is treated as a live
   possible outcome, not a confound to explain away.
4. The archive audit itself (Phase 0) has a meaningful chance of failing outright — i.e.
   the most likely single failure mode of this whole experiment is "no usable archive
   exists in the assumed location," not "the judge fails to learn."

## Experiment
**Phase 0 — Archive audit (blocking gate, must pass before any training).**
Enumerate every candidate source of "solved and failed attempt records" (ergon/probe
ledgers, incubation attempt logs, theseus/corpus generators, any Learner metabolization
logs). For each source, verify it yields a genuine (attempt_context, method/action,
outcome ∈ {solved, failed}, provenance) triple — not a transport/channel event, not a
positional method list without labels. Apply the same refuse-don't-render rule as
C-55004a4674b8: a source contributing zero verifiably-real triples is EXCLUDED, not
padded. Report per-source: n usable triples, n excluded and why, class-balance
(solved:failed), and duplicate/near-duplicate rate (entity leakage risk).

**Phase 1 — Baselines (no training).**
- Heuristic floor: best of {prior success rate by method, by agent, by task-family,
  by problem length/shape}, cross-validated on the same splits used later.
- Base-model zero-shot: prompt the untrained base model to judge each held-out attempt;
  compute AUC.
- Shuffled-label reference: label-permuted training target, same pipeline, establishes
  the null a real gain must clear.

**Phase 2 — Fine-tune.**
LoRA (rank 16, matching the 2026-06 precedent for comparability) on the base model
(candidate: Qwen2.5-Math-1.5B-Instruct, already cached locally at `E:/hf_cache/hub`, or
another model ≤4B params fitting the measured ~3–4B VRAM ceiling on the RTX 5060 Ti,
per `stations/M1_STATUS.md` and `techne/ARSENAL_SCAN_2026-08-21.md`). Train on Phase 0's
audited triples, split by GroupKFold on task/problem-family id so no attempt from a
held-out family appears in training (entity-disjoint).

**Phase 3 — Decomposition (mandatory, not optional).**
Repeat the 2026-06 decomposition battery against this new judge:
(a) shuffled-label control, (b) format-stripped control (structure/template preserved,
informative content replaced by a constant), (c) outcome-base-rate-only control (train
on the marginal label rate alone, no context), (d) leave-one-source-out ablation. The
genuine-judgment residual = raw gain − max(shuffled-label gain, format-only gain,
base-rate-only gain).

**Phase 4 — Held-out generalization.**
Two disjoint test sets: (i) entity-disjoint (held-out problem/task-family, same
domain/relation distribution as train), (ii) relation/domain-disjoint (held-out
problem TYPE never seen in train, mirroring the 148-L design). Report AUC and the
genuine-judgment residual on both, separately.

## Controls
- Shuffled-label control (Phase 1 and 3) — floor for "no real signal."
- Format-stripped control (Phase 3) — isolates format-following.
- Outcome-base-rate-only control (Phase 3) — isolates the prior.
- Heuristic-floor control (Phase 1) — the judge must beat this, not chance.
- GroupKFold split by task/problem-family id (Phases 2 and 4) — blocks entity leakage,
  same mechanism as the leakage-gate precedent's task-grouped split.
- Two-sided leakage read on any auxiliary/metadata features included in the prompt: an
  adversary trained only on those features, scored against its own permutation null,
  must not exceed p95 in EITHER direction (below-null excursions are read as leakage
  too, per the PREREG two-sided ruling, not discarded as "unexplained").

## Confound defenses
- **Fabricated-residue confound (C-55004a4674b8):** any record whose "prior attempt"
  content cannot be traced to a genuine ok-status prepass/execution row is excluded from
  training and test, not imputed. Audited in Phase 0, re-spot-checked on a random 5% of
  the final training set.
- **Truncation/parse-fail confound:** any attempt record that is truncated or fails to
  parse is scored as a defect and excluded, not silently coerced to a score (per the
  fleet's standing truncation-can-flatter-a-gate finding) — direction of the confound
  relative to the primary gate is checked explicitly before Phase 4 is read.
- **Memorization-of-constants confound (148-L):** decomposition (Phase 3) plus the
  relation/domain-disjoint split (Phase 4-ii) exist specifically to catch this; a PASS
  on Phase 4-i alone is not sufficient and will not be reported as generalization.
- **Small-n retention/eviction indistinguishability:** if the audited archive (Phase 0)
  yields fewer than ~500 usable triples per class, the experiment is downgraded to a
  PILOT and no significance claim is made (matching this fleet's small-n caution
  elsewhere in the archive-quality literature).
- **Causal overreach guard (D6A null):** results are reported strictly as "this model's
  judgment on this task distribution changed," never as "archived attempt history
  causes better findability" in general — that broader causal claim was tested and
  failed elsewhere in this fleet and is out of scope here.

## Preregistered falsifiers (numeric thresholds)
1. **Archive gate (Phase 0):** if fewer than 3 independent sources each yield ≥100
   usable triples with a solved:failed ratio between 20:80 and 80:20, the experiment
   HALTS at Phase 0 — reported as an archive-readiness null, not a modeling failure.
2. **Baseline-clearance falsifier:** fine-tuned judge in-distribution AUC must exceed
   max(heuristic-floor AUC, base-model zero-shot AUC, shuffled-label AUC) by ≥0.05,
   with a 95%-CI (bootstrap, 1,000 resamples) excluding 0. Below this: FAIL, "no
   learned judgment signal above the archive's own baselines."
3. **Genuine-judgment falsifier:** the Phase-3 residual (raw gain − max of the three
   decomposition controls) must have a 95% CI excluding 0. If the CI includes 0: FAIL,
   "gain is fully explained by format/prior/memorization" (the 2026-06 outcome,
   replicated).
4. **Entity-disjoint transfer falsifier:** Phase 4-i AUC gain over baselines must
   retain ≥50% of the in-distribution gain (Phase 1 vs Phase 2 in-sample). Below: FAIL,
   "gain does not survive entity-disjoint holdout."
5. **Relation/domain-disjoint transfer falsifier (anti-transfer check):** Phase 4-ii AUC
   must be ≥ its own shuffled-label null (one-sided is insufficient here — a below-null
   result is itself a FAIL, per the two-sided leakage-gate precedent). If Phase 4-ii AUC
   is at or below the shuffled null: FAIL, "anti-transfer," reported exactly as 148-L
   was, not softened.
6. **Family-wise correction:** falsifiers 2–5 are a family of 4 primary comparisons;
   Holm correction applied across them before any is reported as a significant PASS.

## Stopping rule
Single decisive run per preregistered split, 5 seeds minimum before any significance
claim is made (per this fleet's standing replicate-seeds rule); no threshold in
falsifiers 1–6 may be moved after Phase 0 or later results are seen. If Phase 0 fails,
the experiment stops and is reported as an archive-readiness finding — Phases 1–4 are
not attempted on a padded or substituted archive. If falsifier 3 fails (no genuine
residual), the experiment stops after Phase 3; Phase 4 is still run and reported (a
transfer test on a judge already shown to be pure memorization is informative about
*how* memorization fails to transfer, and is cheap given Phase 2 is already trained).

## Expected failure modes
1. Phase 0 archive audit fails outright — the only concretely inspected local ledger
   this session (`ergon/probe/ledgers/campaign/campaign_log.jsonl`) contains
   transport/channel events, not attempt-level outcome triples, echoing the exact
   defect class documented for theseus/corpus. This is judged the single most likely
   outcome.
2. Gain replicates the 2026-06 result almost exactly: large raw AUC gain, ~90% of it
   format/prior/memorization, genuine-judgment residual statistically indistinguishable
   from zero.
3. Relation/domain-disjoint holdout reverses to anti-transfer (148-L pattern).
4. Archive turns out small enough (Phase 0 gate 1) that the whole exercise downgrades
   to an underpowered pilot.
5. Heuristic floor (a trivial success-rate-by-method feature) beats the fine-tuned
   judge outright, as the coprime-to-30 heuristic beat a real solver in this fleet's
   own recent history.

## Compute estimate
Base model ≤4B params (candidate: Qwen2.5-Math-1.5B-Instruct, already local at
`E:/hf_cache/hub`), LoRA rank 16, 1 epoch per the 2026-06 precedent, on the RTX 5060 Ti
(measured local VRAM ceiling ~3–4B). No API calls required for training (local only,
$0); zero-shot baseline judgment calls also run locally. Estimate: Phase 0 audit ~1–2
hours of scripted extraction/validation; Phase 2 training ~30–90 minutes per seed at
this scale; Phase 3 decomposition reuses the same trained checkpoint (no retrain, just
re-scoring against controls) except for the format-stripped/base-rate-only arms, which
are separate small fine-tunes at the same cost as Phase 2 — budget ~5 training runs
total (main + 3 decomposition controls + 1 replicate-seed check before the 5-seed
significance pass) at ≤90 min each, plus scoring. Total wall time: roughly one working
day on the existing local hardware, $0 marginal spend.

## Prior evidence that materially changed this design (or 'none found')
- `stations/M1_STATUS.md` and `techne/ARSENAL_SCAN_2026-08-21.md`: fixed the concrete
  compute envelope (RTX 5060 Ti, ~3–4B local VRAM ceiling, Qwen2.5-Math-1.5B-Instruct
  already cached at `E:/hf_cache/hub`) — this is what the Compute estimate and model
  choice are pinned to, rather than an abstract "small model."
- `ergon/probe/PREREG_adversarial_leakage_gate_2026-08-25.md`: supplied the two-sided
  leakage-verdict logic (a below-null excursion is a FAIL too) and the
  positive-control-runs-first discipline, both written into Controls and falsifier 5.
- Direct inspection of `ergon/probe/ledgers/campaign/campaign_log.jsonl` (this session):
  found only transport-level events, not attempt-outcome triples — this is what makes
  Phase 0 a blocking, preregistered gate rather than an assumed precondition, and is
  the basis for judging archive-failure the most likely single outcome (Expected
  failure modes #1).

## Pack items that changed this design (ids -> concrete decision)
- C-d1ce433f289a / C-01f913ae81af -> mandated Phase 3's exact decomposition battery
  (shuffled-label, format-stripped, base-rate-only, leave-one-source-out) and
  falsifier 3 (genuine-judgment residual CI must exclude 0), because this fleet's own
  prior fine-tune-a-judge experiment on adjacent data showed a raw gain that was ~90%
  non-reasoning.
- C-f1d363ff01e4 -> set the positive-precedent ceiling ("near-perfect out-of-sample
  boundary recovery is achievable from failure evidence alone when the archive has
  clean state/outcome structure") and its scope limit (bounded, not repaired, at the
  task level) informs why Phase 0 explicitly checks for clean (context, method,
  outcome) structure rather than assuming it.
- C-b2cebe551f3b / C-94fc12c3e6af -> decided that Phase 0/2 features must be
  behavioral attempt/outcome traces, not semantic/concept metadata, since metadata
  carried zero routing signal over popularity in this fleet's own prior test while
  behavioral collaborative signal did.
- C-e5e726a050c1 -> added the relation/domain-disjoint split (Phase 4-ii) and
  falsifier 5 as a mandatory anti-transfer check, distinct from and in addition to
  entity-disjoint holdout, because an in-distribution positive result in this fleet
  previously reversed to anti-transfer at held-out relations.
- C-55004a4674b8 -> added the fabricated-residue confound defense (exclude, never
  impute, any record without a traceable genuine prior row) and Phase 0's
  refuse-don't-render rule.
- C-dc484d4cf977 -> directly motivated Phase 0 as a blocking gate with a numeric
  minimum-triples-per-source threshold (falsifier 1), because a structurally similar
  archive in this fleet was closed for navigation when none of 8 generators yielded a
  usable (state, action, outcome) triple; this session's own ledger check reproduced
  the same defect class in a different artifact.
- C-aba202675bd8 -> added the causal-overreach guard in Confound defenses, restricting
  all claims to "this model's judgment changed" and excluding any general causal claim
  about archived history improving findability, since that broader claim was
  preregistered and tested to a clean null elsewhere in this fleet.
- C-82fe472469ca -> added the heuristic-floor baseline (Phase 1) and falsifier 2's
  requirement that the judge beat the heuristic floor, not just chance, since a
  trivial heuristic in this fleet's own recent history beat a real solver.

## Operation log (numbered; ops used / 15, documents opened / 12)
1. Read `F:\Prometheus\evidence_wiki\v2\packs\V2-T08_pack.json` — free of budget per task
   instructions; loaded all 10 pack items.
2. Grep (files_with_matches) `VRAM ceiling|3-4B|7B OOMs` over `F:\Prometheus` — located
   candidate compute-constraint docs.
3. Grep (files_with_matches) `solved and failed attempt|attempt record|prior-attempt
   residue|solve matrix` over `F:\Prometheus` — located candidate archive-schema docs;
   several hits resolved under `evidence_wiki\` and were excluded per rules.
4. Read `F:\Prometheus\docs\TASK_CORPUS_V2.md` — errored: path resolved under
   `evidence_wiki\docs\`, off-limits; not read, no content used.
5. Read `F:\Prometheus\ergon\probe\PREREG_adversarial_leakage_gate_2026-08-25.md` — full
   read; supplied the two-sided leakage-verdict and positive-control-first methodology.
6. Grep (content, -C2) `VRAM|OOMs|3-4B|7B` in
   `F:\Prometheus\techne\ARSENAL_SCAN_2026-08-21.md` — confirmed 3–4B local VRAM ceiling
   and prover-model exclusion rationale.
7. Grep (content) `attempt|solve|fail` in
   `F:\Prometheus\engine\queues\BACKCORPUS_MINING.jsonl` — found small-model eval
   profile entry (Phi-4-mini/Qwen2.5-Math/Llemma), not otherwise used.
8. Glob `ergon/probe/ledgers/**/*.json*` — no matches (pattern/path mismatch); superseded
   by direct git-status-listed paths.
9. Read `F:\Prometheus\stations\M1_STATUS.md` (limit 80 lines) — confirmed compute
   envelope (RTX 5060 Ti, ~3–4B ceiling) and cached local model
   (Qwen2.5-Math-1.5B-Instruct at `E:/hf_cache/hub`).
10. Read `F:\Prometheus\ergon\probe\ledgers\campaign\campaign_log.jsonl` (limit 5 lines)
    — found transport/channel-level events only, not attempt-outcome triples; this
    directly motivated Phase 0 as a blocking gate.

**Ops used: 10 / 15. Distinct documents opened: 5 / 12** (pack read is free and not
counted; op 4 errored before any content was read and is not counted as a document
opened; ops 2, 3, 8 are files_with_matches/no-match searches, not document opens).
