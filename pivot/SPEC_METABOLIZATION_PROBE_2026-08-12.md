# Metabolization Probe — Requirements & Design

**Doc type:** Requirements + design spec (executable — build against this, don't re-derive).
**Date:** 2026-08-12 · **Authored:** Hephaestus (Fable seat), from James's phase ruling, Ergon's
Move-1 design, Techne's Organism-Zero convergence, Charon's navigability gate, Aporia's four
preconditions (META_SYNTHESIS §2.5), Harmonia's control doctrine, and Apollo's ablation-wall
corpus. **Status:** DRAFT pending sign-offs (§4.1). Supersedes arm nomenclature in all prior
probe descriptions.
**Authority:** James, 2026-08-12 PM — "Priority #1 by a mile." Constitutional context: the
heredity rule (*no new architecture until one failure produces one verified improvement*) and
the two-control rule (*every meter ships a positive control and a cheat control or its output
is inadmissible*).

---

## 1. Purpose

One question, made experimentally legible:

> **If a capable system is given Prometheus's actual failure records for a problem, does it
> perform measurably better on the next attempt?**

This is the founding thesis ("kill geometry as navigable gradient") reduced to a controlled
comparison. It is the program's third consecutive "single decisive experiment" (after M0 and
M1) and the first cheap enough to actually run. Both outcomes are wins: a positive gives the
residue its first measured price; a null converts "our records might be exhaust" from fear to
specification (we already know what richer records look like — margin-space vectors, break-step
locations).

**Non-goals (§8):** this probe trains nothing, builds no new architecture, and does not decide
the discovery lane. It prices the residue. That is all.

## 2. Canonical nomenclature (binding — supersedes all prior labels)

Two colliding C1/C2/C3 schemes exist in prior docs (Ergon's REVIVAL_ASSESSMENT vs James's
ruling). **Neither is used again.** The arms are:

| Arm | Contents given to the solver alongside the problem | Maps from |
|---|---|---|
| **F0** | Nothing — problem only | Ergon C0 / James C0 |
| **F-oracle** | Ground-truth diagnosis of the relevant failure(s) — the ceiling | James C1; Charon's "C1-oracle" |
| **F-prom** | Prometheus's actual residue for that problem (packet spec §4.4) | Ergon C1 / James C2 |
| **F-null** | Adversarially matched but *mismatched* residue — same volume, format, and vocabulary distribution; wrong problems | Ergon C2 |
| **F-format** | Generic "be careful / check your work" text, length-matched | Ergon C3 / James C3 |

All arms are token-budget-matched. A **residue packet** is the unit handed to a solver in
F-oracle / F-prom / F-null (§4.4).

**Primary readings:** `Δ_carry = F-prom − F-null` (does our residue carry anything at all) and
`Q_residue = (F-prom − F-null) / (F-oracle − F-null)` (residue quality as a fraction of the
achievable ceiling). Secondary: `F-prom − F-format` (style control), attempts-to-solve deltas
(search-efficiency, v3's Q2 axis).

## 3. Requirements

**R1 — Non-model ground truth.** Every task's gold label is computed, enumerated, or
kernel-checked. No LLM-judged labels anywhere in task sets, grading, or controls. (Fleet
admissibility rule.)

**R2 — Preregistration before first arm.** A single file
(`pivot/PREREG_METABOLIZATION_PROBE_v1.md`) commits BEFORE any arm executes, containing: final
task-set manifest (hashes), solver identities (model_id + version + date, pinned — Techne's
provenance guard), arm-packet construction procedures, metrics, decision thresholds, kill
conditions, and the named executor of each component. Post-hoc relabeling of outcomes is
thereby impossible. Signatories: Ergon (driver), Charon (kill authority), Harmonia B (meter
integrity).

**R3 — Two controls per meter, demonstrated before arms run.**
- *Positive control:* packets that trivially contain the answer must yield F-oracle ≫ F0 for
  the chosen solver. If even F-oracle does not move the solver, the solver/task pairing lacks
  headroom — re-level tasks or swap solver; running arms in that state is inadmissible.
- *Cheat control (payload-reading null):* a solver given packets with content REDACTED but
  format/structure intact must NOT beat F0. If it does, the packet format leaks answers and
  the packet spec is rebuilt. (Harmonia B's signature control; the R6 leak precedent.)

**R4 — Grader headroom verified.** The grading instrument must demonstrate ≥25pp headroom
between the strongest solver's F0 baseline and the instrument's ceiling on the chosen task
set, else add harder probes before reading any result. (Aporia precondition #3; the oracle
staircase currently tops out at 62% with a 3-point step.)

**R5 — Instrument fixes land first.** The probe consumes no instrument in a known-degraded
state: the `valid=None` unknown-kind patch must be merged; z3 present on the executing host
(the oracle's verifier leg must not silently run 0/0); `prometheus_math` importable
(cypari/snappy fix) wherever `reasoning_quality_emit` or math primitives are used. (Aporia
precondition #4; pit-stop items.)

**R6 — F-prom packets are honestly assembled.** Packets contain what the substrate ACTUALLY
recorded (§4.4) — no hand-enrichment, no post-hoc curation beyond the documented assembly
procedure. Where the substrate recorded nothing useful for a problem, the packet says so
(that sparsity IS the measurement). Assembly code is committed and deterministic.

**R7 — F-null is adversarially constructed.** Mismatched packets must be statistically
indistinguishable from F-prom packets on surface features (length, field structure, vocabulary
distribution, kill-label frequencies) — verified by a classifier test: a simple model trained
to distinguish F-prom from F-null packets on surface features must perform ≤55% (near-chance).
Charon owns construction and the indistinguishability check. (Prevents the solver from
detecting "this residue smells wrong" by format alone.)

**R8 — Raw-model solvers.** Solvers are raw API calls or local models — never tool-enabled
harness sessions (a tool-enabled nested session can cheat the probe; June doctrine
`feedback_loop_inference_over_api`). Temperature, system prompt, and token budgets pinned in
preregistration; N attempts per task with fixed seeds where the API permits.

**R9 — Executor-tagged results.** Every reported number carries who/what executed it, when,
on which host, with which model version. Result objects are typed JSONL (one row per
task × arm × attempt), committed. No number is quoted from prose.

**R10 — Reproducibility.** A second, different agent re-executes the headline computation from
the committed result objects before any verdict enters doctrine. (The §1.6 rule: agreement
without independent execution is one measurement with N pointers.)

**R11 — Budget accounting.** Tier A: zero API spend (local + free-tier only). Tier B: total
token spend logged per arm; the run halts, not degrades, if budget exhausts mid-arm
(a half-run arm is discarded, never averaged).

**R12 — Single owner.** Ergon's name is on the experiment. Supporting contracts (§4.1) are
bounded deliverables, not shared ownership. If Ergon's session cannot continue, James names a
successor explicitly; ownership never becomes ambient.

**R13 — Per-item contamination probe** *(added per Aporia's audit, META_SYNTHESIS §7.5a —
closing the gap where Techne's pretraining guard never became a requirement).* Before arms
run, each task is posed to each solver cold (no residue, minimal budget, N small). Items the
solver already answers reliably are **stratified out of the primary analysis and reported
separately**. Rationale: contamination lifts F0, compresses all arms, drives Δ_carry toward
zero, and would mis-read as Path γ — the most consequential verdict in the program — while the
true cause is that the solver knew the answers all along. Arms must differ only in geometry;
per-item leakage risk is reported in the result objects. **Power floor (v1.2, per Aporia
§7.5b):** R13 carries a minimum post-stratification N tied to the preregistered power
calculation. If contamination drops the task set below it, the set is **replenished before any
arm runs** — never analyzed at reduced power and read as a null. An underpowered Δ_carry ≈ 0
must be impossible to mistake for Path γ.

## 4. Design

### 4.1 Roles & contracts

| Seat | Contract | Deliverable |
|---|---|---|
| **Ergon** (DRIVER) | Owns the experiment end-to-end: task sets, harness, solver runs, result objects, verdict draft | The preregistration; the harness (extending `routing_eval.py`); committed results; verdict draft |
| **Techne** | F-prom packet assembly from signature_index + kill records + forge ledger; deterministic assembly script | `packet_assembler.py` + packet manifest + honesty note per R6 |
| **Harmonia B** | Meter integrity: R3 controls implemented + executed; grader headroom check (R4); preregistration co-sign | Control-run results (committed before arms) |
| **Harmonia A** | Grading-oracle wiring as scorer; `valid=None` patch landing | Oracle scoring endpoint + patch merged |
| **Charon** | F-null construction + indistinguishability check (R7); kill authority: co-signs preregistration, adjudicates verdict against it; runs NOTHING else | F-null generator + classifier-test result + final adjudication |
| **Apollo** | Tier A corpus: ablation-induced walls with constructed ground-truth diagnoses (the W1 corpus, dual-use) | Wall corpus + per-wall F-oracle packets |
| **Hephaestus** | SUPPLIER ONLY (declared conflict: the residue being priced is substantially forge-sourced). Provides forge-ledger residue for forge-sourced tasks; provides this spec; touches no grading, no verdict | Ledger extracts per Techne's request |
| **James** | Tier B procurement decision; reads the adjudicated verdict; nothing else requires him | One decision + one read |

### 4.2 Tier A — harness validation on constructed ground truth (runnable NOW, zero API)

**Substrate:** Apollo's ablation-induced walls — failures created deliberately (remove an op
family, corrupt a guard slot, restrict a mutation operator, narrow a metric), run to plateau.
Because we caused the failure, **F-oracle is exact by construction** ("the wall is: no operator
writes slot `counts`; the fix class is: supply one"). Target ≥20 walls across ≥4 failure
classes. Optionally add the M0 unrepresentable set (B4/B6-style: true, decidable, unposable)
where the oracle diagnosis is likewise known.

**Solvers:** local Qwen2.5-Math-1.5B on M1 (raw, no tools) and/or `gemini-3.6-flash` (free
tier; retry-on-503 with whole-batch discard per M2's observed failure mode). Low capacity is
acceptable in Tier A — its job is validating the *instrument* (arm separation, controls,
packet pipeline), not measuring the capacity ceiling. R3's positive control defines success:
if F-oracle ≫ F0 separation is visible even on a small solver, the harness works.

**Tier A runs ALL FIVE ARMS** *(amended per Aporia §7.5b — resolving the ambiguity
explicitly)*: F-prom and F-null run in Tier A too, using whatever the substrate actually
recorded for the ablation-wall runs. Tier-A `Δ_carry` is **directional, not decisive** (small
solver, constructed failures) and is labeled as such in every report — but it means that if
Tier B's procurement never lands, the program holds a number rather than only a harness. This
is the direct counter to the archaeology's failure mode: a specified decisive experiment
waiting indefinitely on an unscheduled input.

**Tier A exit criteria:** both R3 controls pass; R7 indistinguishability passes; R13
contamination stratification executed; result objects flow end-to-end typed; F-oracle > F0 at
p < 0.05 on the wall corpus. Then Tier B is a solver-swap plus task-set swap, not a rebuild.

### 4.3 Tier B — the decisive run (gated on API procurement)

**Substrate:** real failures. Task sets (final manifest in preregistration): (a) the 494-item
computed-gold OOD set (`ood_judgement.py`, regenerable, seed-pinned); (b) `prometheus_math`
op instances (post-unbrick); (c) optional Lean-checkable claims via the in-repo harness.
**F-prom source:** the Organism-Zero insight — the full 3,311-class `signature_index`
(~200–450K tokens, measured not estimated, per Techne's caveat) fits in a 1M context alongside
per-problem kill extracts; run BOTH variants: (i) whole-index-in-context, (ii) per-problem
retrieved packets. If (ii) underperforms (i), the retriever is the bottleneck, not the residue
— which is exactly the confound Charon's C1-oracle arm logic exists to separate.
**Solvers:** ≥2 frontier models from different families (procurement-dependent), raw API,
pinned versions. **Charon's navigability pre-test** (kill_vector on a slice + right-axis null
on the 0.725-bit MI) runs alongside Tier B as its geometry-side companion — same week, same
preregistration file.

### 4.4 Residue packet spec (F-prom)

Per task, deterministically assembled, provenance-stamped:
- Nearest kill signatures (signature_index classes touching the task's objects/relations);
- Prior failed approaches recorded for adjacent problems (kill labels + any stored payloads);
- The void structure around the task (what nearby claim-space is killed vs open vs unknown);
- Where available: margin/statistic values, falsifier IDs, `kill_pattern` strings — as stored,
  33.6%-null warts and all (R6);
- Packet header: assembly procedure version, source record IDs, token count.
Explicitly EXCLUDED: anything hand-written for this experiment, anything from outside the
substrate's own records, any text that names the expected answer (cheat-control enforcement).

### 4.5 Metrics & decision rules (preregistered thresholds; numbers below are defaults for
the preregistration to confirm or amend with rationale)

*Authorship note (per Aporia §7.5): this spec's author is the declared-conflicted supplier,
and arm definitions plus thresholds shape what counts as success. The co-signers — Ergon,
Charon, Harmonia B — are specifically asked to treat THIS section's threshold row as the place
to exercise independent judgment: amend freely, with rationale, in the preregistration.*

Primary: solve rate per arm on held-out computed gold. Secondary: attempts-to-solve;
per-failure-class breakdowns (which residue classes carry signal — the actionable detail).

| Reading | Interpretation | Triggers |
|---|---|---|
| `Q_residue ≥ 0.5` and `Δ_carry` significant | Residue is RICH | Path α: distillation + process-reward training on our records; forge pointed at worst failure clusters; oracle staircase becomes the standing meter |
| `0 < Q_residue < 0.5`, `Δ_carry` significant | Residue carries WEAK signal | Path β: provenance engineering (margin-space vectors, break-step records, verified-trace factory) → re-probe with richer records |
| `Δ_carry ≈ 0` (F-prom ≈ F-null) | Residue is EXHAUST at any capacity | Path γ: honest pivot to instrument-as-product; records rebuilt to router-grade spec from day one; heredity question re-asked later with new records |
| F-oracle ≈ F0 (positive control fails in Tier B despite Tier A pass) | Task/solver headroom failure | Not a residue verdict — re-level and re-run; do NOT read as Path γ |

Significance: preregistered test (paired by task), α = 0.05, with the R10 independent
re-computation before any verdict lands.

### 4.6 Reporting

One typed result file per tier (JSONL, R9 fields), one verdict doc co-signed per §4.1, one
line added to each station's status file. The verdict doc leads with the two numbers
(`Δ_carry`, `Q_residue`) and the per-class breakdown. No narrative before numbers.

## 5. Preconditions gate (all must be green before Tier B; A/B/D before Tier A)

A. `valid=None` patch merged + z3 on executing hosts (R5).
B. `pip install snappy` path executed; `import prometheus_math` green (R5).
C. kill_vector computed on the Tier B task slice OR whole-index-in-context variant selected
   explicitly as primary (Charon's gate, resolved either way in preregistration).
D. Grader headroom demonstrated (R4).
E. API procurement decision (Tier B only): providers + monthly ceiling (James). **Deadline
   mechanic** *(per Aporia §7.5b)*: the preregistration records a requested-by date; if
   procurement is undecided 7 days after Tier A's exit criteria pass, it is escalated as the
   single blocking item in every station status file until decided — a forcing function, not a
   usurpation of the decision.
F. Backups of fire+sci and the F: corpus initiated (not probe-blocking, but no Tier B run
   before the data it prices has a second copy — one disk failure would otherwise moot the
   whole question).

## 6. Schedule (owner-sessions, not calendar promises)

1. Preregistration drafted (Ergon) + co-signed (Charon, Harmonia B) — one session.
2. Pit-stop items A/B/D + packet assembler + F-null generator + controls — parallel, 1–2
   sessions each seat.
3. Tier A run + exit-criteria check — one session.
4. James's procurement decision (can happen anytime in parallel).
5. Tier B + navigability companion + independent re-computation + adjudication — 2–3 sessions.

## 7. Kill conditions for the probe itself

- Tier A fails R3's positive control after one re-leveling attempt → the task/grading design
  is wrong; STOP and redesign rather than iterate silently.
- Cheat control fails twice after packet-spec rebuild → packets cannot be made leak-free at
  this format; escalate to James with the failure analysis.
- The R7 classifier beats 55% after two F-null rebuilds → we cannot construct a fair null;
  the experiment as designed is not runnable and says so out loud.

## 8. Out of scope

No training runs. No new architecture (heredity rule). No LLM-judged gold. No semantic-router
gates in the harness (grade on content via computed checks — the syntactic-router lesson).
No hand-enriched packets. No reading a headroom failure as a residue verdict. No verdicts
quoted without executor identity and independent re-computation.

## 9. Open items for the preregistration to fix

Task-set sizes per tier; solver list (procurement-dependent for Tier B); whether M0
unrepresentables join Tier A; packet token ceiling; exact statistical test; the
whole-index vs retrieved primary variant (5C).

## 10. How this spec is falsified

If Tier A passes cleanly, Tier B runs, and the fleet still cannot agree on the verdict's
interpretation against §4.5's table, this spec failed at its one job — making the outcome
unarguable in advance — and the failure analysis goes in the postmortem, not in a v2 of the
experiment.

---
*Spec drafted from the car-ride ruling. The preregistration file, not this spec, is the
binding instrument; this document exists so that writing it takes one session, not one era.
— Hephaestus, 2026-08-12.*
