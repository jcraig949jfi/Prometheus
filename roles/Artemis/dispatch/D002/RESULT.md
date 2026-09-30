# D002 result -- the frozen D001 analyses, run on Fabric

Artemis, ubu002, 2026-09-30. Plan: PLAN.md (frozen at c628f3e before submission). Receipts: RECEIPTS.json
(Fabric is authoritative). Outputs: stdout/out artifacts of each Task (fetched to ubu002
/home/jcraig/artemis-d002/artifacts, sha256 re-checked). Each verdict applies the rule the D001 worker wrote
before any output existed. Where Artemis had to read a rule against a trajectory (08B), that is marked, and
the owner may re-read it.

## 1. Science (8 of 11 Tasks returned)

| Task | D001 claim tested | frozen rule outcome | notes |
|---|---|---|---|
| D002-04 | Archaeon SFE C2-C5: 12 WEAK_POSITIVE = 4 EMPTY_BATTERY + 1 NO_PATH + 1 ATTACK_FAILED + 6 N_AND_BATTERY; 0 SUPPORTED | CONFIRMS exactly | New: of the 4 "blocked only by battery", C3-SFE-03 passed its threshold trivially (effect 0.0 vs min_effect 0.0). Also trivially thresholded: C4-08, C4-10, C5-03, C5-06. So 3, not 4, weak positives had a real effect and were blocked only by the missing battery (C4-01 .379, C4-02 .408, C5-01 .082). |
| D002-05 | Aporia Gemini queue: 423 / 53 fired / 370 unfired; fired set == fired_log; 32 Moros reports | CONFIRMS | Same as the disclosed local smoke run. |
| D002-07 | Lexis G1 census 2,103 / 89.73% / 5.94%; winners' libraries are decoration; IQ-NULL deltas 0, ADVANCE, no partition key | CONFIRMS (A, C); B CONFIRMS at the margin | Top-tercile load-bearing rate 0.0997 against the worker's bar of 0.10. It is on the knife edge: one more load-bearing ablation in 572 would flip it. Middle tercile .077, bottom .012: load-bearing rises with score. |
| D002-08A | Ares W15 Fisher p (one-sided .085, two-sided .17); plasticity alone solves W15 | CONFIRMS | All 33 W4-evolved PLAST champions score 33.8-40 on W15 (median 40). The report's "10 c1_only_plast at 36.1-40" is a subset. |
| D002-08B | Ares: why do 6 W15 MIXED lineages carry both carriers? (B1 by-product / B2 selected / B3 drift) | INDETERMINATE at n=6 (Artemis reading of the frozen rule) | Recurrence first or tied in 4/6 (203, 204, 207, 209), but B1's fitness band holds cleanly only in 209 (203 arguably); 204 has no recurrence-only phase, 207 is at 27-28 then. B2 at most 2/6 (202; 206's gain is 3.1 < 4). B3 at most 1/6. Load-bearing flags flicker between 5-generation samples (e.g. 202), so first-gen times are coarse. |
| D002-08C | Is MIXED co-dependence an artifact of carriers._cut zeroing plastic R on recurrent edges? | NOT an artifact (rule C not met: 0/6) | Cutting recurrent W while keeping R still collapses all 6 MIXED champions (0.0-2.75 of ~40). The co-dependence is real, which is consistent with D001-08's reading that W15 is co-dependent (MIXED), not REDUNDANT. |
| D002-09 | D8: M1F vs HRND 7/6, p = 1.0 -> history beyond diversity NOT SHOWN; 11/5 p .210; 10/5 p .30; ~650-700 tasks for delta .05 | CONFIRMS exactly | Same task ids as the hand tally. Power: 669 tasks for .05. Seen in passing (not the tested claim; 9 unadjusted comparisons): M1L vs M0b 11/2, p = .022. |
| D002-03q | PROTEUS-46 cliff (declared --quick mode) | B: the cliff IS crossable by a neutral path in principle. A: both single fixes 0/6 (hand derivation holds). D: drift 'score' 1/50 hits (step 188), 'strict' 0/50, control 0/50 | Frozen rule B: all four intermediate steps NEUTRAL (3/6) and the fifth reaches 6/6. PROTEUS-46's 3-step design could not see a 5-edit path. D in quick mode is YES for 'score' by the literal rule, but 1/50 vs 0/50 does not beat the control, so "drift helps" is not shown. E (pop 50 x 100 gens): never reached 6/6. |

NO-RESULT (Fabric timeouts, not science): D002-02 (WTP-03 ablations, 90 min), D002-03 full
(500 walks x 3000 steps, 91 min), D002-06 (C0-A proxy, 60 min). Each retry was cancelled after the first
timeout, because the scripts are deterministic. All three returned 0 bytes of stdout (see s2).

## 2. Fabric (for BUILDER-FABRIC; the CWO RESERVE line)

- 11 Tasks: 8 completed on first attempt, 3 timed out at the wall cap, 0 lost, 0 crashes. Capability routing was
  correct: numpy Tasks went only to worker.ubu001.sci, stdlib Tasks to .a/.b.
- F1: a timeout keeps no partial output. Python's stdout is block-buffered when piped, and the executor's SIGTERM
  loses the buffer. All three timed-out Tasks returned 0 bytes after 60-91 min. Fix candidates: run scripts with
  -u / PYTHONUNBUFFERED=1 in the script executor, or SIGTERM-then-grace so atexit flushes.
- F2: a deterministic timeout is retried by default (max_attempts). That burned a second 27-57 min slot each for
  nothing. Consider not retrying `exit -15 timeout` for the script executor unless asked.
- F3: head-of-line blocking. Once the three long Tasks held all three slots (and then their retries), five Tasks
  that ran in 0-19 min (07, 08A, 08B, 08C, 09) waited about 2.5 h. There is no short-job lane or wall-based ordering.
- F4: `fabric submit --arg` cannot take a value that starts with `--` (argparse). Workaround: `--arg=--repo`.
- Artemis's own defect: the first reconcile_batch.py deliverable check expected `out/` prefixes (fixed).
