"""W2-13 step 2b: executed pre-copy chain length for every genome in the analysis, plus pair records in one file.

    python -B lengths.py -> lengths.json
Groups (pair data reused, never recomputed, except the new random hits from pairs_hits_w*.json):
  EVO_SD   48 evolved state-dependent competent genomes, S3 comparators (forensics/s3_pairs.json), function COMPETENT
  EVO_SF   48 evolved state-free genomes, S3 panel, function COMPETENT+STATE_FREE (secondary: different function)
  RAND     random-hit competent genomes: 3 from W2-6 C2 (minimal_prior.json) + new hits (pairs_hits_w*.json)
  PLANT    12 planted 3-byte copier genomes from W2-6 C2 (unevolved, secondary)
Trace (forensics/core_map.analyse_trace = instrumented dense VM, zero entry state, donor on its passing side):
  side: evolved = core_map row trace.side; unevolved = core_map.pass_side (same rule: side with more of 10 passes).
  For each of 5 victim seeds (12345 = core_map's seed, + 4 more) record
    L_pre   distinct genome positions (opcode or operand bytes) executed by the donor BEFORE the main copy op
    L_exec  distinct genome positions executed by the donor at all
    D_pre   dynamic instruction count before the main copy
  and use the median over seeds where a copy was found. pre_set (seed 12345) is kept to classify pairs.
Strict synthetic lethal pair = lethal and confirmed and null == 0 (both singles kept 3/3).
"""
import glob
import json
import pathlib
import statistics
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
C2 = HERE.parent / "W2-6_theory_tournament" / "c2_unevolved_epistasis.json"
sys.path.insert(0, str(FOR))
import os  # noqa: E402
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
            if moved > best:            # same as max(copies): ties -> later index wins in max((moved, i))
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


rows = json.load(open(FOR / "core_map.json"))["rows"]
s3 = json.load(open(FOR / "s3_pairs.json"))
out = []
for grp, key in (("EVO_SD", "comparators"), ("EVO_SF", "panel")):
    for r in s3[key]:
        row = rows[r["idx"]]
        g = bytes.fromhex(row["hex"])
        m = measure(g, row["trace"]["side"])
        out.append({"group": grp, "name": "core%d" % r["idx"], "hex": row["hex"], "cell": r["cell"],
                    "origin_run": r["origin_run"], "n_disp": r["n_disp"],
                    "pairs": [[i, j, bool(l and c), nu] for i, j, l, c, nu in r["pairs"]], **m})
    print(grp, len(out), round(time.process_time() - t0, 1), flush=True)
c2 = json.load(open(C2))
newrows = []
for f in sorted(glob.glob(str(HERE / "pairs_hits_w*.json"))):
    newrows += json.load(open(f))["rows"]
cands = [("RAND" if r["name"].startswith("random_hit") else "PLANT", r["name"], r["hex"], r["n_disp"], r["pairs"])
         for r in c2["rows"] if r["competent"]]
cands += [("RAND", r["name"], r["hex"], r["n_disp"], [[i, j, bool(l and c), nu] for i, j, l, c, nu in r["pairs"]])
          for r in newrows]
for grp, name, hx, nd, pairs in cands:
    g = bytes.fromhex(hx)
    cnt = M.pass_side(g, True)
    side = 0 if cnt[0] >= cnt[1] else 1
    m = measure(g, side)
    out.append({"group": grp, "name": name, "hex": hx, "cell": "7ae3", "n_disp": nd, "pairs": pairs,
                "side_pass_counts": cnt, **m})
print("unevolved", len(cands), round(time.process_time() - t0, 1), flush=True)
for o in out:
    pre = set(o["pre_set"])
    n0 = [x for x in o["pairs"] if x[3] == 0]
    o["n_null0"] = len(n0)
    o["n_strict"] = sum(1 for x in n0 if x[2])
    o["rate_strict"] = o["n_strict"] / len(n0) if n0 else None
    o["n_null0_both_pre"] = sum(1 for x in n0 if x[0] in pre and x[1] in pre)
    o["n_null0_one_pre"] = sum(1 for x in n0 if (x[0] in pre) != (x[1] in pre))
    o["n_disp_pre"] = None  # dispensable set not stored for every group; pair-level classes used instead
json.dump({"seeds": SEEDS, "rows": out, "cpu_s": round(time.process_time() - t0, 1)}, open(HERE / "lengths.json", "w"))
print("done", len(out), round(time.process_time() - t0, 1))
