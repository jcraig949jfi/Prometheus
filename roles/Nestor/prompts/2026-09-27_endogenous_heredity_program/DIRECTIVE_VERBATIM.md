NESTOR — ENDOGENOUS HEREDITY AND REPRODUCTIVE MACHINERY FRONTIER PROGRAM

W1 is accepted as a completed research window.

Merge the W1 branch into main using the normal integrity-preserving procedure.

Then begin this multi-hour research program.

Do not return after one experiment.

The scientific territory is:

ENDOGENOUS HEREDITY AND REPRODUCTIVE MACHINERY

W1 established two distinct barriers in the current NPE setting:

1. ACQUISITION
    Useful copying capability is difficult to reach from random material.
    Making block-copy easier to encode strongly increases donor acquisition.
2. ESTABLISHMENT
    Possessing a competent donor genome is not sufficient.
    In at least the ffa6 cell class, persistent execution state strongly
    suppresses establishment.

The current path is therefore better represented as something like:

variation
  -> acquisition of useful copying machinery
  -> causal copying
  -> establishment
  -> descendant competence
  -> sustained heredity
  -> further adaptation

Do not assume those are the only barriers.

Do not assume they are independent.

Do not assume NPE’s current representation exposes all of them.

Your job is to deepen this map, connect it to external research, create a large research backlog, execute a bounded number of discriminating experiments, and prepare substantial work for other researchers.

The operator should remain outside routine scientific decisions.

⸻

RESOURCE LEASE REQUIREMENT

Before launching substantial engine compute, reserve the required machine resources using the program’s existing lease mechanism.

This includes work that materially occupies:

* CPU cores;
* GPU;
* RAM;
* or another scarce shared resource.

The lease should identify:

* host;
* resource envelope;
* owning seat/work;
* intended duration or expiry.

Do not reserve more than the experiment needs.

Release the lease promptly when:

* the run ends;
* the run crashes and will not immediately restart;
* the scientific branch is abandoned.

Confirm existing host load before starting.

Tiny probes, literature work, repository analysis, and lightweight deterministic checks do not require a heavy-compute lease.

Do not invent a new general lease bureaucracy if the existing mechanism is sufficient.

The purpose is collision avoidance, not permission seeking.

⸻

BLOCK A — ADVERSARIAL REVIEW OF W1

Treat W1 as a submitted paper.

Attack the two headline mechanism claims.

ACQUISITION

Current interpretation:

donor acquisition is limited by accessibility of copying machinery.

Challenge alternatives such as:

* the 1-byte encoding changes more than accessibility;
* changed instruction density affects unrelated dynamics;
* block-copy presence interacts with mutation structure;
* acquisition depends on particular neighboring instructions;
* some other feature correlated with the encoding is causal.

Ask what intervention would distinguish:

easy to discover

from

intrinsically more effective once discovered.

ESTABLISHMENT

Current interpretation:

persistent register state can create self-poisoning that blocks establishment in ffa6.

Challenge:

* genome-specific interactions;
* cell-specific state semantics;
* initial-condition artifacts;
* execution order;
* state reset frequency;
* register subset effects;
* partner interactions;
* hidden environmental dependence.

Do not generalize ffa6 to NPE globally.

The 7ae3 null is part of the result.

⸻

BLOCK B — WHY FFA6 BUT NOT 7AE3?

This is the highest-value immediate mechanistic question.

Determine what property changes the effect.

Work one variable at a time where feasible.

Potential differences may include:

* instruction composition;
* register usage;
* execution ordering;
* mutation topology;
* copy direction;
* tape position;
* partner interaction;
* donor architecture;
* environmental context.

Prefer a causal bridge between the two cells rather than merely comparing them descriptively.

Examples:

* transplant one relevant mechanism from ffa6 into 7ae3;
* swap register-reset behavior;
* alter only the implicated register subset;
* transplant donor architecture while holding environment fixed.

Use bounded experiments.

The goal is not to create a taxonomy of cell differences.

The goal is to identify why persistent state becomes an establishment barrier in one context and not another.

⸻

BLOCK C — CHARACTERIZE SELF-POISONING

W1 observed:

* 18/18 stalled donors copy from fresh state;
* after one self-execution they copy at 0.0;
* approximately half of established donors also exhibit the same phenomenon.

Therefore self-poisoning is not a sufficient explanation by itself.

Find out what differentiates:

self-poisoning but successful

from

self-poisoning and stalled.

Potential questions:

* Does successful reproduction happen before poisoning?
* Can a descendant reset or overwrite the bad state?
* Is poisoning reversible?
* Which registers matter?
* Does copy order matter?
* Does one execution create the poison or several?
* Is the poison a side effect of the copying machinery itself?

Prefer interventions that alter one mechanism.

A useful result may be that “self-poisoning” is merely a descriptive symptom rather than a causal class.

⸻

BLOCK D — COPIERS THAT DO NOT LOCATE THEMSELVES

W1 found a spontaneous specimen using LDIR/LDDR plus leftover register values without explicitly locating itself.

Treat this as a potentially important architecture, but do not elevate one specimen into a general phenomenon.

Investigate:

* how the copier acquires usable address/state;
* what environmental assumptions it exploits;
* whether the mechanism is robust;
* whether descendants preserve it;
* whether similar architectures arose elsewhere;
* whether it represents a shorter evolutionary path than explicit self-location.

Ask:

Can reproduction exploit inherited/environmental computational context instead of encoding all reproductive machinery in the genome?

That question may connect to several other Prometheus engines.

Preserve it as a broader Thread if warranted.

⸻

BLOCK E — DESCENDANT COMPETENCE

W1’s establishment endpoint currently lumps later stages together.

Separate them where practical.

A donor can potentially:

1. create a copy;
2. create a structurally correct copy;
3. create a copy that can itself execute;
4. create a copy that can itself copy;
5. establish repeated heredity.

Design the smallest useful assays that distinguish these.

Do not immediately construct a large reproductive-success ruler.

The objective is to locate where heredity fails.

A mechanistically useful result might be:

copying succeeds, but the child inherits unusable state.

or:

the child is competent but never reaches the right execution context.

Those are very different scientific failures.

⸻

BLOCK F — REMOVE THE AIDS

W1 used two explicit aids:

* shortened access to block-copy;
* fresh execution state.

Do not simply remove both and ask whether evolution succeeds.

Treat the aids as causal probes.

Ask separately:

CAN EVOLUTION DISCOVER ACCESSIBILITY?

Can evolution itself find shorter/easier encodings or equivalent mechanisms without the artificial 1-byte block-copy encoding?

CAN EVOLUTION DISCOVER STATE ROBUSTNESS?

Can genomes evolve machinery that tolerates, resets, exploits or avoids persistent state without the stateless intervention?

Look for intermediate adaptations.

The important question is not simply whether the aid becomes unnecessary.

It is whether the system can modify the relevant machinery to overcome the barrier endogenously.

That is much closer to the North Star.

⸻

BLOCK G — EXTERNAL RESEARCH RAID

Conduct substantial prior-art research around:

* self-reproducing programs;
* von Neumann constructors;
* Tierra;
* Avida;
* Core War;
* symbiogenesis / hypercycles where relevant;
* digital evolution;
* quines and self-reference;
* endogenous replication;
* replication error thresholds;
* evolvability;
* genotype/phenotype mapping;
* developmental state;
* maternal effects;
* epigenetic inheritance;
* stateful automata;
* inherited execution context;
* bootstrapping;
* self-hosting systems;
* origin-of-life replication barriers;
* autocatalytic sets;
* open-ended evolution.

Also search modern work.

For each useful line ask:

1. What counts as a reproducer?
2. What machinery is supplied by the environment?
3. What has to be encoded by the reproducer?
4. What state passes outside the nominal genome?
5. What are the known establishment barriers?
6. How is descendant competence measured?
7. What evolutionary stepping stones are known?
8. Which assumptions would NPE violate?

Do not import biological language merely because it is familiar.

Prior art should expose missing experiments and known failure modes.

⸻

BLOCK H — CROSS-ENGINE CONNECTIONS

Search other Prometheus engines for mechanisms genuinely related to NPE’s barrier map.

Potential examples:

* BEE reproductive machinery;
* Archaeon’s WHO/WHERE/WHAT distinctions;
* Aphrodite’s accessibility-versus-representability result;
* Ananke’s distributed carriers;
* Aether’s dynamical state;
* Cosmos’s environmental coupling.

Do not produce analogies for their own sake.

Look for actual shared scientific structures such as:

ACCESSIBLE VS REPRESENTABLE

A mechanism can exist in the language but be practically unreachable.

GENOME VS EXECUTION STATE

Nominal hereditary material may not determine reproductive competence by itself.

ENVIRONMENT AS MACHINERY

A reproducer may outsource essential structure to its context.

ACQUISITION VS ESTABLISHMENT

Producing a candidate and sustaining it are different problems.

Create cross-engine Threads where a real comparison could discriminate something.

⸻

BLOCK I — BUILD THE NESTOR BACKLOG

Create a substantial backlog around:

* acquisition of reproductive machinery;
* establishment;
* descendant competence;
* sustained heredity;
* state robustness;
* genome/context boundaries;
* reproductive architecture;
* self-location;
* environmental scaffolding;
* evolvability of copying machinery;
* transition from aided to endogenous replication.

There may be dozens of legitimate Threads.

Do not reduce them merely because current compute is limited.

For each strong Thread capture:

QUESTION

WHY IT MATTERS

EXISTING EVIDENCE

PRIOR ART

UNCERTAINTY

CHEAPEST DISCRIMINATOR

SUITABLE LENS

RESOURCE CLASS

For example:

* repo/literature only;
* light CPU;
* leased CPU;
* GPU;
* multi-host;
* new engine/lens.

The resource field is descriptive and useful for dispatch.

It is not a permission system.

⸻

BLOCK J — PREPARE RESEARCH-READY WORK

Turn several mature Threads into self-contained work packages.

A fresh researcher should be able to take one from Git and work for hours.

Good candidates may include:

* ffa6 versus 7ae3 establishment;
* self-poisoning successful versus stalled;
* non-self-locating copiers;
* descendant competence decomposition;
* endogenous recovery from the two W1 aids;
* external replication-barrier synthesis.

Do not execute everything personally.

Create research inventory for additional agents and machines.

⸻

BLOCK K — DELEGATE NON-COMPUTE WORK

Use subordinate researchers for:

* literature;
* repo archaeology;
* cross-engine comparison;
* existing-data analysis;
* theoretical work.

Do not occupy the NPE compute host with work that can be done elsewhere.

Give delegates questions, not desired conclusions.

Keep the mechanistic synthesis yourself.

⸻

BLOCK L — RUN A BOUNDED COMPUTE PROGRAM

After Blocks A–J have sharpened the frontier, select a small number of high-information experiments.

Reserve resource leases before heavy runs.

Use NPE compute where the experiment actually requires it.

Do not fill the machine merely because a lease exists.

Prefer experiments that discriminate mechanisms rather than collect more examples.

Good candidates are likely to include:

* ffa6/7ae3 causal bridge;
* successful-versus-stalled self-poisoning;
* descendant competence localization.

But allow earlier analysis to change the choice.

⸻

BLOCK M — AVOID BINARY “REPLICATION” THINKING

Do not treat reproduction as a single event.

W1 suggests a chain of bottlenecks.

Develop the minimum useful causal decomposition.

Potential stages:

variation
  -> machinery becomes accessible
  -> candidate donor exists
  -> copying is physically possible
  -> copying happens in context
  -> descendant is competent
  -> descendant reproduces
  -> lineage persists
  -> machinery adapts

Not all stages need to survive.

Use this only where experiments can distinguish them.

The purpose is to stop one ruler from collapsing several causal failures into “didn’t replicate.”

⸻

BLOCK N — NORTH-STAR QUESTION

Repeatedly ask:

Can the system itself modify the machinery or context responsible for crossing these barriers?

An externally supplied easy opcode is informative as a causal probe.

A fresh-state intervention is informative as a causal probe.

Neither is the North-Star result.

The deeper result would be endogenous discovery of:

* a more accessible copying method;
* state-robust reproductive machinery;
* environmental scaffolding;
* architectural changes that improve descendant competence;
* machinery that modifies its own future evolvability.

Look for evidence of such transitions without engineering them into existence.

⸻

BLOCK O — BACKLOG FEEDBACK LOOP

As experiments run, update the backlog.

A null may:

* kill a Thread;
* split a Thread;
* create an instrumentation Thread;
* reveal a different barrier;
* make another old question newly tractable.

Do not preserve questions ceremonially.

Do not treat the backlog as immutable.

It should evolve continuously with the evidence.

⸻

BLOCK P — HITL COMPRESSION

Resolve routine choices yourself.

Do not send the operator every experimental fork.

Return operator attention only for:

* scientific-direction choices;
* substantial new resource commitments;
* destructive/irreversible changes;
* engine-level redesign;
* competing directions whose choice depends on program values.

At the end report:

WHAT CHANGED

WHAT WAS FALSIFIED

WHAT MECHANISMS NOW LOOK REAL

WHAT EXTERNAL RESEARCH CHANGED

WHAT NEW THREADS EXIST

WHAT OTHER AGENTS CAN RUN

WHAT HEAVY COMPUTE IS JUSTIFIED NEXT

WHAT ACTUALLY REQUIRES HITL

If nothing requires operator intervention, say so.

⸻

FINAL DELIVERABLE

Return one integrated synthesis containing:

1. adversarial review of W1;
2. explanation of ffa6 versus 7ae3 if resolved;
3. self-poisoning analysis;
4. non-self-locating copier analysis;
5. descendant-competence decomposition;
6. external replication/heredity research;
7. cross-engine connections;
8. NPE engine/lens implications;
9. durable backlog;
10. research-ready work packages;
11. bounded experiments executed;
12. resource leases used and released;
13. important nulls and withdrawn interpretations;
14. candidate endogenous transitions;
15. what can proceed without another operator interaction.

Do not return because one confirmation finished.

Complete a coherent research arc.

The goal is not to produce more replicators.

The goal is to understand the physical and computational barriers separating random variation from sustained endogenous heredity, and to determine whether those barriers themselves can become objects of evolution.
