"""
Preload Shadow Tensor — Rip through 5K+ cycle logs and extract every
battery result, p-value, z-score, kill mode, and claim.

This is a one-time bulk ingest that populates the shadow tensor from
the full history of research cycles. After this, shadow_tensor.py
can be re-run to compute anomaly scores on the enriched data.

Outputs:
  convergence/data/shadow_preload.jsonl — extracted battery events
  Then rebuilds shadow_tensor.json via shadow_tensor.py

Usage:
    python preload_shadow.py
"""

import json
import re
import sys
import time
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[3]
CONVERGENCE = ROOT / "cartography" / "convergence"
LOGS_DIR = CONVERGENCE / "logs"
PRELOAD_FILE = CONVERGENCE / "data" / "shadow_preload.jsonl"
HUNTER_RESULTS = CONVERGENCE / "data" / "bridge_hunter_results.jsonl"

# Dataset name normalization
DATASET_KEYWORDS = {
    "oeis": "OEIS", "lmfdb": "LMFDB", "knot": "KnotInfo",
    "fungrim": "Fungrim", "antedb": "ANTEDB", "mathlib": "mathlib",
    "metamath": "Metamath", "material": "Materials", "number field": "NumberFields",
    "numberfield": "NumberFields", "isogen": "Isogenies", "local field": "LocalFields",
    "localfield": "LocalFields", "space group": "SpaceGroups", "spacegroup": "SpaceGroups",
    "polytop": "Polytopes", "pi-base": "piBase", "pibase": "piBase",
    "mmlkg": "MMLKG", "mizar": "MMLKG", "genus-2": "Genus2", "genus2": "Genus2",
    "maass": "Maass", "lattice": "Lattices", "findstat": "FindStat",
    "openalex": "OpenAlex", "elliptic curve": "LMFDB", "modular form": "LMFDB",
    "conductor": "LMFDB", "crossing": "KnotInfo", "determinant": "KnotInfo",
    "alexander": "KnotInfo", "jones": "KnotInfo", "class number": "NumberFields",
    "discriminant": "NumberFields", "regulator": "NumberFields",
    "f-vector": "Polytopes", "wyckoff": "SpaceGroups", "crystal": "SpaceGroups",
    "zero.density": "ANTEDB", "exponent": "ANTEDB",
    "sleeping beaut": "OEIS", "cross-reference": "OEIS",
}


def extract_datasets(text):
    """Extract dataset names mentioned in a claim/hypothesis text."""
    text_lower = text.lower()
    found = set()
    for keyword, canonical in DATASET_KEYWORDS.items():
        if keyword in text_lower:
            found.add(canonical)
    return sorted(found)


def pair_key(d1, d2):
    return "--".join(sorted([d1, d2]))


def process_log_file(logpath):
    """Extract battery events from one cycle log file."""
    records = []
    events = []

    with open(logpath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except:
                pass

    # Find battery_started → test results → battery_completed sequences
    current_claim = None
    current_tests = []
    tag = logpath.stem.split("_")[1] if "_" in logpath.stem else ""

    for e in events:
        evt = e.get("event", "")
        data = e.get("data", {})

        if evt == "battery_started":
            current_claim = data.get("claim", "")
            current_tests = []

        elif evt in ("test_pass", "test_fail", "test_skip"):
            current_tests.append({
                "test": data.get("test", ""),
                "verdict": data.get("verdict", evt.split("_")[1].upper()),
                "p_value": data.get("p_value"),
                "z_score": data.get("z_score"),
                "cohens_d": data.get("cohens_d"),
                "rho_partial": data.get("rho_partial"),
                "rho_raw": data.get("rho_raw"),
                "decay_ratio": data.get("decay_ratio"),
                "rho_target": data.get("rho_target"),
                "baselines": data.get("baselines"),
            })

        elif evt == "battery_completed":
            claim = data.get("claim", current_claim or "")
            datasets = extract_datasets(claim)

            if len(datasets) >= 2:
                pk = pair_key(datasets[0], datasets[1])
                record = {
                    "pair": pk,
                    "datasets": datasets,
                    "claim": claim[:300],
                    "verdict": data.get("verdict", ""),
                    "passed": data.get("passed", 0),
                    "failed": data.get("failed", 0),
                    "skipped": data.get("skipped", 0),
                    "kill_tests": data.get("kill_tests", []),
                    "kill_diagnosis": data.get("kill_diagnosis", {}),
                    "tests": current_tests,
                    "tag": tag,
                    "timestamp": e.get("ts", ""),
                    "source": logpath.name,
                }
                records.append(record)

            current_claim = None
            current_tests = []

    return records


def main():
    print("=" * 70)
    print("  PRELOAD SHADOW TENSOR — Mining 5K+ cycle logs")
    print("  Extracting every battery result, p-value, kill mode")
    print("=" * 70)

    t0 = time.time()

    log_files = sorted(LOGS_DIR.glob("cycle_*.jsonl"))
    print(f"\n  Found {len(log_files)} cycle log files")

    all_records = []
    files_processed = 0
    files_with_battery = 0

    for i, lf in enumerate(log_files):
        try:
            records = process_log_file(lf)
            all_records.extend(records)
            files_processed += 1
            if records:
                files_with_battery += 1
        except Exception as e:
            pass  # skip corrupt files

        if (i + 1) % 500 == 0:
            print(f"    Processed {i+1}/{len(log_files)} files, {len(all_records)} battery records...")

    print(f"\n  Processed: {files_processed} files ({files_with_battery} with battery data)")
    print(f"  Battery records extracted: {len(all_records)}")

    # Write preload file
    with open(PRELOAD_FILE, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r) + "\n")
    print(f"  Saved to {PRELOAD_FILE}")

    # Statistics
    pair_counts = Counter()
    kill_mode_counts = Counter()
    verdict_counts = Counter()
    p_values_all = []

    for r in all_records:
        pair_counts[r["pair"]] += 1
        verdict_counts[r["verdict"]] += 1
        for kt in r.get("kill_tests", []):
            kill_mode_counts[kt] += 1
        for t in r.get("tests", []):
            p = t.get("p_value")
            if p is not None:
                p_values_all.append(float(p))

    print(f"\n  Verdicts: {dict(verdict_counts)}")
    print(f"  Unique pairs tested: {len(pair_counts)}")
    print(f"  Total p-values extracted: {len(p_values_all)}")

    print(f"\n  Top 15 most-tested pairs:")
    for pk, count in pair_counts.most_common(15):
        print(f"    {pk:45s} {count:5d} battery runs")

    print(f"\n  Kill mode frequency:")
    for km, count in kill_mode_counts.most_common():
        print(f"    {km:40s} {count:5d}")

    # Now feed this into the shadow tensor
    # Write to hunter_results format so shadow_tensor.py can ingest it
    print(f"\n  Converting to bridge_hunter format for shadow tensor ingestion...")
    n_converted = 0
    with open(HUNTER_RESULTS, "a", encoding="utf-8") as f:
        for r in all_records:
            for t in r.get("tests", []):
                entry = {
                    "hypothesis": {
                        "d1": r["datasets"][0] if len(r["datasets"]) > 0 else "",
                        "d2": r["datasets"][1] if len(r["datasets"]) > 1 else "",
                        "claim": r["claim"],
                        "type": "research_cycle",
                    },
                    "test_result": {
                        "verdict": t["verdict"],
                        "p": t.get("p_value"),
                        "z": t.get("z_score"),
                        "test": t.get("test", ""),
                    },
                    "timestamp": r.get("timestamp", ""),
                }
                f.write(json.dumps(entry) + "\n")
                n_converted += 1

    print(f"  Appended {n_converted} test records to bridge_hunter_results.jsonl")

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")
    print(f"  Now run: python shadow_tensor.py --show-hot --show-kills")


if __name__ == "__main__":
    main()
