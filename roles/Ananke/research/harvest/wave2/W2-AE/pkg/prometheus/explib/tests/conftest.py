"""explib core tests: CPU only, at most 2 threads. The core imports no engine (see test_core_isolation.py)."""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"          # an EMPTY value does not hide the GPU on SKULLPORT
os.environ.setdefault("OMP_NUM_THREADS", "2")
