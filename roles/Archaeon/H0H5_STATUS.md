# H0–H5 status — compact, from receipts only

Maintained by Archaeon. Updated 2026-09-09. Design v0.1
(`roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md`). Every row
below is derived from a committed receipt; nothing is inferred from a plan.
Baseline: `archaeon/docs/h0h5/BASELINE_2026-09-09.json`.

## Iteration 1 (the gate for H0/H1 and every artifact-consuming kind)

| Item | Seat | Stage | Receipt | Next runnable action / blocker |
|---|---|---|---|---|
| Baseline audit | Archaeon | DONE | `archaeon/docs/h0h5/BASELINE_2026-09-09.json` | — |
| Authorized artifact resolution + cost events | Daedalus | DONE on a DEV engine (schema v8), NOT deployed; prod is schema 7 at f1e36c062 | `ef05397f2`; `deploy/CANDIDATE_BUILD.json` | deployment review is the operator's; Archaeon's reader guard moves to 8 on deploy |
| Loader vertical slice (integrating) | Vivarium | NOT REPORTED | — | the gate for H0/H1; needs Daedalus's read-path digest gate (dev) and Mnemosyne's outbox (main) |
| Typed reference index + idempotent publication | Mnemosyne | DONE (migration 011, 16/16 battery) | `dbfb6fe3a` | build X5 witness index when a witness exists |
| Executable qualification cycle | Harmonia | DONE (QR-1.0.0, AF-1.0.0 6/6, H4-ADAPTIVE-1.0.0) | `dd38720c0`; `roles/Harmonia/rulings/RULING_H0_H5_QUALIFICATION_2026-09-08.md` | H0 interaction needs 2x the blocks of the main effect (SE(I) = sqrt(2) SE(main), any rho); threshold frozen from the pilot's OBSERVED SD, never first |
| Producer cost receipts | Archaeon | NOT STARTED | — | next in lane after this status |

## Independent alphas

| Lane | Seat | Stage | Receipt | Finding / next |
|---|---|---|---|---|
| H1 substrate | Proteus | DONE | `790fb4803` | the existing channel expresses 3-input Boolean tasks (16 expressions, exhaustive parity vs an independent evaluator); NOT compiled as XOR x, ONE (VM NOT is bitwise); new interface `proteus.boolean3.v0`, frozen registry untouched; `genome_read` exposed. Next: Vivarium + Proteus `cegis_boolean_v1` |
| H2 alpha | Herakles | DONE as an OBSTRUCTION, not a null | `175b5da08`; `herakles/ca_stream/OBSTRUCTION.md` | the specified configuration (all-zero reset, one port, six density genomes) is provably INERT: every genome maps popcount ≤ 1 to 0. Instrument proven by controls. Four alternatives; recommendation alternative 1 (non-uniform reset at a declared density, relaxation time measured before the horizon). DECISION D-18, operator/designer |
| H5 alpha (kind) | Herakles | DONE | `feca5e688` | `eca_rule_eval_v1`, convention re-earned; 256 rules -> 224 equivalence classes at the 7-ring/8-step scope (32 redundant); next: Archaeon's decoders producer-side |
| H5 alpha (decoders) | Archaeon | NOT STARTED | — | 12-bit genome, 16 per rule, direct/balanced/scrambled, applied in the draw |
| H3 alpha | Archaeon | NOT STARTED | — | stream manifest + four policies offline; X8 bounds |
| Tools | Techne | DONE, on branch `techne/h0h5-tools-2026-09-09` | `b05a6920a` and earlier | z3-solver, hypothesis, ribs pinned by wheel hash; stitch_core pinned by wheel hash only (no matching upstream tag: NONE_AVAILABLE); DreamCoder at cb0e63f5c with submodules pinned, smoke BLOCKED with four measured blockers (DEV-T7); Stitch nuts-bolts fixture reproduced at zero tolerance (manifest DECLARED_NOT_RUN before the run); no pickle in the engine is a test; host RAM is the binding ceiling (~13 of 31.6 GiB free). Land on main. |
| H0 harness, H4 | — | NOT STARTED | — | H0 waits on the loader + cegis kind; H4 alpha loop may be built on synthetic tasks, its campaign waits on H4-ADAPTIVE-1.0.0 |

## Decisions pending (operator)

- **D-17 stitch_core licensing.** Two licences recorded unresolved by Techne;
  stitch_core has no upstream tag matching the pinned wheel. Archaeon's
  recommendation: development-only status; no artifact derived through
  stitch_core enters a scientific campaign until the licence is resolved and
  the source revision is pinned; Techne records the obstruction, not a guess.
- **D-18 H2 injection semantics.** Alternative 1 (non-uniform reset at a
  declared density; relaxation time measured before the horizon is fixed),
  as Herakles recommends; alternative 2 (k-port injection with k bounded
  below the majority threshold) as a separately labelled second arm later.
  A versioned design amendment, not a silent change.
- **Packet JSONs** (`prometheus-tool-acquisition-plan.json`,
  `prometheus-h0-h5-backlog.json`): still absent; Techne recorded DEV-T1/T2.
- **v8 deployment** of Daedalus's candidate build (review record in
  `deploy/CANDIDATE_BUILD.json`).
- **Harmonia's sizing rule for H0:** the interaction needs twice the blocks;
  the 5 pp threshold is a sizing decision frozen from pilot SD.

## Live producer

`ArchaeonTick` registered and ticking: 102 cadence decisions in the last day,
10 experiments completed in the last two days under the 6/day prod quota,
last completion 2026-09-09 19:12. Production engine schema 7.
