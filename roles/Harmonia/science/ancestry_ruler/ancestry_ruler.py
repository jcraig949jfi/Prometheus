"""Ancestry ground-truth ruler. Preregistration: PREREG_ANCESTRY_RULER_2026-09-18.md.

    python ancestry_ruler.py --stage controls        # C-CHEAT, C-POS, C-NEG, C-ORDER on the synthetic world
    python ancestry_ruler.py --stage curves          # D0..D5 loss curves, three replicates, P1-P4 readouts

Input model: a POPULATION RECORD = list of organisms {id, parent_id|None, birth_time, genome, alive_at_end}.
Adapters for .spop / POET / NPE records are owed separately (prereg s7).
"""
import argparse, hashlib, json, os, random, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA = "abcdefghijklmnopqrstuvwxyz"
# AMENDMENT_A (2026-09-18, before any run): INDEL 0.01 -> 0.0 and a candidate window of 12 generations so the
# reconstruction is Hamming-vectorised and runs in minutes on M3 (see PREREG_ANCESTRY_AMENDMENT_A.md).
N, G, L, MU, INDEL = 200, 60, 50, 0.02, 0.0
WINDOW = 12


# ------------------------------------------------------------------ synthetic world
def synth_world(seed, n=N, g=G, length=L, mu=MU, indel=INDEL, selection=0.02):
    rng = random.Random(seed)
    target = "".join(rng.choice(ALPHA) for _ in range(length))
    orgs = []; nid = 0
    pop = []
    for _ in range(n):
        genome = "".join(rng.choice(ALPHA) for _ in range(length))
        orgs.append({"id": nid, "parent_id": None, "birth_time": 0, "genome": genome}); pop.append(nid); nid += 1
    for gen in range(1, g + 1):
        fit = []
        for oid in pop:
            gsq = orgs[oid]["genome"]
            fit.append(1.0 + selection * sum(1 for a, b in zip(gsq, target) if a == b))
        tot = sum(fit); cum = np.cumsum(fit) / tot
        newpop = []
        for _ in range(n):
            u = rng.random(); k = int(np.searchsorted(cum, u)); parent = pop[min(k, len(pop) - 1)]
            gsq = list(orgs[parent]["genome"])
            for i in range(len(gsq)):
                if rng.random() < mu: gsq[i] = rng.choice(ALPHA)
            if rng.random() < indel:
                if rng.random() < 0.5 and len(gsq) > 10: del gsq[rng.randrange(len(gsq))]
                else: gsq.insert(rng.randrange(len(gsq) + 1), rng.choice(ALPHA))
            orgs.append({"id": nid, "parent_id": parent, "birth_time": gen, "genome": "".join(gsq)}); newpop.append(nid); nid += 1
        pop = newpop
    alive = set(pop)
    for o in orgs: o["alive_at_end"] = o["id"] in alive
    return orgs


# ------------------------------------------------------------------ degradations
def ancestors(orgs_by_id, oid):
    out = []; cur = orgs_by_id[oid]["parent_id"]
    while cur is not None:
        out.append(cur); cur = orgs_by_id[cur]["parent_id"]
    return out


def degrade(orgs, mode, param=None, rng=None):
    by = {o["id"]: o for o in orgs}
    if mode == "D0":
        return [dict(o) for o in orgs]
    if mode == "D1":
        return [dict(o, parent_id=None) for o in orgs if o["alive_at_end"]]
    if mode == "D2":
        keep = set()
        for o in orgs:
            if o["alive_at_end"]:
                keep.add(o["id"]); keep.update(ancestors(by, o["id"]))
        return [dict(o) for o in orgs if o["id"] in keep]
    if mode == "D3":
        k = param
        kept = [dict(o) for o in orgs if o["birth_time"] % k == 0 or o["alive_at_end"]]
        ks = {o["id"] for o in kept}
        for o in kept:
            if o["parent_id"] is not None and o["parent_id"] not in ks: o["parent_id"] = None
        return kept
    if mode == "D4":
        return [dict(o, parent_id=None) for o in orgs]
    if mode == "D5":
        p = param; out = [dict(o) for o in orgs]; ids = [o["id"] for o in orgs]
        for o in out:
            if o["parent_id"] is not None and rng.random() < p:
                cand = rng.choice(ids)
                while cand == o["id"] or cand == o["parent_id"]: cand = rng.choice(ids)
                o["parent_id"] = cand; o["_corrupted"] = True
        return out
    raise ValueError(mode)


# ------------------------------------------------------------------ reconstruction
def levenshtein(a, b):
    if a == b: return 0
    if len(a) < len(b): a, b = b, a
    prev = np.arange(len(b) + 1)
    for i, ca in enumerate(a, 1):
        cur = np.empty_like(prev); cur[0] = i
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return int(prev[-1])


def reconstruct(record):
    """PARSIMONY-NEAREST-ANCESTOR: recorded parent ids kept; missing ones inferred as the nearest (Levenshtein)
    organism with strictly earlier birth_time; ties -> most recent birth, then smaller id. Returns {id: inferred_parent}."""
    recs = sorted(record, key=lambda o: (o["birth_time"], o["id"]))
    edges = {}
    by_time = {}
    for o in recs: by_time.setdefault(o["birth_time"], []).append(o)
    times = sorted(by_time)
    # per birth_time: candidate arrays (equal-length genomes -> Hamming, vectorised); unequal lengths -> Levenshtein
    for o in recs:
        if o["parent_id"] is not None:
            edges[o["id"]] = o["parent_id"]; continue
        cand = [q for t in times if o["birth_time"] - WINDOW <= t < o["birth_time"] for q in by_time[t]]
        if not cand:
            edges[o["id"]] = None; continue
        g = np.frombuffer(o["genome"].encode(), dtype=np.uint8)
        best = None
        same = [q for q in cand if len(q["genome"]) == len(o["genome"])]
        if same:
            M = np.frombuffer("".join(q["genome"] for q in same).encode(), dtype=np.uint8).reshape(len(same), -1)
            d = (M != g[None, :]).sum(axis=1)
            # AMENDMENT_B: ties broken by (most recent birth, then genome string), never by id (C-ORDER)
            for q, dq in zip(same, d):
                key = (int(dq), -q["birth_time"], q["genome"])
                if best is None or key < best[0]: best = (key, q["id"])
        for q in cand:
            if len(q["genome"]) != len(o["genome"]):
                key = (levenshtein(o["genome"], q["genome"]), -q["birth_time"], q["genome"])
                if best is None or key < best[0]: best = (key, q["id"])
        edges[o["id"]] = best[1]
    return edges


# ------------------------------------------------------------------ losses
def losses(truth, record, edges, rng, pairs=200):
    tby = {o["id"]: o for o in truth}; kept = {o["id"] for o in record}
    true_edges = {o["id"]: o["parent_id"] for o in truth if o["id"] in kept and o["parent_id"] is not None and o["parent_id"] in kept}
    inf_edges = {k: v for k, v in edges.items() if v is not None}
    n_true = len(true_edges); n_inf = len(inf_edges)
    correct = sum(1 for k, v in true_edges.items() if inf_edges.get(k) == v)
    res = {"n_retained": len(kept), "n_true_edges_among_retained": n_true, "n_inferred_edges": n_inf,
           "edge_recall": (correct / n_true) if n_true else None, "edge_precision": (correct / n_inf) if n_inf else "NO_EDGES"}
    # ancestor recall (k = 1, 5, all) against TRUE ancestors restricted to retained ones
    def inf_anc(oid, depth=None):
        out = []; cur = inf_edges.get(oid); steps = 0
        while cur is not None and (depth is None or steps < depth) and cur not in out:
            out.append(cur); cur = inf_edges.get(cur); steps += 1
        return out
    for k, label in ((1, "1"), (5, "5"), (None, "all")):
        num = den = 0
        for oid in kept:
            ta = [a for a in (ancestors(tby, oid) if k is None else ancestors(tby, oid)[:k]) if a in kept]
            if not ta: continue
            ia = set(inf_anc(oid, None))
            num += sum(1 for a in ta if a in ia); den += len(ta)
        res[f"ancestor_recall_{label}"] = (num / den) if den else None
    # depth error
    def inf_depth(oid):
        d = 0; cur = inf_edges.get(oid); visited = set()
        while cur is not None and cur not in visited:
            visited.add(cur); d += 1; cur = inf_edges.get(cur)
        return d
    tdepth = {oid: tby[oid]["birth_time"] for oid in kept}
    res["depth_error"] = float(np.mean([abs(inf_depth(oid) - len([a for a in ancestors(tby, oid) if a in kept])) for oid in kept]))
    extinct = [o for o in truth if not o["alive_at_end"]]
    res["extinct_recoverable"] = (sum(1 for o in extinct if o["id"] in kept) / len(extinct)) if extinct else None
    # AMENDMENT_C: extinct BRANCHES = extinct organisms with no surviving descendant (the thing D2 loses)
    surv_anc = set()
    for o in truth:
        if o["alive_at_end"]: surv_anc.update(ancestors(tby, o["id"]))
    branches = [o for o in extinct if o["id"] not in surv_anc]
    res["n_extinct_branch_organisms"] = len(branches)
    res["extinct_branch_recoverable"] = (sum(1 for o in branches if o["id"] in kept) / len(branches)) if branches else None
    # MRCA error on survivor pairs
    surv = [o["id"] for o in truth if o["alive_at_end"] and o["id"] in kept]
    def mrca_gen(anc_fn, a, b):
        A = [a] + anc_fn(a); B = set([b] + anc_fn(b))
        for x in A:
            if x in B: return tby[x]["birth_time"]
        return -1
    errs = []
    for _ in range(min(pairs, len(surv) * (len(surv) - 1) // 2)):
        a, b = rng.sample(surv, 2)
        errs.append(abs(mrca_gen(lambda x: ancestors(tby, x), a, b) - mrca_gen(lambda x: inf_anc(x), a, b)))
    res["mrca_error"] = float(np.mean(errs)) if errs else None
    return res


def sha_record(rec):
    return hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()


# ------------------------------------------------------------------ stages
def stage_controls(out):
    os.makedirs(out, exist_ok=True); res = {"stage": "controls", "world": {"N": N, "G": G, "L": L, "mu": MU, "indel": INDEL, "seed": 20260918}}
    truth = synth_world(20260918); res["world"]["n_organisms"] = len(truth); res["world"]["truth_sha256"] = sha_record(truth)
    rng = random.Random(1)
    # C-CHEAT
    e = reconstruct(degrade(truth, "D0")); l = losses(truth, truth, e, random.Random(2))
    res["C-CHEAT"] = {**l, "pass": l["edge_recall"] == 1.0 and l["edge_precision"] == 1.0 and l["depth_error"] == 0.0 and l["mrca_error"] == 0.0}
    # C-POS: D5 p=0.10; flagging rule
    rec = degrade(truth, "D5", 0.10, random.Random(3)); e = reconstruct(rec); l = losses(truth, rec, e, random.Random(4))
    by = {o["id"]: o for o in rec}
    flagged = 0; corrupted = [o for o in rec if o.get("_corrupted")]
    recs_sorted = sorted(rec, key=lambda o: (o["birth_time"], o["id"]))
    by_time = {}
    for q in recs_sorted: by_time.setdefault(q["birth_time"], []).append(q)
    for o in corrupted:
        earlier = [q for t in by_time if o["birth_time"] - WINDOW <= t < o["birth_time"] for q in by_time[t]]
        if not earlier: continue
        g = np.frombuffer(o["genome"].encode(), dtype=np.uint8)
        M = np.frombuffer("".join(q["genome"] for q in earlier).encode(), dtype=np.uint8).reshape(len(earlier), -1)
        dn = int((M != g[None, :]).sum(axis=1).min())
        pg = by[o["parent_id"]]["genome"] if o["parent_id"] in by else None
        dr = int((np.frombuffer(pg.encode(), dtype=np.uint8) != g).sum()) if pg is not None and len(pg) == len(o["genome"]) else 10 ** 6
        if dr - dn >= 3: flagged += 1
    frac = flagged / len(corrupted) if corrupted else None
    res["C-POS"] = {**l, "n_corrupted": len(corrupted), "flagged_fraction": frac, "pass": (l["edge_recall"] is not None and l["edge_recall"] <= 0.95) and (frac is not None and frac >= 0.80)}
    # C-NEG: no reproduction
    neg = [{"id": i, "parent_id": None, "birth_time": 0, "genome": "".join(random.Random(100 + i).choice(ALPHA) for _ in range(L)), "alive_at_end": True} for i in range(50)]
    e = reconstruct(neg); l = losses(neg, neg, e, random.Random(5))
    res["C-NEG"] = {**l, "pass": l["n_inferred_edges"] == 0 and l["edge_precision"] == "NO_EDGES"}
    # C-ORDER: permute ids
    ids = [o["id"] for o in truth]; perm = ids[:]; random.Random(6).shuffle(perm); pm = dict(zip(ids, perm))
    permuted = [dict(o, id=pm[o["id"]], parent_id=(pm[o["parent_id"]] if o["parent_id"] is not None else None)) for o in truth]
    lA = losses(truth, degrade(truth, "D4"), reconstruct(degrade(truth, "D4")), random.Random(7))
    lB = losses(permuted, degrade(permuted, "D4"), reconstruct(degrade(permuted, "D4")), random.Random(7))
    same = all(abs((lA[k] or 0) - (lB[k] or 0)) < 1e-12 for k in ("edge_recall", "edge_precision", "depth_error") if not isinstance(lA[k], str))
    res["C-ORDER"] = {"D4_original": {k: lA[k] for k in ("edge_recall", "edge_precision", "depth_error")}, "D4_permuted": {k: lB[k] for k in ("edge_recall", "edge_precision", "depth_error")}, "pass": bool(same)}
    res["all_controls_pass"] = all(res[k]["pass"] for k in ("C-CHEAT", "C-POS", "C-NEG", "C-ORDER"))
    res["ruler_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    json.dump(res, open(os.path.join(out, "controls.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True, default=str)
    print(json.dumps({k: (v if k.startswith("C-") or k == "all_controls_pass" else "...") for k, v in res.items()}, indent=1, default=str))
    return res["all_controls_pass"]


def stage_curves(out):
    c = json.load(open(os.path.join(out, "controls.json"))); assert c["all_controls_pass"], "controls did not pass; curves refused"
    rows = []; t0 = time.time()
    plan = [("D0", None), ("D1", None), ("D2", None), ("D3", 2), ("D3", 5), ("D3", 10), ("D4", None), ("D5", 0.05), ("D5", 0.10), ("D5", 0.25)]
    for seed in (20260918, 20260919, 20260920):
        truth = synth_world(seed)
        for mode, param in plan:
            rec = degrade(truth, mode, param, random.Random(seed + 7)); e = reconstruct(rec); l = losses(truth, rec, e, random.Random(seed + 11))
            rows.append({"seed": seed, "mode": mode, "param": param, **l}); print(seed, mode, param, {k: l[k] for k in ("edge_recall", "edge_precision", "extinct_recoverable", "depth_error", "mrca_error")}, flush=True)
    def agg(mode, param, key):
        v = [r[key] for r in rows if r["mode"] == mode and r["param"] == param and isinstance(r[key], (int, float))]
        return (float(np.mean(v)), float(np.min(v)), float(np.max(v))) if v else None
    def a0(m, p, k):
        v = agg(m, p, k); return v[0] if v else None
    # P1-P4 exactly as preregistered, with VACUOUS / UNEVALUABLE where the measure has no value
    d1 = [r for r in rows if r["mode"] == "D1"]; d2 = [r for r in rows if r["mode"] == "D2"]
    P = {"P1_D1_recall_lt_0.5_all_reps": ("VACUOUS: no true parent edge has both endpoints among the survivors (non-overlapping generations); edge_recall undefined" if all(r["edge_recall"] is None for r in d1) else all(r["edge_recall"] < 0.5 for r in d1)),
         "P2_D2_recall_1_and_extinct_0": all(r["edge_recall"] == 1.0 and r["extinct_recoverable"] == 0.0 for r in d2),
         "P2_as_written_fails_because": "extinct_recoverable counts extinct ANCESTORS of survivors, which D2 keeps by construction; the loss D2 causes is of extinct BRANCHES (see extinct_branch_recoverable, AMENDMENT_C)" if not all(r["extinct_recoverable"] == 0.0 for r in d2) else None,
         "P3_D3_monotone_in_k": ("UNEVALUABLE on edge_recall: with every k-th generation kept no true parent edge has both endpoints retained" if a0("D3", 2, "edge_recall") is None else (a0("D3", 2, "edge_recall") > a0("D3", 5, "edge_recall") > a0("D3", 10, "edge_recall"))),
         "P4_D4_recall_in_0.6_0.95": all(0.6 <= r["edge_recall"] <= 0.95 for r in rows if r["mode"] == "D4"),
         # POST-HOC (labelled; not preregistered): the measures that DO read D1/D3
         "POSTHOC_P3_mrca_error_monotone_in_k": (a0("D3", 2, "mrca_error") < a0("D3", 5, "mrca_error") < a0("D3", 10, "mrca_error")),
         "POSTHOC_P2_extinct_branch_recoverable_D2": a0("D2", None, "extinct_branch_recoverable"),
         "POSTHOC_P1_D1_mrca_error": a0("D1", None, "mrca_error")}
    res = {"rows": rows, "predictions": P, "summary": {f"{m}:{p}": {k: agg(m, p, k) for k in ("edge_recall", "edge_precision", "ancestor_recall_1", "ancestor_recall_all", "depth_error", "extinct_recoverable", "extinct_branch_recoverable", "mrca_error")} for m, p in plan}, "seconds": round(time.time() - t0, 1)}
    json.dump(res, open(os.path.join(out, "curves.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True, default=str)
    print(json.dumps(P, indent=1)); print("seconds", res["seconds"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", choices=["controls", "curves"], required=True); ap.add_argument("--out", default=os.path.join(HERE, "out", "synthetic_2026-09-18"))
    a = ap.parse_args()
    if a.stage == "controls": sys.exit(0 if stage_controls(a.out) else 2)
    stage_curves(a.out)
