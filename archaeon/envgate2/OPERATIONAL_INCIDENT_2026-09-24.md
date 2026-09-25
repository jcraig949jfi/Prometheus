# ENVGATE-02 -- operational incident receipt

| field | value |
|---|---|
| incident | first ENVGATE-02 launch (21:23Z 2026-09-24, 24 block workers) was terminated by the host's memory-pressure reaper, together with two concurrent Archaeon jobs (4-worker ENVGATE-01 genetic-audit replays; RIE-01 preflight) |
| cause | operational concurrency on shared M2 (31.8 GB): 24 + 4 Archaeon pool workers ran alongside another seat's 20 workers and Vivarium; not a scientific or design failure |
| complete ENVGATE-02 block results at termination | **none** (`archaeon/envgate2/runs/` empty) |
| treatment outcome inspected | **none** |
| scientific configuration | **unchanged**: preregistration `1475b7995` (digest 9e3fb887a4aeaa84); same 24 blocks, seeds, tape streams, arms, exposure, code hashes, cache size, endpoints, analysis, stopping rules |
| relaunch change | **maximum worker concurrency only**: 6 block workers via the operational launcher `archaeon/envgate2/launch_ops.py`, which calls the frozen `run_assay._block` and verifies the frozen code hashes; memory is observed every 60 s (pause new submissions below 4.0 GB available; clean stop below 2.0 GB on 3 consecutive samples). Log: `OPS_LOG.jsonl` |
| other seats | their processes were not touched; the only processes this run may terminate are its own pool workers |
| ruling | `roles/Archaeon/prompts/2026-09-24_envgate_adjudication_rie/01_OPERATOR_RULING_RESUME.md` |
| sequencing from here | one heavy Archaeon job at a time: ENVGATE-02 -> Phase C gate -> (if pass) genetic audit with <= 3 workers -> RIE-01 preflight -> RIE-01 (initial cap 6 workers unless measured headroom clearly supports more) |
