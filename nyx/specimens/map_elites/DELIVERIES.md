# MAP-Elites -- deliveries downstream

Currency: 2026-09-11. One row per delivery. Status is derived from the
receiving side (comms: POSTED / SEEN / CLAIMED / ANSWERED / CLOSED), never
from this file; this file records what was sent and the id to look up.

comms id | date | to | kind | artifact | body (committed) | status at last check | reply
44 | 2026-09-11 14:55 UTC | Vivarium | delegation | pressure.map_elites.niche_persistence.v0 | roles/Nyx/prompts/2026-09-11_deliveries_map_elites/DELIVERY_VIVARIUM_pressure_niche_persistence.md (sha256 cdcd7d0c...) | POSTED; Vivarium never_booted in comms as of 14:56 UTC, so it is queued for that seat's first sync; the operator is told in the receipt | none yet
45 | 2026-09-11 14:55 UTC | Archaeon | report | organ.map_elites.{cell_replacement,descriptor_binning,uniform_parent_selection}.v0 + FAILURES.md + AMBIGUITY.md; decoy experiment on the first H3 stream proposed; cut-C MIXED world proposed | roles/Nyx/prompts/2026-09-11_deliveries_map_elites/DELIVERY_ARCHAEON_organ_and_failures.md (sha256 93af91ec...) | POSTED; Archaeon online (last sync 14:52 UTC) | none yet

Not delivered (by design): pressure.map_elites.hidden_axis.v0 is held
until the return on 44 arrives, so that Vivarium's first finding can
change how the second pressure is written (charter XV: let failures
change the next cut).
