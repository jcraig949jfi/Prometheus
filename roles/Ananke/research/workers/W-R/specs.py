"""W-R spec loader: the 7 census-JOINT cells + E1/E2 exactly as W-M/apply.py,
plus the known-answer plant (echo_hold) under sync update_period 2 / 1."""
import dataclasses, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
for p in (str(REPO), str(REPO / "roles/Ananke/research/workers/W-M")):
    if p not in sys.path:
        sys.path.insert(0, p)
import torch
from prometheus.ananke import envs, plants

CELLS = ["2dccdaa5", "c16d5231", "78f3b0ec", "8c37f32e", "e06701a5", "369f5a5b", "4781b0a1"]
ECHOES = ["E1", "E2"]
PLANT_ENV = envs.EnvSpec(family="HOLD", gap=11, cue_len=2, iti=3, trials=12)   # Pd 17 (odd), ro_off 13


def plant(period: int):
    ph = dataclasses.replace(plants.c1b_echo_physics(), update_period=period)
    return ph, PLANT_ENV, plants.echo_hold(ph)[None]


def ro_off(env):
    return (env.cue_len + env.gap) if env.family == "HOLD" else env.delta


def load(name):
    """-> ph, env, genome, meta"""
    if name.startswith("PLANT"):
        per = int(name[5:])
        ph, env, g = plant(per)
        return ph, env, g, {"plant": "echo_hold", "physics": "c1b_echo_physics", "update_period": per}
    import apply as WM                     # W-M loader (read-only import)
    ph, env, g, _seeds, meta = WM.spec(name)
    torch.set_num_threads(2)
    return ph, env, g, meta
