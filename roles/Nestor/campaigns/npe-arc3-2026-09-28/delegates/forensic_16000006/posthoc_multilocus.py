"""POST-HOC (not pre-registered; run after causal.py returned KILLED). Is robustness a multi-locus property?
Knock the full epoch-700 consensus (paths700.json consensus_vs_d0, 20 positions) into D0 genome #2 (the modal D0),
then leave-one-out over the consensus positions, and the LD DE triplet alone for reference. Same measure() as
causal.py but tag 'F16-POSTHOC'. Writes posthoc_multilocus.json."""
import json
import pathlib

import causal as C

C.TAG = "F16-POSTHOC"
HERE = pathlib.Path(__file__).resolve().parent
G = json.loads((HERE / "genealogy.json").read_text())
P7 = json.loads((HERE / "paths700.json").read_text())
d0 = bytes.fromhex(G["d0_genomes"][2])
cons = {i: int(b, 16) for i, b, _, _ in P7["consensus_vs_d0"]}
rows = []
full = C.patch(d0, cons)
m = C.measure(full)
C.show("ALL", full, m)
rows.append({"variant": "D0+consensus_all", "hex": full.hex(), "m": m})
for i in sorted(cons):
    d = dict(cons)
    del d[i]
    g = C.patch(d0, d)
    m = C.measure(g)
    C.show("-%d" % i, g, m)
    rows.append({"variant": "D0+consensus_minus_%d" % i, "hex": g.hex(), "m": m})
(HERE / "posthoc_multilocus.json").write_text(json.dumps(rows, indent=1))
