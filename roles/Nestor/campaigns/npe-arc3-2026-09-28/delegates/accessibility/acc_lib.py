"""Shared helpers for the ARC3 accessibility delegate (read-only use of campaign code).

Computational artificial life: integer programs on the z8 VM. Nothing biological.

Provides
  make(cell, vm)            -> (world module, ATOMIC runner instance) with world.z8 set to the VM
  point_mutant(r, g, rng)   -> g with EXACTLY ONE mutation event drawn from the cell's own operator
                               (world.Runner._mutate conditioned on one event; see verify_operator())
  assay(world, r, g, k, tag)-> run_dd.assay_one (fresh zero-register start, donor on either side)
  classify(world, r, g, tag)-> dict: stage1 hits (4 seeds), rate20 (if stage1), competent, best partial scores
VMs: 'STOCK' (z8), 'DENSE' (run_dc.dense_z8: 0xE5/0xE7 = LDIR/LDDR), 'SHAM' (run_sh.sham_z8).
"""
from __future__ import annotations

import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[2]
W1 = CAMP / "npe-w1-donor-discovery-2026-09-26"
P2 = CAMP / "npe-p2-endogenous-heredity-2026-09-27"
for p in (W1 / "x_dd_dense_copy", W1 / "x_donor_discovery", P2 / "x_p2_sham",
          CAMP / "c9x-explore-2026-09-24" / "x_donor_swap", CAMP / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))

CELLS = {"7ae3": "7ae3f9c1437c8000-s54765-tL-a0", "ffa6": "ffa6b3fb06df72a7-s55806-tL-a0"}
_VMS = {}


def vm(name):
    if name not in _VMS:
        if name == "STOCK":
            import z8
            _VMS[name] = z8
        elif name == "DENSE":
            import run_dc
            _VMS[name] = run_dc.dense_z8()
        elif name == "SHAM":
            import run_sh
            _VMS[name] = run_sh.sham_z8()
    return _VMS[name]


def make(cell, vmname, seed=1):
    import world
    import run_ds
    world.z8 = vm(vmname)
    a = run_ds.cells()[CELLS[cell]]
    r = run_ds.runner_cls(world)(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    return world, r


def opcode_positions(world, g):
    return set(a for a, _ in world.z8.dis(bytes(g)))


def _perturb(g, i, is_op, rng):
    if is_op:
        g[i] = rng.randrange(256)
        return
    u = rng.random()
    if u < 0.45:
        g[i] = (g[i] + rng.randint(-8, 8)) & 0xFF
    elif u < 0.90:
        g[i] ^= 1 << rng.randrange(8)
    else:
        g[i] = rng.randrange(256)


def point_mutant(world, r, g, rng):
    """One mutation event under the cell's operator (OPERAND, LOCAL, both cells).

    Z8_64 (7ae3): each byte independently at rate m, OPERAND skips linear-disassembly opcode
      positions -> conditioned on one event: a uniform operand position, operand perturbation.
    Z8_SLOTTED (ffa6): each 4-byte slot at rate 4m, OPERAND edits byte 1..3 of the slot, and the
      byte is perturbed as an OPCODE (uniform) if it is a linear-dis opcode position.
    Returns (mutant bytes, site).
    """
    g = bytearray(g)
    ops = opcode_positions(world, g)
    c = r.cell
    if c["representation"] == "Z8_SLOTTED":
        s = rng.randrange(max(1, len(g) // 4))
        j = s * 4 + 1 + rng.randrange(3)
        if j < len(g):
            _perturb(g, j, j in ops, rng)
        return bytes(g), j
    cand = [i for i in range(len(g)) if i not in ops]
    if not cand:
        return bytes(g), -1
    i = cand[rng.randrange(len(cand))]
    _perturb(g, i, False, rng)
    return bytes(g), i


def assay(world, r, g, k, tag):
    import run_dd
    return run_dd.assay_one(world, r, bytes(g), tag, k)


def classify(world, r, g, tag, full=True):
    h, dr = assay(world, r, g, 4, (tag, 1))
    out = {"stage1": h, "best_fid_final": max((d["fid_final"] for d in dr), default=0.0),
           "best_auth": max((d["donor_authored_share"] for d in dr), default=0.0),
           "mean_fid_final": sum(d["fid_final"] for d in dr) / max(1, len(dr)),
           "n_c2": sum(d["C2"] for d in dr), "draw_pass": sum(d["pass"] for d in dr), "rate20": None,
           "competent": False}
    if h and full:
        h2, _ = assay(world, r, g, 20, (tag, 2))
        out["rate20"] = h2 / 20
        out["competent"] = h2 / 20 >= 0.5
    return out


def copy_features(g, vmname):
    """Static counts of copy encodings in a genome."""
    g = bytes(g)
    f = {"ed_b0b8": g.count(b"\xed\xb0") + g.count(b"\xed\xb8"), "ed_32": g.count(b"\xed\x32"),
         "alias": (g.count(b"\xe5") + g.count(b"\xe7")) if vmname == "DENSE" else 0}
    return f


def verify_operator(cell, n=4000, seed=7):
    """Empirical check of point_mutant against world._mutate: which positions _mutate touches."""
    world, r = make(cell, "STOCK", seed)
    rng = random.Random(seed)
    touched_op = touched_nonop = touched_off0 = changed = frame_changed = 0
    r.mut_rate = 0.05                     # raise the rate only to get events quickly
    for _ in range(n):
        g = bytes(rng.randrange(256) for _ in range(r.L))
        ops = opcode_positions(world, g)
        m = r._mutate(g)
        if len(m) != len(g):
            frame_changed += 1
            continue
        diff = [i for i in range(len(g)) if g[i] != m[i]]
        if diff:
            changed += 1
        for i in diff:
            if i in ops:
                touched_op += 1
            else:
                touched_nonop += 1
            if i % 4 == 0:
                touched_off0 += 1
        if opcode_positions(world, m) != ops:
            frame_changed += 1
    return {"cell": cell, "genomes": n, "changed": changed, "sites_at_linear_opcode": touched_op,
            "sites_at_operand": touched_nonop, "sites_at_slot_offset0": touched_off0,
            "genomes_whose_linear_frame_changed": frame_changed}
