# COUPLING CAMPAIGN PREREGISTRATION -- Bellerophon, physics v3 (computation -> copy resource -> reproduction)

Status: FROZEN at the commit that adds this file (freeze record s12). Nothing above the amendments section may change
after the first scientific run. Directive: prompts/00_OPERATOR_DIRECTIVE_verbatim.md (2026-09-24).
Base: branch bellerophon/coupling-campaign-2026-09-24 from 3efdacf7e (the closed grounding round).

## 0. Question

Can useful computation causally affect reproductive success through a physical resource constraint, and does that
coupling create heritable evolutionary pressure on computation or reproductive organisation?
computation -> physical resource -> reproduction -> heritable variation.

## 1. The new physics (v3; prometheus/z80atlas/coupling.py; audit: COUPLING_IMPLEMENTATION_AUDIT.md)

One quantity: each organism's COPY RESOURCE R (a non-negative integer in the World's ledger; no VM instruction can
read or write it). Per interaction: +BASE unconditionally; after the execution, the evaluator compares the FIRST
output with the expected answer for the inputs given (ATOMIC exact, read gate ABR; expected value computed outside
the VM) and pays BONUS according to the coupling mode (s3). Constructing an offspring costs COPY_COST units per
window byte written (a full ENDOGENOUS_COPY child = 64 units at cost 1); an unpaid viable construction is refused
(no child, no charge). Credit earned in an execution is spendable only in a later one. R is capped (256; every
clamped unit counted); newborns start at R = 0; R is lost at death (counted). Ledger identity
earned = spent + clamped + lost + held is asserted in every run (an imbalance VOIDS the run). Everything else is
physics v2 (grounded). scoring = NEUTRAL in every coupled run: the energy path is task-blind, so the ledger is the
ONLY path by which a task can touch the dynamics (tested: test_task_identity_acts_only_through_the_ledger).
Design history: a charge-as-you-write budget was built first and failed its off-plan calibration pilot (organisms
cannot see R, so copiers spent all income on partial copies; F1 in COUPLING_FAILURE_LEDGER.md). The pilot also set
the two parameterizations below; no scientific run preceded this freeze.

## 2. Parameterizations (separate independent arms; never tuned after launch)

K16: BASE 16, BONUS 64 (a pure copier needs 4 interactions per child; a computing copier affords one per interaction).
K40: BASE 40, BONUS 64 (pure copiers marginally viable; coupling is a relative advantage).
If one parameterization fails, the other is analysed as preregistered; no third is added.

## 3. Coupling modes (arms)

ON (correct -> BONUS to the organism) | OFF (base only) | SHUFFLED (output compared with the answer for an
independent unseen input) | RANDOM_REWARD (correct -> BONUS to a uniformly random living organism) | YOKED (tick t's
bonus total of the matched ON run, same seed, divided equally among the living: identical supply, no contingency) |
IRRELEVANT (first output == 0x5A -> BONUS) | DELAYED (credit 60 ticks later, lifespan 40: beyond relevance) |
v2/NONE (no ledger; the grounded reproducer positive control).

## 4. Common settings, fixtures, seeds

ticks 500, cells 256, budget 256, GRID/LOCAL, Z80_64, SHARED, ENDOGENOUS_COPY, IMPLICIT, NEUTRAL scoring, ABR,
FIXED env, BYTE mutation MED, init RANDOM with init_tapes (32 fixture copies among 128 initial organisms;
alternating when two fixtures). Fixtures (coupling_campaign.fixtures; properties tested): REP (8-byte LDIR copier),
HYB (REP + relocated task witness), NOCOMP (HYB with its OUT removed), NOCOPY (HYB with LDIR removed), RANDOUT (REP +
constant output 0x33), BAD (a C = 0 LDIR sweep before the witness: copies itself but wrecks its own task), CORRUPT
(writes the input region before computing), MULTI (three OUTs), SLIDER (all-zero tape). Seeds: 11e12 + lane*1e9 +
block*1e5 + k; arms of one pair share the seed (identical initial population and world-rng stream; the coupling has
its own rng). AUTO seeds 11e12 + 50e9 + ...; EXT seeds 11e12 + 60e9 + ...; pilot seeds were 7e12..7.5e12.

## 5. Lanes, cells, allocation (Phase 1 = 11,372 runs; plan sha256 in s12)

A  qualification (K16 and K40; 40 seeds): A1 HYB ON, A2 HYB OFF, A3 NOCOMP ON, A4 NOCOPY ON, A5 HYB SHUFFLED,
   A6 RANDOUT ON, A7 REP ON; K16 also A8 REP v2 (positive reproducer).                           600
I  exploit probes (K16 ON, 30 seeds): SLIDER + HYB, CORRUPT, MULTI.                                90
C  edge ablation (mixed REP + HYB, INC; K16/K40; 150 seeds): ON, OFF, RANDOM_REWARD, DELAYED, IRRELEVANT, YOKED. 1,800
E2 conflict repair (REP + BAD; K16/K40; 60 seeds): ON, OFF, YOKED.                                 360
F  task generality (mixed REP + HYB(task); K16; 80 seeds): CONST, ECHO, INC, COND_ONE, SUM2, COND_MULTI x ON/OFF/YOKED. 1,440
G  substrate (mixed INC; K16; 80 seeds; ON vs OFF): copy_cost 2, LDIR cost x4, undefined -> HALT, mutation LOW,
   mutation VLOW, VM_COPY, BYTECODE32, CONSTRUCTIVE.                                               1,280
B-rand fresh random populations (INC, CONST; K16/K40; 200 seeds): ON, OFF, SHUFFLED, YOKED.         3,200
B-cop  pure-copier start, no task code (ECHO, CONST; K16/K40; 150 seeds): ON, OFF, SHUFFLED, YOKED.  2,400
J  historical specimens alone (K16; ON vs OFF): 30 sustained + 15 transient historical origins, 30 beneficial-
   density-flagged specimens, 6 copier-damaged-task grafts, 20 failed non-replicators (coupling_inputs.json).   202
Fixed-allocation guarantee: Phase 1 is entirely fixed allocation; Phases 2/EXT only ADD runs.

## 6. Frozen per-run metrics (tools/coupling_analysis.py)

competence: a tape is COMPETENT iff, alone (empty window), it answers every input of the configured task's fixed
16-input panel exactly (tasks.verify_tape). comp_final = competent organisms at tick 500 / 256 (0 if extinct).
comp_sr_alive = >= 1 competent organism born by SELF_REPLICATION alive at the end. Birth competence: on a
deterministic 1-in-8 sample of all births, writer competence; for SELF_REPLICATION births also child competence.
r_cc = P(child competent | competent SR parent), r_nc = P(child competent | non-competent SR parent) (runs with >= 20
sampled births of that class). enrichment = (share of sampled births by competent writers) / (time-mean competent
share of the living, sampled every 10 ticks). denovo_competent_sr = the dominant competent SR tape at the end exists
and is not byte-identical to any fixture of the run. paid_births = constructions paid (= births) in the run.
Architecture (Lane D/E; adjudication.arch_descriptor, frozen): self_copy, copy_op, copy_pc, copy_len, copy_src range,
task_pcs, task_before_copy, copy_covers_task, n_copy_ops, exec_own_bytes, uses_io, task_accuracy, nonzero_bytes.
Exploit probe (every run): correct outputs by organisms whose own tape is NOT competent (partner-code execution,
lucky partial solvers, input manipulation), with up to 20 specimen tapes per run.

## 7. Primary hypotheses (confirmatory; K16; unit = seed pair; exact sign test on the paired difference, ties
dropped; Holm across P1-P6)

P1 correct computation raises reproductive output: Lane A paid_births A1 > A3.
P2 descendant enrichment of competence specifically under contingent earning: Lane C comp_final ON > YOKED.
P3 heritability: in Lane C ON runs, r_cc - r_nc > 0 (unit = run; sign test).
P4 contingent computation lowers extinction: Lane C extinction YOKED > ON.
P5 preservation across reproduction: Lane C r_cc ON > YOKED (pairs where both defined).
P6 conflict repair: Lane E2 comp_sr_alive ON > OFF.
Secondary (reported, labelled): every other arm contrast in A, C, E2 (and all K40 versions); Lane F per-task ON vs
YOKED and ON vs OFF; Lane G per-perturbation ON vs OFF; Lane B denovo_competent_sr ON vs YOKED / OFF / SHUFFLED and
spontaneous replication by arm; Lane I probe outcomes; Lane J by specimen kind; enrichment distributions;
architecture descriptors. Exploratory: anything not listed here, labelled as such.

## 8. Automatic decision tree (no human input)

Phase 1 (fixed, s5) -> Phase 2 AUTO (coupling_campaign.phase2_plan, frozen): candidates = dominant competent
self-replicating tapes at the end of ON runs in B-rand, B-cop, E2 that are not identical to a fixture, self-copy and
are fully competent alone; first 8 per cell by run id; cap 120. Each: transplanted alone into fresh random
populations, 3 seeds x {ON, OFF, RANDOM_REWARD, ON with OUT removed, ON with copy ops removed}. Verdict (frozen):
CAUSAL_COUPLED if ON succeeds (competent SR alive at end) in >= 2/3 AND OFF + RANDOM_REWARD succeed in <= 1/6 AND the
task-ablated version succeeds in <= 1/3; SURVIVES_WITHOUT_COUPLING_OR_TASK if ON >= 2/3 otherwise; NOT_REPRODUCED
else. -> EXT (extension_plan, frozen): for Lane C K16 and each B-cop K16 cell, if the 95% half-width of the paired
ON - YOKED comp_final difference exceeds 0.10, one extra block of 60 seeds for every arm of that cell (max one).
No lane's outcome redefines another lane. No early futility stop (runs of dead worlds cost seconds).

## 9. Stop rule

Phase 1 runs in lane priority A, I, C, E2, F, G, B-cop, B-rand, J; cap 18 h after the FIRST start. Phases 2 + EXT
cap 22 h after the first start. Analysis must finish before 25 h. Runs not completed at a cap are reported NOT_RUN
by cell. A restart re-executes only runs without a result line (each run is a pure function of its spec). Voids
(exceptions, ledger imbalance) are recorded, never re-seeded.

## 10. Exclusions

None, except VOID runs (listed by id). Extinct runs are data (comp_final 0, r_cc undefined). YOKED arms whose ON
partner voided receive an empty yoke (recorded).

## 11. Readiness rule (frozen; directive Phase "FINAL READINESS")

instrument_ok := no VOID runs, no ledger imbalance, a seeded 3% replay sample of Phase 1+EXT byte-identical, and the
A8 positive reproducer persists in >= 90% of seeds.
core := P1 AND P2 AND P3 hold (Holm-adjusted p < 0.05, predicted direction).
novelty := P6 holds OR >= 3 AUTO candidates are CAUSAL_COUPLED spanning >= 2 distinct mechanism keys.
generality := >= 3 of 6 Lane F tasks show ON > YOKED (p < 0.05) AND >= 4 of 8 Lane G perturbations show ON > OFF.
Classification: not instrument_ok -> INSTRUMENT_REPAIR_REQUIRED; core AND novelty AND generality ->
READY_FOR_MULTIDAY; core only -> READY_WITH_RESTRICTED_SCOPE (scope = the tasks/perturbations where P2-type effects
replicated); otherwise REPHYSICS_REQUIRED.

## 12. Freeze record

Phase-1 plan sha256 a3bc8c8ea60ceb00e9a85ff713e95ced9b6cf32009939c4867a9d65aa3400950 (11,372 runs).
Frozen file sha256 (working-tree LF bytes at the freezing commit):
  prometheus/z80atlas/coupling.py            65c9832ee5b5bcff746874cbd1fd86b3469f305fe485ea5612caf8b688f94ac3
  prometheus/z80atlas/world.py               e8dacd5c84e07793a6e50a354a03e3550a8834ad9dd3fc41524530b0a04eb2c1
  prometheus/z80atlas/vm.py                  b68115534d785bdd7b7e1c6ba656f637e58782e98746ab4ea325c16db22b21a2
  prometheus/z80atlas/coupling_campaign.py   1f5f978d02c89e1ab5d6ad008dd780a64dbfad20265293628f3e0037b8fe2032
  prometheus/z80atlas/adjudication.py        8682629b64626bfc791aa76ba3ac9301aeb493ca36e3a5b6153f2a1cccfb4aff
  prometheus/z80atlas/tasks.py               cdf9df5d83a7c5b28ebd624e9c9bd46666ec2235214cecb697b5ab50109e4699
  prometheus/z80atlas/runner.py              fe278c8b19e0dd372932275820df81f6947fade7c500eb0866813df9fc37a495
  tools/coupling_analysis.py                 e2d9497342611e66f5d7e0c6818d1d3219146b9296a5ac534cda553e9fb8f022
  receipts/coupling_inputs.json              fe495ece842756c089970d528c54eee30cf89ac026f47a46a441732f380bff96
Tests at freeze: 58/58 z80atlas tests. Pipeline smoke (seeds shifted -3.5e12, 40 pairs, all phases + analysis +
replay 8/8) passed; smoke artifacts discarded. Pre-freeze fixes found by the smoke: batch executor stalls ->
continuous submission (scheduling only); empty-cell means; C/F/G fixture descendants excluded from independent
origins (counted as variants).
Launch: pinned copy of the freezing commit at C:/Users/James/z80atlas_coupling_2026-09-24/code;
  python -m prometheus.z80atlas.coupling_campaign --workdir C:/Users/James/z80atlas_coupling_2026-09-24
         --inputs <pinned>/coupling_inputs.json --workers 20
Analysis (after stop): tools/coupling_analysis.py --workdir <that> --code <pinned code> --inputs <pinned inputs> --replay 0.03
