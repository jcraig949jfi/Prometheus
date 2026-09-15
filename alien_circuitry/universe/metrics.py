"""Phase A/B measurements on an enumerated universe: difficulty strata, target-conditioned traps,
target-set statistics, uninformed search baselines, oracle headroom, consequence-chart (D, M) accounting,
and holdout-mask proposals.  No compression method is defined or run here.
"""
from __future__ import annotations
import collections, hashlib, lzma, zlib
import numpy as np
from .directed_rewriting import index_word, offsets
from .enumerate import UNREACH

STRATA = {"TRIVIAL": (1, 2), "EASY": (3, 4), "MEDIUM": (5, 6), "HARD": (7, 10**6)}
MIN_START_LEN = 3  # problems start from words of length >= 3 (documented corpus rule)


def stratum_of(d: int) -> str:
    for k, (lo, hi) in STRATA.items():
        if lo <= d <= hi:
            return k
    return "NONE"


# ----------------------------------------------------------------------------- difficulty
def candidate_problems(U: dict):
    D, LEN = U["D"], U["LEN"]
    mask = (D > 0) & (LEN[:, None] >= MIN_START_LEN)
    s_idx, j_idx = np.nonzero(mask)
    return s_idx, j_idx, D[s_idx, j_idx].astype(np.int64)


def difficulty(U: dict) -> dict:
    s_idx, j_idx, d = candidate_problems(U)
    hist = collections.Counter(d.tolist())
    out = {"min_start_len": MIN_START_LEN, "candidate_problems": int(len(d)),
           "distance_histogram": {str(k): int(hist[k]) for k in sorted(hist)},
           "max_D": int(d.max()) if len(d) else 0}
    for name, (lo, hi) in STRATA.items():
        out[f"eligible_{name}"] = int(((d >= lo) & (d <= hi)).sum())
    od, odn = U["outdeg"], U["outdeg_nominal"]
    live_any = (U["D"] >= 0).any(axis=1)
    out["branching_nominal_hist_all_states"] = {str(k): int(v) for k, v in sorted(collections.Counter(odn.tolist()).items())}
    out["branching_effective_hist_all_states"] = {str(k): int(v) for k, v in sorted(collections.Counter(od.tolist()).items())}
    out["mean_branching_nominal_all"] = float(odn.mean()); out["mean_branching_effective_all"] = float(od.mean())
    out["mean_branching_nominal_live"] = float(odn[live_any].mean()); out["mean_branching_effective_live"] = float(od[live_any].mean())
    out["fixpoint_states"] = int((od == 0).sum())
    out["states_live_for_some_target"] = int(live_any.sum())
    return out


# ----------------------------------------------------------------------------- traps
def _forward_region(fwd_indptr, fwd_indices, start: int):
    """Forward-reachable set size and BFS eccentricity from start (max BFS depth)."""
    seen = {start}; frontier = [start]; depth = 0
    while frontier:
        nxt = []
        for v in frontier:
            for u in fwd_indices[fwd_indptr[v]:fwd_indptr[v + 1]]:
                u = int(u)
                if u not in seen:
                    seen.add(u); nxt.append(u)
        if not nxt:
            break
        frontier = nxt; depth += 1
    return len(seen), depth


def trap_analysis(U: dict, max_examples: int = 40) -> dict:
    src, dst, rid, pos = U["src"], U["dst"], U["rule"], U["pos"]
    D, LEN, od, L = U["D"], U["LEN"], U["outdeg"], U["L"]
    rules = U["rules"]; fam = np.array([r.family for r in rules])
    families = sorted(set(fam.tolist()))
    fwd_indptr, fwd_indices = U["fwd"]
    targets = U["targets"]; tlen = np.array([len(index_word(t, L)) for t in targets])
    E = len(src)
    tot = {"live_action_target_triples": 0, "trap": 0, "visible_no_continuation": 0, "visible_length_bound": 0, "latent": 0}
    per_target = []
    fam_live = collections.Counter(); fam_trap = collections.Counter(); fam_latent = collections.Counter()
    latent_dst_all = set()
    latent_outdeg = collections.Counter()
    latent_dD_proxy = collections.Counter()  # change in admissible length bound h=(len-len_t)/2
    # near-clone bookkeeping: per (s, t) with both latent-trap and non-trap actions of identical local signature
    indist_latent = 0; latent_with_nontrap_sibling = 0
    examples = []
    for j, t in enumerate(targets):
        Ds, Dd = D[src, j], D[dst, j]
        live = Ds >= 0
        lost = Dd < 0
        trap = live & lost
        vis0 = trap & (od[dst] == 0)
        visL = trap & ~vis0 & (LEN[dst] < tlen[j])
        latent = trap & ~vis0 & ~visL
        n_live, n_trap, n_v0, n_vL, n_lat = int(live.sum()), int(trap.sum()), int(vis0.sum()), int(visL.sum()), int(latent.sum())
        tot["live_action_target_triples"] += n_live; tot["trap"] += n_trap
        tot["visible_no_continuation"] += n_v0; tot["visible_length_bound"] += n_vL; tot["latent"] += n_lat
        for f in families:
            fm = fam[rid] == f
            fam_live[f] += int((live & fm).sum()); fam_trap[f] += int((trap & fm).sum()); fam_latent[f] += int((latent & fm).sum())
        lat_idx = np.nonzero(latent)[0]
        latent_dst_all.update(dst[lat_idx].tolist())
        latent_outdeg.update(od[dst[lat_idx]].tolist())
        latent_dD_proxy.update(((LEN[dst[lat_idx]].astype(int) - LEN[src[lat_idx]].astype(int)) // 2).tolist())
        # near-clones: group live edges by source; signature = (family, len(dst), outdeg(dst))
        if n_lat:
            live_idx = np.nonzero(live)[0]
            sig = np.stack([np.searchsorted(families, fam[rid[live_idx]]), LEN[dst[live_idx]].astype(np.int64), od[dst[live_idx]].astype(np.int64)], axis=1)
            key = src[live_idx] * 100000 + sig[:, 0] * 10000 + sig[:, 1] * 100 + np.minimum(sig[:, 2], 99)
            trap_here = trap[live_idx]
            # for each key, does it contain both a trap and a non-trap edge?
            order = np.argsort(key, kind="stable")
            k_sorted = key[order]; t_sorted = trap_here[order]; e_sorted = live_idx[order]
            bounds = np.flatnonzero(np.diff(k_sorted)) + 1
            starts = np.concatenate([[0], bounds]); ends = np.concatenate([bounds, [len(k_sorted)]])
            lat_sorted = latent[e_sorted]
            for a, b in zip(starts, ends):
                tb = t_sorted[a:b]; lb = lat_sorted[a:b]
                if lb.any() and (~tb).any():
                    indist_latent += int(lb.sum())
                    if len(examples) < max_examples:
                        ei_trap = int(e_sorted[a:b][lb][0]); ei_ok = int(e_sorted[a:b][~tb][0])
                        s = int(src[ei_trap]); region, ecc = _forward_region(fwd_indptr, fwd_indices, int(dst[ei_trap]))
                        examples.append({
                            "target": index_word(t, L), "state": index_word(s, L), "D_state": int(D[s, j]),
                            "trap_action": rules[rid[ei_trap]].name + f"@{int(pos[ei_trap])}", "trap_successor": index_word(int(dst[ei_trap]), L),
                            "trap_successor_outdeg": int(od[dst[ei_trap]]), "trap_successor_forward_region": region, "trap_successor_eccentricity": ecc,
                            "ok_action": rules[rid[ei_ok]].name + f"@{int(pos[ei_ok])}", "ok_successor": index_word(int(dst[ei_ok]), L),
                            "ok_successor_D": int(D[dst[ei_ok], j]), "ok_successor_outdeg": int(od[dst[ei_ok]]),
                        })
            # latent traps whose source also has ANY non-trap action (any signature)
            src_has_ok = np.zeros(U["NS"], dtype=bool); src_has_ok[src[live_idx][~trap_here]] = True
            latent_with_nontrap_sibling += int(src_has_ok[src[lat_idx]].sum())
        per_target.append({"target": index_word(t, L), "live_triples": n_live, "traps": n_trap, "visible_no_continuation": n_v0,
                           "visible_length_bound": n_vL, "latent": n_lat, "trap_rate": (n_trap / n_live) if n_live else 0.0})
    # continuation statistics for every distinct latent-trap successor (target-independent forward region)
    regions = []; eccs = []
    for v in sorted(latent_dst_all):
        r, e = _forward_region(fwd_indptr, fwd_indices, v)
        regions.append(r); eccs.append(e)
    def hist(xs):
        c = collections.Counter(xs); return {str(k): int(c[k]) for k in sorted(c)}
    def q(xs):
        if not xs: return None
        a = np.array(xs); return {"min": int(a.min()), "p25": float(np.percentile(a, 25)), "median": float(np.median(a)), "p75": float(np.percentile(a, 75)), "max": int(a.max()), "mean": float(a.mean())}
    return {
        "nominal_edges": int(E), "totals": tot,
        "trap_rate_of_live_triples": tot["trap"] / max(1, tot["live_action_target_triples"]),
        "latent_fraction_of_traps": tot["latent"] / max(1, tot["trap"]),
        "by_rule_family": {f: {"live": fam_live[f], "trap": fam_trap[f], "latent": fam_latent[f], "trap_rate": fam_trap[f] / max(1, fam_live[f])} for f in families},
        "distinct_latent_trap_successors": len(latent_dst_all),
        "latent_successor_forward_region_size": q(regions), "latent_successor_forward_region_hist": hist(regions),
        "latent_successor_eccentricity": q(eccs), "latent_successor_eccentricity_hist": hist(eccs),
        "latent_successor_outdeg_hist": hist(list(latent_outdeg.elements())),
        "latent_trap_delta_length_bound_hist": hist(list(latent_dD_proxy.elements())),
        "latent_traps_with_a_nontrap_sibling_action": latent_with_nontrap_sibling,
        "latent_traps_locally_indistinguishable_from_a_nontrap_sibling": indist_latent,
        "local_signature": "(rule family, len(successor), outdeg(successor))",
        "per_target": per_target, "examples": examples,
    }


# ----------------------------------------------------------------------------- baselines
class Searcher:
    def __init__(self, U: dict):
        fi, fx = U["fwd"]; ri, rx = U["rev"]
        self.fi, self.fx, self.ri, self.rx = fi.tolist(), fx.tolist(), ri.tolist(), rx.tolist()
        self.D, self.od = U["D"], U["outdeg"]

    def forward_bfs(self, s: int, t: int):
        fi, fx = self.fi, self.fx
        dist = {s: 0}; dq = collections.deque([s]); expanded = 0; examined = 0
        while dq:
            v = dq.popleft(); expanded += 1
            if v == t:
                return {"dist": dist[v], "states_expanded": expanded, "transitions_examined": examined}
            for u in fx[fi[v]:fi[v + 1]]:
                examined += 1
                if u not in dist:
                    dist[u] = dist[v] + 1; dq.append(u)
        return {"dist": -1, "states_expanded": expanded, "transitions_examined": examined}

    def bidirectional_bfs(self, s: int, t: int):
        """Layer-complete bidirectional BFS on the directed graph (forward from s, backward from t)."""
        if s == t:
            return {"dist": 0, "states_expanded": 1, "transitions_examined": 0}
        fi, fx, ri, rx = self.fi, self.fx, self.ri, self.rx
        dA = {s: 0}; dB = {t: 0}; fa = [s]; fb = [t]; la = 0; lb = 0; expanded = 0; examined = 0
        while fa and fb:
            if len(fa) <= len(fb):
                nf = []; la += 1
                for v in fa:
                    expanded += 1
                    for u in fx[fi[v]:fi[v + 1]]:
                        examined += 1
                        if u not in dA:
                            dA[u] = la; nf.append(u)
                fa = nf
                hits = [dA[u] + dB[u] for u in fa if u in dB]
            else:
                nf = []; lb += 1
                for v in fb:
                    expanded += 1
                    for u in rx[ri[v]:ri[v + 1]]:
                        examined += 1
                        if u not in dB:
                            dB[u] = lb; nf.append(u)
                fb = nf
                hits = [dA[u] + dB[u] for u in fb if u in dA]
            if hits:
                return {"dist": min(hits), "states_expanded": expanded, "transitions_examined": examined}
        return {"dist": -1, "states_expanded": expanded, "transitions_examined": examined}

    def oracle(self, s: int, j: int):
        """Perfect consequential information: descend D greedily, preferring the lowest-burden successor.
        States expanded = D; transitions examined = every legal action at each visited state (the oracle must
        look at each successor to rank it)."""
        fi, fx, D = self.fi, self.fx, self.D
        v = s; examined = 0; d0 = int(D[s, j])
        for _ in range(d0):
            best = None
            for u in fx[fi[v]:fi[v + 1]]:
                examined += 1
                if D[u, j] == D[v, j] - 1 and (best is None or self.od[u] < self.od[best]):
                    best = u
            v = best
        return {"dist": d0, "states_expanded": d0, "transitions_examined": examined}


def sample_problems(U: dict, per_stratum: int, seed: int = 20260912):
    s_idx, j_idx, d = candidate_problems(U)
    rng = np.random.default_rng(seed)
    out = []
    for name, (lo, hi) in STRATA.items():
        ii = np.nonzero((d >= lo) & (d <= hi))[0]
        if len(ii) == 0:
            continue
        pick = ii if len(ii) <= per_stratum else rng.choice(ii, per_stratum, replace=False)
        for i in pick:
            out.append((name, int(s_idx[i]), int(j_idx[i]), int(d[i])))
    return out


def baselines(U: dict, per_stratum: int = 500, seed: int = 20260912) -> dict:
    S = Searcher(U); probs = sample_problems(U, per_stratum, seed)
    rows = []
    mismatches = 0
    for name, s, j, d in probs:
        t = U["targets"][j]
        f = S.forward_bfs(s, t); b = S.bidirectional_bfs(s, t); o = S.oracle(s, j)
        if not (f["dist"] == b["dist"] == d == o["dist"]):
            mismatches += 1
        rows.append((name, d, f, b, o, j))
    out = {"sampled": len(rows), "distance_mismatches_bfs_bibfs_D_oracle": mismatches, "per_stratum": {}, "per_target": {}}
    def agg(sub):
        if not sub: return None
        F = np.array([[r[2]["states_expanded"], r[2]["transitions_examined"]] for r in sub], dtype=float)
        B = np.array([[r[3]["states_expanded"], r[3]["transitions_examined"]] for r in sub], dtype=float)
        O = np.array([[r[4]["states_expanded"], r[4]["transitions_examined"]] for r in sub], dtype=float)
        Dm = np.array([r[1] for r in sub], dtype=float)
        res = {"n": len(sub), "mean_D": float(Dm.mean()),
               "forward_bfs": {"mean_states_expanded": float(F[:, 0].mean()), "mean_transitions_examined": float(F[:, 1].mean())},
               "bidirectional_bfs": {"mean_states_expanded": float(B[:, 0].mean()), "mean_transitions_examined": float(B[:, 1].mean())},
               "oracle": {"mean_states_expanded": float(O[:, 0].mean()), "mean_transitions_examined": float(O[:, 1].mean())}}
        for k, col in (("states", 0), ("transitions", 1)):
            sa_bfs = 1 - O[:, col].sum() / F[:, col].sum(); sa_bi = 1 - O[:, col].sum() / B[:, col].sum()
            res[f"oracle_SA_vs_forward_bfs_{k}"] = float(sa_bfs); res[f"oracle_SA_vs_bibfs_{k}"] = float(sa_bi)
            res[f"ordering_inflation_{k}_points"] = float(100 * (sa_bfs - sa_bi))
            res[f"bibfs_over_bfs_{k}_ratio"] = float(B[:, col].sum() / F[:, col].sum())
        return res
    out["all"] = agg(rows)
    for name in STRATA:
        out["per_stratum"][name] = agg([r for r in rows if r[0] == name])
    for j in range(len(U["targets"])):
        out["per_target"][index_word(U["targets"][j], U["L"])] = agg([r for r in rows if r[5] == j])
    return out


# ----------------------------------------------------------------------------- target set
def target_stats(U: dict) -> dict:
    D, LEN, L = U["D"], U["LEN"], U["L"]
    out = []
    for j, t in enumerate(U["targets"]):
        col = D[:, j]; live = col >= 0
        hist = collections.Counter(col[live].tolist())
        out.append({"target": index_word(t, L), "len": len(index_word(t, L)), "reachable_states": int(live.sum()),
                    "reachable_fraction_of_parity_compatible": float(live.sum() / max(1, ((LEN % 2) == (len(index_word(t, L)) % 2)).sum())),
                    "distance_histogram": {str(k): int(hist[k]) for k in sorted(hist)}})
    return {"targets": out, "note": "length parity and the length lower bound are syntactically visible reachability filters; see receipt"}


# ----------------------------------------------------------------------------- charts
def _sizes(b: bytes) -> dict:
    return {"raw_bytes": len(b), "zlib9_bytes": len(zlib.compress(b, 9)), "lzma_bytes": len(lzma.compress(b, preset=6))}


def chart_D(U: dict) -> dict:
    D = U["D"]; live = D >= 0
    vals = collections.Counter(D[live].tolist())
    b = np.ascontiguousarray(D).tobytes()
    # canonical sparse (COO) encoding of the live entries: (state int32, target uint8, value uint8), row-major order.
    si, tj = np.nonzero(live)
    coo = si.astype(np.int32).tobytes() + tj.astype(np.uint8).tobytes() + D[live].astype(np.uint8).tobytes()
    return {"dtype": str(D.dtype), "shape": list(D.shape), "unreach_value": UNREACH, "live_entries": int(live.sum()),
            "density": float(live.mean()), "value_histogram": {str(k): int(vals[k]) for k in sorted(vals)},
            "storage_dense": _sizes(b), "storage_sparse_coo": _sizes(bytes(coo)),
            "reference_size_note": "M1 denominators must use an entropy-coded size (lzma of the sparse COO) so that generic sparsity is not credited as structure",
            "sha256": hashlib.sha256(b).hexdigest()}


M_SCHEMA = {
    "edge_table": {"key": "one row per nominal legal action (s, rule, position)", "fields": {
        "src": "int32 state index", "dst": "int32 successor index", "rule": "int8 rule id", "pos": "int8 position",
        "dst_outdeg": "int16 distinct-successor out-degree of dst", "dst_forward_region": "int32 forward-reachable set size from dst (target-independent)",
        "dst_eccentricity": "int16 BFS eccentricity from dst"}},
    "edge_target_table": {"key": "(edge row, target column); only rows with D[src,t] >= 0 are live", "fields": {
        "dD": "int8: D[dst,t]-D[src,t] when both live; +127 = target lost (trap); -128 = source not live (entry inert)",
        "flags": "uint8 bitfield: 1=live, 2=target_retained, 4=on_shortest_path (D[dst]+1==D[src]), 8=trap, 16=latent_trap"}},
}


def chart_M(U: dict, region_cache: dict | None = None) -> dict:
    src, dst, D, od, LEN, L = U["src"], U["dst"], U["D"], U["outdeg"], U["LEN"], U["L"]
    E, T = len(src), len(U["targets"])
    tlen = np.array([len(index_word(t, L)) for t in U["targets"]])
    h = hashlib.sha256(); zc = zlib.compressobj(9); zsize = 0; raw = 0; live_entries = 0
    flag_counts = collections.Counter(); dd_hist = collections.Counter()
    for j in range(T):
        Ds, Dd = D[src, j].astype(np.int16), D[dst, j].astype(np.int16)
        live = Ds >= 0; lost = Dd < 0
        dD = np.full(E, -128, dtype=np.int8)
        both = live & ~lost
        dD[both] = np.clip(Dd[both] - Ds[both], -127, 126).astype(np.int8)
        dD[live & lost] = 127
        flags = live.astype(np.uint8) | ((live & ~lost).astype(np.uint8) << 1) | ((both & (Dd + 1 == Ds)).astype(np.uint8) << 2) \
            | ((live & lost).astype(np.uint8) << 3) | ((live & lost & (od[dst] > 0) & (LEN[dst] >= tlen[j])).astype(np.uint8) << 4)
        b = dD.tobytes() + flags.tobytes()
        h.update(b); zsize += len(zc.compress(b)); raw += len(b); live_entries += int(live.sum())
        for bit, name in ((2, "retained"), (4, "on_shortest_path"), (8, "trap"), (16, "latent_trap")):
            flag_counts[name] += int(((flags & bit) > 0).sum())
        dd_hist.update(dD[both].tolist())
    zsize += len(zc.flush())
    edge_table_bytes = E * (4 + 4 + 1 + 1 + 2 + 4 + 2)
    return {"schema": M_SCHEMA, "edges": int(E), "targets": T, "edge_target_entries": int(E * T), "live_entries": live_entries,
            "live_density": live_entries / (E * T), "flag_counts": dict(flag_counts),
            "dD_histogram_live_retained": {str(k): int(dd_hist[k]) for k in sorted(dd_hist)},
            "storage": {"edge_table_raw_bytes": edge_table_bytes, "edge_target_raw_bytes": raw, "edge_target_zlib9_bytes": zsize},
            "sha256_edge_target": h.hexdigest()}


# ----------------------------------------------------------------------------- masks
def _bucket(key: str) -> float:
    return int(hashlib.sha256(key.encode()).hexdigest()[:12], 16) / 16 ** 12


def mask_proposal(U: dict, state_split=(0.6, 0.2, 0.2), entry_split=(0.6, 0.2, 0.2), heldout_targets: int = 4) -> dict:
    """Deterministic hashed masks over the consequence charts.  Proposal only; sizes reported, nothing frozen."""
    NS, L, name = U["NS"], U["L"], U["name"]
    D = U["D"]; live = D >= 0
    words = [index_word(i, L) for i in range(NS)]
    sb = np.array([_bucket(f"AC01|{name}|state|{w}") for w in words])
    state_role = np.where(sb < state_split[0], 0, np.where(sb < state_split[0] + state_split[1], 1, 2))
    tw = [index_word(t, L) for t in U["targets"]]
    eb = np.stack([np.array([_bucket(f"AC01|{name}|entry|{w}|{t}") for w in words]) for t in tw], axis=1)
    entry_role = np.where(eb < entry_split[0], 0, np.where(eb < entry_split[0] + entry_split[1], 1, 2))
    # target-column holdout is universe-independent so OOD-A/B hold out the SAME targets in every presentation
    tb = sorted(range(len(tw)), key=lambda j: _bucket(f"AC01|target|{tw[j]}"))
    held = tb[:heldout_targets]
    out = {"state_rows": {r: {"states": int((state_role == k).sum()), "live_entries": int(live[state_role == k].sum())} for k, r in enumerate(("train", "val", "test"))},
           "state_target_entries": {r: int((live & (entry_role == k)).sum()) for k, r in enumerate(("train", "val", "test"))},
           "target_columns": {"held_out": [tw[j] for j in held], "held_out_live_entries": int(live[:, held].sum()), "kept_live_entries": int(live.sum() - live[:, held].sum())},
           "hash_scheme": "states: sha256('AC01|<universe>|state|<word>'); entries: sha256('AC01|<universe>|entry|<word>|<target>'); target columns: sha256('AC01|target|<target>') (universe-independent); first 12 hex digits / 16^12; roles by split fractions",
           "state_split": state_split, "entry_split": entry_split}
    return out
