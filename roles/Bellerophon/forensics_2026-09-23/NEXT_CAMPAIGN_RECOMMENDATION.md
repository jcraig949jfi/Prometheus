# NEXT CAMPAIGN RECOMMENDATION -- Bellerophon Z80 x Atlas

Status: FINAL (after GROUNDING_REPORT.md). Part A follows from the forensics; Part B from the grounding round.

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

B0. Do NOT optimise for more spontaneous replicators. Access is settled well enough to study (1-5% of fresh runs,
    causally dependent on LDIR + the undefined-byte slide), and seeded replicators sustain in 37-40/40 runs in every
    topology. Post-replication questions can be studied from SEEDED and TRANSPLANTED replicators (345 genuine
    historical origin tapes are banked in receipts/grounding_inputs.json; 86% self-replicate in fresh worlds),
    with a small fresh-origin lane kept for base rates.

B1. The blocking fact: in this substrate reproduction and computation do not interact, or interact negatively.
    Under IMPLICIT pressure the task is causally inert (five task cells were run-for-run identical); under endogenous
    reproduction the copier is what selection sees and seeded task code decays (G3: 2/100 vs 100/100 external); a
    grafted copier destroys a task routine and the "beneficial" mutations are those that break the copier (G4);
    task-linked reproductive architecture 0/300 (G5). The directive's goal -- evolution modifying the machinery that
    generates future adaptive solutions -- has no pathway to act on yet.

B2. Proposed architecture: ONE coupling mechanism, chosen and preregistered before the campaign, e.g. (a) copy
    cost: each byte written into the window costs energy, and the energy that pays for it is earned only by verified
    task output (reproduction becomes task-funded); or (b) copy permission: a SELF_REPLICATION birth is viable only if
    the writer produced a correct task output in the same execution. Each needs its positive control (a hybrid that
    solves and copies spreads), negative control (a pure copier cannot persist), cheat control (output-before-read /
    input tampering cannot fund reproduction), and a matched coupling-OFF arm. Gate: a bounded (<= 6 h)
    preregistered pilot must show the coupling moves verified task retention in a matched design, and that fresh
    worlds are not uniformly extinct (the v2 base extinction is 95-100% outside WELL_MIXED), before any multi-day run.

B3. Campaign targets once coupled (in priority order): (i) heritable reproductive modifications that raise task
    reaching in DESCENDANTS (measured with paired geometry and verified solving, transplant/ablation tested);
    (ii) task-driven change in reproductive organisation with the frozen structural descriptor (G5 design, now with a
    pathway); (iii) persistence and ecology among replicating lineages (WELL_MIXED vs LOCAL, which survived grounding
    as an association); (iv) novelty beyond the shortest copier basin (the chemistry funnels 57% of origins into one
    LDIR route; track routes by mechanism key, receipts/ORIGINS.json).

B4. Keep for every claim: exposure-matched paired arms, both directions counted, fixed-allocation base-rate lane,
    specimen-level ablation AND transplant, and noting that NOPing the copy byte is not a knockout in this chemistry
    (HIST: 36.5% rescue by a copy instruction at a new position) -- knockouts must remove the setup (T into the
    window), not only the copy opcode.
