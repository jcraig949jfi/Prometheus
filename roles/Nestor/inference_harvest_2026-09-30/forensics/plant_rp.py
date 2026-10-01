"""Q3 supplement: are the zero-padded passing "LD r,n ; copy" motifs of plant.py real copiers, or zero-painting
artifacts of the NOP padding? Each passing motif is re-screened with 3 uniform random 61-byte paddings.

    python -B plant_rp.py      -> plant_rp.json
"""
from __future__ import annotations

import json
import random
import time

import fsetup as F

HERE = F.pathlib.Path(__file__).resolve().parent
t0 = time.process_time()
rng = random.Random(20260930)
fam = json.load(open(HERE / "plant.json"))["family_passing_n"]
out = {}
for k, ns in fam.items():
    op, c = int(k[:2], 16), int(k[-2:], 16)
    for n in ns:
        hits = sum(F.competent("7ae3", bytes((op, n, c)) + bytes(rng.randrange(256) for _ in range(61))) for _ in range(3))
        out["%02X%02X%02X" % (op, n, c)] = hits
summ = {k: {"motifs": len(v), "pass_3of3": sum(out["%s%02X%s" % (k[:2], n, k[-2:])] == 3 for n in v),
            "pass_ge1": sum(out["%s%02X%s" % (k[:2], n, k[-2:])] >= 1 for n in v)} for k, v in fam.items() if v}
(HERE / "plant_rp.json").write_text(json.dumps({"per_motif_hits_of_3": out, "summary": summ, "cpu_s": round(time.process_time() - t0, 1)}, indent=1))
print(json.dumps(summ), round(time.process_time() - t0, 1))
print({k: v for k, v in out.items() if v == 3})
