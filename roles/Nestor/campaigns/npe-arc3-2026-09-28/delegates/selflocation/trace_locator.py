"""Trace the LOCATOR genomes: re-execute with budget b = 1..300 from scratch (exact prefix states), and
report every block-copy / SELF event with its registers, at bases 0, 32, 64. -> trace_locator.txt"""
import json, random, pathlib, selfloc, corpus_analysis as ca
HERE = pathlib.Path(__file__).resolve().parent
d = json.load(open(HERE / 'selfloc_results.json'))
world, rr = ca.env('DENSE', '7ae3'); z8 = world.z8
out = []
for g in [x for x in d['genomes'] if x['cls'] == 'LOCATOR']:
    b = bytes.fromhex(g['hex'])
    for base in (0, 32, 64):
        def fresh():
            vr = random.Random(1); t = bytearray(vr.randrange(256) for _ in range(128))
            for i in range(64): t[(base + i) % 128] = b[i]
            return t
        seen = set(); ev = []
        for bud in range(1, 301):
            t = fresh(); c = z8.Ctx(t, base, 64, policy=z8.ARENA, rng=random.Random(0), copy_mut_rate=0, sense=0)
            pc = z8.run(c, base, bud, ops_enabled=0x2A)
            if c.halted: break
            op = t[pc]; r = c.regs
            is_bc = op in (0xE5, 0xE7) or (op == 0xED and t[(pc + 1) % 128] in (0xB0, 0xB8, 0x32))
            key = (pc, tuple(r), c.ops)
            if is_bc and (pc, c.copy_bytes) not in seen:
                seen.add((pc, c.copy_bytes))
                ev.append('pc=%d(+%d) %s HL=%04X DE=%04X BC=%04X' % (pc, (pc - base) % 128,
                          ('%02X' % op) if op != 0xED else 'ED%02X' % t[(pc + 1) % 128],
                          (r[4] << 8) | r[5], (r[2] << 8) | r[3], (r[0] << 8) | r[1]))
        t = fresh(); c = z8.Ctx(t, base, 64, policy=z8.ARENA, rng=random.Random(0), copy_mut_rate=0, sense=0)
        z8.run(c, base, 300, ops_enabled=0x2A)
        fid = sum(t[(base + 64 + i) % 128] == b[i] for i in range(64)) / 64
        out.append('%s base %d partner-fid %.2f copy_bytes %d\n  ' % (g['origin_run'], base, fid, c.copy_bytes) + '\n  '.join(ev[:8]))
(HERE / 'trace_locator.txt').write_text('\n'.join(out))
print('\n'.join(out))
