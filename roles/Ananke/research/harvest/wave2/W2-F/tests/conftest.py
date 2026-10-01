"""Test setup: W2-F on sys.path; CPU only; the repository root for read-only data fixtures."""
from __future__ import annotations

import os
import pathlib
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"          # an EMPTY value does not hide the GPU on SKULLPORT
os.environ.setdefault("OMP_NUM_THREADS", "2")

HERE = pathlib.Path(__file__).resolve().parent
W2F = HERE.parent
REPO = W2F.parents[5]
for p in (str(W2F), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)
