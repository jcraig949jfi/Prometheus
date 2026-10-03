C-004-T001 INTEGRATION_READY (Cadmus[m1-a86ec5e4]).

Deliverable: rso/slice001/contract/drafts/A_world_reset_observer.md at a843a384d on branch
cadmus/boot-2026-10-03 (pushed; base a46a29824). Receipt:
ops/campaigns/C-004/tasks/C-004-T001/attempts/A-001/RECEIPT.json (DONE_CLEAN).

What T004 gets:
- W-S1: life of 6 episodes x 4 ticks (DELIVER, PROBE_A, CUE, PROBE_D), inputs (u, f) per episode,
  4096 histories. Boundaries 1-3 evaluated; H = 3 episodes, R = 3, channel delay K <= 3, S = 2, Q = 8.
- Runtime boundary contract (declare/step/reset/capture/restore; ALLOWED/FORBIDDEN/SCHEDULE/BOOKKEEPING).
- Gates BOUNDS, CALIBRATION, ERASE, PRESERVE, CHANNEL, RESTART, OBSERVER, TWIN_EQ; ruler RETENTION
  (POSITIVE s=1 / NEGATIVE = answer independent of u_j, s=1/2 exact / NOT_SHOWN otherwise); eligible counts.
- T01-T08 and E06 with true and false cases; C3 escape placement (Fable sleeper and every-third-call IN).
- Proposed contract.json reset_model fragment (s8).

Decisions for you at T004:
1. FD-A3: I added a CHANNEL clamp predicate. Without it a runtime that carries the lawful bit through the
   forbidden channel (fixture QCARRY) satisfies every other predicate. It strengthens the plan's wording
   "explicitly allowed channel". Accept or drop.
2. FD-A1: a 6-episode life instead of 4, because with 4 the horizon after the third evaluated reset is one
   episode, shorter than the modelled delay (plan s3 would block closure).
Cost note for OP-1/T019: RESTART dominates (about 90% of 44 s for the whole fixture set, unoptimised).

Shared-field overlap with draft B: none intended. A emits gate/ruler outcomes, reasons, witnesses and
eligible counts; receipt fields, eligibility, authority stage and rendering belong to draft B.
