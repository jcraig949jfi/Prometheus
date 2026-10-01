"""W2-51 p1: byte-1 provenance from EXISTING replay records only (W2-26 s1_out births+hist; W2-41 r1_out rows).
 A. Per family birth (donor pre-genome dg in 7ae3 family, >=51/64 at shift 0): class of every position j whose
    child final g[j] != dg[j]:
      MUT_BIRTH   xg[j]==dg[j], g[j]!=xg[j]  (_mutate applied to the newborn half)
      RESIDUE     prov[j]==0 (execution never changed byte j; the victim's byte survives)
      VICTIM_W    prov[j]==victim ctx (the overwritten organism's own execution last changed j)
      DONOR_ROT   prov[j]==donor, best circular shift of xg vs dg != 0 (W2-35 rotation/tiling)
      DONOR_PRE   prov[j]==donor, donor's own byte j was changed in place in the SAME interaction to xg[j]
      DONOR_CE1   prov[j]==donor, popcount(xg^dg)==1 at j, cerr_d>0, frame 0 (single-bit copy error)
      DONOR_OTHER prov[j]==donor, anything else (multi-bit write by the donor in frame 0)
 B. In-place events (hist) of tracked orgs whose pre-genome is family: class of each changed position:
      IP_SELF_CE1 (prov==self, single-bit, cerr_self>0), IP_SELF (prov==self, other), IP_PARTNER (prov==other ctx),
      IP_MUTATE (_mutate on the surviving, unrelabelled half). Denominator: family interactions (r1_out rows).
 C. Lineage attribution of every r1 family row with g[1] != 0x21: walk the oid's byte-1 timeline back to the
    event that produced the value (recursing through faithful births into the parent's pre-birth state).
python -B p1_provenance.py -> p1_provenance.json"""
import gzip, json, pathlib, collections, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
S1 = W / "W2-26_switch_source" / "s1_out"
R1 = W / "W2-41_carried_context" / "r1_out"
sys.setrecursionlimit(20000)


def pc(x):
    return bin(x).count("1")


def best_shift(x, d):
    best = (-1, 0)
    for s in range(64):
        m = sum(x[(k + s) % 64] == d[k] for k in range(64))
        if m > best[0]:
            best = (m, s)
    return best[1], best[0]


A_pos = collections.defaultdict(collections.Counter)
A_b1_vals = collections.defaultdict(collections.Counter)
A_n = collections.Counter(); A_n_by_side = collections.Counter(); A_b1_side = collections.Counter()
A_b1_detail = []
B_pos = collections.defaultdict(collections.Counter)
B_b1_events = collections.Counter(); B_b1_loss = collections.Counter(); B_b1_size = collections.defaultdict(list)
B_b1_side = collections.Counter(); B_b1_vals = collections.defaultdict(collections.Counter)
B_b1_footprints = collections.defaultdict(collections.Counter)
B_events_fam = collections.Counter()
C_rows = collections.Counter(); C_rows_run = {}
C_side = collections.defaultdict(collections.Counter)
C_events = collections.Counter()
recon_ok = recon_n = 0
n_family_rows = 0; n_family_rows_by_side = collections.Counter()

for p in sorted(S1.glob("*.json")):
    lab = p.stem
    d = json.loads(p.read_text())
    imp = bytes.fromhex(d["implant"])

    def fam(g):
        return sum(x == y for x, y in zip(g, imp)) >= 51

    births = {int(k): v for k, v in d["births"].items()}
    hist = {int(k): v for k, v in d["hist"].items()}
    # ---- A: births
    bclass = {}
    for c, b in births.items():
        dg, xg, g = bytes.fromhex(b["dg"]), bytes.fromhex(b["xg"]), bytes.fromhex(b["g"])
        prov = bytes.fromhex(b["prov"])
        dside = b["pside"] + 1
        vside = 2 - b["pside"]
        sh = None
        cls_by_pos = {}
        for j in range(64):
            if g[j] == dg[j]:
                continue
            if xg[j] == dg[j]:
                cl = "MUT_BIRTH"
            elif prov[j] == 0:
                cl = "RESIDUE"
            elif prov[j] == vside:
                cl = "VICTIM_W"
            else:
                assert prov[j] == dside
                if sh is None:
                    sh = best_shift(xg, dg)
                pre = [ev for ev in hist.get(b["p"], []) if ev["e"] == b["e"]]
                pre_hit = any(x[0] == j and x[2] == xg[j] for ev in pre for x in ev["ex"])
                if sh[0] != 0:
                    cl = "DONOR_ROT"
                elif pre_hit:
                    cl = "DONOR_PRE"
                elif pc(xg[j] ^ dg[j]) == 1 and b["cerr_d"] > 0:
                    cl = "DONOR_CE1"
                else:
                    cl = "DONOR_OTHER"
            cls_by_pos[j] = cl
        if fam(dg):
            A_n["fam_births"] += 1
            A_n_by_side[b["pside"]] += 1
            for j, cl in cls_by_pos.items():
                A_pos[cl][j] += 1
            if 1 in cls_by_pos:
                cl = cls_by_pos[1]
                A_b1_vals[cl]["%02x>%02x" % (dg[1], g[1])] += 1
                A_b1_side[(cl, b["pside"])] += 1
                A_n["b1_changed"] += 1
                A_n["b1_loss_from_wt" if dg[1] == 0x21 else "b1_change_from_mutant"] += 1
                A_b1_detail.append({"run": lab, "child": c, "e": b["e"], "pside": b["pside"], "cls": cl,
                                    "dg1": "%02x" % dg[1], "xg1": "%02x" % xg[1], "g1": "%02x" % g[1],
                                    "vg1": b["vg"][2:4], "ndiff": len(cls_by_pos),
                                    "shift": None if sh is None else list(sh), "cerr_d": b["cerr_d"],
                                    "cerr_v": b["cerr_v"], "fam_child": fam(g), "causal": b["c"],
                                    "diff_pos": sorted(cls_by_pos)})
        bclass[c] = cls_by_pos.get(1, "FAITHFUL")
    # ---- B: in-place events; per-oid timelines
    timeline, genome_at = {}, {}
    for oid in set(births) | {0}:
        if oid == 0:
            g = bytearray(imp); e0 = -1; tag = ("FOUNDER",)
        else:
            g = bytearray(bytes.fromhex(births[oid]["g"])); e0 = births[oid]["e"]
            tag = ("BIRTH", bclass[oid])
        tl = [(e0, g[1], tag)]
        ga = [(e0, bytes(g))]
        for ev in sorted(hist.get(oid, []), key=lambda v: v["e"]):
            pre = bytes(g)
            side = ev["side"]
            ch = {}
            for j, old, new, pv in ev["ex"]:
                if pv == side + 1:
                    cl = "IP_SELF_CE1" if (pc(old ^ new) == 1 and ev["cerr_self"] > 0) else "IP_SELF"
                else:
                    cl = "IP_PARTNER"
                g[j] = new
                ch[j] = cl
            for j, old, new in ev["mu"]:
                g[j] = new
                ch[j] = "IP_MUTATE"
            if fam(pre):
                B_events_fam["events"] += 1
                for j, cl in ch.items():
                    B_pos[cl][j] += 1
                if 1 in ch:
                    cl = ch[1]
                    B_b1_events[cl] += 1
                    B_b1_side[(cl, side)] += 1
                    B_b1_loss[(cl, "from_wt" if pre[1] == 0x21 else "from_mutant")] += 1
                    B_b1_size[cl].append(len(ch))
                    B_b1_vals[cl]["%02x>%02x" % (pre[1], g[1])] += 1
                    ks = sorted(ch)
                    B_b1_footprints[cl][("n=%d lo=%d hi=%d" % (len(ks), ks[0], ks[-1])) if len(ks) > 4 else str(ks)] += 1
            if g[1] != pre[1]:
                tl.append((ev["e"], g[1], ("INPLACE", ch.get(1, "?"), side)))
            ga.append((ev["e"], bytes(g)))
        timeline[oid] = tl
        genome_at[oid] = ga

    # ---- C: lineage attribution of r1 rows
    r1 = json.load(gzip.open(R1 / (lab + ".json.gz"), "rt"))
    G = [bytes.fromhex(h) for h in r1["genomes"]]
    memo = {}

    def origin(oid, e, val):
        key = (oid, e, val)
        if key in memo:
            return memo[key]
        if oid not in timeline:
            res = ("UNTRACKED_ORG",)
        else:
            cand = [t for t in timeline[oid] if t[0] < e]
            if not cand:
                res = ("NO_STATE",)
            elif cand[-1][1] != val:
                res = ("STATE_MISMATCH",)
            else:
                t = cand[-1]
                if t[2][0] == "FOUNDER":
                    res = ("FOUNDER_WT",)
                elif t[2][0] == "INPLACE":
                    res = ("INPLACE", t[2][1], "side%d" % t[2][2], oid, t[0])
                elif t[2][1] == "FAITHFUL":
                    b = births[oid]
                    res = origin(b["p"], b["e"], bytes.fromhex(b["dg"])[1])
                else:
                    res = ("BIRTH", t[2][1], "side%d" % births[oid]["pside"], oid, t[0])
        memo[key] = res
        return res

    nb = 0
    for row in r1["rows"]:
        e, oid, side, gi = row[0], row[1], row[3], row[4]
        g = G[gi]
        n_family_rows += 1
        n_family_rows_by_side[side] += 1
        if oid in genome_at:
            st = [x for x in genome_at[oid] if x[0] < e]
            recon_n += 1
            recon_ok += bool(st) and st[-1][1] == g
        if g[1] == imp[1]:
            continue
        nb += 1
        o = origin(oid, e, g[1])
        k = o[:3]
        C_rows[k] += 1
        C_side[k][side] += 1
        if len(o) > 3:
            C_events[(lab,) + o] += 1
    C_rows_run[lab] = nb

ev_by_class = collections.Counter()
for k in C_events:
    ev_by_class[k[1:4]] += 1


def ser(c):
    return {("|".join(map(str, k)) if isinstance(k, tuple) else str(k)): v for k, v in c.items()}


out = {
    "A_family_births": A_n["fam_births"], "A_counts": dict(A_n), "A_by_donor_side": dict(A_n_by_side),
    "A_pos_by_class": {cl: [c[j] for j in range(64)] for cl, c in A_pos.items()},
    "A_b1_class": {cl: sum(v.values()) for cl, v in A_b1_vals.items()},
    "A_b1_class_side": ser(A_b1_side),
    "A_b1_vals": {cl: v.most_common(12) for cl, v in A_b1_vals.items()},
    "A_b1_detail": A_b1_detail,
    "B_family_rows": n_family_rows, "B_family_rows_by_side": dict(n_family_rows_by_side),
    "B_family_inplace_events": dict(B_events_fam),
    "B_pos_by_class": {cl: [c[j] for j in range(64)] for cl, c in B_pos.items()},
    "B_b1_events": dict(B_b1_events), "B_b1_side": ser(B_b1_side), "B_b1_loss": ser(B_b1_loss),
    "B_b1_size_hist": {cl: collections.Counter(v).most_common(12) for cl, v in B_b1_size.items()},
    "B_b1_vals": {cl: v.most_common(12) for cl, v in B_b1_vals.items()},
    "B_b1_footprints": {cl: v.most_common(15) for cl, v in B_b1_footprints.items()},
    "C_rows_by_origin": ser(C_rows), "C_rows_by_origin_side": {"|".join(k): dict(v) for k, v in C_side.items()},
    "C_distinct_origin_events_by_class": ser(ev_by_class),
    "C_top_origin_events": [[list(k), v] for k, v in C_events.most_common(25)],
    "C_all_origin_events": [[list(k), v] for k, v in C_events.most_common()],
    "C_rows_run": C_rows_run, "recon_genome_match": [recon_ok, recon_n],
}
(HERE / "p1_provenance.json").write_text(json.dumps(out, indent=1))
for k in ("A_family_births", "A_counts", "A_by_donor_side", "A_b1_class", "A_b1_class_side", "B_family_rows",
          "B_family_inplace_events", "B_b1_events", "B_b1_side", "B_b1_loss", "C_rows_by_origin",
          "C_distinct_origin_events_by_class", "recon_genome_match"):
    print(k, json.dumps(out[k]))
print("A b1 vals", json.dumps(out["A_b1_vals"]))
print("B b1 vals", json.dumps(out["B_b1_vals"]))
print("B fp", json.dumps(out["B_b1_footprints"]))
print("B size", out["B_b1_size_hist"])
print("top events", out["C_top_origin_events"][:15])
