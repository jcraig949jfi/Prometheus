"""HT-321a8fd8e0 / W1 Pass 4 evaluator. See NOTES.md.

Controls FIRST (printed and written to CONTROLS.json); treatment statistics
only if every positive and cheat control is detected. Writes PASS4_OUTCOME.json.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
KS = list(range(1, 9))
LOW_KS = [1, 2, 3]
HIGH_KS = [4, 5, 6, 7, 8]


def load():
    return [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl")) if l.strip()]


def pooled(rows, attack, arm):
    ar = [r for r in rows if r["attack"] == attack and r["arm"] == arm and not r.get("exhaustive")]
    assert ar, (attack, arm)
    out = {}
    for k in KS:
        c = [r["success_counts"][str(k)] for r in ar]
        m = [r["n_coalitions"] for r in ar]
        out[k] = {"rate": sum(c) / sum(m), "count": sum(c), "n_coalitions": sum(m), "n_seeds": len(ar),
                  "seed_rate_min": min(a / b for a, b in zip(c, m)),
                  "seed_rate_max": max(a / b for a, b in zip(c, m))}
    return out


def code_clause(st):
    return all(st[k]["rate"] <= 0.02 for k in LOW_KS) and all(st[k]["rate"] >= 0.5 for k in HIGH_KS)


def orig_step(st, t):
    return all(st[k]["count"] == 0 for k in KS if k <= t) and st[t + 1]["count"] > 0


def fully_resistant_K(st):
    K = 0
    for k in KS:
        if st[k]["count"] == 0:
            K = k
        else:
            break
    return K


def rates(st):
    return {str(k): round(v["rate"], 5) for k, v in st.items()}


def main():
    rows = load()
    meta = json.load(open(os.path.join(HERE, "run_meta.json")))

    # ---------------- controls first ----------------
    ctrl = {}
    for attack in ("R", "ORIG", "ALT"):
        pc = pooled(rows, attack, "POSITIVE_CONTROL")
        ctrl[f"{attack}.POSITIVE_CONTROL(k=1>=0.99)"] = pc[1]["rate"] >= 0.99
    ctrl["R.CHEAT(code clause)"] = code_clause(pooled(rows, "R", "CHEAT"))
    ctrl["ORIG.CHEAT_D3(step at t=1)"] = orig_step(pooled(rows, "ORIG", "CHEAT_D3"), 1)
    ctrl["ORIG.CHEAT_D5(step at t=2)"] = orig_step(pooled(rows, "ORIG", "CHEAT_D5"), 2)
    ctrl["ALT.CHEAT_ALT(K==3)"] = fully_resistant_K(pooled(rows, "ALT", "CHEAT_ALT")) == 3
    positive_detected = all(v for k, v in ctrl.items() if "POSITIVE" in k)
    cheat_detected = all(v for k, v in ctrl.items() if "CHEAT" in k)
    json.dump({"controls": ctrl, "positive_detected": positive_detected, "cheat_detected": cheat_detected},
              open(os.path.join(HERE, "CONTROLS.json"), "w"), indent=1)
    print("CONTROLS:", json.dumps(ctrl, indent=1))
    print(f"positive_detected={positive_detected} cheat_detected={cheat_detected}")

    out = {"triplicateId": "HT-321a8fd8e0", "world": "W1",
           "R": {"reproduced": False, "stats": {}},
           "ORIG": {"fired": False, "stats": {}},
           "ALT": {"status": "FAIL", "stats": {}},
           "controls": {"positive_detected": positive_detected, "cheat_detected": cheat_detected,
                        "detail": ctrl},
           "predicate": "PARK", "anomalies": [],
           "core_minutes": meta["core_minutes"], "attempts": meta["attempts"], "notes": ""}

    if not (positive_detected and cheat_detected):
        out["notes"] = "Controls not all detected; no treatment statistic computed. PARK (controls fail)."
        out["ALT"]["status"] = "FAIL"
        json.dump(out, open(os.path.join(HERE, "PASS4_OUTCOME.json"), "w"), indent=1)
        print("PARK: controls not detected; treatment statistics withheld")
        return

    # ---------------- R ----------------
    tr = pooled(rows, "R", "TREATMENT")
    co = pooled(rows, "R", "CONTROL")
    nt = pooled(rows, "R", "NULL_TWIN")
    success = code_clause(tr) and co[1]["rate"] >= 0.5
    failure = any(tr[k]["rate"] > 0.02 for k in LOW_KS) or co[1]["rate"] < 0.5
    nt_meets = code_clause(nt)
    r_class = "CONFOUNDED" if nt_meets else ("SIGNAL" if success and not failure else "NULL")
    out["R"] = {"reproduced": r_class == "SIGNAL",
                "stats": {"round1_class_on_new_seeds": r_class, "seeds": "100-119",
                          "TREATMENT_rate_by_k": rates(tr),
                          "TREATMENT_seed_range_k4": [tr[4]["seed_rate_min"], tr[4]["seed_rate_max"]],
                          "CONTROL_rate_k1": co[1]["rate"], "NULL_TWIN_rate_k1": nt[1]["rate"],
                          "null_twin_meets_code_clause": nt_meets}}

    # ---------------- ORIG ----------------
    d3 = pooled(rows, "ORIG", "BCH_D3")
    d5 = pooled(rows, "ORIG", "BCH_D5")
    s3, s5 = orig_step(d3, 1), orig_step(d5, 2)
    fired = s3 and s5  # two further codes, distinct d (3 and 5)
    out["ORIG"] = {"fired": fired,
                   "stats": {"BCH(31,26,3)": {"step_at_t_plus_1": s3, "t": 1, "rate_by_k": rates(d3)},
                             "BCH(31,21,5)": {"step_at_t_plus_1": s5, "t": 2, "rate_by_k": rates(d5)},
                             "codes_meta": meta["codes"],
                             "prior_art_label": "KNOWN_ANALOGUE_FOUND" if fired else None}}

    # ---------------- ALT ----------------
    cb = pooled(rows, "ALT", "CODE_BCH16")
    mj = pooled(rows, "ALT", "MAJ31")
    m48 = pooled(rows, "ALT", "MAJ_R3_48")
    Kc, Km, K48 = fully_resistant_K(cb), fully_resistant_K(mj), fully_resistant_K(m48)
    exh = {r["arm"]: {"counts": r["success_counts"], "n_coalitions_by_k": r["n_coalitions_by_k"]}
           for r in rows if r.get("exhaustive")}
    alt_pass = Kc > Km
    out["ALT"] = {"status": "PASS" if alt_pass else "FAIL",
                  "stats": {"K_code_BCH31_16": Kc, "K_majority_31": Km,
                            "code_rate_by_k": rates(cb), "majority31_rate_by_k": rates(mj),
                            "aux_MAJ_R3_48_K": K48, "aux_MAJ_R3_48_rate_by_k": rates(m48),
                            "aux_exhaustive_k1_3": exh}}

    # ---------------- anomalies ----------------
    an = []
    if Km == 0:
        an.append("ALT pass is guaranteed by counting: 31 agents cannot give 16 bits >= 3 copies each "
                  "(needs 48), so some single agent is pivotal under any allocation/tie rule; ALT tests "
                  "rate, not mechanism.")
    if K48 != 1:
        an.append(f"aux MAJ_R3_48 K={K48}, expected 1 (majority of 3 resists one liar)")
    for arm, e in exh.items():
        for k in ("1", "2", "3"):
            if arm == "EXH_CODE_BCH16" and e["counts"][k] != 0:
                an.append(f"exhaustive BCH16 k={k}: {e['counts'][k]} manipulating coalitions (sampling hid it)")
    for arm in ("CONTROL", "NULL_TWIN"):
        zc = sorted({r.get("zero_columns") for r in rows if r["attack"] == "R" and r["arm"] == arm})
        if any(z for z in zc):
            an.append(f"R {arm}: parity matrix zero columns {zc}")
    if tr[4]["rate"] < 0.7:
        an.append(f"R: step at k=4 is partial (rate {tr[4]['rate']:.3f}); resistance just beyond t "
                  "depends on which coalition is drawn (not explained in this pass)")
    out["anomalies"] = an

    # ---------------- predicate (NOTES.md order) ----------------
    if not alt_pass:
        pred = "PARK"
    elif not out["R"]["reproduced"]:
        pred = "PARK"
    elif fired:
        pred = "ORIG_FOSSIL_ALT_PASS"
    else:
        pred = "SURVIVES"
    out["predicate"] = pred
    out["notes"] = (f"R: round-1 class on seeds 100-119 = {r_class}; BCH16 rates {rates(tr)}. "
                    f"ORIG: d=3 step {s3}, d=5 step {s5} -> fired={fired}"
                    f"{' (KNOWN_ANALOGUE_FOUND)' if fired else ''}. ALT: K(code)={Kc} vs K(majority,31)={Km} "
                    f"-> {out['ALT']['status']}; aux majority r=3 on 48 agents K={K48}. Predicate {pred}.")
    json.dump(out, open(os.path.join(HERE, "PASS4_OUTCOME.json"), "w"), indent=1)
    print(pred)
    print(out["notes"])


if __name__ == "__main__":
    main()
