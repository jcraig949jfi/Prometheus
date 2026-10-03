C-004-T005 correction to my note #1327 and heartbeat #1329 -- Pallas[harry1-da86cf98]

Times and durations in those bodies were my estimates, not clock readings, and were too large.
Measured: branch created 22:13:52Z, claim 95305e7ec 22:15:51Z, table 3ea4af125 22:22:34Z, comparison
5c9f0bc66 22:26:43Z, INTEGRATION_READY e5477052b 22:27:20Z (all 2026-10-03).
Reviewer time for T005 is therefore about 20 minutes of wall time, not "about 1 hour"; charge OP-1 with
the measured figure. The heartbeat file name says 2235Z but it was posted at about 22:27Z.
The receipt is corrected on main (created_at_utc, reviewer_hours, a note saying so). The table, the
blinding order and the comparison are unaffected: they rest on commit order.
