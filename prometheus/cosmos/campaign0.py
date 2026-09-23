"""Campaign 0 -- instrument qualification. Executes roles/Cosmos/campaigns/c0/PREREG.md in order.

  python -m prometheus.cosmos.campaign0 --out <dir> [--quick]

Steps (each writes <out>/<step>.json; the store and receipt chain live in <out>/store):
  pools      per-family pools of lattice worlds (seeded)
  oracle     PRIVATE dense labels of every pool world (scoring only)
  G0         replay of 30 queried worlds + receipt-chain verification
  G1         within-family validity: shams quiet, both phases present, positive control
  sampler    eta comparison: random / grid / boundary / active at two budgets x seeds
  main       main dataset = active sampler, preregistered budget, seed 0
  mine       law on v1 coordinates (primary); v2 and raw (unnormalized) as declared secondaries
  adversary  up to MAX_ROUNDS attack/revise rounds on visible families only
  G7         family dependence of the final law
  freeze     final law frozen in the ledger
  G5         broker: sealed family predictions (predictions receipted before any D run)
  G6         broker: frozen intervention prescriptions, then ladders
  report     gates table
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos import broker
from prometheus.cosmos.adversary import attack
from prometheus.cosmos.hashing import code_identity, derive_seed
from prometheus.cosmos.miner import Miner, default_workers, law_from_json
from prometheus.cosmos.pipeline import Chamber, design, mine_rows
from prometheus.cosmos.sampler import STRATEGIES, Budget, knn_ba
from prometheus.cosmos.store import Store
from prometheus.cosmos.substrates import visible

COMMITMENT = "48e709653f2bbda12c6b1d1c499d801339ec7897e9bf3081764c50691cfa8265"
CAMPAIGN_SEED = 20260923
POOL = 1200
MAIN_BUDGET = 80
ETA_BUDGETS = (30, 60)
ETA_SEEDS = (1, 2, 3)
MAX_ROUNDS = 3
N_PERM = 19


def _dump(out: Path, name: str, obj: Any) -> None:
    (out / (name + ".json")).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str), encoding="utf-8")


def _ba(pred, y):
    y = np.asarray(y)
    pred = np.asarray(pred, bool)
    if y.sum() == 0 or (1 - y).sum() == 0:
        return float("nan")
    return float(0.5 * ((pred & (y == 1)).sum() / (y == 1).sum() + (~pred & (y == 0)).sum() / (y == 0).sum()))


def build_pools(fams, n: int, seed: int) -> Dict[str, List[Dict[str, Any]]]:
    pools = {}
    for name, fam in fams.items():
        rng = np.random.default_rng(derive_seed(seed, "pool", name) % (2 ** 32))
        sp = fam.space()
        seen, out = set(), []
        tries = 0
        while len(out) < n and tries < 50 * n:
            tries += 1
            p = {k: v[rng.integers(len(v))] for k, v in sp.items()}
            p = {k: (float(x) if isinstance(x, (float, np.floating)) else int(x)) for k, x in p.items()}
            if name == "ca" and p["V"] and (max(1, int(np.ceil(np.log2(p["V"])))) * p["r"] > p["Lc"]):
                continue
            key = json.dumps(p, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            out.append(p)
        pools[name] = out
    return pools


def run(out: Path, quick: bool = False) -> Dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ident = code_identity()
    _dump(out, "identity", ident)
    fams = visible()
    pool_n = 150 if quick else POOL
    budget = 30 if quick else MAIN_BUDGET
    n_perm = 5 if quick else N_PERM
    store = Store(out / "store")
    store.receipts.append("campaign_start", {"identity": ident, "quick": quick, "commitment": COMMITMENT})
    report: Dict[str, Any] = {"identity": ident, "quick": quick, "gates": {}}

    # ---- pools and PRIVATE oracle
    pools = build_pools(fams, pool_n, CAMPAIGN_SEED)
    oracle_ch = Chamber(list(fams.values()), store=None, campaign="c0", code_sha=ident["cosmos_src_sha"])
    oracle: Dict[str, List[Dict[str, Any]]] = {}
    for f, P in pools.items():
        oracle[f] = [oracle_ch.observe(f, p, purpose="oracle", keep=False) for p in P]
    # what a strategy may see about an UNQUERIED world: spec-side fields only (whitelist, never a blacklist)
    POOL_FIELDS = ("family", "lineage", "world_id", "params", "coords", "coords_v2")
    pool_rows = {f: [{k: r[k] for k in POOL_FIELDS} for r in rows] for f, rows in oracle.items()}
    _dump(out, "oracle_summary", {f: {"n": len(v), "pays_rate": float(np.mean([r["y"] for r in v]))} for f, v in oracle.items()})
    report["t_oracle_s"] = round(time.time() - t0, 1)

    # ---- G1 within-family validity
    g1 = {}
    ctl = Chamber(list(fams.values()), store=store, campaign="c0", code_sha=ident["cosmos_src_sha"])
    for f, fam in fams.items():
        rng = np.random.default_rng(derive_seed(CAMPAIGN_SEED, "g1", f) % (2 ** 32))
        idx = rng.choice(len(pools[f]), 20, replace=False)
        shams = []
        for i in idx:
            base_row = ctl.observe(f, pools[f][i], purpose="G1:base", keep=False)
            shams.append(ctl.observe(f, fam.sham(pools[f][i]), purpose="G1:sham", keep=False,
                                     parent=base_row["world_id"], edge_kind="CONTROL_OF", delta={"control": "sham"})["y"])
        rate = float(np.mean([r["y"] for r in oracle[f]]))
        g1[f] = {"sham_pays": int(sum(shams)), "pays_rate": rate, "pass": sum(shams) == 0 and 0.05 <= rate <= 0.95}
    report["gates"]["G1"] = {"per_family": g1, "verdict": "PASS" if all(v["pass"] for v in g1.values()) else "FAIL"}
    _dump(out, "G1", report["gates"]["G1"])

    # ---- sampler efficiency (eta)
    eta = []
    X_or = {f: design(oracle[f]) for f in oracle}
    all_or = [r for f in oracle for r in oracle[f]]
    Xall, yall, gall, _ = design(all_or)
    for B in (ETA_BUDGETS if not quick else (15,)):
        for s in (ETA_SEEDS if not quick else (1,)):
            for name, fn in STRATEGIES.items():
                b = Budget(pool_rows, oracle, B)
                fn(b, np.random.default_rng(1000 * s + B))
                rows = b.rows()
                X, y, g, _ = design(rows)
                best, _ = Miner(X, y, g).search(y)
                if best is not None:
                    L = Miner(X, y, g).refit(best.structure(), X, y)
                    law_ba = _ba(L.predict(Xall), yall)
                    law_s = L.show()
                else:
                    law_ba, law_s = float("nan"), "NONE"
                eta.append({"budget": B, "seed": s, "strategy": name, "n_queries": len(rows),
                            "law": law_s, "law_ba_oracle": law_ba, "knn_ba_oracle": knn_ba(rows, all_or),
                            "pays_rate_queried": float(y.mean())})
    _dump(out, "sampler_eta", eta)
    report["t_eta_s"] = round(time.time() - t0, 1)

    # ---- main dataset (preregistered: active, seed 0)
    ch = Chamber(list(fams.values()), store=store, campaign="c0", code_sha=ident["cosmos_src_sha"])
    b = Budget(pool_rows, oracle, budget)
    STRATEGIES["active"](b, np.random.default_rng(CAMPAIGN_SEED))
    for f in b.pool:
        for i in b.seen[f]:
            ch.observe(f, pools[f][i], purpose="main")
    # matched single-knob neighbours (Nestor control_partner pattern): +-1 level on the cost and
    # noise knobs of 8 main worlds per family. Graph + G1b only; NOT added to the mining rows.
    COST = {"regs": "bitcost", "ring": "ehop", "ca": "ccell"}
    NOISE = {"regs": "q", "ring": "lam", "ca": "p"}
    g1b = {}
    rng_e = np.random.default_rng(CAMPAIGN_SEED + 3)
    for f in fams:
        mains = [r for r in ch.rows if r["family"] == f]
        pick = [mains[i] for i in rng_e.choice(len(mains), min(8, len(mains)), replace=False)]
        up, down = 0, 0
        for r in pick:
            for k, q in fams[f].deform(r["params"]):
                if k not in (COST[f], NOISE[f]):
                    continue
                nb = ch.observe(f, q, purpose="matched_neighbour", parent=r["world_id"], edge_kind="DEFORMATION_OF",
                                delta={"knob": k, "from": r["params"][k], "to": q[k]}, keep=False)
                if k == COST[f] and q[k] > r["params"][k]:
                    up += 1
                    down += nb["fitness"]["SEL"] <= r["fitness"]["SEL"] + 1e-9
        g1b[f] = {"cost_up_edges": up, "sel_fitness_nonincreasing": down,
                  "pass": up > 0 and down / up >= 0.9}
    report["gates"]["G1"]["causal_consistency"] = g1b
    if not all(v["pass"] for v in g1b.values()):
        report["gates"]["G1"]["verdict"] = "FAIL"
    # deformation edges among main nodes (single-knob neighbours that were both queried)
    ids = {(r["family"], json.dumps(r["params"], sort_keys=True)): r["world_id"] for r in ch.rows}
    for r in list(ch.rows):
        for k, q in fams[r["family"]].deform(r["params"]):
            key = (r["family"], json.dumps(q, sort_keys=True))
            if key in ids:
                store.add_edge(r["world_id"], ids[key], "DEFORMATION_OF", {"knob": k})
    store.commit()

    # ---- G0 reproducibility
    rng = np.random.default_rng(CAMPAIGN_SEED + 7)
    reps = [ch.rows[i] for i in rng.choice(len(ch.rows), min(30, len(ch.rows)), replace=False)]
    same = 0
    from prometheus.cosmos.world import evaluate
    for r in reps:
        a = evaluate(fams[r["family"]], r["params"], campaign="c0")
        bb = evaluate(fams[r["family"]], r["params"], campaign="c0")
        same += a["obs_digest"] == bb["obs_digest"]
    chain_ok = store.receipts.verify() is None
    report["gates"]["G0"] = {"replayed": len(reps), "identical": same, "receipt_chain_ok": chain_ok,
                             "verdict": "PASS" if same == len(reps) and chain_ok else "FAIL"}

    # ---- mining: primary v1, secondaries v2 and raw
    main_rows = list(ch.rows)
    res_v1 = mine_rows(main_rows, "v1", n_perm=n_perm)
    res_v2 = mine_rows(main_rows, "v2", n_perm=n_perm)
    raw_rows = [dict(r, coords=dict(r["coords"], C=r["coords"]["C"] * r["params"]["R"])) for r in main_rows]
    res_raw = mine_rows(raw_rows, "v1", n_perm=n_perm)
    _dump(out, "mine_initial", {"v1": res_v1, "v2": res_v2, "raw_unnormalized_C": res_raw})
    report["mine_initial"] = {k: {"verdict": v["verdict"], "law": v["law"]["law"] if v["law"] else None,
                                  "score": v["best_score"], "p": v["p_null"]} for k, v in
                              (("v1", res_v1), ("v2", res_v2), ("raw", res_raw))}

    # ---- adversary rounds on the primary coordinates
    cmap = "v1"
    res = res_v1
    law_id = None
    parent = None
    rounds = []
    for rnd in range(MAX_ROUNDS):
        if res["verdict"] != "CANDIDATE":
            break
        law_id = store.propose_law({"law": res["law"], "cmap": cmap, "mined_on": len(ch.rows), "round": rnd}, parent=parent,
                                   note="mined round %d" % rnd)
        store.event(law_id, "ATTACKED", "round %d" % rnd)
        L = law_from_json(res["law"])
        rep = attack(L, ch, pool_rows, np.random.default_rng(CAMPAIGN_SEED + 100 + rnd), per_family=24 if quick else 48,
                     law_id=law_id)
        rounds.append({"round": rnd, "law": res["law"]["law"], "law_id": law_id, "attack": rep})
        store.receipts.append("attack_round", {"law_id": law_id, "verdict": rep["verdict"], "rate": rep["rate"],
                                               "n_confident": rep["n_confident"], "n_confirmed": rep["n_confirmed"]})
        if rep["verdict"] == "SURVIVED":
            store.event(law_id, "SURVIVED", "attack round %d: %d/%d confirmed" % (rnd, rep["n_confirmed"], rep["n_confident"]))
            break
        store.event(law_id, "FAILED", "attack round %d: %d/%d confirmed counterexamples" % (rnd, rep["n_confirmed"], rep["n_confident"]))
        parent = law_id
        # revision: re-mine on everything observed so far (attack rows included); coordinates may switch to v2
        # only if v2 beats v1 on the enlarged data (both reported)
        r1 = mine_rows(ch.rows, "v1", n_perm=n_perm)
        r2 = mine_rows(ch.rows, "v2", n_perm=n_perm)
        pick = r2 if (r2["verdict"] == "CANDIDATE" and (r1["verdict"] != "CANDIDATE" or r2["best_score"] > r1["best_score"] + 0.01)) else r1
        cmap = "v2" if pick is r2 else "v1"
        rounds[-1]["revision"] = {"v1": {"verdict": r1["verdict"], "law": r1["law"] and r1["law"]["law"], "score": r1["best_score"]},
                                  "v2": {"verdict": r2["verdict"], "law": r2["law"] and r2["law"]["law"], "score": r2["best_score"]},
                                  "picked": cmap}
        res = pick
        law_id = None
    store.commit()
    _dump(out, "adversary", rounds)
    report["adversary"] = [{"round": r["round"], "law": r["law"], "verdict": r["attack"]["verdict"],
                            "confirmed": r["attack"]["n_confirmed"], "confident": r["attack"]["n_confident"],
                            "by_kind": r["attack"]["by_kind"], "revision": r.get("revision")} for r in rounds]
    survived = bool(rounds) and rounds[-1]["attack"]["verdict"] == "SURVIVED"
    final_id = rounds[-1]["law_id"] if survived else None
    report["gates"]["G4"] = {"rounds": len(rounds), "verdict": "PASS" if survived else ("NOT REACHED" if not rounds else "FAIL")}

    # ---- G2 compression on the final data
    final = None
    if final_id:
        final = store.law(final_id)["body"]
        fres = mine_rows(ch.rows, final["cmap"], n_perm=n_perm)
        worst = min(final["law"]["fold_ba"].values())
        mean = float(np.mean(list(final["law"]["fold_ba"].values())))
        raw_score = res_raw["best_score"]
        report["gates"]["G2"] = {"worst_fold_ba": worst, "mean_fold_ba": mean, "p_null": res_v1["p_null"] if final["cmap"] == "v1" else None,
                                 "raw_unnormalized_best_score": raw_score, "law_score": final["law"]["score"],
                                 "verdict": "PASS" if worst >= 0.75 and mean >= 0.85 and final["law"]["score"] >= raw_score + 0.03 else "FAIL"}
        fd = fres.get("family_dependence") or {}
        report["gates"]["G7"] = {**fd, "verdict": "PASS" if fd and (fd["p"] > 0.01 or fd["mu_bits"] < 0.02) else "FAIL"}
    else:
        report["gates"]["G2"] = {"verdict": "FAIL" if res_v1["verdict"] != "CANDIDATE" else "NOT REACHED",
                                 "initial": report["mine_initial"]["v1"]}
        report["gates"]["G7"] = {"verdict": "NOT REACHED"}

    # ---- freeze, holdout, intervention
    if final_id and not quick:
        fh = store.freeze_law(final_id)
        vis_rate = float(np.mean([r["y"] for r in ch.rows]))
        vis = list(ch.rows)
        from prometheus.cosmos.sampler import feats

        def knn(X):
            Zt = feats([r[("coords" if final["cmap"] == "v1" else "coords_v2")] for r in vis])
            yt = np.array([r["y"] for r in vis])
            Zq = feats([{k: X[k][i] for k in X} for i in range(len(X["C"]))])
            d = ((Zq[:, None, :] - Zt[None, :, :]) ** 2).sum(-1)
            return yt[np.argsort(d, 1)[:, :5]].mean(1) >= 0.5

        base = {"majority_visible": lambda X: np.full(len(X["C"]), vis_rate >= 0.5), "knn5_visible": knn}
        hres = broker.adjudicate(store, final_id, COMMITMENT, baselines=base)
        _dump(out, "G5_holdout", hres)
        g5 = hres["law_ba"] >= 0.80 and hres["law_ba"] >= hres["baselines"]["knn5_visible"]["ba"] - 0.05
        report["gates"]["G5"] = {k: v for k, v in hres.items() if k != "rows"}
        report["gates"]["G5"]["verdict"] = "PASS" if g5 else "FAIL"
        ires = broker.intervene(store, final_id, COMMITMENT, hres)
        _dump(out, "G6_intervention", ires)
        report["gates"]["G6"] = {k: v for k, v in ires.items() if k != "rows"}
        report["gates"]["G6"]["verdict"] = ires["G6"]
        report["final_law"] = {"law_id": final_id, "freeze_hash": fh, "law": final["law"]["law"], "cmap": final["cmap"]}
    else:
        for g in ("G5", "G6"):
            report["gates"][g] = {"verdict": "NOT REACHED" if not quick else "SKIPPED (quick)"}
    report["graph"] = {**store.counts(), "edge_kinds": store.edge_counts()}
    from prometheus.cosmos.quotient import quotient
    report["quotient"] = quotient(ch.log + ctl.log, ch.edges + ctl.edges)
    _dump(out, "quotient", report["quotient"])
    report["n_queries"] = ch.n_queries
    report["t_total_s"] = round(time.time() - t0, 1)
    report["laws"] = [{"law_id": l["law_id"], "version": l["version"], "parent": l["parent"],
                       "law": l["body"]["law"]["law"], "cmap": l["body"]["cmap"], "freeze_hash": l["freeze_hash"],
                       "events": [e["status"] for e in l["events"]]} for l in store.laws()]
    store.receipts.append("campaign_end", {"gates": {k: v["verdict"] for k, v in report["gates"].items()}})
    store.commit()
    report["receipt_chain_ok"] = store.receipts.verify() is None
    _dump(out, "REPORT", report)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args(argv)
    rep = run(Path(a.out), quick=a.quick)
    print(json.dumps({k: v["verdict"] for k, v in rep["gates"].items()}, indent=1))


if __name__ == "__main__":
    main()
