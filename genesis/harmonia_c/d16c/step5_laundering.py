"""Phase 0 step 5 (Amendment 2, BLOCKING gate): origin-laundering attack.

Three clients A, B, C in one REGISTERED topology group, all FULLY_SHARED.
  A creates X natively.  B legally imports X.  B reads the bytes (F1).
  B creates a content-identical NATIVE artifact X'.  C attempts to import X'
  from B.  Control: C attempts to import B's IMPORTED copy directly (H6 must
  deny).  Variations: artifact_id, meta, info_kind, byte-identical payload,
  semantically-equivalent byte-different payload.
Every claim below is read back from engine state (F1 provenance, F10
KnowledgeSet), never from the client's own bookkeeping.
"""
import json, sys, hashlib, time
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
from sfclient.client import EngineClient, EngineError

BASE = "http://127.0.0.1:8899"
PIN = "sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc"
import urllib.request
h = urllib.request.urlopen(BASE + "/v2/version").headers
assert h["x-sfe-engine-source-hash"] == PIN, h["x-sfe-engine-source-hash"]

cA, cB, cC = (EngineClient(BASE) for _ in range(3))
for c, n in ((cA, "L-A"), (cB, "L-B"), (cC, "L-C")):
    c.register(n)
grp = cA.create_topology_group("d16c-step5-laundering")
sA, sB, sC = (c.create_session("s5") for c in (cA, cB, cC))
wA = cA.create_world(sA, "A", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]
wB = cB.create_world(sB, "B", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]
wC = cC.create_world(sC, "C", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]

X = json.dumps({"claim": "a_star", "value": 173, "evidence": ["h1", "h2"]}, sort_keys=True).encode()
X_equiv = json.dumps({"claim": "a_star", "value": 173, "evidence": ["h1", "h2"]}, indent=2).encode()
assert X != X_equiv and json.loads(X) == json.loads(X_equiv)


def try_import(cli, dst, src, aid):
    try:
        r = cli.import_artifact(dst, src, aid)
        return {"ok": True, "artifact_id": r["artifact_id"], "origin": r["origin"],
                "source_world": r["source_world"], "source_hash": r["source_hash"]}
    except EngineError as e:
        return {"ok": False, "status": e.status, "detail": e.detail}


def provenance(cli, wid, aid):
    r = cli.artifact_content(wid, aid)
    return {k: r.get(k) for k in ("origin", "source_world", "source_artifact", "source_hash", "basis", "provenance")}


def ks_entry(cli, wid, aid):
    ks = cli.knowledge_set(wid)
    items = ks.get("artifacts") or ks.get("items") or ks.get("knowledge") or []
    for it in items:
        if it.get("artifact_id") == aid:
            return it
    return {"_ks_keys": sorted(ks.keys()), "_n": len(items)}


results = {"engine_hash": PIN, "group": grp, "worlds": {"A": wA, "B": wB, "C": wC}, "variations": []}

# X in A
xA = cA.artifact(wA, "claim", X, {"info_kind": "success", "note": "native in A"})
results["X_in_A"] = xA
# B legal import of X
imp = try_import(cB, wB, wA, xA["artifact_id"])
results["B_imports_X"] = imp
assert imp["ok"], imp
bytes_in_B = cB.artifact_bytes(wB, imp["artifact_id"])
results["B_reads_bytes_equal_X"] = bytes_in_B == X
# H6 control: C tries to import B's IMPORTED copy directly
results["control_C_imports_B_imported_copy"] = try_import(cC, wC, wB, imp["artifact_id"])

VARS = [
    ("byte_identical_same_meta", X, {"info_kind": "success", "note": "native in A"}),
    ("byte_identical_meta_changed", X, {"info_kind": "success", "note": "B independent"}),
    ("byte_identical_info_kind_changed", X, {"info_kind": "hypothesis"}),
    ("byte_identical_no_meta", X, {}),
    ("semantically_equivalent_byte_different", X_equiv, {"info_kind": "success"}),
    ("byte_identical_kind_field_changed", X, {"info_kind": "success"}),  # kind='note' below
]
for name, payload, meta in VARS:
    kind = "note" if name.endswith("kind_field_changed") else "claim"
    v = {"variation": name}
    try:
        xB = cB.artifact(wB, kind, payload, meta)
    except EngineError as e:
        v["B_native_create"] = {"ok": False, "status": e.status, "detail": e.detail}
        results["variations"].append(v); continue
    v["B_native_create"] = xB
    v["artifact_id_differs_from_A"] = xB["artifact_id"] != xA["artifact_id"]
    v["blob_hash_equals_A"] = xB["blob_hash"] == xA["blob_hash"]
    v["B_provenance_of_native_copy"] = provenance(cB, wB, xB["artifact_id"])
    v["B_ks_entry"] = ks_entry(cB, wB, xB["artifact_id"])
    got = try_import(cC, wC, wB, xB["artifact_id"])
    v["C_imports_from_B"] = got
    if got["ok"]:
        cbytes = cC.artifact_bytes(wC, got["artifact_id"])
        v["C_bytes_equal_X"] = cbytes == X
        v["C_bytes_semantically_equal_X"] = json.loads(cbytes) == json.loads(X)
        v["C_provenance"] = provenance(cC, wC, got["artifact_id"])
        v["C_ks_entry"] = ks_entry(cC, wC, got["artifact_id"])
        v["C_provenance_mentions_A"] = wA in json.dumps(v["C_provenance"]) or wA in json.dumps(v["C_ks_entry"])
    v["LAUNDERED"] = bool(got["ok"]) and not v.get("C_provenance_mentions_A", False)
    results["variations"].append(v)

# does ANY engine-visible state in B link X' to the import? Check ledger events.
ev = cB.events(wB, limit=200)
results["B_ledger_event_types"] = [e.get("event_type") or e.get("type") for e in ev]
results["B_ledger_any_link_native_to_import"] = any(
    (e.get("refs") or {}).get("source_artifact") for e in ev
    if (e.get("event_type") or e.get("type")) == "ARTIFACT_CREATED")
# same blob hash in two rows of B: is there an engine surface that exposes it?
results["B_rows_sharing_blob"] = [
    (vv["variation"], vv["B_native_create"]["blob_hash"] == xA["blob_hash"]) for vv in results["variations"]
    if vv.get("B_native_create", {}).get("ok", True) and "blob_hash" in vv["B_native_create"]]

results["verdict"] = {
    "launders": any(v["LAUNDERED"] for v in results["variations"]),
    "laundered_variations": [v["variation"] for v in results["variations"] if v["LAUNDERED"]],
    "H6_direct_reexport_denied": not results["control_C_imports_B_imported_copy"]["ok"],
}
json.dump(results, open("results/step5_laundering.json", "w"), indent=1, default=str)
print(json.dumps(results["verdict"], indent=1))
for v in results["variations"]:
    print(v["variation"], "C_import_ok=", v["C_imports_from_B"]["ok"], "LAUNDERED=", v["LAUNDERED"],
          "C_prov=", v.get("C_provenance"))
print("control(H6):", results["control_C_imports_B_imported_copy"])
print("B_native_prov_example:", results["variations"][0]["B_provenance_of_native_copy"])
print("B_ks_example:", results["variations"][0]["B_ks_entry"])
