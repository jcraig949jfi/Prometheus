# NEXT CAMPAIGN RECOMMENDATION -- Bellerophon Z80 x Atlas (draft; finalized only after GROUNDING_REPORT.md)

Status: DRAFT. Part A (instrument requirements) follows from the forensics alone and does not depend on the grounding
outcome. Part B (scientific targets) is written only after the grounding round completes.

## A. Instrument requirements (from POST_CAMPAIGN_FORENSICS.md + ISSUE_AND_REPAIR_LEDGER.md)

A1. Physics v2 only (GATED aging, COPYALL budget, configured-task seeding with relocated hybrids, no capture credit,
    no world-made copies under endogenous physics). The v1 physics stays in the code solely for historical replay.
A2. Detectors are the v2 predicates (adjudication.py) on repaired fields: SELF_REPLICATION by provenance, verified
    exact solving of the configured task, horizon tails, paired geometry. The v1 triggers are never used for
    promotion or claims. Each detector ships with its positive, negative and cheat control cells (the G8 set) run
    in the EARLY stage; a failing control halts the campaign (as the v1 positive controls did).
A3. Promotion must be keyed to ADJUDICATED detectors and must be selective: in the long campaign 63% of families
    were promoted, promotion steered allocation toward a defect (POLLINATION, P1), and every late-stage "surge" was
    exposure. Require (i) a FIXED-ALLOCATION lane of >= 30% of runs for the whole window that is never
    promotion-driven (it is the only lane from which rates can be estimated), (ii) promotion on a detector only
    after its matched control arm has run on the SAME seeds, (iii) a trigger-score threshold calibrated so that the
    fixed lane promotes <= 10% of families.
A4. Family-level comparisons only through paired designs with a declared unit (seed pair), both directions counted,
    exposure matched (equal runs per arm per pair). No any()-over-unequal-sets flags.
A5. Family identity includes init_tapes; (family, seed) submitted once; late controls carry their own seed
    (M5/m1/M6 repaired).
A6. Resume path (s3): REPAIRED with test_s3 (truncated final line tolerated and recorded; no run-id reuse over
    orphaned run dirs; promotion rule replayed for rows appended after the checkpoint). Remaining gap: the specimen
    archive (novelty) is not rebuilt for appended rows -- irrelevant once promotion uses v2 detectors (A3), else fix
    before launch. The grounding driver re-executes missing runs only.
A7. Record provenance the forensics had to reconstruct: first_self_replication with genealogy and birth tapes
    (now in the summary), per-run SR counts per tick, world copies, and the pinned code commit in every config.json.
A8. Run from a pinned code copy (as both the 72 h campaign and the grounding round did).

## B. Scientific targets

(written after the grounding round)
