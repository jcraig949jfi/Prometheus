# E-007 tasks -- known-answer lane

Expected answers are the historical record: `legacy_sha256` computed from the committed ladder-2 evidence file named in
known_tasks.json (`aeth03_lane_reduce.py expected`). Command on any host, from a checkout pinned to the code commit:
`python Aether/observatory/aeth03_unit.py --law <law> --seed-index <k> --arm <off|on> --slice <a:b> --out <file>`.
Code: pinned b22d9f0d6 (LF-normalised sha256 of each imported module is recorded in every result file). Inputs: the
canonical parameter block only (no files). Resources: 1 CPU, <70 MB, 70 s on a pod core, 381 s on the contended laptop.
Verification: the lane reducer, on BUCKKEEP, against the expected hash. Cleanup: pods terminated and confirmed absent by the
platform (LIST+GET) and by an independent inventory read; nothing is left on BUCKKEEP but the result files.

| Task | Work | Status | Executor | Host |
|---|---|---|---|---|
| T-001 | v1 seed 0 off origins 0:4 | MATCH (3 attempts) | Aether[buckkeep-5c60d0f5] | 6bc0848098e3, BUCKKEEP, dc6dfea44355 |
| T-002 | rcv seed 1 off origins 0:4 | MATCH (2 attempts) | Aether[buckkeep-5c60d0f5] | 6bc0848098e3, dc6dfea44355 |
| T-003 | add seed 2 on origins 4:8 | MATCH (2 attempts) | Aether[buckkeep-5c60d0f5] | 6bc0848098e3, dc6dfea44355 |
| T-004 | mov seed 3 off origins 8:12 | MATCH (2 attempts) | Aether[buckkeep-5c60d0f5] | 6bc0848098e3, dc6dfea44355 |
| T-005 | m4 seed 0 on origins 12:16 | MATCH (2 attempts) | Aether[buckkeep-5c60d0f5] | 6bc0848098e3, dc6dfea44355 |
| T-006 | rcv seed 2 on origins 16:20 | MATCH (2 attempts) | Aether[buckkeep-5c60d0f5] | 6bc0848098e3, dc6dfea44355 |

## Attempts

| Attempt | Task | Host | Result |
|---|---|---|---|
| A-001 | T-001 | BUCKKEEP (Windows-11-10.0.26200-SP, NumPy 2.4.3) | DONE: result_sha256 d3cb0525dc7c..., legacy 1aa05bb79de9... == expected; 381 s; peak n/a (probe defect, fixed) MB; violations 0 |
| A-002 | T-001 | dc6dfea44355 (Linux-6.8.0-138-generic-, NumPy 1.26.3) | DONE: result_sha256 d3cb0525dc7c..., legacy 1aa05bb79de9... == expected; 69 s; peak 39 MB; violations 0 |
| A-003 | T-001 | 6bc0848098e3 (Linux-6.8.0-136-generic-, NumPy 1.26.3) | DONE: result_sha256 d3cb0525dc7c..., legacy 1aa05bb79de9... == expected; 81 s; peak 37 MB; violations 0 |
| A-001 | T-002 | dc6dfea44355 (Linux-6.8.0-138-generic-, NumPy 1.26.3) | DONE: result_sha256 ca4428534256..., legacy 8226926864b0... == expected; 71 s; peak 39 MB; violations 0 |
| A-002 | T-002 | 6bc0848098e3 (Linux-6.8.0-136-generic-, NumPy 1.26.3) | DONE: result_sha256 ca4428534256..., legacy 8226926864b0... == expected; 83 s; peak 37 MB; violations 0 |
| A-001 | T-003 | dc6dfea44355 (Linux-6.8.0-138-generic-, NumPy 1.26.3) | DONE: result_sha256 bc341fdb4c69..., legacy 8df7a44c1f94... == expected; 73 s; peak 39 MB; violations 0 |
| A-002 | T-003 | 6bc0848098e3 (Linux-6.8.0-136-generic-, NumPy 1.26.3) | DONE: result_sha256 bc341fdb4c69..., legacy 8df7a44c1f94... == expected; 83 s; peak 37 MB; violations 0 |
| A-001 | T-004 | dc6dfea44355 (Linux-6.8.0-138-generic-, NumPy 1.26.3) | DONE: result_sha256 b06ebd283ba9..., legacy a45c23b4f102... == expected; 77 s; peak 39 MB; violations 0 |
| A-002 | T-004 | 6bc0848098e3 (Linux-6.8.0-136-generic-, NumPy 1.26.3) | DONE: result_sha256 b06ebd283ba9..., legacy a45c23b4f102... == expected; 85 s; peak 38 MB; violations 0 |
| A-001 | T-005 | dc6dfea44355 (Linux-6.8.0-138-generic-, NumPy 1.26.3) | DONE: result_sha256 51d4049c9306..., legacy 3c0322ce87e7... == expected; 71 s; peak 39 MB; violations 0 |
| A-002 | T-005 | 6bc0848098e3 (Linux-6.8.0-136-generic-, NumPy 1.26.3) | DONE: result_sha256 51d4049c9306..., legacy 3c0322ce87e7... == expected; 82 s; peak 38 MB; violations 0 |
| A-001 | T-006 | dc6dfea44355 (Linux-6.8.0-138-generic-, NumPy 1.26.3) | DONE: result_sha256 72f36396249c..., legacy fca16945e70d... == expected; 72 s; peak 39 MB; violations 0 |
| A-002 | T-006 | 6bc0848098e3 (Linux-6.8.0-136-generic-, NumPy 1.26.3) | DONE: result_sha256 72f36396249c..., legacy fca16945e70d... == expected; 82 s; peak 37 MB; violations 0 |

Battery: **COMPLETE** (`REDUCTION.json`). Hosts: BUCKKEEP (Windows 11, Python 3.13.5, NumPy 2.4.3); RunPod pods xcd5801d7gq579
(container dc6dfea44355) and lt1t7ofxvgrwoq (6bc0848098e3), both Linux 6.8, Python 3.11.10, NumPy 1.26.3, 48 vCPUs.
Pod attempts were produced as by-products of the two scout flights (known units run in every flight of the module).
