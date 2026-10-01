"""Condition aliasing: recorded env d vs the REALIZED sensor-actuator distances envs.build places
(envs.py:99-117 _pick_at fallbacks), on each evolve row's own held-out worlds."""
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"; os.environ["OMP_NUM_THREADS"]="2"
import sys, collections, numpy as np
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
sys.path.insert(0, str(ROOT))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
from prometheus.ananke import envs, search
from prometheus.ananke.physics import Physics
from prometheus.ananke.assays import world_seeds
from prometheus.ananke.rng import H_int
R=[r for r in rows() if r['kind']=='evolve']
stat=collections.defaultdict(lambda: [0,0,0,[]])   # n rows, rows with any world off-d, rows with ALL worlds off-d, mean realized
for r in R:
    fam=r['env']['family']
    if fam=='HOLD': continue
    ph=Physics.from_dict(r['physics']); env=envs.EnvSpec(**r['env'])
    seeds=world_seeds(H_int(r['search_seed'], search.HELD_NS), 64)
    ep=envs.build(ph, env, seeds)
    M=envs.dist_matrix(ph)
    si=ep.schedule.sense_idx.numpy(); ri=ep.schedule.read_idx.numpy()[:,0]
    if fam in ('RELAY','FLIP'):
        dd=M[si[:,0], ri]
    elif fam=='MAJ':
        dd=M[ri[:,None], si]          # [B,5] distance actuator->sensor
    else:
        dd=M[si[:,0], si[:,1]]        # XOR sensor separation (should be d)
    off=(dd!=env.d)
    key=(fam, r['physics']['topology'], env.d)
    s=stat[key]; s[0]+=1; s[1]+=bool(off.any()); s[2]+=bool(off.all()); s[3].append(float(np.mean(dd)))
print("family topology d : rows | rows with some world off-d | rows with every distance off-d | mean realized distance")
for k in sorted(stat):
    s=stat[k]
    if s[1]: print(f"  {k[0]:5s} {k[1]:10s} d={k[2]} : {s[0]:3d} | {s[1]:3d} | {s[2]:3d} | {np.mean(s[3]):.2f}")
