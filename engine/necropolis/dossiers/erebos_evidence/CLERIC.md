# CLERIC -- grave EREBOS (Necropolis first native trial, Rhadamanthus, 2026-09-11)

Role: challenge both the original experiment and the Necromancer. Write scope: this file
plus `cleric_lift_only_calibration.py` / `cleric_lift_only_calibration_result.json`
beside it. Nothing else in the tree was written by the Cleric.

Root for every path below: the worktree `Prometheus-worktrees/rhadamanthus-base-role`
(branch `rhadamanthus/native-trial-2026-09-11`). Dossier examined:
`engine/necropolis/dossiers/erebos.dossier.json` (evidence_baseline
e17934d9a82855b6e0ae1c0bf54c0cce569b7795; the tree at HEAD cc7afb99e also carries the
Keeper's `_keeper_evidence/` and `DEFECTS.md`, which the Necromancer did not have).

Method: every Necromancer script was copied to scratch (so its result file could not
overwrite the Necromancer's), its `REPO = HERE.parents[3]` line replaced by an env-var
root, and re-executed offline from the worktree. `git` was used read-only
(log/show/grep). `validate.py` was never run in the worktree. No database, no network.

Executed re-runs vs the Necromancer's committed result files:

| artefact | Necromancer | Cleric re-run | match |
|---|---|---|---|
| `erebos_seam_census_result.json` | 25 plugins, 11 quarantined, 29 loaders imported, 0 import failures, find_loader 14/25, loader_keys_not_emitted [], control False | identical | yes |
| `erebos_null_instrument_calibration_result.json` | NULL obs [0,0,0] p95 [1,1,1] p [1,1,1]; PLANTED obs [0,1,0] p [1.0,0.345,1.0]; detected 0/3 | identical | yes |
| `erebos_history_census_result.json` | 39 commits 05-26..06-03; 19 loader commits; max ITER 84; ITER-100 named 5x as future | identical | yes |
| `erebos_tests_offline_result.json` | 608 passed / 1 skipped; 59; 146; total 813 | identical | yes |
| `erebos_consumer_audit_rerun_result.json` | 16 fields, 14 with consumers, zero-use information_gain_nats, reuse_value_count | byte-identical | yes |
| `erebos_external_refs_result.json` | A 3 / A2 14 / B 198 | A 4 / A2 19 / B 207 | no (see C-9) |

sha256 of the Necromancer's originals were recorded before any re-run; none changed.


## 1 WHAT THE NECROMANCER CLAIMS

Quoted from `erebos.dossier.json` (`autopsy.*`). Non-ASCII characters in the source are
shown as `?`.

Stack:

- HYPOTHESIS VALID, cause_classes [], load_bearing false: "Two hypotheses sit under one
  agent_id. H-A (Layer 1): composing existing Stygian/Pollux/Hecate verdicts into new
  falsifiable claims yields claims the falsifier can verdict. H-B (Layer 2): a
  kill_tensor + cross-cell motif + routing substrate adds measurable value over a
  Layer-1-only baseline (pre-committed test at ITER-100). Neither was refuted on the
  record: H-A was exercised (14/25 plugins reached a loader; PROMOTED/REJECTED/UNVERIFIED
  verdicts by ITER-5, later self-reclassified to catalog/substrate tier); H-B's pair-aware
  claim was reported STATISTICALLY UNDERDETERMINED and its triplet sub-claim FALSIFIED, and
  the ITER-100 test was never run (max ITER-84). Not a HYPOTHESIS_FAILURE on this record;
  also not a confirmation."
- DESIGN VALID, [], false: "The design pre-committed its own kill (ITER-100
  Layer-2-vs-Layer-1; Sprint-1 rule >=4/10 fails -> PAUSED), capped loader debt with an
  explicit quarantine (the 11 loaderless plugins are exactly the 11 quarantined), and
  shaped its queue rows to the loader contract. Two design weaknesses are recorded but not
  found load-bearing: (i) two hypotheses share one agent and one kill switch; (ii) the
  Sprint-1 gate ran on synthetic fixtures (10/10 PASS) and is calibration, not value."
- IMPLEMENTATION VALID, [], false: "The compose->falsify seam exists in code and
  executes offline today ... 813 tests pass at baseline. The P57 statement that the seam
  'was never built' is contradicted by executed evidence."
- CONFIGURATION VALID, [], false: "No configuration defect found. ... the daemon's own
  tick summaries report stygian_recent=166 / pollux_recent=95, i.e. it saw its inputs.
  Queue-row keys match loader keys (0 missing). Caveat: the runtime config it actually ran
  under (M2, May 2026) is not on the tree; this verdict rests on the code contract plus
  the daemon's self-reports."
- EXECUTION VALID, [], false: "It ran: 213 tick rows 2026-05-26 02:32 .. 2026-05-30
  11:59 (local), all success=true, every summary enqueued=True; 39 commits on the agent
  dir 05-26..06-03 reaching ITER-84 of a 100-ITER pre-commitment. It did not stop on its
  own: 15 May-fleet agents wrote their last row 11:40-12:25 on 05-30 (fleet halt),
  Stygian/Pollux/Hecate included. 234 composed_claim artifacts (P57 count) vs 213 ticks:
  different objects or windows; gap recorded, not reconciled. No runtime artifact
  survives on this host."
- INSTRUMENTATION INVALID, [INSTRUMENT_ERROR], load_bearing false: "The primary
  observations (kill_ledger.jsonl, composed_claim_*.md artifacts, per-plugin logs,
  tick_counter, stygian_priority queue) were gitignored and were never archived ... Not
  load-bearing for the original run (the instruments wrote), but load-bearing for any
  re-audit: the 699-row ledger behind Phase 3.K cannot be re-measured."
- MEASUREMENT INVALID, [MEASUREMENT_ERROR], load_bearing true: "The number behind '0
  permutation-null survivors' is Phase 3.K: observed=2 substrate-vs-pair-aware deltas
  against a null with p95=2 (p=0.105, N=699 rows, 200 permutations, seed 1789).
  Executing the committed harness unchanged on synthetic 699-row ledgers shows the
  statistic has no resolution in this regime ... 'Underdetermined' was therefore a
  property of the instrument, not evidence about Layer-2 value. Scope limit: the planted
  signal is one class; a lift-only signal class was not tried."
- INTERPRETATION INVALID, [INTERPRETATION_ERROR], load_bearing true: "Two later
  interpretations diverge from the primary record. (1) 'STATISTICALLY UNDERDETERMINED'
  (06-03) became 'realized ~0 (0 perm-null survivors)' (06-23/24) and 'realized value ~0'
  (queue): an unresolved test read as a null result. (2) P57 (08-21) asserted the seam
  'was never built' and 'ZERO external references' from a case-sensitive grep whose scope
  excluded charon/agents/stygian ... Load-bearing for the SELF-CONTAINED-GENERATION label;
  not the cause of the pause."
- ECOSYSTEM INVALID, [ECOSYSTEM_FAILURE], load_bearing true: "Erebos stopped because its
  ecosystem stopped, twice: the 2026-05-30 fleet halt (all May agents within 45 minutes)
  and the 2026-06-15 program reset ('immune system with no organism'; 'off-spine until it
  has a consumer'), where 'consumer' meant an organism that uses verdicts, not the
  falsifier (which existed and had loaders). No kill condition of Erebos's own ever
  fired: Sprint-1 rule 10/10 PASS, ITER-100 unreached. This is the primary cause of
  death."

fair_test: verdict "UNFAIR"; scope "H-B (Layer-2 value over Layer-1) is the claim the
death certificates rest on; the only real-data test of it (Phase 3.K, 2026-06-03, 699-row
ledger) used a statistic shown to have no resolution in that regime, and the pre-committed
ITER-100 discriminating test was never run. ..."; finding "No fair test of the capability
the grave is labelled for exists on the record. The composer worked mechanically; the
value bet was measured with an instrument that cannot say yes or no at the ledger size
available; then the ecosystem stopped."

primary_cause "ECOSYSTEM_FAILURE"; contributing_causes ["MEASUREMENT_ERROR",
"INTERPRETATION_ERROR", "INSTRUMENT_ERROR"]; classification (disposition)
NO_FAIR_TEST_ON_RECORD.

death_certificates: P57 OVERTURNED; 06-24 component dossier PARTIALLY_UPHELD; 06-23
disposition row PARTIALLY_UPHELD; Phase 3.K PARTIALLY_UPHELD; 06-15 reset UPHELD;
taxonomy cluster 5 OVERTURNED; QUEUE 'likely TRUE_CORPSE' OVERTURNED.


## 2 OBJECTIONS

Severity key: FATAL changes fair_test, primary_cause or classification; MATERIAL changes a
layer verdict; MINOR otherwise.

### C-1 (MATERIAL, feeds section 3) -- HYPOTHESIS "Neither was refuted on the record" omits the ITER-56/57 refutation of H-B as originally built

Claim attacked: HYPOTHESIS finding, "Neither was refuted on the record"; DESIGN VALID.

Evidence executed: `git show fbe4f6b7a` (2026-05-30, "Erebos Phase 3.0 ITER-56:
real-residue smoke -- FAIL"): "across all 13 plugins in the real data, Layer 2's
motif-based routing recommendation EXACTLY matches the trivial per-plugin majority
counter. Zero actionable routing deltas ... The architectural CLAIM (Layer 2 produces
decision-relevant signal beyond counters on real residue) is empirically falsified on the
current ledger." `git show f837d4281` (ITER-57): "The motif extractor (ITER-40), as
designed, computes the SAME function as a per-plugin majority counter, by construction
... This is not a bug. It's a structural property of the primitive." Re-run with 638
rows: "Plugins where Layer 2 != counter: STILL 0 / 16". Grep of the dossier and README
for `ITER-5[0-9]|Phase 3\.0|real.residue|counter baseline|majority counter|redesign`:
0 hits (executed). The verdict docs exist on the tree:
`pivot/sprint1/phase3/PHASE3_0_SMOKE_VERDICT_2026-05-30.md`,
`pivot/sprint1/phase3/PHASE3_COMBINED_VERDICT_2026-05-30.md`.

Rule cited: LAW N17 "VALID (with executed evidence)"; SCHEMA HYPOTHESIS "the outcome
lives in cause_classes"; charter DESIGN_ERROR "the experiment could not answer the
question it purported to answer"; brief "Are contradictory artifacts ignored? (commits
...)".

What it changes: H-B has two versions on the record. H-B v1 (kill tensor + ITER-40 motif
extractor, the design named in `pivot/erebos_doctrine_v1_2026-05-27.md`) was tested on
real residue and refuted by its own author's counter baseline at ITER-56/57. H-B v2 (the
ITER-58 cross-cell primitive) is what Phase 3.K later left UNDERDETERMINED. The dossier's
H-B is silently v2. The DESIGN layer must record DESIGN_ERROR for v1 (a Layer-2 primitive
that is a counter by construction cannot answer "does Layer 2 beat counters"), non-load-
bearing for the final verdict only because it was repaired the same day with a measured
result (ITER-58: 3 deltas vs counter, `git show c7977df3f`). That is exactly the
"non-load-bearing INVALID with a measurement showing it did not carry the result" the
charter asks for -- and the Necromancer has none of it.

### C-2 (MATERIAL) -- MEASUREMENT ignores the on-record scale-stress trajectory that the author called "the strongest single diagnostic"

Claim attacked: MEASUREMENT finding, "'Underdetermined' was therefore a property of the
instrument, not evidence about Layer-2 value."

Evidence executed: `git show 36f46b97f` (ITER-63/64/66, 2026-05-30): "ITER-66 -- Scale
stress (5x enrichment) ... observed deltas: 3 -> 5 (+1.7x); null mean: 0.64 -> 1.74
(+2.7x) <-- null grew faster than signal; z-score: 2.48 -> 1.92 (DOWN); p-value: 0.055 ->
0.080 (WORSE) ... A real architectural signal would have driven p < 0.01 at 5x."
`pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md` section 7 item 4:
"The signal-grows-slower-than-noise pattern (ITER-66) is now confirmed three ways
(per-plugin p 0.055->0.075 as the ledger grew; pair-aware p=0.105; triplet
observed-below-null). This is the strongest single diagnostic." Dossier grep for
`ITER-6[0-9]|scale|grew|lateral|hierarchical`: 0 hits in findings (the 0.055->0.075
number appears only inside a quoted evidence string, unweighed).

Rule cited: LAW N17 layer question "was this layer actually valid?" answered with
executed evidence; brief "Are contradictory artifacts ignored?".

Why it matters: an instrument-at-floor story predicts a p-value that wanders with no
trend as N grows. The record shows three monotone moves in the same direction across
N = 640 -> 699 -> 895 (per-plugin statistic) plus the pair-aware and triplet tests. That
is weak but real evidence about the data, not only about the instrument. The Necromancer
converted "underdetermined" into "uninformative"; the record supports "underdetermined
with a trend against H-B v2". This does not make H-B FALSIFIED (the trend is three
points on a low-power statistic) but it removes the dossier's licence to say the Layer-2
test carried no evidence about value.

### C-3 (MATERIAL) -- MEASUREMENT_ERROR is misfiled by the charter's own definition; the low-power finding belongs on INSTRUMENTATION (and it does generalise to the lift-only class)

Claim attacked: MEASUREMENT INVALID / MEASUREMENT_ERROR / load_bearing true, on the
ground that the Phase 3.K statistic "has no resolution in this regime".

Rule cited: `engine/necropolis/CHARTER.md` cause table: MEASUREMENT_ERROR = "the recorded
quantity is not the quantity the design named (instrument state in the outcome column; a
metric that carries its own answer)"; INSTRUMENT_ERROR = "the apparatus could not observe
the proposed phenomenon"; SCHEMA INSTRUMENTATION "instrument above chance, chance floor
published"; SCHEMA DESIGN "chance floor".

Argument: Phase 3.K recorded exactly the quantity its protocol named (substrate-vs-pair-
aware delta count under a signature-shuffle null), reported observed, null mean, p95, p,
z and seven seeds, and labelled the result UNDERDETERMINED. Nothing about the recorded
quantity differs from the quantity named. A statistic with a chance floor at or above
the effect size is an apparatus that "could not observe the proposed phenomenon" --
INSTRUMENT_ERROR -- or a test-design defect ("chance floor" is listed under DESIGN). The
Necromancer's own calibration measures the instrument, and the finding sentence says so
("a property of the instrument"). Filing it as MEASUREMENT_ERROR is a taxonomy
collision, not an evidence error.

Evidence executed (new): `engine/necropolis/dossiers/erebos_evidence/cleric_lift_only_calibration.py`
-> `cleric_lift_only_calibration_result.json`. Same harness, same monkeypatch, same
699 rows / 14 plugins / 6 kill patterns / 230 signatures, but the plant is the LIFT-ONLY
class the dossier says it did not try (partner-conditioned globally-rare kp at 5/12
shared signatures vs the globally-common kp at 7/12, so count-max and lift-max must
disagree by construction). Result:
- unshuffled read: every planted cell appears as a substrate-vs-pair-aware disagreement
  in 9/9 (world, seed) runs (e.g. "g02_contrast | given ('g10_boundary',
  'permutation_null') : substrate=boundary_artifact pair_counter=threshold_artifact"), so
  the raw statistic does see lift-only structure;
- NULL: observed [1, 2, 0], null_p95 [1, 1, 1], p [0.275, 0.03, 1.0] -- ONE FALSE POSITIVE
  in 3 at exactly observed=2 (the historical count);
- LIFT2 (two planted pairs): observed [5, 10, 6], null_mean [5.7, 5.1, 4.2], null_p95
  [9, 9, 7], p [0.69, 0.04, 0.23], detected 1/3;
- LIFT3: observed [7, 11, 7], null_p95 [10, 9, 8], p [0.44, 0.01, 0.2], detected 1/3.
The null floor of this statistic is a function of how concentrated each plugin's kp
marginal is: concentrating the partner plugin on one kp (the real ledger's regime per
ITER-57, "one dominant kp per plugin") lifts the null mean from ~0.3 to ~5 and buries
2-3 genuine lift-only deltas. So the Necromancer's uncertainty item 3 ("a lift-only class
might separate the two counters") is answered: it does not, at N=699, with this null. The
instrument-floor conclusion is NOT over-generalised on that axis -- but the false
positive at observed=2 strengthens, not weakens, the point that Phase 3.K could not
say yes or no. The correct home for that finding is INSTRUMENTATION, load-bearing.

Effect on outcome: none on fair_test (INSTRUMENTATION is inside DESIGN..MEASUREMENT, so
UNFAIR still has a load-bearing INVALID to rest on) and none on classification. Effect
on the stack: MEASUREMENT must be re-argued (see C-4) and INSTRUMENTATION becomes
load-bearing.

### C-4 (MATERIAL) -- there IS a charter-grade MEASUREMENT_ERROR on the record, and the Necromancer did not find it: the kill_ledger's outcome column carried pipeline state

Claim attacked: the MEASUREMENT finding's grounds (see C-3), and DESIGN VALID.

Evidence executed: `git show fbe4f6b7a`: "570 rows but only ~8 distinct REAL Layer-1
verdicts; rest are pending / not-yet-implemented." `git show c7977df3f` (ITER-58, the
only real-data Layer-2 PASS ever recorded): all three "actionable deltas" are of the form
"stygian_battery | given (g02_contrast, kp_pending) observed: counter says:
stygian_hecate_meta_test_not_yet_implemented; substrate says:
stygian_battery_verdict_possible" and "given (hephaestus_composed_claim, kp_pending)
... substrate says: stygian_no_loader_registered". ITER-64 (`git show 36f46b97f`): "ALL
of substrate's signal is concentrated on hierarchical prediction. Zero deltas on lateral
structure." The seam census (executed, `erebos_seam_census_result.json`) shows 11/25
plugins short-circuit to `stygian_erebos_composed_loader_pending` by construction.

Rule cited: SCHEMA MEASUREMENT "instrument state not in the outcome column, the metric
does not carry its own answer"; charter MEASUREMENT_ERROR text quoted in C-3; memory
doctrine "measurement carries its answer".

Argument: the "kill patterns" Layer 2 was navigating were, for the large majority of
rows, the pipeline's own states (`kp_pending`, `*_not_yet_implemented`,
`no_loader_registered`, `verdict_possible`). The one signal the redesigned Layer 2 found
is "a composed claim whose parent is pending tends to hit a child state determined by
whether a loader exists" -- the instrument's state predicting the instrument's state.
That is the charter's definition of MEASUREMENT_ERROR, it is load-bearing on every
Layer-2 real-data test (ITER-56 through ITER-84), and it also indicts DESIGN ("could the
experiment as designed answer the question": a Layer-2 value test run on a ledger that
is mostly plumbing state cannot). The Necromancer's MEASUREMENT INVALID / load-bearing
verdict therefore survives, but on grounds it never stated; the grounds it did state
belong to INSTRUMENTATION.

### C-5 (FATAL) -- primary_cause ECOSYSTEM_FAILURE is not what the charter's ECOSYSTEM_FAILURE means, and the record shows the 06-15 pause cited the null results

Claim attacked: ECOSYSTEM finding "This is the primary cause of death"; primary_cause
"ECOSYSTEM_FAILURE".

Rule cited: LAW N17 text: "the `primary_cause` the stack supports. The strong claims --
`HYPOTHESIS_FAILURE`, and above it `PREMISE_FAILURE` -- are admitted only after a fair
test and only after every other cause class has been excluded"; cause table
ECOSYSTEM_FAILURE = "the producer may have worked, but nothing useful consumed what it
emitted"; validate.py "primary_cause {pc} is not carried by any layer of the stack".

Evidence executed: `engine/necropolis/dossiers/_keeper_evidence/fleet_halt_census_result.json`
(read): 15 agent prefixes wrote their last row on 2026-05-30 (deep 06:30; hypatia 11:40 ..
nephele 12:24; erebos 11:59, stygian 12:03, hecate 12:20, pollux 11:55). That is a
fleet-wide process halt: Stygian, the falsifier that consumed Erebos rows, stopped four
minutes AFTER Erebos, so at the moment Erebos stopped its consumer was alive.
`aporia/docs/STATUS_2026-06-15_reset.md` L102-103 (read; NOT cited anywhere in the
dossier): "OFF until they have a consumer: ... Erebos composition (paused; reframe
Phase-3 docs honestly -- 0 signal passes survive nulls, 1 infra pass stands)."
`charon/CHARON_SESSION_2026-06-15.md` L7-9: "Erebos composition is explicitly PAUSED with
the instruction to 'reframe Phase-3 docs honestly -- 0 signal passes survive nulls, 1
infra pass stands' (section 7)." `git show 63ccbc8e0` (06-15): "0 signal passes survive
a null ... endorsed by STATUS_2026-06-15 reset 7."

Argument:
(i) The 05-30 event is an orchestration halt of the whole May fleet, not a consumer
failure. The charter has a classification ORCHESTRATION_FAILURE but no cause class for
it; the Necromancer squeezed it into ECOSYSTEM_FAILURE, whose text is about consumption
of emissions. Nothing in the dossier shows that "nothing useful consumed what it
emitted" -- the IMPLEMENTATION layer argues the opposite (the falsifier consumed and
verdicted composed claims).
(ii) The 06-15 pause names two reasons in one sentence: no consumer, AND "0 signal passes
survive nulls". The Necromancer quotes the first half (from the Charon journal) and omits
the second (from the decision document). The pause was informed by the content reading
that the INTERPRETATION layer itself calls an error (if "0 survive" is a misreading) or
that is evidence against H-B (if it is not). Either way the ecosystem did not stop Erebos
in ignorance of its results.
(iii) A competent reader who accepts the Necromancer's own INTERPRETATION verdict puts
INTERPRETATION_ERROR primary: every certificate on the record (06-23, 06-24, P57, QUEUE)
is about content ("realized ~0", "0 perm-null survivors", "seam never built"), and the
dossier's own kill_boundary kills four content claims and zero ecosystem claims. Under
C-2/C-4 a reader who does NOT accept that verdict puts MEASUREMENT_ERROR primary (the
Layer-2 tests measured plumbing state). Under neither reading is ECOSYSTEM_FAILURE the
cause the stack "supports"; it is the cause of the process stopping, and the doctrine
does not say primary_cause means that (defect DD-2).

Effect: primary_cause changes (FATAL by the brief's definition); fair_test and
classification do not.

### C-6 (MATERIAL) -- EXECUTION VALID contradicts the schema's EXECUTION text on two counts and rests on 3 of 213 sampled summaries

Claim attacked: EXECUTION VALID; "every summary enqueued=True".

Rule cited: SCHEMA EXECUTION "(runs happened, state persisted, artifacts kept, no silent
fallbacks or partial runs)"; LAW N17 "VALID (with executed evidence)".

Evidence executed/read: `_keeper_evidence/intelligence_outputs_census.py` samples
`limit 3` summaries; `intelligence_outputs_census_result.json` carries only
`first_three_summaries` (grep count of "enqueued" in the file = 3), so "every summary
enqueued=True" is an inference from 3/213, not a census. The same file:
distinct_output_summary 212 of 213 (one duplicate summary, unremarked). INSTRUMENTATION
finding (Necromancer's own): the ledger, artifacts, logs, tick_counter and queue "were
never archived". History census (re-executed, identical): max ITER 84 of a 100-ITER
pre-commitment. Keeper caveat in the same result: "DUAL-RECORDED IS NOT INDEPENDENTLY
VERIFIED".

Argument: "artifacts kept" is false (the Necromancer says so one layer down); "no
partial runs" is false for the pre-committed experiment (84/100, kill test never run).
"State persisted" is attested only by the daemon's own rows. Under the schema text
EXECUTION cannot be VALID; under a strict reading of "with executed evidence" it is
NOT_EXAMINED (the README's own D7 concedes this for a strict reader). The Cleric's
position: INVALID / EXECUTION_ERROR (partial run of the pre-committed experiment) is the
verdict the schema text supports; NOT_EXAMINED is the honest fallback if the Keeper
rules that a truncated pre-commitment is not an "execution" defect. Either way the
fair_test stays UNFAIR (EXECUTION is inside DESIGN..MEASUREMENT and would now carry a
load-bearing INVALID or a NOT_EXAMINED, both of which forbid FAIR).

### C-7 (MATERIAL) -- CONFIGURATION VALID and HYPOTHESIS VALID rest on self-report and quoted prose; doctrine does not permit VALID there

Claim attacked: CONFIGURATION VALID ("this verdict rests on the code contract plus the
daemon's self-reports"); HYPOTHESIS VALID (evidence is one executed seam census plus
three QUOTED docs).

Rule cited: LAW N17 "VALID (with executed evidence) ... NOT_EXAMINED (honest)"; brief
"a script you cannot run makes its layer NOT_EXAMINED in your view, not VALID"; Keeper
census caveat "DUAL-RECORDED IS NOT INDEPENDENTLY VERIFIED".

Evidence: `intelligence_outputs_census_result.json` rows are written by the Erebos daemon
(`_enqueue_to_stygian` and the tick summary are the same process); the `stygian_recent=166
/ pollux_recent=95` numbers in the CONFIGURATION finding come from those summaries. The
runtime config (M2, May 2026) is not on the tree (Necromancer's own caveat). For
HYPOTHESIS the executed evidence (seam census) shows the composer can reach a loader; it
says nothing about whether the propositions were well-posed, and the finding's content is
carried entirely by quoted verdict docs.

Position: CONFIGURATION -> NOT_EXAMINED (the code contract is verified; the run
configuration is not). HYPOTHESIS: with C-1 the honest verdict is INVALID for H-B v1
(refuted on record, DESIGN_ERROR carried on DESIGN) and NOT_EXAMINED for H-B v2 and H-A
as value propositions -- but the stack has one HYPOTHESIS slot, so the layer verdict
should be NOT_EXAMINED with the finding rewritten to name both versions (defect DD-3).
Neither change moves fair_test or classification.

### C-8 (MATERIAL) -- DESIGN VALID contradicts the schema's "consumer at birth"

Claim attacked: DESIGN VALID.

Rule cited: SCHEMA DESIGN "(comparators, controls, chance floor, holdout structure,
consumer at birth)"; LAW N6 (consumer at birth) as referenced by the charter; charter
NO_FAIR_TEST_ON_RECORD = "the historical experiment could not have answered its own
question".

Evidence: dossier `kill_boundary` (c): "the 06-15 judgement that no organism consumed the
verdicts stands"; ECOSYSTEM finding: "'consumer' meant an organism that uses verdicts";
uncertainty item 6: CONSUMER_BLOCKED as an alternative classification. `pivot/COMPONENT_DOSSIERS_2026-06-24.md`
Erebos section (read): "predicate_handle + 4 cost-instrumentation fields shipped but never
wired to a producer". Charter design_error text: "the experiment could not answer the
question it purported to answer" -- the question "value = PROMOTED claims per cost"
(dossier premise) had no consumer of PROMOTED claims and no cost producer, so it could
not be answered by construction. Together with C-1 (Layer-2 v1 a counter by
construction) and C-4 (ledger mostly plumbing state), DESIGN cannot be VALID. Position:
INVALID / DESIGN_ERROR, load_bearing true. This keeps UNFAIR and NO_FAIR_TEST_ON_RECORD
but changes WHY: the experiment could not have answered its own question, which is the
charter's definition of that classification -- a better fit than "the instrument was
underpowered".

### C-9 (MINOR) -- external_refs numbers do not reproduce at HEAD, and the script's own-prefix list is incomplete

Claim: `erebos_external_refs_result.json` A=3 / A2=14 / B=198. Re-run at HEAD cc7afb99e:
A=4 / A2=19 / B=207. Diagnosis (executed diff of hit lists): the extra hits are files
added after the evidence baseline (`_keeper_evidence/`, `DEFECTS.md`, this trial's
dossiers), and `OWN_PREFIXES` in `erebos_external_refs.py` excludes the erebos dirs but
not `engine/necropolis/dossiers/_keeper_evidence/`, so Necropolis's own census files
count as "external references". The core claim (P57's grep reproduces in its own scope as
3 self-hits; 53 stygian files; 19 harmonia files; one harmonia import) stands. Fix the
prefix list and pin the baseline in the result.

### C-10 (MINOR) -- 213 ticks vs 234 artefacts: neither count supports more than "it ticked"

Evidence: Keeper census 213 rows, 213 distinct cycle_id, 212 distinct summaries, window
05-26 02:32 .. 05-30 11:59; P57 counted 234 artefacts in August "on a host that still
had them" (dossier); the 06-24 author "Confirmed 234 composed_claim artifacts" with the
files in hand; git shows manual harness runs 05-30..06-03 (ITER-57 layer1_enrichment,
ITER-66 "220 more enrichment rows") that write to `charon/agents/erebos/state/` and
`artifacts/`. The 21-file surplus is consistent with manual runs after the daemon
stopped, or multi-claim ticks; it cannot be reconciled without the artefacts. The count
is evidence of activity, not of value, and the dossier already treats it so. No amendment
beyond recording the two candidate explanations.

### C-11 (MINOR) -- brief/charter mismatch on the outcome vocabulary

The brief says "eight charter outcomes"; `CHARTER.md` lists thirteen classifications and
validate.py accepts thirteen. Recorded so the Keeper's adjudication uses the charter's
list (defect DD-6).


## 3 THE CORPSE CASE

The strongest honest argument that this grave is TRUE_CORPSE / HYPOTHESIS_FAILURE, built
only from the record:

1. H-B v1 was refuted on real data by its own author's discriminating baseline, at
   ITER-56 and again at ITER-57 with 638 rows: zero routing deltas vs a per-plugin
   majority counter, and a structural proof that the primitive IS a counter
   (`git show fbe4f6b7a`, `f837d4281`). That is a fair test of the design as originally
   proposed, and it failed.
2. H-B v2 (the same-day redesign) produced 3 deltas vs the weak counter and 2 vs the
   pair-aware counter; every subsequent adversarial pass narrowed it: p=0.055 (ITER-63),
   worse under 5x data (ITER-66, p=0.080, "null grew faster than signal"), hierarchical-
   only (ITER-64, zero lateral deltas), pair-aware p=0.105 stable over 7 seeds (ITER-83),
   triplet observed BELOW null (ITER-84). The author's own summary: "The claim keeps
   narrowing under each successive adversarial pass -- itself a signal worth heeding" and
   "the affirmative evidence for the doctrine's main claim is, as of this audit, absent."
3. The only Layer-2 signal ever found is pipeline plumbing predicting pipeline plumbing
   (C-4). Stripped of `kp_pending -> no_loader_registered` structure there is no
   candidate signal left on the record at all.
4. H-A produced PROMOTED verdicts that its author immediately reclassified to catalog
   tier ("real verdicts, modest mathematics"), 11/25 plugins never produced a falsifiable
   claim, and no organism ever consumed a PROMOTED composed claim. The premise "value =
   PROMOTED claims per cost" realised no measured value in 4.4 days and 39 commits.
5. The three-way signal-shrinks-with-N trajectory is the shape a null hypothesis leaves
   on a low-power instrument; a true effect on the same instrument leaves the opposite
   shape.

Does the record support TRUE_CORPSE? No, and the Cleric says so plainly. Three things
block it under the charter and validator:

- TRUE_CORPSE needs fair_test FAIR with no load-bearing INVALID in DESIGN..MEASUREMENT.
  C-4 (outcome column carried pipeline state) and C-8 (no consumer at birth) are load-
  bearing design/measurement defects that no measurement on the record shows to be
  non-load-bearing. The H-B v1 refutation (item 1) is fair for v1 but v1 was repaired
  before the pre-committed test; the pre-committed ITER-100 test never ran.
- The trajectory in item 5 is three points on a statistic whose null floor my own
  calibration shows to be marginal-dependent and capable of a false positive at
  observed=2. It is a lean, not a kill.
- HYPOTHESIS_FAILURE requires "every other cause class has been excluded" (LAW N17).
  DESIGN_ERROR, MEASUREMENT_ERROR, INSTRUMENT_ERROR and EXECUTION_ERROR are all live.

Is "no consumer" unfairness or the result? Both, split by hypothesis. For H-A it is the
result: a composer whose PROMOTED output nothing consumes has realised the value its
premise named as zero, and that is not an accident of orchestration -- the design never
specified the consumer (C-8). Calling that unfair is the resurrection bias of section 4.
For H-B it is unfairness: Layer-2 value over Layer-1 could not be measured on a ledger
made of plumbing state, whatever the consumer situation.

The single artefact that would establish TRUE_CORPSE: a Layer-2-vs-Layer-1 run of the
committed harnesses on a ledger whose kill_pattern column contains only real Layer-1
verdicts (no `pending` / `not_yet_implemented` / `no_loader_registered` rows), at or above
the N where `cleric_lift_only_calibration.py` shows the statistic clearing its floor for a
planted lift-only signal, with the ITER-64 lateral/hierarchical split reported. If that
run shows zero lateral deltas and p above 0.05 against the pair-aware counter, H-B is
dead fairly. The `_cross_cell_motif.py` and `pair_aware_permutation_null.py` code needed
to run it is on the tree and passes 813 tests today; only the ledger is missing.


## 4 THE RESURRECTION-BIAS CASE

Where the Necromancer reads toward salvage beyond the evidence:

1. Omitting the ITER-56/57 refutation and the ITER-64/66 narrowing (C-1, C-2) while
   quoting the ITER-5 PROMOTED tally and the 813 passing tests in three separate layers.
   The executed evidence is all on the "it runs" side; the "it was tested and lost"
   commits are on the same `git log` the history census walked and are not mentioned.
2. "Neither was refuted on the record" is stated for a hypothesis whose first version
   was refuted on the record by the author's own commit message using the word
   "falsified".
3. Reading the 06-15 pause as purely "no organism" when the decision document pairs it
   with "0 signal passes survive nulls" in the same clause (C-5). The Necromancer UPHELD
   that certificate without citing the document it comes from.
4. Treating "STATISTICALLY UNDERDETERMINED" as symmetric ignorance. The author's residual
   section and the three-way trend both lean one way; the dossier's own evidence string
   quotes the 0.055->0.075 decay and the finding ignores it.
5. The calibration's synthetic NULL world has null_p95 = 1 while the historical null had
   p95 = 2 and mean 0.48; the synthetic ledger is not structure-matched to the real one,
   so "an observed count of 2 sits AT the instrument floor on 699-row ledgers regardless
   of the data" (calibration `reading`) is asserted from a world with a lower floor than
   the real one. My concentrated-marginal world has a HIGHER floor. The honest statement
   is "the floor depends on marginal structure we can no longer measure".
6. `salvageable_operators` lists `pair_aware_counter_recommendations` and
   `representation_hints` proposes a new statistic, i.e. the dossier already sketches the
   resurrection experiment before establishing that the organism's only observed signal
   was not plumbing (C-4).
7. Six of seven death certificates are OVERTURNED or PARTIALLY_UPHELD. The P57 and
   taxonomy overturns are earned (the grep scope error reproduces). The 06-23/06-24
   "realized ~0" overturns are not: on this record "realized value ~0" is literally
   true (nothing consumed a PROMOTED claim; no Layer-2 signal survived a null); what
   those documents got wrong is the inference to "0 survivors = null result", and that
   is one clause, not the certificate.


## 5 STACK AMENDMENTS DEMANDED

| layer | Necromancer | Cleric would set | evidence |
|---|---|---|---|
| HYPOTHESIS | VALID / [] / false | NOT_EXAMINED, finding rewritten to name H-B v1 (refuted ITER-56/57, repaired ITER-58) and H-B v2 / H-A (untested as value propositions); no cause class on this layer | `git show fbe4f6b7a f837d4281 c7977df3f`; `pivot/sprint1/phase3/PHASE3_0_SMOKE_VERDICT_2026-05-30.md`, `PHASE3_COMBINED_VERDICT_2026-05-30.md` |
| DESIGN | VALID / [] / false | INVALID / [DESIGN_ERROR] / load_bearing TRUE: no consumer at birth for PROMOTED claims and no cost producer (premise unanswerable); Layer-2 v1 a counter by construction (repaired, non-load-bearing with ITER-58 measurement); value test run on a ledger of plumbing state | dossier `kill_boundary` (c); `pivot/COMPONENT_DOSSIERS_2026-06-24.md` Erebos section; C-1; C-4 |
| IMPLEMENTATION | VALID / [] / false | VALID (unchanged) -- seam census and 813 tests re-executed and match | `erebos_seam_census_result.json`, `erebos_tests_offline_result.json` (re-run identical) |
| CONFIGURATION | VALID / [] / false | NOT_EXAMINED: code contract verified (queue keys 0 missing), runtime configuration attested only by daemon self-report | `_keeper_evidence/intelligence_outputs_census_result.json` caveat "DUAL-RECORDED IS NOT INDEPENDENTLY VERIFIED" |
| EXECUTION | VALID / [] / false | INVALID / [EXECUTION_ERROR] / load_bearing TRUE: pre-committed experiment stopped at ITER-84/100, artefacts not kept; or NOT_EXAMINED if the Keeper rules a truncated pre-commitment is not an execution defect. "Every summary enqueued=True" must be restated as "3 of 3 sampled" | history census (re-run identical); `_keeper_evidence/intelligence_outputs_census.py` `limit 3`; SCHEMA EXECUTION text |
| INSTRUMENTATION | INVALID / [INSTRUMENT_ERROR] / false | INVALID / [INSTRUMENT_ERROR] / load_bearing TRUE: the Phase 3.K statistic's null floor is at/above the effect size and marginal-dependent (Necromancer calibration + Cleric lift-only calibration), AND the primary observations were never archived | `erebos_null_instrument_calibration_result.json` (re-run identical); `cleric_lift_only_calibration_result.json` |
| MEASUREMENT | INVALID / [MEASUREMENT_ERROR] / true | INVALID / [MEASUREMENT_ERROR] / load_bearing TRUE -- same verdict, grounds replaced: the kill_ledger outcome column carried pipeline state (`kp_pending`, `not_yet_implemented`, `no_loader_registered`) for most rows and the only Layer-2 signal found was that state predicting itself; the "no resolution" argument moves to INSTRUMENTATION | `git show fbe4f6b7a` ("~8 distinct REAL Layer-1 verdicts"), `c7977df3f` (the three deltas), `36f46b97f` (ITER-64 HIERARCHICAL_ONLY) |
| INTERPRETATION | INVALID / [INTERPRETATION_ERROR] / true | unchanged verdict; finding must add the ITER-66 / Phase 3.K section-7 trend as evidence the 06-23/24 authors were relaying, so the error is narrowed to "0 survivors read as a null RESULT", not to "realized ~0" (which is true on record) | `PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md` sections 4, 7 |
| ECOSYSTEM | INVALID / [ECOSYSTEM_FAILURE] / true | INVALID / [ECOSYSTEM_FAILURE] / load_bearing FALSE for the death (no organism consumed PROMOTED claims -- true, but the design never named one, so it is DESIGN); the 05-30 fleet halt recorded as an orchestration event with no admissible cause class (defect DD-1) | `_keeper_evidence/fleet_halt_census_result.json`; `aporia/docs/STATUS_2026-06-15_reset.md` L102-103 |

primary_cause: MEASUREMENT_ERROR (C-4), with DESIGN_ERROR, INSTRUMENT_ERROR,
INTERPRETATION_ERROR, EXECUTION_ERROR contributing and ECOSYSTEM_FAILURE demoted to
contributing. If the Keeper rejects C-4's reading of the ledger content, the fallback
primary is INTERPRETATION_ERROR (C-5 iii), never ECOSYSTEM_FAILURE.

fair_test: UNFAIR (unchanged), scope rewritten: H-B v1 was fairly tested and lost
(ITER-56/57) but was superseded before the pre-committed test; H-B v2 and H-A's value
premise were never fairly tested (design without consumer, ledger of plumbing state,
underpowered statistic, pre-commitment truncated at 84/100).

classification: NO_FAIR_TEST_ON_RECORD (unchanged), now resting on the charter's own
definition ("the historical experiment could not have answered its own question") rather
than on instrument power alone. CONSUMER_BLOCKED remains the honest neighbour for H-A.

death_certificates: 06-23 and 06-24 should be UPHELD-with-one-error rather than
PARTIALLY_UPHELD (see section 4 item 7); 06-15 reset UPHELD but with the second half of
its sentence quoted; Phase 3.K UPHELD (its label was honest and its section 7 trend is
evidence, not an overstatement). P57, taxonomy cluster 5 and QUEUE overturns stand.


## 6 DOCTRINE DEFECTS

Numbered, not resolved.

DD-1 Taxonomy gap: a fleet-wide process halt (15 agents in 45 minutes) has a
classification (ORCHESTRATION_FAILURE) but no admissible cause class on any layer, so a
Necromancer is forced to misfile it as ECOSYSTEM_FAILURE or omit it. Every May-fleet
grave will hit this.

DD-2 Ambiguity: "primary_cause the stack supports" (LAW N17) does not say whether
primary means the cause of the organism stopping, the cause of the death certificates
being wrong, or the cause of the hypothesis being unanswerable. The Erebos stack yields
three different primaries under the three readings (ECOSYSTEM_FAILURE /
INTERPRETATION_ERROR / DESIGN_ERROR or MEASUREMENT_ERROR).

DD-3 One HYPOTHESIS slot, one DESIGN slot, but two hypotheses (H-A, H-B) and two
versions of H-B (v1 refuted, v2 redesigned the same day). The stack cannot express
"refuted then repaired before the pre-committed test" without either a false VALID or a
lossy NOT_EXAMINED.

DD-4 Taxonomy collision: MEASUREMENT_ERROR ("recorded quantity is not the quantity the
design named") vs INSTRUMENT_ERROR ("apparatus could not observe the phenomenon") vs
DESIGN "chance floor". An underpowered statistic fits all three and the Necromancer and
Cleric filed it on different layers with the same evidence.

DD-5 Whose DESIGN? The layer describes the organism's experimental design, but the
load-bearing test (Phase 3.K) was designed by the same author as an adversarial audit
weeks after the organism. A defect in the audit's statistic is filed on the organism's
DESIGN or INSTRUMENTATION layer with no field to say which artefact is meant.

DD-6 Brief/charter mismatch: "eight charter outcomes" (brief) vs thirteen classifications
(CHARTER.md, validate.py). Also SCHEMA references LAW N6 "consumer at birth" but the
charter text under N6 is not quoted in the dossier; a reader cannot check the rule from
the dossier alone.

DD-7 Missing provenance rule: the Keeper census samples 3 summaries but the dossier says
"every summary ends enqueued=True". Nothing in SCHEMA/validate.py requires a sampled
census to be labelled as a sample, so the validator passed a universal claim built on
n=3.

DD-8 Self-report admissibility: LAW N17 says VALID needs "executed evidence" but does not
say whether evidence executed BY THE ORGANISM (its own agora rows, its own tick
summaries) counts. The Keeper's caveat "DUAL-RECORDED IS NOT INDEPENDENTLY VERIFIED"
exists but no rule consumes it. CONFIGURATION and EXECUTION VALID both rest on it.

DD-9 Reader divergence on truncated pre-commitments: a pre-registered kill test that
never ran is EXECUTION_ERROR ("not executed faithfully"), DESIGN (the kill was designed
but not reachable), or nothing (the organism was stopped from outside). Three readers,
three layers.

DD-10 Certificate review granularity: a certificate that is factually right ("realized
~0") but wrong in one inference ("0 survivors = null result") can only be
PARTIALLY_UPHELD, which the Necromancer used for both "mostly right" (06-23) and "half
wrong" (06-24, "loader never shipped"). The vocabulary cannot separate them.

DD-11 Calibration worlds are not fingerprinted against the real ledger's structure: the
Necromancer's synthetic NULL has null_p95 = 1, the real one had 2, the Cleric's has
7-10. "Instrument at floor" claims need a rule requiring the synthetic null floor to
bracket the historical one before the conclusion is admitted.


## 7 VERDICT

Outcome the record supports in the Cleric's reading: NO_FAIR_TEST_ON_RECORD, fair_test
UNFAIR -- the Necromancer's classification, on different grounds. The experiment could
not have answered its own question: the premise's value measure had no consumer and no
cost producer at birth (DESIGN_ERROR), the Layer-2 tests ran on a ledger whose outcome
column was mostly the pipeline's own state (MEASUREMENT_ERROR, primary), the statistic
that carried the final verdict has a chance floor at the effect size (INSTRUMENT_ERROR),
and the pre-committed discriminating test stopped at 84 of 100 (EXECUTION_ERROR). The
ecosystem stopping is when it died, not why. H-B as first built was fairly tested and
lost at ITER-56/57; that is on the record and belongs in the dossier.

Nearest honest neighbour: CONSUMER_BLOCKED for H-A alone.

The ONE strongest conclusion the record does NOT support: that Erebos is a TRUE_CORPSE --
that Layer-2 routing over falsification residue was fairly tested and found worthless.
Everything on the record leans that way (a refuted v1, a redesign that narrowed under
every adversarial pass, a signal that was plumbing, a trend that worsens with N), and a
resurrection reader should be told so; but the pre-committed test never ran, the ledger
it would need is gone, and the only observations that exist were made through an outcome
column that carried its own answer. Lean is not a kill. The artefact that would settle it
is named at the end of section 3.
