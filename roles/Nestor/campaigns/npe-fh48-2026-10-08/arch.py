"""Architecture assays for genomes (pure functions of bytes; no world run).

robustness(g)    task robustness to single-byte change: for every position j, the 8 single-bit flips and the
                 +-1..+-4 operand deltas (16 variants); share of variants keeping u_gate >= 0.75. Returns overall share
                 and the per-position vector. Under the world's OPERAND/SLOTTED mutation only slot bytes 1-3 of each
                 4-byte slot are mutated; `robustness_world` restricts to those positions.
copier(g, n)     copy competence through the REAL pair path: g on side 0 against n random partners (fresh runner,
                 world mutation disabled); share converted with a P-11 pass, and share where the copy keeps the
                 task (u_gate >= 0.75).
diff_map(g, ref) positions equal to the reference (e.g. CT_UA), by region.
"""
from __future__ import annotations

import random
import sys
import pathlib

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fh  # noqa: E402

REG = {"copier": range(0, 7), "routine": range(7, 39), "padding": range(39, 64)}
_C = fh.UseCache()


def _variants(b):
    out = {b ^ (1 << k) for k in range(8)}
    out |= {(b + d) & 0xFF for d in (-4, -3, -2, -1, 1, 2, 3, 4)}
    out.discard(b)
    return sorted(out)


def robustness(g):
    g = bytes(g)
    per = []
    for j in range(len(g)):
        vs = _variants(g[j])
        ok = sum(_C.u(g[:j] + bytes([v]) + g[j + 1:]) >= fh.COMP_MIN for v in vs)
        per.append(ok / len(vs))
    world_pos = [j for j in range(len(g)) if j % 4 != 0]
    return {"all": round(sum(per) / len(per), 4),
            "world_positions": round(sum(per[j] for j in world_pos) / len(world_pos), 4),
            "by_region": {k: round(sum(per[j] for j in r if j < len(per)) / len(r), 4) for k, r in REG.items()},
            "per_pos": [round(x, 3) for x in per]}


def copier(g, n=40, seed=45_500_000):
    g = bytes(g)
    rng = random.Random(seed)
    conv = keep = 0
    for t in range(n):
        r = fh.make_runner(seed + t, dict(epochs=1, plant=None))
        a = r._place(g, 0, niche=0)
        b = r._place(bytes(rng.randrange(256) for _ in range(64)), 1, niche=0)
        r._init_state()
        r._mutate = lambda x: bytes(x)
        oid = b.oid
        r._pair_interact(0, a, b)
        if b.oid != oid and r.st[b]["prov"] == "P11":
            conv += 1
            keep += _C.u(r._genome(b)) >= fh.COMP_MIN
    return {"n": n, "p11_conv": round(conv / n, 3), "conv_keeps_task": round(keep / max(1, conv), 3)}


def diff_map(g, ref):
    return {k: sum(1 for j in r if j < len(g) and g[j] == ref[j]) / len(r) for k, r in REG.items()}


if __name__ == "__main__":
    for k in ("CT_UA", "CT_U", "COPY_ONLY"):
        g = fh.PLANTS[k]
        print(k, "u", _C.u(g), "robust", robustness(g)["all"], robustness(g)["by_region"], "copier", copier(g, 20))


# ------------------------------------------------------------------------------------------------ on-tape ruler
_TR = {}


def _tape_runner():
    if "r" not in _TR:
        _TR["r"] = fh.make_runner(47_000_000, dict(epochs=1, plant=None))
    return _TR["r"]


def tape_answer(g, partner, side, inputs):
    """g's first OUT when it executes on the real 128-byte pair tape (dense VM, ARENA policy, the cell's ops mask,
    slice budget, fresh registers) with `partner` in the other half; side 0 runs first, side 1 second, exactly as in
    world._pair_interact. Only g's context receives `inputs`."""
    r = _tape_runner()
    import world
    z8 = world.z8
    n = 64
    tape = bytearray(128)
    halves = (g, partner) if side == 0 else (partner, g)
    tape[0:len(halves[0])] = halves[0]
    tape[n:n + len(halves[1])] = halves[1]
    out = None
    for who, start in ((0, 0), (1, n)):
        ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=random.Random(who), copy_mut_rate=0.0, sense=who,
                     inputs=(inputs if who == side else ()))
        z8.run(ctx, start, r.t["slice"], ops_enabled=r._ops_mask())
        if who == side:
            out = ctx.outputs[0] if ctx.outputs else None
    return out


def tape_use(g, partner, n=16, seed=fh.GATE_SEED):
    """On-tape cue-flip USE score of g with this partner, averaged over both sides: share of matched (v, key) pairs
    answered exactly under r = 0 and r = 1."""
    pairs = fh.xtg2.flip_pairs(seed, n)
    ok = 0
    for side in (0, 1):
        for v, key, base, e0, e1 in pairs:
            a0 = tape_answer(g, partner, side, (v, key, 0))
            a1 = tape_answer(g, partner, side, (v, key, 1))
            ok += (a0 == e0 and a1 == e1)
    return ok / (2 * n)
