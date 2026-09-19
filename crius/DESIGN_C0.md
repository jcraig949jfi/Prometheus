# Crius Campaign 0 -- design challenge and frozen design

Currency: 2026-09-19 (written before any sandbox code; committed first so
the preregistration order is in git history). Charter:
roles/Crius/prompts/2026-09-19_charter/CHARTER_CAMPAIGN_0.md
(sha256 5c58c97d...; MANIFEST beside it).

Central question (unchanged): can search discover computational machinery
that makes future learning cheaper because useful structure acquired from
previous experience can be retained, organized, reused, modified and
recombined?

## 1. Challenges to the charter's design, and what was decided

C1. THE FITNESS LANDSCAPE FOR RAW-BYTECODE SEARCH IS DECEPTIVE. Reuse
    machinery is a multi-instruction structure (observe, store, look up,
    compare, branch, replay); a partial version scores nothing, so
    mutation-and-selection from random programs will almost certainly
    find a brute-force solver (if anything) and stop. This program has
    measured that failure shape before (Apollo: plateau was a
    search-operator failure). DECISION: do not change the search (the
    charter says it is scaffolding), but run TWO arms so the failure
    shape is informative: ARM-R starts from random programs; ARM-S starts
    from a hand-written bytecode ENUMERATOR that uses no workspace and no
    artifacts. ARM-S asks the sharper question "given a competent solver,
    can selection under the efficiency metric ADD reuse to it?". The
    seed's competence is in its code, so the FRESH/CODE_ONLY controls and
    reuse_gain = fresh - accumulated read zero for it by construction;
    any positive reuse_gain in its descendants is acquired-state effect.
    The seed contains no cache, lookup or replay mechanism (charter s12:
    the hand-written strategies' mechanisms stay out of the searched
    set). This is declared here, before search.

C2. THE HIDDEN OPERATIONS MUST BE LEARNABLE BY A GENERIC MECHANISM or no
    positive control can be written without domain theory, and the
    sandbox cannot demonstrate the phenomenon it claims to test (s17).
    DECISION: the world's operations are translations on a small integer
    vector, some of them CONDITIONAL on a visible property of the object
    (a context bit), plus one structural (permutation) operation. A
    table of observed (operation -> delta) entries, keyed by nothing or
    by the context bit, is a complete model of the translation
    operations and can be built by any mechanism that can subtract two
    vectors and store the result. The permutation operation is NOT a
    translation; it is the composition family absent from search
    (s11 "at least one composition family absent during search") and it
    is what distinguishes "stored a datum" from "stored a procedure".

C3. INTERACTIONS ARE THE EXPENSIVE RESOURCE; COMPUTE WEIGHT MUST BE
    DECLARED. Planning in the head (invoking stored models) costs VM
    steps; probing the world costs interactions. If the metric weighs
    them equally, mental planning over 258 candidate sequences costs as
    much as physically enumerating them and the pressure for reuse
    vanishes. DECISION (frozen): 1 interaction = 100 VM steps in every
    cost, declared in the config and in the receipts. COMPUTE_MATCHED
    controls exist precisely because this weight is a choice.

C4. reuse_gain IS MEASURABLE EXACTLY, NOT ESTIMATED. Execution is
    deterministic in (player_spec, task_spec, seed), so
    cost_if_solved_fresh is the same Player run on the same task with an
    empty workspace. DECISION: qualification runs FRESH per task and
    reports reuse_gain_t = cost_fresh_t - cost_accumulated_t as a
    measurement, per task, never as an estimate.

C5. "ARTIFACT" AND "DATA" ARE NOT CLEANLY SEPARABLE FOR A VM PLAYER: a
    stored delta plus a generic apply loop in the program computes the
    same function as an executable block holding that delta. DECISION:
    keep both stores (cells/streams/records/links for data; blocks for
    executable artifacts), keep the controls separate (RESET/SCRAMBLE
    act on data and blocks independently; ABLATION and TRANSPLANT act on
    blocks by id), and let the controls make the operational distinction.
    No claim of the form "competence is in the artifacts" is made unless
    ablating blocks with data intact damages later tasks.

C6. RESET IS NOT AN INTERACTION. Returning the object to the task's
    start state gives no information about the hidden operations.
    DECISION: RESET costs one VM step and zero interactions; otherwise
    brute-force cost is dominated by bookkeeping and the interaction
    count stops measuring experience.

C7. ONE ASSOCIATIVE PRIMITIVE IS INCLUDED AND FLAGGED. workspace.find
    (return the first address whose value equals v, charging one cost
    unit per cell scanned) is a content-addressed read. It is a memory
    primitive, not a theory of learning (the charter's create_record /
    get_field is the same capability with an explicit key), and without
    it a lookup is a loop the search must also discover. It is named
    WS_FIND and any result that depends on it will say so.

C8. THE WORLD IS KEPT SMALL. 6 operations, vectors of length 4 modulo
    16, depth <= 3 during search, depth 4 only in qualification. The
    subject is the assay and what search constructs, not the world.
    Nothing here is tuned after seeing a search result: the config hash
    of configs/c0.json is frozen in this commit's successor (the
    freeze commit) and every receipt carries it.

C9. WHAT IS NOT BUILT: no integration with any Prometheus service, no
    comms calls from the sandbox, no LLM in the loop, no JIT, no
    permission layer, no YAML dependency (this host has no PyYAML;
    configs are JSON with the same content).

## 2. The world (crius/world.py, crius/tasks.py)

Objects: tuples of L=4 integers in Z_16.
Hidden operations (fixed for the campaign; labels 0..5 are what a
Player sees; the mapping is never exposed):

    op0  x + (1,0,0,0)                         unconditional translation
    op1  x + (0,3,0,0)                         unconditional translation
    op2  x + (0,0,5,0)                         unconditional translation
    op3  x + (2,0,0,7)  if x[0] even           conditional translation
         x + (0,0,0,1)  if x[0] odd
    op4  x + (0,4,0,0)  if x[0] even           conditional translation
         x + (0,0,0,4)  if x[0] odd
    op5  (x1,x2,x3,x0)                         rotation (structural)

"Component P may substitute for Q only under context R": op3 and op4
change meaning with the parity of coordinate 0, and op0 flips that
parity, so the same label does different things depending on what was
applied before it. Non-commutativity enters through op0 and op5.

Task = (start, target, interaction_budget, step_budget) with target =
composition(start) for a composition drawn from the stage's set;
resampled if target == start. Success = current object equals target.
Actions: APPLY(op) costs one interaction; RESET costs none (C6).
Performance of an object = 1 - hamming(object, target)/L.
Budgets (interactions): depth 1: 18, depth 2: 120, depth 3: 800,
depth 4: 1500 (qualification only). Step budget per task: 20000.
Brute-force iterative deepening cost: depth 1 <= 6, depth 2 <= 114,
depth 3 <= 762 applies, depth 4 <= 5946 (unreachable under budget by
enumeration: only planning machinery can solve depth 4).

Lifetime = 50 tasks (configurable): A 10 depth-1 (every op appears),
B 10 depth-1 new starts, C 12 depth-2 from the SEARCH pair set, D 10
depth-3 from the SEARCH triple set, E 8 held-out (see partitions). Order
within a stage varies by seed; stages are not revealed.

Partitions (frozen in configs/c0.json under "partitions"):
- SEARCH pairs: ordered pairs over ops {0,1,2,3,4} with a fixed 60%
  subset; SEARCH triples: 40% subset of triples over {0,1,2,3,4}.
- QUALIFICATION: (a) unseen instances of A/B (new seeds); (b) the
  REVERSED orderings of search pairs not already in the search set;
  (c) held-out pairs and triples over {0..4}; (d) new combinations:
  triples formed by concatenating two search pairs' ops not in the
  search triple set; (e) the ABSENT family: every composition
  containing op5 (rotation), never present in search stages C/D/E, and
  depth-4 compositions.
- Stage E during SEARCH lifetimes draws from held-out pairs/triples over
  {0..4} only (transfer within known operations); op5 compositions and
  depth 4 appear ONLY in qualification suite heldout_v1.

## 3. The Player VM (crius/vm.py)

Registers R0..R7 hold values: an int or a tuple of ints (vector).
Arithmetic is elementwise on vectors, broadcast for ints, reduced mod
16 by MOD only when the program asks. Program: at most 64 instructions
(opcode, a, b, c). One instruction = one VM step. Halting: program end,
HALT, step budget, interaction budget, or success.

Instruction classes (mechanically neutral names only):
  CONST MOV ADD SUB MUL DIV MOD EQ LT NOT                arithmetic
  VGET VSET VLEN                                          vector access
  BRZ BRNZ JMP HALT                                       control
  INPUT (field: current, target, budget_left, num_ops, task_index,
         steps_left, last_delta)                          observation
  ACT (value in [0,num_ops) applies; == num_ops resets)   action
  WS_READ WS_WRITE WS_APPEND WS_SREAD WS_SLEN WS_REC_NEW WS_REC_GET
  WS_REC_SET WS_LINK WS_LINKS WS_LINK_GET WS_ALLOC WS_FREE WS_FIND
  BLK_NEW BLK_APPEND BLK_PATCH BLK_COPY BLK_COMPOSE BLK_DELETE
  BLK_INVOKE BLK_LEN BLK_COUNT BLK_STATE_GET BLK_STATE_SET
  BLK_REC_BEGIN BLK_REC_END (record the ACT instructions emitted
  between the two into a new block)
Bounds: 64 instructions, 20000 steps per task, 256 workspace cells +
streams/records/links counted in the same byte capacity (4096 value
bytes), 32 blocks, 64 instructions per block, call depth 4.
Blocks run in the caller's register file (a macro call) with their own
local_state slots; a block's ACT instructions act on the world.

## 4. The frozen Campaign-0 metric (crius/evaluate.py)

Per task t (all recorded in TaskResult):
  starting_performance  perf(start)
  final_performance     perf(best object reached)
  gain_t                max(0, final - starting)
  interactions_used, vm_steps_used, ws_cost_units, workspace_bytes,
  artifact_bytes, artifacts_invoked, blocks_created, success
  adaptation_cost_t     interactions_used + 0.01 * (vm_steps_used +
                        ws_cost_units)            [C3: 100 steps = 1]
Per lifetime:
  competence_gained     sum_t gain_t
  experience            sum_t interactions_used_t / budget_t
  compute               sum_t (vm_steps_t + ws_cost_t) / step_budget
  retained_state        mean_t (workspace_bytes_t + artifact_bytes_t)
                        / capacity_bytes
  C0_EFFICIENCY         competence_gained /
                        (1 + experience + compute + retained_state)
  adaptation_curve      [adaptation_cost_t] in presentation order
  late_early_ratio_d    for each depth d: mean cost of the last half of
                        depth-d tasks / mean cost of the first half
  reuse_gain_t          cost_fresh_t - cost_accumulated_t
                        (qualification only; C4)
C0_EFFICIENCY drives search. Nothing else drives search. Every
component is in the receipt.

## 5. Controls (crius/evaluate.py conditions; s10 letters kept)

  A FRESH       each task from an empty workspace and empty block store
  B ACCUMULATED normal lifetime
  C WORKSPACE_RESET       clear data + blocks at the first task of
                          stages C, D and E (indices in config)
  D WORKSPACE_SCRAMBLED   at the same points: permute cell values across
                          written addresses, shuffle each stream,
                          permute record field values across records,
                          re-point links to random existing targets;
                          shuffle each block's instruction order and
                          permute block ids; sizes preserved
  E ARTIFACT_ABLATION     snapshot at the start of stage D; for each
                          block present, delete it alone and run the
                          remainder; report per-block cost delta
  F ARTIFACT_TRANSPLANT   copy the snapshot's blocks (only) into a fresh
                          copy and run the remainder
  G FULL_WORKSPACE_TRANSPLANT  copy data + blocks into a fresh copy
  H CODE_ONLY             run the remainder from empty state
  I COMPUTE_MATCHED       H with step budget raised to what B used on
                          the remainder, times 2
  J STORAGE_MATCHED       H with capacity doubled
Each control's receipt carries the condition name, the snapshot task
index, and the same per-task fields as B.

## 6. Baselines (crius/baselines.py; controls, never in the search set)

  RANDOM        uniform action each step
  HEURISTIC     greedy: try each op from the current object, keep the
                one that reduces hamming distance, reset otherwise
  ENUMERATE     iterative deepening over op sequences using RESET
                (the high-compute brute-force solver; also the ARM-S
                seed, written in bytecode)
  CACHE_REUSE   ENUMERATE that stores every observed (op, context ->
                delta) in workspace records and plans in the head with
                the stored deltas before probing; falls back to
                ENUMERATE for anything the table cannot explain
  ADAPTIVE      CACHE_REUSE that additionally records each solved op
                sequence as an executable block keyed by the delta it
                produced, tries stored blocks first, and tries
                compositions of two stored blocks before planning
Baselines are Python Players against the same Workspace/BlockStore API
so every control applies to them unchanged. Their compute is charged as
1 unit per decision plus workspace/block costs; this is comparable to
the VM only approximately, which is why they are controls and not
competitors.

## 7. Search (crius/search.py)

(mu + lambda) mutation-and-selection, mu=8 lambda=24 per iteration,
truncation selection on C0_EFFICIENCY averaged over 2 search seeds.
Mutations: replace instruction, change one argument, change a constant,
insert, delete, swap two, duplicate a segment. Each candidate's
CandidateReceipt records candidate_id (sha256 of the program),
parent_id, modification, iteration, fitness components. Search
lifetimes use SEARCH seeds only (config "seeds.search").

## 8. Receipts and replay (crius/receipts.py)

RunReceipt as in the charter s14, JSON, one file per lifetime under
crius/runs/<run_id>/; replay_hash = sha256 over the sequence of
(task_index, action, resulting object) tuples; a replay must reproduce
it byte for byte or the receipt is void.

## 9. Predictions written before running (falsifiable, can be lost)

P1 ENUMERATE solves every depth<=3 task and no depth-4 task; its
   late/early ratio is ~1 at every depth (no adaptation).
P2 CACHE_REUSE and ADAPTIVE show late/early ratio < 0.5 at depths 2 and
   3, and positive reuse_gain on stages C-E; WORKSPACE_RESET restores
   their cost to ENUMERATE's on the task after the reset.
P3 ADAPTIVE solves some depth-4 qualification tasks; ENUMERATE none.
P4 ARM-R (random init) does not produce a Player with late/early ratio
   < 0.8 at depth 3 within the modest budget; if it produces a solver
   at all it is a partial enumerator.
P5 ARM-S produces descendants whose C0_EFFICIENCY exceeds the seed's,
   but the improvement comes from budget-management (halting earlier
   on hopeless tasks) rather than acquired state: reuse_gain stays
   ~0 and WORKSPACE_RESET does not hurt them.
P5 is the prediction this campaign would most like to lose.

## 10. Addendum 2026-09-19: deviations from the frozen design, dated

A1 (before freeze, during implementation) POST-SUCCESS GRACE. A task
   ended the instant the object matched the target, so a Player could
   never execute BLK_REC_END after its final action. TaskRun now allows
   post_success_steps=200 compute units after success; any further
   action ends the task. Recorded in configs/c0.json before the freeze
   commit 68cc85ff9.
A2 (after freeze, before any campaign search) STORE-OP BUDGET CHARGING.
   Random programs escaped the step bound by looping over WS_FIND
   (256-cell scans per instruction): the 3-iteration random-arm smoke
   search did not finish in 600 s. Workspace and block cost units are
   now charged against the step budget in the VM (TaskRun.charge_store),
   counted separately from vm_steps so compute = vm_steps + ws_cost is
   not double counted. Python baselines are not budget-charged for store
   units (their compute was declared approximate in section 6). Commit
   f4dae7a66. The metric definition did not change; the reachable
   programs did (a WS_FIND loop now halts within budget).
A3 (after freeze; EXPLORATORY) c0x.json. The 3-iteration seeded smoke
   search produced, as its best, a crippled enumerator that solves only
   depth-1 tasks and halts on everything else (search fitness 2.50
   against the seed's 1.62; 20/50 successes; reuse_gain 0). Under the
   frozen ratio metric, abstaining from expensive tasks beats solving
   them, and on the held-out suite the same quitter (eff 3.00) outranks
   CACHE_REUSE (2.97). That is a finding about the metric, reported as
   the Campaign 0 result. c0x.json is a post-hoc variant that charges an
   unsolved task its full interaction budget as experience. It is NOT
   preregistered; its receipts carry campaign "c0x" and its numbers are
   labelled EXPLORATORY wherever they appear. P4 and P5 are scored on
   the c0 runs only.
A4 ADAPTIVE macro planning (before freeze). The first ADAPTIVE only
   replayed blocks whose key matched exactly (3 invocations per
   lifetime). It now also plans over stored blocks as macro-operators.
   Its blocks remain a net cost at depth <= 3 (ablating all of them
   LOWERS the remainder cost 10.0 -> 7.8 on search seed 101). This is
   recorded as the missing degree of freedom, not repaired: in this
   world, once the operation effects are known as data, nothing
   procedural is left to reuse.
