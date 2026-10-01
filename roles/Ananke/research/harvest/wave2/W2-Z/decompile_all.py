import sys; sys.path.insert(0, '.')
import wz_common as wz, plants_wz as pw
np = wz.np
ph = wz.Physics(topology="ring", n_sites=64, radius=1, state_dim=4, payload_width=1, channels=1, prog_len=29, rules=2, setrule=1)
sys.path.insert(0, '.')
import importlib.util as u
sp = u.spec_from_file_location("rm", "run_maj.py")
txt = []
def show(name, lines):
    b = pw.A(ph, lines)
    d = wz.hc.decompile(ph, b)
    txt.append(f"== {name} ({len(d)} non-NOP lines)\n" + "\n".join(d))
show("RELAY rule, stateless attenuating relay + teacher dispatch (FLIP two-rule; k=5, m=0)", pw.relay_att(1) + pw.DISPATCH)
show("RELAY rule, dedup relay (relay_flood semantics) + dispatch (k=11, m=1)", pw.relay_dedup() + pw.DISPATCH)
show("ACTUATOR rule v3 (FLIP; never emits; free under the economy)", pw.flip_actuator_v3())
MEM = {
 "LEAK3": [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0), ("ADD", "S0", "S0", "IN0_0", 0)],
 "LEAK4s1": [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0), ("SHR", "T0", "S0", 1, 0), ("ADD", "S0", "T0", "IN0_0", 0)],
 "LEAK4s2": [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0), ("SHR", "T0", "S0", 2, 0), ("ADD", "S0", "T0", "IN0_0", 0)],
 "LEAK5": [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0), ("SHR", "T0", "S0", 2, 0), ("SUB", "S0", "S0", "T0", 0), ("ADD", "S0", "S0", "IN0_0", 0)]}
for k, v in MEM.items():
    show(f"MAJ {k} (homogeneous, all rules)", v)
(wz.OUT / "plants_decompiled.txt").write_text("\n\n".join(txt) + "\n")
print("\n\n".join(txt))
