# Archaeology map — reconstructing a claim from an evidence id

Frozen 2026-09-04 (durability/diagnostics pass, Task 4).

Question this answers: an independent investigator, holding only an
`evidence_id` and network access to PEW, wants to reconstruct

    evidence -> claim / packet -> encounter binding -> fossil encounter
             -> player(s) -> world -> SFE event anchor

This document lists the minimum objects and the exact calls, then flags what
is NOT reachable that way. Everything below was walked against the live
service using the first real Harmonia evidence, `E-dbe8c504b8cc`
(transcript: `seam/archaeology_walk.txt`).

## The minimum object set

    ew.evidence            the record and its typed binding columns
                           (encounter_id, encounter_run_id)
    ew.claims              what was asserted (versioned; latest wins)
    ew.source_packets      WHERE the quote came from (uri, kind, content hash)
    ew.fossil_encounters   the execution: (encounter_id, run_id), world_id,
                           players[], seed, outcome, and the SFE anchor
                           (sfe_event_id, sfe_entry_hash, sfe_event_seq)
    ew.fossil_worlds       world version anchor (manifest_hash, sfe_head_hash,
                           world_binding_id, seed_root)
    ew.fossil_players      player version anchor (genome_hash = Proteus
                           organism_id, runtime_hash, lineage_id, generation)

Two relations carry the chain, and both are typed columns, not conventions:

    evidence.(encounter_id, encounter_run_key)
        -> FK -> fossil_encounters.(encounter_id, run_key)
    fossil_encounters.players[]  -> fossil_players.player_id
    fossil_encounters.world_id   -> fossil_worlds.world_id

The last two are joins by identifier, not enforced foreign keys.

## The walk, over HTTP only (all verified 200 unless noted)

    1  GET /api/v1/provenance/evidence/{evidence_id}
       ONE call returns: evidence row, fossil_encounter, sfe{world_id, run_id,
       event_id, entry_hash, event_seq}, proteus{organism_ids}, world_anchor,
       player_anchors. This is the spine of the reconstruction.

    2  GET /api/v1/claims/{claim_id}
       The assertion. NOTE THE SHAPE: the text is at `current.text_canonical`,
       not at the top level; the response also carries `versions`, `evidence`,
       `relations`, `derived`, `canonical_revision`.

    3  GET /api/v1/fossil/encounters/{encounter_id}/evidence
       Reverse direction: everything bound to that encounter.

    4  GET /api/v1/fossil/encounters?run_id=|world_id=|player_id=
       Find sibling executions, everything in a world, everything a given
       organism did.

    5  GET /api/v1/fossil/worlds/{world_id}
       GET /api/v1/fossil/players/{player_id}
       The version anchors on their own.

    6  GET /api/v1/provenance/{object_id}
       Works for evidence and claim ids. See gap A1 for packets.

Leaving PEW: `sfe_event_id` + `sfe_entry_hash` are verified against the SFE
ledger (`events.event_id`, `events.entry_hash`) by whoever holds SFE. PEW
deliberately has no SFE client, so that hop is the investigator's, by design
and not by omission.

## FLAGGED GAPS

### A1 — the source packet is not readable over HTTP  (the real one)

`GET /api/v1/packets/{packet_id}` does not exist (404); there is only
`POST /api/v1/packets`. `GET /api/v1/provenance/{packet_id}` also returns 404
("unknown object"). Confirmed live: `SP-c49bf366d3a2` -> 404 on both.

CONSEQUENCE: an archaeologist can see the evidence's `packet_id` and its
verbatim `source_quote`, but cannot resolve the packet to its `uri`, `kind`,
`git_commit` or `content_sha256` without SQL on M1. The *source of the quote*
— the thing that makes evidence evidence rather than assertion — is
**SQL-only, host-local**.

SEVERITY: high for archaeology, zero for integrity (the data is stored, only
the read path is missing).
FIX (additive, no adaptation): `GET /api/v1/packets/{packet_id}`, and teach
`/api/v1/provenance/{object_id}` to resolve `SP-` ids.
NOT DONE in this pass: priority order was backup, then diagnostics; this is a
missing read path, not an integrity issue.

### A2 — claim payload shape is undocumented knowledge

The claim text lives at `current.text_canonical`. A first-time reader looking
at the top level finds nothing and may conclude the text is missing — as
happened while writing this document. Documented here; no code change.

### A3 — namespace census requires SQL

Which objects are visible in `ew.claims_prod` / `evidence_prod` /
`relations_prod` is answerable only on M1. Same gap as D1 in
`DEFERRED_ISSUES.md`.

### A4 — the SFE hop is host-local by design

Verifying that a `(sfe_event_id, sfe_entry_hash)` pair really exists in the
ledger requires access to SFE's database or `/v2` API. PEW asserts the anchor;
it does not and will not attest ledger membership.

## What is NOT required (deliberately)

No magic filenames, no naming conventions, no free-text parsing, and no
undocumented joins. Every hop in the walk above is either a typed column or a
documented endpoint, and the machine-readable contract at
`GET /api/v1/fossil/contract` describes the identifier semantics without
reference to any document.
