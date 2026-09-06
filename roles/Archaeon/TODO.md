# Archaeon — TODO

## 2026-09-05 — v0 built and qualified

- [x] Read SFE/PEW schemas before writing anything; reuse existing records
- [x] Six weak-signal detectors, thresholds explicit in `archaeon/config.py`
- [x] Eligibility census reported separately from firing
- [x] Deterministic ranking + fixed detector→probe table
- [x] Coverage-biased exploration fallback, reproducible from recorded seed
- [x] Cadence in PostgreSQL: 6/UTC-day, 4h apart, 3 independent mechanisms
- [x] Provenance schema answering all nine required questions
- [x] Negative-authority guard enforced at the write boundary
- [x] Synthetic fossils with paired structural controls
- [x] Calibration harness + power curves; four defects found and fixed
- [x] 55 tests passing, cadence tested against real PostgreSQL incl. 8-thread
      concurrency
- [x] End-to-end: first production proposal `AX-9ec1f5fc35ae` written from
      3241 real SFE fossils

## 2026-09-05 (later) — Proteus link

Earlier entry said player identity was blocked on Daedalus. That was wrong:
Proteus already publishes it, and the SFE binding already works.

- [x] `sfe.proteus_player.v0` chart: player = Proteus `organism_id`, bound via
      `artifacts.kind='proteus_player_manifest'` where `blob_hash ==
      organism_id`. Ambiguous worlds (>1 player) excluded and counted.
- [x] Real coordinate axes from the registry `resource_envelope`
      (`tape_words` 16..1024, `n_regs` 2..16, `genome_instructions` 1..64,
      `tick_budget` 16..1024) — replacing hash-like `spec.candidate`.
- [x] USE-A neutrality guard: bred organisms (generation > 0) refused in
      detector evidence, since D1/D4 are population comparisons and Proteus's
      mutation kernel carries an authored probability current. Precautionary
      today (all 64 specimens are generation 0); load-bearing once breeding
      starts.
- [x] Fixed a conflated blocked_reason: NO_PLAYER_FIELD / EMPTY_CORPUS /
      PLAYER_UNBOUND are now distinguished. The Proteus chart was reporting
      "no player identity" when it HAS identity and simply has no data.
- [x] 13 tests for the link; 68 total.

## 2026-09-06 (UTC) — STAGE 0 kill-gate: KILL

Reframed around Harmonia S14-S18. Ran the approved kill-gate; it killed.

- [x] Frozen S17 imported from a PINNED GIT BLOB (commit 21fbeffbb, blob
      0e2d654851ae), not reimplemented. Stdlib-only, so no dependency obstacle.
- [x] predictor_hash RECOMPUTED and verified == 0106e035868bbe10...
- [x] Positive control PASSES, so zero-eligibility is attributable to the
      corpus and not to the adapter.
- [x] Gate tested in BOTH directions (PASS on a synthetic supportive corpus);
      a gate that can only say KILL is indistinguishable from a broken one.
- [x] VERDICT KILL: 0 eligible claim-units under all three arm rules
      (TOPOLOGY_SPLIT / FORK / SPEC_ARM), insensitive to min_obs in 2..12.
      Groups with >=4 worlds have 0 scored observations; groups with scored
      observations cap at 3 worlds. S17 needs 2 arms x >=2 worlds.
- [x] Evidence class reported: 2934 ENGINE_WORK_RESULT, 307 CLIENT_ASSERTED.
- [x] OBSERVED/INFERRED/UNKNOWN written as VALUES; upstream_selection_history
      stamped UNKNOWN on every survey.
- [x] Discrepancy flagged to Harmonia (roles/Harmonia/INBOX_ARCHAEON_*).
- [x] Fixed two latent time-dependent cadence tests that failed once the run
      crossed 00:00 UTC. The cadence CODE was correct; the tests hard-coded a
      same-UTC-day assumption and were flaky ~4.5h in every 24.

STAGE 1 IS NOT BUILT and must not be until the gate passes.

## Gate-flip condition (what would make Stage 1 buildable)

One comparable group needs >=4 worlds carrying scored observations (two arms of
>=2), each with >=4 observations, AND >=2 such groups (an ordering over one unit
carries no information). Roughly 8 worlds x 4 observations, correctly grouped.
Cheapest routes: an explicit `spec.arm` on experiments, or a topology_group with
>=4 populated worlds. Neither needs new engine machinery -- both are properties
of how experiments are ISSUED.

## Next — blocked on other seats

- [ ] **Scored Proteus encounters** — the real blocker. 13 worlds carry a
      Proteus player; 1 has an experiment, 1 has an observation, and it
      carries no numeric metric (`outputs_digest`/`statuses`/`identity_gate`/
      `replay`). Only 2 of 64 specimens have crossed into SFE.
- [ ] **A world running TWO players.** No SFE world holds more than one
      distinct Proteus player, so D2 and D4 have no comparison unit to form at
      any threshold. One two-player world unblocks both.
- [ ] **QUEUE SEAM CONFLICT — the loop is currently broken.** The Vivarium
      seat opened the same day (branch `vivarium/v0-2026-09-05`, commits
      8b940a165 / 951036c57) and independently built its own queue. TWO live
      tables now exist:
          archaeon.experiment_queue        (Archaeon writes; 1 prod proposal)
          viv.research_experiment_queue    (Vivarium reads; 2 rows)
      Archaeon's proposals therefore go nowhere. NOT resolved unilaterally:
      changing another seat's live schema is an outward-facing decision.
      The two contracts are highly compatible, which makes this cheap to fix:
        - viv REQUIRED columns are created_by, source_reason, experiment_spec,
          spec_hash. Archaeon supplies all four (its `spec` -> `experiment_spec`,
          `proposal_id` -> `experiment_id`).
        - Archaeon's spec_hash already satisfies viv's
          CHECK ^sha256:[0-9a-f]{64}$ (verified against the live proposal).
        - source_evidence is jsonb on both, same provenance contract.
      Deltas: status vocabulary (Archaeon UPPERCASE + DONE vs viv lowercase +
      completed), and Archaeon's cadence columns (lane, day_ordinal, utc_day,
      the partial unique index and the gate) do not exist on viv's table.
      RECOMMENDATION: keep ONE table, Vivarium's, and move Archaeon's cadence
      mechanism onto it — cadence is a property of WRITING to the queue, and
      the queue should be one object. Vivarium's execution machinery (claim
      lease, heartbeat, event log, BEFORE UPDATE state-machine trigger) is the
      more intricate half and should not be re-implemented.

## Next — Archaeon's own

- [ ] Re-verify the SFE ledger hash chain on read, rather than assuming it
      (`SFE_ARCHAEOLOGY_SCHEMA.md` §2). Currently Archaeon asserts integrity it
      does not check.
- [ ] D1 power is ~0.34 at peak with a non-monotone curve (truncated above
      0.9σ by its own upper bound). Either widen the window or hand the range
      to D5 explicitly and document the handoff.
- [ ] Consider step-down / FDR instead of Bonferroni. Recovers power on
      correlated units; costs hand-auditability. Measure before adopting.
- [ ] A closing test that replays a stored `source_evidence` and reproduces
      the proposal — provenance is currently *complete* but not *proven
      sufficient*.
- [ ] Retention policy for `cadence_log` (it grows one row per cycle,
      including refusals, forever).
