"""Calibration of the SIGNAL ruler: assays.pair_ci (percentile bootstrap, fixed seed 0, 2000 resamples)
on 32 mirror pairs. Under true accuracy p0 = 0.55 exactly, how often is lo99 > 0.55 (false SIGNAL)?
Nominal one-sided rate: 0.5%. Pair value = mean of two worlds x 12 trials (Bernoulli p0 per trial)."""
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import sys, numpy as np
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import ROOT
sys.path.insert(0, str(ROOT))
from prometheus.ananke.assays import pair_ci
g=np.random.default_rng(12345)
for p0, trials in ((0.55,12),(0.55,16),(0.70,12)):
    n_sim=3000; hit=0
    for _ in range(n_sim):
        w=g.binomial(trials, p0, size=(32,2))/trials
        m,lo,hi=pair_ci(w.mean(1))
        hit += lo > p0
    print(f"p0={p0} trials={trials}: P(lo99 > p0) = {hit/n_sim:.4f}  (nominal 0.005; binomial SE {np.sqrt(0.005*0.995/n_sim):.4f})")
