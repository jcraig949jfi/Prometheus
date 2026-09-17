# Operator directive (verbatim, chat, 2026-09-17 ~00:05 UTC) -- ARCHAEON: SFE AUTONOMOUS TEN-EXPERIMENT CAMPAIGN

Received by Archaeon[m2-411504ab] on M2 after the SSF cycles 1-3 packet
(main 37ca43bd4). Authority: the operator's verbatim directive; it
declares NO operator and NO HITL for the campaign's duration, so every
decision is a recorded local campaign decision (D-###) in
archaeon/campaign1/DECISIONS.md. Where this directive and the seat
charter ("not an executor") disagree for THIS campaign, the directive
wins (base-role: the operator's verbatim directive outranks a seat file).

----------------------------------------------------------------------

ARCHAEON -- SFE AUTONOMOUS TEN-EXPERIMENT CAMPAIGN

You are the lead for this campaign.

Your job is to take the SFE ecosystem through ten sequential experiments, autonomously, from attempted startup through teardown/documentation.

There is no operator and no HITL for this campaign.

Do not stop to ask questions.
Do not wait for clarification.
Do not leave a decision pending merely because a human could make it.

When a decision is required, make the smallest scientifically defensible and reversible decision yourself, record exactly what you chose and why, and continue.

The campaign ends only after an honest attempt has been made on all ten experiments below.

This is simultaneously:

1. a scientific campaign;
2. an SFE startup/teardown stress test;
3. an autonomous-operations exercise;
4. a search for machinery that should become deterministic;
5. a telemetry-design exercise;
6. a bug and friction discovery campaign.

The campaign is successful even if many scientific hypotheses fail.

A failed, skipped, blocked, malformed, or inconclusive experiment is useful if its failure is accurately characterized and leaves the ecosystem easier to operate next time.

==================================================
I. OPERATING CONSTITUTION

Run the experiments SEQUENTIALLY in the order listed below.

Do not run several simultaneously merely to increase throughput.

The point is to repeatedly exercise:

prepare
-> start
-> observe
-> make local decisions
-> finish or table
-> collect artifacts
-> teardown
-> verify cleanup
-> write lessons
-> start the next experiment

For every experiment, first find the smallest scientifically meaningful run that exercises the relevant SFE machinery.

Do not turn an alpha into a giant production campaign.

TIMEBOX RULE:

If a minimally credible version of an experiment would require more than 24 wall-clock hours to execute, do not run that version.

Reduce the experiment if a scientifically coherent smaller version exists.

If no meaningful version can exercise the machinery in <=24 hours:

TABLE / SKIP it.

Record:

* why it exceeded the bound;
* the measured or estimated bottleneck;
* the smallest future version that could run;
* what infrastructure change would make it practical.

Then immediately proceed to the next experiment.

Never allow one experiment to monopolize the entire campaign.

==================================================
II. AUTONOMOUS DECISION RULE

There is NO OPERATOR.

When ambiguity arises:

1. preserve experimental integrity;
2. preserve prior frozen semantics where they exist;
3. prefer the smallest reversible decision;
4. prefer measurement over intuition;
5. prefer an explicit temporary local policy over hidden improvisation;
6. record the decision before or immediately after taking it;
7. continue.

Do not manufacture an operator dependency.

Do not write:

"Need operator decision."

Instead write:

"Local campaign decision D-###: I chose X because Y. The alternative was Z. Revisit if condition Q occurs."

If a question genuinely cannot be answered without changing the scientific claim, table the affected portion and continue with whatever remains valid.

==================================================
III. DO NOT GET STUCK PERFECTING ONE EXPERIMENT

Each experiment gets an ATTEMPT.

An attempt may end as:

COMPLETE
NULL
NEGATIVE
INCONCLUSIVE
BLOCKED
TABLED
SKIPPED-TIMEBOX
INSTRUMENT-FAILURE

These are all legitimate outcomes.

Do not spend the whole campaign repairing Experiment 1.

If you find a fix that is small, local, testable, and necessary to exercise the machinery, make it.

If the required repair begins turning into a separate engineering project, document it, table the experiment, and move on.

The first campaign is intended to expose the rough edges.

A subsequent campaign can make the experiments clean.

==================================================
IV. REQUIRED NOTES FOR EVERY EXPERIMENT

Maintain a campaign journal.

For every experiment record at minimum:

A. STARTUP

* experiment ID;
* hypothesis/question;
* exact starting commit/version;
* services required;
* datasets/artifacts required;
* world/specification used;
* seeds;
* relevant frozen assumptions;
* startup commands/procedure;
* startup time;
* unexpected manual steps;
* hidden machine assumptions discovered.

B. EXECUTION

* smallest runnable design chosen;
* time budget;
* resource budget;
* major measurements;
* checkpoints;
* decisions made autonomously;
* failures encountered;
* recoveries attempted;
* whether restart/resume worked;
* whether repeated work could have been avoided.

C. SCIENCE

* primary outcome;
* important controls;
* whether the assay was capable of detecting the hoped-for effect;
* evidence for/against/inconclusive;
* possible confounders;
* what must NOT be claimed.

D. TEARDOWN

* teardown procedure;
* time to teardown;
* orphaned jobs/processes/services;
* stale queues/leases/locks;
* temporary files or state left behind;
* whether the next experiment started from a clean state.

E. BENCH IMPROVEMENT

Explicitly record:

BUGS FOUND

FRICTION FOUND

MISSING TELEMETRY

AUTOMATION OPPORTUNITIES

DECISIONS THAT SHOULD MOVE INTO DETERMINISTIC MACHINERY

DECISIONS THAT SHOULD REMAIN SCIENTIFIC/POLICY DECISIONS

MISSING FAILURE STATES

MISSING RECOVERY PROCEDURES

PORTABILITY PROBLEMS

OBSERVABILITY GAPS

F. LANDSCAPE / GRADIENT NOTES

This is especially important.

Ask:

What did the current instrumentation reduce to a binary outcome that should instead expose a landscape?

What intermediate measurements might reveal:

* gradients;
* plateaus;
* cliffs;
* basins;
* local optima;
* dead regions;
* phase transitions;
* useful weak signals;
* precursor behaviors;
* diversity before performance;
* partial transfer;
* partial mechanism reuse?

Do not invent such signals.

Identify places where additional telemetry could make them measurable.

==================================================
V. MACHINE-READABLE IMPROVEMENT LEDGER

Maintain a cumulative ledger across all ten experiments.

Each finding should have:

ID
experiment
category
severity
symptom
evidence
current workaround
proposed deterministic fix
proposed telemetry
whether it blocks future runs
whether it is safe to defer

Do not repeatedly rediscover the same defect without linking to the earlier entry.

If something recurs, increment recurrence count and note whether the attempted mitigation helped.

==================================================
VI. THE TEN SFE EXPERIMENTS

Run in this order.

SFE-01 -- H0 FAILURE + COMPONENT EXCHANGE

Question:

Can residue from prior computation -- failures and reusable components -- improve later target search?

Use the smallest credible four-cell exchange harness:

00 neither transferred
10 failures only
01 components only
11 failures + components

Keep combined gain and interaction conceptually separate.

The purpose of this run is both to exercise artifact exchange and to test whether transported residue has measurable downstream consequence.

SFE-02 -- H3 PROSPECTIVE VALUE OF RETAINED DIVERSITY

Generate one common candidate stream and replay it through bounded retention policies such as:

* source-performance Top-K;
* uniform reservoir;
* behavioral archive;
* behavioral archive + reserved random sample.

Freeze the resulting stores before exposing future tasks.

Ask whether retained diversity produces prospective utility rather than merely interesting archives.

SFE-03 -- H1 RELEVANT FAILURE TRANSPORT

Compare target solving under:

* relevant compatible transported failures;
* random-compatible transported failures;
* fresh bounded search / CEGIS without transferred failure information.

Recompute target relevance honestly.

Do not transport target answers disguised as failures.

SFE-04 -- H2 STATEFUL CA -> CAUSAL COMPONENT -> REUSE

Exercise the smallest stateful cellular-computation path that can distinguish:

1. useful bounded computation;
2. causal contribution;
3. frozen reuse in a new composition.

A whole reservoir performing well is not automatically evidence for a reusable localized component.

Use matched interventions where possible.

SFE-05 -- H4 ADAPTIVE CHALLENGES x TRANSFER

Exercise a bounded 2x2 design:

fixed vs adaptive challenges

crossed with

transfer disabled vs transfer enabled.

Evaluation should remain independently defined.

Ask whether adaptive challenge generation and transfer reinforce one another rather than merely making the environment harder.

SFE-06 -- H5 ENCODING AND ACCESS TO USEFUL VARIATION

Hold the underlying evaluator/phenotype scope fixed while varying genotype->phenotype encoding under matched finite conditions.

Ask whether representation changes:

* navigability;
* accessible useful variation;
* mutation neighborhoods;
* search success.

Do not confuse a balanced decoder with proof of an unbiased search geometry.

SFE-07 -- CROSS-WORLD EXAPTATION

Take frozen artifacts that were weak, specialized, failed, or mediocre in World A.

Expose them prospectively to a predeclared World B.

Compare against suitable controls.

Ask whether previously unimpressive residue becomes useful after environmental change.

No retrospective cherry-picking after seeing World B results.

SFE-08 -- FRANKENSTEIN CHIMERA

Select components/organs from independently failed or incomplete lineages.

Compose them under explicit provenance.

Compare:

* contributing ancestors;
* intended chimera;
* random-compatible recombinations where feasible.

Ask whether individually unsuccessful machinery can become useful through recombination.

Do not interpret mere executability as synergy.

SFE-09 -- REPRESENTATION UNLOCK

Find a bounded task/world in which search is measurably stuck under representation A.

Preserve semantics and resource accounting while expressing the same problem through representation B and, if practical, C.

Ask whether the apparent solver failure is partly imposed by representational geometry.

SFE-10 -- PRODUCER-CONSUMER SPECIALIZATION

Compare a bounded monolithic search organism/process with a system in which:

* producers generate reusable failures/components/artifacts;
* consumers use them later;
* communication and storage carry explicit costs.

Ask whether specialization and artifact exchange improve later solving under matched total resource envelopes.

==================================================
VII. BETWEEN EXPERIMENTS

After each experiment:

1. commit or otherwise durably preserve all relevant receipts and notes;
2. verify that the experiment can be reconstructed;
3. teardown temporary machinery;
4. verify no accidental process or lease remains;
5. update the cumulative improvement ledger;
6. record what should be changed before this experiment is run again;
7. proceed immediately to the next experiment.

Do NOT wait for those improvements to be implemented unless they are tiny and necessary for the next experiment.

==================================================
VIII. FINAL CAMPAIGN REPORT

After all ten have received an attempt, produce a single campaign report.

Include:

* ten-row experiment disposition table;
* scientific outcome of each;
* startup reliability;
* teardown reliability;
* restart/resume reliability;
* number and type of autonomous decisions;
* recurring bugs;
* recurring friction;
* infrastructure coupling discovered;
* manual steps that should disappear;
* deterministic decisions that can now be pushed into machinery;
* places where human/scientific discretion still seems genuinely necessary;
* telemetry additions with highest expected value;
* observed landscape features or places where richer landscapes appear recoverable;
* experiments worth rerunning first;
* experiments that should remain tabled;
* changes required before Campaign 2.

Most importantly:

Separate SCIENTIFIC FAILURES from INSTRUMENT FAILURES.

Do not improve the story.

Improve the machine.

The campaign is complete when all ten experiments have an honest recorded disposition and the ecosystem can explain what it learned about both computation and itself.

BEGIN WITH SFE-01.
