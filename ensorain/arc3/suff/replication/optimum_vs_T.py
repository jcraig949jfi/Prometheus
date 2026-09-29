"""Optimum-k vs T on the Even process, using the Fabric worker's independent implementation (unchanged functions)."""
import ast, pathlib, random
src = (pathlib.Path(__file__).parent / "fabric_worker_suff_replica.py").read_text()
mod = ast.parse(src); keep = [n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.Import)) or
                              (isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "L2" for t in n.targets))]
ns = {}; exec(compile(ast.Module(body=keep, type_ignores=[]), "replica", "exec"), ns)
KS = [0, 1, 2, 3, 4, 6, 8, 10]
for T in (4000, 16000, 64000):
    ex = {k: [] for k in KS}
    for s in range(1, 17):
        xs = ns["gen_even"](random.Random(s), T); b = sum(ns["bayes_even"](xs)) / T
        for k in KS: ex[k].append(sum(ns["stat"](xs, k)) / T - b)
    m = {k: sum(v) / 16 for k, v in ex.items()}
    print("T=%6d " % T + " ".join("k%d:%.4f" % (k, m[k]) for k in KS) + "  argmin=k%d" % min(m, key=m.get))
