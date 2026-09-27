Operator (in session, 2026-09-27), preamble: "Slight pivot to test.  Harmonia should have pushed a structure for work to the repo.  I'd like you to test it:"

Quoted direction (verbatim):

Yes. That’s the correction I’d make too: the model should be descriptive before it becomes prescriptive. We don’t need another doctrine. We need a small shared shape that lets us see work, move it, and recover it.

For Archaeon, I’d fold the existing work into the structure with almost no new rules.

Thread

TH-001 — Causal identity, heredity, and authorship across artificial substrates

This is the long-lived scientific thread. It contains the whole emerging question:

What actually constitutes heredity, authorship, replication and identity when body, executor, code location, code material, inherited material and counterfactual causal power can separate?

It points backward to ENVGATE, PORTABILITY-01, Contract v0.2, B1–B7, the NPE host-conditioned cases, and the BEE provenance/location issue.

The Thread is where we make sure none of those discoveries disappear.

Campaign

C-001 — Causal Lens Hardening

Purpose: take the strongest unresolved findings from TH-001 and determine which distinctions are real enough to become instrumentation versus which were artifacts of our current rulers.

This is not “prove the causal lens.” It is just the current body of related work.

Under it I’d put two Experiments immediately.

Experiment 1

E-001 — B6: Who / Where / What

Question:

When reproduction occurs, can we distinguish the executing entity, execution location, code material, and material governing the inherited writes?

This is the most urgent integrity question.

Initial Tasks:

* T-001: Reproduce the BEE r038751 case from preserved evidence.
* T-002: Reproduce the contrasting BEE case with genuine foreign material.
* T-003: Map NPE’s analogous provenance fields without importing BEE terminology.
* T-004: Compare Archaeon/BEE/NPE readings.
* T-005: Decide whether the lens/adapters need a semantic change.
* T-006: Write the scientific result and identify any historical conclusions affected.

Those are all small enough to move elsewhere later.

Experiment 2

E-002 — B1: Hereditary continuity under recombination

Question:

When two sources contribute to a descendant, under what conditions does “this lineage continued” have a meaningful answer at all?

Initial Tasks:

* T-007: State the candidate continuity criterion.
* T-008: Apply it to the synthetic recombination fixtures.
* T-009: Apply it to the preserved PTE cases.
* T-010: Search specifically for cases where the criterion invents continuity.
* T-011: Compare material continuity versus any usable architecture-level continuity.
* T-012: Adjudicate B1 and write the result.

Attempts

We don’t need to create Attempt objects until something actually runs.

If T-001 runs once and succeeds:

T-001 / A-001 — DONE

If M2 runs out of memory:

T-001 / A-001 — aborted
T-001 / A-002 — rerun elsewhere

That’s enough. No elaborate vocabulary yet.

⸻

And I think the minimal Git representation should initially be equally small:

ops/
  threads/
    TH-001.md
  campaigns/
    C-001/
      CAMPAIGN.md
      E-001/
        EXPERIMENT.md
        TASKS.md
      E-002/
        EXPERIMENT.md
        TASKS.md

That’s it.

No schema engine yet. No twenty-field YAML. No generalized scheduler. No universal lease protocol.

For the first pilot, TASKS.md can literally be a small table:

Task	Work	Status	Executor	Host
T-001	BEE r038751 replay	READY	—	portable
T-002	contrasting BEE replay	READY	—	portable
T-003	NPE provenance mapping	READY	—	portable
T-004	cross-engine comparison	BLOCKED on T1–T3	—	any
T-005	semantic adjudication	BLOCKED on T4	—	any
T-006	report	BLOCKED on T5	—	any

That alone gives us something we’ve been missing: we can look at the repository and see the work graph.

Then we let Archaeon actually use it.

What I particularly like is that T-001, T-002 and T-003 immediately expose the next question you care about: do they really have to run on M2?

Probably not.

If we can make T-001 reproducible on M3, suddenly we have demonstrated the first real unit of Prometheus work moving off the overloaded machine. That’s more valuable right now than designing the perfect scheduler.

So I would make our first operational goal extremely concrete:

Take one real Archaeon Task that would ordinarily run on M2 and successfully execute it somewhere else without changing the science.

That gives us our first true portable Task. Then we learn what information the Task actually needed in order to move. That evidence should drive the system design—not another layer of rules.
