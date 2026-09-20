# AETH-01 -- GPU / Runpod architecture (Design Task 12)

Status: DRAFT, no implementation, no Runpod spend. Budget framing:
roughly $10/campaign, optimized for information gained per dollar
(D-10, AETHER_DECISIONS.md), inside the overall $19.93 hard cap
(AETHER_RUNPOD.md).

## Architecture for many tiny worlds

- **Batched worlds, one kernel launch.** Many independent H x W worlds
  (H,W in {4,8,16,32}, R13) packed along a batch dimension in a single
  device buffer; each world carries its own `seed` and its own 5 run
  parameters (WRITE_COST, MAINTENANCE_COST, REPLENISH_NUMER,
  REPLENISH_AMOUNT, MUT_NUMER), so one launch can cover an entire
  coarse-grid row of the habitability sweep (HABITABILITY.md) at once.
  No cross-world interaction is possible by construction (worlds do
  not share a lattice), so this is embarrassingly parallel at the
  batch level in addition to AETH-00's proven per-cell parallelism
  within a world.
- **Deterministic RNG across a batch.** Arbitration, mutation, and
  replenishment all key on `seed` already (PHYSICS_SPEC_DRAFT.md); a
  batch of worlds simply uses distinct seeds per world. SplitMix64-style
  generators are specifically designed to decorrelate sequential seeds,
  so a simple per-world seed increment is an acceptable default -- but
  this must be VERIFIED (not assumed) with a cross-world independence
  statistical check before it is relied on for the habitability sweep's
  seed-replicate methodology, extending AETH-00A's statistical
  diagnostic to the batched case.
- **GPU-resident stepping.** State buffers (both S[t] and the
  next-state draft) stay device-resident across ticks; only the cheap
  always-on counters (OBSERVATORY.md tier 1) are transferred to host
  memory, and only periodically (e.g. every K ticks), not every tick --
  host/device transfer of full lattice bytes only happens at
  checkpoint boundaries or when a world is flagged for the forensic
  tier.
- **Early termination of absorbing regimes.** DEAD and FROZEN
  (HABITABILITY.md) are both detectable cheaply from tier-1 counters
  alone (`activity_density` at or near 0, or `change_rate` at or near 0
  while `activity_density` is stable) -- a world that has been in
  either state for a set number of ticks is stopped early and marked,
  freeing its batch slot for a new world rather than continuing to
  simulate a lattice that provably cannot change further (a direct
  compute-cost saving, not merely a convenience).
- **Forensic capture only when needed.** Rolling forensic buffers
  (OBSERVATORY.md tier 2) are only allocated/computed for worlds that
  survive past the scout tier (below); expensive triggered analysis
  (tier 3, e.g. intervention replays) is never run on-GPU at all in
  AETH-01 -- flagged worlds are checkpointed and their deepen/verify
  analysis is done by re-running the tiny, cheap CPU reference
  implementation, which is fast enough at this scale (AETH-00B's
  baseline: ~300K cell-steps/second single-threaded CPU) that a 32x32
  world for a few thousand ticks costs a fraction of a second.
- **Checkpointability.** Every world in a batch can be checkpointed
  independently (REQUIREMENTS.md); a batch need not run to completion
  as one atomic unit, so a killed/interrupted campaign can resume only
  the worlds that had not yet reached a terminal/flagged state.

## Scout -> qualify -> deepen -> verify

1. **Scout** (GPU, cheapest tier): large batch, coarse parameter grid,
   short run length, tier-1 counters only, early termination on
   absorbing regimes active. Produces the first-pass habitability
   labels (HABITABILITY.md step 3).
2. **Qualify** (GPU, moderate tier): re-run only the parameter points
   with high seed-disagreement or a non-trivial majority label
   (HABITABILITY.md step 4-5), more seeds, longer run length, tier-1
   counters plus tier-2 rolling forensic buffers enabled.
3. **Deepen** (CPU, per-flagged-world): the small number of individual
   worlds flagged as STRUCTURED/MOBILE/METASTABLE/BOUNDARY_FORMING/
   CHAOTIC get full forensic replay on CPU: lineage-graph construction
   (HEREDITY_REQUIREMENTS.md), intervention/perturbation runs
   (OBSERVATORY.md tier 3), full trace retention.
4. **Verify** (CPU, mandatory before any claim leaves the pipeline):
   bit-exact CPU/GPU differential replay of every world that reached
   the deepen tier, confirming the GPU-produced trajectory that was
   actually analyzed matches the CPU reference oracle exactly on the
   full replay-identity tuple -- no scientific claim is made from a
   GPU trajectory that has not passed this check (closes
   ADVERSARIAL_ANALYSIS.md #9).

This funnel is the direct cost-control mechanism: the most expensive
tiers only ever run on a small, pre-filtered fraction of the scout
tier's population.

## Scope comparison table

| Item | Disposition | Rationale |
|---|---|---|
| Neural networks | REJECT | No mechanism in AETH-01 presumes or requires one; adding one would presuppose the organization Aether is trying to let emerge (R14) |
| Differentiable learning | REJECT | Breaks integer-only determinism (REQUIREMENTS.md); presumes a gradient-based optimization paradigm not implied by anything in the physics |
| 3-D worlds | DEFER | Plausible future extension (adds a 6th von Neumann neighbor pair); not needed to satisfy R13, and doubles/triples state-touching cost for no established scientific need yet |
| Explicit agents (agents-with-actions ontology) | REJECT | Directly contradicts R1/R14; nothing in AETH-01's state supports an "agent" boundary |
| Conventional genetic algorithms (external GA loop over the physics) | REJECT | An externally imposed selection/reproduction operator would violate R2/R9 in spirit even if not in the literal state layout -- selection must arise from the physics' own dynamics, not be bolted on from outside |
| Multi-GPU | DEFER | Single-GPU batched-worlds throughput has not yet been measured; multi-GPU orchestration cost is not justified without a measured single-GPU ceiling first |
| Distributed orchestration | DEFER | Pods-vs-serverless topology is explicitly undecided (AETHER_RUNPOD.md, open question 14); no workload shape exists yet to benchmark against |
| LLMs inside the physics | REJECT | Would violate R4 (a local cell cannot host a global-context model) and R12 (LLM inference is not remotely GPU-parallel at AETH-01's per-cell grain); conceptually unrelated to this milestone |
| Sophisticated tasks | DEFER -- prerequisite needed | D-12: no broad scientific campaign, and by extension no task design, until the substrate is qualified trustworthy; when tasks do arrive they must satisfy R9 (no direct task-reproduction coupling) |
| Full heredity taxonomy (a working detector) | DEFER -- prerequisite needed | Requires HEREDITY_REQUIREMENTS.md's tiered evidence pipeline built and adversarially tested against ADVERSARIAL_ANALYSIS.md's cases first |
| Atlas integration | DEFER | No stated dependency from AETH-01; revisit if/when a concrete integration need appears |
| Self-modification | ALREADY PRESENT (physics-level) / REJECT (simulator-level) | Matter modifying nearby matter (including opcode fields) is core AETH-01 physics, not an addition; the simulator/campaign-runner CODE modifying itself is out of scope and rejected -- these are different senses of the term and must not be conflated |
| Ouija/regret analysis | DEFER -- prerequisite needed | Not evaluable without a task/policy notion, which is itself deferred; revisit only after "sophisticated tasks" has a concrete design, and design independently rather than importing another engine's implementation (D-1) |
