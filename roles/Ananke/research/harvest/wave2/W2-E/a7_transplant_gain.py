"""A7: transplant 'improvements' (62a7fff9 latency+1 .909 vs normal .783; c16d5231
async0.7 .891 vs .807; 4781b0a1 none). The C1 transplant battery uses seeds 0x7A7A
(32 worlds) and has NO matched normal run. Re-run normal on the same seeds, then paired
on 256 fresh worlds."""
from w2e_common import *
ck = Clock()
out = {}
for par, mods in [("62a7fff9", ["latency+1", "jitter+2"]), ("c16d5231", ["async0.7", "latency+1"])]:
    adj = [x for x in rows() if x["kind"] == "adjudicate" and x["parent"].startswith(par)][0]
    ph, env = spec_of(adj); g = genome_of(adj)
    P = {"latency+1": ph.replace(lat_base=ph.lat_base + 1), "jitter+2": ph.replace(lat_jitter=ph.lat_jitter + 2),
         "async0.7": ph.replace(update_mode="async", update_p=0.7)}
    ts = assays.world_seeds(H_int(adj["search_seed"], 0x7A7A), 32)
    res = {"recorded": {m: adj["result"]["transplants"][m]["acc"] for m in mods},
           "recorded_normal_on_D_seeds": adj["result"]["controls"]["normal"]["acc"]}
    a0, *_ = run(ph, g, env, ts); res["normal_on_transplant_seeds"] = float(a0.mean())
    for m in mods:
        a, *_ = run(P[m].validate(), g, env, ts); res[f"{m}_on_transplant_seeds(recheck)"] = float(a.mean())
    fs = seeds(H_int(NS, 0xA7, int(par, 16) & 0xFFFF), 256)
    an, *_ = run(ph, g, env, fs); pn = pairs(an); res["fresh_normal"] = ci(pn)
    for m in mods:
        a, *_ = run(P[m].validate(), g, env, fs); d = pairs(a) - pn
        res[f"fresh_{m}"] = ci(pairs(a)); res[f"fresh_{m}_minus_normal"] = ci(d)
    out[par] = res; print(par, json.dumps(res), flush=True)
out["clock"] = ck.done(); save("a7_transplant_gain.json", out)
