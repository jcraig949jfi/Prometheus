"""W2-3 shared harness. Read-only on campaign code; never calls Runner.run().

pair() re-implements the VM part of world.Runner._pair_interact (world.py:782-812) without material
tracking, so we can (a) snapshot the tape between side 0 and side 1 and (b) switch copy errors off.
equivalence() checks it against the world's own _pair_interact on random inputs (copy errors off).

Vocabulary used in this folder (operational, see REPORT.md section 1):
  site      = an Org slot (fixed for the run)
  content   = the bytes at a site (genome() in world terms)
  context   = (regs, fz, fc) carried by the site; never reset by relabelling (world.py:812/877)
  pair map  = one call of the VM on the 2n-byte ring, side 0 then side 1
  W         = write-back rule: BASE keeps the ring halves; ATOMIC keeps a half only if promoted
  promoted  = p11.predecessor_accepts(fid_other, fid_self, writes_other_of_the_other_context, n)
"""
from __future__ import annotations

import pathlib
import random
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
NESTOR = HERE.parents[1]
CAMP = NESTOR / "campaigns"
FOR = NESTOR / "inference_harvest_2026-09-30" / "forensics"
for p in (CAMP / "c9x-explore-2026-09-24" / "x_donor_swap", CAMP / "z80atlas-verify-2026-09-22", FOR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import world  # noqa: E402
import p11  # noqa: E402
import run_ds  # noqa: E402
import z8 as Z8PLAIN  # noqa: E402

FID = world._fidelity


def runner_for_spec(spec, seed=1):
    """The C9X runner (ATOMIC class, never run) for a frozen H2 specimen cell, stock VM."""
    world.z8 = Z8PLAIN
    a = run_ds.cells()[spec]
    r = run_ds.runner_cls(world)(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    r._vm = Z8PLAIN
    return r


def corpus_runner(cell):
    """fsetup.runner: the C-A3 dense-VM runner for corpus copiers (cell '7ae3' or 'ffa6')."""
    import fsetup
    r = fsetup.runner(cell, dense=True)
    r._vm = fsetup.DENSE
    return r


def rand_ctx(rng):
    return ([rng.randrange(256) for _ in range(8)], bool(rng.getrandbits(1)), bool(rng.getrandbits(1)))


ZERO = (None, False, False)


def pair(r, ga, gb, sa=ZERO, sb=ZERO, cmr=0.0, rng=None, snap=False):
    """One pair-tape VM call: ga at side 0, gb at side 1. Returns dict with new halves, new contexts,
    writes_other per side, and (if snap) the tape after side 0 only."""
    z8 = world.z8 = getattr(r, "_vm", world.z8)
    n = r.L
    tape = bytearray(world._pow2(2 * n))
    tape[0:len(ga)] = ga
    tape[n:n + len(gb)] = gb
    rng = rng or random.Random(0)
    out = {"wo": [0, 0], "ctx": [None, None], "ops": [0, 0], "copy_bytes": [0, 0]}
    for who, start, st in ((0, 0, sa), (1, n, sb)):
        ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=rng, copy_mut_rate=cmr, sense=who)
        ctx.regs = None if st[0] is None else list(st[0])
        ctx.fz, ctx.fc = st[1], st[2]
        z8.run(ctx, start, r.t["slice"], ops_enabled=r._ops_mask())
        out["ctx"][who] = (None if ctx.regs is None else list(ctx.regs), ctx.fz, ctx.fc)
        out["wo"][who] = ctx.writes_other
        out["ops"][who] = ctx.ops
        out["copy_bytes"][who] = ctx.copy_bytes
        if snap and who == 0:
            out["after0"] = (bytes(tape[0:n]), bytes(tape[n:2 * n]))
    out["na"], out["nb"] = bytes(tape[0:n]), bytes(tape[n:2 * n])
    return out


def promoted(old_self, new_self, old_other, other_wrote, n):
    return p11.predecessor_accepts(FID(old_other, new_self), FID(old_self, new_self), other_wrote, n)


def outcome(r, x, y, side, sx=ZERO, sy=ZERO, cmr=0.0, rng=None, snap=False):
    """x at `side`, partner y at the other side. Returns the x-centred outcome of one interaction."""
    n = r.L
    if side == 0:
        o = pair(r, x, y, sx, sy, cmr, rng, snap)
        nx, ny, wx, wy, cx, cy = o["na"], o["nb"], o["wo"][0], o["wo"][1], o["ctx"][0], o["ctx"][1]
    else:
        o = pair(r, y, x, sy, sx, cmr, rng, snap)
        nx, ny, wx, wy, cx, cy = o["nb"], o["na"], o["wo"][1], o["wo"][0], o["ctx"][1], o["ctx"][0]
    res = {
        "conv": FID(x, ny) >= 0.9,                         # partner half now x-like (any author)
        "conv_prom": promoted(y, ny, x, wx, n),           # ... and promoted (world birth, x credited)
        "keep": FID(x, nx) >= 0.9,                         # own half still x-like
        "imp": FID(y, nx) >= 0.9 and FID(x, nx) < 0.9,    # own half now partner-like
        "imp_prom": promoted(x, nx, y, wy, n),            # x's site relabelled to the partner
        "nx": nx, "ny": ny, "cx": cx, "cy": cy, "raw": o,
    }
    # offspring counts (halves x-like after the interaction) under the two write-back rules
    res["m_base"] = int(res["keep"]) + int(res["conv"])
    keep_atomic = (not res["imp_prom"]) or FID(x, nx) >= 0.9   # restored unless promoted away
    res["m_atomic"] = int(keep_atomic) + int(res["conv_prom"])
    return res


def equivalence(r, trials=200, seed=7):
    """Check pair() against the world's own _pair_interact (copy errors off, mutation off)."""
    rng = random.Random(seed)
    n = r.L
    save_cm, save_mut = r.copy_mut, r._mutate
    r.copy_mut = 0.0
    r._mutate = lambda g: bytes(g)
    a = r._place(bytes(n), 0)
    b = r._place(bytes(n), 1)
    bad = 0
    try:
        for _ in range(trials):
            ga, gb = bytes(rng.randrange(256) for _ in range(n)), bytes(rng.randrange(256) for _ in range(n))
            sa, sb = rand_ctx(rng), rand_ctx(rng)
            for o, g, st in ((a, ga, sa), (b, gb, sb)):
                r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
                r.mem[o.slot:o.slot + n] = g
                o.length = n
                o.regs, o.fz, o.fc = list(st[0]), st[1], st[2]
            mine = pair(r, ga, gb, sa, sb, 0.0)
            r._lin_birth = lambda *k, **kw: None
            world.Runner._pair_interact(r, 0, a, b)
            if (r._genome(a), r._genome(b)) != (mine["na"], mine["nb"]):
                bad += 1
            elif (list(a.regs), a.fz, a.fc) != tuple(mine["ctx"][0]) and [list(a.regs), a.fz, a.fc] != list(mine["ctx"][0]):
                bad += 1
    finally:
        r.copy_mut, r._mutate = save_cm, save_mut
    return bad


def rand_genome(rng, n=64):
    return bytes(rng.randrange(256) for _ in range(n))


import statistics as _st


def spearman(a, b):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    ra, rb = rk(a), rk(b)
    ma, mb = _st.mean(ra), _st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else float("nan")


