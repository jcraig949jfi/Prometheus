# AMENDMENTS to regate_v01/PREREG.md (PREREG.md is never edited)

## A1 -- 2026-09-28 11:22Z, after the gate (PASS), before any unplanted world

The unplanted hard stop is tightened from "40 min of cumulative run wall
from the gate start" to "1020 s of unplanted run wall" (first launch at 11:22Z was killed by my own process-cleanup command before any world finished; relaunched 11:24Z) (REGATE_LIMIT_SEC),
so that the report can be written inside the 45-minute task budget. The
gate itself took 384 s, but an idle wait of mine consumed calendar time.
Order is unchanged (U_sigma 1016, rest of U_sigma, U_id, U_frozen); any
world not reached is reported NOT RUN. No threshold, statistic, arm or
rule changed. Stricter only.
