"""Phase 0 step 9: concurrency envelope (Amendment 4).

C1 QUALIFIED OPERATING ENVELOPE: L in {1,2,4,8,16}. L workers, each its own
client + world (enforceable experiments budget B, chosen so the cap BINDS for
some lineages), run an engine-backed LT lineage concurrently, plus: two
idempotent-duplicate posts (same key, same body, concurrent), one conflicting
reuse (same key, different body), a mid-run checkpoint + fork, and imports
into a per-level synthesis world.  After the level completes, the ledger is
audited from the DB:
  write exactness      events per world == recorder counts (+ fixed overhead)
  budget exactness     engine consumed == researcher spent; 409 iff attempted > B
  event ordering       world_index contiguous from 0; event_seq strictly increasing
  ledger validity      independent recompute of every entry_hash + prev links,
                       and the engine's own events.verify_world
  KnowledgeSet det.    F10 twice identical; F10 at fork cutoff == child frontier
  idempotency          duplicate -> 1 event, same response; conflict -> 409
  fork boundary        child inherits exactly the parent frontier at checkpoint
C2 DESTRUCTIVE: L in {32,64,128,256} until collapse (same audits; timeouts /
5xx / 'database is locked' counted).  Private pinned instance only.
usage: python step9_concurrency.py [C1|C2|both]
"""
import json, sys, time, threading, sqlite3, statistics as st
from concurrent.futures import ThreadPoolExecutor
from engine_lineage import *
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine")
from sfe import events as sfe_events
from sfe.ids import content_hash

DB = r"C:\Users\James\AppData\Local\Temp\claude\D--Prometheus\a91ed5fa-bfe9-491c-930e-7d168b730ca1\scratchpad\sfe_private\d16c_private.db"
pinned()
MODE = sys.argv[1] if len(sys.argv) > 1 else "C1"
ONLY = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
B = 8   # A costs 7-14 blind -> cap binds often


def worker(level, k, grp, lt_world, errors, lat):
    """One concurrent lineage. Returns a dict of what it did, for the audit."""
    rep = {"k": k, "ok": False}
    try:
        cli = KeepAliveClient(BASE); cli.timeout = 300
        t = time.perf_counter(); cli.register(f"C{level}-{k}"); lat.append(time.perf_counter() - t)
        s = cli.create_session("s9")
        wid = make_world(cli, s, f"w{level}-{k}", B, grp)
        rep["wid"] = wid
        # idempotency: two identical posts with the same key (concurrently), then a conflict
        key = f"idem-{level}-{k}"
        cli2 = KeepAliveClient(BASE, token=cli.token); cli2.timeout = 300
        with ThreadPoolExecutor(2) as ex:
            r1, r2 = list(ex.map(lambda c: c.hypothesis(wid, "idem-test", idem_key=key), (cli, cli2)))
        rep["idem_same_response"] = r1 == r2
        try:
            cli.hypothesis(wid, "DIFFERENT", idem_key=key); rep["idem_conflict_status"] = "accepted"
        except EngineError as e:
            rep["idem_conflict_status"] = e.status
        rec = EngineRecorder(cli, wid)
        r = Researcher(lt_world.public(), Settings(seed=k, order=("A",), heuristic="random"), oracle_of(lt_world), rec, budget=B + 6)
        # run half, checkpoint+fork, run rest
        for _ in range(3):
            t = time.perf_counter()
            try:
                if not r.step(): break
            finally:
                lat.append(time.perf_counter() - t)
        ck = cli.checkpoint(wid); rep["ck"] = ck
        child, = [c["world_id"] for c in cli.fork(wid, ck["checkpoint_id"], [{"name": f"child-{k}"}])]
        rep["child"] = child
        parent_frontier_at_ck = cli.knowledge_set(wid)
        try:
            r.run()
        except EngineError as e:
            if not rec.exhausted: raise
        arts = []
        for a in r.structured_artifacts() + [r.raw_artifact()]:
            arts.append(cli.artifact(wid, "lt", canon(a).encode(), {"info_kind": a["info_kind"]})["artifact_id"])
        rep.update({"spent": r.spent, "attempted": r.spent + (1 if rec.exhausted else 0), "exhausted": rec.exhausted,
                    "rec": dict(rec.n), "arts": arts, "done": r.done("A")})
        res = cli.resources(wid)
        rep["engine_consumed"] = (res.get("consumed") or res.get("budget", {}).get("consumed") or {}).get("experiments", 0)
        k1 = cli.knowledge_set(wid); k2 = cli.knowledge_set(wid)
        rep["f10_deterministic"] = json.dumps(k1, sort_keys=True) == json.dumps(k2, sort_keys=True)
        kc = cli.knowledge_set(child)
        rep["fork_boundary_ok"] = sorted(i["content_hash"] for i in kc["available"]) == sorted(i["content_hash"] for i in parent_frontier_at_ck["available"])
        rep["ok"] = True
    except Exception as e:
        errors.append({"k": k, "err": repr(e)[:300]}); rep["err"] = repr(e)[:300]
    return rep


def audit_world(db, wid, rep):
    ev = db.execute("SELECT * FROM events WHERE world_id=? ORDER BY world_index", (wid,)).fetchall()
    idx = [e["world_index"] for e in ev]; seqs = [e["event_seq"] for e in ev]
    out = {"n_events": len(ev), "index_contiguous": idx == list(range(len(ev))), "seq_increasing": seqs == sorted(seqs) and len(set(seqs)) == len(seqs)}
    # independent chain recompute
    prev = ""; ok = True
    wrow = db.execute("SELECT parent_world_id, fork_point FROM worlds WHERE world_id=?", (wid,)).fetchone()
    for e in ev:
        eh = content_hash({"world_id": wid, "world_index": e["world_index"], "event_type": e["event_type"], "ts": e["ts"],
                           "actor": e["actor"], "payload": json.loads(e["payload"]), "refs": json.loads(e["refs"]),
                           "causal": json.loads(e["causal"]), "artifacts": json.loads(e["artifacts"]),
                           "prev_hash": e["prev_hash"], "schema_ver": e["schema_ver"]})
        if eh != e["entry_hash"] or (e["world_index"] > 0 and e["prev_hash"] != prev): ok = False
        prev = e["entry_hash"]
    out["chain_recompute_ok"] = ok
    try:
        out["engine_verify_world"] = sfe_events.verify_world(db, wid)["ok"]
    except Exception as ex:
        out["engine_verify_world"] = repr(ex)[:120]
    types = [e["event_type"] for e in ev]
    from collections import Counter
    c = Counter(types)
    rc = rep.get("rec", {})
    exp_events = {"HYPOTHESIS_RECORDED": rc.get("hypothesis", 0) + 1,   # +1 idem hypothesis
                  "PREDICTION_RECORDED": rc.get("prediction", 0),
                  "OBSERVATION_RECORDED": rc.get("observation", 0),
                  "FAILURE_RECORDED": rc.get("failure", 0),
                  "ARTIFACT_CREATED": len(rep.get("arts", []))}
    got = {k: sum(v for t, v in c.items() if t.startswith(k.split("_")[0])) for k in exp_events}
    out["write_exact"] = all(got[k] == v for k, v in exp_events.items())
    out["write_detail"] = {"expected": exp_events, "got": got, "types": dict(c)}
    out["exp_committed"] = c.get("EXPERIMENT_COMMITTED", 0)
    out["budget_exact"] = (rep.get("engine_consumed") == rep.get("spent") == out["exp_committed"]
                          and rep.get("exhausted") == (rep.get("attempted", 0) > B) and rep.get("spent", 99) <= B)
    out["budget_exhausted_event"] = c.get("BUDGET_EXHAUSTED", 0)
    return out


def run_level(L, lt_world):
    grp_cli = new_client(f"grp-{L}"); grp = grp_cli.create_topology_group(f"s9-{L}")
    errors, lat = [], []
    t0 = time.perf_counter()
    with ThreadPoolExecutor(L) as ex:
        reps = list(ex.map(lambda k: worker(L, k, grp, lt_world, errors, lat), range(L)))
    wall = time.perf_counter() - t0
    db = sqlite3.connect(DB); db.row_factory = sqlite3.Row
    audits = [audit_world(db, r["wid"], r) for r in reps if r.get("wid")]
    # cross-world: global seq unique & increasing over all worlds of this level
    wids = [r["wid"] for r in reps if r.get("wid")]
    q = ",".join("?" * len(wids))
    seqs = [x[0] for x in db.execute(f"SELECT event_seq FROM events WHERE world_id IN ({q}) ORDER BY event_seq", wids)]
    n_events = len(seqs)
    # synthesis world imports everything from this level (H5 same group)
    syn = Synthesis(grp_cli, make_world(grp_cli, grp_cli.create_session("s9"), f"syn-{L}", 0, grp))
    for r in reps:
        if r.get("ok"): syn.import_from(r["wid"], [(a, "x") for a in r["arts"]])
    inv = {
        "workers_ok": sum(r.get("ok", False) for r in reps), "errors": errors[:10], "n_errors": len(errors),
        "write_exact": all(a["write_exact"] for a in audits), "budget_exact": all(a["budget_exact"] for a in audits),
        "index_contiguous": all(a["index_contiguous"] for a in audits), "seq_increasing": all(a["seq_increasing"] for a in audits),
        "global_seq_unique": len(set(seqs)) == len(seqs),
        "chain_recompute_ok": all(a["chain_recompute_ok"] for a in audits), "engine_verify_world": all(a["engine_verify_world"] is True for a in audits),
        "f10_deterministic": all(r.get("f10_deterministic") for r in reps if r.get("ok")),
        "idempotency_same_response": all(r.get("idem_same_response") for r in reps if r.get("ok")),
        "idempotency_conflict_409": all(r.get("idem_conflict_status") == 409 for r in reps if r.get("ok")),
        "fork_boundary": all(r.get("fork_boundary_ok") for r in reps if r.get("ok")),
        "imports_ok": len(syn.imported), "imports_denied": len(syn.denied),
        "exhausted_lineages": sum(1 for r in reps if r.get("exhausted")), "done_lineages": sum(1 for r in reps if r.get("done")),
    }
    inv["all_invariants"] = all(v is True for k, v in inv.items() if k in (
        "write_exact", "budget_exact", "index_contiguous", "seq_increasing", "global_seq_unique", "chain_recompute_ok",
        "engine_verify_world", "f10_deterministic", "idempotency_same_response", "idempotency_conflict_409", "fork_boundary")) and inv["imports_denied"] == 0
    perf = {"wall_s": round(wall, 2), "events": n_events, "events_per_s": round(n_events / wall, 1),
            "req_latency_ms": {"p50": round(1000 * st.median(lat), 1), "p95": round(1000 * sorted(lat)[int(0.95 * len(lat)) - 1], 1),
                               "max": round(1000 * max(lat), 1)} if lat else None}
    failed_audits = [{"wid": r["wid"], **{k: v for k, v in a.items() if v is False or k == "write_detail"}}
                     for r, a in zip([r for r in reps if r.get("wid")], audits) if not (a["write_exact"] and a["budget_exact"] and a["chain_recompute_ok"])]
    return {"level": L, "invariants": inv, "perf": perf, "failed_audits": failed_audits[:5],
            "verdict": "PASS" if inv["all_invariants"] and inv["n_errors"] == 0 else
                       ("ENGINE_CORRECTNESS_DEFECT" if not inv["all_invariants"] else "ENGINE_PERFORMANCE_LIMIT")}


lt_world = generate_world(2026)
levels = {"C1": [1, 2, 4, 8, 16], "C2": [32, 64, 128, 256, 512]}
todo = ONLY or (levels["C1"] + levels["C2"] if MODE == "both" else levels[MODE])
results = {"engine_hash": PIN, "mode": MODE, "B": B, "levels": []}
for L in todo:
    r = run_level(L, lt_world)
    results["levels"].append(r)
    print(json.dumps({"level": L, "verdict": r["verdict"], "perf": r["perf"],
                      "inv": {k: v for k, v in r["invariants"].items() if k != "errors"}}, default=str))
    json.dump(results, open(f"results/step9_concurrency_{MODE}{'_' + sys.argv[2] if ONLY else ''}.json", "w"), indent=1, default=str)
    if r["verdict"] != "PASS" and MODE == "C1":
        print("stopping envelope climb at first non-PASS level"); break
