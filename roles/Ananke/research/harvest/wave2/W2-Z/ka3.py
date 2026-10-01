import sys; sys.path.insert(0, '.')
import wz_common as wz, plants_wz as pw
np = wz.np
res = {}
for relay_name, relay in (("att", pw.relay_att(1) + pw.DISPATCH), ("dedup", pw.relay_dedup() + pw.DISPATCH)):
    for un, upd in (("sync1", dict(update_mode="sync", update_period=1)), ("sync2", dict(update_mode="sync", update_period=2)),
                    ("async.5", dict(update_mode="async", update_p=0.5))):
        for eco in ("lite", "full"):
            e = dict(c_emit=1, c_op=0, c_mem=0) if eco == "lite" else dict(c_emit=4, c_op=1, c_mem=1)
            ph = wz.Physics(topology="ring", n_sites=64, radius=1, dest_mode="all", lat_base=1, state_dim=4, payload_width=1,
                            channels=1, prog_len=29, rules=2, setrule=1, e_income=4, e_max=100, **e, **upd)
            env = wz.envs.EnvSpec(family="FLIP", d=3, delta=16, trials=16, block=4)
            g = pw.two_rule(ph, relay, pw.flip_actuator_v3())
            seeds = wz.assays.world_seeds(0x575A4B41, 32)
            o = wz.ws.flip_eval(ph, g, env, seeds)
            k = f"{relay_name}|{un}|{eco}"
            res[k] = {kk: round(o[kk], 3) for kk in ("acc", "lo99", "chg", "same", "bal", "bal_lo99", "ro_zero_frac")}
            print(k, res[k], flush=True)
wz.save("ka3.json", res)
