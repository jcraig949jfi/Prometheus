# Theseus → Ergon Handoff Contract

**Producer**: Theseus engine (`theseus/handoff/ergon_handoff.py`)
**Consumer**: Ergon continuous-ingest agent (filed Fire #29; not yet built when this contract drafted)
**Established**: 2026-05-18 Fire #29
**Format**: substrate_block `training_anchor` v1.0.0 per `techne/contracts/substrate_block_schemas/training_anchor_v1.json`

---

## Directory layout

```
theseus/handoff/ergon_outbox/
  inbox/                # producer writes new bundles here
    theseus_training_anchors_<UTC>.md          # markdown blocks
    theseus_training_anchors_<UTC>.jsonl       # pre-parsed records
    theseus_training_anchors_<UTC>.complete    # zero-byte sentinel
  consumed/             # consumer moves bundles here after successful ingest
  rejected/             # consumer moves bundles here on validation failure
```

The three partitions are pre-created by the producer on every emission.
Consumers move bundles (all three files) atomically between partitions.

## File naming

Pattern: `theseus_training_anchors_<UTC>.{md|jsonl|complete}`

where `<UTC>` is a compact ISO timestamp `YYYYMMDDTHHMMSSZ`.

The three files in a bundle share the same prefix; the consumer should
treat them as an atomic unit.

## Atomic write protocol

For each emission, the producer writes in this order:

1. Write data to `theseus_training_anchors_<UTC>.md.tmp`
2. Write data to `theseus_training_anchors_<UTC>.jsonl.tmp`
3. `os.replace()` (atomic) `.md.tmp` → `.md`
4. `os.replace()` (atomic) `.jsonl.tmp` → `.jsonl`
5. Write zero-byte `theseus_training_anchors_<UTC>.complete`

`Path.replace()` is atomic on both POSIX and Windows. The `.complete`
sentinel is written LAST so its existence guarantees both data files
are intact.

If the producer crashes mid-write, `.tmp` files may be left behind.
Consumers should:
- Ignore any file ending in `.tmp`
- Only read `.md` / `.jsonl` when the matching `.complete` exists

## Consumer responsibilities

For each bundle in `inbox/` with `.complete` present:

1. Read either `.md` (parse via `aporia/scripts/parse_substrate_blocks.py`)
   OR `.jsonl` (pre-parsed; skip the parse step).
2. Validate against the `training_anchor` schema (via
   `aporia/scripts/validate_substrate_blocks.py` or equivalent).
3. Ingest validated anchors into the Learner corpus.
4. On success: move the 3 files (`.md`, `.jsonl`, `.complete`) to
   `consumed/`.
5. On validation failure: move the 3 files to `rejected/` and emit a
   `log_work` event with the failure reason.
6. Optionally: emit a `log_work` per successful ingest with the
   bundle's record count.

Bundles in `consumed/` and `rejected/` are retained for audit but
should not be re-ingested.

## Idempotency

Every anchor carries a stable `id` field:

```
id: anchor-<domain>-<NNNNN>
```

where the NNNNN suffix is the sequential index within the emitting
bundle. The `id` is NOT globally unique across bundles — it's
bundle-local. For global dedup, the consumer should use the inner
`underlying_record_hash` (sha256 of the canonical anchor blob, per
`training_anchor_ingestion_spec.md` §1.3).

The pre-parsed JSONL records additionally carry:
- `source_record_id`: the originating Theseus record's content hash
- `source_generator_id`: which Theseus generator emitted it
- `source_training_weight`: training_weight at the time of emission

These let the consumer trace any anchor back to its substrate provenance.

## Schema version

Current: `training_anchor` schema v1.0.0.

When Theseus bumps to v1.1.0 (adding the `bs_coverage` field per
Ergon's ticket-back-2 from Fire #27), the bundle's `_schema_version`
field will reflect the change. Consumers should validate against
the version declared in the bundle, not assume a fixed version.

## Cadence

**Current (Fire #29)**: one-shot emission via `python -m theseus.handoff.ergon_handoff`.
Producer emits on operator demand only.

**Planned**: continuous emission daemon (option A / B / C from the
Fire #29 discussion — awaiting operator decision). When that ships,
the producer will write a bundle every N minutes / batches without
human invocation.

Consumers should be designed for either cadence: the contract is the
same.

## Failure modes the consumer should handle

1. **Producer crashes mid-write**: `.tmp` files in `inbox/`; treat as
   never-existed. Run periodic cleanup of orphan `.tmp` files older
   than some threshold (e.g., 1 hour).

2. **Disk full**: producer's `Path.replace()` raises. Consumer should
   not retry on the same bundle name without producer's involvement.

3. **Schema drift**: bundle declares unexpected `_schema_version`.
   Move to `rejected/` and surface for operator review.

4. **Empty inbox**: normal idle state. Consumer should poll on a
   bounded interval (e.g., every 30s) and not busy-wait.

5. **Bundle's `.complete` exists but data files missing**: corrupt
   state. Move whatever exists to `rejected/` and surface.

---

*Producer-side contract drafted Fire #29 — to be amended once Ergon's
continuous consumer is built and surfaces any consumer-side needs.*
