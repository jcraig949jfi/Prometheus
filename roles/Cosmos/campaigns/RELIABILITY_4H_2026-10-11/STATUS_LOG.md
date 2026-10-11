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
