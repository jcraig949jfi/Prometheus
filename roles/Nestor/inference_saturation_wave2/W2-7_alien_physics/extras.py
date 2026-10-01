"""W2-7 mechanism checks (small, static).   python -B extras.py -> PROBE_extras.json

X1  RELADDR side symmetry: is `1E 40 E5` (stock side-0 motif) a donor at SIDE 1 under RELADDR (never on stock)?
X2  SIDERAND: per-draw success of `1E 40 E5` at side 0 when it runs first vs when the random partner runs first.
X3  ROTATE: victim fidelity of `1E 40 E5` vs rotation r (prediction from the period-64 tape: (64 - r)/64 for r < 64).
X4  5x budget: why do 62/128 panel copiers fail with slice 1500? Which P-11 criterion fails (C2 fidelity, C4 authorship).
X5  Post-copy termination: share of panel copiers whose block copy is cut off by the end of the slice (instrumented
    VM copy) - i.e. the long count also acts as the donor's HALT.
"""
from __future__ import annotations

import json
import pathlib
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import alien_pair as AP  # noqa: E402
import probes as P  # noqa: E402
import variants as V  # noqa: E402

T0 = time.process_time()
out = {}
FRESH = (None, 0, 0)
LD0 = {"swap": False, "regs": (None, None), "flags": ((0, 0), (0, 0)), "r": 0, "gap": None}


def victim_fid(vm, g, side, lay, ld, seed):
    n = 64
    ga, gb = (g, bytes(n)) if side == 0 else (bytes(n), g)
    vb = bytes(random.Random(seed).randrange(256) for _ in range(n))
    tape, _, _, _ = AP.interact(vm, n=n, tape_len=lay.get("tape_len", 128), ga=ga, gb=gb, st_a=FRESH, st_b=FRESH,
                                budget=300, ops_mask=0x2A, cmr=0.0, rng=random.Random(seed), layout=lay, ld=ld,
                                victim_side=1 - side, victim_bytes=vb)
    v0 = 0 if side == 1 else n
    return sum(a == b for a, b in zip(tape[v0:v0 + n], g)) / n


# X1
gs = [P.pad(P.CTRL["M_STOCK"], random.Random("X1#%d" % j)) for j in range(20)]
x1 = {}
for vname in ("STOCK", "H_RELADDR"):
    vm, lay, _ = V.get(vname)
    x1[vname] = {"side0_seeds_passed": sum(AP.assay_one(vm, g, ("X1", j), 4, lay, sides=(0,))[0] for j, g in enumerate(gs)),
                 "side1_seeds_passed": sum(AP.assay_one(vm, g, ("X1", j), 4, lay, sides=(1,))[0] for j, g in enumerate(gs)),
                 "of": 4 * len(gs)}
out["X1_reladdr_side_symmetry"] = x1
print("X1", x1, flush=True)

# X2
vm, lay, _ = V.get("STOCK")
x2 = {}
for swap in (False, True):
    ld = dict(LD0, swap=swap)
    f = [victim_fid(vm, g, 0, {}, ld, ("X2", j, k)) for j, g in enumerate(gs) for k in range(10)]
    x2["partner_first" if swap else "donor_first"] = {"n": len(f), "fid>=0.9": sum(x >= 0.9 for x in f),
                                                     "mean_fid": round(sum(f) / len(f), 3)}
out["X2_side_order"] = x2
print("X2", x2, flush=True)

# X3
vm, lay, _ = V.get("F_ROTATE")
x3 = {}
for r in (0, 1, 3, 6, 7, 10, 16, 32, 48, 63, 64, 96, 127):
    ld = dict(LD0, r=r)
    f = [victim_fid(vm, g, 0, lay, ld, ("X3", j)) for j, g in enumerate(gs[:10])]
    x3[r] = {"mean_fid": round(sum(f) / len(f), 3), "pred_(64-r)/64": round(max(0, 64 - r) / 64, 3) if r < 64 else None}
out["X3_rotation_vs_r"] = x3
print("X3", x3, flush=True)

# X4 / X5
d = json.loads((P.FOR / "core_map.json").read_text())
rows = [r for r in d["rows"] if r["vm"] == "DENSE" and str(r["competent"]) == "True"]
pan = json.loads((HERE / "PROBE_panel.json").read_text())
surv1500 = set(pan["STOCK_B1500"]["survivors_idx"])
vm, _, _ = V.get("STOCK")
import ast  # noqa: E402
import types  # noqa: E402
import alien_vm  # noqa: E402
_src = alien_vm.build("DENSE").SOURCE
_old = "                    n = room\n                    ctx.budget_exhausted = True\n"
assert _src.count(_old) == 1
tvm = types.ModuleType("z8_trunc")
tvm.__dict__.update(_DENSE=dict(alien_vm.DENSE_MAP), _HITS=[0], _TRUNC=[0])
exec(compile(_src.replace(_old, _old + "                    _TRUNC[0] += 1\n"), "z8_trunc", "exec"), tvm.__dict__)
crit = {"C2_fail": 0, "C4_fail_given_C2": 0, "C5_fail_given_C2C4": 0, "n_draws": 0}
term = {"copy_truncated_by_slice_end": 0, "n": 0}
for i, r in enumerate(rows):
    g = bytes.fromhex(r["hex"])
    spc = ast.literal_eval(r["trace"]).get("side_pass_counts", [1, 0])
    side = 0 if spc[0] >= spc[1] else 1
    ga, gb = (g, bytes(64)) if side == 0 else (bytes(64), g)
    if i not in surv1500:
        res = AP.assay(vm, n=64, tape_len=128, ga=ga, gb=gb, st_a=FRESH, st_b=FRESH, budget=1500, ops_mask=0x2A,
                       cmr=0.002, victim_side=1 - side, seed=("X4", i), early=False)
        for dd in res["draws"]:
            crit["n_draws"] += 1
            if not dd["C2"]:
                crit["C2_fail"] += 1
            elif not dd["C4"]:
                crit["C4_fail_given_C2"] += 1
            elif not dd["C5"]:
                crit["C5_fail_given_C2C4"] += 1
    # X5: donor alone (as the first-running side or after a zero partner), random victim, slice 300:
    # did a block copy run into the end of the slice (so the copy itself ended the donor's execution)?
    tape = bytearray(128)
    tape[64 * side:64 * side + len(g)] = g
    v0 = 64 * (1 - side)
    tape[v0:v0 + 64] = bytes(random.Random(repr(("X5", i))).randrange(256) for _ in range(64))
    ctx = tvm.Ctx(tape, 64 * side, 64, policy=tvm.ARENA, rng=random.Random(i), copy_mut_rate=0.0, sense=side)
    t0 = tvm._TRUNC[0]
    tvm.run(ctx, 64 * side, 300, ops_enabled=0x2A)
    term["n"] += 1
    term["copy_truncated_by_slice_end"] += tvm._TRUNC[0] > t0
out["X4_budget1500_failure_criteria"] = crit
out["X5_long_copy_terminates_slice"] = term
print("X4", crit, "X5", term, flush=True)
out["cpu_s"] = round(time.process_time() - T0, 1)
(HERE / "PROBE_extras.json").write_text(json.dumps(out, indent=1))
print("cpu", out["cpu_s"])
