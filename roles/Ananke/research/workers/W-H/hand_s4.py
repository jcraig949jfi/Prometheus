"""W-H S4 faafa5b0: H4a/H4b per PLAN ADDENDUM B."""
import sys, json, pathlib, dataclasses
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import torch; torch.set_num_threads(2)
from harness import run, acc
from prometheus.ananke import c1b_run, lens, plants
cid = "faafa5b049e1d4b4"
ph, env, g, row = c1b_run.load(cid)
ph1 = dataclasses.replace(ph, rules=1, setrule=0)
res = {"champion": lens.ci(acc(run(ph, g, env)))}
H4a = [("MULQ", "T0", "SENSE", "SENSE", 0), ("ADDI", "T0", "T0", 0, -100), ("SEL", "T0", "SENSE", "S0", 0),
       ("MOV", "S0", "T0", 0, 0)]
# H4b: slot 11 holds the value; index := cue ? 11 : 10 (slot 10 is a NOP whose immediate is unused)
H4b = [("MULQ", "T0", "SENSE", "SENSE", 0),     # 0: 256 on cue, 16 distractor
       ("ADDI", "T0", "T0", 0, -100),            # 1: >0 iff cue
       ("CONST", "T1", 0, 0, 11),                # 2: 11
       ("CONST", "T2", 0, 0, 10),                # 3: 10
       ("SEL", "T0", "T1", "T2", 0),             # 4: index = cue ? 11 : 10
       ("WIMM", "T3", "T0", "SENSE", 0),         # 5: Kp[index] := SENSE
       ("NOP", 0, 0, 0, 0), ("NOP", 0, 0, 0, 0), ("NOP", 0, 0, 0, 0), ("NOP", 0, 0, 0, 0), ("NOP", 0, 0, 0, 0),
       ("ADDI", "S0", "ZERO", 0, 0)]             # 11: S0 := Kp[11] (pre-program Kp)
for name, lines in (("H4a", H4a), ("H4b", H4b)):
    tr = run(ph1, plants.assemble(ph1, lines)[None], env)
    ym = tr.ep.y == -1
    res[name] = {"acc": lens.ci(acc(tr)), "neg": lens.ci(acc(tr, mask=ym)), "pos": lens.ci(acc(tr, mask=~ym))}
res["A_star"] = res["champion"][1]
print(json.dumps(res, default=float))
pathlib.Path("out/hand_s4.json").write_text(json.dumps(res, indent=1, default=float))
