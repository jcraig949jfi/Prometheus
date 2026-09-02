"""V1-A analysis: agreement, disagreement matrix, forced-fit rates, and the
G3 non-circularity retrieval test — all per PREREGISTRATION_V1.md section A.

Mnemosyne's blind labels are loaded ONLY for the non-gating M-A3 comparison,
and this script verifies their sealed hash first (they were committed as a
hash before any annotator launched).
"""
import hashlib
import itertools
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

ANN = HERE / "gold" / "annotations"


def load(fn, key="mechanism"):
    out = {}
    for line in (ANN / fn).open(encoding="utf-8"):
        r = json.loads(line)
        out[r["cand_id"]] = r
    return out


def mechset(r):
    return {m for m in (r.get("mechanism") or [])}


def overlap(a, b):
    return bool(a & b)


def main():
    corpus = {}
    for line in (HERE / "gold" / "holdout_corpus_v1.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        corpus[r["cand_id"]] = r
    ids = sorted(corpus)

    blind_blob = (HERE / "derived" / "v1a_mnemosyne_blind.json").read_text(encoding="utf-8")
    sealed = (HERE / "gold" / "v1a_mnemosyne_blind_sha256.txt").read_text().strip()
    assert hashlib.sha256(blind_blob.encode()).hexdigest() == sealed, \
        "blind-annotation hash mismatch — audit trail broken"
    blind = json.loads(blind_blob)

    A = {n: load(f"ann{n}.jsonl") for n in ("A1", "A2", "B1", "B2")}

    R = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "n_findings": len(ids),
         "blind_hash_verified": True}

    # ---------------- M-A1 pairwise any-overlap (all 6 A/B pairs)
    pair_scores = {}
    for x, y in itertools.combinations(A, 2):
        s = np.mean([overlap(mechset(A[x][i]), mechset(A[y][i])) for i in ids])
        pair_scores[f"{x}-{y}"] = round(float(s), 3)
    R["M_A1_pairwise_any_overlap"] = pair_scores
    R["M_A1_mean"] = round(float(np.mean(list(pair_scores.values()))), 3)
    thr = ("PASS" if R["M_A1_mean"] >= 0.50 else
           "MARGINAL" if R["M_A1_mean"] >= 0.30 else "FAIL")
    R["M_A1_verdict"] = thr

    # ---------------- M-A2 modal exact agreement (first-listed mechanism)
    modal = []
    for i in ids:
        firsts = [(A[n][i].get("mechanism") or ["-"])[0] for n in A]
        c = Counter(firsts).most_common(1)[0][1]
        modal.append(c / len(A))
    R["M_A2_modal_top1_share_mean"] = round(float(np.mean(modal)), 3)

    # ---------------- M-A3 vs Mnemosyne blind (non-gating)
    m3 = {n: round(float(np.mean([overlap(mechset(A[n][i]),
                                          set(blind[i]["mechanism"]))
                                  for i in ids])), 3) for n in A}
    R["M_A3_vs_mnemosyne_blind"] = m3

    # ---------------- M-A4 NONE / NEW rates
    R["M_A4"] = {}
    for n in A:
        none = sum(1 for i in ids if "NONE_OF_THE_ABOVE" in mechset(A[n][i]))
        new = sum(1 for i in ids
                  if any(str(m).startswith("NEW:") for m in mechset(A[n][i])))
        R["M_A4"][n] = {"none_rate": round(none / len(ids), 3),
                        "new_rate": round(new / len(ids), 3)}
    news = Counter()
    for n in ("B1", "B2"):
        for i in ids:
            for m in mechset(A[n][i]):
                if str(m).startswith("NEW:"):
                    news[m] += 1
    R["proposed_new_mechanisms"] = dict(news)

    # ---------------- substrate / failure agreement
    for dim in ("substrate_class", "failure_class"):
        scores = {}
        for x, y in itertools.combinations(A, 2):
            vals = [(A[x][i].get(dim), A[y][i].get(dim)) for i in ids]
            vals = [(a, b) for a, b in vals if a and b]
            scores[f"{x}-{y}"] = round(float(np.mean([a == b for a, b in vals])), 3) if vals else None
        R[f"{dim}_exact_agreement"] = scores

    # ---------------- disagreement matrix (mechanism-level)
    dis = Counter()
    for x, y in itertools.combinations(A, 2):
        for i in ids:
            sx, sy = mechset(A[x][i]), mechset(A[y][i])
            if not overlap(sx, sy):
                for a in sorted(sx):
                    for b in sorted(sy):
                        dis[tuple(sorted((str(a), str(b))))] += 1
    R["disagreement_matrix_top"] = [
        {"pair": list(k), "count": v} for k, v in dis.most_common(15)]

    # ---------------- G3 non-circularity retrieval
    # Gold pairs: cross-agent pairs where A1 AND A2 both assign an
    # intersecting mechanism to the two findings.
    gold_pairs = []
    for i, j in itertools.combinations(ids, 2):
        if corpus[i]["agent"] == corpus[j]["agent"]:
            continue
        a1 = overlap(mechset(A["A1"][i]), mechset(A["A1"][j]))
        a2 = overlap(mechset(A["A2"][i]), mechset(A["A2"][j]))
        if a1 and a2:
            gold_pairs.append((i, j))
    R["G3_gold_pairs_n"] = len(gold_pairs)
    R["G3_gold_pairs"] = [list(p) for p in gold_pairs]

    fallback = False
    if len(gold_pairs) < 4:
        fallback = True
        gold_pairs = []
        for i, j in itertools.combinations(ids, 2):
            if corpus[i]["agent"] == corpus[j]["agent"]:
                continue
            votes = sum(overlap(mechset(A[n][i]), mechset(A[n][j])) for n in A)
            if votes >= 2:
                gold_pairs.append((i, j))
        R["G3_fallback_pooled"] = True
        R["G3_gold_pairs_n_fallback"] = len(gold_pairs)
    R["G3_fallback_used"] = fallback

    # Prediction labels: B1 and B2 (disjoint from pair definition when no
    # fallback; disclosed as weaker under fallback). Rank corpus by label
    # overlap; ties broken by seeded shuffle (seed 3).
    docs = {i: corpus[i]["claim_text"] + " " + corpus[i]["source_quote"]
            for i in ids}
    toks = {i: re.findall(r"[a-z0-9]+", docs[i].lower()) for i in ids}
    from rank_bm25 import BM25Okapi
    bm = BM25Okapi([toks[i] for i in ids])
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer("all-MiniLM-L6-v2")
    emb = st.encode([docs[i] for i in ids], normalize_embeddings=True)
    idx = {i: k for k, i in enumerate(ids)}

    def rank_of(order, tgt):
        return order.index(tgt) + 1 if tgt in order else None

    def eval_method(rank_fn):
        rr, h10 = [], 0
        for src, dst in gold_pairs:
            order = rank_fn(src)
            r = rank_of(order, dst)
            rr.append(1.0 / r if r else 0.0)
            h10 += 1 if (r and r <= 10) else 0
        return {"mrr": round(float(np.mean(rr)), 3),
                "hits@10": round(h10 / len(gold_pairs), 3)} if gold_pairs else None

    rng = np.random.default_rng(3)

    def label_rank(annname):
        def fn(src):
            scores = []
            for j in ids:
                if j == src:
                    continue
                scores.append((len(mechset(A[annname][src]) &
                                   mechset(A[annname][j])),
                               rng.random(), j))
            scores.sort(key=lambda t: (-t[0], t[1]))
            return [j for _, _, j in scores]
        return fn

    def bm_rank(src):
        s = bm.get_scores(toks[src])
        order = np.argsort(s)[::-1]
        return [ids[k] for k in order if ids[k] != src]

    def emb_rank(src):
        s = emb @ emb[idx[src]]
        order = np.argsort(s)[::-1]
        return [ids[k] for k in order if ids[k] != src]

    R["G3_retrieval"] = {
        "labels_B1": eval_method(label_rank("B1")),
        "labels_B2": eval_method(label_rank("B2")),
        "bm25": eval_method(bm_rank),
        "embedding": eval_method(emb_rank),
    }
    if gold_pairs:
        lab = np.mean([R["G3_retrieval"]["labels_B1"]["mrr"],
                       R["G3_retrieval"]["labels_B2"]["mrr"]])
        base = max(R["G3_retrieval"]["bm25"]["mrr"],
                   R["G3_retrieval"]["embedding"]["mrr"])
        h10 = np.mean([R["G3_retrieval"]["labels_B1"]["hits@10"],
                       R["G3_retrieval"]["labels_B2"]["hits@10"]])
        R["G3_verdict"] = ("PASS" if lab >= 2 * base and h10 >= 0.6
                           else "FAIL")
        R["G3_detail"] = {"label_mrr_mean": round(float(lab), 3),
                          "best_baseline_mrr": round(float(base), 3),
                          "label_hits10_mean": round(float(h10), 3)}
    else:
        R["G3_verdict"] = "FAIL_NO_PAIRS"

    (HERE / "benchmarks" / "ontology_v1.json").write_text(
        json.dumps(R, indent=1), encoding="utf-8")
    print(json.dumps(R, indent=1))


if __name__ == "__main__":
    main()
