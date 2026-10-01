import os, sys, hashlib, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
PKG = pathlib.Path(sys.argv[1]).resolve(); sys.path.insert(0, str(PKG))
from prometheus.ananke import envs, assays
from prometheus.ananke.physics import Physics
assert pathlib.Path(envs.__file__).resolve().is_relative_to(PKG)
out = {}
for topo, n in (("ring", 64), ("torus", 100), ("global", 64)):
    ph = Physics(topology=topo, n_sites=n, radius=2)
    for fam in envs.FAMILIES:
        for d in (1, 3, 5):
            ep = envs.build(ph, envs.EnvSpec(family=fam, d=d, delta=4, trials=16, block=4), assays.world_seeds(31, 16))
            h = hashlib.sha256()
            for a in (ep.schedule.sense_idx.numpy(), ep.schedule.sense_val.numpy(), ep.schedule.read_idx.numpy(), ep.y, ep.ro_tick, ep.scored):
                h.update(a.tobytes())
            out[f"{topo}/{fam}/{d}"] = h.hexdigest()[:16]
print(hashlib.sha256(repr(sorted(out.items())).encode()).hexdigest()[:16])
