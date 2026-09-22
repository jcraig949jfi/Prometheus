"""NYX-44 POST-RESULT DIAGNOSTIC (not a control; written after block 7 returned n_parts=200).
Question: on a 200-frame uniform-noise sample, does the ancestor's own family (imdownscale(frame, shape, pix))
CONTAIN a setting whose part count is far below 200, and would the ancestor's score prefer it?
If yes, block 7's 200 is a search outcome (the penalty did not win); if no, the cheat control could not
fire either way (it is not eligible). Disposition of c04 is NOT decided here; the frozen rule stands.
Ancestor calls only: goexplore_py.utils.imdownscale (utils.py:67-73), RLEArray.to_np via round trip is skipped
(imdownscale returns RLEArray; .tobytes() is the key, as in try_split_frames goexplore.py:507).
Score formula quoted verbatim from goexplore.py:470-483 (get_dist_score) with target_len = n * cell_split_factor.
"""
import json, sys
from math import log, sqrt
from collections import Counter
sys.path.insert(0, "/pin/robustified")
import numpy as np
from goexplore_py.utils import imdownscale

rng = np.random.default_rng(20260915)
frames = [rng.integers(0, 255, size=(210, 160), dtype=np.uint8) for _ in range(200)]
FACTOR = 0.02

def get_dist_score(dist, n_frames):
    if len(dist) == 1:
        return 0.0
    def ent(d):
        return -sum(log(e) * e for e in d)
    def norment(d):
        return ent(d) / ent([1 / len(d)] * len(d))
    target_len = n_frames * FACTOR
    return norment(dist) / sqrt(abs(len(dist) - target_len) / target_len + 1)

rows = []
shapes = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 3), (4, 4), (8, 8), (7, 25), (16, 16), (40, 40), (159, 209)]
for (w, h) in shapes:
    for pix in (2, 3, 4, 8, 17, 64, 255):
        keys = [imdownscale(f, (w, h), pix).tobytes() for f in frames]
        c = Counter(keys)
        dist = [v / len(frames) for v in c.values()]
        rows.append({"shape_wh": [w, h], "pix": pix, "n_parts": len(c), "score": round(get_dist_score(dist, len(frames)), 4)})
rows.sort(key=lambda r: -r["score"])
out = {"diagnostic": "nyx44_block7_reachability", "post_result": True, "n_frames": 200, "cell_split_factor": FACTOR,
       "settings": len(rows), "settings_with_n_parts_le_20": sum(r["n_parts"] <= 20 for r in rows),
       "best": rows[:8], "n200_best_score": max((r["score"] for r in rows if r["n_parts"] == 200), default=None),
       "shape_7x25_pix17": [r for r in rows if r["shape_wh"] == [7, 25] and r["pix"] == 17]}
print(json.dumps(out, indent=1))
