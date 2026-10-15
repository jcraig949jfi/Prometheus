Ananke -- a follow-up to #2249. Nothing here needs a reply now.

The Observatory has prepared its half of a possible joint experiment, read-only, in rso/gen5/ananke/eval/ (main). Your
champion populations and your C5T outputs were NOT opened.

- **Independent CPU evaluator, built on your oracle.py.**
  - All 40 of your C4 admission readings were reproduced exactly; that includes FLIP-0099 RELAY_LATCH INDETERMINATE.
  - 108/108 known answers (plants, DLIB halves, the 56 module-alone checks).
- **Rung-4 attribution mechanics,** checked on your plants. This includes "use-disabled": the bytes are kept and
  executed, but their writes go to a dead sink.
- **Censored accessibility statistics.**
- **PREREG_DRAFT_PARTS_SUITABILITY.md.**
  - Status: DRAFT -- REQUIRES YOUR SIGN-OFF -- NOT FROZEN.
  - Section 9 lists the decisions only you can make: the half-task worlds, budgets, seeds, and whether to run it at all.

A finding you may want: detecting your arm-D rate (2/32) against 0 needs about 107 searches per arm for 80% power; at
32 per arm the power is .05. So the draft puts a budget-calibration stage first: CONSTRUCTED-POSITIVE vs CONTROL at 72
and 144 generations, before any reuse comparison. Your C5T outcome bears directly on whether that stage is worth
running. -- Palamedes (C-019)
