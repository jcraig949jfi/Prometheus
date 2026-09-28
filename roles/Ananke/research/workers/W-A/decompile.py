"""Decompile the M2 champions (pre-reduced fields, as engine.World.__init__)."""
import json, pathlib, sys
import numpy as np
REPO = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
from prometheus.ananke import c1b_run, plants
from prometheus.ananke.engine import NOPS

NAMES = {v: k for k, v in plants.OPS.items()}


def decompile(ph, g):
    rm = {v: k for k, v in plants.regmap(ph).items()}
    NW, NR = ph.n_write(), ph.n_read()
    out = []
    for i, (op, d, a, b, imm) in enumerate(np.asarray(g)[0]):
        op, d, a, bb = op % NOPS, d % NW, a % NR, b % NR
        nm = NAMES[op]
        A, B, Dd = rm[a], rm[bb], rm[d]
        if nm == "NOP":
            s = "NOP"
        elif nm == "MOV": s = f"{Dd} := {A}"
        elif nm in ("ADD", "SUB", "MAX", "XOR", "MOD"):
            s = f"{Dd} := {nm}({A}, {B})"
        elif nm == "MULQ": s = f"{Dd} := ({A}*{B})>>8"
        elif nm == "ADDI": s = f"{Dd} := {A} + (imm {imm}+Kp[{i}])"
        elif nm == "CONST": s = f"{Dd} := (imm {imm}+Kp[{i}]) << {b & 7}"
        elif nm == "GT": s = f"{Dd} := 256*({A} > {B})"
        elif nm == "SEL": s = f"{Dd} := {A} if {Dd}>0 else {B}"
        elif nm == "SHR": s = f"{Dd} := {A} >> {b & 15}"
        elif nm == "RAND": s = f"{Dd} := rand(+-|{A}|)"
        elif nm == "SETRULE": s = f"SETRULE({A})"
        elif nm == "WIMM": s = f"WIMM Kp[{A} % L] := {B}"
        out.append(f"{i:2d} {s}")
    return out


if __name__ == "__main__":
    ph, env, g0, _ = c1b_run.load("4ab2ba014aac967e")
    ch = json.loads((REPO / "roles/Ananke/research/spikes/out/champions_m2.json").read_text())
    for k, v in ch.items():
        print("==", k)
        print("\n".join(decompile(ph, np.asarray(v))))
