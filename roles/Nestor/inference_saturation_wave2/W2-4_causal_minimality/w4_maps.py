"""W2-4: per-genome 64-character class maps + adversarial-loop statistics -> class_maps.txt, w4_adversarial.json.

    python -B w4_maps.py   (after w4_run.py, w4_suff.py, w4_summarize.py)

Map legend (one character per genome position):
  P  conversion-necessary AND the main copy op byte (class 2 x class 5: invokes the VM block-copy primitive)
  N  conversion-necessary; the instruction's DELETION (-> NOP) also abolishes conversion (functionally required)
  n  conversion-necessary only against CORRUPTION: deleting the whole instruction leaves conversion intact
     (the environment default / the remaining chain supplies what it set; class 2 under corruption, class 4 under removal)
  p  conversion-partial (0.25 < Z ratio < 0.6)
  E  establishment-only, confirmed on fresh-seed re-assay (C = carried, K = children, P2 = two-step; see the json)
  e  establishment-only on the first assay, not confirmed
  .  causally neutral and transmitted (passenger)
  _  causally neutral and not transmitted
  lower-case x marks a causal position that is not transmitted (none observed)
"""
import json
import pathlib
import statistics as st

HERE = pathlib.Path(__file__).resolve().parent
R = json.loads((HERE / "w4_results.json").read_text())["genomes"]
S = json.loads((HERE / "w4_summary.json").read_text())["genomes"]
lines = []
adv = {"est_ratio_C_confirmed": [], "est_ratio_C_unconfirmed": [], "unconfirmed_reassay_cls": {},
       "est_confirmed_rows": [], "nop_fill_S_conv_Z_ge_half": 0, "nop_fill_S_conv_n": 0,
       "rand_fill_S_conv_Z_ge_half": 0, "passenger_executed": [], "passenger_not_executed": [],
       "causal_not_T": 0, "deletion_vs_corruption": {"conv_nec_bytes": 0, "in_deletion_necessary_instr": 0}}
for r, g in zip(R, S):
    if r["status"] != "OK":
        lines.append("%-22s %s" % (r["id"], r["status"]))
        continue
    hx = bytes.fromhex(r["hex"])
    T = set(r["transmitted"])
    delnec = set()
    for p, b in g["deletion_conv_nec_instr"]:
        delnec |= set(range(p, p + len(b) // 2))
    conf = {p for p, _ in g["est_confirmed"]}
    ex = set((r.get("trace") or {}).get("executed_pos") or [])
    m = []
    for x in r["pos"]:
        p, c = x["p"], x["cls"]
        if c == "CONV_NEC":
            ch = "P" if p == g["copy_pos"] else ("N" if p in delnec else "n")
            adv["deletion_vs_corruption"]["conv_nec_bytes"] += 1
            adv["deletion_vs_corruption"]["in_deletion_necessary_instr"] += p in delnec
        elif c == "CONV_PARTIAL":
            ch = "p"
        elif c == "EST_ONLY":
            ch = "E" if p in conf else "e"
            wc = r["wt"]["C"]
            if "C" in x["killed"] and wc:
                (adv["est_ratio_C_confirmed"] if p in conf else adv["est_ratio_C_unconfirmed"]).append(round(x["ko"]["C"] / wc, 3))
            if p in conf:
                adv["est_confirmed_rows"].append({"id": r["id"], "p": p, "byte": "%02X" % hx[p], "killed": x["killed"],
                                                  "ko_first": x["ko"], "re_same": x["re_same"]["ko"],
                                                  "val2": x.get("re_val2", {}).get("cls"), "wt_C": r["wt"]["C"],
                                                  "executed": p in ex})
            else:
                k = x.get("re_same", {}).get("cls")
                adv["unconfirmed_reassay_cls"][k] = adv["unconfirmed_reassay_cls"].get(k, 0) + 1
        else:
            ch = "." if p in T else "_"
            if p in T:
                (adv["passenger_executed"] if p in ex else adv["passenger_not_executed"]).append(1)
        if c != "NEUTRAL" and p not in T:
            ch = ch.lower() if ch.isalpha() else "x"
            adv["causal_not_T"] += 1
        m.append(ch)
    lines.append("%-22s %s  %s" % (r["id"], "".join(m), ",".join("%d:%s" % (p, "+".join(k)) for p, k in g["est_confirmed"])))
    sf = g.get("suff", {}).get("S_conv")
    if sf and r["grp"] not in ("MIN3", "MIN5"):
        adv["nop_fill_S_conv_n"] += 1
        adv["nop_fill_S_conv_Z_ge_half"] += sf["NOP_Z"] >= 0.5 * r["wt"]["Z"]
        adv["rand_fill_S_conv_Z_ge_half"] += (sf["Z_ratio"] or 0) >= 0.5
adv["passenger_executed"] = len(adv["passenger_executed"])
adv["passenger_not_executed"] = len(adv["passenger_not_executed"])
for k in ("est_ratio_C_confirmed", "est_ratio_C_unconfirmed"):
    v = adv[k]
    adv[k + "_median"] = st.median(v) if v else None
(HERE / "class_maps.txt").write_text(__doc__.split("Map legend")[1] + "\n" + "\n".join(lines) + "\n")
(HERE / "w4_adversarial.json").write_text(json.dumps(adv, indent=1))
print("\n".join(lines))
print(json.dumps({k: v for k, v in adv.items() if k != "est_confirmed_rows"}))
for row in adv["est_confirmed_rows"]:
    print(row["id"], row["p"], row["byte"], row["killed"], "C first/re", row["ko_first"]["C"], row["re_same"]["C"], "Z", row["ko_first"]["Z"], row["re_same"]["Z"], "wtC", row["wt_C"], "val2", row["val2"], "exec", row["executed"])
