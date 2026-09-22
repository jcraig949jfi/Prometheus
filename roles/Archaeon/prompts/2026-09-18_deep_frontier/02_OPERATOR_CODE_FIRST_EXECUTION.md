OPERATOR DIRECTIVE -- ARCHAEON -- CODE-FIRST EXPERIMENT EXECUTION
(received 2026-09-18 in chat after the first Deep Frontier item ran; filed
verbatim by Archaeon[m2-49ee5a4d] at the clock time in MANIFEST.md; pure-ASCII
substitutions only: straight quotes, "--" for em-dashes.)

-----------------------------------------------------------------------
ARCHAEON -- CODE-FIRST EXPERIMENT EXECUTION

Change of operating model.

Effective immediately, the LLM is not the experiment scheduler and is not
the authority that decides whether ordinary experiments may run.

The LLM's role is to DESIGN experiments.

Python's role is to EXECUTE them.

1. EVERY EXPERIMENT BECOMES CODE

Each experiment or experiment family must exist as a runnable Python entry
point, module, or parameterized experiment specification consumed by a
Python runner.

A valid experiment defines at minimum:

* experiment ID;
* world or world-generator specification;
* organism/population specification;
* parameter values;
* random seed handling;
* runtime budget;
* controls;
* required capabilities;
* telemetry;
* output schema;
* checkpoint/replay behavior.

The experiment must be independently runnable without another
conversational decision.

2. LLM RESPONSIBILITIES

Use LLMs to:

* generate hypotheses;
* design experiment families;
* propose parameter sweeps;
* design controls;
* propose perturbations;
* inspect results;
* identify anomalies;
* propose descendants;
* revise world generators;
* propose new measurements;
* explain competing interpretations.

Do not use LLMs as runtime permission systems.

3. EXECUTION RESPONSIBILITIES

The Python scheduler:

* discovers experiment specifications;
* determines whether required capabilities exist;
* executes every runnable item;
* skips locally blocked items;
* resumes interrupted jobs;
* writes structured receipts;
* maintains checkpoints;
* advances the queue automatically.

A blocked experiment never blocks unrelated experiments.

4. DEPENDENCIES

Dependencies must be declared in machine-readable form.

Example:

required_capabilities = {
"graph_runtime",
"composed_world_v1"
}

If a capability is absent:

status = BLOCKED_MISSING_CAPABILITY

Then continue to the next experiment.

No prose ruling is required.

5. FALSIFIERS AND LOCAL CONDITIONS

Scientific preregistrations such as PROTEUS-46 become code or data
attached to the affected experiment family.

They may suppress or alter only the transformations they explicitly
cover.

They may not stop the global scheduler unless they expose a
runtime-integrity failure.

6. GLOBAL HALTS

The runner may stop globally only on executable integrity failures such
as:

* nondeterministic replay where replay is required;
* corrupt checkpoint ancestry;
* invalid evidence writes;
* invalid provenance;
* observation/interpretation contamination;
* unrecoverable runtime state.

These conditions must be represented as assertions, tests, or runtime
errors.

They must not depend on conversational interpretation.

7. RESULTS

Experiments write structured machine-readable receipts first.

Narrative interpretation is downstream.

The raw record must survive even if no LLM is available.

8. FRONTIER GENERATION

After results exist, LLMs may propose descendant experiment
specifications.

Those proposals are translated into runnable Python experiments or
parameter sets.

Once validated syntactically and against the experiment schema, they
enter the queue.

The scheduler does not ask the LLM again for permission to run them.

9. PARAMETER DEPTH

Prefer parameterized experiment families over one-off scripts.

A single hypothesis should support large sweeps across:

* seeds;
* world parameters;
* population sizes;
* mutation regimes;
* schedules;
* horizons;
* histories;
* topologies;
* complexity levels;
* pressure strengths;
* control conditions.

The research tree should deepen by generating executable configurations,
not by generating additional authorization prose.

10. OPERATING PRINCIPLE

LLMS DESIGN.
CODE RUNS.
DATA RECORDS.
LLMS INTERPRET.
CODE BRANCHES AGAIN.

Remove conversational gates from the critical execution path.
-----------------------------------------------------------------------
