"""W2-42 a6: designed static scan of the 'JP-to-own-operand' ejector class on the founder F (W2-30 t2 scorer).
Hypothesis from a2/a3: C3@43 (JP 22EC -> 108), s1438's JPNC@32 (-> 97) and s1505's JPNZ@18 (-> 83) all jump to
absolute p+65 (mod 128): from side 1 that is the jump's own operand byte (execution continues), from side 0 it
throws any runner into the other half before it reaches the LDIR at 52.
Sets:
  nat   : p in {8,20,32,43,50} (F[p+1] & 0x7F == p+65 already) x opcode in {C3,C2,CA,D2,DA}   (1 byte change)
  forced: every p in 0..51, byte p = C3, byte p+1 = (p+65) | hi, hi in {0x00, 0x80}            (<= 2 byte change)
  off   : control, every p in 0..51, byte p = C3, byte p+1 = (p+66) & 0x7F | 0x80 (lands one byte later)
  s1505 : F + 18=C2,19=D3 ; F + 18=C3,19=D3
python -B a6_jp_scan.py -> a6_jp_scan.json"""
import json, sys, pathlib, time
import multiprocessing as mp
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "W2-35_rotation_leak"))
from a2_assay import work, mk  # noqa
import frames  # noqa
F = frames.IMP
JP = {"C3": 0xC3, "C2": 0xC2, "CA": 0xCA, "D2": 0xD2, "DA": 0xDA}

if __name__ == "__main__":
    t0 = time.time()
    jobs = {}

    def add(lab, g):
        jobs.setdefault(g.hex(), []).append(lab)
    add("F", F)
    nat = [p for p in range(63) if (F[p + 1] & 0x7F) == p + 65]
    for p in nat:
        for nm, op in JP.items():
            add("nat|%d|%s" % (p, nm), mk(F, {p: op}))
    for p in range(52):
        for hi in (0x00, 0x80):
            add("forced|%d|hi%02x" % (p, hi), mk(F, {p: 0xC3, p + 1: ((p + 65) & 0x7F) | hi}))
        add("off|%d" % p, mk(F, {p: 0xC3, p + 1: ((p + 66) & 0x7F) | 0x80}))
    add("s1505|18=C2,19=D3", mk(F, {18: 0xC2, 19: 0xD3}))
    add("s1505|18=C3,19=D3", mk(F, {18: 0xC3, 19: 0xD3}))
    items = sorted(jobs)
    with mp.Pool(5) as pool:
        parts = pool.map(work, [items[i::5] for i in range(5)])
    res = dict(x for p in parts for x in p)
    rows = [{"label": lab, "hex": h, **res[h]} for h, labs in jobs.items() for lab in labs]
    (HERE / "a6_jp_scan.json").write_text(json.dumps({"nat_sites": nat, "rows": rows, "wall_s": round(time.time() - t0, 1)}))
    print("nat", nat, "unique", len(items), "wall", round(time.time() - t0, 1))
