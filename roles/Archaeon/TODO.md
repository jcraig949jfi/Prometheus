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

## 2026-09-06 — queue adoption + relation contract (design; NOT Stage 1)

- [x] Adopted viv.research_experiment_queue as the single canonical
      pre-execution register; archaeon.experiment_queue RETIRED not dropped.
- [x] Relation contract in the PROVENANCE partition, none of it hashed:
      family_id, arm_id, replication_of, candidate_set_id, request_key.
      Spec guard refuses notes/experiment_kind/world.name/policy/arm/family.
- [x] Cadence preserved on the new table (6/UTC-day/lane, 4h, DB-enforced,
      6-thread concurrency verified). Only a SELECTED row consumes quota.
- [x] Candidate registration: atomic, unchosen cancelled not deleted, and the
      count is DERIVED (viv.candidate_sets) -- there is deliberately no
      candidate_set_size column, so nobody attests a number they cannot know.
- [x] Vivarium's freeze trigger REPLACED (six checks verbatim + relation
      immutability). Flagged to Vivarium for review.
- [x] 25 non-scientific integration tests; 104 total.
- [x] Stage 0 preserved and still KILL. Not weakened, not re-tuned.

## BLOCKER found: Vivarium cannot produce an eligible claim-unit at any volume

runner.run() calls create_world() per row and records exactly ONE observation.
One row = one new world = one observation, no world reuse. S17 needs >3
observations WITHIN a world for lag-1 autocorrelation, so 1000 rows would give
1000 worlds of 1 observation and eligibility would still be zero. Requested a
declared `repeat` (an EXECUTION input, so inside spec_hash) plus a declared
per-repeat seed derivation. See roles/Vivarium/INBOX_ARCHAEON_QUEUE_ADOPTION.md.

## UNRESOLVED: how family/arm reaches the FOSSIL record

Stage 0 reads SFE, not the queue. SFE publishes only worlds.topology_group and
has no per-world arm field. Preference: topology_group := family_id plus an SFE
lineage_edge per world (relation='IN_ARM'). Needs Daedalus + Vivarium consent.
Until settled, a family fossilizes observations but not STRUCTURE, and Stage 0
would still KILL.

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

## Future candidates from the 2026-09-08 design-packet review (not scheduled)

- F-1  Coupled NK construction for a tightly PAIRED interaction ablation: same
       tables at k=0 and k>0 (add interactions without redrawing). v0 uses the
       ensemble comparison; reopen when a paired ablation claim is wanted.
- F-2  C3-mut: a separately labelled arm of single- and few-bit mutations
       around each recovered EvCA genome, same IC samples — can known
       computation tolerate change, fail distinctly, or vary in ways worth
       following. After C3-hist passes. (Adopted from the review as the next
       CA campaign.)
- F-3  A literal radius-0 executor for CA (v0 compiles centre-only rules into
       the 128-entry table instead).
- F-4  observation_interface = score_and_contribution series on NK (v0 series
       are score_only); and table-access as a declared, separately labelled
       interface if a question needs it.
- F-5  A particle / domain-boundary descriptor for CA trajectories, defined
       AFTER trajectories exist (the record in packet v2 §2.7 is built so the
       question can be asked later, not so it is answered now).
- F-6  Credential reissue route in SFE against an existing client_id
       (Daedalus); a seat that loses its token currently loses write access to
       its worlds permanently (Harmonia 2026-09-08).
- F-7  Vivarium heartbeat.started_at records first appearance of the worker
       id, not the current process (cosmetic; Vivarium's).
- F-8  Credential rotation (Mnemosyne's tracker, evidence_wiki/docs/CREDENTIAL_ROTATION_TRACKER.md): R-1 PEW credentials in git history (operator; must be simultaneous on M1 and M2), R-3 the archive prefixes (low urgency; local disk only, never committed). Not a research dependency.
- F-9  `binds_session` still absent from SFE's verify-anchor (Mnemosyne, unchanged): the wrong-session case rests on PEW's splice witness rather than an engine proof. Daedalus's, when scheduled.

## Added 2026-09-10 (issue day)
- [x] F-10 (operator): d3.v1 ADMITTED 2026-09-10 (D-20); pooled_within is the live default from the next tick. 2026-09-10
- [x] F-11 CLOSED 2026-09-10: Harmonia ruled signature_v0 FAIR and INERT at this scope; RELEVANCE_LICENSED stays False; contrast relabelled transport-only / order-only. 2026-09-10
- [x] F-12 DONE 2026-09-10 12:40: phase 2 ISSUED (cs-h1h0-1-p2, 73 rows incl. the degeneracy-check row) after Vivarium published the 11 artifacts. 2026-09-10
- [ ] F-13 (Archaeon): C3-2 readout when cs-c3-2 completes: ICC across the four IC samples, D3 over C3 (one row per rule), exact-symmetry mask identity on the 18 null rows. 2026-09-10
- [x] F-14 mostly DONE 2026-09-10: D-18 v1 APPROVED; rustup done by Techne; packet JSONs STILL the operator's paste. 2026-09-10
- [ ] F-15 (Archaeon): costs.reconcile joins on the DIGEST when the executor vector carries it (TRACKA-RECON-2). 2026-09-10
- [x] F-16 (Archaeon): D3 upper-fire dossier for Harmonia (item 5) delivered: archaeon/docs/h0h5/D3_LIVE_DOSSIER_2026-09-10.json. 2026-09-10
- [ ] F-17 (Harmonia): read the 15 LOWER fires that survive d3.v1 on the live corpus (dossier carries them under fires_v0 / v1 counts). 2026-09-10
- [x] F-18 DONE 2026-09-10 ~19:30: phase 2 COMPLETE (48 artifact rows under reservation on schema 8); readout with spec-hash dedup handed to Harmonia. 2026-09-10
- [x] F-19 DONE 2026-09-10 ~20:30: operator said ISSUE NOW; cs-h5-1 issued (256 rows). 2026-09-10
- [x] F-20 DONE by Vivarium 30e97ed94 (flags measured off the arrays). 2026-09-10
- [x] F-21 DONE 2026-09-10 ~14:00: random_076 re-issued as cs-c3-2-r1. 2026-09-10
- [x] F-22 BUILT 2026-09-10 21:15 (ARCH-01): campaign_c3_3.py + preflight + design; waits on Harmonia's 3b amendment and go, then the operator's word to issue (ARCH-02). 2026-09-10
- [x] F-23 DONE 2026-09-10 18:30: Vivarium's debit receipt landed (a733f0ad5); the 48 artifact rows re-issued as cs-h1h0-1-p2b. 2026-09-10
- [ ] F-24 (Archaeon): H5-1 readout when cs-h5-1 completes: live class map vs published (224 classes), H5 quantities collapsed to live classes (campaign_h5.live_class_map / h5_readout). 2026-09-10
- [ ] F-25 (Archaeon): after Daedalus issues the B1 grant, move readers to the API path, demonstrate parity with the direct-ledger read, retire the direct read. 2026-09-10
- [~] F-26 (Archaeon): D-6 pilot -- first allocated tick CONFIRMED 20:12 (active, established share, evaluate_bitstring); review packet for 2026-09-24 with Harmonia still to write. 2026-09-10
- [x] F-27 DONE 2026-09-11 04:00 (operator step 5): conformance gate wired fail-closed at submit/tick/enqueue with the record on every row; four-case demonstration receipt; Vivarium's half filed. 2026-09-11
- [ ] F-28 (Vivarium): wire the gate at the claim/dispatch boundary with the complete route set and the record on the load receipt; demonstrate; C3-3 waits. 2026-09-11
- [x] F-29 DONE 2026-09-11 05:00: D-23 workspace missive issued; guard + receipt wired; tick moved to a pinned worktree. 2026-09-11
- [ ] F-30 (every seat): D-23 clean-up reports (claimed/deleted canonical files, pruned worktrees, merged branches deleted, long-lived processes moved). 2026-09-11
- [x] F-31 DONE 2026-09-11 18:04: this pass ran on archaeon/pass-2026-09-11-1804 in Prometheus-worktrees/archaeon-pass-1804; archaeon-loop (merged) and Prometheus-archaeon (archaeon/v0, merged) are removable at close. 2026-09-11
- [ ] F-32 (Archaeon): ARCH-33 -- the tick's rule-10 park (96 consecutive non-WROTE records), then advance the pinned archaeon-tick worktree by a logged command. 2026-09-11
- [ ] F-33 (Archaeon): H5 readout on 256 rules once cs-h5-1-r1 completes (F-24 + ARCH-30 first read). 2026-09-11
- [ ] F-34 (operator): P0-a -- look at the one literal in keys.py that Eos's counts-only scan flagged; if it is not a credential, un-ignore keys.py (D-29). 2026-09-11
- [ ] F-35 (operator): rule on D-28 (producer-declaration invariant). 2026-09-11
