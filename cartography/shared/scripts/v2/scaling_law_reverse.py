"""
Scaling Law in Reverse: Fungrim-to-LMFDB Genus-2 Curves
========================================================
Challenge: C11 showed OEIS algebraic families enriched in mod-p fingerprint
matches with enrichment growing monotonically with prime. Is this universal
across databases, or OEIS-specific?

Test: compute mod-p fingerprints on genus-2 a_p sequences grouped by:
  (a) Sato-Tate group (algebraic family grouping)
  (b) Conductor range bins (arithmetic grouping)
  (c) Endomorphism algebra type (Q, RM, CM, QM)
Compare within-group match rates vs random baseline at primes 2,3,5,7,11.

If enrichment scales with prime for genus-2 families too, the scaling law
is universal (algebraic structure -> mod-p enrichment). If it flatlines,
the law is OEIS-specific (integer sequence recurrences).

Usage:
    python scaling_law_reverse.py
"""

import json
import math
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
G2C_LMFDB = ROOT / "cartography" / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
G2C_CURVES_JSON = ROOT / "cartography" / "genus2" / "data" / "genus2_curves.json"
FUNGRIM_INDEX = ROOT / "cartography" / "fungrim" / "data" / "fungrim_index.json"
FUNGRIM_FORMULAS_DIR = ROOT / "cartography" / "fungrim" / "data" / "pygrim" / "formulas"
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OEIS_FORMULAS = ROOT / "cartography" / "oeis" / "data" / "oeis_formulas.jsonl"
C11_RESULTS = V2_DIR / "algebraic_dna_fungrim_results.json"
C11_BATTERY = V2_DIR / "scaling_law_battery_results.json"
OUT_FILE = V2_DIR / "scaling_law_reverse_results.json"

PRIMES = [2, 3, 5, 7, 11]
FINGERPRINT_LEN = 20  # positions to compare
random.seed(42)

# ---------------------------------------------------------------------------
# Genus-2 curve loading
# ---------------------------------------------------------------------------
def parse_g2c_lmfdb():
    """
    Parse gce_1000000_lmfdb.txt.
    Format per gce_record_format.txt:
      disc : cond : hash : min_eqn : disc_sign : igusa_clebsch :
      root_number : bad_lfactors : st_group : aut_grp : geom_aut_grp :
      torsion : two_selmer_rank : has_square_sha : locally_solvable :
      globally_solvable : good_lfactors

    good_lfactors is a list [[p, a1_p, a2_p], ...]
    We extract: conductor, st_group, aut_grp, geom_aut_grp, good_lfactors.
    """
    curves = []
    print(f"  Loading genus-2 curves from {G2C_LMFDB.name}...")

    with open(str(G2C_LMFDB), "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            fields = line.split(":")
            if len(fields) < 17:
                continue

            try:
                cond = int(fields[1])
                st_group = fields[8].strip()
                aut_grp = fields[9].strip()
                geom_aut_grp = fields[10].strip()

                # Parse good_lfactors: [[p, a1_p, a2_p], ...]
                gf_str = fields[16].strip()
                # It's Python list syntax
                good_lfactors = eval(gf_str)

                # Extract a_p sequence (a1_p values at good primes)
                a_p_dict = {}
                for entry in good_lfactors:
                    if len(entry) >= 2:
                        p = entry[0]
                        a1_p = entry[1]
                        a_p_dict[p] = a1_p

                curves.append({
                    "conductor": cond,
                    "st_group": st_group,
                    "aut_grp": aut_grp,
                    "geom_aut_grp": geom_aut_grp,
                    "a_p": a_p_dict,
                    "good_primes": sorted(a_p_dict.keys()),
                })
            except Exception:
                continue

    print(f"  Loaded {len(curves)} curves")
    return curves


def classify_endomorphism(st_group, geom_aut_grp):
    """
    Classify endomorphism algebra from Sato-Tate group and geometric
    automorphism group.

    Classification:
    - USp(4) -> generic (End = Q)
    - G_{3,3}, N(G_{3,3}) -> RM (real multiplication)
    - E_1, E_2, E_3, E_4, E_6 -> CM (complex multiplication / special)
    - J(E_*) variants -> QM (quaternion multiplication)
    - Others -> by geom_aut_grp size
    """
    st = st_group.strip()

    # CM indicators: E_n groups have extra endomorphisms
    if st.startswith("E_"):
        return "CM"
    if st.startswith("J(E_"):
        return "QM"
    if st in ("F", "F_a", "F_ab", "F_ac", "F_{a,b}"):
        return "CM"
    if st in ("G_{3,3}", "N(G_{3,3})", "G_{1,3}"):
        return "RM"
    if st == "USp(4)":
        return "Q"
    if st.startswith("J("):
        return "QM"
    if st.startswith("C"):
        return "CM"
    if st.startswith("D"):
        return "RM"

    # Fallback: large geometric automorphism group -> CM
    try:
        parts = geom_aut_grp.strip("[]").split(",")
        order = int(parts[0])
        if order > 4:
            return "CM"
        elif order > 2:
            return "RM"
    except Exception:
        pass

    return "Q"


# ---------------------------------------------------------------------------
# Mod-p fingerprint machinery
# ---------------------------------------------------------------------------
def a_p_fingerprint(a_p_dict, p_mod, good_primes, length=FINGERPRINT_LEN):
    """
    Compute mod-p_mod fingerprint from a_p values at good primes.
    Uses the first `length` good primes as the sequence.
    """
    # Get a_p values at the first `length` good primes
    vals = []
    for gp in good_primes[:length]:
        if gp in a_p_dict:
            vals.append(a_p_dict[gp])

    if len(vals) < 5:
        return None

    return tuple(v % p_mod for v in vals)


def compute_enrichment(group_fps, all_fps, primes=PRIMES, n_random=10000):
    """
    Compare within-group fingerprint match rate vs random baseline.

    group_fps: list of fingerprint dicts (one per curve in group)
    all_fps: list of ALL fingerprint dicts (for random baseline)

    Returns: {p: {family_rate, random_rate, enrichment}} for each prime
    """
    results = {}

    for p in primes:
        # Within-group: all pairs
        group_matches = 0
        group_pairs = 0

        fps_at_p = [fp.get(p) for fp in group_fps if fp and p in fp]
        fps_at_p = [f for f in fps_at_p if f is not None]

        n = len(fps_at_p)
        if n < 2:
            continue

        # Sample pairs if too many
        max_pairs = min(n * (n - 1) // 2, 50000)
        if n * (n - 1) // 2 <= 50000:
            for i in range(n):
                for j in range(i + 1, n):
                    min_len = min(len(fps_at_p[i]), len(fps_at_p[j]))
                    if min_len == 0:
                        continue
                    match = all(fps_at_p[i][k] == fps_at_p[j][k] for k in range(min_len))
                    if match:
                        group_matches += 1
                    group_pairs += 1
        else:
            for _ in range(max_pairs):
                i, j = random.sample(range(n), 2)
                min_len = min(len(fps_at_p[i]), len(fps_at_p[j]))
                if min_len == 0:
                    continue
                match = all(fps_at_p[i][k] == fps_at_p[j][k] for k in range(min_len))
                if match:
                    group_matches += 1
                group_pairs += 1

        family_rate = group_matches / group_pairs if group_pairs > 0 else 0

        # Random baseline: pairs from all_fps
        all_at_p = [fp.get(p) for fp in all_fps if fp and p in fp]
        all_at_p = [f for f in all_at_p if f is not None]

        random_matches = 0
        random_pairs = 0
        n_rand_pairs = min(n_random, len(all_at_p) * (len(all_at_p) - 1) // 2)

        for _ in range(n_rand_pairs):
            i, j = random.sample(range(len(all_at_p)), 2)
            min_len = min(len(all_at_p[i]), len(all_at_p[j]))
            if min_len == 0:
                continue
            match = all(all_at_p[i][k] == all_at_p[j][k] for k in range(min_len))
            if match:
                random_matches += 1
            random_pairs += 1

        random_rate = random_matches / random_pairs if random_pairs > 0 else 0

        enrichment = family_rate / random_rate if random_rate > 0 else (
            float("inf") if family_rate > 0 else 1.0
        )

        results[str(p)] = {
            "family_rate": family_rate,
            "random_rate": random_rate,
            "enrichment": enrichment,
            "family_pairs": group_pairs,
            "random_pairs": random_pairs,
            "family_matches": group_matches,
            "random_matches": random_matches,
            "group_size": n,
        }

    return results


def compute_sharing_enrichment(group_fps, all_fps, primes=PRIMES, n_random=10000):
    """
    Softer metric: average fraction of positions matching (sharing rate),
    not just exact matches.
    """
    results = {}

    for p in primes:
        fps_at_p = [fp.get(p) for fp in group_fps if fp and p in fp]
        fps_at_p = [f for f in fps_at_p if f is not None]

        n = len(fps_at_p)
        if n < 2:
            continue

        # Within-group sharing
        group_sharing = []
        max_pairs = min(n * (n - 1) // 2, 20000)

        if n * (n - 1) // 2 <= 20000:
            for i in range(n):
                for j in range(i + 1, n):
                    min_len = min(len(fps_at_p[i]), len(fps_at_p[j]))
                    if min_len == 0:
                        continue
                    matches = sum(1 for k in range(min_len) if fps_at_p[i][k] == fps_at_p[j][k])
                    group_sharing.append(matches / min_len)
        else:
            for _ in range(max_pairs):
                i, j = random.sample(range(n), 2)
                min_len = min(len(fps_at_p[i]), len(fps_at_p[j]))
                if min_len == 0:
                    continue
                matches = sum(1 for k in range(min_len) if fps_at_p[i][k] == fps_at_p[j][k])
                group_sharing.append(matches / min_len)

        # Random baseline
        all_at_p = [fp.get(p) for fp in all_fps if fp and p in fp]
        all_at_p = [f for f in all_at_p if f is not None]

        random_sharing = []
        n_rand = min(n_random, len(all_at_p) * (len(all_at_p) - 1) // 2)
        for _ in range(n_rand):
            i, j = random.sample(range(len(all_at_p)), 2)
            min_len = min(len(all_at_p[i]), len(all_at_p[j]))
            if min_len == 0:
                continue
            matches = sum(1 for k in range(min_len) if all_at_p[i][k] == all_at_p[j][k])
            random_sharing.append(matches / min_len)

        fam_mean = sum(group_sharing) / len(group_sharing) if group_sharing else 0
        rand_mean = sum(random_sharing) / len(random_sharing) if random_sharing else 0
        expected = 1.0 / p  # expected sharing rate for uniform random mod p

        results[str(p)] = {
            "family_sharing": fam_mean,
            "random_sharing": rand_mean,
            "expected_random": expected,
            "enrichment_vs_random": fam_mean / rand_mean if rand_mean > 0 else float("inf"),
            "enrichment_vs_expected": fam_mean / expected,
            "group_size": n,
            "n_pairs": len(group_sharing),
        }

    return results


# ---------------------------------------------------------------------------
# Group curves
# ---------------------------------------------------------------------------
def group_by_st(curves):
    """Group curves by Sato-Tate group."""
    groups = defaultdict(list)
    for c in curves:
        groups[c["st_group"]].append(c)
    return dict(groups)


def group_by_conductor_bin(curves, n_bins=8):
    """Group curves by conductor range (log-spaced bins)."""
    conductors = [c["conductor"] for c in curves]
    if not conductors:
        return {}
    min_c = min(conductors)
    max_c = max(conductors)
    if min_c <= 0:
        min_c = 1

    log_min = math.log10(min_c)
    log_max = math.log10(max_c + 1)
    bin_width = (log_max - log_min) / n_bins

    groups = defaultdict(list)
    for c in curves:
        cond = max(c["conductor"], 1)
        bin_idx = min(int((math.log10(cond) - log_min) / bin_width), n_bins - 1)
        lo = 10 ** (log_min + bin_idx * bin_width)
        hi = 10 ** (log_min + (bin_idx + 1) * bin_width)
        label = f"[{lo:.0f}, {hi:.0f})"
        groups[label].append(c)

    return dict(groups)


def group_by_endomorphism(curves):
    """Group curves by endomorphism algebra type."""
    groups = defaultdict(list)
    for c in curves:
        endo = classify_endomorphism(c["st_group"], c["geom_aut_grp"])
        groups[endo].append(c)
    return dict(groups)


# ---------------------------------------------------------------------------
# Compute fingerprints for a group of curves
# ---------------------------------------------------------------------------
def compute_curve_fingerprints(curves):
    """Compute mod-p fingerprints for each curve's a_p sequence."""
    fps = []
    for c in curves:
        fp = {}
        for p in PRIMES:
            val = a_p_fingerprint(c["a_p"], p, c["good_primes"], FINGERPRINT_LEN)
            if val is not None:
                fp[p] = val
        if fp:
            fps.append(fp)
    return fps


# ---------------------------------------------------------------------------
# OEIS baseline (reproduce C11 for comparison)
# ---------------------------------------------------------------------------
def load_oeis_terms(max_seqs=50000):
    """Load OEIS sequences from stripped_new.txt."""
    seqs = {}
    if not OEIS_STRIPPED.exists():
        print("  WARNING: OEIS stripped file not found")
        return seqs

    print(f"  Loading OEIS terms from {OEIS_STRIPPED.name}...")
    with open(str(OEIS_STRIPPED), "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: A000001 ,0,1,1,...
            m = re.match(r"(A\d+)\s*,?(.+)", line)
            if not m:
                parts = line.split(" ", 1)
                if len(parts) < 2:
                    continue
                seq_id = parts[0]
                terms_str = parts[1].strip().strip(",")
            else:
                seq_id = m.group(1)
                terms_str = m.group(2).strip().strip(",")

            if not terms_str:
                continue
            try:
                terms = [int(x) for x in terms_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(terms) >= 10:
                seqs[seq_id] = terms
            if len(seqs) >= max_seqs:
                break

    print(f"  Loaded {len(seqs)} OEIS sequences")
    return seqs


FUNGRIM_KEYWORD_MAP = {
    "fibonacci": ["fibonacci", "lucas", "golden ratio", "phi", "F(n)", "L(n)"],
    "golden_ratio": ["golden ratio", "phi", "(1+sqrt(5))/2"],
    "bernoulli_numbers": ["bernoulli", "B(n)", "B_n", "Bernoulli number"],
    "bell_numbers": ["bell number", "Bell(n)"],
    "partitions": ["partition", "p(n)", "partitions of n"],
    "dedekind_eta": ["dedekind eta", "eta function", "eta("],
    "eisenstein": ["eisenstein", "E_2", "E_4", "E_6", "E_8"],
    "modular_j": ["j-invariant", "j-function", "klein j", "j(tau)"],
    "riemann_zeta": ["zeta(", "riemann zeta", "zeta function"],
    "jacobi_theta": ["jacobi theta", "theta function", "theta("],
    "chebyshev": ["chebyshev", "Chebyshev"],
    "prime_numbers": ["prime", "p(n)", "pi(n)", "primepi"],
    "totient": ["euler totient", "phi(n)", "euler phi"],
    "stirling_numbers": ["stirling number", "stirling("],
    "gamma": ["gamma function", "Gamma("],
    "exp": ["exponential", "e^", "exp("],
    "sine": ["sin(", "cos(", "trigonometric"],
    "atan": ["arctan", "atan("],
    "log": ["logarithm", "log(", "ln("],
    "factorial": ["factorial", "n!", "binomial"],
    "dirichlet": ["dirichlet", "L-function", "L-series"],
    "modular_transformations": ["modular form", "modular function", "cusp form"],
}


def extract_fungrim_oeis_links():
    """Extract OEIS A-number references from Fungrim source files + keyword bridging."""
    module_to_oeis = defaultdict(set)
    oeis_to_modules = defaultdict(set)

    sloane_re = re.compile(r'SloaneA\(\s*"?(A?\d+)"?\s*')
    oeis_url_re = re.compile(r'oeis\.org/(A\d+)')

    if FUNGRIM_FORMULAS_DIR.exists():
        for py_file in sorted(FUNGRIM_FORMULAS_DIR.glob("*.py")):
            module_name = py_file.stem
            text = py_file.read_text(encoding="utf-8", errors="ignore")

            for m in sloane_re.finditer(text):
                raw = m.group(1)
                seq_id = raw if raw.startswith("A") else f"A{int(raw):06d}"
                oeis_to_modules[seq_id].add(module_name)
                module_to_oeis[module_name].add(seq_id)

            for m in oeis_url_re.finditer(text):
                seq_id = m.group(1)
                oeis_to_modules[seq_id].add(module_name)
                module_to_oeis[module_name].add(seq_id)

    # Keyword bridging: scan OEIS formula text for Fungrim-related keywords
    if OEIS_FORMULAS.exists():
        print("  Scanning OEIS formula text for keyword bridges...")
        n_new = 0
        with open(str(OEIS_FORMULAS), "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                seq_id = rec.get("seq_id", "")
                formula = rec.get("formula", "").lower()
                if not formula or not seq_id:
                    continue
                for module, keywords in FUNGRIM_KEYWORD_MAP.items():
                    for kw in keywords:
                        if kw.lower() in formula:
                            if module not in oeis_to_modules.get(seq_id, set()):
                                oeis_to_modules[seq_id].add(module)
                                module_to_oeis[module].add(seq_id)
                                n_new += 1
                            break
        print(f"  Keyword bridging added {n_new} new (seq, module) links")

    return (
        {k: sorted(v) for k, v in oeis_to_modules.items()},
        {k: sorted(v) for k, v in module_to_oeis.items()},
    )


def oeis_module_enrichment(oeis_terms, oeis_to_modules, module_to_oeis, n_random=10000):
    """
    Compute within-module fingerprint enrichment for OEIS sequences
    (C11 reproduction for comparison).
    """
    # Build fingerprints for all OEIS sequences that have Fungrim links
    linked_seqs = set(oeis_to_modules.keys())
    all_oeis_fps = {}

    for seq_id, terms in oeis_terms.items():
        fp = {}
        for p in PRIMES:
            usable = terms[:FINGERPRINT_LEN]
            if len(usable) >= 5:
                fp[p] = tuple(t % p for t in usable)
        if fp:
            all_oeis_fps[seq_id] = fp

    # Group by Fungrim module
    module_results = {}
    all_fps_list = list(all_oeis_fps.values())

    for module, seq_ids in sorted(module_to_oeis.items()):
        group_fps = [all_oeis_fps[s] for s in seq_ids if s in all_oeis_fps]
        if len(group_fps) < 5:
            continue

        enrichment = compute_sharing_enrichment(group_fps, all_fps_list, n_random=n_random)
        if enrichment:
            module_results[module] = {
                "n_sequences": len(group_fps),
                "enrichment": enrichment,
            }

    return module_results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 72)
    print("SCALING LAW IN REVERSE: Fungrim-to-LMFDB Genus-2 Curves")
    print("=" * 72)

    results = {
        "challenge": "C11_reverse",
        "title": "Scaling Law in Reverse: Fungrim-to-LMFDB",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    # -----------------------------------------------------------------------
    # 1. Load genus-2 curves
    # -----------------------------------------------------------------------
    print("\n[1] Loading genus-2 curves...")
    curves = parse_g2c_lmfdb()

    if not curves:
        print("  FATAL: No curves loaded")
        return

    # Sample if needed (66K is manageable but pairwise is O(n^2))
    # We'll sample for the random baseline but keep all for grouping
    MAX_CURVES = 10000
    if len(curves) > MAX_CURVES:
        print(f"  Sampling {MAX_CURVES} curves from {len(curves)} for efficiency...")
        sampled_curves = random.sample(curves, MAX_CURVES)
    else:
        sampled_curves = curves

    results["n_curves_total"] = len(curves)
    results["n_curves_sampled"] = len(sampled_curves)

    # -----------------------------------------------------------------------
    # 2. Compute fingerprints for all sampled curves
    # -----------------------------------------------------------------------
    print("\n[2] Computing fingerprints for genus-2 a_p sequences...")
    all_g2_fps = compute_curve_fingerprints(sampled_curves)
    print(f"  Computed fingerprints for {len(all_g2_fps)} curves")

    # -----------------------------------------------------------------------
    # 3. Group by Sato-Tate group
    # -----------------------------------------------------------------------
    print("\n[3] Grouping by Sato-Tate group...")
    st_groups = group_by_st(sampled_curves)
    st_results = {}

    for st_name, group_curves in sorted(st_groups.items(), key=lambda x: -len(x[1])):
        n = len(group_curves)
        if n < 5:
            continue
        print(f"  ST group '{st_name}': {n} curves")
        group_fps = compute_curve_fingerprints(group_curves)

        exact_enrich = compute_enrichment(group_fps, all_g2_fps, n_random=10000)
        sharing_enrich = compute_sharing_enrichment(group_fps, all_g2_fps, n_random=10000)

        st_results[st_name] = {
            "n_curves": n,
            "exact_enrichment": exact_enrich,
            "sharing_enrichment": sharing_enrich,
        }

    results["sato_tate_groups"] = st_results

    # -----------------------------------------------------------------------
    # 4. Group by conductor bin
    # -----------------------------------------------------------------------
    print("\n[4] Grouping by conductor range...")
    cond_groups = group_by_conductor_bin(sampled_curves, n_bins=8)
    cond_results = {}

    for label, group_curves in sorted(cond_groups.items()):
        n = len(group_curves)
        if n < 10:
            continue
        print(f"  Conductor bin '{label}': {n} curves")
        group_fps = compute_curve_fingerprints(group_curves)

        exact_enrich = compute_enrichment(group_fps, all_g2_fps, n_random=10000)
        sharing_enrich = compute_sharing_enrichment(group_fps, all_g2_fps, n_random=10000)

        cond_results[label] = {
            "n_curves": n,
            "exact_enrichment": exact_enrich,
            "sharing_enrichment": sharing_enrich,
        }

    results["conductor_bins"] = cond_results

    # -----------------------------------------------------------------------
    # 5. Group by endomorphism algebra
    # -----------------------------------------------------------------------
    print("\n[5] Grouping by endomorphism algebra...")
    endo_groups = group_by_endomorphism(sampled_curves)
    endo_results = {}

    for endo_type, group_curves in sorted(endo_groups.items()):
        n = len(group_curves)
        if n < 5:
            continue
        print(f"  Endomorphism type '{endo_type}': {n} curves")
        group_fps = compute_curve_fingerprints(group_curves)

        exact_enrich = compute_enrichment(group_fps, all_g2_fps, n_random=10000)
        sharing_enrich = compute_sharing_enrichment(group_fps, all_g2_fps, n_random=10000)

        endo_results[endo_type] = {
            "n_curves": n,
            "exact_enrichment": exact_enrich,
            "sharing_enrichment": sharing_enrich,
        }

    results["endomorphism_groups"] = endo_results

    # -----------------------------------------------------------------------
    # 6. OEIS Fungrim module enrichment (C11 comparison)
    # -----------------------------------------------------------------------
    print("\n[6] OEIS Fungrim module enrichment (C11 comparison)...")
    oeis_terms = load_oeis_terms(max_seqs=50000)
    oeis_to_modules, module_to_oeis = extract_fungrim_oeis_links()

    print(f"  Fungrim links: {len(oeis_to_modules)} OEIS sequences, {len(module_to_oeis)} modules")

    oeis_mod_results = oeis_module_enrichment(oeis_terms, oeis_to_modules, module_to_oeis)
    results["oeis_fungrim_modules"] = oeis_mod_results

    # -----------------------------------------------------------------------
    # 7. Summary: enrichment-vs-prime slopes
    # -----------------------------------------------------------------------
    print("\n[7] Computing enrichment-vs-prime slopes...")

    def extract_slope(enrichment_dict, metric="sharing_enrichment", field="enrichment_vs_random"):
        """Extract enrichment values at each prime and compute log-log slope."""
        points = []
        for p in PRIMES:
            sp = str(p)
            if sp in enrichment_dict.get(metric, {}):
                val = enrichment_dict[metric][sp].get(field, 0)
                if val > 0 and val != float("inf"):
                    points.append((math.log(p), math.log(val)))

        if len(points) < 2:
            return None, []

        # Simple linear regression on log-log
        n = len(points)
        sx = sum(x for x, y in points)
        sy = sum(y for x, y in points)
        sxx = sum(x * x for x, y in points)
        sxy = sum(x * y for x, y in points)

        denom = n * sxx - sx * sx
        if abs(denom) < 1e-15:
            return None, points

        slope = (n * sxy - sx * sy) / denom
        return slope, points

    summary = {
        "sato_tate": {},
        "conductor_bins": {},
        "endomorphism": {},
        "oeis_modules": {},
    }

    # ST group slopes
    for st_name, data in st_results.items():
        slope, pts = extract_slope(data)
        summary["sato_tate"][st_name] = {
            "slope": slope,
            "n_curves": data["n_curves"],
            "enrichment_curve": {
                str(PRIMES[i]): data["sharing_enrichment"].get(str(PRIMES[i]), {}).get("enrichment_vs_random", None)
                for i in range(len(PRIMES))
            },
        }

    # Conductor bin slopes
    for label, data in cond_results.items():
        slope, pts = extract_slope(data)
        summary["conductor_bins"][label] = {
            "slope": slope,
            "n_curves": data["n_curves"],
        }

    # Endomorphism slopes
    for endo, data in endo_results.items():
        slope, pts = extract_slope(data)
        summary["endomorphism"][endo] = {
            "slope": slope,
            "n_curves": data["n_curves"],
            "enrichment_curve": {
                str(PRIMES[i]): data["sharing_enrichment"].get(str(PRIMES[i]), {}).get("enrichment_vs_random", None)
                for i in range(len(PRIMES))
            },
        }

    # OEIS module slopes
    for module, data in oeis_mod_results.items():
        slope, pts = extract_slope(data, metric="enrichment", field="enrichment_vs_random")
        summary["oeis_modules"][module] = {
            "slope": slope,
            "n_sequences": data["n_sequences"],
        }

    results["slope_summary"] = summary

    # -----------------------------------------------------------------------
    # 8. Verdict
    # -----------------------------------------------------------------------
    print("\n[8] Verdict...")

    # Collect slopes
    st_slopes = [v["slope"] for v in summary["sato_tate"].values() if v["slope"] is not None]
    cond_slopes = [v["slope"] for v in summary["conductor_bins"].values() if v["slope"] is not None]
    endo_slopes = [v["slope"] for v in summary["endomorphism"].values() if v["slope"] is not None]
    oeis_slopes = [v["slope"] for v in summary["oeis_modules"].values() if v["slope"] is not None]

    mean_st = sum(st_slopes) / len(st_slopes) if st_slopes else 0
    mean_cond = sum(cond_slopes) / len(cond_slopes) if cond_slopes else 0
    mean_endo = sum(endo_slopes) / len(endo_slopes) if endo_slopes else 0
    mean_oeis = sum(oeis_slopes) / len(oeis_slopes) if oeis_slopes else 0

    verdict_lines = []
    verdict_lines.append(f"Mean log-log slope (enrichment vs prime):")
    verdict_lines.append(f"  Sato-Tate groups:  {mean_st:.4f} ({len(st_slopes)} groups)")
    verdict_lines.append(f"  Conductor bins:    {mean_cond:.4f} ({len(cond_slopes)} bins)")
    verdict_lines.append(f"  Endomorphism type: {mean_endo:.4f} ({len(endo_slopes)} types)")
    verdict_lines.append(f"  OEIS modules:      {mean_oeis:.4f} ({len(oeis_slopes)} modules)")

    # The scaling law says enrichment GROWS with prime (positive slope in log-log)
    # For genus-2, we expect:
    # - ST group enrichment: positive slope if universal
    # - Endomorphism enrichment: positive slope, stronger for CM
    # - Conductor bins: likely weak (conductor is arithmetic, not algebraic)

    # Use a softer threshold: positive slopes with magnitude > 0.03 count
    g2_has_scaling = mean_st > 0.03 or mean_endo > 0.03
    oeis_has_scaling = mean_oeis > 0.03

    # Also check: how many individual groups show positive slopes?
    n_positive_st = sum(1 for s in st_slopes if s > 0)
    n_positive_oeis = sum(1 for s in oeis_slopes if s > 0)
    n_positive_endo = sum(1 for s in endo_slopes if s > 0)

    verdict_lines.append(f"\nPositive slope counts:")
    verdict_lines.append(f"  ST groups: {n_positive_st}/{len(st_slopes)}")
    verdict_lines.append(f"  Endo types: {n_positive_endo}/{len(endo_slopes)}")
    verdict_lines.append(f"  OEIS modules: {n_positive_oeis}/{len(oeis_slopes)}")

    if g2_has_scaling and oeis_has_scaling:
        verdict = "UNIVERSAL: Scaling law appears in BOTH OEIS and genus-2 data"
    elif oeis_has_scaling and not g2_has_scaling:
        verdict = "OEIS-SPECIFIC: Scaling law in OEIS but NOT genus-2"
    elif g2_has_scaling and not oeis_has_scaling:
        verdict = "UNEXPECTED: Scaling law in genus-2 but NOT OEIS (check methodology)"
    else:
        verdict = "NEITHER: No clear scaling law detected"

    verdict_lines.append(f"\nVERDICT: {verdict}")

    # CM vs Q comparison
    cm_enrich = summary["endomorphism"].get("CM", {}).get("enrichment_curve", {})
    q_enrich = summary["endomorphism"].get("Q", {}).get("enrichment_curve", {})

    if cm_enrich and q_enrich:
        cm_vals = [v for v in cm_enrich.values() if v is not None and v != float("inf")]
        q_vals = [v for v in q_enrich.values() if v is not None and v != float("inf")]
        if cm_vals and q_vals:
            cm_mean = sum(cm_vals) / len(cm_vals)
            q_mean = sum(q_vals) / len(q_vals)
            verdict_lines.append(f"\nCM vs Q enrichment:")
            verdict_lines.append(f"  CM mean enrichment: {cm_mean:.4f}")
            verdict_lines.append(f"  Q  mean enrichment: {q_mean:.4f}")
            verdict_lines.append(f"  CM/Q ratio: {cm_mean/q_mean:.4f}" if q_mean > 0 else "  Q mean = 0")

    verdict_str = "\n".join(verdict_lines)
    print(verdict_str)
    results["verdict"] = verdict_str

    # -----------------------------------------------------------------------
    # Print enrichment tables
    # -----------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("ENRICHMENT-VS-PRIME TABLES")
    print("=" * 72)

    def print_enrichment_table(name, data_dict, metric_key="sharing_enrichment", field="enrichment_vs_random"):
        print(f"\n--- {name} ---")
        header = f"{'Group':<25} | " + " | ".join(f"p={p:>2}" for p in PRIMES) + " | slope"
        print(header)
        print("-" * len(header))
        for group_name, data in sorted(data_dict.items()):
            vals = []
            for p in PRIMES:
                sp = str(p)
                e = data.get(metric_key, data.get("enrichment", {}))
                if sp in e:
                    v = e[sp].get(field, 0)
                    if v == float("inf"):
                        vals.append("  inf")
                    else:
                        vals.append(f"{v:5.2f}")
                else:
                    vals.append("   --")

            slope_data = None
            for src in [summary.get("sato_tate", {}), summary.get("conductor_bins", {}),
                        summary.get("endomorphism", {}), summary.get("oeis_modules", {})]:
                if group_name in src:
                    slope_data = src[group_name].get("slope")
                    break

            slope_str = f"{slope_data:+.3f}" if slope_data is not None else "   --"
            print(f"{group_name:<25} | " + " | ".join(vals) + f" | {slope_str}")

    print_enrichment_table("Sato-Tate Groups", st_results)
    print_enrichment_table("Conductor Bins", cond_results)
    print_enrichment_table("Endomorphism Algebra", endo_results)
    print_enrichment_table("OEIS Fungrim Modules", oeis_mod_results, metric_key="enrichment")

    # -----------------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------------
    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)

    # Clean up infinities for JSON
    def clean_for_json(obj):
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(v) for v in obj]
        elif isinstance(obj, float):
            if math.isinf(obj):
                return "Infinity" if obj > 0 else "-Infinity"
            if math.isnan(obj):
                return "NaN"
            return obj
        return obj

    results = clean_for_json(results)

    with open(str(OUT_FILE), "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Results saved to {OUT_FILE}")
    print(f"  Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
