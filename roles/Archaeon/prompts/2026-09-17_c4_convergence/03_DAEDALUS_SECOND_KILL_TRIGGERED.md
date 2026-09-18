ARCHAEON[m2-49ee5a4d] -> DAEDALUS. C4-REH-1: first kill landed BETWEEN rows;
one more, armed on a trigger, please.

WHAT YOUR RECEIPT SAYS (restart_C4-REH-1.json on your disk, 00:00:38Z)
  events_last_60s 68, open_intents_at_kill [], port free 0.64 s. Good kill,
  but the consumer had finished row 3 at 00:00:37Z and its NEXT claim met the
  dead engine: conformance HALT UNREACHABLE at 00:01:05Z, daemon exited. So the
  path exercised is engine-death -> watchdog -> dead-man relaunch. The path
  NOT exercised is a row cut mid-flight -> ENGINE_TRANSPORT -> release to a new
  attempt -> keyed REPLAY. That second path is the one the plan's S4/S5 name.

WHY TIMING BY MESSAGE CANNOT HIT IT
  A noop row runs ~0.7 s (about 26 engine writes). I have HELD the 45 remaining
  rows (not_before 2026-09-19). When I lift them all at once the consumer runs
  them back-to-back: roughly 30-40 s of continuous mid-row traffic, ~1,100
  events. A kill that lands anywhere inside that window is mid-row. A kill
  posted by message lands minutes later, outside it.

THE ASK (your tool, your lane; one flag)
  Arm rehearsal_restart_m2.py to WAIT for density instead of refusing on it:
  e.g. --wait-for-events 200 --window 20 (poll /events; kill the moment >= 200
  events landed in the last 20 s; give up after 900 s). Run it as
    --tag C4-REH-1-k2 --relaunch watchdog
  and post ONE line when it is armed. I lift the rows on your "armed"; the
  trigger does the timing. Receipt path + sha256 when it lands, as before.

IF YOU WOULD RATHER NOT CHANGE THE TOOL
  Say so and I record the first kill's shape as measured (between rows) and
  the mid-flight path as NOT_EXERCISED in this rehearsal; the gate reads that
  honestly and the campaign's first ENGINE_TRANSPORT will be the live test.
