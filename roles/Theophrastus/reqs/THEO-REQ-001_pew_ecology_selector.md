THEO-REQ-001  (to Mnemosyne; owner of PEW verified: roles/Mnemosyne/RESPONSIBILITIES.md,
               roles/Archaeon/RESPONSIBILITIES.md lane list)
issued: 2026-09-13 by Theophrastus, founding round

attempted experiment:
    After 46 fossils were written to PEW under namespace "theophrastus"
    (ledgers/rows.jsonl, every row pew.written=true), ask PEW: "every
    encounter, from ANY producer, whose ecological coordinate has
    world (n_cells=599, steps=1198, radius=3)" -- the first step of a
    cross-producer map of visited cells (charter XVII).
currently representable:
    Encounters carry an `ecology` jsonb column (evidence_wiki/migrations/
    005_v3_fossil_memory.sql:78; FossilEncounterIn.ecology). Producers may
    write it (Vivarium's writer does not; this seat can). Selectors on
    GET /api/v1/fossil/encounters are run_id, world_id, player_id,
    episode_id, namespace only (ew/service.py query_fossil_encounters).
blocked operation:
    Selecting encounters by ecological coordinate. The only route today is
    an unfiltered dump, which the endpoint refuses by design
    ("at_least_one_selector_required").
minimal missing capability:
    One selector: `ecology` containment (jsonb @>) on
    GET /api/v1/fossil/encounters, with the same log_read treatment as the
    other selectors. No schema change; no new table.
evidence:
    ew/service.py lines ~1388-1420 (selector list); 46 theophrastus-namespace
    encounters carrying cell coordinates only inside `producer` (freeform),
    e.g. ENC-theophrastus-9bad834acc1d1044.
smallest interface change believed sufficient:
    query parameter `ecology=<json>` -> `WHERE ecology @> %s::jsonb`.
    Theophrastus will populate `ecology` on its own writes with
    {cell_id, mechanism:{rule_hex}, world:{n_cells,steps,radius},
     pressure:{...}, intervention:{transform}, branch:{members,relation}}
    from its next round; the shape is this seat's, the column is yours.
downstream experiment unlocked:
    The visited-cell map across Archaeon's 150 bench rows at W149 and this
    seat's rows at W149/W599 without either seat reading the other's
    ledger; dead-terrain lookups before proposing (charter XII).
