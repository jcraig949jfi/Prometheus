"""W7 PKG-6 (1)+(2a): T4 / dev query-domain mismatch, measured on the frozen
C2 (A19) and C3 (A20) foundry rows.

Per family (every row that reached T4 scoring):
  * witness re-scored by T4 v1 (direct) and the v1a draft (tribunal_t4_v1a);
  * E_dev: the PRISTINE-coverage programs (H1 x H2 x FINAL) extensionally equal
    to the witness on a DEV-DOMAIN probe (100 inputs of length 4..9 + 20 of
    length 20, queries 3..97 -- W2's probe); each is scored by T4 v1 and v1a
    (direct program-level scoring). "q12 artifact" = fails v1, passes v1a.
  * the 8 frozen pilot cells (PRISTINE, L1 x 4) re-walked at the frozen 250k
    escrow with a18.fast_cost (exact); the first hit is scored by v1 and v1a.
    Reproduction check: v1 pilot p equals the frozen p_PRISTINE / p_L1.
Usage: python w7_t4dev.py <workers> [limit]
Writes W7_T4DEV_ROWS.jsonl (resumable) and W7_T4DEV_SUMMARY.json.
"""
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

from w7_common import *              # noqa: F401,F403
import fasteval as FE                # noqa: E402
import tribunal_t4 as T4             # noqa: E402
import tribunal_t4_v1a as T4A        # noqa: E402

H1, H2, FIN = list(G.H1_SPACE), list(G.H2_SPACE), list(G.FINAL_SPACE)
H2SET = set(H2)
OUT = HERE / "W7_T4DEV_ROWS.jsonl"


def probe_inputs(seed="W2/PROBE/v1", n_dev=100, n_long=20, qlo=3):
    rng = random.Random(seed)
    out = []
    for k in range(n_dev + n_long):
        L = rng.randint(4, 9) if k < n_dev else 20
        xs = [rng.randint(2, 30) for _ in range(L)]
        out.append(xs + [rng.randint(qlo, 97)])
    return out


PROBE = probe_inputs()
PINFO = [(n[:-1], n[0], n[-1], n[:-1][-1]) for n in PROBE]
_ACC = None


def pairs():
    """(init, body) pairs of PRISTINE coverage plus the L1-selected entry (derived_0)."""
    out = [(i, b) for i in H1 for b in H2]
    for e in a17.L1_entries()[:-1]:
        out += [(i, b) for i in e["inits"] for b in FR.entry_bodies(e)]
    return list(dict.fromkeys(out))


def acc_table():
    global _ACC
    if _ACC is None:
        _ACC = {}
        for i, b in pairs():
            ifn = FE.fn(i)
            _ACC[(i, b)] = [FE._fold_acc(ifn, FE.fn(b), vals, fst, lst) for vals, fst, lst, _ in PINFO]
    return _ACC


def e_dev(w):
    gold = [FE.run_program(w, vals + [lst], True) for vals, fst, lst, _ in PINFO]
    hits = []
    for (i, b), accs in acc_table().items():
        if any(a is FE._FAIL for a in accs):
            continue
        for f in FIN:
            ffn = FE.fn(f)
            if all((g is not None and FE._final(ffn, a, vl, fst, lst) == g)
                   for a, (vals, fst, lst, vl), g in zip(accs, PINFO, gold)):
                hits.append(("fold", i, b, f))
    return hits


_NUM = __import__("re").compile(r"-?\d+")


def q12_items(name, w, l_max):
    bat = T4.batteries(name, w, l_max, 150)
    out = []
    for t in bat["ce"]:
        nums = [int(x) for x in _NUM.findall(t["prompt"])]
        if nums[-1] in (1, 2):
            out.append((nums[:-1], nums[-1], t["gold"]))
    return out


def q12_only(sc):
    """All failures confined to counterexample items with query 1 or 2."""
    f = sc["fails"]
    if any(f[k] for k in ("ext", "stress", "order")):
        # ext/order tolerate 1-2 misses; failures there are not query-1/2 by construction
        return False
    return bool(f["ce"]) and all(m in (1, 2) for _L, m in f["ce"])


def job(r):
    a18.worker_init()
    T4.use_provider(prov_of(r))
    T4A.use_provider(prov_of(r))
    w = ("fold", r["init"], r["body"], r["final"])
    name = r["name"]
    out = {"tag": r["_tag"], "name": name, "source": r["source"], "body": r["body"], "init": r["init"],
           "final": r["final"], "Q2_size": r["Q2_size"], "T4_qualified_frozen": bool(r.get("T4_qualified")),
           "p_PRISTINE": r.get("p_PRISTINE"), "p_L1": r.get("p_L1")}
    sw1 = T4A.direct_score(w, name, w, "v1")
    swa = T4A.direct_score(w, name, w, "v1a")
    out["witness_v1"] = sw1["qualified"]
    out["witness_v1a"] = swa["qualified"]
    out["witness_v1a_reasons"] = swa["reasons"]
    out["L_max_v1"], out["L_max_v1a"] = sw1["L_max"], swa["L_max"]
    if not (sw1["qualified"] or swa["qualified"]):
        return out
    # E_dev in coverage
    eq = e_dev(w)
    out["k_edev"] = len(eq)
    items = q12_items(name, w, sw1["L_max"])
    out["n_q12_items"] = len(items)
    div = [p for p in eq if any(str(T4.run(p, xs, m)[0]) != g for xs, m, g in items)]
    out["edev_q12_divergent"] = len(div)
    out["edev_q12_divergent_cov"] = sum(1 for p in div if p[2] in H2SET)
    n1 = na = 0
    ex = []
    for p in div[:40]:
        s1 = T4A.direct_score(p, name, w, "v1")
        sa = T4A.direct_score(p, name, w, "v1a")
        n1 += s1["qualified"]
        na += sa["qualified"]
        if len(ex) < 4:
            ex.append({"prog": list(p), "v1": s1["qualified"], "v1a": sa["qualified"], "ce_v1": s1["acc"]["ce"]})
    out.update({"div_scored": min(40, len(div)), "div_v1_pass": n1, "div_v1a_pass": na, "div_examples": ex})
    walk = bool(div) or (int(__import__("hashlib").sha256(name.encode()).hexdigest(), 16) % 8 == 0)
    out["walked"] = walk
    if not walk:
        return out
    # frozen pilot cells, exact walk at 250k
    prov = prov_of(r)
    L = libs()
    for arm in ("PRISTINE", "L1"):
        if r.get("Q2_size") is None:
            break
        _, cs = cells(r, arm, prov)
        cl = []
        for c in cs:
            ch, prog = a18.fast_cost(L[arm], c, FR.ESCROW)
            rec = {"charge": ch, "prog": list(prog) if prog else None}
            if prog:
                s1 = T4A.direct_score(tuple(prog), name, w, "v1")
                sa = T4A.direct_score(tuple(prog), name, w, "v1a")
                rec.update({"v1": s1["qualified"], "v1a": sa["qualified"], "q12_only": q12_only(s1),
                            "v1_acc": s1["acc"], "seg": "lib" if ch <= N_COV else "beyond"})
            else:
                rec.update({"v1": False, "v1a": False})
            cl.append(rec)
        out["cells_" + arm] = cl
        out["p_%s_v1" % arm] = sum(c["v1"] for c in cl) / 4
        out["p_%s_v1a" % arm] = sum(c["v1a"] for c in cl) / 4
    return out


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    allrows = [r for t in ("A19", "A20") for r in rows(t, t4=False) if r.get("T4")]
    if limit:
        allrows = allrows[:limit]
    done = set()
    if OUT.exists():
        done = {(json.loads(x)["tag"], json.loads(x)["name"]) for x in open(OUT, encoding="utf-8")}
    todo = [r for r in allrows if (r["_tag"], r["name"]) not in done]
    print("todo", len(todo), flush=True)
    with ProcessPoolExecutor(max_workers=workers, initializer=a18.worker_init) as ex, \
            open(OUT, "a", encoding="utf-8") as fh:
        futs = [ex.submit(job, r) for r in todo]
        for k, f in enumerate(as_completed(futs)):
            fh.write(json.dumps(f.result(), default=str) + "\n")
            fh.flush()
            if k % 25 == 0:
                print("done", k, flush=True)


if __name__ == "__main__":
    main()
