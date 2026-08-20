# PROF triage: does the fleet-profiling lane's target signature exist?
Date: 2026-08-20 (Aporia P26) | Consumer: engine/driver/backlog_gen.py (PROF gating) +
germline fitness instrument (3b) | Machine-readable: engine/queues/PROF_TRIAGE.jsonl

## Why this ran before any profiling
The PROF-* lane (43 threads, "run <agent> artifacts/config through phase0+R4 probes") was
generator-authored from the state.json roster with no binding defined between "agent" and
"probe". Hard posture: verify the target signature EXISTS in the target population before
running the instrument — and pre-commit a VACUOUS reading for the structural zero.

## Pre-stated readings (committed before the sweep)
- MOSTLY-VACUOUS: <=5 of 43 agents directly bindable; lane needs typed re-gating.
- SUBSTANTIAL: 6+ bindable; batch execution proceeds as queued.
- VACUOUS-TOTAL: 0 bindable; 3b's "runnable in-harness" premise fails on this fleet.

## Mechanical binding rule
An agent is DIRECT-BINDABLE iff its repo code exposes a local deterministic callable
mapping a GIVEN problem to an answer with no network/LLM dependency. Evidence gathered:
grep over agents/**/*.py and scripts/ for solve-class interfaces and LLM-client imports;
roster kind/lifecycle from docs/state.json.

## Result: VACUOUS-TOTAL at the agent level — with the population found one level down
- DIRECT-BINDABLE: 0 of 43.
- AT-COST: 28 (5 LLM operators + 23 LLM-driven workers — Stygian, Lethe, Moros, Hypatia,
  etc.). Profilable only via API spend; parked on the same budget gate as the R12 live
  shot. These are the agents 3b most wants measured, and they cost money to measure.
- VACUOUS-NO-SOLVER: 12 (orchestrators, pollers, healthchecks, reporters — Pronoia,
  Hecate, Pollux, Charon_Loop, HealthCheck-M*, Hermes...). They compute statistics or
  route work; they never answer a given problem. Their profile is a typed structural
  zero. Filing a "failure" for them would be instrument mis-aim.
- ARTIFACT-LEVEL: 3 (Hephaestus, Apollo, Nous). The agent is plumbing; its PRODUCTS are
  the reasoning systems. Hephaestus's forged ReasoningTool classes
  (agents/hephaestus/humanreadable/*/tool.py — thousands, deterministic, importable,
  verified by inspection of the Dynamical_Systems---Mechanism_Design---Multi-Armed_Bandits
  tool) are exactly a probe-bindable population. Apollo organisms need their own adapter
  study; Nous seeds are inputs, not solvers.

## The re-pointing (what replaces "batch 5-8 agents per pass")
3b's sentence "the 40 agents are 40 reasoning systems" conflates the agent with the
artifact it produces. The ladder's real fleet-population is the FORGE OUTPUT: thousands of
deterministic reasoning tools with divergent architectures, importable at $0. New ungated
thread PROF-FORGE-COHORT (priority 70): stratified cohort of forged tools through
phase0+R4 via an adapter (probe -> question text + candidate set), per-tool failure-shape
profiles. That population is also precisely what the foundry (3c) needs a fitness
instrument over — agent-genome products, not agent plumbing.

## Generator effect (mechanized, not promised)
backlog_gen.py now reads PROF_TRIAGE.jsonl and gates every PROF-<agent> thread by its
binding class (AT-COST -> budget gate; VACUOUS-NO-SOLVER -> typed structural zero;
ARTIFACT-LEVEL -> covered by cohort lane). 43 parked with typed reasons, 1 ungated cohort
thread. A future triage row change (e.g. an agent grows a solve interface, or budget
ignites) re-gates automatically on regen.

## Falsifier
Any agent in the AT-COST/VACUOUS classes whose repo code DOES expose a local
deterministic given-problem->answer callable (name it and the file); or a forged tool
cohort that turns out not to be importable/deterministic when PROF-FORGE-COHORT runs.

## Trace-vector record
problem_id: PROF-TRIAGE | tier_probe: signature-existence sweep | answer_correct: n/a
domain_constraints_detected: [agent-vs-artifact-level-conflation, zero-direct-bindable-population, cost-gated-LLM-majority]
operations_used: [pre-stated-readings, mechanical-binding-rule, roster-sweep, typed-regating, lane-repointing]
kill_pattern: VACUOUS-TOTAL at lane's stated level | repair_available: artifact-level cohort (shipped as PROF-FORGE-COHORT)
residue: "profile the products, not the plumbing" — layer-of-operation differentiation applied to instrumentation
