"""W2-7 pair layer: the P-11 randomized-victim assay and the run_de COMPETENT screen, re-implemented with
layout hooks so that INTERACTION-level physics (tape length, side order, entry registers, tape rotation,
relative addressing) can be varied. With the stock layout it must reproduce p11.assay draw-for-draw and
run_de.competent verdict-for-verdict; selftest.py checks both against the campaign code.

The P-11 ruler re-executes the interaction under the same physics as the event it certifies. A layout variant
is therefore applied to BOTH the main run and the donor-disabled control (C5), with the same per-draw layout
draw. (In a world implementation the same must hold for world._pair_interact AND p11.interact - see REPORT.)

Screen parameters (identical in cells 7ae3 / ffa6, checked by fsetup): n = 64, slice 300, ops mask 0x2A,
copy mutation 0.002, fresh (zero) entry state.

Layout spec (dict, all optional):
  tape_len  int   (default 128 = _pow2(2n))           RING192 uses 192: halves at 0 and 64, 64-byte zero gap
  gap       "ZERO" | "RAND"                            RAND: bytes beyond 2n are uniform random per draw
  order     "AB" | "RAND"                              RAND: side order drawn per draw (p = 1/2 partner first)
  regs      "ZERO" | "RAND"                            RAND: both contexts' entry registers + flags uniform per draw
  aoff      "NONE" | "ROT" | "REL"                     needs the AOFF vm. ROT: r ~ U[0,128) per draw, aoff = -r for
                                                       both contexts; REL: aoff = base per context
  budget    int   (default 300)
  mask      int   (default 0x2A)
"""
from __future__ import annotations

import hashlib
import pathlib
import random
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
NESTOR = HERE.parents[1]
C9 = NESTOR / "campaigns" / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
import p11  # noqa: E402  (read-only import; uses constants.C)
from constants import C  # noqa: E402

N = 64
SLICE = 300
MASK = 0x2A
CMR = 0.002
K1, K2 = 4, 20


def _layout_draw(layout, seed, k):
    """Per-draw layout randomness, keyed only on the assay seed and draw index (shared by main and control)."""
    lr = random.Random(p11.event_seed(seed, "W2-7-layout", k))
    d = {"swap": False, "regs": (None, None), "flags": ((0, 0), (0, 0)), "r": 0}
    if layout.get("order") == "RAND":
        d["swap"] = lr.random() < 0.5
    if layout.get("regs") == "RAND":
        d["regs"] = tuple([lr.randrange(256) for _ in range(8)] for _ in range(2))
        d["flags"] = tuple((lr.randrange(2), lr.randrange(2)) for _ in range(2))
    if layout.get("aoff") == "ROT":
        d["r"] = lr.randrange(128)
    d["gap"] = None
    if layout.get("gap") == "RAND":
        d["gap"] = bytes(lr.randrange(256) for _ in range(layout.get("tape_len", 128) - 2 * N))
    return d


def interact(vm, *, n, tape_len, ga, gb, st_a, st_b, budget, ops_mask, cmr, rng, layout, ld,
             victim_side=None, victim_bytes=None, donor_disabled=False):
    """p11.interact with layout hooks. With layout == {} it is p11.interact line for line."""
    tape = bytearray(tape_len)
    tape[0:len(ga)] = ga
    tape[n:n + len(gb)] = gb
    if ld.get("gap") is not None:
        tape[2 * n:] = ld["gap"]
    if victim_bytes is not None:
        v0 = 0 if victim_side == 0 else n
        tape[v0:v0 + n] = bytes(victim_bytes)[:n]
    prov = bytearray(tape_len)
    prov_lit = bytearray(tape_len)
    wo = [0, 0]
    seq = [(0, 0, st_a), (1, n, st_b)]
    if ld["swap"]:
        seq.reverse()
    for who, start, st in seq:
        donor = victim_side is not None and who != victim_side
        pol = vm.OWN if (donor_disabled and donor) else vm.ARENA
        ctx = vm.Ctx(tape, start, n, policy=pol, rng=rng, copy_mut_rate=cmr, sense=who)
        regs, fz, fc = st
        if ld["regs"][who] is not None:
            regs = list(ld["regs"][who])
            fz, fc = ld["flags"][who]
        ctx.regs, ctx.fz, ctx.fc = (list(regs) if regs is not None else None), fz, fc
        ctx.prov, ctx.prov_lit, ctx.who = prov, prov_lit, who + 1
        a = layout.get("aoff", "NONE")
        if a == "ROT":
            ctx.aoff = -ld["r"]
        elif a == "REL":
            ctx.aoff = start
        vm.run(ctx, start, budget, ops_enabled=ops_mask)
        wo[who] = ctx.writes_other
    return tape, prov, prov_lit, wo


def assay(vm, *, n, tape_len, ga, gb, st_a, st_b, budget, ops_mask, cmr, victim_side, seed,
          layout=None, early=True):
    """p11.assay with layout hooks. early=True stops as soon as the 2-of-3 verdict is decided and skips the
    donor-disabled control when C2 or C4 already failed; the VERDICT is unchanged (selftest checks it).
    early=False returns the same draw records as p11.assay."""
    layout = layout or {}
    donor = bytes(gb if victim_side == 0 else ga)
    donor_id = 2 if victim_side == 0 else 1
    v0 = 0 if victim_side == 0 else n
    draws, npass, nfail = [], 0, 0
    D_ = C["P11_DRAWS"]
    M_ = C["P11_MAJORITY"]
    for k in range(D_):
        vr = random.Random(p11.event_seed(seed, "victim", k))
        vb = bytes(vr.randrange(256) for _ in range(n))
        cseed = p11.event_seed(seed, "copy", k)
        ld = _layout_draw(layout, seed, k)
        kw = dict(n=n, tape_len=tape_len, ga=ga, gb=gb, st_a=st_a, st_b=st_b, budget=budget,
                  ops_mask=ops_mask, cmr=cmr, victim_side=victim_side, victim_bytes=vb, layout=layout, ld=ld)
        tape, prov, lit, wo = interact(vm, rng=random.Random(cseed), **kw)
        final = bytes(tape[v0:v0 + n])
        D, auth, auth_lit = p11.directed_authorship(donor, vb, final, prov[v0:v0 + n], lit[v0:v0 + n], donor_id)
        fid_final = p11.fidelity(donor, final)
        share = (auth / len(D)) if D else 0.0
        c2 = fid_final >= C["P11_FINAL_FIDELITY"]
        c4 = bool(D) and share >= C["P11_AUTHORSHIP"]
        if early and not (c2 and c4):
            nfail += 1
            if nfail > D_ - M_:
                return {"pass": False, "draws": draws}
            continue
        tape_d, _, _, _ = interact(vm, rng=random.Random(cseed), donor_disabled=True, **kw)
        fid_dis = p11.fidelity(donor, bytes(tape_d[v0:v0 + n]))
        c5 = fid_dis < C["P11_CONTROL_MAX"]
        ok = bool(c2 and c4 and c5)
        draws.append({"k": k, "fid_init": round(p11.fidelity(donor, vb), 4), "fid_final": round(fid_final, 4),
                      "n_directed": len(D), "donor_authored": auth,
                      "donor_authored_share": round(share, 4),
                      "donor_last_wrote_share": round(auth_lit / len(D), 4) if D else 0.0,
                      "fid_donor_disabled": round(fid_dis, 4),
                      "donor_writes_other": wo[1 - victim_side],
                      "C2": bool(c2), "C4": bool(c4), "C5": bool(c5), "pass": ok})
        npass += ok
        nfail += not ok
        if early and npass >= M_:
            return {"pass": True, "draws": draws}
        if early and nfail > D_ - M_:
            return {"pass": False, "draws": draws}
    return {"pass": npass >= M_, "draws": draws}


def assay_one(vm, g, tag, k, layout=None, early=True, sides=(0, 1)):
    """run_dd.assay_one: k seeds, donor on either side; returns (seeds passed, per-side pass counts)."""
    layout = layout or {}
    n = N
    tl = layout.get("tape_len", 128)
    fresh = (None, 0, 0)
    hits, side_hits = 0, [0, 0]
    for i in range(k):
        ok = False
        for side in sides:
            ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
            res = assay(vm, n=n, tape_len=tl, ga=ga, gb=gb, st_a=fresh, st_b=fresh,
                        budget=layout.get("budget", SLICE), ops_mask=layout.get("mask", MASK), cmr=CMR,
                        victim_side=1 - side, seed=("X-DONOR-DISCOVERY", tag, i, side), layout=layout, early=early)
            side_hits[side] += res["pass"]
            ok = ok or res["pass"]
            if ok and early:
                break
        hits += ok
    return hits, side_hits


def competent(vm, g, layout=None, rate=False):
    """run_de.competent: stage 1 (4 seeds, any pass), stage 2 (20 seeds, >= 0.5). Same seed tags.
    rate=True runs all 20 stage-2 seeds (no early stop) and returns (verdict, stage-2 rate, side counts)."""
    g = bytes(g)
    tag = ("X-DD-ESTABLISH", hashlib.sha256(g).hexdigest()[:16])
    h, _ = assay_one(vm, g, tag + (1,), K1, layout)
    if not h:
        return (False, 0.0, [0, 0]) if rate else False
    if rate:
        h2, sh = assay_one(vm, g, tag + (2,), K2, layout, early=True, sides=(0, 1))
        return h2 / K2 >= 0.5, h2 / K2, sh
    # early-stopping stage 2
    h2 = 0
    for i in range(K2):
        hi, _ = _one_seed(vm, g, tag + (2,), i, layout)
        h2 += hi
        if h2 >= K2 / 2:
            return True
        if h2 + (K2 - 1 - i) < K2 / 2:
            return False
    return h2 / K2 >= 0.5


def _one_seed(vm, g, tag, i, layout):
    layout = layout or {}
    n = N
    fresh = (None, 0, 0)
    for side in (0, 1):
        ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
        res = assay(vm, n=n, tape_len=layout.get("tape_len", 128), ga=ga, gb=gb, st_a=fresh, st_b=fresh,
                    budget=layout.get("budget", SLICE), ops_mask=layout.get("mask", MASK), cmr=CMR,
                    victim_side=1 - side, seed=("X-DONOR-DISCOVERY", tag, i, side), layout=layout)
        if res["pass"]:
            return 1, side
    return 0, None
