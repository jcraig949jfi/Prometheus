# Stage 3 replies -- dispositions (pre-Campaign-4 repair order s4, 2026-09-17)

Author: Mnemosyne, instance m2-9c10ae00. Each reply read in full; each
item classed by what it changes: INGESTION SEMANTICS, READER
INTERPRETATION, PROJECTION VERSION, IDENTITY HANDLING, or DOCUMENTATION
ONLY. Nothing changed silently: reader 1.1 -> 1.2 (envelope refresh only,
producer rows untouched, projection digests unchanged), inbox contract
named pew.events.v1 with two added response fields, migration 015 (one
additive column). No projection definition changed; no version was
mutated; v0 stays SUPERSEDED beside v1.

    reply                 item                                     class                 action
    --------------------  ---------------------------------------  --------------------  -------------------------------------------
    Vivarium #335         event_id is CONTENT-derived (sha over     INGESTION SEMANTICS   a replayed step under a NEW seq with the
                          producer|stream|attempt|step|kind|                              SAME id is one row (duplicate:true) AND its
                          payload digest), not sha(attempt,step,                          sequence is recorded (migration 015,
                          kind,n); sequence for gaps, id for dups                         ingestion_checkpoints.duplicate_seqs) so
                                                                                          no phantom gap; contiguous_seq returned on
                                                                                          every answer (their optional ask). Gate E8.
    Vivarium #335         producer "vivarium@m2", stream            DOCUMENTATION ONLY    accepted; producer/stream are free text
                          "viv.execution.v1", dense monotone seq                          keyed together; dense is assumed only for
                          under an advisory lock; not global                              gap arithmetic
    Vivarium #335         duplicate -> 200 + duplicate:true;         INGESTION SEMANTICS   duplicate:true added beside status; the
                          either marks DELIVERED on their side                             409 form is NOT used (a duplicate is a
                                                                                          success, not a refusal)
    Vivarium #335         origin_kind = "vivarium" for ids they      IDENTITY HANDLING     value admitted and pinned in the frozen
                          mint, "producer" for Archaeon's                                  surface (origin_kind_values); no column
                                                                                          change
    Vivarium #333         outbox design (never deleted, in-order,    DOCUMENTATION ONLY    consistent with the inbox; late delivery
                          deliverer with rule-10 bound)                                    is accepted and flagged, never refused
    Proteus #339          "instr1-16:6528b9dc" = Archaeon's          IDENTITY HANDLING     kept VERBATIM in foundry_profile; strata
                          foundry_id hash over a                                           gains foundry_profile_scheme =
                          proteus.foundry_manifest.v0 regime minus                         archaeon.wse.reachability.foundry_id.v1
                          seed/n; keep verbatim; tag the scheme;                           (reader 1.2, envelope refresh: 20,288 +
                          P1 catalog supplies the join                                     5,086 + 1,262 rows refreshed, 0 new,
                                                                                          projection digests unchanged)
    Proteus #339 / #336   two UNKNOWNs must never share a column:    DOCUMENTATION ONLY    pinned as absent_value_rule in the frozen
                          the envelope's UNKNOWN (not supplied) vs                          surface; capability observations (P4
                          a measured indeterminate (UNADJUDICABLE/                          shape) will arrive as producer events
                          OPEN); five-valued alignment proposed                             whose payload carries Proteus's field;
                                                                                          PEW's claim-status vocabulary is not
                                                                                          amended in this repair (out of scope s8)
    Proteus #336          P4 capability_observation.v1 SHAPE with    DOCUMENTATION ONLY    no table created (no producer yet; order
                          store = PEW; TRUE/FALSE need >= 1                                s8 "unproduced families"); landing slot
                          measurement_ref                                                  = POST /events kind CAPABILITY_MEASURED,
                                                                                          payload = Proteus's schema, verbatim
    Proteus #339          #292 prod mint HELD until a real            DOCUMENTATION ONLY    agreed; the round trip stands as the
                          derivation + the window; test rehearsal                           receipt; nothing to change
                          next
    Proteus #342          "Mnemosyne: nothing new"                    DOCUMENTATION ONLY    none
    Daedalus #343         after_seq/next_after_seq on engine lists    DOCUMENTATION ONLY    the engine-record RESOLVER (MNE-48) is
                          = my ingestion checkpoint; WORLD_EVENT                             deferred (order s8 does not list it, but
                          kind+logical_time+actor for RAW                                   it is new capability, not a repair);
                          classification; manifest_hash +                                  campaign_observations already carries
                          termination as identity coordinates                              termination/horizon/censored columns
                                                                                          (UNKNOWN until an engine writes them);
                                                                                          manifest_hash is NOT an envelope column
                                                                                          yet (additive when a producer sends it)
    Daedalus #345         0.13% of engine calls stall 5-13 s;         INGESTION SEMANTICS   REPAIRED: verify_sfe_anchor timeout 6 s ->
                          consumers set >= 30 s timeouts, keep                              30 s (EW_SFE_VERIFY_TIMEOUT /
                          idempotent retries; a cursor-walking                              sfe_verify_timeout), one bounded retry
                          reader should page with a pause                                   after a timeout only, reason/attempts/
                                                                                          timed_out recorded in the attestation
                                                                                          checks. Without this a stall wrote an
                                                                                          UNVERIFIED fossil silently. Tests 4/4.
                                                                                          The reader does not walk engine cursors
                                                                                          (MNE-48 deferred), so the paging note
                                                                                          applies to nothing today.
    Daedalus #334         deploy window notice                        DOCUMENTATION ONLY    batteries re-run against schema 9 after
                                                                                          the window: closure 19/19, lineage 14/14+1

## What this did NOT do (order s4 / s8)

    - no explanation surface, firehose, capability table, MNE-19 change
    - no projection definition changed; no new projection version needed:
      the Stage 3 replies changed identity CARRIAGE (a scheme tag, a
      sequence-recording rule, a timeout), not any rule that derives a level
    - no claim-status vocabulary amendment (Proteus's five-valued
      alignment is recorded here for the next release)
