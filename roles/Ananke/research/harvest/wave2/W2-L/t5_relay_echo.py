"""Task 2 attainability: RELAY_LATCH = relay of the cue sign (teacher excluded from transport, re-emit on change)
+ the actuator latches the teacher sign without emitting it (so no echo reaches the sensor: e = 1).
No mapping inference: the readout is always a COPY of the last cue wave or the last teacher. 14 lines, state_dim 1.
Analytic prediction (REPORT): acc = 1/2 + a/4, a = P(changed cue delivered by readout). d9cc cell, held seeds (32 pairs)."""
from w2l_common import *
A = plants.assemble
def relay_latch(ph):
    body = A(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0), ("CONST", "T2", 0, 0, 128), ("SUB", "T3", "ZERO", "T2", 0),
        ("GT", "PAY0", "T0", "T2", 0), ("GT", "T3", "T3", "T0", 0), ("SUB", "PAY0", "PAY0", "T3", 0),   # v = cue sign*256 (teacher excluded)
        ("SUB", "T0", "PAY0", "S0", 0), ("MULQ", "EMIT", "T0", "PAY0", 0),                              # emit iff v != 0 and v != S0
        ("MULQ", "T1", "PAY0", "PAY0", 0), ("SEL", "T1", "PAY0", "S0", 0), ("MOV", "S0", "T1", 0, 0),   # S0 := v where v != 0
        ("MULQ", "T3", "SENSE", "SENSE", 0), ("SEL", "T3", "SENSE", "S0", 0), ("MOV", "S0", "T3", 0, 0)])  # S0 := SENSE (teacher latch)
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()
ck = Clock()
r = hc.row("6f82f9c7d51bcef1"); ph, env = cell(r); s = held_seeds(r)
g = relay_latch(ph)
print("\n".join(hc.decompile(ph, g[0])))
res = comm_delta(ph, g, env, s)
Pd = env.period()
def abl(ep): ep.schedule.sense_val[Pd:, :, 1] = 0
b = hc.evaluate(ph, g, env, s, sched_fn=abl)
dm, dlo, dhi = assays.pair_ci(np.array(res["pairs"]) - np.array(b["pairs"]))
res.update({"abl_acc": b["acc"], "ff_diff": float(dm), "ff_diff_lo99": float(dlo), "FLIP_FEEDBACK": bool(res["lo99"] > .55 and dlo > .10),
            "SIGNAL": res["lo99"] > .55, "COMM_DEPENDENT": res["lo99"] > .55 and res["comm_delta_lo99"] > .03, "compute": ck.done()})
print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in res.items() if k != "pairs"})
save("t5_relay_latch_d9cc.json", res)
