"""Step 5: causal test. For each side-1 copier, find the smallest edit that makes it register-independent by giving
it an explicit setter, then ask whether that rescues CVT-R under WORLD order (partner side 0 runs first).

Edits searched:
  E1  every single-byte substitution (64 x 255) -- only with --e1 (too slow for the CPU cap; run on 2 genomes)
  E2  a 2-byte 'LD r,v' overwritten at any offset 0..62, r in {B,C,D,E,H,L}, v in {value r holds at the child copy
      op under FRESH, 0}
  E4  the best E2 plus a second E2 (greedy)
Screen: still a good copy from FRESH (own context), then random-register good rate (the 30 s10 sets). Keep the best
edit per class (highest rate, then earliest offset). For kept edits: s11 register-independence (single register in
16 values, others 0), world-order single-interaction good rate (60 victims, s4 victims 'W2-16'), and CVT-R in WORLD
and NO_PARTNER order (s4 interact2/certs.cvt; victims keyed on the ORIGINAL genome hex so arms are paired)."""
import json, pathlib, random, sys, collections, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-16_side1_heredity"))
sys.path.insert(0, str(HERE))
from _env import A, certs, shabytes                       # noqa: E402
import p11                                                # noqa: E402
from s10_side0_register_dependence import trial           # noqa: E402
from s4_order_and_interference import interact2           # noqa: E402
from s1_operand_taint import SEL, own_run, child_copy     # noqa: E402
from s2_fragility_decomposition import randsets           # noqa: E402

REGS = "BCDEHL"
LDOP = {"B": 0x06, "C": 0x0E, "D": 0x16, "E": 0x1E, "H": 0x26, "L": 0x2E}


def rate(z, P, G, side, sets):
    return sum(trial(z, P, G, side, rs) for rs in sets)


def reg_independent(z, P, G, side):
    for ri in (0, 1, 2, 3, 4, 5, 7):
        for v in (1, 2, 3, 7, 15, 31, 63, 64, 65, 100, 127, 128, 129, 192, 200, 255):
            regs = [0] * 8; regs[ri] = v
            if not trial(z, P, G, side, (regs, 0, 0)):
                return False
    return True


def world_rate(z, P, G, key, side=1, nj=60):
    n = 64; good = 0
    for j in range(nj):
        vb = shabytes("W2-16", key, j, n=n)
        ga, gb = (G, vb) if side == 0 else (vb, G)
        tape, _, _, _ = interact2(z, P, ga, gb, (0, 1))
        v0 = 64 if side == 0 else 0
        good += p11.fidelity(G, bytes(tape[v0:v0 + n])) >= 0.9
    return good


def cvtr(z, P, G, orig_hex, side, order):
    def step(Gx, g, k):
        vb = shabytes("VICTIM", orig_hex, g, k, n=64)
        ga, gb = (Gx, vb) if side == 0 else (vb, Gx)
        tape, _, _, _ = interact2(z, P, ga, gb, order)
        v0 = 64 if side == 0 else 0
        return bytes(tape[v0:v0 + 64])
    rows, base = certs.cvt(step, G, orig_hex, False)
    sc = certs.score(rows, 64)
    return {"CVT1": sc["CVT1"]["n"], "CVT2": sc["CVT2"]["n"], "CVTR": sc["CVTR"]["n"], "accept": sc["CVTR"]["accept"]}


def setters(G, cpregs):
    out = []
    for p in range(63):
        for rname in REGS:
            for v in sorted({cpregs[REGS.index(rname)], 0}):
                M = bytearray(G); M[p] = LDOP[rname]; M[p + 1] = v
                out.append((("LD %s,%02X @%d" % (rname, v, p)), bytes(M)))
    return out


def best(z, P, G, side, cands, sets, pre=None):
    top = None
    s5 = sets[:6]
    for lab, M in cands:
        if M == G or not trial(z, P, M, side, None):
            continue
        if pre is not None and rate(z, P, M, side, s5) < pre:
            continue
        k = rate(z, P, M, side, sets)
        if top is None or k > top[0]:
            top = (k, lab, M)
    return top


if __name__ == "__main__":
    t0 = time.time()
    side = 1
    out = {}
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    for r in SEL[side]:
        if only and r["key"] not in only:
            continue
        G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"])
        sets = randsets(r["key"])
        f = own_run(G, side); cp, _ = child_copy(f, side)
        rec = {"orig": {"randregs": rate(z, P, G, side, sets), "reg_indep": reg_independent(z, P, G, side)}}
        # E1
        c1 = [("byte%d=%02X" % (i, x), G[:i] + bytes([x]) + G[i + 1:]) for i in range(64) for x in range(256) if x != G[i]]
        b1 = best(z, P, G, side, c1, sets, pre=4) if "--e1" in sys.argv else None
        # E2
        c2 = setters(G, cp["regs"])
        b2 = best(z, P, G, side, c2, sets)
        # E4 greedy
        b4 = None
        if b2 is not None:
            M2 = b2[2]
            f2 = own_run(M2, side); cp2, _ = child_copy(f2, side)
            c4 = [(b2[1] + " + " + lab, M) for lab, M in setters(M2, cp2["regs"])]
            b4 = best(z, P, M2, side, c4, sets)
            if b4 is not None and b4[0] <= b2[0]:
                b4 = None
        for cls, b in (("E1", b1), ("E2", b2), ("E4", b4)):
            if b is None:
                rec[cls] = None
                continue
            rec[cls] = {"edit": b[1], "randregs": b[0], "hex": b[2].hex()}
        # full evaluation of the best edit reaching the highest rate with fewest bytes, plus the original
        cand = [(cls, rec[cls]) for cls in ("E1", "E2", "E4") if rec[cls]]
        if cand:
            topk = max(c[1]["randregs"] for c in cand)
            cls, e = next(c for c in cand if c[1]["randregs"] == topk)
            M = bytes.fromhex(e["hex"])
            rec["chosen"] = cls
            rec["rescued"] = {"randregs": e["randregs"], "reg_indep": reg_independent(z, P, M, side),
                              "world_good_60": world_rate(z, P, M, r["key"]),
                              "CVT_WORLD": cvtr(z, P, M, r["hex"], side, (0, 1)),
                              "CVT_NO_PARTNER": cvtr(z, P, M, r["hex"], side, (1,))}
        rec["orig"].update({"world_good_60": world_rate(z, P, G, r["key"]),
                            "CVT_WORLD": cvtr(z, P, G, r["hex"], side, (0, 1))})
        out[r["key"]] = rec
        print(r["key"], json.dumps({k: v for k, v in rec.items()}), round(time.time() - t0), flush=True)
    summ = collections.Counter()
    for k, v in out.items():
        summ["n"] += 1
        summ["orig_reg_indep"] += v["orig"]["reg_indep"]
        summ["orig_CVTR_world_accept"] += v["orig"]["CVT_WORLD"]["accept"]
        summ["orig_world_good"] += v["orig"]["world_good_60"]
        summ["orig_randregs"] += v["orig"]["randregs"]
        if "rescued" in v:
            summ["rescued_reg_indep"] += v["rescued"]["reg_indep"]
            summ["rescued_CVTR_world_accept"] += v["rescued"]["CVT_WORLD"]["accept"]
            summ["rescued_CVTR_nopartner_accept"] += v["rescued"]["CVT_NO_PARTNER"]["accept"]
            summ["rescued_world_good"] += v["rescued"]["world_good_60"]
            summ["rescued_randregs"] += v["rescued"]["randregs"]
            summ["chosen_" + v["chosen"]] += 1
    out["_summary"] = dict(summ)
    out["_seconds"] = round(time.time() - t0)
    print(dict(summ))
    (HERE / ("s5_rescue%s.json" % ("_" + only[0].replace(":", "_") if only else ""))).write_text(json.dumps(out, indent=1))
