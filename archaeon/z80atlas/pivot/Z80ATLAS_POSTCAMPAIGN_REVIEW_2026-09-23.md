+==============================================================================+
| Z80 x ATLAS -- POST-CAMPAIGN REPAIR + TARGETED FALSIFICATION -- REVIEW PACKET |
| Author: Archaeon (M2 / SPECTREX5), session m2-db608f52                        |
| Date: 2026-09-23 (work 11:11Z - 12:30Z)                                       |
| For: operator (HITL) + external reviewers                                     |
| Status: ALL FOUR PHASES COMPLETE. Phase 4 outcome                             |
|         NO_DETECTABLE_DE_NOVO_REPLICATION (0/80, controls 21/21 PASS)         |
| Self-contained: every load-bearing number is inline; no repo access needed.   |
+==============================================================================+

0. SUMMARY / VERDICT
-----------------------------------------------------------------------------
- The 26 "spontaneous_replication" flags were an instrumentation defect,
  confirmed three independent ways (code path, preserved specs, byte-identical
  instrumented replay). All 26 are transplanted-lineage replication. Every
  transplant source was itself a SEEDED-replicator run, so the material was
  inserted twice.
    verified de-novo spontaneous replication in the completed campaign
      = 0 of 101,003 DONE runs.
- Repaired: genetic provenance now travels with genetic material (founder
  origin classes + ancestry sets). The repair is RNG-neutral: every
  pre-existing output of the campaign engine is reproduced exactly.
- Re-scored with the campaign's own scorer, which reproduces the historical
  top-30 exactly: 2ace470e5c47 / 5b237a475b69 / e8394eee206d fall 17 -> 14.
  The corrected top-30 is a 30-way TIE at 14, so the "top family" ordering
  carries no information.
- The real phenomenon under the false label:
  * Transplanted lineages persist and self-replicate when moved (39/39
    persisted), but task competence did NOT travel (0/39 retained).
  * Separately, the campaign holds ONE random-origin world that never went
    extinct, out of 27,141: an input-gated self-copier (a random 32-byte
    tape that copies itself exactly only when the task input byte is 121).
    It fails the frozen fidelity criterion.
- Phase 4 (preregistered, fixed allocation, 5 arms x 16 seeds): 0/80
  de-novo events. Every treatment world went extinct (median epoch 61),
  and no world produced even one clean high-fidelity birth. That includes
  16 fresh seeds of the candidate's own world class.
- A second defect of the same class was found: moat_crossed and
  moat_advantage (8 of the 14 points) are not provenance-qualified. Seeded
  worlds insert a hand-written task witness. The confound is PARTIAL
  (see 7). It is measured, not re-scored; it needs a ruling.

1. DEFECT DIAGNOSIS (directive item 1)
-----------------------------------------------------------------------------
Campaign code commit c7610ea19 (engine.py/scheduler.py unchanged to bcb9f22ad):
  (1) scheduler.py:255  verify() builds transplant specs from the source run's
      final population: t["transplant"]={tapes}; t["init"]="random"
  (2) engine.py:153/158 run(): if spec["transplant"], cells are filled from
      the tapes; no random tape is ever drawn in that branch
  (3) engine.py:371 predicate: spec["init"]=="random" and phys in ENDO and
      births_endo>=50 and final pop>=0.25N and fidelity>=0.9 -- it reads the
      LABEL and has no access to founder origin
  (4) scheduler.py:101 flag -> +5 in the family score
Together: every founder is inserted, the label says random, and a
transplanted lineage that keeps replicating satisfies (3).
Side findings from the audit:
- 27 RUNS.jsonl rows, 26 unique run ids. 466dab00b7b6-t_s100_veri ran twice:
  family 2ace470e5c47's environment swap mapped COND_multi -> COND_multi,
  so it was VACUOUS (identical to transplant:same). Packet labels 10/12/4
  (same/env/world); counting all rows gives 11/12/4.
- The packet reported "5/5 positive controls PASS". scheduler.log shows
  6/6; the vmcopy replicator_replicates verdict never reached the state file.

2. REPAIR, TESTS, COMMITS (items 2, 3, 4)
-----------------------------------------------------------------------------
Provenance v1 (archaeon.z80atlas.provenance.v1):
- Each founder is stamped at tape creation: random | seeded_replicator |
  transplanted_lineage (with tape sha and from_run).
- anc = set of founders whose material MAY have reached the organism
  (conservative). Contributions:
    parent             always
    previous occupant  iff the parent read or executed neighbour memory,
                       the window was sealed, or any window byte was left
                       unwritten and kept (except ENDOGENOUS_PARTIAL, which
                       refills unwritten bytes from the RNG)
    recombination      partner (EXTERNAL)
    migration          moves anc; death clears it
- Repaired predicate: the SAME frozen thresholds (50 / 0.25N / 0.9), counted
  only over births and survivors with random-only ancestry. The legacy
  predicate is kept as spontaneous_replication_legacy_label for replay
  comparison.
- Additional per-run outputs: inserted_lineage_replication; first
  (clean / inserted / clean-hifi) replication records (tape, founders,
  generation, epoch, niche, task); first-crossing ancestry; PROVENANCE.json.
Tests (archaeon/tests/test_z80atlas_provenance.py, test_z80atlas_denovo.py):
  the 10 required cases (1 random->spontaneous possible; 2 seeded never;
  3 transplanted never; 4 400-epoch lineage stays tagged; 5 world swap x5
  topologies; 6 task/env swap x3; 7 migration; 8 overwrite/copy x5 physics
  cannot launder; 9 random and inserted lineages distinguishable in one
  world; 10 REGRESSION: the exact campaign pattern -> legacy True,
  repaired False), plus donor-rule units, recombination inheritance,
  4 RNG-neutrality tests against the c7610ea19 engine, a historical replay
  of 4e132c6e0178, and 5 Phase 4 endpoint tests.
Full non-DB suite: 339 passed / 2 failed / 2 skipped. The 2 failures are
pre-existing and fail identically before the repair (test_base_role manifest
check; test_workspace SFE-ledger host path). Pre-repair baseline: 302/2/2.
The 8 DB-backed modules were not run: they need a named Postgres store and
were not pointed at M1 production. z80atlas touches no database.
scheduler --self-test: unchanged (births_endo 2022).
Commits (branch archaeon/z80atlas-postcampaign-2026-09-23):
  299981e9a  repair + tests + Phase 1-3 artifacts
  8e6245036  PREREG DENOVO-01 frozen and pushed BEFORE any Phase 4 run
  (next)     Phase 4 results + this packet

3. THE 26 RECLASSIFIED RUNS (item 5) -- all transplanted_lineage_replication
-----------------------------------------------------------------------------
Every row: all founders transplanted (122-128 tapes); source init=seeded.
run_id                       family        kind              topo/repro
67cef4faf5e7-t_s100_veri     19a0e0a5300a  same              niches/PARTIAL
36f2d57cd4f2-t_s100_veri     19a0e0a5300a  env_swap          niches/PARTIAL
7252d77c58b8-t_s100_veri     4aa428bd90bd  same              niches/COPY
997f12c1740f-t_s100_veri     4aa428bd90bd  world_swap        well_mixed/COPY
ee082f2db085-t_s100_veri     4aa428bd90bd  env_swap          niches/COPY
11793ae99dd8-t_s100_veri     dd2e76a1189b  same              niches/COPY
8ac55dbf1309-t_s100_veri     dd2e76a1189b  env_swap          niches/COPY
466dab00b7b6-t_s100_veri     2ace470e5c47  same+env(VACUOUS) niches/COPY
8f1eda878795-t_s100_veri     5bb46451d5fb  same              niches/COPY
9dd90a43ab91-t_s100_veri     5bb46451d5fb  env_swap          niches/COPY
3f05e65e3d47-t_s100_veri     5bb46451d5fb  world_swap        well_mixed/COPY
e64ba9b6e468-t_s100_veri     070c3a9ab655  same              niches/COPY
07d1f7853f4c-t_s100_veri     070c3a9ab655  env_swap          niches/COPY
ac1891969d1f-t_s100_veri     ac675613ecd5  same              niches/COPY
771c5c311468-t_s100_veri     ac675613ecd5  env_swap          niches/COPY
d09e8fde50a3-t_s100_veri     636158e75708  same              niches/COPY
78722e5100e6-t_s100_veri     636158e75708  env_swap          niches/COPY
4e132c6e0178-t_s100_veri     5b237a475b69  same              niches/COPY
987e0e2fdf50-t_s100_veri     5b237a475b69  world_swap        well_mixed/COPY
3fe9d02da7fe-t_s100_veri     5b237a475b69  env_swap          niches/COPY
6c3a4a1fb3b8-t_s100_veri     fd8719c6af75  env_swap          niches/PARTIAL
45e6b162ded1-t_s100_veri     d130e2d3e25f  same              niches/PARTIAL
c66e86c73e36-t_s100_veri     d130e2d3e25f  env_swap          niches/PARTIAL
2226fc309f55-t_s100_veri     e8394eee206d  same              niches/COPY
d6eab9d26a29-t_s100_veri     e8394eee206d  env_swap          niches/COPY
2b08271de8ad-t_s100_veri     e8394eee206d  world_swap        well_mixed/COPY
Replay corroboration: 26/26 admitted, with every legacy signal byte-identical
to the preserved RECEIPT. In those replays:
  legacy label reproduced                 26/26
  repaired predicate true                 0/26
  inserted_lineage_replication true       26/26
  random founders                         0 of 3,252
  clean endogenous births                 0
  inserted lineage depth                  1,421 - 3,405 generations

4. ORIGINAL vs CORRECTED RANKING (item 6)
-----------------------------------------------------------------------------
Reconstruction check: re-running the campaign's own family scorer over the
preserved RUNS.jsonl reproduces PACKET top-30 exactly (true).
family        orig(rank) -> corr(rank)  removed                 corrected best run
2ace470e5c47  17 (1)     -> 14 (4)      spontaneous_replication 2ace470e5c47_s1_expl
5b237a475b69  17 (2)     -> 14 (9)      spontaneous_replication 5b237a475b69_s1_expl
e8394eee206d  17 (3)     -> 14 (12)     spontaneous_replication 41d711eb922d_s1_cont
- The score-17 runs were transplants. Without the flag they score 12, and
  each family's max now comes from its own exploration/control run (14:
  +compression, or +coexistence/transport).
- The other 9 touched families were already 14 and stay 14.
- Corrected top-30 = 30 families, all at 14. Ranks inside the tie are
  dict-order artifacts. Corrected spontaneous_replication flag total = 0.

5. CORRECTED READING OF 5b237a475b69 (item 7)
-----------------------------------------------------------------------------
- A seeded-replicator family (task ADD2, niches, ENDOGENOUS_COPY, vmcopy).
- Its tapes (from a0132ad72787_s1_cont) persisted and self-replicated after
  transplant into the same world, a well_mixed world and a COND_multi world:
    same        pop 0.992, 381,361 endo births, fidelity 0.994
    world swap  pop 0.984, fidelity 0.995
    env swap    pop 0.977, fidelity 0.992
    physics swap to EXTERNAL persisted (pop 0.953)
- Final task competence was 0.0 in every transplant, against a source best
  of 1.0. So: transplanted-lineage persistence, not de-novo replication,
  and not competence transport.
- Its remaining moat_crossed / moat_advantage come from a seeded-hybrid
  world, where the witness confound applies (section 7).
- Corrected score 14, tied.

6. NICHES REGIME + RECOMBINATION (items 8, 9)
-----------------------------------------------------------------------------
Niches: an association, not a topology effect.
- Exploration-only moat_advantage rate:
    niches 0.0171 (227/13,313)    other topologies 0.0002 - 0.0013
- The exploration sampler itself coupled topology to migration and
  reservoir: random_spec weights levels by 1/(1+coverage), and
  migration=none / reservoir=False are forced (and counted) in every
  non-niches run. Niches exploration drew migration=none in only 190 of
  13,313 runs, and produced ZERO "bare" niches worlds.
- Adaptive promotion then sent 8,682 promotion runs to niches, against
  about 170-209 for each other topology.
- Verdict: the campaign cannot separate topology from migration, reservoir,
  niche-local environment dynamics or allocation.
Recombination: confounded by construction.
- grammar.matched_controls flips EXTERNAL -> ENDOGENOUS_COPY and DROPS
  recombination and explicit_fitness (grammar constraint: recombination
  only with EXTERNAL).
- Exact pairing, recomputed from the preserved specs: 1,829 recombination
  treatments. Controls keeping recombination: 0. ENDOGENOUS_COPY controls:
  1,829. Treatments that also lost explicit_fitness: 550.
- Holding physics fixed (EXTERNAL exploration runs only), moat_advantage is
  0.1308 (85/650) with recombination vs 0.1192 (115/954) without.
- The "3-5x" figure appears only when adaptively promoted runs are included.
  No causal recombination claim is licensed.

7. SECOND CONFOUND (not in the directive's list; same defect class)
-----------------------------------------------------------------------------
Seeded worlds use init_hybrid (the grammar default). The seeded tape is the
HAND-WRITTEN task witness plus a replicator, so a crossing there can be the
inserted witness scoring rather than an evolved solution.
From the records:
                          seeded task runs     random task runs
  crossed the moat        47,814 / 48,703      20,762 / 45,353
  crossed at epoch 0      36,961               2,486
- Of the 35 families scoring 14, 34 have a seeded best run.
- moat_advantage runs by init and first-crossing epoch:
    seeded  epoch 0: 619   epoch 1-5: 114   epoch >5: 199
    random  epoch 0:  50   epoch 1-5: 125   epoch >5: 2,003
Instrumented replays (all admitted, byte-identical):
                                     crossings by        of which the
                                     inserted-ancestry   unmodified seeded
                                     organisms           tape itself
  seeded, stratified sample (20 runs)  27 / 42           14
  seeded, named families + controls    12 / 26            4
  random worlds (20 runs)               0 / 40            -
So the confound is REAL but PARTIAL. Seeded-world moat flags are mixed
evidence, and random-world moat flags are clean.

8. PHASE 4 PREREGISTRATION (item 10) -- DENOVO-01, frozen at 8e6245036
-----------------------------------------------------------------------------
Held factors (all arms): vmcopy, genome 32, shared layout, ENDOGENOUS_COPY,
  pressure tape_cost, task ECHO_forced, local_byte mutation, resources
  limited, env_mutate, init=random.
  Source: the ONLY random-origin campaign world that stayed alive
  (84616cf8257b_s1_cont). Top-family modes were NOT used: 27/30 of those
  families are seeded worlds and carry no information about random origin.
Arms (2x2 migration x reservoir inside niches, plus well_mixed):
  A niches + env_dependent migration + reservoir
  B niches bare (the topology-only arm)
  C migration only
  D reservoir only
  E well_mixed (spec_id == 84616cf8257b: the candidate's own world class)
Design: 16 seeds per arm (1000-1015); late budget (150M VM steps / 4000
  epochs); fixed allocation; no transplants, seeding, warm starts or
  intervention.
Primary endpoint (per run), DE_NOVO_REPLICATION:
  (i)   0 seeded and 0 transplanted founders
  (ii)  repaired frozen predicate: >=50 random-only endogenous births,
        final random-only population >=0.25N, mean fidelity >=0.90
  (iii) alive at the end of the budget after >=2 x max_age epochs (every
        founder dead, so survival requires endogenous reproduction)
Secondary: SUSTAINED_LOW_FIDELITY_REPRODUCTION = (i) + (iii) + births and
  population thresholds met, fidelity <0.90.
Controls (run first; any failure stops the screen):
  - 6 grammar positive controls
  - 10 seeded positive controls in the arm worlds (>=50 inserted-ancestry
    births at fidelity >=0.9; repaired predicate False)
  - 5 provenance negative controls (hand-written hybrid witness transplanted
    and labelled init=random; must classify 100% transplanted, repaired
    predicate False)
Outcome rules were fixed in advance: REPRODUCIBLE (>=2 seeds in one arm),
  RARE (>=1 event), NO_DETECTABLE (report exact 95% bounds),
  INSTRUMENT_FAILURE, DESIGN_NOT_IDENTIFIABLE (the grammar accepted all 5
  arms, so this one was not triggered).
Code hashes of engine/vm/tasks/grammar/scheduler/runner are frozen and
  verified at launch.

9. PHASE 4 RESULTS (items 11, 12, 13)
-----------------------------------------------------------------------------
Controls 21/21 PASS:
- Positive controls: 192k-203k inserted births at fidelity 0.983-0.991.
- Negative controls, arms A/C/E: the legacy label WOULD have said
  spontaneous. The repaired predicate says false. This is the defect caught
  live.
arm                            primary  secondary  extinct  median ext.
A niches+mig+reservoir         0/16     0/16       16/16    61
B niches bare                  0/16     0/16       16/16    61
C migration only               0/16     0/16       16/16    61
D reservoir only               0/16     0/16       16/16    61
E well_mixed (candidate)       0/16     0/16       16/16    61
Per-arm exact 95% CI: [0, 0.206]. Pooled 0/80: [0, 0.045].
Worlds with even ONE clean high-fidelity birth: 0/80.
OUTCOME: NO_DETECTABLE_DE_NOVO_REPLICATION.
Genuine de-novo replication, exact numerator/denominator:
  frozen definition, campaign             0 / 27,141 random-origin
                                            endogenous runs
  frozen definition, Phase 4              0 / 80
  any self-sustaining random-origin
  reproducer, campaign                    1 / 27,141
  same, Phase 4                           0 / 80
Evidence pointer for the one positive-shaped event:
  84616cf8257b_s1_cont (campaign runs/70d24e947c80/...; full instrumented
  replay under archaeon/z80atlas/postcampaign/replays/84616cf8257b_s1_cont/).
  - Replay admitted byte-identical. 81 random founders, 0 inserted.
  - Founder 48 made an exact copy at epoch 23. Its tape:
      d521f9897030d42ef94aed67c4e2be714e8ed4791f14d54550d911698a00c826
    It is IN C ; LD B,-7 ; ... ; COPY ; JR -7: a copy loop whose
    destination is the task INPUT byte.
  - Of 256 inputs, 26 yield a birth; only input 121 yields an exact copy.
  - The lineage took the whole world by epoch 100 (bottleneck of 14), held
    about 100 organisms to the budget end (epoch 918), and reached
    generation 74 with 91 distinct tapes.
  - The modal final tape is a zero-NOP sled into the loop (a shifted copy
    that still works because the loop's jumps are relative).
  - 4,739 clean births, 190 of them at fidelity >=0.9; mean fidelity 0.485.

10. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------------------------------------------
DOES:
- The spontaneous signal was a label artifact (certain: code + specs +
  replay).
- Transplanted seeded-derived lineages persist and self-replicate across
  world and task swaps.
- Competence did not transfer in any of the 39 transplant runs.
- In this frozen bench, random-origin endogenous worlds almost always die
  within about 60 epochs.
- One lucky random tape can be an input-gated copier and found a lasting
  lineage.
DOES NOT:
- Establish any topology, migration, reservoir or recombination effect.
- Establish a de-novo rate below about 4.5% per world for this world class
  (only 80 worlds).
- Explain why the 84616cf8257b draw happened (it looks like a rare
  initial-tape event; 0/16 fresh seeds of the same world class reproduced
  it).
- Make any Harmonia-grade claim. Archaeon holds no verdict authority on
  these.
STRUCTURAL CEILING: the frozen grammar has no inflow of new random material.
A world's de-novo search window is its initial ~77 random tapes plus about
60 epochs of mutation. More seeds of the same bench mostly re-measure the
initial-tape prior.

11. RECOMMENDATION (item 14) -- operator's call; Archaeon's lean stated
-----------------------------------------------------------------------------
Lean: do NOT spend more compute on seeds of this bench for the de-novo
question.
  (a) Cheapest informative next move: estimate the per-tape prior directly.
      Execute about 10^7 random 32-byte vmcopy tapes against all 256
      inputs, with no worlds, and count exact and near self-copiers. That
      gives the number of worlds needed for any powered claim and shows
      whether input-gating is the dominant route.
  (b) If de-novo emergence is the program question, grow the bench
      (charter item 3) rather than draw again: a preregistered
      random-inflow ("soup") arm so worlds do not die at epoch 60. This is
      a grammar change, so it needs a new grammar digest and campaign
      identity.
  (c) Ruling needed on the witness confound: either re-score seeded-world
      moat flags with provenance-qualified crossings (instrumented replay
      of the seeded moat runs), or mark them unadjudicated. Until then the
      corrected top-30 must not steer allocation.
  (d) Report to the scheduler owner (Archaeon's own code): random_spec's
      coverage weighting makes forced levels starve optional ones. Fix it
      before any future adaptive campaign.
"Not worth continuing" on de-novo-in-this-bench is a defensible answer, and
Archaeon would not argue against it.

12. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------------------------
Q1 The contribution rule taints a clean child whenever it keeps a single
   inserted byte. Is that too conservative, so that it hides real
   random-origin lineages in mixed worlds? Test 9 shows a clean class lost
   to exactly this in about 50 epochs.
Q2 Is holding Phase 4's other factors at ONE survivor's configuration a
   post-hoc choice that biased the screen toward a lucky world class? The
   alternative, top-family modes, was all seeded worlds.
Q3 Does the frozen 0.9 mean-fidelity threshold exclude the only real
   phenomenon (input-gated copying) by design? Should the endpoint be
   lineage-level rather than world-cumulative?
Q4 Is instrumented replay of preserved (spec, seed) a "re-run" the
   directive forbade? Archaeon treated it as re-measurement, admitted only
   on byte-identity, and based the verdicts on the records.
Q5 Should the witness finding void the whole moat ranking, not just
   qualify it?

13. ARTIFACTS
-----------------------------------------------------------------------------
Branch archaeon/z80atlas-postcampaign-2026-09-23; commits 299981e9a,
8e6245036, + results commit.
archaeon/z80atlas/engine.py, scheduler.py                  repair
archaeon/tests/test_z80atlas_provenance.py, test_z80atlas_denovo.py
archaeon/z80atlas/postcampaign/AUDIT_RECEIPT_2026-09-23.json
archaeon/z80atlas/postcampaign/Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.{md,json}
archaeon/z80atlas/postcampaign/replays/REPLAY_{flagged,named,witness_sample,
  denovo_candidates}.json and 84616cf8257b_s1_cont/
archaeon/z80atlas/postcampaign/{adjudicate,replay,render_md}.py
archaeon/z80atlas/denovo/{PREREG,CONTROLS,RESULTS}.json, run_denovo.py
  (run dirs gitignored under denovo/runs/)
Historical inputs (sha256 in the adjudication JSON), read-only, gitignored,
ONLY copy at:
  D:\Prometheus-worktrees\archaeon-wse-2026-09-16\archaeon\z80atlas\campaign
  RUNS.jsonl  3afa36b7...  ATLAS_INDEX.jsonl  7bc020e6...
  PACKET.json 9f3bda54...
DO NOT delete that worktree: it holds the only copy of the evidence.

+==============================================================================+
| END. A clean null is a successful result. "Not worth continuing" remains a   |
| first-class answer for the de-novo question in this bench.                   |
+==============================================================================+
