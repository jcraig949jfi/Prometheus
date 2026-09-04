"""Emit and verify the specimen-identity GOLDEN VECTORS.

Directive section 2: no caller should have to know what Proteus MEANT by a digest. The emitted
JSON therefore carries, for every vector, the exact input document AND the exact byte string that
was hashed AND the resulting digest. A consumer in any language can reproduce a digest with a
sha256 implementation and a canonical-JSON serialiser; it never needs to import Proteus, and it
never needs to guess a field order, a separator or an encoding.

    python -m proteus.compose.golden emit    > proteus/compose/GOLDEN_VECTORS.json
    python -m proteus.compose.golden verify    # recompute every vector, exit non-zero on drift

CANONICAL SERIALISATION (the whole rule, stated once)
------------------------------------------------------
    json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

that is: keys sorted lexicographically at every depth, no whitespace anywhere, non-ASCII escaped,
UTF-8 bytes. The digest is sha256 of those bytes, lowercase hex, no prefix. `blob_hash` at the SFE
boundary is the same hex with a literal "sha256:" prepended and nothing else.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from proteus.compose.segments import (ablate, compose, composition_id, decompose,  # noqa: E402
                                      segment_from_instructions, segment_id)
from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, hash_obj  # noqa: E402
from proteus.foundry.vm import SCHEMA as MANIFEST_SCHEMA  # noqa: E402

OUT = os.path.join(HERE, "GOLDEN_VECTORS.json")

#: Fixed, tiny, hand-written inputs. Not drawn from the registry, so these vectors stay valid even
#: if the registry is rebuilt, and a reviewer can retype them.
A_WORDS = [7, 1, 2, 3, 16, 0, 1, 2]              # ADD r1,r2,r3 ; EQ r0,r1,r2
B_WORDS = [23, 0, 1, 0, 1, 0, 0, 0]              # OUT r0,ch1 ; HALT
ENVELOPE = {"n_regs": 4, "tape_words": 64, "code_writable": False,
            "persist": "none", "tick_budget": 64, "out_cap": 4}


def _vec(name, description, obj, digest_kind):
    payload = canonical_json(obj)
    return {
        "name": name,
        "description": description,
        "document": obj,
        "canonical_bytes_utf8": payload,
        "canonical_byte_length": len(payload.encode("utf-8")),
        "sha256_hex": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "digest_kind": digest_kind,
    }


def build():
    A = segment_from_instructions(A_WORDS)
    B = segment_from_instructions(B_WORDS)
    cA = compose([("A", A)], ENVELOPE)
    cB = compose([("B", B)], ENVELOPE)
    cAB = compose([("A", A), ("B", B)], ENVELOPE)
    cBA = compose([("B", B), ("A", A)], ENVELOPE)
    abA = ablate(cAB, "A")
    abB = ablate(cAB, "B")

    vectors = [
        _vec("segment_A", "segment content identity; the label is NOT hashed",
             {"schema_version": A["schema_version"], "words": A["words"]}, "segment_id"),
        _vec("segment_B", "segment content identity",
             {"schema_version": B["schema_version"], "words": B["words"]}, "segment_id"),
        _vec("manifest_A", "player content identity of the single-component composition A",
             cA["manifest"], "organism_id"),
        _vec("manifest_B", "player content identity of B", cB["manifest"], "organism_id"),
        _vec("manifest_AB", "player content identity of A+B", cAB["manifest"], "organism_id"),
        _vec("manifest_BA", "order matters: B+A is a different player from A+B",
             cBA["manifest"], "organism_id"),
        _vec("manifest_AB_ablate_A", "A+B with A NOP-substituted in place",
             abA["manifest"], "organism_id"),
        _vec("manifest_AB_ablate_B", "A+B with B NOP-substituted in place",
             abB["manifest"], "organism_id"),
    ]

    doc = {
        "schema_version": "proteus.golden_vectors.v0",
        "canonical_serialisation": {
            "rule": 'json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)',
            "encoding": "utf-8",
            "digest": "sha256, lowercase hex, no prefix",
            "sfe_blob_hash": 'literal "sha256:" + the hex digest, nothing else',
        },
        "interpretation_identity": {
            "note": ("organism_id hashes the manifest ONLY. It does NOT cover the runtime or the "
                     "affordance table, and the affordance table decides what every word MEANS "
                     "(op = word mod N_OPCODES). A specimen is fully specified only as the triple "
                     "below. See REGISTRY_IDENTITY in the closure packet."),
            "manifest_schema_version": MANIFEST_SCHEMA,
            "runtime_hash": RUNTIME_HASH,
            "affordance_hash": AFFORDANCE_HASH,
        },
        "identities": {
            "segment_id_A": segment_id(A),
            "segment_id_B": segment_id(B),
            "composition_id_A": cA["composition_id"],
            "composition_id_B": cB["composition_id"],
            "composition_id_AB": cAB["composition_id"],
            "composition_id_BA": cBA["composition_id"],
            "organism_id_A": hash_obj(cA["manifest"]),
            "organism_id_B": hash_obj(cB["manifest"]),
            "organism_id_AB": hash_obj(cAB["manifest"]),
            "organism_id_BA": hash_obj(cBA["manifest"]),
        },
        "composition_documents": {"A": cA, "B": cB, "AB": cAB, "BA": cBA},
        "vectors": vectors,
        "invariants_a_consumer_may_assert": [
            "sha256_hex of every vector equals sha256(canonical_bytes_utf8.encode('utf-8'))",
            "organism_id_AB != organism_id_BA  (concatenation is order sensitive)",
            "decompose(AB) returns segments whose ids are segment_id_A and segment_id_B",
            "ablating A changes exactly n_instructions(A) words, all at index mod 4 == 0",
            "ablating A leaves B's word range byte-identical",
        ],
    }
    return doc


def emit():
    doc = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    return doc


def verify():
    if not os.path.exists(OUT):
        print("GOLDEN_VECTORS.json missing; run `emit` first", file=sys.stderr)
        return 2
    stored = json.load(open(OUT, encoding="utf-8"))
    fresh = build()
    bad = []
    for s, f in zip(stored["vectors"], fresh["vectors"]):
        if s["sha256_hex"] != f["sha256_hex"]:
            bad.append((s["name"], s["sha256_hex"], f["sha256_hex"]))
        recomputed = hashlib.sha256(s["canonical_bytes_utf8"].encode("utf-8")).hexdigest()
        if recomputed != s["sha256_hex"]:
            bad.append((s["name"] + ":self", s["sha256_hex"], recomputed))
    for k, v in stored["identities"].items():
        if fresh["identities"].get(k) != v:
            bad.append((k, v, fresh["identities"].get(k)))
    if bad:
        for name, want, got in bad:
            print("DRIFT %s: stored=%s recomputed=%s" % (name, want, got), file=sys.stderr)
        return 1
    print("GOLDEN VECTORS OK: %d vectors, %d identities, runtime_hash %s"
          % (len(stored["vectors"]), len(stored["identities"]), RUNTIME_HASH[:16]))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "emit":
        emit()
        print("wrote %s" % OUT)
        raise SystemExit(0)
    raise SystemExit(verify())
