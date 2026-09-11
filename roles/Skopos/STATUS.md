# Skopos -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11T17:40Z. This file is FINAL for the parked state; it is
updated again only if the resurrection predicate is satisfied or the
operator rules otherwise.

    disposition       PARKED / INSTRUMENT_SPECIMEN
                      (operator ruling, 2026-09-11; SKOPOS-XL-01 CLOSED)
    four words        PRESENT (code, data, seat directory and, since
                        today, the six historical reports are committed)
                      not ACTIVE (last run 2026-04-01; will not run)
                      not PRODUCTIVE (lifetime: 1 entity scored of 448
                        eligible, 5 rows, 0 Titan prompts)
                      VALID -- not applicable; nothing adjudicated
    latent charter    Skopos does not decide what is relevant. Skopos
                      measures whether a selector had a fair opportunity
                      to decide, and whether its reported performance
                      survives controls.  NOT ACTIVE.
    resurrection      an active seat that owns a selector explicitly
    predicate         requests selection instrumentation AND names the
                      selection surface to be measured. Until then,
                      nothing here becomes live.
    machine           M2 (SPECTREX5)
    worktree          Prometheus-worktrees/skopos-base-role -- removed at
                      session close under WORKING_CONTRACT.md s5
    base_sha          363120e08665af062d40810183624fa23ed19698

## Loops, monitors, watchdogs and scheduled processes owned

NONE ACTIVE, and none left behind by this pass. The single registry row,
SkoposScoreCycle in roles/base-role/MONITORS.md, is state PARKED /
INSTRUMENT_SPECIMEN. No daemon, scorer or model call was made on either
pass. No recurring process exists.

## What was executed under the ruling

    SKOPOS-06   agents/skopos/README.md annotated in place. 116 lines
                inserted, 0 deleted. Original text, including its
                non-ASCII characters, unchanged below the block.
    SKOPOS-07   the six alignment reports annotated, originals preserved
                byte-for-byte with their sha256, at
                roles/Skopos/artifacts/alignment/.

Everything else on the backlog is closed as PARKED, not deferred.

## What was found while executing it

The six reports were NEVER COMMITTED -- .gitignore:200 (`agents/*`), no
re-include for agents/skopos/. They existed only as untracked files in one
working directory on one host for 163 days, while a downstream consumer
(agents/metis/src/metis.py:94-103) read them off disk as model context.
They entered version control for the first time today. Full note:
ARCHAEOLOGY section 1 correction; the seat's own error in describing them
is CALIBRATION.md L-06.

## The finding this specimen carries

    eligible    observed    judged    accepted    rejected

"Rejected" and "not observed" are different outcomes. A rejection rate is
not evidence about selection quality when the observation denominator is
absent. The March result was not "99% rejection"; it was approximately
99.78% NOT LOOKED AT. Recoverable residue, not an invariant this seat is
authorised to impose.

## Nearest honest summary

An agent whose job was to notice what matters could not notice that it had
stopped working, published a number 5x in its own favour for ten days while
a health check said OK, and did it all in files that were never committed.
The seat is parked with that on the record, its artifacts corrected beside
their originals, and nothing running.
