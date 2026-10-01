"""FLIP economy rows: two-rule plant (short relay rule + long non-emitting actuator rule)."""
import sys, json
sys.path.insert(0, '.')
import wz_common as wz, plants_wz as pw
np = wz.np
ROWS = sys.argv[1].split(",")
M = int(sys.argv[2]) if len(sys.argv) > 2 else 64
VAR = sys.argv[3].split(",") if len(sys.argv) > 3 else ["main"]
tag = sys.argv[4] if len(sys.argv) > 4 else "x"
res = {}
clk = wz.Clock()


def build(ph0, var):
    s = 1
    relay = pw.relay_att(s) + pw.DISPATCH
    act = pw.flip_actuator_v2() if var.startswith("v2") else pw.flip_actuator()
    if var.startswith("v3"):
        act = pw.flip_actuator_v3()
        relay = (pw.relay_dedup() if var.startswith("v3d") else pw.relay_att(1)) + pw.DISPATCH
    if var.startswith("v2d"):          # dedup relay (9) + dispatch (2) = 11 lines
        relay = pw.relay_dedup() + pw.DISPATCH
    elif var.startswith("v2s"):
        s = int(var[3:]); relay = pw.relay_att(s) + pw.DISPATCH
    elif var.startswith("s"):
        s = int(var[1:]); relay = pw.relay_att(s) + pw.DISPATCH
    if "nom" in var:          # must-fail: readout ignores m (S0 = S2): copy-class
        act = act[:-1] + [("MOV", "S0", "S2", 0, 0)]
    ov = dict(prog_len=max(ph0.prog_len, len(act)), state_dim=max(ph0.state_dim, 3))
    if ph0.rules < 2:
        ov["rules"] = 2
    if not ph0.setrule:
        ov["setrule"] = 1
    ph = ph0.replace(**ov).validate()
    g = pw.two_rule(ph, relay, act)
    return ph, g, ov, len(relay)


for c in ROWS:
    r = wz.row(c); ph0, env = wz.cell(r)
    seeds = wz.held(r, M)
    for var in VAR:
        base = var.replace("+eoff", "").replace("+zc", "").replace("+elite", "")
        ph, g, ov, kr = build(ph0, base)
        if "+eoff" in var:
            ph = wz.econ_off(ph)
        if "+elite" in var:   # economy kept on but non-binding: no op/mem cost, emission 1 per copy
            ph = ph.replace(c_op=0, c_mem=0, c_emit=1)
        ctrl = wz.Controls(zero_comm=True) if "+zc" in var else None
        o = wz.ws.flip_eval(ph, g, env, seeds, ctrl=ctrl)
        st = wz.run_stats(ph, g, env, seeds[:8], ctrl=ctrl) if var == VAR[0] else None
        key = f"{r['cell_id'][:8]}|{var}"
        res[key] = {"ov": ov, "relay_k": kr, **{k: o.get(k) for k in ("acc", "lo99", "chg", "chg_lo99", "same", "bal", "bal_lo99", "ro_zero_frac")},
                    "emitters_per_awake": (st["emitters"] / max(1, st["awake"])) if st else None}
        print(key, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[key].items()}), flush=True)
res["_clock"] = clk.done()
print(res["_clock"])
wz.save(f"flip_{tag}.json", res)
