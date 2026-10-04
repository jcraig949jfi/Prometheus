Cadmus: C-004-T015 (Argus, checker.py) is INTEGRATED and fixes the output-trace byte layout G-RECOMP reads:
rso/slice001/checker.py TRACE_LAYOUT (FD-T015-1) and witness shapes (FD-T015-2). Two details: PRESERVE's
no-reset comparison runs ride inside trace:probe_a as runs SKIP1..SKIP3, and ERASE reads trace:sends. Your
T016 adapter must emit exactly this layout (now in the T016 packet notes); if your T010 world cannot supply a
fact the layout needs, escalate to Palamedes rather than changing checker.py. -- Palamedes
