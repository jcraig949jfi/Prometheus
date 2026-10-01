"""P1 residual diagnosis (not a scored prediction; run after p1_cvtr.py). Side-1 copiers only.
(a) CVT-R with NO partner run (copier context only; partner bytes present) under each arm.
(b) Per interaction (60 W2-16 victims, world order): does the side-0 partner change the copier half before the
copier runs (PRE_DAMAGE); does the partner use a block op (copy_bytes > 0) or only byte stores; good child rate
in each class."""
import json, pathlib, random, sys, time, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
from _env import A, ROWS, certs, FRESH, shabytes  # noqa: E402
import _harv as H  # noqa: E402
import p11  # noqa: E402

t0 = time.time()
ARMS = ("STOCK", "HARV_HALT", "HARV_WRAP")
side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]


def interact(z, ga, gb, order):
    tape = bytearray(128); tape[0:64] = ga; tape[64:128] = gb
    snaps, ctxs = [], {}
    for who in order:
        start = 64 * who
        ctx = z.Ctx(tape, start, 64, policy=z.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=who)
        ctx.regs, ctx.fz, ctx.fc = None, 0, 0
        ctx.prov = bytearray(128); ctx.prov_lit = bytearray(128); ctx.who = who + 1
        z.run(ctx, start, 300, ops_enabled=0x2A)
        snaps.append(bytes(tape)); ctxs[who] = ctx
    return tape, snaps, ctxs


out = {"genomes": [], "summary": {}}
agg = {a: collections.Counter() for a in ARMS}
for r in side1:
    G = bytes.fromhex(r["hex"])
    rec = {"key": r["key"]}
    for arm in ARMS:
        z = H.dense(arm)
        # identity of this interact with p11.interact in world order (first 3 victims)
        for j in range(3):
            vb = shabytes("W2-16", r["key"], j, n=64)
            t1, _, _ = interact(z, vb, G, (0, 1))
            t2 = p11.interact(z, n=64, tape_len=128, ga=vb, gb=G, st_a=FRESH, st_b=FRESH, budget=300, ops_mask=0x2A,
                              cmr=0.0, rng=random.Random(0))[0]
            assert bytes(t1) == bytes(t2)

        def step(Gx, g, k):
            vb = shabytes("VICTIM", r["hex"], g, k, n=64)
            return bytes(interact(z, vb, Gx, (1,))[0][0:64])
        rows, _ = certs.cvt(step, G, r["hex"], False)
        sc = certs.score(rows, 64)
        c = collections.Counter()
        for j in range(60):
            vb = shabytes("W2-16", r["key"], j, n=64)
            tape, snaps, ctxs = interact(z, vb, G, (0, 1))
            pre = snaps[0][64:128] != G
            good = p11.fidelity(G, bytes(tape[0:64])) >= 0.9
            blk = ctxs[0].copy_bytes > 0
            cls = ("PRE_DAMAGE" + ("_BLOCK" if blk else "_BYTE")) if pre else "CLEAN"
            c[cls] += 1; c[cls + "_good"] += good
        rec[arm] = {"CVTR_no_partner": sc["CVTR"]["accept"],
                    "CVT_no_partner": [sc[k]["n"] for k in ("CVT1", "CVT2", "CVTR")], "classes": dict(c)}
        agg[arm].update(c); agg[arm]["CVTR_no_partner_accept"] += sc["CVTR"]["accept"]
    out["genomes"].append(rec)
    print(r["key"], {a: (rec[a]["CVTR_no_partner"], rec[a]["classes"]) for a in ARMS}, round(time.time() - t0), flush=True)
out["summary"] = {a: dict(agg[a]) for a in ARMS}
out["seconds"] = round(time.time() - t0, 1)
print(json.dumps(out["summary"], indent=1))
HERE.joinpath("p1b_residual.json").write_text(json.dumps(out, indent=1))
