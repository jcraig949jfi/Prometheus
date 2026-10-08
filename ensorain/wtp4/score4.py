"""WTP-04 scorer (PREREG_WTP04 s5, s7). Reads runs/wtp04/<name>.jsonl, writes <name>_score.json.
Cell = (family, axis, level). Unit labels come from habit.classify. Cell label over the seeds:
  all seeds INFO_VALUELESS or all TRAPPED -> that label; any seed ILLEGAL -> ILLEGAL;
  all seeds PAYS (CHEAP or STRUCT) -> STRUCT_PAYS if every seed is STRUCT_PAYS, else CHEAP_PAYS;
  all seeds DEAD or INFO_VALUELESS (mixed) -> DEAD; otherwise SPLIT (seeds disagree on whether learning pays)."""
import collections
import json
import os
import sys

from .axes import AXES, grid
from .families import families
from .habit import classify, CHEAP, STRUCT

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp04")
PAYS = ("CHEAP_PAYS", "STRUCT_PAYS")


def cell_label(labels):
    if any(l == "ILLEGAL" for l in labels):
        return "ILLEGAL"
    if all(l == "INFO_VALUELESS" for l in labels):
        return "INFO_VALUELESS"
    if all(l in PAYS for l in labels):
        return "STRUCT_PAYS" if all(l == "STRUCT_PAYS" for l in labels) else "CHEAP_PAYS"
    if all(l == "TRAPPED" for l in labels):
        return "TRAPPED"
    if all(l in ("DEAD", "INFO_VALUELESS", "TRAPPED") for l in labels):
        return "DEAD"
    return "SPLIT"


def winner_class(w):
    return None if w is None else ("cheap" if w in CHEAP else "struct")


def score(name):
    rows = [json.loads(l) for l in open(os.path.join(OUT, f"{name}.jsonl"))]
    cells = collections.defaultdict(list)
    for r in rows:
        cells[(r["fid"], r["axis"], r["level"])].append(r)
    C = {}
    native_digest = {}
    for (fid, ax, lab), rs in cells.items():
        cl = [classify(r) for r in rs]
        labs = [c["label"] for c in cl]
        wins = [c.get("winner") for c in cl]
        wc = {winner_class(w) for w in wins}
        C[(fid, ax, lab)] = dict(label=cell_label(labs), seeds=labs, winners=wins,
                                 winner=(wins[0] if len(set(wins)) == 1 else None),
                                 winner_class=(wc.pop() if len(wc) == 1 else None),
                                 H=[c.get("H") for c in cl], secs=sum(r.get("secs", 0) for r in rs))
        if ax == "native":
            for r in rs:
                native_digest[(fid, r["seed"])] = {k: (v.get("digest"), v.get("U")) for k, v in (r.get("lives") or {}).items()}
    # instrument check: an axis level is LIVE for a unit if any life's event digest differs from native
    # a level whose genome equals the native genome is a NO-OP and is excluded from the denominator
    G = {f["fid"]: f["g"] for f in families()}
    TF = {(ax, lab): tf for ax, lab, tf in grid()}
    live = collections.Counter()
    tot = collections.Counter()
    noop = collections.Counter()
    for r in rows:
        if r["axis"] == "native" or r.get("status") != "OK":
            continue
        if TF[(r["axis"], r["level"])](G[r["fid"]]) == G[r["fid"]]:
            noop[r["axis"]] += 1
            continue
        nd = native_digest.get((r["fid"], r["seed"]))
        if nd is None:
            continue
        tot[r["axis"]] += 1
        live[r["axis"]] += any((v.get("digest"), v.get("U")) != nd.get(k) for k, v in r["lives"].items())
    fams = sorted({k[0] for k in C})
    out = dict(name=name, n_rows=len(rows), families=fams,
               liveness={ax: dict(live=live[ax], n=tot[ax], noop=noop[ax], inert=tot[ax] > 0 and live[ax] < 0.5 * tot[ax]) for ax in AXES},
               cells={"|".join(k): v for k, v in sorted(C.items())})
    # map per family x axis, boundaries on ordered axes
    maps, bounds = {}, []
    for fid in fams:
        nat = C.get((fid, "native", "native"), {}).get("label")
        maps[fid] = dict(native=nat)
        for ax, (ordered, levels) in AXES.items():
            seq = [(lab, C[(fid, ax, lab)]["label"]) for lab, _ in levels if (fid, ax, lab) in C]
            maps[fid][ax] = seq
            if ordered:
                for (l1, a), (l2, b) in zip(seq, seq[1:]):
                    if (a in PAYS) != (b in PAYS) and "SPLIT" not in (a, b) and "ILLEGAL" not in (a, b):
                        bounds.append(dict(fid=fid, axis=ax, between=[l1, l2], labels=[a, b],
                                           direction="dies" if a in PAYS else "appears"))
    out["maps"], out["boundaries"] = maps, bounds
    labs = collections.Counter(v["label"] for k, v in C.items() if k[1] != "native")
    out["label_counts"] = dict(labs)
    n = sum(labs.values())
    fam_pay = {f for (f, ax, _), v in C.items() if v["label"] in PAYS}
    fam_bound = {b["fid"] for b in bounds}
    split_frac = labs["SPLIT"] / max(1, n)
    out["split_frac"] = split_frac
    if len(fam_pay) < 2:
        verdict = "NO_HABITABLE_REGION"
    elif split_frac >= 0.30:
        verdict = "NOISE_LIMITED"
    elif len(fam_bound) >= 0.5 * len(fams):
        verdict = "ISLANDS_MAPPED"
    else:
        verdict = "PARTIAL_MAP"
    out["verdict"] = dict(rule=verdict, families_with_pays=sorted(fam_pay), families_with_boundary=sorted(fam_bound))
    # per-axis pooled habitability and carrier class among paying cells
    ax_tab = {}
    for ax in AXES:
        for lab, _ in AXES[ax][1]:
            vs = [C[(f, ax, lab)] for f in fams if (f, ax, lab) in C]
            if not vs:
                continue
            ax_tab.setdefault(ax, []).append(dict(level=lab, n=len(vs), pays=sum(v["label"] in PAYS for v in vs),
                                                  struct=sum(v["label"] == "STRUCT_PAYS" for v in vs),
                                                  dead=sum(v["label"] == "DEAD" for v in vs), trapped=sum(v["label"] == "TRAPPED" for v in vs),
                                                  info_valueless=sum(v["label"] == "INFO_VALUELESS" for v in vs), split=sum(v["label"] == "SPLIT" for v in vs)))
    out["axis_table"] = ax_tab
    # carrier change (preview of THEN): does the replicated winning class change along an axis?
    out["carrier_class_changes"] = [dict(fid=f, axis=ax, classes=cls) for f in fams for ax in AXES
                                    for cls in [[C[(f, ax, lab)]["winner_class"] for lab, _ in AXES[ax][1]
                                                 if (f, ax, lab) in C and C[(f, ax, lab)]["label"] in PAYS]]
                                    if len({c for c in cls if c}) > 1]
    json.dump(out, open(os.path.join(OUT, f"{name}_score.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    o = score(sys.argv[1])
    print(json.dumps(dict(verdict=o["verdict"], label_counts=o["label_counts"], split_frac=o["split_frac"],
                          liveness=o["liveness"], n_boundaries=len(o["boundaries"])), indent=1))
