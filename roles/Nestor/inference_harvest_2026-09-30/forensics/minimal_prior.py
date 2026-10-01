"""Q3: minimal-copier prior. Single process, VM calls only.

    python -B minimal_prior.py      -> minimal_prior.json

Screen = run_de.competent (zero entry state) on the dense VM, cell 7ae3 runner. The 7ae3 and ffa6 assay parameters
are identical (L=64, slice 300, ops mask 0x2A, copy_mut 0.002, and competent()'s seed tags depend only on the genome
bytes), so the verdict cannot depend on the cell; this is CHECKED here on every pass plus 1,000 random non-pass candidates.
Sets (program at offset 0, then padding to 64 bytes):
  P1Z  all 256 1-byte programs, zero padding            P1R  all 256 x 4 random paddings
  P2Z  all 65,536 2-byte programs, zero padding          P2R  5,000 random 2-byte programs, random padding
  P3Z  10,000 random 3-byte programs, zero padding       P3R  3,000 random 3-byte programs, random padding
  U64  5,000 uniform random 64-byte genomes
  STOCK: P2Z sample 1,000 and P3Z sample 1,000 on the stock z8 (context)
  PLANT: each distinct passing <=3-byte motif found in P2Z/P3Z (up to 12) planted at offsets 0,8,16,32,48 in random
         genomes (random prefix and suffix), 40 genomes per (motif, offset)
"""
from __future__ import annotations

import json
import random
import time

import fsetup as F

OUT = F.pathlib.Path(__file__).resolve().parent / "minimal_prior.json"
rng = random.Random(20260930)
T0 = time.process_time()
res = {}


def rb(n):
    return bytes(rng.randrange(256) for _ in range(n))


def comp(g, dense=True, cell="7ae3"):
    return F.competent(cell, g, dense=dense)


def run_set(name, progs, dense=True):
    t = time.process_time()
    passes = [g for g in progs if comp(g, dense)]
    res[name] = {"n": len(progs), "passes": len(passes), "rate": len(passes) / len(progs),
                 "pass_hex": [g.hex() for g in passes][:400], "cpu_s": round(time.process_time() - t, 1)}
    print(name, res[name]["n"], res[name]["passes"], res[name]["cpu_s"], flush=True)
    OUT.write_text(json.dumps(res, indent=1))
    return passes


pz = lambda p: p + bytes(64 - len(p))          # noqa: E731
pr = lambda p: p + rb(64 - len(p))             # noqa: E731

p1z = run_set("P1Z", [pz(bytes([a])) for a in range(256)])
p1r = run_set("P1R", [pr(bytes([a])) for a in range(256) for _ in range(4)])
p2z = run_set("P2Z", [pz(bytes([a, b])) for a in range(256) for b in range(256)])
p2r = run_set("P2R", [pr(rb(2)) for _ in range(5000)])
p3z = run_set("P3Z", [pz(rb(3)) for _ in range(10000)])
p3r = run_set("P3R", [pr(rb(3)) for _ in range(3000)])
u64 = run_set("U64", [rb(64) for _ in range(5000)])
run_set("STOCK_P2Z", [pz(rb(2)) for _ in range(1000)], dense=False)
run_set("STOCK_P3Z", [pz(rb(3)) for _ in range(1000)], dense=False)

# cell independence check
allpass = p1z + p1r + p2z + p2r + p3z + p3r + u64
nonpass = [pz(rb(3)) for _ in range(500)] + [rb(64) for _ in range(500)]
mism = sum(comp(g, cell="ffa6") != comp(g, cell="7ae3") for g in allpass + nonpass)
res["cell_check"] = {"n_checked": len(allpass) + len(nonpass), "mismatches_7ae3_vs_ffa6": mism}
print("cell_check", res["cell_check"], flush=True)

# planting
motifs = []
for g in p2z + p3z:
    m = g.rstrip(b"\x00")
    if m and m not in motifs:
        motifs.append(m)
plant = {}
for m in motifs[:12]:
    for off in (0, 8, 16, 32, 48):
        k = 0
        for _ in range(40):
            g = bytearray(rb(64))
            g[off:off + len(m)] = m
            k += comp(bytes(g))
        plant["%s@%d" % (m.hex(), off)] = k / 40
res["PLANT"] = plant
res["n_motifs_found"] = len(motifs)
res["cpu_total_s"] = round(time.process_time() - T0, 1)
OUT.write_text(json.dumps(res, indent=1))
print("done", res["cpu_total_s"])
