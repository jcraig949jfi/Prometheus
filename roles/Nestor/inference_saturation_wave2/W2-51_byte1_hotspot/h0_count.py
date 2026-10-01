"""W2-51 h0: reproduce W2-41's byte-1 count from r1_out; per-position mutation frequency in family interaction rows
(and per distinct (oid, genome) state), byte-1 value spectrum. python -B h0_count.py -> h0_count.json"""
import gzip, json, pathlib, collections, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
R1 = W / "W2-41_carried_context" / "r1_out"
pos_rows = collections.Counter(); pos_states = collections.Counter()
vals = collections.Counter(); n = 0; nb1 = 0; per_run = {}; side_b1 = collections.Counter(); side_n = collections.Counter()
states = set(); imp = None
for p in sorted(R1.glob("*.json.gz")):
    d = json.load(gzip.open(p, "rt")); imp = bytes.fromhex(d["implant"])
    G = [bytes.fromhex(h) for h in d["genomes"]]
    k = 0
    for row in d["rows"]:
        g = G[row[4]]; n += 1; side_n[row[3]] += 1
        for j in range(64):
            if g[j] != imp[j]: pos_rows[j] += 1
        if g[1] != imp[1]:
            nb1 += 1; k += 1; vals["%02x" % g[1]] += 1; side_b1[row[3]] += 1
        key = (d["label"], row[1], row[4])
        if key not in states:
            states.add(key)
            for j in range(64):
                if g[j] != imp[j]: pos_states[j] += 1
    per_run[d["label"]] = [k, len(d["rows"])]
out = {"n_rows": n, "n_b1": nb1, "side_n": side_n, "side_b1": side_b1, "per_run": per_run,
       "b1_values": vals.most_common(), "n_states": len(states),
       "pos_rows": [pos_rows[j] for j in range(64)], "pos_states": [pos_states[j] for j in range(64)]}
(HERE / "h0_count.json").write_text(json.dumps(out, indent=1))
print(n, nb1, dict(side_b1), dict(side_n)); print(vals.most_common(12))
print("rank rows", sorted(range(64), key=lambda j: -pos_rows[j])[:15], [pos_rows[j] for j in sorted(range(64), key=lambda j: -pos_rows[j])[:15]])
print("rank states", sorted(range(64), key=lambda j: -pos_states[j])[:15], [pos_states[j] for j in sorted(range(64), key=lambda j: -pos_states[j])[:15]], len(states))
print(per_run)
