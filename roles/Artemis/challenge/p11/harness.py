"""Generation steppers (H-PAIR / H-HOST / H-GUEST / H-TV / H-QUAD) and the P-11 wrapper."""
from __future__ import annotations

import random

from common import p11, C, FRESH, shabytes, fid
import specimens as S

DRAWS = 3
GENS = 4


# ------------------------------------------------------------------ steppers
def pair_run(vm, n, tape_len, budget, mask, G, side, other, cmr=0.0, rng_seed=0):
    ga, gb = (G, other) if side == 0 else (other, G)
    tape, prov, lit, wo = p11.interact(vm, n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                       budget=budget, ops_mask=mask, cmr=cmr, rng=random.Random(rng_seed))
    return tape, prov, wo


def host_run(vm, sp, G, pre):
    """H-HOST (AMENDMENT item 4). Returns (child bytes, meta)."""
    mem = bytearray(256)
    mem[0:64] = G
    mem[128:256] = pre
    st = {"pending": False, "child": None, "births": 0}

    def on_alloc(ctx, want):
        st["pending"] = True
        ctx.free_lo, ctx.free_hi = 128, 256
        return 128

    def on_birth(ctx, dst, cnt, partial):
        if not st["pending"]:
            return False
        st["child"] = bytes(mem[128:192])
        st["births"] += 1
        return True

    regs, fz, fc, pc = None, 0, 0, 0
    blocked = slices = 0
    for s in range(10):
        ctx = vm.Ctx(mem, 0, 64, policy=vm.FREE, rng=random.Random(0), copy_mut_rate=0.0, sense=0)
        ctx.regs, ctx.fz, ctx.fc = regs, fz, fc
        if st["pending"]:
            ctx.free_lo, ctx.free_hi = 128, 256
        ctx.on_alloc, ctx.on_birth = on_alloc, on_birth
        npc = vm.run(ctx, pc, sp.budget, ops_enabled=sp.mask)
        pc = 0 if ctx.halted else npc
        regs, fz, fc = ctx.regs, ctx.fz, ctx.fc
        blocked += ctx.writes_blocked
        slices += 1
        if st["child"] is not None:
            break
    child = st["child"] if st["child"] is not None else bytes(mem[128:192])
    wrote = sum(1 for i in range(64) if child[i] != pre[i])
    return child, {"births": st["births"], "slices": slices, "writes_blocked": blocked, "wrote": wrote,
                   "repl": st["births"] > 0 and fid(G, child) >= C["REPL_FIDELITY"]
                   and wrote >= C["REPL_WROTE_SHARE"] * 64}


def step(vm, sp, G, g, k):
    """One generation of the specimen's lineage under draw (g, k), copy mutation 0."""
    n = sp.n
    if sp.kind == "pair":
        vb = shabytes("VICTIM", sp.id, g, k, n=n)
        tape, _, _ = pair_run(vm, n, sp.tape_len, sp.budget, sp.mask, G, sp.side, vb)
        v0 = n if sp.side == 0 else 0
        return bytes(tape[v0:v0 + n])
    if sp.kind == "host":
        return host_run(vm, sp, G, shabytes("SLOT", sp.id, g, k, n=128))[0]
    if sp.kind == "guest":
        host = S.Z5A_HOST + shabytes("HOSTCARGO", sp.id, g, k, n=n - len(S.Z5A_HOST))
        tape, _, _ = pair_run(vm, n, sp.tape_len, sp.budget, sp.mask, host, 0, G)
        return bytes(tape[0:n])
    if sp.kind == "quad":
        tape = bytearray(4 * n)
        tape[0:2 * n] = G
        tape[2 * n:4 * n] = shabytes("QUAD", sp.id, g, k, n=2 * n)
        for base in (0, n):
            ctx = vm.Ctx(tape, base, n, policy=vm.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=0)
            vm.run(ctx, base, sp.budget, ops_enabled=0xFF)
        return bytes(tape[2 * n:4 * n])
    raise ValueError(sp.kind)


# ------------------------------------------------------------------ P-11 as implemented
def p11_event(vm, *, sid, n, tape_len, budget, mask, cmr, ga, gb, victim_side, K, tag):
    """Observed event (ga, gb) -> P0 on the victim half; then p11.assay with K seeds (unchanged code)."""
    tape, prov, lit, wo = p11.interact(vm, n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                       budget=budget, ops_mask=mask, cmr=cmr,
                                       rng=random.Random(p11.event_seed(tag, sid, "OBS")))
    v0 = 0 if victim_side == 0 else n
    donor = gb if victim_side == 0 else ga
    old = ga if victim_side == 0 else gb
    final = bytes(tape[v0:v0 + n])
    fo, fs, dw = fid(donor, final), fid(old, final), wo[1 - victim_side]
    p0 = p11.predecessor_accepts(fo, fs, dw, n)
    runs = []
    for j in range(K):
        res = p11.assay(vm, n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH, budget=budget,
                        ops_mask=mask, cmr=cmr, victim_side=victim_side, seed=(tag, sid, j))
        runs.append(res)
    npass = sum(r["pass"] for r in runs)
    fids = [d["fid_final"] for r in runs for d in r["draws"]]
    return {"victim_side": victim_side, "P0": bool(p0), "obs_fid_other": round(fo, 4), "obs_fid_self": round(fs, 4),
            "obs_donor_wrote": dw, "assay_pass_rate": round(npass / K, 4), "K": K,
            "C2_rate": round(sum(r["C2_majority"] for r in runs) / K, 4),
            "C4_rate": round(sum(r["C4_majority"] for r in runs) / K, 4),
            "C5_rate": round(sum(r["C5_majority"] for r in runs) / K, 4),
            "mean_fid_final": round(sum(fids) / len(fids), 4),
            "certify": bool(p0 and npass / K >= 0.5)}


def fert_children(vm, *, sid, n, tape_len, budget, mask, cmr, ga, gb, victim_side, tag):
    """Children of draws k = 0..2 of assay seed j = 0, regenerated exactly as p11.assay does."""
    seed = (tag, sid, 0)
    v0 = 0 if victim_side == 0 else n
    out = []
    for k in range(C["P11_DRAWS"]):
        vr = random.Random(p11.event_seed(seed, "victim", k))
        vb = bytes(vr.randrange(256) for _ in range(n))
        tape, _, _, _ = p11.interact(vm, n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                     budget=budget, ops_mask=mask, cmr=cmr,
                                     rng=random.Random(p11.event_seed(seed, "copy", k)),
                                     victim_side=victim_side, victim_bytes=vb)
        out.append(bytes(tape[v0:v0 + n]))
    return out


def fert(vm, *, sid, n, tape_len, budget, mask, cmr, donor_side, ga, gb, tag, certified):
    if not certified:
        return {"accept": False, "children_pass": None}
    vs = 1 - donor_side
    kids = fert_children(vm, sid=sid, n=n, tape_len=tape_len, budget=budget, mask=mask, cmr=cmr, ga=ga, gb=gb,
                         victim_side=vs, tag=tag)
    passes = []
    for k, ch in enumerate(kids):
        cga, cgb = (ch, bytes(n)) if donor_side == 0 else (bytes(n), ch)
        r = p11.assay(vm, n=n, tape_len=tape_len, ga=cga, gb=cgb, st_a=FRESH, st_b=FRESH, budget=budget,
                      ops_mask=mask, cmr=cmr, victim_side=vs, seed=("FERT", sid, k))
        passes.append(bool(r["pass"]))
    return {"accept": sum(passes) >= 2, "children_pass": passes}
