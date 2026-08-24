"""R2-6 pre-commitment 1 — the channel-capacity (vacuous) reading.

Implements `ergon/probe/SPEC_channel_capacity_2026-08-24.md`, which was committed BEFORE this
ran and fixes every threshold. Read the spec first; this file must not be the place a
threshold is decided.

Measures, per (generator_id, claim_kind) stratum, how many bits of each candidate channel are
available in what a retrieval would return — H_raw (upper bound, inflated by instance values)
and H_template (structural, after instance normalization). $0, local, streaming.

    python ergon/probe/channel_capacity.py
"""
import collections
import json
import math
import os
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS = ROOT / "theseus/corpus"
OUT = ROOT / "ergon/probe/ledgers/channel_capacity"

# ---- fixed by the SPEC, not decidable here -------------------------------------------------
CHANNELS = ("kill_pattern", "canonical_claim_text", "claim_payload", "step_trace")
STRUCTURAL_ZERO_BITS = 1.0
VIABLE_BITS = 3.0
PER_CELL_CAP = 3_000
MIN_CELL_N = 30
SEED = 0

_DIGITS = re.compile(r"\d+")
_FLOATS = re.compile(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?")
_HEX = re.compile(r"\b[0-9a-f]{8,}\b")
_WS = re.compile(r"\s+")


def templated(text):
    """Strip instance particulars, keep structure. Order matters: floats and hex ids before
    bare digits, or the digit rule shreds them into unrecognizable fragments."""
    t = _HEX.sub("#", text)
    t = _FLOATS.sub("#", t)
    t = _DIGITS.sub("#", t)
    return _WS.sub(" ", t).strip()


def channel_value(rec, ch):
    v = rec.get(ch)
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        # payload: keys+shape are the structure, values are the instance
        return json.dumps(v, sort_keys=True, ensure_ascii=False)[:2000]
    return str(v)[:2000]


def entropy(counter):
    n = sum(counter.values())
    if n <= 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in counter.values() if c)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    # reservoir per cell (SPEC §5) — never a head-of-file window
    reservoir = collections.defaultdict(list)
    seen = collections.Counter()
    files = sorted(CORPUS.glob("batch-*.jsonl"))
    print(f"{len(files)} batch files", flush=True)

    for i, f in enumerate(files, 1):
        try:
            with f.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"REJECTED"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if d.get("verdict") != "REJECTED":
                        continue
                    cell = (str(d.get("generator_id")), str(d.get("claim_kind")))
                    seen[cell] += 1
                    # Decide reservoir membership BEFORE extracting channels. Extracting first
                    # meant json.dumps() on all ~132M payloads to decide whether to keep 129k
                    # of them — the sampling is 0.1% but the cost was being paid at 100%.
                    res = reservoir[cell]
                    if len(res) < PER_CELL_CAP:
                        res.append({c: channel_value(d, c) for c in CHANNELS})
                    else:                      # reservoir replacement, uniform over the cell
                        j = rng.randrange(seen[cell])
                        if j < PER_CELL_CAP:
                            res[j] = {c: channel_value(d, c) for c in CHANNELS}
        except Exception as e:                 # a bad file must not kill the measurement
            print(f"  !! {f.name}: {type(e).__name__}", flush=True)
        if i % 5 == 0:
            print(f"  [{i}/{len(files)}] cells={len(reservoir)} "
                  f"sampled={sum(len(v) for v in reservoir.values()):,}", flush=True)

    per_cell = {}
    for cell, recs in reservoir.items():
        row = {"n_sampled": len(recs), "n_population": seen[cell],
               "under_sampled": len(recs) < MIN_CELL_N}
        for ch in CHANNELS:
            vals = [r[ch] for r in recs if r[ch] is not None]
            fill = len(vals) / max(1, len(recs))
            h_raw = entropy(collections.Counter(vals))
            h_tpl = entropy(collections.Counter(templated(v) for v in vals))
            row[ch] = {
                "fill": round(fill, 4),
                "H_raw": round(h_raw, 3),
                "H_template": round(h_tpl, 3),
                "instance_share": round(1 - (h_tpl / h_raw), 4) if h_raw > 0 else None,
                "distinct_templates": len({templated(v) for v in vals}),
            }
        per_cell["/".join(cell)] = row

    usable = {k: v for k, v in per_cell.items() if not v["under_sampled"]}
    mass = sum(v["n_population"] for v in usable.values()) or 1
    summary = {}
    for ch in CHANNELS:
        h = sum(v["n_population"] * v[ch]["H_template"] for v in usable.values()) / mass
        zero_cells = {k: v[ch]["H_template"] for k, v in usable.items()
                      if v[ch]["H_template"] < STRUCTURAL_ZERO_BITS}
        zero_mass = sum(usable[k]["n_population"] for k in zero_cells) / mass
        summary[ch] = {
            "H_template_mass_weighted": round(h, 3),
            "verdict": ("STRUCTURAL-ZERO" if h < STRUCTURAL_ZERO_BITS else
                        "VIABLE" if h >= VIABLE_BITS else "MARGINAL"),
            "cells_structurally_zero": len(zero_cells),
            "corpus_mass_in_zero_cells": round(zero_mass, 4),
            "fill_mass_weighted": round(
                sum(v["n_population"] * v[ch]["fill"] for v in usable.values()) / mass, 4),
        }

    result = {
        "spec": "ergon/probe/SPEC_channel_capacity_2026-08-24.md (thresholds fixed before data)",
        "thresholds": {"structural_zero_bits": STRUCTURAL_ZERO_BITS, "viable_bits": VIABLE_BITS},
        "cells_total": len(per_cell),
        "cells_under_sampled_excluded": sum(1 for v in per_cell.values() if v["under_sampled"]),
        "records_sampled": sum(v["n_sampled"] for v in per_cell.values()),
        "records_population": sum(seen.values()),
        "summary": summary,
        "negative_control": {
            "channel": "kill_pattern",
            "expectation": "must reproduce a known near-zero (full scan: 68% of corpus in "
                           "cells with <=3 bits, 12.6% at 0 bits). If it reads VIABLE, the "
                           "INSTRUMENT is wrong and no other number here may be used.",
        },
        "per_cell": per_cell,
    }
    tmp = (OUT / "capacity.json").with_suffix(".json.tmp")
    tmp.write_text(json.dumps(result, indent=2), encoding="utf-8")
    os.replace(tmp, OUT / "capacity.json")
    print(json.dumps({"summary": summary,
                      "cells": len(per_cell),
                      "sampled": result["records_sampled"]}, indent=2), flush=True)


if __name__ == "__main__":
    sys.exit(main())
