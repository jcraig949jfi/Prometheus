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

## Next — blocked on other seats

- [ ] **Scored Proteus encounters** — the real blocker. 13 worlds carry a
      Proteus player; 1 has an experiment, 1 has an observation, and it
      carries no numeric metric (`outputs_digest`/`statuses`/`identity_gate`/
      `replay`). Only 2 of 64 specimens have crossed into SFE.
- [ ] **A world running TWO players.** No SFE world holds more than one
      distinct Proteus player, so D2 and D4 have no comparison unit to form at
      any threshold. One two-player world unblocks both.
- [ ] **Vivarium consumer** — claim/complete semantics against
      `archaeon.experiment_queue`; the consumer columns are unexercised.

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
