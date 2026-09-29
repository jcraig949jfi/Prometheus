"""W-B: static disassembly of a champion genome (all rule variants)."""
import sys, pathlib
REPO = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
import numpy as np
from prometheus.ananke import c1b_run, plants
from prometheus.ananke.engine import NOPS

def disasm(ph, g):
    rm = {v: k for k, v in plants.regmap(ph).items()}
    ops = {v: k for k, v in plants.OPS.items()}
    NW, NR = ph.n_write(), ph.n_read()
    out = []
    for r in range(ph.rules):
        out.append(f"--- rule {r}")
        for i in range(ph.prog_len):
            op, d, a, b, imm = [int(x) for x in g[r, i]]
            o = ops[op % NOPS]
            if o == "NOP":
                continue
            out.append(f"{i:2d} {o:8s} {rm.get(d % NW, d % NW):6s} {rm.get(a % NR, a % NR):7s} {rm.get(b % NR, b % NR):7s} imm={imm} bf={b}")
    return "\n".join(out)

if __name__ == "__main__":
    for cid in sys.argv[1:]:
        ph, env, g, row = c1b_run.load(cid)
        print("=====", cid, env.family, {k: getattr(ph, k) for k in ("rules", "setrule", "wimm", "prog_len", "state_dim", "n_sites", "topology", "dest_mode")})
        print(disasm(ph, g))
