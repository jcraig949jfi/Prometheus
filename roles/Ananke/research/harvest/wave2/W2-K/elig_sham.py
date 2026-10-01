"""W2-K: exact pair arrays for the A3 'fired' reading of F_sham_positive and F_echo at M2's physics (they decide
Z NOT_ELIGIBLE -> the _UNRESOLVED suffix). Same code path as c1b.eligibility (seeds DEV_NS+1, 64 worlds), CPU."""
import dataclasses, json, os, pathlib, sys
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["OMP_NUM_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent; REPO = HERE.parents[5]
sys.path.insert(0, str(REPO)); os.chdir(REPO)
import numpy as np, torch
torch.set_num_threads(2); assert not torch.cuda.is_available()
from prometheus.ananke import c1b, plants
seeds = c1b.assays.world_seeds(c1b.DEV_NS + 1, c1b.H_WORLDS)
sph, senv = c1b.specimen_physics_env("4ab2ba014aac967e")
hold = dataclasses.replace(senv, family="HOLD")
out, arr = {}, {}
ph = c1b.at_specimen(plants.c1b_echo_physics().replace(prog_len=64), sph)
g = plants.sham_positive_hold(ph)[None]
bat = c1b.m2_battery(ph, hold)
res = c1b.run_battery({k: bat[k] for k in ("normal", "normal_from1", "flush_inflight_iti")}, g, hold, seeds, "cpu")
arr["sham_n1"] = res["normal_from1"]["run"].pairs; arr["sham_iti"] = res["flush_inflight_iti"]["run"].pairs
out["F_sham_positive"] = c1b.fired(res["normal_from1"]["run"], res["flush_inflight_iti"])
ph = c1b.at_specimen(plants.c1b_echo_physics(), sph)
g = plants.echo_hold(ph)[None]
bat = c1b.m2_battery(ph, hold)
res = c1b.run_battery({k: bat[k] for k in ("normal", "flush_inflight")}, g, hold, seeds, "cpu")
arr["echo_n"] = res["normal"]["run"].pairs; arr["echo_flush"] = res["flush_inflight"]["run"].pairs
out["F_echo"] = c1b.fired(res["normal"]["run"], res["flush_inflight"])
np.savez(HERE / "out" / "pairs_elig_m2.npz", **arr)
(HERE / "out" / "pairs_elig_m2.json").write_text(json.dumps(out, indent=1, default=float))
print(json.dumps(out, default=float))
