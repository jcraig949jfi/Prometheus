"""N15: under BASE write-back, does pairing with an exact kin copy protect 7ae3 from erosion (and keep it fertile)?
Static: chain the founder through T successive interactions (registers and BASE-written content carried, copy errors on),
partners either fresh random genomes or exact copies of the CURRENT founder content (kin), or a kin fraction q.
Readouts per step: founder identity to the original, conversion events, and 'still a copier' (zero-context convert test)."""
import sys, os, random, json
CAMP = os.path.join(os.path.dirname(__file__), '..', '..', 'campaigns')
sys.path[:0] = [os.path.join(CAMP, 'c9x-explore-2026-09-24', 'x_donor_swap'), os.path.join(CAMP, 'z80atlas-verify-2026-09-22')]
import world, z8, p11, run_ds
g0 = run_ds.donor_genome()
a = run_ds.cells()['7ae3f9c1437c8000-s54765-tL-a0']
r = world.Runner(dict(a['cell'], atlas_axis='NONE'), 1, tier=a['tier'])
n = r.L; tl = world._pow2(2 * n); budget = r.t['slice']; mask = r._ops_mask(); cmr = r.copy_mut
def step(g, regs, partner, side, rng):
    tape = bytearray(tl)
    ga, gb = (g, partner) if side == 0 else (partner, g)
    tape[0:n] = ga; tape[n:2 * n] = gb
    out_regs = None; wo = 0
    for who, start in ((0, 0), (1, n)):
        ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=rng, copy_mut_rate=cmr, sense=who)
        if who == side:
            ctx.regs = None if regs is None else list(regs)
        else:
            ctx.regs = None
        z8.run(ctx, start, budget, ops_enabled=mask)
        if who == side:
            out_regs = list(ctx.regs); wo = ctx.writes_other
    own = bytes(tape[0:n]) if side == 0 else bytes(tape[n:2 * n])
    other = bytes(tape[n:2 * n]) if side == 0 else bytes(tape[0:n])
    conv = p11.fidelity(other, g) >= 0.9 and wo >= n // 4
    return own, out_regs, conv
def copier(g, rng, k=8):
    ok = 0
    for i in range(k):
        p = bytes(rng.randrange(256) for _ in range(n))
        ok += step(g, None, p, 1, rng)[2] or step(g, None, p, 0, rng)[2]
    return ok / k >= 0.5
res = {}
T = 12; L = 150
for q in (0.0, 0.25, 0.5, 1.0):
    R = random.Random(int(q * 1000) + 7)
    ident = [0.0] * T; convs = [0] * T; fert = [0] * T
    for life in range(L):
        g = g0; regs = None
        for t in range(T):
            partner = g if R.random() < q else bytes(R.randrange(256) for _ in range(n))
            side = R.randrange(2)
            g2, regs, c = step(g, regs, partner, side, R)
            convs[t] += c
            g = g2
            ident[t] += p11.fidelity(g, g0)
            if t in (0, 3, 7, 11):
                fert[t] += copier(g, R, 4)
    res['kin_q=%.2f' % q] = {'identity_by_step': [round(x / L, 3) for x in ident],
                            'conversions_per_step': [round(x / L, 3) for x in convs],
                            'still_copier_at_steps_1_4_8_12': [round(fert[t] / L, 3) for t in (0, 3, 7, 11)]}
    print(q, res['kin_q=%.2f' % q], flush=True)
json.dump(res, open(os.path.join(os.path.dirname(__file__), 'kin.json'), 'w'), indent=1)
