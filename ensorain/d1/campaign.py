"""D-series Round 1 runner. python -m ensorain.d1.campaign <round1|dev> """
import sys
import numpy as np
from .core import sample_dials, sample_dials_local, run

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "round1":
        rng = np.random.default_rng(924_001)
        jobs = [dict(life=i, inst=60000 + i, seed=i, dials=sample_dials(rng)) for i in range(4800)]
        run(jobs, "ensorain/runs/d1_round1.jsonl")
    elif which == "round3":
        rng = np.random.default_rng(924_003)
        jobs = [dict(life=i, inst=80000 + i, seed=800000 + i, dials=sample_dials_local(rng)) for i in range(4800)]
        run(jobs, "ensorain/runs/d3_round3.jsonl")
    elif which == "dev3":
        rng = np.random.default_rng(924_998)
        jobs = [dict(life=i, inst=1900 + i, seed=900000 + i, dials=sample_dials_local(rng)) for i in range(200)]
        run(jobs, "ensorain/runs/d3_dev.jsonl")
    elif which == "dev":
        rng = np.random.default_rng(924_999)
        jobs = [dict(life=i, inst=900 + i, seed=i, dials=sample_dials(rng)) for i in range(300)]
        run(jobs, "ensorain/runs/d1_dev.jsonl")
