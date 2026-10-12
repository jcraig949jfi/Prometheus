"""BETA-03 W12: SELECTION-OVERRIDE ORACLE BOUND (pre-registration: beta03/windows/W12_SELECTION_ORACLE_PREREG.md).

E6's negative diagnosis located the dominant per-pair break at SELECTION (15/22): promoted-dependent schemas are derived
(often eligible) but g11 selects plain schemas. Question: if selection were perfect among the promoted-dependent schemas
arm D actually DERIVED, would the inherited library ENABLE acquisition beyond the pristine recipient on the common
residual? Each non-trivial derived promoted-dependent schema S (not a bare P_x({H})) of arm D (L_g11|w5p_g11_O10) is
built as library [w5p schema_entry(S, reg)] + the pair's inherited L_g11 start (reg = promote_start(L_g11)), and walked
on the pair's E1 common-residual families (both cells, cap 1M). Per pair, the BEST such library (post-hoc max) is an
ORACLE UPPER BOUND on selection. No new donor runs.
Stages: build | walk [w] | report
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402

import b03  # noqa: E402   (b02 first: a18.TAG guard)
import b02  # noqa: E402

R = b02.R
E1D, E5D = b03.E1D, b03.B03 / "E5N"
W12 = b03.B03 / "W12"
BARE = re.compile(r"P_[0-9a-f]+\(\{H\}\)")
log, wj, rj, sha = b02.log, b02.wj, b02.rj, b02.sha


def _w5():
    sys.path.insert(0, str(b03.ROOT / "engine"))
    from w5p import donor as WD
    return WD


def build():
    W12.mkdir(parents=True, exist_ok=True)
    WD = _w5()
    import a18  # noqa: F401  (after b02)
    L = b03._libs_checked()
    C = rj(E1D / "E1_COMMON_RESIDUAL.json")["common_residual"]
    rows = {x["seed"]: x for x in R.rdl(E5D / "E5N_RECIP.jsonl") if x["tag"] == "L_g11|w5p_g11_O10"}
    libs = {}
    for d, n in L["pairs"]:
        start = L["libraries"][str(d)]["L_g11"]
        reg = WD.promote_start(start)
        cands = [s for s in (rows[n].get("derived_schemas") or []) if "P_" in s and not BARE.fullmatch(s.strip())]
        out = []
        for k, s in enumerate(sorted(set(cands))):
            e = WD.schema_entry("w12_%d" % k, s, reg)
            out.append({"schema": s, "entries": [e] + start})
        libs[str(n)] = {"donor": d, "common": C[str(n)], "candidates": out}
    rec = {"libraries": libs}
    rec["sha256"] = sha(rec)
    wj(W12 / "W12_LIBRARIES.json", rec)
    log("W12 build: %d pairs, %d candidate libraries; sha %s" % (
        len(libs), sum(len(v["candidates"]) for v in libs.values()), rec["sha256"][:16]))


def walk(w=4):
    L = rj(W12 / "W12_LIBRARIES.json")
    assert sha({"libraries": L["libraries"]}) == L["sha256"], "W12 library hash mismatch"
    PB = rj(b02.SUP / "PLAN_B.json")
    keys, todo, index = {}, {}, []
    for n, v in L["libraries"].items():
        fams = {f["name"]: f for f in b02._tr(PB["plan"][n], int(n))}
        for c in v["candidates"]:
            k = b02._key(c["entries"], keys)
            for fn in v["common"]:
                for ci in range(2):
                    index.append({"seed": int(n), "schema": c["schema"], "family": fn, "cell": ci, "lib": k})
                    todo.setdefault((k, fn, ci), (k, keys[k], fams[fn], ci))
    wj(W12 / "W12_INDEX.json", {"index": index})
    have = set()
    for p in (E1D / "E1_START_WALKS.jsonl", E1D / "E1_RECIP_WALKS.jsonl", E5D / "E5N_RECIP_WALKS.jsonl"):
        have |= {(x["lib"], x["family"], x["cell"]) for x in R.rdl(p)}
    b02._pool_walks([vv for kk, vv in todo.items() if kk not in have], W12 / "W12_WALKS.jsonl", w, "W12")


def report():
    """Frozen rules: beta03/windows/W12_SELECTION_ORACLE_PREREG.md."""
    L = rj(W12 / "W12_LIBRARIES.json")
    W = {}
    for p in (E1D / "E1_START_WALKS.jsonl", E1D / "E1_RECIP_WALKS.jsonl", E5D / "E5N_RECIP_WALKS.jsonl",
              W12 / "W12_WALKS.jsonl"):
        for x in R.rdl(p):
            W[(x["lib"], x["family"], x["cell"])] = x["result"]
    idx = rj(W12 / "W12_INDEX.json")["index"]
    acq = {}
    for e in idx:
        k = (e["seed"], e["schema"])
        acq.setdefault(k, set())
        if b03._ok(W.get((e["lib"], e["family"], e["cell"]))):
            acq[k].add(e["family"])
    e5 = rj(E5D / "E5N_RESULT.json")["acq_common_per_pair"]
    g = lambda t, n: e5[t][str(n)] if str(n) in e5[t] else e5[t][n]  # noqa: E731
    seeds = sorted(int(n) for n in L["libraries"])
    best = {n: max([len(acq[(n, c["schema"])]) for c in L["libraries"][str(n)]["candidates"]], default=0)
            for n in seeds}
    nc = {n: len(L["libraries"][str(n)]["candidates"]) for n in seeds}
    vsC = b02.flip_test([best[n] - g("L_P|w5p_g11_O10", n) for n in seeds])
    vsD = b02.flip_test([best[n] - g("L_g11|w5p_g11_O10", n) for n in seeds])
    pos = vsC["p_one_sided"] < 0.05 and vsC["sum"] > 0
    res = {"pairs": seeds, "candidates_per_pair": nc, "oracle_best_acq_common": best,
           "oracle_total": sum(best.values()),
           "C_total": sum(g("L_P|w5p_g11_O10", n) for n in seeds),
           "D_selected_total": sum(g("L_g11|w5p_g11_O10", n) for n in seeds),
           "oracle_vs_C": vsC, "oracle_vs_D_selected": vsD,
           "ORACLE_SELECTION_ENABLES": pos,
           "reading": ("UPPER BOUND: perfect selection among derived promoted-dependent schemas could enable learning "
                       "beyond pristine (selection is a binding limit on this substrate)") if pos else
                      ("even ORACLE selection among derived promoted-dependent schemas does not enable learning beyond "
                       "pristine: the binding limit is upstream of selection (candidacy/representation)")}
    wj(W12 / "W12_RESULT.json", res)
    log("W12 ORACLE_SELECTION_ENABLES %s oracle %d vs C %d vs D %d" % (pos, res["oracle_total"], res["C_total"],
                                                                      res["D_selected_total"]))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    w = int(a[-1]) if a and a[-1].isdigit() else 4
    {"build": build, "walk": lambda: walk(w), "report": report}[a[0]]()
