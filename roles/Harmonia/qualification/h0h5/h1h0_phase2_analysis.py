"""H1/H0 phase-2 diagnostic analysis, exactly as declared in
h1h0_phase2_analysis_plan_2026-09-14.md. Harmonia[m2-f541bed9].

Reads archaeon/docs/h0h5/H1H0_PHASE2_READOUT.json. Uses QR-1.1.0 functions
(qualification_rules.py) for every contrast and Sigma. Writes one JSON ledger
(argv[1]). Controls run FIRST; any failure aborts before the real data is
analysed. DIAGNOSTIC: nothing here is evidence for or against H0 or H1.
"""
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

from archaeon import workspace as _ws                          # noqa: E402

_ws.assert_not_canonical("run the H1/H0 phase-2 analysis")

import qualification_rules as QR                                # noqa: E402

READOUT = os.path.join(ROOT, "archaeon", "docs", "h0h5", "H1H0_PHASE2_READOUT.json")
CELLS = ("S00", "S10", "S01", "S11")
PLANTED = "tgt-11"
CAP = 6000
C_T = {"S11": 0.0, "S10": 1.0, "S01": 0.0, "S00": -1.0}


class Refused(Exception):
    pass


def est_dict(e):
    return {"name": e.name, "estimate": e.estimate, "lo": e.lo, "hi": e.hi,
            "se": e.se, "n": e.n, "alpha": e.alpha,
            "min_attainable_p": e.min_attainable_p}


def check_labels(table, dedup):
    """Payload identity comes from the readout's spec_hash_dedup, NOT from row
    observables: two distinct payloads can coincide on (status, solved, vm_ops)
    by chance (tgt-03 S01 and S11 both 6006), so an observable key would refuse
    real data. Refuse if the dedup names two 2x2 labels sharing one hash.

    Known blind spot, reported not hidden: fresh/S00 and random_pack/S10 carry
    DIFFERENT spec hashes for the SAME payload (Charon A1), so the dedup cannot
    see them. They are handled by construction (never cells) and attested by
    the observable identity count below."""
    for group in dedup.get("labels_sharing_a_hash") or []:
        labels = group if isinstance(group, (list, tuple)) else group.get("labels", [])
        inside = [x for x in labels if x in CELLS]
        if len(inside) >= 2:
            raise Refused("spec hash shared by 2x2 labels %s" % inside)
    same = {"fresh==S00": 0, "random_pack==S10": 0}
    for row in table:
        for a, b, k in (("fresh", "S00", "fresh==S00"), ("random_pack", "S10", "random_pack==S10")):
            ra, rb = row[a], row[b]
            if (ra["kind_status"], ra["solved"], ra["vm_ops"]) == (rb["kind_status"], rb["solved"], rb["vm_ops"]):
                same[k] += 1
    return same


def provenance(table):
    out = {}
    for row in table:
        for c in ("fresh", "random_pack") + CELLS + ("S00-deg",):
            r = row.get(c)
            if r:
                k = "%s|%s|%s" % (c, r["set"], r["allowance"])
                out[k] = out.get(k, 0) + 1
    by_cell = {}
    for c in CELLS:
        by_cell[c] = sorted({(row[c]["set"], str(row[c]["allowance"])) for row in table})
    cross = len({tuple(v) for v in by_cell.values()}) > 1
    return {"counts": out, "by_cell": {c: [list(x) for x in v] for c, v in by_cell.items()},
            "CROSS_DEPLOY": cross}


def solve_blocks(table, exclude=()):
    return [{"task": row["task_id"], **{c: 1.0 if row[c]["solved"] else 0.0 for c in CELLS}}
            for row in table if row["task_id"] not in exclude]


def diffs(blocks, c):
    return [sum(c.get(k, 0.0) * b[k] for k in CELLS) for b in blocks]


def contrast(name, blocks, c, alpha, n_primary):
    d = diffs(blocks, c)
    nz = sum(1 for x in d if abs(x) > 0)
    if nz == 0:
        return {"name": name, "label": "NOTHING_COULD_FIRE", "block_differences": d,
                "n": len(d), "nonzero_blocks": 0}
    e = QR.paired_contrast(name, d, alpha, n_primary)
    out = est_dict(e)
    out.update({"block_differences": d, "nonzero_blocks": nz})
    if e.se == 0:
        out["label"] = "ZERO_VARIANCE_INTERVAL_UNDEFINED"
    return out


def shared_arm(blocks):
    t, g = diffs(blocks, C_T), diffs(blocks, QR.C_G)
    n = len(t)
    mt, mg = sum(t) / n, sum(g) / n
    st = math.sqrt(sum((x - mt) ** 2 for x in t) / (n - 1)) if n > 1 else 0.0
    sg = math.sqrt(sum((x - mg) ** 2 for x in g) / (n - 1)) if n > 1 else 0.0
    emp = (sum((a - mt) * (b - mg) for a, b in zip(t, g)) / (n - 1) / (st * sg)) if st > 0 and sg > 0 else None
    sig = QR.sigma_from_blocks(blocks)
    cov = sum(C_T[i] * QR.C_G[j] * sig[(i, j)] for i in CELLS for j in CELLS)
    vt, vg = QR.contrast_variance(C_T, sig), QR.contrast_variance(QR.C_G, sig)
    model = cov / math.sqrt(vt * vg) if vt > 0 and vg > 0 else None
    return {"corr_empirical": emp, "corr_from_sigma": model, "var_T": vt, "var_G": vg,
            "note": "undefined when either contrast has zero variance across blocks"}


def scale_s(table, exclude, label):
    b = solve_blocks(table, exclude)
    res = {"label": label, "n_blocks": len(b), "tasks": [x["task"] for x in b],
           "G": contrast("G_joint_treatment_S11_minus_S00", b, QR.C_G, 0.05, 2),
           "I": contrast("interaction_I", b, QR.C_I, 0.05, 2),
           "M1_secondary": contrast("marginal_main_slot1", b, QR.C_M1, 0.05, 1),
           "M2_secondary": contrast("marginal_main_slot2", b, QR.C_M2, 0.05, 1),
           "transport_secondary_is_also_H1_transport": contrast("S10_minus_S00", b, C_T, 0.05, 1),
           "shared_arm": shared_arm(b)}
    try:
        res["se_ratio_report"] = QR.se_ratio_report(b)
    except ZeroDivisionError:
        res["se_ratio_report"] = "UNDEFINED (zero variance)"
    return res


def v_value(r, mode):
    if mode == "cap":
        return float(CAP) if r["kind_status"] == "BUDGET_VM_OPS" else float(r["vm_ops"])
    raise ValueError(mode)


def scale_v(table):
    out = {}
    # V-1 solved-only: per contrast, blocks where every cell with non-zero weight solved
    v1 = {}
    for name, c in (("G", QR.C_G), ("I", QR.C_I), ("transport", C_T)):
        cells = [k for k in CELLS if c.get(k, 0.0) != 0.0]
        elig = [row for row in table if all(row[k]["solved"] for k in cells)]
        b = [{k: float(row[k]["vm_ops"]) for k in CELLS} for row in elig]
        entry = {"eligible_blocks": [row["task_id"] for row in elig], "n": len(elig)}
        if len(elig) >= 2:
            entry.update(contrast(name, b, c, 0.05, 2 if name in ("G", "I") else 1))
        else:
            entry["label"] = "INELIGIBLE (n < 2)"
            entry["block_differences"] = diffs(b, c)
        v1[name] = entry
    out["V1_solved_only"] = v1
    # V-2 cap substitute
    b2 = [{k: v_value(row[k], "cap") for k in CELLS} for row in table]
    out["V2_cap_substitute"] = {n: contrast(n, b2, c, 0.05, 2 if n in ("G", "I") else 1)
                                for n, c in (("G", QR.C_G), ("I", QR.C_I), ("transport", C_T))}
    # V-3 ranks within block: solved first, then vm_ops ascending; censored tie at worst
    b3 = []
    for row in table:
        keyed = []
        for k in CELLS:
            r = row[k]
            keyed.append((k, (0, r["vm_ops"]) if r["solved"] else (1, None)))
        solved = sorted([x for x in keyed if x[1][0] == 0], key=lambda x: x[1][1])
        cens = [x for x in keyed if x[1][0] == 1]
        ranks = {}
        for i, (k, _) in enumerate(solved):
            ranks[k] = float(i + 1)
        if cens:
            worst = (len(solved) + 1 + len(CELLS)) / 2.0
            for k, _ in cens:
                ranks[k] = worst
        b3.append(ranks)
    out["V3_rank"] = {n: contrast(n, b3, c, 0.05, 2 if n in ("G", "I") else 1)
                      for n, c in (("G", QR.C_G), ("I", QR.C_I), ("transport", C_T))}

    def sign(e):
        if "estimate" not in e:
            return None
        return 0 if e["estimate"] == 0 else (1 if e["estimate"] > 0 else -1)
    agree = {}
    for n in ("G", "I", "transport"):
        s = [sign(out["V1_solved_only"][n]), sign(out["V2_cap_substitute"][n]), sign(out["V3_rank"][n])]
        agree[n] = {"signs_V1_V2_V3": s,
                    "reading": ("CENSORING-DETERMINED" if len({x for x in s if x is not None}) > 1
                                else "signs agree where defined")}
    out["sign_agreement"] = agree
    return out


def controls(table):
    res = {}
    # POSITIVE: planted G=+0.5, I=+0.5 on 0/1 blocks
    rng = random.Random(914)
    pos = []
    for i in range(12):
        # S00 0, S10 0, S01 0, S11 1 in half the blocks -> G=0.5, I=0.5
        on = 1.0 if i % 2 == 0 else 0.0
        pos.append({"S00": 0.0, "S10": 0.0, "S01": 0.0, "S11": on})
    g = contrast("G", pos, QR.C_G, 0.05, 2)
    res["POSITIVE"] = {"G": g, "pass": g.get("lo", -1) > 0}
    # CHEAT: S11 := S00
    cheat_tab = json.loads(json.dumps(table))
    for row in cheat_tab:
        row["S11"] = dict(row["S00"])
        row["S11"]["set"] = "CHEAT"          # keep refusal from firing on identical rows
    cs = scale_s(cheat_tab, (), "cheat")
    cv = scale_v(cheat_tab)
    ok_s = cs["G"].get("label") == "NOTHING_COULD_FIRE"
    ok_v = all(cv[k]["G"].get("estimate", 0.0) == 0.0 or cv[k]["G"].get("label") in
               ("NOTHING_COULD_FIRE", "INELIGIBLE (n < 2)")
               for k in ("V1_solved_only", "V2_cap_substitute", "V3_rank"))
    res["CHEAT"] = {"S_G": cs["G"], "V_G": {k: cv[k]["G"] for k in ("V1_solved_only", "V2_cap_substitute", "V3_rank")},
                    "pass": ok_s and ok_v}
    # REFUSAL: a dedup that says S10 and S01 share one spec hash must be refused,
    # and a clean dedup must NOT be (the negative arm of the refusal itself)
    try:
        check_labels(table, {"labels_sharing_a_hash": [["S10", "S01"]]})
        fired = False
    except Refused as e:
        fired, detail = True, str(e)
    try:
        check_labels(table, {"labels_sharing_a_hash": [["fresh", "S00"]]})
        silent_on_non_cells = True
    except Refused:
        silent_on_non_cells = False
    res["REFUSAL"] = {"pass": fired and silent_on_non_cells,
                      "fires_on_two_2x2_labels": fired,
                      "silent_when_only_one_label_is_a_cell": silent_on_non_cells,
                      "detail": detail if fired else "did not refuse"}
    # NEGATIVE: within-block label permutation reference for G on scale S
    obs = solve_blocks(table)
    g_obs = abs(sum(diffs(obs, QR.C_G)) / len(obs))
    hits = 0
    perms = 2000
    for _ in range(perms):
        pb = []
        for b in obs:
            vals = [b[c] for c in CELLS]
            rng.shuffle(vals)
            pb.append(dict(zip(CELLS, vals)))
        if abs(sum(diffs(pb, QR.C_G)) / len(pb)) >= g_obs - 1e-12:
            hits += 1
    res["NEGATIVE_permutation_reference_S_G"] = {"perms": perms, "abs_G_observed": g_obs,
                                                 "fraction_ge_observed": hits / perms,
                                                 "pass": True,
                                                 "note": "a reference distribution, not a test of H0"}
    return res


def main(out_path):
    raw = open(READOUT, "rb").read()
    d = json.loads(raw)
    table = d["table"]
    if len(table) != 12 or not d.get("complete"):
        raise Refused("readout not complete or not 12 blocks")
    ctl = controls(table)
    failed = [k for k, v in ctl.items() if not v["pass"]]
    ledger = {"schema": "harmonia.h1h0_phase2_analysis.v1", "instance": "m2-f541bed9",
              "plan": "roles/Harmonia/qualification/h0h5/h1h0_phase2_analysis_plan_2026-09-14.md",
              "purpose": "DIAGNOSTIC (QR-1.1.0): not evidence for or against H0 or H1",
              "input": {"path": "archaeon/docs/h0h5/H1H0_PHASE2_READOUT.json",
                        "sha256_bytes": hashlib.sha256(raw).hexdigest(),
                        "sha256_lf": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
                        "written": d.get("written")},
              "receipt": _ws.receipt(), "controls": ctl, "controls_failed": failed}
    if failed:
        ledger["aborted"] = "controls failed: %s" % failed
    else:
        ledger["label_identities"] = check_labels(table, d.get("spec_hash_dedup") or {})
        ledger["spec_hash_dedup_as_read"] = d.get("spec_hash_dedup")
        ledger["planted_control_block"] = PLANTED
        ledger["provenance"] = provenance(table)
        ledger["S_a_all_12"] = scale_s(table, (), "S-a all 12 blocks (tgt-11 = planted instrument control, included)")
        ledger["S_b_excl_planted"] = scale_s(table, (PLANTED,), "S-b 11 blocks, planted control excluded")
        ledger["V"] = scale_v(table)
    with open(out_path, "w") as fh:
        json.dump(ledger, fh, indent=1, default=str)
        fh.flush()
    print("controls failed:", failed)
    if failed:
        return 1
    print("label identities:", ledger["label_identities"])
    print("provenance CROSS_DEPLOY:", ledger["provenance"]["CROSS_DEPLOY"], ledger["provenance"]["by_cell"])
    for k in ("S_a_all_12", "S_b_excl_planted"):
        s = ledger[k]
        for n in ("G", "I", "transport_secondary_is_also_H1_transport"):
            e = s[n]
            print("%-18s %-40s est=%s lo=%s hi=%s nz=%s label=%s" % (k, e["name"], e.get("estimate"), e.get("lo"),
                  e.get("hi"), e.get("nonzero_blocks"), e.get("label")))
        print("   shared_arm", s["shared_arm"]["corr_empirical"], s["shared_arm"]["corr_from_sigma"])
    print("V sign agreement:", json.dumps(ledger["V"]["sign_agreement"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
