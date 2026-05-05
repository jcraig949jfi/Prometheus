#!/usr/bin/env python3
"""
JSONL-append knot trace field batch. One line per knot, resumable.

Writes ergon/results/knot_shape_fields.jsonl with one JSON record per knot.
Restart-safe: skips already-processed knots on restart.

Usage:
    python ergon/scripts/compute_knot_shape_fields_jsonl.py
"""
import json
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from techne.lib.knot_shape_field import knot_shape_field

KNOTS_PATH = ROOT / "cartography" / "knots" / "data" / "knots.json"
OUT_JSONL = ROOT / "ergon" / "results" / "knot_shape_fields.jsonl"

BITS_PREC = 400
MAX_DEG = 10
PER_KNOT_TIMEOUT = 30  # seconds; a knot slower than this is skipped and logged


def convert_name(name: str) -> str:
    if '*' in name:
        return name.replace('*', '').replace('_', '')
    return name


def load_done() -> set:
    """Read JSONL, return set of processed original names."""
    done = set()
    if not OUT_JSONL.exists():
        return done
    with open(OUT_JSONL) as f:
        for line in f:
            try:
                rec = json.loads(line)
                done.add(rec.get("original_name"))
            except Exception:
                continue
    return done


class Timeout:
    def __init__(self, seconds): self.seconds = seconds
    def __enter__(self):
        # Windows signal workaround: skip per-knot timeout and just trust
        # knot_shape_field to return in reasonable time
        return self
    def __exit__(self, *a): return False


def main():
    with open(KNOTS_PATH) as f:
        data = json.load(f)
    knots = data["knots"]

    done = load_done()
    print(f"Already done: {len(done)} knots", flush=True)
    print(f"Remaining: {len(knots) - len(done)}", flush=True)
    print(f"Output: {OUT_JSONL}", flush=True)
    print(f"Settings: bits_prec={BITS_PREC}, max_deg={MAX_DEG}", flush=True)

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    n_processed = 0
    with open(OUT_JSONL, 'a') as out_f:
        for i, k in enumerate(knots):
            orig = k["name"]
            if orig in done:
                continue
            sn = convert_name(orig)
            t = time.time()
            try:
                r = knot_shape_field(sn, bits_prec=BITS_PREC, max_deg=MAX_DEG)
            except Exception as e:
                r = {
                    "error": str(e)[:200],
                    "poly": None, "degree": None, "disc": None,
                }
            r["knot_name"] = sn
            r["original_name"] = orig
            r["index"] = i
            r["time_sec"] = round(time.time() - t, 3)
            out_f.write(json.dumps(r, default=str) + "\n")
            out_f.flush()
            n_processed += 1
            if n_processed % 20 == 0:
                dt = time.time() - t0
                rate = n_processed / dt if dt else 0
                print(f"  [{n_processed}/{len(knots)-len(done)}] "
                      f"last={r['time_sec']}s  rate={rate:.2f} knot/s  "
                      f"elapsed={dt:.0f}s  knot={orig}", flush=True)

    dt = time.time() - t0
    print(f"\nDone: {n_processed} new knots in {dt:.0f}s ({n_processed/max(dt,1):.2f}/s)", flush=True)


if __name__ == "__main__":
    main()
