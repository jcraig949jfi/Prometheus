# Projection rebuild receipt -- 2026-09-17

Author: Mnemosyne, instance m2-9c10ae00. Builder ew.projections/1.0.
Registry: GET /api/v1/projections (digest sha256:29623b7e19af2b89...).

    projection     version  status      rows   evidence  rebuild digest   source code identity
    -------------  -------  ----------  -----  --------  ---------------  -----------------------------------------
    reach_level    v1       BUILT       1,413  1,265     e7625bfb967f...  archaeon.wse.reachability@09558e0cbbc1a2...
    reach_level    v0       SUPERSEDED  1,413  1,265     7037fbc41aff...  archaeon.wse.reachability@bae94c23205a35... (pre-C3)
    corridor_edge  v1       BUILT          25    155     719fa5a1ec6f...  archaeon.wse.corridor@a8954c14953f8cf3...

Every entry carries: definition (prose of the pinned rule), source kinds,
thresholds (every number the rule uses), owner seat (Archaeon for all
three: the scientific definitions are Archaeon's), builder version, built
timestamp, evidence count, rebuild digest, limitations.

## Rebuild equality

    rebuild-check reach_level v1     equal (digest e7625bfb967f7015...)
    rebuild-check reach_level v0     equal (7037fbc41aff4f7d...)
    rebuild-check corridor_edge v1   equal (719fa5a1ec6f4045...)
    cross-cluster                    reach_level v1 and corridor_edge v1
                                     built on the REHEARSAL copy (M2
                                     cluster, pre-migration dump + C3
                                     ingest) produced the SAME digests as
                                     on the canonical store: the projection
                                     is a function of the evidence alone
    after campaigns 1-2 ingested     digests unchanged (the shared
                                     reachability/corridor tables were
                                     already fully ingested with C3;
                                     campaigns 1-2 added no reachability
                                     or corridor rows)

## Pin check (does PEW's copy of the rule match the producer?)

    reach_level v1: level re-derived from the stored numbers by the
    verbatim copy of level_of() AGREES with the producer's level on
    1265/1265 rows. A disagreement would have been reported on the row
    (agrees_with_producer=false), never resolved.

## Two readings, honestly coexisting (order s24)

    v0 (campaign 1-2 reading: full solve = training best >= 0.90, no
    held-out confirmation) versus v1 (D3-006), same 1,265 evidence rows:

        v0 FLOOR                -> v1 FLOOR    676
        v0 FLOOR                -> v1 SHELF     30   (0.45 <= best < 0.5)
        v0 FOOTHOLD             -> v1 SHELF    258
        v0 FULL_SOLVE_TRAINING  -> v1 SHELF    126   the D3-006 class:
                                                     a training-only
                                                     summit, not confirmed
        v0 FULL_SOLVE_TRAINING  -> v1 SUMMIT   175

    126 rows that one reading calls a full solve and the other does not.
    Neither reading touched ew.campaign_observations; a reader who wants
    the old picture gets it with its thresholds and its code identity;
    the registry says which is current.

## What was NOT built (order s6C)

    No generic summit truth, generalization truth or takeover truth.
    takeover_v1 and forgetting_v1 are drafted in the contract and not
    built: the C3-SFE-10 origin-share series and the C3 events{}
    collapse/appearance fields are ingested verbatim (kind run /
    generation), so both can be built from evidence when Archaeon
    states the threshold; PEW will not choose it.
