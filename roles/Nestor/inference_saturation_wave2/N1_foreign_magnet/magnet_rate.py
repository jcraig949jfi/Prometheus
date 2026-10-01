"""N1: per-interaction predecessor-accepted overwrite rate of the 7ae3 founder in foreign cells (9cba, e160) vs own cell,
intact vs copy-byte knockouts, zero vs random contexts, with authorship. Static (p11.interact), stock z8 as in C-SWAP-ACQUIRE.
Question: does a small per-interaction rate, integrated over a run, account for the 100/240 founder-label losses?"""
import sys, random, json, os
CAMP = os.path.join(os.path.dirname(__file__), '..', '..', 'campaigns')
sys.path[:0] = [os.path.join(CAMP, 'c9x-explore-2026-09-24', 'x_donor_swap'), os.path.join(CAMP, 'z80atlas-verify-2026-09-22'),
                os.path.join(CAMP, '..', '..', '..', 'lib')]
import world, z8, p11, run_ds
g = run_ds.donor_genome()
cells = run_ds.cells()
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
out = {}
for sp in ('7ae3f9c1437c8000-s54765-tL-a0', '9cba7113df39009e-s3882-tL-a0', 'e16055dd06cff594-s37315-tL-a0'):
    a = cells[sp]
    r = world.Runner(dict(a['cell'], atlas_axis='NONE'), 1, tier=a['tier'])
    n = r.L; tl = world._pow2(2 * n)
    kw = dict(n=n, tape_len=tl, budget=r.t['slice'], ops_mask=r._ops_mask(), cmr=r.copy_mut)
    variants = {'intact': g}
    for name, pos in (('ko_self', (23, 24)), ('ko_ldir', (52, 53)), ('ko_both', (23, 24, 52, 53))):
        b = bytearray(g)
        for i in pos: b[i] = 0
        variants[name] = bytes(b)
    res = {'ops_mask': r._ops_mask(), 'L': n, 'slice': r.t['slice'], 'epochs': r.t.get('epochs'), 'pop': r.t.get('pop')}
    for ctxname in ('zero', 'random'):
        for vname, fg in variants.items():
            R = random.Random(hash((sp, ctxname, vname)) & 0xffffffff)
            hits = {0: 0, 1: 0}; auth = [0, 0]
            for t in range(N):
                pb = bytes(R.randrange(256) for _ in range(n))
                side = t % 2
                st_f = (None, 0, 0) if ctxname == 'zero' else ([R.randrange(256) for _ in range(8)], 0, 0)
                st_p = (None, 0, 0) if ctxname == 'zero' else ([R.randrange(256) for _ in range(8)], 0, 0)
                ga, gb = (fg, pb) if side == 0 else (pb, fg)
                sa, sb = (st_f, st_p) if side == 0 else (st_p, st_f)
                tape, prov, lit, wo = p11.interact(z8, ga=ga, gb=gb, st_a=sa, st_b=sb, rng=random.Random(t), **kw)
                h0 = 0 if side == 0 else n
                fh = bytes(tape[h0:h0 + n])
                partner_wrote = wo[1 - side]
                if p11.predecessor_accepts(p11.fidelity(fh, pb), p11.fidelity(fh, fg), partner_wrote, n):
                    hits[side] += 1
                    who = [prov[h0 + i] for i in range(n) if fh[i] != fg[i]]
                    auth[0] += sum(1 for x in who if x == side + 1); auth[1] += sum(1 for x in who if x == 2 - side)
            res['%s/%s' % (ctxname, vname)] = {'side0': hits[0], 'side1': hits[1], 'n_per_side': N // 2,
                                                'bytes_by_founder_ctx': auth[0], 'bytes_by_partner_ctx': auth[1]}
    out[sp[:4]] = res
    print(sp[:4], json.dumps(res))
json.dump(out, open(os.path.join(os.path.dirname(__file__), 'magnet_rate.json'), 'w'), indent=1)
