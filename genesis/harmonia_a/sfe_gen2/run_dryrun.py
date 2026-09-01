#!/usr/bin/env python
"""GEN-2 dry-run campaign runner, per FREEZE_DRYRUN.md. Deterministic
client logic; the engine is the authority for budgets, ordering,
isolation, and evidence. Writes results/dryrun_log.jsonl + summary."""

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
SEEDS = (11, 22, 33, 44, 55)
K_SIB = 3
BUDGET = 40
ARMS = ("A1", "A2", "A3", "A4")
OUT = Path("results")


def target_bits(arm, seed, decoy=False):
    tag = f"dryrun1-{'decoy-' if decoy else ''}{arm}-{seed}"
    h = hashlib.sha256(tag.encode()).digest()
    v = int.from_bytes(h[:3], "big")
    return v


def score_of(cand, tgt):
    x = ~(cand ^ tgt) & 0xFFFFFF
    return bin(x).count("1") / 24.0


def main():
    OUT.mkdir(exist_ok=True)
    tok = open(r"C:\ZeusD-var\harmonia\sfe_token.txt").read().strip()
    c = EngineClient(BASE, token=tok, cafile=CA)
    v = c.version()
    assert v["engine_source_hash"] == PIN, "release pin mismatch - STOP"
    log = (OUT / "dryrun_log.jsonl").open("a")

    def rec(kind, **kw):
        kw.update(kind=kind, t=time.time())
        log.write(json.dumps(kw, sort_keys=True, default=str) + "\n")
        log.flush()

    sid = c.create_session("dryrun-topology-1")
    # ---- meta-world: prospective campaign predictions BEFORE any arm world
    meta = c.create_world(sid, "dryrun-meta")
    mw = meta["world_id"]; c.start(mw)
    mh = c.hypothesis(mw, "sharing topology affects search efficiency "
                          "at matched engine-enforced budget")
    preds = {}
    for name, text in (("P1", "mean best-score A2 > A1"),
                       ("P2", "mean best-score A3 >= A2"),
                       ("P3", "|A4-A1| < |A2-A1| (sham inert)")):
        preds[name] = c.prediction(mw, mh, {"claim": text})
    meta_exp = c.experiment(mw, {"campaign": "topology-1",
                                 "freeze": "FREEZE_DRYRUN.md"},
                            hyp_id=mh)
    rec("meta", world=mw, preds=preds, exp=meta_exp["exp_id"],
        engine=v)

    results = {}
    late_pred_probe_done = False
    t0 = time.time()
    for arm in ARMS:
        for seed in SEEDS:
            grp = (c.create_topology_group(note=f"dryrun-{arm}-{seed}")
                   if arm != "A1" else None)
            policy = {"A1": "ISOLATED", "A2": "FAILURES_ONLY",
                      "A3": "FULLY_SHARED", "A4": "FAILURES_ONLY"}[arm]
            tgt = target_bits(arm, seed)
            dtgt = target_bits(arm, seed, decoy=True)
            pool = {}          # artifact_id -> (payload, blob_hash, src)
            imported_pairs = set()
            sibs = []
            for k in range(K_SIB):
                w = c.create_world(
                    sid, f"dr-{arm}-s{seed}-k{k}",
                    sharing_policy=policy, topology_group=grp,
                    budget={"experiments": {"limit": BUDGET,
                                            "enforcement": "enforceable"}})
                c.start(w["world_id"])
                sibs.append(dict(wid=w["world_id"], k=k,
                                 rng=np.random.default_rng(
                                     np.random.SeedSequence(
                                         [20260917, hash(arm) & 0xffff,
                                          seed, k])),
                                 base=None, best=-1.0, tabu=set(),
                                 exported=set(), done=False))
            # round-robin until every sibling's budget blocks
            it = 0
            while not all(s["done"] for s in sibs):
                it += 1
                for s in sibs:
                    if s["done"]:
                        continue
                    rng = s["rng"]
                    if s["base"] is None:
                        cand = int(rng.integers(0, 1 << 24))
                    else:
                        cand = s["base"]
                        for _ in range(int(rng.integers(1, 4))):
                            cand ^= 1 << int(rng.integers(24))
                    tries = 0
                    while cand in s["tabu"] and tries < 8:
                        cand ^= 1 << int(rng.integers(24)); tries += 1
                    try:
                        e = c.experiment(s["wid"], {"candidate": cand},
                                         enqueue=True, kind="score")
                    except EngineError as ex:
                        if ex.status == 409:
                            s["done"] = True
                            rec("budget_stop", wid=s["wid"], iters=it)
                            continue
                        raise
                    wk = c.claim(f"drw-{arm}-{seed}", world_id=s["wid"])
                    sc = score_of(cand, tgt)
                    c.complete(wk["work_id"], f"drw-{arm}-{seed}",
                               wk["claim_id"], {"score": sc})
                    c.observation(s["wid"], e["exp_id"], {"score": sc},
                                  "SURVIVED" if sc > s["best"]
                                  else "INCONCLUSIVE",
                                  work_id=wk["work_id"])
                    s["tabu"].add(cand)
                    if sc > s["best"]:
                        s["best"], s["base"] = sc, cand
                    else:
                        c.failure(s["wid"], failure_type="no_improvement",
                                  falsifier="score", violated="sc>best",
                                  observed={"candidate": cand,
                                            "score": sc})
                    # export per arm rules
                    if arm in ("A2", "A3", "A4") and cand not in s["exported"]:
                        exp_score = (score_of(cand, dtgt) if arm == "A4"
                                     else sc)
                        kind_ = ("success" if (arm == "A3"
                                               and sc >= s["best"])
                                 else "failure")
                        blob = json.dumps({"candidate": cand,
                                           "score": exp_score}).encode()
                        art = c.artifact(s["wid"], "cand", blob,
                                         {"info_kind": kind_})
                        pool[art["artifact_id"]] = (
                            json.loads(blob), art["blob_hash"], s["wid"])
                        s["exported"].add(cand)
                # import step every 5 rounds
                if it % 5 == 0 and arm != "A1":
                    for s in sibs:
                        if s["done"]:
                            continue
                        for aid, (payload, bhash, src_wid) in list(
                                pool.items()):
                            if src_wid == s["wid"]:
                                continue
                            key = (s["wid"], aid)
                            if key in imported_pairs:
                                continue
                            try:
                                imp = c.import_artifact(s["wid"],
                                                        src_wid, aid)
                            except EngineError:
                                imported_pairs.add(key)
                                continue
                            imported_pairs.add(key)
                            if imp.get("source_hash") != bhash:
                                rec("hash_mismatch", aid=aid)
                                continue
                            cnd = payload.get("candidate")
                            scr = payload.get("score", -1)
                            if cnd is not None:
                                s["tabu"].add(cnd)
                                if scr > s["best"]:
                                    s["best"] = scr
                                    s["base"] = cnd
                # live DFX-1 regression once, mid-campaign
                if not late_pred_probe_done and it == 10:
                    late_pred_probe_done = True
                    hh = c.hypothesis(sibs[0]["wid"], "late probe")
                    pp = c.prediction(sibs[0]["wid"], hh, {"x": 1})
                    try:
                        ee = c.experiment(sibs[0]["wid"],
                                          {"candidate": 0})
                        p2 = c.prediction(sibs[0]["wid"], hh, {"y": 2})
                        c.observation(sibs[0]["wid"], ee["exp_id"],
                                      {"s": 0}, "SURVIVED", pred_id=p2)
                        rec("late_pred_probe", result="ACCEPTED_BAD")
                    except EngineError as ex:
                        rec("late_pred_probe", result=f"{ex.status}")
            bests = [s["best"] for s in sibs]
            results[f"{arm}-{seed}"] = bests
            rec("cell_done", arm=arm, seed=seed, bests=bests,
                elapsed=round(time.time() - t0, 1))
            print(f"{arm} seed {seed}: bests={[round(b,3) for b in bests]}"
                  f"  {round(time.time()-t0,0)}s", flush=True)

    # ---- campaign observations against the prospective predictions
    means = {arm: float(np.mean([b for s in SEEDS
                                 for b in results[f"{arm}-{s}"]]))
             for arm in ARMS}
    seed_means = {arm: {s: float(np.mean(results[f"{arm}-{s}"]))
                        for s in SEEDS} for arm in ARMS}
    # permutation on seed-level A2-A1 diffs
    d = [seed_means["A2"][s] - seed_means["A1"][s] for s in SEEDS]
    rng = np.random.default_rng(20260918)
    obs = float(np.mean(d))
    null = [float(np.mean([x * sg for x, sg in
                           zip(d, rng.choice([-1, 1], size=len(d)))]))
            for _ in range(4096)]
    p1_p = float(np.mean([abs(n) >= abs(obs) for n in null]))
    outcomes = {
        "P1": ("SURVIVED" if means["A2"] > means["A1"] else "FALSIFIED"),
        "P2": ("SURVIVED" if means["A3"] >= means["A2"] else "FALSIFIED"),
        "P3": ("SURVIVED"
               if abs(means["A4"] - means["A1"])
               < abs(means["A2"] - means["A1"]) else "FALSIFIED")}
    for name, out in outcomes.items():
        c.observation(mw, meta_exp["exp_id"],
                      {"means": means, "perm_p_A2_A1": p1_p},
                      out, pred_id=preds[name])
    summary = dict(release=v, means=means, seed_means=seed_means,
                   perm_p_A2_A1=p1_p, outcomes=outcomes,
                   meta_world=mw)
    json.dump(summary, open(OUT / "dryrun_summary.json", "w"), indent=1)
    rec("campaign_done", **{k: v2 for k, v2 in summary.items()
                            if k != "release"})
    print(json.dumps({k: v2 for k, v2 in summary.items()
                      if k not in ("release", "seed_means")}, indent=1))


if __name__ == "__main__":
    main()
