"""LM01 ADJUDICATION (ensorain/arc3/LM01_ADJUDICATION_ADDENDUM.md, rules G1-G9). Written and tested BEFORE any
campaign row exists. It runs the FROZEN analysis (ensorain.lm01.analysis) unchanged and adds adjudicated readings beside
each frozen label. Nothing here replaces a frozen label."""
import json
import math
import os

import numpy as np

from ensorain.lm01.analysis import stratum as frozen_stratum, _paired, _win, _eq, _lad, BOUNDED
from ensorain.lm01.margins_reduce_v2 import ci, DELTA

HERE = os.path.dirname(__file__)
Z95, Z80 = 1.645, 0.842


def _n_win(sd, d=DELTA):
    return math.ceil(((Z95 + Z80) * sd / d) ** 2) if sd else None                 # true effect 2*d vs bound d


def _n_tost(sd, d=DELTA):
    return math.ceil(((Z95 + 1.282) * sd / d) ** 2) if sd else None               # TOST, true diff 0, 80% power


def g1_headline_learnable(ok, d):
    lr = _paired(ok, lambda r: _lad(r, "L-R|full"), lambda r: r.get("N1"))
    return dict(LR_minus_N1=lr, pass_=(lr is not None and lr["lo"] > d))


def g9h_bstar(ok, d, end_key):
    """Monotone B*: the smallest rung from which ALL larger bounded rungs are EQUIVALENT to the endpoint."""
    rungs = [g for g in BOUNDED if any(f"random|{g}" in r.get("ladder", {}) for r in ok)]
    eq = [_eq(_paired(ok, lambda r, g=g: _lad(r, end_key), lambda r, g=g: _lad(r, f"random|{g}")), d) for g in rungs]
    for i, g in enumerate(rungs):
        if all(eq[i:]):
            return g
    return None


def g4_relabel(label):
    return {"SELECTIVE_BUYS_BYTES": "HEURISTIC_BEATS_RANDOM(bytes-only)",
            "RESERVOIR_SELECTIVE_ADVANTAGE": "HEURISTIC_BEATS_RANDOM",
            "RANDOM_BEATS_SELECTIVE": "RANDOM_BEATS_HEURISTIC",
            "INDISCRIMINATE_EQUIVALENT": "HEURISTIC_EQUIVALENT_TO_RANDOM"}.get(label, label)


def adjudicate_stratum(rows, dev, d, family):
    ok = [r for r in rows if r.get("status") == "OK"]
    fr = frozen_stratum(rows, dev, d, family)
    out = dict(frozen=fr)
    if fr.get("label") == "UNTESTED" or family == "F1_episodic":
        out["adjudicated"] = dict(note="frozen UNTESTED or F1 branch trigger; no adjudication")
        return out
    adj = {}
    # G1 + G2: headline
    g1 = g1_headline_learnable(ok, d)
    adj["G1_headline_pair"] = g1
    if not g1["pass_"]:
        adj["headline"] = "UNTESTED (headline pair not learnable, G1)"
    else:
        rung_ok = all((c := _paired(ok, lambda r, g=g: _lad(r, f"random|{g}"), lambda r: r.get("N1"))) is not None and c["lo"] > 0
                      for g in BOUNDED if any(f"random|{g}" in r.get("ladder", {}) for r in ok))
        adj["headline"] = dict(frozen_label=fr["headline"]["label"],
                               B_star_LR_monotone=g9h_bstar(ok, d, "L-R|full"),
                               B_star_warm_monotone=g9h_bstar(ok, d, "random|full"),
                               equivalence_readings_valid=rung_ok,
                               power_note="EXACT_RETENTION_PAYS is ~0-power by design (G2); non-firing is not evidence")
    # G3: secondary, bytes only
    sec = []
    for r in ok:
        L = r["arms"].get("LOSSLESS")
        lad = r["arms"].get("SELECTIVE_LADDER", {}).get("ladder", {})
        if L:
            for cap, v in lad.items():
                if "AC" in v:
                    sec.append((cap, v["AC"] - L["AC"], v["meter"]["peak_persistent"] <= L["meter"]["peak_persistent"]))
    caps = sorted({c for c, _, _ in sec}, key=int)
    g3 = {}
    for c in caps:
        dd = [x for cc, x, within in sec if cc == c and within]
        if len(dd) >= 3:
            g3[c] = ci(dd)
    adv = [c for c, v in g3.items() if v["lo"] > d]
    cm = bool(g3) and all(v["hi"] < -d for v in g3.values())
    adj["secondary_bytes_only"] = dict(per_cap=g3, label=("SELECTIVE_ADVANTAGE" if adv else
                                                          ("LOSSLESS_WINS_ALL_BYTE_MATCHED" if cm else "UNRESOLVED")),
                                       frozen_label=fr["secondary"]["label"],
                                       note="frozen read filter asymmetric (review F6); bytes-only per prose 6.2")
    # G4 + G5 + G9b: eviction
    ev = {}
    for g, a in fr["eviction"].get("at", {}).items():
        room = _paired(ok, lambda r: _lad(r, "random|full"), lambda r, g=g: _lad(r, f"random|{g}"))
        if not dev.get("posctl_pass"):
            lab = "UNRESOLVED (E6 fails; prose s7, G9b)"
        elif room is None or room["lo"] <= d:
            lab = "UNTESTED (no headroom at B, G5)"
        else:
            lab = g4_relabel(a["label"])
        # G7: matched-HR2 interpolations clamped at the full store are UNMATCHED
        cl = [r["dual"][g]["B_random"] >= r["ladder"]["random|full"]["B"] for r in ok
              if "B_random" in r.get("dual", {}).get(g, {}) and "B" in r.get("ladder", {}).get("random|full", {})]
        ev[g] = dict(frozen_label=a["label"], adjudicated=lab, headroom=room,
                     matched_HR2=("UNMATCHED (clamped, G7)" if cl and np.mean(cl) > 0.5 else "matched"))
    adj["eviction"] = ev
    # G6: replication sizes from each reading's own dev SD are computed by the caller (needs dev rows); placeholders
    adj["firings_pending_replication"] = [f + " (pending replication, G9g)" for f in fr.get("firings", [])]
    out["adjudicated"] = adj
    return out


def adjudicate(campaign_dir, dev_path=os.path.join(HERE, "..", "lm01", "dev", "margins_reduced_v2.json")):
    dev = json.load(open(dev_path))
    res = {}
    for key, dv in dev.items():
        fn = os.path.join(campaign_dir, key.replace("|", "__") + ".jsonl")
        rows = [json.loads(l) for l in open(fn)] if os.path.exists(fn) else []
        res[key] = adjudicate_stratum(rows, dv, DELTA, key.split("|")[0])
    # G9d: CROSSOVER (headline adjudication switches with level within family x generator)
    cross = {}
    for key, v in res.items():
        f, l, g = key.split("|")
        h = v.get("adjudicated", {}).get("headline")
        lab = h if isinstance(h, str) else (h or {}).get("frozen_label")
        cross.setdefault(f"{f}|{g}", {})[l] = lab
    res["_CROSSOVER"] = {k: v for k, v in cross.items() if len(set(x for x in v.values() if x)) > 1}
    return res
