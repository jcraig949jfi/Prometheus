import json, pathlib
CF = pathlib.Path(r"F:/Prometheus-worktrees/dionysus-base-role/docs/phase3/review/FABLE-5.1/counterfeit")
def load(n): return json.loads((CF / n).read_text(encoding="ascii"))
def shape(x, depth=0, maxd=2, pre=""):
    if isinstance(x, dict):
        for k, v in x.items():
            t = type(v).__name__
            extra = ""
            if isinstance(v, (str, int, float, bool)) or v is None: extra = " = %r" % (v,)
            elif isinstance(v, list): extra = " len %d" % len(v)
            elif isinstance(v, dict): extra = " keys %d" % len(v)
            print("%s%s: %s%s" % (pre, k, t, extra[:200]))
            if depth < maxd and isinstance(v, dict): shape(v, depth + 1, maxd, pre + "    ")
g1 = load("RECEIPT_gauntlet.json")
print("######## RECEIPT_gauntlet.json top"); shape(g1, maxd=0)
print("---- result"); shape(g1["result"], maxd=1)
print("---- v01_verdict full:"); print(json.dumps(g1["result"]["v01_verdict"], indent=1))
for k in g1["result"]:
    if k != "v01_verdict":
        s = json.dumps(g1["result"][k])
        print("---- result[%s]: %s" % (k, s[:1500]))
