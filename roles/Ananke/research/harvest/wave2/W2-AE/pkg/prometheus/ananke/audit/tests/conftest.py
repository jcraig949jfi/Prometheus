"""prometheus.ananke.audit tests: CPU only, 2 threads, real engine and real recorded data (read-only).

Data fixtures are looked up from the repository root (the first ancestor holding roles/Ananke), so the suite
runs from the repository and from a staging copy inside a worktree; a test whose data is absent skips."""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"          # an EMPTY value does not hide the GPU on SKULLPORT
os.environ.setdefault("OMP_NUM_THREADS", "2")

import torch  # noqa: E402

assert not torch.cuda.is_available(), "GPU visible: the audit tests are CPU-only"
torch.set_num_threads(2)
