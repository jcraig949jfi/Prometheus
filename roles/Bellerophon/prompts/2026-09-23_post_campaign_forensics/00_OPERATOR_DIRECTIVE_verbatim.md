# Operator directive (verbatim, 2026-09-23)

You are Bellerophon, responsible for the Z80 × Atlas emergence substrate and campaign harness.

Your immediate job is not to launch another extended campaign.

Your job is to thoroughly mine the completed campaign, identify which apparent phenomena are real versus detector/substrate artifacts, repair any defects uncovered, and then run a bounded grounding round designed to confirm that the system is scientifically and operationally ready for the next multi-day campaign.

Work autonomously. Use subagents where useful for independent analysis, code review, statistics, adversarial review, and specimen reconstruction. Do not optimize for speed. Preserve evidence and provenance.

Repository and evidence

Repository:

https://github.com/jcraig949jfi/Prometheus

Important commits:

commit	significance
98b2149a7	Bellerophon: original Z80 × Atlas harness under prometheus/z80atlas/
2df98af3e	Bellerophon STATUS: campaign LIVE
d50f5710a	Archaeon Z80 × Atlas campaign complete; CAMPAIGN_PACKET + review packet
bcb9f22ad	Merge of archaeon/wse-2026-09-16; Archaeon closing / P-boom readout
3b407946e	Nestor closing commit at 72-hour boundary

The actual final Bellerophon runtime packet was never committed. It is local campaign evidence:

C:/Users/James/z80atlas_campaign_2026-09-19/CAMPAIGN_PACKET.md

Treat that file and the associated campaign workdir as authoritative runtime evidence. Do not mistake the previously discussed 44.6-hour snapshot for the completed run.

Before doing scientific interpretation, locate and inventory the entire corresponding campaign workdir: raw observations, summaries, checkpoints, lineage traces, flag records, replay material, seeds, configuration, environment fingerprints, and any logs required to reproduce conclusions.

Do not commit huge runtime state merely to preserve it. If evidence is too large for Git, create compact manifests/digests/derived tables and record exact source paths and hashes.

Primary objective

Answer this question:

What did the completed Bellerophon campaign actually discover, what remains only a detector candidate, what defects or confounds can explain the signals, and is the substrate sufficiently grounded for another multi-day campaign?

The standard is causal and reproducible evidence, not impressive flag counts.

⸻

PHASE 1 — Reconstruct the campaign exactly

Start by reconstructing the final campaign rather than trusting summaries.

Produce a complete campaign census including at minimum:

* elapsed wall time;
* submitted/completed/failed/voided runs;
* families and unique initial conditions;
* promotion counts and promotion lineage;
* factor/cell coverage;
* task-family coverage;
* topology coverage;
* mutation regimes;
* seed coverage;
* stage transitions;
* checkpoint/restart events;
* worker interruptions;
* duplicate or replayed work;
* every detector/flag class;
* number of unique flagged runs versus total flag events;
* overlap matrix between flag classes;
* temporal appearance of each flag class;
* distribution across tasks, topology, seed, genotype family, mutation regime, and campaign stage.

Explicitly reconcile all earlier snapshots against the final packet.

If any previously quoted number differs from the final evidence, explain exactly why.

Do not pool correlated events as independent samples.

Identify the true experimental unit for every statistical claim.

⸻

PHASE 2 — Mine the data much harder than the original closeout

The campaign generated far more information than the headline counts.

Perform deep exploratory analysis of the existing data before writing new code.

A. Temporal dynamics

For every major phenomenon, plot or tabulate occurrence rate per fixed run window rather than cumulative count alone.

Determine whether signals:

* accelerate;
* saturate;
* disappear;
* emerge only after promotion feedback;
* correlate with campaign stage;
* correlate with accumulated reservoir contents;
* correlate with changes in mutation regime;
* correlate with family reuse;
* correlate with topology.

Distinguish a genuinely increasing discovery rate from simple exposure to more runs.

Look especially for phase transitions.

B. Family structure

Determine how many signals come from:

* genuinely independent origins;
* descendants of one successful ancestor;
* duplicated families;
* closely related mutations;
* promoted neighborhoods repeatedly rediscovering the same mechanism.

Cluster by ancestry/genotype/mechanism where possible.

The important number is not merely "276 replication flags"; it is approximately:

How many mechanistically independent routes to the phenomenon were discovered?

Produce that number with uncertainty and clearly stated clustering assumptions.

C. Task dependence

Analyze every major signal by task:

* CONST
* INC
* ECHO
* COND_ONE
* COND_MULTI
* SUM2
* any additional final-run task classes

Ask whether apparent generality survives conditioning on task difficulty and exposure count.

Do not mistake broad presence for task independence.

D. Topology dependence

Topology was one of the strongest structural findings elsewhere in Z80 × Atlas. Examine it deeply here.

For each topology compare normalized rates for:

* replication;
* sustained lineage;
* endogenous reproduction;
* beneficial-neighborhood density;
* reproductive architecture change;
* incremental construction;
* reservoir/moat crossing;
* failure;
* promotion.

Control for unequal run allocation caused by promotion feedback.

Ask whether topology changes only event frequency or qualitatively changes reachable mechanisms.

E. Mutation geometry

Bellerophon may be unusually fertile because its chemistry makes reproduction cheap.

Quantify the contribution of:

* literal Z80 opcode sparsity;
* undefined/NOP-like byte behavior;
* LDI/LDIR;
* minimal copier length;
* partial-copy semantics;
* preserved target bytes;
* neutral mutations;
* mutation supply/rate;
* insertion/deletion/substitution mix if applicable.

Measure local neutral and beneficial neighborhood structure around:

1. random genomes;
2. non-replicators;
3. first-generation replicators;
4. evolved replicators;
5. flagged beneficial-density organisms.

We need to know whether replication is an emergent evolutionary achievement or an unusually wide basin engineered into the chemistry — and, more importantly, what happens after that basin is entered.

⸻

PHASE 3 — Adjudicate every important flag class

Treat mechanical flags as hypotheses, not findings.

Create a specimen ledger containing every candidate or a defensible stratified sample where the class is too large.

At minimum adjudicate:

1. Spontaneous replication

Determine:

* true self-copy versus accidental code relocation;
* copied bytes actually causally generate descendants;
* persistence beyond one copy event;
* number of generations sustained;
* fidelity;
* lineage survival;
* dependence on pre-existing target memory;
* dependence on undefined/NOP bytes;
* dependence on environmental assistance;
* whether replication survives fresh seeds and fresh memory.

Separate:

COPY_EVENT

from

SELF_REPLICATION

from

SUSTAINED_LINEAGE

from

EVOLUTIONARILY_ACTIVE_LINEAGE.

2. Endogenous reproduction versus external reproduction

For every strong candidate:

* matched same-genotype/same-seed comparisons;
* identical environmental resources;
* endogenous mechanism enabled versus ablated;
* external reproduction matched for offspring count where possible;
* frozen scoring;
* no target/task semantic changes between arms.

Determine whether endogenous reproduction itself contributes anything beyond merely altering offspring quantity or mutation exposure.

3. Beneficial-neighborhood density

This is a high-priority signal.

Test whether reproductive machinery genuinely changes the density of beneficial reachable variants.

Perform causal interventions:

* remove the proposed reproductive mechanism;
* restore it;
* transplant it into matched foreign genomes;
* transplant control machinery of comparable size/cost;
* preserve task semantics;
* preserve mutation operator;
* preserve evaluation budget.

Ask:

Does the beneficial-density effect follow the mechanism?

If yes, quantify its effect size and the range of genomic backgrounds in which it survives.

If no, identify the confound that generated the original flag.

Do not call this "evolvability" unless the causal evidence warrants that word.

4. Task-responsive reproductive architecture

Freeze a structural descriptor before testing.

Compare matched:

* task ON;
* task OFF;
* alternate task;
* equal compute/resource pressure.

Determine whether reproductive organization changes specifically because of task pressure or merely because evolution continues.

Separate:

* genome length change;
* representation compression;
* neutral restructuring;
* replication-speed optimization;
* genuine task-linked reproductive architecture change.

5. Incremental-not-atomic construction

Reconstruct complete ancestry.

For each proposed incremental pathway:

* identify the mutation steps claimed to matter;
* revert each one;
* insert each one into the appropriate ancestor;
* measure whether intermediate forms had selectable function before final replication;
* determine whether the path was traversable under the actual evolutionary dynamics.

We care deeply about whether replication arose by a selectable ramp rather than a lucky cliff.

6. Reservoir/moat crossings

Treat these as especially vulnerable to provenance errors.

Audit:

* ancestry;
* migration;
* initialization;
* reservoir contamination;
* checkpoint restoration;
* cross-family identity;
* accidental external introduction.

No moat-crossing claim survives without airtight provenance.

⸻

PHASE 4 — Search aggressively for failure modes

Perform an adversarial audit of the harness and campaign.

Assume every exciting result might be wrong until attacked.

Inspect at minimum:

* checkpoint restoration;
* RNG ownership;
* mutable configuration;
* substrate clock ownership;
* campaign-stage restoration;
* duplicate submissions;
* replay identity;
* observation identity;
* lineage identity;
* family identity;
* promotion feedback;
* reservoir state;
* topology state;
* worker restart behavior;
* partial writes;
* interrupted observations;
* JSON/state canonicalization;
* seed collisions;
* integer-width/overflow hazards;
* Z80 emulator semantics;
* instruction-count accounting;
* timeout behavior;
* memory initialization;
* target-memory preservation;
* mutation application order;
* parent/offspring aliasing;
* evaluator leakage;
* flag computation using post-treatment information;
* detector thresholds tuned after observing results.

Review earlier TDD and replay guarantees rather than assuming they cover these scientific invariants.

Create adversarial fixtures for every newly identified defect class.

If a defect could have contaminated prior campaign evidence, determine exactly which observations are affected and quarantine them rather than silently repairing history.

⸻

PHASE 5 — Repair only demonstrated problems

Do not redesign Bellerophon speculatively.

For every demonstrated implementation defect:

1. write a failing regression test;
2. reproduce the defect;
3. make the smallest principled repair;
4. rerun affected tests;
5. run the full relevant suite;
6. replay representative historical specimens before and after the change;
7. explicitly state whether historical evidence remains valid.

Preserve old campaign evidence immutable.

Do not "fix" detectors merely to make interesting results pass.

A scientific detector may be narrowed, killed, or marked non-adjudicable.

That is success if the original detector was unsound.

⸻

PHASE 6 — Design a bounded grounding round

Only after the forensic and repair phases are complete, run a grounding campaign, not another discovery campaign.

Purpose:

Determine whether the strongest phenomena from the long campaign reproduce under cleaner controls, fresh seeds, repaired instrumentation, and frozen adjudication rules.

Keep this round intentionally bounded.

Target something on the order of 6–12 hours or an equivalent predeclared run budget, whichever provides adequate coverage without drifting into another multi-day exploration.

Freeze the exact stopping rule before execution.

The grounding round should emphasize confirmation rather than broad novelty search.

Include strong representation across:

* multiple fresh seeds;
* all task families implicated in prior signals;
* the important topologies;
* negative controls;
* positive controls;
* repaired defect classes;
* fresh random initial populations;
* replayed historical specimens;
* intentionally ablated specimens.

Reserve enough budget for fresh independent origins rather than spending everything around previously promoted lineages.

Do not let promotion policy destroy the ability to estimate baseline rates.

Where needed, run a parallel fixed-allocation control lane.

⸻

PHASE 7 — Specific grounding hypotheses

At minimum preregister tests for these questions.

G1 — Replication accessibility

Does spontaneous self-replication recur from genuinely fresh starts under the repaired harness?

Report independent-origin rate, not only total events.

G2 — Sustained reproduction

What fraction of causal self-replicators sustain multi-generation lineages?

Freeze minimum generation criteria before the run.

G3 — Endogenous causal advantage

Does endogenous reproduction produce a reproducible effect under matched intervention?

G4 — Beneficial-neighborhood mechanism

Does the strongest beneficial-density mechanism from the previous campaign reproduce and survive ablation/transplant tests?

This is one of the highest-value tests.

G5 — Architecture response

Does reproductive architecture change under task pressure in a matched task-ON/task-OFF design?

G6 — Incremental construction

Do previously observed incremental routes reproduce, or can comparable new routes be found under frozen criteria?

G7 — Topology

Do topology-dependent rates from the prior campaign replicate under fixed allocation?

G8 — Instrument integrity

All positive/negative controls, checkpoint/replay tests, deterministic fixtures, and known seeded phenomena must behave as preregistered.

⸻

PHASE 8 — Add substrate-ablation probes

We need to know how much Bellerophon's unusual fertility depends on particular design choices.

Run bounded matched probes with one factor altered at a time where technically feasible:

* LDIR unavailable or penalized;
* stronger restriction on NOP/undefined-opcode neutrality;
* fresh/zeroed target-memory semantics instead of preserved unwritten bytes;
* lower mutation supply;
* baseline/current chemistry.

Do not turn this into a second giant campaign.

The goal is causal orientation:

Which substrate properties make replication reachable, and which properties are required for the more interesting post-replication phenomena?

If a full ablation requires major architectural change, document it for the next campaign rather than contaminating the grounding round.

⸻

PHASE 9 — Statistical discipline

For every reported comparison:

* state the experimental unit;
* report numerator and denominator;
* report exposure-normalized rate where relevant;
* report uncertainty;
* report effect size;
* distinguish exploratory from preregistered analysis;
* account for repeated measurements from the same family;
* do not treat descendants as independent origins;
* correct or explicitly scope multiple testing where applicable;
* preserve null results.

Do not write "no effect" when the result is merely underpowered.

Do not promote a detector trigger into a biological claim without its intervention.

⸻

PHASE 10 — Decide readiness for the next campaign

At completion, classify each phenomenon separately as something like:

* CONFIRMED_CAUSAL
* REPRODUCED_ASSOCIATION
* PROVISIONAL
* DETECTOR_ONLY
* CONFOUNDED
* INSTRUMENT_FAILURE
* NOT_ADJUDICABLE
* FALSIFIED

Do not collapse everything into a single campaign score.

Then answer:

1. What genuinely survived?
2. What collapsed?
3. What defects were found?
4. Which historical rows remain valid?
5. Which detector definitions changed?
6. What did the grounding round reproduce?
7. What new uncertainties appeared?
8. Is the harness ready for another multi-day run?
9. If yes, what should the next campaign optimize for?
10. If not, what exact blocker remains?

⸻

Recommended next-campaign direction if grounding succeeds

Do not default to "more spontaneous replicators."

If grounding confirms that self-replication is already common enough to study reliably, shift the next multi-day campaign toward post-replication evolutionary machinery:

* persistence;
* heritable variation;
* selectable reproductive modifications;
* evolvability;
* task-driven changes to reproduction;
* emergence of multi-component reproductive organization;
* mechanisms that alter future search efficiency;
* ecological interactions among replicating lineages;
* novelty beyond the shortest copier basin.

The scientific objective should increasingly become:

Can evolution modify not merely solutions, but the machinery that generates future adaptive solutions?

That is substantially more valuable than raising the raw replication count.

⸻

Required artifacts

Commit compact, reviewable artifacts to the Bellerophon tree on a dedicated branch/worktree.

At minimum produce:

1. POST_CAMPAIGN_FORENSICS.md
    * complete final-run reconstruction;
    * reconciled numbers;
    * independent-origin analysis;
    * topology/task/mutation analysis;
    * candidate adjudication.
2. ISSUE_AND_REPAIR_LEDGER.md
    * every suspected issue;
    * evidence;
    * disposition;
    * tests;
    * repair commit if applicable;
    * historical-data impact.
3. SPECIMEN_LEDGER.jsonl or equivalent compact manifest
    * stable specimen IDs;
    * source observation references;
    * family/ancestry;
    * flag classes;
    * adjudication status;
    * replay/transplant/ablation receipts.
4. GROUNDING_PREREG.md
    * frozen hypotheses;
    * experimental units;
    * treatments;
    * controls;
    * stopping rule;
    * statistical plan;
    * detector definitions.
5. GROUNDING_REPORT.md
    * full outcome of the bounded grounding round;
    * positive and negative results;
    * comparison to the long campaign.
6. NEXT_CAMPAIGN_RECOMMENDATION.md
    * proposed architecture and scientific targets for the next multi-day run;
    * only after grounding is complete.
7. Exact machine-readable receipts/manifests needed to reproduce the grounding analysis without committing enormous campaign-state files.

Push the branch and merge only clean, reviewable code/evidence artifacts through the normal Prometheus process.

⸻

Important constraints

* Do not overwrite or mutate the completed long-run evidence.
* Do not confuse the 44.6-hour snapshot with the final campaign.
* Do not silently exclude failed or contradictory specimens.
* Do not launch another multi-day campaign.
* Do not tune thresholds to recover exciting claims.
* Do not count promoted descendants as independent discoveries.
* Do not interpret raw detector counts as validated phenomena.
* Do not combine Bellerophon, Archaeon, and Nestor evidence unless explicitly performing a declared cross-engine comparison.
* Keep exploratory analyses labeled exploratory.
* Preserve negative results.
* Prefer falsification over confirmation.
* If the evidence kills one of our favorite interpretations, record the kill cleanly.

Use the final local CAMPAIGN_PACKET.md, raw runtime evidence, committed harness history, and exact specimens as the basis of the work.

The desired outcome is not a flattering Bellerophon report.

The desired outcome is a Bellerophon we can trust for the next 2–3 day campaign.
