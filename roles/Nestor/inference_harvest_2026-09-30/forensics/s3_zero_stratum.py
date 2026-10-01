"""s3 step 6 (post hoc, descriptive): pairs whose BOTH single knockouts kept function in 3/3 draws (null = 0), i.e.
strict synthetic lethals. Per-group rate, class pairs, distance, genome spread, examples. -> s3_zero_stratum.json"""
import collections, json
d = json.load(open("s3_pairs.json")); sg = json.load(open("s3_singles.json"))
out = {}
for grp in ("panel", "comparators"):
    ref = {g["idx"]: g for g in sg[grp]}
    n = l = 0; cls = collections.Counter(); dist = collections.Counter(); per = []; ex = []
    cls_all = collections.Counter()
    for r in d[grp]:
        p = ref[r["idx"]]["p"]; a = r["ann"]; gn = gl = 0
        for i, j, le, c, nu in r["pairs"]:
            if p[str(i)] or p[str(j)]:
                continue
            n += 1; gn += 1
            k = " + ".join(sorted((a[str(i)]["cls"], a[str(j)]["cls"]))); cls_all[k] += 1
            if le and c:
                l += 1; gl += 1; cls[k] += 1
                dd = min(j - i, 64 - (j - i)); dist["1" if dd == 1 else "2-3" if dd <= 3 else ">=4"] += 1
                if len(ex) < 12:
                    ex.append({"genome": r["idx"], "i": i, "j": j, "i_ann": a[str(i)], "j_ann": a[str(j)]})
        per.append((gl, gn))
    out[grp] = {"pairs": n, "lethal": l, "rate": round(l / n, 4), "genomes_with_any": sum(x[0] > 0 for x in per),
                "max_per_genome": max(x[0] for x in per), "class_pairs_lethal": dict(cls.most_common(8)),
                "class_pair_rate": {k: round(cls[k] / cls_all[k], 3) for k, _ in cls_all.most_common(6)},
                "distance_lethal": dict(dist), "examples": ex}
json.dump(out, open("s3_zero_stratum.json", "w"), indent=1)
for g in out:
    print(g, {k: v for k, v in out[g].items() if k != "examples"})
for e in out["panel"]["examples"][:8]:
    print(e)
