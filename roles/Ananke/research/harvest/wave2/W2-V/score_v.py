"""Fresh scoring on W2VS worlds (64 = 32 mirror pairs) + must-fail (sensor-2 cue zeroed, 64 worlds), STRICT genome.
usage: python score_v.py tag   (reads the candidate list from CANDS in this file)"""
import sys
from v_common import *
import sbf
import sbnor
import sb8

CANDS = {
    "4222_sbf_c800": ("4222a5f7", lambda ph: sbf.sbf(100, 3)),
    "4222_sbf_c400": ("4222a5f7", lambda ph: sbf.sbf(100, 2)),
    "48256f59_sbnor": ("48256f59", lambda ph: sbnor.sbnor(80, 0, 1)),
    "1974a9cf_sbnor": ("1974a9cf", lambda ph: sbnor.sbnor(80, 0, 1)),
    "333d6b2b_sbnor": ("333d6b2b", lambda ph: sbnor.sbnor(80, 0, 1)),
    "48256f59_sb8": ("48256f59", lambda ph: sb8.sb8("pay")),
    "1974a9cf_sb8": ("1974a9cf", lambda ph: sb8.sb8("pay")),
    "333d6b2b_sb8": ("333d6b2b", lambda ph: sb8.sb8("pay")),
}

def score(names, tag):
    ck = Clock()
    seeds = assays.world_seeds(V_NS, 64)
    out = {}
    for name in names:
        c8, fn = CANDS[name]
        ph, env = row_phys(c8)
        lines = fn(ph)
        g = asm(ph, lines)                       # asserts len(lines) <= row prog_len: NO override
        acc, st = veval(ph, g[None], env, seeds)
        mf, _ = veval(ph, g[None], env, seeds, sched_fn=zero_s2)
        rec = {"cell": c8, "len": len(lines), "prog_len": ph.prog_len, "strict": True,
               "program": hc.decompile(ph, g[0]), "normal": summarize(acc[0]), "mf_s2_zeroed": summarize(mf[0]),
               "stats": {k: int(v[0]) for k, v in st.items()}}
        out[name] = rec
        print(name, rec["len"], "/", rec["prog_len"], rec["normal"], "mf", rec["mf_s2_zeroed"]["acc"], ck.cpu(), flush=True)
    save(f"score_{tag}.json", {"rows": out, "ns": hex(V_NS), "M": 64, "cpu_s": ck.cpu()})

if __name__ == "__main__":
    tag = sys.argv[1]
    names = sys.argv[2:] or list(CANDS)
    score(names, tag)
