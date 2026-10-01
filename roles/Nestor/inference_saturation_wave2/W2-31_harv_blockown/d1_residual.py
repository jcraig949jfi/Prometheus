"""D1 diagnosis (after score.py): where does SO_OP (partner runs, cannot write into the copier's half before the
copier runs) still differ from NO-PARTNER (copier alone, same victim bytes)?
(a) the 60-victim interactions whose SO_OP child != no-partner child: per differing byte, did the copier write it
    (prov_lit == copier) in SO_OP? A byte the copier did not write = the partner's edit of ITS OWN half surviving
    under a partial copy; a byte the copier wrote differently = the copier READ partner-changed data.
(b) q1_competent:59 CVT under SO_OP vs no-partner (certs unchanged), plus the same per-byte split over every
    step call of its CVT run where the two physics give different children.
Writes d1_residual.json."""
import json, pathlib, random, sys, time, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
from _env import A, ROWS, certs, FRESH, shabytes  # noqa: E402
import _arms as W  # noqa: E402
import p11  # noqa: E402

t0 = time.time()
side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
SO, HALT = W.vm("SO_OP"), W.vm("HALT")


def run(z, ga, gb, order):
    tape = bytearray(128); tape[0:64] = ga; tape[64:128] = gb
    lit = bytearray(128); info = {}
    for who in order:
        start = 64 * who
        ctx = z.Ctx(tape, start, 64, policy=z.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=who)
        ctx.regs, ctx.fz, ctx.fc = None, 0, 0
        ctx.prov = bytearray(128); ctx.prov_lit = lit; ctx.who = who + 1
        W.reset(z)
        z.run(ctx, start, 300, ops_enabled=0x2A)
        info[who] = dict(W.counts(z), copy_bytes=ctx.copy_bytes, writes=ctx.writes, ops=ctx.ops, halted=ctx.halted)
    return bytes(tape), lit, info


def split(vb, G):
    a, la, ia = run(SO, vb, G, (0, 1))
    b, lb, ib = run(HALT, vb, G, (1,))
    ca, cb = a[0:64], b[0:64]
    if ca == cb:
        return None
    diff = [i for i in range(64) if ca[i] != cb[i]]
    return {"n_diff": len(diff),
            "diff_not_written_by_copier": sum(1 for i in diff if la[i] != 2),
            "diff_written_by_copier": sum(1 for i in diff if la[i] == 2),
            "copier_copy_bytes_SO": ia[1]["copy_bytes"], "copier_copy_bytes_NP": ib[1]["copy_bytes"],
            "copier_ops_SO": ia[1]["ops"], "copier_ops_NP": ib[1]["ops"],
            "good_SO": p11.fidelity(G, ca) >= 0.9, "good_NP": p11.fidelity(G, cb) >= 0.9}


out = {"a_60victims": [], "b_q1_59": {}}
agg = collections.Counter()
for r in side1:
    G = bytes.fromhex(r["hex"])
    for j in range(60):
        s = split(shabytes("W2-16", r["key"], j, n=64), G)
        if s:
            s.update(key=r["key"], j=j); out["a_60victims"].append(s)
            agg["n"] += 1; agg["diff_bytes"] += s["n_diff"]
            agg["diff_not_written_by_copier"] += s["diff_not_written_by_copier"]
            agg["diff_written_by_copier"] += s["diff_written_by_copier"]
out["a_summary"] = dict(agg)

r = next(x for x in side1 if x["key"] == "b:q1_competent:59")
G = bytes.fromhex(r["hex"])
calls = collections.Counter()


def mk(physics):
    def step(Gx, g, k):
        vb = shabytes("VICTIM", r["hex"], g, k, n=64)
        if physics == "SO":
            t = run(SO, vb, Gx, (0, 1))[0]
            s = split(vb, Gx)
            calls["calls"] += 1
            if s:
                calls["differ"] += 1
                calls["diff_not_written_by_copier"] += s["diff_not_written_by_copier"]
                calls["diff_written_by_copier"] += s["diff_written_by_copier"]
        else:
            t = run(HALT, vb, Gx, (1,))[0]
        return bytes(t[0:64])
    return step


for phys in ("SO", "NP"):
    rows, base = certs.cvt(mk(phys), G, r["hex"], False)
    sc = certs.score(rows, 64)
    out["b_q1_59"][phys] = {"CVT": [sc[c]["n"] for c in ("CVT1", "CVT2", "CVTR")], "accept": sc["CVTR"]["accept"],
                            "base_fid_by_gen": [[round(p11.fidelity(G, base[k][g]), 3) for g in range(4)] for k in range(3)]}
# score.py's adapter run must agree with this driver for SO
out["b_q1_59"]["SO_agrees_with_score_json"] = None
sj = json.loads(HERE.joinpath("score.json").read_text())
g59 = next(g for g in sj["genomes"] if g["key"] == "b:q1_competent:59")
out["b_q1_59"]["SO_agrees_with_score_json"] = g59["SO_OP"]["CVT"] == out["b_q1_59"]["SO"]["CVT"]
out["b_q1_59"]["SO_step_calls"] = dict(calls)
out["seconds"] = round(time.time() - t0, 1)
HERE.joinpath("d1_residual.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "a_60victims"}, indent=1))
for s in out["a_60victims"]:
    print(s)
