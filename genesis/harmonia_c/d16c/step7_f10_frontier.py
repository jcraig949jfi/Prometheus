"""Phase 0 step 7: F10 fork / frontier reconstruction (packet R6-R8; Q5).

R6 fork inheritance is exact at the CHECKPOINT (not fork-call time) and
   transitive to grandchildren.
R7 seq cutoff is fail-closed and monotone; F10 is deterministic across calls.
R8 native re-creation of inherited/imported content: does F10 keep the
   earlier availability (fork/import) or flip basis to native_creation?
Plus: import into a child, then fork the child -> grandchild inherits the
import with the right first_available_seq.
Everything asserted from F10 responses (API) + ledger seqs.
"""
import json, sys
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
from sfclient.client import EngineClient, EngineError
import urllib.request
BASE = "http://127.0.0.1:8899"
PIN = "sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc"
assert urllib.request.urlopen(BASE + "/v2/version").headers["x-sfe-engine-source-hash"] == PIN

c = EngineClient(BASE); c.register("F10"); s = c.create_session("s7")
c2 = EngineClient(BASE); c2.register("F10-src")
grp = c.create_topology_group("s7")
P = c.create_world(s, "P", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]
SRC = c2.create_world(c2.create_session("s7"), "SRC", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]


def ks(w, seq=None):
    r = c.knowledge_set(w, seq)
    return r, {(i["content_hash"], i["origin"], i["basis"]): i for i in r["available"]}


def hashes(r): return sorted(i["content_hash"] for i in r["available"])


def seq_of(w, aid):
    for e in c.events(w, limit=500):
        if (e.get("refs") or {}).get("artifact_id") == aid: return e["event_seq"]


R = {"engine_hash": PIN, "checks": {}}
def chk(name, ok, **info): R["checks"][name] = {"ok": bool(ok), **info}; print(("PASS " if ok else "FAIL ") + name, info if not ok else "")

a1 = c.artifact(P, "k", b"a1", {"info_kind": "success"}); a2 = c.artifact(P, "k", b"a2", {"info_kind": "success"})
ck1 = c.checkpoint(P)
a3 = c.artifact(P, "k", b"a3", {"info_kind": "success"})          # after ck1, before fork
K1, = [k["world_id"] for k in c.fork(P, ck1["checkpoint_id"], [{"name": "K1"}])]
ck2 = c.checkpoint(P)
K2, = [k["world_id"] for k in c.fork(P, ck2["checkpoint_id"], [{"name": "K2"}])]
h1, h2, h3 = a1["blob_hash"], a2["blob_hash"], a3["blob_hash"]

# R6 checkpoint boundary
r, m = ks(K1)
chk("R6_child_inherits_checkpoint_only", hashes(r) == sorted([h1, h2]), got=hashes(r), a3_leaked=h3 in hashes(r))
chk("R6_child_basis_fork_inheritance", all(i["basis"] == "fork_inheritance" and i["origin"] == "INHERITED" for i in r["available"]))
r2, _ = ks(K2)
chk("R6_second_child_sees_a3", hashes(r2) == sorted([h1, h2, h3]))
fork_seq_K1 = next(e["event_seq"] for e in c.events(K1, limit=50) if e["event_type"] == "WORLD_FORKED")
chk("R6_first_available_is_fork_seq", all(i["first_available_seq"] == fork_seq_K1 for i in r["available"]), fork_seq=fork_seq_K1)
# transitive grandchild
ckK1 = c.checkpoint(K1)
G, = [k["world_id"] for k in c.fork(K1, ckK1["checkpoint_id"], [{"name": "G"}])]
rg, _ = ks(G)
chk("R6_grandchild_transitive", hashes(rg) == sorted([h1, h2]), got=hashes(rg))

# R7 cutoff semantics
s1 = seq_of(P, a1["artifact_id"]); s2 = seq_of(P, a2["artifact_id"])
rp1, _ = ks(P, s1); rp2, _ = ks(P, s2)
chk("R7_parent_cutoff_exact", hashes(rp1) == [h1] and hashes(rp2) == sorted([h1, h2]))
rb, _ = ks(K1, fork_seq_K1 - 1); ra, _ = ks(K1, fork_seq_K1)
chk("R7_child_fail_closed_before_fork", hashes(rb) == [] and hashes(ra) == sorted([h1, h2]), before=hashes(rb), at=hashes(ra))
chk("R7_deterministic", json.dumps(ks(K1)[0], sort_keys=True) == json.dumps(ks(K1)[0], sort_keys=True))
mono = True; prev = set()
for q in range(1, fork_seq_K1 + 3):
    cur = set(hashes(ks(K1, q)[0]))
    if not prev <= cur: mono = False
    prev = cur
chk("R7_monotone_in_seq", mono)

# import into child, then fork child -> grandchild inherits import at correct seq
src = c2.artifact(SRC, "k", b"src", {"info_kind": "success"})
K1i = c.create_world(s, "K1i", sharing_policy="FULLY_SHARED", topology_group=grp)["world_id"]
imp = c.import_artifact(K1i, SRC, src["artifact_id"]); imp_seq = seq_of(K1i, imp["artifact_id"])
ckI = c.checkpoint(K1i); GI, = [k["world_id"] for k in c.fork(K1i, ckI["checkpoint_id"], [{"name": "GI"}])]
rgi, mgi = ks(GI)
it = [i for i in rgi["available"] if i["content_hash"] == src["blob_hash"]]
chk("IMPORT_then_fork_inherited", len(it) == 1 and it[0]["origin"] == "INHERITED" and it[0]["source_artifact"] == imp["artifact_id"], got=it)
ri1, _ = ks(K1i)
chk("IMPORT_first_available_is_import_seq", [i["first_available_seq"] for i in ri1["available"]] == [imp_seq])

# R8 basis flip: K1 re-creates a1 natively
before, _ = ks(K1)
b_entry = next(i for i in before["available"] if i["content_hash"] == h1)
a1n = c.artifact(K1, "k", b"a1", {"info_kind": "success"}); s_n = seq_of(K1, a1n["artifact_id"])
after, _ = ks(K1)
entries = [i for i in after["available"] if i["content_hash"] == h1]
chk("R8_inherited_entry_survives_native_recreation", any(i["basis"] == "fork_inheritance" for i in entries),
    before=b_entry, after=entries)
chk("R8_first_available_not_later_than_before", all(i["first_available_seq"] <= b_entry["first_available_seq"] for i in entries),
    before_seq=b_entry["first_available_seq"], after_seqs=[i["first_available_seq"] for i in entries])
at_fork, _ = ks(K1, fork_seq_K1)
chk("R8_cutoff_view_still_shows_inheritance", any(i["content_hash"] == h1 and i["basis"] == "fork_inheritance" for i in at_fork["available"]))
R["R8_note"] = ("F10(now) vs F10(seq=fork) disagree on the basis/first_available_seq of the same content when it is "
                "re-created natively after inheritance: the answer to 'when could K1 first know h1' depends on the cutoff asked.")
# same flip for IMPORTED then native (already shown in step 5 for B; record from F10 here)
a_imp_native = c.artifact(K1i, "k", b"src", {"info_kind": "success"})
ri2, _ = ks(K1i)
ent = [(i["origin"], i["basis"], i["first_available_seq"]) for i in ri2["available"] if i["content_hash"] == src["blob_hash"]]
chk("R8_import_and_native_both_listed", len(ent) == 2, entries=ent)
R["R8_import_native_entries"] = ent

R["summary"] = {"n": len(R["checks"]), "pass": sum(v["ok"] for v in R["checks"].values()),
                "fail": [k for k, v in R["checks"].items() if not v["ok"]]}
json.dump(R, open("results/step7_f10_frontier.json", "w"), indent=1, default=str)
print(json.dumps(R["summary"]))
