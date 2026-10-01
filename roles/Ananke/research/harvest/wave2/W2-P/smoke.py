from w2p_common import *
R = [r for r in hc.rows() if r["kind"] == "evolve" and r["env"]["family"] == "MAJ" and r["physics"]["topology"] in ("random", "smallworld")]
r = R[0]; ph, env, g = load(r)
ck = Clock()
o = hc.evaluate(ph, g, env, held_seeds(r))
print(r["cell_id"], r["result"]["held"], {k: o[k] for k in ("acc", "lo99", "hi99")}, ck.done())
