"""Q1/Q2 refinement: a dynamic backward slice of the main block copy's operands (run after core_map/reclassify).

    python -B slice.py      -> adds per-genome slice fields to core_map.json

For every competent sampled genome the donor's zero-state execution on its passing side is traced (the same draw
as core_map.classify). Walking backward from the main block copy, needed = {B,C,D,E,H,L}. Each earlier instruction
that writes a needed register or memory byte joins the DATA slice, and its reads (registers, flags, memory at the
effective address) become needed. At the start of the trace:
  - registers still needed are WORLD-SUPPLIED (they come from the entry state);
  - memory still needed inside the donor half are genome DATA bytes (read, not executed).
CONTROL = conditional jumps executed before the main copy, plus their flag slice.
Each necessary position is then classified as: COPY | DATA_SLICE (instruction bytes of the slice) | DATA_READ |
CONTROL | PATH_ONLY (executed before the copy, in neither slice) | OTHER (post-copy / not executed).
It is a single-draw dynamic slice: approximate. Earlier block copies are treated as writing B,C,D,E,H,L only.
"""
from __future__ import annotations

import collections
import json

import core_map as M
import ivm

RN = "BCDEHL"          # z8 index 0..5; 6 = (HL); 7 = A


def rw(op, op2, regs, dense):
    """(reads, writes) as sets of 'B','C','D','E','H','L','A','F' and ('M', addr)."""
    R, W = set(), set()
    hl = (regs[4] << 8) | regs[5]

    def reg(i, read):
        if i == 6:
            R.update("HL")
            (R if read else W).add(("M", hl))
        else:
            (R if read else W).add("BCDEHL?A"[i])
    if M.is_copy(op, op2, dense):
        R.update("BCDEHL")
        W.update("BCDEHLF")
        return R, W
    if op == 0xED:
        if op2 == 0x32:
            W.update("HLBC")
        return R, W
    if 0x40 <= op < 0x80:
        if op != 0x76:
            reg(op & 7, True)
            reg((op >> 3) & 7, False)
        return R, W
    if 0x80 <= op < 0xC0:
        k = (op >> 3) & 7
        reg(op & 7, True)
        R.add("A")
        if k in (1, 3):
            R.add("F")
        W.add("F")
        if k != 7:
            W.add("A")
        return R, W
    lo = op & 7
    if op < 0x40 and lo in (4, 5):
        reg((op >> 3) & 7, True)
        reg((op >> 3) & 7, False)
        W.add("F")
        return R, W
    if op < 0x40 and lo == 6:
        reg((op >> 3) & 7, False)
        return R, W
    pairs = {0x01: "BC", 0x11: "DE", 0x21: "HL", 0x03: "BC", 0x0B: "BC", 0x13: "DE", 0x1B: "DE", 0x23: "HL", 0x2B: "HL"}
    if op in pairs:
        W.update(pairs[op])
        if op not in (0x01, 0x11, 0x21):
            R.update(pairs[op])
        return R, W
    if op in (0x02, 0x12):
        p = "BC" if op == 0x02 else "DE"
        R.update(p)
        R.add("A")
        W.add(("M", (regs["BCDEHL".index(p[0])] << 8) | regs["BCDEHL".index(p[1])]))
        return R, W
    if op in (0x0A, 0x1A):
        p = "BC" if op == 0x0A else "DE"
        R.update(p)
        R.add(("M", (regs["BCDEHL".index(p[0])] << 8) | regs["BCDEHL".index(p[1])]))
        W.add("A")
        return R, W
    if op in (0x20, 0x28, 0x30, 0x38, 0xC2, 0xCA, 0xD2, 0xDA):
        R.add("F")
        return R, W
    if op in (0xC6, 0xD6, 0xE6, 0xEE, 0xF6, 0xFE):
        R.add("A")
        W.add("F")
        if op != 0xFE:
            W.add("A")
        return R, W
    if op == 0xDB:
        W.add("A")
    return R, W


def backward(tr, tape, upto, seed_needed, dense, tl):
    needed = set(seed_needed)
    sl = []
    for i in range(upto - 1, -1, -1):
        pc, op, regs = tr[i]
        R, W = rw(op, tape[(pc + 1) % tl], regs, dense)
        W = {(w[0], w[1] % tl) if isinstance(w, tuple) else w for w in W}
        R = {(r[0], r[1] % tl) if isinstance(r, tuple) else r for r in R}
        if W & needed:
            sl.append(i)
            needed = (needed - W) | R
    return sl, needed


def main():
    d = json.load(open(M.OUT))
    for row in d["rows"]:
        if not row["competent"]:
            continue
        g = bytes.fromhex(row["hex"])
        dense = row["vm"] == "DENSE"
        side = row["trace"]["side"]
        t = M.analyse_trace(g, dense, side)
        if not t["main_copy"]:
            row["slice"] = None
            continue
        tape, tr, base, n = t["tape"], t["trace"], t["base"], 64
        tl = len(tape)
        ci = t["main_copy"][0]
        dsl, need = backward(tr, tape, ci, set("BCDEHL"), dense, tl)
        world_regs = sorted(x for x in need if isinstance(x, str))
        data_read = sorted({a[1] - base for a in need if isinstance(a, tuple) and base <= a[1] < base + n})
        ctrl_i = [i for i in range(ci) if tr[i][1] in (0x20, 0x28, 0x30, 0x38, 0xC2, 0xCA, 0xD2, 0xDA)]
        csl = set(ctrl_i)
        cneed_world = set()
        for i in ctrl_i:
            s2, nd2 = backward(tr, tape, i, {"F"}, dense, tl)
            csl |= set(s2)
            cneed_world |= {x for x in nd2 if isinstance(x, str)}
        pos = lambda idx: set().union(*[M.span(tape, tr[i][0], dense, base, n) for i in idx]) if idx else set()  # noqa: E731
        copy_pos = M.span(tape, tr[ci][0], dense, base, n)
        dpos, cpos = pos(dsl), pos(csl)
        pre_exec = pos(range(ci))
        cls = {}
        for p in row["necessary"]:
            cls[str(p)] = ("COPY" if p in copy_pos else "DATA_SLICE" if p in dpos else "DATA_READ" if p in data_read
                           else "CONTROL" if p in cpos else "PATH_ONLY" if p in pre_exec else "OTHER")
        coll = {str(p): cls[str(p)] for p in row.get("collapse", [])}
        row["slice"] = {"world_regs_at_copy": world_regs, "control_world_regs": sorted(cneed_world),
                        "data_slice_positions": sorted(dpos), "data_read_positions": data_read,
                        "control_positions": sorted(cpos), "slice_size": len(dpos | set(data_read) | copy_pos),
                        "necessary_class": cls, "necessary_class_counts": dict(collections.Counter(cls.values())),
                        "collapse_class_counts": dict(collections.Counter(coll.values())),
                        "slice_instr": [("%02X" % tr[i][1]) for i in sorted(dsl)]}
    M.OUT.write_text(json.dumps(d))


if __name__ == "__main__":
    main()
