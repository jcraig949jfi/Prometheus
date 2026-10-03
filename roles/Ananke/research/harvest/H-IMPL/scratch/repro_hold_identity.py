"""H-IMPL: HOLD distractors are mirror-NEGATED (envs.py:164), so after a mid-gap
swap the two chimeras receive different inputs; the census identity is then not
forced. Known-answer: an accumulator S0 += SENSE that also integrates distractors."""
import numpy as np, torch
torch.set_num_threads(2)
from prometheus.ananke import assays, envs, plants, lens_swap as L
from prometheus.ananke.physics import Physics
ph = Physics(topology="ring", n_sites=16, radius=1, state_dim=1, payload_width=1, channels=1, prog_len=4).validate()
g = plants.plant("null", ph)
g[:, 0] = (plants.OPS["ADD"], 0, plants.regmap(ph)["SENSE"], 0, 0)      # S0 := S0 + SENSE
env = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, amp=256, amp_dist=64, trials=12)
seeds = assays.world_seeds(0x1D, 64)
off = env.cue_len + env.gap // 2 - 1
arms = [L.Arm("normal")] + [L.Arm(f"{n}{k}", tuple(L.SITE if n == "s" else L.FLIGHT), off, k) for k in range(2, 10) for n in "sc"]
r = L.run_arms(ph, g, env, seeds, arms, device="cpu")
n = r.per_trial["normal"]
site = np.full_like(n, np.nan); chan = np.full_like(n, np.nan)
ss = np.full(n.shape, L.NOT_RUN, np.int64); sc = ss.copy()
for k in range(2, 10):
    site[:, k] = r.per_trial[f"s{k}"][:, k]; chan[:, k] = r.per_trial[f"c{k}"][:, k]
    ss[:, k] = r.s0[f"s{k}"][:, k]; sc[:, k] = r.s0[f"c{k}"][:, k]
c = L.census(n, site, chan, ss, sc, range(2, 10), n_boot=200)
print("normal acc", np.nanmean(n[:, 2:10]).round(3), "eligible", c["eligible"], "identity", c["identity"],
      "identity_s0", c["identity_s0"], "class", L.classify(c))
