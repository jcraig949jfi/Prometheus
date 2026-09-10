# Operation Necropolis

Systematic archaeology and selective resurrection of Prometheus' historical agents.

Prometheus v1 accumulated ~48 historical agents/components across several architectural eras.
Many were labelled dead, shelved, superseded, low-yield, or failed. Later audits showed those
labels **conflated very different states** — a falsified premise, an implementation failure, a
representation failure, a measurement failure, a producer dead with a healthy consumer (or the
reverse), a resource gate, an orchestration/liveness failure, a good mechanism buried under
low-information emissions, or no established design failure at all.

Necropolis revisits each agent as a historical experimental organism and drives it through:

```
historical organism -> evidence -> kill boundary -> surviving mechanism
                    -> reusable residue -> descendant experiment -> consumption/effect
```

**A corpse is not automatically resurrected.** The parent stays historically dead (LAW N2). Any
resurrection is a *new descendant* with an explicitly changed design (LAW N8) and a preregistered
discriminating test (LAW N9). Read `CHARTER.md` first — it is the operating contract.

## Layout

```
engine/necropolis/
    README.md          <- this file
    CHARTER.md         <- the 16 laws + classification vocabulary + death-axis vocabulary
    SCHEMA.json        <- machine-readable dossier schema (JSON Schema 2020-12 superset of AGENT_AUTOPSIES.jsonl)
    ROLES.md           <- Necromancer / Cleric / Doctor Frankenstein role contracts (laws F1-F6)
    SEAMS.md           <- how Necropolis objects interoperate with existing engine/ machinery
    ROSTER.jsonl       <- 48 canonical agents (intake only; no resurrection decisions)
    QUEUE.jsonl        <- seeded Necromancer investigations (READY, not dispatched)
    build_roster.py    <- reproducible ROSTER generator (derives from evidence, not memory)
    validate.py        <- dependency-free validator + invariant tests (dossiers, organs, monsters)
    build_organs.py    <- ONLY writer of ORGANS.jsonl; harvests residue from validating dossiers (F5)
    ORGANS.jsonl       <- organ inventory: one row per certified residue item, typed + located
    ORGAN_NOTES.json   <- Keeper overlay: executed_by_necromancer per organ (read != executed, LAW N17)
    MONSTER_SCHEMA.json<- machine-readable monster (recomposition proposal) schema
    monsters/
        _TEMPLATE.monster.json   <- placeholder-marked exemplar (skipped by the validator)
        FRANK-000.monster.json   <- kind=chimera: failure-mined forge (PROPOSED, not dispatched)
        FRANK-001.monster.json   <- kind=repair: Argos with a bootstrapped selector history (PROPOSED)
    dossiers/
        _TEMPLATE.dossier.json   <- placeholder-marked exemplar (proves schema shape)
        acheron.dossier.json     <- a real existing autopsy mapped into the schema (no new claims)
        <agent>.dossier.json     <- Necromancer passes (coeus, argos, hephaestus so far) + <agent>_evidence/
    descendants/       <- Cleric implementations land here (empty until a dossier is accepted)
```

## Lifecycle

```
ROSTER (intake)
  -> QUEUE (Keeper seeds a Necromancer target, status=READY)
    -> Necromancer investigates -> dossiers/<agent>.dossier.json (identity..disposition)
      -> [optional] descendant_candidate proposed (LAW N6/N8/N9 enforced by validator)
        -> independent falsification pass (LAW N13)
          -> HITL sign-off (James)
            -> Cleric implements -> descendants/<id>/  + preregistered experiment
              -> consumption/effect recorded (CONSUMPTION.jsonl seam)
```

A dossier may terminate at `disposition.classification = TRUE_CORPSE` and that is a completed,
successful result (LAW N10). Not every corpse yields a descendant.

### The Frankenstein cycle (recomposition, not resurrection)

```
dossiers/*.residue --build_organs.py--> ORGANS.jsonl
  -> Doctor Frankenstein assembles organs across graves -> monsters/FRANK-NNN.monster.json (PROPOSED)
    -> Cleric gates (CLERIC_REVIEW -> GATED_APPROVED | GATED_REJECTED), James signs off
      -> Cleric implements + runs the lightning experiment (RUNNING)
        -> ALIVE (CONSUMPTION.jsonl row exists)  |  DEAD -> ROSTER row kind=chimera + Necromancer dossier
```

A living monster moves the *conditional viability frontier*; it never vindicates an ancestor (F2).
A dead monster is a corpse like any other (F6) and its organs carry the failure forward.

Monsters come in two kinds. A **chimera** recombines organs across graves. A **repair** (F7) is
Frankenstein saying "had they only done this instead": one ancestor, exactly one change, the record
checked first so a change the ancestor already tried is `GATED_REJECTED` on sight, and an ancestral
comparison that is *mandatory* because the ancestor without the change is the control. F2 still
holds: a living repair proves that one repaired configuration lives, not that the ancestor was right.

### Assume the author erred (LAW N17)

"No signal distinguishable from noise" is the *last* explanation any role may reach, not the first.
Every dossier carries an `author_error_audit` with four lenses (design vs hypothesis, code vs design,
execution parameters, hallucination scan), each `CLEAN` / `ERROR_FOUND` / `NOT_EXAMINED`; `CLEAN`
needs executed evidence, and the audit applies to prior verdicts and to our own dossiers as much as to
the corpse. Three author-error death axes exist (`bug-dead`, `parameter-dead`, `hallucination-dead`)
and `contributing_axes` lets a corpse be premise-dead *and* bug-dead, which is where all three
Necromancer passes so far landed. Organs record whether the Necromancer executed them or only read
them (13 of 39 executed); a monster harvesting an unexecuted organ must carry an `organ_execution_plan`.
The validator runs the Cleric's hallucination scan mechanically: every repo path cited by a dossier or
monster is resolved and the count printed (currently 80/80).

## Ground rules for anyone extending this tree

1. Historical records are **evidence, not doctrine** — some dispositions and autopsies have already
   been corrected by later evidence (LAW N11). Cite prior verdicts; do not trust them.
2. Reuse existing machinery (`engine/ledger/AGENT_AUTOPSIES.jsonl`, `AUTOPSY_TAXONOMY.md`,
   `engine/queues/CONSUMPTION.jsonl`) — do not build parallel infrastructure. See SEAMS.md.
3. Never touch H0-H5 (LAW N12).
4. Run `python engine/necropolis/validate.py` before committing. Green means the machine-readable
   files parse, every dossier satisfies the schema and the laws, the roster has no duplicate IDs,
   every queue target resolves to a roster entry, ORGANS.jsonl equals what the dossiers certify,
   and every monster resolves its organs, carries the F2 sentence verbatim, and has a kill condition.
5. Never hand-edit `ORGANS.jsonl`. Add residue to a dossier (Necromancer) or an annotation to
   `ORGAN_NOTES.json` (Keeper), then regenerate. The validator regenerates and fails if it was stale.

## Provenance

Founded by Mnemosyne (Keeper of the Necropolis), M2, on `necropolis/foundation` from baseline
`b91880a2dccf1630d6b1c47cff14a73f46e8ef4a`. This founding pass builds the substrate and nominates
exactly one first Necromancer target (see the handoff packet); it investigates no agent and
resurrects nothing.
