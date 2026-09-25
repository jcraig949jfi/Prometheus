"""P-A02 [T-X05, exploratory-mechanism]: e08 fossil ablation, the original two-arm form (random rank profile
of identical total bond width with cores re-drawn; read mask scrambled at equal bit count), assayed on
held64. An independent draw (seed 802) of P-D08's first two arms. Computational scope: tensor-train
policies in a bounded encounter world."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "P-D08"))
import run_PD08 as D           # noqa: E402

if __name__ == "__main__":
    D.HERE = HERE
    D.main(pid="P-A02", arms=(("ranks", True, False), ("masks", False, True)), seed=802)
