# Hecate calibration ledger

Currency: 2026-09-29. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-30 | wrote "index nodes 651" in the Pass 0-3 commit message from a partial printout | 607 (SUMMARY.json) | self, before push; message amended | every number in a commit message is read from the artifact in the same shell step, never from a truncated display
2026-09-30 | wrote Pass 4 ALT for HT-321a8fd8e0 W1 as "code beats matched-redundancy majority vote at equal agent count" | with 31 agents and 16 bits, majority vote cannot give each bit 3 copies; the ALT passes by counting (standard coding gain), so it could not fail | Pass 4 implementer, PASS4_OUTCOME.json notes | before freezing any attack, compute its outcome under the known-mechanism hypothesis; an attack whose result is fixed by arithmetic is not an attack (doctrine: guard that cannot fire)
