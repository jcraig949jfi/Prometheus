# E-001 tasks

| Task | Work | Status | Executor | Host |
|---|---|---|---|---|
| T-001 | BEE r038751 replay (code-material provenance) | DONE (A-002) | Archaeon[m2-1034e815] | ubu001 |
| T-002 | contrasting BEE replay with genuine foreign material (r016299) | RUNNING (A-001) | Archaeon[m2-1034e815] | ubu002 |
| T-003 | NPE provenance mapping (NPE's own terms) | READY | -- | portable |
| T-004 | cross-engine comparison | BLOCKED on T-001..T-003 | -- | any |
| T-005 | semantic adjudication | BLOCKED on T-004 | -- | any |
| T-006 | report | BLOCKED on T-005 | -- | any |

## T-001 inputs (everything reachable from git; no M2 disk needed)
- Code:
  * BEE frozen harness = git 16fc6c2a:prometheus/z80atlas/. It is byte-identical to C:\Users\James\z80atlas_campaign_2026-09-19\code
    (checked: world.py, vm.py, grammar.py).
  * BEE traced VM = origin/bellerophon/coupling-campaign-2026-09-24:roles/Bellerophon/forensics_2026-09-23/tools/{traced_replay.py
    (sha256 fcb280d0bca5ca9a), load.py}.
  * Probe = archaeon/causal_lens/tools_bee/codeprov_replay.py (this branch).
- Run config: inputs/r038751.config.json (sha256 aaca26e1834bf17a; copied from M2's campaign run directory).
- Command:
  `python codeprov_replay.py r038751 OUT.json --config r038751.config.json --harness <dir holding prometheus/z80atlas at 16fc6c2a>`
- Expected (science unchanged):
  * result_sha256 = cd9547c24811f52b5f332ca9bcd2a793a7c6f816296559369f309dea9812f6cd (the pre-pilot M2 run, 2026-09-27);
  * births rows identical to BEE's preserved traced log r038751.jsonl.gz (74,800 rows; the check runs on M2, where that log lives);
  * harness module hashes equal to 16fc6c2a.
- Resources: 1 CPU, < 1 GB RAM, about 1-2 min. Stdlib Python only.

## T-002 inputs (the T-001 recipe, unchanged except for the run id)
- Code: same three refs as T-001.
- Config: inputs/r016299.config.json (sha256 6b82f33f51504e11).
- Expected: result_sha256 = fb10f7e45c8f258bb57b3e02dbe82fde9847780b48929c458c2749d7d4d8f8c8 (the pre-pilot M2 run, 2026-09-27, fixed
  probe); rows identical to BEE's preserved r016299.jsonl.gz (83,384; checked on M2).
- Host: ubu002 (the second node, to test whether the recipe transfers unchanged).

## Attempts
| Attempt | Task | Host | Result |
|---|---|---|---|
| (pre-pilot) | T-001 | M2 SPECTREX5 | ran 2026-09-27 during Contract v0.2 (58-60 s); gives the reference result_sha256 above |
| A-001 | T-001 | ubu001 (192.168.1.218; 4 threads, 7 GB, Ubuntu 26.04, Python 3.14.4) | FAILED (claimed 2026-09-27T11:27:01Z): SyntaxError in the probe -- my portability edit turned "\r\n" into literal newlines and was pushed without a compile check. Host and inputs fine (tool sha fcb280d0, config sha aaca26e1 verified on ubu001). Not a science or host failure |
| A-002 | T-001 | ubu001 | DONE, claimed 2026-09-27T11:27:36Z. result_sha256 cd9547c2... == M2 reference; 74,800/74,800 rows identical to the preserved BEE log (checked on M2); harness hashes == 16fc6c2a (world 5b985241, vm 2536b1ac, grammar 3767d73d); 50.9 s wall, 141 MB RSS. Output copied to C:/Prometheus-data/evidence/ops_pilot_2026-09-27/T-001_A-002/out.json (sha256 b1fef410070c2997). Cleanup: ubu001 task dir removed, no process left (verified) |
| A-001 | T-002 | ubu002 (192.168.1.219; 4 threads, 7 GB, Python 3.14.4) | RUNNING; claimed 2026-09-27T13:03:33Z |
