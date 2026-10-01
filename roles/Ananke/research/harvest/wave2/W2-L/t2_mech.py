"""Task 2 mechanism: per-trial decomposition of relay_flood on FLIP by (m, cue same/changed vs previous trial),
and what the actuator's S0 at readout equals (x_k, y_{k-1}). usage: python t2_mech.py <cell> [physics overrides k=v ...]"""
from w2l_common import *
from prometheus.ananke.engine import World
cid = sys.argv[1]
GN = os.environ.get("W2L_G", "relay")
r = hc.row(cid); ph, env = cell(r)
over = {}
for kv in sys.argv[2:]:
    k, v = kv.split("="); over[k] = type(getattr(ph, k))(v) if not isinstance(getattr(ph, k), float) else float(v)
if over:
    ph = ph.replace(**over).validate()
if ph.prog_len < 12:
    ph = ph.replace(prog_len=12).validate()
ck = Clock()
seeds = held_seeds(r)
M = len(seeds)
ep = envs.build(ph, env, seeds)
ws = [seeds[m - (m % 2)] for m in range(M)]
import hp_plants as _hp
if GN == "latch":
    sys.argv = [sys.argv[0]]; import importlib.util as _u
    _sp = _u.spec_from_file_location("rl", str(HERE / "relay_latch_def.py")); _m = _u.module_from_spec(_sp); _sp.loader.exec_module(_m)
    G = _m.relay_latch(ph)
elif GN == "pflip":
    G = _hp.p_flip(ph)
else:
    G = plants.plant("relay_flood", ph)
g = np.repeat(G[None], M, axis=0)
w = World(ph, g, ws, device="cpu", schedule=ep.schedule)
w.run(env.T(), graph=False)
trace = w.trace.cpu().numpy()
B, tr = ep.y.shape
s0 = trace[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot]
ans = np.sign(s0)
Pd = env.period()
sv = ep.schedule.sense_val.numpy()          # [T,B,K]
x = np.sign(sv[np.arange(tr) * Pd][:, :, 0]).T  # [B,tr] cue sign (with mirror sign)
y = ep.y
m = y * x
corr = np.where(s0 == 0, 0.5, (ans == y).astype(float))
sc = ep.scored.copy()
prev_same = np.zeros_like(sc); prev_same[:, 1:] = x[:, 1:] == x[:, :-1]
ans_eq_x = (ans == x); ans_eq_yprev = np.zeros_like(sc); ans_eq_yprev[:, 1:] = ans[:, 1:] == y[:, :-1]
tab = {}
for mv in (1, -1):
    for same in (True, False):
        k = (sc & (m == mv) & (prev_same == same))
        tab[f"m{'+' if mv > 0 else '-'}_{'same' if same else 'change'}"] = {
            "n": int(k.sum()), "acc": float(corr[k].mean()), "ans=x_k": float(ans_eq_x[k].mean()),
            "ans=y_prev": float(ans_eq_yprev[k].mean()), "ans=0": float((s0[k] == 0).mean())}
acc_w = (corr * sc).sum(1) / sc.sum(1)
pairs = acc_w.reshape(-1, 2).mean(1)
mm, lo, hi = assays.pair_ci(pairs)
tab["changed_trials_acc"] = float(corr[sc & ~prev_same].mean()); tab["same_trials_acc"] = float(corr[sc & prev_same].mean())
out = {"genome": GN, "cell": cid, "overrides": over, "acc": float(mm), "lo99": float(lo), "hi99": float(hi), "table": tab, "compute": ck.done()}
print(cid, over, "acc %.3f [%.3f,%.3f]" % (mm, lo, hi))
for k, v in tab.items():
    print(" ", k, {kk: round(vv, 3) for kk, vv in v.items()} if isinstance(v, dict) else round(v, 3))
save(f"t2_mech_{GN}_{cid[:8]}{'_' + '_'.join(f'{k}{v}' for k, v in over.items()) if over else ''}.json", out)
