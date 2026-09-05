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

## Next — blocked on other seats

- [ ] **Player identity in SFE specs** (needs Daedalus). Until then D1/D2/D4
      are eligible only on synthetic corpora. This is the single highest-value
      unblock: it takes the suite from 3/6 to 6/6 on production data.
- [ ] **A chart over a real parameter.** `spec.candidate` is a hash-like
      integer, so coordinate adjacency is close to meaningless and D2/D6 are
      much weaker on live data than synthetically.
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
