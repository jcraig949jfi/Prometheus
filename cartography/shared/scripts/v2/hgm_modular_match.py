#!/usr/bin/env python3
"""
HGM Motive → Modular Form Correspondence Detector
===================================================
Matches hypergeometric motives (degree 2, weight 1 = classical weight 2)
against the modular forms database via a_n coefficient comparison.

Also attempts twist detection for near-matches and leverages the
Euler survey for higher-degree motives.

Data sources:
  - HGM motives:   cartography/lmfdb_dump/hgm_motives.json   (285 motives)
  - HGM Euler survey: cartography/lmfdb_dump/hgm_euler_survey.json (97K records)
  - Modular forms: charon/data/charon.duckdb  (102K forms, all weight 2)
"""

import json
import sys
import os
import time
from pathlib import Path
from collections import defaultdict
from fractions import Fraction

# -- paths --------------------------------------------------------------
REPO = Path(__file__).resolve().parents[4]  # F:/Prometheus
HGM_MOTIVES  = REPO / "cartography" / "lmfdb_dump" / "hgm_motives.json"
HGM_EULER    = REPO / "cartography" / "lmfdb_dump" / "hgm_euler_survey.json"
DUCKDB_PATH  = REPO / "charon" / "data" / "charon.duckdb"
OUT_PATH     = Path(__file__).parent / "hgm_modular_results.json"

# -- small primes for matching ------------------------------------------
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def load_hgm_motives():
    """Load HGM motives, return list of dicts."""
    with open(HGM_MOTIVES, "r") as f:
        data = json.load(f)
    return data["records"]


def extract_ap_from_coeffs(coeffs, primes):
    """
    coeffs is a_1, a_2, a_3, ... (1-indexed semantics in 0-indexed list).
    a_p = coeffs[p-1] for prime p.
    """
    ap = {}
    for p in primes:
        idx = p - 1
        if idx < len(coeffs):
            ap[p] = int(coeffs[idx])
    return ap


def load_modular_forms_at_levels(levels):
    """Load dim=1 modular forms at given levels from DuckDB. Returns dict: level -> list of form dicts."""
    import duckdb
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    # Also load forms at nearby levels for twist detection
    twist_levels = set()
    for N in levels:
        for d in [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 16, 25, 36, 49]:
            if N * d <= 10000:
                twist_levels.add(N * d)
            if N % d == 0:
                twist_levels.add(N // d)
    all_levels = levels | twist_levels

    level_list = ",".join(str(l) for l in sorted(all_levels))
    rows = con.execute(f"""
        SELECT lmfdb_label, level, dim, traces, related_objects, char_order
        FROM modular_forms
        WHERE level IN ({level_list}) AND dim = 1
    """).fetchall()

    forms_by_level = defaultdict(list)
    for label, level, dim, traces, related, char_order in rows:
        ap = {}
        for p in PRIMES:
            idx = p - 1
            if traces and idx < len(traces):
                ap[p] = int(traces[idx])
        forms_by_level[level].append({
            "label": label,
            "level": level,
            "dim": dim,
            "ap": ap,
            "related_objects": related or [],
            "char_order": char_order,
        })
    con.close()
    return forms_by_level


def match_ap(ap1, ap2, min_primes=10):
    """
    Compare two ap dicts. Returns (match_type, details).
    match_type: "exact", "twist", "partial", "none"
    """
    common_primes = sorted(set(ap1.keys()) & set(ap2.keys()))
    if len(common_primes) < min_primes:
        return "insufficient", {"common": len(common_primes)}

    # Exact match
    exact_matches = sum(1 for p in common_primes if ap1[p] == ap2[p])
    if exact_matches == len(common_primes):
        return "exact", {"matched_primes": len(common_primes)}

    # Check for sign twist: a_p -> -a_p at some primes
    # Quadratic twist by character chi: a_p -> chi(p) * a_p
    # For quadratic chi, chi(p) in {-1, 0, 1}
    # Try: ratio a_p(motive) / a_p(form) at primes where both nonzero
    nonzero_primes = [p for p in common_primes if ap1[p] != 0 and ap2[p] != 0]
    if len(nonzero_primes) >= 8:
        ratios = {p: ap1[p] / ap2[p] for p in nonzero_primes}
        # Quadratic twist: all ratios should be +1 or -1
        if all(abs(r) == 1.0 for r in ratios.values()):
            signs = {p: int(ratios[p]) for p in nonzero_primes}
            # Check if this is a Dirichlet character mod small d
            return "twist", {
                "matched_primes": len(common_primes),
                "nonzero_ratio_primes": len(nonzero_primes),
                "sign_pattern": signs,
                "exact_matches": exact_matches,
            }

    # Partial match
    if exact_matches >= 0.7 * len(common_primes):
        mismatches = {p: (ap1[p], ap2[p]) for p in common_primes if ap1[p] != ap2[p]}
        return "partial", {
            "matched_primes": exact_matches,
            "total_primes": len(common_primes),
            "mismatches": mismatches,
        }

    return "none", {"exact_matches": exact_matches, "total": len(common_primes)}


def detect_twist_character(sign_pattern):
    """
    Given a dict {p: +1/-1}, try to identify a quadratic Dirichlet character.
    Returns (discriminant, confidence) or None.
    """
    from math import gcd

    def kronecker(a, p):
        """Kronecker symbol (a/p) for odd prime p."""
        if a % p == 0:
            return 0
        # Euler criterion
        result = pow(a, (p - 1) // 2, p)
        return result if result <= 1 else result - p

    # Try small discriminants
    candidates = []
    for D in range(-100, 101):
        if D == 0:
            continue
        # Check D is a fundamental discriminant (simplified check)
        matches = 0
        total = 0
        for p, s in sign_pattern.items():
            if p == 2:
                continue  # Skip 2 for simplicity
            k = kronecker(D, p)
            if k != 0:
                total += 1
                if k == s:
                    matches += 1
        if total >= 5 and matches == total:
            candidates.append((D, total))

    if candidates:
        best = max(candidates, key=lambda x: x[1])
        return {"discriminant": best[0], "primes_checked": best[1]}
    return None


def load_euler_survey_degree2():
    """
    Load Euler survey for degree-2 families.
    Returns dict: family_label -> {prime -> list of (t_value_index, a_p)}.
    The Euler survey gives all specializations, so we extract a_p = -middle_coeff.
    """
    print("Loading Euler survey (degree 2)...")
    with open(HGM_EULER, "r") as f:
        data = json.load(f)
    records = data["records"]

    survey = defaultdict(dict)
    for rec in records:
        if rec["d"] != 2:
            continue
        label = rec["label"]
        p = rec["p"]
        # eulers is list of [1, -a_p, p] for each t-specialization
        euler_aps = []
        for euler in rec["eulers"]:
            # euler = ["1", str(-a_p), str(p)] or similar
            if len(euler) == 3:
                a_p = -int(euler[1])  # Euler factor 1 - a_p T + p T^2, so coeff is -a_p
                euler_aps.append(a_p)
        survey[label][p] = euler_aps
    print(f"  Loaded {len(survey)} degree-2 families from Euler survey")
    return survey


def check_known_correspondence(motive_label, form_label, form_related):
    """Check if the LMFDB already knows about this HGM<->MF correspondence."""
    # related_objects in modular forms often has 'EllipticCurve/Q/N/x'
    # HGM motives don't have related_objects in our dump, but the LMFDB
    # website does link them. We check if any related object mentions HGM.
    for obj in form_related:
        if "hypergeometric" in obj.lower() or "hgm" in obj.lower():
            return True
        # Also check if elliptic curve is linked (HGM -> EC -> MF chain)
        if "EllipticCurve" in obj:
            return "via_ec"
    return False


def analyze_higher_degree_motives(motives, euler_survey):
    """
    For degree-4 motives, check if their L-function factors into
    degree-2 pieces that could match modular forms.
    Uses Euler survey data.
    """
    results = []
    d4_motives = [m for m in motives if m["degree"] == 4]

    for m in d4_motives:
        family_label = f"A{'.'.join(str(a) for a in m['A'])}_B{'.'.join(str(b) for b in m['B'])}"
        if family_label not in euler_survey:
            continue
        # For degree 4 with weight 3 (classical weight 4), the Euler factors
        # are degree 4 polynomials. If they factor as product of two degree-2
        # polynomials, each piece could be a weight-2 modular form.
        results.append({
            "label": m["label"],
            "degree": m["degree"],
            "weight": m["weight"],
            "cond": m["cond"],
            "note": "degree-4 motive in Euler survey; factorization analysis needed"
        })

    return results


def main():
    t0 = time.time()
    print("=" * 70)
    print("HGM Motive -> Modular Form Correspondence Detector")
    print("=" * 70)

    # -- 1. Load HGM motives -------------------------------------------
    motives = load_hgm_motives()
    print(f"\nLoaded {len(motives)} HGM motives")

    # Focus on degree-2, weight-1 (= classical weight 2 modular forms)
    d2w1 = [m for m in motives if m["degree"] == 2 and m["weight"] == 1]
    print(f"Degree-2, weight-1 motives (target): {len(d2w1)}")

    # -- 2. Extract a_p from motive coefficients -----------------------
    for m in d2w1:
        m["ap"] = extract_ap_from_coeffs(m["coeffs"], PRIMES)

    # -- 3. Load modular forms -----------------------------------------
    conductors = {m["cond"] for m in d2w1}
    print(f"Unique conductors: {sorted(conductors)}")
    forms_by_level = load_modular_forms_at_levels(conductors)
    total_forms = sum(len(v) for v in forms_by_level.values())
    print(f"Loaded {total_forms} dim-1 modular forms at relevant levels")

    # -- 4. Match each motive against forms ----------------------------
    exact_matches = []
    twist_matches = []
    partial_matches = []
    no_matches = []

    print(f"\n{'-' * 70}")
    print("MATCHING degree-2 weight-1 HGM motives against modular forms")
    print(f"{'-' * 70}")

    for m in d2w1:
        cond = m["cond"]
        label = m["label"]
        m_ap = m["ap"]

        best_match = None
        best_type = "none"

        # Search at exact conductor first, then nearby levels
        search_levels = [cond]
        for d in [2, 3, 4, 5, 8, 9, 16, 25]:
            if cond * d <= 10000:
                search_levels.append(cond * d)
            if cond % d == 0:
                search_levels.append(cond // d)
        search_levels = sorted(set(search_levels))

        for level in search_levels:
            if level not in forms_by_level:
                continue
            for form in forms_by_level[level]:
                mtype, details = match_ap(m_ap, form["ap"])
                if mtype == "exact":
                    known = check_known_correspondence(label, form["label"], form["related_objects"])
                    match_info = {
                        "hgm_label": label,
                        "hgm_cond": cond,
                        "hgm_A": m["A"],
                        "hgm_B": m["B"],
                        "hgm_t": m["t"],
                        "hgm_sign": m["sign"],
                        "mf_label": form["label"],
                        "mf_level": form["level"],
                        "match_type": "exact",
                        "primes_matched": details["matched_primes"],
                        "known_to_lmfdb": known,
                        "mf_related_objects": form["related_objects"],
                    }
                    exact_matches.append(match_info)
                    if best_type != "exact":
                        best_match = match_info
                        best_type = "exact"
                elif mtype == "twist" and best_type not in ("exact",):
                    twist_char = detect_twist_character(details["sign_pattern"])
                    match_info = {
                        "hgm_label": label,
                        "hgm_cond": cond,
                        "hgm_A": m["A"],
                        "hgm_B": m["B"],
                        "hgm_t": m["t"],
                        "mf_label": form["label"],
                        "mf_level": form["level"],
                        "match_type": "twist",
                        "exact_matches": details["exact_matches"],
                        "total_primes": details["matched_primes"],
                        "twist_character": twist_char,
                    }
                    twist_matches.append(match_info)
                    best_match = match_info
                    best_type = "twist"
                elif mtype == "partial" and best_type not in ("exact", "twist"):
                    match_info = {
                        "hgm_label": label,
                        "hgm_cond": cond,
                        "hgm_A": m["A"],
                        "hgm_B": m["B"],
                        "hgm_t": m["t"],
                        "mf_label": form["label"],
                        "mf_level": form["level"],
                        "match_type": "partial",
                        "matched_primes": details["matched_primes"],
                        "total_primes": details["total_primes"],
                        "mismatches": {str(k): list(v) for k, v in details["mismatches"].items()},
                    }
                    partial_matches.append(match_info)
                    best_match = match_info
                    best_type = "partial"

        if best_type == "none":
            no_matches.append({
                "hgm_label": label,
                "hgm_cond": cond,
                "hgm_A": m["A"],
                "hgm_B": m["B"],
                "hgm_t": m["t"],
                "ap_sample": {str(p): v for p, v in list(m_ap.items())[:5]},
            })

    # -- 5. Deduplicate exact matches (same MF matched multiple times) -
    seen_pairs = set()
    unique_exact = []
    for em in exact_matches:
        pair = (em["hgm_label"], em["mf_label"])
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_exact.append(em)
    exact_matches = unique_exact

    # Deduplicate twists
    seen_twist = set()
    unique_twist = []
    for tm in twist_matches:
        pair = (tm["hgm_label"], tm["mf_label"])
        if pair not in seen_twist:
            seen_twist.add(pair)
            unique_twist.append(tm)
    twist_matches = unique_twist

    # -- 6. Classify known vs new --------------------------------------
    known_exact = [e for e in exact_matches if e["known_to_lmfdb"]]
    new_exact = [e for e in exact_matches if not e["known_to_lmfdb"]]

    # -- 7. Group by motive to see which motives map to same form ------
    motive_to_forms = defaultdict(list)
    for em in exact_matches:
        motive_to_forms[em["hgm_label"]].append(em["mf_label"])

    form_to_motives = defaultdict(list)
    for em in exact_matches:
        form_to_motives[em["mf_label"]].append(em["hgm_label"])

    # -- 8. Higher-degree analysis stub --------------------------------
    higher_deg_notes = []
    d2w0 = [m for m in motives if m["degree"] == 2 and m["weight"] == 0]
    d3 = [m for m in motives if m["degree"] == 3]
    d4 = [m for m in motives if m["degree"] == 4]
    higher_deg_notes.append(f"Degree-2 weight-0 motives (Artin reps): {len(d2w0)}")
    higher_deg_notes.append(f"Degree-3 motives: {len(d3)}")
    higher_deg_notes.append(f"Degree-4 motives: {len(d4)} (would need weight-4 forms or Siegel forms)")

    # -- 9. Print report -----------------------------------------------
    print(f"\n{'=' * 70}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 70}")
    print(f"Degree-2 weight-1 motives analyzed:  {len(d2w1)}")
    print(f"Exact matches found:                 {len(exact_matches)}")
    print(f"  Known to LMFDB (via EC link):      {len(known_exact)}")
    print(f"  NEW potential correspondences:      {len(new_exact)}")
    print(f"Twist matches:                       {len(twist_matches)}")
    print(f"Partial matches:                     {len(partial_matches)}")
    print(f"No match found:                      {len(no_matches)}")

    print(f"\n{'-' * 70}")
    print("EXACT MATCHES")
    print(f"{'-' * 70}")
    for em in exact_matches:
        known_str = "KNOWN" if em["known_to_lmfdb"] else "**NEW**"
        print(f"  {em['hgm_label']:40s} <-> {em['mf_label']:15s}  "
              f"[{em['primes_matched']} primes] {known_str}")
        if em["mf_related_objects"]:
            print(f"    Related: {em['mf_related_objects']}")

    if twist_matches:
        print(f"\n{'-' * 70}")
        print("TWIST MATCHES")
        print(f"{'-' * 70}")
        for tm in twist_matches:
            char_str = ""
            if tm.get("twist_character"):
                char_str = f" (twist by D={tm['twist_character']['discriminant']})"
            print(f"  {tm['hgm_label']:40s} ~ {tm['mf_label']:15s}  "
                  f"[{tm['exact_matches']}/{tm['total_primes']} exact]{char_str}")

    if partial_matches:
        print(f"\n{'-' * 70}")
        print("PARTIAL MATCHES (top 10)")
        print(f"{'-' * 70}")
        partial_sorted = sorted(partial_matches,
                                key=lambda x: x["matched_primes"] / max(x["total_primes"], 1),
                                reverse=True)
        for pm in partial_sorted[:10]:
            print(f"  {pm['hgm_label']:40s} ~ {pm['mf_label']:15s}  "
                  f"[{pm['matched_primes']}/{pm['total_primes']} primes match]")
            print(f"    Mismatches at: {list(pm['mismatches'].keys())}")

    if no_matches:
        print(f"\n{'-' * 70}")
        print(f"UNMATCHED MOTIVES ({len(no_matches)})")
        print(f"{'-' * 70}")
        for nm in no_matches:
            print(f"  {nm['hgm_label']:40s} cond={nm['hgm_cond']}")

    # Multi-to-one analysis
    multi_motive_forms = {f: ms for f, ms in form_to_motives.items() if len(ms) > 1}
    if multi_motive_forms:
        print(f"\n{'-' * 70}")
        print("MODULAR FORMS WITH MULTIPLE HGM CORRESPONDENCES")
        print(f"{'-' * 70}")
        for f, ms in sorted(multi_motive_forms.items()):
            print(f"  {f}: <- {ms}")

    print(f"\n{'-' * 70}")
    print("HIGHER-DEGREE NOTES")
    print(f"{'-' * 70}")
    for note in higher_deg_notes:
        print(f"  {note}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # -- 10. Save results ----------------------------------------------
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "total_hgm_motives": len(motives),
            "degree2_weight1_analyzed": len(d2w1),
            "exact_matches": len(exact_matches),
            "known_correspondences": len(known_exact),
            "new_correspondences": len(new_exact),
            "twist_matches": len(twist_matches),
            "partial_matches": len(partial_matches),
            "unmatched": len(no_matches),
        },
        "exact_matches": exact_matches,
        "twist_matches": twist_matches,
        "partial_matches": partial_matches[:20],  # top 20
        "unmatched_motives": no_matches,
        "multi_correspondence_forms": {
            f: ms for f, ms in form_to_motives.items() if len(ms) > 1
        },
        "higher_degree_notes": higher_deg_notes,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
