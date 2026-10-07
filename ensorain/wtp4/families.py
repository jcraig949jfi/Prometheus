"""WTP-04 founding families (PREREG_WTP04 s2). The 13 WTP-03 founder lineages are read from
runs/wtp03/waveA.json (admitted worlds, `root` = founder lineage). Independence rule, fixed before any
WTP-04 row: two lineages are the SAME family when they share generator class, dims style and
observation kind (the three genes that set what the stream can carry). One representative per family:
the lineage member with the highest WTP-03 information demand (ties: lowest genome hash)."""
import json
import os

RUNS = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp03", "waveA.json")


def dims_style(dims):
    if all(d == 2 for d in dims):
        return "binary"
    if len(dims) <= 3:
        return "few_big"
    return "many_small"


def key(g):
    return (g["substrate"]["gen"], dims_style(g["substrate"]["dims"]), g["observation"]["kind"])


def lineages(path=RUNS):
    adm = json.load(open(path))["admitted"]
    out = {}
    for r in adm:
        out.setdefault(r["root"], []).append(r)
    return out


def families(path=RUNS):
    """-> list of dicts (family id, key, member lineages, representative genome/seed/hash), sorted by key."""
    fam = {}
    for root, rs in lineages(path).items():
        rep = max(rs, key=lambda r: (r["pre"]["demand"], [-ord(ch) for ch in r["h"]]))
        k = key(rep["g"])
        cur = fam.get(k)
        if cur is None:
            fam[k] = dict(key=list(k), lineages=[root], rep=rep)
        else:
            cur["lineages"].append(root)
            if (rep["pre"]["demand"], [-ord(ch) for ch in rep["h"]]) > (cur["rep"]["pre"]["demand"], [-ord(ch) for ch in cur["rep"]["h"]]):
                cur["rep"] = rep
    out = []
    for i, k in enumerate(sorted(fam)):
        f = fam[k]
        r = f["rep"]
        out.append(dict(fid=f"F{i:02d}", key=f["key"], lineages=sorted(f["lineages"]), h=r["h"], wtp03_seed=r["seed"],
                        demand=r["pre"]["demand"], learning_pays_wtp03=r["pre"]["learning_pays"], carrier=r["g"]["memory"]["carrier"],
                        g=r["g"]))
    return out
