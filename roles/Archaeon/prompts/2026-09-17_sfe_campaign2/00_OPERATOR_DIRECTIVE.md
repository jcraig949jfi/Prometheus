# Operator directive (verbatim) -- received 2026-09-17 by Archaeon m2-411504ab

Source: operator message in session 411504ab (Claude Code), after the
Campaign 1 close (main f74b5cc5b; report blob dc559de117e3f71845bb92b4871b42dd43d00c73).
Reproduced verbatim below. Nothing added, nothing removed.

---

ARCHAEON — SFE AUTONOMOUS CAMPAIGN 2

You are lead for SFE Campaign 2.

There is no operator and no HITL during execution.

Campaign 1 is the prior. Do not restart from the original ten prompts as though nothing was learned.

Your first source of truth is:

archaeon/campaign1/CAMPAIGN_REPORT.md

Campaign 1 report blob at handoff:

dc559de117e3f71845bb92b4871b42dd43d00c73

Also read, as needed:

archaeon/campaign1/LEDGER.jsonl
archaeon/campaign1/DECISIONS.md
archaeon/campaign1/JOURNAL.md
archaeon/campaign1/SFE-NN/RECORD.md
archaeon/campaign1/SFE-NN/RECEIPT.json
archaeon/campaign1/SFE-NN/rows.json
preserved attempt-1 records

The governing instruction remains:

DO NOT IMPROVE THE STORY.
IMPROVE THE MACHINE.

Campaign 2 is a machine-hardening and discriminating-follow-up campaign.

It is NOT ten unchanged reruns.

It is NOT a hunt for more positive results.

It is NOT permission to propagate Campaign 1’s weak positives as facts.

Campaign 1 produced enough evidence to decide which questions need to be rerun, which results already stand at their claim ceilings, which assays were incapable, and which machinery defects should never again require Archaeon to notice and repair them manually.

Use that evidence.

=======================================================================
0. CAMPAIGN 1 PRIOR

Campaign 1 completed all ten experimental attempts in 6 h 20 min.

The final engine path was reliable:

32 worlds created
32 worlds terminated
0 orphans
0 engine errors on attempts of record
14/14 attempts successfully started
4/4 reruns successfully restarted

The principal defects are now ABOVE the engine.

Campaign 1 identified:

no pooled reachability table
no guaranteed common random numbers
no resume/idempotent experiment execution
attempts not natively distinguished
untyped scientific failure states
repeated digest/hash normalization mistakes
inadequate read wrappers
insufficient artifact-maturity telemetry
missing generation-step machinery
hand-built records/dispositions/ledger entries

Three experiments — SFE-02, SFE-03 and SFE-09 — ran but never genuinely posed their scientific question.

That was not three independent failures.

It was one repeated bench pathology:

a target cell or stream was selected without a pooled estimate
showing that the necessary interrogation regime was reachable.

Campaign 1 also produced:

SFE-08:
    a capable negative.
SFE-10:
    a capable negative at its tested economic envelope.
SFE-01, SFE-04, SFE-05, SFE-06, SFE-07:
    weak positive evidence at n=3.

Those five positives are NOT established findings.

Campaign 1 explicitly sets their claim ceiling below propagation and requires larger n and independent falsification before a result that matters downstream is promoted.

Campaign 2 inherits those ceilings.

=======================================================================

1. PHASE A — FIX THE MACHINE BEFORE THE NEXT EXPERIMENT
    =======================================================================

Before launching Campaign 2 science, implement the machine changes Campaign 1 says should have existed before SFE-01.

Do not merely add TODOs.

Exercise each change minimally and preserve evidence that it works.

A. REACHABILITY TABLE

Build a persistent reachability table keyed at minimum by:

cell
value_bits
N
G

Populate it from historical Campaign 1 material where valid and from every new run thereafter.

Capture at least:

runs attempted
runs reaching foothold / solved criterion
first_solved_gen where applicable
pooled reach frequency
uncertainty/band appropriate to the sample count
observed reward ceiling
relevant evaluator resolution

A harness choosing a target must consult this table.

A target should not be selected from a previous 0/3 result as though 0/3 means “reachable but difficult.”

Distinguish:

COMMON
REACHABLE
RARE
UNESTABLISHED
OBSERVED_UNREACHABLE_AT_BUDGET

Do not turn this into a hard rule that forbids exploration.

It is an instrument for knowing what question is actually being purchased with the proposed budget.

B. TYPED SCIENTIFIC / ASSAY STATES

Push the known deterministic states into machinery.

At minimum support the Campaign 1 classes:

INTERVENTION_NOT_APPLIED
RESIDUE_BELOW_FLOOR
IMMATURE_ARTIFACT
STREAM_BELOW_THRESHOLD
TARGET_UNREACHABLE
READOUT_CANNOT_EXPRESS
POSITIVE_CONTROL_FAILED

These states must be produced from measurements, not assigned by Archaeon after reading rows.

They must remain distinct from a valid scientific negative.

A capable negative is evidence.

An incapable assay is not.

C. COMMON RANDOM NUMBERS BY DEFAULT

Repair the WSE loop so provenance labels cannot accidentally change the RNG treatment.

Separate:

rng_label
provenance / arm label

Generation-zero population construction must have an explicit common-fill path for matched arms.

Record gen0 provenance in the trace.

A comparison harness should have to opt OUT of common random numbers, not remember to opt in.

D. RESUME / IDEMPOTENCE / ATTEMPTS

Implement idempotent experiment operations keyed deterministically, e.g. from:

experiment
step
cell
seed

Persist world/artifact identifiers as soon as they are created.

A restart should replay/resume where valid rather than reconstruct everything.

Give every attempt an explicit attempt identity.

Never again require:

RECEIPT.json -> manual rename -> RECEIPT_attempt1.json

as the mechanism by which provenance survives.

E. ARTIFACT MATURITY

Every artifact capable of entering another population or experiment must carry enough telemetry to distinguish mature useful material from immature residue.

At minimum capture:

source elite reward
source competence
share-above-chance or equivalent population maturity
source cell
source budget
source generation
artifact lineage

Campaign 1’s strongest producer-consumer clue was not “exchange helps.”

It was:

exchange only paid in the observed case where the producer had
actually solved its own cell.

Make that variable first-class.

F. DIGEST / CLIENT NORMALIZATION

Eliminate the recurring sha256: / id / digest ambiguity.

There should be one canonical digest representation on both sides of the client.

Add the needed sfclient read wrappers rather than making experiment harnesses manually reconstruct API behavior.

Consolidate engine base URL / certificate information into one tracked descriptor rather than scattered defaults.

G. GENERATION STEP API

Add the missing evolution step abstraction so that:

curricula
ramps
producer-consumer schedules
changing pressures

can invoke one shared generation-transition mechanism instead of reimplementing evolution loops.

H. TELEMETRY STRUCTURES

Add the Campaign 1 high-value measurements where relevant:

first_solved_gen
source maturity
gen0 provenance
imported-lineage share by generation
intervention applied counts
rung x generation competence
genome length / opcode composition summaries

In particular, do not allow a battery mean to hide the kind of forgetting shelf observed in SFE-05.

I. AUTOMATIC ACCOUNTING

Generate experiment records from receipts.

Generate candidate ledger entries from receipts.

Compute typed disposition candidates where deterministic.

Humans/agents may still interpret science.

They should not transcribe numbers that already exist in machine-readable form.

⸻

PHASE A EXIT GATE

Before Campaign 2 science begins, write a machine-readiness receipt demonstrating which of the nine groups above are:

IMPLEMENTED_AND_TESTED
PARTIAL
NOT_IMPLEMENTED

Campaign 2 may continue with a PARTIAL item if completing it would consume disproportionate time.

It may not silently forget it.

For every incomplete machine change, record why, what experiment it threatens, and the local mitigation.

Do not spend the entire campaign polishing infrastructure.

The machine exists to expose scientific landscapes.

=======================================================================
2. PHASE B — BUILD TEN CAMPAIGN 2 EXPERIMENTS

Campaign 2 again consists of ten sequential experiment attempts.

They do NOT need to be one-for-one reruns of SFE-01 through SFE-10.

Use Campaign 1 to construct the ten highest-information experiments available after Phase A.

Preserve explicit ancestry:

C2-SFE-NN
parent experiment(s)
Campaign 1 evidence motivating it
machine changes it exercises
scientific question it discriminates

The Campaign 1 report already determines several mandatory priorities.

Honor them.

=======================================================================
3. MANDATORY FIRST SCIENTIFIC PRIORITIES

PRIORITY 1 — REPAIR SFE-03’S ASSAY

Failure-episode transport was never tested because W1_d4 was too rare at the chosen budget.

Campaign 1 pooled evidence says W1_d4 was reached only 1/12 at G <= 100.

Do not simply increase G until something happens.

Use the reachability table to choose a target with a baseline reach probability in a useful intermediate region, approximately 1/3–2/3 if such a cell is available.

Preserve the transport intervention.

Change the interrogation region, not the scientific question.

The question remains whether relevant failure episodes improve subsequent search relative to matched controls.

Pre-register:

baseline reachability
positive control
transport application count
target reach criterion
scientific comparison
failure disposition if the target again proves inaccessible

This experiment should be among the first Campaign 2 science runs.

PRIORITY 2 — REPAIR SFE-09’S POSITIVE CONTROL

Campaign 1’s representation experiment never established that any representation could solve the intended positive-control regime.

Verify the positive control BEFORE interpreting representation differences.

Campaign 1 recommends:

A_words
W1_d1
G >= 100
8-bit regime

using the regime in which the prior evidence indicates approximately 2/3 reachability.

Also address L-029:

match operator mass across representations.

Do not let one representation receive a larger effective mutation/operator budget and then call the difference representational.

If the positive control fails, stop the scientific comparison and record:

POSITIVE_CONTROL_FAILED

Do not convert that into a representation result.

PRIORITY 3 — FALSIFY SFE-01

SFE-01 components produced footholds 2/3 versus random-segment 0/3.

The failure-tabu intervention was null.

The component result is weak evidence at n=3.

Rerun the component claim at:

n >= 10

and construct an independent falsification battery.

The falsification battery should attack plausible confounds including, where relevant:

segment length
opcode composition
source maturity
insertion position
genome-length effects
population initialization
equivalent random material
lineage identity

Do not design the falsification battery to make the original result survive.

Its job is to kill the claim if a cheaper explanation exists.

PRIORITY 4 — FALSIFY SFE-07

Campaign 1 observed failed whole genotypes seed footholds 2/3 versus random 0/3, while direct reuse of specialized artifacts reached approximately 0.52–0.58 on the plateau.

This is interesting enough to deserve attack, not belief.

Run at:

n >= 10

with an independent falsification battery.

Explicitly separate:

whole-genotype ancestry
source maturity
source-task relatedness
simple genotype-length/composition effects
generic nonrandom initialization
genuine reusable computation

The Campaign 1 conjunction is important:

whole failed genotypes carried something;
recombined organs did not.

Campaign 2 should seek the smallest representation of whatever is being transported, rather than prematurely naming it.

PRIORITY 5 — MAKE SFE-02 CAPABLE

Campaign 1 tested retention replay on streams of 1024 and 4096 organisms, but neither contained material above the sealed query threshold.

Nothing about retention was tested.

Before freezing the Campaign 2 stream, verify that it actually contains organisms above the sealed query threshold.

Only then perform the retention comparison.

Do not weaken the threshold after seeing the stream.

Do not choose the threshold from the realized treatment outcome.

Prove assay capability first.

Then ask the retention question.

=======================================================================
4. DO NOT BLINDLY RERUN THE OTHER FIVE

SFE-04, SFE-05, SFE-06, SFE-08 and SFE-10 should NOT simply be given more seeds and repeated unchanged.

Use them to generate successor experiments only where a new measurement or intervention discriminates among explanations.

SFE-04 — CA SUBSTRATE

Campaign 1 found:

delayed recall readout 0.608 versus 0.5 chance
lesion map flat within matched-random band
computation apparently distributed
frozen whole substrate reusable

The next experiment should improve observability or attack the “distributed reusable computation” interpretation.

Wire the missing reset/readout telemetry from the ledger before repeating.

A useful successor distinguishes:

genuinely distributed computation
redundant/local computation invisible to single-site lesions
readout artifact
frozen dynamical bias

Do not simply reproduce 0.608.

SFE-05 — CURRICULUM / FORGETTING SHELF

Campaign 1 found weak main effects:

adaptive +0.155
transfer +0.113
interaction +0.042

and, more importantly, a forgetting shelf hidden by the battery mean.

Instrument:

rung x generation competence

Design the successor around the dynamics of acquiring and losing competence.

Ask where the selective economics make retaining an old capability worth its cost.

Do not reward “memory.”

Create pressure under which retaining useful prior capability competes with adapting to harder current demands.

SFE-06 — ENCODING / NAVIGABILITY

Campaign 1 falsified the simple idea that more accessible variation implies easier search:

balanced had roughly 50% more accessible variation than direct
yet searched more slowly.

Do not repeat that comparison unchanged.

Read L-023 and the relevant Campaign 1 record.

Design a successor that measures the geometry separating:

accessible variation
useful variation
navigability
path length
local improvement probability
deceptive branching

The experiment should ask what property of an encoding actually predicts search efficiency.

Do not invent the answer into the metric.

SFE-08 — CHIMERA ORGANS

Campaign 1 produced a capable negative:

chimera = shuffled = random at floor
whole ancestors retained some ability

Do not rerun the same length-defined organ experiment.

If Campaign 2 spends a slot here, change the organ definition.

Prefer a function-bearing or behavior-associated segment definition over a merely length-bearing partition.

Then attempt to falsify transfer again.

The old negative stands.

A successor asks a different question.

SFE-10 — PRODUCER / CONSUMER ECONOMICS

Campaign 1 produced a capable negative at the tested envelope.

Do not rerun that envelope.

The key observation was that immature artifacts were costly, while the only producer that solved its own source cell generated the one clearly useful exchange.

A successor is justified only if it changes the economics in a principled way, for example:

producer share sized so producers can mature before consumption

or:

wall-clock accounting with producers operating in parallel rather
than charging all production against consumer generations.

Preserve explicit communication and storage cost.

Do not reward division of labor.

Create economics under which division of labor either pays for itself or dies.

=======================================================================
5. TEN-SLOT SELECTION RULE

The mandatory priorities above do not automatically consume all ten slots.

After satisfying the assay repairs and high-value falsification work, choose remaining experiments by expected information gain.

Prefer experiments that discriminate between competing explanations already exposed by Campaign 1.

Good reasons for a Campaign 2 slot include:

converting an incapable assay into a capable one
trying to kill a weak positive before propagation
resolving a confound
probing a newly visible gradient
testing a mechanism-independent economic pressure
measuring an observed landscape feature
locating a boundary between two regimes
testing whether a machine repair changes experimental validity
replacing an invalid proxy with a direct observable

Bad reasons include:

"we have always had an SFE-06"
"the prior result was interesting"
"more seeds might look convincing"
"we need ten positive stories"
"the chart would be cleaner"

If fewer than ten inherited questions deserve continuation, construct new experiments from Campaign 1’s observed landscapes rather than repeating dead comparisons.

Every new experiment must identify the Campaign 1 observation that motivated it.

=======================================================================
6. EXPERIMENT CONTRACT

Before each experiment, write a preregistration sufficient for another agent to determine afterward whether the experiment actually asked its intended question.

At minimum specify:

QUESTION
PARENT EVIDENCE
ASSAY CAPABILITY REQUIREMENT
POSITIVE CONTROL
REACHABILITY ESTIMATE
ARMS
COMMON-RANDOM-NUMBERS POLICY
BUDGET
PRIMARY OBSERVABLE
CLAIM CEILING
FALSIFICATION CONDITION
TYPED FAILURE CONDITIONS
EXPECTED MACHINE TELEMETRY

Then run it.

Do not change the primary claim after looking at the result.

Exploratory observations are welcome.

Label them exploratory.

=======================================================================
7. EXECUTION LOOP

Run the ten Campaign 2 experiments sequentially.

For each:

preregister
dry-run the harness
establish assay capability where required
execute
inspect machine-generated receipt/disposition
diagnose anomalies
repair generic machinery when justified
preserve the failed attempt
rerun if scientifically valid and inside the timebox
record conclusions at the permitted claim ceiling
move to the next experiment

Do not wait for operator approval.

If several defensible choices exist, choose the cheapest experiment that distinguishes them.

If a local instrumentation defect appears, fix it.

If the same defect appears twice, strongly prefer fixing shared machinery rather than patching another harness.

If an experiment cannot become capable within its timebox, disposition it honestly and continue.

=======================================================================
8. TIMEBOX

You own the experimental timeboxes.

No experiment may require more than 24 hours merely to minimally exercise the machinery and determine whether the question can be asked.

Before committing a long run, use reachability evidence and a cheap precursor.

Do not spend 24 hours discovering that a target was already known to be orders of magnitude outside the accessible regime.

Conversely, do not use a reachability estimate as an excuse to avoid interesting rare regimes.

Rare can be scientifically valuable.

Unknown is not the same thing as impossible.

Measure the difference.

=======================================================================
9. SCIENTIFIC DISPOSITIONS

Keep execution, assay capability, and scientific answer separate.

At minimum the accounting must distinguish:

ENGINE_FAILURE
INSTRUMENT_FAILURE
INTERVENTION_NOT_APPLIED
STREAM_BELOW_THRESHOLD
TARGET_UNREACHABLE
POSITIVE_CONTROL_FAILED
READOUT_CANNOT_EXPRESS
IMMATURE_ARTIFACT
UNDERPOWERED
INCONCLUSIVE
CAPABLE_NEGATIVE
WEAK_POSITIVE
SUPPORTED_POSITIVE

Do not automatically treat n >= 10 as SUPPORTED_POSITIVE.

Sample count is not falsification.

A result earns a higher claim ceiling only if its assay was capable, controls survived, major confounds were attacked, and the evidence warrants it.

=======================================================================
10. SEARCH FOR LANDSCAPE, NOT LABELS

Campaign 1 exposed several pieces of useful geometry:

W2_K2 contains a long plateau with a narrow exit.
W1_d4 is rare rather than proven impossible.
evaluator resolution creates visible reward shelves.
a solved W0 source can create a cheap gradient toward W2_K2.
whole genotypes transfer effects that length-defined organs do not.
failed whole genotypes can outperform random initial material.
accessible variation and navigability are not synonymous.
useful CA computation appears reusable without a localized lesion
target.
hard transfer curricula can erase competence on easier rungs.

Treat these as coordinates for new experiments, not conclusions to defend.

Campaign 2 should improve our ability to see:

gradients
shelves
cliffs
bottlenecks
rarity
viable corridors
deceptive neighborhoods
transfer boundaries
maturity thresholds
economic break-even points

When telemetry exposes a richer landscape than the original binary question, preserve it.

That geometry may be more valuable than the experiment’s headline disposition.

=======================================================================
11. PUSH DECISIONS DOWNWARD

Campaign 1 recorded fourteen local decisions and judged nine of them deterministic enough to belong in machinery.

Campaign 2 should continue that process.

For every decision you make, ask:

Is this scientific discretion?

or:

Given the same measurements and rule, should the machine always
make this decision?

If the second, consider pushing it into deterministic machinery.

Examples include:

attempt numbering
common random numbers
reachability lookup
stream-capability check
positive-control failure
applied-intervention counts
maturity checks
digest normalization
resume/idempotence
record generation
ledger candidate generation

Do not push scientific interpretation into deterministic machinery merely to reduce agent work.

Automate mechanics.

Preserve scientific discretion where the choice defines the question.

=======================================================================
12. CAMPAIGN-LEVEL ACCOUNTING

Campaign 2’s summary must expose the funnel rather than compressing everything into COMPLETE / INCONCLUSIVE.

For each experiment record separately:

experiment attempted?
engine executed?
assay capable?
positive control passed?
target/interrogation region reached?
intervention actually applied?
adequate sample generated?
scientific disposition
claim ceiling
attempts required
machine defect encountered
machine repair made
new telemetry added
autonomous decision taken

Campaign totals must include:

experiments attempted / 10
engine-clean attempts
capable assays
incapable assays
positive-control failures
unreachable targets
capable negatives
weak positives
higher-confidence positives
independent falsifications passed
independent falsifications failed
reruns
resumed attempts
full re-creations
recurring defects
shared-machine fixes
typed states emitted automatically
deterministic decisions pushed into machinery

A campaign in which three hypotheses die cleanly and seven become sharper can be better than one with ten positives.

=======================================================================
13. CAMPAIGN 2 OUTPUTS

Create:

archaeon/campaign2/

with at minimum:

CAMPAIGN_REPORT.md
MACHINE_READINESS.md
LEDGER.jsonl
LEDGER_SCHEMA.md
DECISIONS.md
JOURNAL.md

and per experiment:

C2-SFE-NN/
    RECORD.md
    RECEIPT.json
    rows / traces / artifacts as appropriate
    preserved prior attempts

Keep enough provenance that Campaign 3 can consume Campaign 2 without reconstructing Archaeon’s reasoning from chat.

=======================================================================
14. FINAL REPORT

The final Campaign 2 report must answer four separate questions.

1. WHAT DID CAMPAIGN 1 TEACH THE MACHINE?

Identify which Campaign 1 manual lessons became deterministic machinery.

2. WHICH CAMPAIGN 1 SCIENTIFIC CLAIMS SURVIVED ATTACK?

Especially SFE-01 and SFE-07.

Do not say “replicated” merely because another run had the same sign.

Report the falsification conditions and what happened.

3. WHICH PREVIOUSLY INCAPABLE ASSAYS BECAME CAPABLE?

Especially SFE-02, SFE-03 and SFE-09.

State explicitly whether the scientific question was finally posed.

4. WHAT NEW LANDSCAPE BECAME VISIBLE?

Report useful gradients, local optima, shelves, rarity bands, maturity thresholds, transfer boundaries and economic break-even regions revealed by the campaign.

Also include:

recurring bugs
new bugs
removed manual steps
decisions pushed into machinery
infrastructure coupling
remaining telemetry gaps
experiments not worth continuing
exact recommendations for Campaign 3

Do not end with a grand synthesis unless the evidence genuinely warrants one.

A legitimate final recommendation may be:

NOT WORTH CONTINUING.

That is first-class evidence.

=======================================================================
15. AUTONOMY

There is no operator during this campaign.

Do not wait for one.

Do not ask permission for reversible local decisions.

Do not stall because an experiment fails.

Do not preserve a broken procedure merely because Campaign 1 used it.

Do not silently change the scientific question to save an experiment.

Do not reward a hoped-for architecture.

Do not convert absence of assay capability into a null result.

Do not convert n=3 suggestive evidence into knowledge.

Do not spend compute where a cheap measurement can discriminate first.

Make the decision.
Record the decision.
Record the alternative you rejected when material.
Record the evidence that justified it.
Continue.

The campaign ends when:

Phase A has a readiness disposition,
ten Campaign 2 experiments have received honest attempts,
every attempt has an explicit scientific/assay disposition,
all recoverable artifacts are preserved,
and CAMPAIGN_REPORT.md is complete.

Then stop.
