"""Step 6 (adversarial check on external validity): CVT-R's partner is uniform random bytes. Replace it with
realistic partners from the same cell: (KIN) the copier itself, (S0COP) each side-0-certified DENSE donor of the same
cell in ROWS (up to 20). One interaction each, world order, cmr 0. Outcome for the side-1 copier G at side 1:
  G_CHILD   the side-0 half ends >= 0.9 identical to G (G reproduced)
  G_LOST    G's own half ends < 0.9 identical to G
Also G placed at side 0 against the same partners (its wrong side)."""
import json, pathlib, collections
from _env import A, ROWS
from s4_order_and_interference import interact2
import p11

side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
s0cop = [r for r in ROWS if r["P11"]["certified_sides"] == [0] and r["vm"] == "DENSE"]
out = []
agg = collections.Counter()
for r in side1:
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"]); n = P["n"]
    parts = [("KIN", G)] + [("S0COP", bytes.fromhex(x["hex"])) for x in s0cop if x["cell"] == r["cell"]][:20]
    c = collections.Counter()
    for kind, Q in parts:
        t, prov, _, _ = interact2(z, P, Q, G, (0, 1))          # G at side 1
        child_ok = p11.fidelity(G, bytes(t[0:n])) >= 0.9
        lost = p11.fidelity(G, bytes(t[n:2 * n])) < 0.9
        part_child = p11.fidelity(Q, bytes(t[n:2 * n])) >= 0.9
        c[kind + "_s1_n"] += 1; c[kind + "_s1_G_CHILD"] += child_ok; c[kind + "_s1_G_LOST"] += lost
        c[kind + "_s1_partner_copied_over_G"] += part_child
        t, _, _, _ = interact2(z, P, G, Q, (0, 1))             # G at side 0
        c[kind + "_s0_n"] += 1
        c[kind + "_s0_G_CHILD"] += p11.fidelity(G, bytes(t[n:2 * n])) >= 0.9
        c[kind + "_s0_G_LOST"] += p11.fidelity(G, bytes(t[0:n])) < 0.9
    out.append({"key": r["key"], "cell": r["cell"], **c}); agg.update(c)
    print(r["key"], dict(c))
print(dict(agg))
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps({"aggregate": dict(agg), "genomes": out}, indent=1))
