"""W2-41 a3: register mechanism.
(A) Dead-register test for the 5 named genomes: for every DISTINCT self-carried context (r1_out), every distinct
    birth-conditioned W2-26 dctx, and 3000 uniform-random contexts, run the genome at side 0 and at side 1 against
    2 fixed bank partners on the traced stock VM and compare the genome's own LDIR/LDDR records (src, dst, count)
    and final halves with the ZERO-context run. Also record the first step after which the genome's own
    register file + flags equal the ZERO run's (convergence step / pc).
(B) For every W2-26 context-dependent switch edge (k_c0 < 0.5 under ZERO, >= 0.5 with its actual carried
    context): single-register ablation on 40 bank partners at side 0. NEC(r) = resetting only r to the ZERO
    value drops side-0 conversion below 0.5; SUF(r) = ZERO context with only r set to the actual value raises it
    to >= 0.5. Also the donor's own first LDIR (src, dst) under ZERO vs actual, and which of the genome's
    initialiser bytes (implant positions 0-3, 19-25, 48-50) differ from the implant.
python -B a3_mechanism.py -> a3_mechanism.json"""
import gzip, json, pathlib, random, sys, time, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
sys.path.insert(0, str(W / "W2-24_keep_variant"))
from q1_trace import panel, mk  # noqa: E402
from tvm import C, pair_t  # noqa: E402

r = C.runner_for_spec(C.run_ds.DONOR)
n = r.L
F = C.run_ds.donor_genome()
G = {"F": F, "C3": mk(F, {43: 0xC3}), "AC": mk(F, {44: 0xAC}), "5C": mk(F, {49: 0x5C}),
     "C3+AC": mk(F, {43: 0xC3, 44: 0xAC})}
RN = ["B", "C", "D", "E", "H", "L", "x", "A"]


def norm(st):
    regs, fz, fc = st
    return (None if regs is None else tuple(regs), bool(fz), bool(fc))


def own(x, y, s, sx, sy):
    ga, gb, sa, sb = (x, y, sx, sy) if s == 0 else (y, x, sy, sx)
    na, nb, ctxs, tr, wl, a0, ld = pair_t(r, ga, gb, sa, sb)
    lds = tuple((p, sr, d, k) for who, p, sr, d, k, _ in ld if who == s)
    trace = [(pc, regs, fz, fc) for who, pc, op, regs, fz, fc in tr if who == s]
    return (na, nb), lds, trace


def conv_gap(trace, ztrace):
    """first own-step index from which (pc, regs, flags) equal the ZERO run step for step to the end."""
    m = min(len(trace), len(ztrace))
    k = m
    while k > 0 and trace[k - 1] == ztrace[k - 1]:
        k -= 1
    return k, (trace[k][0] if k < len(trace) else None)


def partA():
    rows = []
    for p in sorted((HERE / "r1_out").glob("*.json.gz")):
        rows += [tuple(q[5:8]) for q in json.load(gzip.open(p, "rt"))["rows"]]
    selfc = sorted({json.dumps(norm(q)) for q in rows})
    bc = set()
    for p in sorted((W / "W2-26_switch_source" / "s1_out").glob("*.json")):
        for b in json.loads(p.read_text())["births"].values():
            if sum(x == y for x, y in zip(bytes.fromhex(b["dg"]), F)) >= 51:
                bc.add(json.dumps(norm(b["dctx"])))
    rng = random.Random("W2-41a3")
    rnd = [json.dumps(norm(C.rand_ctx(rng))) for _ in range(3000)]
    pan = panel()
    parts = [pan[0][:2], pan[1][:2]]
    out = {"n_self_distinct": len(selfc), "n_birthcond_distinct": len(bc), "n_rand": len(rnd), "res": {}}
    for nm, x in G.items():
        for s in (0, 1):
            Z = [own(x, y, s, C.ZERO, cy) for y, cy in parts]
            res = {}
            for pool, lst in (("SELF", selfc), ("BIRTHCOND", sorted(bc)), ("RAND", rnd)):
                diff_ld = diff_half = 0
                gaps = collections.Counter()
                ex = []
                for js in lst:
                    st = json.loads(js)
                    sx = (st[0], st[1], st[2])
                    for (y, cy), (zh, zl, zt) in zip(parts, Z):
                        h, l, t = own(x, y, s, sx, cy)
                        diff_ld += l != zl
                        diff_half += h != zh
                        k, pc = conv_gap(t, zt)
                        gaps[pc if pc is None else (pc - s * n)] += 1
                        if l != zl and len(ex) < 5:
                            ex.append({"ctx": st, "ld": l[:2], "ld_zero": zl[:2]})
                res[pool] = {"calls": 2 * len(lst), "diff_ldir": diff_ld, "diff_halves": diff_half,
                             "converge_at_own_pc": dict(gaps.most_common(6)), "examples": ex}
            out["res"]["%s_side%d" % (nm, s)] = res
            print(nm, s, {k: (v["diff_ldir"], v["diff_halves"], v["calls"]) for k, v in res.items()}, flush=True)
    return out


def partB():
    s3 = json.loads((W / "W2-26_switch_source" / "s3_assay.json").read_text())["rows"]
    s2 = {(e["run"], e["k"], e["kk"], e["e2"]): e for e in
          json.loads((W / "W2-26_switch_source" / "s2_switch_diffs.json").read_text())["edges"]}
    pan = panel()[:40]
    init_pos = [0, 1, 2, 3, 19, 20, 21, 22, 23, 24, 25, 48, 49, 50]

    def c0(g, sx):
        return sum(C.outcome(r, g, y, 0, sx, cy, 0.0, None)["conv"] for y, cy, _cx, _s in pan) / len(pan)

    out = []
    seen = set()
    for row in s3:
        if not (row["k_c0"] < 0.5 and row["k_c0_actctx"] >= 0.5):
            continue
        e = s2[(row["run"], row["k"], row["kk"], row["e2"])]
        g = bytes.fromhex(e["kE2"])
        regs, fz, fc = e["kk_dctx"]
        key = (g, json.dumps([regs, fz, fc]))
        if key in seen:
            continue
        seen.add(key)
        act = (list(regs), bool(fz), bool(fc))
        base_act, base_zero = c0(g, act), c0(g, C.ZERO)
        nec, suf = [], []
        for i in (0, 1, 2, 3, 4, 5, 7):
            a = list(regs); a[i] = 0
            if c0(g, (a, act[1], act[2])) < 0.5:
                nec.append(RN[i])
            z = [0] * 8; z[i] = regs[i]
            if regs[i] != 0 and c0(g, (z, False, False)) >= 0.5:
                suf.append(RN[i])
        for fl in ("fz", "fc"):
            a = (list(regs), False if fl == "fz" else act[1], False if fl == "fc" else act[2])
            if (act[1] if fl == "fz" else act[2]) and c0(g, a) < 0.5:
                nec.append(fl)
        y, cy = pan[0][:2]
        _, lz, tz = own(g, y, 0, C.ZERO, cy)
        _, la, ta = own(g, y, 0, act, cy)
        out.append({"run": row["run"], "cls": row["cls"], "P_fam": row["P_fam"], "k_fam": row["k_fam"],
                    "match_implant": sum(a == b for a, b in zip(g, F)),
                    "init_bytes_changed": {p: "%02x>%02x" % (F[p], g[p]) for p in init_pos if g[p] != F[p]},
                    "ctx": [regs, fz, fc], "c0_zero": base_zero, "c0_act": base_act, "NEC": nec, "SUF": suf,
                    "ldir_zero": lz[:2], "ldir_act": la[:2]})
    return out


if __name__ == "__main__":
    t0, c0_ = time.time(), time.process_time()
    which = sys.argv[1] if len(sys.argv) > 1 else "AB"
    res = {}
    if "B" in which:
        res["B"] = partB()
        print("B done", len(res["B"]), "cpu %.0f" % (time.process_time() - c0_), flush=True)
    if "A" in which:
        res["A"] = partA()
    res["cpu_s"] = round(time.process_time() - c0_, 1)
    (HERE / ("a3_mechanism_%s.json" % which)).write_text(json.dumps(res, indent=1))
    print("cpu", res["cpu_s"])
