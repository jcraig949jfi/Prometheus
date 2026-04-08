"""
Sleeper Fingerprinter — Transform sleeping beauties and match to known hubs.
=============================================================================
For each OEIS sleeping beauty (high entropy, low connectivity), apply a battery
of mathematical transforms and check whether the result matches any known
sequence. Matches reveal hidden structure — a sleeper whose first-differences
are the primes is *not* actually isolated.

Uses dictionary lookup on tuple(first_8_terms) for O(1) matching per transform.

Usage:
    python sleeper_fingerprinter.py
"""

import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

# --- Imports from search_engine ---
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from search_engine import (
    _load_oeis, _oeis_cache,
    _load_oeis_crossrefs, _oeis_xref_cache, _oeis_xref_reverse,
    _load_oeis_names, _oeis_names_cache,
)

REPO = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
OUTPUT_FILE = OUTPUT_DIR / "sleeper_fingerprints.json"

MIN_MATCH_LEN = 8   # minimum overlapping terms for a match
TERM_SLICE = 20      # use first 20 terms of each sequence
MAX_SLEEPERS = 5000  # cap for initial run


# ---------------------------------------------------------------------------
# Transform Functions
# ---------------------------------------------------------------------------

def first_differences(terms: list[int]) -> list[int] | None:
    if len(terms) < 2:
        return None
    return [terms[i + 1] - terms[i] for i in range(len(terms) - 1)]


def second_differences(terms: list[int]) -> list[int] | None:
    d = first_differences(terms)
    if d is None or len(d) < 2:
        return None
    return [d[i + 1] - d[i] for i in range(len(d) - 1)]


def ratios_rounded(terms: list[int]) -> list[int] | None:
    if len(terms) < 2:
        return None
    if any(t <= 0 for t in terms):
        return None
    result = []
    for i in range(len(terms) - 1):
        if terms[i] == 0:
            return None
        result.append(round(terms[i + 1] / terms[i]))
    return result


def partial_sums(terms: list[int]) -> list[int] | None:
    if len(terms) < 2:
        return None
    s = []
    acc = 0
    for t in terms:
        acc += t
        s.append(acc)
    return s


def mod_reduce(terms: list[int], m: int) -> list[int] | None:
    if len(terms) < MIN_MATCH_LEN:
        return None
    return [t % m for t in terms]


def absolute_values(terms: list[int]) -> list[int] | None:
    if not any(t < 0 for t in terms):
        return None  # only useful when negatives are present
    return [abs(t) for t in terms]


TRANSFORMS = {
    "first_differences": first_differences,
    "second_differences": second_differences,
    "ratios_rounded": ratios_rounded,
    "partial_sums": partial_sums,
    "mod2": lambda t: mod_reduce(t, 2),
    "mod3": lambda t: mod_reduce(t, 3),
    "mod6": lambda t: mod_reduce(t, 6),
    "absolute_values": absolute_values,
}


# ---------------------------------------------------------------------------
# Build fast lookup dict: tuple(first 8 terms) -> list of seq_ids
# ---------------------------------------------------------------------------

def build_lookup(cache: dict, n: int = MIN_MATCH_LEN) -> dict[tuple, list[str]]:
    """Map tuple(first n terms) -> [seq_ids] for O(1) matching."""
    lookup: dict[tuple, list[str]] = {}
    for seq_id, terms in cache.items():
        if len(terms) < n:
            continue
        key = tuple(terms[:n])
        lookup.setdefault(key, []).append(seq_id)
    return lookup


# ---------------------------------------------------------------------------
# Identify sleeping beauties
# ---------------------------------------------------------------------------

def find_sleepers(max_count: int = MAX_SLEEPERS) -> list[tuple[str, list[int]]]:
    """Return (seq_id, terms) pairs for sleeping beauties."""
    _load_oeis()
    _load_oeis_crossrefs()

    sleepers = []
    for seq_id, terms in _oeis_cache.items():
        if len(terms) < MIN_MATCH_LEN:
            continue

        # Connectivity check
        out_deg = len(_oeis_xref_cache.get(seq_id, set()))
        in_deg = len(_oeis_xref_reverse.get(seq_id, set()))
        if out_deg + in_deg > 2:
            continue

        # Shannon entropy of first differences
        diffs = [terms[i + 1] - terms[i] for i in range(min(len(terms) - 1, 30))]
        if not diffs:
            continue
        counts = Counter(diffs)
        total = len(diffs)
        entropy = -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)
        if entropy < 4.0:
            continue

        sleepers.append((seq_id, terms[:TERM_SLICE]))
        if len(sleepers) >= max_count:
            break

    return sleepers


# ---------------------------------------------------------------------------
# Degree of a hub (for ranking)
# ---------------------------------------------------------------------------

def hub_degree(seq_id: str) -> int:
    return len(_oeis_xref_cache.get(seq_id, set())) + len(_oeis_xref_reverse.get(seq_id, set()))


# ---------------------------------------------------------------------------
# Main fingerprinting loop
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()

    print("=== Sleeper Fingerprinter ===\n")

    # 1. Load data
    _load_oeis()
    _load_oeis_names()
    _load_oeis_crossrefs()

    # 2. Build fast lookup
    print(f"Building lookup dict from {len(_oeis_cache):,} sequences...")
    lookup = build_lookup(_oeis_cache, MIN_MATCH_LEN)
    print(f"  Lookup has {len(lookup):,} unique {MIN_MATCH_LEN}-term prefixes\n")

    # 3. Find sleepers
    print("Identifying sleeping beauties...")
    sleepers = find_sleepers(MAX_SLEEPERS)
    print(f"  Found {len(sleepers):,} sleepers (capped at {MAX_SLEEPERS})\n")

    if not sleepers:
        print("No sleepers found. Check data files.")
        return

    # 4. Apply transforms and match
    matches = []           # list of match dicts
    transform_counts = {name: 0 for name in TRANSFORMS}
    multi_hub_sleepers = {}  # seq_id -> list of matches

    checked = 0
    for seq_id, terms in sleepers:
        checked += 1
        if checked % 500 == 0:
            print(f"  Checked {checked:,}/{len(sleepers):,} sleepers...")

        for tname, tfunc in TRANSFORMS.items():
            transformed = tfunc(terms)
            if transformed is None or len(transformed) < MIN_MATCH_LEN:
                continue

            key = tuple(transformed[:MIN_MATCH_LEN])
            hit_ids = lookup.get(key)
            if not hit_ids:
                continue

            # Verify match extends beyond 8 terms where possible
            for hub_id in hit_ids:
                if hub_id == seq_id:
                    continue  # skip self-matches

                hub_terms = _oeis_cache.get(hub_id, [])
                # Count how many terms actually match
                match_len = 0
                for i in range(min(len(transformed), len(hub_terms))):
                    if transformed[i] == hub_terms[i]:
                        match_len += 1
                    else:
                        break

                if match_len < MIN_MATCH_LEN:
                    continue

                deg = hub_degree(hub_id)
                hub_name = _oeis_names_cache.get(hub_id, "")
                sleeper_name = _oeis_names_cache.get(seq_id, "")

                match_rec = {
                    "sleeper_id": seq_id,
                    "sleeper_name": sleeper_name,
                    "transform": tname,
                    "hub_id": hub_id,
                    "hub_name": hub_name,
                    "hub_degree": deg,
                    "match_length": match_len,
                }
                matches.append(match_rec)
                transform_counts[tname] += 1

                # Track multi-hub sleepers
                multi_hub_sleepers.setdefault(seq_id, []).append(match_rec)

    elapsed = time.time() - t0

    # 5. Sort matches by hub degree (most connected hubs first)
    matches.sort(key=lambda m: -m["hub_degree"])

    # 6. Multi-transform sleepers: those matching different hubs under different transforms
    multi_transform = {}
    for sid, recs in multi_hub_sleepers.items():
        transforms_used = set(r["transform"] for r in recs)
        hubs_hit = set(r["hub_id"] for r in recs)
        if len(transforms_used) > 1 or len(hubs_hit) > 1:
            multi_transform[sid] = {
                "sleeper_name": _oeis_names_cache.get(sid, ""),
                "transforms": sorted(transforms_used),
                "hubs": sorted(hubs_hit),
                "matches": recs,
            }

    # 7. Report
    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"  Sleepers checked:   {checked:,}")
    print(f"  Total matches:      {len(matches):,}")
    print(f"  Elapsed time:       {elapsed:.1f}s")
    print(f"\nBreakdown by transform:")
    for tname, cnt in sorted(transform_counts.items(), key=lambda x: -x[1]):
        if cnt > 0:
            print(f"  {tname:25s} {cnt:,}")

    print(f"\nTop 20 matches (by hub connectivity):")
    for m in matches[:20]:
        print(f"  Sleeper {m['sleeper_id']} under {m['transform']} "
              f"-> Hub {m['hub_id']} (deg={m['hub_degree']}, "
              f"match={m['match_length']} terms) — {m['hub_name'][:60]}")

    if multi_transform:
        print(f"\nMulti-transform sleepers ({len(multi_transform):,}):")
        for sid, info in sorted(multi_transform.items(),
                                key=lambda x: -len(x[1]["transforms"]))[:20]:
            print(f"  {sid} ({info['sleeper_name'][:40]}): "
                  f"transforms={info['transforms']}, hubs={info['hubs']}")

    # 8. Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sleepers_checked": checked,
        "total_matches": len(matches),
        "elapsed_seconds": round(elapsed, 1),
        "transform_counts": {k: v for k, v in transform_counts.items() if v > 0},
        "top_matches": matches[:100],
        "multi_transform_sleepers": multi_transform,
        "all_matches": matches,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
