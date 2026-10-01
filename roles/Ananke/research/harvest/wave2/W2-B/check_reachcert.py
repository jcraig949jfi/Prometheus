"""W2-B check R: attainability gaps of the proposed reach_certificate (harvest/H-INST/pte_trace.py).
(a) ANY-aggregation + VALUE (not decision) output: a +1 nudge to S0 at the readout site of ONE world reads
    REACHED_OUTPUT for the batch although no decision changed anywhere.
(b) WINDOW ALIASING: a hook in trial 0 that touches the readout site (and is erased by trial 1's cue) makes
    trial K read ABSORBED ("admissible null"), although nothing reached trial K.
usage: python check_reachcert.py"""
import sys

import w2b_common as c
from w2b_common import np, envs, assays, plants, torch

sys.path.insert(0, str(c.ROOT / "roles/Ananke/research/harvest/H-INST"))
import pte_trace as P  # noqa: E402
from prometheus.ananke import c1b  # noqa: E402

SEEDS = assays.world_seeds(c.NS + 3, 16)
M = len(SEEDS)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)
TK = c1b.ticks(HOLD)
K = 5


def main():
    ck = c.Clock()
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    g = plants.plant("hold_latch", ph)
    ep = envs.build(ph, HOLD, SEEDS)
    a = torch.as_tensor(ep.schedule.read_idx[:, 0])

    def nudge_world0(w):
        w.S[0, a[0], 0] += 1

    def zero_readout_S0(w):
        w.S[torch.arange(M), a, 0] = 0

    def s0_elsewhere(w):
        w.S[torch.arange(M), (a + 5) % w.N, 0] += 7

    out = {}
    ra = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["ro"][K] - 1: nudge_world0}, K)
    dt = ra.pop("trace")
    rt = ep.ro_tick[:, K]
    dec = (np.sign(dt.traceA[rt, np.arange(M), 0]) != np.sign(dt.traceB[rt, np.arange(M), 0])).mean()
    out["a_nudge_one_world"] = {**{k: ra[k] for k in ("verdict", "applied", "touched", "output")},
                                "decision_changed_frac": float(dec)}
    rb = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["mid"][0]: zero_readout_S0}, K)
    rb.pop("trace")
    out["b_trial0_hook_read_at_trialK"] = {k: rb[k] for k in ("verdict", "applied", "touched", "output", "first_touch_lag")}
    rb2 = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["mid"][0]: zero_readout_S0, TK["mid"][K]: s0_elsewhere}, K)
    rb2.pop("trace")
    rb3 = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["mid"][K]: s0_elsewhere}, K)
    rb3.pop("trace")
    out["b2_trialK_hook_plus_trial0_hook"] = {k: rb2[k] for k in ("verdict", "applied", "touched", "output")}
    out["b3_trialK_hook_alone"] = {k: rb3[k] for k in ("verdict", "applied", "touched", "output")}
    out["compute"] = ck.done()
    for k, v in out.items():
        print(k, v)
    c.save("check_reachcert.json", out)


if __name__ == "__main__":
    main()
