"""Mark the void pre-fix KA rows and write the decompiled plant listing (no engine runs)."""
import json, sys
sys.dont_write_bytecode = True
p = "out/ka.json"; d = json.load(open(p))
d["VOID_ROWS"] = ("INT_2/INT_3/INT_3NB rows in this file used the pre-fix relay gate EMIT=cue+CNT0, under which zero "
                  "packets circulate forever and the run tally never resets. They are void; out/ka_mh.json supersedes them.")
json.dump(d, open(p, "w"), indent=1)
import w2m_common as c, w2m_plants as wp
from prometheus.ananke.physics import Physics
ph = Physics(topology="ring", n_sites=64, radius=1, state_dim=3, payload_width=3, prog_len=20)
txt = []
for name, kw in (("INT_CO", None), ("INT_LEAK", None), ("INT_1", dict(lanes=1)), ("INT_1A6", dict(lanes=1, reset="age", k=6)),
                 ("INT_1G", dict(lanes=1, gated=True)), ("INT_2", dict(lanes=2)), ("INT_2A6", dict(lanes=2, reset="age", k=6)),
                 ("INT_3NB", dict(lanes=3, weights=[-2, 1, 1])), ("FIRST", None)):
    g = {"INT_CO": wp.int_co, "INT_LEAK": wp.int_leak, "FIRST": wp.first}[name](ph) if kw is None else wp.member(ph, **kw)[1]
    lines = c.hc.decompile(ph, g[0]); txt.append(f"== {name} ({len(lines)} lines)"); txt += lines
open("out/plants_decompiled.txt", "w").write("\n".join(txt) + "\n")
print("\n".join(txt))
