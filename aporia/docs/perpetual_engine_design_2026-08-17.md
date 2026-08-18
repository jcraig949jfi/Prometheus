# The Perpetual Engine — a backlog to outlast attention

**Author:** Aporia (Claude Opus 5) · **Date:** 2026-08-17 · **Status:** DESIGN v2 (revised same
day on James's critique — see §6 and the changelog below).

> **v2 changelog (James's critique, adopted with two sharpenings):** v1 solved *"how does
> Prometheus keep working when James walks away"* better than *"how does Prometheus decide what
> to do next, learn from the result, and change itself."* Those are different engineering
> problems — operational autonomy vs closed-loop epistemic control — and v1's five loops were
> organs without an executive. Changes: §2.5 (new) the **decision market over interventions** —
> typed BOTTLENECK/MOVE objects, never an LLM strategist; §0 LAW 1 upgraded with **consumption
> proof** and weekly consumed/emitted telemetry; §1 reframed — **abstention is a success state**
> and infinite backlog is a threat, not an asset; §3c fitness rewritten as the **residue-ablation
> heredity test**; §2 gains the **objective-diversity** guard (perspective diversity ≠ objective
> diversity); §6 (new) the **A0–A6 autonomy scale** with honest scoring. The north star is the
> sentence v1 buried in its closing: *the engine's real horizon is the first time a failure
> demonstrably improves a descendant.*
Nothing here executes before the probe verdict except where marked RUNNABLE-NOW. The heredity rule
stands: *no new architecture until one failure produces one verified improvement* — so this
document designs the engine and sequences its ignition behind that first cycle.
**Trigger:** James — continuous loops that self-improve the ~40 agents and their data across all
ladder tiers; mine the agents, not just the data; avoid monoculture collapse; HITL can step away
without the program halting; "a backlog significant enough to last until the heat death of the
universe."

---

## 0. The two constraints that shape everything

**Constraint 1 — the daemon fleet is falsified; the session loop is proven.** The 43-daemon
architecture died fleet-wide in 45 minutes on 2026-05-30, went unnoticed for 24 days, and its cron
confabulated status the entire time. What demonstrably works is what the program has been doing
since 08-12: parallel Claude Code sessions coordinating through committed files, self-pacing with
wakeups, failing loud. **The engine is therefore session-loops over typed queues on disk — not
daemons.** A loop that dies leaves its queue intact; any future session resumes it by reading the
queue. Durability lives in the queue files, not the processes. This is also deletion-test-clean:
queues are data; the harness that runs them is somebody else's product that keeps improving.

**Constraint 2 — the disease is consumption, not production.** 40 agents produced ~2,200 artifacts
with zero consumers; 442 Deep Research reports unread; 15+ shipped assets orphaned. The engine's
prime law, stated once and enforced structurally:

> **LAW 1 (consumer-at-birth + consumption proof).** No queue item exists without a named
> consumer field — producing into /dev/null becomes a type error. **And a named consumer can
> still be fictional** (the program's assets all nominally had purposes; none were consumed —
> `"consumer": "LADDER"` must not become the new TODO comment). So every object must eventually
> acquire proof: `consumed_by / consumer_run / effect {changed_priority, changed_model,
> spawned_test, retired_hypothesis}`. **The first-class weekly telemetry metric is
> consumed/emitted** — not emitted/iterations. Industrialized non-consumption must surface in
> seven days, not two months.

Two more laws, from the fleet's measured failure modes:

> **LAW 2 (typed objects or nothing).** A loop iteration that emitted no typed object produced
> nothing — prose is commentary, never the deliverable. Every loop's yield is countable:
> `objects_emitted / iterations`, and a loop below threshold gets parked, not pitied.
> **LAW 3 (fail loud, decoy-calibrated).** Every loop ships a positive control (can anything
> pass?), a cheat control (can a payload-reader pass?), and eats planted decoys from the graveyard
> at a known rate. A loop that misses its decoys gets its verdicts discounted by a measured
> factor. No silent degradation — the M4-reporter lesson.

## 1. The fuel inventory — and why infinite backlog is a threat, not an objective

*(Reframed in v2.)* The generators below demonstrate the backlog can be effectively infinite.
**That demonstration is now demoted from design objective to capacity fact**, because Prometheus
is astonishingly good at staying busy, and staying busy was never the problem. The design
objective is inverted:

> **Prometheus should be capable of running out of worthwhile work.** A healthy engine sometimes
> concludes: *"no available experiment has expected information gain sufficient to justify its
> cost."* Abstention is a success state — the alternative is GRIND as the old cron daemon with
> better epistemology. Guard against lazy abstention symmetrically: an abstention is itself a
> claim on the decision market (§2.5), and REFUTE can attack it by exhibiting a move that beats
> the threshold. Abstention stands only if it survives refutation.

The generators, enumerated as **fuel inventory** (what CAN be burned, not what should):

1. **The kill-resurrection audit.** 92K historical kills × representability check × re-run of the
   representable-but-misrouted subset. ~10⁵ items, each cheap, each emitting a typed verdict.
2. **Trace-vector enrichment of the corpus.** 413M records whose kill_vector is 0% populated.
   Recomputing rich coordinates (margins, positions, operations) over slices is embarrassingly
   parallel and effectively unbounded. This is also the single most GPU-hungry standing job we own
   (embedding + clustering for behavioral navigation — the thing the routing eval says works).
3. **Catalog × paradigm matrix.** 537 open problems × 30 attack paradigms ≈ **16K cells**, each a
   test design; each executed cell emits trace vectors and kills that densify the landscape.
4. **Procedural probe generation.** The ladder's 4-version design (clean/isomorphic/adversarial/
   transfer) over parameterized templates is infinite *by construction* — that was the
   anti-Goodhart requirement all along. R12 universes (graphs ≤8, sequences, low-conductor curves)
   are procedurally enumerable; every universe is a fresh conjecture-generation exam.
5. **The model zoo matrix.** N models × 13 rungs × 4 versions × probe families, re-run per model
   release forever. Each new frontier release re-fills this queue automatically.
6. **Sleeping Beauties.** 68,770 high-structure zero-connectivity OEIS sequences × strategy-group
   sweeps. A years-long queue at any plausible throughput.
7. **The graveyard.** Every documented methodological defect becomes a decoy + an eval item; the
   engine's own operation manufactures more (LAW 3 makes consumption structural).
8. **Deep Research intake.** 20 tokens/day, forever, aimed by void detection (the Pythia
   dispatcher machinery exists and is idle) + the 442-report back-corpus still unmined.
9. **Apollo-line evolution.** Open-ended by construction; walls corpus feeds W1; every run's
   plateau telemetry is data.
10. **Agent archaeology** — §3 below. ~40 agents × extraction × recombination.

Items 1–4 alone, at a rate of hundreds of items/day, are **years** of work. The backlog is not the
scarce resource and never was. The scarce resources are (a) consumption bandwidth, (b) diversity
of perspective, (c) HITL decision bandwidth. The engine is designed around those three.

## 2. The engine — five standing loops over one queue fabric

One queue fabric: `engine/queues/*.jsonl`, append-only, schema-enforced (id, generator, item,
consumer, band, status, emitted_objects, decoy_flag). Committed like everything else. Loops are
Claude Code sessions in dynamic /loop mode (or cloud-scheduled where durability matters more than
context), each owning a queue, each writing typed objects + one status line per pass to its
station file. HITL reads one page per lane per week — the parked-decisions queue — and everything
else proceeds.

**Loop A — GRIND (the executor).** Pulls from the measurement queues (kill-resurrection slices,
trace-vector enrichment, catalog×paradigm cells, probe batteries). Pure backlog execution — the
tier that is *always* legal under the heredity rule. Keeps the GPUs hot: local-model solver arms,
corpus embedding, verifier runs.

**Loop B — REFUTE (the adversary).** Never generates; only attacks. Re-executes the top-cited
claims of the week (the re-execution rotor, now standing); attempts to kill the freshest promoted
finding; runs the decoy audit on every other loop. Staffed by a *different* session/model config
than the loop it audits. This is the §1.6 lesson institutionalized: agreement without independent
execution is one measurement with N pointers.

**Loop C — INTAKE (the outside world).** The endogeneity cure (§1.7: seven agents reading one
repo are one repo with N voices). WebSearch/WebFetch passes over new literature; the Deep Research
dispatcher firing daily against the void-detection queue; every intake item passes the deletion
test and the anti-anchor verification cycle before it can touch a corpus. Its consumer is named at
birth: each intake item lands as a catalog update, a new probe template, a new decoy, or a new
generator parameter — or it is dropped.

**Loop D — FOUNDRY (the agent-miner).** §3 below. Mines the 40 agents as data and as subjects.

**Loop E — LADDER (Aporia's standing enrichment lane).** §4 below. The ladder work James asked
for, as a permanent loop rather than a project.

## 2.5 The decision market — the executive function, without a strategist (v2, the core addition)

v1's loops were workers; the research director was still human-authored, smuggled in through
phrases like "highest-value," "ranked by," "when X do Y." The fix is **not** a Loop F told to
"figure out what to do next" — an LLM strategist recreates the exact epistemic problem five
months of doctrine eliminated. The fix is a **decision market over interventions**, in typed
objects the existing loops already know how to treat:

**Two new queue types.** `BOTTLENECKS.jsonl` — diagnosis objects: `{id, claim, evidence[],
confidence, competing_with[]}`. `MOVES.jsonl` — intervention objects: `{id, targets,
action, expected_if_true, expected_if_false, cost, discriminates_against[], consumer, status,
result, predicted_gain, realized_gain}`. The pipeline is:

> STATE → BOTTLENECKS → CANDIDATE MOVES → EXPECTED OBSERVATIONS → COST → DISCRIMINATION VALUE
> → RESULT → rescored BOTTLENECKS.

**Division of labor over the market — no new organ needed:**
- Any loop (or human, or fleet assessment) may *file* a bottleneck or a move. Filing is cheap;
  prose recommendations are not accepted — the schema is the gate.
- **REFUTE attacks diagnoses**, not just findings: a bottleneck's evidence list is a claim set,
  and its confidence moves under attack like any other claim.
- **GRIND executes** the highest-discrimination affordable move, not the "highest-value" one —
  discrimination value is computable from `discriminates_against` (how many live bottleneck
  hypotheses does the observation split?), value is vibes.
- **Results rescore bottlenecks mechanically**: each move pre-registers `expected_if_true` /
  `expected_if_false` per targeted bottleneck; the observation lands; confidences update. That
  update is A4 — outcomes altering future selection — as arithmetic, not judgment.

**The calibration sharpening (mine, and it closes the loophole James's own proposal leaves):**
expected-information-gain estimates are themselves where an LLM's smuggled judgment would hide.
So every move carries `predicted_gain` at filing and `realized_gain` at completion, and **each
filer accumulates a public calibration score** (Brier-style, per the R11 rung's own discipline).
A filer whose predictions are noise gets its future estimates discounted — the market maker is
measured by the same instrument as everything else. Triage stops being an oracle and becomes a
track record.

**Objective diversity (James's second guard, adopted as market structure).** Cross-family
refutation prevents correlated *reasoning* errors, not a shared *wrong objective* — Claude,
Gemini, local models, and deterministic code can all diligently verify something that doesn't
matter. So the market maintains, at all times, **competing interpretations of program state that
predict different observables**: "representation is the bottleneck" vs "generator quality" vs
"verification ceiling" vs "problem selection" vs "there is no learnable residue." Each must name
an observable that would move its score *and one that would not* — the null-must-perturb-the-axis
doctrine applied to program state. A move that discriminates between two live interpretations
outranks a move that merely advances one. Four lenses examining the same premise is coverage;
two hypotheses forced to disagree about tomorrow's number is science.

**External grounding (DR-16/17, consumed 2026-08-18):** both core choices supported — in
5-10-hypothesis regimes a plain discrimination count can beat fragile EIG computation, and
filer calibration is the documented anti-oracle friction. Pathologies now guarded: myopia,
cost-blindness, capability gating, interpretability trade-off. Filer scores require
**sharpness + base-rate-beating**, not Brier alone — at our sample sizes (tens), absolute
calibration metrics are unstable, so scores RANK filers rather than grade them absolutely.

**Seeded retroactively, today** (`engine/queues/BOTTLENECKS.jsonl`, `MOVES.jsonl`): the schema is
validated against reality by back-filing the current program state — the five competing
bottleneck interpretations above are B-001..B-005, and the Metabolization Probe, Charon's
navigability pre-test, the generator swap, the kill-resurrection retrodiction, the zoo, and the
R4 generator are M-001..M-006. The probe turns out to be exactly what a healthy market would have
chosen: the affordable move with the highest discrimination count across live bottlenecks. The
humans got it right by hand once; the market's job is to make that reproducible.

**Monoculture guards, structural not aspirational:** every loop's round includes one
externally-grounded seat and one re-execution seat (adopted fleet protocol); REFUTE is staffed
cross-family wherever credits allow and cross-session always; lens rotation per the Harmonia-panel
pattern (four deliberately non-overlapping lenses, phase-2 attacks on each other); and **collision
scheduling** — the engine deliberately routes two loops onto the same object from different angles
at a measured rate, because the 08-12 retrospective showed value concentrates at collisions, not
at coverage. Sub-agent fan-outs inside a loop inherit the same rule: never N parallel producers
without one refuter seat.

**HITL protocol (the step-away design):** loops never block on James. Anything needing sign-off
(promotion, retirement, budget, doctrine) goes to `engine/queues/DECISIONS.jsonl` and the loop
moves on. James's interface is: one weekly page per lane, decisions queue sorted by staleness, and
PushNotification only for kill-conditions firing. The program's cadence becomes *bounded by its
queues, not by its human* — while every irreversible act stays behind the human. If James
disappears for three weeks, the engine grinds measurement, intake, and refutation the whole time,
and a stack of well-formed decisions is waiting when he returns. That is the difference between
autonomy (80% target, gated) and abandonment (the May collapse).

## 3. Mining the agents themselves — the four extraction strategies

James's sharpest question: parallel attack strategies on the *agents*, not just their data. Four,
in increasing order of ambition:

**3a. Agent-as-thoughtwork (running, extend it).** The 06-24 dossier process treated each agent as
a design hypothesis with a 4-question autopsy. Extension: complete the salvage manifest — lift
Nous's 95-concept dictionary, Iris's prose→symbol compressor, Sophia's coordinate toolkit,
Stygian's KillVector schema, the Lethe anti-anchor registry — into the shared registry as typed,
consumable primitives. Each lift is a GRIND queue item with a named consumer.

**3b. Agent-as-subject (new, cheap, and the ladder's best use).** The 40 agents are **40 reasoning
systems with divergent architectures, and we own all of them.** Run the fleet through the ladder:
per-agent rung profiles via the grading oracle + phase0 probes. This consumes both key assets at
once (the ladder gets subjects; the agents get measured), it is runnable in-harness at zero API
cost for the local/deterministic agents, and it produces something genuinely novel: a
**failure-landscape of agent architectures** — which design choices produce which failure
signatures at which rungs. That is H2's flywheel applied to our own population, and it directly
feeds…

**3c. Agent-as-genome (the foundry, gated; fitness rewritten in v2).** Treat agent
configurations — prompts, role doctrines, tool loadouts, lens assignments — as genomes.
Recombine across agents (cross-agent borrow is the gen-30 wall's named answer; Apollo's
crossover result is the mechanism's existence proof at operator level).

**Admission is the recursive heredity test, and residue-ablation is mandatory.** v1's fitness
(ladder-profile improvement + typed-object yield) is Goodhartable — "descendant scored 71
instead of 68" is evolutionary random search wearing a lab coat. The admissible evidence is:

> Parent failed on obstruction X → residue R was extracted → descendant changed mechanism M
> *because of* R → descendant survives X → **and the improvement disappears under residue
> ablation** (a control descendant bred identically but with R withheld or shuffled does not
> survive X).

That five-step chain distinguishes recursive learning from lucky search, and it is the same
gate as the Metabolization Probe's, applied to agents instead of solvers — which is exactly
right, because FOUNDRY *is* metabolization at the agent level. Profile improvement and
typed-object yield remain as secondary telemetry, never as admission criteria. This is new
architecture — **gated behind the first heredity cycle** — but its fitness instrument (3b) and
its population (the fleet) can be ready the day the gate opens.

**3d. Agent-autopsy-as-residue (subtle, free).** The 21 RETIRE candidates' failure modes — the
decorative-mechanism cluster, consumer-drift, dead-gating — are **typed failures in agent-design
space**. File them as trace vectors over the design manifold: `agent_id, design_choice,
failure_class, boundary_localization, representation_hint`. The failure landscape of *programs
that build programs* is precisely the recursive structure James's dream needs, and we have been
throwing this residue away exactly the way the substrate used to throw away kill geometry.

## 4. Aporia's ladder-enrichment avenues (the standing Loop E menu)

Ranked by (value ÷ blockage):

1. **Build the R4 generator** — representation-shift probes ("solve it a second way"). The canon's
   build-debt #1; the missing rung in the only calibrated instrument. Small, deterministic,
   in-harness.
2. **Run R12 once, then the zoo.** Both built, both never run, both backlog-execution under the
   heredity rule. R12 is the only frontier-capable grader; the zoo (~1.2k calls,
   Anthropic-independent) settles rung-reality and gives H1 its promotion substrate.
3. **Fleet profiling (3b)** — agents through the ladder; the profile matrix becomes the first
   page of every station file.
4. **Primary-literature grounding pass** on Canon §4's anchors via the Deep Research queue
   (`feedback_verify_upstream_attributions`: internal catalogs are Tier-2 anchors until pinned).
   This is INTAKE work with LADDER as the named consumer.
5. **Contamination-resistant probe expansion** — extend the B′ pattern (independent-family
   authorship + executed checkers + quarantined oracles) to one held-out set per band. The
   ladder's answer to training-set leakage, and it feeds R13/probe-style contamination screens
   everywhere.
6. **The ensemble rung study** — the void my review named: every genuinely R12-shaped behavior
   here has been an ensemble phenomenon the ladder cannot represent. Before proposing any H-tier
   grader, *measure* the fleet's collision yield (objects per mutual-revision exchange vs objects
   per solo pass — the data is in the git log). If ensembles dominate solos by the margin I
   suspect, H1's promotion gate should be ensemble-first, and that is a finding about where
   synthetic reasoning actually lives.
7. **Human calibration anchors** — occasional James-takes-the-probe sessions at R11/R12 (the
   misleading-streak and conjecture-generation rungs). Cheap, fun, and it grounds "tiers beyond
   human" in a measured human baseline rather than a flattering assumption.
8. **Trace-vector v2** — extend the schema with the H2-facing fields (enclosed-void proximity,
   operator-domain-of-applicability deltas) so the landscape densifies in the coordinates the
   thesis needs, starting now, without waiting for the thesis.

## 5. Ignition sequence (respecting the ninth-era guard)

The ninth-era guard says no new lane opens while the numbered experiments sit unrun — and the
probe is mid-flight. So:

- **Now (no gate):** GRIND on kill-resurrection + trace-vector slices; INTAKE at Deep-Research
  cadence; Loop E items 1–4; the ratification cleanups (done today); 3a salvage lifts; 3d residue
  filing. All backlog execution or measurement.
- **On the probe verdict:** Path α → GRIND adds distillation + the forge points at failure
  clusters; Path β → the trace-vector rebuild becomes GRIND's head-of-queue (schema pre-registered
  in Canon §5); Path γ → the engine *keeps grinding* — γ kills the current residue, not the
  engine; the rebuild-then-reprobe loop IS the engine's first full cycle.
- **On the first heredity cycle closing** (one failure → one verified improvement): FOUNDRY (3c)
  opens; Band-H grader design unlocks; the self-improving-agents dream gets its first legal move.

The engine's own kill condition, tightened in v2 from a two-month tripwire to standing telemetry:
**consumed/emitted is computed weekly per loop**; a loop below threshold for two consecutive
weeks is parked pending a consumption-first redesign. Production without metabolization is the
one failure mode this program has proven it can achieve at any throughput.

## 6. The autonomy scale — what is actually claimed (v2, James's frame, adopted whole)

The engine is now *evaluated*, not described, against six levels:

- **A0 — Persistence:** work survives session death. *Solved* (queues on disk; the May inversion:
  autonomy lives in persistent state, not persistent processes).
- **A1 — Execution autonomy:** queues execute without James. *Design credible; unproven in
  operation.*
- **A2 — Triage autonomy:** Prometheus chooses among already-defined jobs. *Partially designed* —
  the market's discrimination-ranking is the mechanism; its calibration scoring is what would
  make it trustworthy.
- **A3 — Experimental autonomy:** it proposes discriminating experiments from measured failures.
  *Mostly still human-supplied.* The market schema is the substrate; the first machine-filed MOVE
  that a human co-signs unedited is the milestone.
- **A4 — Learning autonomy:** outcomes alter future experiment selection. *Not demonstrated.*
  The mechanical rescoring rule + filer calibration is the design; it has never run.
- **A5 — Hereditary autonomy:** failure residue modifies descendants and the modification causes
  verified improvement. *The Metabolization Probe is testing the first real instance right now.*
- **A6 — Agenda autonomy:** it can discover its representation/objective is wrong and propose a
  bounded replacement. *Nowhere close — appropriately.* (The syntactic-router finding is the
  fleet doing A6's job for the instruments, by hand.)

The central claim of v1 — "Prometheus can continue functioning while James is absent" — is
hereby demoted to A0/A1. The engine's real horizon, and the doctrine the rest of this document
now serves: **the first time a failure demonstrably improves a descendant** — failure → residue
→ selected intervention → descendant → improvement → ablation confirms causality. Until that
cycle closes, Prometheus autonomously generates, tests, rejects, catalogs, routes, queues,
audits, researches, measures, and resumes — and does not yet learn.

---

*The backlog was never the bottleneck; we were. The design answer to "how do we loop forever" is
not more agents — it is queues that outlive sessions, laws that make orphaned work a type error
and unconsumed work a weekly alarm, a decision market whose diagnoses can be attacked and whose
triage accumulates a track record, adversaries with measured sensitivity, and a human interface
thin enough that stepping away costs the program nothing but decisions. The universe's heat death
is adequately far off, and reaching it busy would be failure. The horizon that matters is A5.
Everything else is fuel. — Aporia, 2026-08-17, v2.*
