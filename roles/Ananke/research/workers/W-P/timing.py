import sys, time, torch
import common
from prometheus.ananke import assays
import tt
nt = int(sys.argv[1]); torch.set_num_threads(nt)
for name in ("369f5a5b", "4781b0a1"):
    ph, env, g, _ = common.load(name)
    seeds = assays.world_seeds(0x7777, 256)        # timing-only namespace, outputs discarded
    comps = tt.coarse_components(ph)
    subs = tt.all_subsets(len(comps))[:32]
    t = time.time()
    tt.run_table(ph, g, env, seeds, 6, [2, 14], comps, subs, chunk=32)
    print(name, len(comps), "comps; 32 subsets x 2 offsets x 256 worlds:", round(time.time() - t, 1), "s", flush=True)
