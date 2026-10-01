"""W2-42 a7: F's one-BYTE absolute-jump neighbourhood (W2-30 t2 scorer): every position p in 0..63 x every
absolute-jump opcode {C3 JP, C2 JPNZ, CA JPZ, D2 JPNC, DA JPC}, F's own following bytes kept as the operand.
Protected copier (W2-30 rule, F/C3 midpoint on this panel): keepF0 >= (0.55 + 0.985)/2 = 0.7675 and max-side
convF >= 0.5. Also reports bit distance F[p] -> opcode and the landing address (F[p+1] & 0x7F).
python -B a7_onebyte_jp.py -> a7_onebyte_jp.json"""
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
THR = (0.55 + 0.985) / 2

if __name__ == "__main__":
    t0 = time.time()
    jobs = {}
    for p in range(64):
        for nm, op in JP.items():
            if F[p] != op:
                jobs[mk(F, {p: op}).hex()] = (p, nm)
    items = sorted(jobs)
    with mp.Pool(5) as pool:
        parts = pool.map(work, [items[i::5] for i in range(5)])
    res = dict(x for p_ in parts for x in p_)
    rows = []
    for h, (p, nm) in jobs.items():
        s = res[h]
        prot = s["keepF0"] >= THR and max(s["convF0"], s["convF1"]) >= 0.5
        rows.append({"pos": p, "op": nm, "bits": bin(F[p] ^ JP[nm]).count("1"), "land": F[(p + 1) % 64] & 0x7F,
                     "protected": prot, **{k: s[k] for k in ("keepF0", "keepF1", "convF0", "convF1", "m_class")}})
    (HERE / "a7_onebyte_jp.json").write_text(json.dumps({"thr": THR, "rows": rows, "wall_s": round(time.time() - t0, 1)}))
    pr = [r for r in rows if r["protected"]]
    print("variants", len(rows), "protected", len(pr), "wall", round(time.time() - t0, 1))
    for r in sorted(pr, key=lambda r: (r["pos"], r["op"])):
        print(r["pos"], r["op"], "bits", r["bits"], "land", r["land"], "k0 %.3f k1 %.3f c1 %.3f m %.3f" % (
            r["keepF0"], r["keepF1"], r["convF1"], r["m_class"]))
