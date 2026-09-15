"""Trap table, matched siblings, Q1 exact lookahead classification, observability horizon, residual set."""
from __future__ import annotations
import collections, csv, gzip, hashlib, io
import numpy as np
from ..universe.directed_rewriting import index_word
from .observation import Observer, SIBLING_MATCH_FEATURES, LOOSE_MATCH_FEATURES

UNREACH = -1


def forward_region(obs: Observer, s: int):
    """(region size, BFS eccentricity) of the forward-reachable set from s."""
    fi, fx = obs.fi, obs.fx
    seen = {s}; frontier = [s]; depth = 0
    while frontier:
        nxt = []
        for v in frontier:
            for u in fx[fi[v]:fi[v + 1]]:
                if u not in seen:
                    seen.add(u); nxt.append(u)
        if not nxt:
            break
        frontier = nxt; depth += 1
    return len(seen), depth


def trap_table(U: dict, obs: Observer, height: np.ndarray) -> dict:
    """All (edge, target) traps with source distance, successor features, region, eccentricity (graph) and height (tree)."""
    src, dst, rid, pos, D, L = U["src"], U["dst"], U["rule"], U["pos"], U["D"], U["L"]
    fam = obs.rule_family
    rows = {k: [] for k in ("edge", "target_j", "src", "dst", "rule", "family", "pos", "D_src")}
    for j in range(len(U["targets"])):
        Ds, Dd = D[src, j], D[dst, j]
        idx = np.nonzero((Ds >= 0) & (Dd < 0))[0]
        rows["edge"].append(idx); rows["target_j"].append(np.full(len(idx), j)); rows["src"].append(src[idx]); rows["dst"].append(dst[idx])
        rows["rule"].append(rid[idx]); rows["family"].append(fam[rid[idx]]); rows["pos"].append(pos[idx]); rows["D_src"].append(Ds[idx])
    T = {k: np.concatenate(v) if v else np.zeros(0, dtype=np.int64) for k, v in rows.items()}
    n = len(T["edge"])
    ecc_cache = {}; reg_cache = {}
    for v in np.unique(T["dst"]).tolist():
        reg_cache[v], ecc_cache[v] = forward_region(obs, v)
    T["region"] = np.array([reg_cache[v] for v in T["dst"].tolist()], dtype=np.int64)
    T["ecc"] = np.array([ecc_cache[v] for v in T["dst"].tolist()], dtype=np.int64)
    T["height"] = height[T["dst"]].astype(np.int64)
    T["succ_len"] = obs.LEN[T["dst"]]; T["succ_outdeg"] = obs.outdeg[T["dst"]]
    T["succ_n_cancel"] = obs.n_cancel[T["dst"]]; T["succ_n_relator"] = obs.n_relator[T["dst"]]
    T["visible"] = (T["succ_outdeg"] == 0)
    T["n"] = n
    return T


def sibling_match(U: dict, obs: Observer, T: dict) -> dict:
    """For every trap (edge, target): non-trap sibling actions from the same source; exact match on the six frozen
    features and loose match on three. H_pair = min(ecc(trap successor), D(best good successor)) (graph semantics);
    H_pair_tree uses height instead of ecc."""
    src, dst, rid, D, L = U["src"], U["dst"], U["rule"], U["D"], U["L"]
    fam = obs.rule_family
    # edges grouped by source
    order = np.argsort(src, kind="stable"); s_sorted = src[order]
    starts = np.searchsorted(s_sorted, np.arange(U["NS"] + 1))
    targets = U["targets"]
    n = T["n"]
    exact = np.zeros(n, dtype=bool); loose = np.zeros(n, dtype=bool); has_good = np.zeros(n, dtype=bool)
    good_edge = np.full(n, -1, dtype=np.int64); good_D = np.full(n, -1, dtype=np.int64); n_exact = np.zeros(n, dtype=np.int64)
    for i in range(n):
        s = int(T["src"][i]); j = int(T["target_j"][i]); t = targets[j]; e = int(T["edge"][i])
        sib = order[starts[s]:starts[s + 1]]
        sib = sib[sib != e]
        if len(sib) == 0:
            continue
        good = sib[D[dst[sib], j] >= 0]
        if len(good) == 0:
            continue
        has_good[i] = True
        # best good successor by D (for H_pair), independent of matching
        gd = D[dst[good], j].astype(np.int64)
        k = int(np.argmin(gd)); good_edge[i] = good[k]; good_D[i] = gd[k]
        fs = (fam[rid[e]], int(obs.LEN[dst[e]]), int(obs.outdeg[dst[e]]), dst[e] == t, int(obs.n_cancel[dst[e]]), int(obs.n_relator[dst[e]]))
        cnt = 0; loose_hit = False; best_matched = -1; best_md = 10**9
        for g in good.tolist():
            fg = (fam[rid[g]], int(obs.LEN[dst[g]]), int(obs.outdeg[dst[g]]), dst[g] == t, int(obs.n_cancel[dst[g]]), int(obs.n_relator[dst[g]]))
            if fg[:3] == fs[:3]:
                loose_hit = True
            if fg == fs:
                cnt += 1
                if int(D[dst[g], j]) < best_md:
                    best_md = int(D[dst[g], j]); best_matched = g
        loose[i] = loose_hit; exact[i] = cnt > 0; n_exact[i] = cnt
        if cnt > 0:
            good_edge[i] = best_matched; good_D[i] = best_md
    T["has_good_sibling"] = has_good; T["exact_match"] = exact; T["loose_match"] = loose; T["n_exact_matches"] = n_exact
    T["good_edge"] = good_edge; T["good_D"] = good_D
    T["H_trap"] = T["ecc"]; T["H_trap_tree"] = T["height"]
    hp = np.where(has_good, np.minimum(T["ecc"], np.where(good_D >= 0, good_D, 10**6)), T["ecc"])
    hpt = np.where(has_good, np.minimum(T["height"], np.where(good_D >= 0, good_D, 10**6)), T["height"])
    T["H_pair"] = hp; T["H_pair_tree"] = hpt
    return {"traps": int(n), "with_any_nontrap_sibling": int(has_good.sum()), "exact_match_6_features": int(exact.sum()),
            "loose_match_3_features": int(loose.sum()), "match_features": SIBLING_MATCH_FEATURES, "loose_features": LOOSE_MATCH_FEATURES}


def hobs_hist(values: np.ndarray, hmax: int = 5) -> dict:
    out = {str(h): int((values == h).sum()) for h in range(hmax + 1)}
    out[f">{hmax}"] = int((values > hmax).sum()); out["n"] = int(len(values))
    return out


def q1_exact(U: dict, T: dict, hmax: int = 5) -> dict:
    """Exact (sound) lookahead classification over ALL live (s, a, t) triples.
    TRAP proven at depth h iff dead successor with ecc <= h (graph) ; SAFE proven iff D[s', t] <= h ; else UNKNOWN."""
    src, dst, D = U["src"], U["dst"], U["D"]
    n_live = 0; n_trap = int(T["n"]); safe_at = np.zeros(hmax + 1, dtype=np.int64)
    for j in range(len(U["targets"])):
        Ds, Dd = D[src, j], D[dst, j]
        live = Ds >= 0; n_live += int(live.sum())
        dd = Dd[live]
        for h in range(hmax + 1):
            safe_at[h] += int(((dd >= 0) & (dd <= h)).sum())
    n_non = n_live - n_trap
    out = {"live_triples": n_live, "traps": n_trap, "non_traps": n_non, "prevalence": n_trap / max(1, n_live), "per_depth": {}}
    for h in range(hmax + 1):
        tp = int((T["ecc"] <= h).sum()); tp_tree = int((T["height"] <= h).sum())
        fn = n_trap - tp
        # mapping A: UNKNOWN -> SAFE (sound trap predictor); mapping B: UNKNOWN -> TRAP
        fpB = n_non - int(safe_at[h])
        out["per_depth"][str(h)] = {
            "traps_proven_graph": tp, "traps_proven_tree": tp_tree, "nontraps_proven_safe": int(safe_at[h]),
            "resolved_fraction": (tp + int(safe_at[h])) / max(1, n_live),
            "A_unknown_as_safe": {"precision": 1.0 if tp else 0.0, "recall": tp / max(1, n_trap), "fpr": 0.0, "fnr": fn / max(1, n_trap),
                                   "balanced_accuracy": 0.5 * (tp / max(1, n_trap) + 1.0)},
            "B_unknown_as_trap": {"precision": n_trap / max(1, n_trap + fpB), "recall": 1.0, "fpr": fpB / max(1, n_non), "fnr": 0.0,
                                   "balanced_accuracy": 0.5 * (1.0 + (n_non - fpB) / max(1, n_non))},
        }
    out["base_rates"] = {"always_safe": {"precision": 0.0, "recall": 0.0, "balanced_accuracy": 0.5},
                         "always_trap": {"precision": n_trap / max(1, n_live), "recall": 1.0, "balanced_accuracy": 0.5}}
    out["pr_auc_note"] = "not reported: the exact controller is three-valued and sound, so precision is 1 at every recall it attains; a PR curve would be a step function."
    return out


def lookahead_cost_sample(U: dict, obs: Observer, n: int, seed: int, hmax: int = 5) -> dict:
    """Mean cost per lookahead call from random live successors (uncached), per depth, with resolved fractions."""
    rng = np.random.default_rng(seed)
    src, dst, D = U["src"], U["dst"], U["D"]
    T = len(U["targets"])
    e = rng.integers(0, len(src), size=n * 4); j = rng.integers(0, T, size=n * 4)
    live = D[src[e], j] >= 0
    e, j = e[live][:n], j[live][:n]
    out = {}
    for h in range(hmax + 1):
        exp = exm = 0; verdict = collections.Counter()
        for ee, jj in zip(e.tolist(), j.tolist()):
            r = obs.lookahead(int(dst[ee]), U["targets"][jj], h)
            verdict[r[0]] += 1; exp += r[2]; exm += r[3]
        out[str(h)] = {"calls": len(e), "mean_states_expanded": exp / len(e), "mean_transitions_examined": exm / len(e),
                       "verdicts": dict(verdict), "resolved_fraction": (verdict["SAFE"] + verdict["TRAP"]) / len(e)}
    return out


def residual_set(U: dict, T: dict, hmax: int = 5) -> dict:
    L = U["L"]
    m = T["exact_match"] & (T["H_pair"] > hmax)
    mt = T["exact_match"] & (T["H_pair_tree"] > hmax)
    def summarize(mask):
        if not mask.any():
            return {"count": 0}
        return {"count": int(mask.sum()), "fraction_of_traps": float(mask.sum() / max(1, T["n"])),
                "targets": dict(collections.Counter([index_word(U["targets"][j], L) for j in T["target_j"][mask].tolist()])),
                "D_src_hist": dict(collections.Counter(T["D_src"][mask].tolist())),
                "family": dict(collections.Counter(T["family"][mask].tolist())),
                "succ_outdeg_hist": dict(collections.Counter(T["succ_outdeg"][mask].tolist())),
                "region_hist": dict(collections.Counter(T["region"][mask].tolist())),
                "ecc_hist": dict(collections.Counter(T["ecc"][mask].tolist())), "height_hist": dict(collections.Counter(T["height"][mask].tolist())),
                "examples": [{"state": index_word(int(T["src"][i]), L), "target": index_word(U["targets"][int(T["target_j"][i])], L),
                              "trap_action": f"{U['rules'][int(T['rule'][i])].name}@{int(T['pos'][i])}", "trap_successor": index_word(int(T["dst"][i]), L),
                              "good_action": f"{U['rules'][int(U['rule'][int(T['good_edge'][i])])].name}@{int(U['pos'][int(T['good_edge'][i])])}",
                              "good_successor": index_word(int(U["dst"][int(T["good_edge"][i])]), L), "D_src": int(T["D_src"][i]), "good_D": int(T["good_D"][i]),
                              "ecc": int(T["ecc"][i]), "height": int(T["height"][i]), "region": int(T["region"][i])}
                             for i in np.nonzero(mask)[0][:12].tolist()]}
    return {"R5_graph_semantics": summarize(m), "R5_tree_semantics": summarize(mt)}


def write_trap_csv(U: dict, T: dict, path: str) -> str:
    L = U["L"]; rules = U["rules"]
    buf = io.StringIO(); w = csv.writer(buf)
    cols = ["source", "target", "family", "rule", "pos", "successor", "D_src", "succ_len", "succ_outdeg", "succ_n_cancel", "succ_n_relator", "visible",
            "region", "ecc", "height", "has_good_sibling", "exact_match", "loose_match", "n_exact_matches", "good_action", "good_successor", "good_D", "H_pair", "H_pair_tree"]
    w.writerow(cols)
    for i in range(T["n"]):
        ge = int(T["good_edge"][i])
        w.writerow([index_word(int(T["src"][i]), L), index_word(U["targets"][int(T["target_j"][i])], L), T["family"][i], rules[int(T["rule"][i])].name, int(T["pos"][i]),
                    index_word(int(T["dst"][i]), L), int(T["D_src"][i]), int(T["succ_len"][i]), int(T["succ_outdeg"][i]), int(T["succ_n_cancel"][i]), int(T["succ_n_relator"][i]),
                    int(T["visible"][i]), int(T["region"][i]), int(T["ecc"][i]), int(T["height"][i]), int(T["has_good_sibling"][i]), int(T["exact_match"][i]), int(T["loose_match"][i]),
                    int(T["n_exact_matches"][i]), (f"{rules[int(U['rule'][ge])].name}@{int(U['pos'][ge])}" if ge >= 0 else ""), (index_word(int(U["dst"][ge]), L) if ge >= 0 else ""),
                    int(T["good_D"][i]), int(T["H_pair"][i]), int(T["H_pair_tree"][i])])
    data = buf.getvalue().encode()
    with gzip.open(path, "wb", compresslevel=9) as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()
