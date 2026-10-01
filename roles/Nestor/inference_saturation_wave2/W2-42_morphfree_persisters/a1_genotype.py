"""W2-42 a1: genotype the causal lineage of the three replays (r1_*.json). Static, no sims.
Per genome: diffs vs 7ae3 (IMP), W2-35 frame, core diffs (copier bytes 23..53), bytes 43/44/45/49.
Per run: births by donor genotype class and by epoch window; dominant live genotypes per epoch window;
realized per-side keep / conversion of lineage members by genotype class (from 'minter')."""
import json, sys, pathlib, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-35_rotation_leak"))
import frames  # noqa
IMP = frames.IMP
CORE = range(23, 54)


def fid(a, b):
    return sum(x == y for x, y in zip(a, b)) / 64


def desc(g):
    s, c, c0 = frames.frame(g)
    d = [i for i in range(64) if g[i] != IMP[i]]
    core = [i for i in d if i in CORE]
    return {"frame": s, "frame_match": c, "n_diff": len(d), "core_diff": ["%d:%02x>%02x" % (i, IMP[i], g[i]) for i in core],
            "b43_44_45_49": "%02x%02x%02x%02x" % (g[43], g[44], g[45], g[49]),
            "edge_diff": ["%d:%02x>%02x" % (i, IMP[i], g[i]) for i in d if i not in CORE]}


def cls(g):
    s, c, c0 = frames.frame(g)
    if s != 0 and c >= 16:
        return "ROT%d" % s
    if c0 < 32:
        return "FOREIGN"
    core = tuple(i for i in CORE if g[i] != IMP[i])
    if g[43] == 0xC3:
        return "C3" + ("" if len(core) == 1 else "+core%d" % (len(core) - 1))
    if not core:
        return "Fcore" if g != IMP else "F"
    return "core:" + ",".join("%d=%02x" % (i, g[i]) for i in core)


def main():
    out = {}
    for name in ("FULL_1438", "FULL_1469", "BANK_1505"):
        X = json.loads((HERE / ("r1_%s.json" % name)).read_text())
        gs = [bytes.fromhex(h) for h in X["gid"]]
        C = [cls(g) for g in gs]
        B = X["births"]
        R = {"out": X["out"]}
        # births by donor class (donor pre genome) and child class
        R["births_by_donor_class"] = collections.Counter(C[b[4]] for b in B).most_common(25)
        R["births_by_child_class"] = collections.Counter(C[b[5]] for b in B).most_common(25)
        R["bxk_by_donor_class"] = collections.Counter(C[b[4]] for b in B if b[6] != 0).most_common(25)
        R["births_by_donor_side"] = collections.Counter(b[3] for b in B)
        R["bxk_by_donor_side"] = collections.Counter(b[3] for b in B if b[6] != 0)
        # time course: per 5-epoch window, births by donor class + snapshot composition
        tc = []
        snaps = {s[0]: s for s in X["snaps"]}
        E = X["out"]["epochs"]
        for w0 in range(0, E, 5):
            bw = [b for b in B if w0 <= b[0] < w0 + 5]
            sn = snaps[min(w0 + 4, E - 1)]
            comp = collections.Counter()
            for k, v in sn[3].items():
                comp[C[int(k)]] += v
            tc.append({"ep": "%d-%d" % (w0, w0 + 4), "births": len(bw), "bxk": sum(b[6] != 0 for b in bw),
                       "donor_classes": collections.Counter(C[b[4]] for b in bw).most_common(4),
                       "A": sn[1], "N": sn[2], "live_lineage_classes": comp.most_common(4)})
        R["timecourse"] = tc
        # dominant genomes (by births as donor) with descriptions
        dc = collections.Counter(b[4] for b in B)
        R["top_donor_genomes"] = [{"gid": k, "donor_births": v, "bxk": sum(1 for b in B if b[4] == k and b[6] != 0),
                                   "cls": C[k], **desc(gs[k])} for k, v in dc.most_common(12)]
        # realized per-side keep/conv for lineage members by class: kept = same oid and FID(post,pre)>=0.9
        st = collections.defaultdict(lambda: [0, 0, 0, 0, 0])   # n, kept, converted partner (non-kin), lost_to_overwrite, partner_bg
        for m in X["minter"]:
            ep, s, oid, pre, post, chg, anc, ppre, panc, pinl, ppost, pconv = m
            key = (C[pre], s)
            v = st[key]
            v[0] += 1
            v[1] += (not chg) and fid(gs[pre], gs[post]) >= 0.9
            v[2] += bool(pconv) and panc != 0
            v[3] += bool(chg)
            v[4] += panc != 0
        R["realized_by_class_side"] = sorted([[k[0], k[1], v[0], round(v[1] / v[0], 3),
                                               round(v[2] / max(v[4], 1), 3), v[4], v[3]] for k, v in st.items()],
                                             key=lambda x: -x[2])[:30]
        # lineage-founding path: ancestry of the top donor genome back to founder (class of each ancestor)
        par = {c: (p, e) for c, p, e in X["causal_edges"]}
        bchild = {b[1]: b for b in B}
        top = R["top_donor_genomes"][0]["gid"]
        oid = next(b[1] for b in B if b[5] == top)
        path = []
        while oid in par:
            b = bchild.get(oid)
            path.append([oid, par[oid][1], None if b is None else C[b[5]], None if b is None else b[3]])
            oid = par[oid][0]
        R["ancestry_of_first_top_genome"] = path[::-1]
        out[name] = R
    (HERE / "a1_genotype.json").write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
