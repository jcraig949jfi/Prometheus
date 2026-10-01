"""KA-MH re-run after the relay-gate fix (zero packets circulated forever under CNT0 gating, so the run
tally never reset; ka.py's INT_2/INT_3/INT_3NB rows are void). 512 worlds, namespace 0x57324D."""
import w2m_common as c, w2m_plants as wp
from prometheus.ananke import envs, assays
from prometheus.ananke.engine import Controls
from ka import PH  # noqa  (re-imports run ka.py? guarded below)
seeds = assays.world_seeds(0x57324D, 512)
ck = c.Clock(); out = []
CASES = [("KA-1H", 3, dict(lanes=2)), ("KA-MH", 2, dict(lanes=2)), ("KA-MH", 2, dict(lanes=3)),
         ("KA-MH", 2, dict(lanes=3, weights=[-2, 1, 1])), ("KA-MH", 2, dict(lanes=2, gated=True))]
for name, d, kw in CASES:
    ph = PH[name][0].validate(); env = envs.EnvSpec(family="MAJ", d=d, delta=8, trials=12)
    ph2, g, ok, n = wp.member(ph, **kw)
    ctrls = [("none", {})]
    if kw == dict(lanes=3, weights=[-2, 1, 1]) or (name == "KA-MH" and kw == dict(lanes=2)):
        ctrls += [("zero_comm", dict(ctrl=Controls(zero_comm=True))), ("DICT", dict(sched_fn=wp.dict_sched))]
    for cn, ex in ctrls:
        r = c.hc.evaluate(ph2, g, env, seeds, **ex)
        out.append({"physics": name, "member": kw, "lines": n, "control": cn, "prog_len_used": ph2.prog_len,
                    "acc": r["acc"], "lo99": r["lo99"], "hi99": r["hi99"]})
        print(name, kw, n, cn, "%.4f [%.4f,%.4f]" % (r["acc"], r["lo99"], r["hi99"]), flush=True)
c.save("ka_mh.json", {"rows": out, "compute": ck.done()}); print(ck.done())
