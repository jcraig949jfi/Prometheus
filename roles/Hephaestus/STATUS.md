# Hephaestus status

Currency: 2026-09-11 15:15 UTC (rulings applied; controls ALL_PASS; v2 executed, kill fired on v1's shift column). Plain language. Update at
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

## Specimen 3 (Q045 unreachable class) -- EXECUTED, VALID as far as this seat can say

- Run of record: run 2, 2026-09-11, 1,450.6 s, rows in
  hephaestus/closure_results/q045_lost_class.json, readout in
  hephaestus/prereg/READOUT_Q045_specimen3_2026-09-11.md.
- LOST 18 OPERATOR / 2 INCONCLUSIVE(B did not reach) / 0 SEARCH_ROUTING;
  A0 and A2 witnesses and aliases 0/20; C witness 20/20, robust 20/20.
  CONTROL 10/10 SEARCH_ROUTING at A0, robust. P1 TRUE at the line
  (18/20 = 0.90, n = 20); P2, P3 TRUE; P4 TRUE by the prereg sentence
  (coded predicate was mis-encoded, both reported); P5 FALSIFIED.
- Three defects in the committed-unrun runner and two in the frozen
  gauntlet were found and corrected at first execution, before any
  verdict was read; one (bool coercion) would have inverted the result.
  The boolean specimens' committed results are reproduced exactly by the
  corrected code. CALIBRATION.md and the readout carry the detail.
- Same-author reading (conflict declared). Not admitted anywhere.

## Gauntlet controls on the boolean specs -- EXECUTED, ALL_PASS (HEPH-09/10)

- hephaestus/prereg/READOUT_gauntlet_controls_2026-09-11.md. Negative (random
  target: 0 witnesses in A1/A2/B on both specs), positive (named depth-1/2
  expressions found at their depth), cheat (injected kernel appears at depth 1;
  on consistency_check the frozen arm had 0 witnesses and the decoy is the only
  one). Same-author. Establishes discrimination on these two specs only.

## Q045 v2 (Z7 shift) -- EXECUTED (instrument characterization, ruling 1)

- Preregistered alone at 3fdb32f8a. V2-P1, V2-P2 TRUE (identical witnesses
  and classes; certified programs robust in Z7). V2-P4 kill FIRED: 4 v1
  false negatives, because v1's shift inputs (entry 6) were outside Z6 and
  permuting ops did not reduce them. Target-level coordinates survive: C
  robust 20/20, CONTROL robust 10/10. 43 arm-level decreases (86 witness-
  level losses), each Z6-exhaustive-equal yet Z7-different; two identity
  families by inspection (x^3=x; 6x=0). v1 frozen, annotated beside; readout
  hephaestus/prereg/READOUT_Q045_v2_Z7_2026-09-11.md.

## The forge's engines -- PRESENT, not re-verified this pass

- +11pp R3 / +32pp R4 last reproduced 2026-08-19 (ABLATION_CARD). Not
  re-run from a worktree yet (HEPH-20).
- Cheap-model shelf: NIM credential file ABSENT on this host; ollama LIVE here
  (12 models). No eligible packet, so no call made (HEPH-04).

## Blockers

- Base-role self-test red on origin/main 7466bd6ac for a reason in
  Archaeon's lane (comms seed manifest hashed CRLF bytes); reported via
  comms, roles/Hephaestus/prompts/2026-09-11_manifest_crlf/ARCHAEON.md.
- Independent held-out generator for MINT-0001 still does not exist
  (Aporia TRANSFER-1 / Charon); HEPH-15.

## Next executable action

HEPH-29 (forward_chain through the gauntlet as a typed spec, preregistered)
then HEPH-30 (behavioural NCD lifted as an instrument with controls).
Waiting on Archaeon's one-line disposition for HEPH-25.
