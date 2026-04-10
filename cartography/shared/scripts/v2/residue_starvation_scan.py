"""
C02: Mod-p Residue Class Starvation Scan

Scans dim=1 weight-2 modular forms for residue class starvation -- when
Hecke eigenvalues a_p only occupy a fraction of available residue classes
mod small primes ell.

Methodology:
- dim=1 forms have rational integer eigenvalues a_p.
- Bad primes (p | level) excluded: a_p is not a Hecke eigenvalue there.
- p = ell excluded: a_p mod ell has special structure at the test prime.
- Uses ALL available eigenvalues (up to p=997, ~168 primes).
- Starvation at mod 2 (ratio=0.5) typically means rational 2-torsion.
- Starvation at larger primes is rarer and more interesting.
"""

import json
import time
from collections import Counter
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[4]
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
MAASS_PATH = REPO_ROOT / "cartography" / "lmfdb_dump" / "maass_rigor.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "residue_starvation_results.json"


def sieve(n):
    s = [True] * (n + 1); s[0] = s[1] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            for j in range(i*i, n+1, i):
                s[j] = False
    return [i for i in range(2, n+1) if s[i]]


PRIMES = sieve(997)
TEST_ELLS = [2, 3, 5, 7, 11, 13, 17, 19, 23]
MIN_GOOD = 30  # Need 30+ good primes after filtering
# Thresholds: mod-2 starvation is common (2-torsion), use different thresholds
THRESHOLD_SMALL = 0.75  # For ell=2,3
THRESHOLD_LARGE = 0.85  # For ell >= 5


def get_threshold(ell):
    return THRESHOLD_SMALL if ell <= 3 else THRESHOLD_LARGE


def compute_starvation(good_vals, ell):
    residues = set(v % ell for v in good_vals)
    dist = Counter(v % ell for v in good_vals)
    return len(residues), len(residues) / ell, dict(sorted(dist.items()))


def qr_set(ell):
    """Quadratic residues mod ell (including 0)."""
    return {(x * x) % ell for x in range(ell)}


def analyze_classes(classes_hit, ell):
    """Try to identify the residue class pattern."""
    qr = qr_set(ell)
    qnr = set(range(ell)) - qr

    if classes_hit == qr:
        return "quadratic residues (CM signature)"
    if classes_hit == qnr | {0}:
        return "quadratic non-residues + 0"

    # Check if it's a coset of a subgroup
    for d in range(2, ell):
        if (ell - 1) % d == 0:
            # Subgroup of order (ell-1)/d in (Z/ell)*
            gen = None
            for g in range(2, ell):
                if pow(g, (ell-1)//d, ell) != 1:
                    if pow(g, ell-1, ell) == 1:
                        gen = g
                        break
            if gen:
                subgroup = {pow(gen, k*d, ell) for k in range((ell-1)//d)}
                subgroup_with_0 = subgroup | {0}
                if classes_hit == subgroup_with_0:
                    return f"subgroup of index {d} in (Z/{ell})* + {{0}}"

    return None


def scan():
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    total = conn.execute(
        "SELECT count(*) FROM modular_forms WHERE dim=1 AND weight>=2 AND ap_coeffs IS NOT NULL"
    ).fetchone()[0]
    print(f"Scanning {total} dim=1 forms")

    results = {
        "metadata": {
            "scan_date": time.strftime("%Y-%m-%d %H:%M"),
            "test_primes": TEST_ELLS,
            "threshold_small_ell": THRESHOLD_SMALL,
            "threshold_large_ell": THRESHOLD_LARGE,
            "min_good_primes": MIN_GOOD,
        },
        "starved_forms": [],
        "summary_by_prime": {},
        "cm_breakdown": {"cm_total": 0, "cm_starved": 0,
                          "noncm_total": 0, "noncm_starved": 0},
        "interesting_patterns": [],
        "maass_analysis": {},
    }

    # Track per-ell stats
    ell_stats = {ell: {"starved": 0, "min_ratio": 1.0, "min_form": "",
                       "ratios": []} for ell in TEST_ELLS}

    batch = 5000
    offset = 0
    processed = 0

    while True:
        rows = conn.execute(f"""
            SELECT lmfdb_label, level, weight, ap_coeffs, is_cm, is_rm,
                   self_twist_type, sato_tate_group
            FROM modular_forms
            WHERE dim=1 AND weight>=2 AND ap_coeffs IS NOT NULL
            ORDER BY level, weight
            LIMIT {batch} OFFSET {offset}
        """).fetchall()
        if not rows:
            break

        for label, level, weight, ap_str, is_cm, is_rm, twist, st in rows:
            try:
                ap = [int(x[0]) for x in json.loads(ap_str)]
            except:
                continue

            processed += 1
            is_cm_bool = bool(is_cm)

            if is_cm_bool:
                results["cm_breakdown"]["cm_total"] += 1
            else:
                results["cm_breakdown"]["noncm_total"] += 1

            starvation = {}
            for ell in TEST_ELLS:
                good = [ap[i] for i, p in enumerate(PRIMES)
                        if i < len(ap) and level % p != 0 and p != ell]
                if len(good) < MIN_GOOD:
                    continue

                hits, ratio, dist = compute_starvation(good, ell)
                threshold = get_threshold(ell)

                ell_stats[ell]["ratios"].append(ratio)

                if ratio < threshold:
                    classes_hit = set(v % ell for v in good)
                    pattern = analyze_classes(classes_hit, ell)

                    starvation[str(ell)] = {
                        "classes_hit": hits,
                        "ratio": round(ratio, 4),
                        "distribution": dist,
                        "classes": sorted(classes_hit),
                        "missing": sorted(set(range(ell)) - classes_hit),
                        "pattern": pattern,
                        "num_good_primes": len(good),
                    }

                    ell_stats[ell]["starved"] += 1
                    if ratio < ell_stats[ell]["min_ratio"]:
                        ell_stats[ell]["min_ratio"] = ratio
                        ell_stats[ell]["min_form"] = label

            if starvation:
                entry = {
                    "label": label,
                    "level": level,
                    "weight": weight,
                    "is_cm": is_cm_bool,
                    "is_rm": bool(is_rm),
                    "self_twist_type": twist,
                    "sato_tate_group": st,
                    "starvation": starvation,
                }

                # Flag non-CM starvation at large primes as especially interesting
                if not is_cm_bool:
                    large_starved = {ell: v for ell, v in starvation.items()
                                     if int(ell) >= 5}
                    if large_starved:
                        entry["flag"] = "NON-CM large-prime starvation"
                        results["interesting_patterns"].append(entry)

                results["starved_forms"].append(entry)

                if is_cm_bool:
                    results["cm_breakdown"]["cm_starved"] += 1
                else:
                    results["cm_breakdown"]["noncm_starved"] += 1

        offset += batch
        if processed % 5000 == 0 and processed > 0:
            print(f"  {processed} forms, {len(results['starved_forms'])} starved")

    # Summarize
    results["metadata"]["total_scanned"] = processed
    results["metadata"]["total_starved"] = len(results["starved_forms"])

    for ell in TEST_ELLS:
        s = ell_stats[ell]
        ratios = s["ratios"]
        results["summary_by_prime"][str(ell)] = {
            "total_starved": s["starved"],
            "min_ratio": round(s["min_ratio"], 4),
            "min_ratio_form": s["min_form"],
            "avg_ratio": round(sum(ratios) / max(1, len(ratios)), 4),
            "p10_ratio": round(sorted(ratios)[len(ratios)//10], 4) if ratios else 1.0,
        }

    conn.close()
    return results


def analyze_maass(results):
    try:
        with open(MAASS_PATH) as f:
            data = json.load(f)
        results["maass_analysis"] = {
            "total_forms": data.get("total_records", len(data.get("records", []))),
            "columns": data.get("columns", []),
            "has_coefficients": False,
            "verdict": "No Fourier coefficients available; only spectral parameters stored.",
        }
    except FileNotFoundError:
        results["maass_analysis"] = {"error": "File not found"}


def print_report(results):
    meta = results["metadata"]
    print(f"\n{'='*75}")
    print("C02: RESIDUE CLASS STARVATION SCAN -- FINDINGS")
    print(f"{'='*75}")
    print(f"Forms scanned: {meta['total_scanned']} (dim=1, weight>=2)")
    print(f"Total starved: {meta['total_starved']}")

    cm = results["cm_breakdown"]
    print(f"\nCM:     {cm['cm_total']:>6} total, {cm['cm_starved']:>5} starved "
          f"({100*cm['cm_starved']/max(1,cm['cm_total']):.1f}%)")
    print(f"Non-CM: {cm['noncm_total']:>6} total, {cm['noncm_starved']:>5} starved "
          f"({100*cm['noncm_starved']/max(1,cm['noncm_total']):.1f}%)")

    print(f"\n{'ell':<6} {'Starved':<10} {'Min':<8} {'Avg':<8} {'P10':<8} {'Worst Form'}")
    print("-" * 75)
    for ell in TEST_ELLS:
        s = results["summary_by_prime"][str(ell)]
        print(f"{ell:<6} {s['total_starved']:<10} {s['min_ratio']:<8.3f} "
              f"{s['avg_ratio']:<8.3f} {s['p10_ratio']:<8.3f} {s['min_ratio_form']}")

    # Mod-2 starvation analysis
    mod2_forms = [f for f in results["starved_forms"] if "2" in f["starvation"]]
    mod2_cm = sum(1 for f in mod2_forms if f.get("is_cm"))
    print(f"\nMOD-2 STARVATION: {len(mod2_forms)} forms (all a_p even)")
    print(f"  Interpretation: rational 2-torsion point on the elliptic curve")
    print(f"  CM: {mod2_cm}, Non-CM: {len(mod2_forms)-mod2_cm}")

    # Mod-3 starvation
    mod3_forms = [f for f in results["starved_forms"] if "3" in f["starvation"]]
    if mod3_forms:
        print(f"\nMOD-3 STARVATION: {len(mod3_forms)} forms")
        print(f"  Interpretation: likely rational 3-isogeny (Borel mod-3 image)")
        for f in mod3_forms[:10]:
            info = f["starvation"]["3"]
            print(f"  {f['label']:<22} classes={info['classes']}, "
                  f"pattern={info.get('pattern', '?')}")

    # Large-prime starvation (the interesting stuff)
    interesting = results["interesting_patterns"]
    if interesting:
        print(f"\nNON-CM LARGE-PRIME STARVATION ({len(interesting)} forms):")
        print("-" * 75)
        for f in sorted(interesting,
                        key=lambda x: min(v["ratio"] for v in x["starvation"].values())):
            large = {ell: v for ell, v in f["starvation"].items() if int(ell) >= 5}
            for ell, v in sorted(large.items(), key=lambda x: x[1]["ratio"]):
                print(f"  {f['label']:<22} mod {ell}: {v['classes_hit']}/{int(ell)} "
                      f"= {v['ratio']:.3f}")
                print(f"    Classes: {v['classes']}")
                print(f"    Missing: {v['missing']}")
                if v.get("pattern"):
                    print(f"    Pattern: {v['pattern']}")

    # CM forms with large-prime starvation
    cm_large = [f for f in results["starved_forms"]
                if f.get("is_cm") and any(int(ell) >= 5 for ell in f["starvation"])]
    if cm_large:
        print(f"\nCM FORMS WITH LARGE-PRIME STARVATION ({len(cm_large)} forms):")
        for f in sorted(cm_large[:15],
                        key=lambda x: min(v["ratio"] for v in x["starvation"].values())):
            large = {ell: v for ell, v in f["starvation"].items() if int(ell) >= 5}
            for ell, v in sorted(large.items(), key=lambda x: x[1]["ratio"]):
                print(f"  {f['label']:<22} mod {ell}: {v['classes_hit']}/{int(ell)} "
                      f"= {v['ratio']:.3f}, pattern={v.get('pattern','?')}")

    # Maass
    maass = results.get("maass_analysis", {})
    print(f"\nMAASS: {maass.get('verdict', maass.get('error', 'N/A'))}")


def main():
    print("C02: Residue Class Starvation Scan")
    print(f"DB: {DB_PATH}")
    print()

    t0 = time.time()
    results = scan()
    analyze_maass(results)
    results["metadata"]["elapsed_seconds"] = round(time.time() - t0, 1)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved: {OUTPUT_PATH}")

    print_report(results)


if __name__ == "__main__":
    main()
