#!/usr/bin/env python3
"""
Mnemosyne battery-sweep coverage extension — 2026-04-29 fill-in session.

Context: Stoa Ask 3 (cross-family validation of OBSTRUCTION_SHAPE on
A148/A150/A151 octant walks) is blocked because battery_sweep_v2.jsonl has
0 coverage on A150* and only 3 entries on A151*, despite asymptotic_deviations
having 142 / 52 sequences flagged regime_change=True in those families.

Bottleneck: cartography/shared/scripts/v2/battery_sweep.py only tests the
top-100 sequences by |delta_pct|. A149* dominated that window
(delta_pct 78-83%); A150* maxes at ~20% and A151* at ~53%, so most fell
below the cutoff.

This script extends coverage by running the same falsification battery
(F1+F6+F9+F11 via cartography/shared/scripts/falsification_battery.run_battery)
on the missing flagged sequences and appending results to battery_sweep_v2.jsonl
in the existing format.

Provenance: new entries carry "extended_by": "mnemosyne_fillin_20260429" so
they're distinguishable from the original sweep.

Run from repo root:
    python mnemosyne/extend_battery_sweep_20260429.py
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "cartography" / "convergence" / "data"
ASYM = DATA / "asymptotic_deviations.jsonl"
SWEEP = DATA / "battery_sweep_v2.jsonl"
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
NEW_TERMS = ROOT / "cartography" / "oeis" / "data" / "new_terms"

# Add the cartography scripts dir to path for falsification_battery.
sys.path.insert(0, str(ROOT / "cartography" / "shared" / "scripts"))
from falsification_battery import run_battery  # noqa: E402


TARGET_FAMILIES = ("A148", "A150", "A151")


def load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def load_oeis_terms() -> dict[str, list[int]]:
    """Build seq_id -> list of integer terms from stripped_new.txt + new_terms/."""
    out: dict[str, list[int]] = {}
    if OEIS_STRIPPED.exists():
        with OEIS_STRIPPED.open(encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or not line.startswith("A"):
                    continue
                if "," not in line:
                    continue
                parts = line.split(",")
                seq_id = parts[0].strip()
                terms: list[int] = []
                for p in parts[1:]:
                    p = p.strip()
                    if p:
                        try:
                            terms.append(int(p))
                        except ValueError:
                            pass
                if terms:
                    out[seq_id] = terms

    if NEW_TERMS.exists():
        for f in NEW_TERMS.glob("*.json"):
            try:
                d = json.loads(f.read_text())
                sid = d.get("seq_id")
                if not sid:
                    continue
                base = list(out.get(sid, []))
                ext = {int(k.replace("a(", "").replace(")", "")): v
                       for k, v in d.get("new_terms", {}).items()}
                for idx in sorted(ext.keys()):
                    while len(base) <= idx:
                        base.append(0)
                    base[idx] = ext[idx]
                out[sid] = base
            except Exception:
                continue
    return out


def battery_one(seq_id: str, terms: list[int], delta_pct: float) -> dict | None:
    """Run the battery on a single sequence's consecutive ratios. Return a
    battery_sweep_v2-shaped dict, or None if data is too thin to test."""
    if len(terms) < 20:
        return None
    arr = np.asarray(terms, dtype=float)
    nonzero = arr[:-1] != 0
    if int(nonzero.sum()) < 10:
        return None
    ratios = arr[1:][nonzero] / arr[:-1][nonzero]
    ratios = ratios[np.isfinite(ratios) & (ratios > 0)]
    if len(ratios) < 10:
        return None

    mid = len(ratios) // 2
    a, b = ratios[:mid], ratios[mid:]
    if len(a) < 5 or len(b) < 5:
        return None

    try:
        verdict, results = run_battery(a, b, claim=f"Regime change in {seq_id}")
    except Exception as ex:
        return {
            "layer": 1, "source": "regime_change", "seq_id": seq_id,
            "delta_pct": delta_pct, "verdict": "ERROR",
            "kill_tests": [f"battery_exception:{type(ex).__name__}:{ex}"[:200]],
            "extended_by": "mnemosyne_fillin_20260429",
        }

    if isinstance(results, dict):
        items = results.items()
    else:
        items = [(r.get("test", f"F{i}"), r) for i, r in enumerate(results)]
    kill_tests = [k for k, v in items if v.get("verdict") == "FAIL"]

    return {
        "layer": 1, "source": "regime_change", "seq_id": seq_id,
        "delta_pct": delta_pct, "verdict": verdict, "kill_tests": kill_tests,
        "extended_by": "mnemosyne_fillin_20260429",
    }


def main() -> int:
    print("=" * 72)
    print("MNEMOSYNE FILL-IN: extend battery_sweep_v2 coverage on A148/A150/A151")
    print("=" * 72)

    asym = load_jsonl(ASYM)
    sweep = load_jsonl(SWEEP)
    print(f"  loaded asym={len(asym)}, sweep={len(sweep)}")

    sweep_seqs = {r.get("seq_id") for r in sweep if r.get("seq_id")}

    # Candidate sequences: target families, regime_change=True, not yet in sweep.
    candidates: list[dict] = []
    for r in asym:
        sid = r.get("seq_id", "")
        if not any(sid.startswith(f) for f in TARGET_FAMILIES):
            continue
        if not r.get("regime_change"):
            continue
        if sid in sweep_seqs:
            continue
        candidates.append(r)

    by_fam = Counter(r["seq_id"][:4] for r in candidates)
    print(f"  uncovered candidates: {len(candidates)} total")
    for fam in TARGET_FAMILIES:
        print(f"    {fam}*: {by_fam.get(fam, 0)}")

    if not candidates:
        print("  no work to do")
        return 0

    print()
    print(f"  loading OEIS terms (stripped_new.txt + new_terms/)...")
    oeis_terms = load_oeis_terms()
    print(f"  loaded terms for {len(oeis_terms)} sequences")

    print()
    print(f"  running battery on candidates...")
    t0 = time.time()
    new_rows: list[dict] = []
    n_killed = 0
    n_survived = 0
    n_skipped = 0
    n_error = 0

    for i, c in enumerate(candidates):
        sid = c["seq_id"]
        terms = oeis_terms.get(sid)
        if not terms:
            n_skipped += 1
            continue

        result = battery_one(sid, terms, float(c.get("delta_pct", 0.0)))
        if result is None:
            n_skipped += 1
            continue

        new_rows.append(result)
        v = result["verdict"]
        if v == "ERROR":
            n_error += 1
        elif v == "SURVIVES":
            n_survived += 1
        else:
            n_killed += 1

        if (i + 1) % 50 == 0:
            print(f"    progress {i+1}/{len(candidates)}  killed={n_killed} survived={n_survived} skipped={n_skipped} error={n_error}  ({time.time()-t0:.1f}s)")

    print()
    print(f"  done in {time.time() - t0:.1f}s")
    print(f"  killed:   {n_killed}")
    print(f"  survived: {n_survived}")
    print(f"  skipped:  {n_skipped} (no terms or insufficient data)")
    print(f"  error:    {n_error}")
    print(f"  total new rows for sweep: {len(new_rows)}")

    # Append to battery_sweep_v2.jsonl
    if new_rows:
        with SWEEP.open("a", encoding="utf-8") as f:
            for row in new_rows:
                f.write(json.dumps(row) + "\n")
        print(f"  appended {len(new_rows)} rows to {SWEEP.relative_to(ROOT)}")

    # Final coverage check
    sweep2 = load_jsonl(SWEEP)
    fam_cov = Counter(r["seq_id"][:4] for r in sweep2 if r.get("seq_id"))
    print()
    print("  coverage after extension:")
    for fam in TARGET_FAMILIES + ("A149",):
        print(f"    {fam}*: {fam_cov.get(fam, 0)}")

    # Quick check: how many of the new rows hit the unanimous battery?
    unanimous = {"F1_permutation_null", "F6_base_rate", "F9_simpler_explanation", "F11_cross_validation"}
    n_unanimous = sum(1 for r in new_rows if unanimous.issubset(set(r.get("kill_tests", []))))
    print()
    print(f"  unanimous-kill rate on new rows: {n_unanimous}/{len(new_rows)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
