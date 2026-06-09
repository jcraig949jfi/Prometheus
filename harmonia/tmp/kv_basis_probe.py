"""Introspect _native_kill_vector_pilot.json structure (phase 1).

Audit question: is the KillVector basis effectively multi-dimensional, or
rank-1-but-continuous? Phase 1 just maps the JSON shape so phase 2 can pull
a per-record component-margin matrix.
"""
import json, os, sys

p = r"D:\Prometheus\prometheus_math\_native_kill_vector_pilot.json"
print("size_bytes:", os.path.getsize(p))
with open(p, "r", encoding="utf-8") as f:
    d = json.load(f)

def shape(x, depth=0, maxd=3):
    ind = "  " * depth
    if isinstance(x, dict):
        print(f"{ind}dict[{len(x)}] keys: {list(x.keys())[:20]}")
        if depth < maxd:
            for k in list(x.keys())[:8]:
                print(f"{ind}.{k}:")
                shape(x[k], depth + 1, maxd)
    elif isinstance(x, list):
        print(f"{ind}list[{len(x)}]")
        if x and depth < maxd:
            print(f"{ind}[0]:")
            shape(x[0], depth + 1, maxd)
    else:
        s = repr(x)
        print(f"{ind}{type(x).__name__}: {s[:120]}")

shape(d)

# Hunt for a per-record list carrying kill-vector component data.
def find_record_lists(x, path="root"):
    hits = []
    if isinstance(x, dict):
        for k, v in x.items():
            hits += find_record_lists(v, f"{path}.{k}")
    elif isinstance(x, list) and x and isinstance(x[0], dict):
        keys = set(x[0].keys())
        if keys & {"kill_vector", "components", "margins", "kv", "killvector"}:
            hits.append((path, len(x), sorted(keys)[:25]))
    return hits

print("\n=== candidate per-record lists with KV-ish keys ===")
for path, n, keys in find_record_lists(d):
    print(f"  {path}  n={n}  keys={keys}")
