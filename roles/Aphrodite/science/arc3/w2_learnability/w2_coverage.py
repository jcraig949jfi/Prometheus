"""W2 stage 1 (cheap, exact): PRISTINE-coverage census of T4-qualified foundry families.

For every T4-qualified C2 foundry family:
  * extensional equivalence class inside PRISTINE coverage H1 x H2 x FINAL
    (151,920 programs) on a 120-input probe set (dev-length and length-20 lists);
  * per pilot cell (the SAME 4 cells as the foundry: label A19-pilot-PRISTINE):
      - the charge of the first dev-consistent program inside coverage (== fast_cost
        charge whenever it is <= 151,920; verified against a18.fast_cost),
      - the charge of the first EXTENSIONALLY-equivalent program,
      - the number of dev-consistent programs in coverage (spurious + true);
  * body features (atoms, depth, operator set, dependence on first / query).
Output: w2_coverage.json.  Single core.
"""
import random, re, sys
from w2_common import *
import fasteval as FE

H1, H2, FIN = list(G.H1_SPACE), list(G.H2_SPACE), list(G.FINAL_SPACE)
NB, NF = len(H2), len(FIN)


def probe_inputs(seed="W2/PROBE/v1", n_dev=100, n_long=20):
    rng = random.Random(seed)
    out = []
    for k in range(n_dev + n_long):
        L = rng.randint(4, 9) if k < n_dev else 20
        xs = [rng.randint(2, 30) for _ in range(L)]
        out.append(xs + [rng.randint(3, 97)])
    return out


PROBE = probe_inputs()
PINFO = [(n[:-1], n[0], n[-1], n[:-1][-1]) for n in PROBE]


def outputs(prog, pinfo):
    return tuple(G.run_program(prog, vals + [lst], True) for vals, fst, lst, _ in pinfo)


_ACC = {}
def acc_table(pinfo_key, pinfo):
    t = _ACC.get(pinfo_key)
    if t is None:
        t = {}
        for i in H1:
            ifn = FE.fn(i)
            for b in H2:
                t[(i, b)] = [FE._fold_acc(ifn, FE.fn(b), vals, fst, lst) for vals, fst, lst, _ in pinfo]
        _ACC[pinfo_key] = t
    return t


def consistent(pinfo, gold, pinfo_key):
    """All (i, b, f) in coverage whose outputs equal gold (strings) on pinfo."""
    tab = acc_table(pinfo_key, pinfo)
    hits = []
    for (i, b), accs in tab.items():
        if any(a is FE._FAIL for a in accs):
            continue
        for f in FIN:
            ffn = FE.fn(f)
            ok = True
            for a, (vals, fst, lst, vl), g in zip(accs, pinfo, gold):
                got = FE._final(ffn, a, vl, fst, lst)
                if got is None or str(got) != g:
                    ok = False
                    break
            if ok:
                hits.append((i, b, f))
    return hits


def charge(prog, seed):
    """1-based charge of prog in the PRISTINE segment of the keyed walk."""
    i, b, f = prog
    ri = FR.keyed(H1, seed, "init").index(i)
    rb = _kb(seed).index(b)
    rf = _kf(seed).index(f)
    return ri * NB * NF + rb * NF + rf + 1


_KB, _KF = {}, {}
def _kb(seed):
    if seed not in _KB:
        _KB[seed] = FR.keyed(H2, seed, "body")
    return _KB[seed]
def _kf(seed):
    if seed not in _KF:
        _KF[seed] = FR.keyed(FIN, seed, "final")
    return _KF[seed]


def depth(s):
    d = m = 0
    for ch in s:
        if ch == "(":
            d += 1; m = max(m, d)
        elif ch == ")":
            d -= 1
    return m


def feats(r):
    b = r["body"]
    atoms = set(re.findall(r"\b(acc|v|first|last|0|1)\b", b))
    ops = set(re.findall(r"(\+|-|\*|//|%|pow|gcd)", b))
    bf = FE.fn(b)
    rng = random.Random("W2/DEP/" + b)
    dep_first = dep_last = False
    for _ in range(60):
        a, v, f, l = rng.randint(-50, 200), rng.randint(2, 30), rng.randint(2, 30), rng.randint(3, 97)
        try:
            y = bf(a, v, f, l)
            if bf(a, v, rng.randint(2, 30), l) != y: dep_first = True
            if bf(a, v, f, rng.randint(3, 97)) != y: dep_last = True
        except Exception:
            pass
    return {"atoms": sorted(atoms), "foreign_atoms": sorted(atoms - {"acc", "v"}), "ops": sorted(ops),
            "depth": depth(b), "in_H2_syntactic": b in set(H2), "dep_first": dep_first, "dep_query": dep_last}


def analyse(r):
    w = ("fold", r["init"], r["body"], r["final"])
    gold = tuple(str(x) for x in outputs(w, PINFO))
    eq = consistent(PINFO, gold, "probe")
    out = {"name": r["name"], "source": r["source"], "init": r["init"], "body": r["body"], "final": r["final"],
           "Q2_size": r["Q2_size"], "p_PRISTINE": r["p_PRISTINE"], "p_L1": r["p_L1"],
           "k_cov": len(eq), "m_cov_pairs": len({(i, b) for i, b, f in eq}),
           "m_cov_bodies": len({b for i, b, f in eq}), "eq_examples": [list(p) for p in eq[:3]]}
    out.update(feats(r))
    prov, cs = cells(r)
    cl = []
    for c in cs:
        pinfo = [(n[:-1], n[0], n[-1], n[:-1][-1]) for n, g in c.parsed]
        devgold = tuple(g for n, g in c.parsed)
        dc = consistent(pinfo, devgold, None if False else ("cell", r["name"], c.seed))
        dch = sorted((charge(p, c.seed), p) for p in dc)
        ech = sorted(charge(p, c.seed) for p in eq)
        first = dch[0] if dch else None
        cl.append({"seed": c.seed, "n_dev_consistent_cov": len(dc),
                   "first_dev_charge": first[0] if first else None,
                   "first_dev_prog": list(first[1]) if first else None,
                   "first_dev_is_equiv": bool(first and tuple(first[1]) in set(eq)),
                   "first_equiv_charge": ech[0] if ech else None})
        _ACC.pop(("cell", r["name"], c.seed), None)
    out["cells"] = cl
    return out


if __name__ == "__main__":
    a18.worker_init()
    src = sys.argv[1] if len(sys.argv) > 1 else "NAT"
    res = [analyse(r) for r in rows(None if src == "ALL" else src)]
    (HERE / ("w2_coverage_%s.json" % src)).write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("wrote", len(res))
