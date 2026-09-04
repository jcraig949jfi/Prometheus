# Memory-Clean Session Procedure — STATUS: UNQUALIFIED

Qualification state: UNQUALIFIED. This procedure has NOT been demonstrated
to prevent ambient-memory injection. A running Mnemosyne session cannot
certify its own memory cleanliness (V3 AMENDMENT 1: the index survived both
worktree isolation and physical directory relocation performed from inside
a live parent session, via parent-session caching). Do not perform semantic
work under a "clean" label until an independently launched session has run
the probe below and demonstrated absence.

## Operator procedure (candidate)

All steps happen BEFORE any Claude Code session is launched — no parent
session may be running for project F--Prometheus during steps 1-3.

1. Close every Claude Code session (terminal, desktop, IDE) that has the
   F:\Prometheus project open. Verify no claude processes remain.
2. Relocate the ambient memory directory:
       ren "C:\Users\jcrai\.claude\projects\F--Prometheus\memory" memory.QUARANTINE
   Do NOT delete it (it is the forensic corpus; see
   AMBIENT_MEMORY_DISPOSITION.md).
3. Launch a FRESH session for the experiment.
4. FIRST ACTION in that session — the probe, before any task content:
   ask the session to state whether a memory index / MEMORY.md content is
   present in its context, and to quote any memory-derived doctrine it can
   see. Record the answer verbatim to disk.
   - Index visible  -> procedure FAILED; abort the clean-condition run,
     restore the directory, record the failure.
   - Index absent   -> the SESSION is a candidate-clean session; the
     PROCEDURE stays UNQUALIFIED until this outcome is reproduced by an
     independent operator launch and committed.
5. After the run: restore the directory name, note the restoration time.

## Qualification criterion (future, independent)

The procedure may be relabeled QUALIFIED only when: an operator-launched
fresh session (not spawned by any live session) runs step 4, finds no
index, completes its task, and the transcript + probe output are committed
by that session itself. Until then every result produced under this
procedure carries the caveat AMBIENT_ISOLATION_UNVERIFIED.

Known upstream contradiction: vendor docs state subagents do not receive
auto-memory; observed behavior in V3 contradicts this (feedback filed).
Behavior, not documentation, is authoritative here.
