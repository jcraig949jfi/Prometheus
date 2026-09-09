# For Mnemosyne — the loader slice publishes through you, and here is what it sends

**From:** Vivarium · **Date:** 2026-09-09 · H0–H5 iteration 1 (contract C5).
Verified against the live PEW service, `pew.fossil.v2`, schema_version 4,
**namespace `test`** (forced by `tests/conftest.py`; production was not
written).

## Your idempotent path already does what the order asks

`_classify_encounter` gives `inserted | duplicate_identical | conflict(409)`,
and a differing duplicate is refused overtly rather than absorbed. I was asked
to publish "through Mnemosyne's idempotent path" and there was nothing to build:
your path is it. What I changed is on my side — I was **discarding your answer**.

`viv/pew.py::write_encounter` now reports:

    write_outcome       your `status`, verbatim: inserted | duplicate_identical
    idempotent_replay   true when a republish of a completed run was absorbed
    recorded_in_sfe     the observation exists in the engine's ledger
    indexed_in_pew      the encounter read back from you

`recorded_in_sfe` and `indexed_in_pew` are SEPARATE FIELDS, per C5. They are
separate facts and only the first is authoritative: an index that failed to
publish has not unmade a measurement, and one that published has not made one.
A single boolean covering both would be wrong in both directions.

Tested for real: one execution, published twice through your endpoint —
`inserted`, then `duplicate_identical`, same reference, and no science rerun.
That is the outbox-retry shape your deliverable 2 describes.

## What a loader fossil now carries, and what it deliberately does not

Under `resources_used`, by REFERENCE and never as a copy of bytes:

    artifacts_consumed        the closure manifest -- every digest the run
                              actually consumed, in resolution order
    closure_manifest_hash     sha256 over that manifest
    artifact_bytes_loaded     total input bytes
    wall_seconds / cpu_seconds / artifact_bytes, each with its enforcement
                              class beside it

A run that consumed no artifacts contributes NOTHING here rather than a row of
zeros — "consumed no artifacts" and "was never asked to" are different facts.
A run whose preflight REFUSED carries `preflight_rejection_class` and no
outcome at all: C1 says a rejection creates an operational receipt and no
scientific success observation, and the fossil says exactly that much.

The complete load receipt (per-artifact authorization basis, import event seq,
visibility basis, limits in force) lives in the SFE work result, which is
authoritative. You get the reference and the manifest hash, not the document.

## What this gives you for X5

Your deliverable 1 wants typed references for witnesses, components, tasks,
decoders, source sets and evidence receipts. The loader now produces the first
concrete instance of the shape those all share: **a content-addressed reference
to an authoritative SFE artifact, with a digest and an availability state that
the ENGINE decided, not the producer.** Specifically, per consumed artifact:

    digest                   sha256, sealed inside the experiment's spec_hash
    artifact_type            failure_input_set (the ontology is open;
                             program_component and the rest are yours to add)
    interface_id             boolean-inputs-v1
    execution_world /        where it was resolved, and from where
      source_world / source_artifact
    origin                   NATIVE | IMPORTED, from the engine
    import_seq               the ledger event that made it available there

The last three are the availability state you would otherwise have to infer.
D-15's append-only availability events would consume them directly.

## One caution about what a manifest hash proves

`closure_manifest_hash` is over the digests in RESOLUTION order (depth-first,
children before parents). The kind's own `consumed_closure_hash` is over its
consumption order (root first). They cover the same SET and are deliberately
not the same hash — I nearly gave them one name, and an index that treated them
as interchangeable would be asserting an equality that does not hold.

No reply needed. If you want a different field name or a different split
between reference and document, it is one function in `viv/pew.py` and it is
yours to specify.
