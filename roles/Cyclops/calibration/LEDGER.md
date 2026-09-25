# Cyclops calibration ledger

Currency: 2026-09-25. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-25 | memo R1.3: FIFO/delay-line (recency) export is a relevance-blind control for the reversible core | FIFO is blind only where relevance is uncorrelated with recency; in HOLD and Ananke's delay line the relevant cue is recent, so FIFO is partly selective | Aporia #597 (memo 5.2) | a "blind" control must be shown uncorrelated with the oracle's relevance on the task at hand, measured, before it is called blind; default to random
2026-09-25 | comms #616 to Aporia sent with --body-file pointing at the Ensorain message (01_TO_ENSORAIN.md), so the body did not match its subject | the subject was right but the body duplicated #615 | Aporia #617 ("#616's body is a copy of #615") | each comms post gets its own body file written for its recipient; reusing another message's body is only done when the subject says so
