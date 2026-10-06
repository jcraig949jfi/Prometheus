"""B05 -- what did the W2_K2 summits learn: two SLOTS or keyed MEMORY? (Phase 2-B Beta)

Every summit organism from B03 (any arm) plus the two hand-written solvers is scored, without further evolution, on
neighbouring worlds that separate mechanisms:
  W2_K2 held-out vocabulary (tags in [2^15, 2^16))       -- tag-identity overfit?
  W3_K3 / W4_K4 (K streams, D=1)                          -- slots (fail at K>2) vs indexed memory (transfer)
  W2_K2 delay 4 (NOISE ticks before the asks)             -- robustness to interference ticks
  W2_K2 interleaved asks                                  -- does it need all PUTs before any ASK?
  W2_D2 (K=2, D=2: state = sum of two PUTs)               -- store-last vs accumulate
Readout per organism: held-out reward on each (48 episodes, seed 7), and a mechanism label read from the
behaviour, not the code: SLOT2 if K3 <= .70 and K2 >= .90; GENERAL if K3 >= .90; OTHER otherwise.

PREDICTION (before running): every evolved summit is SLOT2 (K3 ~ .67, the share of asks hitting a stored slot); no
GENERAL organism appears; the hand-written solvers are SLOT2 by construction.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import CAMPAIGN_SEED, SOLVER, manifest
from archaeon.beta.b02_shelf_summit_path import ladder
from archaeon.beta.b01_w2k2_existence import _prog
from archaeon.wse.evolve import evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for

OUT = Path(__file__).resolve().parent / "results"
WORLDS = {
    "W2_K2": WorldSpec("W2_K2", K=2, value_bits=4),
    "W2_K2_heldout_vocab": WorldSpec("W2_K2", K=2, value_bits=4, vocab="heldout"),
    "W3_K3": WorldSpec("W3_K3", K=3, value_bits=4),
    "W4_K4": WorldSpec("W4_K4", K=4, value_bits=4),
    "W2_K2_delay4": WorldSpec("W2_K2_delay4", K=2, value_bits=4, delay=4),
    "W2_K2_interleaved": WorldSpec("W2_K2_il", K=2, value_bits=4, ask_timing="interleaved"),
    "W2_D2": WorldSpec("W2_D2", K=2, D=2, value_bits=4),
}


def profile(m):
    out = {}
    for k, spec in WORLDS.items():
        try:
            out[k] = round(evaluate(m, episodes_for(spec, CAMPAIGN_SEED, "heldout", 7, 48), rng_seed=7)["reward"], 4)
        except Exception as e:                 # noqa: BLE001 -- a world the grammar cannot build is recorded, not fatal
            out[k] = "ERR " + type(e).__name__
    k2, k3 = out["W2_K2"], out["W3_K3"]
    lab = "OTHER"
    if isinstance(k3, float) and k3 >= .90:
        lab = "GENERAL"
    elif isinstance(k2, float) and k2 >= .90 and isinstance(k3, float) and k3 <= .70:
        lab = "SLOT2"
    out["label"] = lab
    return out


LD, ST, ADD, JMP = 5, 6, 7, 18
NEG = lambda k: k & 0xFFFFFFFF                                  # noqa: E731
from archaeon.beta.b01_w2k2_existence import EQ, HALT, IN, JNZ, JZ, LDC, OUT_   # noqa: E402

# POSITIVE CONTROL for GENERAL: a (tag, value) table on the tape at 160.. (outside the 112-word read-only code region), pointer r10, linear search on ASK.
TABLE = _prog([
    (IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, 12),                                # 0-3  PUT? else -> 15
    (IN, 4, 0), (IN, 5, 0), (LDC, 11, 160), (ADD, 12, 11, 10), (ST, 12, 4),             # 4-8  table[ptr] = tag
    (LDC, 13, 1), (ADD, 12, 12, 13), (ST, 12, 5), (LDC, 13, 2), (ADD, 10, 10, 13), (HALT,),   # 9-14 value; ptr += 2
    (IN, 4, 0), (LDC, 12, 160),                                                         # 15-16 ASK: scan from 64
    (LD, 6, 12), (EQ, 3, 6, 4), (JNZ, 3, 4), (LDC, 13, 2), (ADD, 12, 12, 13), (JMP, 0, NEG(-5)),  # 17-22
    (LDC, 13, 1), (ADD, 12, 12, 13), (LD, 7, 12), (OUT_, 7, 0), (HALT,),                # 23-27 found
])


def main(argv):
    OUT.mkdir(exist_ok=True)
    rows = [{"who": "control_GENERAL_table", **profile(manifest(TABLE, n_regs=14, tape_words=256))},
            {"who": "hand_solver_20", **profile(manifest(SOLVER))},
            {"who": "hand_solver_16", **profile(manifest(_prog(ladder()[-1][1])))}]
    b3 = json.loads((OUT / "B03_result.json").read_text(encoding="utf-8"))
    for r in b3["rows"]:
        if r.get("summit_manifest"):
            rows.append({"who": "B03_%s_%d" % (r["arm"], r["seed"]), "first_summit_gen": r["first_summit_gen"],
                         "genome_instr": len(r["summit_manifest"]["genome"]) // 4, "persist": r["summit_manifest"]["persist"],
                         **profile(r["summit_manifest"])})
    for x in rows:
        print(json.dumps(x), flush=True)
    labels = {}
    for x in rows:
        labels[x["label"]] = labels.get(x["label"], 0) + 1
    print("labels", labels)
    (OUT / "B05_result.json").write_text(json.dumps({"probe": "B05", "labels": labels, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
