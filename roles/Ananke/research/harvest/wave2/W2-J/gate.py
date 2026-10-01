"""Known-answer gate: H-PLANT P-XOR at X0 reproduces 1.000 on 32 pairs (64 worlds), W2-J namespace."""
from wj_common import *
import time
import run_xor as rx  # H-PLANT (read-only import)
import hp_plants as hp
from prometheus.ananke import assays
t0 = time.process_time()
seeds = assays.world_seeds(WJ_NS, 64)
g = hp.p_xor(rx.X0, rx.ENV0.period())
r = hc.evaluate(rx.X0, g, rx.ENV0, seeds)
mf = hc.evaluate(rx.X0, g, rx.ENV0, seeds, sched_fn=rx.zero_s2)
r.pop("pairs"); mf.pop("pairs")
out = {"normal": r, "mf_s2_zeroed": mf, "pass": r["acc"] == 1.0 and abs(mf["acc"] - 0.5) < 0.02,
       "cpu_s": time.process_time() - t0}
print(out)
save("gate.json", out)
