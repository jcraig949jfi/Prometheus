"""s3 timing probe: per-call CPU of competent() and fair_rates() on panel genomes (no writes)."""
import json, time, random
import fsetup as F
d = json.load(open("core_map.json"))
sf = [r for r in d["rows"] if r.get("state_free")]
sd = [r for r in d["rows"] if r.get("competent") and not r.get("state_free")]
rng = random.Random(1)
for lab, rows in (("SF", sf[:4]), ("SD", sd[:4])):
    for r in rows:
        g = bytearray(bytes.fromhex(r["hex"])); dense = r["vm"] == "DENSE"
        t = time.process_time(); c = [F.competent(r["cell"], bytes(g), dense=dense)]
        for _ in range(5):
            m = bytearray(g); p = rng.randrange(64); m[p] = rng.randrange(256); c.append(F.competent(r["cell"], bytes(m), dense=dense))
        t1 = time.process_time(); fr = F.fair_rates(r["cell"], bytes(g), dense=dense); t2 = time.process_time()
        print(lab, r["origin_run"][-20:], "comp/call %.3f" % ((t1 - t) / 6), sum(c), "fair %.3f" % (t2 - t1), fr)
