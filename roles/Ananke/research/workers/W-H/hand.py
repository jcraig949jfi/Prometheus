"""W-H Part 2 (H): hand-compiled rules=1 programs of the champion's L. CPU."""
import sys, json, pathlib, dataclasses
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np, torch
torch.set_num_threads(2)
from harness import run, acc
from prometheus.ananke import c1b_run, lens, plants

OUT = pathlib.Path(__file__).parent / "out"
H1 = [("MAX", "EMIT", "SENSE", "ZERO", 0), ("CONST", "PAY0", 0, 7, 90), ("MOV", "T0", "CNT0", 0, 0),
      ("CONST", "T1", 0, 3, 97), ("ADDI", "T2", "S0", 0, -60), ("SEL", "T0", "T1", "T2", 0), ("MOV", "S0", "T0", 0, 0)]
H2 = [("MULQ", "T0", "SENSE", "SENSE", 0), ("ADDI", "T0", "T0", 0, -100), ("SEL", "T0", "SENSE", "S0", 0),
      ("MOV", "S0", "T0", 0, 0)]
H3 = [("MOV", "EMIT", "S1", 0, 0), ("CONST", "PAY0", 0, 7, 1), ("MAX", "T0", "SENSE", "ZERO", 0),
      ("GT", "T1", "CNT0", "ZERO", 0), ("ADD", "T2", "T0", "T1", 0), ("MOV", "T3", "S1", 0, 0),
      ("SEL", "T3", "ZERO", "T2", 0), ("MOV", "S1", "T3", 0, 0), ("MOV", "S0", "CNT0", 0, 0)]
PLAN = {"b59e6c3afebce00a": [("H1", H1)], "311c465fd5a624cb": [("H2", H2)],
        "95649e2c29e72d45": [("H3", H3), ("H3alt_H1", H1)]}
A_STAR = {"b59e6c3afebce00a": .707, "311c465fd5a624cb": .715, "95649e2c29e72d45": .648}

if __name__ == "__main__":
    res = {}
    for cid, progs in PLAN.items():
        ph, env, g, row = c1b_run.load(cid)
        ph1 = dataclasses.replace(ph, rules=1, setrule=0)
        for name, lines in progs:
            gen = plants.assemble(ph1, lines)[None]
            tr = run(ph1, gen, env)
            c = lens.ci(acc(tr))
            res[f"{cid[:8]}/{name}"] = {"acc": c, "A_star": A_STAR[cid], "reaches": c[0] >= A_STAR[cid],
                                        "n_instr": len(lines), "L": ph.prog_len}
            print(cid[:8], name, [round(x, 3) for x in c], "A*", A_STAR[cid], flush=True)
    (OUT / "hand.json").write_text(json.dumps(res, indent=1, default=float))
