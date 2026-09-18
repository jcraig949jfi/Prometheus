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
