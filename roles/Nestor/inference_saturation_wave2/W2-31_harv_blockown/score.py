"""W2-31 scoring (run only after PREREG freeze and SELFTEST all_pass).
Side-1 copiers (17, side 1) and W2-16 s4 side-0 copiers (18, side 0), arms HALT / BO_OP / SO_OP / BO_BL / SO_BL:
 - CVT-R via Artemis adapter.cvt_side(z, ...) (certs unchanged; the step's p11.interact receives the arm module)
 - 60 W2-16 victims sha256("W2-16", key, j), world order, FRESH regs: good child (fidelity >= 0.9), via p11.interact,
   with a traced re-run (own driver, asserted tape-identical) giving: copier half changed before the copier runs,
   partner block op used, partner dropped writes by kind (and how many would have changed a byte)
 - side 1 only: no-partner run (copier alone) child, for D1
 - P-11 competence (alien_pair.competent) per arm
Writes score.json."""
import json, pathlib, random, sys, time, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
from _env import A, ROWS, FRESH, shabytes  # noqa: E402
import _arms as W  # noqa: E402
import alien_pair as AP, p11  # noqa: E402

assert json.loads(HERE.joinpath("SELFTEST.json").read_text())["all_pass"]
t0 = time.time()
ARMS = ("HALT", "BO_OP", "SO_OP", "BO_BL", "SO_BL")
side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
s0 = [r for r in ROWS if r["P11"]["certified_sides"] == [0] and r["vm"] == "DENSE"]
s0 = [r for r in s0 if not r["CVTR_accept"]] + [r for r in s0 if r["CVTR_accept"]][:12]
assert len(side1) == 17 and len(s0) == 18


def traced(z, ga, gb, order):
    tape = bytearray(128); tape[0:64] = ga; tape[64:128] = gb
    snaps, info = [], {}
    for who in order:
        start = 64 * who
        ctx = z.Ctx(tape, start, 64, policy=z.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=who)
        ctx.regs, ctx.fz, ctx.fc = None, 0, 0
        ctx.prov = bytearray(128); ctx.prov_lit = bytearray(128); ctx.who = who + 1
        W.reset(z)
        z.run(ctx, start, 300, ops_enabled=0x2A)
        snaps.append(bytes(tape)); info[who] = dict(W.counts(z), copy_bytes=ctx.copy_bytes)
    return tape, snaps, info


out = {"genomes": [], "summary": {}}
for r in side1 + s0:
    side = 1 if r in side1 else 0
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"])
    assert (P["n"], P["tape_len"], P["budget"], P["mask"]) == (64, 128, 300, 0x2A), P
    v0 = 0 if side == 1 else 64           # child (victim) half
    c0 = 64 * side                        # copier half
    rec = {"key": r["key"], "side": side, "record_cvtr_side": r["CVT"][str(side)]["CVTR"]["accept"]}
    if side == 1:
        np_ = []
        z = W.vm("HALT")
        for j in range(60):
            vb = shabytes("W2-16", r["key"], j, n=64)
            t, _, _ = traced(z, vb, G, (1,))
            np_.append(bytes(t[0:64]))
        rec["nopartner_good_60"] = sum(p11.fidelity(G, c) >= 0.9 for c in np_)
    for arm in ARMS:
        z = W.vm(arm)
        sc = A.cvt_side(z, G, 64, 128, 300, 0x2A, side, r["hex"])
        a = {"CVT": [sc[c]["n"] for c in ("CVT1", "CVT2", "CVTR")], "accept": sc["CVTR"]["accept"], "inter": []}
        for j in range(60):
            vb = shabytes("W2-16", r["key"], j, n=64)
            ga, gb = (G, vb) if side == 0 else (vb, G)
            tape = p11.interact(z, n=64, tape_len=128, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH, budget=300,
                                ops_mask=0x2A, cmr=0.0, rng=random.Random(0))[0]
            t2, snaps, info = traced(z, ga, gb, (0, 1))
            assert bytes(t2) == bytes(tape)
            child = bytes(tape[v0:v0 + 64])
            good = p11.fidelity(G, child) >= 0.9
            first = info[0]
            row = {"good": good}
            if side == 1:
                row.update(pre=snaps[0][64:128] != G, pblk=first["copy_bytes"] > 0,
                           dHB=first["_HB"], dHBC=first["_HBC"], dHS=first["_HS"], dHSC=first["_HSC"],
                           harv0=first["_HITS"], same_as_nopartner=child == np_[j])
            a["inter"].append(row)
        a["good_60"] = sum(x["good"] for x in a["inter"])
        if side == 1:
            a["p11_competent"] = AP.competent(z, G)
        rec[arm] = a
    out["genomes"].append(rec)
    print(r["key"], side, {k: (rec[k]["accept"], rec[k]["good_60"]) for k in ARMS}, round(time.time() - t0),
          flush=True)

S = {}
for s in (0, 1):
    sel = [g for g in out["genomes"] if g["side"] == s]
    S["side%d" % s] = {"n": len(sel), "record_accept": sum(g["record_cvtr_side"] for g in sel)}
    for arm in ARMS:
        d = {"accept": sum(g[arm]["accept"] for g in sel), "good": sum(g[arm]["good_60"] for g in sel),
             "of": 60 * len(sel)}
        if s == 1:
            d["p11_competent"] = sum(g[arm]["p11_competent"] for g in sel)
            c = collections.Counter()
            for g in sel:
                for x in g[arm]["inter"]:
                    cls = ("PRE_DAMAGE_" + ("BLOCK" if x["pblk"] else "BYTE")) if x["pre"] else "CLEAN"
                    c[cls] += 1; c[cls + "_good"] += x["good"]
                    c["same_as_nopartner"] += x["same_as_nopartner"]
            d["classes"] = dict(c)
        S["side%d" % s][arm] = d
    if s == 1:
        S["side1"]["nopartner_good"] = sum(g["nopartner_good_60"] for g in sel)
out["summary"] = S
out["seconds"] = round(time.time() - t0, 1)
HERE.joinpath("score.json").write_text(json.dumps(out, indent=1))
print(json.dumps(S, indent=1))
