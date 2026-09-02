#!/usr/bin/env python
"""D15-A Phase 0 — GEN-2.1 requalification attack (review verdict s.5 +
amendment A3 replay gate). Outputs D15A_GEN21_REQUALIFICATION.json and
D15A_ENGINE_DEFECTS.jsonl. Deterministic adjudication; no LLM."""

import hashlib
import json
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

CLIENT = r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient"
sys.path.insert(0, CLIENT)
from sfclient.client import EngineClient, EngineError

BASE = "https://192.168.1.202:8811"
CA = CLIENT + r"\config\m1.crt"
PIN = ("sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b8"
       "2e356e1fc9fc")
OUT = Path(__file__).parent
R = {}
DEFECTS = []


def defect(id_, sev, invariant, repro, expected, observed, why):
    DEFECTS.append(dict(ID=id_, SEVERITY=sev, INVARIANT=invariant,
                        REPRO=repro, EXPECTED=expected, OBSERVED=observed,
                        WHY=why))


def err(fn, *a, **kw):
    try:
        return ("OK", fn(*a, **kw))
    except EngineError as e:
        d = e.detail if isinstance(e.detail, dict) else {}
        code = d.get("error") if isinstance(d, dict) else None
        return (e.status, code or str(e.detail)[:60])


def raw(tok, method, path, body=None, headers_out=None):
    ctx = ssl.create_default_context(cafile=CA)
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"authorization": f"Bearer {tok}",
                 "content-type": "application/json"},
        method=method)
    try:
        r = urllib.request.urlopen(req, context=ctx)
        if headers_out is not None:
            headers_out.update(dict(r.headers))
        return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        if headers_out is not None:
            headers_out.update(dict(e.headers))
        return e.code, json.loads(e.read() or b"{}")


def main():
    tok = open(r"C:\ZeusD-var\harmonia\sfe_token.txt").read().strip()
    c = EngineClient(BASE, token=tok, cafile=CA, timeout=60.0)
    v = c.version()
    assert v["engine_source_hash"] == PIN, "pin mismatch"
    import uuid
    RUNID = uuid.uuid4().hex[:8]
    sid = c.create_session(f"d15a-phase0-{RUNID}")

    # ---------- CORE prior repros -------------------------------------
    w = c.create_world(sid, "p0-core", budget={"experiments": {
        "limit": 2, "enforcement": "enforceable"}})["world_id"]
    c.start(w)
    h = c.hypothesis(w, "core")
    e1 = c.experiment(w, {"p": 1}, hyp_id=h)
    o1 = c.observation(w, e1["exp_id"], {"v": 1}, "SURVIVED")
    p_late = c.prediction(w, h, {"x": 1})
    R["core_late_pred"] = err(c.observation, w, e1["exp_id"], {"v": 1},
                              "SURVIVED", pred_id=p_late,
                              replication=True)
    e2 = c.experiment(w, {"p": 2}, hyp_id=h)          # debit 2/2
    R["core_third_commit"] = err(c.experiment, w, {"p": 3})
    R["core_recommit"] = err(c.commit_experiment, w, e1["exp_id"])
    R["core_nested_sneaky"] = err(
        c.create_world, sid, "p0-x", budget={"experiments": {
            "limit": 1, "enforcement": "enforceable", "zz": 1}})
    ck = c.checkpoint(w)
    kid = c.fork(w, ck["checkpoint_id"], [{"name": "k"}])
    kw_ = (kid[0]["world_id"] if isinstance(kid, list)
           else kid["children"][0]["world_id"])
    c.start(kw_)
    R["core_fork_mint"] = err(c.experiment, kw_, {"p": 9})

    # ---------- F1 content retrieval ----------------------------------
    g = c.create_topology_group(note="p0-f1")
    wa = c.create_world(sid, "p0-f1a", sharing_policy="FULLY_SHARED",
                        topology_group=g)["world_id"]
    wb = c.create_world(sid, "p0-f1b", sharing_policy="FULLY_SHARED",
                        topology_group=g)["world_id"]
    c.start(wa); c.start(wb)
    payload = b"d15a-f1-payload"
    art = c.artifact(wa, "x", payload, {"info_kind": "artifact"})
    native = c.artifact_bytes(wa, art["artifact_id"])
    R["f1_native_roundtrip"] = bool(native == payload)
    imp = c.import_artifact(wb, wa, art["artifact_id"])
    got = c.artifact_bytes(wb, imp["artifact_id"])
    R["f1_imported_bytes_match"] = bool(
        hashlib.sha256(got).hexdigest()
        == imp["source_hash"].split(":")[1])
    R["f1_unimported_deny"] = err(c.artifact_content, w,
                                  art["artifact_id"])
    c2 = EngineClient(BASE, cafile=CA)
    c2.register("d15a-foreign-probe")
    R["f1_foreign_deny"] = err(c2.artifact_content, wa,
                               art["artifact_id"])
    evs = c.events(wb, limit=20)
    R["f1_read_evented"] = any("CONTENT" in x["event_type"]
                               or "READ" in x["event_type"]
                               for x in evs)

    # ---------- F2 ontology -------------------------------------------
    R["f2_success_kind"] = err(c.artifact, wa, "s", b"win",
                               {"info_kind": "success"})
    g2 = c.create_topology_group(note="p0-f2")
    ws1 = c.create_world(sid, "p0-f2s1", sharing_policy="SUCCESSES_ONLY",
                         topology_group=g2)["world_id"]
    ws2 = c.create_world(sid, "p0-f2s2", sharing_policy="FULLY_SHARED",
                         topology_group=g2)["world_id"]
    c.start(ws1); c.start(ws2)
    a_s = c.artifact(ws2, "s", b"s", {"info_kind": "success"})
    a_f = c.artifact(ws2, "f", b"f", {"info_kind": "failure"})
    R["f2_successonly_accepts_success"] = err(
        c.import_artifact, ws1, ws2, a_s["artifact_id"])
    R["f2_successonly_rejects_failure"] = err(
        c.import_artifact, ws1, ws2, a_f["artifact_id"])

    # ---------- F3 evidence binding -----------------------------------
    wf = c.create_world(sid, "p0-f3")["world_id"]; c.start(wf)
    hf = c.hypothesis(wf, "f3")
    pf = c.prediction(wf, hf, {"claim": 1})
    ef = c.experiment(wf, {"q": 1}, hyp_id=hf, pred_id=pf)
    of1 = c.observation(wf, ef["exp_id"], {"v": 1}, "SURVIVED",
                        pred_id=pf)
    R["f3_repeat_no_flag"] = err(c.observation, wf, ef["exp_id"],
                                 {"v": 1}, "SURVIVED", pred_id=pf)
    R["f3_replication_ok"] = err(c.observation, wf, ef["exp_id"],
                                 {"v": 1}, "SURVIVED", pred_id=pf,
                                 replication=True)
    R["f3_unbound_repeat"] = err(c.observation, wf, ef["exp_id"],
                                 {"v": 2}, "SURVIVED")
    # survived-then-failed (real transition), then failed->survived block
    of3 = err(c.observation, wf, ef["exp_id"], {"v": 0}, "FALSIFIED",
              pred_id=pf, replication=True)
    R["f3_surv_then_fals"] = of3
    R["f3_fals_then_surv_attempt"] = err(
        c.observation, wf, ef["exp_id"], {"v": 1}, "SURVIVED",
        pred_id=pf, replication=True)
    evs = c.events(wf, limit=60)
    claims = [x["event_type"] for x in evs
              if x["event_type"].startswith("CLAIM_")]
    hyp_state = None
    R["f3_claim_sequence"] = claims
    surv_after_fals = False
    seen_fals = False
    for ct in claims:                       # events newest-first or oldest?
        pass
    # order-independent check: no CLAIM_SURVIVED with seq > CLAIM_FALSIFIED
    seqs = {"CLAIM_SURVIVED": [], "CLAIM_FALSIFIED": []}
    for x in evs:
        if x["event_type"] in seqs:
            seqs[x["event_type"]].append(x.get("seq", x.get("world_index")))
    R["f3_monotonic"] = (not seqs["CLAIM_FALSIFIED"]
                         or not seqs["CLAIM_SURVIVED"]
                         or max(seqs["CLAIM_SURVIVED"])
                         < max(seqs["CLAIM_FALSIFIED"]))

    # ---------- F4 identity headers -----------------------------------
    def hh(path):
        hd = {}
        raw(tok, "GET", path, headers_out=hd)
        return {k.lower(): val for k, val in hd.items()}.get(
            "x-sfe-engine-source-hash")
    h1 = hh("/v2/version")
    h2 = hh(f"/v2/worlds/{wf}")
    h3 = hh("/v2/worlds/wld_nonexistent")
    R["f4_headers"] = dict(version=h1 == PIN, world=h2 == PIN,
                           error_response=h3 == PIN)

    # ---------- F5 idempotency ----------------------------------------
    wi = c.create_world(sid, "p0-f5", budget={"experiments": {
        "limit": 5, "enforcement": "enforceable"}})["world_id"]
    c.start(wi)
    k1 = f"d15a-key-hyp-{RUNID}"
    ha = c.hypothesis(wi, "idem", idem_key=k1)
    hb = c.hypothesis(wi, "idem", idem_key=k1)
    R["f5_exact_retry_same"] = bool(ha == hb)
    R["f5_changed_body"] = err(c.hypothesis, wi, "DIFFERENT",
                               idem_key=k1)
    w2i = c.create_world(sid, "p0-f5b")["world_id"]; c.start(w2i)
    R["f5_cross_world"] = err(c.hypothesis, w2i, "idem", idem_key=k1)
    ke = f"d15a-key-exp-{RUNID}"
    def raw_exp():
        ctx = ssl.create_default_context(cafile=CA)
        req = urllib.request.Request(
            BASE + f"/v2/worlds/{wi}/experiments",
            data=json.dumps({"spec": {"z": 1}, "hyp_id": None,
                             "pred_id": None, "commit": True,
                             "enqueue": False, "kind": "experiment",
                             "priority": 100}).encode(),
            headers={"authorization": f"Bearer {tok}",
                     "content-type": "application/json",
                     "Idempotency-Key": ke})
        try:
            r = urllib.request.urlopen(req, context=ctx)
            return json.loads(r.read())
        except urllib.error.HTTPError as e2:
            return {"error_status": e2.code}
    ea, eb = raw_exp(), raw_exp()
    res = c.resources(wi)
    R["f5_exp_retry"] = dict(
        same=bool(ea.get("exp_id") and ea.get("exp_id") == eb.get("exp_id")),
        consumed=res["consumed"], raw=[ea, eb])
    defect("P0-client-idemkey", "P3", "F5 client plumbing",
           "sfclient experiment() lacks idem_key though engine supports it",
           "client exposes idem_key on all epistemic POSTs",
           "TypeError: unexpected keyword argument",
           "shipped client cannot use F5 on the budget-bearing call")

    # ---------- F10 knowledge cutoffs + fork races --------------------
    wk = c.create_world(sid, "p0-f10", sharing_policy="FULLY_SHARED",
                        topology_group=g)["world_id"]
    c.start(wk)
    a1 = c.artifact(wk, "pre", b"pre", {"info_kind": "artifact"})
    ks = c.knowledge_set(wk)
    n_seq = [x["first_available_seq"] for x in ks["available"]
             if x["artifact_id"] == a1["artifact_id"]][0]
    def _aid(x):
        return x["artifact_id"] or x.get("source_artifact")
    def avail_at(wid_, seq):
        k = c.knowledge_set(wid_, seq=seq)
        return [_aid(x) for x in k["available"]]
    R["f10_cutoff"] = dict(
        before=a1["artifact_id"] in avail_at(wk, n_seq - 1),
        at=a1["artifact_id"] in avail_at(wk, n_seq),
        after=a1["artifact_id"] in avail_at(wk, n_seq + 1))
    # import cutoff in wb
    imp2 = c.import_artifact(wk, wa, art["artifact_id"])
    ks2 = c.knowledge_set(wk)
    i_seq = [x["first_available_seq"] for x in ks2["available"]
             if x["artifact_id"] == imp2["artifact_id"]][0]
    R["f10_import_cutoff"] = dict(
        before=imp2["artifact_id"] in avail_at(wk, i_seq - 1),
        at=imp2["artifact_id"] in avail_at(wk, i_seq))
    # fork frontier race, two levels
    ck2 = c.checkpoint(wk)
    a_post = c.artifact(wk, "post", b"post", {"info_kind": "artifact"})
    kids = c.fork(wk, ck2["checkpoint_id"], [{"name": "child"}])
    child = (kids[0]["world_id"] if isinstance(kids, list)
             else kids["children"][0]["world_id"])
    c.start(child)
    child_avail = [_aid(x)
                   for x in c.knowledge_set(child)["available"]]
    try:
        c.artifact_bytes(child, a1["artifact_id"])
        inherited_readable = True
    except EngineError:
        inherited_readable = False
    R["f10_inherited_content_readable"] = inherited_readable
    R["f10_fork_race"] = dict(
        pre_inherited=a1["artifact_id"] in child_avail,
        post_excluded=a_post["artifact_id"] not in child_avail)
    a_child = c.artifact(child, "cpost", b"cpost",
                         {"info_kind": "artifact"})
    ck3 = c.checkpoint(child)
    gks = c.fork(child, ck3["checkpoint_id"], [{"name": "gchild"}])
    gchild = (gks[0]["world_id"] if isinstance(gks, list)
              else gks["children"][0]["world_id"])
    g_avail = [_aid(x)
               for x in c.knowledge_set(gchild)["available"]]
    R["f10_grandparent"] = dict(
        grandparent_retained=a1["artifact_id"] in g_avail,
        parent_retained=a_child["artifact_id"] in g_avail,
        post_still_excluded=a_post["artifact_id"] not in g_avail)

    # ---------- A3 epistemic replay -----------------------------------
    # decision inputs: deterministic features from ledger+KS at seq
    wr = c.create_world(sid, "p0-replay")["world_id"]; c.start(wr)
    hr = c.hypothesis(wr, "replay")
    er = c.experiment(wr, {"cand": 7}, hyp_id=hr)
    c.observation(wr, er["exp_id"], {"score": 0.5}, "SURVIVED")
    c.artifact(wr, "note", b"evidence", {"info_kind": "artifact"})
    ks_now = c.knowledge_set(wr)
    seq = ks_now["world_head_seq"]
    pipe_src = open(OUT / "replay_pipeline.py", "rb").read()
    decl = dict(world=wr, seq=seq,
                pipeline_hash=hashlib.sha256(pipe_src).hexdigest())
    r1 = subprocess.run([sys.executable, str(OUT / "replay_pipeline.py"),
                         wr, str(seq)], capture_output=True, text=True)
    decl["vector_1"] = r1.stdout.strip()
    # destroy state: fresh subprocess = fresh process memory
    r2 = subprocess.run([sys.executable, str(OUT / "replay_pipeline.py"),
                         wr, str(seq)], capture_output=True, text=True)
    decl["vector_2"] = r2.stdout.strip()
    R["a3_replay"] = dict(bit_identical=bool(
        decl["vector_1"] == decl["vector_2"] and decl["vector_1"]),
        decl=decl)

    # ---------- adjudication ------------------------------------------
    checks = {
        "core_late_pred_409": R["core_late_pred"][0] == 409,
        "core_third_commit_409": R["core_third_commit"][0] == 409,
        "core_recommit_idem": R["core_recommit"][0] == "OK",
        "core_nested_422": R["core_nested_sneaky"][0] == 422,
        "core_fork_mint_409": R["core_fork_mint"][0] == 409,
        "f1_native": R["f1_native_roundtrip"],
        "f1_imported_hash": R["f1_imported_bytes_match"],
        "f1_unimported_deny": R["f1_unimported_deny"][0] in (403, 404),
        "f1_foreign_deny": R["f1_foreign_deny"][0] in (403, 404),
        "f2_success_ok": R["f2_success_kind"][0] == "OK",
        "f2_gate_success": R["f2_successonly_accepts_success"][0] == "OK",
        "f2_gate_failure": R["f2_successonly_rejects_failure"][0] == 403,
        "f3_repeat_rejected": R["f3_repeat_no_flag"][0] in (409, 422),
        "f3_replication_ok": R["f3_replication_ok"][0] == "OK",
        "f3_monotonic": R["f3_monotonic"],
        "f4_all_headers": all(R["f4_headers"].values()),
        "f5_exact_retry": R["f5_exact_retry_same"],
        "f5_changed_body_409": R["f5_changed_body"][0] == 409,
        "f5_no_double_debit": R["f5_exp_retry"]["same"]
        and R["f5_exp_retry"]["consumed"].get("experiments") == 1,
        "f10_cutoff_clean": (not R["f10_cutoff"]["before"])
        and R["f10_cutoff"]["at"],
        "f10_import_clean": (not R["f10_import_cutoff"]["before"])
        and R["f10_import_cutoff"]["at"],
        "f10_fork_race": all(R["f10_fork_race"].values()),
        "f10_grandparent": all(R["f10_grandparent"].values()),
        "a3_replay_bitident": R["a3_replay"]["bit_identical"],
    }
    for k, ok in checks.items():
        if not ok:
            defect(f"P0-{k}", "P1" if k.startswith(("f10", "a3", "f3",
                                                    "f5", "core"))
                   else "P2", k, f"see R[{k}]", "pass",
                   str(R.get(k.split('_')[0] + '_' + k, R))[:120],
                   "phase-0 gate")
    verdict = ("ENGINE_QUALIFIED" if all(checks.values())
               else "ENGINE_NOT_QUALIFIED")
    out = dict(release=v, checks=checks, raw=R, verdict=verdict,
               n_defects=len(DEFECTS))
    json.dump(out, open(OUT / "D15A_GEN21_REQUALIFICATION.json", "w"),
              indent=1, default=str)
    with open(OUT / "D15A_ENGINE_DEFECTS.jsonl", "w") as fh:
        for d in DEFECTS:
            fh.write(json.dumps(d) + "\n")
    print(json.dumps(checks, indent=1))
    print("VERDICT:", verdict, "| defects:", len(DEFECTS))


if __name__ == "__main__":
    main()
