"""W2-35 a4: aggregate s1_out (23 W2-17 replays, BASE). Mechanism (which LDIR, whose code, which context, D, n) and
the shift rule s = s_src + m*D (mod 64), D = (DE - HL) mod 128, 1 <= m <= n/D + 1 (one LDIR) or two-LDIR compositions;
creation rate per founder-lineage birth; viability of created frames (s3 rule: s <= 10 or s >= 41);
frame-lineage births (parent and child in the same rotated frame), labelled anc 0 or not; end census.
python -B a4_rates.py -> a4_rates.json"""
import json, glob, collections, pathlib
HERE = pathlib.Path(__file__).resolve().parent
RUNAWAY = {"XH2N_s1", "CNR_s22", "XTK_59", "XTK_121", "XTK_35", "CRW_1", "CRW_103", "CRW_145", "CRW_75", "CRW_78",
           "CRW_48", "CRW_126"}


def fs(c):
    return int(c[3:]) if c.startswith("ROT") else 0


def viable(s):
    return s <= 10 or s >= 41


def shiftset(l, base):
    D = l["d_minus_s_mod128"]
    if D in (0, 64):
        return set()
    mmax = l["n"] // D + 1
    return {(b + m * D) % 64 for b in base for m in range(1, mmax + 1)}


per, mech = {}, collections.Counter()
pred = collections.Counter()
allE = []
for f in sorted(glob.glob(str(HERE / "s1_out" / "*.json"))):
    d = json.loads(pathlib.Path(f).read_text())
    lab = d["label"]
    prim_inter = set()
    prim_halves = collections.Counter()
    for e in d["events"]:
        if e["kind"] != "CREATE":
            continue
        prim = "F0" in (e["partner_class"], e["victim_old_class"])
        s = e["new_frame"][0]
        if not prim:
            prim_halves["secondary"] += 1
            continue
        prim_inter.add((e["e"], e["i"]))
        prim_halves["halves"] += 1
        prim_halves["viable"] += viable(s)
        prim_halves["rot32"] += e["new_frame"][1] >= 32
        prim_halves["victim_anc0"] += e["victim_anc"] == 0
        prim_halves["victim_was_F0"] += e["victim_old_class"] == "F0"
        prim_halves["viable_unlabelled_slot"] += viable(s) and e["victim_anc"] != 0
        t = e["trace"]
        pred["reproduced" if t["retrace_reproduces"] else "not_reproduced"] += 1
        if not t["retrace_reproduces"]:
            continue
        base = {0, fs(e["partner_class"]), fs(e["victim_old_class"])}
        rl = [l for l in t["ldirs"] if l["d_minus_s_mod128"] not in (0, 64)]
        one = set().union(*[shiftset(l, base) for l in rl]) if rl else set()
        two = set()
        for a in rl:
            for b in rl:
                if a is not b:
                    two |= shiftset(b, shiftset(a, base))
        pred["one_ldir" if s in one else "two_ldir" if s in two else "unexplained"] += 1
        pre_cls = {"H%d" % e["vside"]: e["victim_old_class"], "H%d" % (1 - e["vside"]): e["partner_class"]}
        for l in rl:
            if s in shiftset(l, base) or s in two:
                runner = "victim_ctx" if l["ctx"] == e["vside"] else "partner_ctx"
                code = pre_cls[l["code_half"]]
                own = "own_half_code" if l["code_half"] == "H%d" % l["ctx"] else "foreign_half_code"
                mech[(code if code in ("F0", "none") else "ROT", own, "pos%d" % (l["pc"] % 64), "n>=128" if l["n"] >= 128 else "n<128")] += 1
                entry = t["paths"][str(l["ctx"])]["first_foreign_pc"] if str(l["ctx"]) in t["paths"] else t["paths"][l["ctx"]]["first_foreign_pc"]
                mech[("entry_into_foreign_half_pos", None if entry is None else entry % 64 // 8 * 8)] += 1
                break
    B = d["births"]
    fl = [b for b in B if b["parent_anc"] == 0 and b["parent_class"] == "F0"]
    fl_c = [b for b in fl if b["c"]]
    rotb = [b for b in B if b["parent_class"].startswith("ROT")]
    same = [b for b in rotb if b["child_class"] == b["parent_class"]]
    cen = d["census"][max(d["census"], key=int)]
    tot = sum(cen.values())
    sh = lambda pred_: round(sum(v for k, v in cen.items() if pred_(k)) / tot, 3)
    per[lab] = {"runaway": lab in RUNAWAY, "epochs": d["epochs"], "rot_interactions_with_F0": len(prim_inter),
                "rot_halves": dict(prim_halves), "founder_lineage_births": len(fl), "founder_lineage_causal": len(fl_c),
                "rot_halves_per_FL_birth": round(prim_halves["halves"] / max(1, len(fl)), 3),
                "viable_unlab_per_FL_birth": round(prim_halves["viable_unlabelled_slot"] / max(1, len(fl)), 4),
                "rot_parent_births": len(rotb), "rot_same_frame_births": len(same),
                "rot_same_frame_causal": sum(b["c"] for b in same),
                "rot_births_parent_anc0": sum(b["parent_anc"] == 0 for b in same),
                "frames_with_births": dict(collections.Counter(b["parent_class"] for b in same).most_common(4)),
                "end_census": {"anc0_share": sh(lambda k: k.startswith("anc0")), "F0": sh(lambda k: k.endswith("F0")),
                               "ROT_any": sh(lambda k: "ROT" in k), "ROT_unlabelled": sh(lambda k: "ROT" in k and k.startswith("other")),
                               "ROT_anc0": sh(lambda k: "ROT" in k and k.startswith("anc0"))}}
tot = collections.Counter()
for v in per.values():
    tot["halves"] += v["rot_halves"].get("halves", 0); tot["viable_unlab"] += v["rot_halves"].get("viable_unlabelled_slot", 0)
    tot["viable"] += v["rot_halves"].get("viable", 0); tot["FL"] += v["founder_lineage_births"]
    tot["inter"] += v["rot_interactions_with_F0"]
out = {"per_run": per, "totals": dict(tot),
       "pooled_rot_halves_per_FL_birth": round(tot["halves"] / tot["FL"], 3),
       "pooled_viable_unlabelled_per_FL_birth": round(tot["viable_unlab"] / tot["FL"], 4),
       "shift_rule": dict(pred), "mechanism": {str(k): v for k, v in mech.most_common(25)}}
(HERE / "a4_rates.json").write_text(json.dumps(out, indent=1))
for k, v in per.items():
    print(k, "RUN" if v["runaway"] else "ctl", v["rot_interactions_with_F0"], v["rot_halves"], v["founder_lineage_births"],
          v["rot_halves_per_FL_birth"], v["viable_unlab_per_FL_birth"], "|rotbirths", v["rot_same_frame_births"],
          v["rot_births_parent_anc0"], v["frames_with_births"], v["end_census"])
print({k: v for k, v in out.items() if k != "per_run"})
