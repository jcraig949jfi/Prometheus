"""Phase 1 census runner. Executes PREREG-CENSUS against one grammar basis.

Usage: python run_census.py G1
Writes ledgers/census_<basis>.json and ledgers/census_<basis>_classes.jsonl
"""
import json
import sys
import time
import random
import itertools

from d2 import probes, census, classify
from d2.core import vhash, ser

LEGACY = set(classify.LEGACY)
SUBSTANTIVE = set(classify.SUBSTANTIVE)


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def spearman(a, b):
    def rk(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    ra, rb = rk(a), rk(b)
    n = len(a)
    ma = sum(ra) / n
    mb = sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    da = sum((ra[i] - ma) ** 2 for i in range(n)) ** 0.5
    db = sum((rb[i] - mb) ** 2 for i in range(n)) ** 0.5
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def gates(lab, n_struct, n_sem12, n_sem24):
    nt = [v for v in lab.values() if v[0] == "LIVE"]
    n = len(nt)
    if n == 0:
        return None
    leg = [v for v in nt if v[1] & LEGACY]
    non = [v for v in nt if not (v[1] & LEGACY)]
    r2 = [v for v in non if not (v[2] & SUBSTANTIVE)]
    audited = [v for v in non if v[2] & SUBSTANTIVE]
    mL = median([v[3] for v in leg])
    mN = median([v[3] for v in non])
    prod = [v for v in nt if v[7]]
    prod_leg = [v for v in prod if v[1] & LEGACY]
    return {
        "n_nontrivial": n,
        "n_legacy": len(leg),
        "n_nonlegacy": len(non),
        "n_audited_residual": len(audited),
        "n_R2": len(r2),
        "legacy_share": len(leg) / n,
        "R2_share": len(r2) / n,
        "worst_share": (len(leg) + len(r2)) / n,
        "median_minsize_legacy": mL,
        "median_minsize_nonlegacy": mN,
        "CG_B_struct_classes": n_struct,
        "CG_B_pass": n_struct >= 500,
        "CG_C_pass": (len(leg) / n) <= 0.60,
        "CG_C_margin": 0.60 - len(leg) / n,
        "CG_Cworst_pass": ((len(leg) + len(r2)) / n) <= 0.60,
        "CG_Cworst_margin": 0.60 - (len(leg) + len(r2)) / n,
        "CG_D_pass": (mL is not None and mN is not None and mL >= mN - 1.0),
        "CG_D_margin": (mL - (mN - 1.0)) if (mL is not None and mN is not None) else None,
        "CG_E_pass": (len(r2) / n) <= 0.25,
        "CG_G_delta": abs(n_sem24 - n_sem12) / max(1, n_sem12),
        "CG_G_pass": abs(n_sem24 - n_sem12) / max(1, n_sem12) <= 0.10,
        "productive_n": len(prod),
        "productive_legacy_share": (len(prod_leg) / len(prod)) if prod else None,
        "family_counts": _famcount(nt),
    }


def _famcount(nt):
    c = {}
    for v in nt:
        key = "+".join(sorted(v[1])) if v[1] else "OTHER"
        c[key] = c.get(key, 0) + 1
    return dict(sorted(c.items(), key=lambda kv: -kv[1]))


def main(which):
    if which == "G1":
        from d2 import g1 as basis
        Enum = basis.Enum
        nterm, nbterm, nvf, nbf = len(basis.V_TERMS), len(basis.B_TERMS), len(basis.V_FORMS), len(basis.B_FORMS)
    elif which == "G2":
        from d2 import g2 as basis
        Enum = basis.Enum
        nterm, nbterm, nvf, nbf = basis.ORDER_DIMS
    elif which == "G3B":
        from d2 import g3b as basis
        Enum = basis.Enum
        nterm, nbterm, nvf, nbf = basis.ORDER_DIMS
    elif which == "G3":
        from d2 import g3 as basis
        Enum = basis.Enum
        nterm, nbterm, nvf, nbf = basis.ORDER_DIMS
    else:
        raise SystemExit("unknown basis")

    HORIZON = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    ORD_HORIZON = HORIZON - 1

    t0 = time.time()
    E = Enum()
    C = census.Census(basis, probes.A, probes.I12, probes.I24)
    rec = C.scan(E, HORIZON, per_term_labels_upto=ORD_HORIZON)
    print("scan done", rec["seconds"], "s  total", rec["n_total"],
          "dead", rec["n_dead"], "struct", rec["n_struct_classes"],
          "sem12", rec["n_sem_classes_I12"], "sem24", rec["n_sem_classes_I24"])

    idh = [h for h, r in rec["classes"].items() if r[3] == "x"]
    idh = idh[0] if idh else None
    cp = C.class_pairs(rec["classes"], identity_h=idh)
    print("class pairs done", round(time.time() - t0, 1), "s")

    sens = {}
    for c in (0.7, 0.8, 0.9, 1.0):
        lab = C.label_at(cp, c)
        g = gates(lab, rec["n_struct_classes"], rec["n_sem_classes_I12"], rec["n_sem_classes_I24"])
        sens[str(c)] = g
        if c == 0.9:
            main_lab = lab
            main_g = g
    print("classified", round(time.time() - t0, 1), "s")

    # ---- CG-C threshold sensitivity (0.40..0.80)
    ls = main_g["legacy_share"]
    ws = main_g["worst_share"]
    thr_sens = {str(round(t, 2)): {"CG_C": ls <= t, "CG_Cworst": ws <= t}
                for t in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]}
    d_sens = {str(d): (main_g["median_minsize_legacy"] >= main_g["median_minsize_nonlegacy"] - d)
              for d in (0.5, 1.0, 1.5, 2.0)}

    # ---- CG-F ordering battery
    fams = list(classify.LEGACY) + ["NONLEGACY"]
    pt = rec["per_term_labels"]
    vecs = []
    orders = []
    for oi in range(12):
        if oi == 0:
            perms = (list(range(nterm)), list(range(nbterm)), list(range(nvf)), list(range(nbf)))
            tag = "declaration"
        elif oi == 1:
            perms = (list(range(nterm))[::-1], list(range(nbterm))[::-1],
                     list(range(nvf))[::-1], list(range(nbf))[::-1])
            tag = "reverse"
        else:
            rnd = random.Random(oi - 1)
            perms = tuple(rnd.sample(range(k), k) for k in (nterm, nbterm, nvf, nbf))
            tag = "seed%d" % (oi - 1)
        EO = Enum(*perms)
        minrank = {f: None for f in fams}
        minsize = {f: None for f in fams}
        for r, t in EO.stream(ORD_HORIZON):
            labs = pt.get(t)
            if labs is None:
                continue
            keys = list(labs) if labs else ["NONLEGACY"]
            for f in keys:
                if f in minrank and minrank[f] is None:
                    minrank[f] = r
                sz = basis.size(t)
                if f in minsize and (minsize[f] is None or sz < minsize[f]):
                    minsize[f] = sz
        orders.append({"tag": tag, "minrank": minrank, "minsize": minsize})
        vecs.append([minrank[f] if minrank[f] is not None else 10 ** 9 for f in fams])

    rhos = [spearman(vecs[i], vecs[j]) for i, j in itertools.combinations(range(len(vecs)), 2)]
    size_invariant = all(o["minsize"] == orders[0]["minsize"] for o in orders)
    cgf = {"median_rho": median(rhos), "min_rho": min(rhos), "max_rho": max(rhos),
           "minsize_invariant": size_invariant,
           "rank_claims_robust": median(rhos) >= 0.8,
           "families": fams,
           "orderings": orders}

    st4 = main_g["CG_B_pass"] and main_g["CG_C_pass"] and main_g["CG_Cworst_pass"] and main_g["CG_D_pass"]
    cgh = all((sens[k]["CG_C_pass"] == main_g["CG_C_pass"] and
               sens[k]["CG_Cworst_pass"] == main_g["CG_Cworst_pass"]) for k in sens)

    out = {
        "basis": which,
        "horizon": HORIZON,
        "ordering_battery_horizon": ORD_HORIZON,
        "physics": {"eval_step_limit": census.LIMIT, "depth_limit": census.DMAX},
        "probe_hash_A": vhash(tuple(probes.A)),
        "probe_hash_I12": vhash(tuple(probes.I12)),
        "probe_hash_I24": vhash(tuple(probes.I24)),
        "counts": {k: rec[k] for k in ("n_total", "n_dead", "n_live", "n_struct_classes",
                                       "n_sem_classes_I12", "n_sem_classes_I24", "evals", "seconds")},
        "error_kinds": rec["errkinds"],
        "class_kinds": _kindcount(main_lab),
        "gates": main_g,
        "CG_H_invariant": cgh,
        "CG_H_detail": {k: {"legacy_share": v["legacy_share"], "worst_share": v["worst_share"],
                            "CG_C_pass": v["CG_C_pass"], "CG_Cworst_pass": v["CG_Cworst_pass"]}
                        for k, v in sens.items()},
        "CG_C_threshold_sensitivity": thr_sens,
        "CG_D_threshold_sensitivity": d_sens,
        "CG_F": cgf,
        "ST4_pass": st4,
        "wall_seconds": round(time.time() - t0, 1),
    }
    with open("ledgers/census_%s.json" % which, "w") as f:
        json.dump(out, f, indent=1, default=str)
    with open("ledgers/census_%s_classes.jsonl" % which, "w") as f:
        for h, v in main_lab.items():
            if v[0] == "TRIV_DEAD":
                continue
            f.write(json.dumps({"kind": v[0], "labels": sorted(v[1]), "secondary": sorted(v[2]),
                                "minsize": v[3], "minrank": v[4], "members": v[5],
                                "rep": ser(v[6]), "productive": v[7]}) + "\n")
    print(json.dumps({k: out[k] for k in ("counts", "class_kinds", "ST4_pass")}, indent=1, default=str))
    print(json.dumps(out["gates"], indent=1, default=str))
    print("CG_F median rho", cgf["median_rho"], "minsize_invariant", cgf["minsize_invariant"])
    return out


def _kindcount(lab):
    c = {}
    for v in lab.values():
        c[v[0]] = c.get(v[0], 0) + 1
    return c


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "G1")
