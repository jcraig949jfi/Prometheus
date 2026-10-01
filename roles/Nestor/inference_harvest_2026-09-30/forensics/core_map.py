"""Q1 / Q2 / Q4: per-position knockout maps, STATE_FREE, instruction composition, and source diversity.

    python -B core_map.py [--limit N]      -> core_map.json (one row per sampled genome), progress on stdout

Sample: corpus.json (51,007 competent genomes), strata = (vm, cell, origin_run) [90 strata]; per stratum, sorted by
first_epoch, one genome drawn at random from the early half and one from the late half (a 1-genome stratum gives 1);
seed 20260930. Plus the 8 epoch-700 modal genomes of 7ae3/16000006 (paths700.json).
Screen: run_de.competent (zero entry state, 4-seed stage 1 any pass, 20-seed stage 2 rate >= 0.5), with the job's
VM (dense for DENSE-origin genomes, stock z8 for PLAIN-origin) and the genome's own cell runner, built exactly as
run_ci._run builds it. STATE_FREE = fair_assay R1 and R2 >= 0.5 over 20 seeds, tag "SFL"+hex (run_ci.sf()).
Knockout: each position gets up to 3 random replacement values (distinct, != original; RNG keyed on genome and
position); NECESSARY iff competence is lost in >= 2 of 3 (the third value is only drawn when the first two disagree).
"""
from __future__ import annotations

import collections
import hashlib
import json
import math
import random
import sys
import time

import fsetup as F
import ivm

OUT = F.pathlib.Path(__file__).resolve().parent / "core_map.json"
CORPUS = F.CAMP / "npe-p2-endogenous-heredity-2026-09-27" / "delegates" / "corpus" / "corpus.json"
P700 = F.ARC3 / "delegates" / "forensic_16000006" / "paths700.json"
SEED = 20260930
B, C, D, E, H, L = 0, 1, 2, 3, 4, 5
COPY_OPS = {0xE5: "E5", 0xE7: "E7"}


def sample():
    cor = json.load(open(CORPUS))
    strata = collections.defaultdict(list)
    for x in cor:
        strata[(x["vm"], x["cell"], x["origin_run"])].append(x)
    rng = random.Random(SEED)
    out = []
    for k in sorted(strata):
        s = sorted(strata[k], key=lambda x: (x["first_epoch"], x["hex"]))
        if len(s) == 1:
            picks = [("only", s[0])]
        else:
            h = len(s) // 2
            picks = [("early", rng.choice(s[:h])), ("late", rng.choice(s[h:]))]
        for half, x in picks:
            out.append({"src": "corpus", "vm": x["vm"], "cell": x["cell"], "origin_run": x["origin_run"],
                        "first_epoch": x["first_epoch"], "half": half, "stratum_size": len(s), "hex": x["hex"]})
    for p in json.load(open(P700))["paths"]:
        out.append({"src": "16000006_e700", "vm": "DENSE", "cell": "7ae3", "origin_run": "x_dd_dense_copy/DENSE_COPY/16000006",
                    "first_epoch": 700, "half": "e700", "stratum_size": 8, "hex": p["genome"], "vid": p["vid"]})
    return out, len(cor), len(strata)


def reg_writes(op, op2, dense):
    """Registers among B,C,D,E,H,L an instruction writes (z8 semantics, ops mask 0x2A)."""
    if dense and op in COPY_OPS:
        return {B, C, D, E, H, L}
    if op == 0xED:
        if op2 in (0xB0, 0xB8):
            return {B, C, D, E, H, L}
        if op2 == 0x32:
            return {B, C, H, L}
        return set()
    if 0x40 <= op < 0x80:
        d = (op >> 3) & 7
        return set() if op == 0x76 or d in (6, 7) else {d}
    if op < 0x40 and (op & 7) in (4, 5, 6):
        d = (op >> 3) & 7
        return set() if d in (6, 7) else {d}
    return {0x01: {B, C}, 0x11: {D, E}, 0x21: {H, L}, 0x03: {B, C}, 0x0B: {B, C}, 0x13: {D, E}, 0x1B: {D, E},
            0x23: {H, L}, 0x2B: {H, L}}.get(op, set())


def is_copy(op, op2, dense):
    return (dense and op in COPY_OPS) or (op == 0xED and op2 in (0xB0, 0xB8))


def analyse_trace(g, dense, side=0):
    """Donor execution from zero state on `side`. Main copy = executed block copy moving the most bytes.
    Returns main copy pc and regs, the last setter of each register before it, and executed spans."""
    tape, tr, _, n = ivm.interact(g, side=side, dense=dense, seed=12345)
    ptr = list(ivm.LAST_PARTNER_TRACE)
    base = 0 if side == 0 else n
    tl = len(tape)
    pexec = set()
    for pc, op, regs in ptr:
        for j in range(ivm.ilen(tape, pc, dense)):
            a = (pc + j) % tl
            if base <= a < base + n:
                pexec.add(a - base)
    copies = []
    for i, (pc, op, regs) in enumerate(tr):
        op2 = tape[(pc + 1) % tl]
        if is_copy(op, op2, dense):
            desc = (op == 0xE7) or (op == 0xED and op2 == 0xB8)
            de0 = (regs[D] << 8) | regs[E]
            if i + 1 < len(tr):
                r2 = tr[i + 1][2]
                de1 = (r2[D] << 8) | r2[E]
                moved = ((de0 - de1) if desc else (de1 - de0)) & 0xFFFF
            else:
                moved = 10 ** 6
            copies.append((moved, i))
    execd = collections.defaultdict(list)          # genome position -> [(trace idx, instr start pc, op)]
    for i, (pc, op, regs) in enumerate(tr):
        ln = ivm.ilen(tape, pc, dense)
        for j in range(ln):
            a = (pc + j) % tl
            if base <= a < base + n:
                execd[a - base].append((i, pc, op))
    if not copies:
        return {"main_copy": None, "execd": execd, "tape": tape, "trace": tr, "base": base, "pexec": pexec}
    moved, ci = max(copies)
    pc_c, op_c, regs_c = tr[ci]
    setters = {}
    for rg in (B, C, D, E, H, L):
        for i in range(ci - 1, -1, -1):
            pc, op, _ = tr[i]
            if rg in reg_writes(op, tape[(pc + 1) % tl], dense):
                setters[rg] = (i, pc, op)
                break
    return {"main_copy": (ci, pc_c, op_c, regs_c, moved), "setters": setters, "execd": execd, "tape": tape,
            "trace": tr, "base": base, "n_copies": len(copies), "pexec": pexec}


def span(tape, pc, dense, base, n):
    tl = len(tape)
    return {((pc + j) % tl) - base for j in range(ivm.ilen(tape, pc, dense)) if base <= (pc + j) % tl < base + n}


def pass_side(g, dense, k=10):
    """Zero-state P-11 pass counts per donor side (k seeds each; own tags), as run_dd.assay_one runs each side."""
    r = F.runner("7ae3", dense)
    n, tl = r.L, F.world._pow2(2 * r.L)
    fresh = (None, 0, 0)
    cnt = [0, 0]
    for i in range(k):
        for side in (0, 1):
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            cnt[side] += F.world.p11.assay(F.world.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=fresh, st_b=fresh,
                                           budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=r.copy_mut,
                                           victim_side=1 - side, seed=("FFC-SIDE", g.hex(), i, side))["pass"]
    return cnt


JUMPS = {0x18, 0x20, 0x28, 0x30, 0x38, 0xC3, 0xC2, 0xCA, 0xD2, 0xDA}
STORES = {0x02, 0x12, 0x34, 0x35, 0x36} | {x for x in range(0x70, 0x78) if x != 0x76}


def pre_kind(op, op2, dense):
    if op in JUMPS:
        return "JUMP"
    if op in STORES:
        return "STORE"
    if op == 0xED:
        return "ED_other"
    if reg_writes(op, op2, dense):
        return "REG_BCDEHL_overwritten"
    if 0x80 <= op < 0xC0 or op in (0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE) or op in (0x0A, 0x1A, 0xDB) or             (0x78 <= op < 0x80) or op in (0x3C, 0x3D, 0x3E):
        return "A_or_FLAGS"
    return "NOP_or_other"


def classify(g, dense, nec, side=None):
    """Assign each necessary position one role (first match): COPY, DEST (last setter of D/E), SRC (H/L),
    COUNT (B/C), SELF (executed ED 32), EXEC_PRE (other instruction executed before the main copy),
    EXEC_POST (executed only after it), EXEC_BY_PARTNER (not executed by the donor, but executed by the partner whose pc
    runs into the donor half), NOT_EXEC (executed by neither in the traced draw). Trace side = the side that passes."""
    if side is None:
        cnt = pass_side(g, dense)
        side = 0 if cnt[0] >= cnt[1] else 1
    else:
        cnt = None
    t = analyse_trace(g, dense, side)
    tape, base, n = t["tape"], t["base"], 64
    roles = {}
    motif = set()
    pre = {}
    info = {"n_copies": t.get("n_copies", 0), "side": side, "side_pass_counts": cnt}
    if t["main_copy"]:
        ci, pc_c, op_c, regs_c, moved = t["main_copy"]
        info.update({"copy_pc": pc_c, "copy_op": "%02X" % op_c + ("%02X" % tape[(pc_c + 1) % len(tape)] if op_c == 0xED else ""),
                     "HL": (regs_c[H] << 8) | regs_c[L], "DE": (regs_c[D] << 8) | regs_c[E],
                     "BC": (regs_c[B] << 8) | regs_c[C], "moved": moved})
        sp = {"COPY": span(tape, pc_c, dense, base, n)}
        for nm, rs in (("DEST", (D, E)), ("SRC", (H, L)), ("COUNT", (B, C))):
            s = set()
            for rg in rs:
                if rg in t["setters"]:
                    s |= span(tape, t["setters"][rg][1], dense, base, n)
            sp[nm] = s
        info["set_by_genome"] = {nm: sorted(rg_n for rg_n, rg in zip("BCDEHL", (B, C, D, E, H, L)) if rg in t["setters"]
                                            and rg in {"DEST": (D, E), "SRC": (H, L), "COUNT": (B, C)}[nm]) for nm in ("DEST", "SRC", "COUNT")}
        info["setter_ops"] = {"BCDEHL"[rg]: "%02X" % v[2] for rg, v in t["setters"].items()}
        for nm in ("COPY", "DEST", "SRC", "COUNT"):
            motif |= sp[nm]
        ci_ = ci
    else:
        sp, ci_ = {}, None
    for p in nec:
        role = None
        for nm in ("COPY", "DEST", "SRC", "COUNT"):
            if p in sp.get(nm, ()):
                role = nm
                break
        if role is None:
            ex = t["execd"].get(p, [])
            if any(op == 0xED and tape[(pc + 1) % len(tape)] == 0x32 for _, pc, op in ex):
                role = "SELF"
            elif ex and ci_ is not None and any(i < ci_ for i, _, _ in ex):
                role = "EXEC_PRE"
                i0, pc0, op0 = min(e for e in ex if e[0] < ci_)
                pre[p] = pre_kind(op0, tape[(pc0 + 1) % len(tape)], dense)
            elif ex:
                role = "EXEC_POST" if ci_ is not None else "EXEC_NOCOPY"
            elif p in t["pexec"]:
                role = "EXEC_BY_PARTNER"
            else:
                role = "NOT_EXEC"
        roles[p] = role
    info["motif_positions"] = sorted(motif)
    info["pre_kinds"] = dict(collections.Counter(pre.values()))
    return roles, info


def knockout(cell, g, dense):
    nec, detail = [], []
    for p in range(len(g)):
        rng = random.Random(int(hashlib.sha256(g + bytes([p])).hexdigest()[:16], 16) ^ SEED)
        vals = rng.sample([v for v in range(256) if v != g[p]], 3)
        lost = 0
        tried = 0
        for v in vals:
            m = bytearray(g)
            m[p] = v
            tried += 1
            lost += not F.competent(cell, bytes(m), dense=dense)
            if lost >= 2 or (tried - lost) >= 2:
                break
        detail.append((lost, tried))
        if lost >= 2:
            nec.append(p)
    return nec, detail


def entropy(bs):
    c = collections.Counter(bs)
    return -sum(v / len(bs) * math.log2(v / len(bs)) for v in c.values())


def diversity(g, dense):
    """Q4: after one pair interaction (zero state, random victim), how many distinct DONOR loci are the source of
    the victim half's final bytes (origin tracking through chained block copies; register stores = -1)."""
    rows = []
    for side in (0, 1):
        for s in range(3):
            tape, _, orig, n = ivm.interact(g, side=side, dense=dense, seed=1000 + 17 * s + side, trace=False, orig=True)
            d0 = 0 if side == 0 else n
            v0 = n - d0
            fin = bytes(tape[v0:v0 + n])
            fid = F.world.p11.fidelity(g, fin)
            og = orig[v0:v0 + n]
            loci = {o for o in og if d0 <= o < d0 + n}
            rows.append({"side": side, "fid": round(fid, 4), "donor_loci": len(loci),
                         "reg_stores": sum(o == -1 for o in og), "own_loci": sum(v0 <= o < v0 + n for o in og),
                         "child_distinct_values": len(set(fin)), "child_entropy": round(entropy(fin), 3)})
    best = max(rows, key=lambda r: (r["fid"] >= 0.9, r["donor_loci"], r["fid"]))
    good = [r for r in rows if r["fid"] >= 0.9]
    return {"best": best, "n_draws_fid90": len(good),
            "median_donor_loci_fid90": sorted(r["donor_loci"] for r in good)[len(good) // 2] if good else None,
            "donor_distinct_values": len(set(g)), "donor_entropy": round(entropy(g), 3),
            "donor_zero_bytes": sum(b == 0 for b in g)}


def main():
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    smp, ncor, nstrata = sample()
    if lim:
        smp = smp[:lim]
    t0 = time.process_time()
    rows = []
    for k, x in enumerate(smp):
        g = bytes.fromhex(x["hex"])
        dense = x["vm"] == "DENSE"
        row = dict(x)
        row["competent"] = F.competent(x["cell"], g, dense=dense)
        if row["competent"]:
            row["fair"] = F.fair_rates(x["cell"], g, dense=dense)
            row["state_free"] = all(v >= 0.5 for v in row["fair"].values())
            nec, det = knockout(x["cell"], g, dense)
            roles, info = classify(g, dense, nec)
            row.update({"necessary": nec, "n_necessary": len(nec), "roles": {str(p): r for p, r in roles.items()},
                        "role_counts": dict(collections.Counter(roles.values())), "trace": info,
                        "beyond_motif": len([p for p in nec if p not in set(info["motif_positions"])]),
                        "ko_detail": det, "div": diversity(g, dense)})
        rows.append(row)
        print(k, x["vm"], x["cell"], x["origin_run"][-8:], row["competent"], row.get("n_necessary"), row.get("state_free"),
              round(time.process_time() - t0, 1), flush=True)
        if k % 10 == 0:
            OUT.write_text(json.dumps({"meta": {"n_corpus": ncor, "n_strata": nstrata}, "rows": rows}))
    meta = {"n_corpus": ncor, "n_strata": nstrata, "sample_seed": SEED, "n_sample": len(smp),
            "cpu_s": round(time.process_time() - t0, 1)}
    OUT.write_text(json.dumps({"meta": meta, "rows": rows}))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
