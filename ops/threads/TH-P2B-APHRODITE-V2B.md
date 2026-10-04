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
