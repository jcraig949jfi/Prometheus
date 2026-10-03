# Phase 2-B intake ledger (carried across the M1 drain)

Recorded by Aporia under the operator directive of 2026-10-03, section 1. Each item becomes part of the owning seat's
Phase 2-B re-entry campaign. None is an emergency repair.

## Holds and dependencies

- **C4 foreign visible family (Cosmos).**
  - Original assignment: Aporia #1139 (2026-09-30T17:4xZ) to Theseus.
  - Re-ping: #1282 at 2026-10-03T11:36Z. ACK is due within the next heartbeat window, about 13:06Z.
  - Blocked: Cosmos (C4 review cycle, #1233), Ananke (R-STAT final; interim ded6f5729), Bellerophon (R-MECH final;
    interim 164df3cdd).
  - Dependency chain: Theseus family commit -> Cosmos C3 publication (V1-V5 dry run PASS, not executed) -> reviewer
    finals -> RECONCILIATION_v0.2.md -> operator build decision.
  - If Theseus does not ACK: status `HOLD_REHOME`, reassigned cleanly at Phase 2-B. Do NOT give it to Achilles, and do
    not launch a new science seat for it before the reset.
  - **Status: ACKED** by Theseus at 11:42Z (#1301), with an independence statement. The C4 chain is live; no
    HOLD_REHOME.

## Defect reports

### Epimetheus #1246

Source: docs/phase3/design/OPUS-5.5/salvage/NEW_DEFECTS.md. Owners must reproduce before acting.

**GLOBAL / MEDIUM.** Routed to Archaeon (#1283):
- comms/manifest.py: short-binary hash collision;
- comms/identity.py: null db identity accepted;
- archaeon/workspace.py: receipt() fails open on git errors.

**Phase 2-B / LOW** (owner verification):
- Proteus VM: `st['ticks']` never advanced. Owner: the Proteus / Archaeon Campaign 6 evaluators.
- Harmonia qualification_rules.py: t_crit rounds df up (anti-conservative). Owner: Harmonia.

**Seat-local** (Phase 2-B owner verification, per NEW_DEFECTS.md):
- Nemesis: cheatlib chance_floor defaults.
- Hecate: shadow_decisions q().
- Ergon: p3_analyze decide() truncates unequal arms.
- Charon: c1c2 C2 is 0-based.
- Ananke: explib certify_gate attainability; rng.py 32-bit state.
- Proteus: prng seed_from not injective; crucible spectral_gap.
- Tyche: lexicase tests pass for random selection.
- D-5: fast/reference equivalence covers <= 2 inputs.
- The rest of the list in NEW_DEFECTS.md.

### Nestor #1207 sweep candidates

Sent by Nestor directly to Bellerophon, Archaeon, Ananke and Cosmos. They verify at re-entry.

## Do-not-dispatch

- **X-TASK-GATE** (Nestor; frozen 62d30e443): `DO_NOT_DISPATCH_AS_FROZEN`.
  - The stage-0 planted positive cannot exercise CD, the ruler that every stage-1 verdict uses. No execution occurred.
  - Required amendment (Nestor intake): add a stage-0 PAIR arm with a planted copier+task-competent genome, plus a
    reachability check. If no such genome can be built, that is itself the finding.
  - Erratum: roles/Nestor/campaigns/npe-frontier-2026-09-30/x_task_gate/ERRATA_2026-10-01_DO_NOT_DISPATCH_AS_FROZEN.md

## Pending scientific rulings -> Harmonia at Phase 2-B relaunch

- **Hecate C1-C8** (#1213, revised in #1238). Hecate withdrew its own APPLY recommendations after a red-team; K4 was
  added to the contested set. Rule per READING across every decision it touches. Hecate keeps the question set unchanged:
  roles/Hecate/... RULING_REQUEST_C1_C8.md plus addendum.
- **Nyx packets waiting on Harmonia** (Nyx #1316: its queue is exhausted, it holds idle):
  - #1270 ASAL replication 001: I1-I5 plus the native column on M2.
  - #1069 Avida ancestry: 3 days, no ACK.
  - #1315 MECH-POET-PATA-EC-001: frozen blind ea2adf88; numpy-only, seconds on any host.
  These are Harmonia's first adjudications at relaunch. No reassignment: packet author and adjudicator stay separate.

## Custody incidents -> Harmonia / evidence owner after Phase 2-B seating

- **Dionysus #1247** (2026-10-01).
  - An untested search exclusion displayed one line (line 18, cut at 250 characters) of
    evidence_wiki/gold/holdout_corpus_v1.jsonl to a read-only salvage worker.
  - Dionysus redacted that worker's one-sentence description, and nothing was used.
  - Other holdout-named paths were touched by counts or names only.
  - Table: docs/phase3/design/FABLE-5.1/salvage_reports/00_SEARCH_RULE_INCIDENT.md.
  - No immediate action was requested. Mnemosyne (evidence owner) is parked and is not woken for this.

## Census

- Achilles's docs/fleet/fleet_state.json is the canonical fleet census (operator, 2026-10-03).
- ops/fleet/CENSUS.json is historical.

## Aporia registrar duty (Phase 3, C-004-OP2)

- Palamedes #1326: an append-only custody store locator is needed before C-004-T020 (not urgent).
- Proposed: a hash-chained, append-only Postgres table on M1.
- Pending operator confirmation, because it is a custody mechanism.
