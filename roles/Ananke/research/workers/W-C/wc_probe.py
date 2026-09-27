"""W-C probes (PLAN.md X1, X2, X3). CPU, 2 threads, namespace 0x5E6.

X1 twin-difference decomposition (presence vs content, fire vs payload)
X2 reach audit of the S-CT counts swap (mirror pairs)
X3 presence-code plants (P-FIRE, P-FIRE-SUM, route_relay) + swaps
Physics untouched: only between-tick reads and lens swaps.
"""
import json
import pathlib
import sys
import time

import numpy as np
import torch

REPO = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
torch.set_num_threads(2)
from prometheus.ananke import assays, c1b, c1b_run, envs, lens, plants  # noqa: E402
from prometheus.ananke.engine import Schedule, World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

OUT = pathlib.Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
DEV = "cpu"
NS = 0x5E6
K_TRIAL = 5
T0 = time.time()


def g3(body, ph):
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


def p_fire(ph, reader="CNT0"):
    return g3(plants.assemble(ph, [
        ("CONST", "T0", 0, 7, 1),            # 128
        ("GT", "EMIT", "SENSE", "T0", 0),    # 256 iff SENSE > 128 (fire only on + cue)
        ("CONST", "PAY0", 0, 7, 2),          # constant payload 256
        ("GT", "T1", reader, "ZERO", 0),     # 256 iff something arrived (count or sum)
        ("ADD", "S0", "T1", "T1", 0),
        ("ADDI", "S0", "S0", 0, -256),       # +256 / -256
    ]), ph)


def specimens():
    out = {}
    ph, env, g, _ = c1b_run.load("4ab2ba014aac967e")
    out["M2:4ab2ba01"] = (ph, env, g)
    for r in c1b_run.d_wave_cells():
        ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
        out[f"{env.family}:{r['extra']['source_cell'][:8]}"] = (
            ph, env, np.asarray(r["extra"]["genome"], dtype=np.int64))
    return out


def plant_specs():
    pda = plants.c1b_da_physics()
    eda = envs.EnvSpec(family="RELAY", d=1, delta=4, cue_len=2, trials=12, iti=50)
    prt = plants.c1b_route_physics()
    ert = envs.EnvSpec(family="RELAY", d=2, delta=8, cue_len=4, trials=12)
    return {
        "PLANT:P-FIRE": (pda, eda, p_fire(pda, "CNT0")),
        "PLANT:P-FIRE-SUM": (pda, eda, p_fire(pda, "IN0_0")),
        "PLANT:route_relay": (prt, ert, g3(plants.route_relay(prt), prt)),
    }


def swap_ticks(env):
    tk = c1b.ticks(env)
    if env.family == "HOLD":
        return list(tk["mid"])
    return [t0 + max(1, env.delta // 2) for t0 in tk["t0"]]


# ------------------------------------------------------------------ X1
def x1(ph, env, g, M=64):
    seeds = assays.world_seeds(NS ^ 0xF1, M)
    ep = envs.build(ph, env, seeds)
    sv = ep.schedule.sense_val.clone()
    Pd = env.period()
    tk0 = K_TRIAL * Pd
    for b in range(1, M, 2):
        sv[:, b] = sv[:, b - 1]
        sv[tk0:tk0 + env.cue_len, b] = -sv[tk0:tk0 + env.cue_len, b - 1]
    sch = Schedule(ep.schedule.sense_idx.clone(), sv, ep.schedule.read_idx.clone())
    for b in range(1, M, 2):
        sch.sense_idx[b] = sch.sense_idx[b - 1]
        sch.read_idx[b] = sch.read_idx[b - 1]
    ws = [seeds[m - (m % 2)] for m in range(M)]
    w = World(ph, np.repeat(g[None], M, 0), ws, device=DEV, schedule=sch)
    ro = int(ep.ro_tick[0, K_TRIAL])
    c = dict(presence=0, content_only=0, fire=0, payload_only=0, chan_only=0,
             w_diff_ticks=0, r_diff=0, S_diff=0)
    first_presence_without_fire_or_w = None
    for t in range(ro + 1):
        w.step()
        if t < tk0:
            continue
        mc, ms = w.Mcnt, w.Msum
        dc = mc[:, 0::2] != mc[:, 1::2]
        ds = (ms[:, 0::2] != ms[:, 1::2]).any(-1) & ~dc
        e = w.last_emit
        fd = e[0::2] != e[1::2]
        both = e[0::2] & e[1::2]
        pdiff = both & (w.last_pay[0::2] != w.last_pay[1::2]).any(-1)
        cdiff = both & ~pdiff & (w.last_chan[0::2] != w.last_chan[1::2])
        wd = int((w.w[0::2] != w.w[1::2]).sum()) if w.R else 0
        c["presence"] += int(dc.sum())
        c["content_only"] += int(ds.sum())
        c["fire"] += int(fd.sum())
        c["payload_only"] += int(pdiff.sum())
        c["chan_only"] += int(cdiff.sum())
        c["w_diff_ticks"] += int(wd > 0)
        c["r_diff"] += int((w.r[0::2] != w.r[1::2]).sum())
        c["S_diff"] += int((w.S[0::2] != w.S[1::2]).any(-1).sum())
        if (c["presence"] > 0 and c["fire"] == 0 and c["chan_only"] == 0 and c["w_diff_ticks"] == 0
                and first_presence_without_fire_or_w is None):
            first_presence_without_fire_or_w = t - tk0
    pc = c["presence"] + c["content_only"]
    fp = c["fire"] + c["payload_only"] + c["chan_only"]
    c["presence_share"] = c["presence"] / pc if pc else None
    c["fire_share"] = c["fire"] / fp if fp else None
    c["chan_share"] = c["chan_only"] / fp if fp else None
    c["presence_without_fire_chan_or_w_at_lag"] = first_presence_without_fire_or_w
    c["window"] = [tk0, ro]
    return c


# ------------------------------------------------------------------ X2
def x2(ph, env, g):
    seeds = assays.world_seeds(NS, 64)
    rec = []

    def probe(w):
        mc, ms = w.Mcnt, w.Msum
        pc = (mc[:, 0::2] != mc[:, 1::2]).flatten(2).any(-1).any(0)       # [pairs]
        pcm = (ms[:, 0::2] != ms[:, 1::2]).flatten(2).any(-1).any(0)
        l1 = float((mc[:, 0::2] - mc[:, 1::2]).abs().sum()) / max(1.0, float(mc.sum()))
        rec.append((float(pc.float().mean()), float(pcm.float().mean()), l1))
    ticks = swap_ticks(env)
    lens.run(ph, g, env, seeds, hooks={t: probe for t in ticks}, device=DEV)
    a = np.array(rec)
    return {"pairs_mcnt_differ": float(a[:, 0].mean()), "pairs_msum_differ": float(a[:, 1].mean()),
            "mcnt_l1_rel": float(a[:, 2].mean()), "n_swap_ticks": len(ticks)}


# ------------------------------------------------------------------ X3
def x3_swaps(ph, env, g):
    seeds = assays.world_seeds(NS, 64)
    ep = envs.build(ph, env, seeds)
    ticks = [int(x) - 1 for x in ep.ro_tick[0]]        # after tick ro-1: packets due at ro in flight
    tr = range(env.trials)
    base = lens.run(ph, g, env, seeds, device=DEV, ep=ep)
    nrm = lens.trial_acc(base, tr)
    res = {"normal": lens.ci(nrm)}
    arms = {"inflight": lambda w: lens.swap(w, lens.FLIGHT_ARRAYS),
            "payload": lambda w: lens.swap(w, ["Msum"]),
            "counts": lambda w: lens.swap(w, ["Mcnt"]),
            "sitestate": lambda w: lens.swap(w, lens.SITE_ARRAYS)}
    for an, fn in arms.items():
        r = lens.run(ph, g, env, seeds, hooks={t: fn for t in ticks}, device=DEV, ep=ep)
        pr = lens.trial_acc(r, tr)
        res[an] = {"acc": lens.ci(pr), "verdict": lens.swap_verdict(nrm, pr)}
    return res


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    res = {}
    if which in ("x3", "all"):
        for name, (ph, env, g) in plant_specs().items():
            row = {"swaps_at_ro_minus_1": x3_swaps(ph, env, g), "x1": x1(ph, env, g)}
            res[name] = row
            print(name, json.dumps({k: v["verdict"] if isinstance(v, dict) else v
                                    for k, v in row["swaps_at_ro_minus_1"].items()}),
                  {k: row["x1"][k] for k in ("presence_share", "fire_share", "chan_share")}, flush=True)
        (OUT / "x3.json").write_text(json.dumps(res, indent=1, default=float))
    if which in ("x12", "all"):
        res = {}
        for name, (ph, env, g) in specimens().items():
            row = {"x1": x1(ph, env, g), "x2": x2(ph, env, g)}
            res[name] = row
            v = row["x1"]
            print(f"{name:16s} pres {v['presence_share']} fire {v['fire_share']} chan {v['chan_share']} "
                  f"wdiff {v['w_diff_ticks']} | x2 {row['x2']}", flush=True)
        (OUT / "x12.json").write_text(json.dumps(res, indent=1, default=float))
    print("wall", time.time() - T0)
