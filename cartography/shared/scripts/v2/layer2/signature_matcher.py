"""
Signature Matcher — cross-domain bridge detection via tiered invariants.
========================================================================
Loads signatures from all extractors, builds hash indices for exact-match
invariants (Tier 1), computes pairwise soft distances (Tier 2), and applies
cross-tier confirmation (Tier 3) before sending survivors to the battery.

Tier 1 (exact, O(1)): operadic skeleton, Newton polytope vertices,
    symmetry class, mod-p fingerprint vector.
Tier 2 (approximate): spectral signature (cosine), convexity profile
    (Euclidean), discriminant (log-ratio).
Tier 3: >= 1 Tier-1 match AND >= 2 Tier-2 matches required.

Usage:
    python signature_matcher.py                     # full run
    python signature_matcher.py --dry-run           # report matches, skip battery
    python signature_matcher.py --tier2-threshold 0.90  # tighten cosine cutoff
"""

import argparse
import json
import sys
import time
import hashlib
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "cartography" / "convergence" / "data"

# Signature input files
SIG_FILES = {
    "operadic":     DATA / "operadic_signatures.jsonl",
    "newton":       DATA / "newton_polytopes.jsonl",
    "symmetry":     DATA / "symmetry_signatures.jsonl",
    "mod_p":        DATA / "mod_p_signatures.jsonl",
    "spectral":     DATA / "spectral_signatures.jsonl",
    "convexity":    DATA / "convexity_signatures.jsonl",
    "discriminant": DATA / "discriminant_signatures.jsonl",
}

TRIAGE_FILE = DATA / "formula_triage.jsonl"

# Output files
OUT_MATCHES    = DATA / "signature_matches.jsonl"
OUT_BRIDGES    = DATA / "bridge_candidates.jsonl"
OUT_BATTERY    = DATA / "bridge_battery_results.jsonl"

# Tier 2 default thresholds
COSINE_THRESH  = 0.92   # spectral cosine similarity
EUCLID_THRESH  = 3.0    # convexity Euclidean distance (lower = closer)
LOGRATIO_THRESH = 1.0   # discriminant |log(a/b)| tolerance


# ── Loaders ──────────────────────────────────────────────────────────────

def load_jsonl(path):
    """Load JSONL file, return list of dicts. Empty list if missing."""
    if not path.exists():
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def load_triage_set():
    """Return set of formula hashes in the triage set."""
    entries = load_jsonl(TRIAGE_FILE)
    return {e["hash"] for e in entries if "hash" in e}


def item_id(rec):
    """Canonical ID from a signature record (hash or id field)."""
    return rec.get("hash") or rec.get("id", "")


def item_domain(rec):
    """Best-effort domain extraction."""
    return rec.get("domain") or rec.get("source") or "unknown"


# ── Tier 1: exact hash indices ──────────────────────────────────────────

def build_tier1_indices(sigs, triage):
    """Build hash -> [(id, domain, record)] for each Tier 1 invariant."""
    indices = {
        "operadic":  defaultdict(list),
        "newton":    defaultdict(list),
        "symmetry":  defaultdict(list),
        "mod_p":     defaultdict(list),
    }

    # Operadic: skeleton_hash
    for rec in sigs.get("operadic", []):
        fid = item_id(rec)
        if triage and fid not in triage:
            continue
        h = rec.get("skeleton_hash", "")
        if h:
            indices["operadic"][h].append((fid, item_domain(rec), rec))

    # Newton polytope: vertex_hash
    for rec in sigs.get("newton", []):
        fid = item_id(rec)
        if triage and fid not in triage:
            continue
        h = rec.get("vertex_hash", "")
        if h:
            indices["newton"][h].append((fid, item_domain(rec), rec))

    # Symmetry: symmetry_class
    for rec in sigs.get("symmetry", []):
        fid = item_id(rec)
        if triage and fid not in triage:
            continue
        h = rec.get("symmetry_class", "")
        if h:
            indices["symmetry"][h].append((fid, item_domain(rec), rec))

    # Mod-p: hash the signature vector itself
    for rec in sigs.get("mod_p", []):
        fid = item_id(rec)
        if triage and fid not in triage:
            continue
        sig = rec.get("signature")
        if sig:
            h = hashlib.md5(json.dumps(sig, sort_keys=True).encode()).hexdigest()[:16]
            indices["mod_p"][h].append((fid, item_domain(rec), rec))

    return indices


def find_cross_domain_buckets(index):
    """Return list of (hash_key, items) where items span 2+ domains."""
    cross = []
    for key, items in index.items():
        domains = {d for _, d, _ in items}
        if len(domains) >= 2:
            cross.append((key, items))
    return cross


# ── Tier 2: soft similarity ─────────────────────────────────────────────

def build_tier2_lookup(sigs, triage):
    """Build id -> record lookups for Tier 2 signatures."""
    lookups = {}
    for kind in ("spectral", "convexity", "discriminant"):
        lk = {}
        for rec in sigs.get(kind, []):
            fid = item_id(rec)
            if triage and fid not in triage:
                continue
            lk[fid] = rec
        lookups[kind] = lk
    return lookups


def cosine_sim(a, b):
    """Cosine similarity between two float vectors."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-15 or nb < 1e-15:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def euclid_dist(a, b):
    """Euclidean distance between two float vectors."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    minlen = min(len(a), len(b))
    return float(np.linalg.norm(a[:minlen] - b[:minlen]))


def log_ratio(x, y):
    """Absolute log-ratio, safe for zeros."""
    ax, ay = abs(x), abs(y)
    if ax < 1e-300 and ay < 1e-300:
        return 0.0
    if ax < 1e-300 or ay < 1e-300:
        return 999.0
    return abs(np.log(ax / ay))


def tier2_score(id_a, id_b, lookups, thresholds):
    """Compute Tier 2 matches between two formula IDs.

    Returns: (n_matches, detail_dict)
    """
    cos_t, euc_t, lr_t = thresholds
    n = 0
    detail = {}

    # Spectral
    sp = lookups.get("spectral", {})
    ra, rb = sp.get(id_a), sp.get(id_b)
    if ra and rb:
        va = ra.get("signature_vector")
        vb = rb.get("signature_vector")
        if va and vb:
            cs = cosine_sim(va, vb)
            detail["spectral_cosine"] = round(cs, 6)
            if cs >= cos_t:
                n += 1

    # Convexity
    cv = lookups.get("convexity", {})
    ra, rb = cv.get(id_a), cv.get(id_b)
    if ra and rb:
        va = ra.get("curvature_vector")
        vb = rb.get("curvature_vector")
        if va and vb:
            ed = euclid_dist(va, vb)
            detail["convexity_euclid"] = round(ed, 6)
            if ed <= euc_t:
                n += 1

    # Discriminant
    dc = lookups.get("discriminant", {})
    ra, rb = dc.get(id_a), dc.get(id_b)
    if ra and rb:
        da = ra.get("discriminant")
        db = rb.get("discriminant")
        if da is not None and db is not None:
            lr = log_ratio(da, db)
            detail["disc_logratio"] = round(lr, 6)
            if lr <= lr_t:
                n += 1

    return n, detail


# ── Tier 3: cross-tier confirmation ─────────────────────────────────────

def find_bridges(tier1_indices, tier2_lookups, thresholds):
    """Identify all Tier-3 confirmed bridge candidates.

    Returns: (all_matches, bridge_candidates)
        all_matches: every cross-domain Tier 1 hit with Tier 2 detail
        bridge_candidates: subset passing Tier 3 (1 T1 + 2 T2)
    """
    all_matches = []
    bridges = []

    for t1_name, index in tier1_indices.items():
        cross = find_cross_domain_buckets(index)
        for key, items in cross:
            ids = [(fid, dom) for fid, dom, _ in items]
            # Pairwise Tier 2 check
            for (id_a, dom_a), (id_b, dom_b) in combinations(ids, 2):
                if dom_a == dom_b:
                    continue
                t2_n, t2_detail = tier2_score(id_a, id_b, tier2_lookups, thresholds)
                match_rec = {
                    "id_a": id_a,
                    "domain_a": dom_a,
                    "id_b": id_b,
                    "domain_b": dom_b,
                    "tier1_type": t1_name,
                    "tier1_key": key,
                    "tier2_matches": t2_n,
                    "tier2_detail": t2_detail,
                }
                all_matches.append(match_rec)
                if t2_n >= 2:
                    match_rec["tier3_confirmed"] = True
                    bridges.append(match_rec)

    return all_matches, bridges


# ── Battery interface ────────────────────────────────────────────────────

def run_battery_on_bridges(bridges, sigs):
    """Run falsification battery where possible. Returns list of results."""
    try:
        from falsification_battery import run_battery
    except ImportError:
        print("  WARNING: falsification_battery not importable, skipping battery")
        return [{"bridge": b, "verdict": "SKIP", "reason": "no battery"} for b in bridges]

    # Build lookup for mod-p signatures (directly comparable arrays)
    mod_p_lookup = {}
    for rec in sigs.get("mod_p", []):
        fid = item_id(rec)
        sig = rec.get("signature")
        if fid and sig:
            mod_p_lookup[fid] = np.array(sig, dtype=float)

    # Build lookup for discriminant numerical properties
    disc_lookup = {}
    for rec in sigs.get("discriminant", []):
        fid = item_id(rec)
        if fid:
            vals = []
            for k in ("discriminant", "log_abs_disc", "f_at_1", "f_at_neg1",
                       "leading_coeff", "constant_term", "n_sign_changes"):
                v = rec.get(k)
                if v is not None:
                    vals.append(float(v))
            if vals:
                disc_lookup[fid] = np.array(vals, dtype=float)

    results = []
    for b in bridges:
        id_a, id_b = b["id_a"], b["id_b"]
        t1_type = b["tier1_type"]
        tested = False

        # Mod-p: signature arrays directly battery-testable
        if id_a in mod_p_lookup and id_b in mod_p_lookup:
            va, vb = mod_p_lookup[id_a], mod_p_lookup[id_b]
            minlen = min(len(va), len(vb))
            if minlen >= 10:
                verdict, details = run_battery(
                    va[:minlen], vb[:minlen],
                    claim=f"mod-p bridge {id_a} <-> {id_b}"
                )
                results.append({
                    "id_a": id_a, "id_b": id_b,
                    "test_type": "mod_p",
                    "verdict": verdict,
                    "n_tests": len(details),
                })
                tested = True

        # Discriminant: compare numerical properties
        if id_a in disc_lookup and id_b in disc_lookup:
            va, vb = disc_lookup[id_a], disc_lookup[id_b]
            minlen = min(len(va), len(vb))
            if minlen >= 5:
                verdict, details = run_battery(
                    va[:minlen], vb[:minlen],
                    claim=f"disc bridge {id_a} <-> {id_b}"
                )
                results.append({
                    "id_a": id_a, "id_b": id_b,
                    "test_type": "discriminant",
                    "verdict": verdict,
                    "n_tests": len(details),
                })
                tested = True

        # Structural matches (operadic, newton, symmetry): flag for review
        if not tested:
            results.append({
                "id_a": id_a, "id_b": id_b,
                "test_type": t1_type,
                "verdict": "REVIEW",
                "reason": "structural match, no numeric arrays for battery",
            })

    return results


# ── Output ───────────────────────────────────────────────────────────────

def write_jsonl(path, records):
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec, default=str) + "\n")
    print(f"  Wrote {len(records):,} records -> {path.name}")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Cross-domain signature matcher")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report matches without running battery")
    ap.add_argument("--cosine-threshold", type=float, default=COSINE_THRESH,
                    help=f"Spectral cosine similarity threshold (default {COSINE_THRESH})")
    ap.add_argument("--euclid-threshold", type=float, default=EUCLID_THRESH,
                    help=f"Convexity Euclidean distance threshold (default {EUCLID_THRESH})")
    ap.add_argument("--logratio-threshold", type=float, default=LOGRATIO_THRESH,
                    help=f"Discriminant log-ratio threshold (default {LOGRATIO_THRESH})")
    ap.add_argument("--no-triage", action="store_true",
                    help="Process all formulas, not just triaged set")
    args = ap.parse_args()

    thresholds = (args.cosine_threshold, args.euclid_threshold, args.logratio_threshold)
    t0 = time.time()

    # 1. Load triage set
    triage = set()
    if not args.no_triage:
        triage = load_triage_set()
        print(f"[1] Triage set: {len(triage):,} formulas")
    else:
        print("[1] Triage disabled — processing all formulas")

    # 2. Load all signature files
    sigs = {}
    for name, path in SIG_FILES.items():
        records = load_jsonl(path)
        sigs[name] = records
        status = f"{len(records):,}" if records else "MISSING"
        print(f"[2] {name:>14s}: {status}")

    # 3. Build Tier 1 indices
    tier1 = build_tier1_indices(sigs, triage if triage else None)
    for name, index in tier1.items():
        n_keys = len(index)
        n_cross = sum(1 for k, items in index.items()
                      if len({d for _, d, _ in items}) >= 2)
        print(f"[3] T1 {name:>10s}: {n_keys:,} buckets, {n_cross:,} cross-domain")

    # 4. Build Tier 2 lookups
    tier2_lookups = build_tier2_lookup(sigs, triage if triage else None)
    for name, lk in tier2_lookups.items():
        print(f"[4] T2 {name:>14s}: {len(lk):,} entries")

    # 5. Find bridges
    print("[5] Running tiered matching...")
    all_matches, bridges = find_bridges(tier1, tier2_lookups, thresholds)

    # Summary
    n_t1 = len(all_matches)
    n_bridge = len(bridges)
    print(f"\n    Tier-1 cross-domain pairs: {n_t1:,}")
    print(f"    Tier-3 confirmed bridges:  {n_bridge:,}")

    # 6. Write matches and bridges
    write_jsonl(OUT_MATCHES, all_matches)
    write_jsonl(OUT_BRIDGES, bridges)

    # 7. Battery (unless dry run)
    if args.dry_run:
        print("\n  --dry-run: skipping battery")
    else:
        if bridges:
            print(f"\n[7] Running battery on {n_bridge:,} bridge candidates...")
            battery_results = run_battery_on_bridges(bridges, sigs)
            write_jsonl(OUT_BATTERY, battery_results)

            n_survive = sum(1 for r in battery_results if r["verdict"] == "SURVIVES")
            n_killed = sum(1 for r in battery_results if r["verdict"] == "KILLED")
            n_review = sum(1 for r in battery_results if r["verdict"] == "REVIEW")
            n_skip = sum(1 for r in battery_results if r["verdict"] == "SKIP")
            print(f"    Battery: {n_survive} survive, {n_killed} killed, "
                  f"{n_review} review, {n_skip} skip")
        else:
            print("\n  No bridge candidates — skipping battery")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
