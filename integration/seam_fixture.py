#!/usr/bin/env python3
"""PROTEUS -> SFE SEAM REGRESSION FIXTURE

Freezes the ownership boundary between Proteus and SFE as an executable test.

    python integration/seam_fixture.py \
        --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt

Two assertions, and BOTH directions matter:

  F1  The historical Proteus payload -- proteus/foundry/export.py's
      sfe_artifact_payload(), which sends "name" and omits "kind" --
      MUST FAIL CLOSED with HTTP 422, naming both faults.

  F2  A Harmonia-shaped payload satisfying the live contract
      MUST SUCCEED with HTTP 200 and return a content-addressed artifact id.

F1 is not a bug report. It is a BOUNDARY. The historical payload is not the
seam, and it is deliberately NOT being repaired: Proteus owns organism identity
and its foundry tree stays bound to its V0.6 audit identity; SFE owns world
artifacts; the binding between them belongs to Harmonia's integration layer.

If F1 ever starts PASSING (i.e. the Engine begins accepting the historical
payload), that is a REGRESSION IN THE ENGINE, not progress -- it would mean the
artifact endpoint stopped failing closed on unknown fields. This fixture exists
to make that loud.

Exit 0 = boundary intact. Non-zero = the seam moved; read the output.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import ssl
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://192.168.1.202:8811/v2"

# Verbatim shape emitted by proteus/foundry/export.py::sfe_artifact_payload()
# as of commit a2898d19 / branch main. Reproduced here so the fixture does NOT
# import from proteus -- importing it would couple the seam we are separating.
HISTORICAL_PROTEUS_PAYLOAD_SHAPE = {
    "name": "proteus:<organism_id[:16]>",     # extra_forbidden
    "data_b64": "<canonical_json(manifest)>",
    "meta": {"info_kind": "artifact", "proteus": {"...": "..."}},
    # NOTE: no "kind" -> missing required field
}


def call(base, method, path, cacert, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    ctx = ssl.create_default_context(cafile=cacert)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--cacert", required=True)
    ap.add_argument("--token", default=None)
    a = ap.parse_args()

    print("=" * 78)
    print("PROTEUS -> SFE SEAM REGRESSION FIXTURE")
    print("=" * 78)

    token = a.token
    if not token:
        _s, c = call(a.base, "POST", "/clients", a.cacert,
                     body={"name": "seam-fixture"})
        token = c.get("token")
    if not token:
        print("FAIL: could not obtain a token")
        return 2
    _s, se = call(a.base, "POST", "/sessions", a.cacert, token,
                  {"name": "seam-fixture"})
    _s, w = call(a.base, "POST", "/worlds", a.cacert, token,
                 {"session_id": se["session_id"], "name": "SEAM-FIXTURE"})
    wid = w["world_id"]
    call(a.base, "POST", "/worlds/%s/start" % wid, a.cacert, token, {})
    print("fixture world: %s\n" % wid)

    manifest = {"schema_version": 1, "genes": [1, 2, 3]}
    blob = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    b64 = base64.b64encode(blob).decode()
    oid = hashlib.sha256(b"specimen").hexdigest()
    failures = []

    # ---- F1: the historical payload MUST fail closed --------------------
    historical = {
        "name": "proteus:%s" % oid[:16],
        "data_b64": b64,
        "meta": {"info_kind": "artifact",
                 "proteus": {"organism_id": oid, "lineage_id": "lin",
                             "generation": 0, "runtime_hash": "rh",
                             "manifest_schema": 1}},
    }
    st, resp = call(a.base, "POST", "/worlds/%s/artifacts" % wid, a.cacert,
                    token, historical)
    detail = resp.get("detail", []) if isinstance(resp, dict) else []
    locs = {".".join(str(p) for p in d.get("loc", [])): d.get("type")
            for d in detail} if isinstance(detail, list) else {}
    missing_kind = locs.get("body.kind") == "missing"
    extra_name = locs.get("body.name") == "extra_forbidden"

    print("F1  historical Proteus payload (name, no kind)")
    print("      expect: HTTP 422, missing body.kind, extra_forbidden body.name")
    print("      got   : HTTP %s, missing body.kind=%s, extra_forbidden "
          "body.name=%s" % (st, missing_kind, extra_name))
    if st == 422 and missing_kind and extra_name:
        print("      [PASS] boundary intact -- the Engine fails closed\n")
    else:
        failures.append("F1")
        print("      [FAIL] REGRESSION: the artifact endpoint no longer "
              "rejects the historical payload on both counts.")
        print("             If HTTP 200, the endpoint STOPPED FAILING CLOSED "
              "on unknown fields.\n")

    # ---- F2: a Harmonia-shaped payload MUST succeed ----------------------
    # Same bytes, same metadata. The ONLY differences are transport-shaped:
    # "name" dropped (it is Proteus-internal identity, not an SFE field) and
    # "kind" supplied (SFE's own required field). Organism identity is
    # preserved intact inside meta -- world association stays EXTRINSIC.
    harmonia = {
        "kind": "artifact",
        "data_b64": b64,
        "meta": {"info_kind": "artifact",
                 "proteus": {"organism_id": oid, "lineage_id": "lin",
                             "generation": 0, "runtime_hash": "rh",
                             "manifest_schema": 1}},
    }
    st2, resp2 = call(a.base, "POST", "/worlds/%s/artifacts" % wid, a.cacert,
                      token, harmonia)
    aid = resp2.get("artifact_id") if isinstance(resp2, dict) else None
    print("F2  Harmonia-shaped payload (kind, no name; same bytes, same meta)")
    print("      expect: HTTP 200 with an artifact_id")
    print("      got   : HTTP %s artifact_id=%s" % (st2, str(aid)[:34]))
    if st2 == 200 and aid:
        print("      [PASS] the seam Harmonia must implement is open\n")
    else:
        failures.append("F2")
        print("      [FAIL] the documented contract no longer works: %s\n"
              % json.dumps(resp2)[:300])

    # ---- F3: organism identity survived transport unchanged --------------
    if aid:
        st3, got = call(a.base, "GET",
                        "/worlds/%s/artifacts/%s/content" % (wid, aid),
                        a.cacert, token)
        rt = (base64.b64decode(got.get("content_b64", ""))
              if isinstance(got, dict) else b"")
        same_oid = (got.get("meta", {}).get("proteus", {}).get("organism_id")
                    == oid) if isinstance(got, dict) else False
        print("F3  organism identity is preserved, not rewritten by the world")
        print("      bytes round-trip exactly : %s" % (rt == blob))
        print("      organism_id unchanged    : %s" % same_oid)
        if rt == blob and same_oid:
            print("      [PASS] world association is EXTRINSIC -- the same "
                  "organism_id can enter many worlds\n")
        else:
            failures.append("F3")
            print("      [FAIL] transport altered the specimen\n")

    call(a.base, "POST", "/worlds/%s/terminate" % wid, a.cacert, token, {})

    print("=" * 78)
    if failures:
        print("SEAM FIXTURE FAILED: %s" % ", ".join(failures))
    else:
        print("SEAM FIXTURE INTACT: historical payload fails closed (422), "
              "Harmonia-shaped payload succeeds (200), identity preserved.")
    print("=" * 78)
    return len(failures)


if __name__ == "__main__":
    sys.exit(main())
