# RSO Scaling Assessment (C-013-T030, Workstream A)

Palamedes[harry1-679179c6], 2026-10-10 (v1). Case studies: C-004 (RSO methods slice), C-009 (execution binding), C-010
(first native witness). Every number is marked MEASURED (from the ledgers, packet histories or git, with the command
or file) or ESTIMATED (with the method). CROSS-CHECK: Eupalamus's independent tool (rso/scale/ledger_numbers.py,
C-013-T020, with a known-answer test and a self-crosscheck against rso.slice001.ledger usage()) reproduces the ledger
figures exactly: 53.1 / 31.8 / 26.2 CPU-minutes, 17 / 10 / 8 launches, all MATCH.

## 0. Answers (directive s17, questions 1 and 2)

What prevents a 10-100x increase in useful scientific throughput is not compute. C-010's complete native witness used
26.2 CPU-minutes. The three bottlenecks, in order:

  B1  QUALIFICATION IS BESPOKE AND SERIAL. Every new evidence path needed its own adversarial challenge, repair round
      and re-check (7 challenges in 3 campaigns; 7 of 7 found real defects), and about 83% of the implementation code
      written was specific to one experiment. Qualification is not yet a reusable asset. (architectural)
  B2  COORDINATION LATENCY, NOT WORK, DOMINATES WALL TIME. 69-82% of packet lifetime was waiting -- for a seat to
      claim, or for the coordinator to integrate. Work is session-bound, hourly-polled, launched from one thermally
      limited host, and lost when a headless session ends. The job, not the conversation, must own execution state.
      (architectural + organisational)
  B3  DISCRIMINATING EXPERIMENTS ARE SCARCE. There are few worlds or targets with a reference solution, a known
      simpler alternative that fails, and qualified controls (Hestia: 0 VIABLE_SEED of 25 engines; the composition wall
      measured 7 times). Throughput of "genuinely discriminating findings" is bounded by the supply of such targets, not
      by how fast we can run them. (scientific)

Computational in the strict sense: almost nothing today. Compute becomes binding only once B1-B3 are relieved and an
experiment has earned a 4x/16x budget (s12).

## 1. The three campaigns (MEASURED unless marked)

| | C-004 methods slice | C-009 binding | C-010 witness |
|---|---|---|---|
| wall time, open -> close | ~3.1 days (OP-1 2026-10-03T21:48Z -> 10-07T00:30Z) | 8.0 h (00:35Z -> 08:34Z 10-07) | 6.2 h (08:34Z -> 14:45Z 10-07) |
| packets (non-operator) / escalations | 44 / 11 | 15 / 0 | 11 / 2 |
| operator rulings needed | 8 (OP-1..OP-8) + chat pokes | 0 (ran under one directive) | 0 (one NULL decision taken by the coordinator, reversible) |
| top-level launches | 17 of 20 | 10 of 12 | 8 of 10 |
| ledgered CPU | 53.1 min (+40 dev booked) | 31.8 min | 26.2 min |
| artifacts | 31.8 MB | 13.4 MB | 10.3 MB |
| reviewer (Q3) time | ~2.2 h | ~1.5 h | ~1.7 h (cap 1.5: overrun) |
| independent challenges / defects found | 3 / 3 (S3, S4, R2) | 2 / 2 (B1, B2) | 2 / 2 (W1, W2) |
| integrator-found defects | several | 1 (BX5b node-id pin) | 4 (pairing bug, shared-ledger P-FLAT, P-OBS prefix, seed-list format) |
| process incidents | git pull in canonical; red-main risks | 2 headless reviewer sessions lost; 1 red push | 1 red push; work pushed to main directly once |
| result | INCOMPLETE CLOSURE | CLOSED (scoped) | instrument QUALIFIED; S4, S15 NEGATIVE |

Sources: rso/slice001/S5_FINAL_DISPOSITION.md, rso/binding/CLOSURE.md, rso/witness/RESULT.md, the three LEDGER.jsonl,
ops/campaigns/C-00{4,9}/ and C-010/.

## 2. Where the wall time went (MEASURED from packet histories)

Command: for every non-operator packet, first READY -> first CLAIMED (waiting for a seat), CLAIMED -> INTEGRATION_READY
(being worked), INTEGRATION_READY -> INTEGRATED (waiting for integration).

| | waiting to be claimed | being worked | waiting to be integrated | share waiting |
|---|---|---|---|---|
| C-004 (n=36) | median 391 min, sum 19,539 | median 12, sum 2,610 | median 3, sum 1,982 | 82% |
| C-009 (n=15) | median 11, sum 359 | median 12, sum 335 | median 39, sum 459 | 71% |
| C-010 (n=10) | median 5, sum 213 | median 15, sum 183 | median 3, sum 186 | 69% |

Reading: C-004 waited hours per packet for operator pokes and seat wake-ups; under the completion directive (C-009,
C-010) same-seat relaunch and hourly polls cut claim latency 35-80x, and the residual waiting is the polling interval
(claims landed at :24-:29 past the hour) and the coordinator's integration queue (C-009 median 39 min). The work
itself is minutes. A 100x throughput increase therefore needs event-driven dispatch and parallel integration, not
faster seats.

## 3. Reusable infrastructure vs experiment-specific work (lines MEASURED; classification ESTIMATED)

Implementation lines (tests and challenge code excluded): rso/slice001 7,763; rso/binding 109; rso/witness 1,859.

  reusable across experiments (~1,700 lines, ~17%): ledger.py 304 (caps, launches, CPU, bytes); binding.py 109
  (execution binding); receipt.py canonical bytes (~150 of 770); evidence.py custody/store reads (~150 of 845);
  mutation.py 434 (the reviewers' mutation runner, used in 6 challenges); ruler.py 257 (exact binomial ruler, McNemar);
  run_witness.py driver core (~300 of 458: ledgered launches, artifact storage, per-launch inventory, seed refusals).
  experiment-specific (~83%): the slice world, reset, observer, rulers, adapter, encoding, matrix, bundles, fixtures,
  expected tables, stage records; the Ares adapter, configs, evaluator's predicate map.

The reusable part is exactly what C-010 inherited and did not have to rebuild; C-010 was 12x faster than C-004 in wall
time largely because of it (and because the operator removed gates). The next 10 runtimes will each cost roughly the
C-010 witness-specific work (~1,500 lines + one challenge + one repair) unless more of it becomes shared.

## 4. Qualification overhead (MEASURED counts; cost ESTIMATED from reviewer logs)

7 of 7 independent challenges found real defects -- 3 false/admitted shapes in C-004, BX5 siblings and three unpinned
edits in C-009, ten survivors in C-010 W1 including a control that would have disqualified the instrument in exactly
the positive case (NULL). Author regression never caught these. This is the strongest single fact in the record: the
adversarial challenge is worth its cost, and therefore it is the scarce, expensive stage that must not be spent on
every candidate. Per qualified evidence path: ~1.5-2.2 reviewer-hours of Q3 model time, 1 repair round, 4-10 hours of
wall time. At that rate, Q3 review alone caps the Observatory near one qualified evidence path per reviewer-day.

## 5. Resource utilisation (MEASURED)

CPU: < 1.6 CPU-hours across all three campaigns; the fleet (six ubu nodes, M1/M2 GPUs) was unused by them. Every
headless seat ran on harry1 (thermally limited). Fabric: 0 live workers of 53 registered (read-only check 2026-10-10;
roles/Palamedes/comms/2026-10-10_fabric_defect_packet.md). GPU: not used; no workload in these campaigns would have
benefited (single-organism Ares rollouts at 0.08 CPU-s per 64x16 episodes).

## 6. Operator dependency (MEASURED)

C-004: 8 operator rulings, each a schedule gate (median claim latency 6.5 h). C-009 + C-010: 0 operator gates under one
72-hour directive; one scientific choice (the NULL amendment) taken by the coordinator and flagged for overrule. The
operator dependency that remains is the right kind: authorising spend, scope and reviewers -- not scheduling.

## 7. The three bottlenecks, with the smallest investment that relieves each

  B1 bespoke serial qualification -> QUALIFY ONCE, REUSE MANY: a multi-fidelity ladder (cheap exploration ->
     provisional screen -> qualified assay -> independent challenge -> preserved result) where only promoted claims
     reach the challenge; qualified components (rulers, binding, custody, drivers) carry their qualification stage and
     are reused without re-challenge unless touched. Smallest step: a "qualified component registry" -- the stage
     records of C-004 generalised to rso/binding, rso/witness ruler and driver -- so the next runtime pays only for its
     adapter. Target: next runtime's witness-specific work < 500 lines, one challenge.
  B2 coordination latency -> THE JOB OWNS ITS STATE: immutable manifests, append-only progress events and checkpoint
     records that a job writes and any seat can resume; event-driven claiming instead of hourly polls; integration that
     seats can do for each other's mechanical packets. DONE IN THIS WINDOW (single host): the session-independent
     runner rso/scale/runner/ (C-013-T022) passed its kill-everything fire test 13/13 -- worker, supervisor and the
     launching session killed mid-epoch, resumed by a DIFFERENT session from one command line, final digest equal to
     the uninterrupted control (rso/scale/runner/FIRE_TEST.md); retention (T024) and an idempotent relaunch entry
     tested with a simulated scheduler (T025) followed. Remaining: cross-host transport (port onto Themis's C-012
     NF transport, P-4) and a live worker plane (Fabric: 0 live workers; Themis's bounded workers ran C-012-T003).
  B3 scarce discriminating experiments -> MAKE TARGETS, NOT RUNS: reachability cartography on existing deserts with
     known constructions (C-013 D1), and the World-Demand Foundry admission ladder (reference solver succeeds, specified
     simpler alternatives fail). Smallest step: D1 itself, then one Foundry world with a qualified admission ladder.

## 8. What would make a 100x claim honest (s8 measure)

Count "independently qualified, genuinely discriminating findings per week and per dollar". Today: 1 qualified
native result (C-010, negative) in the push window; 3 campaigns in ~4 days; $0. A 100x increase means ~tens of
qualified findings per week; the arithmetic in s4 says Q3 review alone forbids that unless the challenge stage is
reserved for promoted claims and the reusable share of qualification rises from ~17% to most of it.

## 9. Known limits of this assessment

Seat-hours and token costs are not metered; reviewer times are wall-clock estimates from logs. The reusable/specific
split is a judgment over files. One coordinator wrote most integration glue (a bias in the integration-latency figure).
Three campaigns are a small sample; C-004 ran under a different operating regime than C-009/C-010.
