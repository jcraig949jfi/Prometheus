"""Step 4: execution-order / partner-interference decomposition.
interact2 = p11.interact with an explicit run order and the option to skip the partner context; checked identical to
p11.interact for the world's order. Per genome, 60 fresh random victims (sha256 'W2-16', key, j) at the donor's
P-11 side, one interaction each, modes:
  WORLD        partner(side0) then donor(side1) for side-1 donors; donor then partner for side-0 donors (= world)
  NO_PARTNER   only the donor's context executes (partner bytes present, never run)
  SWAPPED      the reverse of WORLD order (donor executes first on a side-1 donor)
Per WORLD interaction (side-1 donors): did the partner change the donor half before the donor ran (PRE_DAMAGE)?
did the partner's pc enter the donor half (ENTERED)? who authored the child (V/D share)? is the child a good copy?
Then CVT (certs unchanged) with the step function in NO_PARTNER and SWAPPED modes, Artemis victims."""
import json, random, pathlib, collections, time
from _env import A, ROWS, certs, FRESH, shabytes, traced_dense
import p11

T = traced_dense()


def interact2(z, P, ga, gb, order=(0, 1), trace=False):
    n = P["n"]; tl = P["tape_len"]
    tape = bytearray(tl); tape[0:n] = ga; tape[n:2 * n] = gb
    prov = bytearray(tl); lit = bytearray(tl)
    snaps = []; trs = {}
    for who in order:
        start = 0 if who == 0 else n
        ctx = z.Ctx(tape, start, n, policy=z.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=who)
        ctx.regs, ctx.fz, ctx.fc = None, 0, 0
        ctx.prov, ctx.prov_lit, ctx.who = prov, lit, who + 1
        if trace:
            T._TR = []
        z.run(ctx, start, P["budget"], ops_enabled=P["mask"])
        if trace:
            trs[who] = T._TR; T._TR = None
        snaps.append(bytes(tape))
    return tape, prov, snaps, trs


def per_interaction(r, side, nj=60):
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"]); n = P["n"]
    d0 = 0 if side == 0 else n; v0 = n - d0
    world = (0, 1)
    c = collections.Counter()
    ok_by = collections.defaultdict(lambda: [0, 0])
    for j in range(nj):
        vb = shabytes("W2-16", r["key"], j, n=n)
        ga, gb = (G, vb) if side == 0 else (vb, G)
        for mode, order in (("WORLD", world), ("NO_PARTNER", (side,)), ("SWAPPED", world[::-1])):
            zz = T if mode == "WORLD" else z
            tape, prov, snaps, trs = interact2(zz, P, ga, gb, order, trace=(mode == "WORLD"))
            child = bytes(tape[v0:v0 + n])
            good = p11.fidelity(G, child) >= 0.9
            exact = child == G
            c[mode + "_good"] += good; c[mode + "_exact"] += exact
            if mode == "WORLD":
                if j < 5:   # identity check vs p11.interact
                    t2 = p11.interact(z, n=n, tape_len=P["tape_len"], ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                      budget=P["budget"], ops_mask=P["mask"], cmr=0.0, rng=random.Random(0))
                    c["identity_mismatch"] += (bytes(t2[0]) != bytes(tape))
                if side == 1:
                    pre = snaps[0][d0:d0 + n] != G
                    ent = any(d0 <= pc < d0 + n for _, pc, _ in trs[0])
                    ndiff = sum(1 for i in range(n) if snaps[0][d0 + i] != G[i])
                    vshare = sum(1 for i in range(n) if prov[v0 + i] == 1) / n
                    cls = ("PRE_DAMAGE" if pre else "CLEAN") + ("+ENTERED" if ent else "")
                    ok_by[cls][0] += good; ok_by[cls][1] += 1
                    if good:
                        c["good_child_V_majority"] += vshare > 0.5
                    c["pre_damage_bytes_sum"] += ndiff
    return dict(c), {k: v for k, v in ok_by.items()}


def cvt_mode(r, side, mode):
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"]); n = P["n"]
    order = {"NO_PARTNER": (side,), "SWAPPED": (1, 0), "WORLD": (0, 1)}[mode]

    def step(Gx, g, k):
        vb = shabytes("VICTIM", r["hex"], g, k, n=n)
        ga, gb = (Gx, vb) if side == 0 else (vb, Gx)
        tape, _, _, _ = interact2(z, P, ga, gb, order)
        v0 = n if side == 0 else 0
        return bytes(tape[v0:v0 + n])
    rows, base = certs.cvt(step, G, r["hex"], False)
    sc = certs.score(rows, n)
    return [sc[c]["n"] for c in ("CVT1", "CVT2", "CVTR")] + [sc["CVTR"]["accept"]]


if __name__ == "__main__":
    t0 = time.time()
    side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
    s0 = [r for r in ROWS if r["P11"]["certified_sides"] == [0] and r["vm"] == "DENSE"]
    s0 = [r for r in s0 if not r["CVTR_accept"]] + [r for r in s0 if r["CVTR_accept"]][:12]
    out = []
    agg = {0: collections.Counter(), 1: collections.Counter()}
    aggcls = collections.defaultdict(lambda: [0, 0])
    for r in side1 + s0:
        s = r["P11"]["certified_sides"][0]
        c, ob = per_interaction(r, s)
        rec = {"key": r["key"], "side": s, "record_cvtr": r["CVTR_accept"], "per_interaction_60": c, "world_by_class": ob}
        for m in ("WORLD", "NO_PARTNER", "SWAPPED"):
            rec["CVT_" + m] = cvt_mode(r, s, m)
        out.append(rec)
        agg[s].update(c)
        for k, v in ob.items():
            aggcls[k][0] += v[0]; aggcls[k][1] += v[1]
        print(r["key"], s, c, ob, rec["CVT_WORLD"], rec["CVT_NO_PARTNER"], rec["CVT_SWAPPED"], round(time.time() - t0))
    summ = {"side%d" % s: dict(agg[s]) for s in (0, 1)}
    summ["side1_world_by_class"] = dict(aggcls)
    for s in (0, 1):
        sel = [o for o in out if o["side"] == s]
        summ["side%d_CVTR_accept" % s] = {m: sum(o["CVT_" + m][3] for o in sel) for m in ("WORLD", "NO_PARTNER", "SWAPPED")}
        summ["side%d_n" % s] = len(sel)
    print(json.dumps(summ, indent=1))
    pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps({"summary": summ, "genomes": out}, indent=1))
