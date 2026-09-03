"""MINIMUM REPRODUCER -- GEN21_ORIGIN_LAUNDERING (for Daedalus).

Engine: SFE GEN-2.1, engine_source_hash
  sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc
Reproduced 2026-09-02 on a private pinned instance (serve.py --insecure
--registration open); same source hash as live 192.168.1.202:8811.

Claim violated (runtime.py import_artifact docstring): an imported artifact
"can NEVER be mistaken for something independently discovered in the
destination (I5, section 14, T10)".  H6 correctly denies C <- B(IMPORTED).
But B may re-create the imported bytes as a NATIVE artifact (create_artifact
never consults existing IMPORTED rows in the world, by blob_hash or
otherwise), and C then imports that NATIVE row legally.  C's provenance says
source_world=B, origin NATIVE in B.  A never appears.

Usage:  python GEN21_ORIGIN_LAUNDERING_repro.py [base_url]   (default private
        instance http://127.0.0.1:8899; needs open registration)
Expect: prints LAUNDERED=True for byte-identical and byte-different payloads.
"""
import json, sys
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
from sfclient.client import EngineClient, EngineError

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8899"
A, B, C = EngineClient(base), EngineClient(base), EngineClient(base)
for cli, n in ((A, "rA"), (B, "rB"), (C, "rC")):
    cli.register(n)
grp = A.create_topology_group("laundering-repro")
wA = A.create_world(A.create_session("s"), "A", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]
wB = B.create_world(B.create_session("s"), "B", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]
wC = C.create_world(C.create_session("s"), "C", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]

X = b'{"claim":"a_star","value":173}'
xA = A.artifact(wA, "claim", X, {"info_kind": "success"})            # 1. A creates X natively
imp = B.import_artifact(wB, wA, xA["artifact_id"])                    # 2. B legally imports X
assert B.artifact_bytes(wB, imp["artifact_id"]) == X                  # 3. B reads the bytes (F1)
try:                                                                  # control: H6 holds
    C.import_artifact(wC, wB, imp["artifact_id"]); print("H6 FAILED: direct re-export allowed")
except EngineError as e:
    print("H6 ok: direct re-export of IMPORTED copy denied", e.status)

for label, payload in (("byte_identical", X), ("byte_different_equiv", b'{"claim": "a_star", "value": 173}')):
    xB = B.artifact(wB, "claim", payload, {"info_kind": "success"})   # 4. B republishes as NATIVE
    got = C.import_artifact(wC, wB, xB["artifact_id"])                # 5. C imports through B
    prov = C.artifact_content(wC, got["artifact_id"])
    print(label, "LAUNDERED=", got["origin"] == "IMPORTED" and prov.get("source_world") == wB
          and wA not in json.dumps(prov),
          "| B row origin:", B.artifact_content(wB, xB["artifact_id"]).get("origin"),
          "| same blob as A:", xB["blob_hash"] == xA["blob_hash"])
