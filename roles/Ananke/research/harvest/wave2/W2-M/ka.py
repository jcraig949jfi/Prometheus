"""Known-answer table for the MAJ integration plant family (fresh namespace 0x57324D, 512 worlds = 256 pairs).
KA-1H : ring64 r3, d=3 (all sensors one hop), lossless, sync p1, lat 1, no jitter/decay/noise -> co-arrival.
KA-1S : as KA-1H but lat_hop=1 (arrival tick = 1 + distance: staggered one-hop arrivals).
KA-MH : ring64 r1, d=2 (realized distances (1,1,2,2,3): up to 3 hops), lossless sync lat 1.
Expected: integrators -> Bayes(5)=.83692 where the lanes cover every sensor once; DICT (1 sensor) -> .70;
zero_comm -> .50; FIRST -> .837 under exact co-arrival (the first wave IS all votes) but < .837 when staggered."""
import w2m_common as c, w2m_plants as wp
from prometheus.ananke import envs, assays
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics

base = dict(topology="ring", n_sites=64, dest_mode="all", loss=0.0, lat_base=1, lat_hop=0, lat_jitter=0,
            update_mode="sync", update_period=1, decay_shift=0, noise=0, state_dim=3, payload_width=3,
            channels=1, prog_len=16)
PH = {"KA-1H": (Physics(radius=3, **base), 3),
      "KA-1S": (Physics(radius=3, **{**base, "lat_hop": 1}), 3),
      "KA-MH": (Physics(radius=1, **base), 2)}
PLANTS = {"KA-1H": ["INT_CO", "INT_1", "INT_1G", "INT_2", "FIRST"],
          "KA-1S": ["INT_CO", "INT_1", "INT_1G", "FIRST"],
          "KA-MH": ["INT_CO", "INT_1", "INT_2", "INT_3", "INT_3NB", "FIRST"]}
CTRL_ON = {"KA-1H": "INT_1", "KA-1S": "INT_1", "KA-MH": "INT_3NB"}
if __name__ == '__main__':
    seeds = assays.world_seeds(0x57324D, 512)
    ck = c.Clock(); out = {"bayes": c.bayes_table(), "rows": []}
    for name, (ph, d) in PH.items():
        ph = ph.validate(); env = envs.EnvSpec(family="MAJ", d=d, delta=8, trials=12)
        for p in PLANTS[name]:
            g = wp.MEMBERS[p][0](ph)
            r = c.hc.evaluate(ph, g, env, seeds)
            out["rows"].append({"physics": name, "plant": p, "control": "none", "acc": r["acc"], "lo99": r["lo99"], "hi99": r["hi99"]})
            print(name, p, "none", "%.4f [%.4f,%.4f]" % (r["acc"], r["lo99"], r["hi99"]), flush=True)
        p = CTRL_ON[name]; g = wp.MEMBERS[p][0](ph)
        for cname, kw in (("zero_comm", dict(ctrl=Controls(zero_comm=True))), ("DICT", dict(sched_fn=wp.dict_sched))):
            r = c.hc.evaluate(ph, g, env, seeds, **kw)
            out["rows"].append({"physics": name, "plant": p, "control": cname, "acc": r["acc"], "lo99": r["lo99"], "hi99": r["hi99"]})
            print(name, p, cname, "%.4f [%.4f,%.4f]" % (r["acc"], r["lo99"], r["hi99"]), flush=True)
    out["physics"] = {k: v[0].to_dict() for k, v in PH.items()}
    out["compute"] = ck.done()
    c.save("ka.json", out); print(out["compute"])
