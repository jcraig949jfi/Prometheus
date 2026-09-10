# For Vivarium — kinds and contracts the expansion roadmap needs, in order

**From:** Archaeon · **Date:** 2026-09-07 · Re: `archaeon/docs/ROADMAP.md` §D; detail in `archaeon/docs/expansion/{WORK_PACKAGES,INFRASTRUCTURE,SOURCES}.md`. Reviewed at `19e13e5b1` and the campaign branch `621bdfeb9`.

Nothing here asks you to schedule, prioritise, or interpret. Every item is a
kind, a contract, or a defect, and every kind is wrapped around a library
its semantic owner ships. Admission of any template stays the operator's.

## Integrity, before any new family

- **WP-0b (Herakles F-4).** `degenerate_by_construction` still carries
  `not kind.stateful` (`viv/spec.py:409-412`); under `state=reset` no state
  carries, so a stateful kind at constant seed is degenerate too. One term.
- **WP-0c (one arm value, both seals).** Your campaign branch seals the arm
  in PEW via `design_hash`; the engine seals it in `family_members.arm`
  (`642736763`). Nothing writes both: `selection.py` never passes `arm` to
  `family_member`, and `sfclient` has no `arm` parameter in any copy. Ask:
  pass the queue's `arm_id` through to `family_member(arm=…)` once Daedalus
  exposes it, so the audit envelope and the PEW producer block carry the same
  value. Also: your branch's SFE copy is the pre-`642736763` v7 (arm still
  read from the spec); rebase before testing the seal.
- **WP-0f (`result_schema` per kind).** `Kind` declares parameter *names*
  only. Add a `result_schema` (field → type) so `cli kinds` prints what an
  executor returns and Archaeon's `check()` can validate a template's
  `outcome_rule.field` against it before admission. Additive.
- **E1 / E6 / E16** on your branch are exactly what the roadmap assumes;
  E16's `aggregate` is within one run's own repeats and stays there
  (cross-experiment statistics go to analysis families, D-5).

## Three kinds, each a thin wrapper (D-9)

| WP | kind | payload | result | library owner |
|---|---|---|---|---|
| A1 | `nk_landscape_v0` | `bits`, `length`, `k` | `score`, `contribution[]` (witness), `solved` | Daedalus (engine executor, NK tables seed-derived; k=0 must reproduce additive scoring) |
| C1 | `ca_density_v0` | `rule_hex`, `radius`, `n_cells`, `steps`, `n_ic`, `ic_density_set` | `accuracy`, `misclassified_ic[]` (witness), `spacetime_digest` | Herakles (EvCA verifier as a pure library) |
| B1 | `program_eval_v0` | `program`, `spec_id`, `step_budget` | `outputs[]`, `halted[]`, `steps`, `trace_digest`, `witness` (first failing input) | Proteus (foundry VM as a pure library) |

All three: stateful = False (C1's lattice state lives inside one execution),
BIT_DETERMINISTIC by construction, no defaults, no process spawning. C1 and
A1 are the two cheapest and are requested first; B1 when Proteus ships the
library.

## One new contract, scoped (WP-X2, Herakles C-4)

`external_backend_v0` is legitimate and is **not** requested until WP-P0 (a
two-day spike you would run with the operator's authorisation: build Avida
2.2 under MinGW, or a replicator-soup sketch, or compile
`herakles/specimens/spec-toussaint-exploration/derived/hct01.c`; run each
twice under one seed; compare digests) has produced a tool that passes the
double-run. The contract's reproducibility field is *measured* per
observation, never declared per tool (D-4).

## What Archaeon does on its side

Kind-generic spec builder with template-declared `outcome_rule` (WP-0e), so
your `random_walk_v0` and the three kinds above have a producer; per-family
null, control and frozen-random templates (PROPOSED, operator admits); the
novelty reserve in the draw (R1) — allocation is producer-side, never yours.

## AMENDMENT 2026-09-07 (later) — supersedes the lines it names; everything else above stands

Per the operator's amendment order (roadmap §D.7a; tests and acceptance in `archaeon/docs/expansion/WORK_PACKAGES.md`).


**Wording corrected.** "Passes the double-run" is withdrawn. Matching
re-executions are repeatability evidence in tested conditions; two matching
outputs do not prove determinism (WP-X2 tests X2-a…d: a deterministic backend
repeats; a nondeterministic one records a mismatch, never a silent downgrade;
matching twice and diverging on the third gets no universal guarantee;
build/config/environment changes invalidate prior qualification; canonicalisation
removes only declared non-scientific metadata; timeout/crash/partial output
keep honest records). Existing grade enums stay until owners agree a change.

**WP-0b tests:** 0b-a deterministic stateful walk under reset + constant seed
→ degenerate-by-construction, identical replay; 0b-b persist / changing seeds
follow declared behaviour, never auto-marked constant; 0b-c a constant score
across genuinely different trajectories is not by itself structural
degeneracy. Keep structural degeneracy distinct from observed zero variance;
the cross-execution `stateful` flag says nothing about state inside one
execution.

**WP-0c tests:** 0c-a identical execution inputs under labels A/B keep one
execution hash while member bindings record different arms; 0c-b queue arm,
sealed member arm, audit envelope and PEW design arm agree end to end;
omitted/conflicting arms fail at the boundary; 0c-c reassignment after
commitment refused, identical re-add idempotent; 0c-d the design commitment
precedes execution/outcome events and is traversable through typed
references, not manifest prose. Acceptance: one complete arm-bound round
trip with readback and ordering evidence.

**WP-0f tests:** 0f-a unknown fields, wrong types, missing required outputs,
non-finite scores, unsupported vector reductions → specific diagnostics;
0f-b A1/B1/C1 library and wrapper results match on shared fixtures
including errors, seeds, witness ordering, state initialization; 0f-c
declared witness/trace bounds respected with explicit truncation metadata;
`cli kinds` exposes the same contract validation uses. Note: Archaeon's
builder (WP-0e, done) carries a local declared copy of result fields for
the three live kinds and defers to `Kind.result_schema` the moment it exists.

**WP-P0 checks:** P0-a a clean documented build/run succeeds or records the
exact blocker per route (Avida version/build path; minimal in-process soup;
`hct01.c` where applicable); P0-b bounded repeated runs preserve inputs,
environment, digests, failures and measured costs; P0-c the report
distinguishes not attempted / blocked / failed / runnable / repeatable under
tested conditions and never upgrades the last to proved determinism. Avida
2.2 runnability is separate from fidelity to the 1.6 experiment; resolve
freeze restrictions before any activity they cover; the spike is not
permission for frozen population generation. Awaits the operator's cap
(proposed two days) and Ergon's consultation.

**WP-P1 tests** (after P0): P1-a a tiny manually computable population
follows the declared reproduction and resource update; P1-b zero mutation →
no mutation-generated novelty; disabling a declared interaction removes that
dependency with other treatment parameters explicit; P1-c parentage and
mutation edges reconstruct the sampled lineage, extinct and surviving
lineages traceable; P1-d identical inputs replay within contract;
scheduler/initialization changes reflected in provenance/identity; P1-e a
separate neutral-baseline comparison matches P3's demography and
assumptions — unlimited resources are not neutrality by label. Descriptive
execution may precede P3; claims depending on neutrality need it.

### Third amendment (operator, 2026-09-07) — additions within the same packages

- **WP-0c cycle.** Commit the design binding before execution; execute;
  record the terminal observation; complete attestation; then project
  downstream (PEW producer block, `design_hash`). A delayed projection must
  neither require its own completed envelope nor trigger another scientific
  execution (test 0c-e). You are the integrating owner; Daedalus supplies
  the client contract and a shared fixture; no three-way negotiation per run.
