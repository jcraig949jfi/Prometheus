"""CPU-only process setup for pte_mut (COMMON_RULES_ARC3 s5). Import BEFORE torch anywhere."""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "1")

import pathlib  # noqa: E402
import sys  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent          # .../W2-C/pte_mut
W2C = HERE.parent                                       # .../W2-C
ROOT = HERE.parents[6]                                  # worktree root
HARVEST = ROOT / "roles/Ananke/research/harvest"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch  # noqa: E402

assert not torch.cuda.is_available(), "GPU visible; refusing (CPU-only brief)"
NTHREADS = int(os.environ.get("PTE_MUT_THREADS", "1"))
assert 1 <= NTHREADS <= 2
torch.set_num_threads(NTHREADS)
DEVICE = "cpu"
