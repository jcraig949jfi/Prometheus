"""W2-Y task 1: joint ceilings for every C1 B/B2 transect row, on the row's OWN physics/env and OWN seeds.
plant metric -> campaign.plant_viability seeds  world_seeds(H_int(search_seed, 0x9147), 32)  (campaign.py:299)
acc metric   -> held seeds                      world_seeds(H_int(search_seed, HELD_NS), M_held)  (evolve rows)
Ceiling models (read-only reuse):
  RELAY/XOR/FLIP: W2-U w2u_ceil.ceilings ('joint'; FLIP also joint_block / copy_block)
  MAJ:            W2-P task2_timing.ceilings ('joint'; any-program Bayes majority over arrived votes)
  HOLD:           sensor == actuator (envs.build HOLD branch), no transport: sync with period <= cue_len -> 1;
                  async -> .5 + .5*(1-(1-p)^cue_len)  (perfect memory, optimistic; decay NOT in any ceiling).
CPU only, 2 threads (w2p_common asserts no CUDA)."""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-P")); sys.path.insert(0, str(HERE.parent / "W2-U"))
from w2p_common import *          # noqa
import w2u_ceil as U               # noqa
import task2_timing as T2          # noqa
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)


def save(name, obj):   # local: w2p_common.save writes into W2-P/out
    (OUT / name).write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))


def hold_ceil(ph, env):
    if ph.update_mode == "sync":
        return 1.0 if T2.next_awake(0, ph) < env.cue_len else 0.5
    p = ph.p16(ph.update_p) / 65536.0
    return 0.5 + 0.5 * (1 - (1 - p) ** env.cue_len)


def ceil(ph, env, seeds):
    f = env.family
    if f == "HOLD":
        c = hold_ceil(ph, env); return {"joint": c, "lc": 1.0}
    if f == "MAJ":
        return T2.ceilings(ph, env, seeds)
    return U.ceilings(ph, env, seeds)


if __name__ == "__main__":
    ck = Clock()
    R = [r for r in hc.rows() if r["wave"] in ("B", "B2")]
    out = []
    for i, r in enumerate(R):
        ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
        o = {"cell": r["cell_id"], "wave": r["wave"], "kind": r["kind"], "family": env.family,
             "dial": r["extra"]["transect"], "base": r["extra"]["base"], "track": r["extra"].get("track", "evo"),
             "li": r["extra"]["level_index"], "rep": r["extra"].get("rep", 0),
             "level": r["levels"].get(r["extra"]["transect"], r["env_levels"].get(r["extra"]["transect"])),
             "plant": r["result"]["plant"]["acc"],
             "sens": r["result"].get("gen0", {}).get("frac_sensitive_any"),
             "emit": r["result"].get("gen0", {}).get("frac_emitting"),
             "acc": r["result"].get("held", {}).get("acc")}
        ps = assays.world_seeds(H_int(r["search_seed"], 0x9147), 32)
        c = ceil(ph, env, ps)
        o["ceil_plant"] = c["joint"]; o["lc_plant"] = c.get("lc")
        for k in ("joint_block", "copy_block"):
            if k in c: o[k + "_plant"] = c[k]
        if r["kind"] == "evolve":
            hs = held_seeds(r)
            ch = ceil(ph, env, hs)
            o["ceil_held"] = ch["joint"]
            for k in ("joint_block", "copy_block"):
                if k in ch: o[k + "_held"] = ch[k]
        out.append(o)
        if i % 100 == 0:
            print(i, len(R), ck.done(), flush=True)
    save("task1_ceilings.json", {"rows": out, "compute": ck.done()})
    print(ck.done())
