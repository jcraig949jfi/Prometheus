"""Eroding-target test for X-REDISCOVER-SUPPLY: replay RS1_DIR100 seed 45100000 (deterministic; same cfg) and track,
every 25 epochs, the share of live organisms that are ONE STEP from use (u >= 0.75 once byte 31 is set to 0x25)."""
import json, sys
sys.dont_write_bytecode = True
import exp, fh
cfg = dict(gate="CONST", p_const=1.0, order="DIR", plant=exp.ct_ua_add(0x24), epochs=400)
r = fh.make_runner(45_100_000, cfg)
anc = 0
for i in range(r.pop_cap):
    g = r._pad(r._implant_genome()) if i == 0 else r._seed_genome()
    o = r._place(g, anc, niche=r._initial_niche(i)); o.energy = r.t["slice"] * 2; anc += 1
r._validate(force=True)
out = []
while r.epoch < 400:
    r.step()
    if r.epoch % 25 == 0:
        alive = [o for o in r.orgs if o.alive]
        one = cop = 0
        for o in alive:
            g = bytearray(r._genome(o))
            cop += g[:7] == fh.PLANTS["CT_UA"][:7]
            g[31] = 0x25
            one += r.cache.u(bytes(g)) >= fh.COMP_MIN
        out.append({"e": r.epoch, "one_step_share": round(one / len(alive), 3), "copier_prefix_share": round(cop / len(alive), 3)})
        print(out[-1], flush=True)
json.dump(out, open("runs/X-REDISCOVER-SUPPLY/MINE_EROSION_45100000.json", "w"), indent=1)
