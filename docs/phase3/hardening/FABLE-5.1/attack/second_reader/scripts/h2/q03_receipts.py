import json, pathlib
CF = pathlib.Path(r"F:/Prometheus-worktrees/dionysus-base-role/docs/phase3/review/FABLE-5.1/counterfeit")
def load(n): return json.loads((CF / n).read_text(encoding="ascii"))
for name in ("RECEIPT_gauntlet2.json", "RECEIPT_gauntlet3.json"):
    d = load(name)
    print("########", name, "top keys:", {k: (type(v).__name__, (v if isinstance(v, (str, int, float, bool)) else len(v))) for k, v in d.items()})
    print("params:", json.dumps(d.get("params"))[:1500])
    print("expected:", json.dumps(d.get("expected"))[:800])
    for c, v in d["cells"].items():
        print("  cell %-14s verdict %-5s keys %s" % (c, v.get("verdict"), sorted(k for k in v if k not in ("replicates",))))
        print("       counts:", json.dumps(v.get("counts")))
        print("       conj/other:", {k: v[k] for k in v if k not in ("replicates", "counts", "medians", "verdict")} if len(json.dumps({k: v[k] for k in v if k not in ("replicates", "counts", "medians", "verdict")})) < 600 else "(long)")
        print("       medians:", json.dumps(v.get("medians"))[:700])
    for k in d:
        if k not in ("cells", "params", "expected"):
            s = json.dumps(d[k]); print("  top[%s] = %s" % (k, s[:600]))
k = load("RECEIPT_keys.json")
print("######## RECEIPT_keys.json top keys:", list(k))
for kk, v in k.items():
    s = json.dumps(v)
    print("  [%s] %s" % (kk, s[:3000]))
