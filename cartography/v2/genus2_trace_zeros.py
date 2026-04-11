"""
Genus-2 Trace Zero Density by Sato-Tate Group
===============================================
For EC, CM curves have a_p=0 at ~50% of primes (inert primes).
What's the zero density for genus-2 traces by ST group?

Data: g2c-data/gce_1000000_lmfdb.txt (66K curves, LMFDB postgres envelope)
Format per gce_record_format.txt:
  disc:cond:hash:min_eqn:disc_sign:igusa_clebsch:root_number:bad_lfactors:
  st_group:aut_grp:geom_aut_grp:torsion:two_selmer_rank:has_square_sha:
  locally_solvable:globally_solvable:good_lfactors

good_lfactors entries: [p, a1, a2] where a1 = trace of Frobenius
"""
import json
import ast
import re
import os
import sys
from collections import defaultdict
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
OUT_FILE = Path(__file__).resolve().parent / "genus2_trace_zeros_results.json"


def parse_good_lfactors(raw: str):
    """Parse the good_lfactors field: [[p,a1,a2],[p,a1,a2],...]"""
    # The field is the last colon-separated entry; it's a nested list
    # Format: [[2,3,5],[3,2,1],...]
    try:
        data = ast.literal_eval(raw)
        return data
    except Exception:
        return []


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found")
        sys.exit(1)

    # Accumulators per ST group
    st_zero_fracs = defaultdict(list)  # st_group -> list of zero fractions per curve
    st_counts = defaultdict(int)
    parse_errors = 0
    total = 0

    with open(DATA_FILE, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total += 1

            parts = line.split(":")
            # Fields by index (0-based):
            # 0:disc 1:cond 2:hash 3:min_eqn 4:disc_sign 5:igusa_clebsch
            # 6:root_number 7:bad_lfactors 8:st_group 9:aut_grp 10:geom_aut_grp
            # 11:torsion 12:two_selmer_rank 13:has_square_sha 14:locally_solvable
            # 15:globally_solvable 16:good_lfactors
            #
            # But min_eqn and igusa_clebsch contain colons inside brackets!
            # Need smarter parsing.

            # Rejoin and split carefully: find field boundaries
            # Strategy: regex to extract st_group and good_lfactors
            pass

    # The colon-delimited format is tricky because list fields contain colons
    # Better approach: parse with bracket awareness
    print(f"Parsing {DATA_FILE}...")

    st_zero_fracs = defaultdict(list)
    st_counts = defaultdict(int)
    st_trace_stats = defaultdict(lambda: {"n_primes": 0, "n_zeros": 0})
    curve_details = []
    parse_errors = 0

    with open(DATA_FILE, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            # Parse with bracket awareness
            # Split on colons that are NOT inside brackets
            fields = []
            depth = 0
            current = []
            for ch in line:
                if ch in "([":
                    depth += 1
                    current.append(ch)
                elif ch in ")]":
                    depth -= 1
                    current.append(ch)
                elif ch == ":" and depth == 0:
                    fields.append("".join(current))
                    current = []
                else:
                    current.append(ch)
            fields.append("".join(current))

            if len(fields) < 17:
                parse_errors += 1
                continue

            st_group = fields[8]
            good_lfactors_raw = fields[16]

            traces = parse_good_lfactors(good_lfactors_raw)
            if not traces:
                parse_errors += 1
                continue

            # Extract a1 (trace) for each prime
            n_primes = len(traces)
            n_zeros = sum(1 for entry in traces if len(entry) >= 2 and entry[1] == 0)
            zero_frac = n_zeros / n_primes if n_primes > 0 else 0.0

            st_zero_fracs[st_group].append(zero_frac)
            st_counts[st_group] += 1
            st_trace_stats[st_group]["n_primes"] += n_primes
            st_trace_stats[st_group]["n_zeros"] += n_zeros

            if line_num % 10000 == 0:
                print(f"  ...{line_num} curves processed")

    print(f"\nTotal lines: {line_num}")
    print(f"Parse errors: {parse_errors}")
    print(f"ST groups found: {len(st_zero_fracs)}")

    # Compute summary statistics per ST group
    results = {}
    print(f"\n{'ST Group':<20} {'Count':>7} {'Mean Zero%':>10} {'Median%':>9} {'Min%':>7} {'Max%':>7} {'Agg Zero%':>10}")
    print("-" * 80)

    for st in sorted(st_zero_fracs.keys(), key=lambda s: -len(st_zero_fracs[s])):
        fracs = st_zero_fracs[st]
        fracs_sorted = sorted(fracs)
        n = len(fracs)
        mean_frac = sum(fracs) / n
        median_frac = fracs_sorted[n // 2]
        min_frac = fracs_sorted[0]
        max_frac = fracs_sorted[-1]
        agg_zero_frac = st_trace_stats[st]["n_zeros"] / st_trace_stats[st]["n_primes"]

        results[st] = {
            "count": n,
            "mean_zero_fraction": round(mean_frac, 6),
            "median_zero_fraction": round(median_frac, 6),
            "min_zero_fraction": round(min_frac, 6),
            "max_zero_fraction": round(max_frac, 6),
            "aggregate_zero_fraction": round(agg_zero_frac, 6),
            "total_primes": st_trace_stats[st]["n_primes"],
            "total_zeros": st_trace_stats[st]["n_zeros"],
        }

        print(f"{st:<20} {n:>7} {mean_frac*100:>9.3f}% {median_frac*100:>8.3f}% {min_frac*100:>6.3f}% {max_frac*100:>6.3f}% {agg_zero_frac*100:>9.3f}%")

    # EC comparison context
    ec_comparison = {
        "non_CM": "~0% trace zeros (a_p=0 is rare, density 0 by Serre)",
        "CM": "~50% trace zeros (inert primes have a_p=0)",
    }

    # Group classification
    # USp(4) = generic (no extra endomorphisms)
    # Others have real/complex multiplication
    group_classification = {
        "USp(4)": "generic (no extra endomorphisms)",
        "N(U(1))": "RM by sqrt(d), abelian surface with real multiplication",
        "SU(2)": "QM, abelian surface is isogenous to square of CM elliptic curve",
        "U(1)": "CM, abelian surface has complex multiplication",
        "F": "splits as product of non-isogenous non-CM elliptic curves",
        "F_a": "splits as product of non-isogenous elliptic curves, one CM",
        "F_ab": "splits as product of non-isogenous CM elliptic curves",
        "F_ac": "splits as product of CM elliptic curves with same CM field",
        "E_1": "splits as square of non-CM elliptic curve",
        "E_2": "splits as square of non-CM elliptic curve (different twist)",
        "E_3": "splits as square of non-CM elliptic curve (cubic twist)",
        "E_4": "splits as square of non-CM elliptic curve (quartic twist)",
        "E_6": "splits as square of non-CM elliptic curve (sextic twist)",
        "J(E_1)": "splits as square of CM elliptic curve",
        "J(E_2)": "splits as square of CM elliptic curve (quadratic twist)",
        "J(E_3)": "splits as square of CM elliptic curve (cubic twist)",
        "J(E_4)": "splits as square of CM elliptic curve (quartic twist)",
        "J(E_6)": "splits as square of CM elliptic curve (sextic twist)",
        "G_{3,3}": "genus 2, geometric automorphisms order 3",
        "N(G_{3,3})": "normalizer of G_{3,3}",
        "G_{1,3}": "genus 2, geometric automorphisms",
        "N(G_{1,3})": "normalizer of G_{1,3}",
        "U(1)_2": "CM type",
        "SU(2)_2": "QM type",
    }

    output = {
        "description": "Genus-2 trace zero density by Sato-Tate group",
        "data_source": "LMFDB g2c database (gce_1000000_lmfdb.txt)",
        "total_curves_parsed": sum(st_counts.values()),
        "parse_errors": parse_errors,
        "ec_comparison": ec_comparison,
        "interpretation": {
            "USp(4)_expected": "Low zero density (~generic random matrix prediction)",
            "split_CM_expected": "Higher zero density from CM elliptic curve factors",
            "key_question": "Does genus-2 CM/RM show 50% analog or different pattern?",
        },
        "results_by_st_group": results,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
