"""W2-39 a2 (adversarial): what do the founder-label members carry at the end of M* runs?
Re-runs selected seeds (deterministic; asserted equal to the logged row) with w22.make_runner wrapped to capture the
runner (no file edits), then reads bytes 37/43/44 of every live anc==0 member.
Q1: in founder-arm runs with B_xk >= 163, do members carry a morph (37=81, 44=AC, 43=C3) => is M*'s founder persistence
    morph-driven (de novo morph through the mutation kernel)?  Q2: in morph-arm runs, is the implanted morph retained?"""
import json, sys
import mstar as M
w22 = M.w22
CAP = {}
_orig = w22.make_runner


def cap_mr(*a, **k):
    r = _orig(*a, **k)
    CAP["r"] = r
    return r


w22.make_runner = cap_mr
ORIG = {37: 0xA5, 43: 0xC1, 44: 0xEC}
MORPH = {37: 0x81, 43: 0xC3, 44: 0xAC}


def profile(g, row):
    res = M.run(g, row["seed"])
    assert all(res[k] == row[k] for k in ("B", "Bxk", "maxA", "epochs", "stop")), (g, row["s"])
    r = CAP["r"]
    mem = [r._genome(o) for o in r.orgs if o.alive and o.anc == 0]
    prof = {"n_members": len(mem), "exact_founder_geno": sum(x[:64] == M.GENOS[g] for x in mem)}
    for p in (37, 43, 44):
        prof["b%d_orig" % p] = sum(x[p] == ORIG[p] for x in mem)
        prof["b%d_morph" % p] = sum(x[p] == MORPH[p] for x in mem)
    prof.update(s=row["s"], Bxk=row["Bxk"], stop=row["stop"], epochs=row["epochs"])
    return prof


out = {}
for g, sel, lim in (("F", lambda r: r["Bxk"] >= 163, 12), ("F", lambda r: 27 <= r["Bxk"] < 163, 6),
                    ("AC", lambda r: r["Bxk"] >= 163, 5), ("81", lambda r: r["Bxk"] >= 163, 5),
                    ("C3", lambda r: r["Bxk"] >= 27, 5), ("C3+AC", lambda r: r["Bxk"] >= 163, 4)):
    rows = [json.loads(l) for l in open(M.HERE / ("runs_%s.jsonl" % g.replace("+", "_")))]
    rows = sorted([r for r in rows if sel(r)], key=lambda r: r["s"])[:lim]
    key = g + ("_ge163" if lim in (12, 5, 4) and g != "C3" else "_27to163" if g == "F" else "_ge27")
    out[key] = [profile(g, r) for r in rows]
    print(key, json.dumps(out[key]), flush=True)
json.dump(out, open(M.HERE / "a2_genotypes.json", "w"), indent=1)
