PROMETHEUS / ARCHAEON CAMPAIGN 4

DAMAGE GEOMETRY AND EVOLVABILITY

Campaign state: READY_TO_PREREGISTER; execution begins automatically only after the launch gate below is green.

Lead: Archaeon
Execution: Vivarium
Engine: frozen SFE 9.0.1 surface
Identity / structure: Proteus frozen Campaign-4 surface
Observer / projections: PEW, observer only
Adjudication: Harmonia where a preregistered comparison requires it

There is no operator and no HITL during the campaign.

The lead proceeds through all ten experiments sequentially. It may make bounded, reversible implementation decisions required to execute the preregistered experiment, but it may not rescue a scientific hypothesis by changing the question after seeing the result.

Every experiment receives an attempted disposition.

If the minimum experiment necessary to exercise a hypothesis is credibly estimated to require more than 24 hours, record SKIPPED_RESOURCE_BOUND with the estimate and continue.

Harness or infrastructure defects may be repaired and the same experiment rerun. Preserve every failed attempt beside the repaired attempt.

Do not silently convert a scientific failure into an engineering task.

⸻

0. CAMPAIGN QUESTION

Previous campaigns repeatedly encountered a boundary where mutations cease to produce informative phenotypes and instead produce unreachable summits, inert shelves, execution failures, or mechanically invalid organisms.

Campaign 4 asks:

Can the Foundry expose a region in which mutations usually produce different, bounded, coherent computation rather than either no change or catastrophic failure—and does access to that region improve subsequent evolutionary discovery?

The target is NOT robustness by itself.

A substrate full of harmless NOPs that produces nothing new is a failure.

The target is also NOT immediate task fitness.

The target is heritable computational variation that remains executable long enough for selection, transfer, recombination, or further mutation to operate on it.

Call this property:

COMPUTATIONAL MUTATIONAL LOCALITY

Campaign 4 must distinguish at least:

GENOTYPE CHANGE
→ DECODABLE
→ EXECUTABLE
→ BOUNDED
→ BEHAVIORALLY DISTINCT
→ VIABLE
→ TRANSFERABLE / RECOMBINABLE
→ USEFUL DESCENDANT

Do not collapse the first several states into FAILED.

⸻

1. LAUNCH GATE — NOT A SCIENCE EXPERIMENT

Execution REFUSES until the machine-readable readiness check can prove the following against the frozen surfaces.

Daedalus / SFE

Campaign-rate long-run measurement on 9.0.1 has completed with no 5xx and no unexplained >5 s calls; WAL behavior is bounded or explicitly accepted for the intended campaign rate; crash/restart recovery has been measured.

Archaeon + Vivarium

One synthetic Campaign-4-shaped specimen has traveled:

producer declaration
→ population manifest
→ Vivarium execution
→ keyed engine actions
→ forced engine interruption/restart
→ retry/resume
→ exactly-once-or-proven-replay observations
→ artifact publication
→ PEW ingestion
→ projection rebuild
→ reproducible terminal receipt.

Vivarium

The Campaign-4 consumer identity is live and its M2 B1 read grant is valid.

PEW

If its writer credential is available, drain the Vivarium outbox before launch. If not, Campaign 4 may execute because the outbox is durable, but the final campaign disposition may not claim complete PEW closure until the backlog is delivered.

Proteus

Campaign population manifests and structural descriptors exist for the exact Campaign-4 starting organisms. No organism of unknown ancestry enters an experimental arm.

Once green, freeze the readiness receipt and begin C4-01 without asking the operator.

⸻

2. COMMON DAMAGE TAXONOMY

Every mutated offspring in this campaign should receive the most specific observable classification that evidence permits:

D0 — UNDECODABLE
Representation cannot be interpreted.

D1 — EXECUTION_FAULT
Decoded, but execution terminates through an invalid operation or equivalent fatal substrate event.

D2 — DEGENERATE
Bounded execution occurs but behavior collapses into trivial/no-op behavior.

D3 — DISTINCT_NONVIABLE
Produces measurable behavior different from the parent but cannot satisfy the world's viability floor.

D4 — VIABLE_WORSE
Retains coherent behavior and viability while losing current task performance.

D5 — NEUTRAL
Behavior remains within the preregistered equivalence band for the current task.

D6 — EXAPTIVE
Inferior or neutral in the parent environment but measurably useful in another preregistered environment.

D7 — IMPROVED_OR_NOVEL
Produces improved or newly successful external behavior.

Keep raw observations underneath these labels. The label is not the evidence.

For every condition record at minimum:

decode fraction; execution fraction; bounded fraction; fatal fraction; degenerate fraction; neutral fraction; non-neutral behavioral yield; behavioral displacement from parent; current-task retention; cross-world usefulness; lineage survival; descendant production; compute/energy cost; mutation description; structural descriptor before/after.

Never reward a D-category directly.

⸻

3. EXPERIMENTS

C4-01 — DAMAGE-BOUNDARY CENSUS

Question

Where does the current frozen substrate actually destroy variation?

Method

Take a fixed, manifest-backed sample of Campaign-4 parents spanning the existing structural population.

Generate a preregistered set of small mutations using the existing grammar and current mutation operators.

Do not select them.

Execute all of them through the ordinary stack and classify their outcomes D0-D7.

Stratify by mutation operator and structural region.

Primary output

A measured flow diagram from mutation to outcome rather than a single survivor/failure count.

Estimate:

P(Dk | mutation class, parent structure)

and the distribution of behavioral displacement conditional on surviving execution.

Why

This establishes the actual damage boundary before trying to improve it.

Falsifying outcome

Nearly all mutation classes show the same result distribution, or the instrumentation cannot distinguish where loss occurs.

Do not "fix" that during C4-01. Record it.

⸻

C4-02 — MUTATION-RADIUS RESPONSE CURVE

Question

Does genotypic distance have any usable relationship to behavioral distance?

Method

Using matched parents and seeds, generate mutation radii such as:

1 elementary edit
2 edits
4 edits
8 edits
and one larger preregistered radius that remains cheap.

Use the frozen grammar mass machinery. Do not tune the radius after seeing results.

Measure:

D(delta) = behavioral_distance(parent, child)

conditional on decode/execution, plus catastrophic probability at each delta.

Desired landscape

Not necessarily smooth.

What matters is whether there exists a region between:

"nothing changes"

and

"everything dies."

Failure shapes to preserve

flat-neutral, cliff, exploding variance, parent-specific islands, operator-specific islands, and complete catastrophe.

This replaces further blind attacks on the old hard summit.

⸻

C4-03 — LOCAL FAILURE VS GLOBAL DEATH

Question

When one mutated operation becomes invalid, is evolutionary search better served by killing the organism or by localizing the failure?

Matched conditions

HARD: current fatal behavior.

FIZZLE: the invalid operation alone produces no effect and execution continues.

Use the same parent, same mutation, same seed, same world, and same budget in each condition.

The FIZZLE rule must remain mechanically simple. It may not infer intent, repair the program, substitute a useful value, or inspect the task.

Measure

How much probability mass moves:

D0/D1 → D2
D0/D1 → D3-D7

The second movement is the important one.

Critical distinction

If FIZZLE merely converts fatal organisms into inert organisms, it has not improved evolvability.

Support requires

an increase in coherent, nontrivial behavioral variation—not merely survival.

⸻

C4-04 — ADDRESSING DAMAGE

Question

How much brittleness comes specifically from references that are destroyed by insertion, deletion, or displacement?

Conditions

Compare the closest available implementations of:

position/index-sensitive reference semantics

versus

relational, structural, template, or otherwise locally recoverable reference semantics.

Do not add a reasoning primitive.

Do not let the alternative addressing mode search for the "correct" target.

It may only alter how a reference resolves under structural perturbation.

Use identical structural insertion/deletion mutations.

Measure

reference-resolution success, fatal rate, retained behavior, behavioral displacement, and novel behaviors.

Disposition

If the frozen substrate cannot express a legitimate relational-address condition without introducing a new primitive, record:

REPRESENTATION_BLOCKED

That is a scientific result. Do not mutate the ISA during the campaign.

⸻

C4-05 — NEUTRAL-NETWORK WALK

Question

Can lineages move through genotype space while preserving current competence, and does such movement expose new reachable behaviors?

Method

From matched parents, perform bounded neutral walks.

A step may continue only when the offspring remains inside the preregistered current-task equivalence band.

Do not select for the later challenge.

After depths such as 0, 2, 4, 8, and the largest cheap preregistered depth, expose archived walkers to a held-out challenge suite.

Track structural divergence even when current fitness is unchanged.

Measure

connected neutral depth, structural diversity accumulated under neutrality, later behavioral diversity, and held-out exaptation.

Failure

A large neutral network that yields no additional later behavior is a neutral swamp, not success.

This replaces repeated measurement of the old flat shelf with a direct test of whether the shelf has traversable internal structure.

⸻

C4-06 — LATENT STRUCTURE, RECOMBINATION, AND VALLEY CROSSING

Question

Can separately accumulated neutral or weakly viable changes combine into capabilities that ordinary one-step search rarely reaches?

Method

Create matched lineages from C4-05 or equivalent fresh preregistered neutral walks.

Compare equal-budget search using:

ordinary mutation only

versus

the existing recombination machinery over independently drifted viable lineages.

Use a challenge for which the starting population does not already contain the successful behavior.

Do not reward intermediate architecture.

Do not reveal a desired motif to the organisms.

Measure

viable offspring yield, catastrophic recombinants, structural novelty, held-out behavioral novelty, and successful multi-generation crossings.

Key question

Does recombination turn accumulated latent structure into useful computation, or does it simply multiply damage?

⸻

C4-07 — THE COST OF INSULATION

Question

Is graceful degradation useful only when it is free, and if so does it collapse into neutrality?

Method

Take the most informative local-insulation condition from C4-03.

Run matched worlds in which invoking the insulating behavior carries preregistered resource costs:

free
small cost
moderate cost
high cost

Cost only the recovery/fizzle event itself.

Do not reward avoiding it.

Measure

fatal rate, degenerate rate, neutral rate, viable novelty, descendant depth, compute consumed, and useful behavior per unit resource.

Desired observation

A frontier may exist where enough insulation preserves evolutionary paths while enough cost prevents organisms from living indefinitely on meaningless failures.

The campaign must be willing to find that no such frontier exists.

⸻

C4-08 — CAN ROBUSTNESS BE CONSTRUCTED RATHER THAN GIVEN?

Question

When free semantic insulation is removed, can selection assemble structures that move their own effective damage boundary?

Method

Use only primitives and affordances already present in the frozen Campaign-4 substrate.

Do not add checksums, retry, redundancy, typing, validation, indirection, or error correction merely because those are mechanisms humans expect.

Expose lineages to repeated ordinary computational pressure plus a preregistered perturbation regime.

Use Proteus structural descriptors to identify repeated structural changes only after behavior has been measured.

Ablate suspected structures prospectively where possible.

Compare

ancestral population

versus

descendants produced under perturbation

under the SAME fresh mutation assay from C4-01.

Question

Have descendants changed their own D0-D7 transition probabilities?

Strong evidence

requires both:

greater survival of useful computation under fresh perturbation

and

an intervention showing that an evolved structural difference contributes to that effect.

Mere duplication or larger genomes are not explanations.

This absorbs the former selection-vs-construction slot.

⸻

C4-09 — LATERAL EXAPTATION / PAIRED ECOLOGY

Question

Are we destroying useful stepping stones merely because they are bad at the environment that produced their parent?

Method

Maintain a small preregistered ecology of cheap related worlds.

A new mutant is first evaluated normally in its parent world.

Before a coherent D3-D5 mutant is discarded, evaluate it against the other worlds using a bounded fixed transfer budget.

A mutant may enter another lineage only because of measured behavior there.

No classifier may predict that it "looks promising."

If affordable, permit new neighboring worlds to be generated only by a frozen rule from already viable worlds, with explicit too-easy and too-hard rejection bounds.

Control

matched search in which parent-world failure ends the lineage immediately.

Measure

rescued lineages, genuine cross-world improvements, transfer direction, later descendants, novelty, and total extra compute.

Failure

If almost every rescue is merely permissive survival with no downstream consequence, lateral evaluation is overhead, not a stepping-stone mechanism.

This is the campaign's POET-like test without assuming that POET is the answer.

⸻

C4-10 — HELD-OUT EVOLVABILITY TRIAL

This is the decisive experiment.

Do not choose its conditions until C4-01 through C4-09 are complete, but the selection rule must be preregistered now.

Select at most TWO Campaign-4 conditions solely from preregistered mechanistic evidence:

they must decrease catastrophic loss AND increase nontrivial viable variation relative to the frozen baseline.

Do not select a condition merely because it achieved the best task score.

Compare those conditions with the original frozen baseline on a HELD-OUT family of cheap worlds not used to develop the Campaign-4 interventions.

Same starting population class.
Same mutation budget.
Same execution budget.
Same number of independent seeds.
Same selection algorithm.
No manual rescue.

Measure:

fatal mutation mass

nontrivial executable phenotype yield

behavioral diversity

lineage depth

cross-world transfer

successful recombination

novel held-out capability

compute cost

and the number of useful descendants produced per unit mutation budget.

Campaign claim

Campaign 4 may claim evidence for improved computational mutational locality only if the held-out trial shows all three:

1. less computation is lost at the damage boundary;
2. the recovered mass contains more nontrivial behavioral variation rather than merely more NOP-like neutrality;
3. the extra variation leads to greater downstream evolutionary reach under equal budget.

If only 1 is true:

ROBUST_BUT_INERT

If 1 and 2 are true but not 3:

LOCALITY_WITHOUT_EVOLVABILITY

If 3 appears without 1 or 2:

do not attribute it to damage-boundary repair.

If all three appear:

SUPPORTED_DAMAGE_GEOMETRY_EFFECT

Preserve the baseline regardless.

⸻

4. WHAT CAMPAIGN 4 DELIBERATELY RETIRES

Do not spend another campaign slot merely repeating:

a harder version of the two-value summit;

another flat shelf with only a longer horizon;

another basin causal test without new geometry;

another CA mechanism test simply because the prior one failed;

another safe-import/takeover experiment whose main behavior is mechanical import bookkeeping.

Those failures remain fossils.

Campaign 4 uses what they taught us: when a world returns only DEAD/UNREACHABLE, move sideways and measure the boundary rather than hitting the wall harder.

Reader anatomy is likewise no longer a standalone science experiment. It is infrastructure for C4-01 and C4-08.

⸻

5. CAMPAIGN DISCIPLINE

Every experiment must publish enough information for an external reviewer to reconstruct:

starting population identity and manifest;

foundry profile;

runtime/grammar/affordance hashes;

world definition and hash;

mutation manifests;

seed schedule;

budgets;

all D0-D7 outcomes;

behavior descriptors before and after mutation;

lineage and parentage;

execution attempts and replay status;

structural descriptors;

interventions/ablations;

termination reason;

wall time and resource use;

PEW/SFE/Vivarium identifiers;

and the exact reason for the experiment's disposition.

Required terminal dispositions include at least:

SUPPORTED
NEGATIVE
INCONCLUSIVE
REPRESENTATION_BLOCKED
INSTRUMENT_INVALID
SKIPPED_RESOURCE_BOUND

Do not convert REPRESENTATION_BLOCKED into a substrate modification during this campaign.

No new ISA primitive enters Campaign 4.

No world or interpreter is allowed to contain a recognizer for the hoped-for solution.

No reward term names robustness, memory, indirection, redundancy, repair, neutrality, evolvability, or a desired architecture.

External behavior and resource economics remain the selection surface.

⸻

6. CAMPAIGN-LEVEL OUTPUT

At the end, publish one compact DAMAGE GEOMETRY MAP.

For every tested substrate/environment condition it should show:

mutation magnitude
→ probability of fatal loss
→ probability of degeneracy
→ probability of neutrality
→ probability of coherent behavioral displacement
→ probability of viability
→ probability of exaptation
→ eventual descendant consequence.

The primary scientific product is not "which safety rail won."

It is a map of:

where evolutionary computation can move, where it cannot move, and whether widening the traversable region actually creates new reasoning machinery.

Then stop.

Do not automatically build Campaign 5.

Campaign 5 should be derived from whichever part of that geometry proves real.
