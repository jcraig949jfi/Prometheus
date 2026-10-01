"""W2 stage 2 (exact, analytic): where does the EARLIEST extensionally-equivalent
program sit in the FULL PRISTINE walk (coverage segment, then the G4/G5 fallback)?

Walk (a18.fast_cost, PRISTINE library):
  segment A  H1 x H2 x FINAL in keyed order ................ charges 1..151,920
  segment B  180 expression-only finals (acc = 0) ........... 151,921..152,100
  segment C  keyed INIT_SPACE (116) x keyed G5 (465,954) x keyed FINAL (180)
             charge = 152,100 + ri*|G5|*180 + rb*180 + rf + 1
Equivalence used here (a LOWER BOUND on the true class; stated in REPORT):
  init'  : INIT_SPACE expr whose value equals the witness init on every probe;
  body'  : G5 body whose post-fold accumulator equals the witness body's on every
           probe (given the witness init value);
  final' : FINAL expr whose output equals the witness final's on the witness acc.
  (The in-coverage census w2_coverage.py counts full program equivalence.)
Probes: 8 signature inputs, then 120-input verification (w2_coverage.PROBE).
Output: w2_fallback_<SRC>.json.  Single core.
"""
import bisect, hashlib, pickle, sys, time
from w2_common import *
import fasteval as FE
import w2_coverage as W

SIGP = W.PINFO[:8]
FIN = list(G.FINAL_SPACE)
SCR = Path(os.environ.get("W2_SCRATCH", HERE))


def sig_table():
    p = SCR / "w2_g5_sigtable.pkl"
    if p.exists():
        return pickle.loads(p.read_bytes())
    t0 = time.time()
    tab = {}
    for init in ("0", "1"):
        ifn = FE.fn(init)
        d = {}
        for k, b in enumerate(G.BODY_SPACE):
            bfn = FE.fn(b)
            s = tuple(FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _ in SIGP)
            if any(a is FE._FAIL for a in s):
                continue
            d.setdefault(hash(s), []).append(k)
        tab[init] = d
    p.write_bytes(pickle.dumps(tab))
    print("sigtable %.0fs" % (time.time() - t0), flush=True)
    return tab


def keys_sorted(items, seed, slot):
    ks = sorted(hashlib.sha256(("APHRODITE/S2/ORDER/v1/%d/%s/%s" % (seed, slot, it)).encode()).hexdigest()
                for it in dict.fromkeys(items))
    return ks


def kval(seed, slot, it):
    return hashlib.sha256(("APHRODITE/S2/ORDER/v1/%d/%s/%s" % (seed, slot, it)).encode()).hexdigest()


def analyse(r, tab):
    init, body, final = r["init"], r["body"], r["final"]
    ifn, bfn, ffn = FE.fn(init), FE.fn(body), FE.fn(final)
    s = tuple(FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _ in SIGP)
    cand = tab[init].get(hash(s), [])
    wacc = [FE._fold_acc(ifn, bfn, vals, fst, lst) for vals, fst, lst, _ in W.PINFO]
    eqb = []
    for k in cand:
        b = G.BODY_SPACE[k]
        f2 = FE.fn(b)
        if all(FE._fold_acc(ifn, f2, vals, fst, lst) == a for (vals, fst, lst, _), a in zip(W.PINFO, wacc)):
            eqb.append(b)
    wout = [FE._final(ffn, a, vl, fst, lst) for a, (vals, fst, lst, vl) in zip(wacc, W.PINFO)]
    eqf = [f for f in FIN if all(FE._final(FE.fn(f), a, vl, fst, lst) == o
                                 for a, (vals, fst, lst, vl), o in zip(wacc, W.PINFO, wout))]
    iv = [FE.fn(init)(0, 0, fst, lst) for vals, fst, lst, _ in W.PINFO]
    eqi = [i for i in G.INIT_SPACE if all(_safe(FE.fn(i), fst, lst) == x for (vals, fst, lst, _), x in zip(W.PINFO, iv))]
    h2 = set(G.H2_SPACE)
    out = {"name": r["name"], "source": r["source"], "init": init, "body": body, "final": final,
           "p_PRISTINE": r["p_PRISTINE"], "p_L1": r["p_L1"], "Q2_size": r["Q2_size"],
           "k_body_G5": len(eqb), "k_body_H2": sum(b in h2 for b in eqb), "k_final": len(eqf), "k_init": len(eqi),
           "eq_bodies_sample": eqb[:6], "eq_finals": eqf[:6]}
    prov, cs = cells(r)
    NG5, NF = len(G.BODY_SPACE), len(FIN)
    base = W.N_COV if hasattr(W, "N_COV") else N_COV
    cl = []
    for c in cs:
        sd = c.seed
        ik = sorted(kval(sd, "g4init", i) for i in dict.fromkeys(G.INIT_SPACE))
        ri = min(bisect.bisect_left(ik, kval(sd, "g4init", i)) for i in eqi)
        bk = keys_sorted(G.BODY_SPACE, sd, "g4body")
        rb = min(bisect.bisect_left(bk, kval(sd, "g4body", b)) for b in eqb)
        fk = sorted(kval(sd, "g4final", f) for f in FIN)
        # earliest final for the chosen body: min over eq finals (finals order is body-independent)
        rf = min(bisect.bisect_left(fk, kval(sd, "g4final", f)) for f in eqf)
        cl.append({"seed": sd, "r_init": ri, "r_body": rb, "r_final": rf,
                   "fallback_equiv_charge": N_COV + NF + ri * NG5 * NF + rb * NF + rf + 1})
    out["cells"] = cl
    return out


def _safe(f, fst, lst):
    try:
        return f(0, 0, fst, lst)
    except Exception:
        return None


if __name__ == "__main__":
    a18.worker_init()
    src = sys.argv[1] if len(sys.argv) > 1 else "NAT"
    tab = sig_table()
    res = []
    for r in rows(None if src == "ALL" else src):
        res.append(analyse(r, tab))
        if len(res) % 20 == 0:
            print(len(res), flush=True)
    (HERE / ("w2_fallback_%s.json" % src)).write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("wrote", len(res))
