# HT-8a87057933 / W5 -- Pass 4 (first falsification), round 2: implementation notes

Prompt: hecate/programs/_prompts/pass4_impl_v2.md (sha256 e55576b2...2d8c).
Bound by roles/Hecate/prereg/2026-09-30_pass4_round2/PREREG.md (section
"HT-8a87057933 W5") and, for common rules, ../2026-09-30_pass4_round1/PREREG.md
and ../2026-09-29_probe_round1/PREREG.md. Written BEFORE any run.

Frozen inputs (read/imported, never modified; sha256 at start):
controls.py e7e814dc..5f4c, probe/world.py c8ec78b5..550a, spec.json 73616e52..7f36,
ATTAINABILITY.json 975988ac..4895. Everything written by this pass is in pass4/.
All scripts set sys.dont_write_bytecode = True before importing anything from
W5/ (the round-3 probe wrote W5/__pycache__ once; avoided here).

## Files and order of execution

1. NOTES.md (this file), before any code runs.
2. alt_controls.py -> alt_control_rows.jsonl + ALT_ATTAINABILITY.json. Contains the
   ALT world and ONLY its non-treatment arms (CONTROL_REF, POSITIVE_CONTROL,
   NULL_TWIN, CHEAT, CHANNEL_RESET). No core-guided repair code exists when it runs.
3. Only after ALT_ATTAINABILITY.json exists: attack.py (R, ORIG, ALT treatment)
   -> rows.jsonl, and evaluate.py -> PASS4_OUTCOME.json.

## R (replication), original W5 world

Seeds 100..109 (disjoint from round-3 seeds 0..9). Parameters unchanged
(K=8, V=8, W=32, EPS=0.03, STEPS=2400, SWITCH_EVERY=80).
Arms: CONTROL_REF, POSITIVE_CONTROL, NULL_TWIN, CHEAT from the frozen
controls.run; TREATMENT from the frozen probe/world.run (core-guided MUS
repair, imported, not copied).
PREREG: "errors ratio vs drop-oldest <= 0.50 and 10/10 seeds". Reading:
reproduced iff pooled sum errors(TREATMENT)/sum errors(CONTROL_REF) <= 0.50 AND
every one of the 10 seeds has errors(TREATMENT) <= 0.50 x errors(CONTROL_REF,
same seed). S3 (valid-deleted per UNSAT ratio) is reported, not gated.
Controls for this world variant: positive detected iff POSITIVE_CONTROL meets
frozen S1, S2, S3 (controls.clause_values/passes); cheat detected iff CHEAT meets
S1..S3 AND trips the frozen error floor (some seed errors < 0.5 x switches);
also reported: NULL_TWIN fails S1..S3 (discriminating), PC and twin not floor-flagged.

## ORIG (trivial-explanation attack), original W5 world, seeds 100..109

CHANNEL_RESET arm, no SAT/MUS: on a violated observation (the window is UNSAT
right after appending the new clause, i.e. the same trigger as every arm), drop
every stored clause about the mismatched channel.
Ambiguity: does "stored clause" include the observation just appended?
Reading chosen: no -- the new observation is kept, every OLDER window clause on
its channel k is deleted (reset the channel, then record the new observation).
This restores SAT in one step (the window was SAT before the append, so all
other channels agree). deleted / valid_deleted counted as in controls.run.
Implementation: orig_run() in attack.py is a verbatim copy of the world loop of
probe/world.run with one extra branch. Faithfulness check: orig_run is also
executed for CONTROL_REF, POSITIVE_CONTROL, NULL_TWIN, TREATMENT on seeds
100..109 and must equal controls.run / probe world.run row for row; a mismatch
is an anomaly and sets controls not detected (instrument fail).
Fires iff sum errors(CHANNEL_RESET) <= 1.10 x sum errors(TREATMENT).
Expectation stated in the PREREG: FIRE (every MUS was a same-channel pair).

## ALT world (control-first)

PREREG: "a plant whose stored clauses are relations ACROSS channel pairs, so a
conflict's minimal core spans channels and the mismatched channel does not
identify the stale clause." What changed from W5, and why:

- Task requests an ORDERED channel pair (i, j), i != j, uniform over the 56
  ordered pairs (was: one channel). Needed so an observation is a relation.
- Plant: y = (u + theta_i - theta_j) mod 8 (was u + theta_k). The output depends
  on a difference of two channel offsets, so the observation clause is the
  cross-channel relation "theta_i - theta_j == (y_obs - u) mod 8".
- SAT: the window (a set of difference constraints over Z_8) is SAT iff it is
  consistent; decided exactly by weighted union-find with potentials in Z_8
  (valid for any abelian group, no field needed). A minimal core is a cycle in
  the constraint graph, i.e. it spans >= 2 channels by construction.
- Controller: theta_hat_ij = the value of theta_i - theta_j implied by the window
  if i and j are connected in the window's constraint graph, else 0 (the
  "smallest allowed value" when all 8 are allowed, as in W5). u = (r - theta_hat) mod 8.
Everything else unchanged: K=8, V=8, W=32 FIFO, EPS=0.03 sensor noise (uniform
other value), STEPS=2400, switch every 80 steps of one uniform channel to a
uniform other value (29 switches), RNG streams seed*1000+{1,2,3} (world: theta,
switches, tasks; sensor; arm-private random drop). Task draw: i = rng_w.randrange(K),
j = (i + 1 + rng_w.randrange(K-1)) % K.

ALT arms (same trigger: UNSAT after the append; same stop rule: until SAT):
- CONTROL_REF: drop-oldest, one at a time, until SAT.
- POSITIVE_CONTROL: oracle, delete exactly the window clauses with
  theta_i - theta_j != d under the true current theta.
- NULL_TWIN: random drop (rng_a) one at a time until SAT.
- CHEAT: NULL_TWIN run with errors and valid_deleted overwritten to 0.
- CHANNEL_RESET (ORIG heuristic transferred): the violated observation mentions
  two channels i and j and nothing tells which is mismatched. Reading chosen:
  drop every OLDER window clause that mentions i or j (both endpoints; picking
  one would be arbitrary). This restores SAT in one step.
- TREATMENT (written only after ALT_ATTAINABILITY.json): core-guided, the W5
  spec rule unchanged: repeat { MUS by deletion scanning window clauses
  oldest-first using only the generic SAT test; delete the clause with the
  smallest timestamp in that MUS } until SAT.

ALT clauses (PREREG: "Pass iff core-guided errors <= 0.50 x drop-oldest AND
<= 0.80 x the channel-reset heuristic, 10 seeds"). Reading: pooled over the 10
seeds, seeds 100..109 in the ALT world.
  A1: sum errors(X) / sum errors(CONTROL_REF) <= 0.50
  A2: sum errors(X) / sum errors(CHANNEL_RESET) <= 0.80
Control-first eligibility (ALT_ATTAINABILITY.json): every clause attainable
(POSITIVE_CONTROL meets it) and discriminating (NULL_TWIN fails it); cheat
detected (CHEAT meets A1 and A2 AND trips the error floor: some seed with
errors < 0.5 x switches); PC and twin not floor-flagged. Floor rationale as W5:
after a switch of channel c the first request touching c errs with prob >= 7/8
for any policy not told of the switch. If any condition fails: ALT
NOT_ELIGIBLE, no treatment is run for the ALT world, no repair.
Diagnostic (no MUS code, recorded in the control rows): at each UNSAT event,
whether the violated observation's channels contain the channel that switched
most recently; and CHANNEL_RESET's valid deletions (valid clauses thrown away
because the mismatched channel does not identify the stale clause).

## Predicate (in evaluate.py code)

controls_detected = R-world PC and cheat detected AND faithfulness ok AND (ALT
world PC and cheat detected, recomputed from attack.py's rerun and equal to
ALT_ATTAINABILITY.json statuses, when ALT is eligible).
ALT status: NOT_ELIGIBLE if ALT_ATTAINABILITY not eligible; else PASS iff A1 and
A2 hold for TREATMENT; else FAIL.
predicate: PARK if ALT != PASS or not controls_detected; else
ORIG_FOSSIL_ALT_PASS if ORIG fired; else SURVIVES if R reproduced; else PARK
(ambiguity: R failing with ORIG not firing and ALT passing is not named in the
PREREG; SURVIVES requires R, so PARK is chosen and recorded).

## Seeds, attempts, budget

R/ORIG seeds 100..109; ALT seeds 100..109 (a different world, same seed ids).
One attempt planned; a rerun only for a described crash or bug. Budget <= 10
CPU core-minutes total, measured with time.process_time in each script.
No threshold or parameter is changed after any treatment statistic is printed.
