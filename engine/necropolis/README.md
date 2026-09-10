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
    CHARTER.md         <- the 15 laws + classification vocabulary
    SCHEMA.json        <- machine-readable dossier schema (JSON Schema 2020-12 superset of AGENT_AUTOPSIES.jsonl)
    ROLES.md           <- the Necromancer and Cleric role contracts
    SEAMS.md           <- how Necropolis objects interoperate with existing engine/ machinery
    ROSTER.jsonl       <- 48 canonical agents (intake only; no resurrection decisions)
    QUEUE.jsonl        <- seeded Necromancer investigations (READY, not dispatched)
    build_roster.py    <- reproducible ROSTER generator (derives from evidence, not memory)
    validate.py        <- dependency-free validator + invariant tests
    dossiers/
        _TEMPLATE.dossier.json   <- placeholder-marked exemplar (proves schema shape)
        acheron.dossier.json     <- a real existing autopsy mapped into the schema (no new claims)
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

## Ground rules for anyone extending this tree

1. Historical records are **evidence, not doctrine** — some dispositions and autopsies have already
   been corrected by later evidence (LAW N11). Cite prior verdicts; do not trust them.
2. Reuse existing machinery (`engine/ledger/AGENT_AUTOPSIES.jsonl`, `AUTOPSY_TAXONOMY.md`,
   `engine/queues/CONSUMPTION.jsonl`) — do not build parallel infrastructure. See SEAMS.md.
3. Never touch H0-H5 (LAW N12).
4. Run `python engine/necropolis/validate.py` before committing. Green means the machine-readable
   files parse, every dossier satisfies the schema and the laws, the roster has no duplicate IDs,
   and every queue target resolves to a roster entry.

## Provenance

Founded by Mnemosyne (Keeper of the Necropolis), M2, on `necropolis/foundation` from baseline
`b91880a2dccf1630d6b1c47cff14a73f46e8ef4a`. This founding pass builds the substrate and nominates
exactly one first Necromancer target (see the handoff packet); it investigates no agent and
resurrects nothing.
