"""N12: which register bits does 'ZERO' actually supply?  Screen the 16 C-ZERO-SPECIFIC donors (all zero-competent) from
PATTERN entry vectors (order B C D E H L (HL) A as reset_axis) that hold the pointer phase at 0 (H=L=0x80: low 7 bits 0)
or perturb only one register group."""
import sys, json, random, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from escape import G, run_side, n
PAT = {
 'ZERO':            [0, 0, 0, 0, 0, 0, 0, 0],
 'HL80_rest0':      [0, 0, 0, 0, 0x80, 0x80, 0, 0],      # HL phase 0 mod 128, page differs
 'BC5A_HL0':        [0x5A, 0x5A, 0, 0, 0, 0, 0, 0],      # count nonzero only
 'DE5A_HL0':        [0, 0, 0x5A, 0x5A, 0, 0, 0, 0],      # destination nonzero only
 'A5A_HL0':         [0, 0, 0, 0, 0, 0, 0, 0x5A],         # accumulator only
 'HL80_all5A':      [0x5A, 0x5A, 0x5A, 0x5A, 0x80, 0x80, 0x5A, 0x5A],  # only HL phase-0, everything else 5A
 'CONST5A':         [0x5A] * 8,
 'L01_rest0':       [0, 0, 0, 0, 0, 0x01, 0, 0],         # HL phase 1
}
rows = []
for k, g in enumerate(G):
    R = random.Random(4321 + k); row = {'donor': k}
    for name, regs in PAT.items():
        best = 0
        for side in (0, 1):
            ok = sum(run_side(g, bytes(R.randrange(256) for _ in range(n)), side, list(regs))[0] for _ in range(12))
            best = max(best, ok / 12)
        row[name] = round(best, 2)
    rows.append(row); print(row, flush=True)
summ = {name: sum(r[name] >= 0.5 for r in rows) for name in PAT}
print('competent donors (of 16) per entry pattern:', summ)
json.dump({'rows': rows, 'summary': summ}, open(HERE / 'pattern_screen.json', 'w'), indent=1)
