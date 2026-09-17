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

## 2026-09-16 — consumer-side interface reads (not world-side)

- 2026-09-16 · `vivarium/viv/cegis_boolean.py` · lines 150–260 (`_size`, `_Split`,
  `enumerate_candidates`, `_Oracle`) and 340–360 (the K-prefix seeding loop) · to state the
  kind's size measure, leaf set and seeding rule exactly in the H1 beta sizing table
  (`proteus/eval/BOOLEAN_UNIVERSE_TABLE.json`) rather than re-derive them · CONSUMER INTERFACE.
  Not a world; the kind that consumes Proteus's evaluator. Read, never modified. (The same file
  was read on 2026-09-10 for the witness-collapse finding and not ledgered then; recorded now.)
- 2026-09-16 · `herakles/evca/derive.py` · lines 1–135 and 264–284 (module docstring, ids,
  `_record` shape, `normalise_edits`, `verify_record`) and `core.py` lines 167–190 (the hex
  spelling `decode_table` accepts) · to join Herakles's content id to PR-ID's `organism_ref`
  without re-implementing or contradicting their canonicalisation · LIBRARY INTERFACE (identity
  and record shape; the CA update rule itself was not read).
- 2026-09-16 · `roles/Vivarium/INBOX_HERAKLES_CA_DENSITY_LIBRARY_ADDITIONS_2026-09-16.md` · whole
  · cross-seat mail on main naming `herakles.evca.derive` as built · ROLE MAIL.

## 2026-09-17 -- point-release Stage 0 reads (directive section A; instance m2-7d051790)

- 2026-09-17 - `archaeon/campaign1/CAMPAIGN_REPORT.md` (grep for organism/foundry/grammar lines
  + sections 0, 7, 11), `archaeon/campaign2/CAMPAIGN_REPORT.md` (whole), `archaeon/campaign3/
  CAMPAIGN_REPORT.md` (whole) - required reading A of the operator's point-release directive;
  the reports describe cells (W0, W1_dN, W2_K2 ...) at the level of published results and
  named world specs - PROGRAM / CAMPAIGN DOCUMENT. **Declared:** no world implementation,
  physics, generator or cost table was opened; `archaeon/wse/worlds.py` was NOT read; the
  campaigns are CLOSED (cb9135104), so no world was active in qualification.
- 2026-09-17 - `archaeon/wse/evolve.py` lines 1-27 (module docstring), 44-57 (the FOUNDRY
  dict), 160-200 (gen0/common_fill, the `proteus.foundry.generate` call sites) - to state
  exactly how Proteus's generator is consumed and what the generation-0 regime dict is -
  CONSUMER INTERFACE. Selection, evaluation and world binding in the same file were not read.
- 2026-09-17 - `archaeon/wse/reachability.py` lines 30-52 (`foundry_id`, `default_foundry_id`)
  - to answer Mnemosyne #327 ("whose identity is instr1-16:6528b9dc") by recomputation -
  CONSUMER INTERFACE.
- 2026-09-17 - `archaeon/campaign1/sfe01.py` line 47 (FOUNDRY_C1), `archaeon/campaign2/
  c2base.py` line 36 (FOUNDRY_C2), `archaeon/campaign3/c3base.py` lines 15, 36 (imports
  FOUNDRY_C2) - to catalog which regime ran in which campaign - CONSUMER INTERFACE.
- 2026-09-17 - `SerendipityFoundry/SerendipityFoundryEngine/docs/point_release_2026-09/
  SFE_POINT_RELEASE_REVIEW.md` (D4 block, Stage 3 asks), `evidence_wiki/docs/point_release/
  PEW_CAMPAIGN_INGESTION_CONTRACT.md` (s2, s9), `evidence_wiki/ew/ontology.py` (vocabularies),
  `evidence_wiki/migrations/005/006/013` (fossil_players columns), `roles/Vivarium/
  point_release/IDENTITY_TRANSLATION_CONTRACT.md` (section D rows naming Proteus, A7),
  `START_BUNDLE_SCHEMA.md` (s2-s3) - Stage 3 peer review as the directive requires - PEER
  INTERFACE / SCHEMA. Not world-side.

- 2026-09-17 - `evidence_wiki/docs/PROTEUS_MINT_WRITE_CONTRACT.md` (whole), `evidence_wiki/ew/client.py`
  (register_fossil_player / get_fossil_player / token resolution lines), `evidence_wiki/ew/service.py`
  (class FossilPlayerIn only), `archaeon/campaign2/C2-SFE-02/PREREG.json` (budget.foundry_id, a
  receipt field) - PROTEUS-36 rehearsal against Mnemosyne's route and the receipt join test of
  PROTEUS-29 - PEER INTERFACE / RECEIPT. Not world-side. Token file existence checked, contents
  never read.
