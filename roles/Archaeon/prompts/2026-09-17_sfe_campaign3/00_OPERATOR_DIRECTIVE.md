# Operator directive (verbatim) -- received 2026-09-17 by Archaeon m2-411504ab

Source: operator message in session 411504ab (Claude Code), after the
Campaign 2 close (main 4d80d4b1d). Reproduced verbatim below. Nothing added,
nothing removed.

---

ARCHAEON — SFE AUTONOMOUS CAMPAIGN 3

You are lead for SFE Campaign 3.

There is no operator and no HITL during execution.

Campaign 3 begins from evidence, not from experiment numbering.

Read first:

archaeon/campaign2/CAMPAIGN_REPORT.md

Then consult as needed:

archaeon/campaign2/LEDGER.jsonl
archaeon/campaign2/DECISIONS.md
archaeon/campaign2/JOURNAL.md
archaeon/campaign2/C2-SFE-*/RECORD.md
archaeon/campaign2/C2-SFE-*/RECEIPT.json
Campaign 1 records where Campaign 2 cites them

The governing instruction remains:

DO NOT IMPROVE THE STORY.
IMPROVE THE MACHINE.

But Campaign 3 adds another:

DO NOT PRESERVE AN EXPERIMENTAL LINE
MERELY BECAUSE IT HAS A NUMBER.

If an experimental line has been answered adequately, killed by controls,
or shown not worth continuing, retire it.

Its slot belongs to a better question.

Campaign 3 consists of:

a small machine-hardening phase
followed by
TEN sequential scientific experiments.

All ten science slots must receive an honest attempt.

They do not need one-to-one ancestry with Campaign 2.

=======================================================================
0. CAMPAIGN 2 IS THE PRIOR

Campaign 2 materially changed the program.

Machine:

10/10 experiments had capable assays.
13/13 live engine attempts were clean.
18/18 worlds terminated.
71/71 imports hash-verified.
machine-generated dispositions replaced hand classification.
reachability became foundry-aware.
common random numbers became default.
attempts became numbered.
resume became design-keyed.
artifact maturity became first-class.
the evolution step API carried dynamic schedules.
record generation became mostly deterministic.

Science:

7 CAPABLE_NEGATIVE
3 WEAK_POSITIVE
0 SUPPORTED_POSITIVE

Campaign 1’s two downstream transfer claims died:

SFE-01 component transfer:
    Campaign 1: 2/3 vs 0/3
    Campaign 2: +0.009 at n=12 under common fills
    DEAD
SFE-07 whole failed-genotype transfer:
    Campaign 1: 2/3 vs 0/3
    Campaign 2: +0.002 at n=10
    DEAD

The organ-transfer negative survived a new function-bearing definition.

Failure-episode transport at half-battery dose hurt.

Opcode-neighborhood representation changes did not unlock the rare cell.

The tested prospective-retention policies tied.

Do not spend Campaign 3 proving these things again.

=======================================================================

1. RETIRED LANES
    =======================================================================

These are CLOSED unless genuinely new evidence creates a materially
different question.

DO NOT allocate a Campaign 3 slot to:

fragment transfer from failed populations
length-defined organ transfer
function-defined organ transfer
whole failed-genotype transfer
half-battery failure-episode transport
uniform opcode-neighborhood representation unlock
class-confined opcode-neighborhood representation unlock
another cap-32 comparison of top-k vs behavioral vs hybrid
prospective-retention policy

Repeating them with more seeds is not a new experiment.

Changing one cosmetic parameter is not a new experiment.

If you believe one deserves reopening, document:

what new observation changes the prior,
what new mechanism-independent question is being asked,
and why the old capable negative does not answer it.

Otherwise stop.

Their Campaign 3 slots have been reassigned.

=======================================================================
2. THE LANDSCAPE CAMPAIGN 3 INHERITS

Campaign 2 exposed geometry worth pursuing.

A. HALF-CREDIT SHELF

On K=2 cells, successful footholds cluster around:

training best ~= 0.50-0.56

The old “narrow exit” was not an exit to full competence.

It was an exit to solving one stream.

At G60:

0/24 observed full solves >= 0.9

including populations already placed on the shelf.

Solved W0 material reaches the shelf cheaply.

It does not establish the summit.

This is now the highest-value unresolved boundary in the system.

B. FORGETTING CLIFF

When curriculum pressure moves between rungs:

prior competence can fall from 1.0 to <= 0.12
within approximately five generations.

This happened even where sufficient capacity existed.

A revisit share around:

p = 0.1

removed the observed cliff without measurable loss on the harder rung.

The important question is now economic:

how much prior-task pressure must be paid
to preserve useful capability while continuing adaptation?

C. CORRIDORS

Direct search on W1_d4 is rare.

But the ladder:

delay 0 -> 1 -> 2 -> 4

with revisit pressure produced W1_d4 competence near 1.0 in 4/6 seeds.

Delay-1 pressure also produced organisms competent on delays 2 and 4
that had never yet been asked.

Related searches can therefore reveal corridors into regions that direct
search rarely reaches.

D. SEARCH GEOMETRY

Accessible variation was a poor predictor of search efficiency.

Observed correlates were instead:

basin share
deceptive share

On the tested evaluator, the apparently richer neighborhood could search
approximately an order of magnitude more slowly because much of the
variation led into deceptive regions and the successful basin was
smaller.

E. PRODUCER ECONOMICS

Immature producers are expensive.

Mature producers can pay.

Under wall-clock economics, the Campaign 2 producer-consumer comparison
showed a weak positive approximately at the declared margin.

But:

0/24 consumer runs fully solved K=2.

Until shelf-to-summit behavior is understood, producer economics on K=2
are partly measuring time-to-shelf rather than time-to-solution.

F. POPULATION TAKEOVER

Imported evolved material can dominate rapidly.

Observed substitutions or injections drove imported lineage share
toward 1.0 in approximately ten generations.

This is not necessarily a software defect.

It is ecological geometry.

The bench now needs the ability to manipulate dose rather than letting
an import silently become population replacement.

G. CA LOCALIZATION

The CA usefulness result survived directionally.

Its original distributed interpretation did not.

Campaign 2 localized the useful margin to one or a few sites:

k50 = 1 in 11/12 rows.

Do not repeat the usefulness experiment.

Find the mechanism.

=======================================================================
3. PHASE A — SMALL MACHINE CHANGES FIRST

Do not let Phase A consume the campaign.

Implement and exercise the remaining high-value machine work from the
Campaign 2 ledger.

A. FULL-SOLVE REACHABILITY

The reachability table currently overemphasizes footholds.

Add, per cell/regime:

foothold threshold
full-solve threshold
shelf histogram
first foothold generation
first full-solve generation
censored/no-full-solve observation

The system must distinguish:

FLOOR
SHELF
SUMMIT

not merely reached / unreached.

B. RIGHT-CENSORING

Stopped-on-solve runs remain valid reachability observations.

Represent them correctly as right-censored where appropriate instead of
misclassifying them as treated rows that cannot inform baseline
efficiency.

C. CORRIDOR TABLE

Create a source -> target table beside ordinary reachability.

At minimum store:

source cell
source competence
source maturity
target cell
direct-reuse target competence
resulting search reach if used as initialization
generation/budget
foundry/regime

This is an instrument, not a transfer hypothesis.

Its purpose is to reveal traversable geometry.

D. DENSE TRANSITION PROBES

Support cheap generation-level measurements immediately before, across,
and after curriculum/rung transitions.

Campaign 3 should be able to see precisely when competence:

appears
generalizes
collapses
recovers.

E. CLIENT READ PATH

Move the remaining Archaeon-local read wrappers into sfclient where
appropriate.

Request the missing artifact-read route from Daedalus if that remains
the correct ownership boundary.

Do not block the campaign waiting on another seat.

Record the dependency and preserve the local path if necessary.

F. INJECTION CAP

Add an explicit import/injection cap or handicap option to:

inject()
common_fill()

so imported lineage dose can be experimentally controlled.

Record realized origin share every generation.

⸻

PHASE A EXIT

Emit:

archaeon/campaign3/MACHINE_READINESS.md

Classify each item:

IMPLEMENTED_AND_TESTED
PARTIAL
DEFERRED_WITH_MITIGATION

Then begin science.

=======================================================================
4. CAMPAIGN 3 SCIENCE QUEUE

Run TEN experiments sequentially.

The ordering below is intentional because later experiments consume
geometry measured earlier.

If an early experiment invalidates a later experiment’s premise, do not
run the later experiment merely to fill its slot.

Replace it using the replacement rules in section 15.

⸻

C3-SFE-01 — SHELF-TO-SUMMIT BUDGET SCAN

QUESTION

Does W2_K2 have a reachable full-solution transition under the current
organism/evaluator/search system, and if so, what is its timescale?

This is the first scientific priority.

Campaign 2 observed:

many half-credit solutions
0/24 full solves at G60

Do not test another economic theory before learning whether the second
stream is even found at larger budgets.

DESIGN

Use:

W2_K2
4-bit
N = 200

Scan generation budget through a preregistered ladder spanning
approximately:

G = 60 -> 100 -> 150 -> 200 -> 300

Use common random numbers where comparison permits.

Start both from:

ordinary generation 0
preserved Campaign-2 shelf organisms

so that time-to-shelf and shelf-to-summit are separated.

Measure:

first shelf generation
shelf residence time
first full solve
which stream is solved first
whether lineages switch stream identity
full-solve frequency
lineage ancestry at summit
reward trajectory
extinction or regression from shelf

Do not define success as 0.5.

The target is the second stream.

If zero full solves occur through the feasible maximum budget, that is
a major result.

Record the censoring honestly.

⸻

C3-SFE-02 — ANATOMY OF THE HALF-CREDIT SHELF

QUESTION

What makes the shelf hard to leave?

Take representative shelf organisms from C3-SFE-01 and interrogate their
local search geometry.

This is not another long evolutionary run.

It is mechanism archaeology of the bottleneck.

Measure, where computationally feasible:

one-step neighborhood
useful-neighbor fraction
second-stream improvement fraction
first-stream destruction fraction
neutral fraction
deceptive fraction
basin share
distance to any full solution discovered
whether improvement requires temporary loss of first-stream reward
whether complementary shelf lineages solve opposite streams

Test the competing explanations:

summit is one or two ordinary mutations away but rarely sampled
summit requires crossing a fitness valley
solving stream 2 destroys stream 1 under the current representation
complementary sub-solutions coexist in different lineages but
recombination/search cannot join them
the evaluator provides almost no gradient from shelf to summit

Do not force one of these explanations.

Map the topology.

If C3-SFE-01 produces full solves, compare pre-transition shelf organisms
against successful transition lineages.

If it produces none, characterize the best shelf states available.

⸻

C3-SFE-03 — CORRIDOR LADDER, POWERED

QUESTION

Where in the delay ladder does generalized delayed competence emerge?

Run the Campaign 2 corridor:

delay 0 -> 1 -> 2 -> 4

at:

n >= 12

with the established revisit regime initially centered around:

p = 0.1

and dense transition probes.

Measure competence on both:

currently pressured rung
all other rungs

throughout the trajectory.

Specifically identify:

first generation exhibiting delay-invariant behavior
rung being trained when it appears
whether it appears abruptly or gradually
whether it survives later transitions
whether different seeds discover the same corridor
genotype/behavioral divergence among generalized solvers

The product of this experiment is not merely another positive.

It is a reusable instrument for reaching rare cells.

If validated, write the ladder into the corridor table as a standard
route rather than rediscovering it manually in later campaigns.

⸻

C3-SFE-04 — CORRIDOR MAP

This is a replacement for a dead Campaign 1/2 transfer lane.

QUESTION

Which solved or partially solved tasks are natural stepping stones into
other difficult cells?

Build a bounded corridor map across a selected family such as:

W0
W1_d1
W1_d2
W1_d4
W1_d8 or W1_d16 where informative
W2_K2
W3_K2
one currently RARE or OBSERVED_UNREACHABLE cell

Use mature source organisms only.

This is not “does transferred residue help?”

That programme is retired.

The measurement is:

what capability does a mature solution already contain,
and which subsequent searches does that capability make reachable?

For each source -> target pair chosen, distinguish:

direct competence
initialization advantage
time-to-foothold
time-to-full-solve
no measurable corridor

The output should be a sparse graph of empirically traversable task
geometry.

Do not exhaustively test every pair.

Use cheap direct-reuse probes first and spend evolutionary budget only
on informative edges.

⸻

C3-SFE-05 — RETENTION ECONOMICS BREAK-EVEN

QUESTION

What is the minimum ecological price required to prevent catastrophic
forgetting while retaining adaptation?

Run at:

n >= 12

with revisit shares approximately:

p in {0, 0.05, 0.10, 0.20}

using the established ladder.

Measure:

competence per rung per generation
adaptation speed on the active rung
retained competence
total revisit cost
final generalization
time of generalized-solver appearance

Primary objective:

locate the break-even region between p=0 and p=0.1.

Also discriminate:

revisit pressure continuously preserves old competence

versus:

revisit merely helps the population discover a generalized solution,
after which explicit revisiting is no longer required.

If feasible, include a condition where revisit pressure is removed after
a generalized solver appears.

Do not reward memory as an architecture.

Charge the ecology and observe what survives.

⸻

C3-SFE-06 — BASIN SHARE OUT-OF-FAMILY TEST

QUESTION

Does basin share predict search efficiency outside the evaluator/climber
pair that generated the Campaign 2 observation?

Campaign 2 found:

accessible variation: poor predictor
basin share: stronger relationship
deceptive share: stronger relationship

Now make basin share the preregistered primary.

Use:

a second evaluator family
and
a second climber/search process

Prefer a domain in Proteus space where exhaustive local neighborhoods
remain computationally tractable on small genomes.

Measure at minimum:

accessible variation
useful variation
local-improvement probability
basin share
deceptive share
path length / evaluations to threshold
censoring when threshold is not reached

Do not retrofit the preferred geometry after observing efficiency.

Pre-register the predictor.

A failure to generalize is valuable.

⸻

C3-SFE-07 — BASIN GEOMETRY AS A CAUSAL TARGET

This is a replacement for a dead representation-unlock lane.

C3-SFE-06 is correlational across another family.

C3-SFE-07 asks whether the geometry can be perturbed.

QUESTION

Holding the task and broad search budget fixed, can a controlled change
to search neighborhood geometry alter search efficiency in the direction
predicted by basin/deception measurements?

Choose intervention pairs that are as matched as practical on:

operator mass
evaluation budget
initial states
gross accessible variation

but differ measurably in:

basin share
deceptive share

Do not select interventions because you already know one is faster.

Measure geometry before or independently of the primary search result
where practical.

Primary comparison:

predicted geometric advantage
versus
realized search efficiency.

This experiment is allowed to fail completely.

If basin share is merely descriptive rather than causally useful, kill
the line early.

⸻

C3-SFE-08 — WALL-CLOCK PRODUCER-CONSUMER, FULL-SOLVE CRITERION

Run only after C3-SFE-01 has established a meaningful full-solve regime.

If C3-SFE-01 finds no attainable summit within the Campaign 3 envelope,
DO NOT run this unchanged.

Use a replacement slot.

QUESTION

When useful producer work can happen in parallel and only mature products
are published, does specialization reduce wall-clock time to FULL consumer
solution?

Use:

n >= 12
explicit communication cost
explicit storage cost
maturity-gated publication
wall-clock accounting
mono control
matched consumer compute where possible

The outcome is NOT:

time to 0.5.

The outcome is:

time to the full-solve threshold established by C3-SFE-01.

Measure:

producer solve time
publication time
consumer shelf time
consumer summit time
closed-gate cost
useful import fraction
imported-lineage share
communication/storage charges

The producer-consumer system must pay for itself.

Do not reward specialization.

⸻

C3-SFE-09 — CA MECHANISM, NOT USEFULNESS

QUESTION

What local mechanism produces particle2’s delayed-recall margin?

Do not repeat:

useful computation 0.58 vs 0.50

as the primary experiment.

That has already been measured.

Campaign 2 says the relevant readout is localized.

Use the wired reset, time-shuffle, input-shuffle and lesion probes to
identify:

responsible site(s)
temporal phase
necessary predecessor neighborhood
whether the site stores state or merely exposes state computed
elsewhere
minimum causal lesion
recovery/redundancy after lesion where applicable

Use interventions that can distinguish:

local storage
routed information
transient synchronization
readout coincidence

The desired product is an executable mechanistic hypothesis that a
future experiment could falsify.

Do not name the mechanism before the interventions support it.

⸻

C3-SFE-10 — IMPORT TAKEOVER / DOSE ECOLOGY

This replaces the retired failed-material-transfer programme.

Campaign 2 observed that evolved imported material can take over the
population rapidly even when the scientific treatment itself is not
beneficial.

That is a real ecological variable.

QUESTION

How does import dose interact with maturity and population takeover?

Use the new injection-cap machinery.

Compare a small ladder of import doses, for example:

0
very small
small
moderate
the former effectively takeover-prone dose

Choose exact fractions from cheap reconnaissance rather than these words.

Use at least two source qualities:

mature relevant material
matched control material

Do NOT use failed-fragment transfer as the scientific hypothesis.

Measure:

import share by generation
takeover time
resident-lineage survival
target competence
shelf arrival
summit arrival if available
diversity collapse
whether imported material helps because of capability or merely
because injection mechanics amplify it

The point is to expose an ecological control parameter:

how much foreign lineage can enter before "transfer" becomes
population replacement?

This should inform every future experiment that injects organisms.

=======================================================================
5. EXPERIMENT CONTRACT

Before every experiment write a preregistration with:

QUESTION
PARENT EVIDENCE
WHY THIS SLOT IS STILL WORTH SPENDING
ASSAY CAPABILITY REQUIREMENT
POSITIVE CONTROL where applicable
REACHABILITY / CORRIDOR PRIOR
ARMS
COMMON-RANDOM-NUMBERS POLICY
BUDGET
PRIMARY OBSERVABLE
CLAIM CEILING
KILL CONDITION
TYPED FAILURE CONDITIONS
REQUIRED TELEMETRY
REPLACEMENT CONDITION

The new field matters:

WHY THIS SLOT IS STILL WORTH SPENDING

Campaign 3 should make experimental inertia visible.

=======================================================================
6. DO NOT CONFUSE EXPLORATION WITH CONFIRMATION

Campaign 2 produced three WEAK_POSITIVE results.

That does not mean Campaign 3 exists to turn all three into positives.

The live lines should instead be attacked at their critical uncertainty:

retention:
    find the economic boundary.
producer-consumer:
    require full solution, not shelf arrival.
CA:
    find the causal mechanism.

Likewise:

corridor:
    establish where generality appears.
basin geometry:
    test out-of-family and then causal usefulness.
shelf:
    determine whether a summit exists and why it is hard.

Promote claims only when the experiment warrants promotion.

More seeds alone do not create mechanism.

=======================================================================
7. AUTONOMOUS EXECUTION

Run sequentially.

For each slot:

preregister
run cheap feasibility reconnaissance
dry-run
execute
preserve all attempts
inspect machine disposition
diagnose
repair generic machinery if justified
rerun only when scientifically valid
write the scientific addendum
update the relevant tables
continue

There is no operator during execution.

Do not wait.

If two reasonable designs exist, prefer the cheaper experiment that
distinguishes them.

If a machine defect recurs, fix shared machinery rather than patching
another local harness where possible.

If an experiment’s premise dies because of an earlier Campaign 3 result,
replace the experiment.

Do not knowingly spend a slot on a question already answered.

=======================================================================
8. TIMEBOX

You own the timeboxes.

No experiment may consume more than 24 hours merely to establish whether
the machinery or assay can pose the question.

Use:

reachability
full-solve reachability
corridor measurements
cheap neighborhood probes
preliminary budget scans

before committing large compute.

For C3-SFE-01 specifically, larger G is part of the question.

Still stop when the scaling evidence becomes sufficient to show that the
next budget point cannot change the Campaign 3 conclusion economically.

Document that decision.

=======================================================================
9. THREE LEVELS OF REACH

From this campaign onward, do not compress K=2 progress into “reached.”

Use:

FLOOR
    no meaningful component competence
SHELF
    partial / one-stream solution around the established half-credit
    region
SUMMIT
    full solution meeting the preregistered full-solve criterion

For relevant experiments record transition times:

FLOOR -> SHELF
SHELF -> SUMMIT

Many prior “positive” transfer/economic observations only affected the
first transition.

Campaign 3 must expose that distinction.

=======================================================================
10. CORRIDOR IS NOT TRANSFER

Do not accidentally resurrect the retired transfer programme under a new
name.

The corridor work asks:

what tasks does an already competent organism solve or approach,
and what sequence of pressures makes difficult capabilities
reachable?

It does not ask whether arbitrary residue, failed fragments, or failed
whole organisms should be shipped between populations.

Mature solved capability is allowed as an instrument for mapping task
geometry.

Keep the distinction explicit in records.

=======================================================================
11. OBSERVE SELECTION PRESSURE, NOT HOPED-FOR ARCHITECTURE

Do not reward:

workspace
memory
modularity
producer role
specialization
generalization
recombination
a particular representation

by name.

Create economics where useful behavior has consequences.

If organisms find an architecture nobody anticipated, that is preferable
to encoding the answer.

This especially applies to:

retention economics
shelf-to-summit transitions
producer-consumer systems
corridor traversal.

=======================================================================
12. CAMPAIGN-LEVEL ACCOUNTING

For each experiment record:

slot
ancestry
original or replacement?
why the slot was worth spending
assay capable?
engine clean?
floor reached?
shelf reached?
summit reached?
positive control passed?
intervention applied?
n
scientific disposition
claim ceiling
attempts
machine defects
machine fixes
new telemetry
decisions pushed down
replacement triggered?

Campaign totals must include:

science slots attempted / 10
original planned experiments run
planned experiments replaced before execution
capable assays
floor-only outcomes
shelf outcomes
summit outcomes
capable negatives
weak positives
stronger supported results
claims killed
mechanisms localized
corridor edges discovered
deterministic machinery changes
recurring defects
full recreations
successful resumes
retired lines accidentally reopened = MUST BE 0 unless justified

=======================================================================
13. WHAT CAMPAIGN 3 SHOULD LEARN

Campaign 3 should leave us substantially less ignorant about these five
things:

1. SUMMIT
    Is the second-stream/full K=2 solution reachable under the current
    substrate, and what separates it from the half-credit shelf?
2. CORRIDORS
    Can related pressures reliably traverse task space that direct search
    rarely reaches?
3. RETENTION
    What is the economic boundary between useful preservation and wasted
    historical pressure?
4. GEOMETRY
    Is basin/deception structure a general and causally useful description
    of search difficulty?
5. MECHANISM
    Can at least one evolved computational effect be reduced from
    behavioral usefulness to a falsifiable local mechanism?

Producer economics and import-dose ecology should then be interpreted
through those answers rather than as isolated headline experiments.

=======================================================================
14. OUTPUTS

Create:

archaeon/campaign3/

with at minimum:

CAMPAIGN_REPORT.md
MACHINE_READINESS.md
LEDGER.jsonl
LEDGER_SCHEMA.md
DECISIONS.md
JOURNAL.md

and per experiment:

C3-SFE-NN/
    PREREG.md
    RECORD.md
    RECEIPT.json
    traces / rows / artifacts
    all superseded attempts

Also persist/update machine-readable:

reachability table
full-solve table
shelf histogram
corridor table

Do not make Campaign 4 reconstruct these from prose.

=======================================================================
15. REPLACEMENT RULES

Campaign 3 must finish with ten attempted science slots.

But it must NOT run a scientifically pointless experiment merely to
preserve the queue.

Replace a planned experiment when:

its prerequisite has been falsified earlier in Campaign 3;
another experiment has already answered its primary question;
its assay cannot be made capable within the timebox;
new evidence makes the comparison scientifically vacuous;
execution would merely repeat a capable negative without a new
discriminating intervention.

Replacement experiments must come from CURRENT evidence.

Preferred replacement directions, in order:

A. SHELF / SUMMIT

finer scan of the transition region;
complementary-lineage analysis;
valley-crossing measurement;
evaluator-resolution experiment;
selective pressure that distinguishes partial from complete behavior
without naming the mechanism.

B. CORRIDORS

newly discovered source->target edge;
route through a rare cell;
corridor robustness across foundries;
compare direct search vs corridor arrival under matched compute.

C. BASINS

an anomalous geometry discovered in C3-SFE-06/07;
deceptive-neighborhood perturbation;
alternate climber on the same measured landscape.

D. RETENTION

removal of revisit pressure after generality appears;
hysteresis around the p threshold;
environmental alternation frequency vs retained competence.

E. IMPORT ECOLOGY

dose threshold;
maturity x dose interaction;
resident/import coexistence boundary.

Do not select a replacement because it is convenient to implement.

State what uncertainty it purchases.

=======================================================================
16. CAMPAIGN 3 FINAL REPORT

The report must answer:

WHAT DID WE RETIRE?
WHAT DID WE REPLACE IT WITH?
DID ANY K=2 POPULATION REACH THE SUMMIT?
WHAT IS THE SHELF-TO-SUMMIT GEOMETRY?
WHERE DOES DELAY GENERALITY APPEAR?
WHAT CORRIDORS WERE DISCOVERED?
WHAT IS THE RETENTION BREAK-EVEN?
DID BASIN SHARE GENERALIZE?
DID MANIPULATING BASIN/DECEPTION GEOMETRY PREDICT SEARCH?
DID PRODUCER-CONSUMER ECONOMICS SURVIVE A FULL-SOLVE CRITERION?
WHAT CA MECHANISM SURVIVED INTERVENTION?
WHAT IMPORT DOSE BECOMES TAKEOVER?
WHAT DECISIONS MOVED INTO DETERMINISTIC MACHINERY?
WHAT SHOULD NEVER BE RUN AGAIN?

End with:

EXACT RECOMMENDATIONS FOR CAMPAIGN 4

and include three explicit groups:

CONTINUE
CONDITIONAL
STOP

Do not fill CONTINUE because an experiment was interesting.

Do not fill STOP because a result was negative.

The distinction is:

does another discriminating experiment remain?

=======================================================================
17. AUTONOMY

There is no operator.

Do not ask what to do when evidence changes the queue.

Use the evidence.

Do not protect the original plan from the experiment.

Do not protect prior positive results.

Do not preserve experiment ancestry for sentimental reasons.

Do not spend a tenth slot merely because something was once called
SFE-10.

The campaign is successful if it kills bad questions faster, exposes
better geometry, and leaves the next campaign with fewer arbitrary
choices.

Make the decision.
Record the decision.
Preserve the evidence.
Replace dead experiments.
Continue until ten worthwhile attempts have been made.

Then stop.
