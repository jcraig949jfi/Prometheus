"""Step 6: per-copier tables (all 17 side-1, a matched side-0 sample of 17: same subset and cell, drawn with
random.Random('W2-21-match')), and a soundness check: every s11 empirical register dependency must appear in the
taint (data or control) set of the child copy op."""
import json, pathlib, random, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
s1 = json.loads((HERE / "s1_operand_taint.json").read_text())
s2 = json.loads((HERE / "s2_fragility_decomposition.json").read_text())["per_genome"]
s11 = json.loads((HERE.parent / "W2-16_side1_heredity" / "s11_register_dependency_set.json").read_text())


def short(x):
    return x.replace("INHERITED", "INH")


def row(s, k):
    v = s1["side%d" % s][k]; g = s2[k]
    return {"key": k, "op": v["op"], "geom": "%d->%d" % (v["src"], v["dst"]), "BC": v["BC"],
            "src": short(v["src_from"]), "dst": short(v["dst_from"]), "cnt": short(v["cnt_from"]),
            "ctrl_inh": "".join(x for x in g["ctrl_inherited"]), "s11_deps": s11["side%d" % s]["per_genome"][k],
            "randregs_of_30": g["all_random_good"], "opd_regs_fresh_rest_random": g["non_opd_random_good"],
            "n_inh_operands": sum(v[o + "_from"].startswith("INH") for o in ("src", "dst", "cnt"))}


rows1 = [row(1, k) for k in s1["side1"]]
rng = random.Random("W2-21-match")
pool = [k for k, v in s1["side0"].items() if v.get("op")]
rows0 = []
used = set()
for k in s1["side1"]:
    sub = k.split(":")[1]
    cands = [c for c in pool if c.split(":")[1] == sub and c not in used]
    c = rng.choice(sorted(cands)); used.add(c); rows0.append(row(0, c))
# soundness
viol = []
for s in (0, 1):
    for k, deps in s11["side%d" % s]["per_genome"].items():
        if k not in s2:
            continue
        allowed = set(s2[k]["data_inherited"]) | set(s2[k]["ctrl_inherited"])
        miss = [d for d in deps if d not in allowed]
        if miss:
            viol.append((k, deps, sorted(allowed)))
# set-a vs q1 side split
sub = collections.Counter()
for s in (0, 1):
    for k in s1["side%d" % s]:
        sub[(k.split(":")[1], s)] += 1
out = {"side1": rows1, "side0_matched": rows0, "soundness_violations": viol,
       "subset_by_side": {"%s|side%d" % k: n for k, n in sorted(sub.items())}}
for name, rows in (("SIDE 1", rows1), ("SIDE 0 matched", rows0)):
    print(name)
    for r in rows:
        print(" | ".join(str(r[c]) for c in ("key", "op", "geom", "src", "dst", "cnt", "ctrl_inh", "s11_deps",
                                              "n_inh_operands", "randregs_of_30", "opd_regs_fresh_rest_random")))
    print("mean inherited operands", sum(r["n_inh_operands"] for r in rows) / len(rows),
          "randregs", sum(r["randregs_of_30"] for r in rows), "/", 30 * len(rows))
print("soundness violations", viol)
print(out["subset_by_side"])
(HERE / "s6_tables.json").write_text(json.dumps(out, indent=1))
