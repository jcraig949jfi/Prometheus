# Deep Frontier -- decisions (DF-###)

Format: DF-### | when (UTC, from the clock) | decision | evidence | alternative rejected | revisit-if.
Directive verbatim: roles/Archaeon/prompts/2026-09-18_deep_frontier/00_OPERATOR_DIRECTIVE.md.

DF-001 | 2026-09-18 21:58 | REGISTRY SHAPE: append-only JSONL (LINEAGES.jsonl versions, EVENTS.jsonl), one
record per lineage with every directive-s6 field; interpretations a separate field with a
status (PROVISIONAL/OVERTURNED/SURVIVING) so they can never be read as observations;
retirement requires a condition A-E and a non-empty reopen condition (asserted in code).
| registry.py. | Alternative: Postgres tables now -- rejected until Mnemosyne names the
producer (migration 016 is DRAFT); JSONL is committed and diffable. DETERMINISTIC.

DF-002 | 2026-09-18 21:58 | ALLOCATION RULES FROZEN (ALLOCATION_RULES_frozen.json): .40/.40/.20 initial,
floors .20/.15, ceiling .60, epoch 1e5 evaluations or 24 h, yield from registry events,
+-25% step capped at .10 per epoch, AUDIT never rewarded, anti-collapse distant reopen at
.50 single-lineage share for two epochs, relevance floor +-1/16 by >= 3 controlled
descendants. Changing these is a charter change (directive s12) -> operator. | allocation.py.
| Alternative: bandit allocation on a scalar -- rejected (one score; the directive forbids
it). SCIENTIFIC DISCRETION (constants), DETERMINISTIC (application).

DF-003 | 2026-09-18 21:58 | INGEST: 12 seed lineages / 77 transformations from C4 (cliff, exaptation
vs yield), C5 (flat elite, fault asymmetry, hidden load), C6 (population-churn blind spot,
six UNABLE rulers, escalation volume, five novelty misses) and three breadth seeds (40-world
procedural scatter with reserved seeds 10000-10039, world-generator mutation, machinery-
demanding pressures). Lanes: the scatter PROCEDURAL; the rest LLM_PROPOSED (they are my
proposals and say so). NOTHING EXECUTED before G6-0. | ingest.py; registry summary. | -- |
The first frontier is a prepared object; the loop reorders it by allocation.

DF-004 | 2026-09-18 21:58 | FREEZE ECONOMICS (directive s9) implemented as an opt-in segment policy
'tiered' (EVENT_RECORD always; PARTIAL when only 10/11 or unvalidated rulers fire; FULL on an
admitted detector, two corroborating rulers, persistence >= 3 archived generations, or the
seeded 1-in-50 audit draw); Campaign 6's G6-0 keeps 'c6_all_full'; Harmonia's policy
supersedes both when issued. `admitted` defaults to the three rulers the packet found
admittable until she rules. | segment.py _tier; charter s5. | -- | Revisit on Harmonia's
policy. DETERMINISTIC.

DF-005 | 2026-09-18 22:01 | LOOP RUNNER CONSTRUCTED (loop.py), gated: executes only with --live AND the
gate file archaeon/frontier/G6-0_CLOSED.json (written by the lead when the fleet-wide G6-0
receipt is on main); the self-test runs on a temporary registry outside the repo. One
iteration: choose the pool by share deficit -> pop -> build a segment spec from the
transformation (concrete builders for the procedural scatter, the complexity sweep, the
flat-elite horizon, the FIZZLE load; graph-profile and other descriptive transformations
return BLOCKED with the reason and stay on the frontier, demoted) -> run in checkpointed
chunks (outputs gzipped under frontier/runs/, never rewritten) -> registry CHUNK/FREEZE_REF/
RUN/OBSERVATION events -> branch on triggers (seed control, horizon x4 persistence, replay
view on disagreement, adjacent-bin on classifier failure, 1-in-50 audit) as new PENDING
transformations with param overrides, lane EVOLUTION_GENERATED. | loop self-test: 2 chunks,
branches deduped, lineage versions advance, gate refuses. | -- | Builders grow with the
frontier; the gate rule never changes without the operator. DETERMINISTIC.

DF-006 | 2026-09-18 22:25 | GRAPH PROFILE REGISTERED through Proteus's handover (proteus/graph/handover.py:
player_for / meter_for / organism_record_for / descend_for / generate_for / fingerprint_for;
runtime f850a6ed1e52..., profile pfp1:2595e1aefd59975f). archaeon/campaign6/substrate.py is the
substrate-neutral evaluator/rows/gen-0; segment.resolve_profile("graph") uses it; the worlds
runtime and detectors dispatch on the manifest schema; structural_reuse returns UNABLE on graph
until node execution counts are read (C6_GEOMETRY stage). test_graph_profile: gen-0 from the
graph foundry, evaluate deterministic, Proteus's graph row <= 1 KiB, composed world runs a graph
organism, cross-substrate mate refused, 12-generation segment deterministic and continuous
across a boundary. THE THREE GRAPH TRANSFORMATIONS (C4-cliff.T1, C6-blind.T1, C5-asym.T1) are
GATED on Proteus's PROTEUS-46 falsifier: the loop runs them only if archaeon/frontier/
PROTEUS-46_FALSIFIER.json carries verdict CLIFF_DOES_NOT_SURVIVE; a CLIFF_SURVIVES verdict makes
them retirement candidates under condition A before they run, as Proteus asked. Graph gen-0 comes
from the graph foundry; no lift from v0 parents exists or is offered. | Proteus #478 report;
test_graph_profile. | -- | The gate file is written by the lead from Proteus's posted verdict.
DETERMINISTIC.

DF-007 | 2026-09-18 23:36 | OPERATOR EXECUTION DIRECTIVE (verbatim: roles/Archaeon/prompts/2026-09-18_
deep_frontier/01_OPERATOR_EXECUTION_DIRECTIVE.md): Deep Frontier STARTS NOW. Gate file
archaeon/frontier/OPERATOR_EXECUTION_AUTHORIZED.json (authority OPERATOR_EXECUTION_AUTHORIZED,
is_verification false; it lists what G6-0 still has unverified and which integrity invariants
Archaeon's own tests cover). It is NOT G6_0_ALL_COMPONENTS_VERIFIED. Global stop only for a
named failing invariant among {deterministic replay, checkpoint continuity, evidence write
correctness, provenance, observation/interpretation separation, crash recovery} with a
reproducing receipt and the evidence it would invalidate; everything else is local (BLOCKED /
UNABLE / FALSIFIER_FAILED / PARTIAL) and the loop moves on. Crash recovery: CLAIMED -> PENDING
at start; chunks are on disk. | the directive. | -- | OPERATOR AUTHORITY.

DF-008 | 2026-09-18 23:36 | PROTEUS-46 CONSUMED WITH CORRECTED SEMANTICS (verdict file proteus/round2/
PROTEUS-46_FALSIFIER.json: verdict CLIFF_SURVIVES, falsifier_status FALSIFIER_FAILED,
neighbourhood_exhausted false, four reopen conditions). Only the transformation the falsifier
COVERS -- C4-cliff.T1 (the single-edit neighbourhood under graph_grammar.v1 vs v0.4) -- is
BLOCKED as formulated; no lineage is retired. RECONCILIATION of my 3-vs-8 bookkeeping: I had
gated all eight graph-touching transformations on the verdict; seven of them (C4-cliff.T3,
C4-exapt.T2, C5-flat.T2, C5-asym.T1, C6-blind.T1, C6-unable.T4, C6-unable.T5) ask different
questions (evolution, worlds, walks, blind spots) the falsifier did not measure and are
UNGATED (registry events per transformation). | Proteus #482; registry EVENTS. | -- | The
covered set changes only if Proteus extends the falsifier. DETERMINISTIC.

DF-009 | 2026-09-18 23:36 | GENERIC BUILDERS: every transformation maps its dims and target onto the
spec knobs (N, E, generations, profile v0/graph/repb_fizzle, composed world by bin, labeled/
unlabeled/stable schedule); lane MIXED for LLM-named directions realised by procedural samplers.
Resolution before launch: 76 runnable / 1 FALSIFIER_FAILED / 0 BLOCKED of 77. | build() sweep. |
-- | Builders may be refined per lineage; the mapping is recorded in each run's provenance.

DF-010 | 2026-09-19 00:03 | CODE-FIRST EXECUTION (operator directive, verbatim 02_OPERATOR_CODE_FIRST_
EXECUTION.md): experiments are validated specs (specs.py, archaeon.frontier.experiment_spec.v1:
id, world/world-generator, organism/population, params, seed, budget, controls,
required_capabilities, telemetry, output schema, checkpoint/replay, provenance); families
expand by sweep grids; capabilities are probes (capabilities.py) and a missing one yields
BLOCKED_MISSING_CAPABILITY with no prose; preregistrations are data under suppressions/
(PROTEUS-46.json covers C4-cliff.T1 only, active while the source file says
FALSIFIER_FAILED); global halts are assertions (integrity.py: replay A, checkpoint ancestry,
evidence writes incl. anchor coverage/chain, provenance, observation/interpretation
separation, append-only registry) that write GLOBAL_HALT.json with invariant + receipt +
invalidated evidence; the scheduler (scheduler.py) discovers, checks, executes, resumes from
the last chunk, writes RECEIPT.json first and per chunk, branches descendants as specs
(controls + persistence + adjacent bins) and advances the queue. Self-test: v0 and graph
specs ran, suppression blocked the covered one, resume ran only the missing chunk, replay A
SAME, 5 descendants. Migration attached 82 specs to the existing transformations and added the
breadth FAMILY (40 world seeds x {v0, graph} x N {16, 64} = 160 specs). The LLM-scheduled
loop (loop.py) is superseded and stopped; the scheduler runs detached with an 8 h wall.
| self-test; migrate output. | -- | OPERATOR AUTHORITY on the model; DETERMINISTIC in code.
