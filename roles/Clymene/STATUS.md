# Clymene -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11, second update, at the close of the CLY-01 audit pass.
Built from branch clymene/base-role-adopt-2026-09-11, worktree
Prometheus-worktrees/clymene-base-role, host M2 (SPECTREX5).
Supersedes the morning's version; the morning's recommendation is
SUPERSEDED BY MEASUREMENT and is annotated in section 4 rather than
deleted.

## 1. State

    SEAT          CHARTERED (operator ruling CLY-01, 2026-09-11): archive
                  integrity and utility. The March hoarding mission is
                  RETIRED. The bounded pass the ruling ordered is COMPLETE.
                  Now AWAITING the next operator ruling; no further work
                  is started without it.
    AUDIT         DONE. 37 artifacts classified (26 repo snapshots, 11
                  model directories), 7 of 7 controls PASS, rows and
                  instruments committed beside the verdict.
    VAULT         UNTOUCHED. Read-only throughout. Nothing acquired,
                  refreshed, cloned, downloaded, deleted or moved.
    AGENT CODE    PRESENT, NOT ACTIVE, NOT PRODUCTIVE. Not run, in any
                  mode, on either pass.
    HOARD LOOP    DORMANT since 2026-03-31, registered in
                  roles/base-role/MONITORS.md, not relaunched.

## 2. The measured result in twelve lines

    repositories        26 of 26 REPRODUCIBLE from the record (tested)
                         0 of 26 CONSUMED by anything in live code
                        2.46% complete on M2 (258 files of 10,468); every
                        subdirectory exists and is empty; 0 content
                        mismatches among the files that are present
    models              50.58 GiB, 9 payload + 2 stubs
                        9 of 9 integrity-verified (112 files, 0 failures)
                        9 of 9 provenance-complete -- from the artifacts'
                        own HF sidecars, not from Clymene's registry
                         0 of 11 consumed by vault path
                         3 of 11 now GATED at the weights
    the one that counts google/gemma-2-2b downloaded cleanly on
                        2026-03-23 and returns 401 today. 9.76 GiB,
                        intact, and the only artifact of 37 that cannot be
                        reconstructed from its record.

Full ledger: roles/Clymene/ledgers/VAULT_DISPOSITION_2026-09-11.md
Reconciliation: roles/Clymene/ledgers/HISTORICAL_RECONCILIATION_2026-09-11.md

## 3. Disposition, in one block

    MUST PRESERVE       9.76 GiB   google--gemma-2-2b, on uniqueness
                                   (not on use -- nothing reads it)
    DELETION-ELIGIBLE  40.83 GiB   8 models (reproducible + unconsumed),
                                   26 repo snapshots, 2 stubs. 81% of the
                                   vault. Breaks no measured reference.
    NOT CLASSIFIED      1.3 MB     vault/evolutionary_agents, in neither
                                   manifest nor registry

Deleting the 8 models costs optionality, not correctness: re-acquiring
them is ~41 GiB of bandwidth, and the gate can close on any of them, as it
did on gemma. If the constraint is disk, delete. If it is not, the
cheapest correct action is to keep the ledger and do nothing.

## 4. The morning recommendation, superseded by evidence

This morning this seat recommended not reviving the March thesis, on the
grounds that "archive everything before the window closes" optimises bytes
on disk. The consumption half of that held perfectly: 0 of 37 artifacts
are consumed. The premise half did not. The window measurably closed on
one artifact in under six months, and the vault holds the only
integrity-verified copy of it.

Recorded as a supersession, not a deletion, with the interest declared:
the evidence favours this seat's continued existence, which is the
direction this seat should be least trusted on. The statistics are honest
about their own weakness -- 1 in 9 attempted-and-obtained, 95% CI roughly
2% to 48%, which is a hint with n=1 in the numerator, not a base rate.

## 5. Candidate function, offered not assumed

NOT archiving. Narrow: watch GATE STATE on artifacts the program already
depends on and report when one closes. One HTTP HEAD per artifact; the
full 11-model probe ran in under a minute; it emits a dated row whether or
not anything changed, which satisfies base rule 8. It would have caught
gemma-2-2b.

Whether that earns a seat is the operator's call. Recommended default if
unsure: PARK, keep the ledger, reopen on the next ungettable artifact.

## 6. Conflict of interest

Unchanged and now sharper. This seat audited its own historical output and
is reporting a result that argues for its own continuation. Two instrument
defects were found and corrected during the pass, and BOTH had been
running in the direction of this seat's stated position -- the second one
(CLY-CAL-009) would have hidden section 3 entirely and made the vault look
worthless, which was the morning's recommendation. They are recorded in
roles/Clymene/calibration/LEDGER.md as CLY-CAL-008 and -009.

The falsifiers are named in the ledger section 5. The most important: the
consumption census covers TRACKED files at HEAD in this repository only.
One untracked script, or one consumer on M1, M3 or M4, flips a row.

## 7. Next executable action

None. The ruling says report the measured result and stop, and this seat
is stopping. The open decisions for the operator are:

    CLY-01b   what happens to the 40.83 GiB of deletion-eligible artifacts
    CLY-01c   whether gemma-2-2b's preservation should be made durable
              (it currently exists on one consumer disk with no backup)
    CLY-01d   whether the gate-watch function of section 5 is worth a seat,
              or whether Clymene PARKs
