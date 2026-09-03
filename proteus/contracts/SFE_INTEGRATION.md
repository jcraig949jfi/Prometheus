# SFE integration contract (V0). Amendment A9; brief §12 ("SFE remains authoritative for what happened").

**Status:** a contract and a payload shaper (`foundry/export.py`), not a client. Proteus holds no
SFE token, opens no connection, and the quarantine audit forbids any network import in
`proteus/`. Everything below is what the neutral operator / SFE-side binding layer does with
Proteus's identities. Read against `SerendipityFoundry/SerendipityFoundryClient/docs/API.md`
(the only SFE document Proteus has read; see `roles/Proteus/READ_LEDGER.md`).

## 1. Division of authority

| object | minted by | authoritative record |
|---|---|---|
| organism (manifest, `organism_id`) | Proteus | Proteus population rows; stored in SFE as a NATIVE artifact |
| descent record (`record_id`) | Proteus | Proteus lineage rows; may be stored as an artifact |
| checkpoint (`checkpoint_id`) | Proteus runtime, at the operator's request | artifact in the world that produced it |
| encounter identity | Proteus `encounter_identity()` from operator-supplied inputs | the SFE **committed experiment** it is attached to |
| what happened in an encounter (transcripts, meter vectors, outcomes) | **SFE** (engine work result) | SFE event ledger, `ENGINE_WORK_RESULT` |
| phenotype / failure emission | **SFE** | SFE `failures` and `observations` |
| interpretation | PEW (Mnemosyne) | PEW; never flows back |

Proteus never records an outcome. If a Proteus-side file ever says an organism "won", "lost",
"scored" or "survived", that is a defect.

## 2. Storing a population

For each organism the operator calls `POST /v2/worlds/{wid}/artifacts` with
`export.sfe_artifact_payload(organism)`: the canonical manifest bytes (content-addressed on both
sides; SFE's `blob_hash` must equal sha256 of the same bytes, which is a free cross-check),
`meta.info_kind = "artifact"`, and `meta.proteus = {organism_id, lineage_id, generation,
runtime_hash, manifest_schema}`. `info_kind` stays within SFE's closed ontology; Proteus adds no
kind. Cross-world sharing of organisms, if ever wanted, goes through SFE's import with provenance
(`origin: IMPORTED`) — Proteus does not copy organisms between worlds itself.

## 3. Running an encounter

1. The operator registers a **world binding**: which channels carry what, in which order, with
   what budgets — as an SFE artifact in the world, hashed; its id is `world_binding_id`. This is
   the binding layer's object. Proteus never sees its contents.
2. The operator computes `encounter_id = export.encounter_identity(organism_ids,
   world_binding_id, seed, checkpoint_ids)`.
3. The operator registers and **commits** an SFE experiment whose `spec` carries
   `{encounter_id, organism_ids, world_binding_id, seed, checkpoint_ids, runtime_hash,
   proteus_population_ref}` and enqueues it as work (`enqueue=True`). Any prediction the
   operator wants counted as prospective is registered BEFORE this commit — SFE enforces it.
4. A worker runs the player(s) through `run_tick` per the binding, and completes the work item
   with the transcripts, statuses, meter vectors and any checkpoints taken. That completion is
   the authoritative record (`ENGINE_WORK_RESULT`).
5. Observations and failures are posted against the committed experiment with `work_id`.
   Failure records use SFE's own required fields (`failure_type`, `falsifier`, `violated`); the
   Incubator's failure-coordinate schema is a world-side choice.

Nothing in steps 1–5 is executed by Proteus. Step 4's worker imports `proteus.foundry` as a
library; the library has no idea it is inside SFE.

## 4. Biography across encounters (brief §6)

A lineage's life is a chain of checkpoints. INHERIT-policy descent names a parent
`checkpoint_id`; the operator restores it (`lineage.restore`, which refuses a foreign runtime)
and the child's first tick continues from the parent's state. Because checkpoints are SFE
artifacts in the world that produced them, the chain from any state back to a genome and a
sequence of encounters is walkable through SFE's lineage endpoint plus Proteus's descent
records, and none of it can be rewritten.

## 5. Immutable experience (brief §7)

If a later analysis finds the world was broken, the encounter's record stands; the operator posts
a new observation or failure with `replication` or a new experiment, and PEW carries the
reinterpretation. Proteus provides no API to amend a record and will not add one.

## 6. Open items for Daedalus (A9: coordinate, do not define)

Filed here rather than in Daedalus's tree, per his boundary. Proteus needs to know, before a
first population enters SFE:

- **Payload size.** A generation of 10⁴–10⁶ organisms as individual artifacts is many POSTs;
  is a population blob (one artifact, JSONL, content-addressed) acceptable with per-organism
  ids inside, or should each organism be its own artifact so SFE's lineage graph can point at
  it?
- **Meter vector as observation payload.** Confirm the `observations` body accepts a nested
  dict of the size `Meter.as_dict` produces per player per tick, or whether it should be an
  artifact referenced by id.
- **Encounter id placement.** Is `spec.encounter_id` the right anchor, or does SFE want a
  first-class field so `lineage?kind=` can walk it?
- **Checkpoint artifacts.** `info_kind` for a checkpoint: `artifact` (Proteus's assumption) or
  something the sharing policies should treat differently.

Until answered, the payload shapes in `export.py` are Proteus's best reading of `API.md` and are
marked provisional.
