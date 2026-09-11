# CLERIC -- Pollux (Necropolis first native trial, Rhadamanthus, 2026-09-11)

Role: challenge both the original experiment and the Necromancer. Read-only on the
tree except this file and cleric_*.py / cleric_*_result.json in this directory. No
database, no network, no validate.py run in the worktree. All Necromancer numbers
below were RE-EXECUTED, not read (section 2, C-0).

Evidence I executed (all from the worktree root, offline):

    pollux_rescan.py, pollux_instrument_null.py, pollux_consumer_trace.py,
    pollux_record_census.py     -- re-run via module import with OUT redirected to
                                   scratch; deep-diffed against the on-tree JSONs:
                                   0 / 0 / 0 / 0 differing values.
    cleric_chance_floor.py      -- NEW: PROMOTED chance floor on the REAL Mahler
                                   subsets, three nulls, seed 20260911, 1000 draws.
    cleric_census_fit.py        -- NEW: can code + v0.5 + any May verdict map
                                   produce P69's 86/39/161 and 54/56?
    git log/show (read-only)    -- charon/agents/pollux/ (2 commits, no repairs),
                                   prometheus_math/databases/_mahler_data.py
                                   (last data commit 2026-05-03, before the run).
    Keeper second channel       -- _keeper_evidence/intelligence_outputs_census_
                                   result.json, fleet_halt_census_result.json.
    Historical certificates     -- AGENT_AUTOPSIES.jsonl:18 (P69), AUTOPSY_TAXONOMY.md
                                   clusters 2 and 4, COMPONENT_DISPOSITION_PLAN_2026-06-23
                                   row 34, COMPONENT_DOSSIERS_2026-06-24.md Pollux section,
                                   roles/Ergon/GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md:32-56.

---------------------------------------------------------------------------------
## 1  WHAT THE NECROMANCER CLAIMS (quoted from pollux.dossier.json)

cause_of_death_stack:

  HYPOTHESIS      VALID     cause_classes []      "The question - do two Mahler-measure
                            subsets share a spacing profile beyond what scale explains -
                            is coherent and answerable: the normalized statistic is
                            non-degenerate on real data, varies between pairs (-0.69 to
                            +0.47), and a label-permutation null distinguishes some pairs
                            from chance (T3). It was never fairly tested, so it is neither
                            confirmed nor falsified."
  DESIGN          INVALID   [DESIGN_ERROR]          load_bearing true
                            "...hard-coding 'truncate the larger to its n smallest values'
                            - a choice T5 shows decides the verdict ... thresholded
                            corr_norm at 0.30 with no null, no chance floor and no seed
                            replication (T4: PROMOTED rate under independence up to 0.33)
                            ... settle policy excluded UNVERIFIED so non-settling pairs
                            consumed the run (replay: 256/286 rows on three pairs)."
  IMPLEMENTATION  INVALID   [IMPLEMENTATION_ERROR]  load_bearing true
                            "corr_raw = _spearman(sorted(a_vals)[:n], sorted(b_vals)[:n])
                            ... equals 1 identically ... The loader also returns values
                            already sorted by M, so even a non-sorting implementation of
                            the same design would have produced 1.0"
  CONFIGURATION   VALID     cause_classes []
  EXECUTION       VALID     cause_classes []      "Pollux executed as written for the
                            whole swarm window: 286 ticks, every one success=true ...
                            Caveat: the second channel was written by the daemon itself
                            in the same tick as the ledger row (single mechanism)"
  INSTRUMENTATION INVALID   [INSTRUMENT_ERROR]      load_bearing true
  MEASUREMENT     INVALID   [MEASUREMENT_ERROR]     load_bearing true
                            "...against a label-permutation null one PROMOTED pair fails
                            (deg14 p=0.093) and the two that pass (salem p=0.014,
                            small_large p=0.001) flip to REJECTED in 100% of random
                            size-n subsamples (T5)."
  INTERPRETATION  INVALID   [INTERPRETATION_ERROR]  load_bearing false
  ECOSYSTEM       INVALID   [ECOSYSTEM_FAILURE]     load_bearing false

fair_test.verdict: "UNFAIR"
primary_cause: "DESIGN_ERROR"
contributing_causes: ["IMPLEMENTATION_ERROR", "INSTRUMENT_ERROR", "MEASUREMENT_ERROR",
                      "INTERPRETATION_ERROR", "ECOSYSTEM_FAILURE"]
disposition.classification: "NO_FAIR_TEST_ON_RECORD"
disposition.rationale (opening): "Chosen over MEASUREMENT_FAILURE because the deepest
  load-bearing INVALID is DESIGN: with the tautological raw leg repaired, the same design
  ... would still emit verdicts with a chance floor up to 0.33 and 0% truncation
  stability (T4, T5); the measurement faults are downstream of that."
kill_boundary, NOT KILLED clause: "the hypothesis itself (some Mahler subset pairs share
  a spacing profile beyond scale) - it was never given a fair test; the normalized
  statistic is non-degenerate on real data (T3 p ranges 0.001..0.84 across pairs) and
  two pairs reject the label-permutation null, which is neither confirmation
  (truncation-unstable) nor refutation. NOT KILLED: P69's 9-facts-in-286-rows census in
  FORM ... though its numbers (86/39/161) are unreproducible from the on-tree code"
surviving_claims[3]: "The normalized correlation differs between pairs in a way a
  label-permutation null can sometimes distinguish (salem_vs_pisot p=0.014,
  small_deg_vs_large_deg p=0.001, narrow_band p=0.002) - a fact about the STATISTIC,
  not yet a fact about Mahler measures, because those values move to different
  verdicts under random subsampling."

---------------------------------------------------------------------------------
## 2  OBJECTIONS

Severity key (brief): FATAL = changes fair_test / primary_cause / classification;
MATERIAL = changes a layer verdict; MINOR = text or number amendment.

### C-0  Re-execution (no objection; the precondition for everything below)
Claim attacked: every number in the four *_result.json files.
Executed: all four scripts imported from
  engine/necropolis/dossiers/pollux_evidence/ with OUT redirected to scratch and
  main() called from the worktree root; deep-diff vs the on-tree JSONs.
  Got: rescan 0 diffs, instrument_null 0 diffs (seeded), consumer_trace 0 diffs,
  record_census 0 diffs. corr_raw max deviation 2.22e-16; T3 salem p=0.014,
  small_large p=0.001, deg14 p=0.093; T4 max PROMOTED 0.332; T5 salem/small_large
  stability 0.00; consumers wired 4, used verdict bit 0; 20/20 citations found;
  daemon commits 8c619443a (v0.5) and 43b094552 (v0.6) only.
Rule: brief ("EXECUTE, do not read"); LAW N17 "VALID (with executed evidence)".
Severity: none. Every layer the Necromancer marked rests on scripts I could run, so
no layer becomes NOT_EXAMINED on the executability ground.

### C-1  IMPLEMENTATION INVALID / IMPLEMENTATION_ERROR load-bearing is refuted by the
###      Necromancer's own T2
Claim attacked: "IMPLEMENTATION: INVALID [IMPLEMENTATION_ERROR] load_bearing true".
Executed: pollux_instrument_null_result.json T2 (re-run): for all 9 real pairs
  daemon_corr_raw_db_order = 1.0, daemon_corr_raw_shuffled = 1.0,
  daemon_corr_raw_reversed = 1.0 AND nonsorted_spearman_db_index_pairing = 1.0
  (the loader returns values sorted by M). git show 8c619443a: the v0.5 docstring
  states the intended experiment as "compute Spearman correlation BEFORE and AFTER
  mean-spacing normalization" on two subsets; the code comment at run_tick says
  "Truncate to shared length so spearman has paired indices". The author
  manufactured a pairing on purpose because the design had none.
Rule: CHARTER cause table, IMPLEMENTATION_ERROR = "the code did something materially
  different from the intended experiment". The record contains no intended
  experiment the code departed from; the Necromancer's own finding says a
  different implementation of the same design gives the same 1.0.
Consequence: the layer's defect is the DESIGN defect seen through code. Under the
  charter's load-bearing definition ("whether it changed the historical answer")
  T2 IS the measurement showing the implementation did not carry the result.
Demand: IMPLEMENTATION -> VALID, cause_classes [], or INVALID load_bearing false
  with T2 cited as the non-carrying measurement; drop IMPLEMENTATION_ERROR from
  contributing_causes.
Severity: MATERIAL.

### C-2  HYPOTHESIS VALID on T3 alone is not executed evidence of well-posedness
Claim attacked: "HYPOTHESIS: VALID ... coherent and answerable ... a label-permutation
  null distinguishes some pairs from chance (T3)".
Executed: cleric_chance_floor_result.json.
  N2 (two INDEPENDENT samples of ONE density, sizes n_a/n_b, through the daemon's
  own arithmetic): PROMOTED fraction lehmer 0.938 (A's marginal), salem 0.874 (B's
  marginal), narrow 0.760, smyth 0.448, deg10 0.284, small_large 0.265, deg18 0.216.
  N1 (independent draws from each pair's OWN marginal): salem PROMOTED 0.441 with
  p(null corr_norm >= observed 0.3985) = 0.14; small_large PROMOTED 0.327, p = 0.042
  (uncorrected; 0.38 Bonferroni over 9 pairs); deg14 PROMOTED 0.13, p = 0.06.
  What this shows: corr_norm is a similarity of gap-by-rank profiles, i.e. of
  marginal density SHAPE. It is high whenever two samples come from similar
  densities, with no relation between the sets at all. The T3 label-permutation
  null rejects exchangeability of the two MARGINALS (for salem_vs_pisot, 8513 vs
  112 values, that is the class definition), which is a different proposition
  from "share a spacing profile beyond scale". No executed evidence on the record
  examines whether the latter is well-posed for two sets of different sizes with
  no pairing relation; the daemon's design does not define it, and the dossier's
  own what_would_move_it concedes a "defined pairing relation or a two-sample
  spacing-distribution test" is still to be written.
Rule: SCHEMA HYPOTHESIS layer: "Was the proposition well-posed and reachable by an
  experiment at all?"; LAW N17: VALID requires executed evidence. T3 is executed
  evidence that the STATISTIC is non-degenerate, which the Necromancer's own text
  ("a fact about the STATISTIC, not yet a fact about Mahler measures") admits is
  not evidence about the proposition.
Demand: HYPOTHESIS -> NOT_EXAMINED (evidence: none executed on well-posedness), or
  VALID with the finding rewritten to say only "reachable by SOME experiment" and
  the T3 clause removed. Classification unaffected (validate.py requires only
  fair_test UNFAIR for NO_FAIR_TEST_ON_RECORD).
Severity: MATERIAL.

### C-3  EXECUTION VALID on self-report rows whose census the code cannot produce
Claim attacked: "EXECUTION: VALID ... 286 ticks ... the exact count a deterministic
  9-pair menu predicts".
Executed: cleric_census_fit_result.json.
  S1: the Necromancer's replay (k=0 v0.5 ticks, today's map) is 255 rows from P69
      (15/15/256 vs 86/39/161).
  S2: with a v0.5 round-robin prefix of k ticks, k=95 with the rotation index
      inherited reproduces P69's per-pair numbers EXACTLY: deg18 54, even_odd 56,
      lehmer 51, attenuates 161, seed pairs 29/29/29/28, small_large 5, narrow 5.
      The Necromancer's record_census mentions the v0.5 phase ("~22.6 h of v0.5
      ... unrecorded") but never modelled it.
  S3: under today's map k=95 gives REJECTED 62 / PROMOTED 63, never 86/39; over
      all 729 May verdict assignments of the six unpinned pairs and k in 0..139
      there are 0 exact matches. S3b: freeing even the three second-channel-pinned
      pairs, exact matches exist only at k=95 and only if THREE of the four seed
      pairs were sign_flips in May, which the second channel's first three rows
      (deg14 PROMOTED, salem PROMOTED) exclude.
  Cadence: 95 ticks between 05-24 03:08 and the v0.6 commit at 05-25 01:46 is a
      14.3-min cadence against the recorded 28-min rotation; at 28 min the 95th
      tick lands ~05-25 23:30, i.e. v0.6 would have been deployed ~22 h after its
      commit (and v0.6's 191 ticks then run at ~34 min, matching the 05-28 roster's
      "43 ev/24h"). The deploy time is nowhere on the record.
  Data: git log on prometheus_math/databases/_mahler_data.py: last commit
      2026-05-03; no data commit during or after the run. Today's subsets are May's
      subsets (this CONFIRMS the Necromancer's Q4 assumption, which the dossier
      left as an assumption).
  Two readers report the same 86/39/161: COMPONENT_DOSSIERS_2026-06-24.md:404
      ("verdicts REJECTED 86 / PROMOTED 39 / UNVERIFIED 161") read the file directly;
      P69 repeats it as patterns. If the ledger really carried 86/39, the v0.5 phase
      gave deg10+smyth 71 ticks and deg14+salem 24 (47 single-tick restarts that
      reset pair_rotation_idx plus 12 full cycles is one arithmetic that lands on 95
      exactly) -- a partial-run signature. If it did not, both readers copied a
      mis-bucketed count. The record cannot say which.
Rule: SCHEMA EXECUTION: "(runs happened, state persisted, artifacts kept, no silent
  fallbacks or partial runs)". "Runs happened" is triply recorded (second channel
  286 rows; 06-24 direct read 286 rows; ergon manifests source_stats.pollux yielded
  286) but all three are downstream of the one daemon. "State persisted, artifacts
  kept": kill_ledger.jsonl, pair_history.json, settled_pairs.json,
  candidate_pool_idx.json and artifacts/ are absent from the tree
  (consumer_trace runtime_state_on_this_tree: all false). "No partial runs": the
  tick distribution is unexplained by the code. LAW N14 / memory: attest the
  process, not the heartbeat.
Ruling on (c): VALID is admissible on the first criterion only. On the schema's
  literal conjunction the layer is NOT_EXAMINED.
Demand: EXECUTION -> NOT_EXAMINED, or VALID with the finding narrowed to "process
  ran and computed what it computes today (3 of 9 summaries verified)" and the
  census discrepancy recorded in unresolved_questions with the settling query
  (below). Classification unaffected either way.
Settling artifact (one read-only query on the Keeper's channel): SELECT
  output_summary, count(*) FROM agora.intelligence_outputs WHERE stage ILIKE
  'pollux%' GROUP BY 1; plus count(*) WHERE finished_at < '2026-05-25 23:30'.
  Prediction if the code produced the ledger: 62/63/161 by verdict and 95 rows
  before the boundary. Prediction if the two readers are right: 86/39/161.
Severity: MATERIAL.

### C-4  The published chance floor (T4, "up to 0.33") is understated ~3x on the real
###      marginals
Claim attacked: DESIGN and MEASUREMENT findings and disposition.rationale: "chance
  floor up to 0.33 (T4)"; kill_boundary "(2) ... chance floor up to 33% under
  independence".
Executed: cleric_chance_floor_result.json, summary.max_PROMOTED_floor_any_null_any_pair
  = 0.938; N2 per pair as in C-2; N1 (own marginals) salem 0.441, small_large 0.327.
  T4 used exponential and uniform marginals at capped sizes; on the tree's own
  Mahler subsets the daemon PROMOTES two independent samples of one density up
  to 94% of the time.
Rule: SCHEMA INSTRUMENTATION/DESIGN: "chance floor published"; memory doctrine
  "every metric needs a payload-reading null + published chance floor".
Demand: amend the three numbers to "up to 0.94 on the real marginals (N2), 0.44 on
  the pair's own marginals (N1)". Verdicts unchanged; this strengthens the
  Necromancer against the organism.
Severity: MINOR (number amendment; direction is against resurrection).

### C-5  The two label-permutation survivors are marginal-shape facts, and the third
###      pair does not "fail"
Claim attacked: MEASUREMENT finding "one PROMOTED pair fails (deg14 p=0.093) and
  the two that pass ... flip to REJECTED in 100% of random size-n subsamples";
  kill_boundary (2); surviving_claims[3].
Executed: cleric_chance_floor_result.json D_label_permutation_signed: PROMOTED is
  reachable only from corr_norm >= +0.30, so the relevant p is one-sided. Signed
  p: salem 0.000, small_large 0.000, deg14 0.023. All three PROMOTED pairs beat the
  label-permutation null; the Necromancer's "deg14 fails" is an artifact of
  testing |null| >= |obs| on a one-sided verdict. N1 (own marginals): salem p=0.14,
  small_large p=0.042 (uncorrected), deg14 p=0.06 -- none beats its own-marginal
  independence null after correcting for 9 pairs.
Reading for (e): neither "surviving claim under-weighted" nor "truncation
  artifact". The label-permutation result is real and says the two subsets have
  different marginal shapes (for salem_vs_pisot, the class definition; for
  small_vs_large degree, a known degree-dependence of Mahler measures). It is not
  evidence of a spacing coincidence: the pair's own densities, independently
  sampled, reproduce the PROMOTED verdict 44% / 33% of the time.
Rule: LAW N4 (kill boundary strongest-and-no-stronger, in both directions); LAW N5
  (survivors explicit and correctly stated).
Demand: surviving_claims[3] -> "The label-permutation null rejects marginal
  exchangeability for salem_vs_pisot, small_deg_vs_large_deg, narrow_band and
  (one-sided) deg14_vs_deg16; the pairs' own marginals, sampled independently,
  reproduce the observed corr_norm (N1 p = 0.14 / 0.042 / 0.06): the statistic
  reads density shape, not a relation between the sets." kill_boundary (2): delete
  "one of the three PROMOTED pairs does not beat a label-permutation null".
Severity: MINOR by the brief's scale (no layer verdict moves), but it corrects a
  kill-boundary sentence that is false as written.

### C-6  T5 "0% stable" is design sensitivity, not measurement instability
Claim attacked: MEASUREMENT finding "The measured quantity was 'which corr_norm
  interval did the n-smallest truncation land in'"; DESIGN "a choice T5 shows
  decides the verdict".
Executed: T5 (re-run): salem verdict_stable 0.00 (random-subsample REJECTED 1.0).
  For salem the daemon compares the 112 SMALLEST of 8513 Salem values (a narrow
  band near the Lehmer floor) with all 112 non-Salem values; T5 compares a RANDOM
  112 of the Salem values (spanning 1..2) with the same 112. These are two
  different comparisons of two different sub-populations; the verdict differing
  between them is the design's failure to say which sub-population it meant, not
  noise in a measurement. Under the daemon's own rule the verdict is deterministic
  (rescan deterministic_on_rerun true) and recurs under independence 44% (N1).
Rule: CHARTER MEASUREMENT_ERROR = "the recorded quantity is not the quantity the
  design named". The design named exactly this quantity (n-smallest truncation);
  the record shows the design named the wrong quantity, which is DESIGN_ERROR and
  already charged there.
Demand: move the T5 sentence out of MEASUREMENT; MEASUREMENT rests on "no null, no
  chance floor, no replication, corr_raw=1.0 recorded as an outcome" (C-4 numbers).
Severity: MINOR.

### C-7  The primary-cause ranking rule the dossier cites does not exist in doctrine
Claim attacked: disposition.rationale "Chosen over MEASUREMENT_FAILURE because the
  deepest load-bearing INVALID is DESIGN"; contradictory_evidence "the
  classification hinges on whether the deepest load-bearing INVALID is DESIGN or
  INSTRUMENTATION".
Executed: text only. SCHEMA primary_cause: "The proximate cause the evidence best
  supports. Must appear in some layer's cause_classes". CHARTER LAW N17 orders
  only the STRONG classes ("admitted only after a fair test and only after every
  other cause class has been excluded"); it says nothing about ordering among
  weak classes. CHARTER MEASUREMENT_ERROR's own parenthetical example, "a metric
  that carries its own answer", is a literal description of corr_raw = 1.
  CHARTER NO_FAIR_TEST_ON_RECORD = "the historical experiment could not have
  answered its own question", which is DESIGN_ERROR's definition verbatim;
  MEASUREMENT_FAILURE has no definition in the charter at all.
Ruling on (b): LAW N17's text forces neither. "Proximate" (schema) points at the
  layer nearest the recorded outcome (MEASUREMENT); "deepest" (dossier) is a rule
  the Necromancer wrote. My reading of the evidence: DESIGN_ERROR is the better-
  supported primary because T2 shows the tautology is implementation-independent
  and the charter's classification definition is written in DESIGN_ERROR's words
  -- but that is a doctrine reading, not a measurement, and it is filed as defect
  D-1 rather than resolved here.
Demand: keep primary_cause DESIGN_ERROR; rewrite the rationale to cite the charter's
  NO_FAIR_TEST_ON_RECORD definition and T2, and delete the "deepest" rule.
Severity: FATAL-class by the brief's definition (it concerns primary_cause and
  classification) but NOT upheld on the evidence: the outcome survives, the
  stated reason does not.

### C-8  P69's certificate is more wrong AND more right than the dossier says
Claim attacked: death_certificates P69 PARTIALLY_UPHELD; kill_boundary "NOT KILLED:
  P69's 9-facts-in-286-rows census in FORM ... though its numbers (86/39/161) are
  unreproducible from the on-tree code and the ledger is lost"; DESIGN finding
  "(replay: 256/286 rows on three pairs)".
Executed: cleric_census_fit_result.json S2/S3/S3b (see C-3). P69's per-pair census
  (54 / 56 / 51 / "n up to 56") IS reproducible from the on-tree code once the v0.5
  phase is modelled (k=95). P69's pattern split (86/39) is NOT reproducible under
  any assignment consistent with the second channel. The DESIGN finding's "256/286"
  is the k=0 replay's number; the run's own number is 161/286.
Rule: LAW N11 (evidence beats old verdicts); LAW N4 (no stronger than the evidence).
Demand: kill_boundary last clause -> "P69's per-pair census is reproduced by code +
  a 95-tick v0.5 phase; its 86/39 verdict split is not reproducible under the
  second channel's pinned rows and is shared with the 06-24 reader; the ledger is
  lost". DESIGN finding: "256/286" -> "161/286 (P69; cleric_census_fit S2)".
  unresolved_questions: add the settling query from C-3.
Severity: MINOR for the stack (INTERPRETATION stays INVALID non-load-bearing);
  MATERIAL for the certificate row, which should record both directions.

### C-9  git history (pressure point f): nothing contradicts a VALID layer
Executed: git log -- charon/agents/pollux/ : 8c619443a 2026-05-24T03:10:34-04:00
  (v0.5), 43b094552 2026-05-25T01:46:55-04:00 (v0.6 "4-patch tuning": SEED_PAIRS +
  CANDIDATE_POOL + settle + Stygian enqueue; message: "Pollux 100% deterministic",
  "the real loader belongs in loaders/pollux_survivor.py as v0.7 work"). No later
  commit. charon/agents/stygian/loaders/pollux_survivor.py absent. Hecate's
  LEDGER_CANDIDATES still lists the Pollux ledger (hecate/daemon.py:33), so the
  06-24 "remove from LEDGER_CANDIDATES" was never done. The v0.6 message shows
  the author knew on 05-25 that the output was deterministic and that the closed
  loop was a stub, which supports INTERPRETATION INVALID and ECOSYSTEM INVALID.
Severity: none (support). One provenance note: the v0.6 commit time is not a
  deploy time (C-3), and the dossier treats it as one.

---------------------------------------------------------------------------------
## 3  THE CORPSE CASE

The strongest honest argument for TRUE_CORPSE / HYPOTHESIS_FAILURE:

  1. The hypothesis the daemon actually operationalized is "for some pair of
     Mahler subsets, the gap-by-rank profiles of the two n-smallest truncations
     rank-correlate at >= 0.30". On the real data this is TRUE for three of nine
     pairs and the record explains why without any coincidence: corr_norm reads
     density shape, and two independent samples of one density clear 0.30 up to
     94% of the time (N2). For the three PROMOTED pairs, independent resampling of
     each pair's own marginal reproduces the observed statistic (N1 p = 0.14, 0.042,
     0.06; none survives a 9-pair correction). So the operationalized hypothesis
     is not merely untested -- on nine pairs and one seed it is INDISTINGUISHABLE
     FROM ITS OWN NULL. That is a falsification of the only version of the
     hypothesis anyone ever wrote down.
  2. The "spacing coincidence" reading of the surviving T3 results is dead for the
     same reason: the label-permutation null detects that salem and non-salem
     values have different marginals, which is the definition of the classes.
  3. Nothing on the record describes a pairing relation or a two-sample spacing
     test under which "share a spacing profile beyond scale" means something
     other than "have similar density shape", and similar density shape between
     Mahler subsets is not a coincidence, it is the Mossinghoff table.

Where it stops:

  a. Doctrine. HYPOTHESIS_FAILURE is admissible only with fair_test FAIR, and
     fair_test is a property of the HISTORICAL experiment, which had a constant
     leg, no null and no chance floor. The Cleric's N1/N2 is a new experiment run
     in the Necropolis, not a fair test on record. validate.py refuses the strong
     class at fair_test UNFAIR and refuses TRUE_CORPSE without it. Answer to the
     brief's doctrine question: no, doctrine does not permit a strong cause when
     the historical statistic is tautological, and it has no way to record a
     Necropolis-executed kill of the hypothesis (defect D-3).
  b. Evidence. N1/N2 kill the corr_norm operationalization on 9 pairs at one seed
     (1000 draws). They do not kill "some Mahler subset pairs share a spacing
     profile beyond scale" because that sentence has no defined test; an
     ill-posed proposition cannot be falsified, only discharged, and the doctrine
     has no class for "ill-posed" (D-2). The honest state is: the general
     proposition is undefined; its only definition is dead at the p-values above.
  c. The single artifact that would settle it: a preregistered two-sample
     spacing-distribution test (normalized gap distributions of the two subsets,
     matched-marginal null, published chance floor, 5 seeds) over the same 9
     pairs, with expected-if-alive / expected-if-dead written before it runs
     (LAW N9). If no pair rejects, the hypothesis dies fairly and a descendant
     TRUE_CORPSE record can be written; if one does, the Necromancer's "hypothesis
     stands untested" was the right call and the descendant has its consumer.

Verdict on the corpse case: the record supports "the only operationalized form of
the hypothesis is inside its own null" and does NOT support TRUE_CORPSE.

---------------------------------------------------------------------------------
## 4  THE RESURRECTION-BIAS CASE

Where the dossier reads toward salvage beyond the evidence:

  1. HYPOTHESIS VALID "coherent and answerable" is written on T3, which the dossier
     itself calls a fact about the statistic. The evidence that would show
     well-posedness (a pairing relation, a two-sample test) is listed under
     what_would_move_it, i.e. it is future work, not executed evidence (C-2).
  2. surviving_claims[3] and the kill_boundary NOT KILLED clause keep "two pairs
     reject the label-permutation null" alive as a possible signal with the
     hedge "neither confirmation nor refutation". Under the pair's own marginals
     the strongest pair is at p = 0.14. The hedge is the wrong reason (T5) for a
     conclusion the right null makes plainly: there is nothing there beyond
     density shape (C-5).
  3. IMPLEMENTATION_ERROR framing offers Doctor Frankenstein a repair target
     ("fix the raw leg") that the Necromancer's own T2 says changes nothing.
     A stack that names a fixable bug where the design is the bug invites a
     descendant that repeats the parent's death (LAW N8) (C-1).
  4. The chance floor is reported from assumed marginals (0.33) when the real
     marginals give 0.94; the smaller number makes the PROMOTED verdicts look
     less like noise than they are (C-4).
  5. "The hypothesis stands untested" is stated as if a test were pending; the
     record shows the hypothesis has never been given a form in which a test
     could be pending.

Where the bias runs the other way (recorded for balance): the Necromancer marked
EXECUTION VALID on the daemon's self-report (C-3), left P69's per-pair census as
"unreproducible" when it is reproducible (C-8), and under-claimed the chance floor
against the organism (C-4). The net direction is toward salvage, but it is not a
one-sided reading.

---------------------------------------------------------------------------------
## 5  STACK AMENDMENTS DEMANDED

  HYPOTHESIS      -> NOT_EXAMINED, cause_classes []
                     evidence: cleric_chance_floor_result.json (N1, N2); no executed
                     evidence on well-posedness exists on the record. (C-2)
                     Fallback if the Keeper keeps VALID: finding limited to
                     "reachable by some experiment"; T3 clause removed.
  DESIGN          -> INVALID [DESIGN_ERROR] load_bearing true  (unchanged)
                     evidence add: cleric_chance_floor_result.json (N2 floor 0.94,
                     N1 0.44); number "0.33" -> "0.94 real / 0.44 own-marginal";
                     "256/286" -> "161/286 (cleric_census_fit S2)". (C-4, C-8)
  IMPLEMENTATION  -> VALID, cause_classes []  (preferred)  or
                     INVALID [IMPLEMENTATION_ERROR] load_bearing FALSE with T2 cited
                     as the non-carrying measurement. Drop IMPLEMENTATION_ERROR from
                     contributing_causes. (C-1)
  CONFIGURATION   -> VALID (unchanged)
  EXECUTION       -> NOT_EXAMINED on the schema's literal criteria, or VALID with
                     the finding narrowed and the census discrepancy + settling
                     query recorded. evidence: cleric_census_fit_result.json (S1-S3b),
                     git log _mahler_data.py (data unchanged since 05-03). (C-3)
  INSTRUMENTATION -> INVALID [INSTRUMENT_ERROR] load_bearing true (unchanged)
  MEASUREMENT     -> INVALID [MEASUREMENT_ERROR] load_bearing true (unchanged);
                     finding: remove the T5 sentence and "deg14 fails"; rest on
                     no-null / no-floor / no-replication / corr_raw=1.0 recorded as
                     outcome; add signed T3 (D) and N1 numbers. (C-5, C-6)
  INTERPRETATION  -> INVALID [INTERPRETATION_ERROR] load_bearing false (unchanged);
                     evidence add: cleric_census_fit_result.json (P69 per-pair
                     reproduced, 86/39 not). (C-8)
  ECOSYSTEM       -> INVALID [ECOSYSTEM_FAILURE] load_bearing false (unchanged)
  fair_test       -> UNFAIR (unchanged)
  primary_cause   -> DESIGN_ERROR (unchanged); rationale rewritten per C-7.
  contributing    -> [INSTRUMENT_ERROR, MEASUREMENT_ERROR, INTERPRETATION_ERROR,
                      ECOSYSTEM_FAILURE]
  classification  -> NO_FAIR_TEST_ON_RECORD (unchanged)
  surviving_claims[3] -> reworded per C-5; kill_boundary (2) and last clause per
                     C-5 / C-8; death_certificates P69 row per C-8;
                     unresolved_questions add the C-3 settling query.

---------------------------------------------------------------------------------
## 6  DOCTRINE DEFECTS HIT (numbered, not resolved)

  D-1  Primary-cause ranking. SCHEMA says "proximate cause the evidence best
       supports"; the dossier applies "deepest load-bearing INVALID"; LAW N17
       orders only STRONG classes. When one fact (corr_raw = 1) is INVALID on
       DESIGN, INSTRUMENTATION and MEASUREMENT at once, doctrine gives no rule for
       which is primary, and the classification pair NO_FAIR_TEST_ON_RECORD /
       MEASUREMENT_FAILURE rides on the choice. MEASUREMENT_FAILURE is in the
       classification enum but has no definition in the charter; NO_FAIR_TEST_ON_
       RECORD's definition is DESIGN_ERROR's sentence. (C-7)
  D-2  Ill-posed hypothesis has no class. HYPOTHESIS carries only
       HYPOTHESIS_FAILURE / PREMISE_FAILURE, both STRONG, both needing FAIR. A
       proposition with no defined test can therefore only be VALID ("well-posed",
       per the Necromancer's gloss) or NOT_EXAMINED. The schema also lets
       HYPOTHESIS be "VALID and falsified" (validate.py:185), so VALID on this
       layer means two different things. (C-2, section 3)
  D-3  No path for a Necropolis-executed kill. fair_test is historical; a null
       run by the Cleric or Necromancer today that kills the operationalized
       hypothesis can be recorded only as prose. TRUE_CORPSE is unreachable for
       every organism whose historical test was unfair, regardless of what later
       evidence shows -- which is every organism in this trial so far (charter:
       "Three of three ... none ... fairly tested"). (section 3)
  D-4  EXECUTION grade. The schema's criteria are a conjunction (runs happened,
       state persisted, artifacts kept, no partial runs); there is no grade for
       "attested only by the organism's own recording channel" and no rule for
       whether state lost AFTER the run counts against EXECUTION or ECOSYSTEM.
       (C-3)
  D-5  load_bearing on post-outcome layers. The charter defines load-bearing as
       "whether it changed the historical answer" and asks for a measurement
       showing it did not; for INTERPRETATION and ECOSYSTEM (which act after the
       answer exists) no such measurement is possible, and the dossier's
       "non-load-bearing" there is a category statement, not a measurement.
  D-6  Two readers vs one execution. The 86/39/161 count is attested by two
       independent readers of the lost file (06-24, 08-21) and contradicted by
       execution of the code that wrote it. LAW N11 ("evidence beats old
       verdicts") does not say whether a model of the producer beats two
       observations of its product. (C-3, C-8)
  D-7  Commit time is not deploy time. The dossier dates the v0.5/v0.6 boundary
       by commit; the census fit implies deployment ~22 h later. Doctrine has no
       field for deploy attestation (program memory: CODE_FIXED != SERVICE_
       DEPLOYED). (C-3)
  D-8  One-sided verdicts, two-sided nulls. The Necromancer's T3 reports
       |null| >= |obs| for a verdict reachable only from one side; doctrine
       ("chance floor published") does not say the null must match the verdict's
       sidedness. (C-5)
  D-9  Validator gap (not hit here, recorded): validate.py:210 checks fair_test
       FAIR for STRONG classes only when they are primary_cause; a STRONG class
       listed in contributing_causes under UNFAIR passes.

---------------------------------------------------------------------------------
## 7  VERDICT

Outcome the record supports in my reading: NO_FAIR_TEST_ON_RECORD, fair_test
UNFAIR, primary_cause DESIGN_ERROR -- the Necromancer's outcome, reached with a
corrected stack (HYPOTHESIS NOT_EXAMINED, IMPLEMENTATION VALID or non-load-bearing,
EXECUTION NOT_EXAMINED or narrowed) and corrected numbers (chance floor 0.94 / 0.44,
signed T3, P69 per-pair census reproduced at k=95, verdict split not reproduced).
No objection is upheld at FATAL: the classification, fair_test and primary_cause
all survive; C-7 fails the stated reason, not the result.

The ONE strongest conclusion the record does NOT support: that the Mahler
spacing-coincidence hypothesis is dead (TRUE_CORPSE / HYPOTHESIS_FAILURE). The
record supports the narrower and harder statement that the only form of the
hypothesis anyone ever operationalized -- corr_norm >= 0.30 on n-smallest
truncations -- is reproduced by each pair's own marginals sampled independently
(N1 p = 0.14 / 0.042 / 0.06, N2 floor up to 0.94), and that the general form has
no defined test on the record, so nothing exists yet that a fair test could kill.
