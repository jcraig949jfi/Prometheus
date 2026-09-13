# PREREGISTRATION -- pin-evidence semantics (batch 10 P1)

Filed BEFORE any change to the instrument.
Charter: roles/Techne/prompts/2026-09-13_batch10/OPERATOR_CHARTER.md sha256 2c28f471c33abc52...

## THE DEFECT, STATED MECHANICALLY

`acquire()` resolves a pin and writes it to TWO places:
  - `source_origin.artifacts[i]`  gains `sha256` (url) / `commit_resolved` (git)
  - `hashes.artifacts[i]`         gains `sha256` / `commit`

Every batch script's `main()` then rebuilds the record from a literal skeleton and copies forward
only `run_classification, test_classification, receipts, hashes, acquisition_date, observability,
nyx_handoff`. `source_origin` is NOT in that list, so re-running a batch script OVERWRITES
source_origin with the batch file's literal and DESTROYS the resolved pin. All 9 batch files share
this identical block.

Consequence measured BEFORE any change (2026-09-13):
  git artifacts                                    49
    source_origin says "HEAD" while a resolved
    commit is known (i.e. pin destroyed)           21
  url artifacts                                   407
    sha256 present in hashes but lost from
    source_origin                                 239
  TOTAL pin facts destroyed                       260   (all recoverable from hashes.artifacts)

This is not only a census-reading problem. A record whose source_origin says `commit: "HEAD"` asks
a future re-acquisition to trust a MOVING reference. That is precisely the question P7 requires us
to be able to answer NO to.

## INTENDED SEMANTICS (the thing being fixed to)

1. `source_origin.artifacts[]` is the REQUEST: where this body came from and which exact revision
   is wanted.
2. `hashes.artifacts[]` is the RECEIPT: what was actually obtained, with its digest/commit.
3. A pin is ESTABLISHED for an artifact when either side records a fixed identifier
   (`sha256` for url, a 40-hex `commit`/`commit_resolved` for git). "HEAD" is NOT a fixed identifier.
4. INVARIANT (new, to be enforced): once a pin is ESTABLISHED it must never be lost or downgraded.
   Rewriting a record may add or remove artifacts, but it may not replace a fixed reference with a
   moving one, nor drop a known digest.
5. The authoritative reader consults the RECEIPT first and the REQUEST second. Neither alone is
   sufficient: the receipt can be missing for a never-acquired body, and the request can be stale.

## WHAT WILL CHANGE

- `record.merge_artifact_pins(new, old)`: carries established pins from the old record's
  source_origin AND hashes.artifacts onto the matching artifacts of a rebuilt record, matched by
  url (git) or filename (url). Adding/removing artifacts stays legal; losing a pin does not.
- All 9 batch `main()` blocks call it, so re-running a batch script can no longer destroy a pin.
- A one-time BACKFILL restores the 260 destroyed pins into source_origin from hashes.artifacts.
- The census reader is NOT being re-patched; it already consults hashes.artifacts (batch 09).

## PREREGISTERED PREDICTIONS (falsifiable)

P-A. After the fix + backfill, "resolved commit lost from source_origin" goes 21 -> 0 and
     "sha256 lost from source_origin" goes 239 -> 0.
P-B. The preservation census counts DO NOT MOVE: SELF_CONTAINED 97, FULLY_PINNED_EXTERNALS 2,
     UNPINNED_EXTERNAL_DEPENDENCY 18, KNOWN_INCOMPLETE 0 (n=117).
     RATIONALE: the census reader already reads the receipt, so the request's fidelity should not
     affect it. IF THE CENSUS MOVES, my model of the defect is WRONG and that is the finding --
     it would mean the census was depending on source_origin somewhere I have not accounted for.
P-C. Re-running a batch script twice in a row is idempotent with respect to pins.

## CONTROLS THAT MUST EXIST (each must be able to FAIL)

C1 REPRODUCE-THE-59: a record with the pin present ONLY in hashes.artifacts must be classified
   PINNED by the authoritative reader, and UNPINNED by a deliberately source_origin-only reader.
   This reconstructs the exact error that reported 59 instead of 18. If C1's source_origin-only
   reader does not report "unpinned", the control is not reproducing the historical failure.
C2 NOT-ALWAYS-PINNED: a record with no pin anywhere must be classified UNPINNED. Without C2, C1
   would pass for a reader that simply always says "pinned".
C3 WRITER-DEFECT: simulate a batch re-run over an acquired record; every established pin must
   survive. Before the fix this control MUST fail; after it MUST pass.
C4 NO-MOVING-HEAD: no git artifact in any record may say "HEAD" while a resolved commit is known.

## WHAT IS PRESERVED AS AN INSTRUMENT FAILURE

The batch-09 erroneous census (59 fossils reported with unpinned artifacts; status tally
SELF_CONTAINED 44 / KNOWN_INCOMPLETE 2 / UNPINNED_EXTERNAL_DEPENDENCY 63 over n=109) is recorded in
INSTRUMENT_FAILURE_PIN_EVIDENCE_2026-09-13.json rather than deleted. The corrected batch-09 run
(SELF_CONTAINED 89 / KNOWN_INCOMPLETE 2 / UNPINNED 18) is recorded beside it.
