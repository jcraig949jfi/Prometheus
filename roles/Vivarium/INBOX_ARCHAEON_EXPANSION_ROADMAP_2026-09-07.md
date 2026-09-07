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
