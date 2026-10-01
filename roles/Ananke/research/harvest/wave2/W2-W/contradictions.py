"""W2-W step 3: every cell where two Wave-2 sources disagree, with the resolution. Reads out/placement.json.
Writes contradictions.csv (one row per cell x contradiction id) and prints the per-id counts."""
import json, csv
from pathlib import Path
from collections import Counter
HERE = Path(__file__).resolve().parent
P = [o for o in json.load(open(HERE / "out/placement.json"))]
out = []
def add(cid, o, a, b, res):
    out.append({"id": cid, "family": o["family"], "cell": o["cell"], "source_a": a, "source_b": b,
                "resolution": res, "final_class": o["final_class"]})
f3 = lambda v: "-" if v is None else "%.3f" % v
for o in P:
    fam, k = o["family"], o["cell"][:8]
    if fam == "HOLD": continue
    tcap = o["w2t_class"] == "CAPPED"; ucap = bool(o.get("w2u_capped")); pcap = bool(o.get("w2p_capped"))
    jcap = str(o.get("w2j_class", "")).startswith("CAPPED")
    hcap = o["hplant_lc"] is not None and o["hplant_lc"] < 0.60
    fcap = o["final_class"] in ("P_PROVEN", "CONSTRUCTION_PLACEMENT")
    b = "T=%s U1024=%s Uheld=%s Hplant=%s J-LC2=%s[hi %s] M=%s epi=%s" % (
        f3(o["w2t_combined"]), f3(o.get("w2u_joint")), f3(o.get("w2u_joint_held")), f3(o["hplant_lc"]),
        f3(o.get("w2j_lc2")), f3(o.get("w2j_lc2_hi")), f3(o.get("w2m_lc")), f3(o.get("w2s_epidemic")))
    # C1: cap membership (W2-T CAPPED at .60 combined vs W2-P/W2-U at .614 joint vs W2-J LC1/LC2 vs final)
    if len({tcap, ucap, pcap} | ({jcap} if fam == "XOR" else set())) > 1:
        add("C1-cap-membership", o, "W2-T CAPPED=%s; W2-U=%s; W2-P=%s%s" % (tcap, ucap, pcap, "; W2-J=%s" % o.get("w2j_class") if fam == "XOR" else ""),
            b, "final %s: min sound bound %s (%s); threshold .60 for proof, [.60,.614) = P_CANDIDATE" % (
                o["final_class"], f3(o["best_bound"]), o["best_bound_src"]))
    # C2: H-PLANT lc census (64 SCORE worlds, no async) vs the final cap
    if hcap != fcap and fam in ("XOR", "FLIP", "RELAY"):
        add("C2-hplant-vs-final", o, "H-PLANT lc %s (cap=%s)" % (f3(o["hplant_lc"]), hcap), b,
            "H-PLANT is a 32-pair estimate without wake/fanout/loss; superseded by W2-U (1024 worlds) and W2-T/W2-J")
    # C3: W2-P placement-only vs tighter bound
    if o.get("w2p_placement_only"):
        add("C3-placement-only", o, "W2-P placement-only (inward %s)" % f3(o.get("w2p_inward")), b,
            "CONSTRUCTION_PLACEMENT" if o["final_class"] == "CONSTRUCTION_PLACEMENT" else
            "P_PROVEN: inward margin (%.3f) < gap between W2-P model and W2-T exact-wake bound (%.3f)" % (
                o["w2p_inward"] - o["w2p_thr"], o["w2p_joint"] - o["w2t_combined"]))
    # C4: a plant exists but the checklist marks the champion inadmissible
    if o["plant_tier"] != "NONE" and o["final_class"] in ("INERT", "FLAT", "LATCHED_PARTIAL"):
        add("C4-plant-but-inadmissible", o, "plant %s (%s: %s)" % (o["plant_tier"], o["plant_src"], o["plant_note"]),
            "W2-T %s" % o["w2t_class"], "kept %s per the W2-O checklist (admissibility precedes plant); counted in the 'plant, any admissibility' tier" % o["final_class"])
    # C5: W2-L vs W2-S (FLIP)
    if fam == "FLIP":
        L, S = o["w2l_class"], o["w2s_class"]
        same = (L == S) or (L == "P(lightcone)" and S == "P(lightcone)")
        if not same:
            add("C5-W2L-vs-W2S", o, "W2-L %s" % L, "W2-S %s" % S,
                "W2-S supersedes (later, adds epidemic bound, B certificate, physics removal)")
        # C6: W2-S class vs W2-T admissibility (W2-S did not apply the checklist)
        if o["w2t_class"] in ("INERT", "FLAT") and not S.startswith(("P(", "UNDECIDED")):
            add("C6-W2S-vs-W2T", o, "W2-S %s" % S, "W2-T %s" % o["w2t_class"], "final %s (admissibility precedes plant-relative classes)" % o["final_class"])
    # C7: P-1b vs P-2 (RELAY decay>0 relay_flood failures), resolved by the W2-W refresh check
    if fam == "RELAY" and o.get("w2w_refresh"):
        add("C7-P1b-vs-P2", o, "P-1b %s (plant-dead read as physics)" % o["p1b"],
            "P-2: decay_shift %d failure = relay_flood artefact" % o["decay_shift"],
            "W2-W refresh check: %s -> %s" % (o["w2w_refresh"],
                "P-2 holds (plant rescued)" if o["plant_src"] == "W2-W" else "P-2 does NOT hold here (decay not binding)"))
    # C8: W2-T item 12 (no XOR/FLIP/MAJ plant) vs task plants found by W2-J/W2-L/W2-M
    if fam in ("XOR", "FLIP", "MAJ") and o["plant_tier"] in ("IN_SPACE", "OVERRIDE"):
        add("C8-W2T-item12-vs-plants", o, "W2-T: recorded plant relay_flood %s (not a task plant)" % f3(o["rec_plant_acc"]),
            "%s: %s" % (o["plant_src"], o["plant_note"]), "task plant wins; W2-T item 12 is superseded for this cell")
    # C9: W2-O sample vs W2-T / final
    if o.get("w2o_class"):
        wo = o["w2o_class"].split("(")[0].split("+")[0]
        if wo != o["w2t_class"] or (o["final_class"] not in (wo, "PLANT_SOLVED_IN_SPACE", "UNDECIDED") and not (wo == "CAPPED" and o["final_class"] == "P_PROVEN")):
            add("C9-W2O-vs-W2T", o, "W2-O %s" % o["w2o_class"], "W2-T %s marginal=%s" % (o["w2t_class"], o["w2t_marginal"]),
                "final %s (%s)" % (o["final_class"], b))
    # C10: W2-D tags vs final
    tags = o["w2d_tags"] or ""
    if "P:lightcone" in tags and not fcap:
        add("C10-W2D-vs-final", o, "W2-D %s" % tags, b, "final %s" % o["final_class"])
    if "P:lightcone" not in tags and fcap and tags:
        add("C10-W2D-vs-final", o, "W2-D %s (not P)" % tags, b, "final %s: W2-D used H-PLANT only" % o["final_class"])
    if "notRP" in tags and o["plant_tier"] == "NONE":
        add("C10-W2D-vs-final", o, "W2-D notRP (family plant >= .75)", "no in-space task plant", "final %s" % o["final_class"])
    # C11: W2-J XOR plant tier vs W2-J own class name
    if o.get("w2j_class") == "PLANT-SOLVED":
        add("C11-W2J-PLANT-SOLVED-scope", o, "W2-J PLANT-SOLVED (lo99 > .60, any length)",
            "row genome: no plant fits (W2-J F3)", "final %s / plant tier %s (%s)" % (o["final_class"], o["plant_tier"], o["plant_note"]))
    # C12: W2-M words vs tier
    if k in ("c7ec8097", "5c35b832"):
        add("C12-W2M-R-candidate", o, "W2-M 'R-candidate' (override INT_2)", "INT_2 at prog_len 14 is inside C1 genome space",
            "c7ec8097 lo99 .636 -> PLANT_SOLVED_OVERRIDE; 5c35b832 lo99 .535 < .55 -> no plant" if k == "c7ec8097" else
            "5c35b832 override lo99 .535 < .55: not plant-solved; final %s" % o["final_class"])
with open(HERE / "contradictions.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
c = Counter(x["id"] for x in out)
for k2, v in sorted(c.items()): print(k2, v, "cells")
print("total rows", len(out), "distinct cells", len({x["cell"] for x in out}))
