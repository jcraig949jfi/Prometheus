"""W2-41 a2: re-assay F, C3, AC, 5C, C3+AC with the donor context drawn from the SELF-CARRIED distribution of
7ae3-family organisms in the 23 replayed runs (r1_out), partners from the W2-14 BASE bank (N17e panel:
partner genome + its carried registers + side). Paired design: every arm uses the same 1000 (y, cy, side);
only the donor context differs.

Donor-context arms:
  ZERO        (N17e / W2-24 / W2-30 primary)
  BANK        (N17e cx: a background bank context)
  SELF        every recorded pre-interaction carried context of a 7ae3-family org (uniform over rows)
  SELF_S0     ... only rows where the org was about to run at side 0
  SELF_RUN / SELF_CTL   rows from runaway / control runs
  SELF_AGE0 / SELF_AGE1_4 / SELF_AGE5P  age bins (epoch - birth epoch); founder born 0
  SELF_E0_9 / SELF_E10P epoch bins
  BIRTHCOND   W2-26 s1_out dctx of births whose donor genome is 7ae3-family (conditioned on a birth)
Rulers (BASE write-back): FID (>=0.9), class (FID>=0.9 and bytes 43,44,45,49 equal), exact. Also class ATOMIC.
Copy errors off. python -B a2_assay.py -> a2_assay.json"""
import gzip, json, pathlib, random, sys, time
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
sys.path.insert(0, str(W / "W2-24_keep_variant"))
from q1_trace import panel, mk  # noqa: E402
from tvm import C  # noqa: E402

CTL = {"CNR_s4", "XH2N_s9", "XTK_14", "CRW_35", "CRW_47", "CRW_71", "CRW_79", "CRW_107", "CRW_66", "CRW_91", "CRW_85"}
CLS = (43, 44, 45, 49)
r = C.runner_for_spec(C.run_ds.DONOR)
n = r.L
F = C.run_ds.donor_genome()
G = {"F": F, "C3": mk(F, {43: 0xC3}), "AC": mk(F, {44: 0xAC}), "5C": mk(F, {49: 0x5C}),
     "C3+AC": mk(F, {43: 0xC3, 44: 0xAC})}


def load_rows():
    rows = []
    for p in sorted((HERE / "r1_out").glob("*.json.gz")):
        d = json.load(gzip.open(p, "rt"))
        assert d["exact_vs_w26"] and bytes.fromhex(d["implant"]) == F
        for e, oid, born, side, g, regs, fz, fc, pg, pregs, pfz, pfc, nb, ncb, keep in d["rows"]:
            rows.append({"run": d["label"], "ctl": d["label"] in CTL, "e": e, "age": None if born is None else e - born,
                         "side": side, "g": d["genomes"][g], "ctx": (regs, bool(fz), bool(fc)), "pg": d["genomes"][pg],
                         "pctx": (pregs, bool(pfz), bool(pfc)), "births": nb, "cb": ncb, "keep": keep})
    return rows


def birthcond():
    out = []
    for p in sorted((W / "W2-26_switch_source" / "s1_out").glob("*.json")):
        d = json.loads(p.read_text())
        for b in d["births"].values():
            dg = bytes.fromhex(b["dg"])
            if sum(x == y for x, y in zip(dg, F)) >= 51:
                regs, fz, fc = b["dctx"]
                out.append((regs, bool(fz), bool(fc)))
    return out


def one(x, y, s, sx, sy):
    ga, gb, sa, sb = (x, y, sx, sy) if s == 0 else (y, x, sy, sx)
    o = C.pair(r, ga, gb, sa, sb, 0.0)
    na, nb, wa, wb = o["na"], o["nb"], o["wo"][0], o["wo"][1]
    fa = na if C.promoted(ga, na, gb, wb, n) else ga
    fb = nb if C.promoted(gb, nb, ga, wa, n) else gb
    (nx, ny), (ax, ay) = ((na, nb), (fa, fb)) if s == 0 else ((nb, na), (fb, fa))
    f = lambda h: C.FID(x, h) >= 0.9
    c = lambda h: f(h) and all(h[i] == x[i] for i in CLS)
    return {"kF": f(nx), "cF": f(ny), "kC": c(nx), "cC": c(ny), "kE": nx == x, "cE": ny == x, "kCa": c(ax), "cCa": c(ay)}


def assay(x, pan, ctxs):
    t = {}
    for (y, cy, _cx, s), sx in zip(pan, ctxs):
        e = one(x, y, s, sx, cy)
        t["n%d" % s] = t.get("n%d" % s, 0) + 1
        for k, v in e.items():
            t[k + str(s)] = t.get(k + str(s), 0) + int(v)
    N = t["n0"] + t["n1"]
    res = {}
    for rl, kk, cc in (("FID", "kF", "cF"), ("class", "kC", "cC"), ("exact", "kE", "cE"), ("class_atomic", "kCa", "cCa")):
        res[rl] = {"m": (t[kk + "0"] + t[kk + "1"] + t[cc + "0"] + t[cc + "1"]) / N,
                   "keep": (t[kk + "0"] + t[kk + "1"]) / N,
                   "keep_s0": t[kk + "0"] / t["n0"], "keep_s1": t[kk + "1"] / t["n1"],
                   "conv_s0": t[cc + "0"] / t["n0"], "conv_s1": t[cc + "1"] / t["n1"]}
    return res


def main():
    t0, c0 = time.time(), time.process_time()
    pan = panel()
    rows = load_rows()
    bc = birthcond()
    rng = random.Random("W2-41")
    pools = {
        "SELF": rows,
        "SELF_S0": [q for q in rows if q["side"] == 0],
        "SELF_RUN": [q for q in rows if not q["ctl"]],
        "SELF_CTL": [q for q in rows if q["ctl"]],
        "SELF_AGE0": [q for q in rows if q["age"] == 0],
        "SELF_AGE1_4": [q for q in rows if q["age"] is not None and 1 <= q["age"] <= 4],
        "SELF_AGE5P": [q for q in rows if q["age"] is not None and q["age"] >= 5],
        "SELF_E0_9": [q for q in rows if q["e"] < 10],
        "SELF_E10P": [q for q in rows if q["e"] >= 10],
    }
    arms = {"ZERO": [C.ZERO] * len(pan), "BANK": [p[2] for p in pan]}
    for k, pool in pools.items():
        arms[k] = [rng.choice(pool)["ctx"] for _ in pan]
    arms["BIRTHCOND"] = [rng.choice(bc) for _ in pan]
    out = {"pool_sizes": {k: len(v) for k, v in pools.items()}, "birthcond_n": len(bc), "N": len(pan),
           "n_none_regs_SELF": sum(q["ctx"][0] is None for q in rows), "res": {}}
    for nm, x in G.items():
        out["res"][nm] = {}
        for a, ctxs in arms.items():
            out["res"][nm][a] = assay(x, pan, ctxs)
        z, s = out["res"][nm]["ZERO"]["FID"], out["res"][nm]["SELF"]["FID"]
        print(nm, "ZERO m %.3f c0 %.3f c1 %.3f | SELF m %.3f c0 %.3f c1 %.3f | BC c0 %.3f" % (
            z["m"], z["conv_s0"], z["conv_s1"], s["m"], s["conv_s0"], s["conv_s1"],
            out["res"][nm]["BIRTHCOND"]["FID"]["conv_s0"]), "cpu %.0f" % (time.process_time() - c0), flush=True)
    out["wall_s"], out["cpu_s"] = round(time.time() - t0, 1), round(time.process_time() - c0, 1)
    (HERE / "a2_assay.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
