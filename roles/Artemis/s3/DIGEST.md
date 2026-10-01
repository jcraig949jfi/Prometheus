# S3 digest -- Q1..Q10 worker reports, adversarial review (Artemis, ubu002)

Base of all reports: 5266ccebea3ad5522b7cfa7a07a8718cac113a70 (verified against that commit with git show).
All workers ran on ubu001, model claude-opus-5-5, no code executed. Durations (env_receipt): Q1 4.0m/37 turns,
Q2 0.8m/7, Q3 0.8m/7, Q4 2.9m/13, Q5 4.6m/41, Q6 3.9m/30, Q7 6.3m/55, Q8 2.6m/12, Q9 5.9m/37, Q10 5.0m/27.
Q2 and Q3 (under 1 minute, 7 turns) and Q4/Q8 (12-13 turns) relied on delegated sub-agent sweeps; the
receipt appears to count only top-level turns. For those four I spot-checked harder. No citation I opened was
fabricated.

Verification key: VERIFIED = cited file at 5266cceb says what the claim says; WRONG = it does not;
UNCHECKABLE = depends on something not in git or not practical to recompute here.

---------------------------------------------------------------------------------------------------------------
## Q1 -- Recombinant continuity: C-OP', ARG, privileged-operator null, FLOW vs DIFFERENCE

Claims checked (3 highest-stakes):
- C1 deep block 72923db05 is merged: VERIFIED -- `git merge-base --is-ancestor 72923db05 5266cceb` is true, so
  the harvest's "not merged" is stale. Merged still does not mean adopted: A_E002_REVIEW.md:36 says "proposed, not adopted".
- C3 C-OP' clause (b) fails on E1b/E4/E5; the root defect is testing a per-child share against a population null:
  VERIFIED -- A_E002_REVIEW.md:20-47 has the case table, the root defect and the narrowed version as quoted.
- C9 v0 singular parent is computed on IBD (FLOW) shares over all units, so E4 gets parent b: VERIFIED --
  schema.py donors() sums segment lengths / n_units over all units. SINGULAR_MIN=0.75 and SECOND_MAX=0.10. E4
  gives b=0.9375 and a=0.0625, so parent_id=b. Block A's narrowed DIFFERENCE rule gives a. This is plain
  arithmetic.

Answered the question? YES. All five sub-questions get a status with citations. The privileged-operator null
is answered as "unanswered, and arguably the wrong question for a per-child label". That is argued, not measured.
Usable without redoing? YES.
analysis.py: OPTIONAL. It only confirms the E4 threshold arithmetic, which is trivial and which I confirmed by hand.
Its inputs are archaeon/causal_lens/deep_block/cop_prime_attack.py and archaeon/attribution/schema.py. It is
stdlib, but it imports those two repo modules.

Consequential findings for owners:
- DEFECT / open tension (Archaeon, attribution v0 and C-001 E-002 line): v0's only singular-parent convention
  uses FLOW/IBD shares. On a content question it therefore gives the genealogy answer: a byte-identical-to-a
  child gets parent b. v0 has no DIFFERENCE/IBS aggregation rule, so Block B's "content uses DIFFERENCE" is not
  implemented.
- FALSE PREMISE in the harvest: "deep block not merged" is stale.
- DECISION-RELEVANT NULL: C-OP' has never been tested in a second substrate. The per-unit convention was applied
  only to Archaeon block 13. BEE and NPE preserved records carry no per-byte descent, so NPE splice cells cannot
  be tested without a taint replay. The F2 margins are on M2, not in git.
- Nestor (H-D2-37): NPE "founder-descended" claims are label descent. No material-share endpoint has been adopted.
SI / forgetting / LM01 / sealed-holdout flag: NO.

---------------------------------------------------------------------------------------------------------------
## Q2 -- Aether assay blind spots; does the observer smuggle a heredity ontology?

Claims checked:
- C8b Astra closure review: S04/M08 PARTIALLY_CLOSED, energy-donor false negative, K3 helper "restricted field
  ontology": VERIFIED -- ASTRA_CLOSURE_REVIEW_02.md:78,88,104-110,460-462, text as quoted.
- C8c the terminology linter does not check parent/template/copy/inherit/Mu: VERIFIED --
  test_aeth01_terminology_audit.py:34-61. The DEPRECATED list has "copier" and "self-copying" but no bare
  "copy", "parent", "template", "inherit" or "Mu".
- C10 the twin assay scores single-parent sufficiency, and joint causation is 2/2,793 and lower-bounded:
  VERIFIED -- PROPAGATION_ASSAY_AUDIT.md:118-119,146-150.

Answered? YES for H-D3-14 and H-D3-16. PARTLY for H-D3-15: the "how much" is not quantified. The report says so
and defers it to analysis.py.
Usable without redoing? YES. The three-layer split (vocabulary / inference contract / instrument) is a clear,
cited reading.
analysis.py: DECISIVE for the H-D3-15 "how much". It classifies each causal event in the twin assay by channel
(COPY_CONTENT, COPY_OTHER, ENABLING, ENERGY, HIDDEN, JOINT):
- copy share >= 0.8 for every law/arm means the ontology is the physics' own;
- non-copy share >= 0.5 for any law/arm means the tier ladder is blind there.
It is NOT standalone stdlib/numpy. It imports Aether/observatory/aeth03_assay_audit, aeth03_propagation,
aeth03_scouts and aeth03_variants (all present at 5266cceb). It runs simulations at 128x128, 300 warmup + 400
ticks, 32 origins per law, which is a real compute job.

Consequential findings for owners (Aether):
- DEFECT: tiers 2-5 of the claim ladder still admit transmission only as a winning-write copy of
  payload/opcode/arg. Energy, hidden-state and contest routes cannot reach them. Astra already showed one false
  negative (the funded prewired writer).
- DEFECT: the linter does not watch the terms Astra named.
- NEW POSITIVE: Aether's negatives rest mainly on the heredity-neutral twin assay, so they are less exposed than
  a positive heredity claim would be.
- DECISION-RELEVANT NULL: no ontology-neutral re-analysis exists, and no mutual-constructor detector exists. The
  cross-substrate known-answer battery is Artemis P-11.
SI flag: NO.
Reliability note: 47 s / 7 turns. The receipt does not show the depth, but all three spot-checks and the line
numbers were exact.

---------------------------------------------------------------------------------------------------------------
## Q3 -- Does the offspring-outcome distribution deform before fitness moves?

Claims checked:
- C4 E1 cycles 4 targets every generation and returns only the final population: VERIFIED --
  e1_experiment.py:59-78 has `S = targets[g % len(targets)]` and the docstring "Returns the final population".
- C6 the evolution-as-learning directory has exactly 3 commits, with no rerun or v3: VERIFIED --
  git log 5266cceb -- techne/research/evolution-as-learning/ lists a6f08ea33, e9fcabfe0 and 468a1f9ba.
- C11b Herakles HC-T01 T2 precedence NOT ATTEMPTED (fitness slope +0.02 to +0.13, no plateau); verdict
  downgraded to WEAK_SIGNAL_ONLY: VERIFIED -- HC_T01_EXECUTION_REVIEW_PACKET.txt:186-205 and
  HC_T01_CORRECTION_2026-09-03.md:9-19.

Answered? YES, as "OPEN, never measured". It explains correctly why E1 could not bear on the question even in
principle.
Usable without redoing? YES for the status verdict. C12 (Ergon/Bellerophon/Nestor cross-sectional pointers)
and the HC-T01 reanalysis "reverse precedence" point come from a sub-agent and the worker did not open them.
Treat those as leads.
analysis.py: DECISIVE, but it is a NEW EXPERIMENT, not a reanalysis. It uses the Watson Eq.1 substrate with
constants copied from e1_experiment.py@468a1f9ba, numpy. Setup: POP 200, 2000 generations, 10 seeds x 2 arms
(B-mutable vs B-frozen), kernel resampled every 50 generations. Decision rule:
- YES if there are >= 30 matched pairs and the cross-time energy distance beats the floor at p<0.01 in >= 8/10
  mutable seeds and <= 2/10 frozen seeds;
- NO if positivity holds and the mutable arm fails in >= 8/10 seeds;
- INDETERMINATE otherwise.
The onset-lag variant ("before fitness moves") is not implemented.

Consequential findings for owners:
- FALSE PREMISE in the harvest: E1 is framed as the test of H-D5-12, but E1 has a different estimand and
  non-constant selection, so even a clean E1 v3 would not answer it.
- DEFECT (Techne, E1 code, low stakes): C0/C1 controls are separate populations with independently drawn
  random-sign targets, not "within one treatment" (prereg :120 vs code :190-191, :227). The diagnostic's "22"
  pairs is about 11 unordered pairs.
- DECISION-RELEVANT NULL (Herakles, Techne): the precedence-at-flat-fitness measurement has never been made.
  The best existing instrument is an HC-T01 rerun with a plateau during signal emergence.
SI flag: WEAK. The only near-evidence (Parter 2008 Fig 9D, via Elenchus) is memory LOSS / forgetting under a
constant goal. That is relevant to forgetting/retention theory, but it is second-hand.
Reliability note: 51 s / 7 turns, with a delegated sweep. The core claims are exact. The peripheral pointers are
self-flagged as unverified.

---------------------------------------------------------------------------------------------------------------
## Q4 -- Reanalyses needing no new compute (Atlas RA-1..RA-5)

Claims checked:
- C-STATUS-1 the harvest quote is truncated ("need nothing FROM TECHNE"): VERIFIED --
  roles/Techne/journal/2026-09-25_gandalf-a04f7c25_RESET.md:91-92 reads "RA-1/RA-3 need nothing / from Techne".
- C-RA3-1 R-21 census, 38 events (21/11/5/1), latencies, "cannot yield a rate": VERIFIED --
  roles/Artemis/selftest/runs/R-21/REPORT.md:120-133,175-176.
- C-RA4-2 PART takeover counts 32/582, 25/592, 6/597, plus C-RA1-3 (pool endogenous to firings): VERIFIED --
  crius/runs/C2_TERMINAL_DISPOSITION.md:54,63,79 sums match. scheduler.py:181-200 sends controls to AUDIT only
  when an ADMITTED detector fired. C2 disposition is "CLOSED -- ACCESSIBILITY FRONTIER MAPPED" (:103).

Answered? YES on status and feasibility for all five RAs. PARTLY on answers: RA-3 and RA-5 are answered from
existing Artemis work, and RA-1 and RA-4 are left to analysis.py.
Usable without redoing? YES for the status table and the confound analysis. The independent RA-3 re-census
(catcher split of about 13/11/11/5) is one reader via sub-agent with no inter-rater check. Use it as indicative.
analysis.py: DECISIVE for RA-1 and RA-4, stdlib only (gzip/csv/json).
- ra1 reads archaeon/frontier/queues/*.jsonl and archaeon/frontier/registry/EVENTS.jsonl (drop the 299,991
  BLOCKED_BY_SUPPRESSION rows). Decision: a within-lineage permutation p<0.05 that survives excluding
  `branch: control` items means curriculum-shaped. If only the global null rejects, it is composition.
- ra4 reads crius/runs/search_c2*/takeovers.jsonl and candidates.jsonl.gz (36 and 66 files present at
  5266cceb). Decision: PART > ELITE within (run, iteration) in >= 2/3 seeds.
- The ra3/ra5 modes need hand-coded CSVs (out/ra3_census.csv, out/ra5_pairs.csv) that were NOT delivered, so
  those modes cannot run.

Consequential findings for owners:
- FALSE PREMISE (harvest): the "need nothing" quote was truncated. The RAs were designed over the uncommitted
  Atlas Postgres index on M1. Atlas is PARKED, so nobody owns running them.
- NEW POSITIVE (Artemis): RA-3 was done in substance by R-21 and RA-5 partly by FAILURE_PRINCIPLES s4 and R-26.
  Link them to Atlas RA-3/RA-5.
- DEFECT / design finding (Archaeon frontier): pool assignment depends on prior firings and lineage mode. A naive
  pool-vs-firing association would be an artefact, and the RA-1 anticheat as written does not remove it.
- DECISION-RELEVANT: the long-latency exploit catches (Nemesis ~162 d, Eos ~163 d) were all made by human or
  external reading, never by cheat controls. Preregistered nulls missed WSE W8 and Ensorain WTP-01. No
  exploitation rate is possible because exploit-free runs are unrecorded.
- RA-5: September "three engine" recurrences are shared-design echoes (R-26 factor removal). The robust
  rediscoveries are across eras and uncited.
SI flag: WEAK (retention of evidence). REVISIT.jsonl is git-ignored, and R-21's per-row table was left in
scratch. In both cases evidence needed later was not retained.

---------------------------------------------------------------------------------------------------------------
## Q5 -- A term-rewriting substrate (rewrite-strategy pressures unhostable)

Claims checked:
- C7 Archaeon's asset survey called s3_trs.py "the only term-rewriting substrate in the repo" and recommended
  "ADAPT D3 s3_trs.py for a rewriting world": VERIFIED -- archaeon/docs/expansion/ASSETS.md:123-124.
- C5 Nyx ledgers still show #189 unanswered although Proteus replied: VERIFIED -- nyx/LOOP.md:127 has "#189
  Proteus+Vivarium question, no answer". The Proteus reply file is committed with "ANSWER: (b)".
- C9 both earlier rewriting substrates were killed: VERIFIED -- agent_d4_blind/VERDICT-PHASE1.md:85-96 ("dead
  accessibility geometry", far-stratum 0.00).
- Extra check, C4 (fifth pressure mutual_normalisation.cut2 has no hosting block): the file fact is VERIFIED
  (grep count 0). The "undercount" reading is doubtful: nyx/LOOP.md:108-110 says "6 returned ... 4 unhostable,
  +3 held", so cut2 may simply never have been routed.

Answered? YES on Q5a and Q5b. PARTLY on the "should" (Q5c), which is conditional and appropriately so.
Usable without redoing? YES.
analysis.py: OPTIONAL for the headline and DECISIVE only for the sub-question "is the boolean-v0 pointer a
non-vacuous world for growing_store_must_terminate". It is stdlib and mirrors proteus/eval/boolean.py rather
than importing it. Pass/fail: the cheat control separates the disciplined and undisciplined store, and
direct-evaluation does not match every answer.

Consequential findings for owners:
- FALSE PREMISE (harvest): "no rewriting substrate" is true of hosting and ownership, not of code. s3_trs.py,
  S3_REWRITE and the egglog adapter exist, and Archaeon recommended ADAPT before the thread began. The real gap
  is an owner plus instrumentation (step log, per-fact examination counts, fired trace).
- DEFECT (Nyx): ledgers (LOOP.md:127, CHOP_SHOP_CALIBRATION:88, hypothesis_shrinker cuts.json:1038) are stale on
  #189.
- DECISION-RELEVANT: ownership is structurally absent. Vivarium hosts only, Nyx does not build worlds, and
  Proteus declines. There is also a possible vacuity risk in the n=3 boolean pointer: every function can be
  decided by an 8-row truth table. That is an inference.
SI flag: WEAK. The lean_simp pressures (growing_store_must_terminate, conditional_facts_must_be_paid_for,
retrieval_at_store_scale) are store-growth / store-discipline pressures, adjacent to retention and eviction.

---------------------------------------------------------------------------------------------------------------
## Q6 -- H3: does any archive/QD policy beat top-K on a real stream?

Claims checked:
- C3 per-seed live-arm family_b_solved: top_k 8/11/10/11/12, behavioral 7/11/7/10/11, hybrid 7/11/6/10/11:
  VERIFIED -- H3_DEAD_STREAM_CONTROL_v2_2026-09-11.json per_seed[*].arms.live, and the summary means are
  10.4/9.2/9.0. Paired diffs 1,0,3,1,1: mean 1.2, sd 1.095, SE 0.49. Hand arithmetic is correct.
- C2 real-stream sealed-query tallies top_k 4, uniform 6, behavioral 7, hybrid 6 of 9, SCORED_WITHOUT_RANKING:
  VERIFIED -- adapter_qualification-pyribs-20260911T065018Z.json:309-310,441-442,573-574,705-706,771-780. The
  claim that the gap is made up entirely of cell-occupancy queries was not re-checked item by item.
- C6 coverage identical between live and score-permuted dead streams; occupancy "does not see" the relation:
  VERIFIED -- H3_DEAD_STREAM_READOUT_2026-09-11.md:98-124.

Answered? YES. On a real stream the answer is "no evidence either way" (no informative stream exists). On the
synthetic stream there is no QD advantage. The descriptors resolve occupancy, not the relation.
Usable without redoing? YES, with one correction. The worker read retained_n only for seed 1. The JSON shows
behavioral retained 15, 15 and 14 items on seeds 3, 4 and 5 (hybrid 15 on seed 4) against 16 for top_k. The
budget is matched as a cap but not as items actually retained. That slightly handicaps QD and weakens the "top_k
ahead on every seed" reading, but it does not change "no QD advantage".
analysis.py: OPTIONAL. It recomputes the paired statistics and tallies, stdlib only. Inputs are the v2 and v1
control JSONs and the pyribs receipt. I have confirmed the per-seed inputs.

Consequential findings for owners (Archaeon: ARCH-07, C3-3; Techne: TECHNE-03/24):
- DECISION-RELEVANT NULL: no QD advantage at matched cap on the only stream with a planted relation. This is
  consistent with Chen 2026, but the stream is non-deceptive and direct-reuse only, so QD's stepping-stone case
  was never tested.
- DEFECT in reading: the real-stream 7-vs-4 in favour of behavioral comes from query families the program itself
  certified unsafe. It must not be cited as a QD win.
- OPEN: ARCH-07 has not been run, and C3-3 is still waiting on the operator's word.
SI flag: YES (retention). The whole question is about retention policy (top-K vs archive retention under a
budget cap) and uses a sealed future-query manifest (digest de4cae9b). That manifest is a sealed-query design,
not Cosmos D2.

---------------------------------------------------------------------------------------------------------------
## Q7 -- Density-CA: exp one-class collapse; does the signed-margin curve transport?

Claims checked:
- C6 the exp/W599/P_d40 prereg prediction 0.3042 failed (observed 0.3475, pass false), yet SPEC-002 lists .35 as
  "predicted": VERIFIED -- ADAPTIVE_RECORD_02.json:69-93 has pass:false and tolerance 0.0342.
  SPECIMENS_ROUND2:116-118 reads ".35 (d=.40) at N=599 (predicted; observed 1.000 and .3475)". SPEC-001
  (:36-39) counts it as a miss.
- C4 "collapse to all ones" is not recorded; per-IC files store only success: VERIFIED -- theophrastus/dissect.py:
  65-81 computes `correct` against all-ones/all-zeros and writes only `success`.
- C1/C3 no exp ablation exists, and zero-side failure at N=599 is .0043 vs .9911 (z -29.79): VERIFIED --
  stepA_tests.json:2843-2857. git grep edit_entries finds only derive.py, the Proteus GKL mint test and two
  request/inbox docs.

Answered? YES, as a well-evidenced OPEN: no ablation, particle1 not replicated, transport untested and
structurally untestable with the current kinds. It also reframes H-D4-64 correctly: the decomposition is an
exchangeability identity, so the empirical question is whether k is sufficient under non-exchangeable ICs.
Usable without redoing? YES.
analysis.py: DECISIVE for H-D4-63 (Part C, 128 single-entry flips of exp at N=599) and for the reframed
H-D4-64 (Part D, blocky vs uniform fixed-k ICs). Part A2 (m* bootstrap) and Part E (particle1 on 5 seeds) are
also in the file. numpy. Inputs: roles/Theophrastus/crucible/round2/per_ic.jsonl and per_ic_round2.jsonl
(present), genome hexes from herakles/evca/genomes.py; one part imports herakles.evca.core. Runtime is minutes
to tens of minutes on one core.

Consequential findings for owners:
- DEFECT (Theophrastus): SPEC-002 presents a failed preregistered prediction as "predicted". "Saturated
  599->999" also sits beside a failed exp W999 P_unif prediction (.7887 vs .8228).
- DEFECT: the "all ones" mechanism is asserted but never recorded. Downgrade it to "near-total zero-side
  failure" until final states are logged.
- DECISION-RELEVANT: the intervention has been executable since 2026-09-16 (Herakles derive_edit/derive_flip;
  Vivarium runs derived rules), but nobody has submitted the scan. Theophrastus has been inactive since
  2026-09-14. The particle1 replication is an unchecked Herakles todo.
SI flag: NO.

---------------------------------------------------------------------------------------------------------------
## Q8 -- Implicit-pressure citation sweep (claims with no task causation)

Claims checked:
- C1 BEE IMPLICIT is task-inert: VERIFIED -- prometheus/z80atlas/world.py:35 (INIT_ENERGY 12.0), :46 (default
  IMPLICIT), :648 (uniform EXTERNAL weights), :671 (base + 0.5*s); grounding.py:28-31 (BASE pressure
  IMPLICIT).
- C4 G2/G6 pool G1T, whose seeds are task-independent, so about 20 of 160 origins are duplicates: VERIFIED in
  mechanism -- grounding.py:112-124 sets seed = SEED_BASE + lane_no*1e9 + k with one lane "G1T" for all six
  tasks, so seeds are identical across task cells. grounding_analysis.py:212 pools lane in (G1, G1T).
  GROUNDING_REPORT:51 says five cells are run-for-run identical at 5/150. The exact count is UNCHECKABLE without
  running A1.
- C9 NPE A-2 is confined to EXTERNAL reproduction: VERIFIED -- Nestor grammar.py:175-177
  (explicit_fitness_needs_external), world.py:644-652 (tournament on comp only inside _external_births),
  :838-839 (called only when reproduction == EXTERNAL), grammar.py:70-71 (NONE_IMPLICIT "no task coupling").

Answered? YES. All three parts are answered: BEE claims, wiki/Atlas exposure, and NPE A-2. The H-D2-41 link is
also addressed.
Usable without redoing? YES. The wiki/Atlas absence (C7) came from a sub-agent and was not re-verified. It is
an absence claim.
analysis.py: DECISIVE for three quantitative follow-ups; the verdict does not depend on them. Stdlib (gzip/json).
- A1 counts the G1T duplicates inside the G2/G6 pool, from roles/Bellerophon/forensics_2026-09-23/receipts/
  GROUNDING_RESULTS_RAW.jsonl.gz (present).
- B1 and B2 give the NONE_IMPLICIT share of the NPE reproduction->EXTERNAL axes and of the 65 endogenous-reach
  flags, from roles/Nestor/campaigns/z80atlas-2026-09-19/observatory/INDEX.jsonl.gz (present).

Consequential findings for owners:
- NEW DEFECT (Bellerophon): G2 sustained 63/160 (39.4%), G6 origin counts and the ERRATA 103/160 are
  pseudo-replicated, because the G1T task cells share seeds. This is not flagged anywhere else.
- DEFECT (Bellerophon): POST_CAMPAIGN_FORENSICS.md:116-120 ("replication shows no task dependence") still stands
  unqualified and pools all pressures. It should be marked NOT_ADJUDICABLE.
- NEW POSITIVE / scope (Nestor): A-2 +0.30 is a valid selection-vs-drift contrast, but only inside EXTERNAL
  reproduction. Citations (Nestor FINDINGS, W1_NPE_LENS, roles/Cosmos/design/01_engine_design_2026-09-23.md:74)
  need an EXTERNAL-only scope note, not a retraction.
- DECISION-RELEVANT NULL: the evidence wiki and Atlas hold no BEE entries, so there is nothing to retract. NPE
  has never had a task-coupled endogenous-vs-external test.
SI flag: NO. Cosmos is named only as a citer of A-2, not for D2.

---------------------------------------------------------------------------------------------------------------
## Q9 -- Aether expressivity ceiling; arbitration hash as hidden economics

Claims checked:
- C1 the required AETH-01-scale arbitration-bias rerun was never performed: VERIFIED --
  REPAIR_LEDGER_01.md:494-505 says "named, not executed this cycle". git grep for arbitration bias/neutral and
  win rate under Aether/ and ops/ returns only AETH-00_REVIEW, AETHER_SPEC, AETHER_TEST_PLAN and
  test_statistical_diagnostics.py. (Note: ledger :494-505 is the M07 Mu-independence item, which extends the
  rerun requirement. The arbitration-specific falsifier is at DECISIONS.md:161-177.)
- C5 derived proof: P[M(h^a) > M(h^b)] = 1/2 exactly, and tick->h3 is a bijection: VERIFIED (mathematically) --
  AETHER_SPEC.md:246-270 gives M as a bijection and the chain h0..h3 with source XORed last. Substituting
  h' = h^a^b swaps the events. The proof is sound but applies to the full 2^64 tick domain. The practically
  relevant finite-window deviation is exactly what stays unmeasured, and the report says so.
- C14 fwd (non-conservative forwarding) was run as a positive control and failed E-P1 (3.1%):
  VERIFIED -- PHYSICS_DESIGN_03_2026-09-27.md:118-135,183-188,216-224.

Answered? YES for both entries: H-D3-17 is bounded by argument but formally unverified; H-D3-18 is answered
with a ranking.
Usable without redoing? YES. The verdict "unlikely material at v1 stakes" is argument-grade and should not be
cited as the pre-campaign check.
analysis.py: DECISIVE for H-D3-17, meaning it IS the missing pre-campaign check. numpy, mirrors the spec law,
cross-checks against Aether/test/reference/oracle_aeth01.py (present). It flags a material hidden law on any of:
(A) a Bonferroni-significant directional deviation above delta=0.005 in fixed-seed trajectories; (B) a per-pair
dispersion index above 1; (C) lag or cross-field winner association. No flags, with CI half-widths below delta,
closes it.

Consequential findings for owners (Aether):
- DECISION-RELEVANT NULL: the flagged "required pre-campaign check" has never been run. The D-AETH01-08
  falsifier is open.
- NEW POSITIVE: two-way contests (99.998%) cannot carry a persistent trait-linked bias by construction. The real
  contest economics is the open loser-pays / energy-destroyed rule, not the hash.
- FALSE PREMISE (harvest): "no non-conservative movement primitive tried" is partly wrong, because fwd was run.
  Literal whole-tuple relocation has never been built.
- The explicit conditional (cnd) is counter-indicated. Receipt sensitivity plus energy steering is the only
  productive affordance so far.
SI flag: NO.

---------------------------------------------------------------------------------------------------------------
## Q10 -- Residual bridges; incidents as splittable hypotheses

Claims checked:
- C4 FP-003's three anchors have different mechanisms with opposite remedies (STOP vs GROW): VERIFIED --
  harmonia/primitives/failure_primitives.py:440-490 ("SHARPEST OPEN CRITIQUE ... opposite remedies under one
  observable"; subclass-discriminator probe "owed").
- C7 Null-2 was run once (H5a OEIS), verdict NULL, family metadata absent, 3/5 controls STUB: VERIFIED --
  aporia/results/h5_oeis_mvp_2026_06_04.json:1-4,24-30,183-191 (real 200.07 vs shuffle 169.07).
- C8 split() is exercised only in a test: VERIFIED -- git grep "split(" under roles/Hermes shows the definition
  at record.py:125 and one call at test_convergence.py:204.

Answered? YES. H-D5-56 is "not answerable as posed; adjacent evidence negative on signature => mechanism".
H-D5-55: design YES but unvalidated; the ancestry half is untestable on committed data.
Usable without redoing? YES, with one caveat on C9. The live incident c84e26826cc12217 is presented as a real
multi-cause case (the CTL-2 situation). Its three "fix paths" (comms, Evidence Wiki, viv/db.py) look like ONE
root cause, clients resolving to the M2 fork DB with no identity check, showing up in several clients. That is
closer to one cause with several exposures than to two causes hidden under one key. So the "CTL-2 occurring for
real" claim is over-read.
analysis.py: OPTIONAL. The report itself says even a positive would be a fixture-bound lead. It reads
agents/nemesis/adversarial/adversarial_results.jsonl (present, 92 records), stdlib. Rule: rho>0 at p<0.01 with
>= 20 effective depth>0 records inside NEI x category strata.

Consequential findings for owners:
- DECISION-RELEVANT NULL / partial negative (Harmonia): the one coordinate-invariant failure shape (FP-003) is a
  triage key, not a mechanism key. September data (Artemis FAILURE_PRINCIPLES:877-885, FR-132) falsify its GROW
  remedy (0/4,881). The FP-004 independence audit and the FP-003 discriminator probe are still owed.
- FALSE PREMISE (harvest): "later evidence: none found (never built)" misses the June FP atlas and the Artemis
  September recurrence audit.
- DEFECT / data loss (Ares): search.py builds full population ancestry but persists only the champion chain and
  pooled mutation_survival. That makes "does ancestry predict breakage" untestable. Nemesis's 52 lineage-bearing
  records sit in a negative-fixture ledger.
- Hermes: split() has never been used on a live incident, and its falsifiers are unmeasured.
SI flag: WEAK. It touches retention/erasure (Ares discards non-champion ancestry) and holdouts (the only
Null-2 run used a random holdout because family metadata was absent). Not Cosmos D2.

---------------------------------------------------------------------------------------------------------------
## Cross-package notes
- No report is fabricated. 30/30 checked claims VERIFIED (Q8 C4's exact count and Q6 C2's query-by-query
  composition remain uncheckable or unchecked).
- Recurrent pattern across the harvest: "later evidence: none found" was wrong or stale in Q1 (merged), Q4
  (R-21 / FAILURE_PRINCIPLES), Q5 (existing executors), Q9 (fwd) and Q10 (FP atlas). Harvest "later evidence"
  fields should be treated as unreliable.
- analysis.py that would change a decision: Q9 (the missing pre-campaign check), Q7 Part C (exp ablation), Q8 A1
  (G2/G6 pseudo-replication), Q2 (the ontology share), Q4 ra1/ra4, Q3 (a new experiment). Q1, Q6 and Q10 are
  confirmatory or optional.
