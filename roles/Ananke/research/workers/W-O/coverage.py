"""Which inventory groups still lack a successful SINGLE record."""
import glob, json, audit
keys, g = audit.groups()
done = set()
for f in glob.glob(str(audit.OUT / "rerun_s*.jsonl")):
    for l in open(f):
        if l.strip():
            x = json.loads(l)
            if "error" not in x:
                done.add(tuple(x["group"]))
miss = [k for k in keys if tuple(k) not in done]
print(len(keys), "done", len(done), "missing", len(miss))
for k in miss:
    print(keys.index(k) % 8, k)
