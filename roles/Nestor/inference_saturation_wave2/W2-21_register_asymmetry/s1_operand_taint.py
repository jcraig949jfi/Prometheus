"""Step 1: (a) validate the taint interpreter against the real dense z8.run; (b) for every DENSE P-11-certified
single-side copier (17 side-1, 111 side-0), run it in its own context (own base, own sense, own entry, HALT
partner half) from FRESH registers and record the copy op that writes the child: its effective operands
(src = L&127, dst = E&127, count = BC) and, per operand, the label set (inherited register / SELF / SENSE / code).
Also the executed instruction listing from entry to that copy op."""
import json, pathlib, random, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
sys.path.insert(0, str(HERE))
from _env import A, ROWS          # noqa: E402
import p11                        # noqa: E402
from _taint import trun, dis1, REGSET   # noqa: E402

SEL = {s: [r for r in ROWS if r["P11"]["certified"] and r["P11"]["certified_sides"] == [s] and r["vm"] == "DENSE"]
       for s in (0, 1)}


def setup(G, side, n=64, tl=128):
    tape = bytearray(tl); d0 = 0 if side == 0 else n; v0 = n - d0
    tape[d0:d0 + n] = G; tape[v0:v0 + n] = bytes([0x76]) * n
    return tape, d0, v0


def own_run(G, side, rs=None, budget=300):
    """Taint run in own context. rs = (regs8, fz, fc) or None (FRESH)."""
    tape, d0, v0 = setup(G, side)
    regs, fz, fc = (None, 0, 0) if rs is None else (list(rs[0]), rs[1], rs[2])
    res = trun(tape, d0, 64, side, regs, fz, fc, d0, budget)
    res["good"] = p11.fidelity(G, bytes(tape[v0:v0 + 64])) >= 0.9
    res["tape"] = bytes(tape)
    return res


def child_copy(res, side):
    """The copy op that wrote most bytes into the victim half (offset of victim = 64 if side 0 else 0)."""
    v0 = 64 if side == 0 else 0
    best, bw = None, -1
    for c in res["copies"]:
        st = 1 if c["op"] == "LDIR" else -1
        w = sum(1 for k in range(min(c["n"], 256)) if v0 <= (c["dst"] + st * k) % 128 < v0 + 64)
        if w > bw:
            best, bw = c, w
    return best, bw


def validate():
    """taint interpreter == z8.run on tape / regs / flags, own context and partner-entry contexts."""
    mism = 0; tot = 0
    for s in (0, 1):
        for r in SEL[s]:
            G = bytes.fromhex(r["hex"]); _, _, z = A.env(r["vm"], r["cell"])
            rr = random.Random("W2-21-val-" + r["key"])
            for k in range(12):
                rs = None if k == 0 else ([rr.randrange(256) for _ in range(8)], rr.randrange(2), rr.randrange(2))
                for base, sense, pc0 in ((64 * s, s, 64 * s), (64 * (1 - s), 1 - s, 64 * s)):
                    tape, d0, v0 = setup(G, s)
                    if k % 3 == 2:   # random partner half
                        for i in range(64):
                            tape[v0 + i] = rr.randrange(256)
                    t2 = bytearray(tape)
                    regs, fz, fc = (None, 0, 0) if rs is None else (list(rs[0]), rs[1], rs[2])
                    ctx = z.Ctx(t2, base, 64, policy=z.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=sense)
                    ctx.regs, ctx.fz, ctx.fc = (None if regs is None else list(regs)), fz, fc
                    z.run(ctx, pc0, 300, ops_enabled=42)
                    res = trun(tape, base, 64, sense, regs, fz, fc, pc0, 300)
                    ok = bytes(t2) == bytes(tape) and list(ctx.regs) == res["regs"] and ctx.fz == res["fz"] and ctx.fc == res["fc"]
                    mism += not ok; tot += 1
    return {"runs": tot, "mismatches": mism}


def classify(labels):
    inh = sorted(set(labels) & REGSET)
    ctx = sorted(set(labels) & {"SELF", "SENSE", "GETPC"})
    if inh:
        return "INHERITED(" + ",".join(inh) + ")"
    if ctx:
        return "CTX(" + ",".join(ctx) + ")"
    return "CODE"


def listing(G, side, res, upto_step):
    """Executed instructions (in order, deduplicated by pc) up to the child copy op."""
    tape = bytearray(128); d0 = 0 if side == 0 else 64
    tape[d0:d0 + 64] = G; tape[64 - d0:128 - d0] = bytes([0x76]) * 64
    seen = []; out = []
    for pc in res["trace"][:upto_step]:
        if pc in seen:
            continue
        seen.append(pc)
        ln, txt = dis1(tape, pc)
        out.append("%02d:%s %s" % (pc - d0, tape[pc:pc + ln].hex(), txt))
    return out


if __name__ == "__main__":
    val = validate()
    print("validation", val)
    out = {"validation": val, "side0": {}, "side1": {}}
    for s in (0, 1):
        for r in SEL[s]:
            G = bytes.fromhex(r["hex"])
            res = own_run(G, s)
            cp, w = child_copy(res, s)
            if cp is None:
                out["side%d" % s][r["key"]] = {"good": res["good"], "copy": None}
                continue
            # step index of the copy in the trace
            idx = cp["step"]
            rec = {"good": res["good"], "op": cp["op"], "pc_off": (cp["pc"] - 64 * s) % 128, "src": cp["src"],
                   "dst": cp["dst"], "BC": cp["BC"], "n": cp["n"], "victim_bytes": w,
                   "src_from": classify(cp["t_src"]), "dst_from": classify(cp["t_dst"]),
                   "cnt_from": classify(cp["t_cnt"]), "ctrl_from": sorted(set(cp["ctrl"]) & REGSET),
                   "n_copy_ops": len(res["copies"]), "listing": listing(G, s, res, idx)}
            out["side%d" % s][r["key"]] = rec
    # summaries
    summ = {}
    for s in (0, 1):
        recs = [v for v in out["side%d" % s].values() if v.get("op")]
        c = collections.Counter()
        for v in recs:
            for opd in ("src", "dst", "cnt"):
                c[opd + ":" + v[opd + "_from"].split("(")[0]] += 1
            c["ctrl_inherited"] += bool(v["ctrl_from"])
            ninh = sum(v[o + "_from"].startswith("INH") for o in ("src", "dst", "cnt"))
            c["n_inherited_operands=%d" % ninh] += 1
            c["op:" + v["op"]] += 1
            c["copy(src->dst)=%d->%d" % (v["src"], v["dst"])] += 1
        summ["side%d" % s] = {"n": len(recs), **dict(sorted(c.items()))}
        print(s, summ["side%d" % s])
    out["summary"] = summ
    (HERE / "s1_operand_taint.json").write_text(json.dumps(out, indent=1))
