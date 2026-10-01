"""N9: static decomposition of the ATOMIC write-back rule for 7ae3 in its own cell (stock VM, splice off).
Per interaction (founder vs uniform random partner, founder side 50/50), apply alternative write-back rules W to the
post-interaction tape and count founder-like halves (identity >= 0.9 to founder) -> offspring law (p0,p1,p2) -> GW P_est.
W variants:
  BASE        both halves written back as left on the tape
  ATOMIC      a half keeps its tape content only if predecessor-promoted (fid_other>=.9, fid_self<.9, donor wrote>=n/4),
              else it is restored to its pre-interaction content (world rule of C-ATOMIC)
  ATOM+SELF   as ATOMIC, but a restored half keeps the bytes its OWN context wrote (self-writes kept)
  WRITEGATE   a half keeps its tape content iff the other side wrote >= n/4 bytes into it (no fidelity clause)
Contexts: ZERO (founder fresh) and RANDOM registers. Copy errors at the cell rate."""
import sys, json, random, os
CAMP = os.path.join(os.path.dirname(__file__), '..', '..', 'campaigns')
sys.path[:0] = [os.path.join(CAMP, 'c9x-explore-2026-09-24', 'x_donor_swap'), os.path.join(CAMP, 'z80atlas-verify-2026-09-22'),
                os.path.join(CAMP, '..', '..', '..', 'lib')]
import world, z8, p11, run_ds
g = run_ds.donor_genome()
a = run_ds.cells()['7ae3f9c1437c8000-s54765-tL-a0']
r = world.Runner(dict(a['cell'], atlas_axis='NONE'), 1, tier=a['tier'])
n = r.L; tl = world._pow2(2 * n)
kw = dict(n=n, tape_len=tl, budget=r.t['slice'], ops_mask=r._ops_mask(), cmr=r.copy_mut)
def gw(p0, p1, p2):
    s = 0.5
    for _ in range(2000):
        s = 1 - (p0 + p1 * (1 - s) + p2 * (1 - s) ** 2)
    return max(0.0, s)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
out = {}
for ctx in ('ZERO', 'RANDOM'):
    R = random.Random(hash(ctx) & 0xffff)
    cnt = {w: [0, 0, 0] for w in ('BASE', 'ATOMIC', 'ATOM+SELF', 'WRITEGATE')}
    for t in range(N):
        pb = bytes(R.randrange(256) for _ in range(n))
        side = t % 2
        stf = (None, 0, 0) if ctx == 'ZERO' else ([R.randrange(256) for _ in range(8)], 0, 0)
        stp = ([R.randrange(256) for _ in range(8)], 0, 0)
        ga, gb = (g, pb) if side == 0 else (pb, g)
        sa, sb = (stf, stp) if side == 0 else (stp, stf)
        tape, prov, lit, wo = p11.interact(z8, ga=ga, gb=gb, st_a=sa, st_b=sb, rng=random.Random(t), **kw)
        pre = [ga, gb]; fin = [bytes(tape[0:n]), bytes(tape[n:2 * n])]
        def promoted(h):
            other = pre[1 - h]
            return p11.predecessor_accepts(p11.fidelity(fin[h], other), p11.fidelity(fin[h], pre[h]), wo[1 - h], n)
        res = {}
        res['BASE'] = fin
        res['ATOMIC'] = [fin[h] if promoted(h) else pre[h] for h in (0, 1)]
        def selfkept(h):
            if promoted(h):
                return fin[h]
            b = bytearray(pre[h]); off = 0 if h == 0 else n
            for i in range(n):
                if prov[off + i] == h + 1:
                    b[i] = fin[h][i]
            return bytes(b)
        res['ATOM+SELF'] = [selfkept(0), selfkept(1)]
        res['WRITEGATE'] = [fin[h] if wo[1 - h] >= n // 4 else pre[h] for h in (0, 1)]
        for w, halves in res.items():
            k = sum(p11.fidelity(hh, g) >= 0.9 for hh in halves)
            cnt[w][k] += 1
    out[ctx] = {}
    for w, c in cnt.items():
        p0, p1, p2 = (x / N for x in c)
        out[ctx][w] = {'p0': round(p0, 3), 'p1': round(p1, 3), 'p2': round(p2, 3), 'm': round(p1 + 2 * p2, 3), 'P_est': round(gw(p0, p1, p2), 3)}
    print(ctx, json.dumps(out[ctx]))
json.dump(out, open(os.path.join(os.path.dirname(__file__), 'wdecomp.json'), 'w'), indent=1)
