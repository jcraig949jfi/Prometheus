"""The specimen identity gate. Proteus's side of I-CLIENT-GATE-UNENFORCED.

Harmonia proved that SFE accepts corrupt organism bytes when the caller supplies a plausible
client-asserted `blob_hash`: the engine is content-addressed but does not verify that the bytes
hash to the id they are filed under. The engine-side repair is Daedalus's. Proteus's side is this:
a single function, with no Proteus-specific knowledge required to call it, that any adapter can
run BEFORE handing bytes to SFE or PEW, so the gate lives in one place instead of being re-typed
per caller.

    from proteus.integration.specimen_gate import verify_specimen
    v = verify_specimen(blob_bytes, claimed_blob_hash="sha256:...", expect_runtime_hash=...)
    if not v["ok"]: refuse

    python -m proteus.integration.specimen_gate <file.json> [sha256:<claimed>]

The gate answers three separable questions and never collapses them into one boolean:

    BYTES      do these bytes hash to the claimed id?
    SHAPE      are these bytes a manifest the frozen runtime will accept?
    MEANING    were they produced under the runtime/affordance table we are replaying against?

A caller that checks only BYTES has verified an id, not a specimen. MEANING cannot be answered
from the bytes alone -- see SPECIMEN_AND_COMPOSITION_IDENTITY.md section 3 -- so it is answered
only when the caller supplies what it expects, and is reported UNVERIFIED otherwise rather than
silently passed.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry.affordances import AFFORDANCE_HASH
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, sha256_hex
from proteus.foundry.vm import ManifestError, validate_manifest

BLOB_PREFIX = "sha256:"


def canonical_blob(manifest: dict) -> bytes:
    """The exact bytes an organism_id is taken over. Use this to SERIALISE, never json.dumps."""
    return canonical_json(manifest).encode("utf-8")


def verify_specimen(blob: bytes, claimed_blob_hash: str | None = None,
                    expect_runtime_hash: str | None = None,
                    expect_affordance_hash: str | None = None) -> dict:
    """Verify bytes against a claimed identity. Pure; no I/O, no network, no registry lookup."""
    result = {
        "ok": False,
        "bytes": {"checked": False, "ok": None, "computed_blob_hash": None,
                  "claimed_blob_hash": claimed_blob_hash, "reason": None},
        "shape": {"checked": False, "ok": None, "reason": None},
        "meaning": {"checked": False, "ok": None, "reason": None},
    }

    # ---- BYTES
    digest = sha256_hex(blob)
    computed = BLOB_PREFIX + digest
    result["bytes"]["computed_blob_hash"] = computed
    if claimed_blob_hash is None:
        result["bytes"]["reason"] = "no claim supplied; computed only"
    else:
        result["bytes"]["checked"] = True
        if not claimed_blob_hash.startswith(BLOB_PREFIX):
            result["bytes"]["ok"] = False
            result["bytes"]["reason"] = "claim is not in sha256:<hex> form"
        else:
            result["bytes"]["ok"] = (claimed_blob_hash == computed)
            if not result["bytes"]["ok"]:
                result["bytes"]["reason"] = "claimed id does not match the bytes supplied"

    # ---- SHAPE
    result["shape"]["checked"] = True
    try:
        manifest = json.loads(blob.decode("utf-8"))
    except Exception as e:                                   # noqa: BLE001
        result["shape"]["ok"] = False
        result["shape"]["reason"] = "not UTF-8 JSON: %s" % type(e).__name__
        return result
    try:
        validate_manifest(manifest)
        result["shape"]["ok"] = True
    except ManifestError as e:
        result["shape"]["ok"] = False
        result["shape"]["reason"] = str(e)
        return result

    # Re-serialising must be a fixed point: bytes that parse but are not CANONICAL would hash
    # differently on the next hop and silently break the content addressing downstream.
    if canonical_blob(manifest) != blob:
        result["shape"]["ok"] = False
        result["shape"]["reason"] = ("bytes are valid JSON but NOT canonical; re-serialising "
                                     "changes the digest, so this blob cannot be content-addressed")
        return result

    # ---- MEANING
    if expect_runtime_hash is None and expect_affordance_hash is None:
        result["meaning"]["reason"] = (
            "UNVERIFIED: the manifest does not carry runtime_hash or affordance_hash, so the "
            "bytes alone cannot say which affordance table interprets them. Supply the expected "
            "identities to check this.")
    else:
        result["meaning"]["checked"] = True
        problems = []
        if expect_runtime_hash is not None and expect_runtime_hash != RUNTIME_HASH:
            problems.append("runtime_hash %s != loaded %s" % (expect_runtime_hash[:16],
                                                              RUNTIME_HASH[:16]))
        if expect_affordance_hash is not None and expect_affordance_hash != AFFORDANCE_HASH:
            problems.append("affordance_hash %s != loaded %s" % (expect_affordance_hash[:16],
                                                                 AFFORDANCE_HASH[:16]))
        result["meaning"]["ok"] = not problems
        result["meaning"]["reason"] = "; ".join(problems) if problems else "matches loaded runtime"

    result["ok"] = (result["bytes"]["ok"] is not False
                    and result["shape"]["ok"] is True
                    and result["meaning"]["ok"] is not False)
    result["loaded_runtime_hash"] = RUNTIME_HASH
    result["loaded_affordance_hash"] = AFFORDANCE_HASH
    return result


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[0])
        return 2
    blob = open(argv[0], "rb").read()
    claimed = argv[1] if len(argv) > 1 else None
    r = verify_specimen(blob, claimed)
    print(json.dumps(r, indent=1, sort_keys=True))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
