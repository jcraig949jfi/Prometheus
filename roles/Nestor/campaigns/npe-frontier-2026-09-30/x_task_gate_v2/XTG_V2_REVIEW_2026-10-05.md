+==============================================================================+
|  REVIEW PACKET -- X-TASK-GATE v2: ENDOGENOUS TASK-COUPLED DESCENT            |
|  Author : Nestor (seat), host BUCKKEEP, CPU only                             |
|  Date   : 2026-10-05                                                         |
|  For    : operator (HITL) + external reviewers                               |
|  Status : CLOSED -- Stage 0 INSTRUMENT_UNREACHABLE (TRANSIENT_ONLY);         |
|           Stage 1 NOT run (frozen stop rule)                                 |
|  Self-contained: no repository access is needed to read this packet          |
+==============================================================================+

-----
0. SUMMARY
-----

Question:
  Can task competence spread through the organisms' OWN causal replication
  (P-11 certified) when the chance that two organisms interact depends on
  their competence? The alternative is that it appears only through
  injection, sorting, bookkeeping or a broken ruler.

Verdict:
  Stage 0 = INSTRUMENT_UNREACHABLE. Descriptive subtype: TRANSIENT_ONLY.

  Stage 0 planted the planted-positive genome CT_UA (a copier plus a correct
  task routine) on the pair-tape path:
    - it established in 4/6 runs;
    - it produced task-competent, P-11-born descendants carrying TRANSMITTED
      competence: CD_TX peaked at 0.40-0.54 of the population at epochs 20-30;
    - the routine was then lost from every copy by epochs 60-90, while the
      copier stayed fixed to epoch 2000;
    - final-state CD_TX >= 0.10 occurred in 0/6 runs (the rule needed 3/6).

  Both negatives were rejected in 6/6 runs each:
    - CT_U (reads the cue, ignores it);
    - COPY_ONLY.
  This held including 9 runaway runs between them.

  By the frozen rule, Stage 1 (random populations, TG vs SHUF) was not run.

Technical status: COMPLETE.
  - 18/18 runs.
  - 841 s wall, 4 workers.
  - <= 88 MB per worker.
  - Code SHA ef6d68cee.

-----
1. WHAT WAS BUILT (committed BEFORE production)
-----

The historical freeze (62d30e443) was invalid and was NOT executed: its
Stage-0 ruler was 0 by construction, and it carried 8 recorded semantic
defects. v2 repairs exactly those defects:

  a. Task pinned STATIC: FORCED_READ ADD37.
     - Inputs are (v, key, r).
     - Expected answer: base = v XOR key when r = 0; base + 37 when r = 1.
     - The old COEVO environment rotated the task away from ADD37 after
       epoch 25.
  b. Competence = CUE-FLIP USE.
     - 16 matched (v, key) pairs, each run with r = 0 AND with r = 1.
     - A pair counts only if both answers are exact.
     - Competent iff use >= 0.75 on a gate set AND on a disjoint held-out set.
     - Any program whose answer does not depend on the cue scores exactly 0.
  c. Cache keyed by (task identity, episode set, genome).
     - Regression RG-1: the same genome under XOR5A misses and scores 0.
  d. Competence is recomputed from the CURRENT genome at every use.
     - This fixes stale and relabelled values.
  e. Provenance: prov INIT / P11 / LABEL, plus the ORIGIN of the current
     competence:
       INIT               competent from the start
       P11_TX / LABEL_TX  carried in from a competent donor
       *_CREATED          created at a birth
       MUT                created by in-place mutation
     A creation-root log and a transmission-hop count are kept.
     The decisive quantity:
       CD_TX = competent AND P-11 born AND origin P11_TX.
  f. Stage 0 plants CT_UA ON THE PAIR PATH.
     - This is the repair the historical design lacked.

Static known answers (cue-flip use, gate / held sets):

  construct   use (gate / held)   old bridge   old ruler
  ---------   -----------------   ----------   ------------------------------
  CT_UA       1.0 / 1.0           1.0          competent
  CT_U        0 / 0               0.75         PASSES (reads 3) -- the defect
                                                 the repair targets
  COPY_ONLY   0 / 0               0            fails
  witness     1.0                 --           world witness

Tests: 5/5 pass.

Repair found in Flight 1:
  - Defect: the donor's state was read AFTER its own in-place mutation in
    the same interaction, so carried competence was mislabelled *_CREATED.
  - Fixed. Test PV-3 FAILS on the pre-fix code and passes on the fixed code
    (checked).
  - Semantics: provenance labels only; no world change.

-----
2. WHY IT MATTERS
-----

Prior Nestor work established, in this pair-tape world, that:
  - causal copying arises;
  - copying establishes lineages;
  - material becomes endogenous.

The next rung: can causal heredity carry a USEFUL functional property under
endogenous dynamics?

-----
3. DESIGN AS EXECUTED
-----

World:
  - The ffa6 cell, dense VM, ATOMIC write-back runner.
  - Population 256; 2000 epochs; slice 300.
  - Z8_SLOTTED, OPERAND mutation at rate LOW (about 0.13 mutations per
    genome per interaction).
  - Pressure TASK_GATED_INTERACTION:
      p_interact = 0.15 + 0.85 * max(u_a, u_b)
    where u is the use score of the CURRENT genome.

Stage 0 (seeds 43_000_000 + s, s < 6, backgrounds paired across arms):
  - One organism is planted per run; the other 255 are random.
  - Arms:
      PAIR_POS = CT_UA
      PAIR_READ_NO_USE = CT_U
      PAIR_COPY_ONLY

Stage 0 PASS iff all of:
  - CT_UA final CD_TX >= 0.10 in >= 3/6 runs;
  - each negative has 0/6 runs with CD >= 0.10;
  - each negative has 0/6 runs with CS >= 0.10.

Stage 1 (not run):
  - TG vs SHUF, 18 random seeds each.
  - SHUF reads the gate from two other random organisms.

-----
4. FLIGHTS (disclosed in the prereg BEFORE the freeze)
-----

Setup:
  - Flight seeds 43_900_000 + s; 12 runs per stage-0 arm-set; full length.

PAIR_POS:
  - Final CD_TX = 0 in 6/6 runs.
  - Established in 3/6.
  - A 10-epoch trace of one established run:

      epoch    10    20    30    40    50    60
      CD_TX  0.32  0.48  0.28  0.21  0.14  0.06

Negatives:
  - CD = CS = 0 everywhere.

Scaling:
  - 3 workers: 6 jobs in 270 s.
  - 6 workers: 12 jobs in 565 s (per-run wall time x1.75).
  - No throughput gain, so production used 4 workers.

Response to the flights:
  - The prereg declared the expected outcome INSTRUMENT_UNREACHABLE in
    advance.
  - The decisive rule was NOT loosened.
  - No world parameter was changed in response to the flights.

-----
5. RESULTS (production Stage 0, exact)
-----

  arm               seed  est  depth  CD_TX_peak@e  CS=0 from  final CD_TX
  PAIR_POS          +0    no     1    0            --         0
  PAIR_POS          +1    yes  107    0.543 @20    e90        0
  PAIR_POS          +2    no     1    0            --         0
  PAIR_POS          +3    yes  112    0.414 @20    e80        0
  PAIR_POS          +4    yes   86    0.398 @30    e80        0
  PAIR_POS          +5    yes   85    0.406 @20    e60        0
  PAIR_READ_NO_USE  +0..5 4/6 established, depth 88-113;
                          CD = CS = 0 at final and at every snapshot
  PAIR_COPY_ONLY    +0..5 5/6 established, depth 91-123;
                          CD = CS = 0 at final and at every snapshot

Final P11-born share in established runs: 0.77-1.0. The copier is fixed.

P-11 events per established run: about 24k-34k.

Interaction rate:
  - PAIR_POS: 0.160-0.163.
  - Negatives: about 0.149.
  - Both are near the 0.15 floor, so the gate is almost never opened once
    competence is lost.

Competence-creation roots in PAIR_POS:
  - INIT 1 per run.
  - In addition, across the established runs: MUT 5, P11_CREATED 3.
  - None persisted.

STAGE0.json:
  stage0 = INSTRUMENT_UNREACHABLE
  pos_runs_CD_TX_ge_0.10 = 0
  neg CD / CS runs = 0 / 0 (both arms)
  descriptive_subtype = TRANSIENT_ONLY  (peak >= 0.10 in 4/6)

-----
6. INCIDENTS / PROCESS
-----

- One provenance-ordering defect was found in Flight 1 and repaired before
  the freeze, with a fail-on-old regression test (PV-3).
- The plant is lost early in about one third of seeds. This is
  establishment stochasticity; the same seed fails across the paired arms.
- No crash, OOM or thermal issue.
- BUCKKEEP has 16 logical CPUs, but scaling is poor beyond 3-4 processes.

-----
7. WHAT THIS DOES AND DOES NOT ESTABLISH
-----

DOES establish (measured):
  - The cue-flip use ruler separates USE from READING and from COPYING:
    statically, and dynamically through runaway copying.
  - The old "competent and reader" ruler does not: CT_U passes it.
  - In this world, causal replication CAN carry a task routine across many
    P-11 generations. The competence of up to 54% of the population was
    transmitted from the planted competent founder.
  - The world does NOT MAINTAIN the routine:
      - it is extinct within 60-90 epochs of a 2000-epoch run;
      - the copier persists.

Mechanism reading (inferred, not separately tested):
  - The symmetric interaction-rate gate gives a competent organism more
    interactions.
  - But every interaction both copies it and overwrites it, and mutates
    both halves.
  - So nothing selects for the routine against mutation.

Does NOT establish:
  - Anything about random populations: Stage 1 was not run.
  - Whether the gate is neutral or harmful to competence: no "no gate" arm.
  - Anything about other worlds, other mutation rates, multiple plants, or
    asymmetric gates.

Claim ceiling: one cell, one gate form, final-state readout.

-----
8. DECISION / RECOMMENDATION
-----

Under the frozen rule this line STOPS. Stage 1 was not run and should not be
run on this design. Running it would yield an uninterpretable FLOOR or NO
REGIME.

Nestor's lean (the operator's call), if task-coupled heredity remains
priority:
  - a NEW preregistered experiment, not an amendment;
  - competence buys a replication ASYMMETRY: it decides who copies whom, or
    protects the competent half from being overwritten;
  - matched against the same CT_UA / CT_U / COPY_ONLY qualification, which
    is now built and tested.

"Not worth continuing" is an acceptable answer:
  - the transient result is itself the finding for this world;
  - the program could move on.

-----
9. QUESTIONS FOR THE REVIEWER
-----

1. Is a FINAL-state readout the right qualification for Stage 0?
   - A reviewer may argue that "the ruler fires (peak 0.54)" suffices.
   - I hold that it does not, because Stage 1 reads the final state. Attack
     that.
2. Is the transient purely mutational erosion, or could part of it be a
   measurement artifact?
   - For example, the plain scoring VM versus the dense world VM.
   - CT_UA was verified on the plain VM, as the world itself scores.
3. Does a 16-pair exact cue-flip test with a 0.75 bar risk false negatives
   for partially competent evolved programs, in a way that would matter for
   Stage 1?
4. Would a no-gate control have been necessary to read anything from
   Stage 0? Is "gate neutral vs harmful" worth one cheap run?
5. Is a single plant per run a design defect for a reachability test,
   rather than a world property?

-----
10. ARTIFACTS
-----

Location: branch nestor/buckkeep-boot-2026-10-05 (pushed)

Commits:
  5c585c035  prep: directive verbatim, instrument, tests
  ef6d68cee  FREEZE (PREREG_V2.md + code + flight evidence)
  7a521dc91  RESULT

Directory: roles/Nestor/campaigns/npe-frontier-2026-09-30/x_task_gate_v2/
  PREREG_V2.md
  RESULT.md
  STAGE0.json
  MECHANISM_STAGE0.txt
  xtg2.py
  test_xtg2.py
  results/stage0/      18 rows + detail .json.gz + RECEIPT
  flights/             f1_dyn, f2_scale

Directive: roles/Nestor/prompts/2026-10-05_xtg_v2_science_order/ (MANIFEST verified)

Historical freeze (untouched): ../x_task_gate/ @ 62d30e443

+==============================================================================+
|  END. Reviewer: "this line is not worth continuing" is a first-class answer. |
+==============================================================================+
