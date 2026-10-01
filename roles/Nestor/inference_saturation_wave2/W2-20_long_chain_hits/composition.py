"""W2-20 step 4: does S_late plant evolved structure? Byte composition of new hits vs EVO_SD, EVO_SF, old RAND, uniform.

    python -B composition.py -> composition.json
C1 high-nibble histogram: total-variation distance between group-pooled histograms (prefix [0,35) and whole genome).
C2 evolved-enriched bigrams: the 25 bigrams (adjacent byte pairs) most over-represented in EVO_SD+EVO_SF relative to
   uniform expectation (count >= 4); occurrences per genome in each group.
C3 nearest-neighbour Hamming distance from each genome to the closest EVO genome (excluding itself), by group,
   including 2,000 fresh uniform genomes and 2,000 fresh uniform genomes conditioned on S_late's static event.
C4 shared 4-mers: fraction of genomes containing any 4-byte substring also present in some EVO genome.
"""
import collections
import json
import pathlib
import random
import statistics

HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / "lengths.json"))["rows"]
grp = collections.defaultdict(list)
for r in D:
    g = "NEW" if r.get("source") == "W2-20 S_late" else r["group"]
    grp[g].append(bytes.fromhex(r["hex"]))
rng = random.Random(99)


def first_copy(g):
    for i in range(64):
        if g[i] in (0xE5, 0xE7) or (i < 63 and g[i] == 0xED and g[i + 1] in (0xB0, 0xB8)):
            return i
    return None


uni = [bytes(rng.randrange(256) for _ in range(64)) for _ in range(2000)]
late = []
while len(late) < 2000:
    g = bytes(rng.randrange(256) for _ in range(64))
    f = first_copy(g)
    if f is not None and f >= 35:
        late.append(g)
grp["UNIFORM"] = uni
grp["UNIFORM_SLATE"] = late
EVO = grp["EVO_SD"] + grp["EVO_SF"]


def nib(gs, a, b):
    c = collections.Counter(x >> 4 for g in gs for x in g[a:b])
    t = sum(c.values())
    return [c[i] / t for i in range(16)]


def tv(p, q):
    return 0.5 * sum(abs(x - y) for x, y in zip(p, q))


out = {"n": {k: len(v) for k, v in grp.items()}, "C1": {}, "C2": {}, "C3": {}, "C4": {}}
U = [1 / 16] * 16
for k, v in grp.items():
    out["C1"][k] = {"TV_to_uniform_prefix": tv(nib(v, 0, 35), U), "TV_to_uniform_all": tv(nib(v, 0, 64), U),
                    "TV_to_EVO_prefix": tv(nib(v, 0, 35), nib(EVO, 0, 35)), "TV_to_EVO_all": tv(nib(v, 0, 64), nib(EVO, 0, 64))}
bc = collections.Counter(g[i:i + 2] for g in EVO for i in range(63))
exp = len(EVO) * 63 / 65536
top = [b for b, c in sorted(bc.items(), key=lambda kv: -kv[1]) if c >= 4][:25]
out["C2"]["bigrams"] = [b.hex() for b in top]
out["C2"]["evo_count_vs_uniform_expect"] = [[b.hex(), bc[b], round(exp, 3)] for b in top]
for k, v in grp.items():
    out["C2"][k] = sum(1 for g in v for i in range(63) if g[i:i + 2] in set(top)) / len(v)


def ham(a, b):
    return sum(x != y for x, y in zip(a, b))


for k, v in grp.items():
    ds = [min(ham(g, e) for e in EVO if e != g) for g in v[:300]]
    out["C3"][k] = {"median": statistics.median(ds), "min": min(ds), "mean": statistics.mean(ds)}
evo4 = set(g[i:i + 4] for g in EVO for i in range(61))
for k, v in grp.items():
    out["C4"][k] = sum(1 for g in v if any(g[i:i + 4] in evo4 for i in range(61) if g not in EVO)) / len(v)
json.dump(out, open(HERE / "composition.json", "w"), indent=1)
for s in ("n", "C1", "C2", "C3", "C4"):
    print(s, json.dumps({k: v for k, v in out[s].items() if k not in ("bigrams", "evo_count_vs_uniform_expect")}))
print("top bigrams", out["C2"]["evo_count_vs_uniform_expect"][:10])
