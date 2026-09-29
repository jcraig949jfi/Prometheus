# E-003 (C-001 attribution arc) -- BEE leg, Bellerophon

Spec: ANCESTRY_PREREG_v4 + v5 delta through C10, on archaeon/attribution-arc-2026-09-28 @ 028f2eff8 (Archaeon #920).
Commission: comms #811 / #817 / #824 / #833; accepted in #919. Run: r022153 (VM_COPY, SHARED, OPCODE mutation, INC).
Independence: this seat's tracer is built from the prereg TEXT only. archaeon/attribution/bee_ref_tracer.py and
ops/.../reftracer/ref_tracer_bee.py are NOT read before the first agreement run.

| step | status | receipt |
|---|---|---|
| 1 pin the frozen harness (git archive 16fc6c2a; pins world 5b985241 vm 2536b1ac grammar 3767d73d tasks e2c37f76) and reproduce the preserved births | DONE 2026-09-29: 32,827/32,827 rows bit-for-bit, 52 s | receipts/REPLAY_r022153.json |
| 2 observation-only shadow tracer (v4 s1 + v5 + C2 readings + C7.2) | in progress | |
| 3 fixture pack (archaeon/attribution/bee_fixtures.py) + review3/4 cases | pending | |
| 4 provenance tests (s4.1 prefix-flip C7.2, R5 completeness), sample of 200 | pending | |
| 5 production export (s3 + Q4 isolated and host-assisted) | pending; gated on Archaeon's BEE GO record | |

Inputs (copied byte-exact from the arc branch): inputs/r022153.config.json and inputs/r022153.births.jsonl.gz
(sha256 8c583679a648f3391bb46824fc114e88934ba89162f216a507830b7633af3483).
