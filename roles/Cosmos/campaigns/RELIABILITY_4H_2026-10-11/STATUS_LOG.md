```
COSMOS RELIABILITY TEST -- hour 1/4   wake 2026-10-11T07:35:23Z (scheduled 07:13)
======================================================================
wake          LATE by 22 min (scheduler fires only when the session is idle,
              plus jitter) -> P1 h1 MISSED (window 07:13-07:33). Recorded.
jobs          EXP-05 DONE 160/160 (06:10-07:15, 0 restarts)
              EXP-06 DONE 22/22   EXP-07 DONE 38/38   EXP-08 DONE 38/38
              sweep: ok, no STALLED/DEAD, none running without lease
lease         renewed 07:35Z -> expires 09:05Z (had 4 min left)
results       EXP-05 INCONCLUSIVE (H-ACCUM contradicted; return geometry
              right in direction; H-SPREAD post hoc)
              EXP-06 INSTRUMENT_DEFECT UNEXPLAINED; EXP-07 H-START REJECTED
              (narrow; descriptively dominant); EXP-08 H-GAIN REJECTED
infra         supervise sweep (OS-timer ready; timer NOT installed)
gap           no job 07:15:05 -> 07:35 (waiting for this wake; < 30 min)
next          EXP-09 H-SPREAD prereg + run on fresh DISCOVERY batch 4
c4 head       58bef96c05      holdouts D2 SEALED/UNREAD/UNSPENT   $0
======================================================================
```
```
COSMOS RELIABILITY TEST -- hour 2/4   wake 2026-10-11T08:31:57Z (cron :03; P1 ref 08:13)
======================================================================
wake          29 min after cron time, 19 min after P1 reference (window
              closes 08:33) -> committed at ~08:32: P1 h2 MET (narrowly).
              Wake latency again ~20-30 min after the session went idle.
jobs          EXP-09 DONE 60/60 (07:36-08:00). NS-01 jobs (operator order
              07:44Z): engine qualification 82/82, A/B eval 16/16, Arm D
              8/8, deep 40/40 -- all DONE under supervise, 0 restarts.
              sweep ok; nothing running now.
lease         renewed 08:32Z -> 10:01Z (had 33 min left)
results       EXP-09 H-SPREAD REJECTED (8a6d96717). NS-01: atlas + protocol
              frozen (eb0e1c14f), engine QUALIFIED (FR 1/66, FA 0/7),
              32 proposals evaluated (8407a30bd).
gap           no job 08:09:25 -> 08:31:57 (idle so the wake could fire;
              logged); < 30 min.
next          NS-01 failure-15 candidate (readout decodes the cue better
              than the full-state decoder: B01, B05, B08) -> prereg test
c4 head 8a6d96717 | ns01 head 8407a30bd | D2 SEALED/UNREAD/UNSPENT | $0
======================================================================
```
```
COSMOS RELIABILITY TEST -- hour 3/4   wake 2026-10-11T09:31:56Z (cron :03; P1 ref 09:13)
======================================================================
wake          29 min after cron, 19 min after P1 reference -> committed
              ~09:32: P1 h3 MET (narrowly). Latency pattern stable: the
              session-idle scheduler fires ~29 min after its cron minute.
jobs          since h2: F15 test, F15 capacity, NS-02 engine requal, NS-01
              re-measure, NS-02 D loop, NS-02 A/B eval, full suite (NS-01
              branch 178/178) -- all DONE under supervise, 0 restarts.
              sweep ok; nothing running now.
lease         renewed 09:32Z -> 11:01Z (had 30 min left)
results       NS-01: FAILURE_15 SUPPORTED rel. archive (b4b584bbc); NS-02
              learning test: redirection NOT SUPPORTED (ff8b8b24a); review
              packet (d805edc14); NS-01 tests 4/4 (71b2b3853).
gap           no job 09:03:21 -> 09:31:56 (28.6 min; idle so the wake could
              fire; logged). P3 limit 30 min: met narrowly.
next          h4 at ~10:03 cron: final full suite, VERDICT.md vs P1-P6
D2 SEALED/UNREAD/UNSPENT | confirmation data none | $0
======================================================================
```
```
COSMOS RELIABILITY TEST -- hour 4/4   2026-10-11T10:00:12Z (P1 ref 10:13)
======================================================================
wake          by the completion of the final-suite job (a job-driven wake),
              not by the scheduler (cron :03 not yet fired; latency ~29 min)
jobs          since h3: suites c4-v03 174/174, main 112/112, FINAL ns01
              178/178 -- DONE; sweep ok (16 runs, none stalled/dead)
lease         renewed 10:00Z -> 11:30Z
constraints   D2 untouched; no confirmation data; autopsy branch absent on
              origin; cosmos/c4-v03 not merged into main; $0
verdict       VERDICT.md: FAIL by rule (P1 hour 1); P2-P6 met
======================================================================
```
