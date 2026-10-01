"""Known-answer gate for multi_eval + FLIP_BIT16 at 6f82f9c7 (W2-L gate: P-FLIP .943 on the row's 32 held pairs),
then the matched decay counterfactual (decay_shift 1/3/6 on the same cell and worlds)."""
from w2ad_common import *
import w2ad_plants as P
from prometheus.ananke.search import HELD_NS
ck = Clock()
r = [x for x in hc.rows() if x["cell_id"].startswith("6f82f9c7") and x["kind"] == "evolve"][0]
ph0 = Physics.from_dict(r["physics"]).validate(); env = envs.EnvSpec(**r["env"])
print("prog_len", ph0.prog_len, "state_dim", ph0.state_dim, "decay", ph0.decay_shift, ph0.topology, ph0.update_mode, env)
seeds = assays.world_seeds(H_int(r["search_seed"], HELD_NS), 64)
res = {}
for dk in (0, 1, 3, 6):
    ph = ph0.replace(decay_shift=dk).validate()
    o, _ = multi_eval(ph, env, seeds, [("P_FLIP", P.DESIGNS["FLIP"]["P_FLIP"](ph), None),
                                      ("FLIP_BIT16", P.flip_bit16(ph), None),
                                      ("RELAY_LATCH", P.relay_latch(ph), None)])
    res[dk] = {k: {kk: round(v[kk], 4) for kk in ("acc", "lo99", "B", "B_lo99", "chg", "same")} for k, v in o.items()}
    print(dk, res[dk], flush=True)
print("lines FLIP_BIT16", P.nlines(P.flip_bit16(ph0)), ck.done())
jdump(OUT / "ka_flip.json", {"cell": r["cell_id"], "res": res, "compute": ck.done()})
