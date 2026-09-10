"""Publish Archaeon's phase-2 packs into a producer world on the LIVE engine.

Archaeon holds no engine scope, so the bytes exist in their receipt and nowhere
else. This puts them where the consumer can legally import them, and returns
the address book that turns 72 unissued rows into 72 issuable ones.

WHY THE PRODUCTION IDENTITY AND NOT THE TEST ONE. The consumer runs as the
durable `vivarium` client. An artifact published under any other client would
be a CROSS-CLIENT import at execution time, which the engine refuses without a
registered bilateral topology group -- so publishing as `vivarium-test` would
produce 11 artifacts that look right and cannot be read. The world is created
`EXPLICIT_IMPORT_ONLY` for the same reason: an ISOLATED world emits nothing.

WHAT IS VERIFIED BEFORE ANYTHING IS SENT. Every pack's canonical bytes are
hashed here and compared with the slot digest Archaeon sealed. A mismatch
aborts the whole publish rather than uploading ten good artifacts and one that
will be refused at preflight. The engine is then TOLD the digest as well
(expected_blob_hash), so the identity is enforced on their side too, and the
returned blob_hash is checked a third time.

    python tools/publish_phase2_artifacts.py --receipt <path> --out <path>
    python tools/publish_phase2_artifacts.py ... --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REPO = HERE.parent
for extra in (str(HERE), str(REPO),
              str(REPO / "SerendipityFoundry" / "SerendipityFoundryClient")):
    if extra not in sys.path:
        sys.path.insert(0, extra)

from viv import db as _db                                     # noqa: E402
from viv import identity as _identity                         # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    packs = receipt["artifacts_to_publish"]

    # ---- verify BEFORE the network -------------------------------------
    prepared = []
    for digest, entry in sorted(packs.items()):
        raw = entry["canonical_json"].encode("utf-8")
        actual = "sha256:" + hashlib.sha256(raw).hexdigest()
        slot = entry["slot"]
        if actual != digest or slot["digest"] != digest:
            print("ABORT: %s hashes to %s (slot says %s). Nothing published."
                  % (digest, actual, slot["digest"]), file=sys.stderr)
            return 2
        if len(raw) != slot["expected_bytes"]:
            print("ABORT: %s is %d bytes, slot declares %d. Nothing published."
                  % (digest, len(raw), slot["expected_bytes"]), file=sys.stderr)
            return 2
        prepared.append((digest, entry, raw))
    print("verified %d/%d packs against their sealed digests and sizes"
          % (len(prepared), len(packs)))
    types = {}
    for _d, e, _r in prepared:
        types[e["artifact_type"]] = types.get(e["artifact_type"], 0) + 1
    print("  by type: %s" % types)
    if args.dry_run:
        print("dry run: nothing sent")
        return 0

    cfg = _db.load_config()
    role = cfg.get("identity_role", _identity.ROLE_PRODUCTION)
    if role != _identity.ROLE_PRODUCTION:
        print("ABORT: identity_role is %r. These artifacts must be owned by "
              "the client the CONSUMER runs as, or every import at execution "
              "time is a cross-client import the engine will refuse." % role,
              file=sys.stderr)
        return 2
    cacert = cfg.get("sfe_cacert")
    if cacert and not Path(cacert).is_absolute():
        cacert = str(REPO / cacert)

    from sfclient import EngineClient
    client = EngineClient(cfg["sfe_base_url"], _identity.token_for(role),
                          cafile=cacert, timeout=120.0)
    version = client.version()
    print("engine %s schema=%s %s"
          % (version.get("engine_instance_id"), version.get("schema_version"),
             cfg["sfe_base_url"]))

    sid = client.create_session("vivarium-phase2-publish")
    world = client.create_world(
        sid, "h1h0-phase2-packs-%s" % uuid.uuid4().hex[:8],
        seed_root=int(receipt.get("retrieval_seed") or 0) or None,
        sharing_policy="EXPLICIT_IMPORT_ONLY")
    wid = world["world_id"]
    client.start(wid)
    print("producer world %s (EXPLICIT_IMPORT_ONLY)" % wid)

    locators, published = {}, []
    for digest, entry, raw in prepared:
        out = client.artifact(wid, entry["artifact_type"], raw,
                              expected_blob_hash=digest)
        if out["blob_hash"] != digest:
            print("ABORT after %d: engine stored %s for %s"
                  % (len(published), out["blob_hash"], digest), file=sys.stderr)
            return 2
        locators[digest] = {"source_world": wid,
                            "source_artifact": out["artifact_id"]}
        published.append({"digest": digest, "artifact_id": out["artifact_id"],
                          "artifact_type": entry["artifact_type"],
                          "bytes": len(raw),
                          "target_task_id": entry.get("target_task_id"),
                          "policy": entry.get("policy"),
                          "instrument_control": entry.get("instrument_control")})
        print("  %-8s %s -> %s"
              % (entry["artifact_type"][:8], digest[:26] + "...",
                 out["artifact_id"][:26] + "..."))

    # ---- read every one back through the authorized path ----------------
    # Publishing is not the deliverable; being READABLE is. A locator file
    # whose addresses were never resolved is a promise, and the whole point of
    # the loader is that a promise about bytes is not evidence about them.
    verified = 0
    for digest, loc in sorted(locators.items()):
        got = client.artifact_content(loc["source_world"],
                                      loc["source_artifact"],
                                      expected_blob_hash=digest)
        import base64
        raw = base64.b64decode(got["content_b64"])
        assert "sha256:" + hashlib.sha256(raw).hexdigest() == digest
        verified += 1
    print("read back and re-hashed %d/%d through the authorized path"
          % (verified, len(locators)))

    out_doc = {
        "schema": "vivarium.phase2.locators.v1",
        "campaign": receipt.get("campaign"),
        "produced_at_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "producer_world": wid,
        "sharing_policy": "EXPLICIT_IMPORT_ONLY",
        "engine": {"base_url": cfg["sfe_base_url"],
                   "engine_instance_id": version.get("engine_instance_id"),
                   "schema_version": version.get("schema_version"),
                   "engine_source_hash": version.get("engine_source_hash"),
                   "source_commit": version.get("source_commit")},
        "published_by": {"role": role, "sfe_client": "vivarium"},
        "source_receipt": str(Path(args.receipt).as_posix()),
        "artifact_count": len(locators),
        "read_back_verified": verified,
        "locators": locators,
        "published": published,
        "note": "locators are ADDRESSING, not sealed input and not provenance: "
                "preflight verifies every resolved artifact against the digest "
                "inside spec_hash, so an address can decide WHETHER a row runs "
                "and never WHAT it computes.",
    }
    Path(args.out).write_text(json.dumps(out_doc, indent=2) + "\n",
                              encoding="utf-8")
    print("\nlocators: %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
