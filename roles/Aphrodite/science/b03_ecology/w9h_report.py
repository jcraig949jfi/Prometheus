"""W9-H pilot report: admission statistics, reachability, certification, tribunal FP/FN, semantic diversity and
distribution shift vs W8 LIN. Reads the pilot directory only; writes W9H_PILOT_METRICS.json."""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w9h_grammar as W  # noqa: E402
import w9h_admit as A  # noqa: E402
from a18 import I  # noqa: E402

W8 = HERE.parent / "arc3" / "w8_lin_generator" / "W8_SUPPLIES.json"


def top_op(body):
    return I.normalise(I.parse(body))[0]


def ops_of(body):
    out = []

    def walk(t):
        if t[1] and not t[0].startswith(("var:", "const:")):
            out.append(t[0])
            for c in t[1]:
                walk(c)
    walk(I.normalise(I.parse(body)))
    return out


def depth(body):
    def d(t):
        return 0 if not t[1] or t[0].startswith(("var:", "const:")) else 1 + max(d(c) for c in t[1])
    return d(I.normalise(I.parse(body)))


def additive_one_hole(body):
    """W8-audit shape: (acc + X) / (acc - X) / (X + v) at the root (any X)."""
    t = I.normalise(I.parse(body))
    if t[0] not in ("add", "sub") or len(t[1]) != 2:
        return False
    a, b = t[1]
    acc = ("var:acc", [])
    v = ("var:v", [])
    return a == acc or (t[0] == "add" and (b == acc or a == v or b == v))


def hist(xs):
    c = Counter(xs)
    n = sum(c.values()) or 1
    return {k: round(v / n, 4) for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))}


def tvd(p, q):
    ks = set(p) | set(q)
    return round(0.5 * sum(abs(p.get(k, 0) - q.get(k, 0)) for k in ks), 4)


def profile(bodies):
    import ruler_v2 as R
    return {"top_op": hist(top_op(b) for b in bodies),
            "all_ops": hist(o for b in bodies for o in ops_of(b)),
            "depth": hist(depth(b) for b in bodies),
            "fclass": hist(R.fclass(b) for b in bodies),
            "additive_one_hole_share": round(sum(additive_one_hole(b) for b in bodies) / max(1, len(bodies)), 4),
            "nonadditive_fclass_share": round(sum(R.fclass(b) == "OTHER" for b in bodies) / max(1, len(bodies)), 4),
            "n": len(bodies)}


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 3), round(min(1, c + h), 3)]


def report(pdir):
    W.init()
    pdir = Path(pdir)
    sups = json.loads((pdir / "W9H_SUPPLIES.json").read_text())
    truths = json.loads((pdir / "W9H_TRUTH.json").read_text())
    rows = A.rdl(pdir / "W9H_FOUNDRY.jsonl")
    certs = {r["name"]: r for r in A.rdl(pdir / "W9H_CERTIFY.jsonl")}
    by = {r["name"]: r for r in rows}
    adm = A.admit(rows, truths)
    M = {"config_sha": W.config_sha(), "seeds": sorted(sups)}

    # ---------------- generator + admission yield
    gen = {}
    for k, s in sups.items():
        for lv, x in s["stats"]["by_level"].items():
            g = gen.setdefault(lv, Counter())
            g["generator_proposals"] += x["proposals"]
            g["generated"] += x["admitted"]
    for n, a in adm.items():
        g = gen[a["level"]]
        r = by.get(n, {})
        g["Q2"] += r.get("Q2_size") is not None
        g["T4_qualified"] += bool(r.get("T4_qualified"))
        g["admitted"] += a["admitted"]
        g["why_not:%s" % a["why_not"]] += not a["admitted"]
    yld = {}
    for lv, g in sorted(gen.items()):
        yld[lv] = dict(g, admitted_per_generated=round(g["admitted"] / max(1, g["generated"]), 3),
                       admitted_per_proposal=round(g["admitted"] / max(1, g["generator_proposals"]), 4))
    tot = Counter()
    for g in gen.values():
        tot.update(g)
    yld["ALL"] = dict(tot, admitted_per_generated=round(tot["admitted"] / max(1, tot["generated"]), 3),
                      admitted_per_proposal=round(tot["admitted"] / max(1, tot["generator_proposals"]), 4))
    M["GENERATOR_ADMISSION_YIELD"] = yld

    # ---------------- strata
    strata = defaultdict(Counter)
    for k, tr in truths.items():
        mst = {m["id"]: m["stratum"] for m in tr["mechanisms"]}
        cst = {c["id"]: "%s>%s" % tuple(c["strata"]) for c in tr["compositions"]}
        for n, meta in tr["families"].items():
            lab = "L0" if meta["level"] == "L0" else (mst.get(meta["src"]) if meta["level"] == "L1"
                                                     else cst.get(meta["src"]))
            strata["%s:%s" % (meta["level"], lab)]["generated"] += 1
            strata["%s:%s" % (meta["level"], lab)]["admitted"] += adm[n]["admitted"]
    M["STRATUM_SIZES"] = {k: dict(v) for k, v in sorted(strata.items())}
    M["MECHANISMS"] = {k: [[m["id"], m["stratum"], m["shape"], m["schema"]] for m in tr["mechanisms"]]
                       for k, tr in truths.items()}
    M["COMPOSITIONS"] = {k: [[c["id"], c["outer"], c["inner"], c["schema"], c["screen"].get("w5_share")]
                             for c in tr["compositions"]] for k, tr in truths.items()}

    # ---------------- pristine reachability (admitted families)
    pr = defaultdict(Counter)
    for n, a in adm.items():
        if not a["admitted"]:
            continue
        r = by[n]
        c = pr[a["level"]]
        c["n"] += 1
        c["p30k>0"] += r.get("p_PRISTINE", 0) > 0
        c["cells30k_reached"] += round(4 * r.get("p_PRISTINE", 0))
        c["cells30k"] += 4
        tx = r.get("PRISTINE_TX", [])
        c["reached1M_any"] += any(not x["censored"] for x in tx)
        c["cells1M_reached"] += sum(not x["censored"] for x in tx)
        c["cells1M"] += len(tx)
    M["PRISTINE_REACHABILITY"] = {lv: dict(c, share_p30k=round(c["p30k>0"] / max(1, c["n"]), 3),
                                           share_1M=round(c["reached1M_any"] / max(1, c["n"]), 3))
                                  for lv, c in sorted(pr.items())}

    # ---------------- certification / promoted reachability
    cr = defaultdict(lambda: defaultdict(Counter))
    cert_list = []
    for n, c in certs.items():
        a = adm.get(n)
        if not a:
            continue
        grp = "admitted" if a["admitted"] else "T4q_not_admitted"
        for lib, s in c["summary"].items():
            x = cr["%s/%s" % (c["level"], grp)][lib]
            x["families"] += 1
            x["dev_cells_reached"] += s["dev_reached"]
            x["dev_cells"] += len(s["dev_charges"])
            x["tx_cells_reached"] += s["tx_reached"]
            x["tx_cells"] += len(s["tx_charges"])
            x["fam_reached_1M"] += s["tx_reached"] >= 1
            x["fam_reached_30k"] += s["dev_reached"] >= 1
        if a["admitted"]:
            cert_list.append({"name": n, "seed": a["seed"], "level": c["level"], "src": c["src"],
                              "in_W5": a["in_W5"], "CERTIFIED": c["CERTIFIED"],
                              "CERTIFIED_ORACLE": c["CERTIFIED_ORACLE"],
                              "tx_reached": {k: v["tx_reached"] for k, v in c["summary"].items()},
                              "dev_reached": {k: v["dev_reached"] for k, v in c["summary"].items()}})
    M["REACHABILITY_BY_LIBRARY"] = {g: {lib: dict(x, fam_share_1M=round(x["fam_reached_1M"] / max(1, x["families"]), 3),
                                                  fam_share_30k=round(x["fam_reached_30k"] / max(1, x["families"]), 3))
                                        for lib, x in d.items()} for g, d in sorted(cr.items())}
    l2 = [c for c in cert_list if c["level"] == "L2"]
    l1 = [c for c in cert_list if c["level"] == "L1"]
    M["DEPTH_TWO_WITNESS_COUNT"] = {
        "generated_L2": sum(1 for a in adm.values() if a["level"] == "L2"),
        "T4_qualified_L2": sum(1 for n, a in adm.items() if a["level"] == "L2" and by.get(n, {}).get("T4_qualified")),
        "admitted_L2": sum(1 for a in adm.values() if a["level"] == "L2" and a["admitted"]),
        "admitted_L2_outside_W5": sum(1 for a in adm.values() if a["level"] == "L2" and a["admitted"] and not a["in_W5"]),
        "certified_L2": sum(c["CERTIFIED"] for c in l2),
        "certified_L2_outside_W5": sum(c["CERTIFIED"] and not c["in_W5"] for c in l2),
        "certified_oracle_L2": sum(bool(c["CERTIFIED_ORACLE"]) for c in l2),
        "certified_L2_ci95": wilson(sum(c["CERTIFIED"] for c in l2), len(l2)),
        "per_seed_certified_L2": dict(Counter(c["seed"] for c in l2 if c["CERTIFIED"])),
        "distinct_compositions_with_certified_family": len({(c["seed"], c["src"]) for c in l2 if c["CERTIFIED"]}),
        "certified_L1": sum(c["CERTIFIED"] for c in l1), "certified_L1_of": len(l1),
    }
    M["CERTIFIED_FAMILIES"] = cert_list

    # ---------------- tribunal FP / FN (every qualified walk endpoint in foundry TX + certification)
    q = fp1 = fp2 = spur = fn = 0
    def acc_walk(x):
        nonlocal q, fp1, fp2, spur, fn
        spur += x.get("spurious", 0)
        fn += x.get("fn", 0)
        if not x["censored"]:
            q += 1
            fp1 += not x.get("equal_B1", True)
            fp2 += not x.get("equal_B2", True)
    for r in rows:
        for x in r.get("PRISTINE_TX", []):
            acc_walk(x)
    for c in certs.values():
        for lib, v in c["walks"].items():
            if lib == "PRISTINE":            # the PRISTINE 1M walks repeat the foundry's (same cells): count dev only
                for x in v["dev"]:
                    acc_walk(x)
                continue
            for x in v["dev"] + v["tx"]:
                acc_walk(x)
    M["FALSE_POSITIVE_RATE"] = {"qualified_endpoints": q, "fp_vs_B1": fp1, "fp_vs_B2_audit": fp2,
                                "rate_B1": round(fp1 / max(1, q), 4), "rate_B2": round(fp2 / max(1, q), 4),
                                "rate_B2_ci95": wilson(fp2, q),
                                "spurious_rejected": spur, "fn_rejected_but_B1_equal": fn,
                                "fn_rate": round(fn / max(1, spur), 4)}

    # ---------------- semantic diversity
    div = {}
    for k in sorted(sups):
        names = [n for n, a in adm.items() if a["seed"] == k and a["admitted"]]
        progs = [("fold", by[n]["init"], by[n]["body"], by[n]["final"]) for n in names]
        bids = {I.behavior_id(p, True) for p in progs}
        import ruler_v2 as R
        div[k] = {"admitted": len(names), "behaviour_classes": len(bids),
                  "body_vec_classes": len({R.vec(p[2]) for p in progs}),
                  "fclass": dict(Counter(R.fclass(p[2]) for p in progs)),
                  "levels": dict(Counter(adm[n]["level"] for n in names))}
    M["SEMANTIC_CLASS_DIVERSITY"] = div

    # ---------------- distribution shift vs W8 LIN
    w8 = json.loads(W8.read_text())
    w8b = [f[2] for s in range(8) for f in w8["LIN:%d" % s]["families"]]
    gen_b = [f[2] for k in sups for f in sups[k]["families"]]
    adm_b = [by[n]["body"] for n, a in adm.items() if a["admitted"]]
    pw8, pg, pa = profile(w8b), profile(gen_b), profile(adm_b)
    M["DISTRIBUTION_SHIFT"] = {"W8_LIN_0_7": pw8, "W9H_generated": pg, "W9H_admitted": pa,
                               "TVD_generated_vs_W8": {k: tvd(pg[k], pw8[k]) for k in ("top_op", "all_ops", "depth",
                                                                                        "fclass")},
                               "TVD_admitted_vs_W8": {k: tvd(pa[k], pw8[k]) for k in ("top_op", "all_ops", "depth",
                                                                                       "fclass")}}

    # ---------------- cost
    fs = [r.get("seconds", 0) for r in rows]
    cs = [c["seconds"] for c in certs.values()]
    M["COST"] = {"foundry_cpu_s_total": round(sum(fs)), "foundry_cpu_s_per_family": round(sum(fs) / max(1, len(fs)), 1),
                 "certify_cpu_s_total": round(sum(cs)),
                 "certify_cpu_s_per_family": {lv: round(sum(c["seconds"] for c in certs.values() if c["level"] == lv)
                                                        / max(1, sum(1 for c in certs.values() if c["level"] == lv)), 1)
                                              for lv in ("L1", "L2")},
                 "generator_s_per_seed": {k: s["stats"]["seconds"] for k, s in sups.items()}}
    (pdir / "W9H_PILOT_METRICS.json").write_text(json.dumps(M, indent=1, sort_keys=True, default=str))
    print(json.dumps({k: M[k] for k in ("GENERATOR_ADMISSION_YIELD", "PRISTINE_REACHABILITY", "DEPTH_TWO_WITNESS_COUNT",
                                        "FALSE_POSITIVE_RATE", "COST")}, indent=1, default=str))
    return M


if __name__ == "__main__":
    report(sys.argv[1] if len(sys.argv) > 1 else HERE / "pilot")
