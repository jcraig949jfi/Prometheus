# Hestia audit 1 -- plan, frozen before any dossier is written

Currency: 2026-10-06. Instance Hestia[buckkeep-8cd68af4], branch
hestia/boot-2026-10-06, base 013e7ce5e, worktree
Prometheus-worktrees/hestia-boot-2026-10-06.
Charter: roles/Hestia/prompts/2026-10-06_charter/ (verbatim, MANIFEST).

This file is committed BEFORE any engine dossier exists, so the
population, the rubric and the verdict vocabulary cannot be bent to fit
what the audit finds. Additions after this commit are annotated, never
silent.

## 1. Population

Source of the inventory: docs/fleet/fleet_state.json at 013e7ce5e
(Achilles census, prometheus.fleet_census.v2), key `engines`, 134 rows by
kind: legacy 45, research-engine 33, infrastructure 23, auditor 12,
reporting 8, data 4, experiment-ecosystem 3, index-search 2, dashboard 2,
communication 2.

INCLUSION: an engine is audited if it is a SUBSTRATE or ECOLOGY in which
reasoning-like mechanisms are meant to arise, be grown, or be measured as
arising -- i.e. it bears on the charter's question ("alternative synthetic
cognitive architectures ... primitive reasoning circuits").

Audited (25 engines, 8 audit groups):

    G1  Aether (AGE native-circuitry engine; Aether/, roles/Aether)
    G2  primordial (Nestor; Primordial Machine swarm, tensor brains)
        odysseus (spiking circuit sharded across machines)
    G3  prometheus/ananke (PTE packet-tensor substrate, primitive VM)
        Moonshot H2/H3 design (Themis; survival-only evolution, integer
          neural primitive; roles/Themis/design/)
        sigma_kernel (substrate kernel)
    G4  prometheus/cosmos (world physics, law mining)
        ensorain (tensor world engine, WTP-01..04)
        ludus (board games as worlds)
    G5  prometheus/z80atlas (Bellerophon) and archaeon/z80atlas
        ares (graph organism under pressure)
        crius (adaptive workspace sandbox)
    G6  SFE ecology: SerendipityFoundry/SerendipityFoundryEngine,
          SerendipityFoundry/worldfoundry, vivarium, proteus,
          archaeon/frontier, archaeon/wse
        nyx (ORGAN disassembly)
    G7  roles/Aphrodite/engine (Campaign 1 engine; BETA-02)
        incubation, incubation_d (D-VM)
        alien_circuitry
        agent_d2_blind .. agent_d5_blind (August D-series)
    G8  theseus/synth (k-way concept collision, no LLM)
        tyche (evolved perceptual lenses)
        herakles/evca (CA executor)
        forge lineage: forge, agents/hephaestus, agents/nous, hecate
          (LLM-generated reasoning tools; audited as the cosplay control)

EXCLUDED, with reason:
- Neural/LLM evolution (apollo, aethon, ignis, rhea, arcanum): the charter
  scopes architectures "distinct from ... traditional artificial neural
  networks, and current LLMs". Named here so the exclusion is visible.
- Mathematical-data cartography (aporia catalogue, charon, cartography,
  harmonia tensor-train, koios, zoo, theseus generator, ergon): instruments
  over human mathematical data, not cognitive substrates.
- Infrastructure, auditors, reporting, dashboards, index-search,
  communication, data: not engines in the charter's sense.
- Remaining legacy agents/* daemons: corpus, crawler and scheduling loops.
An excluded engine can be added by the operator; it is then audited under
this same rubric and the addition annotated here.

## 2. Rubric (the charter's, made operational)

Per engine, a dossier at roles/Hestia/audit/2026-10-06/dossiers/<id>.md:

    0. Identity      paths, seat, census state, SHAs read, what was NOT read
    1. Mechanism     what the code actually does, cited file:line;
                     documented claims vs observed code kept separate
    2. Evidence      what has been measured, cited to committed result
                     files; tier each: OBSERVED (rows on main) / CLAIMED
                     (prose only) / DESIGNED (not run)
    3. Matrix
       3a Combinatorial explosion and reachability: the search space
          written as a number or a formula; where it explodes; where the
          reachable set is a desert; what the measured hit rates imply
       3b Cosplay vs foundation: which component does the work that is
          called reasoning; is it a fixed algorithm, a hand-coded
          heuristic, a selection loop over a tiny operator set, or a
          mechanism that composes; the ceiling, stated concretely
       3c Substrate bottlenecks: representation, state, memory,
          addressing, credit assignment, compositionality, I/O bandwidth
    4. Deliverable sections (the charter's four)
       Discovery Approach / The Brick Walls / Seed Viability /
       Evolutionary Roadmap
    5. What would change this verdict (the falsifier of the audit itself)

## 3. Verdict vocabulary (seed viability)

    DEAD_END             no component survives as a seed; the mechanism's
                         ceiling is reached or provably near
    SALVAGE_COMPONENT    the engine as built does not scale, but a named
                         component (instrument, primitive, representation)
                         should be carried forward elsewhere
    VIABLE_SEED          a named mechanism composes and has a credible
                         path past its current wall; roadmap given
    INSUFFICIENT_EVIDENCE the code and rows do not support any of the
                         above; what measurement would decide is named

Instruments (rulers, harnesses, ledgers) are judged on whether they would
detect a real reasoning circuit if one arose, not on whether they are one.

## 4. Discipline

- Read-only. No engine is run, edited, or written to (base rule 6). Small
  side calculations (state-space sizes, combinatorics) are done in a
  scratch directory and their numbers shown.
- Code beats prose: a claim in a README is CLAIMED until the code or a
  committed row shows it.
- This audit is a model's assessment for the operator. It admits,
  retires and promotes nothing; it marks no seat dead (base role, "seat
  states"). A DEAD_END verdict is about the mechanism as built, not the
  lineage.
- Conflict of interest: the auditor is the same model family as most
  engine authors; shared blind spots are likely. An independent reviewer
  (different model or human) should attack the verdicts.
