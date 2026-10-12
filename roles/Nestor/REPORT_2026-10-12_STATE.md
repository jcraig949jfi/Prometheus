# Nestor: where the seat stands (2026-10-12)

**State:** IDLE / READY.
- Nothing is running on BUCKKEEP.
- No lease, no scheduled task, no open experiment.
- The last campaign is closed. Its work is merged to main with this report.

## What was done since the 2026-10-05 move to BUCKKEEP

### 1. X-TASK-GATE v2 (operator order 2026-10-05)

- **Verdict:** INSTRUMENT_UNREACHABLE (TRANSIENT_ONLY).
- **What happened:** a planted copier + task genome (CT_UA) passed competence to its P-11 descendants (up to 54% of
  the population). The task was gone by epoch 60-90 while the copier stayed fixed.
- **Freeze:** ef6d68cee. Report: `campaigns/npe-frontier-2026-09-30/x_task_gate_v2/RESULT.md`.

### 2. NPE-48h functional-heredity window

- **Directive:** operator, 2026-10-08.
- **Pause:** for the operator demo, 10-08 14:42 -> 10-10 02:48.
- **Closed:** 10-10 08:24.
- **Compute:** 560 runs, 66 CPU-h.

**Answer:** a transmitted function persists iff competence biases the DIRECTION of the copy exchange (who overwrites
whom). Coupling it to interaction RATE does not work; the XTG rate gate was harmful.

**CONFIRMED** (fresh seeds, frozen protocols):
- C-DIR-MAINTAIN: 12/12 vs 0/12.
- C-ONTAPE-MAINTAIN: priority earned from the organism's own in-copy answers, no offline scorer; 12/12 vs 0/12.

**Generalizes:** to the 7ae3 world (DIR 12/12, ONTAPE 6/6, vs 0).

**NOT_CONFIRMED:** C-ARCH-COMPETE, robust-architecture substitution (7/9 vs a bar of 8; a founder-establishment
lottery).

**Killed:**
- rate-gate selection;
- the invader's counter-copy hypothesis;
- the distributed form's advantage (it is neutral);
- supply-limited re-discovery (the unselected routine erodes the target within about 50 interactions).

**Architecture seen:**
- pair-distributed function (genomes answering through their partner's code), a neutral alternative state;
- tape-live dead code rewritten;
- a modest robustness gain only at high mutation;
- no task-copier fusion.

**Defects repaired, each with a fail-on-old regression test:** DEF-FH-1 to DEF-FH-4. fh tests: 13/13.

**Documents:**
- `campaigns/npe-fh48-2026-10-08/SYNTHESIS_FH48.md` (the end-of-window package);
- `FH48_REVIEW_2026-10-10.md` (the review packet);
- `FINDINGS_FH48.md` (F1-F17, C1-C3, Atlas packets A1-A3).

**Graph:** every node is in `EXPERIMENT_GRAPH.jsonl`; none of this window's nodes is open.

## Open items (none blocking; none started)

**Recommended next science** (operator's call):
1. The integration rung: a world where the task output is causally needed by the copier.
2. A multi-founder architecture CONFIRM.

**Deferred administration** (operator ruling 2026-10-05: not launch gates):
- the M1-drain receipt and the 14 stale queue items;
- `pm-data` custody (it stays on M1);
- the bld-g/h/q branches;
- D2 commitment anchoring;
- the key-holder scan.

**Comms since the window closed:** Bellerophon #1884 and #1983. Both are informational reports; no Nestor action is
requested.

## Workspace

| | |
|---|---|
| active worktree | C:/Prometheus-worktrees/nestor-npe48-2026-10-08 |
| branch | nestor/npe48-2026-10-08 (merged to main with this report) |
| older worktree | C:/Prometheus-worktrees/nestor-buckkeep-2026-10-05 (XTG-v2; its branch is contained in main via this merge); removable |
