"""ATLAS MEASUREMENTS per task (Experiment 2): existence, enumeration hitting cost and rank, viable-intermediate
density, the known-positive route (canonical and credit-favourable), feedback gradient, exact mutator step
probabilities, mutation robustness, revisitability, and a CANDIDATE limit classification.

Definitions (all target-blind where they could guide a search; the witness/test are used only for measurement):
  hitting cost (enumeration)  charges of the keyed TFS-1 walk to the first QUALIFIED program (common.Certifier), per
                              CRN seed; first dev-consistent-but-spurious hits ("false hits") are listed with charges.
  witness rank                static 1-based keyed-walk rank of the (comm-canonical) witness (sample.ranks_of).
  viable intermediate         a program whose exact dev credit is >= 1 but < |dev| (dev-consistent on a non-empty
                              proper subset). density(n) = share of the size-n class (exhaustive if the class is
                              <= exhaustive_cap, else a uniform sample) that is viable; also all-FAIL, dev-consistent
                              and (among dev-consistent) qualified shares, and the exact-credit histogram.
  route                       route.canonical_route (structure only) and route.credit_route (most credit-favourable
                              pruning path, by exact then partial dev credit) -- both are real mutator paths.
  feedback gradient           per route step: exact / partial / magnitude credit, the exact single-attempt step
                              probability p_single, p_none (sampled) and p_eff = p_single / (1 - p_none).
                              unrewarded segment = maximal run of consecutive steps with no strict increase in the
                              channel, closed by the first rewarded step. widest_unrewarded_segment (steps) and
                              crossing_cost_estimate = max over segments of 1 / prod(p_eff) over the segment's steps
                              (a directed-walk estimate, NOT a hitting time).
  mutation robustness         N single mutations of the witness and of each route program: share that stay
                              QUALIFIED (witness), keep exact credit >= parent, raise it, are all-FAIL, and keep the
                              identical dev behaviour.
  revisitability              (i) genotype restore exactness (re-evaluating the stored genotype reproduces the stored
                              dev outputs); (ii) re-encounter cost under enumeration = static rank of every route
                              program; (iii) re-encounter probability from its route predecessor = p_eff.
"""
import time
from typing import Dict, List, Optional, Sequence

from tfs1 import core as C
from tfs1.enum import Enumerator, canon_comm
from tfs1.mutate import Mutator

from . import common as K
from . import route as R
from .sample import ranks_of, sample_uniform


def hitting_cost(task: Dict, lib, seeds: Sequence, budget: int, max_size: int = 8, witness: Optional[str] = None,
                 E: Optional[Enumerator] = None) -> List[Dict]:
    E = E or Enumerator(lib)
    cert = K.Certifier(task, lib, witness)
    rows = []
    for sd in seeds:
        t0 = time.process_time()
        r = E.search(task["dev"], task["output_type"], sd, task["family_id"], budget, max_size, verify=cert.verify)
        rows.append({"seed": sd, "hit": r["hit"], "hit_charge": r["hit_charge"], "program": r["program"],
                     "censored": r["censored"], "charges": r["charges"],
                     "first_false_hits": r["false_hits"][:5], "n_false_hits": len(r["false_hits"]),
                     "complete_through_size": r["complete_through_size"], "units_expanded": r["units_expanded"],
                     "units_promoted": r["units_promoted"], "verify_evals": r["verify_evals"],
                     "cpu_s": round(time.process_time() - t0, 2)})
    return rows


def density(task: Dict, lib, max_n: int = 7, exhaustive_cap: int = 100_000, samples: int = 5000, seed=0,
            E: Optional[Enumerator] = None) -> List[Dict]:
    E = E or Enumerator(lib)
    view = K.LearnerView(task)
    cert = K.Certifier(task, lib)
    T = task["output_type"]
    nd = len(view.dev)
    r = K.rng("DENSITY", task["family_id"], seed)
    out = []
    for n in range(1, max_n + 1):
        tot = E.count(T, (), n)
        if tot == 0:
            out.append({"size": n, "class_size": 0})
            continue
        if tot <= exhaustive_cap:
            terms = [t for t, _s in E.terms(T, (), n)]
            mode = "exhaustive"
        else:
            terms = [sample_uniform(E, T, (), n, r) for _ in range(samples)]
            mode = "uniform_sample"
        hist = [0] * (nd + 1)
        allfail = devc = qual = 0
        for t in terms:
            o = K.outs_of(t, view.dev_inputs, lib)
            k = K.exact_credit(o, view.targets)
            hist[k] += 1
            allfail += all(v == C.FAIL for v in o)
            if k == nd:
                devc += 1
                qual += cert.verify(t)
        m = len(terms)
        out.append({"size": n, "class_size": tot, "mode": mode, "evaluated": m,
                    "viable_share": round(sum(hist[1:nd]) / m, 6), "all_fail_share": round(allfail / m, 6),
                    "dev_consistent": devc, "dev_consistent_share": round(devc / m, 8),
                    "qualified_among_dev_consistent": qual, "exact_credit_hist": hist})
    return out


def _credit_vec(t, view, lib) -> Dict:
    o = K.outs_of(t, view.dev_inputs, lib)
    return {"exact": K.exact_credit(o, view.targets) / max(1, len(view.targets)),
            "partial": round(K.partial_credit(o, view.targets), 6),
            "magnitude": round(K.magnitude_credit(o, view.targets), 6), "outs": o}


def _segments(vals: List[float]) -> List[List[int]]:
    """Unrewarded segments over route steps 1..k (step i goes i-1 -> i): runs of non-increasing steps closed by the
    first rewarded step (if any)."""
    segs, cur = [], []
    for i in range(1, len(vals)):
        cur.append(i)
        if vals[i] > vals[i - 1]:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    return segs


class RouteMeter:
    """Credit vectors per program and exact/effective step probabilities per forward edge (cached)."""

    def __init__(self, view, lib, mut: Mutator, T: str, seed=0, pnone_n: int = 1000):
        self.view, self.lib, self.mut, self.T = view, lib, mut, T
        self.sp = R.StepProb(mut)
        self.rr = K.rng("PNONE", view.family_id, seed)
        self.pnone_n = pnone_n
        self._cv, self._pn, self._pe = {}, {}, {}

    def credit(self, text, term=None):
        c = self._cv.get(text)
        if c is None:
            c = self._cv[text] = _credit_vec(term if term is not None else C.parse(text), self.view, self.lib)
        return c

    def p_none(self, text, term):
        v = self._pn.get(text)
        if v is None:
            v = self._pn[text] = self.sp.p_none(term, self.T, self.rr, self.pnone_n)
        return v

    def edge(self, q_text, q_term, t_text, t_term):
        key = (q_text, t_text)
        v = self._pe.get(key)
        if v is None:
            ps = self.sp.single(q_term, t_term, self.T)
            pn = self.p_none(q_text, q_term)
            v = self._pe[key] = (ps, pn, ps / (1 - pn) if pn < 1 else 0.0)
        return v


def _seg_costs(vals: List[float], peff: List[float]) -> List[float]:
    costs = []
    for sg in _segments(vals):
        p = 1.0
        for i in sg:
            p *= peff[i]
        costs.append(1.0 / p if p > 0 else float("inf"))
    return costs


def route_profile(texts: List[str], terms: List, meter: RouteMeter, density_rows=None) -> Dict:
    view = meter.view
    steps = []
    for i, (tx, tm) in enumerate(zip(texts, terms)):
        cv = meter.credit(tx, tm)
        row = {"i": i, "program": tx, "size": C.size(tm), "exact": cv["exact"], "partial": cv["partial"],
               "magnitude": cv["magnitude"]}
        if i > 0:
            ps, pn, pe = meter.edge(texts[i - 1], terms[i - 1], tx, tm)
            row.update({"p_single": ps, "p_none": pn, "p_eff": pe})
        if density_rows:
            d = next((x for x in density_rows if x["size"] == row["size"] and x.get("exact_credit_hist")), None)
            if d:
                k = round(cv["exact"] * len(view.targets))
                hist = d["exact_credit_hist"]
                row["share_same_size_with_exact_credit_ge"] = round(sum(hist[k:]) / max(1, sum(hist)), 6)
        steps.append(row)
    peff = [1.0] + [s["p_eff"] for s in steps[1:]]
    summary = {}
    for ch in ("exact", "partial", "magnitude"):
        vals = [s[ch] for s in steps]
        costs = _seg_costs(vals, peff)
        inc = sum(1 for a, b in zip(vals, vals[1:]) if b > a)
        dec = sum(1 for a, b in zip(vals, vals[1:]) if b < a)
        summary[ch] = {"values": vals, "strict_increases": inc, "decreases": dec,
                       "flat_steps": len(vals) - 1 - inc - dec, "monotone_nondecreasing": dec == 0,
                       "widest_unrewarded_segment": max((len(s) for s in _segments(vals)), default=0),
                       "crossing_cost_estimate": max(costs) if costs else None, "segment_costs": costs}
    pe = peff[1:]
    summary["guided_route_cost_estimate"] = sum(1.0 / p for p in pe) if pe and all(pe) else float("inf")
    return {"steps": steps, "gradient": summary}


def best_routes(lat: Dict, w_text: str, meter: RouteMeter, cap: int = 200_000) -> Dict:
    """For each credit channel, the lattice path (start -> W) with the smallest crossing_cost_estimate
    (ties: smaller sum of segment costs, then fewer steps, then text). Exhaustive over all pruning paths up to cap."""
    nodes = lat["nodes"]
    ap = R.all_paths(lat, w_text, cap)
    best = {}
    for path in ap["paths"]:
        terms = [nodes[t]["term"] for t in path]
        peff = [1.0] + [meter.edge(path[i - 1], terms[i - 1], path[i], terms[i])[2] for i in range(1, len(path))]
        for ch in ("exact", "partial", "magnitude"):
            vals = [meter.credit(t, tm)[ch] for t, tm in zip(path, terms)]
            costs = _seg_costs(vals, peff)
            key = (max(costs) if costs else 0.0, sum(costs), len(path), path)
            if ch not in best or key < best[ch][0]:
                best[ch] = (key, path)
    return {"n_paths": len(ap["paths"]), "truncated": ap["truncated"],
            "best": {ch: v[1] for ch, v in best.items()}}


def robustness(terms: Sequence, view, cert: Optional[K.Certifier], lib, mut: Mutator, T: str, n: int = 1000,
               seed=0) -> List[Dict]:
    r = K.rng("ROBUST", view.family_id, seed)
    out = []
    for t in terms:
        po = K.outs_of(t, view.dev_inputs, lib)
        pk = K.exact_credit(po, view.targets)
        parent_q = cert.verify(t) if cert is not None and pk == len(view.targets) else False
        keep = up = fail = same = qual = made = 0
        for _ in range(n):
            c = mut.mutate(t, T, r)
            if c is None:
                continue
            made += 1
            o = K.outs_of(c, view.dev_inputs, lib)
            k = K.exact_credit(o, view.targets)
            keep += k >= pk
            up += k > pk
            fail += all(v == C.FAIL for v in o)
            same += o == po
            if parent_q and k == len(view.targets):
                qual += cert.verify(c)
        m = max(1, made)
        out.append({"program": C.to_str(t), "exact_credit": pk, "children": made,
                    "keep_credit_share": round(keep / m, 4), "raise_credit_share": round(up / m, 4),
                    "all_fail_share": round(fail / m, 4), "same_dev_behaviour_share": round(same / m, 4),
                    "stay_qualified_share": round(qual / m, 4) if parent_q else None})
    return out


def atlas(task: Dict, lib=None, witness: Optional[str] = None, seeds: Sequence = (0, 1, 2, 3),
          enum_budget: int = 1_000_000, enum_max_size: int = 8, density_max_n: int = 7, robust_n: int = 1000,
          rank_max_class: int = 7_000_000, max_fill: int = 3, E: Optional[Enumerator] = None) -> Dict:
    t0 = time.process_time()
    witness = witness if witness is not None else task.get("witness")
    E = E or Enumerator(lib)
    mut = Mutator(E, max_fill=max_fill)
    view = K.LearnerView(task)
    cert = K.Certifier(task, lib, witness)
    T = task["output_type"]
    rec = {"atlas_version": K.ATLAS_VERSION, "family_id": task["family_id"], "output_type": T,
           "dev_n": len(task["dev"]), "test_n": len(task["test"]), "dev_test_overlap": task.get("_dev_test_overlap"),
           "library_entries": len(lib) if lib else 0, "params": {"seeds": list(seeds), "enum_budget": enum_budget,
           "enum_max_size": enum_max_size, "density_max_n": density_max_n, "robust_n": robust_n,
           "max_fill": max_fill, "mutator_max_size": mut.max_size}}
    rec["existence"] = K.witness_existence(task, lib, witness)
    rec["hitting_cost_enumeration"] = hitting_cost(task, lib, seeds, enum_budget, enum_max_size, witness, E)
    rec["density"] = density(task, lib, density_max_n, E=E)
    if witness is None or not rec["existence"].get("exists"):
        rec["route"] = None
        rec["cpu_s"] = round(time.process_time() - t0, 1)
        return rec
    W = C.parse(witness)
    wtext = C.to_str(W)
    meter = RouteMeter(view, lib, mut, T)
    canon = R.canonical_route(mut, W, T)
    lat = R.lattice(mut, W, T)
    rec["lattice"] = {"size": len(lat["nodes"]), "truncated": lat["truncated"]}
    bydepth = {}
    for k, nd in lat["nodes"].items():
        bydepth.setdefault(nd["depth"], []).append(meter.credit(k, nd["term"]))
    rec["lattice"]["credit_by_prune_depth"] = {
        str(d): {"n": len(v), "max_exact": max(x["exact"] for x in v), "max_partial": max(x["partial"] for x in v),
                 "mean_exact": round(sum(x["exact"] for x in v) / len(v), 4),
                 "mean_partial": round(sum(x["partial"] for x in v) / len(v), 4)} for d, v in sorted(bydepth.items())}
    nonw = [cv for k, v in bydepth.items() if k > 0 for cv in v]
    rec["lattice"]["any_intermediate_with_exact_credit"] = any(x["exact"] > 0 for x in nonw)
    rec["lattice"]["any_intermediate_with_partial_credit"] = any(x["partial"] > 0 for x in nonw)
    br = best_routes(lat, wtext, meter)
    rec["lattice"]["n_paths"] = br["n_paths"]
    rec["lattice"]["paths_truncated"] = br["truncated"]
    rec["route"] = {"canonical": route_profile([n["text"] for n in canon], [n["term"] for n in canon], meter,
                                               rec["density"])}
    for ch, path in br["best"].items():
        rec["route"]["best_for_" + ch] = route_profile(path, [lat["nodes"][t]["term"] for t in path], meter,
                                                       rec["density"])
    # revisitability: static enumeration ranks of route programs (seed 0) + genotype restore exactness
    rtexts = sorted({s["program"] for r in rec["route"].values() for s in r["steps"]})
    rterms = [C.parse(t) for t in rtexts]
    ranks = ranks_of(E, rterms, T, seeds[0], task["family_id"], rank_max_class)
    restore_ok = all(K.outs_of(C.parse(C.to_str(t)), view.dev_inputs, lib) == K.outs_of(t, view.dev_inputs, lib)
                     for t in rterms)
    rec["revisitability"] = {"genotype_restore_exact": restore_ok,
                             "enumeration_rank_seed0": dict(zip(rtexts, ranks)),
                             "witness_rank_by_seed": {str(sd): ranks_of(E, [W], T, sd, task["family_id"],
                                                                         rank_max_class)[0] for sd in seeds}}
    rec["robustness"] = robustness([W] + [n["term"] for n in canon[:-1]], view, cert, lib, mut, T, robust_n)
    rec["cpu_s"] = round(time.process_time() - t0, 1)
    return rec


# ================================================================ candidate classification
def classify(rec: Dict, budget: int, scale: int = 16, arm_results: Optional[Dict] = None,
             search_channel: str = "exact", alt_channels=("partial",), diag_channels=("magnitude",)) -> Dict:
    """CANDIDATE labels (thresholds are frozen-parameter candidates, not frozen). Separate verdicts for
    enumeration (no credit use) and for credit-guided local search (the mutator arms)."""
    ex = rec.get("existence", {})
    out = {"budget": budget, "scale": scale, "notes": []}
    if ex.get("exists") is False:
        out["enumeration"] = out["local_search"] = "MEASUREMENT_FAILURE"
        out["notes"].append("witness does not verify: %s" % ex.get("reason") or "dev/test")
        return out
    if ex.get("exists") is None:
        out["notes"].append("no witness: route-based labels unavailable")
    if ex.get("size_promoted", 0) > rec["params"]["mutator_max_size"]:
        out["enumeration"] = out["local_search"] = "REPRESENTATION_LIMIT"
        out["notes"].append("witness larger than the mutator's max_size")
        return out
    hc = rec["hitting_cost_enumeration"]
    hits = [r["hit_charge"] for r in hc if r["hit"] and r["hit_charge"] <= budget]
    wr = rec.get("revisitability", {}).get("witness_rank_by_seed", {})
    rank_lo = [v["rank"] if v.get("rank") else (v.get("bracket") or [None])[0] for v in wr.values()]
    if len(hits) == len(hc):
        out["enumeration"] = "REACHED"
    elif rank_lo and all(r is not None and r <= scale * budget for r in rank_lo):
        out["enumeration"] = "RARITY_LIMIT"
    elif rank_lo and any(r is not None for r in rank_lo):
        out["enumeration"] = "RARITY_LIMIT_BEYOND_%dx" % scale
    else:
        out["enumeration"] = "UNRESOLVED"
    rt = rec.get("route")
    if not rt:
        out["local_search"] = "UNRESOLVED"
        return out
    cross = {ch: rt["best_for_" + ch]["gradient"][ch]["crossing_cost_estimate"]
             for ch in (search_channel,) + tuple(alt_channels) + tuple(diag_channels)}
    out["crossing_cost_estimate"] = cross
    out["widest_unrewarded_segment_search_channel"] = \
        rt["best_for_" + search_channel]["gradient"][search_channel]["widest_unrewarded_segment"]
    lim = scale * budget
    if arm_results and any(arm_results.get(a, 0) > 0 for a in ("A-FRESH", "A-CHAIN")):
        out["local_search"] = "REACHED"
    elif cross[search_channel] <= lim:
        out["local_search"] = "RARITY_LIMIT"
    elif any(cross[ch] <= lim for ch in alt_channels):
        out["local_search"] = "CREDIT_LIMIT"
        out["notes"].append("search channel %r cannot cross within %dx; alternative channel(s) %s can" %
                            (search_channel, scale, [ch for ch in alt_channels if cross[ch] <= lim]))
    else:
        out["local_search"] = "REACHABILITY_DESERT"
        for ch in diag_channels:
            if cross[ch] <= lim:
                out["notes"].append("diagnostic: the %s channel (a numeric-closeness heuristic, not a correctness "
                                    "credit; used by no search here) WOULD see a gradient (crossing estimate %.3g)"
                                    % (ch, cross[ch]))
    return out
    g_cf = rt["credit_favourable"]["gradient"]
    sc = {ch: g_cf[ch] for ch in search_channels}
    best = min(sc.values(), key=lambda g: g["crossing_cost_estimate"])
    cross = best["crossing_cost_estimate"]
    out["crossing_cost_estimate_best_search_channel"] = cross
    out["widest_unrewarded_segment_exact"] = g_cf["exact"]["widest_unrewarded_segment"]
    if arm_results and any(arm_results.get(a, 0) > 0 for a in ("A-FRESH", "A-CHAIN")):
        out["local_search"] = "REACHED"
    elif cross <= scale * budget:
        out["local_search"] = "RARITY_LIMIT"
    else:
        ex_c = g_cf["exact"]["crossing_cost_estimate"]
        other = [ch for ch in search_channels if ch != "exact" and g_cf[ch]["crossing_cost_estimate"] < ex_c]
        out["local_search"] = "CREDIT_LIMIT" if (other and g_cf[other[0]]["crossing_cost_estimate"]
                                                   <= scale * budget) else "REACHABILITY_DESERT"
    mg = g_cf["magnitude"]
    if out["local_search"] == "REACHABILITY_DESERT" and mg["crossing_cost_estimate"] <= scale * budget:
        out["notes"].append("diagnostic: the magnitude (numeric-closeness) channel, not used by any search here, "
                            "WOULD see a gradient (crossing estimate %.3g)" % mg["crossing_cost_estimate"])
    return out
