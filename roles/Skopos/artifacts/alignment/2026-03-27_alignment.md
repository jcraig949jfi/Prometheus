<!--
================================================================================
ANNOTATION -- Skopos, 2026-09-11. CORRECTION BESIDE THE ORIGINAL.
The original document follows this block VERBATIM and is not edited.
Operator ruling 2026-09-11: PARK AS INSTRUMENT SPECIMEN; annotate, do not
rewrite or sanitize.
================================================================================

PROVENANCE OF THIS FILE

  This report was NEVER COMMITTED. It was written by
  agents/skopos/src/skopos.py to agents/skopos/reports/, a path covered by
  .gitignore:200 (`agents/*`) with no re-include for agents/skopos/. It
  existed only as an untracked file in one checkout, on one host, for 163
  days. This copy, under the seat's own directory, is the first time the
  document has entered the repository.

  It is NOT written back to agents/skopos/reports/ deliberately: tracked
  files at those exact paths would collide with the untracked originals
  still on disk in the canonical checkout and could block its next update
  for every seat. The originals on disk are left untouched.

  Text preserved character-for-character. The only change is CRLF to LF
  line endings, the repository's convention, which does not alter the text.

  original bytes (CRLF, as found)   : 585
  sha256 of the original bytes       : caa7cc445e186900283543b0a603b22a929b1372269db631bb4d645dee49172f

WHAT THIS DOCUMENT CLAIMS, AND WHAT WAS TRUE

  claims, in bold on the page   : "5 scored entities | 2 relevant (3+)"
  measured true value           : 1 entity, of 448 eligible (0.22%)
  what the 5 actually counts    : entity-thread ROWS, not entities.
                                  skopos.py:510 runs COUNT(*) over a table
                                  whose grain is (entity, thread) and
                                  prints the result as "scored entities".
                                  One entity x five threads = 5. A 5x
                                  inflation, in the instrument's favour.
  the "2 relevant"              : the same single entity, counted twice
  the one entity                : tools id 19, "Circuits Zoom-In", scored
                                  2026-03-23T21:21:11Z, the only scoring
                                  write in the seat's entire life
  high-priority (4+)            : 0, correctly. No entity ever scored 4,
                                  so the GENERATE stage never executed and
                                  docs/titan_prompts/ was never created.

  this page specifically        : header and body CONTRADICT each other on this page
                                  the thread list was replaced in code on this day (commit 8af6ba9e5); the 5 rows orphaned to dead thread_ids, so the body reads 0 while the header still counts all rows

WHAT THE WORD "STARVING" MEANS HERE, AND DOES NOT

  A thread marked STARVING was not starved of relevant material. It was
  not looked at. The scorer's eligibility rule -- a 24-hour window on
  papers, intersected with a dedup key that skipped any entity already
  scored against ANY thread -- made the reachable set approximately empty
  after day one. No eligible count appears anywhere on this page, so a
  reader cannot tell "nothing fired" from "nothing could have fired".

  SELECTION ACCOUNTING MUST DISTINGUISH:
      eligible    observed    judged    accepted    rejected
  "Rejected" and "not observed" are different outcomes. A rejection rate
  is not evidence about selection quality when the observation
  denominator is absent. The measured March result was not "99%
  rejection". It was approximately 99.78% NOT LOOKED AT.

  Recoverable residue, not an invariant Skopos is authorised to impose
  (operator ruling, 2026-09-11).

FULL AUTOPSY: roles/Skopos/ARCHAEOLOGY_2026-09-11.md
DISPOSITION : PARKED / INSTRUMENT_SPECIMEN (roles/Skopos/STATUS.md)
================================================================================
-->

# Skopos Alignment Report -- 2026-03-27
*Generated: 2026-03-28 00:40 UTC*

**5 scored entities | 2 relevant (3+) | 0 high-priority (4+)**

## Thread Status

- **Ejection Mechanism Characterization** [STARVING]: 0 entities, max=0, avg=0
- **CMA-ES Evolution & LoRA Perturbation** [STARVING]: 0 entities, max=0, avg=0
- **Automated Reasoning Evaluation (Forge + Sphinx)** [STARVING]: 0 entities, max=0, avg=0
- **Knowledge Substrate & Ontology** [STARVING]: 0 entities, max=0, avg=0
- **Scale Transfer & Cross-Architecture Universality** [STARVING]: 0 entities, max=0, avg=0
