import os, sys, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
ROOT = pathlib.Path(__file__).resolve().parents[7]
sys.path.insert(0, str(ROOT))
import torch
assert not torch.cuda.is_available()
torch.set_num_threads(2)
