"""W2-30 T1: exact-identity m_base / m_atomic for F, C3, AC, 5C, C3+AC on the N17e/W2-24 realized-partner panel
(W2-14 BASE bank, epochs 10-299, N=1000, random side, copy errors off). A half counts as a child only if it is
byte-identical to the focal genome. ATOMIC write-back exactly as W2-24 q3 finals(): a half takes its new bytes
only if p11-promoted, else it is restored. Donor context ZERO (as N17e/W2-24 primary) and BANK (cx).
Also reports FID>=0.9 m (C.outcome) on the same calls for a side-by-side column, and exact keep/conv per side."""
import json, sys, pathlib, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-24_keep_variant"))
from q1_trace import panel, mk  # noqa: E402
from tvm import C  # noqa: E402

r = C.runner_for_spec(C.run_ds.DONOR)
n = r.L
F = C.run_ds.donor_genome()
G = {"F": F, "C3": mk(F, {43: 0xC3}), "AC": mk(F, {44: 0xAC}), "5C": mk(F, {49: 0x5C}),
     "C3+AC": mk(F, {43: 0xC3, 44: 0xAC})}


def exact_one(x, y, s, sx, sy):
    """returns dict of exact keep/conv under BASE and ATOMIC, and FID-based m via the same raw pair."""
    ga, gb, sa, sb = (x, y, sx, sy) if s == 0 else (y, x, sy, sx)
    o = C.pair(r, ga, gb, sa, sb, 0.0)
    na, nb, wa, wb = o["na"], o["nb"], o["wo"][0], o["wo"][1]
    fa = na if C.promoted(ga, na, gb, wb, n) else ga
    fb = nb if C.promoted(gb, nb, ga, wa, n) else gb
    (nx, ny), (ax, ay) = ((na, nb), (fa, fb)) if s == 0 else ((nb, na), (fb, fa))
    return {"kb": nx == x, "cb": ny == x, "ka": ax == x, "ca": ay == x,
            "fk": C.FID(x, nx) >= 0.9, "fc": C.FID(x, ny) >= 0.9}


def assay(x, pan, dctx):
    t = {"N": 0}
    for y, cy, cx, s in pan:
        sx = C.ZERO if dctx == "ZERO" else cx
        e = exact_one(x, y, s, sx, cy)
        for k, v in e.items():
            t[k + str(s)] = t.get(k + str(s), 0) + v
            t[k] = t.get(k, 0) + v
        t["n" + str(s)] = t.get("n" + str(s), 0) + 1
        t["N"] += 1
        # offspring-count distribution (exact BASE) for branching analysis
        c = int(e["kb"]) + int(e["cb"])
        t["dist_base_%d" % c] = t.get("dist_base_%d" % c, 0) + 1
        c = int(e["ka"]) + int(e["ca"])
        t["dist_atomic_%d" % c] = t.get("dist_atomic_%d" % c, 0) + 1
    N = t["N"]
    res = {"m_base_exact": (t["kb"] + t["cb"]) / N, "m_atomic_exact": (t["ka"] + t["ca"]) / N,
           "m_base_FID": (t["fk"] + t["fc"]) / N,
           "keep_exact": t["kb"] / N, "conv_exact": t["cb"] / N, "keep_FID": t["fk"] / N,
           "keep_atomic_exact": t["ka"] / N, "conv_atomic_exact": t["ca"] / N}
    for s in (0, 1):
        ns = t["n%d" % s]
        res["side%d" % s] = {"n": ns, "keep_exact": t.get("kb%d" % s, 0) / ns, "conv_exact": t.get("cb%d" % s, 0) / ns,
                             "keep_FID": t.get("fk%d" % s, 0) / ns, "conv_FID": t.get("fc%d" % s, 0) / ns,
                             "keep_atomic_exact": t.get("ka%d" % s, 0) / ns, "conv_atomic_exact": t.get("ca%d" % s, 0) / ns}
    res["dist_base"] = [t.get("dist_base_%d" % c, 0) / N for c in range(3)]
    res["dist_atomic"] = [t.get("dist_atomic_%d" % c, 0) / N for c in range(3)]
    return res


if __name__ == "__main__":
    t0 = time.time()
    pan = panel()
    out = {}
    for nm, g in G.items():
        out[nm] = {d: assay(g, pan, d) for d in ("ZERO", "BANK")}
        z = out[nm]["ZERO"]
        print(nm, "m_base exact %.3f FID %.3f | m_atomic exact %.3f | keep_ex s0 %.3f s1 %.3f conv_ex s0 %.3f s1 %.3f"
              % (z["m_base_exact"], z["m_base_FID"], z["m_atomic_exact"], z["side0"]["keep_exact"], z["side1"]["keep_exact"],
                 z["side0"]["conv_exact"], z["side1"]["conv_exact"]), "BANK m_base_ex %.3f" % out[nm]["BANK"]["m_base_exact"], flush=True)
    out["wall_s"] = round(time.time() - t0, 1)
    (HERE / "t1_exact_m.json").write_text(json.dumps(out, indent=1))
    print("wall", out["wall_s"])
