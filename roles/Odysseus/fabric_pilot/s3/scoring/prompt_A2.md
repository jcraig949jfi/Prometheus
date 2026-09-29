You are a blind quality scorer for research reports about the Prometheus research repository. You receive several
reports, each labelled X###. They come from different sources, and you do not know which. Score each report
independently against the rubric below. Do not try to find out where a report came from: do NOT search the
repository for a report's own sentences, title or label. Only verify the evidence its claims cite.

Tools: Read, Grep and Glob inside the repository, and `rogit` for git history (a single command, used exactly like
git).

Rubric (frozen, S3_PROTOCOL s5). Score each item 0, 1 or 2:
1. EVIDENCE: are the load-bearing claims tied to checkable primary evidence (path:line, commit:path, data)?
   0 = mostly unsupported, 1 = partly, 2 = consistently.
2. CORRECTNESS: pick the 3 highest-stakes claims and verify them in the repository yourself.
   0 = a load-bearing claim is false, 1 = unverifiable or partly true, 2 = all 3 verified true.
   Name the 3 claims and what you found.
3. ANSWERS THE QUESTION: does it answer what it set out to answer, or state precisely why it could not?
   0 = no, 1 = partly, 2 = yes.
4. LIMITS STATED: does it say what was not checked and what would change the conclusion?
   0 = no, 1 = partly, 2 = yes.
5. USABLE: could a research principal act on it without redoing the work?
   0 = no, 1 = with significant rework, 2 = yes.

Write `scores.json` in your output directory:
{"<label>": {"evidence": n, "correctness": n, "answers": n, "limits": n, "usable": n, "total": n,
             "checked_claims": ["claim -> verified/false/unverifiable, with path:line"], "notes": "one or two sentences"},
 ...}
Finish with one line per report: `<label>: <total>/10`.


---------------- THE REPORTS ----------------


======== REPORT X006 ========

# REPORT

## 1. WHAT I SET OUT TO TEST

The program has three connected proposals that were never started. (a) A "reversible
core" experiment: an agent whose update is a bijection, whose state is bounded and which
receives fresh input, must push one item per step out through a priced export channel.
Does it learn to export irrelevant state, compared with random export (and FIFO export)
at a matched elimination curve? (b) A distinction-survival assay: which input distinctions
survive in a system's accessible state, with counter-keyed RNG and a matched blind control.
(c) A common replay-and-perturb hook with full-state hashes (RNG included). No reversible
agent substrate exists on any host, so within this budget I built the smallest honest one
myself and used it to answer the design question behind (a), and to calibrate the parts of
(b) and (c) that can be checked on a toy: does the experiment as specified discriminate
anything, and do the proposed controls and fixtures behave as the stewards expected?

## 2. WHAT I DID

Inputs: only the design memo, falsifier table and M2 attack notes (read, not run) at
repo origin/main 6ff2b2f8a (memo first committed at d50103524). No engine code was run;
I did not archive or execute repository code. All code is new, under
[redacted]
- revcore.py (sha256 27cff279...): bounded reversible agent. K=8 slots; each step one new
  item (value bit, tag bit, birth stamp) arrives; the policy picks one of the K+1
  candidates and swaps it onto an export tape (outside the boundary, never read back).
  Latent relevance rel~Bern(0.25) is generator-side; tag = rel with prob (1+rho)/2.
  Competence = recall of target weight held (accuracy = 0.5 + 0.5*recall), queried every
  step after t=100 of N=400. Two regimes: "decorr" (target uniform over all relevant items
  so far: relevance independent of age by construction) and "coupled" (target weight
  exp(-age/16): relevance correlated with recency). RNG is counter-based splitmix keyed by
  (seed, t, site, purpose), with a "seq" option (sequential stream whose tie-break draw
  count depends on state) for the cheat fixture. Includes an explicit inverse and a
  full-state SHA-256 (slots + RNG counter/key + clock).
- [redacted].py: inverse run from final state + tape back to the empty initial state
  (64 episodes x 400 steps): exact. Replay to t=200 gives identical full-state hashes in
  both RNG modes; a perturbation at t=150 changes the hash.
- experiment.py (sha256 4eb9181c...): per (regime, rho in {0,.1,.25,.5,1}): learn a
  3-weight linear export score (tag, age/K, tag*age/K) by cross-entropy ES (12 gens x 16,
  256 training seeds); evaluate on 2000 held-out seeds with common random numbers:
  learned, random, FIFO, blind_matched (the learned policy fed an independent tag with
  the same marginal: relevance-blind, same dynamics), planted (export lowest tag; positive
  control). Equivalence margin = 95th pct |random - random| over 10 independently keyed
  pairs on 512 dev seeds; verdicts by 90% CI (TOST) against that margin. Merge-time curve =
  distribution of residence time at export (KS distance reported).
- dsa.py (sha256 bac18a34...): paired runs (2000 pairs) differing only in one item born at
  t*=200 (value flip = inert distinction; tag flip = dynamics-relevant distinction);
  fraction of pairs whose accessible state still differs at t*+h, stratified by that
  item's generator relevance; random vs tag-selective export; keyed vs sequential RNG.
Commands: python3 [redacted].py; python3 experiment.py (outputs experiment.log,
out_experiment.json); python3 dsa.py (dsa.log, out_dsa.json). A first experiment run
(experiment_v1.log, out_experiment_v1.json) scaled age by N; that made the age feature
too small for the learner to use (it could not rediscover FIFO in the coupled regime,
learned 0.297 vs FIFO 0.368 on training seeds). I fixed the scaling to age/K and reran; v2
is reported. The decorr results are unchanged between versions.

## 3. RESULT

Reversible core (recall; margin decorr 0.0005, coupled 0.0036; CI = 90%):

  regime   rho  I(tag;rel)  learned random fifo  blindM planted  learned-random (verdict)      learned-blindM (verdict)
  decorr   0    0.000       .0370   .0369  .0369 .0363  .0370    +.0001 [-.0006,.0008] UNRESOLVED +.0007 UNRESOLVED
  decorr   .1   0.005       .0429   .0369  .0369 .0369  .0429    +.0060 SELECTIVE             +.0060 SELECTIVE
  decorr   .5   0.143       .0745   .0369  .0369 .0370  .0745    +.0375 SELECTIVE             +.0375 SELECTIVE
  decorr   1    0.811       .1501   .0369  .0369 .0364  .1501    +.113  SELECTIVE             +.114  SELECTIVE
  coupled  0    0.000       .3676   .3090  .3676 .3676  .2301    +.0586 SELECTIVE (false)     .0000 EQUIVALENT
  coupled  .1   0.005       .3745   .3090  .3676 .3577  .2601    +.0655 SELECTIVE             +.0168 SELECTIVE
  coupled  .25  0.034       .4147   .3090  .3676 .3231  .3090    +.106  SELECTIVE             +.092  SELECTIVE
  coupled  1    0.811       .8505   .3090  .3676 .2073  .6307    +.542  SELECTIVE             +.643  SELECTIVE

- Export rate is identical for every policy (exactly 1 item/step) by conservation; it
  needs no matching. The merge-time (residence) curves are NOT matched by random export
  (KS learned vs random 0.17-0.83) but are matched by blind_matched (KS <= 0.001).
- The outcome is set by the generator: whenever the observable features carry any
  information about future relevance (even 0.005 bits/item), the learned exporter beats
  random far beyond dev noise. With zero information (decorr, rho=0) every policy is
  identical in expectation; the "random = learned" reading then comes out EQUIVALENT or
  UNRESOLVED depending only on how noisy the arbitrary learned weights are (v1:
  EQUIVALENT; v2: UNRESOLVED, CI half-width just above the margin).
- Coupled regime, rho=0: the learner rediscovers FIFO. Against RANDOM export it earns a
  large, significant "selective advantage" (+.059) that is pure recency. The
  curve-matched blind control (and FIFO) read EQUIVALENT (0.0000), correctly.
- The planted positive control (tag-only selective policy) FAILS to beat random in the
  coupled regime at rho <= .25 (-.079 at rho=0, 0.000 at .25), because it discards recency.
  A positive control that works in one task can be silent in another.
- blind_matched can be WORSE than random (coupled rho=1: .207 vs .309): holding the
  learner's age profile with blind content is a different, harsher baseline.

Distinction-survival assay on the reversible core (fraction of pairs still differing):
- Keyed RNG: every distinction leaves accessible state once its item is exported (differ
  -> 0.000-0.003 by h=199). In a reversible core "merging" in accessible state is export
  and nothing else; the full state (including the tape) never merges.
- Relevance stratification works on this substrate: rho=1, selective export, inert (value)
  flip: relevant items differ 0.906/0.743/0.349/0.027 at h=0/8/32/128, irrelevant items
  0.000 at all h; random export shows no strata difference (0.131 vs 0.129 at h=16).
- Cheat fixture reproduced: with a sequential RNG whose draw count depends on ties, a
  tag flip leaves 49% (rho=0) and 67% (rho=1) of pairs NEVER reconverging at h=199,
  versus 0.0% and 0.3% with keyed RNG. The inert value flip is immune (does not change
  draw counts). The contamination starts at once (h=1: 0.96 seq vs 0.85 keyed).
- Pair-type matters: tag flips (which change how the item is treated) erase the relevance
  strata (rel .743 vs irr .698 at h=8), value flips show them cleanly.
- My own harness bug, fixed before reporting: the first DSA run took the relevance oracle
  from the keyed generator path while the sequential-RNG runs drew items from another
  stream, so the strata were wrong in seq mode. The oracle must come from the same
  generator path as the specimen.

Replay-and-perturb hook: a common interface is small in a toy (replay to t, perturb one
item, full-state hash including RNG counter; bit-identical replays). On origin/main a
term grep found checkpoint state hashes only in SFE (currently down); no cross-engine
replay-and-perturb interface. That was a grep, not a code audit.

## 4. DID IT RESOLVE THE QUESTION

Partly. On the design question behind the reversible-core experiment: yes, at toy scale.
The experiment as specified is mostly decided by construction. A bounded reversible
agent that can learn will export selectively exactly when observable state carries
information about future relevance; the falsifying reading "random export does as well
as learned export" holds exactly when the generator provides none. The quantity that
determines the result, I(observable features at export time; future relevance), is
fixed by whoever designs the task. The real experiment was not built on an engine (no
NPE substrate), and the DSA was not applied to any frozen specimen (PTE, AGE, Z80). The
replay hook was demonstrated only in the toy. Those remain.

## 5. CONSEQUENCES

- False or weak premise: the reversible-core experiment is not a strong attack on the
  "reversible" and "indiscriminate loss" countermodels unless the preregistration (i)
  measures and reports I(features; relevance) per task before the run, (ii) treats a
  "random = learned" result at I=0 as uninformative (decided by the generator, not the
  agent), and (iii) says what it would mean for the law if a learner is selective whenever
  I>0 (which is close to a theorem about learners). Whoever owns the selective-
  irreversibility hypothesis and falsifier table, and the engine seat named to build the
  reversible core, should know.
- Positive result for the stewards' design rules: rate matching is automatic on a
  reversible substrate and random export is NOT curve-matched; the random control issues a
  false selectivity certificate when relevance tracks recency (+.059), while a
  curve-matched blind control (same policy fed a shuffled cue) catches it. The FIFO third
  arm only helps where recency-relevance decorrelation is measured. Recommend the
  shuffled-cue, curve-matched control as the primary blind arm, with random reported too.
- Instrument caution: a planted positive control can be silent when the task has a
  second relevant axis (recency). Positive controls must be validated per task.
- Reproduction of a predicted defect: the sequential-RNG cheat fixture behaves exactly as
  the M2 attack predicted (up to 67% false non-merging). Engines whose RNG streams consume
  state-dependent draw counts must be keyed before any DSA reading.
- DSA on reversible substrates must read export (distinction leaves accessible state), not
  exact merge; the relevance oracle must come from the same generator path as the
  specimen; inert vs dynamics-relevant perturbations give different strata.
- Harness lesson from my own run: feature scaling in the learner (age/N) silently hid a
  whole policy class; a "learned" arm needs a check that it can rediscover known
  baselines (FIFO) before its non-difference is read.

## 6. COST

About 1.5 hours of my time. CPU about 40 minutes total (experiment v1 12 min, v2 20 min,
DSA two runs about 4 min, one accidental duplicate start about 2 min that I killed before
it wrote output, small checks). At most 2 processes of mine at a time, under 150 MB RAM,
CPU only. Not done: an engine-hosted reversible core (NPE), DSA adapters on frozen PTE /
AGE / Z80 specimens, a code audit of each engine's RNG and state for a common replay hook,
a closed-form bound linking advantage to I(tag; rel), and replication over K, p, N and
learner seeds.



======== REPORT X007 ========

# [redacted] / H-D4-20 -- H3: does any archive/QD policy beat top-K on a real stream, and do the descriptors resolve anything?

Read-only analysis of repository commit 5266ccebea3ad5522b7cfa7a07a8718cac113a70. No code was run.
Any figure below not quoted from a committed file is my hand arithmetic on committed per-seed rows,
labelled as such. `out/analysis.py` recomputes it, and its output takes precedence over mine.

## Question

With retention budget held equal, does an archive or quality-diversity (QD) retention policy
(`behavioral` grid, `hybrid`) beat plain top-K / sequential-champion retention on a stream? And
does any declared descriptor pair separate candidates in a way that tells us something?

## Short answer

- **On a real stream: no evidence either way.** The only real stream is cs-c3-2, and it cannot
  answer the question. All 120 acquisition-arm candidates score exactly 0.0. The only
  per-policy scores on it come from query types that the program's own dead-stream control
  ruled unsafe.
- **On the synthetic stream (the dead-stream control v2, the only stream with a planted
  relation): no QD policy beats top_k.** On the live arm, top_k was at least as good as
  `behavioral` and at least as good as `hybrid` on every one of 5 seeds. Hand-computed paired
  means were +1.2 tasks (SE about 0.49) over `behavioral` and +1.4 (SE about 0.68) over
  `hybrid`, out of 12. Neither gap clears a df=4 t-threshold. So the result is "no QD
  advantage", not "top_k proven better". This is consistent with the external prior art
  (Chen 2026, no archive advantage at matched budget).
- **The descriptors resolve occupancy, not the relation.** The v1 equal-mass descriptors spread
  the random arm from 4 cells to 15 of 16. But coverage/occupancy was shown to be identical to
  the cell between a live stream and its score-permuted twin. So the descriptors separate
  candidates by table statistics, and that separation carries no information about which
  candidates are good. No behavioural descriptor has been tried.
- **Status:** the harvest entry's "later evidence: none found" still holds for a real or
  generated beta stream. ARCH-07 is open, TECHNE-03 runs on request only, and C3-3 is
  unissued. It is partly answered by the synthetic control, which the harvest entry quotes
  only for its caveat.

## Method

1. I read the three cited sources in full: the dead-stream readout, Techne's alpha receipt and
   [redacted]'s backlog.
2. I searched the tree at the pinned commit for later H3 work: ARCH-07, H3 beta, TECHNE-03,
   generated stream, the Chen 2026 citation, the sealed future-query scoring (TECHNE-24) and
   C3-3 issuance.
3. I extracted per-seed `family_b_solved` for every policy and arm from the committed v2
   control rows, and formed paired top_k − QD differences by hand.
4. I read the per-policy tallies from the committed TECHNE-24 receipt on the real stream, and
   classified each true answer as a score-threshold query or a cell-occupancy query.

## Evidence

### E1. The real stream cannot discriminate policies

- cs-c3-2 has 150 candidates. **126 of 150 score exactly 0.0, including all 120 random
  rules** (`roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:123-125`).
- Under the v0 descriptors, the 120 random rules fall into four cells
  (`roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:114-119`).
- In the three tie-dominated cells, all 107 candidates are exactly 0.0
  (`roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:135-150`).
- The receipt itself refuses to rank policies
  (`roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:182-187`).
- [redacted]'s verdict says nothing about a real C3/H1 stream: "none exists yet: C3-2's random
  arm was constant zero and C3-3 is unissued"
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:130-131`).
- C3-3 issuance "still waits on the operator's word" as of 2026-09-16
  (`roles/[redacted]/BACKLOG_H0H5.md:51`).

### E2. Real-stream sealed-query scores exist, but only on unsafe query types

The TECHNE-24 receipt scored cs-c3-2 against the 12-query sealed manifest (digest de4cae9b),
and was "SCORED_WITHOUT_RANKING"
(`techne/acquisition/receipts/adapter_qualification-pyribs-20260911T065018Z.json:775,780`;
`roles/Techne/BACKLOG_H0H5.md:34`).

| Policy | True answers (of 9 scorable) | Receipt lines |
|---|---|---|
| top_k | 4 | :309-310 |
| uniform | 6 | :441-442 |
| behavioral | 7 | :573-574 |
| hybrid | 6 | :705-706 |

- Two of the nine are unattainable by any policy (:771-774), which leaves 7 that discriminate.
- The three transfer queries cannot be scored (:776).
- top_k's 4 are all score-threshold queries, and it misses every cell query (:187-280). The
  gap in `behavioral`'s favour is made up entirely of `occupies_cell` answers.
- The dead-stream control ruled exactly these two query families UNSAFE:
  - coverage/occupancy "does not see whether a stream carries a relation";
  - score-threshold reuse "measures the score marginal, not reuse".

  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:50-52,117-124`.)
- So the 7-vs-4 real-stream tally is not evidence that QD beats top_k. It measures the fact
  that a grid archive fills cells. Even `uniform` (6) beats top_k on it.

### E3. The synthetic stream: top_k at least as good as QD on every seed

Setup: 200 candidates, v1 descriptors, 16-item cap, reserve 4, 5 seeds, and 12 hidden 5-bit
tasks sealed before the run. The predictions and the v2 addendum were committed before the
v2 run (`[redacted]/docs/h0h5/H3_DEAD_STREAM_PREDICTION_2026-09-11.md:9-27`;
`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:59-86`).

Means as committed (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:93-97`):

| Policy | family B, live | family B, dead | family B, cheat |
|---|---|---|---|
| top_k | 10.4 | 4.2 | 10.6 |
| uniform | 4.2 | 4.2 | 4.2 |
| behavioral | 9.2 | 4.4 | 10.6 |
| hybrid | 9.0 | 4.0 | 10.2 |

Per-seed live-arm rows (`[redacted]/docs/h0h5/H3_DEAD_STREAM_CONTROL_v2_2026-09-11.json`; the
line numbers are the `family_b_solved` fields):

| Policy | seed 1 | seed 2 | seed 3 | seed 4 | seed 5 | Lines |
|---|---|---|---|---|---|---|
| top_k | 8 | 11 | 10 | 11 | 12 | :51, :317, :583, :849, :1115 |
| behavioral | 7 | 11 | 7 | 10 | 11 | :91, :357, :623, :889, :1155 |
| hybrid | 7 | 11 | 6 | 10 | 11 | :111, :377, :643, :909, :1175 |

Hand arithmetic, to be confirmed by `analysis.py`:

| Paired difference | Per seed | Mean | SE | t | Seeds won / lost |
|---|---|---|---|---|---|
| top_k − behavioral | 1, 0, 3, 1, 1 | +1.2 | ≈0.49 | ≈2.4 | 4 / 0 |
| top_k − hybrid | 1, 0, 4, 1, 1 | +1.4 | ≈0.68 | ≈2.1 | 4 / 0 |

- The critical t at df=4 is 2.78, so neither gap is significant. The exact two-sided sign test
  on 4 wins and 0 losses gives p = 0.125.
- On the cheat arm, top_k and `behavioral` are tied (10.6 vs 10.6).
- The readout says the three score-retaining policies' "differences here are within one SE of
  each other" and makes no ranking claim
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:131-133`). The paired view here
  sharpens that: every seed where the policies differ favours top_k, not QD.
- At the ceiling (v1, 3-bit tasks), top_k was 12.0, `behavioral` 11.8 and `hybrid` 11.8
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:10-13`). No QD advantage there
  either, although the ceiling makes that uninformative.
- Where QD does "win" in v1 is family A (`behavioral` 8.0 vs top_k 6.2), which again includes
  cell-occupancy queries (same lines). That is unsafe by E2.

### E4. What the descriptors resolve

- The v0 equal-width edges put 120 random rules in 4 cells (E1). The v1 equal-mass edges are
  the quartiles of Binomial(128,1/2) × Binomial(64,1/2)
  (`[redacted]/docs/h0h5/H3_DESCRIPTORS_v1.json:12-17,27-31`). On cs-c3-2 they put the random
  arm into **15 of 16 cells** (commit 2baf0680f message: "cells occupied v0: 8 of 16 v1: 15 of
  16; random rules in v0: 4 cells v1: 15 cells").
- The declaration itself says v1 "does not separate rules by behaviour; two tables in one cell
  may compute very different things. A behavioural descriptor is a different experiment and
  would need the C3-3 criterion first"
  (`[redacted]/docs/h0h5/H3_DESCRIPTORS_v1.json:35-36`).
- With v1 edges, coverage was identical between a live stream and its score-permuted twin "to
  the cell ... for every policy, on ten runs"
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:100-101,117-122`). So the
  descriptor separation is orthogonal to the fitness relation.
- On cs-c3-2 the separated random arm is a zero plateau, so no descriptor can make it
  informative for score-based retention.

### E5. Prior art and open work

- Chen 2026 (arXiv:2608.19703, "Loreley") is marked VERIFIED, with the note "the verified
  contrast is at 48" jobs (not 1,008) (`[redacted]/docs/hypotheses/H1/CITATIONS.md:69-72`).
- It is summarised as "NO archive advantage over a sequential champion at matched budgets"
  (`roles/[redacted]/REVIEW_PACKET_2026-09-10.md:260-261`).
- ARCH-07 (the generated 1,024-candidate beta stream with sealed queries) has no completion
  annotation (`roles/[redacted]/BACKLOG_H0H5.md:9`).
- TECHNE-03 (the CVTArchive comparator) is "only when Ludus/[redacted] ask"
  (`roles/Techne/BACKLOG_H0H5.md:13`; `roles/Techne/DONOR_FOUNDRY_CLOSEOUT_2026-09-12.md:125`).
- There are no H3 files under `[redacted]/docs/h0h5/` after 2026-09-11. In the git log, the last
  commit touching the H3 replay, seam or readout is 179cd46e4 / 11730100c, on 2026-09-11.
- A crosswalk entry notes that a QD advantage "cannot appear on onemax" and needs a deceptive
  landscape (`[redacted]/docs/expansion/CROSSWALK.md:720`).

## Result

1. **Does a QD policy beat top-K on a real stream?** Unanswered. It cannot be answered from
   committed content: no informative real stream exists. The one real-stream tally that favours
   `behavioral` (7 vs 4) comes only from cell-occupancy queries, which are certified unsafe.
2. **On a generated or synthetic stream at matched budget?** No. In the only such experiment
   (dead-stream control v2, live arm), neither `behavioral` nor `hybrid` beat top_k on any seed.
   top_k is ahead by +1.2 and +1.4 tasks of 12, and that is not significant at n=5. This agrees
   in direction with Chen 2026.
3. **Do the descriptors resolve anything?**
   - They resolve occupancy: v1 gives 15 of 16 cells for the random arm, against 4 under v0.
   - They do not resolve the organism→score relation: coverage is blind to it.
   - No descriptor pair tested so far separates candidates by behaviour or by stepping-stone
     value.
   - The neutral zero plateau on cs-c3-2 stays invisible to the archive, as the harvest entry
     feared.

## Limits

- The synthetic stream is not deceptive. Its score is agreement with a hidden target on
  random-table tasks, and its descriptors are table statistics unrelated to the target, which
  structurally favours top_k. QD's theoretical advantage (stepping stones on deceptive
  landscapes) was never put to the test.
- The control was designed as a dead-stream instrument check, not a policy comparison. The
  paired statistics here are post hoc, and n=5 seeds.
- Only direct reuse was measured, with no adaptation or search from the archive
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:133-134`). That is the setting
  where archive stepping stones would matter.
- On seed 1 of the synthetic run, `behavioral` and `hybrid` retain 16 items, like top_k (JSON
  `retained_n`), so the budget is matched on items. I did not read the other seeds' counts.
  Byte caps never bound (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:91`).
- The pinned tree may lack uncommitted or unmerged work, for example on other branches. I did
  not search all branches for ARCH-07 output.

## What would change the conclusion

- An ARCH-07-style generated stream with a policy-independent generator and queries sealed
  first, on which `behavioral` or `hybrid` beats top_k on family-B-type (task-level reuse)
  queries with paired t > 2.78. That would overturn "no QD advantage".
- A deceptive-landscape stream (a planted stepping-stone relation) where top_k's retained set
  cannot reach the high-value region. This is the first test that could favour QD at all.
- A behavioural descriptor (for example the C3-3 cellwise criterion) under which live and dead
  coverage *differ*. That would show descriptors resolving the relation.
- C3-3 issued with a non-constant acquisition arm, giving a real stream with score variance.
- If `analysis.py` shows my per-seed extraction is wrong (for example, if top_k − behavioral
  is negative on any seed), claim C3 must be revised.



======== REPORT X008 ========

# [redacted] [redacted] -- Recombinant continuity: C-OP', per-unit ancestry (ARG), the privileged-operator null, FLOW vs DIFFERENCE

[redacted]
was run. Paths without a commit prefix are at HEAD.

## 1. Question
The harvest entries (H-D1-07, H-D1-08, H-D2-14, H-D2-15, H-D2-37) ask five things:
1. Does the E-002 rule C-OP' hold outside PTE?
2. What is the null for a privileged (asymmetric) recombination operator?
3. Should material contribution be counted by FLOW or by DIFFERENCE?
4. Should the lineage contract replace a singular parent with graded per-unit (ARG-style) ancestry plus a declared convention?
5. Does label-based "descent" count as heredity?

## 2. Method
- I read the E-002 record (RESULT.md, T-007_CRITERION.md, T-008_T-011_RESULTS.md).
- I read the deep-block review files (A_E002_REVIEW.md, B_B1_B6_B8.md, G_PRIOR_ART.md) and Block A's attack script
  (cop_prime_attack.py).
- I read the later Attribution v0 campaign: the spec, schema.py, the assay and the packet.
- I traced the history with `rogit log` and `rogit branch --contains`.
- I did not run any code. The one computation that would tighten the result is written as out/analysis.py, and its output is not
  stated here.

**Provenance correction to the harvest:** the harvest says the deep block (72923db05) is "Not merged" / "unmerged". At HEAD it is
merged. `rogit branch -a --contains 72923db05` lists `remotes/origin/main` and the current HEAD, and the files are at
ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/. Being merged does not make it adopted: Block A still marks its narrowed rule
"proposed, not adopted" (A_E002_REVIEW.md:36).

## 3. Evidence

### 3.1 C-OP' as proposed
- The proposal (RESULT.md:42-45) is:
  * collapse identical contributors and exclude inert units;
  * lift ILL_POSED only when the difference-making share clears the declared operator null at a declared alpha;
  * "NOT adopted, and NOT tested outside PTE". The alpha is "a free choice" (0.005 suggested, not tuned).
- Clause (b) is defined only for an exchangeable operator, "Binomial(n, 1/2)" (RESULT.md:28-29).
- For a privileged operator, C-OP falls back to C-MAJ (T-007_CRITERION.md:28, :36; T-008_T-011_RESULTS.md:13).

### 3.2 C-OP' attacked and narrowed (Block A, now on main)
Block A (A_E002_REVIEW.md) implemented the rule in [redacted]/causal_lens/deep_block/cop_prime_attack.py. It found:
- **E1b** (A_E002_REVIEW.md:23): a child byte-identical to a, from parents that differ at 3 units, is called **ILL_POSED**. With
  nd = 3 no child can clear alpha. The real GA crossovers had nd = 10-28.
- **E4** (:26): 15/16 units flow from b, but the only distinguishing unit comes from a. The child is byte-identical to a.
  DIFFERENCE says a, FLOW says b, and C-OP' says ILL_POSED.
- **E5** (:27): 75-81% of the distinguishing units come from a, and the child is still ILL_POSED "purely by a significance
  convention".
- **E7** (:29): the phenotype is exactly a's while the material share is 4/16 from a. Clause (a) is ambiguous between MATERIAL
  difference and EFFECT difference.
- **E3/E3b** (:25): the privileged case is "unaddressed". Under a 90%-a operator a 14/16 child is typical, yet it is extreme under
  the unbiased null.
- **Root defect** (:31-34): clause (b) tests one realized operator draw. That asks whether the operator was biased, which is a
  population question, not a per-child fact. "Nearly every PTE recombinant has no singular parent" therefore "restates the chosen
  alpha".
- **Narrowed version** (:36-43):
  * keep self-cross collapse and NOT_IDENTIFIABLE;
  * report the DIFFERENCE and FLOW shares separately as graded quantities;
  * make a singular label a declared convention on the difference share (>= 1 - eps), not a significance test;
  * "operator symmetry ... cannot make a realized child's content ill-posed";
  * report MATERIAL and EFFECT separately.
- Status line (:46-47): C-OP' is "operator-specific in (b) and wrong at close relatives". The narrowed version is "tested only on
  synthetic units here and on PTE by the worker".

### 3.3 FLOW vs DIFFERENCE
- E-002 (RESULT.md:69-73) makes three points:
  * FLOW = which source the operator copied a unit from; DIFFERENCE = which source's distinguishing material the child carries;
  * the FF-33 "correction" swapped one referent for the other and fixed no error;
  * NPE v0.2 uses DIFFERENCE.
- Block B (B_B1_B6_B8.md:32-39) answers "No as a distinction; yes as a lesson":
  * FLOW = IBD; DIFFERENCE = IBS at informative units;
  * "continuity/identity questions about CONTENT use DIFFERENCE; genealogy questions use FLOW";
  * do not open B8.
- Block A agrees that FLOW answers ARE facts about genealogy, not about distinguishing content (A_E002_REVIEW.md:57-58).
- Block G maps the pair onto IBD/IBS and calls it a rediscovery (G_PRIOR_ART.md:8). The ARG row is at :9, and the challenge to C-OP' at :28.
- Minor inconsistency: B_B1_B6_B8.md:28 describes clause (b) as testing a "per-child FLOW-share". But C-OP' and
  cop_prime_attack.py count k over differing units only, which is the DIFFERENCE share (cop_prime_attack.py:21, :25). The defect
  Block B identifies (per-child share vs population null) holds either way.

### 3.4 What the later campaign actually shipped (Attribution v0, on main)
- Terminology ([redacted]/attribution/ATTRIBUTION_V0.md:192-194):
  * "FLOW -> identity by descent (IBD); FLOW retired";
  * "RESEMBLANCE / DIFFERENCE -> IBS; informative sites; retired";
  * "per-unit lineage / B1 -> local ancestry, ARG". v0 records local ancestry but builds no ARG.
- Record shape: there is no parent field (ATTRIBUTION_V0.md:54). A1 rejects parent/ancestor/template keys outside aggregation
  (schema.py:54-55).
- A singular parent_id appears only as an aggregation label under rule SINGULAR_MATERIAL_PARENT. It is allowed only when one donor
  supplies >= 0.75 of the child's units AND no other donor supplies >= 0.10, which is "a declared convention"
  (ATTRIBUTION_V0.md:52; schema.py:65-66, 134-139; validator A11 at schema.py:283-291).
- The shares are IBD (FLOW) shares over ALL child units (schema.py:88-95, `donors`). They are not DIFFERENCE shares over
  informative units.
- Self-cross collapse is built in: two segments from one entity count as one donor (schema.py:89). A15 says a recombinant needs
  >= 2 distinct donors (ATTRIBUTION_V0.md:110).
- The rule has no operator-null or significance clause anywhere in v0 (schema.py:134-139).
- Second-substrate use: the assay applies the convention to [redacted] block 13 (53,185 events, native per-byte taint):
  * two or more donors in 3.3%;
  * a singular parent loses identified structure in 4.9%;
  * the other engines are "not identifiable" (ASSAY.md:23-29).
  * BEE and NPE preserved records carry no per-byte descent, and NPE's z8taint tracks the executing code (ASSAY.md:49-55).
  * Recombinant births in block 13 are 0.07% (440/655,307) (ITEM8_RESULT.md:53; ATTRIBUTION_PACKET.md:307).
- Regression cases "organism recombination, [redacted], 2 donors" and "EXTERNAL crossover, BEE" are synthetic event shapes checked by
  A11 (ATTRIBUTION_PACKET.md:216-217). The packet notes this "does NOT show v0 would have caught the errors from the data available
  at the time" (:221-222).
- Status: "attribution v0 BUILT and TESTED; two adversarial reviews". Reproduction definitions are "NOT frozen"
  (ATTRIBUTION_PACKET.md:5; ATTRIBUTION_V0.md:123).

### 3.5 Privileged operator (F2)
- E-002 found no thin-margin case in Git:
  * [redacted]'s 15 two-source events are >= 27/32;
  * NPE is decided only at donor share >= 0.906;
  * the full distributions sit on M2, not in Git (T-008_T-011_RESULTS.md:60-66).
- Block A leaves F2 "Unresolved" (A_E002_REVIEW.md:70).
- v0 sidesteps the null entirely with an operator-independent convention.
- I found no committed null for a privileged operator.

### 3.6 Label descent vs content (H-D2-37)
- [redacted], roles/[redacted]/FINDINGS.md:360-366 at HEAD (the harvest cites :362 at 345e0ceef): in anc-descended NPE runaways only 13-25% of bytes are founder
  material (z8taint). "Every 'founder-descended' statement above ... is lineage descent, not content inheritance".
- v0 answers this in form. Validator A8 says "a descent label needs a material donor ... (IBS is not IBD)" (ATTRIBUTION_V0.md:103).
- The assay then shows NPE's preserved record cannot supply material donors (ASSAY.md:25, :53). No material-share endpoint rule
  for NPE heredity claims has been adopted.

## 4. Result

| sub-question | answer from committed content | confidence |
|---|---|---|
| 1. Does C-OP' hold beyond PTE? | **No; it is superseded, not extended.** Its clause (b) fails on synthetic counter-cases that are substrate-neutral (E1b, E4, E5). The failure is structural: a per-child label is tested against a population null. No second substrate has ever tested C-OP'. The later v0 instrument drops clause (b) and keeps clause (1) (self-cross collapse) and NOT_IDENTIFIABLE | high that it is superseded in the committed record; C-OP' is formally neither adopted nor rejected by a contract revision |
| 2. Null for a privileged operator? | **Unanswered, and on the record's own logic the wrong question for a per-child label.** Block A says operator symmetry or asymmetry cannot make a realized child's content ill-posed; an operator null answers "is the operator biased" (a population question). v0 uses an operator-independent convention. A privileged-operator null (Binomial(nd, p_a)) is only meaningful for auditing the operator, and the data for that ([redacted]/BEE margins) are on M2 | medium: this is a reviewer argument plus a design choice, not an empirical result |
| 3. FLOW vs DIFFERENCE? | **Both, for different questions:** genealogy uses FLOW = IBD; content/identity uses DIFFERENCE = IBS at informative sites (Block B, Block G). v0 adopts the IBD/IBS vocabulary. **Open tension:** v0's only shipped singular-parent convention is defined on the IBD (FLOW) share over all units. So for a content question it gives the genealogy answer. Reading schema.py:134-139, E4 (child byte-identical to a, 15/16 flow from b) gets parent_id = b (0.9375 >= 0.75; 0.0625 < 0.10), where Block A's narrowed DIFFERENCE rule gives a. v0 has no DIFFERENCE-based aggregation rule | high for the division of labour; high for the tension (plain threshold arithmetic, confirmable with analysis.py) |
| 4. Graded per-unit ancestry + declared convention? | **Yes, and it is implemented in v0 for [redacted]:** per-locus IBD segments, no parent field, and parent_id only as a declared convention (0.75/0.10). No ARG is built. It "behaves" in [redacted] block 13 (3.3% multi-donor, 4.9% lossy singular parent). It is **not testable** in NPE splice cells or BEE from preserved records, because those have no per-byte descent. It has not been tested on [redacted] RECOMBINATION births specifically (0.07% of births) | medium-high |
| 5. Label descent as heredity? | **No, not without material.** The v0 validator requires a material donor for descent labels (A8). NPE's founder-descended claims are lineage-label claims ([redacted]). A cross-engine material-share endpoint is not adopted, and NPE cannot currently supply it | medium-high |

**Bottom line:** in the committed record, the singular lineage of a recombinant is an aggregation over per-unit ancestry. It must name
its referent and a declared convention; an operator-null significance test does not decide it. C-OP' clause (b) is rejected on
review. Two things remain open:
1. v0's convention is on FLOW (IBD), so the "CONTENT uses DIFFERENCE" half of Block B is not implemented.
2. The privileged-operator null and any practitioner-accepted convention remain unaddressed.

## 5. Limits
- No code was run. All numbers are quoted from committed files.
- The E4 v0 verdict in section 4 is my reading of schema.py thresholds applied to Block A's case. It is not an executed output
  (analysis.py would confirm it).
- Block A's counter-cases are synthetic (16 abstract units). Block A's narrowed rule was reviewed by no second party I could find.
- v0's 0.75/0.10 thresholds are declared, not justified. Nothing in Git calibrates them against practitioner use.
- The F2 data (the [redacted] 53,185-event margins and BEE's per-birth margins) are on M2 and not in Git (T-008_T-011_RESULTS.md:65).
- I did not search other seats' unmerged branches exhaustively. The one I checked ([redacted]/e003) has nothing beyond HEAD.

## 6. What would change the conclusion
- **A contract revision** adopting C-OP' clause (b), or a v1 aggregation rule defined on DIFFERENCE shares, would change answers 1
  and 3.
- **Running out/analysis.py:**
  * if v0 returns `b` on E4 while the DIFFERENCE convention returns `a`, the FLOW/DIFFERENCE tension in v0 is confirmed;
  * if it returns `a`, my reading of schema.py is wrong and the tension claim should be withdrawn.
  * For E3b, compare p under p_a = 0.5 with p under p_a = 0.9. A large p under 0.9 and a small p under 0.5 shows the privileged null
    only relocates the question to operator bias.
- **F2 margins from M2:**
  * if [redacted] or BEE privileged-operator events cluster near the 0.75/0.10 boundary, the choice of convention becomes
    outcome-determining for establishment counts;
  * if they stay >= 27/32 as in the 200-event sample, F2 is empirically moot there.
- **A per-byte material-taint replay for NPE** (T-003 births) or BEE, as recommended in ASSAY.md:56, would make the per-unit
  convention testable in a second and third engine, including NPE splice cells.



======== REPORT X009 ========

# Report: why non-additive task families never qualify in the G4 foundry

## 1. WHAT I SET OUT TO TEST

[redacted]'s second recursion-campaign execution (commit 4f937e88f, branch
origin/[redacted]/a16-campaign-2026-09-26) got a valid "no" on bounded recursive
self-improvement. The seat itself put a caveat on that answer: the catalog could only
contain additive and subtractive folds, which is exactly the ground the inherited
abstraction already covers. In both catalogs the mul, mod and powr strata accepted 0 of
32 draws each, and fdiv and gcd accepted almost none. The report blamed a sampler
"dominated by degenerate draws" and proposed a new sampler that excludes degenerate
witnesses. I tested whether that diagnosis is right. The question was whether
non-additive families fail because the sampler draws degenerate witnesses (such as
division by constant 0 or pow with a non-positive base), or because of a real property
of the task space and the qualification instrument. The answer decides whether a
cleaner sampler could ever supply the non-additive families that a meaningful
recursion test needs.

## 2. WHAT I DID

Inputs, all committed at 4f937e88f and exported with `git archive` into
work/[redacted]/src:
- roles/[redacted]/engine/A17_DRAWS_2026-09-26.json (the drawn catalogs A and B)
- roles/[redacted]/engine/A17_FOUNDRY_EVALS_2026-09-26.jsonl (verdicts for all 416
  evaluated draws: [redacted] size, [redacted] result, [redacted] pilot)
- the code in a17.py, meta_tribunal.py, basis_v4.py, engine.py and tier3e.py

Scripts are in work/[redacted]/analysis/, with outputs next to them:
- **join.py** joins each draw to its verdict and gives the stage where it was rejected
  (rows.json). It reproduces the report's totals exactly: 151 rejected at [redacted], 233 at [redacted]
  and 12 at [redacted].
- **diag.py** takes each of the 416 draws, builds the TRUE witness artifact exactly as
  a17.job_q23 does (emitter 2), and re-scores it with the real MetaTribunal. I call the
  tribunal's input sets "batteries". It also records:
  - the fraction of tribunal instances whose gold is "None" (overflow above 1e40, or an
    exception);
  - whether the witness is invariant under the tribunal's own permutation probes;
  - the number of distinct outputs and the dependence on the input values at search
    lengths;
  - a counterfactual score in which gold "None" counts as matched by the artifact's
    "overflow" or None.

  Output: diag.json, summarised by tab.py into tab.txt.
- **census.py, core_census.py and sens.py** make an exhaustive census of the G4 fold
  space in the form a17.draws samples it: every init in H1_SPACE times every body with
  the given top operator that mentions both acc and v. That is 424 (init, body) cores
  per stratum, and 27,136 programs per stratum once finals are included. They use fixed
  batteries that copy the tribunal's distributions:
  - 150 held-out instances of length 20-60;
  - 40 stress instances of length 200;
  - 40 counterexamples of length 2, 3, 80 or 150, with m in {1, 2, 3..97};
  - 25 permutation pairs.

  Each core is classified as:
  - **admissible:** defined on at least 99% of each battery, and defined and invariant
    on all permutation probes;
  - **non-degenerate:** strong means at least 10 distinct accumulator values and at
    least 20% dependence on the values after the first; weak means at least 2 and 5%;
  - **novel:** its accumulator behaviour is not identical to any add or sub core.

  sens.py repeats the census with the overflow requirement relaxed, the
  order-invariance requirement relaxed, and both relaxed (sens.txt).

Everything was run with
`env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE python3 <script>`, with 2 worker
processes.

## 3. RESULT

**A. The stratum gap is created almost entirely at [redacted], the hostile tribunal applied to
the TRUE witness.** It is not created at [redacted], the identifiability check where degenerate
draws fail.

| Stratum | Pass [redacted] | Pass [redacted] given [redacted] |
|---------|---------|------------------|
| add     | 29/42   | 11/29            |
| sub     | 43/54   | 13/43            |
| mul     | 42/64   | 1/42             |
| fdiv    | 49/64   | 2/49             |
| mod     | 37/64   | 1/37             |
| gcd     | 26/64   | 3/26             |
| powr    | 39/64   | 1/39             |

The [redacted] failures are the low-information draws: median 1-2 distinct outputs in mul, powr,
add and sub. They occur at similar rates in add and sub. I re-scored [redacted] on every draw
that passed [redacted] and got the same verdict every time (0 mismatches).

**B. Why the true witness fails [redacted], among draws that passed [redacted] and failed [redacted]:**

| Stratum | Undefined only | Order-dependent only | Both |
|---------|----------------|----------------------|------|
| mul     | 21             | 3                    | 17   |
| powr    | 0              | 0                    | 38   |
| fdiv    | 0              | 14                   | 33   |
| mod     | 0              | 11                   | 25   |
| gcd     | 1              | 16                   | 6    |

"Undefined" means the gold is None on more than 1% of instances in some battery. Real
product and power folds are necessarily undefined at the tribunal's lengths: with
values of 2-30, a product passes 1e40 after about 30-130 elements. For mul, the median
share of stress instances that are undefined is 100%. In fdiv and mod, "undefined" is
mostly division by zero once the accumulator reaches 0. "Order-dependent" means the
tribunal's metamorphic check fails. Its docstring assumes that "every declared body is
commutative-associative over the sequence", but the G4 sampler does not impose that, so
the check filters out almost every sequential mod, fdiv or pow fold.

**C. An instrument defect on top of this.** On any instance where the true value
overflows or raises, the gold is str(None) = "None". The emitter-2 artifact returns
"overflow" there, or None on an exception. So the TRUE witness is scored wrong on
instances it gets right by construction:
- 223 of 416 true witnesses score below 0.99 on some accuracy battery.
- With that encoding repaired, all 416 score 1.00. The encoding is the only difference
  between witness and gold.
- The repair alone would lift [redacted] passes for mul from 1 to 22, add from 11 to 15, sub
  from 13 to 18 and gcd from 3 to 4. It would not change fdiv, mod or powr.
- The 21 extra mul families would be families whose answer is "overflow" on 50-100% of
  stress instances, so the repair does not produce useful families.

**D. Exhaustive census of the whole grammar (sens.txt), under the current strict
tribunal:**
- Admissible, strongly non-degenerate cores: 6 in mul, 0 in fdiv, 2 in mod, 7 in gcd and
  0 in powr. In add and sub the counts are 152 and 100.
- Of the 15 non-additive-stratum cores, 12 behave exactly like an add or sub core. An
  example is (1 * (acc + v)). The novel behaviours that remain number 0 in mul, fdiv, mod
  and powr, and 2 in gcd: gcd over (first % v), and gcd(last, product of v).
- With the weak threshold, the novel behaviours are 0 in mul, 1 in fdiv, 2 in mod, 9 in
  gcd and 11 in powr. Almost all of them are 0/1-valued predicates, for example
  "some v shares a factor with last" or "some exponent was 0".

Relaxing the tribunal opens the space. Counts are distinct strongly-novel behaviours:

| Tribunal setting | mul | fdiv | mod | gcd | powr |
|------------------|-----|------|-----|-----|------|
| Current (strict) | 0   | 0    | 0   | 2   | 0    |
| Overflow accepted as an answer | 16 | 0 | 0 | 2 | 0 |
| Order-invariance dropped | 13 | 20 | 25 | 47 | 7 |
| Both relaxed | 61 | 20 | 25 | 47 | 13 |

**E. The only non-additive draws that passed [redacted] and [redacted] are degenerate or additive in
disguise, or they are gcd or predicate families.**
- Rejected at [redacted] as too easy (PRISTINE 16/16):
  - (1 * (v + acc)), which is a sum;
  - gcd(0, acc + v), also a sum;
  - 1 % gcd(...), which is constant;
  - pow(v, 0 - acc), which only depends on the last v;
  - v // (acc + v).
- Accepted:
  - gcd(last, v * acc);
  - gcd(acc, first % v);
  - acc // gcd(v, last), a predicate.

**Plain conclusion:** mul, mod and powr go to 0 because of how the task space and the
tribunal fit together, not because of degenerate witnesses:
- The tribunal demands totality under a 1e40 ceiling at length 200, and invariance to
  the order of every element after the first.
- In this grammar almost no non-additive fold meets both demands without collapsing
  into something additive or trivial. Growth folds overflow. Sequential mod, fdiv and
  pow folds depend on order or divide by zero.

A sampler that only excludes degenerate witnesses would, by this census, still find
0-2 genuinely new qualifiable behaviours per non-additive stratum, nearly all of them
gcd.

## 4. DID IT RESOLVE THE QUESTION

**Yes, for the question actually posed:** was it degenerate witnesses or a real property
of the task space?
- The mechanism is identified per draw, and it is reproduced exactly with the seat's own
  tribunal code.
- The census covers the entire sampled grammar, not just the 416 draws.

**Only partly for the question behind it:** can an inherited abstraction derive
something new when the task supply contains families it does not explain? That needs
a new catalog and a donor assay, which is out of scope and would need a new preregistration.

Caveats:
- The census uses batteries with fixed seeds that copy the tribunal's distributions, not
  the per-family tribunal seeds. The per-draw part uses the real ones.
- "Novel" means not behaviourally identical to an add or sub core on about 150 probe
  inputs. It is not a semantic proof.
- [redacted] and [redacted] were not applied in the census, so the census gives upper bounds on what
  could qualify.

## 5. CONSEQUENCES

- **False premise.** The explanation "the sampler is dominated by degenerate draws" is
  right about [redacted] but not about the gap between strata. The proposed repair, a sampler
  that excludes degenerate witnesses, would not supply mul, mod, fdiv or powr families.
  It should not be preregistered on the expectation that it would.
- **Instrument defect.** In the tribunal (meta_tribunal.py together with
  basis_v4.run_program and the gold construction), gold "None" never matches the
  artifact's "overflow" or None. The TRUE witness is therefore marked wrong on
  instances it gets right. This affects 223 of 416 draws. It is small in effect on
  qualification, but it is a real mismatch between the emitter and the gold, and it
  should be fixed or explicitly declared.
- **Design constraint to surface.** The metamorphic check assumes bodies are
  commutative-associative. The G4 sampler does not impose that, so the tribunal quietly
  restricts the catalog to order-invariant folds. The stress lengths together with the
  1e40 ceiling exclude every growth fold. Either the tribunal must change (drop or
  condition the permutation check, use length regimes suited to each operator, treat
  "overflow" as an answer), or the grammar must (bounded operators such as max, min or
  a modulus applied at the top level, or bodies whose modulus is on the left). Without
  one of these, no non-additive supply is possible.
- **Labelling issue.** The stratum is taken from the body's top operator, which does not
  match the semantics. (1 * (acc + v)) counts as "mul". A real "sum mod m" family lives
  in the "add" stratum through the final (acc % last).
- **Who should know:** the [redacted] seat (foundry and tribunal owner) and whoever
  decides on the next recursion prereg. The recursion "no" should be kept explicitly
  conditional: with this instrument, a treatment-blind catalog cannot contain a
  non-additive family at all, apart from a handful of gcd or predicate folds.

## 6. COST

- About 50 minutes of my own time.
- About 11 CPU-minutes in total, never more than 2 processes, under 100 MB of RAM.
- I did not rerun [redacted] or [redacted] on counterfactual draws, build a new catalog, or run any
  donor assay. Those would need a new preregistration and more budget.
- No sealed data or holdout was touched, and nothing was written to the repository.



======== REPORT X010 ========

# [redacted] [redacted]: Reanalyses that need no new compute (Atlas RA-1..RA-5)

[redacted]
Every path below is at that commit unless another sha is given. No code was executed.

## 1. Question

Harvest entry H-D1-51 (roles/[redacted]/backlog/harvest/D1_program.md:473-480) says Atlas's five "reanalyses that need no new
compute" are an unfollowed recommendation ("none run"). The [redacted] asks for them to be answered from committed repository
content. That breaks into three parts:

- **(Q-a) Status.** Were RA-1..RA-5 run, in name or in substance?
- **(Q-b) Feasibility.** Can each be answered from committed files alone, as the harvest's "repo-only science" framing claims?
- **(Q-c) Answers.** Where committed evidence already answers part of a question, what is the answer?

The five records are at roles/Atlas/proposals/2026-09-21_prior_art_raid/EXPERIMENTS.jsonl:30-34:
- **RA-1:** did queue pools act as a curriculum?
- **RA-2:** learned descriptors over GraphWorld and CW01. The harvest omits it, but the [redacted] title covers it.
- **RA-3:** evaluator-exploitation census.
- **RA-4:** Crius PARTS takeovers as cross-niche recombination.
- **RA-5:** rediscovery rate across seats.

## 2. Method

1. Read the five records and their status everywhere they are cited: the Atlas journal, backlog, STATUS, roadmaps and prompts; the Techne journal; the [redacted] threads.
2. Searched commit messages on all refs (`rogit log --all --grep`) for RA-n or reanalysis.
3. For each RA, found where its named inputs live. I read the Atlas harvesters to tell whether an input is a committed file or a row in the uncommitted M1 Postgres `atlas` schema.
4. Three read-only search sweeps (sub-agents) covered: (i) committed exploit-shaped events and their catchers; (ii) committed cross-seat convergence and rediscovery documents plus the Nyx and Techne inventories; (iii) committed frontier-queue and Crius C2 data.
5. I re-verified the load-bearing lines myself: the [redacted] report in full, the FAILURE_PRINCIPLES s4 table, the [redacted] verdict, the Crius C2 disposition, the scheduler code and the WSE/Eos/Nemesis/ASAL lines. Sub-agent rows I did not re-open are marked MEDIUM confidence in [redacted].
6. Where a question needs computation over committed data (RA-1, RA-4), I wrote it as `out/analysis.py`, with decision rules fixed in advance. I did not run it.

## 3. Evidence and results

### 3.0 Status and a quote correction (Q-a)

- **The quote behind "RA-1/RA-3 need nothing" is truncated.** The source says RA-1/RA-3 "need nothing *from Techne*" (roles/Techne/journal/2026-09-25_gandalf-a04f7c25_RESET.md:91-92; also roles/Atlas/prompts/2026-09-21_to_techne/TO_TECHNE.md:19: "they run over the Atlas index"). It is a statement about donor dependencies, not about compute or data.
- **Atlas designed the RAs to run over its Postgres index, which is not in git.** The schema `atlas` lives on the M1 store (atlas/README.md:3-5; atlas/db.py:1-7,27-29), and the only committed Atlas data file is atlas/registry.json. So the counts quoted in the records cannot be recomputed from git: "442 queue items, 22 RUN attempts, 1,196 detector_firing facts" (EXPERIMENTS.jsonl:30), "218 defects, 610 control facts" (:32), and "atlas.conclusion (468), mechanism_claim facts (99)" (:34).
- **Atlas could not run them anyway.** The Atlas seat is PARKED (roles/Atlas/STATUS.md:7, :58 "REPORTS ONLY"), and its own journal says "Crius and the Nyx mechanism ledger are not yet indexed, so RA-4 and RA-5 cannot run today" (roles/Atlas/journal/2026-09-21.md:41-42). The index extensions ATLAS-34/35/36 are still open (roles/Atlas/BACKLOG_H0H5.md:27-29; atlas/registry.json:256).
- **Only RA-2 and RA-4 rank in the policy layer.** They appear in Atlas's ROADMAP top-15 (roles/Atlas/reports/ROADMAP_2026-09-25.txt:118,123). RA-1, RA-3 and RA-5 do not.
- **"None run" is true under the Atlas names but stale in substance.**
  - [redacted] [redacted] [redacted] (roles/[redacted]/[redacted]/runs/[redacted]/REPORT.md, committed by 7e1ca095d/088608cdf on 2026-09-28) ran an RA-3-equivalent census.
  - [redacted] FAILURE_PRINCIPLES s4 (roles/[redacted]/challenge/FAILURE_PRINCIPLES.md:797-898, d5241a102, 2026-09-28) and [redacted] (roles/[redacted]/[redacted]/runs/[redacted]/REPORT.md:222-235) did partial RA-5 work, with independence coding.
  - None of these three cite "RA-3" or "RA-5".
- **Name collision.** The commits "RA-1 INDETERMINATE" (d51d1fa82) and "RA-1 preregistration" (9c1badfba) are Herakles's own RA-1/RA-2 (herakles/specimens/spec-toussaint-exploration/reanalysis/...). They are unrelated to Atlas RA-1.

### 3.1 RA-1: queue pools as curriculum

**Feasibility: YES from git, with gaps.** Atlas's frontier harvester reads committed files (atlas/harvest/frontier.py:39, `ls_tree(ref, "[redacted]/frontier")`). The per-chunk detector counts behind the 1,196 detector_firing facts come instead from host-only receipts (atlas/harvest/frontier_runs_m2.py:3-6,205-210; RUN_HOST "M2"). The data committed @5266ccebe:

- **Queue rows** carrying pool, lane, priority, budget and state: [redacted]/frontier/queues/{EXPLORATION,EXPLOITATION,AUDIT}.jsonl (414/144/134 lines, append-only snapshots). REVISIT.jsonl is git-ignored ([redacted]/frontier/.gitignore:3).
- **Events:** [redacted]/frontier/registry/EVENTS.jsonl holds 130 RUN events (my count) and 129 OBSERVATION events whose text carries per-run firings, written at scheduler.py:385. The format is, for example, EVENTS.jsonl:12793 "B-scatter.T000.d_seed: 2 chunks, 9984 evaluations, firings {...}". It also holds 299,991 BLOCKED_BY_SUPPRESSION rows, which are a logging defect ([redacted]/frontier/scheduler.py:269-271; roles/Atlas/journal/2026-09-25.md:29-36) and must be dropped.
- **Pool outcomes at epoch 2026-09-21T2054Z** ([redacted]/frontier/digests/EPOCH_2026-09-21T2054Z.json:49-105; RUN = 119 at :18):

  | pool | done | pending | dropped |
  |---|---|---|---|
  | EXPLORATION | 50 | 202 | 25 |
  | EXPLOITATION | 36 | 12 | 5 |
  | AUDIT | 21 | 40 | 3 |
  | REVISIT | 12 | 1 | 0 |

**Design finding that changes the reading (new; not in the RA-1 record).** Pool assignment is partly a function of prior firings and of lineage mode:

- `descendants()` enqueues the seed/initialization controls of a depth-0 run into AUDIT only when an ADMITTED detector fired on that run (scheduler.py:181-200; ADMITTED at :178).
- Items seeded by `ingest` get their pool from the lineage's mode ([redacted]/frontier/ingest.py:120).
- The scheduler chooses a pool by share deficit (`choose_pool`, scheduler.py:239-248), not by item merit.

So an unstratified pool-vs-firing association is expected by construction, and is not evidence of a curriculum. The proposal's time-window permutation null (EXPERIMENTS.jsonl:30 anticheat) does not remove this. A within-lineage null and exclusion of scheduler-spawned controls are needed; both are in analysis.py.

A second confound: firing thresholds were calibrated on v0 populations, and graph populations fire "two orders of magnitude fewer" (EPOCH_2026-09-21T2054Z.json:46). Firing rate therefore partly tracks the substrate profile, which is itself lineage-bound.

**Answer: not yet computed.** The analysis.py `ra1` decision rule:
- **Ineligible** if fewer than 2 pools have at least 10 joined runs.
- **"Curriculum-shaped association"** only if the within-lineage permutation p < 0.05 and the effect survives excluding `branch: control` items.
- **"Composition, not curriculum"** if only the global null rejects.

REVISIT runs cannot be joined, because their queue file is not committed.

### 3.2 RA-2: learned descriptors (included because the [redacted] title says RA-1..RA-5)

Not repo-only in practice. It is NEEDS_DONOR, needs the ATLAS-07 row/cell harvest and a descriptor pipeline (EXPERIMENTS.jsonl:31; BACKLOG_H0H5.md:29, ATLAS-36 open), and is "S" compute, not zero. No committed run was found. Not pursued further.

### 3.3 RA-3: evaluator-exploitation census

**Already done in substance.** [redacted] [redacted] (roles/[redacted]/[redacted]/runs/[redacted]/REPORT.md, repo @6ff2b2f8a) used RA-3's own event definition (:30-31) and read every roles/*/calibration ledger (:29). Its results:

- **Size:** "38 recorded events across about 20 seats and engines" (:120).
- **By class** (:121-122): 21 found by selection/search, 11 instrument/analyst bugs, 5 human-built trivial baselines passing, 1 mixed.
- **Caught by:** "mostly null, shuffled or cheat controls, then human reading and adversarial review. A second independent evaluator caught one, and it was the planted case" (:123-124).
- **Latency:** usually within the same campaign. The outliers were caught 6 weeks to about 5 months late: Nemesis about 162 days, Eos about 163 days, [redacted] about 6 weeks, Hephaestus months (:125-127).
- **Rate:** "the repository cannot yield a rate because it does not record its denominators" (:175-176; also :138-139).
- **Limit:** only the summary is committed. The per-row table stayed in scratch (:23). RA-3's own anticheat, a hand-labelled sample to measure classifier error (EXPERIMENTS.jsonl:32), was not done. [redacted] says so itself: "the remaining census rows rest on a single read" (:232-234).

**Independent re-census (this attempt, one reader, not hand-validated).** A separate sweep reconstructed 38 events with citations, listed in [redacted] C-RA3-*. My tally by primary catcher:

| caught by (primary or co-primary) | events |
|---|---|
| cheat control or exploit probe | about 13 |
| null, shuffled or held-out control | about 11 |
| human reading or self-audit | about 11 |
| external review or second evaluator | about 5 |
| positive control as sole catcher | 0 |

**The RA-3 claim under test is SUPPORTED on the recorded frame, weakly.** The claim is "cheat controls, not positive controls or human reading, caught most exploitation". Controls of some kind (cheat plus null) caught roughly 24 of 38. Positive controls caught none alone. But human reading is not a minor catcher (about 11), and cheat controls alone are not a majority.

Two observations, both from single-read coding:
1. **The long-latency catches all come from human, external or audit catches, never from a cheat control:** Nemesis constant string, 0.674, "292 of 294 tools score below it" (roles/Nemesis/CALIBRATION.md:16); Eos CHEAT 100/100 (roles/Eos/CALIBRATION.md:118-121); [redacted] R6 answer key; Hephaestus constant floor (roles/Hephaestus/journal/2026-09-19.md:163).
2. **In at least two events a preregistered null control missed the exploit:**
   - WSE W8: "The null battery ... could not see a one-tick-lag echo, so the leak passed the s5 gate" ([redacted]/wse/READOUT_v01.md:111-112).
   - [redacted] WTP-01: the shuffled control hit 0-2 of 5, so the ARTIFACT rule did not fire ([redacted]/ENSORAIN_WTP01_REPORT.md:50-63, sub-agent citation).

**Where denominators exist, exploitation is common** ([redacted]:128-133):
- ASAL: 49 of 105 threshold-crossers were METRIC_EXPLOIT (roles/[redacted]/rulings/RULING_ASAL_LEGIT_SEARCH_001_2026-09-18.md:69).
- Crius: abstention in 6/6 C0 runs.
- WSE: 1 of 18 cells.
- [redacted]: 0/90 probes became dominant.

**Denominator and category problems:**
- The Atlas "218 defects" come from two harvested sources only: [redacted] campaign ledgers (atlas/harvest/archaeon_campaigns.py) and NPE CW01 DEFECTS.jsonl, whose 92 rows are the only ones with a `found_by` field (atlas/harvest/npe.py:514-538).
- These are defects, not exploits. FR-057 makes the same point: "These are defects, not reversals" (roles/[redacted]/backlog/threads/FR-057.md:46-48).
- The roughly 45 calibration ledgers that hold most exploit events are not harvested.
- Category vocabularies differ per seat, and `caught_by` is rarely a field.

### 3.4 RA-4: Crius PARTS takeovers

**Feasibility: YES from git. The prerequisite is now met.** The record required "Crius C2 arm complete" (EXPERIMENTS.jsonl:33). The arm is complete: crius/runs/C2_TERMINAL_DISPOSITION.md:95 `R5_survives false`, :103 `"CLOSED -- ACCESSIBILITY FRONTIER MAPPED"`. All 36 runs' takeovers.jsonl and candidates.jsonl.gz are committed under crius/runs/search_c2{a..d}_{arm}_s{1..3}/ (sub-agent listing). ATLAS-34 is still open (atlas/registry.json:256), but the Atlas index is not needed.

**Committed partial answer (PART donors only, rung d)** from C2_TERMINAL_DISPOSITION.md:54,63,79:

| run | P_INV | P_PLAN | P_REC | PART-child takeover rate |
|---|---|---|---|---|
| c2d recombination s1 | 15/203 | 7/197 | 10/182 | 32/582 = 5.5% |
| c2d recombination s2 | 9/189 | 8/194 | 8/209 | 25/592 = 4.2% |
| c2d recombination [redacted] | 1/205 | 4/195 | 1/197 | 6/597 = 1.0% |

The per-run totals and percentages are my arithmetic from those lines. **No committed comparison with population-donor (ELITE) or self-splice children exists**, so RA-4's primary endpoint is not yet answered.

Three facts bound what it could show:
1. **Takeovers of PART children are mostly selectively neutral.** The top lineages' PART takeovers carry paired fitness deltas of about +0.0005 and solved delta 0 (C2_TERMINAL_DISPOSITION.md:55-57,65-69). Takeover rate is therefore a weak proxy for "selective value".
2. **The donor type is confounded with everything else.** PART donors exist only at rung d. They descend from P_BASE, not from the population's ENUMERATE_VM seed, and sit at fixed structural distances from it (sub-agent: crius/DESIGN_C2.md:104-110,228-231; C2_SUMMARY.md:116-119). So donor class, rung, ancestry and distance move together. Only within-rung-d contrasts are interpretable.
3. **The population donor pool includes the parent itself** (crius/search.py:312-315). "Within-lineage" therefore has to be split into SELF vs ELITE.

analysis.py `ra4` does this, with a within-(run, iteration) permutation null that respects Crius's common-random streams (search.py:321-326).

### 3.5 RA-5: rediscovery rate across seats

**Feasibility as specified: NO.** Both named inventories record outside mechanisms harvested by a single seat, with no discovering-seat field:
- Nyx MECHANISMS.json: 6 entries, `source_lineage` = external origin (nyx/atlas/gates/MECHANISMS.json).
- Techne CATALOG: 121 fossils, no seat/author field (techne/fossils/CATALOG.json).

Seat-level rediscovery is 0 by construction in those files. The Atlas mechanism_claim/conclusion rows are uncommitted.

**Partial answer already committed (failure-principle unit, not mechanism unit).** FAILURE_PRINCIPLES s4 (roles/[redacted]/challenge/FAILURE_PRINCIPLES.md:797-898):
- It counts a structure as rediscovered when "at least two catalogues reach the same mechanism from different evidence" (:799-800).
- It codes evidence independence as IND/SP/SS (:761-766).
- Result: five of 15 principles (P01, P04, P07, P13, P08) are found by all three catalogues on at least partly independent evidence (:840-842).
- [redacted]'s June Failure-Primitive Atlas: "three of four fossil classes recurred in September engines, and every recurrence was rediscovered without citation" (:895-896). FP-001, FP-003 and FP-004 recur uncited; FP-002 does not (:867-893).

**Independence is weaker than "rediscovery" suggests.** [redacted] tested the Z80 "three engines" recurrences and found "Survives in 2 or more engines with its factor removed: none ... They are not three independent sightings of a law" (roles/[redacted]/[redacted]/runs/[redacted]/REPORT.md:230-235). The three builds came from one directive and one paper (:234).

**Participant-written convergence lists** (selected, not a rate; sub-agent citations, MEDIUM):
- Herakles CROSS_SEAT_META_ANALYSIS_2026-09-04.txt:13, "SIX convergences", with "None cites the others" at :133.
- Elenchus CROSS_SEAT_COMPARISON.md:23-30, the 16-minute opposite finding.
- [redacted] CROSSWALK.md:102-103, "existence is not accessibility -- found three times without citation".
- Hermes CONVERGENCE_PROBE_2026-09-11.md:49-81, ops defects hit by 5-7 seats uncited.

**Result for RA-5.** No rate over a defined denominator exists or can be formed from committed inventories.

What the committed record does show:
- Rediscovery of failure classes happens.
- It happens mostly **without citation**. That is the transmission failure RA-5's secondary endpoint asks about ("whether the later one cited the earlier").
- Apparent cross-engine recurrence within one directive/model/day cohort does not survive a factor-removal test.

That mix is two different things. For the "convergence the operator fears" (H-D1-51), the committed evidence says the September recurrences are shared-design echoes. It does not say they are independent convergence. The robust rediscoveries are across eras (June [redacted] vs September engines).

## 4. Result (summary)

| RA | Run under this name? | Answerable from git? | Committed answer |
|---|---|---|---|
| RA-1 | No | Yes, from queues + EVENTS.jsonl; REVISIT missing | None. Pool is endogenous to firings and lineage, so a naive association would be an artefact. analysis.py `ra1` decides it. |
| RA-2 | No | No (donor + pipeline + ATLAS-07) | None |
| RA-3 | In substance ([redacted] [redacted]) | Yes, as a census; No as a rate | 38 events. Controls (cheat + null) catch most; positive controls catch none alone; human reading is significant and owns the long-latency catches; a rate is impossible because exploit-free runs are unrecorded. |
| RA-4 | No | Yes (C2 complete, all files committed) | PART-child takeover 1.0-5.5% per seed, with no ELITE/SELF comparator yet; takeovers near-neutral; donor type confounded with rung and ancestry. analysis.py `ra4` decides the within-rung contrast. |
| RA-5 | Partially (FAILURE_PRINCIPLES s4, [redacted]) | No for mechanisms; partly for failure classes | Failure-class rediscovery is common and uncited across eras. Within-cohort "independent" recurrence does not survive factor removal. No rate. |

Overall, H-D1-51's framing is half right:
- RA-1 and RA-4 really are no-compute and repo-only (a short stdlib pass).
- RA-3 and RA-5 are already partly answered by [redacted]'s 09-28 work, and their "rate" forms are unanswerable from the repo because the denominators (exploit-free runs; a seat-attributed mechanism inventory) are not recorded.
- "RA-1/RA-3 need nothing" was misquoted: they needed nothing *from Techne*, but did need the uncommitted Atlas index.

## 5. Limits

- No code was run. The RA-1 and RA-4 numbers are not computed, and analysis.py is untested.
- The RA-3 re-census and the RA-5 convergence list were assembled by one reader via sub-agent sweeps. I re-opened the load-bearing rows only (see [redacted] confidence). There is no inter-rater check, and exploit-vs-bug classification is subjective.
- Only recorded events are visible. Undetected exploits and uncited convergences that nobody noticed are missing by construction.
- [redacted] [redacted]'s per-row table is not committed, so my 38 cannot be matched row-for-row to its 38.
- I could not see the Atlas Postgres counts (442/22/1,196; 218/610; 468/99), so I cannot confirm them or reconcile them to git.

## 6. What would change the conclusion

- **RA-1:** a within-lineage permutation p < 0.05 that survives excluding scheduler-spawned controls would move it from "no evidence" to "association". Committing REVISIT.jsonl would add a pool.
- **RA-4:** if PART takeover rate exceeds ELITE rate within (run, iteration) in at least 2/3 seeds, it provisionally supports donor splices beating within-population variation (still confounded with ancestry). Otherwise QD-9 needs a prospective design.
- **RA-3:**
  - Committing [redacted]'s row table, or two-coder labelling of 30 rows with kappa of at least 0.6, would firm up the catcher split.
  - Per-campaign records of "runs with a cheat control" and "exploit-free runs" ([redacted]:209-212) would allow a rate.
  - A finding that the long-latency catches had cheat controls available but unused would sharpen the doctrine claim.
- **RA-5:**
  - A seat-attributed inventory (ATLAS-35 with a discoverer field) plus a labelled dedup sample would allow a rate.
  - Finding cross-seat recurrences that survive [redacted]-style factor removal within a cohort would overturn "shared-design echo".

