# Cycle 054 — PRE-REGISTRATION: verifying the MAHLER_TABLE provenance chain

**DISCLOSURE FIRST, because it changes what may honestly be predicted.** Before writing this
document I read `_mahler_data.py`'s header. **It already documents the expansion**, and it
contradicts my own cycle-053 finding rather than confirming it:

> *2026-04-29 refresh — Loaded `Known180.gz` (the canonical Mossinghoff "M < 1.3 through
> degree 180" list, **8438 polynomials**) from the Wayback Machine snapshot ... new entries are
> appended to `MAHLER_TABLE` after the original 178-entry Phase-1 curated section.*
> Plus Sac-Épée 2024 and Idris/Sac-Épée 2026 entries, *"each independently M-verified."*

**So cycle 053's claim — "Mossinghoff's published list is ~178 specimens, the table is 48x
that" — is itself an attribution error, mine.** I took the *test's* docstring as the authority
on what Mossinghoff published, and never opened the data module that documents the refresh.
**Mossinghoff's own canonical list is 8,438 entries**, not 178; 178 was one curated Phase-1
section of it.

**No prediction below concerns whether the expansion is documented — that is settled and I am
not scoring myself on it.** What remains open is whether the documented chain is *true*, which
the docstring cannot establish about itself.

## The open question

A docstring asserting its own provenance is not evidence for it. The bundled raw artifact is.

## Predictions, with confidence and a DIFFICULTY tag

New this cycle per cycle 053's trap: **`difficulty`** records when the mechanism was known
relative to the prediction — `PRIOR` (established before the prediction), `OPEN` (genuinely
undetermined at write time). A clean sweep of `PRIOR` calls is not calibration evidence.

1. **`_known180_raw.gz` exists and parses to 8,438 polynomials**, matching the header.
   Confidence **moderate-to-high**; difficulty **OPEN** — I have not opened the file, and a
   count that fails to reproduce would mean the header describes an import that did not happen
   as written.
2. **The arithmetic closes**: 178 + 8,438 + (Sac-Épée/Idris entries) = 8,625 exactly, with the
   residual accounted for by name. Confidence **moderate**; difficulty **OPEN**.
3. **Every Known180 entry satisfies M < 1.3**, the list's own defining cutoff — an internal
   consistency check the label makes falsifiable. Confidence **moderate-to-high**; difficulty
   **OPEN**.
4. **The ~178-entry Phase-1 section is a SUBSET of Known180** rather than disjoint from it, so
   the table double-counts nothing. Confidence **low-to-moderate**; difficulty **OPEN** — the
   header says "appended after", which describes position, not disjointness.
5. **`mahler.py`'s wrapper docstring is stale relative to `_mahler_data.py`'s** and still
   describes the pre-refresh table. Confidence **moderate**; difficulty **OPEN**.

## Kill test

**If prediction 3 fails — Known180 entries exceeding M < 1.3 — the table is contaminated**, not
merely mislabelled, and every conclusion drawn over "all 8,625 entries" (including my cycle-048
closure of HITL #266) needs re-examination rather than a docstring fix.

## What I will NOT do

Not editing `test_authority_mossinghoff_178_entries` or either docstring this cycle. **A stale
test that has been correctly reporting drift is more valuable red than green** until the
provenance is established; silencing it before knowing the answer would destroy the only signal
that surfaced this.

*— Techne, cycle 054, after reading one docstring and before opening any artifact.*
