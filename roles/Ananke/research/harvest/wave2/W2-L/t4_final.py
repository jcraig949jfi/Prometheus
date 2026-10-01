"""Rescore + FLIP_FEEDBACK (W2-B ruler semantics: normal minus 'teachers after trial 0 removed', lo99 > .10).
mode full: normal M=64 + ablated M=64, paired diff CI (exact W2-B semantics, re-implemented with hc.evaluate).
mode abl <M>: ablated only on the first M held worlds; conservative diff_lo = reading_lo99 - ablated_hi99.
usage: python t4_final.py full <variant> <cells>   |   python t4_final.py abl <M> <variant> <cells>"""
from w2l_common import *
import hp_variants as hv
mode = sys.argv[1]
if mode == "full":
    M, variant, cells = 64, sys.argv[2], sys.argv[3].split(",")
else:
    M, variant, cells = int(sys.argv[2]), sys.argv[3], sys.argv[4].split(",")
ck = Clock(); out = []
for c in cells:
    r = hc.row(c); ph, env = cell(r)
    need = hv.NEED_L[variant]
    exact = ph.state_dim >= 2 and ph.prog_len >= need
    p2 = ph if exact else ph.replace(state_dim=max(2, ph.state_dim), prog_len=max(need, ph.prog_len)).validate()
    g = hv.plant(variant, p2); s = held_seeds(r, M); Pd = env.period()
    def abl(ep): ep.schedule.sense_val[Pd:, :, 1] = 0
    b = hc.evaluate(p2, g, env, s, sched_fn=abl)
    o = {"cell": c, "variant": variant, "exact_space": exact, "M": M, "abl_acc": b["acc"], "abl_lo99": b["lo99"], "abl_hi99": b["hi99"]}
    if mode == "full":
        a = hc.evaluate(p2, g, env, s)
        dm, dlo, dhi = assays.pair_ci(np.array(a["pairs"]) - np.array(b["pairs"]))
        o.update({"acc": a["acc"], "lo99": a["lo99"], "hi99": a["hi99"], "pairs": a["pairs"], "ff_diff": float(dm), "ff_diff_lo99": float(dlo),
                  "FLIP_FEEDBACK": bool(a["lo99"] > 0.55 and dlo > 0.10)})
    out.append(o)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items() if k != "pairs"}, flush=True)
save(f"t4_{mode}_{variant}_{cells[0][:8]}_n{len(cells)}.json", {"rows": out, "compute": ck.done()})
print(ck.done())
