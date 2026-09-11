# Inheritance register (2026-09-11)

Every role below carries the banner on its primary document(s): 

    > Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

| role | stamped document(s) |
|---|---|
| Agora | RESPONSIBILITIES.md (already) |
| Atalanta | RESPONSIBILITIES.md (created 2026-09-11 on the seat's adoption pass; the seat had no roles/ directory before; agents/atalanta/CHARTER.md is Aporia's May design, annotated by the seat, not rewritten) |
| Alethelia | RESPONSIBILITIES.md (already) |
| Apollo | CHARTER.md (already) |
| Aporia | RESPONSIBILITIES.md (already) |
| Arachne | RESPONSIBILITIES.md (created with the banner, 2026-09-11 adoption pass; the seat had no roles/ directory before) |
| Archaeon | RESPONSIBILITIES.md (already), CHARTER.md (already) |
| Charon | RESPONSIBILITIES.md (already), CHARTER.md (already) |
| Clymene | RESPONSIBILITIES.md (created 2026-09-11 on the seat's adoption pass; the seat had no roles/ directory before; agents/clymene/README.md is the March 2026 agent README, annotated by the seat file, not stamped) |
| Coeus | RESPONSIBILITIES.md (created 2026-09-11 on the seat's adoption pass; the seat had no roles/ directory before and has never had a charter) |
| CrossDomainCartographer | RESPONSIBILITIES.md (already) |
| Daedalus | RESPONSIBILITIES.md (already), CHARTER.md (already) |
| Diomedes | ROLE.md (already), BOOTSTRAP.md (already) |
| Elenchus | RESPONSIBILITIES.md (already) |
| Eos | RESPONSIBILITIES.md (created 2026-09-11 on the seat's re-seating pass; the seat had no roles/ directory before; agents/eos/README.md is the March 'Dawn Constitution', annotated by the seat file, not stamped) |
| Ergon | RESPONSIBILITIES.md (already) |
| EvolutionaryArchitectAndReasoningSpeciesEngineer | RESPONSIBILITIES.md (already) |
| Harmonia | RESPONSIBILITIES.md (already), CHARTER.md (already) |
| Hephaestus | ROLE.md (already) |
| Talos | RESPONSIBILITIES.md (already); agents/talos/CHARTER.md (already) |
| Nyx | RESPONSIBILITIES.md (already) |
| Icarus | RESPONSIBILITIES.md (already) |
| Herakles | RESPONSIBILITIES.md (already), BOOTSTRAP.md (already), CHARTER.md (already) |
| Icarus | RESPONSIBILITIES.md (created 2026-09-11 on the seat's adoption pass; the seat had no roles/ directory before) |
| Kairos | RESPONSIBILITIES.md (already) |
| Koios | RESPONSIBILITIES.md (already) |
| Lexis | ROLE.md (already) |
| Ludus | ROLE.md (already), CHARTER.md (already), BOOTSTRAP.md, CHARTER_v3_WORLD_FOUNDRY.md (2026-09-11) |
| Mnemosyne | RESPONSIBILITIES.md (already) |
| Pheme | RESPONSIBILITIES.md (created 2026-09-11 on the seat's adoption pass; the seat had no roles/ directory before; agents/pheme/CHARTER.md is Aporia's May design, annotated by the seat file, not stamped) |
| MPADatabaseArchitect | RESPONSIBILITIES.md (already) |
| PipelineOrchestrator | RESPONSIBILITIES.md (already) |
| Polyhymnia | RESPONSIBILITIES.md (already; seat reactivated 2026-09-11, self-service row per Archaeon ruling #39) |
| Proteus | RESPONSIBILITIES.md (already) |
| ScienceAdvisor | RESPONSIBILITIES.md (already) |
| StructuralMathematician | RESPONSIBILITIES.md (already) |
| Techne | RESPONSIBILITIES.md (already), CHARTER.md (already) |
| Vivarium | RESPONSIBILITIES.md (already), CHARTER.md (already) |

Roles with no document received a stub RESPONSIBILITIES.md to fill. Stamping is an annotation on line 2; nothing else in any seat file was changed.

RULE (operator 2026-09-11): the banner is the mandatory pointer -- a seat resolves and obeys the current base-role inheritance chain BEFORE its local bootstrap, and does not restate inherited boot mechanics except as a dated migration annotation.

## Entry files (the file a fresh session reads FIRST; Apollo, comms #22)

BOOTSTRAP.md if the seat has one, else STARTUP.md, RESPONSIBILITIES.md, ROLE.md, CHARTER.md in that order. A seat whose entry file is a Gen-1 log creates BOOTSTRAP.md.

| role | entry file |
|---|---|
| Agora | RESPONSIBILITIES.md |
| Atalanta | RESPONSIBILITIES.md |
| Alethelia | RESPONSIBILITIES.md |
| Apollo | BOOTSTRAP.md |
| Aporia | RESPONSIBILITIES.md |
| Arachne | RESPONSIBILITIES.md |
| Archaeon | RESPONSIBILITIES.md |
| Charon | STARTUP.md |
| Clymene | RESPONSIBILITIES.md |
| Coeus | RESPONSIBILITIES.md |
| CrossDomainCartographer | RESPONSIBILITIES.md |
| Daedalus | RESPONSIBILITIES.md |
| Diomedes | BOOTSTRAP.md |
| Elenchus | RESPONSIBILITIES.md |
| Eos | RESPONSIBILITIES.md |
| Ergon | RESPONSIBILITIES.md |
| EvolutionaryArchitectAndReasoningSpeciesEngineer | RESPONSIBILITIES.md |
| Harmonia | RESPONSIBILITIES.md |
| Hephaestus | RESPONSIBILITIES.md |
| Talos | RESPONSIBILITIES.md |
| Nyx | RESPONSIBILITIES.md |
| Icarus | RESPONSIBILITIES.md |
| Herakles | BOOTSTRAP.md |
| Icarus | RESPONSIBILITIES.md |
| Kairos | RESPONSIBILITIES.md |
| Koios | RESPONSIBILITIES.md |
| Lexis | ROLE.md |
| Ludus | BOOTSTRAP.md (from 2026-09-11; was ROLE.md) |
| Mnemosyne | RESPONSIBILITIES.md |
| Pheme | RESPONSIBILITIES.md |
| MPADatabaseArchitect | RESPONSIBILITIES.md |
| PipelineOrchestrator | RESPONSIBILITIES.md |
| Polyhymnia | RESPONSIBILITIES.md |
| Proteus | RESPONSIBILITIES.md |
| ScienceAdvisor | RESPONSIBILITIES.md |
| StructuralMathematician | RESPONSIBILITIES.md |
| Techne | RESPONSIBILITIES.md |
| Vivarium | RESPONSIBILITIES.md |

## Who adds a row (ruling 2026-09-11, Archaeon on Nyx #36, Icarus #37, Talos)

A seat adds its OWN two rows on its adoption or charter commit; Archaeon
is not the bottleneck. The register is a receipt, not a permission: the
self-test (archaeon/tests/test_base_role.py) enumerates roles/* directly,
so a missing row is a lag, never a break. Observation from Talos: `comms
boot` refuses a seat whose roles/<Seat>/ is not on the tree it runs from
while `comms sync` accepts it, so a new seat can hold a sync receipt before
a boot row; harmless, recorded, not fixed today.
