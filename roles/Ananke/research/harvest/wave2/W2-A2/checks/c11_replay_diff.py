"""Which twin keys differ between the recorded (C1, GPU, code 362f2189b) twin and a CPU replay at HEAD
for the 2 mismatching cells; also replay held accuracy (evaluate) for the same cells."""
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import sys, numpy as np
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
sys.path.insert(0, str(ROOT))
import torch; torch.set_num_threads(2)
from prometheus.ananke import assays, envs, search
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
for cid in ("05fea1b5","062b2018"):
    r=next(x for x in rows() if x['cell_id'].startswith(cid) and x['kind']=='evolve')
    ph=Physics.from_dict(r['physics']); env=envs.EnvSpec(**r['env'])
    hs=assays.world_seeds(H_int(r['search_seed'], search.HELD_NS), 64)
    champ=np.asarray(r['result']['champion'])
    tw=assays.twin_assay(ph, champ[None], env, hs[:16], device="cpu")
    for k,v in r['result']['twin'].items():
        if abs(float(tw[k][0])-v)>1e-9: print(cid, "twin", k, "recorded", v, "replay", float(tw[k][0]))
    rh=assays.evaluate(ph, champ[None], env, hs, device="cpu")
    print(cid, "held recorded", r['result']['held']['acc'], "replay", float(rh.pair_acc()[0].mean()), "T", env.T(), "fam", env.family, ph.topology, ph.update_mode, "lat", ph.lat_base, ph.lat_hop, ph.lat_jitter)
