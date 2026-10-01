"""MAJ SIGNAL / promoted rows: realized actuator->sensor distance multiset vs recorded d."""
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import sys, collections, numpy as np
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
sys.path.insert(0, str(ROOT))
import torch; torch.set_num_threads(2)
from prometheus.ananke import envs, search
from prometheus.ananke.physics import Physics
from prometheus.ananke.assays import world_seeds
from prometheus.ananke.rng import H_int
for r in rows():
    if r['kind']!='evolve' or r['env']['family']!='MAJ' or not r['labels']['SIGNAL']: continue
    ph=Physics.from_dict(r['physics']); env=envs.EnvSpec(**r['env'])
    ep=envs.build(ph, env, world_seeds(H_int(r['search_seed'], search.HELD_NS), 64))
    M=envs.dist_matrix(ph); si=ep.schedule.sense_idx.numpy(); ri=ep.schedule.read_idx.numpy()[:,0]
    dd=np.sort(M[ri[:,None], si],1)
    prof=collections.Counter(tuple(x) for x in dd).most_common(2)
    hop = ph.radius if ph.topology in ('ring','torus') else 1
    print(f"{r['cell_id'][:8]} {r['wave']:2s} {ph.topology:10s} r{ph.radius} d={env.d} held {r['result']['held']['acc']:.3f} lo {r['result']['held']['lo99']:.3f} sorted dists {prof} sensors within one hop: {np.mean(dd<=hop):.2f}")
