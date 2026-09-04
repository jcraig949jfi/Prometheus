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

## 2026-09-04 — M2 deployment window (infrastructure, not world-side)

James moved agent work to M2 (`SPECTREX5`, `192.168.1.191`) after M1's Claude budget ran out and
directed this seat to bring up SFE and PEW here. The reads below are **deployment surface** —
launchers, service configuration, connection contracts, schema DDL. No world physics, generator,
cost table, or world implementation source was opened, and R2's standing refusals are unchanged.

- 2026-09-04 · `SerendipityFoundry/SerendipityFoundryEngine/serve.py`, `sfe/release.py` · whole
  files · to launch the Engine on M2 and to diagnose why a service-launched instance reported
  `source_commit: null` · DEPLOYMENT SURFACE.
- 2026-09-04 · `SerendipityFoundryClient/docs/CONNECTING.md` (§1–3), `config/engine.example.json`,
  `SerendipityFoundryEngine/deploy/sfengine.cmd`, `GEN2.1_RELEASE_PACKET.md`,
  `SERENDIPITY_FOUNDRY_STATUS.txt` · to mint an M2 cert with the same posture as M1's and to know
  which battery results M2 had to reproduce · INTERFACE / DEPLOYMENT SURFACE.
- 2026-09-04 · `evidence_wiki/README.md`, `docs/OPERATIONS_V1.md`, `ew/db.py`, `ew/service.py`
  (route list only), `migrations/001–007` · to stand up PEW on M2 before the seat was told to
  stand down · DEPLOYMENT SURFACE. **Declared:** this is PEW's store layer, not an interface
  contract. Mnemosyne owns PEW; this seat has no further business in it.

**Boundary note.** SFE is Daedalus's tree and PEW is Mnemosyne's; this seat modified both under an
explicit operator directive, which is a departure from RESPONSIBILITIES §3 ("I do not maintain or
modify ... `SerendipityFoundry/`"). Recorded here rather than left implicit. Per James's ruling of
2026-09-04, **PEW reverts to Mnemosyne** and this seat has stood down from it; the SFE M2 instance
is deployment work carried out for Daedalus and committed under Daedalus's name in `53f11b286`.
