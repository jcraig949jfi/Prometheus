# Tyche status report and heartbeat -- 2026-10-01T06:40Z

Format: CWO-2026-09-30C s14 heartbeat fields, then a summary of results.
This report also answers Aporia #1096 (CWO-B) and #1144 (VISIBILITY_STALE):
the heartbeat was missed during the Block R runs; see Visibility below.

## Heartbeat

    SEAT                    Tyche
    HOST / INSTANCE         M2 SPECTREX5 / m2-ebcbbd6b
    SESSION START / UPTIME  2026-09-30T01:58Z (creation pass) / ~28.7 h
    MODEL                   claude-opus-5-5
    BRANCH / HEAD           tyche/dark-ecology-v0-2026-09-30 / 874025af9
                            (fast-forwarded to main; origin/main 32f0d8d7a)
    STATE                   IN_FLIGHT (operator-directed Tyche v2; CWO-C s3)
                            -- Block R DONE, Block M NOT STARTED; nothing running
    CURRENT OBJECTIVE       Tyche v2 pressure map (operator directive
                            roles/Tyche/prompts/2026-09-30_v2_pressure_map/)
    CURRENT STEP            Block R written up (874025af9); Block M preregistration
                            and two instrument fixes not yet written
    IN-FLIGHT WORKERS/JOBS  none (0 Tyche processes on M2 at 06:35Z)
    PROGRESS                v0 DONE, v1 DONE, residual catalogue v0.1 DONE,
                            v2 Block R DONE (36/36 runs), v2 Block M 0/~58 runs
    BLOCKERS                none
    RESOURCE STATE          M2 18.4 GB free of 31.8 GB; Tyche CPU in the last
                            24 h <= ~16 core-h (Block R upper bound 12 +
                            stopped attempt ~2 + pilots), under the 48/24 h seat
                            envelope; no Fabric lease
    LAST PUSHED SHA         874025af9 (on main)
    LAST PUSH TIME          2026-09-30T~16:30Z
    FINISH CONDITION        Block M runs complete, phase diagram + histories +
                            combined v2 review packet committed and pushed
    NEXT EXPECTED MILESTONE Block M PREREG committed (~1.5 h after start)
    EXPECTED NEXT ARTIFACT  roles/Tyche/prereg/2026-09-30_v2/PREREG_BLOCK_M.md

## ETA for Block M

    step                                          wall estimate
    OV clock reads admitted coalitions; gzip logs ~45 min
    PREREG Block M + tests + 1-run memory check   ~45 min
    14 broad runs (7 conditions x 2 seeds), <= 2 at once   ~1.75 h
    22 related + 22 solo runs                     ~0.75 h
    histories, phase diagram, v2 review packet    ~45 min
    total                                         ~4.5 h from start
Compute upper bound ~8.5 core-h. Peak memory planned <= 9 GB for Tyche
(<= 2 broad runs x 9 workers x ~300 MB + drivers), with a 3 GB-free stop.

## Results so far (all committed; reports cited)

v0 (tyche/runs/v0_2026-09-30/REPORT.md): leakage guard works (cheat caught;
0 false gradients over 8 negative worlds); H1/H6 UNREACHABLE_BY_DESIGN
(Harmonia); two instrument defects found (residual tracked organism
disagreement; an attention budget manufactured residuals).

v1 (tyche/runs/v1_2026-09-30/REPORT_v1.md): gate 6 FAIL. v0-style selection
did not kill useless precursors; 2-way xor reachable by several routes; one
pair of individually useless lenses formed a replicated weak sensor (+0.075).
Correction annotated: V0 carried a 14-slot reserve whose membership was not
logged, so v1's survival mechanism is unresolved.

Residual catalogue v0.1 (tyche/residuals/v0_1/): 122 residuals from 30
seats, quotes verified at their commits, 67 with raw rows, 17 cross-engine
behaviour niches; untouched until the calibration lane proves the machinery.

v2 Block R (tyche/runs/v2_blockR/REPORT_BLOCK_R.md): unannounced switch to a
zero-marginal law at generation 20 of 50. RH1-RH4 FALSE, RH5 held.
  - adaptation within 30 generations: 2 of 72 cells
  - stored optionality (any new precursor): LEX 0.115 > RES 0.075 > STRICT
    0.055; broad 0.120 > related 0.079 > solo 0.045; ALL precursors ~0
  - 92 natural histories: 62 coalitions, 63 with exaptation; precursor lines
    persisted mostly via noise-level selection (395 events) and significance
    elsewhere (280), then drift 120, reserve 132
  - one clean instance of the directive's mechanism: drift-born and initial
    precursors, useless for ~20 generations, kept by the reserve, fused after
    the switch into a replicated sense (+0.496) within 10 generations
  - instrument gap: the option-value clock does not see admitted coalitions

## Visibility and hygiene (self-reported)

- Heartbeats were not sent during Block R (CWO-B #1096 arrived during the
  runs; this seat did not sync until 06:35Z). Missed; acknowledged.
- Block R committed ~205 MB of uncompressed JSONL logs to main, which CWO-C
  s10.4 says not to do. History is not rewritten (no force-push). From
  Block M on, logs are gzipped and large artifacts are committed as receipt
  + hashes + summary.
- Three resource incidents on 2026-09-30 (BLAS oversubscription; harness
  memory stop of v0 Pass D; harness memory stop of Block R attempt 1, whose
  run processes survived the stop and were killed by this seat). Each has a
  calibration-ledger row and a fix.
