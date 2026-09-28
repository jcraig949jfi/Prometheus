# W-F PLAN  T-CT-1 carrier census over all C1 SIGNAL cells

Written 2026-09-27 BEFORE any census run. Thresholds, classes, features and
the decision rule below are frozen; they will not change after results.
Worker W-F, analysis namespace 0x5EA: seeds = assays.world_seeds(0x5EA, 64),
64 worlds = 32 mirror pairs, 99% pair bootstrap (lens.ci). Brief:
threads/T-CT-1_carrier_census.md. Rules: handoffs/COMMON_RULES.md.
Instrument: lens.carrier_table (INSTRUMENT_CARRIER_SWAP.md, F1-F6).

## Question
For every C1 champion that reached SIGNAL, where does the task bit sit at
mid-interval (site state, channel, jointly, elsewhere), and is the carrier
class predicted better by physics dials than by the task family?

## Specimens
All rows of roles/Ananke/pte/c1_rows/cells.jsonl.gz with kind == "evolve"
and result.held.lo99 > 0.55. Pre-count (read from the rows, no simulation):
166 cells (HOLD 97, RELAY 50, MAJ 19; waves A 41, B 75, B2 25, C 5, D 15,
E 5). Genome = result.champion (c1b_run.load semantics); physics and env as
stored (env variant as stored).

## Probe ticks
One mid-interval tick per trial, from c1b.ticks(env)["mid"] (the frozen
helper): HOLD t0 + cue_len + gap//2; RELAY/MAJ t0 + cue_len +
max(1, (delta - cue_len)//2). The swap is applied after that tick in EVERY
trial; accuracy over all scored trials (as in the pilot spikes/s_ct.py).
NOTE: the pilot used t0 + max(1, delta//2) for non-HOLD, which is up to 1
tick earlier; the 12 D-wave cells are a consistency check, not a replicate.
Secondary ticks (reported, NOT used for the class):
- late = ro - 1 (c1b.ticks "late"), site_all and channel_all only (F2
  handoff check).
- pre-cue = t0 - 1 for trials k >= 1, site_all and channel_all only (F6
  history control: must not FLIP).

## Arms (carrier_table, device cuda)
normal, site_all, channel_all, channel_content, channel_count, pay<k> for
every payload component, w. Joint arm (site_all + channel_all together,
F1: sanity only) run when NEITHER site_all NOR channel_all FLIPs.
Every arm records verdict, acc ci and arm_identical (F4).

## Carrier classes (from the mid-tick verdicts; frozen)
UNREADABLE  normal lo99 < 0.60 (weak champion; not classified)
SITE        site_all FLIP, channel_all not FLIP
CHANNEL     channel_all FLIP, site_all not FLIP
DUAL        both FLIP (should be rare; possible only if either copy is
            sufficient, i.e. the other is overwritten)
JOINT       neither FLIPs, joint arm FLIPs (sub-tag JOINT-SPLIT if both
            singles CHANCE, JOINT-ASYM otherwise)
ELSEWHERE   neither single nor joint FLIPs (bit not in these arrays at the
            probe tick: schedule/sensor latch, in transit, or F6 history)
Qualifiers (reported, do not change the class):
- F4: a class-defining NO-EFFECT with arm_identical=True is tagged TRIVIAL.
- F6: pre-cue swap FLIP on the class-defining arm -> tag HISTORY.
- F2: late-tick class differs from mid-tick class -> tag HANDOFF.
Channel sub-reading: which pay<k> FLIPs; channel_count FLIP means count
coding.

## Features (physics dials; encoding frozen)
Primary set = the 8 dials named in the brief:
  decay     = 0 if decay_shift == 0 else 2**-decay_shift   (S -= S>>k)
  loss      = physics.loss
  async     = update_mode == "async"
  lat_base  = physics.lat_base
  capinv    = 0 if cap == 0 else 1/cap                       (strictness)
  fanout    = physics.fanout
  pw        = payload_width
  wimm      = physics.wimm
Secondary 6-dial set for logistic regression: decay, loss, async, lat_base,
capinv, wimm (standardised).

## Models and decision rule (frozen)
Target: carrier class of READABLE cells (not UNREADABLE). Classes with < 5
cells are merged into OTHER before fitting.
Physics model (primary): DecisionTreeClassifier(max_depth=2,
  random_state=0) on the 8 primary dials.
Family-only baseline: predict the training-fold majority class per family.
CV: 20 repeats of stratified 5-fold (KFold if a class has < 5 after
  merge), seeds 0..19; mean accuracy per model; the gain's 95% spread over
  repeats reported.
Also reported (not decisional): logistic regression (C=1, multinomial) on
the 6-dial set; tree on dials + family one-hot; overall majority baseline.
DECISION: "physics selects the carrier" iff mean CV acc(tree, physics) -
  mean CV acc(family-only) >= 0.10; otherwise "family selects".
Eligibility guards (declared before data):
- If < 30 cells are READABLE: INCONCLUSIVE (too few).
- If the most common class covers >= 0.90 of readable cells the gain
  cannot reach 0.10 by construction: report "carrier near-uniform; the
  decision is not informative" alongside the rule's formal output.
- Physics and family are confounded by wave design; the tree+family model
  is reported so a gain can be attributed.

## Predictions (before data)
P1 HOLD: SITE dominant (pilot 4/4). RELAY and MAJ: mixed, CHANNEL most
   common. So family-only already strong (~0.75+).
P2 decay > 0 favours CHANNEL (site memory leaks); larger lat_base favours
   CHANNEL (bits live longer in flight).
P3 Expected outcome: "family selects" (gain < 0.10), ~65% confidence.
P4 UNREADABLE fraction ~25% (many held acc 0.6-0.7).

## Budget and compute
~13-15 runs per cell, ~166 cells. GPU lease (lease.py, owner W-F) with ttl
sized from a 1-cell smoke timing; results checkpointed per cell to
out/census.jsonl so a crash or lease expiry resumes. If BUSY: QUEUE.md +
CPU subset with torch.set_num_threads(2).
Deliverables: out/census.jsonl, out/census_table.csv, out/model.json,
REPORT.md, BACKLOG_T-CT-1_UPDATE.md (proposed backlog text; Ananke applies
it, since workers write only in their own directory).
