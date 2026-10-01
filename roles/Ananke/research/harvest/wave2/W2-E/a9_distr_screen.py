"""A9: screen every HOLD evolve champion with held lo99 > .60 for distractor dependence
(amp_dist 64 -> 0), 32 fresh worlds each, paired. Incremental, resumable, time-capped."""
from w2e_common import *
import dataclasses
cap = float(sys.argv[1]) if len(sys.argv) > 1 else 540
ck = Clock(); t0 = time.time()
path = OUT / "a9_distr_screen.json"
done = json.loads(path.read_text()) if path.exists() else {}
cells = [r for r in rows() if r["kind"] == "evolve" and r["env"]["family"] == "HOLD" and r["result"]["held"]["lo99"] > .60]
for r in cells:
    cid = r["cell_id"][:8]
    if cid in done: continue
    if time.time() - t0 > cap: break
    ph, env = spec_of(r); g = genome_of(r)
    S = seeds(H_int(NS, 0xA9, int(cid, 16) & 0xFFFF), 32)
    a, *_ = run(ph, g, env, S)
    b, *_ = run(ph, g, dataclasses.replace(env, amp_dist=0), S)
    d = pairs(b) - pairs(a)
    done[cid] = {"normal": float(a.mean()), "no_distr": float(b.mean()), "diff": ci(d),
                 "rules": ph.rules, "setrule": ph.setrule, "decay": ph.decay_shift, "topology": ph.topology}
    path.write_text(json.dumps(done, indent=1))
print(len(done), "of", len(cells), ck.done())
for k, v in sorted(done.items(), key=lambda kv: kv[1]["diff"][0])[:8]:
    print(k, v)
