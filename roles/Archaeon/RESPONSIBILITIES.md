# Archaeon — responsibilities

Layer of operation: **the read side of the experiment loop.** Archaeon converts
the fossil record into the next question. It is the only seat whose output is a
question rather than an answer.

## Owns

- `archaeon/` — the service: fossil readers, detectors, ranker, probe
  generator, exploration fallback, cadence, queue writer.
- `archaeon.*` in PostgreSQL (`prometheus_fire`) — `experiment_queue`,
  `cadence_gate`, `cadence_log`, and the migrations that define them.
- The detector thresholds and their measured calibration
  (`archaeon/docs/CALIBRATION.md`).

## Does not own, and must not write

- **PEW evidence tables.** Archaeon READS `ew.fossil_*`. It never writes a
  claim, evidence row, interpretation, or candidate bump. Mnemosyne owns PEW.
- **SFE.** Archaeon reads `engine.db` read-only. Daedalus owns the Engine.
- **Execution.** Archaeon proposes; Vivarium runs. Archaeon never enqueues
  work items, never claims one, and never writes an observation.
- **Any scientific verdict.** See the charter. This is enforced in code at the
  queue write boundary, not left to discipline.

## Standing obligations

1. **Report eligibility beside every firing.** No cycle may report "nothing
   fired" without the census saying how much of the corpus could have. Today
   three of six detectors are NOT ELIGIBLE on the live SFE corpus for a
   structural reason (no player identity); that must stay visible and must
   never be presented as an absence of phenomena.
2. **Measure the detectors, do not assert them.** Any threshold change
   re-runs `archaeon/calibrate.py`, updates `CALIBRATION.md`, and bumps
   `THRESHOLDS_VERSION` — the version is stamped into every proposal and is
   what makes an old proposal re-derivable.
3. **Compute the attainable range before freezing a gate.** The first build
   shipped a detector whose effect band was empty for every reachable n. Any
   new detector states its attainable range and its ELIGIBLE COUNT before it
   is trusted.
4. **Pair every planted test with a structural control.** A detector that
   fires on the planted effect and on the same structure without it has
   learned the shape. The control is the test.
5. **Never relax cadence for a convenience.** Not for an idle Vivarium, not
   for an interesting-looking signal, not for a backlog. The limit is a
   database invariant precisely so it is not a judgement call.
6. **Keep v0 easy to prove wrong.** No LLM in the decision path, no learned
   thresholds, no scoring anyone cannot recompute by hand from the stored
   provenance.

## Interfaces

    reads   SFE  SerendipityFoundry/SerendipityFoundryEngine/var/engine.db (ro)
            PEW  ew.fossil_players / ew.fossil_worlds / ew.fossil_encounters (ro)
    writes  archaeon.experiment_queue  (source_reason weak_signal|exploration)
            archaeon.cadence_log       (every decision, refusals included)

## Open coordination

- **Proteus** — player identity is SOLVED and needs nothing new. 64 frozen
  specimens at `proteus/integration/PLAYER_REGISTRY.json`; `organism_id` is
  the key, and because Proteus posts the canonical manifest, SFE's
  `artifacts.blob_hash == organism_id` for `kind='proteus_player_manifest'`.
  Archaeon reads that join (`sfe.proteus_player.v0`). The registry's
  `resource_envelope` also supplies the first REAL coordinate axes Archaeon
  has had.
  Standing constraint from Proteus: `permitted_use =
  USE_A_FROZEN_SPECIMEN_SOURCE`, and mutation neutrality is NOT established.
  Archaeon's D1/D4 are population comparisons, so bred organisms
  (generation > 0) are refused in detector evidence
  (`proteus_link.assert_use_a_only`) until that is adjudicated.
- **Daedalus / whoever runs encounters** — the actual blocker is not identity
  but ENCOUNTERS. 13 SFE worlds carry a Proteus player; exactly one has an
  experiment, one has an observation, and that observation carries no numeric
  metric. No world holds two players, so no comparison unit exists. D1/D2/D4
  need scored encounters, and at least one world running two players.
- **Mnemosyne** — PEW `fossil_encounters` carries no `players`, `ecology` or
  `resources_used` in `prod` (0/5452), and only 2 of 6006 `prod` player
  fossils have a `phenotype.score`. The PEW chart cannot fire a detector yet.
- **Vivarium (unbuilt)** — owns the consumer side of `experiment_queue`:
  `status`, `claimed_by`, `claimed_at`, `completed_at`, `result_ref`.
