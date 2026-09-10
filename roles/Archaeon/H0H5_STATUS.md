# H0–H5 status — compact, from receipts only

Maintained by Archaeon. Updated 2026-09-10 (evening). Review packet: `roles/Archaeon/REVIEW_PACKET_2026-09-10.md`. Delegation: `roles/Archaeon/prompts/2026-09-10_tracks/` (Tracks A-E from the operator's Chimera brief; three corrections verified: sqrt(6) counterexample, client_id retention gap, XOR-injection non-conservation). Design v0.1
(`roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md`). Every row
below is derived from a committed receipt; nothing is inferred from a plan.
Baseline: `archaeon/docs/h0h5/BASELINE_2026-09-09.json`.

## Iteration 1 — COMPLETE on every seat (2026-09-09); the H0/H1 gate is open

| Item | Seat | Stage | Receipt | Next runnable action / blocker |
|---|---|---|---|---|
| Baseline audit | Archaeon | DONE | `archaeon/docs/h0h5/BASELINE_2026-09-09.json` | — |
| Authorized artifact resolution + cost events | Daedalus | DONE on a DEV engine (schema v8), NOT deployed; prod is schema 7 at f1e36c062 | `ef05397f2`; `deploy/CANDIDATE_BUILD.json` | deployment review is the operator's; Archaeon's reader guard moves to 8 on deploy |
| Loader vertical slice (integrating) | Vivarium | **DONE** on a dev engine (127.0.0.1:8899, schema 7); 364 tests, 24 real boundary executions | `959d35043` + `01376aa87`; `roles/Vivarium/H0H5_ITERATION1_RECEIPT_2026-09-09.md` | GATE OPEN for H0/H1. `artifact_probe_v1` with slot `failure_inputs`; ten ordered preflight rejections; kind called with frozen bytes and no client; consumed digest changes the seal, locator does not; budget exhaustion a distinct status; publish reports write_outcome / recorded_in_sfe / indexed_in_pew separately. Enforceable: artifact_bytes (debited before fetch), wall_seconds; measured: cpu, peak memory, fetches, items; unavailable: gpu. Limits filed: engine-side cost events absent (Daedalus C4-3) so vectors cannot yet reconcile; sfclient cannot pass expected_blob_hash and register() discards the engine-issued client_id (Daedalus). Next: `cegis_boolean_v1` with Proteus. |
| Typed reference index + idempotent publication | Mnemosyne | DONE (migration 011, 16/16 battery) | `dbfb6fe3a` | build X5 witness index when a witness exists |
| Executable qualification cycle | Harmonia | DONE (QR-1.0.0, AF-1.0.0 6/6, H4-ADAPTIVE-1.0.0) | `dd38720c0`; `roles/Harmonia/rulings/RULING_H0_H5_QUALIFICATION_2026-09-08.md` | H0 interaction needs 2x the blocks of the main effect (SE(I) = sqrt(2) SE(main), any rho); threshold frozen from the pilot's OBSERVED SD, never first |
| Producer cost receipts | Archaeon | DONE (code) | `archaeon/producer/costs.py`, `tests/test_h0h5_producer.py` | CostEvent with unique id, attempt, stage, refs, environment, resource vector {quantity, unit, method, enforcement_class, scope}; unavailable is not zero; roll-ups reference children and never sum peak memory; counterfactual attribution under a frozen reuse horizon charges the physical cost once; reconcile() names the absent engine side (Daedalus C4-3). Next: wire into tick source_evidence and the H1/H3 producers |

## Independent alphas

| Lane | Seat | Stage | Receipt | Finding / next |
|---|---|---|---|---|
| H1 substrate | Proteus | DONE | `790fb4803` | the existing channel expresses 3-input Boolean tasks (16 expressions, exhaustive parity vs an independent evaluator); NOT compiled as XOR x, ONE (VM NOT is bitwise); new interface `proteus.boolean3.v0`, frozen registry untouched; `genome_read` exposed. Next: Vivarium + Proteus `cegis_boolean_v1` |
| H2 alpha | Herakles | DONE as an OBSTRUCTION, not a null | `175b5da08`; `herakles/ca_stream/OBSTRUCTION.md` | the specified configuration (all-zero reset, one port, six density genomes) is provably INERT: every genome maps popcount ≤ 1 to 0. Instrument proven by controls. Four alternatives; recommendation alternative 1 (non-uniform reset at a declared density, relaxation time measured before the horizon). DECISION D-18, operator/designer |
| H5 alpha (kind) | Herakles | DONE | `feca5e688` | `eca_rule_eval_v1`, convention re-earned; 256 rules -> 224 equivalence classes at the 7-ring/8-step scope (32 redundant); next: Archaeon's decoders producer-side |
| H5 alpha (decoders) | Archaeon | DONE (producer side) | `archaeon/producer/h5_decoders.py`, tests | direct / seeded-balanced / seeded-scrambled decoders, all total on 4,096 genomes with exactly 16 per rule (checked exactly, broken decoders refused); matched starts by seeded preimage draw; one uniformly chosen bit flip; accessible-variation probe on independent parents shows the ACCESS difference (direct ≤ 8 distinct neighbour phenotypes because the 4 high bits are inert; balanced > direct) with catalogue and multiplicities identical; collapses to Herakles's equivalence classes. Provenance rides in the draw; the evaluator receives only the rule. Next: a `eca.decoder_probe.v0` template family and the H5 alpha comparison as a human-issued batch once Vivarium wraps `eca_rule_eval_v1` |
| H3 alpha | Archaeon | NOT STARTED | — | stream manifest + four policies offline; X8 bounds |
| Tools | Techne | DONE, on branch `techne/h0h5-tools-2026-09-09` | `b05a6920a` and earlier | z3-solver, hypothesis, ribs pinned by wheel hash; stitch_core pinned by wheel hash only (no matching upstream tag: NONE_AVAILABLE); DreamCoder at cb0e63f5c with submodules pinned, smoke BLOCKED with four measured blockers (DEV-T7); Stitch nuts-bolts fixture reproduced at zero tolerance (manifest DECLARED_NOT_RUN before the run); no pickle in the engine is a test; host RAM is the binding ceiling (~13 of 31.6 GiB free). Land on main. |
| H0 harness, H4 | — | NOT STARTED | — | H0 waits on `cegis_boolean_v1` only (loader done); H4 alpha loop may be built on synthetic tasks, its campaign waits on H4-ADAPTIVE-1.0.0 |

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
  `deploy/CANDIDATE_BUILD.json`). Vivarium's slice ran against schema 7 on a
  dev engine; the read-path digest gate it needs in production is in v8.
- **Daedalus C4-3:** engine-side cost events do not exist yet, so Vivarium's
  resource vector and Archaeon's producer receipts cannot be reconciled
  until they do (Vivarium's inbox to Daedalus, 2026-09-09).
- **Harmonia's sizing rule for H0:** the interaction needs twice the blocks;
  the 5 pp threshold is a sizing decision frozen from pilot SD.

## Also on branches (not main)

- Vivarium `e43a6c7f2`: `ca_density_v0` wraps herakles/evca; six genomes reproduce golden exactly; both success masks measured; a period-2 fixture separates at_T from stable. Branch C can run its first corpus once C2 templates are admitted.
- Aporia deck (`3b1fb8a0f`, vivarium branch): four of six hypotheses untested in the literature as posed; H2's encoding confound published (Glover et al. 2024); nearest H3 test found no QD advantage (Chen 2026); H4 precedent only vs a tuned baseline.
- Techne inbox to Archaeon (`f6acabefb`): pyribs GridArchive is first-writer-wins on exact ties; z3 separates timeout from rlimit exhaustion, use rlimit for cross-host repeatability; stitch_core ships NO licence in any artifact (export blocked, internal use continues).

## Live producer

`ArchaeonTick` registered and ticking: 102 cadence decisions in the last day,
10 experiments completed in the last two days under the 6/day prod quota,
11 completed since registration, all published to PEW (production encounters 5458 -> 5469). Production engine schema 7. D3 on the live corpus: 77/93 regions eligible (median n=40), 30 fire (28 LOWER); unadjudicated detector output, no interpretation offered.

## Track B ready in Archaeon's lane

`archaeon/producer/campaign_c3.py`: 150 rows (6 historical, 6 baselines incl. constant-output and four centre-only rules compiled into the 128-entry table, 18 transform nulls, 120 random), 600 observations, one seed_root so every rule shares four IC samples; `--check` reports `kind_registered: false` in this tree until ca_density_v0 lands on main, then validates each spec with Vivarium's validator; `--issue` is the operator's act.
