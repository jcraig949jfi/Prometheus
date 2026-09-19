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

DF-011 | 2026-09-19 00:40 | TWO DEFECTS FOUND BY THE FIRST LIVE HOUR, FIXED LOCALLY, SCHEDULER RESTARTED (its
resume ran only the missing chunks): (1) a graph organism's fingerprint row exceeded Proteus's
1 KiB cap by 13 bytes (two 64-hex ids on a large row) and the whole experiment errored -> the
row is kept with 32-hex ids and ext.id_truncated = true; the full ids are in the segment
records; (2) the tiered freeze policy granted FULL on any non-10/11 firing, so the unvalidated
structural_reuse ruler (base rate ~.4 on composed worlds) drove 5,853 FULL freezes in one 16,000-
evaluation run; charter s5 says FULL needs an ADMITTED ruler -> FULL now requires an admitted
firing (or corroboration among admitted rulers, admitted persistence >= 3, or the 1-in-50 audit
draw); everything else is PARTIAL with the EVENT_RECORD always kept. The digest now reads the
scheduler's receipts through the registry run refs. Neither defect touched replay, ancestry,
provenance or separation; no global halt was warranted. | scheduler_2026-09-19_a.log; digest
0038Z. | -- | Threshold table untouched. DETERMINISTIC.

DF-012 | 2026-09-19 02:02 | DIGEST 0159Z (19 runs, 415,776 evaluations) READ; three scheduler-policy defects
fixed in code and the scheduler restarted with resume: (1) controls spawned controls -- a seed
control of a seed control eleven deep consumed 11 of 19 runs; descendants now come only from
depth-0 runs, controls go to AUDIT, persistence (x4 horizon) only when an ADMITTED ruler fired
goes to EXPLOITATION, adjacent bins to EXPLORATION, descendant priority below the parent's;
pending depth->=2 chain items DROPPED with the reason; (2) classifier_failure fired on 100% of
firing subjects because five rulers are STRUCTURALLY unable on every current run (no probe
worlds, no replay D, no ablation set, no regime change, no persistent state) -- CALIBRATION_
EPOCH-001 (registry event): structural UNABLEs no longer count toward the >= 3 rule; no
threshold moved; (3) the old-loop parent B-scatter.T000 and its scheduler descendants ran on
DIFFERENT worlds (bin 3 vs bin 7 from the same seed record) -- not comparable; the spec is
re-run as an AUDIT control instead of explained. FIRST OBSERVATIONS RECORDED with PROVISIONAL
interpretations: C5-flat.T1 (N=200, W3_K3) max .500 > best starting parent .382 in three
seeds -- confounded by total compute vs C5 (60,000 vs 9,000-36,000) -> equal-compute N family
(50/100/200/400 x 3 seeds at 60,000 evaluations) queued to EXPLOITATION at top priority;
graph populations fire two orders of magnitude less than v0 at v0-calibrated thresholds
(undetermined: churn vs spread); the bin-5 composed world of C4-exapt.T1 is dead for this
population (reward 0 for 40,000 evaluations). | digests/DIGEST_2026-09-19T0159Z.md; registry
OBSERVATION/INTERPRETATION events. | -- | DETERMINISTIC (policy), PROVISIONAL (readings).

DF-013 | 2026-09-19 02:19 | SCIENTIFIC AUTHORITY RETURNED TO ARCHAEON (operator, verbatim 03_OPERATOR_SCIENTIFIC_
AUTHORITY.md). Kept: specs, capabilities, integrity halts, receipts, resume, allocation floors,
the scheduler as executor. Removed from the scheduler: every scientific choice -- its branching
is now the two evidence controls only, and only after an admitted ruler fired. Added, authored
by Archaeon as code the scheduler runs: archaeon/frontier/design/ modules (emit() queues
validated specs), nominate.py (spec / design / pursue), pursue.json (priority multipliers by
lineage/family), forensic nominations (top-k FULL freezes at named generations), and two
measurement/world mutations recorded in the spec hash: world_options.eval_order
(population | seeded_shuffle) and world_options.persist_shared (shared world state carried
across generations in the checkpoint). FIRST DESIGNS: P-boom (the boom-bust maximum on the
coupled world the receipts show: A baseline x3 seeds with nominated freezes at the spike
generations, B seeded-shuffle x3, C coupling off, D persist_shared, E N=8/128 -- evaluation
order vs population effect, nothing assumed), W-artifacts (12 procedural coupled worlds x
persist on/off: niche construction across generations), CALIBRATION_EPOCH-002 (two population-
level rulers, population_shift and max_spike, unvalidated, computed into receipts; no
threshold moved). Pursuit multipliers: P-boom x4, C5-flat x2. | receipts scan 02:0xZ; tests. |
-- | OPERATOR AUTHORITY on the model; SCIENTIFIC DISCRETION on the designs.

## DF-014 (2026-09-19T02:58Z) Operator protections before the P-boom precedent

Operator (verbatim points, 2026-09-19): unvalidated rulers non-authoritative; archive enough state to reconstruct the
spike; spike rate is the preregistered primary statistic, not the whole observation space; do not template this
pursuit; every multiplier change carries provenance; "I will return with that answer" is not part of the contract.

Implemented as state and code:
1. AUTHORITY. design/measurement.py declares AUTHORITY = "NONE"; every receipt chunk's measurements carry
   `"authority": "NONE"`; the scheduler never reads measurements (branching = evidence controls only; priority = queue
   + pursue table). RULER_AUTHORITY event on LIN-f14ab25f names what the rulers may (nominate through design modules)
   and may not (branch, prioritise, set freeze tier, select) do until Harmonia admits them against synthetic nulls,
   forced positives, order artefacts and population-size effects. Admission request goes to Harmonia with the readout.
2. FORENSIC CAPTURE. segment.py `nominate.population` + `window` -> `population_captures` (ordering, evaluation order,
   parentage, shared state before/after every evaluation, endogenous writes, +-window). Tested deterministic (16 rows
   per generation, generations 4/5/6 captured for a gen-5 nomination with window 1). Arm F_popcapture_s1 queued in
   P-boom (window 2, top_k 32 at the four spike generations).
3. PRIMARY STATISTIC + DENSE TELEMETRY. boom_readout.py computes only the preregistered spike rate; the captures and
   the dense archive are preserved beside it, unreduced. The readout writes no interpretation.
4. NO TEMPLATE. The next anomaly gets its own design module; nothing in design/ is imported by another family. The
   lesson recorded is the loop (anomaly -> executable pursuit module -> controlled descendants -> forensic
   preservation), not the arms.
5. PROVENANCE ON MULTIPLIERS. pursue.json entries are records {multiplier, cause, author, at, expires_evaluations,
   spent_evaluations, reconsider, state}. nominate pursue requires --cause; the scheduler applies a multiplier only
   while LIVE and unspent, charges every finished run's evaluations to the entries that steered it, and flips them to
   EXPIRED in the file (history keeps the expiry). A bare number is treated as expired. The two existing multipliers
   (P-boom x4, C5-flat x2) were rewritten with their causes and expiries.
6. DURABLE READOUTS. design/readouts.json registers a readout as a queued object {module, lineage, condition
   {family, done_min}, state}; the scheduler runs it when the condition holds and writes an OBSERVATION with the result
   file into the lineage. Whoever reads the registry later finds the readout, or its pending condition, in state.
   P-boom.readout.1 registered (8 DONE receipts -> boom_readout).
Boundary as stated by the operator and adopted: Scientist designs/nominates/interprets; Scheduler executes and
branches only on evidence controls; Receipts hold all the numbers; Harmonia admits instruments and rulers.
Scheduler restarted on the new code at 2026-09-19T02:57Z (session e); the in-flight P-boom run resumes from its receipt.
