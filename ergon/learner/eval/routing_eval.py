"""Routing eval — does mined-failure residue carry navigable routing signal?

Preregistered design: roles/Ergon/ROUTING_EVAL_2026-06-09.md

Two evals on the Hephaestus failure-mining solve matrix (80 scraps x probe-slots):
  Eval A  cold-start feature routing  : route a held-out scrap to probes by its FIELDS,
                                        zero of its own solves revealed. FEATURE vs POP.
  Eval B  warm-start collaborative    : reveal half a scrap's solves, predict the rest. COLLAB vs POP.

Instrument validation (positive / negative / floor controls) runs first; if it fails,
the real-data verdict is not trustworthy and the script says so.

No new resources, no network, no probe-identity reconstruction. Deterministic (seeded).
"""
from __future__ import annotations
import json, os, sys
import numpy as np

HEPH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "agents", "hephaestus")
MINING = os.path.join(HEPH, "failure_mining_results.json")
SCRAP_DIR = os.path.join(HEPH, "scrap")

SEEDS = [0, 1, 2, 3, 4]


# ----------------------------------------------------------------------------- data
def load_data():
    recs = json.load(open(MINING))
    n = len(recs)
    P = max(p for r in recs for p in r["wrong_probes_solved"]) + 1
    M = np.zeros((n, P), dtype=int)
    for i, r in enumerate(recs):
        for p in r["wrong_probes_solved"]:
            M[i, p] = 1
    active = np.where(M.sum(0) > 0)[0]              # probes solved by >=1 scrap
    # field features (join via sibling scrap/*.json); None if missing
    fields = []
    for r in recs:
        fn = os.path.join(SCRAP_DIR, r["file"].replace(".py", ".json"))
        if os.path.exists(fn):
            j = json.load(open(fn))
            fields.append(frozenset(j.get("concept_fields", [])) or None)
        else:
            fields.append(None)
    return M, active, fields, recs


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    u = len(a | b)
    return len(a & b) / u if u else 0.0


def set_jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    u = len(a | b)
    return len(a & b) / u if u else 0.0


# --------------------------------------------------------------------------- metric
def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    """ROC-AUC via Mann-Whitney, ties = 0.5. labels in {0,1}. NaN if degenerate."""
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    # rank-sum
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    alls = np.concatenate([pos, neg])
    ranks = np.empty(len(alls))
    sorted_vals = alls[order]
    # average ranks for ties
    i = 0
    r = np.empty(len(alls))
    while i < len(alls):
        j = i
        while j + 1 < len(alls) and sorted_vals[j + 1] == sorted_vals[i]:
            j += 1
        r[i:j + 1] = (i + j) / 2.0 + 1
        i = j + 1
    ranks[order] = r
    rank_pos = ranks[:len(pos)].sum()
    return (rank_pos - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg))


def recall_at_k(scores, labels, k=10):
    idx = np.argsort(-scores, kind="mergesort")[:k]
    return labels[idx].sum() / max(1, labels.sum())


# ------------------------------------------------------------------ Eval A: cold-start
def eval_A(M, active, fields):
    """For each held-out scrap with fields, route to probes by field-Jaccard neighbour vote.
    FEATURE = field-weighted; POP = field-blind popularity. LOO, no query solves revealed."""
    idx = [i for i, f in enumerate(fields) if f]          # scraps with field features
    Ma = M[:, active]
    out = {"feature": [], "pop": [], "feature_ap": [], "pop_ap": [], "feat_r10": [], "pop_r10": []}
    for q in idx:
        labels = Ma[q]
        if labels.sum() == 0 or labels.sum() == len(active):
            continue
        train = [s for s in idx if s != q]
        sims = np.array([jaccard(fields[q], fields[s]) for s in train])
        Mtr = Ma[train]
        feat = sims @ Mtr                                  # field-weighted vote
        pop = Mtr.sum(0).astype(float)                     # field-blind popularity
        out["feature"].append(auc(feat, labels))
        out["pop"].append(auc(pop, labels))
        out["feat_r10"].append(recall_at_k(feat, labels))
        out["pop_r10"].append(recall_at_k(pop, labels))
    return {k: np.array(v, float) for k, v in out.items()}


# ---------------------------------------------------------------- Eval B: warm-start
def eval_B(M, active, seed, exclude_top=0):
    """Reveal half of each scrap's solved set; predict the rest via collaborative similarity.
    COLLAB neighbour sim = Jaccard on revealed probes; POP = popularity. Candidates = held-out
    positives + all never-solved-by-q active probes.
    exclude_top>0: drop the N most globally-popular probes from the candidate pool (tail-only
    robustness check — does the structure survive where routing actually matters?)."""
    rng = np.random.RandomState(seed)
    Ma = M[:, active]
    n = Ma.shape[0]
    full = [set(np.where(Ma[i])[0]) for i in range(n)]
    pop_rank = np.argsort(-Ma.sum(0))                      # most popular active-probe indices
    banned = set(pop_rank[:exclude_top].tolist())
    collab, pop = [], []
    for q in range(n):
        solved = [p for p in full[q] if p not in banned]
        if len(solved) < 4:
            continue
        rng.shuffle(solved)
        half = len(solved) // 2
        revealed = set(solved[:half])
        held = set(solved[half:])
        cand = list(held) + [p for p in range(len(active))
                             if p not in full[q] and p not in banned]
        labels = np.array([1 if c in held else 0 for c in cand])
        # collaborative: neighbours by revealed-set Jaccard (full solves of others)
        sims = np.array([set_jaccard(revealed, full[s]) for s in range(n) if s != q])
        others = np.array([Ma[s] for s in range(n) if s != q])
        cscore = (sims @ others)[cand]
        pscore = others.sum(0).astype(float)[cand]
        collab.append(auc(cscore, labels))
        pop.append(auc(pscore, labels))
    return np.array(collab, float), np.array(pop, float)


# ------------------------------------------------------------------- controls
def control_positive(active, fields):
    """Synthetic: field DETERMINES solves. Each distinct field -> a fixed probe block.
    FEATURE must crush POP (AUC ->~1)."""
    idx = [i for i, f in enumerate(fields) if f]
    fset = sorted({x for i in idx for x in fields[i]})
    fmap = {f: k for k, f in enumerate(fset)}
    P = len(fset)
    M = np.zeros((len(fields), P), dtype=int)
    for i in idx:
        for f in fields[i]:
            M[i, fmap[f]] = 1                  # solves = its own fields' blocks
    return eval_A(M, np.arange(P), fields)


def control_negative(M, active, fields, seed):
    """Real solve matrix, fields SHUFFLED across scraps. FEATURE must ~= POP."""
    rng = np.random.RandomState(seed)
    idx = [i for i, f in enumerate(fields) if f]
    perm = list(idx)
    rng.shuffle(perm)
    shuffled = list(fields)
    for a, b in zip(idx, perm):
        shuffled[a] = fields[b]
    return eval_A(M, active, shuffled)


# ------------------------------------------------------------------- significance
def paired_bootstrap_p(delta, seed=0, n=10000):
    """Two-sided bootstrap p that mean(delta) <= 0 (H1: feature > pop)."""
    delta = delta[~np.isnan(delta)]
    if len(delta) == 0:
        return np.nan, np.nan
    rng = np.random.RandomState(seed)
    means = np.array([rng.choice(delta, len(delta), replace=True).mean() for _ in range(n)])
    p_le0 = (means <= 0).mean()
    return delta.mean(), p_le0


def fmt(a):
    a = a[~np.isnan(a)]
    return f"{a.mean():.3f}±{a.std():.3f} (n={len(a)})"


def main():
    M, active, fields, recs = load_data()
    print(f"# data: {M.shape[0]} scraps x {len(active)} active probes "
          f"({M.shape[1]} slots); fields on {sum(bool(f) for f in fields)}/{len(fields)}\n")

    print("## Instrument validation")
    posc = control_positive(active, fields)
    print(f"  positive control (field=>solves): FEATURE AUC {fmt(posc['feature'])} | "
          f"POP {fmt(posc['pop'])}  [expect FEATURE >> POP]")
    negs_f, negs_p = [], []
    for s in SEEDS:
        nc = control_negative(M, active, fields, s)
        negs_f.append(nc["feature"]); negs_p.append(nc["pop"])
    nf = np.concatenate(negs_f); npp = np.concatenate(negs_p)
    d_neg, p_neg = paired_bootstrap_p(nf - npp)
    print(f"  negative control (fields shuffled): FEATURE {fmt(nf)} | POP {fmt(npp)} | "
          f"ΔAUC={d_neg:+.3f} (expect ~0)\n")

    print("## Eval A — cold-start feature routing (H_A: route by fields, no solves revealed)")
    a = eval_A(M, active, fields)
    dA = a["feature"] - a["pop"]
    mA, pA = paired_bootstrap_p(dA)
    print(f"  FEATURE AUC {fmt(a['feature'])} | POP AUC {fmt(a['pop'])}")
    print(f"  Recall@10  FEATURE {fmt(a['feat_r10'])} | POP {fmt(a['pop_r10'])}")
    print(f"  ΔAUC (FEATURE−POP) = {mA:+.4f} | bootstrap P(Δ≤0) = {pA:.4f}")
    print(f"  -> H_A {'SUPPORTED' if (mA > 0 and pA < 0.05) else 'NULL'}\n")

    print("## Eval B — warm-start collaborative completion (H_B: any navigable structure?)")
    bc, bp = [], []
    for s in SEEDS:
        c, p = eval_B(M, active, s)
        bc.append(c); bp.append(p)
    bc = np.concatenate(bc); bp = np.concatenate(bp)
    dB = bc - bp
    mB, pB = paired_bootstrap_p(dB)
    print(f"  COLLAB AUC {fmt(bc)} | POP AUC {fmt(bp)}")
    print(f"  ΔAUC (COLLAB−POP) = {mB:+.4f} | bootstrap P(Δ≤0) = {pB:.4f}")
    print(f"  -> H_B {'SUPPORTED' if (mB > 0 and pB < 0.05) else 'NULL'}")

    print("\n## Eval B (tail-only) — adversarial check: drop top-8 popular probes from candidates")
    tc, tp = [], []
    for s in SEEDS:
        c, p = eval_B(M, active, s, exclude_top=8)
        tc.append(c); tp.append(p)
    tc = np.concatenate(tc); tp = np.concatenate(tp)
    mT, pT = paired_bootstrap_p(tc - tp)
    print(f"  COLLAB AUC {fmt(tc)} | POP AUC {fmt(tp)}")
    print(f"  ΔAUC (COLLAB−POP) = {mT:+.4f} | bootstrap P(Δ≤0) = {pT:.4f}")
    print(f"  -> tail structure {'SURVIVES' if (mT > 0 and pT < 0.05) else 'VANISHES (head-driven)'}")


if __name__ == "__main__":
    main()
