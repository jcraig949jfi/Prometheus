"""Step 2: per-draw trace of the CVT-R BASE lineage (the 3 draws x 4 generations every variant is compared to).
For each interaction: child fidelity to parent / to G0, per-position authorship of the child half (prov: who changed
the byte last; 'V' = the victim-half context, 'D' = the donor context, '-' = untouched), the fraction of each
context's executed steps whose pc lay in the donor's half / victim half, and every LDIR (who, src, dst, n)."""
import json, random, pathlib, collections
from _env import A, ROWS, traced_dense, FRESH, shabytes
import p11

T = traced_dense()


def interact_traced(G, side, sid, g, k, P, vb=None):
    n = P["n"]
    if vb is None:
        vb = shabytes("VICTIM", sid, g, k, n=n)
    ga, gb = (G, vb) if side == 0 else (vb, G)
    T._TR = []; T._LD = []
    tape, prov, lit, wo = p11.interact(T, n=n, tape_len=P["tape_len"], ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                       budget=P["budget"], ops_mask=P["mask"], cmr=0.0, rng=random.Random(0))
    tr, ld = T._TR, T._LD
    T._TR = T._LD = None
    v0 = n if side == 0 else 0
    d0 = 0 if side == 0 else n
    child = bytes(tape[v0:v0 + n])
    donor_who = side + 1
    victim_who = 2 - side
    sym = {0: "-", donor_who: "D", victim_who: "V"}
    au = "".join(sym[prov[v0 + i]] for i in range(n))
    # after the interaction: is the donor's own half intact?
    own_after = bytes(tape[d0:d0 + n])
    steps = {}
    for who in (1, 2):
        pcs = [pc for w, pc, _ in tr if w == who]
        steps[{donor_who: "D", victim_who: "V"}[who]] = {
            "n": len(pcs),
            "in_donor_half": sum(1 for pc in pcs if d0 <= pc < d0 + n),
            "in_victim_half": sum(1 for pc in pcs if v0 <= pc < v0 + n)}
    lds = [{"by": {donor_who: "D", victim_who: "V"}[w], "src": s & 0x7f, "dst": d & 0x7f, "n": m, "step": st}
           for w, s, d, m, st, _pc in ld]
    return {"child": child, "authorship": au, "own_after": own_after, "steps": steps, "ldir": lds}


def lineage(G0, side, sid, k, P):
    out = []
    G = G0
    for g in range(1, 5):
        r = interact_traced(G, side, sid, g, k, P)
        c = r["child"]
        out.append({"g": g, "fid_parent": round(p11.fidelity(G, c), 3), "fid_G0": round(p11.fidelity(G0, c), 3),
                    "child_eq_parent": c == G, "own_half_intact": r["own_after"] == G,
                    "auth_counts": dict(collections.Counter(r["authorship"])), "authorship": r["authorship"],
                    "steps": r["steps"], "ldir": r["ldir"][:6], "n_ldir": len(r["ldir"])})
        G = c
    return out


if __name__ == "__main__":
    side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
    s0 = [r for r in ROWS if r["P11"]["certified_sides"] == [0] and r["vm"] == "DENSE"]
    res = []
    for r in side1 + s0:
        G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); A.env(r["vm"], r["cell"])
        s = r["P11"]["certified_sides"][0]
        L = [lineage(G, s, r["hex"], k, P) for k in range(3)]
        res.append({"key": r["key"], "cell": r["cell"], "side": s, "cvtr": r["CVTR_accept"],
                    "cvt_n": [r["CVT"][str(s)][c]["n"] for c in ("CVT1", "CVT2", "CVTR")], "lineages": L})
    pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(res, indent=0))
    # compact summary
    def summ(rs):
        c = collections.Counter()
        for x in rs:
            for L in x["lineages"]:
                for e in L:
                    c["inter"] += 1
                    c["exact"] += e["child_eq_parent"]
                    c["fid>=.9"] += e["fid_parent"] >= 0.9
                    c["V_auth"] += e["auth_counts"].get("V", 0)
                    c["D_auth"] += e["auth_counts"].get("D", 0)
                    c["V_steps_in_D"] += e["steps"]["V"]["in_donor_half"]
                    c["V_steps"] += e["steps"]["V"]["n"]
                    c["own_intact"] += e["own_half_intact"]
                    c["V_ldir"] += sum(1 for l in e["ldir"] if l["by"] == "V")
        return dict(c)
    print("side1", summ([x for x in res if x["side"] == 1]))
    print("side0", summ([x for x in res if x["side"] == 0]))
    for x in res[:17]:
        print(x["key"], x["cvt_n"], [[(e["child_eq_parent"], e["fid_parent"], e["auth_counts"].get("V", 0), e["steps"]["V"]["in_donor_half"]) for e in L] for L in x["lineages"]])
