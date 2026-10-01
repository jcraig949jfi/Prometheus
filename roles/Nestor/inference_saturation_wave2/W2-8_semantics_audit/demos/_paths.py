"""Path setup shared by the W2-8 demos. READ-ONLY with respect to campaign folders: run every demo with `python -B`
so no __pycache__ is written next to the frozen campaign files. Outputs go to demos/out/ in this folder only."""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
NESTOR = HERE.parents[2]                      # roles/Nestor
CAMP = NESTOR / "campaigns"
C9 = CAMP / "z80atlas-verify-2026-09-22"
W1 = CAMP / "npe-w1-donor-discovery-2026-09-26"
ARC3 = CAMP / "npe-arc3-2026-09-28"
FRONT = CAMP / "npe-frontier-2026-09-30"
for p in (C9, CAMP / "c9x-explore-2026-09-24" / "x_donor_swap", W1 / "x_donor_discovery", W1 / "x_dd_dense_copy",
          W1 / "x_dd_establish", ARC3 / "x_a3_fair", NESTOR / "lib"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

FFA6 = "ffa6b3fb06df72a7-s55806-tL-a0"
AE73 = "7ae3f9c1437c8000-s54765-tL-a0"


def dump(name, obj):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=1, default=str))
    print(json.dumps(obj, indent=1, default=str))
