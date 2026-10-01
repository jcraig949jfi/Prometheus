"""Secondary check: evaluate strict-genome plants on each row's OWN C1 held-out worlds
(search.HELD_NS from the row's search_seed; read-only use of the C1 seed derivation), next to C1's champion score."""
from v_common import *
from prometheus.ananke.rng import H_int
from prometheus.ananke.search import HELD_NS
import sbf, sbnor
ck = Clock()
out = {}
for name, c8, lines in [("sbf_c800", "4222a5f7", sbf.sbf(100, 3)),
                        ("sbnor", "48256f59", sbnor.sbnor(80, 0, 1)), ("sbnor", "1974a9cf", sbnor.sbnor(80, 0, 1)),
                        ("sbnor", "333d6b2b", sbnor.sbnor(80, 0, 1))]:
    r = row(c8); ph, env = row_phys(c8)
    hseeds = assays.world_seeds(H_int(r["search_seed"], HELD_NS), 64)
    acc, _ = veval(ph, asm(ph, lines)[None], env, hseeds)
    s = summarize(acc[0]); s["c1_champion_held"] = r["result"]["held"]
    out[f"{c8}_{name}"] = s
    print(c8, name, s["acc"], s["lo99"], "| C1 champion", {k: round(v, 3) for k, v in r["result"]["held"].items() if k in ("acc", "lo99")}, ck.cpu(), flush=True)
save("c1held.json", {"rows": out, "cpu_s": ck.cpu()})
