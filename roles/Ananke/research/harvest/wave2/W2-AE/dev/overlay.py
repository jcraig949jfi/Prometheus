"""Import this first in dev scripts: CPU, 2 threads, package overlay (see run_tests.py)."""
import os, sys, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ.setdefault("OMP_NUM_THREADS", "2")
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parents[1]
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO))
import prometheus, prometheus.ananke
prometheus.__path__.append(str(HERE / "pkg/prometheus"))
prometheus.ananke.__path__.append(str(HERE / "pkg/prometheus/ananke"))
import torch
assert not torch.cuda.is_available()
torch.set_num_threads(2)
