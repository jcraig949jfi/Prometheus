"""Apply PHYSICS_DESIGN_03 s2.3 (Block D) and s3 (Block E) verbatim.

Input: a directory of assay unit results (aeth03_unit.py, instrument
"assay", one law x seed x arm each, slice 0:32). Pools the 128 origins per
law and arm, then:

  per law (OFF):  P_sust (SUSTAINED share, as ladder 2), P_content (share of
                  origins whose CONTENT differences reach generation >= 5 AND
                  radius >= 5), G_content (median content max-generation over
                  origins with any content), preserved and altered content
                  counts, content gen >= 2, locality violations.
  Block D, per combination vs its two components, OFF:
     N1  P_sust >= max(0.10, 2 x larger component) AND > sum of components
     N2  P_content >= max(0.05, 3 x larger component) AND > sum of components
     -> NEW_BEHAVIOUR if N1 or N2, else ADDITIVE_OR_LESS.
  Block E, fwd vs rcv, OFF:
     E-P1  share of origins whose PRESERVED content reaches generation >= 5
           is >= 2 x rcv's AND >= 0.05  -> the metric recognises transport;
     E-P2  altered share of fwd's content differences at generation >= 2
           (probe triggered if > 0.25).
"""

import argparse
import glob
import json
import os
import statistics

COMBOS = {"rcv_add": ("rcv", "add"), "rcv_cnd": ("rcv", "cnd"), "rcv_str": ("rcv", "str")}


def load(d):
    by = {}
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            r = json.load(fh)
        if "runs" not in r or r.get("inputs", {}).get("instrument") != "aeth03_propagation.assay":
            continue
        inp = r["inputs"]
        by.setdefault((inp["law"], inp["arm"]), []).append(r)
    return by


def law_stats(results):
    s = [run["summary"] for r in results for run in r["runs"]]
    n = len(s)
    c = [x["content"] for x in s]
    with_content = [x for x in c if x["new"] > 0]
    return {
        "origins": n,
        "seeds": sorted(r["inputs"]["seed_index"] for r in results),
        "P_sust": sum(x["class"] == "SUSTAINED" for x in s) / float(n),
        "P_sec": sum(x["max_generation"] >= 2 for x in s) / float(n),
        "P_esc": sum(x["max_radius"] >= 3 for x in s) / float(n),
        "max_radius": max(x["max_radius"] for x in s),
        "M_gen1_share": (sum(x["new_gen1"] for x in s) / float(sum(x["new_differences"] for x in s))
                         if sum(x["new_differences"] for x in s) else None),
        "P_content": sum(x["max_generation"] >= 5 and x["max_radius"] >= 5 for x in c) / float(n),
        "P_preserved_gen5": sum(x["preserved_max_generation"] >= 5 for x in c) / float(n),
        "G_content": (statistics.median([x["max_generation"] for x in with_content])
                      if with_content else None),
        "content_new": sum(x["new"] for x in c),
        "content_preserved": sum(x["preserved"] for x in c),
        "content_altered": sum(x["altered"] for x in c),
        "content_gen_ge2": sum(x["gen_ge2"] for x in c),
        "content_preserved_gen_ge2": sum(x["preserved_gen_ge2"] for x in c),
        "content_max_radius": max(x["max_radius"] for x in c),
        "locality_violations": sum(x["locality_violations"] for x in s),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir")
    a = ap.parse_args(argv)
    by = load(a.dir)
    laws = {"%s_%s" % k: law_stats(v) for k, v in sorted(by.items())}
    out = {"laws": laws, "block_d": {}, "block_e": {}}
    for combo, (c1, c2) in COMBOS.items():
        k, k1, k2 = combo + "_off", c1 + "_off", c2 + "_off"
        if not all(x in laws for x in (k, k1, k2)):
            continue
        L, A, B = laws[k], laws[k1], laws[k2]
        n1 = (L["P_sust"] >= max(0.10, 2 * max(A["P_sust"], B["P_sust"]))
              and L["P_sust"] > A["P_sust"] + B["P_sust"])
        n2 = (L["P_content"] >= max(0.05, 3 * max(A["P_content"], B["P_content"]))
              and L["P_content"] > A["P_content"] + B["P_content"])
        out["block_d"][combo] = {
            "components": [c1, c2], "N1": n1, "N2": n2,
            "P_sust": [L["P_sust"], A["P_sust"], B["P_sust"]],
            "P_content": [L["P_content"], A["P_content"], B["P_content"]],
            "verdict": "NEW_BEHAVIOUR" if (n1 or n2) else "ADDITIVE_OR_LESS"}
    if "fwd_off" in laws and "rcv_off" in laws:
        F, R = laws["fwd_off"], laws["rcv_off"]
        altered_share = (1.0 - F["content_preserved_gen_ge2"] / float(F["content_gen_ge2"])
                         if F["content_gen_ge2"] else None)
        out["block_e"] = {
            "E_P1": F["P_preserved_gen5"] >= max(0.05, 2 * R["P_preserved_gen5"]),
            "P_preserved_gen5": {"fwd": F["P_preserved_gen5"], "rcv": R["P_preserved_gen5"]},
            "E_P2_altered_share_gen_ge2": altered_share,
            "E_P2_probe_triggered": altered_share is not None and altered_share > 0.25}
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
