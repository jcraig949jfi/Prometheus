"""Q1: mutational accessibility of usable copy behaviour around NPE's copiers.

Computational artificial life: integer programs on the z8 VM. Nothing biological.

Parts (python q1_landscape.py <part>):
  initial  - arm initial material (RANDOM under STOCK/DENSE/SHAM, PLANT under STOCK), per cell, N genomes:
             static copy-encoding counts (anywhere / at a linear-frame opcode position / at a MUTABLE site),
             fresh-start execution of the copy primitive (does a block copy execute in the donor's slice, how
             many bytes land in the victim half), stage-1 / COMPETENT rate of the genome itself and of one
             one-mutant and one two-mutant under the cell's operator.
  focal    - competent (corpus rate_full >= 0.5) and near-miss (corpus 0 < rate_full < 0.5) genomes, per
             (VM, cell) stratum: K one-mutants and K two-mutants (cell operator), each classified
             (stage1, rate20, COMPETENT, best fid_final, best donor_authored_share); plus a KNOCKOUT walk:
             the executed copy site is destroyed and we ask how many operator steps restore competence.
Outputs q1_initial.json, q1_focal.json.
"""
from __future__ import annotations

import json
import random
import sys
import time

import acc_lib as A

N_INIT = 400
K_NEI = 24
N_FOCAL = 24
PATS = (bytes((0xED, 0xB0)), bytes((0xED, 0xB8)))


def plant(g, prng):
    g = bytearray(g)
    p = prng.randrange(0, len(g) - 1)
    g[p:p + 2] = PATS[prng.randrange(2)]
    return bytes(g)


def copy_sites(world, r, g, vmname):
    """Copy encodings: all occurrences, those whose first byte is a linear-frame opcode position
    (executed if control flows linearly), and those whose defining byte is MUTABLE under the operator."""
    g = bytes(g)
    ops = A.opcode_positions(world, g)
    sites = []
    for i in range(len(g) - 1):
        if g[i] == 0xED and g[i + 1] in (0xB0, 0xB8):
            sites.append((i, "ED"))
    if vmname == "DENSE":
        sites += [(i, "ALIAS") for i in range(len(g)) if g[i] in (0xE5, 0xE7)]
    slotted = r.cell["representation"] == "Z8_SLOTTED"

    def mutable(i):
        return (i % 4 != 0) if slotted else (i not in ops)
    in_frame = [s for s in sites if s[0] in ops]
    return {"n_any": len(sites), "n_in_frame": len(in_frame),
            "n_in_frame_frozen": sum(1 for i, k in in_frame if not mutable(i if k == "ALIAS" else i)),
            "n_in_frame_second_byte_mutable": sum(1 for i, k in in_frame if k == "ED" and mutable(i + 1))}


def fresh_exec(world, r, g, seed=0):
    """Donor on side 0, random victim on side 1, fresh registers, one slice, the cell's mask."""
    z8 = world.z8
    n = r.L
    tl = world._pow2(2 * n)
    rng = random.Random(seed)
    tape = bytearray(tl)
    tape[0:len(g)] = g
    tape[n:2 * n] = bytes(rng.randrange(256) for _ in range(n))
    before = bytes(tape[n:2 * n])
    ctx = z8.Ctx(tape, 0, n, policy=z8.ARENA, rng=random.Random(seed + 1), copy_mut_rate=r.copy_mut, sense=0)
    z8.run(ctx, 0, r.t["slice"], ops_enabled=r._ops_mask())
    after = bytes(tape[n:2 * n])
    donor_bytes_in_victim = sum(1 for i in range(min(len(g), n)) if after[i] == g[i] and before[i] != g[i])
    return {"copy_bytes": ctx.copy_bytes, "world_ops": ctx.world_op_calls, "writes_other": ctx.writes_other,
            "donor_bytes_in_victim": donor_bytes_in_victim}


def part_initial():
    out = {}
    for cell in ("7ae3", "ffa6"):
        for mat, vmname in (("RANDOM", "STOCK"), ("RANDOM", "DENSE"), ("RANDOM", "SHAM"), ("PLANT", "STOCK")):
            world, r = A.make(cell, vmname)
            rng = random.Random(repr(("initial", cell, mat)))
            prng = random.Random(repr(("plant", cell)))
            mrng = random.Random(repr(("mut", cell, mat)))
            agg = {"n": 0, "any": 0, "in_frame": 0, "in_frame_frozen": 0, "exec_copy": 0,
                   "copy_into_victim_ge8": 0, "stage1": 0, "competent": 0, "m1_stage1": 0, "m1_competent": 0,
                   "m2_stage1": 0, "m2_competent": 0, "mean_best_fid": 0.0, "fid_ge_0.5": 0}
            t0 = time.time()
            for j in range(N_INIT):
                g = bytes(rng.randrange(256) for _ in range(r.L))
                if mat == "PLANT":
                    g = plant(g, prng)
                cs = copy_sites(world, r, g, vmname)
                fe = fresh_exec(world, r, g, j)
                c0 = A.classify(world, r, g, ("init", cell, mat, vmname, j))
                m1, _ = A.point_mutant(world, r, g, mrng)
                m2, _ = A.point_mutant(world, r, m1, mrng)
                c1 = A.classify(world, r, m1, ("m1", cell, mat, vmname, j))
                c2 = A.classify(world, r, m2, ("m2", cell, mat, vmname, j))
                agg["n"] += 1
                agg["any"] += cs["n_any"] > 0
                agg["in_frame"] += cs["n_in_frame"] > 0
                agg["in_frame_frozen"] += cs["n_in_frame_frozen"] > 0
                agg["exec_copy"] += (fe["copy_bytes"] > 0 and fe["world_ops"] > 0) if vmname != "SHAM" else 0
                agg["copy_into_victim_ge8"] += fe["donor_bytes_in_victim"] >= 8
                agg["stage1"] += c0["stage1"] > 0
                agg["competent"] += c0["competent"]
                agg["m1_stage1"] += c1["stage1"] > 0
                agg["m1_competent"] += c1["competent"]
                agg["m2_stage1"] += c2["stage1"] > 0
                agg["m2_competent"] += c2["competent"]
                agg["mean_best_fid"] += c0["best_fid_final"] / N_INIT
                agg["fid_ge_0.5"] += c0["best_fid_final"] >= 0.5
            agg["mean_best_fid"] = round(agg["mean_best_fid"], 4)
            agg["wall_s"] = round(time.time() - t0, 1)
            out["%s/%s/%s" % (cell, mat, vmname)] = agg
            print(cell, mat, vmname, agg, flush=True)
    (A.HERE / "q1_initial.json").write_text(json.dumps(out, indent=1))


def knockout_walk(world, r, g, site, rng, steps=12, walks=6):
    """Destroy the executed copy site (replace the defining byte by a non-copy value), then walk
    with the cell's operator (neutral, no selection) and record the first step that is COMPETENT.
    Returns list of first-hit steps (None = not within `steps`)."""
    hits = []
    for w in range(walks):
        x = bytearray(g)
        x[site] = 0x00
        x = bytes(x)
        first = None
        for s in range(1, steps + 1):
            x, _ = A.point_mutant(world, r, x, rng)
            c = A.classify(world, r, x, ("ko", site, w, s))
            if c["competent"]:
                first = s
                break
        hits.append(first)
    return hits


def executed_copy_site(world, r, g, vmname):
    """The copy site whose knockout removes the most fresh-start copy bytes (defining byte index:
    the second byte of ED B0/B8, or the alias byte). None if no knockout reduces copying."""
    g = bytes(g)
    base = fresh_exec(world, r, g, 0)["copy_bytes"]
    cands = [i + 1 for i in range(len(g) - 1) if g[i] == 0xED and g[i + 1] in (0xB0, 0xB8)]
    if vmname == "DENSE":
        cands += [i for i in range(len(g)) if g[i] in (0xE5, 0xE7) and not (i > 0 and g[i - 1] == 0xED)]
    best, drop = None, 0
    for i in cands:
        x = bytearray(g)
        x[i] = 0x00
        d = base - fresh_exec(world, r, bytes(x), 0)["copy_bytes"]
        if d > drop:
            best, drop = i, d
    return best


def part_focal():
    rows = [json.loads(line) for line in open(A.P2 / "delegates" / "corpus" / "q1_partial.jsonl")]
    rng = random.Random(20260928)
    strata = {}
    for x in rows:
        kind = "competent" if x["rate_full"] >= 0.5 else ("near_miss" if x["rate_full"] > 0 else "zero")
        strata.setdefault((x["vm"], x["cell"], kind), []).append(x)
    out = {}
    for (vmn, cell, kind), xs in sorted(strata.items()):
        if kind == "zero":
            continue
        vmname = "DENSE" if vmn == "DENSE" else "STOCK"
        world, r = A.make(cell, vmname)
        rng.shuffle(xs)
        sel = xs[:N_FOCAL]
        agg = {"n_focal": len(sel), "stratum_size": len(xs), "focal_rate_mean": 0.0,
               "m1": {"n": 0, "stage1": 0, "competent": 0, "fid_sum": 0.0},
               "m2": {"n": 0, "stage1": 0, "competent": 0, "fid_sum": 0.0},
               "per_focal_m1_competent_share": [], "copy_site_kind": {}, "knockout_first_hit": []}
        t0 = time.time()
        for fi, x in enumerate(sel):
            g = bytes.fromhex(x["hex"])
            agg["focal_rate_mean"] += x["rate_full"] / len(sel)
            mc = 0
            for k in range(K_NEI):
                m1, _ = A.point_mutant(world, r, g, rng)
                m2, _ = A.point_mutant(world, r, m1, rng)
                for key, m in (("m1", m1), ("m2", m2)):
                    c = A.classify(world, r, m, (key, vmn, cell, fi, k))
                    agg[key]["n"] += 1
                    agg[key]["stage1"] += c["stage1"] > 0
                    agg[key]["competent"] += c["competent"]
                    agg[key]["fid_sum"] += c["best_fid_final"]
                    if key == "m1":
                        mc += c["competent"]
            agg["per_focal_m1_competent_share"].append(round(mc / K_NEI, 3))
            site = executed_copy_site(world, r, g, vmname)
            if site is not None:
                kd = "ED" if g[site] in (0xB0, 0xB8) and site > 0 and g[site - 1] == 0xED else "ALIAS"
                ops = A.opcode_positions(world, g)
                slotted = r.cell["representation"] == "Z8_SLOTTED"
                mutable = (site % 4 != 0) if slotted else (site not in ops)
                key = "%s_%s" % (kd, "mutable" if mutable else "frozen")
                agg["copy_site_kind"][key] = agg["copy_site_kind"].get(key, 0) + 1
                if kind == "competent" and fi < 8:
                    agg["knockout_first_hit"].append(knockout_walk(world, r, g, site, rng))
            else:
                agg["copy_site_kind"]["none_fresh"] = agg["copy_site_kind"].get("none_fresh", 0) + 1
        for key in ("m1", "m2"):
            n = max(1, agg[key]["n"])
            agg[key]["mean_best_fid"] = round(agg[key].pop("fid_sum") / n, 4)
            agg[key]["competent_share"] = round(agg[key]["competent"] / n, 4)
            agg[key]["stage1_share"] = round(agg[key]["stage1"] / n, 4)
        agg["focal_rate_mean"] = round(agg["focal_rate_mean"], 3)
        agg["wall_s"] = round(time.time() - t0, 1)
        out["%s/%s/%s" % (vmn, cell, kind)] = agg
        print(vmn, cell, kind, {k: agg[k] for k in ("n_focal", "m1", "m2", "copy_site_kind", "wall_s")}, flush=True)
        (A.HERE / "q1_focal.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"initial": part_initial, "focal": part_focal}[sys.argv[1]]()
