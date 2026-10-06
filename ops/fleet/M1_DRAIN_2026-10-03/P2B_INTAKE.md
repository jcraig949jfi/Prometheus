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

## Updates (2026-10-04)

- **Aether (#1389): READY.** E-012 closed as DYNAMIC_COUPLING_REQUIRED (rcv_sfz 6/128, exactly on the boundary; record
  ops/campaigns/C-002/E-012/RESULT.md @ 1d2d374e8). Promexec round 2 still waits on the operator's install of 3cf32a64.
  Its Phase 2-B first campaign stays as in the manifest: the 10k-tick rcv_add/rcv_str falsifier plus one alternative
  energy regime.
- **Aphrodite (#1395): already running Phase 2-B autonomously** under an operator directive of 2026-10-04
  (ops/threads/TH-P2B-APHRODITE-V2B.md): C-006 Beta-01, 12 alternating DEV/TEST windows on M4. Per that thread, CWOs
  may delegate to Aphrodite but do not activate it. Aporia does not dispatch it. Recorded only.
- **Palamedes (#1361):** custody store v1.0.2 adopted into the C-004 contract.
- **Aether (#1396): now ACTIVE and autonomous** under the operator's Phase 2-B directive TH-P2B-AETHER-V2B. Recorded
  only, the same as Aphrodite.
- **Control-plane defect (Aphrodite #1404, owner Achilles / PrometheusWorker):**
  - Generic-worker attempts return only output hashes.
  - The files stay in /home/jcraig/prometheus-worker/results/ on the worker host, and the owning seat has no designed
    path to fetch them: no upload or results branch, and ssh from M4 fails host-key verification.
  - This blocks science sharding on the fleet; the first case is Aphrodite T51.
  - Options listed by Aphrodite: commit outputs <= N MB, add an artifact table on M1 Postgres, or distribute SSH keys.
  - Sent directly to Achilles; not duplicated by Aporia. LOW, and not blocking Aphrodite.
- **CLOSED (Archaeon #1408):** the three GLOBAL/MEDIUM control-plane defects now fail closed (f188be013, on main):
  comms manifest short-binary hashing, comms identity null db, workspace receipt. The #1148 Postgres keepalive fix is
  also on main (6277c59ab).
- **Control-plane defect (Aether #1439, owner Odysseus/Fabric; cc Achilles):**
  - ubu001's Fabric workers (.a, .b, .sci) have shown "online" while dead since 2026-10-02 10:37: last_seen is stale
    and they claim nothing. This is the stale-instance class DEF-ODY-017. It probably coincides with Achilles moving
    ubu001-003 to PrometheusWorker on 10-02.
  - 28 Aether tasks sat unclaimed and were cancelled; Aether fell back to native R3 on BUCKKEEP.
  - Impact: any seat relying on Fabric python.numpy will hit this.
  - Needs: restart, or explicit retirement of the Fabric v0.2 workers in favour of PrometheusWorker, plus liveness from
    last_seen rather than from status. Already sent to Odysseus.
- **Aether host move (#1554, #1555, #1559, 2026-10-05):** BUCKKEEP -> M2 (GPU), done as a single-writer handoff. This
  supersedes the placement-matrix row (BUCKKEEP); M2 RAM contention, already noted, now also includes Aether.
- **TECHNE-123A (#1558; operator directive 8 to Techne):** Open-Oasis qualification on RunPod, $10 cap, 12 h ceiling.
  Techne asks Aether for a credential-safe launch path; Aporia is cc only. This is coordination between those two
  seats, so Aporia takes no action.

## Phase 2-B launches observed on comms (2026-10-05, operator-directed; recorded, not dispatched by Aporia)

| Seat | Host | Order | State at ~11:40Z |
|---|---|---|---|
| Ananke | M1 GPU (Fabric lease skullport:gpu0 lse-659cff0ca264) | operator science order PTE-C2A Search-Limit Localization (34bcebe4b) | prep; freeze <= 14:50Z, then production <= 12 h |
| Nestor | BUCKKEEP CPU (C:/Prometheus-worktrees/nestor-buckkeep-2026-10-05) | X-TASK-GATE v2 (roles/Nestor/prompts/2026-10-05_xtg_v2_science_order/) | DONE: INSTRUMENT_UNREACHABLE (TRANSIENT_ONLY); Stage 1 not run (7a521dc91) |
| Aether | M2 (moved from BUCKKEEP) | ER01 | production launched 11:30Z, 38 units, about 9.1 h (prereg 7ce2a58b9) |
| Techne | M3, flying RunPod A40 | TECHNE-123A, directive 8 ($10 cap) | production in flight; key held on a physical carrier, not in git |
| Aphrodite | harry1 (M4) | C-006 Beta-01 T09 | frozen; compute hold until 12:45Z |

- **X-TASK-GATE:** the original freeze 62d30e443 stays DO_NOT_DISPATCH_AS_FROZEN and was not executed. v2 superseded
  it under an operator order, and the v2 result is above.
- **Nestor's note:** Nestor says the operator ruled that the historical M1-drain and pm-data items do not block this
  experiment.
- **Aphrodite C-006 Beta-01 CLOSED (#1606, main 56e5e2bd5).**
  - T12 replicated on fresh, unexposed seeds: IMPROVER_REPLICATED_POSITIVE (60 vs 20 held-out families, 5/0/3,
    sign-flip p 0.031 = the attainable minimum, NULL gate 0/8).
  - The effect is carried by abstraction-only candidacy. The historical improver selects memorisation in 4 of 8 seeds.
  - First replicated R7, tier 2. Not R8, not RSI.
  - Close synthesis: a higher-power replication should come before any Tier-4 bridge.
  - The seat is idle pending operator direction.
- **Techne:** READY since 12:10Z. The manifest's recommended first campaign, TECHNE-131 (successor scorer plus packet
  validator hardening), is offered to the operator and awaits a go or no-go.
- **Ananke PTE-C2A CLOSED (#1619, #1621; packet roles/Ananke/pte/c2a/RESULT_PTE_C2A.md, main b3b2863fd).**
  - Production 362/362, 0 stop flags, positive control alive.
  - RELAY-mh and FLIP are both SEARCH_LIMIT_SUPPORTED: 8/8 cells located in search; BASE 1/48 and 0/48; PSEED 16/16
    each.
  - Neither W0 nor M32 rescues search; every upper 95% bound on the gain is <= .13.
  - Post-hoc, labelled descriptive: all 15 KSEED "recoveries" were neutral edits, and 0/81 broken starts recovered.
    KSEED should be conditioned on a broken start; recorded as a prereg defect.
  - Proposed next: broken-start KSEED plus B4X or STEP at the same 8 cells. Needs operator authority. The M1 GPU lease
    should now be released.
- **Aether ER01 CLOSED (#1630; Aether/V2B/ER01/RESULT.md @ bae71a02b).**
  - 38/38 units, 9.04 h on M2, technical PASS, deterministic.
  - Disposition: MOBILE_BUT_TRIVIAL. The frozen medium's extent does not change with energy: late frozen fraction about
    0.987, and 37.3% of sites are ever changed, in every regime. Energy scales only the flicker rate of the same ~1.2%
    minority, and those flips revisit recent states.
  - Proposed next (TH-009, not started): one law change in which a write re-aims the writer. Needs operator authority.

## 2026-10-06 00:35Z check (msgs 1647-1664)
- Palamedes #1653 + #1656 (C-004-T045): 8 custody rows registered (34-39 STAGE_RECORD @48f9529b4; 40 EVIDENCE_MANIFEST,
  41 RUN_INVENTORY @0e1943bff). All blob hashes cross-checked, verify chain_ok rows=41,
  head 216829137ae611ea2704f2a6adb381377b7ffa2599c411d790053d314aaf834f. Reply #1664.
- Ananke PTE-C2B: production launched under operator order (freeze c699838cf). Review request #1659 has NO in-scope
  reviewer (Argus declined; Harmonia HOLD; Aporia holds no scientific authority). Surfaced to operator: P2B_SUPPORT item.

## 2026-10-06 01:34Z check (msgs 1665-1671)
- Aether AIM01 (= TH-009, write re-aims the writer), operator order roles/Aether/prompts/2026-10-05_aim01. M2,
  freeze 1ec63c053 (aether/mwo0001-2026-09-28); Flights 1+2 technical PASS; production 49 units launched 01:16Z, ~6 h.
  Non-blocking review #1668 is UNASSIGNED (same gap as PTE-C2B #1659).
- Aphrodite BETA-02 (C-007, operator directive 2026-10-05): E1/E2 frozen + launched on HARRY1; E3 (R8) gated;
  prereg main 122b0c8cb.
- Phase 3 traffic (Palamedes -> Pallas C-004-T041; Pallas heartbeat/claim): no Aporia action.

## 2026-10-06 05:34Z check (msgs 1672-1680)
- Aphrodite BETA-02 #1680: E1 REPLICATED (162 vs 63, 16/0/6, p 1.5e-5); E2 names memorisation exclusion as the
  mechanism; gate passed, so E3 (R8) launched per prereg. Self-reported; no external review yet.
- Aether AIM01 production 36/49 (#1679). Others: Phase 3 traffic and heartbeats only.

## 2026-10-06 06:20Z check (msgs 1681-1687)
- Ananke PTE-C2B COMPLETE (#1683/#1684): 248/248 jobs, 0 integrity flags, 64/64 B4X prefix gates PASS, 5.55 h.
  GPU lease released, schtasks deleted. Packet roles/Ananke/pte/c2b/RESULT_PTE_C2B.md (main 1ac44021c).
  RELAY-mh = MIXED (rarity barrier, responsive to budget); FLIP = LANDSCAPE_BARRIER_WITH_SPARSE_EXCEPTIONS
  (path barrier). External review still unassigned. Proposed next (FLIP operator/representation test + RELAY
  budget curve) needs operator authority; NOT started. M1 GPU is free again.
- Aether AIM01 44/49. Phase 3: Palamedes -> Argus C-004-T046 (claimed), Pallas T048 notice; no Aporia action.

## 2026-10-06 06:29Z check (msg 1688)
- Ananke START C2BX (RELAY B4X continued to 8x/16x budget, stops at 16x) + PTE-C2C (FLIP 2x2: frozen vs block
  operator x BASE vs graded stepping stone, 8 searches/cell/arm, fresh seeds). Operator order verbatim at
  roles/Ananke/prompts/2026-10-06_c2b_close_c2bx_c2c/ (64dad7553). PTE-C2B CLOSED. Operator ruled external review
  = non-blocking audit. M1 GPU busy again: lease skullport:gpu0 lse-d5be3b4e224c (not in ~/ananke_runs/leases).

## 2026-10-06 07:34Z check (msgs 1689-1694)
- Aether AIM01 FINAL (#1692/#1693, eee3d9003, Aether/V2B/AIM01/RESULT.md): INITIAL_GEOMETRY_DOMINANT under L0;
  re-aim CAUSAL (+0.37/+0.45/+0.39 EFFECT support, 8/8 seeds x 3 densities, persistent); frozen
  REAIM_NONTRIVIAL_CANDIDATE label NOT ROBUST (non-AIM novelty 0.099-0.105 at the 0.10 floor; prereg instrument
  defect recorded). Proposed next (operator's call): measurement-only L1 non-AIM vs turnover-matched flicker
  null. Review #1668 unassigned. NOT started.
- Ananke C2BX + PTE-C2C frozen 2d2c1bed3, launched 152 jobs (#1694), operator order 64dad7553.
- Phase 3 (operator-level, not Aporia's to route): Pallas #1691 runs on Opus 5.5 (Q2) and will not claim
  C-004-T048 (Q3, no downgrade). Options: fresh Fable 5.1 Pallas session / Dionysus fallback OP-3 / relabel to Q2
  (Pallas advises against). Argus T046 INTEGRATION_READY.

## 2026-10-06 09:34Z check (msgs 1695-1697)
- Aether AIM02 (matched-flicker richness test, measurement only) under operator order (Aether cites order s15 and
  the operator disposition REAIM_SUPPORT_CONFIRMED__NONTRIVIALITY_OPEN). AIM01 integrated to main 9bffb1f7c.
  Frozen 619dd3b25 (branch aether/aim02-2026-10-06); production 65 units, ~80 min, on M2.
- Aphrodite BETA-02 CLOSED (#1696, main 201d1a873): E1 replicated; mechanism = memorisation exclusion;
  R8 = NO (an inherited library transfers capability, 104 vs 32 families, but not next-generation improvement). Tier 2.
  Seat IDLE pending operator direction.
