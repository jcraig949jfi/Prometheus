"""OFFER01 reducer: L2 (reaim1 + exchange) vs BOTH L1 (reaim1) and X (exchange only), paired seeds, activity-matched.

    python offer01_reduce.py UNIT_DIR --window W --ticks T [--rules RULES.json] [--out REDUCTION.json]

Primary channel: DELIVERED payload view (changes only by ordinary winning writes; direct uptake excluded by
construction). Families vs each comparator via aim02_meter.compare_conds (comparator weighted by L2's activity-bin
mix):
  REPERTOIRE  upc diff     NOVELTY  n64 diff     DISCOVERY  dr2 diff
DELIVERY (provenance, absolute): share of L2's late winning template writes whose delivered byte was acquired by
uptake AND landed in opcode/arg1 (DOWNSTREAM_NONPAYLOAD) -- acquired values reaching fields no rule touches.
DOWNSTREAM richness (opcode/arg1 channel, same families) is reported, not gated.
"""

import argparse
import glob
import hashlib
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "AIM02"))
import aim02_meter as MTR  # noqa: E402

REDUCER_VERSION = "offer01_reduce.v1"
FAM = {"REPERTOIRE": "upc", "NOVELTY": "n64", "DISCOVERY": "dr2"}


def load(d):
    out = {}
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            u = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(u, dict) and u.get("schema") == "aether.offer01.unit.v1":
            out[(u["law"], u["seed_index"], u["window"], u["ticks"], os.path.basename(p).startswith("dup_"))] = u
    return out


def u_shares(an):
    h = an["U_hist"]
    tot = sum(h) or 1
    return {"U2": h[2] / tot, "U3": h[3] / tot, "U4plus": sum(h[4:]) / tot,
            "meanU": sum(i * x for i, x in enumerate(h)) / tot, "changing": an["columns_changing"]}


def per_law(units, W, T):
    out = {}
    for (law, k, w, t, dup), u in units.items():
        if w != W or t != T or dup:
            continue
        c = u["counts_late"]
        tw = c["tmpl_writes"] or 1
        r = out.setdefault(law, [])
        r.append({"seed": k, "delivered": u_shares(u["delivered"]), "downstream": u_shares(u["downstream"]),
                  "writer_payload": u_shares(u["writer_payload_diag"]) if u["writer_payload_diag"] else None,
                  "deliv_acq_share": c["deliv_acq"] / tw, "deliv_acq_nonpay_share": c["deliv_acq_nonpay"] / tw,
                  "uptake_share_of_changes": c["uptake_changes"] / (c["tmpl_changes"] or 1),
                  "dv_changes": c["dv_changes"], "tmpl_changes": c["tmpl_changes"]})
    return out


def contrasts(units, W, T):
    res = {}
    seeds = sorted(k for (law, k, w, t, d) in units if law == "L2" and w == W and t == T and not d)
    for k in seeds:
        u2 = units[("L2", k, W, T, False)]
        row = {"seed": k}
        for comp in ("L1", "X"):
            uc = units.get((comp, k, W, T, False))
            if uc:
                row[comp] = {"delivered": MTR.compare_conds(u2["delivered"]["bins"], uc["delivered"]["bins"]),
                             "downstream": MTR.compare_conds(u2["downstream"]["bins"], uc["downstream"]["bins"])}
        res[k] = row
    return res


def decide(con, laws, R):
    fam = {}
    for f, m in FAM.items():
        ok = 0
        vals = {"L1": [], "X": []}
        for k, row in con.items():
            beat = []
            for comp in ("L1", "X"):
                v = row.get(comp, {}).get("delivered", {})
                if m in v and v.get("coverage", 0) >= R["coverage_min"]:
                    vals[comp].append(v[m]["diff"])
                    beat.append(v[m]["diff"] >= R["margins"][f])
                else:
                    beat.append(False)
            ok += all(beat)
        fam[f] = {"seeds_beating_both": ok, "seeds": len(con), "material": ok >= R["seeds_min"],
                  "median_diff_vs_L1": st.median(vals["L1"]) if vals["L1"] else None,
                  "median_diff_vs_X": st.median(vals["X"]) if vals["X"] else None}
    l2 = laws.get("L2", [])
    dsh = [r["deliv_acq_nonpay_share"] for r in l2]
    fam["DELIVERY"] = {"median_share": st.median(dsh) if dsh else None,
                       "seeds_ge_margin": sum(1 for x in dsh if x >= R["delivery_min"]),
                       "material": sum(1 for x in dsh if x >= R["delivery_min"]) >= R["seeds_min"]}
    core = [f for f in FAM if fam[f]["material"]]
    if len(core) == len(FAM) and fam["DELIVERY"]["material"]:
        disp = "OFFER_REPERTOIRE_SUPPORTED"
    elif core:
        disp = "OFFER_WEAK"
    else:
        disp = "OFFER_TRIVIAL"
    u2 = [r["delivered"]["U2"] for r in l2]
    return {"families": fam, "disposition": disp,
            "shuttle_signature": {"L2_delivered_U2_share_median": st.median(u2) if u2 else None,
                                  "note": "U2 share ~ 0.9+ with dr2 ~ 0 = fixed two-value catalogue (A<->B shuttle)"}}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("unit_dir")
    ap.add_argument("--window", type=int, required=True)
    ap.add_argument("--ticks", type=int, required=True)
    ap.add_argument("--rules")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    units = load(a.unit_dir)
    hashes = sorted({u["table_hash"] for u in units.values()})
    dups = [{"law": l, "seed": k, "equal": (l, k, w, t, False) in units and
             units[(l, k, w, t, False)]["final_digest"] == u["final_digest"] and
             units[(l, k, w, t, False)]["delivered"] == u["delivered"]}
            for (l, k, w, t, d), u in units.items() if d]
    laws = per_law(units, a.window, a.ticks)
    con = contrasts(units, a.window, a.ticks)
    res = {"schema": "aether.offer01.reduction.v1", "reducer": REDUCER_VERSION, "units": len(units),
           "table_hashes": hashes, "duplicates": dups, "per_law": laws, "contrasts": con,
           "gates": {"single_table_hash_ok": len(hashes) == 1,
                     "duplicates_ok": bool(dups) and all(d["equal"] for d in dups)}}
    if a.rules:
        raw = open(a.rules, "rb").read()
        res["rules_sha256"] = hashlib.sha256(raw).hexdigest()
        dec = decide(con, laws, json.loads(raw))
        if not all(res["gates"].values()):
            dec["disposition_if_valid"] = dec["disposition"]
            dec["disposition"] = "MEASUREMENT_FAILED"
        res["decision"] = dec
    if a.out:
        open(a.out, "w", encoding="utf-8").write(json.dumps(res, indent=1))
    for law, rows in sorted(laws.items()):
        md = lambda f: st.median(f(r) for r in rows)  # noqa: E731
        print(law, "k=%d" % len(rows),
              "DELIV U2 %.3f U4+ %.4f meanU %.3f chg %d" % (md(lambda r: r["delivered"]["U2"]),
                                                        md(lambda r: r["delivered"]["U4plus"]),
                                                        md(lambda r: r["delivered"]["meanU"]),
                                                        md(lambda r: r["delivered"]["changing"])),
              "| DOWN U2 %.3f meanU %.3f" % (md(lambda r: r["downstream"]["U2"]), md(lambda r: r["downstream"]["meanU"])),
              "| WRITERPAY meanU %s" % (md(lambda r: r["writer_payload"]["meanU"]) if rows[0]["writer_payload"] else None),
              "| acq_deliv %.3f acq_nonpay %.3f uptake_share %.3f" % (md(lambda r: r["deliv_acq_share"]),
                                                                    md(lambda r: r["deliv_acq_nonpay_share"]),
                                                                    md(lambda r: r["uptake_share_of_changes"])))
    for k, row in con.items():
        for comp in ("L1", "X"):
            if comp in row:
                v = row[comp]["delivered"]
                print("L2 s%d vs %s DELIV cov %.2f" % (k, comp, v.get("coverage", 0)),
                      " ".join("%s %+.4f" % (m, v[m]["diff"]) for m in ("n16", "n64", "upc", "tpc", "dr2") if m in v),
                      "ret %s" % (("%.2fx" % v["return_median"]["ratio"]) if v.get("return_median") and v["return_median"]["ratio"] else "-"))
    print(json.dumps(res.get("decision", res["gates"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
