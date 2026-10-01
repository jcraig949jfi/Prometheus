"""P-XOR runs. usage: python run_xor.py dev|score|mf|screen|screen_score <args>"""
import sys

import hp_common as hc
from hp_common import Clock, save, evaluate, decompile, row
import hp_plants as hp
from prometheus.ananke import assays, envs
from prometheus.ananke.physics import Physics

X0 = Physics(topology="torus", n_sites=64, radius=3, dest_mode="all", loss=0.0, lat_base=1,
             lat_hop=0, lat_jitter=0, dup=0.0, noise=0, cap=0, collision="none", decay_shift=0,
             update_mode="sync", update_period=1, state_dim=4, payload_width=2, channels=1,
             rules=1, prog_len=16).validate()
ENV0 = envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)
STRUCT = dict(prog_len=16, state_dim=4, payload_width=2, channels=1, rules=1, setrule=0, wimm=0,
              plastic_route=0, adapt_shift=X0.adapt_shift)


def at_c1(r):
    ph = Physics.from_dict(r["physics"]).replace(**STRUCT).validate()
    return ph, envs.EnvSpec(**r["env"])


def zero_s2(ep):
    ep.schedule.sense_val[:, :, 1] = 0


def main():
    mode = sys.argv[1]
    ck = Clock()
    out = {"mode": mode}
    if mode in ("dev", "score", "mf"):
        seeds = assays.world_seeds(hc.DEV_NS if mode == "dev" else hc.SCORE_NS, 32 if mode == "dev" else 256)
        g = hp.p_xor(X0, ENV0.period())
        out["physics"] = X0.to_dict(); out["env"] = ENV0.to_dict()
        out["program"] = decompile(X0, g[0])
        if mode in ("dev", "score"):
            out["normal"] = evaluate(X0, g, ENV0, seeds)
        if mode in ("dev", "mf"):
            out["mf_xor_a_sensor2_zeroed"] = evaluate(X0, g, ENV0, seeds, sched_fn=zero_s2)
            out["mf_xor_b_q_readout"] = evaluate(X0, hp.p_xor(X0, ENV0.period(), "mf_q_readout"), ENV0, seeds)
    elif mode == "screen":
        cands = []
        for r in hc.rows():
            p = r["physics"]
            if (r["env"]["family"] == "XOR" and p["update_mode"] == "sync" and p["update_period"] == 1
                    and p["decay_shift"] == 0 and p["mut_site"] == 0 and p["c_op"] == 0):
                cands.append(r)
        cands.sort(key=lambda r: r["cell_id"])
        seeds = assays.world_seeds(hc.DEV_NS, 32)
        out["screen"] = []
        for r in cands:
            ph, env = at_c1(r)
            res = evaluate(ph, hp.p_xor(ph, env.period()), env, seeds)
            res.pop("pairs")
            out["screen"].append({"cell": r["cell_id"], "wave": r["wave"], "env": r["env"],
                                  "physics": r["physics"], "acc": res["acc"], "lo99": res["lo99"]})
            print(r["cell_id"], r["wave"], r["physics"]["topology"], r["env"]["d"], r["env"]["delta"],
                  round(res["acc"], 3), flush=True)
    elif mode in ("score_cell", "score_cell_literal"):
        r = row(sys.argv[2])
        ph, env = at_c1(r)
        if mode == "score_cell_literal":
            ph = Physics.from_dict(r["physics"]).validate()
        seeds = assays.world_seeds(hc.SCORE_NS, 256)
        g = hp.p_xor(ph, env.period())
        out.update(cell=r["cell_id"], physics=ph.to_dict(), env=env.to_dict(), program=decompile(ph, g[0]))
        out["normal"] = evaluate(ph, g, env, seeds)
        out["mf_xor_a_sensor2_zeroed"] = evaluate(ph, g, env, seeds, sched_fn=zero_s2)
        out["mf_xor_b_q_readout"] = evaluate(ph, hp.p_xor(ph, env.period(), "mf_q_readout"), env, seeds)
    out["compute"] = ck.done()
    for k, v in out.items():
        if isinstance(v, dict) and "acc" in v:
            print(k, round(v["acc"], 4), round(v["lo99"], 4), round(v["hi99"], 4))
    print(out["compute"])
    save(f"xor_{mode}{'_' + sys.argv[2] if len(sys.argv) > 2 else ''}.json", out)


if __name__ == "__main__":
    main()
