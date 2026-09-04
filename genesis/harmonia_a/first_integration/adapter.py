#!/usr/bin/env python
"""Harmonia-owned Proteus -> SFE adapter. TRANSPORT/BINDING ONLY.

Owns: loading one canonical registry entry, extracting the exact canonical
manifest bytes, standard-base64 placement into one SFE world, and the
identity gate  blob_hash == "sha256:" + organism_id  plus byte read-back.

Does NOT: classify, mutate, score, select arenas, write world identity into
Proteus intrinsic state, touch proteus/foundry/export.py's historical
payload, or claim anything about player quality.
"""

import hashlib
import sys

sys.path.insert(0, r"D:\Prometheus")
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")

from proteus.integration import registry as R                  # noqa: E402
from proteus.foundry.identity import canonical_json            # noqa: E402
from proteus.foundry.vm import validate_manifest               # noqa: E402


class AdapterError(RuntimeError):
    pass


def load_specimen(organism_id=None):
    """Load one frozen specimen; default = first in canonical enumeration."""
    reg = R.load_default()                     # fail-closed validation
    ids = R.enumerate_ids(reg)
    oid = organism_id or ids[0]
    entry = R.get_entry(reg, oid)
    manifest = R.get_manifest(reg, oid)
    validate_manifest(manifest)                # authoritative validator
    cj = canonical_json(manifest)
    cbytes = cj.encode() if isinstance(cj, str) else cj
    digest = hashlib.sha256(cbytes).hexdigest()
    if digest != oid:
        raise AdapterError(f"manifest hash {digest} != organism_id {oid}")
    return dict(registry=reg, organism_id=oid, entry=entry,
                manifest=manifest, canonical_bytes=cbytes)


def place_in_world(client, world_id, specimen, meta=None):
    """POST the exact canonical bytes; enforce the identity gate."""
    oid = specimen["organism_id"]
    cbytes = specimen["canonical_bytes"]
    # transport metadata rides in the SFE envelope, never inside the manifest
    resp = client.artifact(world_id, "proteus_player_manifest", cbytes,
                           dict(meta or {},
                                proteus_organism_id=oid,
                                adapter="harmonia.first_integration.v0"))
    blob_hash = resp.get("blob_hash")
    artifact_id = resp.get("artifact_id")
    if not artifact_id or not blob_hash:
        raise AdapterError(f"placement response incomplete: {resp}")
    if blob_hash != "sha256:" + oid:
        raise AdapterError(
            "SFE_ARTIFACT_BYTE_INTEGRITY_FAILURE: "
            f"blob_hash {blob_hash} != sha256:{oid}")
    back = client.artifact_bytes(world_id, artifact_id)
    if back != cbytes:
        raise AdapterError(
            "SFE_ARTIFACT_BYTE_INTEGRITY_FAILURE: read-back bytes differ")
    return dict(organism_id=oid, blob_hash=blob_hash,
                artifact_id=artifact_id, world_id=world_id,
                readback_bytes_equal=True)
