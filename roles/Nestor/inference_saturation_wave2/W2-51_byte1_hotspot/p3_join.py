"""W2-51 p3: join p1's lineage-origin events (every r1 byte-1-mutant row -> the event that produced its byte-1
value) with the recorded footprint (s1_out hist / births) and t2's re-executed writer instruction.
Tables: rows and distinct events by (origin class, footprint class, writer instruction).
python -B p3_join.py -> p3_join.json"""
import json, pathlib, collections, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
S1 = W / "W2-26_switch_source" / "s1_out"
P1 = json.loads((HERE / "p1_provenance.json").read_text())
T2 = json.loads((HERE / "t2_reexec.json").read_text())
t2 = {}
for r in T2["rows"]:
    t2[(r["run"], r["kind"], r["oid"], r["e"])] = r
det = {(x["run"], x["child"]): x for x in P1["A_b1_detail"]}
cache = {}


def fpc(k):
    return "1-2B" if k <= 2 else ("3-6B" if k <= 6 else ("7-49B" if k < 50 else "50-64B"))


rows = collections.Counter(); evs = collections.Counter(); out_ev = []
for key, nrows in P1["C_all_origin_events"]:
    lab, kind, cls, side, oid, e = key
    if lab not in cache:
        d = json.loads((S1 / (lab + ".json")).read_text())
        cache.clear(); cache[lab] = d
    d = cache[lab]
    if kind == "INPLACE":
        ev = [v for v in d["hist"][str(oid)] if v["e"] == e]
        ks = sorted({x[0] for v in ev for x in v["ex"]} | {x[0] for v in ev for x in v["mu"]})
        w = t2.get((lab, "INPLACE", oid, e))
    else:
        b = d["births"][str(oid)]
        ks = det[(lab, oid)]["diff_pos"]
        w = t2.get((lab, "DONOR_PRE", b["p"], e)) if cls == "DONOR_PRE" else None
    wr = "n/a" if w is None else "%s:%s@%s%d%s" % (w["actor"], w["op"], "own" if w["code_half"] == "own" else "ptr", w["pc"],
                                                   "" if w["repro_b1"] else "(nr)")
    k = (kind + ":" + cls, fpc(len(ks)))
    rows[k + (wr,)] += nrows
    evs[k + (wr,)] += 1
    out_ev.append({"key": key, "rows": nrows, "footprint_n": len(ks), "footprint": ks if len(ks) <= 8 else [ks[0], "..", ks[-1]],
                   "writer": wr})
tot = sum(rows.values())
agg_fp = collections.Counter(); agg_fp_ev = collections.Counter()
agg_instr = collections.Counter(); agg_instr_ev = collections.Counter()
for (o, f, w), v in rows.items():
    agg_fp[(o, f)] += v
    agg_instr[w.split("@")[0] if w != "n/a" else "n/a"] += v
for (o, f, w), v in evs.items():
    agg_fp_ev[(o, f)] += v
    agg_instr_ev[w.split("@")[0] if w != "n/a" else "n/a"] += v
out = {"rows_total": tot,
       "by_origin_footprint": [[list(k), v, agg_fp_ev[k]] for k, v in agg_fp.most_common()],
       "by_writer_instr": [[k, v, agg_instr_ev[k]] for k, v in agg_instr.most_common()],
       "by_origin_footprint_writer": [[list(k), v, evs[k]] for k, v in rows.most_common(40)],
       "events": out_ev}
(HERE / "p3_join.json").write_text(json.dumps(out, indent=1))
print("rows", tot, "events", len(out_ev))
for x in out["by_origin_footprint"]:
    print(x)
print()
for x in out["by_writer_instr"]:
    print(x)
print()
for x in out["by_origin_footprint_writer"][:30]:
    print(x)
