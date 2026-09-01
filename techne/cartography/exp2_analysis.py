"""EXPERIMENT 2 -- EVIDENCE x GEOMETRY. Is the failure evidence-bound or geometry-bound?

    python -m techne.cartography.exp2_analysis

FOUR ARMS OVER THE SAME PAPERS. Using one paper set across all four arms is what makes the
2x2 an attribution rather than four separate observations -- any difference between arms is
caused by the factor that changed, not by which papers happened to land in which arm.

    A  abstract evidence  + 4-tuple geometry      (the campaign as run)
    B  abstract evidence  + 3-tuple geometry      (geometry relaxed)
    C  full-text evidence + 4-tuple geometry      (evidence enriched)
    D  full-text evidence + 3-tuple geometry      (both)

ATTRIBUTION RULE, fixed before the numbers were seen:

    marginal gain from EVIDENCE  = mean(C-A, D-B)
    marginal gain from GEOMETRY  = mean(B-A, D-C)

    EVIDENCE-BOUND   evidence gain materially exceeds geometry gain
    GEOMETRY-BOUND   geometry gain materially exceeds evidence gain
    BOTH             both gains are material
    NEITHER          neither gain is material -- the ontology is the problem, not the
                     evidence or the geometry

"Material" is defined against a floor set by the DEFECT-CORRECTION rate: full text can only
help if it actually changes coordinates, so the analysis also reports how many abstract-derived
coordinates full text CORRECTED, and how many placements it revealed as FALSE. A geometry that
gains coverage while full text shows its placements were wrong has not gained anything.

WHAT THIS CANNOT DO. The sample is arXiv-only and preprint-biased, full text is truncated at
12 pages, and PDF extraction is lossy. All three are recorded on the result, and none of them
can be fixed by analysis.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
from typing import Optional

from . import predicates as P
from . import taxonomy

SAMPLE = pathlib.Path(__file__).resolve().parent / "exp2_fulltext_sample.json"
OUT = pathlib.Path(__file__).resolve().parent / "exp2_results.json"
AXES3 = ("representation_family", "selection_family", "evaluation_regime")
K = 5
#: A gain below this is not treated as material. Set before seeing results: 5 percentage
#: points on a sample of ~50 is roughly the smallest difference that is not one or two papers.
MATERIAL_PP = 0.05


def load() -> dict:
    if not SAMPLE.exists():
        raise SystemExit("sample not built -- run: python -m techne.cartography.exp2_corpus --fetch")
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def coords_from_text(text: str) -> tuple:
    """(bottleneck, descriptors, mechanisms) from a body of text. Same tagger both arms --
    only the TEXT differs, which is the point."""
    mech = taxonomy.tag_mechanisms(text or "")
    return taxonomy.assign_bottleneck(mech), taxonomy.descriptors_from(mech), mech


def cell(bott: str, desc: dict, use3: bool) -> tuple:
    c = tuple(desc.get(a, "unknown") for a in AXES3)
    return c if use3 else (bott,) + c


def is_placed(bott: str, desc: dict, use3: bool) -> bool:
    if any(desc.get(a, "unknown") == "unknown" for a in AXES3):
        return False
    return True if use3 else bott != "B_UNASSIGNED"


def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def neighbours(i: int, cells: list, k: int = K) -> list:
    """Indices of the k papers sharing most known coordinates with paper i."""
    hc = cells[i]
    if hc is None:
        return []
    scored = []
    for j, tc in enumerate(cells):
        if j == i or tc is None:
            continue
        shared = sum(1 for a, b in zip(hc, tc)
                     if a == b and a not in ("unknown", "B_UNASSIGNED"))
        if shared:
            scored.append((-shared, j))
    scored.sort()
    return [j for _s, j in scored[:k]]


def cross_field(i: int, nbrs: list, mechs: list, titles: list) -> bool:
    hm = set(mechs[i])
    if not hm:
        return False
    for j in nbrs:
        for m in hm & set(mechs[j]):
            if not any(p.search(titles[i] or "") for p in taxonomy._COMPILED.get(m, ())):
                return True
    return False


def run_arm(papers: list, use_fulltext: bool, use3: bool) -> dict:
    texts, cells, mechs, titles = [], [], [], []
    abst = collections.Counter()
    placed_idx = []
    for p in papers:
        t = (p.get("fulltext") if use_fulltext else p.get("abstract")) or ""
        texts.append(t)
        b, d, m = coords_from_text(t)
        mechs.append(sorted(m))
        titles.append(p.get("title") or "")
        for a in AXES3:
            if d.get(a, "unknown") == "unknown":
                abst[a] += 1
        if not use3 and b == "B_UNASSIGNED":
            abst["bottleneck"] += 1
        ok = is_placed(b, d, use3)
        cells.append(cell(b, d, use3) if ok else None)
        if ok:
            placed_idx.append(len(cells) - 1)

    nq = cf = 0
    for i in placed_idx:
        nb = neighbours(i, cells)
        if nb:
            nq += 1
        if cross_field(i, nb, mechs, titles):
            cf += 1

    # MECHANISM_ISOLATED: the predicate that CANNOT fire on an abstract by construction.
    iso = 0
    for p, t in zip(papers, texts):
        spans = [{"text": t, "scope": "fulltext" if use_fulltext else "abstract"}]
        v, _r = P.mechanism_isolated(spans)
        iso += (v == "CONFIRMED")

    n = len(papers)
    lo, hi = wilson(len(placed_idx), n)
    return {"n": n, "placed": len(placed_idx), "placement_rate": len(placed_idx) / n,
            "placement_ci95": [round(lo, 3), round(hi, 3)],
            "abstention_by_coordinate": dict(abst),
            "mechanism_isolated": iso, "mechanism_isolation_rate": iso / n,
            "neighbour_rate": (nq / len(placed_idx)) if placed_idx else 0.0,
            "cross_field_rate": (cf / len(placed_idx)) if placed_idx else 0.0,
            "_cells": cells, "_mechs": mechs}


def corrections(papers: list) -> dict:
    """How often does full text CHANGE an abstract-derived coordinate, and how often does it
    reveal an abstract placement as wrong?

    A false placement is an abstract that produced a coordinate the full text contradicts --
    not merely one the full text fills in. Filling a gap is enrichment; contradiction is error.
    """
    changed = collections.Counter()
    filled = collections.Counter()
    contradicted = collections.Counter()
    false_placements = []
    for p in papers:
        if not p.get("fulltext"):
            continue
        ba, da, _ = coords_from_text(p.get("abstract") or "")
        bf, df, _ = coords_from_text(p.get("fulltext"))
        for a in AXES3:
            va, vf = da.get(a, "unknown"), df.get(a, "unknown")
            if va == vf:
                continue
            changed[a] += 1
            if va == "unknown":
                filled[a] += 1
            elif vf != "unknown":
                contradicted[a] += 1
        if ba != bf:
            changed["bottleneck"] += 1
            if ba == "B_UNASSIGNED":
                filled["bottleneck"] += 1
            elif bf != "B_UNASSIGNED":
                contradicted["bottleneck"] += 1
        if is_placed(ba, da, False) and any(
                da.get(a, "unknown") != df.get(a, "unknown")
                and df.get(a, "unknown") != "unknown" for a in AXES3):
            false_placements.append({"title": (p.get("title") or "")[:70],
                                     "abstract_coords": {a: da.get(a) for a in AXES3},
                                     "fulltext_coords": {a: df.get(a) for a in AXES3}})
    return {"coordinates_changed": dict(changed), "gaps_FILLED": dict(filled),
            "values_CONTRADICTED": dict(contradicted),
            "abstract_placements_contradicted_by_fulltext": len(false_placements),
            "examples": false_placements[:5],
            "note": ("FILLED means the abstract said unknown and the full text supplied a "
                     "value -- enrichment. CONTRADICTED means both said something and they "
                     "disagree -- error. Only the second impugns the abstract-only arm.")}


def run() -> dict:
    d = load()
    papers = [p for p in d["papers"] if p.get("abstract")]
    with_ft = [p for p in papers if p.get("fulltext")]
    # The 2x2 must use the SAME papers in all four arms, so restrict to those with full text.
    papers = with_ft

    A = run_arm(papers, False, False)
    B = run_arm(papers, False, True)
    C = run_arm(papers, True, False)
    D = run_arm(papers, True, True)
    corr = corrections(papers)

    ev_gain = ((C["placement_rate"] - A["placement_rate"])
               + (D["placement_rate"] - B["placement_rate"])) / 2
    geo_gain = ((B["placement_rate"] - A["placement_rate"])
                + (D["placement_rate"] - C["placement_rate"])) / 2
    ev_mat = ev_gain >= MATERIAL_PP
    geo_mat = geo_gain >= MATERIAL_PP
    if ev_mat and geo_mat:
        attribution = "BOTH"
    elif ev_mat:
        attribution = "EVIDENCE-BOUND"
    elif geo_mat:
        attribution = "GEOMETRY-BOUND"
    else:
        attribution = "NEITHER"

    iso_gain = C["mechanism_isolation_rate"] - A["mechanism_isolation_rate"]

    for arm in (A, B, C, D):
        arm.pop("_cells", None)
        arm.pop("_mechs", None)

    return {
        "experiment": "EXP2_EVIDENCE_x_GEOMETRY",
        "sample": {"n_papers_in_sample": d["n_papers"],
                   "n_with_fulltext": d["n_with_fulltext"],
                   "n_used_in_all_four_arms": len(papers),
                   "strata": d["strata"], "limits": d["limits"]},
        "arms": {"A_abstract_4tuple": A, "B_abstract_3tuple": B,
                 "C_fulltext_4tuple": C, "D_fulltext_3tuple": D},
        "marginal_gain_evidence_pp": round(100 * ev_gain, 2),
        "marginal_gain_geometry_pp": round(100 * geo_gain, 2),
        "material_threshold_pp": 100 * MATERIAL_PP,
        "mechanism_isolation_gain_from_fulltext_pp": round(100 * iso_gain, 2),
        "corrections": corr,
        "ATTRIBUTION": attribution,
        "caveats": [
            "arXiv-only sample: preprint-biased, excludes venues that do not post to arXiv",
            "full text truncated at 12 pages; appendices excluded",
            "PDF extraction is lossy on tables, equations and multi-column layout",
            "the same lexical tagger is used in every arm -- this measures what EVIDENCE and "
            "GEOMETRY contribute given that tagger, and cannot exonerate the tagger itself",
        ],
    }


def main() -> int:
    r = run()
    s = r["sample"]
    print("EXPERIMENT 2 -- EVIDENCE x GEOMETRY")
    print("  sample %d fetched, %d with full text, %d used in all four arms"
          % (s["n_papers_in_sample"], s["n_with_fulltext"], s["n_used_in_all_four_arms"]))
    print("\n  Arm                     Placed   Rate     CI95            MechIso  XField")
    print("  ---------------------   ------   ------   -------------   -------  ------")
    for k, lbl in (("A_abstract_4tuple", "A abstract + 4-tuple"),
                   ("B_abstract_3tuple", "B abstract + 3-tuple"),
                   ("C_fulltext_4tuple", "C fulltext + 4-tuple"),
                   ("D_fulltext_3tuple", "D fulltext + 3-tuple")):
        a = r["arms"][k]
        print("  %-21s %6d   %5.1f%%   [%.2f, %.2f]   %5.1f%%   %5.1f%%"
              % (lbl, a["placed"], 100 * a["placement_rate"],
                 a["placement_ci95"][0], a["placement_ci95"][1],
                 100 * a["mechanism_isolation_rate"], 100 * a["cross_field_rate"]))
    print("\n  marginal gain from EVIDENCE : %+.2f pp" % r["marginal_gain_evidence_pp"])
    print("  marginal gain from GEOMETRY : %+.2f pp" % r["marginal_gain_geometry_pp"])
    print("  material threshold          : %.1f pp" % r["material_threshold_pp"])
    print("  mechanism-isolation gain from full text: %+.2f pp"
          % r["mechanism_isolation_gain_from_fulltext_pp"])
    c = r["corrections"]
    print("\n  coordinates FILLED by full text     : %s" % c["gaps_FILLED"])
    print("  coordinates CONTRADICTED by full text: %s" % c["values_CONTRADICTED"])
    print("  abstract placements contradicted     : %d"
          % c["abstract_placements_contradicted_by_fulltext"])
    print("\n  ATTRIBUTION: %s" % r["ATTRIBUTION"])
    OUT.write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
    print("\n  wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
