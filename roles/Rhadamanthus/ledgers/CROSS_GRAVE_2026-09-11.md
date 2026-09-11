# Cross-grave comparison, first native trial (2026-09-11)

Keeper: Rhadamanthus. Trial branch rhadamanthus/native-trial-2026-09-11,
read at 776c90ea6 (validate.py twice ALL GREEN, 7 dossiers, 5 monsters).
Numbers below are computed from the dossier JSON, not transcribed from
prose (script in the journal entry of the same date). RHAD-25.

Charter constraint applied: the three migrated graves (Argos, Coeus,
Hephaestus) and their 3/3 UNFAIR are ZERO-WEIGHT evidence. Section 3
cites them as contrast only; nothing in sections 1-2 depends on them.

## 1. The three native graves side by side

  grave   fair_test primary_cause     classification          certs (U/PU/O/NR)
  ------  --------- ----------------- ----------------------- -----------------
  Pollux  UNFAIR    DESIGN_ERROR      NO_FAIR_TEST_ON_RECORD  1/3/2/0 of 6
  Erebos  UNFAIR    MEASUREMENT_ERROR NO_FAIR_TEST_ON_RECORD  2/2/3/0 of 7
  Nous    UNFAIR    DESIGN_ERROR      NO_FAIR_TEST_ON_RECORD  0/3/3/1 of 7

  layer            Pollux        Erebos        Nous
  ---------------  ------------  ------------  ------------
  HYPOTHESIS       NOT_EXAMINED  NOT_EXAMINED  NOT_EXAMINED
  DESIGN           INVALID LB    INVALID LB    INVALID LB
  IMPLEMENTATION   INVALID       VALID         VALID
  CONFIGURATION    VALID         NOT_EXAMINED  INVALID
  EXECUTION        VALID         INVALID LB    VALID
  INSTRUMENTATION  INVALID LB    INVALID LB    INVALID
  MEASUREMENT      INVALID LB    INVALID LB    INVALID LB
  INTERPRETATION   INVALID       INVALID LB    INVALID LB
  ECOSYSTEM        INVALID       INVALID       INVALID LB

  evidence rows                     34           42           46
  organs executed / not / unknown   9/4/6        9/1/8        8/2/6
  surviving_claims                  5            5            5
  uncertainty rows                  5            7            4
  contradictory_evidence rows       5            5            3
  unresolved_questions              5            9            9
  Frankenstein repair (DESIGN ONLY) FRANK-004    FRANK-002    FRANK-003
  Zombies                           0            0            0
  Cleric verdict sought TRUE_CORPSE no           no           no

Shared by all three (this is the finding, not the table):

  (a) UNFAIR with classification NO_FAIR_TEST_ON_RECORD. In none of the
      three does the record contain a test that could have returned the
      organism's premise FALSE at power. That is not the same as the
      premise being true; it is the statement that the certificate
      "dead" was issued without the experiment that would license it.
  (b) HYPOTHESIS NOT_EXAMINED on all three. Necropolis never reached the
      question the charter actually asks ("was the premise wrong") because
      a lower layer failed first in every case. The stack's nine layers
      are ordered so that a DESIGN or MEASUREMENT failure masks the
      hypothesis; the trial therefore says nothing about whether any of
      the three premises is alive. It says only that they were not killed.
  (c) DESIGN INVALID and load-bearing on all three; MEASUREMENT INVALID
      and load-bearing on all three; ECOSYSTEM INVALID on all three
      (nothing consumed what was emitted, or the consumer was halted from
      outside). The three graves fail at the same two layers and are
      abandoned in the same way.
  (d) Certificates: 20 on record, 19 reviewed: 3 UPHELD (16%), 8
      PARTIALLY_UPHELD, 8 OVERTURNED, 1 NOT_REVIEWED. The historical death
      certificates were wrong or half-wrong 16 times in 19 reviewed.
      This is the strongest single number in the trial and it supports
      the governing law (Necropolis does not inherit death certificates)
      empirically rather than by fiat.
  (e) No Cleric argued TRUE_CORPSE or HYPOTHESIS_FAILURE on any grave, and
      each Cleric was asked to. The record on all three lacks the
      artefacts a TRUE_CORPSE argument needs (an executed, seeded,
      powered null against the premise). This is the outcome the charter
      warned about ("a graveyard in which everything can supposedly be
      resurrected is evidence that Necropolis has become mythology") and
      it must be read two ways: either the three graves really were
      never tested, or the doctrine as written cannot reach TRUE_CORPSE
      from artefacts alone. D-84 and D-85 record the second reading as an
      open doctrine defect; section 4 below records what would falsify
      the first.

Where they differ:

  - EXECUTION: Pollux and Nous ran what they were designed to run
    (Pollux settling verified by the Keeper's live query, 47 rows, unique
    k=47 v0.5 prefix; Nous keys were re-run by the May forge). Erebos did
    not: the pre-registered Phase 3.K kill test never ran (D-77). Erebos
    is therefore the only native grave with an execution failure of its
    own; the other two are design/measurement failures of experiments
    that ran to completion.
  - IMPLEMENTATION: only Pollux carries code bugs (two, neither
    load-bearing: replay semantics on pool exhaustion, and the unreachable
    pollux_no_correlation_observed branch). Erebos and Nous code did what
    the code said.
  - Executed evidence: the organ inventory shows 9/9/8 organs executed
    by a Necromancer or Keeper for Pollux/Erebos/Nous, so all three
    passes ran code rather than only reading it. The difference is what
    could be run against: Pollux against live M2 settling state and the
    committed daemon, Erebos against committed ITER artefacts, Nous
    against the sampler and prompt only -- its logs and runs were
    gitignored (D-67) and the historical judge cannot be re-run. The
    Nous MEASUREMENT and INTERPRETATION verdicts therefore rest on the
    weakest evidence class of the three and the receipt says so.
  - Primary cause: DESIGN on Pollux (no null, no chance floor, a
    correlation statistic that cannot distinguish subset structure from
    table structure) and Nous (no control arm; self-rating as selection
    criterion), MEASUREMENT on Erebos (outcome column carried pipeline
    state, not the named quantity). Under the D-62/D-83 ruling (cause of
    the QUESTION being unanswerable) these are the same class of defect
    wearing two labels: the recorded number was never the number the
    hypothesis was about.

## 2. What this does to the charter's target statement

Target: "Prometheus mostly buried assembly failures." The charter asks
me to try to discover whether that is FALSE.

For the three native graves it is false as stated. None of the three
died because parts failed to assemble:

  - Pollux assembled, ran, settled 47 pairs and promoted/rejected them
    on schedule; its death is that the statistic it settled on cannot
    answer its own question.
  - Erebos assembled and ran (ITER-100 is the last on record); its
    death is that the outcome column measured pipeline state, and the
    one test that could have decided it was designed and not run.
  - Nous assembled, ran, and fed the forge for two months; its death is
    that it had no control arm, so the forge signal it produced was
    uninterpretable.

All three are failures of experiments that ran, not failures to build
an experiment. The nearest thing to an assembly failure is Erebos's
unrun kill test, and that is an execution decision by the author, not a
part that would not fit.

Counter-reading recorded, not resolved: "assembly failure" could be read
at the ECOSYSTEM layer (the organism assembled but the fleet never
assembled around it -- no consumer, halted from outside). All three
carry ECOSYSTEM INVALID. On that reading the statement is partly true of
the three, but it is true in a sense that makes it unfalsifiable for any
May-fleet grave (D-64: the fleet-wide halt has no class of its own).
Whoever wrote the target statement should say which reading they meant;
I filed the question as a HITL item rather than choosing.

Scope: three graves, chosen by the charter, is not a sample of the
graveyard. The migrated three (section 3) are a different investigator's
work and are zero-weight. A base-rate claim about "mostly" needs the
count over the roster (48 agents, 43 disposition-covered); this trial
does not license it in either direction.

## 3. Migrated three as contrast only (zero-weight evidence)

  grave       fair_test primary_cause     classification          certs
  ----------  --------- ----------------- ----------------------- ------------
  Argos       UNFAIR    DESIGN_ERROR      ORCHESTRATION_FAILURE   0/1/1/0 of 2
  Coeus       UNFAIR    MEASUREMENT_ERROR MEASUREMENT_FAILURE     0/1/1/0 of 2
  Hephaestus  UNFAIR    INSTRUMENT_ERROR  NO_FAIR_TEST_ON_RECORD  1/1/0/1 of 3
  organs executed / not / unknown: Argos 5/1/8, Coeus 4/0/6, Hephaestus 4/2/7

Contrast points, cited for what they say about the INSTRUMENT
(Necropolis) rather than about the graves:

  - The migrated dossiers carry 2-3 certificates and 23-26 evidence rows
    each; the native three carry 6-7 certificates and 34-46 rows, with a
    Cleric pass and a Keeper adjudication on top. The same UNFAIR verdict
    was reached from a thinner record and a single reader. Either the
    migrated verdicts are right for the wrong reasons or the native
    process over-collects; the trial cannot
    tell which, and that is exactly why the charter zero-weights them.
  - Argos is the only dossier with all nine layers INVALID and seven of
    them load-bearing. A stack in which everything is load-bearing
    carries no information about ordering (D-87 family). The native
    three never produced that shape; the Keeper reads that as the native
    process discriminating better, but a Cleric could equally read it as
    the native Keeper being reluctant to mark layers.
  - Two of the migrated three have a descendant_candidate (argos-d1,
    coeus-d1) written into the dossier itself; Nous also carries one
    (nous-d1-control-arm, mirrored by FRANK-003). The native three carry
    their counterfactuals as separate FRANK monsters with kill-before-run
    and organs_inventory_sha. The two forms are not interchangeable and
    the doctrine names only the second (D-88 family: which artefact is
    the proposal of record).
  - The classification vocabulary differs: ORCHESTRATION_FAILURE and
    MEASUREMENT_FAILURE appear only on migrated graves. Whether those
    are retired classes or classes the native Keeper failed to reach is a
    taxonomy question (D-64 adjacent), not a fact about the graves.

## 4. Falsifiers for the trial's own conclusions

Precommitted so the next adjudicator can lose them for me:

  F1  "NO_FAIR_TEST_ON_RECORD on all three" is falsified if any reader
      finds, in the repository at 776c90ea6 or in the M1/M2 stores, an
      executed run that returns the organism's premise FALSE with a
      published null and a seed. Where to look first: Erebos ITER-83/84
      pair-aware null (d7120eb5a) -- the Keeper ruled it underpowered
      (D-72), and that ruling is the softest of the three.
  F2  "HYPOTHESIS NOT_EXAMINED on all three is forced by the stack" is
      falsified if a reader can fill HYPOTHESIS on any of the three from
      artefacts alone without a lower-layer VALID; if so D-84 is a
      Keeper error, not a doctrine gap.
  F3  "The target statement is false for the native three" is falsified
      under the ECOSYSTEM reading (section 2) -- I have already conceded
      that; it is falsified under the parts-did-not-fit reading only if
      one of the three is shown never to have run its main loop. Pollux
      settling rows and Erebos ITER logs make that a hard falsification
      for two of them; Nous depends on the May forge windows (D-69).
  F4  "Certificates wrong 16/20" is falsified by re-review under a
      three-state enum (D-78); several PARTIALLY_UPHELD rows are
      right-in-count-wrong-in-one-inference and a finer enum would move
      them toward UPHELD. The number is enum-sensitive; the direction
      (majority not UPHELD) is not, unless 6+ of the 8 PU rows move.
