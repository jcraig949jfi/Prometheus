# CLERIC challenge -- grave NOUS (Rhadamanthus native trial, 2026-09-11)

Cleric pass over engine/necropolis/dossiers/nous.dossier.json (HEAD 03ac0249b on branch
rhadamanthus/native-trial-2026-09-11). Everything below was executed from the worktree root;
no network, no database, no git writes, no validate.py run in the tree. All five Necromancer
scripts were re-executed and their result JSONs compared byte-for-byte against the committed
files (hash prefixes dc2b3f5b / 5b5979a0 / f817e188 / 4c9cca92 / 6abcda64): four of five are
byte-identical on re-execution; nous_forge_join_result.json is not (C-1). The committed result
files were restored to their original bytes afterwards. One cleric script was added:
cleric_strata_and_orphans.py -> cleric_strata_and_orphans_result.json (numpy only, seed 7,
2000 permutations, deterministic stratum order, no hephaestus import).

## 1. WHAT THE NECROMANCER CLAIMS (quoted)

cause_of_death_stack (autopsy.cause_of_death_stack):

- HYPOTHESIS: NOT_EXAMINED, cause_classes []. "'Cross-field concept collisions yield computable
  reasoning criteria at a rate above a random-triple baseline' was never put to a controlled
  test: no non-Nous or random-triple input was ever forged under a fixed judge, and the only
  external outcome (forge status) is dominated by the forge calendar."
- DESIGN: INVALID [DESIGN_ERROR], load_bearing true. "The design cannot answer its own question:
  (a) the selection score is the generating model's self-rating of its own completion, averaged
  over the three dimensions the README itself reports as non-predictive of forge (weight 0.000)
  while excluding the one it reports as predictive (implementability); (b) no control arm;
  (c) the prompt was changed mid-series (theorist -> engineer, commit da42cc7e0) and the shipped
  README kept the v1-regime yield claim."
- IMPLEMENTATION: VALID. "scorer replay reproduces 5918/5918 stored scores from stored text;
  rating parse failures are 1.5% overall and concentrated in the 800-max_tokens run (79/87)".
- CONFIGURATION: INVALID [CONFIGURATION_ERROR], load_bearing false. "manifest.yaml default_model
  is qwen/qwen3.5-397b-a17b and the README advertises a 397B model, but 5915/5918 entries were
  produced by nemotron-3-super-120b-a12b (unlimited=true runs); Nous reads its key from
  agents/nous/.env or the environment (no keys.py)".
- EXECUTION: VALID. "Nous ran: 12 runs with data over 2026-03-24..03-28 (5918 entries ...), plus
  evidenced uncommitted output through 2026-04-02 (1212 ledger orphans incl. 9 priority
  triples)".
- INSTRUMENTATION: INVALID [INSTRUMENT_ERROR], load_bearing false. "No run log, no token/cost
  accounting, no STATUS/Agora emission until 2026-05-13 ..., and the 03-31..04-02 output was
  never committed, so the record of what ran is the forge's ledger rather than Nous's own. The
  800-token truncation made 87/87 ratings unparseable in run 115258 before rescore."
- MEASUREMENT: INVALID [MEASUREMENT_ERROR], load_bearing true. "The measurement carries its
  answer: the composite is the LLM's self-rating; its apparent forge signal (pooled AUC 0.755)
  is the forge calendar crossed with the prompt switch, and vanishes within forge day (0.519,
  p=0.12 ...). The score distribution moved from 41.8% high_potential to 0.84% when the prompt
  changed with the model held fixed: the score measures the prompt."
- INTERPRETATION: INVALID [INTERPRETATION_ERROR, IDENTITY_PROVENANCE_ERROR], load_bearing true.
  "Later readers turned an input dependency and a launch pairing into a 'zombie gate', a
  lower-bound date into 'stopped', an unread generator into 'exhaust', and a superseded lineage
  into a stall".
- ECOSYSTEM: INVALID [ECOSYSTEM_FAILURE], load_bearing true. "Nous had exactly one coded consumer
  (the forge) and one feedback producer (Coeus ...); within six days the pipeline forked to
  nous_t2/nous_t3 and the March forge lineage was abandoned, the M4 daemon shelved, and the key
  later lapsed. The shelving is an ecosystem event: nothing in the record shows Nous failing on
  its own terms before it was superseded."

fair_test: "UNFAIR", scope "All committed runs (2026-03-24..03-28) and the forge windows that
consumed them (03-24..04-02, 05-16..05-28)." Finding: "the selection score is a self-rating
with no external criterion (MEASUREMENT, load-bearing), there is no control arm and the prompt
changed mid-series with the claim frozen at v1 (DESIGN, load-bearing). The forge outcome cannot
serve as the criterion because it is instrument-dominated (58% -> 2.5% by day) and the
stratified test is null."

primary_cause: "DESIGN_ERROR". contributing_causes: ["MEASUREMENT_ERROR", "ECOSYSTEM_FAILURE",
"INTERPRETATION_ERROR"]. classification: "NO_FAIR_TEST_ON_RECORD". Rationale (part): "Chosen
over SUPERSEDED_BUT_ORGANS_SALVAGEABLE because supersession (nous_t2) explains why it stopped,
not whether it worked. Not TRUE_CORPSE: the hypothesis was never tested. Not optimistic: the
record also fails to show Nous doing anything a random-triple generator would not have done."

Also attacked: identity.historical_machine "M4 (ROSTER label ...)"; observed_history.run_period
"forge ledger holds 1212 Nous-shaped keys attempted 2026-03-31 10:53 .. 2026-04-02 12:43 with
no committed Nous record"; uncertainty items 2-5.

## 2. OBJECTIONS

### C-1  The stratified null is not reproducible (MINOR)
Claim attacked: MEASUREMENT evidence "stratified_by_forge_day" null_p025 0.4638 / null_p975
0.5345 / null_mean 0.4994 / frac_null_ge_obs 0.12 (nous_forge_join_result.json).
Executed: python engine/necropolis/dossiers/nous_evidence/nous_forge_join.py from the worktree
root -> 0.4669 / 0.5302 / 0.5011 / 0.155; observed AUC 0.5194 identical. Cause: strat_auc and
the null loop iterate `set(strata)` (hash-randomised order) so the seeded RNG draws in a
different order per process. cleric_strata_and_orphans_result.json A1 (sorted strata, 2000
perms): 0.4647 / 0.533 / 0.5001 / 0.138. Rule: LAW N17 requires VALID/INVALID to rest on
"executed evidence"; an executed number a second party cannot reproduce is weaker than the
dossier presents it. The conclusion (null) survives every rerun; only the p-value moves.

### C-2  Weak point 1 (regime x day interaction) is closed -- against Nous, not for it (MINOR, verdict-preserving)
Claim attacked: uncertainty item 4, "a regime x day interaction cannot be excluded at these
counts", and the MEASUREMENT finding that the signal "vanishes within forge day".
Executed: cleric_strata_and_orphans_result.json:
- A2 strata = regime x forge_day (28 strata, n 3449, 413 forged): composite AUC 0.4577, null
  mean 0.4994, null 2.5%..97.5% = 0.4649..0.5348, frac_null_ge_obs 0.9905.
- A3 v1 only, day strata: 0.4519, frac_null_ge_obs 0.989. A4 v2 only: 0.4774, 0.7605.
- A5 the Necromancer's own per-regime unstratified blocks re-run: v1 0.5757 (null p975 0.5372,
  0/2000 nulls above), v2 0.6527 (null p975 0.554, 0/2000 above) -- a within-regime signal
  DOES exist unstratified, which is exactly what weak point 1 feared.
- A6 shows why it is a confound: within v1, mean composite and forge rate fall together by
  forge day (03-25: 7.535 / 0.583; 03-26: 7.283 / 0.263; 03-27: 7.118 / 0.196); within v2 the
  same (03-25: 6.30 / 0.5625 ... 05-28: 4.33 / 0.0). Per stratum, the v1 score is at ceiling:
  222/223 entries on 03-25 and 498/502 on 03-26 have composite >= 7.
Reading: once regime AND day are held fixed, the Nous composite ranks forge survivors at or
slightly BELOW chance (99% of stratified nulls exceed it; two-sided about 0.02). The
Necromancer's null is upheld and its named weakness is removed; the per-regime AUCs it reported
in v1_/v2_attempted_excl_apifail should not be read as signal. Rule: LAW N4 (state the strongest
proposition the evidence kills, and no stronger) -- the record now kills "the self-rating ranks
forgeable triples within a fixed judge state", which the dossier stops short of saying.

### C-3  Weak point 2 (orphan attribution "by shape only") is answerable from the record (MINOR, evidence upgrade)
Claim attacked: uncertainty item 2 "a second producer of Nous-shaped triples is not excluded by
the tree"; run_period "1212 Nous-shaped keys".
Executed: cleric B1: 1212 orphan keys = 1212 rows, every key has exactly 3 concepts and all
1212 keys use only the 95-name dictionary; rows by day 03-31 776 / 04-01 81 / 04-02 355; first
row 2026-03-31T10:53:24, last 2026-04-02T12:43:47; frames A..H; reasons api_call_failed 739,
trap_battery_failed 292, validation 148, scrap 31, forged 2. B3: 1726 rows on 03-31 match
committed Nous keys (the frame replay), so 03-31 = 1726 replayed + 776 new.
Uncited record that pins the producer:
- roles/PipelineOrchestrator/athena_forge_status_20260329.md: "Nous | Running | 2026-03-29
  03:50 | 1,718 new responses in current run (22+ hours)" -- a Nous run that no commit holds.
- forge/STATUS_T1_T2_20260403.md Backlog: "Nous last run 20260402_090737 | 150 responses, 95
  concepts, model: nemotron-3-super-120b-a12b"; "Nous idle since Apr 2 12:43 | 3 unprocessed
  files"; "Hephaestus | Idle since Apr 2 12:43". 12:43 is the last orphan timestamp to the minute.
- .gitignore commit d5b0130e1 (2026-03-29 17:49) added agents/nous/runs/ and
  agents/hephaestus/runs/: every Nous run started after 03-29 is uncommitted BY RULE, which is
  the whole reason the 03-29..04-02 runs are missing from the tree.
- agents/hephaestus/src/hephaestus.py at 9e189d683 (04-01) has exactly one ingestion path,
  load_nous_results / load_all_nous_results over agents/nous/runs/*/responses.jsonl; no code
  path generates triples without Nous. replay_multiframe.py likewise.
- agents/hephaestus/logs/hephaestus_2026-04-02.jsonl (tracked) carries the two 04-02
  forge_success events that are the 2 forged orphans.
Rule: LAW N11 (evidence beats old verdicts) and LAW N15 (HEAD is a lower bound). The orphans
are Nous output by contemporaneous record, not by shape. Uncertainty item 2 should be closed;
EXECUTION evidence should cite the two status documents.

### C-4  ECOSYSTEM: "superseded", "M4 daemon shelved" and the cause class are not what the record shows (MATERIAL)
Claim attacked: ECOSYSTEM finding (quoted above) and the rationale sentence "supersession
(nous_t2) explains why it stopped".
Executed/read:
- roles/PipelineOrchestrator/journal_20260402.md defines the tiers: T1 = Nous concept triples,
  T2 = tool combinations, T3 = substrate, "Tiers run in parallel -- lower tiers never stop
  (substrate generators)", "Let T1 keep running 24/7 as substrate generator". nous_t2 is an
  ADDED tier over a different input (tool combinations), not a successor of the triple engine.
- The dated stop coincides with the consumer's instrument failing, not with nous_t2:
  athena_forge_status_20260329.md "Hephaestus | Stopped | 2026-03-28 20:04 | Last run: 0/98
  forged (API failures + battery fails)", "NVIDIA API (Qwen 397B) appears to still be degraded";
  STATUS_T1_T2_20260403.md "API forge yield 0% last run | 20 attempts, all scrap";
  journal_20260403.md root-causes the API forge at P0 (Frame H prompt/validator contradiction),
  P1 (frames E/F/G), P2 (missing import) -- all forge-side. cleric B1: 739 of the 1212 orphan
  rows are api_call_failed.
- The operator re-routed forging away from the API consumer: commit c181461cd (03-28) "v7:
  Opus-forged gap-targeted tools -- 84/89 coverage (94%), bypass NVIDIA API";
  athena_forge_status_20260329.md "backlog is not urgent -- the v7 Opus-forged tools already
  pushed coverage to 97.8%"; journal_20260402.md "APIs mine cheap ore in bulk (~8% yield) ...
  Claude Code forges gems (100%)".
- No commit 2026-03-24..04-04 on agents/nous or agents/hephaestus states a shelving reason
  (git log read-only: 2f3e4eb6f, da42cc7e0, 2a186ba24, 2e75abf0f, 923d11c66, 5573808c7,
  6daaada54, 302c002d3, 921c4f7b8, c181461cd, 6058e6eb1, 9e189d683, dc2c800ba, b674a9976,
  4b250fa97). Repairs in that window are all forge-side (backoff/retry 9e189d683, aggie-api
  fallback dc2c800ba, Frame H + validator b674a9976/4b250fa97).
- "M4": pivot/agents_nous_resume_2026-05-13.md line 6 "Machine assignment: M4 (per James,
  2026-05-13 session)" is a FORWARD assignment made six weeks after the last run; the only
  launch record, run_forge_pipeline.bat (2e75abf0f, 4b250fa97), starts Nous from an F-drive
  checkout with `--unlimited --delay 2.0` and names no machine. The dossier's
  identity.historical_machine says "unverified" but the ECOSYSTEM finding and run_period then
  use "the M4 daemon" as fact.
- Charter vocabulary: ECOSYSTEM_FAILURE = "the producer may have worked, but nothing useful
  consumed what it emitted". The dossier's own numbers say the opposite: 95.1% of committed
  output attempted by the forge, 385 forged keys in the ledger, the humanreadable tool tree
  built from them. What the layer actually describes is consumer-instrument degradation plus an
  operator attention re-allocation -- for which the charter has no class (D-2).
Rule: LAW N17 (cause class must name the defect the layer shows), LAW N14 (an unreachable API is
a fact about the apparatus), LAW N4. Verdict INVALID stands (the consumer seam did fail Nous:
its output was API-forged at 0-8% then not forged at all); the finding, the "superseded" and
"M4 daemon shelved" clauses, and the rationale sentence do not.

### C-5  INSTRUMENTATION "No run log" is false in mechanism (MINOR)
Claim attacked: "No run log ... the record of what ran is the forge's ledger rather than Nous's
own."
Executed/read: agents/nous/src/nous.py line 36 `log_file = NOUS_ROOT / "nous.log"` with a
logging.FileHandler, present since the first commit 2f3e4eb6f; `*.log` is gitignored;
scripts/check_forge_pipeline.py (commit 9e189d683, 04-01) monitors agents/nous/nous.log and the
runs backlog, i.e. the log existed and was consumed by monitoring; the resume doc calls
nous.log the "top-level run log". The gap is record PRESERVATION (gitignore d5b0130e1 plus
`*.log`), not an apparatus that "could not observe the proposed phenomenon" (charter definition
of INSTRUMENT_ERROR). What legitimately remains under INSTRUMENTATION: no token/cost accounting,
no STATUS/Agora emission before 05-13 (Keeper census: 0 Nous rows in agora.intelligence_outputs,
15502 rows total -- consistent with the dossier). The 800-token truncation belongs to
CONFIGURATION (C-6). Rule: LAW N17 cause-class table. Verdict INVALID non-load-bearing stands on
the narrower grounds.

### C-6  CONFIGURATION is INVALID for the wrong reason (MATERIAL: same verdict, different defect)
Claim attacked: the model mismatch as a CONFIGURATION_ERROR.
Executed/read: nous.py line 474 `--model` default is
os.environ.get("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b"); run_forge_pipeline.bat
passes no --model; nothing under agents/nous/src reads configs/manifest.yaml (grep: no match);
the README CLI table itself lists the nemotron default. nous_run_census_result.json
totals.models_overall = nemotron 5915, qwen 3 (re-executed, byte-identical). So Nous ran on its
coded default; the "397B" claims in README prose and manifest.yaml are documentation that no
code consumes -- an INTERPRETATION/provenance defect (README yield claim family), not a bad
parameter. The honest CONFIGURATION_ERROR is the one the Necromancer filed under
INSTRUMENTATION: max_tokens 800 in run 20260324_115258 ("original 800 caused 100% rating parse
failures", README; 87/87 unparseable before rescore.py) -- a cap (charter: "bad threshold,
comparator, parameter regime, model, dataset, path, cap"), repaired, non-load-bearing. The
.env-versus-keys.py point is a program convention, not a configuration of the experiment.
Rule: LAW N17 cause-class table.

### C-7  DESIGN clause (a) leans on a README claim the dossier's own numbers refute (MINOR)
Claim attacked: "the three dimensions the README itself reports as non-predictive of forge
(weight 0.000) while excluding the one it reports as predictive (implementability)".
Executed: nous_forge_join_result.json auc_implementability 0.2564 (ALL_attempted), 0.2683
(excl. api fail), 0.4182 within forge day; cleric A2 per-stratum implementability is not
computed but the day-stratified figure is below 0.5. Implementability is NOT predictive under
the dossier's own stratified reading; the README weight table is the same calendar confound
the MEASUREMENT layer diagnoses. Clause (a) should rest on "self-rating with no external
criterion" alone; clauses (b) and (c) carry the layer. Rule: LAW N11 (evidence beats old
verdicts -- including the README's).

### C-8  Script hygiene (MINOR)
nous_forge_join.py imports agents/hephaestus/src/hephaestus.py, which on import writes
agents/hephaestus/hephaestus.log, agents/hephaestus/logs/hephaestus_<today>.jsonl and
src/__pycache__ (all gitignored, but the evidence run mutates the specimen tree).
nous_salvage_reproduce.py writes to the system temp directory and records that drive-letter
path in its result JSON. Rule: the brief's "no drive letters in code"; LAW N2 spirit (evidence
runs should not touch the corpse).

Not objected to (re-executed, byte-identical): nous_run_census (12 runs with data, 5918
entries, models_overall), nous_scorer_replay (5918/5918 reproduced, composite definition),
nous_gate_trace (loaders, launch coupling, 1212 orphans, descendants), nous_salvage_reproduce.

## 3. THE CORPSE CASE

Strongest honest argument for TRUE_CORPSE / HYPOTHESIS_FAILURE:
1. The only thing Nous adds over a dictionary sampler is its selection score, and within a fixed
   judge state that score is at or below chance (C-2: AUC 0.4577, 99% of stratified nulls above;
   v1 at ceiling, 222/223 >= 7). As a SELECTOR Nous demonstrably did nothing.
2. The one consumer's yield on Nous input fell 58% -> 26% -> 10% -> 0% (by_forge_day; 04-02:
   "20 attempts, all scrap"), and the ecosystem reached 97.8% coverage by a route that did not
   use the API forge (c181461cd, athena_forge_status_20260329.md) -- the market verdict was
   that Nous-fed API forging was not worth its cost ("~8% yield" vs "100%").
3. Ledger totals: 385 forged of 6651 keys (5.8%), 739/1212 of the last window api_call_failed.
Why the record does not support it: (i) no random-triple or non-Nous arm was ever forged under
any judge, so the 5.8% has no baseline; (ii) the forge outcome is judge-state dominated (A6:
forge rate tracks day, not score) so the yield collapse is a fact about the forge's API, not
about the triples (LAW N14); (iii) point 1 kills the self-rating, not the triple hypothesis --
"cross-field triples are forgeable above random" was never scored by anything except the
forge under drifting instrument state; (iv) validate.py refuses HYPOTHESIS_FAILURE without
fair_test FAIR and refuses TRUE_CORPSE without it. The single artifact that would change this:
one forge run under a frozen judge with api-state rows excluded, N Nous triples interleaved with
N uniform dictionary triples (and ideally N same-field triples), with the forge outcome as the
criterion -- i.e. exactly the dossier's nous-d1-control-arm. Nothing of that shape exists in
agents/, forge/, roles/PipelineOrchestrator/ or engine/queues/CONSUMPTION.jsonl (the 08-20
SALVAGE-NOUS row lifts the dictionary; it tests nothing).
Conclusion: NO_FAIR_TEST_ON_RECORD is not being used optimistically. The dossier's sentence
"the record also fails to show Nous doing anything a random-triple generator would not have
done" is UNDER-stated after C-2: the record shows the selector ranking at or below chance.

## 4. THE RESURRECTION-BIAS CASE

Where the Necromancer reads toward salvage beyond the evidence:
1. "nothing in the record shows Nous failing on its own terms before it was superseded"
   (ECOSYSTEM). C-2 shows the selector failing on its own terms inside every fixed judge state;
   the dossier had the per-regime AUCs (0.5757 / 0.6527) in hand and did not run them down.
2. The "superseded by nous_t2" story casts Nous as a victim of design succession; the record
   (journal_20260402: T1 "never stops") shows the operator intended it to keep running and it
   simply stopped being worth running when the API forge failed and Claude Code forging won.
   That is closer to a consumer judgment on Nous's output value than the dossier admits.
3. "Load-bearing: the '20-30% warrant forging' and 'high-potential' framing that later dossiers
   inherited" -- measured high_potential is 41.8% (v1) and 0.84% (v2); neither is 20-30%, so the
   README claim is not even a v1 fossil, it is unsourced. The dossier treats it as provenance
   for downstream readers rather than as a false claim in its own right.
4. The descendant nous-d1-control-arm inherits the forge as judge. Under A6 the forge judge is
   the least stable object in the record; "frozen judge" is asserted, not designed.
5. EXECUTION VALID is right, but it was reached by inference from ledger shape when the two
   status documents (C-3) were on the tree; the Necromancer stopped at the first channel.

## 5. STACK AMENDMENTS DEMANDED

- HYPOTHESIS: NOT_EXAMINED, [] -- retain. Add to finding: "the selection score is at or below
  chance within regime x forge-day strata (cleric A2), which kills the selector, not the
  premise." Evidence: dossiers/nous_evidence/cleric_strata_and_orphans_result.json (A2, A3, A6).
- DESIGN: INVALID [DESIGN_ERROR] load_bearing true -- retain verdict; strike the README-weight
  clause of (a) (C-7); keep self-rating / no control arm / mid-series prompt change. Evidence
  add: cleric A2, A5, A6.
- IMPLEMENTATION: VALID -- retain (scorer replay byte-identical on re-execution).
- CONFIGURATION: INVALID [CONFIGURATION_ERROR] load_bearing false -- retain verdict, replace
  finding: max_tokens 800 cap in run 20260324_115258 (87/87 ratings unparseable; repaired by
  max_tokens 2048 + rescore.py, C-6). Withdraw "wrong model": coded default nemotron
  (agents/nous/src/nous.py line 474), launch without --model (run_forge_pipeline.bat), manifest
  unread. Move README/manifest 397B mismatch to INTERPRETATION evidence.
- EXECUTION: VALID -- retain; evidence add: roles/PipelineOrchestrator/athena_forge_status_
  20260329.md (Nous running 03-29, 1,718 responses), forge/STATUS_T1_T2_20260403.md Backlog
  (last run 20260402_090737, idle since Apr 2 12:43), .gitignore@d5b0130e1, cleric B1/B3.
  Reword run_period "Nous-shaped keys" -> "Nous output by contemporaneous record".
- INSTRUMENTATION: INVALID [INSTRUMENT_ERROR] load_bearing false -- retain verdict; finding
  becomes: no token/cost accounting; no STATUS/Agora emission before 05-13 (Keeper census 0
  rows); run log and post-03-29 runs existed but were gitignored (record preservation, not
  instrument absence). Evidence: agents/nous/src/nous.py line 36, scripts/check_forge_pipeline.py
  @9e189d683, .gitignore@d5b0130e1, _keeper_evidence/intelligence_outputs_census_result.json.
- MEASUREMENT: INVALID [MEASUREMENT_ERROR] load_bearing true -- retain; replace the
  nondeterministic null with cleric A1 (0.5194, frac 0.138) and add A2 (0.4577, frac 0.9905);
  state that the per-regime unstratified AUCs are calendar confounds (A5 + A6).
- INTERPRETATION: INVALID [INTERPRETATION_ERROR, IDENTITY_PROVENANCE_ERROR] load_bearing true
  -- retain; add the README "20-30%" and "397B" claims as unsourced, and "M4" as a forward
  assignment (pivot/agents_nous_resume_2026-05-13.md line 6) read back as history.
  identity.historical_machine -> "unknown (launch script starts Nous from an F-drive checkout;
  M4 first appears 2026-05-13 as a forward assignment)".
- ECOSYSTEM: INVALID [ECOSYSTEM_FAILURE] load_bearing true -- retain verdict and class only
  because the charter admits no other class on this layer (D-2); finding becomes: the single
  consumer's API instrument degraded 03-28..04-02 (0/98, then 20/20 scrap; 739/1212 api_call_
  failed), the operator re-routed forging to Claude Code (c181461cd; 97.8% coverage without the
  API forge), and the pipeline idled 2026-04-02 12:43; nous_t2 is an added T2 tier over tool
  combinations, T1 was designed to keep running. Strike "superseded", "M4 daemon shelved".
  Evidence: journal_20260402.md, journal_20260403.md, athena_forge_status_20260329.md,
  forge/STATUS_T1_T2_20260403.md, cleric B1.
- fair_test UNFAIR (scope unchanged) -- retain. primary_cause DESIGN_ERROR -- retain (a
  control-free, self-scored design cannot be rescued by any measurement; C-2 makes the
  MEASUREMENT layer a consequence, which is the Necromancer's own argument). contributing
  [MEASUREMENT_ERROR, ECOSYSTEM_FAILURE (reworded), INTERPRETATION_ERROR] -- retain.
  classification NO_FAIR_TEST_ON_RECORD -- retain. Rationale: strike "supersession (nous_t2)
  explains why it stopped"; replace with the C-4 account.
- uncertainty: close items 2 and 4; rewrite 3 as "the stop is dated (04-02 12:43) and
  coincides with API-forge failure and the Claude Code re-route; no commit or journal states a
  decision to shelve Nous"; item 5 stands.

## 6. DOCTRINE DEFECTS (numbered, not resolved)

D-1 primary_cause among several load-bearing INVALID layers (DESIGN, MEASUREMENT,
    INTERPRETATION, ECOSYSTEM): the charter and validate.py give no ordering rule; "upstream
    wins" is the Necromancer's convention, not doctrine (weak point 3 is unresolvable by rule).
D-2 The ECOSYSTEM layer admits one class, ECOSYSTEM_FAILURE = "nothing useful consumed what it
    emitted". Consumer-instrument failure, operator attention re-allocation and deliberate
    shelving have no class, so the layer is forced to misuse the one it has (C-4).
D-3 load_bearing has two readings in one dossier: "carried the historical result" (DESIGN,
    MEASUREMENT) versus "carried the recorded status" (ECOSYSTEM). validate.py treats them
    identically for UNFAIR only within DESIGN..MEASUREMENT.
D-4 A mid-series prompt change is filed under DESIGN; the charter's CONFIGURATION_ERROR text
    ("parameter regime") covers it equally. No rule decides.
D-5 Record not preserved (gitignored logs and runs) has no layer or class: INSTRUMENT_ERROR
    requires an apparatus that could not observe; the apparatus observed and the record was
    discarded (C-5).
D-6 "Executed evidence" (LAW N17) does not require determinism; a hash-order-dependent null
    passed the Necromancer's own bar (C-1).
D-7 fair_test scope includes the May forge windows (05-16..05-28), where a later forge version
    re-ran March Nous keys. Whether a later consumer's re-run is part of the organism's test is
    undefined.
D-8 Classification collision: NO_FAIR_TEST_ON_RECORD / MEASUREMENT_FAILURE / SUPERSEDED_BUT_
    ORGANS_SALVAGEABLE were separated by argument in the rationale; the validator only enforces
    UNFAIR for the first. Two Necromancers could pick differently on the same stack.
D-9 identity.historical_machine carries a ROSTER label the pass calls unverified, and the
    schema has no UNKNOWN value or evidence requirement for it; the label then leaks into
    findings as fact.
D-10 The brief says "eight charter outcomes"; CHARTER.md lists thirteen classifications. The
    cleric cannot tell which list the Keeper adjudicates against.

## 7. VERDICT

Outcome the record supports in my reading: NO_FAIR_TEST_ON_RECORD, fair_test UNFAIR,
primary_cause DESIGN_ERROR -- the Necromancer's outcome, with the ECOSYSTEM finding rewritten
(C-4), CONFIGURATION regrounded (C-6), and the measurement case strengthened (C-2). No objection
reaches FATAL: nothing found changes fair_test, primary_cause or classification. TRUE_CORPSE is
not reachable on this record (section 3); CAPABILITY_BOUND is not argued by anyone and no
capability frontier is named; SUPERSEDED_BUT_ORGANS_SALVAGEABLE fails because the "successor"
was an added tier, not a replacement.

The ONE strongest conclusion the record does NOT support: "supersession by forge/v2/nous_t2
explains why Nous stopped, and the M4 daemon was shelved." The record dates the stop to
2026-04-02 12:43, ties it to the consumer's API failure and the operator's re-route to Claude
Code forging, shows T1 was designed to keep running beside T2, and contains no evidence that
Nous ever ran on M4.
