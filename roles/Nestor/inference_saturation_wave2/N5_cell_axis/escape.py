"""N5: does the CF (Z8_SLOTTED) world-mutation operator let founders escape self-poisoning faster than C7 (OPERAND, opcodes
immune)?  Static: single world-mutation mutants of each panel donor, scored for carried-state copying (copy from the
registers left by the genome's own previous execution).  Reuses forensics/map_common.py's exact cell construction."""
import sys, json, random, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'inference_harvest_2026-09-30' / 'forensics'))
import map_common as mc
import world, p11
z8 = mc.DENSE
P2 = mc.P2
donors = json.load(open(P2 / 'c_zero_specific' / 'DONORS.json'))
donors = donors if isinstance(donors, list) else donors.get('donors', donors)
def hexof(d): return d['hex'] if isinstance(d, dict) and 'hex' in d else (d.get('genome') if isinstance(d, dict) else d)
G = [bytes.fromhex(hexof(d)) for d in donors]
runners = {c: mc.Harness('ZERO', 1, cell=c).r for c in ('C7', 'CF')}
r0 = runners['CF']; n = r0.L; tl = world._pow2(2 * n); budget = r0.t['slice']; mask = r0._ops_mask()

def run_side(g, partner, side, regs):
    tape = bytearray(tl)
    a, b = (g, partner) if side == 0 else (partner, g)
    tape[0:n] = a[:n]; tape[n:2 * n] = b[:n]
    prov = bytearray(tl); lit = bytearray(tl); out_regs = None; wo = 0
    for who, start in ((0, 0), (1, n)):
        ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=who)
        if who == side:
            ctx.regs = None if regs is None else list(regs)
        ctx.prov, ctx.prov_lit, ctx.who = prov, lit, who + 1
        z8.run(ctx, start, budget, ops_enabled=mask)
        if who == side:
            out_regs = list(ctx.regs); wo = ctx.writes_other
    other = bytes(tape[n:2 * n]) if side == 0 else bytes(tape[0:n])
    conv = p11.fidelity(other, g[:n]) >= 0.9 and wo >= n // 4
    return conv, out_regs

def carried_ok(g, R, trials=6):
    """copies from zero first (screen), then from its own carried registers, against fresh random partners; per side."""
    best = 0.0
    for side in (0, 1):
        ok0 = okc = 0
        for t in range(trials):
            p = bytes(R.randrange(256) for _ in range(n))
            c0, regs = run_side(g, p, side, None)
            ok0 += c0
            p2 = bytes(R.randrange(256) for _ in range(n))
            c1, _ = run_side(g, p2, side, regs)
            okc += c1 and c0
        if ok0:
            best = max(best, okc / trials)
    return best

def mutant(r, g, R):
    r.rng = R
    for _ in range(200):
        m = r._mutate(g)
        if m != g:
            return m
    return g

def _main():
    out = []
    for k, g in enumerate(G):
        R = random.Random(1000 + k)
        base = carried_ok(g, R)
        row = {'donor': k, 'base_carried_ok': base}
        for c, r in runners.items():
            vals = [carried_ok(mutant(r, g, R), R) for _ in range(80)]
            row[c] = {'mean': round(sum(vals) / len(vals), 3), 'escape': sum(v >= 0.5 for v in vals)}
        out.append(row); print(row, flush=True)
    json.dump(out, open(HERE / 'escape.json', 'w'), indent=1)
    pois = [x for x in out if x['base_carried_ok'] < 0.5]
    print('poisoned donors', len(pois), 'escape C7', sum(x['C7']['escape'] for x in pois), 'CF', sum(x['CF']['escape'] for x in pois), 'of', 80 * len(pois))
    
if __name__ == "__main__":
    _main()
