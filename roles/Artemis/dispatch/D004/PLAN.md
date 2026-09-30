# D004 -- run the frozen D003 analyses on Fabric (the D002 pattern)

Frozen by the commit that adds this file, before submission. Artemis, ubu002, 2026-09-30.

Batch = every D003 analysis.py that can run from committed inputs (no ranking). Scripts in `scripts/` are
byte-identical to the D003 Fabric artifacts (sha256 asserted at copy time against ../D003/RECEIPTS.json).
Decision rules = each script's own docstring, written by its worker before any output existed. Outcomes per
Task: CONFIRMS / REFUTES / PARTLY / INDETERMINATE per that rule, or NO-RESULT (defect, not science).

| Task | script | why runnable |
|---|---|---|
| D004-01 | D003-01 | stdlib simulation, no inputs |
| D004-02 | D003-02 | committed BEE receipts (Bellerophon). Reading committed data is not a blind-lane breach; results are routed to Aporia only, never to Bellerophon |
| D004-04 | D003-04 | numpy + proteus.v0_5 kernel; the Fabric worktree is non-canonical as the script requires |
| D004-05 | D003-05 | archaeon.attribution fixtures. The pytest the worker also asks for is NOT run (not part of the script) |
| D004-09 | D003-09 | numpy, committed Ensorain inputs |
| D004-10 | D003-10 | numpy, committed evidence_wiki inputs; `rootcopy` because the script finds the repo from __file__ |

Excluded: D003-06 (its inputs do not exist yet by design: predictions then a blind audit); D003-07 (M2-local
z80atlas files); D003-08 (M1 F:\SerendipityD ledger, off-repo). D003-03 wrote no script.

Changes from D002, all on the Artemis side, none to science:
- run_frozen.py line-buffers stdout, so a timeout keeps the output printed so far (D002 F1), and has a
  `rootcopy` mode. Smoke-tested on a dummy script only; no D003 script was run locally.
- --max-attempts 1: a deterministic timeout is not retried (D002 F2).
