"""W-Y (T-INS-20): readout Kp[7] swap. PLAN fc8bfa171 s2 + PLAN_ADDENDUM A1.
Fork runner (W-V wv.run structure, plain World): per (trial k, offset o) tile the normal state after tick
k*Pd+o into one block per arm, apply the arm's SINGLE swap, run to trial k's readout.
python wy.py <spec> <M> <ns hex> <offsets comma> <tag>      spec in {4781b0a1, PA, PB}"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
for p in (str(REPO), str(HERE.parent / "W-R"), str(HERE.parent / "W-S"), str(HERE.parent / "W-V"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import torch

from prometheus.ananke import assays, envs, lens_swap as LS  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402
import plants_wy  # noqa: E402

OUT = HERE / "out"
NOT_RUN = LS.NOT_RUN


def _threads():
    torch.set_num_threads(int(os.environ.get("WY_THREADS", "1")))


def load(name):
    import specs as WRS
    ph, env, g, meta = WRS.load("4781b0a1")
    _threads()
    if name == "4781b0a1":
        return ph, env, g, meta
    php = plants_wy.physics(ph)
    kind = {"PA": "A", "PB": "B"}[name]
    return php, env, plants_wy.genome(php, kind), {"plant": name, "physics": "plants_wy.physics(4781b0a1)"}


def arm_list(plant=False):
    arms = [("NORMAL", "normal"), ("KP7", "kp7"), ("KPALL", "kpall"), ("FLA", "fla"),
            ("KP7+FLA", "kp7fla"), ("SITE_R", "site_r")]
    if plant:
        arms.append(("KPX", "kpx"))
    return arms


def apply_arm(w, kind, rows, ro, j=7, jx=None):
    import probe as WS                                  # W-S site_a / flight_a
    p = rows ^ 1
    if kind == "normal":
        return
    if kind in ("kp7", "kp7fla"):
        w.Kp[rows, ro, j] = w.Kp[p, ro, j]
    if kind == "kpx":
        w.Kp[rows, ro, jx] = w.Kp[p, ro, jx]
    if kind == "kpall":
        w.Kp[rows, ro] = w.Kp[p, ro]
    if kind in ("fla", "kp7fla"):
        WS.swap_targeted(w, "flight_a", rows, ro)
    if kind == "site_r":
        WS.swap_targeted(w, "site_a", rows, ro)


def _tile_state(src, dst, K):
    for n, v in src.state_arrays().items():
        d = getattr(dst, n)
        if n in ("Msum", "Mcnt"):
            d.copy_(v.repeat(1, K, *([1] * (v.dim() - 2))))
        else:
            d.copy_(v.repeat(K, *([1] * (v.dim() - 1))))
    dst.t = src.t
    dst.t_dev.fill_(src.t)


def run(ph, genome, env, seeds, offsets, trials, arms, j=7, jx=None, device="cpu", log=None):
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    Pd, T = env.period(), env.T()
    nt = env.trials
    base = World(ph, np.repeat(genome[None], M, 0), ws1, device=device, ctrl=Controls(), schedule=ep.schedule)
    ro = torch.as_tensor(ep.schedule.read_idx[:, 0], dtype=torch.int64)
    assert (ro[0::2] == ro[1::2]).all()
    at = {}
    for k in trials:
        for oi, o in enumerate(offsets):
            at.setdefault(k * Pd + o, []).append((k, oi))
    A, O, P = len(arms), len(offsets), M // 2
    arm_s0 = np.full((A, O, M, nt), NOT_RUN, np.int64)
    L = ph.prog_len
    cen = {"kp7_diff": np.zeros((O, P, nt), bool), "kp_any_diff": np.zeros((O, P, nt), bool),
           "kp_slot_diff": np.zeros((O, P, nt, L), bool), "fla_diff": np.zeros((O, P, nt), bool),
           "inbox_diff": np.zeros((O, P, nt), bool), "S_diff": np.zeros((O, P, nt), bool),
           "kp7_val": np.zeros((O, M, nt), np.int64)}
    ar = torch.arange(M)
    t_start = time.time()
    for t in range(T):
        base.step()
        for k, oi in at.get(t, ()):
            kp = base.Kp[ar, ro]                                   # [M, L]
            cen["kp_slot_diff"][oi, :, k] = (kp[0::2] != kp[1::2]).numpy()
            cen["kp7_diff"][oi, :, k] = (kp[0::2, j] != kp[1::2, j]).numpy()
            cen["kp7_val"][oi, :, k] = kp[:, j].numpy()
            cen["kp_any_diff"][oi, :, k] = (kp[0::2] != kp[1::2]).any(-1).numpy()
            ms = base.Msum[:, ar, ro]                              # [LM, M, C, P]
            mc = base.Mcnt[:, ar, ro]
            cen["fla_diff"][oi, :, k] = ((ms[:, 0::2] != ms[:, 1::2]).flatten(2).any(-1).any(0)
                                         | (mc[:, 0::2] != mc[:, 1::2]).flatten(2).any(-1).any(0)).numpy()
            ib = base.Acc_sum[ar, ro].flatten(1)
            cen["inbox_diff"][oi, :, k] = (ib[0::2] != ib[1::2]).any(-1).numpy()
            s = base.S[ar, ro]
            cen["S_diff"][oi, :, k] = (s[0::2] != s[1::2]).any(-1).numpy()
            rt = int(ep.ro_tick[:, k].max())
            w = World(ph, np.repeat(genome[None], M * A, 0), ws1 * A, device=device, ctrl=Controls(),
                      schedule=LS.tile_schedule(ep.schedule, A))
            _tile_state(base, w, A)
            for a, (_lab, kind) in enumerate(arms):
                rows = torch.arange(a * M, (a + 1) * M)
                apply_arm(w, kind, rows, ro, j=j, jx=jx)
            for _ in range(t + 1, rt + 1):
                w.step()
            tr = w.trace.cpu().numpy()
            for a in range(A):
                tra = tr[:, a * M:(a + 1) * M]
                arm_s0[a, oi, :, k] = tra[ep.ro_tick[:, k], np.arange(M), ep.ro_slot[:, k]]
            if log:
                log(f"t{t} trial {k} o{offsets[oi]} done {time.time() - t_start:.0f}s")
    tr = base.trace.cpu().numpy()
    ns0 = tr[ep.ro_tick, np.arange(M)[:, None], ep.ro_slot].astype(np.int64)
    out = {"normal_s0": ns0, "arm_s0": arm_s0, "y": ep.y, "scored": ep.scored, "offsets": np.array(offsets),
           "trials": np.array(trials), "Pd": Pd, "update_period": ph.update_period}
    out.update({f"cen_{k}": v for k, v in cen.items()})
    return out


def main(argv):
    name, M, ns = argv[0], int(argv[1]), int(argv[2], 16)
    offsets = [int(x) for x in argv[3].split(",")]
    tag = argv[4]
    ph, env, g, meta = load(name)
    plant = name != "4781b0a1"
    arms = arm_list(plant)
    seeds = assays.world_seeds(ns, M)
    trials = list(range(1, env.trials))
    t = time.time()
    r = run(ph, g, env, seeds, offsets, trials, arms, j=7, jx=plants_wy.JX if plant else None,
            log=lambda s: print(name, s, flush=True))
    wall = time.time() - t
    OUT.mkdir(exist_ok=True)
    np.savez_compressed(OUT / f"raw_{tag}.npz", **r)
    meta_out = {"spec": name, "meta": meta, "M": M, "ns": hex(ns), "offsets": offsets, "trials": trials,
                "arms": [a[0] for a in arms], "wall_s": wall, "threads": torch.get_num_threads(),
                "physics": ph.to_dict(), "env": env.to_dict(), "pid": os.getpid(),
                "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))}
    (OUT / f"meta_{tag}.json").write_text(json.dumps(meta_out, indent=1, default=str))
    print(f"{name} DONE wall {wall:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
