#!/usr/bin/env python3
"""One-time cleanup script for Hephaestus data after pipeline changes.

Fixes:
1. Re-scores all forge/ tools against the new 15-trap battery
2. Moves broken tools (no ReasoningTool class) to scrap/
3. Updates forge/ JSON sidecars with new scores
4. Rebuilds ledger.jsonl with margin-over-NCD data
5. Re-runs Coeus to rebuild the causal graph

Run from anywhere:
    python agents/hephaestus/src/cleanup_once.py
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

HEPHAESTUS_ROOT = Path(__file__).resolve().parent.parent
FORGE_DIR = HEPHAESTUS_ROOT / "forge"
SCRAP_DIR = HEPHAESTUS_ROOT / "scrap"
LEDGER_PATH = HEPHAESTUS_ROOT / "ledger.jsonl"

sys.path.insert(0, str(HEPHAESTUS_ROOT / "src"))

from test_harness import load_tool_from_file, run_trap_battery, run_ncd_baseline


def main():
    print("=" * 60)
    print("HEPHAESTUS CLEANUP")
    print("=" * 60)

    # --- Step 0: Get NCD baseline scores ---
    print("\n[0] Running NCD baseline on 15-trap battery...")
    ncd = run_ncd_baseline()
    print(f"    NCD baseline: acc={ncd['accuracy']:.0%} cal={ncd['calibration']:.0%}")

    # --- Step 0.5: Move utility wrappers to forge/utils/ ---
    UTILS_DIR = FORGE_DIR / "utils"
    UTILS_DIR.mkdir(exist_ok=True)
    wrapper_names = ["perturbation_calibrator", "criticality_regularizer"]
    moved_to_utils = []
    for wname in wrapper_names:
        for ext in (".py", ".json"):
            src = FORGE_DIR / f"{wname}{ext}"
            if src.exists():
                dest = UTILS_DIR / src.name
                shutil.move(str(src), str(dest))
                moved_to_utils.append(f"{wname}{ext}")
    if moved_to_utils:
        print(f"\n[0.5] Moved utility wrappers to forge/utils/: {', '.join(moved_to_utils)}")

    # --- Step 1: Re-score all forge tools, move broken ones ---
    print("\n[1] Re-scoring forge/ tools...")
    py_files = sorted(FORGE_DIR.glob("*.py"))
    forge_scores = {}  # name -> {accuracy, calibration, margin_accuracy, margin_calibration}
    moved_to_scrap = []

    for py in py_files:
        name = py.stem
        json_sidecar = FORGE_DIR / f"{name}.json"

        try:
            tool = load_tool_from_file(py)
        except Exception as e:
            # Broken tool — move to scrap
            print(f"    BROKEN: {name} — {e}")
            dest_py = SCRAP_DIR / py.name
            shutil.move(str(py), str(dest_py))
            if json_sidecar.exists():
                dest_json = SCRAP_DIR / json_sidecar.name
                shutil.move(str(json_sidecar), str(dest_json))
                meta = json.loads(dest_json.read_text(encoding="utf-8"))
                meta["failure_reason"] = f"cleanup: no ReasoningTool class ({e})"
                meta["scrapped_at"] = datetime.now().isoformat()
                dest_json.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            moved_to_scrap.append(name)
            continue

        try:
            r = run_trap_battery(tool)
            forge_scores[name] = {
                "accuracy": r["accuracy"],
                "calibration": r["calibration"],
                "margin_accuracy": r.get("margin_accuracy", 0),
                "margin_calibration": r.get("margin_calibration", 0),
                "passed": r["passed"],
                "correct_count": r["correct_count"],
                "n_traps": r["n_traps"],
            }
            status = "PASS" if r["passed"] else "FAIL"
            print(f"    {name:60s} acc={r['accuracy']:.0%} cal={r['calibration']:.0%} "
                  f"m_acc={r.get('margin_accuracy',0):+.0%} m_cal={r.get('margin_calibration',0):+.0%} {status}")

            # Update JSON sidecar
            if json_sidecar.exists():
                meta = json.loads(json_sidecar.read_text(encoding="utf-8"))
            else:
                meta = {"concept_names": [], "concept_fields": []}
            meta["test_accuracy"] = r["accuracy"]
            meta["test_calibration"] = r["calibration"]
            meta["margin_over_ncd_accuracy"] = r.get("margin_accuracy", 0)
            meta["margin_over_ncd_calibration"] = r.get("margin_calibration", 0)
            meta["n_traps"] = r["n_traps"]
            meta["rescored_at"] = datetime.now().isoformat()
            json_sidecar.write_text(json.dumps(meta, indent=2), encoding="utf-8")

            # If it no longer passes, move to scrap
            if not r["passed"]:
                print(f"    DEMOTED: {name} (no longer beats NCD)")
                dest_py = SCRAP_DIR / py.name
                shutil.move(str(py), str(dest_py))
                dest_json = SCRAP_DIR / json_sidecar.name
                if json_sidecar.exists():
                    shutil.move(str(json_sidecar), str(dest_json))
                moved_to_scrap.append(name)

        except Exception as e:
            print(f"    ERROR: {name} — {e}")
            forge_scores[name] = {"accuracy": 0, "calibration": 0, "passed": False}

    # --- Step 2: Rebuild ledger with margin data ---
    print("\n[2] Rebuilding ledger.jsonl with margin data...")
    LEDGER_BAK = LEDGER_PATH.with_suffix(".jsonl.bak")
    if LEDGER_PATH.exists():
        shutil.copy2(str(LEDGER_PATH), str(LEDGER_BAK))
        print(f"    Backup: {LEDGER_BAK}")

    # Load existing ledger
    old_entries = []
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    old_entries.append(json.loads(line))

    # Build name-to-forge-score lookup
    # Map concept combo keys to forge scores
    forge_score_by_file = {}
    for py in FORGE_DIR.glob("*.py"):
        name = py.stem
        if name in forge_scores:
            forge_score_by_file[name] = forge_scores[name]

    # Also build lookup from concept names in JSON sidecars
    forge_score_by_key = {}
    for jf in FORGE_DIR.glob("*.json"):
        meta = json.loads(jf.read_text(encoding="utf-8"))
        names = meta.get("concept_names", [])
        if names:
            key = " + ".join(sorted(names))
            stem = jf.stem
            if stem in forge_scores:
                forge_score_by_key[key] = forge_scores[stem]

    # Rebuild ledger
    updated = 0
    new_entries = []
    for entry in old_entries:
        key = entry.get("key", "")
        if entry.get("status") == "forged" and key in forge_score_by_key:
            scores = forge_score_by_key[key]
            entry["accuracy"] = scores["accuracy"]
            entry["calibration"] = scores["calibration"]
            entry["margin_accuracy"] = scores.get("margin_accuracy", 0)
            entry["margin_calibration"] = scores.get("margin_calibration", 0)
            # Check if it was demoted
            name_parts = [n.replace(" ", "_") for n in entry.get("concept_names", [])]
            file_stem = "_x_".join(name_parts).lower()
            if file_stem in [n for n in moved_to_scrap]:
                entry["status"] = "scrap"
                entry["reason"] = "cleanup: demoted (no longer beats NCD baseline)"
            updated += 1
        elif "margin_accuracy" not in entry:
            entry["margin_accuracy"] = 0.0
            entry["margin_calibration"] = 0.0

        new_entries.append(entry)

    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        for entry in new_entries:
            f.write(json.dumps(entry) + "\n")

    print(f"    Updated {updated} forged entries with new scores")
    print(f"    Total ledger entries: {len(new_entries)}")

    # --- Step 3: Re-run Coeus ---
    print("\n[3] Rebuilding Coeus causal graph...")
    coeus_src = HEPHAESTUS_ROOT.parent / "coeus" / "src"
    if coeus_src.exists():
        sys.path.insert(0, str(coeus_src))
        try:
            from coeus import main as coeus_main
            coeus_main()
            print("    Coeus rebuild complete")
        except Exception as e:
            print(f"    Coeus rebuild failed: {e}")
            print("    Run manually: python agents/coeus/src/coeus.py")
    else:
        print("    Coeus not found — run manually: python agents/coeus/src/coeus.py")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print(f"  NCD baseline:     acc={ncd['accuracy']:.0%} cal={ncd['calibration']:.0%}")
    print(f"  Tools re-scored:  {len(forge_scores)}")
    print(f"  Moved to scrap:   {len(moved_to_scrap)} ({', '.join(moved_to_scrap) or 'none'})")
    print(f"  Ledger updated:   {updated} entries backfilled")
    print(f"  Ledger backup:    {LEDGER_BAK}")
    print("=" * 60)


if __name__ == "__main__":
    main()
