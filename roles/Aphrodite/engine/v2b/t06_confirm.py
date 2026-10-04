"""TEST-6 (Beta-01): T51-C -- FROZEN CONFIRMATION of the T51 exploratory finding on FRESH LIN seeds 8-15.
Spec: beta01/windows/T06_T51C_SPEC.md. Pipeline = t51_natural (unchanged code path; arms P, G1, G1_NC, PA via
V2B_T51_ARMS; seeds via V2B_T51_SEEDS; output V2B_T51_DIR=T06_T51C). This module adds only the FROZEN absolute
endpoint:
  gain(lib, arm, seed) = number of the seed's 32 TRANSFER families where `lib` reaches a T4-v1a-qualified program at
                         <= 1M in >= 1 of 2 cells AND PRISTINE is censored in that cell.
  H1 ENDOGENOUS_DERIVATION: sum_seeds gain(SEL, P) >= 0.70 * sum_seeds gain(START, G1), AND gain(SEL, P) > 0 in
                            >= 6/8 seeds.
  H2 DERIVES_BASE_CLASS:   P's selected schema is EQUAL_ANY (ruler v2.1) to G1 or to one of its re-expressions in
                            >= 5/8 seeds.
  H3 COMPOSITION_SMALL:    sum gain(SEL, G1) - sum gain(START, G1) <= 0.25 * sum gain(START, G1)  (descriptive gate).
  Gate: inherited benefit must exist: gain(START, G1) > 0 in >= 6/8 seeds, else UNTESTABLE_NO_INHERITED_BENEFIT.
  Reported (not gated): G1_NC SEL vs START equality (composition off; LGG selections may legitimately add).
"""
import json
import os
from collections import defaultdict

os.environ.setdefault("V2B_T51_DIR", "T06_T51C")
import t51_natural as T  # noqa: E402
import instruments as INS  # noqa: E402
import a18  # noqa: E402


def main():
    T.init_worker()
    idx = T.rd("T51_TRANSFER_INDEX.json")["index"]
    W = {(w["lib"], w["family"], w["cell"]): w for w in T.rdl("T51_WALKS.jsonl")}
    tech = [k for k, w in W.items() if w["status"] != "OK"]
    cell = defaultdict(dict)
    for e in idx:
        w = W.get((e["lib"], e["family"], e["cell"]))
        if w and w["status"] == "OK":
            cell[(e["catalog"], e["arm"], e["family"], e["cell"])][e["lib_role"]] = w["result"]
    ok = lambda r: bool(r) and not r.get("censored", True)  # noqa: E731
    fams = defaultdict(set)
    for (cat, arm, f, ci) in cell:
        fams[(cat, arm)].add(f)
    gain = defaultdict(lambda: defaultdict(int))
    for (cat, arm), fs in fams.items():
        for f in fs:
            for role in ("SEL", "START"):
                if any(ok(cell.get((cat, arm, f, i), {}).get(role)) and not ok(cell.get((cat, arm, f, i), {}).get("PRISTINE"))
                       for i in range(T.TCELLS)):
                    gain[(cat, arm)][role] += 1
    cats = sorted({c for c, _ in fams})
    P_sel = {c: gain[(c, "P")]["SEL"] for c in cats}
    G1_start = {c: gain[(c, "G1")]["START"] for c in cats}
    G1_sel = {c: gain[(c, "G1")]["SEL"] for c in cats}
    donors = {(d["catalog"], d["arm"]): d for d in T.rdl("T51_DONORS.jsonl")}
    refs = set(INS.ruler("v2.1").reexpressions(a18.G1)) | {a18.G1}
    base = {}
    for c in cats:
        s = donors.get((c, "P"), {}).get("selected_schema")
        base[c] = bool(s) and any(INS.equal_extensional(s, r, "v2.1") for r in refs)
    nc_eq = {c: gain[(c, "G1_NC")]["SEL"] == gain[(c, "G1_NC")]["START"] for c in cats}
    sP, sG = sum(P_sel.values()), sum(G1_start.values())
    H1 = sG > 0 and sP >= 0.70 * sG and sum(1 for c in cats if P_sel[c] > 0) >= 6
    H2 = sum(base.values()) >= 5
    H3 = (sum(G1_sel.values()) - sG) <= 0.25 * sG if sG else None
    supply_ok = sum(1 for c in cats if G1_start[c] > 0) >= 6
    disp = ("TECHNICAL_FAILURE" if tech else ("UNTESTABLE_NO_INHERITED_BENEFIT" if not supply_ok else "MEASURED"))
    res = {"disposition": disp, "seeds": cats, "P_SEL_gain": P_sel, "G1_START_gain": G1_start, "G1_SEL_gain": G1_sel,
           "PA": {c: dict(gain[(c, "PA")]) for c in cats}, "G1_NC_SEL_eq_START": nc_eq, "P_derives_base_class": base,
           "ratio_P_over_inherited": round(sP / sG, 3) if sG else None,
           "H1_ENDOGENOUS_DERIVATION": H1, "H2_DERIVES_BASE_CLASS": H2, "H3_COMPOSITION_SMALL": H3,
           "technical": tech[:10]}
    (T.OUTDIR / "T06_RESULT.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("disposition", "ratio_P_over_inherited", "H1_ENDOGENOUS_DERIVATION",
                                          "H2_DERIVES_BASE_CLASS", "H3_COMPOSITION_SMALL")}))


if __name__ == "__main__":
    main()
