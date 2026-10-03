"""H-IMPL repros: trace overwrite past the schedule, Controls.label with a mask,
no-op guard vs LM-shaped digests, handoff vacuity, wave_D resume drift."""
import copy, numpy as np, torch
torch.set_num_threads(2)
from prometheus.ananke import assays, envs, plants, lens_swap, campaign as C
from prometheus.ananke.engine import Controls, World, Schedule
from prometheus.ananke.physics import Physics

# 1. trace row T-1 is overwritten by ticks run past the schedule
ph = Physics(topology="ring", n_sites=8, radius=1, state_dim=1, payload_width=1, channels=1, prog_len=4).validate()
g = plants.plant("sense_copy", ph)[None].repeat(2, 0)
T = 4
sv = torch.zeros(T, 2, 1, dtype=torch.int32); sv[T - 1] = 300          # cue on the last scheduled tick
sch = Schedule(torch.zeros(2, 1, dtype=torch.int64), sv, torch.zeros(2, 1, dtype=torch.int64))
a = World(ph, g, [1, 1], device="cpu", schedule=sch); a.run(T, graph=False)
b = World(ph, g, [1, 1], device="cpu", schedule=sch); b.run(T + 2, graph=False)
print("1. trace[T-1] after T ticks:", a.trace[T - 1, :, 0].tolist(), " after T+2 ticks:", b.trace[T - 1, :, 0].tolist())

# 2. Controls.label() with a reset mask
try:
    print("2. label:", Controls(reset_state_at=(3,), reset_state_mask=np.ones((2, 8), bool)).label())
except Exception as e:
    print("2. Controls.label() with a mask raises", type(e).__name__, str(e)[:80])

# 3. no-op guard: lat_base 1 -> 0 leaves every delay at 1 (clamp) but shrinks LM
ph3 = Physics(topology="ring", n_sites=24, radius=1, dest_mode="all", lat_base=1, lat_hop=0, lat_jitter=0,
              payload_width=1, channels=1, prog_len=12).validate()
env = envs.EnvSpec(family="RELAY", d=2, delta=8, trials=12)
gr = plants.plant("relay_flood", ph3)
seeds = assays.world_seeds(0xC0DE, 8)
r1 = assays.evaluate(ph3, gr[None], env, seeds, device="cpu", graph=False, want_digest=True)
ph3b = ph3.replace(lat_base=0)
r0 = assays.evaluate(ph3b, gr[None], env, seeds, device="cpu", graph=False, want_digest=True)
print("3. LM", ph3.lm(), "->", ph3b.lm(), "acc", r1.mean()[0], r0.mean()[0],
      "identical per-world acc:", bool(np.array_equal(r1.acc, r0.acc)), "digests equal (guard would fire):", r1.digests == r0.digests)

# 4. handoff KA7: clause (b) passes vacuously when the final 4 offsets were never scanned
mk = lambda cls, fC: {"class": cls, "fC": fC}
print("4. handoff on offsets {3:CHANNEL, 5:SITE}, ro_off=10:", lens_swap.handoff({3: mk("CHANNEL", .9), 5: mk("SITE", 0)}, 10))

# 5. wave_D: promoted pool changes once D's own evolve rows exist (resume)
cfg = C.CampaignConfig()
def row(cid, fam, lo, wave):
    return {"cell_id": cid, "wave": wave, "kind": "evolve", "env": {"family": fam}, "physics": {"p": cid},
            "levels": {}, "env_levels": {}, "result": {"held": {"lo99": lo, "comm_delta_lo99": 0.0}, "champion": [[0]]}}
prior = [row("a%d" % i, "RELAY", 0.60 + 0.01 * i, "A") for i in range(6)]
d_first = C.wave_D(cfg, prior)
d_resume = C.wave_D(cfg, prior + [row("drep", "RELAY", 0.99, "D")])
ids = lambda s: sorted(C.cell_id(dict(x)) for x in s)
print("5. wave_D specs first run:", len(d_first), " on resume:", len(d_resume),
      " identical cell ids:", ids(d_first) == ids(d_resume))
