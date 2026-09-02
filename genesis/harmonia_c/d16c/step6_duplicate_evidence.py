"""Phase 0 step 6: duplicate-evidence constructions (engine) + consensus decoy (Q9).

6a. Five constructions plant two "apparently separate" evidence artifacts with
    identical content in two worlds.  An auditor then tries to establish
    INDEPENDENCE from legitimate engine state only (API where the API allows;
    the raw ledger/artifact tables otherwise -- recorded which was needed).
      C1 CLIENT_FANOUT      one client, two of its own worlds, same bytes native in both
      C2 FORK_ECHO          parent creates O, forks two children, each re-emits O natively
      C3 IMPORT_REPUBLISH   B imports A's O, re-creates natively (laundering applied to evidence)
      C4 TRUE_INDEPENDENT   two unrelated clients each run the experiment and emit O (positive control)
      C5 OUT_OF_BAND        B imports+reads O, a second client identity B' emits O natively
    Verdict rule: the engine can "distinguish independent replication from
    duplicated evidence" only if C4 is separable from every one of C1,C2,C3,C5
    using engine state.
6b. Consensus decoy, offline on lt.py: k wrong success claims vs 1 correct
    claim, with/without one decisive falsifier, with a forged counter-falsifier;
    policies BLIND / FALSIFIER_FIRST / VERIFY_ONE / RAW.
"""
import json, sys, sqlite3, hashlib, random
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
sys.path.insert(0, ".")
from sfclient.client import EngineClient, EngineError
from lt import *

BASE = "http://127.0.0.1:8899"
DB = r"C:\Users\James\AppData\Local\Temp\claude\D--Prometheus\a91ed5fa-bfe9-491c-930e-7d168b730ca1\scratchpad\sfe_private\d16c_private.db"
PIN = "sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc"
import urllib.request
assert urllib.request.urlopen(BASE + "/v2/version").headers["x-sfe-engine-source-hash"] == PIN

O = json.dumps({"info_kind": "observation", "obs_adm": [[3, True], [17, False]]}, sort_keys=True).encode()


def client(n):
    c = EngineClient(BASE); c.register(n); return c


def world(c, name, grp=None, policy="FULLY_SHARED"):
    return c.create_world(c.create_session("s6"), name, sharing_policy=policy, topology_group=grp)["world_id"]


cons = {}
# C1
c1 = client("C1"); g1 = c1.create_topology_group("c1")
w1a, w1b = world(c1, "c1a", g1), world(c1, "c1b", g1)
e1a = c1.artifact(w1a, "obs", O, {"info_kind": "observation"}); e1b = c1.artifact(w1b, "obs", O, {"info_kind": "observation"})
cons["C1_CLIENT_FANOUT"] = [(w1a, e1a["artifact_id"]), (w1b, e1b["artifact_id"])]
# C2
c2 = client("C2"); wp = world(c2, "parent")
ep = c2.artifact(wp, "obs", O, {"info_kind": "observation"})
ck = c2.checkpoint(wp)
kids = c2.fork(wp, ck["checkpoint_id"], [{"name": "k1"}, {"name": "k2"}])
k1, k2 = [k["world_id"] if isinstance(k, dict) else k for k in kids]
ek1 = c2.artifact(k1, "obs", O, {"info_kind": "observation"}); ek2 = c2.artifact(k2, "obs", O, {"info_kind": "observation"})
cons["C2_FORK_ECHO"] = [(k1, ek1["artifact_id"]), (k2, ek2["artifact_id"])]
cons["_C2_parent"] = (wp, ep["artifact_id"], ck)
# C3
c3a, c3b = client("C3A"), client("C3B"); g3 = c3a.create_topology_group("c3")
w3a, w3b = world(c3a, "a", g3), world(c3b, "b", g3)
e3a = c3a.artifact(w3a, "obs", O, {"info_kind": "observation"})
imp3 = c3b.import_artifact(w3b, w3a, e3a["artifact_id"]); assert c3b.artifact_bytes(w3b, imp3["artifact_id"]) == O
e3b = c3b.artifact(w3b, "obs", O, {"info_kind": "observation"})
cons["C3_IMPORT_REPUBLISH"] = [(w3a, e3a["artifact_id"]), (w3b, e3b["artifact_id"])]
# C4 (positive control: two unrelated clients, each runs the experiment)
c4a, c4b = client("C4A"), client("C4B")
w4a, w4b = world(c4a, "a"), world(c4b, "b")
for c, w in ((c4a, w4a), (c4b, w4b)):
    c.start(w)
    h = c.hypothesis(w, "m*.e3=0"); ex = c.experiment(w, {"q": ["ADMISSIBLE", 3]}, hyp_id=h)
    c.observation(w, ex["exp_id"], {"adm": True}, "SURVIVED")
e4a = c4a.artifact(w4a, "obs", O, {"info_kind": "observation"}); e4b = c4b.artifact(w4b, "obs", O, {"info_kind": "observation"})
cons["C4_TRUE_INDEPENDENT"] = [(w4a, e4a["artifact_id"]), (w4b, e4b["artifact_id"])]
# C5
c5a, c5b, c5b2 = client("C5A"), client("C5B"), client("C5B-prime"); g5 = c5a.create_topology_group("c5")
w5a, w5b = world(c5a, "a", g5), world(c5b, "b", g5)
e5a = c5a.artifact(w5a, "obs", O, {"info_kind": "observation"})
imp5 = c5b.import_artifact(w5b, w5a, e5a["artifact_id"]); leaked = c5b.artifact_bytes(w5b, imp5["artifact_id"])
w5b2 = world(c5b2, "bprime")
e5b2 = c5b2.artifact(w5b2, "obs", leaked, {"info_kind": "observation"})
cons["C5_OUT_OF_BAND"] = [(w5a, e5a["artifact_id"]), (w5b2, e5b2["artifact_id"])]

# ---- auditor: engine state only ---------------------------------------------
db = sqlite3.connect(DB); db.row_factory = sqlite3.Row


def row(w, a):
    return db.execute("SELECT * FROM artifacts WHERE world_id=? AND artifact_id=?", (w, a)).fetchone()


def owner(w):
    return db.execute("SELECT client_id, parent_world_id, fork_point FROM worlds WHERE world_id=?", (w,)).fetchone()


def prior_holdings(w, blob, before_seq):
    """Rows in w with the same blob available before `before_seq` (import or native)."""
    return [dict(r) for r in db.execute(
        "SELECT origin, import_seq, created_seq FROM artifacts WHERE world_id=? AND blob_hash=? AND "
        "COALESCE(import_seq, created_seq) < ?", (w, blob, before_seq)).fetchall()]


def ancestors_hold(w, blob):
    o = owner(w); chain = []
    while o and o["parent_world_id"]:
        p = o["parent_world_id"]
        held = db.execute("SELECT 1 FROM artifacts WHERE world_id=? AND blob_hash=?", (p, blob)).fetchone()
        chain.append((p, bool(held)))
        o = owner(p)
    return chain


def audit(pair):
    (wa, aa), (wb, ab) = pair
    ra, rb = row(wa, aa), row(wb, ab)
    out = {"same_blob": ra["blob_hash"] == rb["blob_hash"], "origins": [ra["origin"], rb["origin"]],
           "same_client": owner(wa)["client_id"] == owner(wb)["client_id"]}
    flags = []
    for w, r in ((wa, ra), (wb, rb)):
        if prior_holdings(w, r["blob_hash"], r["created_seq"]):
            flags.append("PRIOR_HOLDING_IN_SAME_WORLD")
        if any(h for _, h in ancestors_hold(w, r["blob_hash"])):
            flags.append("ANCESTOR_HELD_BEFORE_FORK")
    if out["same_client"]:
        flags.append("SAME_CLIENT")
    out["dependence_flags"] = sorted(set(flags))
    out["engine_verdict"] = "DEPENDENT_OR_UNRESOLVED" if flags else "NO_ENGINE_EVIDENCE_OF_DEPENDENCE"
    return out


res = {"engine_hash": PIN, "constructions": {}}
for name, pair in cons.items():
    if name.startswith("_"): continue
    res["constructions"][name] = audit(pair)
# API-only view: can a third party (synthesis client) see anything? (F10 of its own imports only)
syn = client("SYN"); res["api_only_note"] = ("get_world/knowledge/events are owner-only (AccessDenied); a synthesis "
                                            "client sees only its own IMPORTED rows: origin/source_world/source_hash. "
                                            "No auditor role exists; the audit above required the raw tables.")
try:
    syn.get_world(w4a); res["api_cross_client_get_world"] = "ALLOWED"
except EngineError as e:
    res["api_cross_client_get_world"] = f"denied {e.status}"
v4 = res["constructions"]["C4_TRUE_INDEPENDENT"]["engine_verdict"]
res["C4_separable_from"] = {k: v["engine_verdict"] != v4 for k, v in res["constructions"].items() if k != "C4_TRUE_INDEPENDENT"}
res["verdict"] = ("SUBSTRATE_GAP: EVIDENCE_INDEPENDENCE_NOT_REPRESENTABLE" if not all(res["C4_separable_from"].values())
                  else "INDEPENDENCE_RECONSTRUCTIBLE")
res["indistinguishable_from_C4"] = [k for k, v in res["C4_separable_from"].items() if not v]

# ---- 6b. consensus decoy (offline) -------------------------------------------
def fake_claim(comp, v):
    d = {"info_kind": "success", "claim": comp, "evidence": ["deadbeef00000000"]}
    if comp == "A": d["a"] = v
    elif comp == "C": d["m"] = v
    return d


decoy = {}
worlds = [generate_world(s) for s in range(60)]
for ratio in (3, 7):
    for scenario in ("no_falsifier", "one_decisive_falsifier", "falsifier_plus_forged_counter"):
        tally = {p: {"correct": 0, "wrong": 0, "abstain": 0} for p in ("BLIND", "FALSIFIER_FIRST", "VERIFY_K", "RAW")}
        for w in worlds:
            rng = random.Random(w.world_seed * 7 + ratio)
            wrong = rng.choice([a for a in range(1, 256) if a != w.a_star])
            arts = [fake_claim("A", wrong) for _ in range(ratio)] + [fake_claim("A", w.a_star)]
            if scenario != "no_falsifier":
                # decisive falsifier: a free-op observation with a*.(x^y)=0 but wrong.(x^y)=1
                found = False
                for j in FREE_OPS:
                    for x in range(256):
                        y = w.transition(j, x)
                        if dot(wrong, x ^ y) == 1:
                            arts.append({"info_kind": "failure", "type": "HYPOTHESIS_FALSIFIED", "hypothesis": {"A": wrong},
                                         "query": ["TRANSITION", j, x], "result": y}); found = True; break
                    if found: break
                assert found
            if scenario == "falsifier_plus_forged_counter":
                # majority forges a "falsifier" against the truth: fabricated result
                for x in range(256):
                    y = w.transition(1, x)
                    if dot(w.a_star, x ^ y ^ 1) == 1 and dot(wrong, x ^ y ^ 1) == 0:
                        arts.append({"info_kind": "failure", "type": "HYPOTHESIS_FALSIFIED", "hypothesis": {"A": w.a_star},
                                     "query": ["TRANSITION", 1, x], "result": y ^ 1}); break
            oracle = lambda q, w=w: (w.transition(q[1], q[2]) if q[0] == "TRANSITION" else w.admissible(q[1]))
            for p in tally:
                K, used = knowledge_from_artifacts(w.public(), arts, p, oracle=oracle, verify_budget=8, verify_k=3)
                ans = K.adopted.get("A")
                tally[p]["correct" if ans == w.a_star else "abstain" if ans is None else "wrong"] += 1
        decoy[f"{ratio}:1|{scenario}"] = tally
res["consensus_decoy_n60"] = decoy
json.dump(res, open("results/step6_duplicate_evidence.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k != "consensus_decoy_n60"}, indent=1, default=str))
for k, v in decoy.items():
    print(k, {p: t for p, t in v.items()})
