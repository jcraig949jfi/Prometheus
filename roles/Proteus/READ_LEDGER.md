# Proteus — world-side read ledger

Rule R2 of `RESPONSIBILITIES.md`: every world-side file this seat opens is recorded here with the
reason, before or at the time of reading. Interface contracts are readable. Physics, generators,
cost tables, and world implementation source are not. A world active in qualification is not
readable at all. An entry that cannot state an interface-level reason is a firewall breach and
is recorded as one.

Format: date · path · what was read (line range or section) · why · classification.

- 2026-09-02 · `SerendipityFoundry/SerendipityFoundryClient/docs/API.md` · lines 1–420, the whole
  REST contract · to specify the SFE integration contract (deliverable 9) · INTERFACE.
- 2026-09-02 · `SerendipityFoundry/incubator/PROMETHEUS_INCUBATOR_OEE_RESEARCH_PROGRAM_V0.txt` ·
  lines 1–150 (program thesis, revised World-0 scope, the three hypotheses, what World-0 does not
  test) · to understand the program Proteus supplies the player side of; contains a *description*
  of World-0 physics (conserved charge, costed VM steps, channel payout) at the level of the
  published program document, not implementation · PROGRAM DOCUMENT. **Declared:** this is the
  closest the seat has come to world internals; no cost values, generator distribution, or
  instruction set were read, and none will be.
- 2026-09-02 · `SerendipityFoundry/incubator/PROMETHEUS_INCUBATOR_WORLD0_DESIGN_REVIEW.txt` ·
  lines 1–60 (executive verdict, revisions R1–R3 headings) plus grep hits for "organism" naming
  section 3 "ORGANISM / CLIENT INTERFACE" · to locate the organism/client interface the Foundry
  must bind to; section 3 itself not yet read · PROGRAM DOCUMENT.
- 2026-09-02 · `SerendipityFoundry/incubator/world_phylogeny.schema.v0.json` and
  `failure_coordinate_schema.v0.json` · headers and required fields · to mirror schema discipline
  in the player manifest and lineage schemas · SCHEMA / INTERFACE.
- 2026-09-02 · `roles/Ludus/ROLE.md` · lines 1–60 (mandate, registries, the interface bet) · to
  place Ludus in §2 of the responsibilities; no world code opened · ROLE DOCUMENT.
- 2026-09-02 · `roles/Daedalus/RESPONSIBILITIES.md`, `CHARTER.md` (lines 1–60) · to place
  Daedalus and SFE in §2 · ROLE DOCUMENT.

**Not read, and will not be read:** `ludus/bench/worlds.py`, any file under
`SerendipityFoundry/SerendipityFoundryEngine/sfe/` beyond what `API.md` documents, any World-0
implementation once it exists.
