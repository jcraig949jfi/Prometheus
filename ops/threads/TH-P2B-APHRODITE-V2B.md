# TH-P2B-APHRODITE-V2B -- Aphrodite V2-B: Improvement-Process Maturation

epic: EP-PHASE2B

| Field | Value |
|---|---|
| Status | ACTIVE / autonomous |
| Owner | Aphrodite |
| Model | Claude Code Opus 5.5 |
| Type | PROGRAM THREAD |
| Authority | operator directive, 2026-10-04 |
| Directive text (verbatim) | roles/Aphrodite/prompts/2026-10-04_v2b_beta01/01_OPERATOR_DIRECTIVE_verbatim.md |
| Parent scientific threads | TH-018 (abstraction compounding), TH-019 (recurrence x visibility), TH-020 (second order / representation), TH-021 (instrument validity). These remain the authoritative scientific history; this thread coordinates their maturation |
| Campaigns | C-006 = C-P2B-APH-BETA-01 (12 DEV/TEST pairs, nominally 96 h) |

## Governance (published explicitly at the operator's request)

**CWOs may delegate work to Aphrodite; they do not activate Aphrodite.**

- Aphrodite selects and executes work inside this thread without Aporia dispatch, CWO assignment, or any other
  coordinator's permission.
- This supersedes the earlier Aphrodite NEXT_SESSION.md / WORK_STATE.json language ("awaiting Aporia assignment").
- Aporia and CWOs remain valid INBOUND delegation lanes. At each window boundary Aphrodite checks for applicable CWO work.
  It may fold that work into a DEV or TEST window, sequence it against the autonomous frontier, or report a genuine
  charter or resource conflict.
- A CWO does not terminate this thread unless the operator explicitly says it does.
- Urgent fleet work may preempt the NEXT window. It does not interrupt an atomic experiment in execution unless safety or
  infrastructure integrity requires it.

## Mission

Iteratively improve both (1) the improvement process under study and (2) the apparatus that determines why it
improved. The loop is: design/repair -> experiment -> diagnose -> redesign -> experiment.

The target is an experimental system that can distinguish each of:
- memory;
- search prior;
- reusable abstraction;
- improver change;
- compounding;
- recursive compounding.

The question is APHRODITE-08's: does an improvement process become better at producing future improvements, and if so,
what mechanism actually changed? A positive RSI result is not required.

## Causal ladder (every serious experiment names its rung)

| Rung | Name | Question |
|---|---|---|
| R0 | REPRESENTABLE | Can the representation express the candidate mechanism? |
| R1 | REACHABLE | Does a path to it exist under the declared operators? |
| R2 | FINDABLE | Can the declared search reach it under the allowed resources? |
| R3 | SELECTABLE | Does the validation/fitness process prefer it for the intended reason? |
| R4 | SOLVED | Does it solve held-out members of the target family? |
| R5 | REUSED | Does the inherited object help on genuinely new instances or families? |
| R6 | CAUSAL | Does removing or ablating the inherited structure remove the effect? |
| R7 | IMPROVER_CHANGED | Did the machinery for generating future improvements change, rather than only its stored data or ordering prior? |
| R8 | COMPOUNDED | Did an acquired improvement enable acquisition of a later improvement unavailable to the prior process? |
| R9 | RECURRED | Can the new improvement process itself participate in another such step? |

A negative at R8 is uninterpretable if R0 or R7 was impossible.

## Separable components

Each component is maintained by Aphrodite, and each must stay separable from the others so that an answer cannot leak
between them:
- Task World;
- Worker;
- Improver;
- Inherited State;
- Evaluator/Tribunal;
- Escrow/Meter;
- Ruler;
- Transplant layer.

## Standing rules

- **Evidence tiers 1-4. No silent promotion.** Local-engine evidence is Tier 1-2, never Tier 4. Campaign 1 and every
  live-model experiment remain FROZEN unless separately authorised. There is no GPU or model-host deployment and no
  real-model positive RSI claim.
- **Cadence.** Alternating 4-hour DEV and TEST windows, held as durable state (roles/Aphrodite/beta01/STATE.json). After a
  missed wake, run the due window ONCE; never burst through missed windows. Heavy deterministic shards go to
  Fabric/PrometheusWorkers. Aphrodite remains owner and interpreter.
- **Instrument doctrine.** The standing requirements are:
  - a pre-freeze supply screen;
  - evaluator conformance;
  - a positive control;
  - a matched negative;
  - an equal-expressivity sham;
  - causal knockout;
  - a chance base rate;
  - reachability/representability certificates;
  - escrow/window analysis;
  - extensional identity;
  - held-out transfer separated from development;
  - treatment-blind execution where practical.

  Controls must be able to fail. The historical S4 constant gates and non-discriminating positive control are NEVER
  reproduced as valid controls.
- **Outcomes.** UNTESTABLE, SEARCH_LIMITED, SUPPLY_LIMITED, RULER_FAILED, REPRESENTATION_LIMITED, MEASUREMENT_FAILED,
  INVALID_DESIGN and TECHNICAL_FAILURE / BLOCKED_TECHNICAL are never collapsed into NO.
- **Technical reruns.** The original attempt plus up to 3 reruns. A repair that changes a scientific variable gives the
  experiment a new version.
- **Version boundary.** No representation-changing W5P assay runs without separate authorisation. It may be designed,
  tested and frozen.
- **History is immutable.** Historical labels stay. Repairs produce new experiments and bridge analyses.
- **Evidence contract.** Every window ends with code/spec, a frozen experiment or result, receipts, a report, hashes,
  updated state, and commit -> push -> merge to main. Every TEST gets an external-review packet; every substantial DEV
  gets a repair/design packet.

## Frontier

natural recurrence -> visible recurrence -> selection -> reuse -> mutable improver -> second-order compounding.

Central question: **can an inherited improvement change the machinery that generates the next improvement, and can that
change survive another generation?**

## Log

| Date | Entry |
|---|---|
| 2026-10-04 | Thread opened by operator directive; C-006 (C-P2B-APH-BETA-01) instantiated; DEV window 1 (bootstrap) begins |
| 2026-10-04 | DEV-1 closed. The v2b-1 apparatus is built (engine/v2b/); conformance is GREEN; 3 new historical constant gates were recorded; no labels flip; T01 is frozen. TEST-1 opened |
| 2026-10-04 | TEST-1 (T01 known-answer assay) QUALIFIED: 10/10 cases; full conformance GREEN. DEV-2 opened |
| 2026-10-04 | DEV-2: T53 frozen. Finding: A20-A23 P/OFF_0 controls could not score by construction, so A23 H1's only live control was G1_NC (label unchanged). TEST-2 (T53) launched |

| 2026-10-04 | TEST-2 (T53) closed MEASUREMENT_FAILED (PC_ONE control mis-specified). NEW: A23's G1 SAME pairs in CON1/CON8 are extensional duplicates, so distinct-family G1 REUSED_SAME = 5/10 < k=6 (correction-only; label unchanged). DEV-3 opened |
| 2026-10-04 | DEV-3: apparatus v2b-2 (distinctness screen); t1v2 QUALIFIED. T53 CORRECTION (post-exposure): G1 distinct-class capability 5/10 < 6, shams 8/9/10, so the effect is generic. T52 frozen; TEST-3 launched |

| 2026-10-04 | TEST-3 (T52) MEASURED: selection recovery 0.11/0.46/0.875 by dose; at dose 0, 89% select the SHOWN other motif. A23 selection = shown-structure recovery. DEV-4 opened (T51 design) |
| 2026-10-04 | DEV-4: T51 frozen (LIN seeds 0-7, pooled X_S dose slope, escrow 30k declared, D endpoint at 1M, distinct-class reuse). TEST-4 launched |

| 2026-10-04 | TEST-4 (T51) MEASURED: natural composition-dose slope NOT_SHOWN (p 0.16); G1 not specific. Exploratory: a pristine donor derives the G1 class endogenously from natural supply (57 vs inherited 70 of 256 families beyond PRISTINE). DEV-5 opened (midpoint synthesis) |
| 2026-10-04 | DEV-5: midpoint synthesis 1 (limit = R7). donor_g genome interpreter (g0 conformance 3/3). TEST-5 (GTC R7 probe) launched |
| 2026-10-04 | TEST-5 (GTC R7) INCONCLUSIVE_INSTRUMENT: the UNSEEN stratum is a transfer floor for every library; the rule genomes g2/g3/g4 leave selections unchanged (20/20). DEV-6 opened |
| 2026-10-04 | DEV-6: T51-C frozen (fresh LIN seeds 8-15; endogenous base-class derivation confirmation). TEST-6 launched |

| 2026-10-04 | TEST-6 (T51-C) MEASURED: the frozen confirmation is NOT met (ratio 0.644, base class derived in 3/7 seeds). When derived, 100% of the inherited benefit; otherwise 0. DEV-7 opened (R7 v2) |
| 2026-10-05 | DEV-7: endogenous-route failure modes diagnosed (observation starvation 3/15, selection 4/15). R7E frozen (rule genomes g8/g9 plus ORACLE/NULL controls, no library carried). TEST-7 launched |

| 2026-10-05 | TEST-7 (R7E) MEASUREMENT_FAILED: the oracle candidate was rejected in 5/15 seeds. Diagnostic: on natural supply the binding R3 limit is validation representativeness (the correct abstraction is rejected where VALIDATE does not show it). DEV-8 opened (validation breadth) |
| 2026-10-05 | DEV-8: T08 validation breadth frozen (VALIDATE 4 to 12 on the endogenous route). TEST-8 launched |

| 2026-10-05 | TEST-8 (validation breadth) MEASURED: breadth 12 HURTS (86 to 76), rescuing 1 of 5 seeds. The R3 limit is the selection criterion (average saving vs subset benefit), not the amount of evidence. DEV-9 opened (midpoint synthesis 2) |
| 2026-10-05 | DEV-9: midpoint synthesis 2 (the limit is the R3 selection criterion). T09 frozen (subset-benefit criterion g10, fresh breadth-12 validation). TEST-9 opens with a compute hold until about 12:45Z (rolling 48 core-h cap) |

| 2026-10-05 | TEST-9 (T09 subset criterion g10) MEASURED, NOT positive: NULL gate passed (OFF selected 0/15). g0 93 vs g10 98, better/worse/tied 1/0/14, p 0.5. g10 and g0 select the same schema in 14/15 seeds. The empty seeds are candidacy failures (0, 7 and 12 derive nothing; 9 derives the wrong class) plus validation content (14). Revision of midpoint 2: the R3 criterion is not the dominant limit on fresh supply (g0 at breadth 12 swings 76 vs 93 across draws). First broken rung = candidacy. DEV-10 opened (OBSERVE breadth) |
| 2026-10-05 | DEV-10: first broken rung = candidacy (R2). T10 frozen: OBSERVE breadth 4 to 10 under g10, everything else fixed at T09; continuity 2/2 exact. TEST-10 launched |
| 2026-10-05 | TEST-10 (T10 OBSERVE breadth) MEASURED: gate passed. CANDIDACY_POSITIVE NO (98 to 99, 4/3/8, p 0.5). STARVATION_RESCUE YES (seed 0: 0 to 11; seed 7: 0 to 3; seed 9: 0 to 5). Losses where derivation re-partitions (seed 6: 8 to 0; 13: 7 to 0). Derivation is non-monotone in observation; first broken rung = R2 derivation stability. DEV-11 opened |
| 2026-10-05 | DEV-11: the diagnostic REFUTES non-monotone derivation. MEMORISE (stored observed programs) wins selection in T09 seeds 7, 9 and 14 and T10 seeds 6, 12, 13 and 14, and never transfers. Errata added to the T09/T10 reports. T11 frozen: g11 = g10 minus MEMORISE in candidacy; K1/K2 pass. TEST-11 launched |
| 2026-10-05 | TEST-11 (g11 = g10 minus MEMORISE) MEASURED: gate passed. Primary NOT positive (123 vs 99, 4/0/11, p 0.0625, the attainable minimum: underpowered pre-registration, recorded). Cumulative vs I_0 NOT positive (123 vs 93, 6/2/7, p 0.14). Mechanism confirmed: every seed MEMORISE had won gains, 0 harmed. Exposed seeds; no R7 label issued. DEV-12 opened (powered fresh-seed replication) |
| 2026-10-05 | DEV-12: first broken rung = evidential (the improver package has no unexposed, powered replication). T12 frozen: fresh W8 LIN 16-23, g11 O10 vs I_0 (sign-flip primary), NULL gate; K1/K2 pass; power limit stated before data. TEST-12 launched |
| 2026-10-05 | TEST-12 (fresh-seed replication, LIN 16-23) MEASURED, POSITIVE: g11 O10 60 vs I_0 20 held-out families, 5/0/3, sign-flip p 0.031 (= the attainable minimum); NULL gate passed. The effect is carried by abstraction-only candidacy (g10 O10 = I_0). First replicated R7 at tier 2; not R8 or RSI |
| 2026-10-05 | **BETA-01 CLOSED.** The close synthesis (beta01/windows/BETA01_CLOSE_SYNTHESIS.md) answers the 7 questions. The historical improver's acceptance test prefers memorisation over abstraction on natural supply; with that repaired, the ladder stops at R8 (untested). W5P is not yet justified |
| 2026-10-06 | **BETA-02 OPENED** (operator directive 2026-10-05; campaign C-007). Beta-01/T12 accepted as IMPROVER_CHANGE_REPLICATED_LOCAL = YES, tier 2, first-order only, R8 untested. Pre-registration roles/Aphrodite/beta02/BETA02_PREREG.md is frozen before any outcome: E1 replication (24 fresh LIN seeds 24-47, power about 0.8); E2 factorial (rules g0/g0x/g10/g11 x O4/O10); E3 R8 (gated; unseen LIN 48-71; next-generation improvement over its own inherited library). K0-K5 pass |
| 2026-10-06 | Beta-02 E1/E2 MEASURED (22 unexposed seeds, LIN 24-47). E1 replication: g11 @ O10 162 vs I_0 63, 16/0/6, p 1.5e-5. E2: MEMORISE exclusion is the cause (+2.52 per seed, Holm-significant; it holds at O4 too, so G11_ONLY_WORKS_AT_O10 = NO); the g10 criterion alone is null; width is additive (+1.57) but not Holm-significant; interaction null. I_0 picks memorisation in 11/22 seeds. REPLICATION_GATE PASS, so R8 was launched |
| 2026-10-06 | Beta-02 E3 R8 = **NO** (20 unseen-lineage pairs). Next-generation improvement with L_g11 10 vs L_I0 39 (0/5/15) under I_0 machinery; also NO under g11 machinery. The g11 library carries capability across lineages (104 vs 32 families) but substitutes for, rather than enables, the next generation's improvement. Frozen reading: first-order inheritance only |
| 2026-10-06 | **BETA-02 CLOSED** (C-007): improver change replicated and mechanism = memorisation exclusion; R8 NO. Report: roles/Aphrodite/beta02/R8_REPORT_AND_BETA02_CLOSE.md. W5P / representation depth is now directly motivated by the R8 failure but stays separately authorised; LLM bridge parked |
| 2026-10-08 | **BETA-03 ACTIVATED** (operator directive 2026-10-08; C-011 -- id corrected from C-008, which belongs to Themis; 48 h, 12 windows; W5P authorised, bounded). W01: R8 autopsy on frozen Beta-02 data (diagnostic): about 93% of the deficit under g11 machinery is unequal headroom; the residual on the common opportunity set is -7, n.s.; 88% of the common residual is unacquired by any arm. E1 frozen (fresh LIN 72-119, common-residual endpoint, positive control). Leads (W5P / g12 / ecology) launched in separate worktrees |
