"""s3 step 3: joint knockouts of sampled dispensable pairs, panel and comparators interleaved (matched order).

    python -B s3_pairs.py [--npairs 200] -> s3_pairs.json (checkpointed)
Per genome: up to NPAIRS pairs from its dispensable set (s3_pipeline.sample_pairs), 3 joint random-value draws
(s3_common.pair_vals), lethal = function lost in >= 2 of 3; each lethal pair re-assayed with seed suffix "/S3R" and
counted only if still lethal. Null per pair = binomial >= 2/3 at q = 1-(1-p_i)(1-p_j). Each position is annotated
from the donor's zero-state trace on its passing side (core_map.analyse_trace): role in the main copy motif, or
executed before / after the main copy, executed only by the partner, or not executed; opcode vs operand byte.
"""
import json
import sys
import time

import core_map as M
import s3_common as S
import s3_pipeline as P

NP = int(sys.argv[sys.argv.index("--npairs") + 1]) if "--npairs" in sys.argv else 200
t0 = time.process_time()
rows = json.load(open("core_map.json"))["rows"]
sg = json.load(open("s3_singles.json"))


def annotate(row, g):
    side = row["trace"]["side"]
    t = M.analyse_trace(g, True, side)
    tape, base = t["tape"], t["base"]
    motif = {}
    ci = None
    if t["main_copy"]:
        ci, pc_c = t["main_copy"][0], t["main_copy"][1]
        for p in M.span(tape, pc_c, True, base, 64):
            motif[p] = "COPY"
        for nm, rs in (("DEST", (M.D, M.E)), ("SRC", (M.H, M.L)), ("COUNT", (M.B, M.C))):
            for rg in rs:
                if rg in t["setters"]:
                    for p in M.span(tape, t["setters"][rg][1], True, base, 64):
                        motif.setdefault(p, nm)
    ann = {}
    for p in range(64):
        ex = t["execd"].get(p, [])
        if p in motif:
            cls = motif[p]
        elif ex and ci is not None and any(i < ci for i, _, _ in ex):
            cls = "EXEC_PRE"
        elif ex:
            cls = "EXEC_POST" if ci is not None else "EXEC_NOCOPY"
        elif p in t["pexec"]:
            cls = "EXEC_BY_PARTNER"
        else:
            cls = "NOT_EXEC"
        first = min(ex) if ex else None
        ann[p] = {"cls": cls, "byte": "%02X" % g[p],
                  "instr": None if first is None else "%02X" % first[2],
                  "is_opcode": None if first is None else (first[1] - base) == p}
    return ann


def run(entry, sf):
    row = rows[entry["idx"]]; g = bytes.fromhex(entry["hex"]); cell = entry["cell"]
    pairs = P.sample_pairs(g, entry["disp"], NP)
    p = {int(k): v for k, v in entry["p"].items()}
    ann = annotate(row, g)
    res = []
    for i, j in pairs:
        l, c = P.pair_call(cell, g, True, sf, i, j)
        res.append([i, j, l, c, S.null_lethal(p[i], p[j])])
    n = len(res); nl = sum(1 for x in res if x[2] and x[3])
    null = sum(x[4] for x in res) / n if n else None
    return {"idx": entry["idx"], "origin_run": entry["origin_run"], "cell": cell, "src": row["src"], "sf": sf,
            "n_disp": len(entry["disp"]), "n_pairs": n, "n_lethal_raw": sum(1 for x in res if x[2]),
            "n_lethal": nl, "rate": nl / n if n else None, "null": null,
            "excess": (nl / n / null) if n and null else (float("inf") if n and nl else None),
            "pairs": res, "ann": {str(k): v for k, v in ann.items()}}


out = {"npairs": NP, "panel": [], "comparators": []}
for k in range(len(sg["panel"])):
    for grp, sf in (("panel", True), ("comparators", False)):
        r = run(sg[grp][k], sf)
        out[grp].append(r)
        print(grp[:4], k, r["origin_run"][-8:], r["n_disp"], r["n_pairs"], r["n_lethal_raw"], r["n_lethal"],
              None if r["null"] is None else round(r["null"], 4), round(time.process_time() - t0, 1), flush=True)
    out["cpu_s"] = round(time.process_time() - t0, 1)
    json.dump(out, open("s3_pairs.json", "w"))
print("cpu", out["cpu_s"])
