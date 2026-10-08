# C3R stage 2: deadline deviation (recorded 2026-10-08T15:28Z, before any post-deadline row was read)

## What happened
- PREREG_PTE_C3R.md s4 says: "stage 2 at its launch + 14 h. No job starts after its deadline."
- Launch was 2026-10-08T00:58:51Z, so the preregistered deadline is 2026-10-08T14:58:51Z.
- The workers were launched with --deadline-utc 2026-10-08T16:58:51Z, i.e. launch + 16 h. This was a launch-parameter
  error, found by the watch at 15:27Z.

## Jobs claimed after 14:58:51Z (claim-file mtime)
- FLIP-0000-adbab9bf|R0|05|s2 at 15:10:54Z
- FLIP-0004-125dfbff|R0|05|s2 at 15:25:34Z
- FLIP-0099-df143630|R0|05|s2 at 15:27:34Z

All three are R0 (the order puts R0 last in every round). No R3 or R4 job started late.

## Action
- At 15:28:11Z the one remaining unclaimed job (FLIP-0167-b6d3fceb|R0|05|s2) was pre-claimed with the content
  "PREREG_DEADLINE_BLOCK", so that it never starts.
- Running workers were NOT killed (never patch mid-run). The three late jobs complete and their rows are kept.

## Analysis rule (fixed now, before any of these rows exists)
- PRIMARY: rows of jobs claimed at or before 14:58:51Z, which is the preregistered sample.
- SENSITIVITY: all rows. Reported beside the primary.
- If the two disagree on any label or on the kill criterion, the PRIMARY governs and the disagreement is stated.
