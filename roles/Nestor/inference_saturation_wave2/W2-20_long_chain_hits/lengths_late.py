"""W2-20 step 2b: L_pre tracing for the S_late hits, with trace_seed/measure COPIED verbatim from W2-13 lengths.py
(that module runs at import, so it is copied, not imported). Output lengths.json = all W2-13 rows (unchanged, reused)
+ new RAND rows (names late_w<W>_k<K>), with the same derived per-row fields as lengths.py.

    python -B lengths_late.py -> lengths.json
"""
import glob
import json
import os
import pathlib
import statistics
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W13 = HERE.parent / "W2-13_chain_length_epistasis"
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
sys.path.insert(0, str(FOR))
os.chdir(FOR)
import core_map as M  # noqa: E402
import ivm  # noqa: E402

SEEDS = (12345, 1, 2, 3, 4)
t0 = time.process_time()


def trace_seed(g, side, seed):
    tape, tr, _, n = ivm.interact(g, side=side, dense=True, seed=seed)
    base = 0 if side == 0 else n
    tl = len(tape)
    ci = None
    best = -1
    for i, (pc, op, regs) in enumerate(tr):
        op2 = tape[(pc + 1) % tl]
        if M.is_copy(op, op2, True):
            desc = (op == 0xE7) or (op == 0xED and op2 == 0xB8)
            de0 = (regs[M.D] << 8) | regs[M.E]
            if i + 1 < len(tr):
                r2 = tr[i + 1][2]
                moved = ((de0 - ((r2[M.D] << 8) | r2[M.E])) if desc else (((r2[M.D] << 8) | r2[M.E]) - de0)) & 0xFFFF
            else:
                moved = 10 ** 6
            if moved > best:
                best, ci = moved, i
            elif moved == best:
                ci = i
    pre, allx = set(), set()
    for i, (pc, op, regs) in enumerate(tr):
        for j in range(ivm.ilen(tape, pc, True)):
            a = (pc + j) % tl
            if base <= a < base + n:
                allx.add(a - base)
                if ci is not None and i < ci:
                    pre.add(a - base)
    return {"copy": ci is not None, "L_pre": len(pre) if ci is not None else None, "L_exec": len(allx),
            "D_pre": ci, "pre": sorted(pre)}


def measure(g, side):
    rs = [trace_seed(g, side, s) for s in SEEDS]
    ok = [r for r in rs if r["copy"]]
    med = lambda k: statistics.median(r[k] for r in ok) if ok else None  # noqa: E731
    return {"side": side, "n_seed_copy": len(ok), "L_pre": med("L_pre"), "L_exec": statistics.median(r["L_exec"] for r in rs),
            "D_pre": med("D_pre"), "L_pre_seed12345": rs[0]["L_pre"], "pre_set": rs[0]["pre"] if rs[0]["copy"] else
            (ok[0]["pre"] if ok else []), "L_pre_by_seed": [r["L_pre"] for r in rs]}


old = json.load(open(W13 / "lengths.json"))["rows"]
new = []
for f in sorted(glob.glob(str(HERE / "pairs_hits_w*.json"))):
    for r in json.load(open(f))["rows"]:
        g = bytes.fromhex(r["hex"])
        cnt = M.pass_side(g, True)
        side = 0 if cnt[0] >= cnt[1] else 1
        m = measure(g, side)
        o = {"group": "RAND", "name": r["name"].replace("rand_", "late_"), "hex": r["hex"], "cell": "7ae3",
             "n_disp": r["n_disp"], "pairs": [[i, j, bool(l and c), nu] for i, j, l, c, nu in r["pairs"]],
             "side_pass_counts": cnt, "source": "W2-20 S_late", **m}
        pre = set(o["pre_set"])
        n0 = [x for x in o["pairs"] if x[3] == 0]
        o["n_null0"] = len(n0)
        o["n_strict"] = sum(1 for x in n0 if x[2])
        o["rate_strict"] = o["n_strict"] / len(n0) if n0 else None
        o["n_null0_both_pre"] = sum(1 for x in n0 if x[0] in pre and x[1] in pre)
        o["n_null0_one_pre"] = sum(1 for x in n0 if (x[0] in pre) != (x[1] in pre))
        o["n_disp_pre"] = None
        new.append(o)
        print(o["name"], o["L_pre"], o["n_null0"], o["n_strict"], flush=True)
json.dump({"seeds": SEEDS, "rows": old + new, "n_new": len(new), "cpu_s": round(time.process_time() - t0, 1)},
          open(HERE / "lengths.json", "w"))
print("done", len(old), len(new), round(time.process_time() - t0, 1))
