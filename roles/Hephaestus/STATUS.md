# Hephaestus status

Currency: 2026-09-11 11:55 UTC (adoption pass). Plain language. Update at
least every four hours of activity. Each status line says which of
PRESENT / ACTIVE / PRODUCTIVE / VALID it asserts.

## Where the seat is running

- Host: the Postgres host (M1), not M3. Worktree
  F:\Prometheus-worktrees\hephaestus-base-role, branch
  hephaestus/base-role-adopt-2026-09-11, base SHA 7466bd6ac.
- Base role adopted this pass (roles/base-role at 7466bd6ac). Boot order
  in roles/Hephaestus/RESPONSIBILITIES.md.

## The queue (hephaestus/mint_queue/) -- PRESENT, ACTIVE from this pass

- 4 packets. MINT-0001 DORMANT (Level-1 composition + representation
  adapter, operator ruling 2026-09-01; candidate stays CANDIDATE-PRODUCED
  in its history, never admitted). MINT-0002 SCRAPPED. MINT-0003 DORMANT
  (PARSER gap). MINT-0004 DORMANT (SEARCH_ROUTING).
- READY-FOR-DEEP-MINT: 0. In APPRENTICE-TESTING: 0.
- No events on any packet between 2026-09-01 and 2026-09-11 (the seat
  was idle; recorded as DORMANT for that span in
  roles/base-role/MONITORS.md).
- No scheduled tasks exist for this seat on this host (verified
  2026-09-11 with Get-ScheduledTask); none should (charter Addendum 4).

## Specimen 3 (Q045 unreachable class) -- ACTIVE, result pending

- Preregistered 2026-09-01 (hephaestus/prereg/PREREG_Q045_specimen3_2026-09-01.md),
  runner committed unrun. First execution 2026-09-11 from this worktree.
- Two tooling corrections on first execution, both before any target was
  evaluated and neither touching a preregistered rule: (1) the canonical-
  order sort compared S and V signatures and raised TypeError; now sorts
  V-typed behaviours only (S were never eligible); (2) stage timing to
  stderr and `deep_seconds` in the result, so the prereg's 10-minute
  clause for R_imp8 is measurable.
- Measured so far (stderr log): R_full5 3,319 signatures (all types) from
  9,134 candidates; R_imp5 1,546 from 4,406; R_imp8 63,050 from 315,899
  candidates, budget NOT exhausted, 8.0 s. The 10-minute clause does not
  fire; depth 8 stands. The per-target gauntlet (30 targets x 4 arms x
  300,000 budget) is the slow stage: more than 2.5 minutes per target.
- Result file: hephaestus/closure_results/q045_lost_class.json (written by
  the program with the workspace receipt). P1-P5 are read only from that
  file, in the readout, after it exists.

## The forge's engines -- PRESENT, not re-verified this pass

- +11pp R3 / +32pp R4 last reproduced 2026-08-19 (ABLATION_CARD). Not
  re-run from a worktree yet (HEPH-20).
- Cheap-model shelf (nvidia NIM, ollama) last verified on M3 2026-09-01;
  UNVERIFIED on this host (HEPH-04).

## Blockers

- Base-role self-test red on origin/main 7466bd6ac for a reason in
  Archaeon's lane (comms seed manifest hashed CRLF bytes); reported via
  comms, roles/Hephaestus/prompts/2026-09-11_manifest_crlf/ARCHAEON.md.
- Independent held-out generator for MINT-0001 still does not exist
  (Aporia TRANSFER-1 / Charon); HEPH-15.

## Next executable action

Read q045_lost_class.json when it lands; write the readout beside the
prereg (HEPH-06); commit rows + readout together; regenerate handoff/rank
(HEPH-03); review packet.
