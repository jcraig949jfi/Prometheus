Your charter and responsibility is to put players into a world and see if we can create a fitness function where they are rewarded for learning to learn.

CRIUS — CAMPAIGN 0: ADAPTIVE WORKSPACE SANDBOX

MISSION

Build a self-contained Python sandbox testing this question:

Can search discover programs that become progressively more efficient at solving new problems because they construct, organize, reuse, modify, and recombine useful computational state during a run?

The target is not maximum task score.

The target is increasing efficiency at converting new experience into reusable competence.

This is an isolated sandbox.

Do not integrate with SFE, NPE, Archaeon, Vivarium, Ludus, or other Prometheus infrastructure yet.

Do not build agent-level authorization, gating, orchestration, or permission systems.

Design the experiment as runnable Python code.

LLMs may help design or interpret experiments, but execution must not require another LLM decision.

==================================================

1. BASIC MODEL
    ==================================================

Use these computational terms consistently:

Player
An executable candidate program.

Workspace
Mutable state available to a Player during one lifetime/run.

Artifact
A persistent data structure or executable component constructed by a Player.

Task
A problem instance presented to a Player.

TaskFamily
A generator producing related but non-identical tasks.

Lifetime
A sequence of tasks presented to one Player instance while its Workspace persists.

SearchIteration
An outer search step that produces modified Player specifications.

Do not use biological terminology in code, schemas, filenames, or runtime messages.

==================================================
2. CENTRAL EXPERIMENT

A Player starts with:

player = Player(
    program=...,
    workspace=Workspace.empty(),
)

During one lifetime it encounters a sequence:

tasks = [
    task_0,
    task_1,
    task_2,
    ...
    task_n,
]

Tasks should share latent computational structure while differing in surface details.

The Player may solve early tasks inefficiently.

The desired phenomenon is:

task 1: expensive discovery
task 2: some reuse
task 3: faster adaptation
task 4: recombination of previous machinery
task 5: unfamiliar composition solved using accumulated machinery

The question is whether search can discover Players for which later learning becomes cheaper because earlier experience has produced reusable internal machinery.

==================================================
3. WORLD / TASK DESIGN

Do NOT begin with a simple resource-choice or contextual-bandit problem.

Build a fixed computational workshop containing compositional tasks.

The underlying mechanics stay constant throughout Campaign 0.

Individual Task instances vary.

Construct tasks from a hidden grammar containing reusable primitives and compositions.

Possible abstract structure:

TaskSpec(
    inputs=...,
    available_operations=...,
    hidden_transforms=...,
    intermediate_objects=...,
    target_condition=...,
    interaction_budget=...,
)

Examples of relationships the grammar may generate:

A transformed by X produces B
B combined with C produces D
operation Y reverses one property but preserves another
component P may substitute for Q only under context R
two previously encountered mechanisms appear together in a new task
an intermediate result from one problem becomes useful in another

Do not expose the hidden grammar directly to Players.

A Player must infer useful regularities through interaction.

Prefer tasks where brute-force solving is possible but increasingly expensive compared with effective reuse.

==================================================
4. WORKSPACE

Give Players a fixed, general-purpose computational workspace.

The workspace should be rich enough to permit organization and reuse but should NOT encode a theory of learning.

Do not provide operations named:

LEARN
PLAN
MODEL
REMEMBER_FACT
HYPOTHESIS
KNOWLEDGE
REASON

Provide mechanically neutral primitives.

Suggested starting API:

workspace.read(address)
workspace.write(address, value)
workspace.append(stream_id, value)
workspace.read_stream(stream_id, start, count)
workspace.create_record(fields)
workspace.get_field(record_id, field)
workspace.set_field(record_id, field, value)
workspace.create_link(source, label, target)
workspace.links_from(source)
workspace.allocate(size)
workspace.free(handle)

All workspace operations have measurable costs.

Workspace capacity is bounded.

==================================================
5. EXECUTABLE ARTIFACTS

Memory alone is insufficient.

Players must also be able to construct reusable executable machinery.

Provide a small generic executable-block representation.

For example:

artifact = ExecutableBlock(
    instructions=[...],
    constants=[...],
    local_state=[...],
    input_ports=...,
    output_ports=...,
)

Players may perform operations such as:

create_block(...)
invoke_block(block_id, inputs)
copy_block(block_id)
modify_block(block_id, patch)
connect_blocks(a, b)
compose_blocks([a, b, c])
delete_block(block_id)

Artifacts may persist across tasks within a lifetime.

Do not assign semantic types such as:

classifier
planner
memory
detector
world_model

The system should only know that artifacts are executable blocks with state and interfaces.

If search discovers recognizable computational roles, that should be an observation after the fact.

==================================================
6. PLAYER SUBSTRATE

Begin with a small programmable representation.

A simple bytecode VM is acceptable.

Possible instruction classes:

LOAD
STORE
CONST
ADD
SUB
MUL
DIV
MOD
COMPARE
BRANCH
JUMP
CALL
RETURN
READ_INPUT
EMIT_ACTION
WORKSPACE_OP
ARTIFACT_OP

Bound:

* program length;
* execution steps;
* memory;
* artifact count;
* artifact size;
* recursion/call depth.

Execution must be deterministic given:

(player_spec, task_spec, seed)

Do not build a sophisticated JIT or native runtime for Campaign 0.

Correctness and experimental clarity matter more than throughput.

==================================================
7. SEARCH

Use a transparent outer search algorithm first.

A mutation-and-selection strategy is sufficient.

Search may modify:

instructions
constants
control flow
workspace operation usage
artifact construction
artifact invocation
program length within limits

Do not spend Campaign 0 optimizing the search algorithm.

The search algorithm is scaffolding.

The subject of the experiment is what Player machinery appears.

Preserve complete ancestry:

CandidateReceipt(
    candidate_id=...,
    parent_id=...,
    modification=...,
)

==================================================
8. LIFETIME STRUCTURE

Each evaluation should contain enough tasks for accumulated machinery to matter.

Start with approximately:

tasks_per_lifetime = 50

but make this configurable.

Use stages such as:

Stage A
simple primitive tasks
Stage B
unseen instances using familiar primitives
Stage C
new combinations of familiar primitives
Stage D
one or more previously unseen compositions
Stage E
held-out transfer tasks

Do not reveal stage labels to the Player.

Task order should vary by seed.

==================================================
9. PRIMARY MEASUREMENT

Do not optimize final task score alone.

Measure how the cost of acquiring competence changes during a lifetime.

For every task record:

TaskResult(
    starting_performance=...,
    final_performance=...,
    interactions_used=...,
    vm_steps_used=...,
    workspace_bytes=...,
    artifact_bytes=...,
    artifacts_invoked=...,
    success=...,
)

Define a frozen Campaign-0 metric based on:

competence gained
divided by
experience + compute + retained state

Also measure improvement in adaptation cost as lifetime experience accumulates.

A conceptual quantity is:

reuse_gain =
    estimated_cost_if_solved_fresh
    - observed_cost_with_accumulated_workspace

Do not hide individual measurements inside a single scalar.

The composite metric may drive search, but receipts must retain all components.

==================================================
10. CRITICAL CONTROLS

The assay must distinguish reusable learning machinery from easier explanations.

Implement at least these comparisons.

A. FRESH

run(player, tasks, workspace=empty)

B. ACCUMULATED

Normal lifetime with persistent workspace.

C. WORKSPACE_RESET

Same Player code, but clear accumulated Workspace before selected later tasks.

D. WORKSPACE_SCRAMBLED

Preserve size and rough structure but scramble addresses/contents/relationships where meaningful.

E. ARTIFACT_ABLATION

Remove individual accumulated artifacts and measure the effect.

F. ARTIFACT_TRANSPLANT

Transfer selected artifacts into a fresh instance of the same Player program.

G. FULL_WORKSPACE_TRANSPLANT

Transfer accumulated workspace into a fresh copy.

H. CODE_ONLY

Same inherited Player code without acquired workspace.

I. COMPUTE_MATCHED

Give controls equivalent extra execution budget where necessary so increased compute is not mistaken for better learning.

J. STORAGE_MATCHED

Give controls equivalent storage capacity where necessary.

These tests should let us ask:

Is useful competence in the program?
In accumulated data?
In executable artifacts?
In relationships between artifacts?
Or simply in extra compute/storage?

==================================================
11. HELD-OUT GENERALIZATION

Separate SEARCH tasks from QUALIFICATION tasks before the long run.

Qualification must include:

unseen instances of known primitives
unseen orderings
held-out compositions
new combinations of known components
at least one composition family absent during search

Freeze these partitions before evaluating searched candidates.

A fresh qualification instance receives:

same_player_code = True
initial_workspace = empty

unless explicitly running a transplant control.

==================================================
12. BASELINES

Include several reference Players:

RANDOM
simple fixed heuristic
high-compute brute-force solver
hand-written cache/reuse strategy
simple explicit adaptive strategy

The hand-written strategies are controls only.

Do not put their specialized mechanisms into the searched Player instruction set.

The assay should establish that reuse helps without telling search how to implement reuse.

==================================================
13. WHAT COUNTS AS INTERESTING

Do not require a searched Player to beat every hand-written baseline.

Campaign 0 becomes interesting if search produces a lineage where:

1. adaptation cost declines across a lifetime;
2. the improvement reproduces on held-out task compositions;
3. accumulated workspace or artifacts causally contribute;
4. destroying or scrambling acquired machinery damages later adaptation;
5. useful accumulated machinery transfers between fresh copies;
6. later solutions reuse components assembled for earlier tasks;
7. the effect cannot be explained solely by more compute, more memory, or high initial competence.

Especially flag cases where:

a component constructed for task X
is reused unexpectedly for task Y

or:

two independently constructed components
are later recombined into a useful mechanism

Those are high-value observations.

==================================================
14. RECEIPTS FIRST

Write structured results before narrative analysis.

Suggested structure:

RunReceipt(
    run_id=...,
    candidate_hash=...,
    parent_hash=...,
    code_commit=...,
    config_hash=...,
    seed=...,
    search_or_qualification=...,
    task_sequence_hash=...,
    task_results=[...],
    workspace_history=[...],
    artifact_history=[...],
    adaptation_curve=[...],
    compute_cost=...,
    storage_cost=...,
    replay_hash=...,
)

Narrative interpretation must be generated from these records afterward.

==================================================
15. OBSERVABILITY

Make constructed machinery inspectable.

For interesting candidates be able to produce:

workspace allocation timeline
artifact creation timeline
artifact invocation counts
artifact dependency graph
task-by-task adaptation curve
artifact ablation results
artifact transplant results
program ancestry

Do not require semantic labels for artifacts.

Show structure and behavior first.

==================================================
16. IMPLEMENTATION SHAPE

Prefer a small repository such as:

crius/
    world.py
    tasks.py
    vm.py
    workspace.py
    artifacts.py
    player.py
    search.py
    evaluate.py
    qualify.py
    receipts.py
    report.py
    configs/
    tests/

Runnable commands should be ordinary Python commands.

Example:

python -m crius.baselines --config configs/c0.yaml
python -m crius.search \
    --config configs/c0.yaml \
    --iterations 1000 \
    --seed 1
python -m crius.qualify \
    --run RUN_ID \
    --suite heldout_v1
python -m crius.report \
    --run RUN_ID

No further conversational authorization should be necessary once configuration is valid.

==================================================
17. TESTS BEFORE SEARCH

Before running a long search, prove:

same inputs and seed replay exactly
workspace persists across tasks
workspace resets between independent lifetimes
qualification partitions do not leak into search
artifact invocation is deterministic
artifact deletion and ablation actually remove effects
transplant copies only the requested acquired state
program code does not silently change during a lifetime
receipts reconstruct the executed configuration

Also demonstrate that at least one hand-written reuse baseline benefits from accumulated machinery.

If the positive control cannot benefit, the sandbox is not yet testing the intended phenomenon.

==================================================
18. FIRST CAMPAIGN

Do not immediately launch a massive run.

First:

1. implement the sandbox;
2. execute deterministic tests;
3. run baselines;
4. inspect adaptation curves;
5. freeze task partitions and scoring;
6. run a modest search;
7. qualify promising candidates plus random contemporaries and ancestors;
8. perform workspace reset, scramble, ablation, and transplant tests;
9. inspect actual accumulated machinery;
10. report whether the pressure appears capable of selecting reusable adaptive computation.

If the result is predictable or trivial, say so.

Do not add complexity merely to rescue the hypothesis.

Instead identify precisely which degree of freedom appears missing.

==================================================
19. DESIGN FREEDOM

The structures above are starting constraints, not a requirement to implement my exact imagined architecture.

Before implementation, briefly challenge this design.

If there is a simpler or more powerful way to create pressure for reusable acquired computation while preserving the controls above, propose it.

You may change:

task grammar
workspace primitives
artifact representation
Player VM
search algorithm
measurement details

when you can explain why the change improves the experiment.

Do not change the central question:

Can search discover computational machinery that makes future learning cheaper because useful structure acquired from previous experience can be retained, organized, reused, modified, and recombined?

==================================================
20. DELIVERABLE

Return with:

architecture
runnable Python
tests
frozen Campaign-0 configuration
baseline results
search results
qualification results
raw receipt locations
adaptation curves
artifact/workspace causal tests
examples of interesting Player machinery
failures and null findings
your proposed Campaign-1 experiment

Separate:

OBSERVATION
what actually happened

from:

INTERPRETATION
what the machinery may be doing.

Do not build infrastructure beyond what this sandbox requires.

BUILD THE EXPERIMENT.
RUN THE EXPERIMENT.
SHOW US WHAT THE PROGRAMS CONSTRUCT.
