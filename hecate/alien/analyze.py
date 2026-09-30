"""Aggregate scored runs into the preregistered metrics, hypothesis decisions
and failure taxonomy (roles/Hecate/prereg/2026-09-30_alien_lawful_assay/).

    python -m hecate.alien.analyze <model>   # -> hecate/alien/runs/<model>/RESULTS.json
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

from hecate.alien import score as S
from hecate.alien.dataset import OUT
from hecate.alien.runner import RUNS, load, subsets

LEARN_MARGIN = 0.15          # PREREG s4: T2 component accuracy above the trivial bar
LEARN_EXACT = 0.25
CODE_LEARN_EXACT = 0.5


def _baselines():
    with open(os.path.join(OUT, "BASELINES.json"), encoding="utf-8") as fh:
        return {r["id"]: r for r in json.load(fh)["rows"]}


def per_system(model):
    pub, key = load()
    base = _baselines()
    blind, fam = S.read(model, "blind"), S.read(model, "fam")
    reveal, active, prose = S.read(model, "reveal"), S.read(model, "active"), S.read(model, "prose")
    cache = {}
    rows = {}
    for sid, e in sorted(key.items()):
        p, ans = e["params"], e["answers"]
        b = base[sid]
        bar_t2 = max(b["identity_t2_comp"], b["nn_t2_comp"])
        bar_ev = max(b["identity_eval_comp"], b["nn_eval_comp"])
        r = {"id": sid, "group": S.grp(e), "family": e["family"], "bar_t2": bar_t2, "bar_eval": bar_ev,
             "planted_n": sum(1 for pr in e["planted"] if pr.get("primary", True)),
             "rule_complexity": e["nuisance"]["obs_compression_ratio"]}
        br = blind.get(sid)
        if br and br["ok"]:
            o = br["parsed"]
            r["t1_score"], r["t1_verdict"] = S.structure_score(o)
            r["t2_exact"], r["t2_comp"] = S.score_t2(p, o, ans)
            r["t3_exact"], r["t3_comp"] = S.score_t3(p, o, ans)
            claims, cap = S.score_claims(p, o, e["planted"], cache)
            r["t4"] = Counter(c["status"] for c in claims)
            r["t4_captured"] = cap
            r["t5"] = S.score_code(p, ((o.get("t5") or {}).get("code")), ans, cache)
            r["learned"] = bool((r["t2_comp"] >= bar_t2 + LEARN_MARGIN and r["t2_exact"] >= LEARN_EXACT) or
                                (r["t5"].get("eval_exact") or 0) >= CODE_LEARN_EXACT)
            r["behav_score"] = max(r["t2_comp"] - bar_t2, (r["t5"].get("eval_comp") or 0) - bar_ev)
        fr = fam.get(sid)
        if fr and fr["ok"]:
            o = fr["parsed"]
            r["coherence"] = str(o.get("coherence", "")).upper()
            r["familiar"] = str(o.get("familiar", "")).upper()
            ac = o.get("analogy_code")
            asc = S.score_code(p, ac, ans, cache) if isinstance(ac, str) and "def" in ac else None
            r["analogy_score"] = asc
            r["analogy_class"] = S.analogy_class(o, asc if asc and asc.get("status") == "OK" else None, bar_ev)
            r["analogy_name"] = o.get("analogy")
        rv = reveal.get(sid)
        if rv and rv["ok"]:
            o = rv["parsed"]
            claims, cap = S.score_claims(p, o, e["planted"], cache)
            r["reveal"] = {"coherence": str(o.get("coherence", "")).upper(),
                           "t2": S.score_t2(p, o, ans), "t3": S.score_t3(p, o, ans),
                           "t4": Counter(c["status"] for c in claims), "captured": cap}
        ac = active.get(sid)
        if ac and ac["ok"]:
            o = ac["parsed"]
            ex, comp = S.score_t2(p, o, ans)
            code = S.score_code(p, ((o.get("t5") or {}).get("code")), ans, cache)
            claims, cap = S.score_claims(p, o, e["planted"], cache)
            r["active"] = {"t1": S.structure_score(o), "t2": (ex, comp), "t5": code,
                           "captured": cap, "n_experiments": ac.get("n_experiments"),
                           "learned": bool((comp >= bar_t2 + LEARN_MARGIN and ex >= LEARN_EXACT) or
                                           (code.get("eval_exact") or 0) >= CODE_LEARN_EXACT)}
        pr = prose.get(sid)
        if pr and pr["ok"]:
            r["prose_t2"] = S.score_t2(p, pr["parsed"], ans)
        rows[sid] = r
    return rows, key


def _rate(xs):
    xs = [x for x in xs if x is not None]
    return (float(np.mean(xs)), len(xs)) if xs else (None, 0)


def taxonomy(r, in_reveal, in_active):
    tags = []
    learned = r.get("learned")
    verbal_neg = r.get("t1_verdict") in ("RANDOM", "UNCERTAIN") or r.get("coherence") in ("INCOHERENT", "UNCLEAR")
    captured = any((r.get("t4_captured") or {}).values())
    if learned and verbal_neg:
        tags.append("PREDICTIVE_WITHOUT_EXPLANATION")
    elif not learned:
        if r.get("analogy_class") == "FALSE_COLLAPSE_TO_FAMILIAR":
            tags.append("FALSE_FAMILIAR_COLLAPSE")
        elif r.get("t1_verdict") == "RANDOM":
            tags.append("FALSE_NOISE")
        elif r.get("coherence") == "INCOHERENT":
            tags.append("FALSE_INCOHERENT")
        elif captured:
            tags.append("EXPLANATORY_WITHOUT_PREDICTION")
        elif (r.get("t4") or {}).get("TRUE", 0) > 0 or (r.get("t2_comp", 0) >= r["bar_t2"] + 0.05):
            tags.append("PARTIAL_STRUCTURE")
        elif r.get("t1_verdict") == "RULE" and (r.get("t5") or {}).get("status") == "OK":
            tags.append("RIGHT_STRUCTURE_WRONG_MECHANISM")
        else:
            tags.append("NO_STRUCTURE_DETECTED")
    if not tags:
        return []                                   # not a miss
    if in_active and r.get("active", {}).get("learned") and not learned:
        tags.append("RECOVERED_AFTER_EXPERIMENTATION")
    rv = r.get("reveal")
    if in_reveal and rv and not learned and (rv["t2"][0] >= 0.75 or any(rv["captured"].values())):
        tags.append("RECOVERED_AFTER_RULE_REVEAL")
    return tags


def summarize(model):
    rows, key = per_system(model)
    sub = subsets(key)
    G = defaultdict(list)
    for r in rows.values():
        G[r["group"]].append(r)
    incomp = [r for g in S.INCOMP for r in G[g]]
    A, K = G["A"], G["K"]
    Aall = G["A"] + G["AADV"]
    out = {"model": model, "n_blind": sum(1 for r in rows.values() if "t1_score" in r)}

    # --- metrics by group
    mg = {}
    for g, rs in sorted(G.items()):
        mg[g] = {"n": len(rs),
                 "t1_RULE_rate": _rate([float(r["t1_verdict"] == "RULE") for r in rs if "t1_verdict" in r])[0],
                 "t1_RANDOM_rate": _rate([float(r["t1_verdict"] == "RANDOM") for r in rs if "t1_verdict" in r])[0],
                 "t2_comp": _rate([r.get("t2_comp") for r in rs])[0],
                 "t2_exact": _rate([r.get("t2_exact") for r in rs])[0],
                 "t2_bar": _rate([r["bar_t2"] for r in rs])[0],
                 "t3_comp": _rate([r.get("t3_comp") for r in rs])[0],
                 "code_eval_comp": _rate([(r.get("t5") or {}).get("eval_comp") for r in rs])[0],
                 "code_eval_exact": _rate([(r.get("t5") or {}).get("eval_exact") for r in rs])[0],
                 "code_intervention_exact": _rate([(r.get("t5") or {}).get("intervention_exact") for r in rs])[0],
                 "code_length_median": float(np.median([r["t5"]["length"] for r in rs if (r.get("t5") or {}).get("length")] or [0])),
                 "learned_rate": _rate([float(r["learned"]) for r in rs if "learned" in r])[0],
                 "incoherent_rate": _rate([float(r["coherence"] == "INCOHERENT") for r in rs if "coherence" in r])[0],
                 "familiar_yes_rate": _rate([float(r["familiar"] == "YES") for r in rs if "familiar" in r])[0],
                 "analogy_classes": dict(Counter(r.get("analogy_class") for r in rs if "analogy_class" in r)),
                 "t4_status": dict(sum((r.get("t4") or Counter() for r in rs), Counter()))}
        caps = [v for r in rs for v in (r.get("t4_captured") or {}).values()]
        mg[g]["planted_recall"] = _rate([float(v) for v in caps])
        t4 = mg[g]["t4_status"]
        mg[g]["invariant_precision"] = (t4.get("TRUE", 0) / (t4.get("TRUE", 0) + t4.get("FALSE", 0))
                                        if t4.get("TRUE", 0) + t4.get("FALSE", 0) else None)
    out["by_group"] = mg

    # --- confusion matrices (behavioural labels, not truth)
    def cm(field, labels):
        return {g: dict(Counter(r.get(field) for r in rs if field in r)) for g, rs in sorted(G.items())}
    out["confusion"] = {"t1_verdict": cm("t1_verdict", None), "coherence": cm("coherence", None),
                        "familiar": cm("familiar", None)}

    # --- discrimination
    def aucf(pos, neg, f):
        return S.auc([f(r) for r in pos if f(r) is not None], [f(r) for r in neg if f(r) is not None])
    t1 = lambda r: r.get("t1_score")
    bh = lambda r: r.get("behav_score")
    disc = {}
    for name, f in (("t1", t1), ("behav", bh)):
        disc[f"{name}_K_vs_incomp"] = aucf(K, incomp, f)
        disc[f"{name}_A_vs_incomp"] = aucf(A, incomp, f)
        disc[f"{name}_Aall_vs_incomp"] = aucf(Aall, incomp, f)
        disc[f"{name}_AADV_vs_SEDUCTIVE"] = aucf(G["AADV"], G["N_SEDUCTIVE"], f)
        disc[f"{name}_A_vs_DESTROY"] = aucf(A, G["N_DESTROY"], f)
    out["discrimination"] = disc

    # --- pairs
    pr = S.read(model, "pair")
    pair_rows = []
    for a_id, n_id in sub["pairs"]:
        row = pr.get(a_id)
        if row and row["ok"]:
            ch = str(row["parsed"].get("choice", "")).upper()
            pair_rows.append({"alien": a_id, "null_type": key[n_id]["null_type"],
                              "correct": ch == row["lawful"]})
    by_nt = defaultdict(list)
    for x in pair_rows:
        if x["null_type"] != "DESTROY":
            by_nt["INCOMP"].append(x["correct"])
        by_nt["type:" + x["null_type"]].append(x["correct"])
    out["pairs"] = {k: {"n": len(v), "accuracy": float(np.mean(v))} for k, v in by_nt.items()}

    # --- hypotheses (PREREG s6)
    H = {}
    d = lambda a, b: (S.auc([t1(r) for r in a[0] if t1(r) is not None], [t1(r) for r in a[1] if t1(r) is not None]))
    def diff_auc(f, k_rows, a_rows, n_rows):
        def fn(ab, _):
            kk, aa, nn = ab
            x, y = aucf(kk, nn, f), aucf(aa, nn, f)
            return None if x is None or y is None else x - y
        import random as _r
        rng = _r.Random(S.BOOT_SEED)
        vals = []
        for _ in range(S.BOOT):
            kk = [rng.choice(k_rows) for _ in k_rows]
            aa = [rng.choice(a_rows) for _ in a_rows]
            nn = [rng.choice(n_rows) for _ in n_rows]
            v = fn((kk, aa, nn), None)
            if v is not None:
                vals.append(v)
        vals.sort()
        if not vals or not k_rows or not a_rows or not n_rows:
            return None, (None, None)
        est = aucf(k_rows, n_rows, f) - aucf(a_rows, n_rows, f)
        return est, (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1])

    def decide(est, ci, thr):
        if est is None or ci[0] is None:
            return "NOT_ELIGIBLE"
        if est >= thr and ci[0] > 0:
            return "SUPPORTED"
        if ci[1] < thr / 2 and est <= 0:
            return "NOT_SUPPORTED"
        return "INDETERMINATE"

    for name, f in (("H1_t1", t1), ("H1_behav", bh)):
        est, ci = diff_auc(f, [r for r in K if f(r) is not None], [r for r in A if f(r) is not None],
                           [r for r in incomp if f(r) is not None])
        H[name] = {"estimate": est, "ci95": ci, "decision": decide(est, ci, 0.10)}

    def rate_diff(field_fn, a_rows, k_rows, thr):
        av = [field_fn(r) for r in a_rows if field_fn(r) is not None]
        kv = [field_fn(r) for r in k_rows if field_fn(r) is not None]
        if not av or not kv:
            return {"decision": "NOT_ELIGIBLE"}
        est = float(np.mean(av) - np.mean(kv))
        ci = S.boot_diff(lambda a, b: float(np.mean(a) - np.mean(b)), av, kv)
        return {"estimate": est, "ci95": ci, "n_A": len(av), "n_K": len(kv), "decision": decide(est, ci, thr)}

    false_neg = lambda r: (float(r.get("t1_verdict") == "RANDOM" or r.get("coherence") == "INCOHERENT")
                           if "t1_verdict" in r or "coherence" in r else None)
    H["H2"] = rate_diff(false_neg, A, K, 0.15)
    H["H2_within_family"] = {f: rate_diff(false_neg, [r for r in A if r["family"] == f],
                                          [r for r in K if r["family"] == f], 0.15).get("estimate")
                             for f in ("tab", "graph", "rewrite", "vm", "map")}
    collapse = lambda r: float(r["analogy_class"] == "FALSE_COLLAPSE_TO_FAMILIAR") if "analogy_class" in r else None
    H["H5"] = rate_diff(collapse, A, K, 0.15)

    # H3 active: on the active subset, gap K-A in learned rate, passive vs active
    act = [rows[s] for s in sub["active"] if "active" in rows[s]]
    aa = [r for r in act if r["group"] == "A"]
    kk = [r for r in act if r["group"] == "K"]
    nn = [r for r in act if r["group"].startswith("N_")]
    def gap(rs_k, rs_a, f):
        return (np.mean([f(r) for r in rs_k]) - np.mean([f(r) for r in rs_a])) if rs_k and rs_a else None
    pl = lambda r: float(r.get("learned", False))
    al = lambda r: float(r["active"]["learned"])
    H["H3"] = {"n_A": len(aa), "n_K": len(kk), "n_N": len(nn),
               "passive_gap_K_minus_A": gap(kk, aa, pl), "active_gap_K_minus_A": gap(kk, aa, al),
               "A_learned_passive": _rate([pl(r) for r in aa])[0], "A_learned_active": _rate([al(r) for r in aa])[0],
               "N_learned_active": _rate([al(r) for r in nn])[0],
               "note": "descriptive; underpowered by design (PREREG s6)"}
    g_p, g_a = H["H3"]["passive_gap_K_minus_A"], H["H3"]["active_gap_K_minus_A"]
    H["H3"]["decision"] = ("NOT_ELIGIBLE" if g_p is None or g_a is None else
                           "SUPPORTED" if g_p - g_a >= 0.10 else "INDETERMINATE")

    # H4 reveal: false-incoherence/noise gap A-K with rule revealed vs blind, same systems
    rv = [rows[s] for s in sub["reveal"] if "reveal" in rows[s]]
    ra = [r for r in rv if r["group"] == "A"]
    rk = [r for r in rv if r["group"] == "K"]
    bl_neg = lambda r: false_neg(r)
    rv_neg = lambda r: float(r["reveal"]["coherence"] in ("INCOHERENT", "UNCLEAR"))
    gb = (np.mean([bl_neg(r) for r in ra if bl_neg(r) is not None]) -
          np.mean([bl_neg(r) for r in rk if bl_neg(r) is not None])) if ra and rk else None
    gr = (np.mean([rv_neg(r) for r in ra]) - np.mean([rv_neg(r) for r in rk])) if ra and rk else None
    H["H4"] = {"n_A": len(ra), "n_K": len(rk), "blind_gap": gb, "reveal_gap": gr,
               "reveal_coherent_rate": {g: _rate([float(r["reveal"]["coherence"] == "COHERENT") for r in rv if r["group"] == g])[0]
                                        for g in ("A", "K", "N_DESTROY")},
               "reveal_t2_exact": {g: _rate([r["reveal"]["t2"][0] for r in rv if r["group"] == g])[0]
                                   for g in ("A", "K", "N_DESTROY")},
               "reveal_planted_recall": _rate([float(v) for r in ra for v in r["reveal"]["captured"].values()])}
    H["H4"]["decision"] = ("NOT_ELIGIBLE" if gb is None or gr is None else
                           "SUPPORTED" if gb - gr >= 0.10 else "INDETERMINATE")

    # H6 dissociation: learnable alien, verbally judged random/incoherent
    diss = [r["id"] for r in Aall if r.get("learned") and
            (r.get("t1_verdict") == "RANDOM" or r.get("coherence") == "INCOHERENT")]
    diss_soft = [r["id"] for r in Aall if r.get("learned") and
                 (r.get("t1_verdict") in ("RANDOM", "UNCERTAIN") or r.get("coherence") in ("INCOHERENT", "UNCLEAR"))]
    H["H6"] = {"strict_ids": diss, "soft_ids": diss_soft,
               "decision": "SUPPORTED" if len(diss) >= 2 else "NOT_SUPPORTED"}

    # --- detector validation (directive: critical control)
    auc_a = disc.get("t1_A_vs_incomp")
    ci_lo = None
    if A and incomp:
        vals = S.boot_diff(lambda a, b: S.auc([t1(r) for r in a if t1(r) is not None],
                                              [t1(r) for r in b if t1(r) is not None]), A, incomp)
        ci_lo = vals[0]
    pair_inc = out["pairs"].get("INCOMP", {}).get("accuracy")
    out["detector_validation"] = {
        "t1_auc_A_vs_incomp": auc_a, "ci95_low": ci_lo, "pair_accuracy_incomp": pair_inc,
        "verdict": ("NOVELTY_DETECTOR_VALIDATED" if auc_a is not None and auc_a >= 0.80 and
                    ci_lo is not None and ci_lo >= 0.65 and pair_inc is not None and pair_inc >= 0.80
                    else "NOVELTY_DETECTOR_NOT_VALIDATED")}

    # --- failure taxonomy
    tax = {}
    for r in Aall:
        tags = taxonomy(r, r["id"] in sub["reveal"], r["id"] in sub["active"])
        if tags:
            tax[r["id"]] = tags
    out["failure_taxonomy"] = {"n_misses": len(tax), "primary": dict(Counter(t[0] for t in tax.values())),
                               "all_tags": dict(Counter(x for t in tax.values() for x in t)), "by_system": tax}
    # --- representation ablation
    pr_rows = [r for r in rows.values() if "prose_t2" in r and "t2_comp" in r]
    out["prose_vs_tuple_t2_comp"] = {g: {"tuple": _rate([r["t2_comp"] for r in pr_rows if r["group"] == g])[0],
                                         "prose": _rate([r["prose_t2"][1] for r in pr_rows if r["group"] == g])[0]}
                                     for g in sorted({r["group"] for r in pr_rows})}
    out["hypotheses"] = H
    return out, rows


if __name__ == "__main__":
    model = sys.argv[1]
    res, rows = summarize(model)
    path = os.path.join(RUNS, model, "RESULTS.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"summary": res, "rows": rows}, indent=1, default=lambda o: dict(o) if isinstance(o, Counter) else str(o)) + "\n")
    print(json.dumps({k: res[k] for k in ("n_blind", "discrimination", "pairs", "detector_validation")}, indent=1, default=str))
