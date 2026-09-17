# PEW point release -- Stage 0 inventory, Stage 1 delta, Stage 2 self-critique

Author: Mnemosyne, instance m2-9c10ae00, 2026-09-17. Status: DRAFT for
Stage 3. Read-only pass against origin/main cb9135104 (Campaign 3 CLOSED,
report authoritative). Companion documents in this directory:
PEW_CAMPAIGN_INGESTION_CONTRACT.md, PEW_STORE_LOCATION_DISPOSITION.md.
Directive and amendment verbatim: roles/Mnemosyne/prompts/
2026-09-17_point_release/. Inherits the base role.

## STAGE 0 -- evidence inventory (compact)

Campaign 1 lessons that land in PEW's layer
  - L-012/L-013: no resume, attempts indistinguishable, files renamed by
    hand. PEW consequence: attempt identity must be a typed column with
    an origin ('producer' vs 'reconstructed'); Campaign 1 attempts can
    only ever be reconstructed (contract T2).
  - L-007: intervention applied counts were untyped; INCONCLUSIVE was
    assigned by hand. PEW consequence: intended vs realized dose are two
    fields; disposition is never ingested as fact.
  - Section 11 telemetry list (first_solved_gen per cell/budget, source
    elite reward on every artifact, gen0 provenance, applied counts,
    rung x generation matrix, genome-length summaries): all of these are
    now rows Archaeon writes (C2/C3). None reach PEW.

Campaign 2 lessons
  - The foundry is part of the regime (L2 foundry keying; 2/3 prior was
    the other foundry's): foundry_profile is an envelope coordinate on
    every row, never a producer jsonb detail.
  - Design-keyed resume replayed another design's steps once (L2-021)
    before the fix: design_id (prereg_digest) belongs on every step ref.
  - Takeover by substituted material (L2-037/048): the raw fact is the
    per-generation origin share; "takeover" is a projection with a
    threshold parameter.
  - A forgetting shelf hidden by a battery mean (L-022): the per-rung x
    generation matrix is the evidence; the collapse is a projection.

Campaign 3 lessons (report sections 13, 15, 17)
  - Summit redefined mid-campaign to require held-out confirmation
    (D3-006): the single strongest argument for versioned projections
    over stored labels; reach_level v1/v2 in the contract.
  - Right-censoring and monotone budget lookup: censoring is a raw
    field (summit_censored, stopped_on_solve); "unreachable at budget"
    is a projection over pooled rows.
  - "An instrument gated on a fixed constant rather than on the measured
    state of its own space" recurred twice (slots 03, 06). PEW's own
    version of this defect: gate S2 keyed by machine (fixed 2026-09-16).
  - Import takeover is mechanics, not capability (12/12 vs 12/12): a
    projection over origin_shares must never carry a competence
    implication in its name or definition.
  - Campaign identity mis-stamped on every C3 receipt ("cmp2"): T1.

Recurring defects across the three: identity carried in prose or file
names rather than fields (attempts C1, campaign C3); labels standing in
for measurements (disposition by hand C1; summit C3); a fixed constant
standing in for a measured state (C3 x2, PEW S2).

Local patches that belong in PEW's layer: none from the campaigns --
Archaeon's machine never called PEW. In PEW itself: the environment-
keyed S2 gate (done), the fail-closed workspace guard (done).

Missing instrumentation (PEW side): ingestion of any of it; producer
checkpoints; a projection registry; the envelope columns.

Manual decisions that can become deterministic: none are PEW's to take.
The reader is deterministic by construction (content-addressed rows).

Scientific discretion that MUST stay above PEW: every threshold (0.45,
0.90, takeover theta), every disposition, every "corridor exists"
claim, the choice of which campaigns to ingest into which projection
version. PEW indexes and counts.

## STAGE 1 -- proposed delta (classified per amendment section 12)

    id   change                                   class        ship
    ---  ---------------------------------------  -----------  ------------
    P1   campaign ingestion reader over committed FIX /        MUST SHIP
         files (contract s3, s7) -- deterministic, INSTRUMENT
         idempotent, content-addressed; fixtures
         A1-A4, A7, A8
    P2   migration 014: envelope columns on        GENERALIZE   MUST SHIP
         typed_refs; campaign_observations;                     (deploy
         ingestion_checkpoints; projections                     window)
         registry (contract s4)
    P3   projection registry entries reach_level   NEW          MUST SHIP
         v1, corridor_edge v1; rebuild + digest;   CAPABILITY   (small)
         fixtures A5, A6
    P4   forgetting v1, takeover v1 projections     NEW          SHOULD SHIP
                                                   CAPABILITY   IF CHEAP
    P5   store-location resolution: O2 (M2-owned    HARDEN       MUST SHIP
         dump + weekly restore); O1/O3 per ruling                (blocking,
                                                                 operator)
    P6   MNE-19: ONTOLOGY_VERSION code constant 2    FIX          SHOULD SHIP
         vs registry 7 -- decide and align                       IF CHEAP
    P7   MNE-43: closure fails closed when the      HARDEN       DEFER (XL;
         engine verify config is absent                          needs a
                                                                 ruling)
    P8   post-campaign explanation surface          NEW          DEFER
         (Prompt 2 s7)                              CAPABILITY   (amend. 7F)
    P9   per-organism observation events            NEW          DEFER
                                                   CAPABILITY   (amend. 7E)
    P10  WORLD_PHASE_CHANGED / LESION_APPLIED typed  NEW          REJECT for
         tables without a producer                  CAPABILITY   this release
    P11  PEW computing shelf/summit with own         --           REJECT
         thresholds; PEW as sync dependency
    P12  Redis/stream transport                      --           REJECT
    P13  archaeon/workspace.py fail-open guard        FIX          not mine;
         (reported #290)                                         Archaeon

Per-change fields for P1-P3 (the MUST SHIP set):
  problem/evidence   zero campaign rows in PEW (measured); identity in
                     prose (T1-T4)
  owning layer       PEW (reader, schema, registry); Archaeon (row
                     definitions, unchanged)
  consumers          Archaeon (campaign 4 design from pooled evidence),
                     Harmonia (audit of a campaign's claims against its
                     rows), Kairos (read-only), Proteus (foundry-keyed
                     evidence), Vivarium (attempt ids join)
  compatibility      additive columns, new tables, new ref kinds; every
                     existing route and battery unchanged; old rows
                     NULL/UNKNOWN, never back-filled
  migration          one file, 014, in the deploy window, on the
                     canonical host named by the ruling (P5)
  scientific risk    a projection mistaken for a row. Mitigation: the
                     registry row carries version + params + source
                     kinds + limitations, and the API returns them
                     with every projection read (like fossil/contract)
  operational risk   the reader runs from a task worktree against
                     committed blobs; a PEW outage loses nothing (the
                     files remain the record); a store outage is P5
  cost               ~10^4 rows for campaigns 1-3; 21 MB ew grows by an
                     estimated <50 MB; one index per envelope column
  acceptance         contract s8 A1-A8
  rollback/revisit   drop the four objects (no producer depends on them
                     until campaign 4 chooses to post); revisit if
                     campaign 4's runner (Vivarium or Archaeon) emits a
                     different attempt/step identity -- the envelope
                     absorbs it by origin_kind

## STAGE 2 -- self-critique

  Does this encode the answer to a scientific question?
    KEEP with one MODIFY: reach_level v1 stores Archaeon's level AS
    WRITTEN and does not recompute -- so a later reader might take
    "level=SHELF" as PEW's finding. MODIFY: the API for
    campaign_observations returns level only through the projection
    endpoint (with its version), never as a bare column on the raw
    read; the raw read returns the measured numbers.
  Does it turn an interpretation into fact?
    The disposition_candidate is the trap. DROP from ingestion (kept:
    the receipt blob is content-addressed, so it is retrievable, just
    not a row).
  Could it contaminate old results?
    No write path from PEW to archaeon/wse exists (measured). ADD to
    the contract: a test that greps archaeon/wse for ew imports and
    fails if one appears -- the quarantine as a fixture, not a promise.
  Future-information leakage?
    A campaign-4 design that reads pooled reachability from PEW instead
    of REACHABILITY.jsonl reads the same numbers from a second place.
    Leakage would come from projections built over campaign 4's own
    partial rows during the campaign. ADD: projections are built over
    CLOSED campaigns by default; a build over an open campaign is a
    named parameter recorded in the registry row.
  New abstraction more flexible, or merely more complex?
    campaign_observations with kind + measured jsonb + a typed subset is
    two tables' worth of concept in one. KEEP for this release (three
    kinds, one reader); revisit at the next if a fourth kind needs its
    own typed columns.
  Long runs, partial failures, restarts, duplicates?
    The reader is restartable by construction (checkpoints per stream,
    content-addressed rows). Duplicates are no-ops. KEEP.
  Reconstructable after a crash?
    Yes: from git. That is the whole point of reading committed files
    first. KEEP.
  Telemetry nobody will query?
    Per-generation series (P1/R7) are the largest and least certain
    consumer. MODIFY: ingest per-generation rows for campaign 3 only at
    first (its series are the ones the forgetting/takeover projections
    need); campaigns 1-2 at run granularity; extend when a query asks.
  Generic enough for worlds not yet imagined?
    The envelope is; campaign_observations.kind is an open vocabulary
    extended by migration (as 012 did for ref kinds). KEEP.

Net: KEEP P1-P3, P5; MODIFY P1 (C3-only series at first) and the
projection read surface; DROP disposition ingestion; ADD the quarantine
fixture and the closed-campaign default.

## What remains agent judgment after this release

Which projection version a campaign report cites; whether a pooled
corridor edge is "a corridor"; when a campaign is closed enough to
build over; what to do when a producer row and its re-commit disagree
(the CONFLICT event is recorded; the ruling is Archaeon's).
