"""W2-AH common: CPU-only evaluation (H-PLANT hp_common.evaluate semantics = c1b/campaign evaluate, mirror pairs
share physics seeds), frugal RELAY plants, and the exact single-emitter energy DP bound (engine.py step 5).
Writes only into W2-AH/out."""
import os, sys, pathlib, json
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"; os.environ["HP_THREADS"] = "2"; os.environ["OMP_NUM_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "H-PLANT"))
import hp_common as hc  # noqa: E402  (asserts no CUDA, sets threads)
import numpy as np  # noqa: E402
import torch  # noqa: E402
assert not torch.cuda.is_available() and torch.get_num_threads() <= 2
from prometheus.ananke import plants, envs, assays  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402
A = plants.assemble
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- frugal plants
BODIES = {
    # F1 two-sided direct emitter, 3 non-NOP lines; sensor S stays 0 (m=0). == W2-Z/W2-M "LEAK3" (convergent).
    "F1": [("MULQ", "EMIT", "SENSE", "SENSE", 0),     # 256 on a cue tick (either sign), else 0
           ("MOV", "PAY0", "SENSE", 0, 0),            # sign carried in payload
           ("ADD", "S0", "S0", "IN0_0", 0)],          # receiver: saturating accumulator
    # F1x: same with payload 2*SENSE (larger steps; identical line count)
    "F1x": [("MULQ", "EMIT", "SENSE", "SENSE", 0),
            ("ADD", "PAY0", "SENSE", "SENSE", 0),
            ("ADD", "S0", "S0", "IN0_0", 0)],
    # F0 saturating write-on-change flood, 4 non-NOP lines (relay_flood has 12)
    "F0": [("ADD", "T0", "SENSE", "IN0_0", 0),        # v = cue + arrivals since last awake tick
           ("SUB", "PAY0", "T0", "S0", 0),            # d = v - S0 (clamped) -> payload; saturates on flips
           ("MULQ", "EMIT", "PAY0", "T0", 0),         # emit iff v*(v-S0) >= 256: news (flip or growth)
           ("ADD", "S0", "S0", "T0", 0)],             # S0 += v (saturating latch)
}


def body(ph, name):
    return A(ph, BODIES[name])


def genome(ph, name):
    if name == "relay_flood":
        return plants.plant("relay_flood", ph)
    return hc.bc(ph, body(ph, name))


def n_nonnop(name, ph):
    g = genome(ph, name)[0]
    return int((g[:, 0] % 16 != 0).sum())


def cell(r):
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    return ph, env


def plant_seeds(r, M=32):
    return assays.world_seeds(H_int(r["search_seed"], 0x9147), M)   # campaign.py plant_viability


# ---------------------------------------------------------------- energy DP (exact, any emission policy)
def dp_max_served(ph, env, k, m=0, win=None, t_first=None):
    """Max over ALL emission policies of the number of trials in which ONE site (the sensor) emits at least once
    inside the trial's useful window, under engine.py step 5 exactly:
      E0 = e_max; tick t: awake(t); emit allowed iff awake & E >= cE; E <- clip(E + inc - emit*cE
      - awake*c_op*k - c_mem*m, 0, e_max).  k = non-NOP lines of the rule, m = nonzero S registers (held const).
    win(t) -> trial index if an emission at t can still inform that trial's readout, else -1.
    Sync wake only (all rows here are sync)."""
    assert ph.update_mode == "sync"
    cE = ph.c_emit * ph.copies()
    T = env.T()
    NEG = -10 ** 9
    best = np.full(ph.e_max + 1, NEG, dtype=np.int64); best[ph.e_max] = 0
    # served-flag for current trial folded in: state (E, served_this_trial)
    st = {0: best, 1: np.full(ph.e_max + 1, NEG, dtype=np.int64)}
    cur_trial = -1
    E = np.arange(ph.e_max + 1)
    for t in range(T):
        tr = win(t)
        if tr != cur_trial and tr >= 0:
            st = {0: np.maximum(st[0], st[1]), 1: np.full(ph.e_max + 1, NEG, dtype=np.int64)}
            cur_trial = tr
        aw = (t % ph.update_period) == 0
        n0 = {0: np.full(ph.e_max + 1, NEG, dtype=np.int64), 1: np.full(ph.e_max + 1, NEG, dtype=np.int64)}
        cost = (ph.c_op * k if aw else 0) + ph.c_mem * m
        e_no = np.clip(E + ph.e_income - cost, 0, ph.e_max)
        e_em = np.clip(E + ph.e_income - cost - cE, 0, ph.e_max)
        for s in (0, 1):
            v = st[s]
            np.maximum.at(n0[s], e_no, v)                          # no emission
            if aw and tr >= 0:
                ok = (E >= cE) & (v > NEG)
                gain = 1 if s == 0 else 0
                np.maximum.at(n0[1], e_em[ok], v[ok] + gain)       # emission informing trial tr
        st = n0
    return int(max(st[0].max(), st[1].max()))


def relay_window(ph, env, dmin):
    """Emission at tick t informs trial j iff t0_j <= t <= ro_j - dmin (cue onset to last useful send)."""
    Pd = env.period()
    def win(t):
        j, ph_ = divmod(t, Pd)
        return j if (j < env.trials and ph_ <= env.delta - dmin) else -1
    return win


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
