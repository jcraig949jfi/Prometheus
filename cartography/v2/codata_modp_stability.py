#!/usr/bin/env python3
"""
Charon — Mod-p fingerprint stability of CODATA physical constants.

For each dimensionless constant (no unit field), extract significant digits
as an integer, compute mod-p residues at p in {2,3,5,7,11}, then test
whether constants from the same physics domain share mod-p fingerprints
more than random.

Domain grouping: first token of the constant name (alpha, deuteron, electron,
fine-structure, helion, muon, neutron, proton, tau, triton, etc.).

Similarity metric: fraction of matching mod-p residues between two constants'
fingerprint vectors.  Within-group mean vs between-group mean gives the
enrichment ratio per prime and overall.
"""

import json
import itertools
import os
import re
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import numpy as np

# ── paths ────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent          # cartography/
DATA = REPO / "physics" / "data" / "codata" / "constants.json"
OUT  = Path(__file__).resolve().parent / "codata_modp_stability_results.json"

PRIMES = [2, 3, 5, 7, 11]


# ── helpers ──────────────────────────────────────────────────────────────
def extract_sig_digits(raw: str) -> int:
    """
    From value_raw like '7294.299 541 71' or '3.972 599 690 252',
    strip spaces, remove leading zeros, remove decimal point,
    and return the significant digits as an integer.
    """
    s = raw.strip()
    # Remove spaces within the number
    s = s.replace(" ", "")
    # Remove any exponent part (e.g. 'e-10')
    if "e" in s.lower():
        s = s[:s.lower().index("e")]
    # Remove decimal point
    s = s.replace(".", "")
    # Remove leading zeros / minus signs
    s = s.lstrip("0").lstrip("-").lstrip("0")
    if not s:
        return 0
    return int(s)


def classify_domain(name: str) -> str:
    """
    Assign a physics domain from the constant name.
    Uses first word, with some multi-word merges.
    """
    n = name.lower().strip()
    # Multi-word prefixes
    for prefix in [
        "alpha particle", "fine-structure", "inverse fine-structure",
        "sackur-tetrode", "weak mixing", "shielded helion",
        "shielded proton", "shielding difference",
        "w to z",
    ]:
        if n.startswith(prefix):
            return prefix
    return n.split("-")[0].split()[0]


def modp_fingerprint(sig_int: int, primes: list[int]) -> list[int]:
    """Return [sig_int mod p for p in primes]."""
    return [sig_int % p for p in primes]


def fingerprint_similarity(fp1: list[int], fp2: list[int]) -> float:
    """Fraction of matching residues."""
    return sum(a == b for a, b in zip(fp1, fp2)) / len(fp1)


def per_prime_match(fp1: list[int], fp2: list[int]) -> list[int]:
    """Return list of 0/1 for each prime position."""
    return [int(a == b) for a, b in zip(fp1, fp2)]


# ── main ─────────────────────────────────────────────────────────────────
def main():
    with open(DATA) as f:
        constants = json.load(f)

    # Filter to dimensionless (no unit key or empty unit)
    dimless = [c for c in constants if not c.get("unit")]
    print(f"Total constants: {len(constants)}, dimensionless: {len(dimless)}")

    # Build records
    records = []
    for c in dimless:
        raw = c.get("value_raw", str(c["value"]))
        sig = extract_sig_digits(raw)
        fp = modp_fingerprint(sig, PRIMES)
        domain = classify_domain(c["name"])
        records.append({
            "name": c["name"],
            "value": c["value"],
            "sig_digits_int": sig,
            "domain": domain,
            "fingerprint": fp,
        })

    # Group by domain
    groups = defaultdict(list)
    for r in records:
        groups[r["domain"]].append(r)

    print(f"Domains ({len(groups)}): {sorted(groups.keys())}")
    print(f"Group sizes: { {k: len(v) for k, v in sorted(groups.items())} }")

    # ── Compute within-group and between-group similarity ────────────
    # Per-prime accumulators
    n_primes = len(PRIMES)
    within_per_prime  = [[] for _ in range(n_primes)]
    between_per_prime = [[] for _ in range(n_primes)]
    within_overall  = []
    between_overall = []

    # Within-group pairs
    for domain, members in groups.items():
        if len(members) < 2:
            continue
        for a, b in itertools.combinations(members, 2):
            sim = fingerprint_similarity(a["fingerprint"], b["fingerprint"])
            within_overall.append(sim)
            matches = per_prime_match(a["fingerprint"], b["fingerprint"])
            for i, m in enumerate(matches):
                within_per_prime[i].append(m)

    # Between-group pairs (all pairs from different domains)
    for i, ri in enumerate(records):
        for j in range(i + 1, len(records)):
            rj = records[j]
            if ri["domain"] == rj["domain"]:
                continue
            sim = fingerprint_similarity(ri["fingerprint"], rj["fingerprint"])
            between_overall.append(sim)
            matches = per_prime_match(ri["fingerprint"], rj["fingerprint"])
            for k, m in enumerate(matches):
                between_per_prime[k].append(m)

    # ── Null model: permutation test ─────────────────────────────────
    rng = np.random.default_rng(42)
    N_PERM = 10000
    null_enrichments = {str(p): [] for p in PRIMES}
    null_enrichments["overall"] = []

    domain_labels = [r["domain"] for r in records]
    fps = [r["fingerprint"] for r in records]

    for _ in range(N_PERM):
        perm_labels = list(domain_labels)
        rng.shuffle(perm_labels)

        # Build shuffled groups
        perm_groups = defaultdict(list)
        for idx, lab in enumerate(perm_labels):
            perm_groups[lab].append(idx)

        # Within-group match rates under permutation
        pw_per_prime = [[] for _ in range(n_primes)]
        pw_overall = []
        for members in perm_groups.values():
            if len(members) < 2:
                continue
            for a, b in itertools.combinations(members, 2):
                sim = fingerprint_similarity(fps[a], fps[b])
                pw_overall.append(sim)
                matches = per_prime_match(fps[a], fps[b])
                for k, m in enumerate(matches):
                    pw_per_prime[k].append(m)

        # Between-group (complement)
        pb_per_prime = [[] for _ in range(n_primes)]
        pb_overall = []
        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                if perm_labels[i] == perm_labels[j]:
                    continue
                sim = fingerprint_similarity(fps[i], fps[j])
                pb_overall.append(sim)
                matches = per_prime_match(fps[i], fps[j])
                for k, m in enumerate(matches):
                    pb_per_prime[k].append(m)

        # Enrichment for this permutation
        for k, p in enumerate(PRIMES):
            w = np.mean(pw_per_prime[k]) if pw_per_prime[k] else 0
            b = np.mean(pb_per_prime[k]) if pb_per_prime[k] else 1e-12
            null_enrichments[str(p)].append(w / b if b > 0 else 1.0)
        w = np.mean(pw_overall) if pw_overall else 0
        b = np.mean(pb_overall) if pb_overall else 1e-12
        null_enrichments["overall"].append(w / b if b > 0 else 1.0)

    # ── Assemble results ─────────────────────────────────────────────
    results = {
        "description": "Mod-p fingerprint stability of CODATA dimensionless constants",
        "n_constants": len(dimless),
        "n_domains": len(groups),
        "primes": PRIMES,
        "domain_sizes": {k: len(v) for k, v in sorted(groups.items())},
        "per_prime": {},
        "overall": {},
        "null_permutations": N_PERM,
    }

    for k, p in enumerate(PRIMES):
        w_rate = float(np.mean(within_per_prime[k])) if within_per_prime[k] else 0
        b_rate = float(np.mean(between_per_prime[k])) if between_per_prime[k] else 0
        enrichment = w_rate / b_rate if b_rate > 0 else float("inf")
        null_dist = null_enrichments[str(p)]
        p_value = float(np.mean([1 if ne >= enrichment else 0 for ne in null_dist]))
        results["per_prime"][str(p)] = {
            "within_group_match_rate": round(w_rate, 6),
            "between_group_match_rate": round(b_rate, 6),
            "enrichment_ratio": round(enrichment, 6),
            "null_mean_enrichment": round(float(np.mean(null_dist)), 4),
            "null_std_enrichment": round(float(np.std(null_dist)), 4),
            "p_value": round(p_value, 4),
            "n_within_pairs": len(within_per_prime[k]),
            "n_between_pairs": len(between_per_prime[k]),
        }
        print(f"  p={p:2d}: within={w_rate:.4f}  between={b_rate:.4f}  "
              f"enrichment={enrichment:.4f}  p-val={p_value:.4f}")

    w_all = float(np.mean(within_overall)) if within_overall else 0
    b_all = float(np.mean(between_overall)) if between_overall else 0
    e_all = w_all / b_all if b_all > 0 else float("inf")
    null_dist_all = null_enrichments["overall"]
    p_val_all = float(np.mean([1 if ne >= e_all else 0 for ne in null_dist_all]))

    results["overall"] = {
        "within_group_mean_similarity": round(w_all, 6),
        "between_group_mean_similarity": round(b_all, 6),
        "enrichment_ratio": round(e_all, 6),
        "null_mean_enrichment": round(float(np.mean(null_dist_all)), 4),
        "null_std_enrichment": round(float(np.std(null_dist_all)), 4),
        "p_value": round(p_val_all, 4),
    }
    print(f"\n  OVERALL: within={w_all:.4f}  between={b_all:.4f}  "
          f"enrichment={e_all:.4f}  p-val={p_val_all:.4f}")

    # Per-domain detail
    domain_detail = {}
    for domain, members in sorted(groups.items()):
        fps_d = [m["fingerprint"] for m in members]
        if len(fps_d) < 2:
            domain_detail[domain] = {
                "n": len(fps_d),
                "note": "too few for pairwise comparison",
            }
            continue
        sims = []
        for a, b in itertools.combinations(fps_d, 2):
            sims.append(fingerprint_similarity(a, b))
        domain_detail[domain] = {
            "n": len(fps_d),
            "mean_internal_similarity": round(float(np.mean(sims)), 4),
            "std_internal_similarity": round(float(np.std(sims)), 4),
        }
    results["domain_detail"] = domain_detail

    # Constants table
    results["constants"] = [
        {
            "name": r["name"],
            "domain": r["domain"],
            "sig_digits_int": r["sig_digits_int"],
            "fingerprint": {str(p): r["fingerprint"][i] for i, p in enumerate(PRIMES)},
        }
        for r in records
    ]

    # Verdict
    sig_count = sum(
        1 for p in PRIMES
        if results["per_prime"][str(p)]["p_value"] < 0.05
    )
    if sig_count == 0 and p_val_all >= 0.05:
        verdict = "NO_SIGNAL"
        explanation = (
            "No prime shows statistically significant within-domain enrichment "
            "over random grouping. Mod-p residues of significant digits do not "
            "cluster by physics domain."
        )
    elif sig_count <= 1:
        verdict = "MARGINAL"
        explanation = (
            f"{sig_count}/5 primes show p<0.05; could be multiple-testing artifact."
        )
    else:
        verdict = "SIGNAL"
        explanation = (
            f"{sig_count}/5 primes show p<0.05; mod-p fingerprints cluster by domain."
        )
    results["verdict"] = verdict
    results["explanation"] = explanation

    print(f"\nVerdict: {verdict}")
    print(explanation)

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
