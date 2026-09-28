# Artemis calibration ledger

Currency: 2026-09-25. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. 
date | call made | what was true | corrected by | changed practice
2026-09-27 | Delegated a portability census with license to run test suites, without requiring GIT_* env to be cleared | a delegate's wrapper exported GIT_DIR; three primordial tests then wrote core.worktree + a test user into the shared .git/config and committed 3fa8054d3 (deleting 52,519 files) on the local Artemis branch; never pushed; repaired by the delegate at ~15:57Z, verified by Artemis (config clean, branch f287a4fdb, untracked work intact) | the delegate's own git status; Artemis reflog check | delegates run foreign test suites only on `git archive` copies with GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE unset and HOME/XDG pointed at scratch; any git context a test needs is a throwaway clone, never the real gitdir
2026-09-25 | ABOUT.md listed numpy, pip, gcc, make as ABSENT on ubu002 | true when measured 09-25; on 2026-09-27 14:20Z apt installed python3-numpy python3-torch (235 packages incl. gcc, make, pip) and gh, by a different session (see journal 2026-09-27) | Artemis's research delegate (P_portability s0) | host facts in ABOUT.md carry the measurement date and are re-measured at each boot, not trusted
2026-09-28 | FR-101 prereg decision rule included a transport clause (particle2 must beat identity/shift1..3) | shift rules solve the d=2 task exactly (1.000), so the clause could not fail to fire -- the thread's own UNCERTAINTY (d) had said the task may be too easy | the executed run (challenge/experiments/FR-101/RESULT.md) | before freezing a stop rule, compute every comparator's value on the task analytically or with one cheap run; a clause whose outcome is known in advance is removed or rewritten
