"""Parity: W2-AA tool (scope=window) vs W2-I tool over roles/Ananke .md/.txt; and block vs window deltas."""
import collections, importlib.util, pathlib, sys
ROOT = pathlib.Path("F:/Prometheus-worktrees/ananke-base-role")
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
new = load("ka_new", ROOT / "roles/Ananke/research/harvest/wave2/W2-AA/tools/kind_audit.py")
old = load("ka_old", ROOT / "roles/Ananke/research/harvest/wave2/W2-I/kind_audit.py")
target = ROOT / "roles/Ananke"
o = old.scan(target, old.Resolver(old.load_index()))
idx = new.load_index()
nw = new.audit_paths([target], idx, scope="window")
nb = new.audit_paths([target], idx, scope="block")
def keyed(recs):
    seen, out = collections.Counter(), {}
    for r in recs:
        k = (r["file"], int(r["line"]), r["token"]); seen[k] += 1
        out[k + (seen[k],)] = r["severity"]
    return out
osev, wsev, bsev = keyed(o), keyed(nw), keyed(nb)
print("W2-I citations", len(o), collections.Counter(osev.values()))
print("new window    ", len(nw), collections.Counter(wsev.values()))
print("new block     ", len(nb), collections.Counter(bsev.values()))
only_new = set(wsev) - set(osev); only_old = set(osev) - set(wsev)
print("only in new (window):", len(only_new), "upper/mixed:", sum(k[2] != k[2].lower() for k in only_new))
for k in sorted(only_new): print("   ", k, wsev[k])
print("only in old:", len(only_old), sorted(only_old)[:10])
diff = [(k, osev[k], wsev[k]) for k in set(osev) & set(wsev) if osev[k] != wsev[k]]
print("severity disagreements old vs new-window:", len(diff), diff[:10])
print("block vs window severity changes:")
for k in sorted(bsev):
    if bsev[k] != wsev[k]: print("   ", k, wsev[k], "->", bsev[k])
