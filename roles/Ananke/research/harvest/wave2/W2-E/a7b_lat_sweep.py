"""A7b: 62a7fff9 latency sweep (fresh paired 128 worlds) + env delta sweep at native latency."""
from w2e_common import *
import dataclasses
ck = Clock()
adj = [x for x in rows() if x["kind"] == "adjudicate" and x["parent"].startswith("62a7fff9")][0]
ph, env = spec_of(adj); g = genome_of(adj)
fs = seeds(H_int(NS, 0xA7B), 128)
out = {"env": env.to_dict(), "lat": [ph.lat_base, ph.lat_hop, ph.lat_jitter], "decompiled": decompile(ph, g[0])}
for db in range(0, 5):
    a, *_ = run(ph.replace(lat_base=ph.lat_base + db).validate(), g, env, fs); out[f"lat_base+{db}"] = round(ci(pairs(a))[0], 3)
for dd in (-2, -1, 1, 2):
    e2 = dataclasses.replace(env, delta=env.delta + dd)
    a, *_ = run(ph, g, e2, fs); out[f"delta{dd:+d}"] = round(ci(pairs(a))[0], 3)
out["clock"] = ck.done(); save("a7b_lat_sweep.json", out); print(json.dumps(out, indent=1))
