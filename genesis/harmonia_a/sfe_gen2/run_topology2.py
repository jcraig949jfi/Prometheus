#!/usr/bin/env python
"""TOPOLOGY-2 runner, per FREEZE_TOPOLOGY2.md. Deterministic client
logic; engine authoritative for budgets/ordering/isolation/evidence.
Resumable at (K, idx, arm) cell granularity."""

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
from sfclient.client import EngineClient, EngineError

BASE = "https://192.168.1.202:8811"
CA = (r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient"
      r"\config\m1.crt")
PIN = ("sha256:e367e791c10080decc8ac8152c82fde61b426682a9bc298403f0"
       "ccc970f9ed1a")
N = 24
KS = (0, 4, 8)
N_INST = 6
K_SIB = 2
BUDGET = 35
ARMS = ("A1", "A2", "A3", "A4", "A5")
OUT = Path("results")
FREEZE_HASH = open(OUT / "t2_freeze_hash.txt").read().strip()


class Instance:
    def __init__(self, K, idx, tag="main"):
        rng = np.random.default_rng(np.random.SeedSequence(
            [20260919, K, idx] + ([99] if tag == "decoy" else [])))
        self.K = K
        self.nbrs = [rng.choice([j for j in range(N) if j != i],
                                size=K, replace=False).tolist()
                     for i in range(N)]
        self.tables = [rng.random(1 << (K + 1)) for _ in range(N)]

    def score(self, x):
        total = 0.0
        for i in range(N):
            bits = (x >> i) & 1
            for b, j in enumerate(self.nbrs[i]):
                bits |= ((x >> j) & 1) << (b + 1)
            total += self.tables[i][bits]
        return total / N


def main():
    OUT.mkdir(exist_ok=True)
    tok = open(r"C:\ZeusD-var\harmonia\sfe_token.txt").read().strip()
    c = EngineClient(BASE, token=tok, cafile=CA, timeout=120.0)
    v = c.version()
    assert v["engine_source_hash"] == PIN, "release pin mismatch - STOP"
    log = (OUT / "t2_log.jsonl").open("a")

    def rec(kind, **kw):
        kw.update(kind=kind, t=time.time())
        log.write(json.dumps(kw, sort_keys=True, default=str) + "\n")
        log.flush()

    done_cells = set()
    results = {}
    logp = OUT / "t2_log.jsonl"
    if logp.exists():
        for line in open(logp):
            r0 = json.loads(line)
            if r0.get("kind") == "cell_done":
                key = (r0["K"], r0["idx"], r0["arm"])
                done_cells.add(key)
                results[f"{r0['K']}-{r0['idx']}-{r0['arm']}"] = r0["bests"]
    if done_cells:
        print(f"RESUME: {len(done_cells)} cells done", flush=True)

    sid = c.create_session("topology-2")
    if not done_cells:
        mw = c.create_world(sid, "t2-meta")["world_id"]
        c.start(mw)
        mh = c.hypothesis(mw, "shared negative evidence is context-"
                              "sensitive information, not generic "
                              "diversification")
        preds = {}
        for name, text in (
                ("P1", "pooled D_failure > 0"),
                ("P2", "pooled (D_failure - D_misleading) >= 0.02"),
                ("P3", "d(D_full)/dK < 0")):
            preds[name] = c.prediction(mw, mh, {
                "claim": text, "freeze_hash": FREEZE_HASH})
        me = c.experiment(mw, {"campaign": "topology-2",
                               "freeze_hash": FREEZE_HASH}, hyp_id=mh)
        rec("meta", world=mw, preds=preds, exp=me["exp_id"], engine=v)
    else:
        meta_line = [json.loads(l) for l in open(logp)
                     if json.loads(l).get("kind") == "meta"][0]
        mw, preds = meta_line["world"], meta_line["preds"]
        me = {"exp_id": meta_line["exp"]}

    late_probe_done = any(json.loads(l).get("kind") == "late_pred_probe"
                          for l in open(logp)) if logp.exists() else False
    t0 = time.time()
    for K in KS:
        for idx in range(N_INST):
            inst = Instance(K, idx)
            decoy = Instance(K, idx, tag="decoy")          # A4 scores
            mislead = Instance(K, (idx + 1) % N_INST)      # A5 scores
            for arm in ARMS:
                if (K, idx, arm) in done_cells:
                    continue
                grp = (c.create_topology_group(
                    note=f"t2-{K}-{idx}-{arm}") if arm != "A1" else None)
                policy = {"A1": "ISOLATED", "A2": "FAILURES_ONLY",
                          "A3": "FULLY_SHARED", "A4": "FAILURES_ONLY",
                          "A5": "FAILURES_ONLY"}[arm]
                pool = {}
                imported_pairs = set()
                sibs = []
                for k in range(K_SIB):
                    w = c.create_world(
                        sid, f"t2-{arm}-K{K}-i{idx}-k{k}",
                        sharing_policy=policy, topology_group=grp,
                        budget={"experiments": {
                            "limit": BUDGET,
                            "enforcement": "enforceable"}})
                    c.start(w["world_id"])
                    sibs.append(dict(
                        wid=w["world_id"], k=k,
                        rng=np.random.default_rng(np.random.SeedSequence(
                            [20260921, K, idx,
                             ARMS.index(arm), k])),
                        base=None, best=-1.0, tabu=set(),
                        exported=set(), done=False))
                it = 0
                while not all(s["done"] for s in sibs):
                    it += 1
                    for s in sibs:
                        if s["done"]:
                            continue
                        rng = s["rng"]
                        if s["base"] is None:
                            cand = int(rng.integers(0, 1 << N))
                        else:
                            cand = s["base"]
                            for _ in range(int(rng.integers(1, 4))):
                                cand ^= 1 << int(rng.integers(N))
                        tries = 0
                        while cand in s["tabu"] and tries < 8:
                            cand ^= 1 << int(rng.integers(N))
                            tries += 1
                        try:
                            e = c.experiment(s["wid"],
                                             {"candidate": cand},
                                             enqueue=True, kind="score")
                        except EngineError as ex:
                            if ex.status == 409:
                                s["done"] = True
                                continue
                            raise
                        wk = c.claim(f"t2w-{arm}-{K}-{idx}",
                                     world_id=s["wid"])
                        sc = inst.score(cand)
                        c.complete(wk["work_id"], f"t2w-{arm}-{K}-{idx}",
                                   wk["claim_id"], {"score": sc})
                        c.observation(s["wid"], e["exp_id"],
                                      {"score": sc},
                                      "SURVIVED" if sc > s["best"]
                                      else "INCONCLUSIVE",
                                      work_id=wk["work_id"])
                        s["tabu"].add(cand)
                        if sc > s["best"]:
                            s["best"], s["base"] = sc, cand
                        else:
                            c.failure(s["wid"],
                                      failure_type="no_improvement",
                                      falsifier="score",
                                      violated="sc>best",
                                      observed={"candidate": cand,
                                                "score": sc})
                        if arm != "A1" and cand not in s["exported"]:
                            if arm == "A4":
                                exp_score = decoy.score(cand)
                            elif arm == "A5":
                                exp_score = mislead.score(cand)
                            else:
                                exp_score = sc
                            kind_ = ("artifact"
                                     if (arm == "A3" and sc >= s["best"])
                                     else "failure")
                            blob = json.dumps(
                                {"candidate": cand,
                                 "score": exp_score}).encode()
                            art = c.artifact(s["wid"], "cand", blob,
                                             {"info_kind": kind_})
                            pool[art["artifact_id"]] = (
                                json.loads(blob), art["blob_hash"],
                                s["wid"])
                            s["exported"].add(cand)
                    if it % 5 == 0 and arm != "A1":
                        for s in sibs:
                            if s["done"]:
                                continue
                            for aid, (payload, bhash, src_wid) in list(
                                    pool.items()):
                                if src_wid == s["wid"]:
                                    continue
                                key2 = (s["wid"], aid)
                                if key2 in imported_pairs:
                                    continue
                                try:
                                    imp = c.import_artifact(
                                        s["wid"], src_wid, aid)
                                except EngineError:
                                    imported_pairs.add(key2)
                                    continue
                                imported_pairs.add(key2)
                                if imp.get("source_hash") != bhash:
                                    rec("hash_mismatch", aid=aid)
                                    continue
                                cnd = payload.get("candidate")
                                scr = payload.get("score", -1)
                                if cnd is not None:
                                    s["tabu"].add(cnd)
                                    if scr > s["best"]:
                                        # ancestry log (review invariant)
                                        rec("adoption", wid=s["wid"],
                                            aid=aid, from_wid=src_wid,
                                            claimed_score=scr)
                                        s["best"] = scr
                                        s["base"] = cnd
                    if not late_probe_done and it == 8:
                        late_probe_done = True
                        hh = c.hypothesis(sibs[0]["wid"], "late probe")
                        try:
                            ee = c.experiment(sibs[0]["wid"],
                                              {"candidate": 0})
                            p2 = c.prediction(sibs[0]["wid"], hh,
                                              {"y": 2})
                            c.observation(sibs[0]["wid"], ee["exp_id"],
                                          {"s": 0}, "SURVIVED",
                                          pred_id=p2)
                            rec("late_pred_probe",
                                result="ACCEPTED_BAD")
                        except EngineError as ex:
                            rec("late_pred_probe", result=str(ex.status))
                # NOTE: adopted "best" may be decoy/mislead-inflated for
                # A4/A5; the CELL RESULT is the TRUE best on the real
                # instance over evaluated candidates:
                bests = []
                for s in sibs:
                    true_best = max((inst.score(cd) for cd in s["tabu"]
                                     if True), default=0.0)
                    bests.append(true_best)
                results[f"{K}-{idx}-{arm}"] = bests
                rec("cell_done", K=K, idx=idx, arm=arm, bests=bests,
                    elapsed=round(time.time() - t0, 1))
                print(f"K={K} idx={idx} {arm}: "
                      f"{[round(b,3) for b in bests]} "
                      f"{round(time.time()-t0,0)}s", flush=True)

    # ---------------- frozen adjudication (estimation-first)
    def Y(K, idx, arm):
        return float(np.mean(results[f"{K}-{idx}-{arm}"]))

    D = {arm: {K: [Y(K, i, arm) - Y(K, i, "A1")
                   for i in range(N_INST)] for K in KS}
         for arm in ("A2", "A3", "A4", "A5")}
    pooled = {arm: float(np.mean([d for K in KS for d in D[arm][K]]))
              for arm in D}
    perK = {arm: {K: float(np.mean(D[arm][K])) for K in KS}
            for arm in D}
    slope = {arm: float(np.polyfit(
        [K for K in KS for _ in range(N_INST)],
        [d for K in KS for d in D[arm][K]], 1)[0]) for arm in D}
    rng = np.random.default_rng(20260920)
    boots = {arm: [] for arm in D}
    pairs = [(K, i) for K in KS for i in range(N_INST)]
    for _ in range(10000):
        pick = rng.integers(len(pairs), size=len(pairs))
        for arm in D:
            boots[arm].append(float(np.mean(
                [D[arm][pairs[j][0]][pairs[j][1]] for j in pick])))
    ci = {arm: [float(np.percentile(boots[arm], q)) for q in (2.5, 97.5)]
          for arm in D}
    disc = pooled["A2"] - pooled["A5"]

    if pooled["A2"] >= 0.02 and disc >= 0.02:
        verdict = "T2_SUPPORTS"
    elif (pooled["A2"] >= 0.02 and pooled["A5"] >= 0.02
          and abs(disc) < 0.01):
        verdict = "T2_CONTRADICTS_DIVERSIFICATION"
    elif pooled["A2"] <= 0:
        verdict = "T2_CONTRADICTS_WORTHLESS"
    else:
        verdict = "T2_INDETERMINATE"
    inversion = bool(slope["A3"] < 0
                     and perK["A3"][8] < perK["A3"][0] - 0.02)

    outcomes = {
        "P1": "SURVIVED" if pooled["A2"] > 0 else "FALSIFIED",
        "P2": "SURVIVED" if disc >= 0.02 else "FALSIFIED",
        "P3": "SURVIVED" if slope["A3"] < 0 else "FALSIFIED"}
    for name, out in outcomes.items():
        c.observation(mw, me["exp_id"],
                      {"pooled": pooled, "perK": perK,
                       "slopes": slope, "freeze_hash": FREEZE_HASH},
                      out, pred_id=preds[name])
    summary = dict(release=v, pooled=pooled, perK=perK, slopes=slope,
                   ci95=ci, discrimination=disc, outcomes=outcomes,
                   inversion=inversion, verdict=verdict, meta_world=mw)
    json.dump(summary, open(OUT / "t2_summary.json", "w"), indent=1)
    rec("campaign_done", **{k: v2 for k, v2 in summary.items()
                            if k != "release"})
    print(json.dumps({k: v2 for k, v2 in summary.items()
                      if k != "release"}, indent=1))


if __name__ == "__main__":
    main()
