# Campaign 4 -- local campaign decisions (no operator, no HITL during execution)

Format: D4-### | when (UTC) | decision | evidence | alternative rejected |
revisit-if. Each decision states SCIENTIFIC DISCRETION or DETERMINISTIC
(and where the machinery went). Vocabulary in prose follows
DISPOSITION_C4-REH-1.md section 6; field names and schemas are untouched.

D4-001 | 2026-09-18 01:10 | EXECUTION PATH FOR C4-01 AND C4-02 (pure
evaluation censuses): the campaign harness path used by campaigns 1-3
(archaeon.campaign2.c2base.Experiment parametrized for campaign 4: local
evaluation with the frozen runtime, every world / experiment / observation
written to the engine under the campaign identity, PEW ingest by
Mnemosyne's reader), NOT a Vivarium queue row. | The directive header says
"Execution: Vivarium", but the executing seat's admissible work kinds
(noop_v0, evaluate_bitstring, random_walk_v0, ca_density_v0,
artifact_probe_v1, cegis_boolean_v1, eca_rule_eval_v1) contain no kind
that evaluates a program variant (a Proteus manifest) in a WSE world;
campaigns 1-3 ran exactly this way; the queue path itself was proved by
C4-REH-1 (G2 GREEN). | Alternative: wait for Vivarium to build the kind
(their lane; asked in parallel, roles/Archaeon/prompts/2026-09-17_c4_convergence/
06_VIVARIUM_WSE_KIND.md) -- rejected for C4-01/02 because the census is
minutes of evaluation and the kind's absence is a machine gap to report,
not a reason to idle. | Revisit when the kind exists: C4-05 onward move
onto the queue; if the operator rules (a) before the gate is green, C4-01
waits. PUT TO THE OPERATOR in chat 2026-09-18 01:00Z; silence = proceed.
SCIENTIFIC DISCRETION on scope, DETERMINISTIC application.

D4-002 | 2026-09-18 01:10 | THE FROZEN INTERPRETER IS TOTAL, SO D1
EXECUTION_FAULT CANNOT FIRE. proteus/foundry/vm.py run_tick reduces the
opcode word modulo the table size, every register operand modulo n_regs,
every address modulo tape_words and every jump modulo the tape; its status
vocabulary is {halt, yield, budget} with no fault. D0 UNDECODABLE is only
a post-mutation manifest validation failure (grammar.mutate raises
ManifestError). Every C4 census reports D1 with eligible count 0 and the
reason "no fatal operation exists on this substrate", never as "0
observed". Consequence for C4-03: the HARD condition ("current fatal
behaviour") does not exist to compare against; the substrate is already
FIZZLE-everywhere. C4-03 is therefore expected to close
REPRESENTATION_BLOCKED for its HARD arm unless a HARD interpreter mode can
be expressed without a new ISA primitive (it cannot: a fault is a new
termination status). Recorded now so the census is read correctly. |
vm.py lines 149-300; affordances.py TABLE (25 opcodes, NOP 0). |
Alternative: add a fault mode for the census -- forbidden by the
directive (no ISA change during the campaign) and would measure a
different substrate than the one the campaign is about. | Revisit never
within campaign 4. DETERMINISTIC (a property of the frozen code).

D4-003 | 2026-09-18 01:10 | C4-01 CLASSIFICATION CONSTANTS, fixed before
any row: viability floor = reward_per_ask >= 3/16 on the parent
environment (E=16, K=1: three correct asks of sixteen; P(>= 3 | chance
1/16) about 0.08); equivalence band = 1/16 (one ask at E=16); behavioral
displacement = normalized Hamming distance between parent and child
answer vectors over the same 16 episodes' ask positions (unanswered =
its own symbol); DEGENERATE = answered_share 0 OR one constant answer on
every ask; precedence D0 > D2 > D7 > D6 > D5 > D4 > D3; D6 needs the
child to beat the parent by >= band AND clear the floor on at least one
OTHER preregistered environment while not D7 on its own. | The
directive's taxonomy plus the evaluator's resolution (1/16 at E=16, one
ask per episode on the K=1 cells). | Alternative: floor at chance
(1/16): one lucky ask would make a variant "viable". | Revisit if C4-01
shows a reward mass between 2/16 and 4/16 that the floor splits
arbitrarily; then report both readings side by side, never move the
floor. SCIENTIFIC thresholds, DETERMINISTIC application.

D4-004 | 2026-09-18 01:10 | PARENT ENVIRONMENTS BY STRATUM: gen0_random
and w0_solver -> W0 (K=1, 4-bit); shelf -> W2_K2 (K=2, 4-bit; the cell
C3-SFE-01 selected them in); delay_general -> W1_d4 (the top rung of the
ladder they generalized on). OTHER environments (for D6, identical set
for every parent): W0 held-out vocabulary, W1_d1, W1_d4, W2_K2, minus the
parent's own. | STARTING_POPULATION.json ancestries (experiment and arm
per organism); worlds.WorldSpec. | Alternative: one environment for all
(would call every delay-general organism "worse" on W0 by construction).
| Revisit never within C4-01. DETERMINISTIC (ancestry -> world map).

D4-005 | 2026-09-18 05:57 | C4-01 attempt a01 FAILED at the final publish step
(engine HTTP 422: artifact meta info_kind "measurement" is not one of the
engine's five: artifact/failure/hypothesis/observation/success) AFTER the
census and all 798 records had landed; the runner was repaired (info_kind
"artifact") and the slot rerun as a02, which RESUMED a01 (803 steps replayed
by the harness's attempt machinery; same world, same records; 0 errors) and
is the attempt of record. a01 is preserved beside it. Flow tables of a01 and
a02 are byte-identical (wall_s excluded). | Directive: harness defects are
repaired and the same experiment rerun with the failed attempt preserved;
this was a harness defect (a wrong string), not a scientific failure. |
Alternative: hand-edit a01's receipt -- never. | Revisit never.
DETERMINISTIC (the census is a pure function of its seeds).

D4-006 | 2026-09-18 06:05 | C4-02 RADIUS = the number of grammar.mutate()
applications from one rng seeded by (campaign_seed, organism_id, radius,
draw), operators drawn by the FROZEN WEIGHTS (name=None), INCLUDING steps
whose operator returns its noop record (noop_steps recorded per child):
the radius is what the grammar was asked to do, not what changed. The
prediction written to be lost: loss_rate(r8) - loss_rate(r1) >= 0.05
(measured: .930 - .522 = .408, not lost). Consistency control: the
radius-1 D-distribution within TVD 0.10 of C4-01's frozen-weight mixture
of per-operator distributions (measured .029). | C4-02/DESIGN.md. |
Alternative: count only effective steps (would make the radius depend on
the parent's length and hide the noop mass). | Revisit never in C4.
DETERMINISTIC.
