"""Q3 supplement (minimal_prior.py found no passing 2- or 3-byte motif to plant, so the motif family is enumerated
directly).

    python -B plant.py      -> plant.json

(a) All "LD r,n ; copy" programs, zero-padded: r in {B,C,D,E,H,L,(HL),A} (opcodes 06..3E), n in 0..255, copy in
    {E5, E7}: 4,096 programs, dense VM, run_de.competent (cell 7ae3; the verdict is cell-independent, see
    minimal_prior.json cell_check).
(b) Reachability: the motif 1E 40 E5 planted at offset p in uniform random 64-byte genomes (random prefix and suffix),
    p in {0, 4, 8, 16, 32, 48}, 50 genomes per offset.
"""
from __future__ import annotations

import json
import random
import time

import fsetup as F

OUT = F.pathlib.Path(__file__).resolve().parent / "plant.json"
t0 = time.process_time()
rng = random.Random(20260930)
fam = {}
for op in (0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0x36, 0x3E):
    for c in (0xE5, 0xE7):
        ok = [n for n in range(256) if F.competent("7ae3", bytes((op, n, c)) + bytes(61))]
        fam["%02X nn %02X" % (op, c)] = ok
print({k: len(v) for k, v in fam.items()}, round(time.process_time() - t0, 1), flush=True)
reach = {}
for off in (0, 4, 8, 16, 32, 48):
    k = 0
    for _ in range(50):
        g = bytearray(rng.randrange(256) for _ in range(64))
        g[off:off + 3] = b"\x1e\x40\xe5"
        k += F.competent("7ae3", bytes(g))
    reach[off] = k / 50
print(reach, flush=True)
OUT.write_text(json.dumps({"family_passing_n": fam, "family_counts": {k: len(v) for k, v in fam.items()},
                           "reach_1E40E5_by_offset": reach, "cpu_s": round(time.process_time() - t0, 1)}, indent=1))
print("cpu", round(time.process_time() - t0, 1))
