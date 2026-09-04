"""V0 benchmark suite (charter §17, §18, §21).

Tasks:
  T1 known-item retrieval (G3)
  T2 cross-vocabulary related-finding retrieval on the 10 HELD-OUT curated
     pairs — bm25 / embedding / graph / tensor-CP / metadata-exact
  T3 counterevidence surfacing (G5, deterministic)
  T5 held-out missing-cell ranking: CP / Tucker / TT vs random + marginal
  T6 provenance reconstruction over every claim (G1, deterministic)
  Stability (18A), Recovery (18B), Contamination (G8), Rebuild (G17)

Leakage disclosure (18F): tensor and metadata-exact consume the curated
mechanism/substrate labels; bm25/embedding see source text only. The tensor's
margin over metadata-exact — not over text — is the latent-structure claim.
The held-out pairs were never ingested as relations before this run.
"""
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from ew import compiler, db, store  # noqa: E402
from ew.search import SearchIndex  # noqa: E402

OUT = HERE / "benchmarks" / "results_v0.json"
R = {"generated": time.strftime("%Y-%m-%d %H:%M:%S")}


def rank_of(results, target, key="claim_id"):
    for i, r in enumerate(results):
        if r[key] == target:
            return i + 1
    return None


def mrr(ranks):
    return float(np.mean([1.0 / r if r else 0.0 for r in ranks]))


def hits(ranks, k):
    return float(np.mean([1.0 if (r and r <= k) else 0.0 for r in ranks]))


def main():
    conn = db.connect()
    ix = SearchIndex(conn)
    id_map = json.loads((HERE / "gold" / "id_map.json").read_text())
    holdout = json.loads((HERE / "gold" / "benchmark_holdout.json").read_text())
    curation = json.loads((HERE / "gold" / "curation_v1.json").read_text(encoding="utf-8"))
    n_claims = len(ix.ids)

    # -------------------------------------------------- T1 known-item
    ranks = []
    for d in ix.docs:
        res = ix.lexical(d["title"], k=10)
        ranks.append(rank_of(res, d["claim_id"]))
    R["T1_known_item"] = {"n": len(ranks), "bm25_mrr": mrr(ranks),
                          "bm25_hits@1": hits(ranks, 1)}

    # -------------------------------- T2 cross-vocabulary holdout pairs
    snap = compiler.compile(conn, "evidence_v1", {})
    cp = compiler.factor(conn, snap["snapshot_id"], "cp", rank=6, seed=0)
    cp["view_name"] = "evidence_v1"

    # metadata-exact baseline: claims sharing >=1 canonical mechanism term
    mech_of = {}
    for cand, asg in curation["assignments"].items():
        cid = id_map[cand]["claim_id"]
        mech_of[cid] = set(asg.get("mechanism", []))

    def metadata_related(cid, k=10):
        mine = mech_of.get(cid, set())
        out = []
        for other, ms in mech_of.items():
            if other == cid:
                continue
            inter = len(mine & ms)
            if inter:
                out.append({"claim_id": other, "score": float(inter)})
        random.Random(0).shuffle(out)  # break ties without id-order bias
        out.sort(key=lambda x: -x["score"])
        return out[:k]

    methods = {
        "bm25": lambda cid: ix.lexical(
            next(d["text"] for d in ix.docs if d["claim_id"] == cid), k=n_claims),
        "embedding": lambda cid: ix.semantic_related(cid, k=n_claims),
        "graph_2hop": lambda cid: sorted(
            ix.graph_neighbors(cid, hops=2)[0], key=lambda x: -x["score"]),
        "tensor_cp": lambda cid: ix.tensor_related(cid, cp, k=n_claims),
        "metadata_exact": lambda cid: metadata_related(cid, k=n_claims),
    }
    t2 = {}
    per_pair = []
    for m, fn in methods.items():
        ranks = []
        for pair in holdout:
            res = [r for r in fn(pair["src_claim"]) if r["claim_id"] != pair["src_claim"]]
            rk = rank_of(res, pair["dst_claim"])
            ranks.append(rk)
            if m == "tensor_cp":
                per_pair.append({"pair": f"{pair['src']}->{pair['dst']}",
                                 "type": pair["type"], "tensor_rank": rk})
        t2[m] = {"mrr": mrr(ranks), "hits@5": hits(ranks, 5),
                 "hits@10": hits(ranks, 10),
                 "ranks": [r if r else None for r in ranks]}
    R["T2_cross_vocabulary_holdout"] = {
        "n_pairs": len(holdout), "corpus_size": n_claims, "methods": t2,
        "tensor_per_pair": per_pair,
        "leakage_note": "tensor/metadata use curated labels; text methods do not"}

    # ------------------------------------------- T3 counterevidence (G5)
    checks = []
    a1 = id_map["A-001"]["claim_id"]
    ce = store.counterevidence(conn, a1)
    checks.append({"claim": "A-001", "expect": "A-002 QUALIFIES",
                   "found": any(r["src_id"] == id_map["A-002"]["claim_id"]
                                for r in ce["counter_relations"])})
    c23 = id_map["C-023"]["claim_id"]
    ce2 = store.counterevidence(conn, c23)
    checks.append({"claim": "C-023", "expect": "C-024 CORRECTS visible via relations",
                   "found": any(r["src_id"] == id_map["C-024"]["claim_id"]
                                for r in store.get_claim(conn, c23)["relations"])})
    R["T3_counterevidence"] = {"checks": checks,
                               "pass": all(c["found"] for c in checks)}

    # ------------------------- T5 held-out missing-cell (charter §21)
    snap_full, modes, dicts, coo, vals, eids = compiler.load_snapshot(
        conn, snap["snapshot_id"])
    T = compiler._dense(modes, dicts, coo, vals)
    obs = np.argwhere(T > 0)
    rng = np.random.default_rng(42)
    picks = rng.choice(len(obs), size=min(10, len(obs)), replace=False)
    import tensorly as tl
    from tensorly.decomposition import parafac, tucker, tensor_train
    t5 = {m: [] for m in ("cp", "tucker", "tt", "random", "marginal")}
    for pi in picks:
        cell = tuple(obs[pi])
        T2 = T.copy()
        T2[cell] = 0.0
        unobs_mask = (T2 == 0)
        n_unobs = int(unobs_mask.sum())
        # marginal baseline
        margs = [T2.sum(axis=tuple(j for j in range(T2.ndim) if j != i))
                 for i in range(T2.ndim)]
        M = np.ones_like(T2)
        for i, mg in enumerate(margs):
            shape = [1] * T2.ndim
            shape[i] = -1
            M = M * mg.reshape(shape)
        for method in ("cp", "tucker", "tt"):
            tt_ = tl.tensor(T2)
            if method == "cp":
                rec = tl.cp_to_tensor(parafac(tt_, rank=6, init="random",
                                              random_state=0, n_iter_max=300))
            elif method == "tucker":
                rk = [min(4, s) for s in T2.shape]
                rec = tl.tucker_to_tensor(tucker(tt_, rank=rk, init="random",
                                                 random_state=0, n_iter_max=300))
            else:
                rk = [1] + [min(6, 8)] * (T2.ndim - 1) + [1]
                rec = tl.tt_to_tensor(tensor_train(tt_, rank=rk))
            rec = np.asarray(rec)
            score = rec[cell]
            better = int((rec[unobs_mask] > score).sum())
            t5[method].append(1.0 - better / n_unobs)  # percentile (1=top)
        score_m = M[cell]
        t5["marginal"].append(1.0 - int((M[unobs_mask] > score_m).sum()) / n_unobs)
        t5["random"].append(0.5)
    R["T5_missing_cell"] = {
        "held_out_cells": len(picks),
        "mean_percentile": {m: float(np.mean(v)) for m, v in t5.items()},
        "note": "percentile of the removed observed cell among unobserved cells; 1.0 = ranked top"}

    # -------------------------------- T6 provenance reconstruction (G1)
    missing = []
    for cand, m in id_map.items():
        chain = store.provenance_chain(conn, m["evidence_id"])
        layers = [c["layer"] for c in chain]
        if "ew.source_packets" not in layers:
            missing.append(cand)
    R["T6_provenance"] = {"n": len(id_map), "failures": missing,
                          "pass": not missing}

    # ------------------------------------------ stability (18A) + rank
    base = compiler.factor(conn, snap["snapshot_id"], "cp", rank=6, seed=0,
                           persist=False)
    from scipy.optimize import linear_sum_assignment
    sims = []
    for seed in (1, 2, 3, 4):
        alt = compiler.factor(conn, snap["snapshot_id"], "cp", rank=6,
                              seed=seed, persist=False)
        A = np.concatenate([np.array(f) for f in base["_payload"]["factors"]])
        B = np.concatenate([np.array(f) for f in alt["_payload"]["factors"]])
        An = A / (np.linalg.norm(A, axis=0, keepdims=True) + 1e-12)
        Bn = B / (np.linalg.norm(B, axis=0, keepdims=True) + 1e-12)
        C = An.T @ Bn
        ri, ci = linear_sum_assignment(-np.abs(C))
        sims.append(float(np.abs(C[ri, ci]).mean()))
    errs = {r: compiler.factor(conn, snap["snapshot_id"], "cp", rank=r,
                               seed=0, persist=False)["relative_error"]
            for r in (2, 4, 6, 8)}
    R["stability_18A"] = {"cp_seed_factor_match_cosine": sims,
                          "mean": float(np.mean(sims)),
                          "cp_relative_error_by_rank": errs}

    # ------------------------------------------------ recovery (18B)
    # Factorize with the mechanism mode marginalized away; cluster evidence
    # by remaining-mode CP cell vectors; compare clusters to mechanism labels.
    keep = [m for m in modes if m != "mechanism"]
    con = compiler.contract(conn, snap["snapshot_id"], ["mechanism"], keep)
    # build per-evidence vector from cp on the marginalized tensor
    idx_maps = {m: {v: i for i, v in enumerate(dicts[m])} for m in modes}
    shape = [len(dicts[m]) for m in keep]
    Tm = np.zeros(shape)
    for c in con["cells"]:
        Tm[tuple(idx_maps[m][c["cell"][m]] for m in keep)] = c["value"]
    res = parafac(tl.tensor(Tm), rank=6, init="random", random_state=0,
                  n_iter_max=300)
    facs = [np.asarray(f) for f in res.factors]
    ev_vec, ev_label = [], []
    with db.dict_cur(conn) as cur:
        cur.execute(
            "SELECT c.evidence_id, c.coords, m.term_id FROM ew.coordinates c "
            "JOIN ew.evidence_terms t ON t.evidence_id=c.evidence_id AND "
            "t.dimension='mechanism' JOIN ew.term_mappings m ON "
            "m.dimension='mechanism' AND m.source_term=t.source_term "
            "WHERE c.view_name='evidence_v1'")
        for row in cur.fetchall():
            co = row["coords"]
            v = np.ones(6)
            for i, m in enumerate(keep):
                v = v * facs[i][idx_maps[m][co[m]]]
            ev_vec.append(v)
            ev_label.append(row["term_id"])
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score
    X = np.array(ev_vec)
    labs = KMeans(n_clusters=8, n_init=10, random_state=0).fit_predict(X)
    ari = adjusted_rand_score(ev_label, labs)
    R["recovery_18B"] = {
        "n_evidence_obs": len(ev_label), "kmeans_k": 8,
        "ari_vs_mechanism_labels": float(ari),
        "note": "mechanism mode marginalized before factorization; labels never shown to the model"}

    # -------------------------------------- contamination (G8) + rebuild (G17)
    try:
        dp = store.register_packet(conn, "evidence_wiki/derived/contam_test.json",
                                   "derived_view", "Mnemosyne", "M1")
        store.submit_evidence(conn, dp, "quote", "STATISTICAL_RESULT",
                              "Mnemosyne", "M1")
        contam = False
    except store.RejectedWrite:
        contam = True
    snap2 = compiler.compile(conn, "evidence_v1", {})
    f1 = compiler.factor(conn, snap["snapshot_id"], "cp", rank=6, seed=0)
    art_path = Path(json.loads(json.dumps(str(HERE / "derived" /
                    f"{f1['artifact_id']}.cp.json"))))
    if art_path.exists():
        art_path.unlink()
    f2 = compiler.factor(conn, snap["snapshot_id"], "cp", rank=6, seed=0)
    R["contamination_G8"] = {"derived_view_rejected_as_evidence": contam}
    R["rebuild_G17"] = {
        "snapshot_sha_stable": snap2["content_sha256"] == snap["content_sha256"],
        "factor_repro_sha_stable_after_delete": f1["repro_sha256"] == f2["repro_sha256"]}

    OUT.write_text(json.dumps(R, indent=1), encoding="utf-8")
    slim = json.loads(json.dumps(R))
    slim["T2_cross_vocabulary_holdout"].pop("tensor_per_pair")
    print(json.dumps(slim, indent=1))
    conn.close()


if __name__ == "__main__":
    main()
