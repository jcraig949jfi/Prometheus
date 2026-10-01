"""W2-51 p2: anatomy of the byte-1 ORIGIN events found by p1 (C). For each distinct origin event (run, oid, epoch):
footprint (positions changed in that event, by class), whether the post-event genome is family, and - if not -
the later event that brought the organism back into the family without restoring byte 1 (its footprint).
Rows (r1 family interactions carrying the mutation) are weighted per event. Also the founder-half byte-1 value vs
the partner's byte-1 / A-register guess is NOT attempted (no register log in s1_out hist).
python -B p2_origin_events.py -> p2_origin_events.json"""
import gzip, json, pathlib, collections, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
S1 = W / "W2-26_switch_source" / "s1_out"
R1 = W / "W2-41_carried_context" / "r1_out"
P1 = json.loads((HERE / "p1_provenance.json").read_text())


def pc(x):
    return bin(x).count("1")


def fp(ks):
    ks = sorted(ks)
    if ks == [1]:
        return "ISO[1]"
    if ks == [0, 1]:
        return "ISO[0,1]"
    if len(ks) <= 6:
        return "SMALL(<=6)"
    if ks[0] >= 1 and ks[0] <= 2 and len(ks) >= 50:
        return "WHOLE_lo>=1"
    if len(ks) >= 50:
        return "WHOLE_lo0"
    return "MID(7-49)"


ev_rows = collections.Counter()
for k, v in P1["C_top_origin_events"]:
    pass
# recompute full event list (p1 kept only top 25): re-derive quickly from p1 logic
res = []
agg_rows = collections.Counter(); agg_ev = collections.Counter()
agg_restore = collections.Counter()
for p in sorted(S1.glob("*.json")):
    lab = p.stem
    d = json.loads(p.read_text())
    imp = bytes.fromhex(d["implant"])

    def fam(g):
        return sum(x == y for x, y in zip(g, imp)) >= 51

    births = {int(k): v for k, v in d["births"].items()}
    hist = {int(k): v for k, v in d["hist"].items()}
    # per oid: sequence of (epoch, pre, post, changed dict)
    seq = {}
    for oid in set(births) | {0}:
        g = bytearray(imp if oid == 0 else bytes.fromhex(births[oid]["g"]))
        L = []
        for ev in sorted(hist.get(oid, []), key=lambda v: v["e"]):
            pre = bytes(g); ch = {}
            for j, old, new, pv in ev["ex"]:
                g[j] = new; ch[j] = "S" if pv == ev["side"] + 1 else "P"
            for j, old, new in ev["mu"]:
                g[j] = new; ch[j] = "M"
            L.append((ev["e"], pre, bytes(g), ch, ev["side"], ev["cerr_self"]))
        seq[oid] = L
    r1 = json.load(gzip.open(R1 / (lab + ".json.gz"), "rt"))
    G = [bytes.fromhex(h) for h in r1["genomes"]]
    # rows with b1 mutated, for in-place origin events: find the event = last in-place change of byte 1 before row,
    # recursing through faithful births is done in p1; here only INPLACE-origin rows of tracked orgs whose own
    # timeline holds the change (child-inherited rows are attributed to the ancestor event in p1 and counted there).
    for row in r1["rows"]:
        e, oid, side, gi = row[0], row[1], row[3], row[4]
        g = G[gi]
        if g[1] == imp[1] or oid not in seq:
            continue
        evs = [x for x in seq[oid] if x[0] < e and 1 in x[3]]
        if not evs:
            continue
        x = evs[-1]
        if x[2][1] != g[1]:
            continue
        key = (lab, oid, x[0])
        agg_rows[(fp(x[3]), fam(x[2]))] += 1
        if key not in {r["key"] for r in res[-50:]} and not any(r["key"] == key for r in res):
            # first sighting of this event: describe it and any family-restoring later event
            restore = None
            if not fam(x[2]):
                for y in seq[oid]:
                    if y[0] > x[0] and y[0] < e and fam(y[2]) and not fam(y[1]):
                        ks = sorted(y[3])
                        restore = {"e": y[0], "n": len(ks), "lo": ks[0], "hi": ks[-1], "touch1": 1 in y[3],
                                   "actor": collections.Counter(y[3].values()).most_common(1)[0][0]}
                        break
            ks = sorted(x[3])
            r_ = {"key": key, "run": lab, "oid": oid, "e": x[0], "side": x[4], "fp": fp(x[3]), "n": len(ks),
                  "lo": ks[0], "hi": ks[-1], "b1_actor": x[3][1], "b1": "%02x>%02x" % (x[1][1], x[2][1]),
                  "post_family": fam(x[2]), "match_post": sum(a == b for a, b in zip(x[2], imp)),
                  "restore": restore, "rows": 0}
            res.append(r_)
            agg_ev[(r_["fp"], r_["post_family"], r_["b1_actor"])] += 1
            if restore:
                agg_restore[(restore["lo"], restore["hi"], restore["touch1"], restore["actor"])] += 1
        for r_ in res:
            if r_["key"] == key:
                r_["rows"] += 1
                break
out = {"events": [dict(r, key=list(r["key"])) for r in res],
       "rows_by_fp_postfam": {"%s|%s" % k: v for k, v in agg_rows.items()},
       "events_by_fp_postfam_actor": {"%s|%s|%s" % k: v for k, v in agg_ev.most_common()},
       "restore_events": {"%s|%s|%s|%s" % k: v for k, v in agg_restore.most_common()}}
(HERE / "p2_origin_events.json").write_text(json.dumps(out, indent=1))
print("events", len(res), "rows", sum(r["rows"] for r in res))
print(out["rows_by_fp_postfam"])
print(out["events_by_fp_postfam_actor"])
print(out["restore_events"])
for r in sorted(res, key=lambda r: -r["rows"])[:15]:
    print(r)
