"""W2-44 shared: harness = W2-3 common via W2-24 tvm (stock z8, copy errors off, donor ctx ZERO),
panel = W2-24/N17e realized-partner panel (W2-14 BASE bank, N=1000, rng 'N17e'); assay = W2-35 s3 assay."""
import json, sys, pathlib, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
sys.path.insert(0, str(W2 / "W2-24_keep_variant"))
sys.path.insert(0, str(W2 / "W2-35_rotation_leak"))
from tvm import C, pair_t  # noqa
from q1_trace import panel  # noqa
from s3_frames_assay import assay, rot_of  # noqa
from frames import frame  # noqa
r = C.runner_for_spec(C.run_ds.DONOR)
F = C.run_ds.donor_genome()
PAN = panel()
T0 = json.loads((HERE / "t0_genomes.json").read_text())["G"]
GEN = {k: bytes.fromhex(v["hex"]) for k, v in T0.items()}


def A(x, pan=PAN):
    return assay(r, x, pan, F)


def conv_ldirs(x, side, pan=PAN, lim=200):
    """Trace donor x at `side` against the first `lim` panel partners with that side. For each interaction where x
    converts (FID>=0.9 of the partner half), identify the donor-context LDIR(s) whose destination window covers the
    partner half, and label how its DE was reached:
      'direct'   = DE not equal to previous donor LDIR's end (DE set by register code),
      'chained'  = DE == previous donor LDIR's DE+n (post-increment of an earlier LDIR, no DE reload).
    Returns Counter of (k-th donor LDIR, pc mod 64 (own coords), dst mod 128, n_bucket, how)."""
    c = collections.Counter()
    nconv = ntot = 0
    for y, cy, cx, s in pan:
        if s != side:
            continue
        ntot += 1
        if ntot > lim:
            break
        ga, gb, sa, sb = (x, y, C.ZERO, cy) if side == 0 else (y, x, cy, C.ZERO)
        na, nb, ctxs, tr, wl, after0, ld = pair_t(r, ga, gb, sa, sb)
        ny = nb if side == 0 else na
        if C.FID(x, ny) < 0.9:
            continue
        nconv += 1
        mine = [(pc, src, dst, n) for w, pc, src, dst, n, rg in ld if w == side]
        lab = []
        prev_end = None
        for k, (pc, src, dst, n) in enumerate(mine):
            dm = dst & 127
            other = range(64, 128) if side == 0 else range(0, 64)
            covers = (dm in other) or (n > 64 and ((dm + n - 1) & 127) in other) or n >= 128
            how = "chained" if prev_end is not None and dst == prev_end else "direct"
            prev_end = (dst + n) & 0xFFFF
            if covers:
                lab.append((k, pc - 64 * side, dm, "n<=64" if n <= 64 else "n>64", how))
                break
        c[tuple(lab[0]) if lab else ("none",)] += 1
    return {"n_side": min(ntot, lim), "n_conv": nconv, "conv_ldir": {str(k): v for k, v in c.most_common(6)}}
