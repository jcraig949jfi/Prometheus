"""X-STATE (EXPLORE, MEASUREMENT; child of X-POSITION). Declared before running.

X-POSITION: none of the 16 panel donor genomes copies from FRESH registers (0/16 either
direction), yet their P-11 events passed the assay run with the donor's OBSERVED registers.
So copying here may be a property of genome + register state, not of the genome alone.

Method: replay the first 200 epochs of a CONFIRMED runaway (C-RUNAWAY splice-off seed that ran
away; chosen as the lowest-index runaway seed in C-RUNAWAY's results), and for every P-11-causal
event in epochs 1-200 (up to 300 sampled deterministically, every k-th) re-assay the same donor
genome and victim side with (i) its observed registers and (ii) fresh zeroed registers.
Readout: pass rate with observed registers (should be ~1 by construction) vs fresh registers.
Classification: STATE_DEPENDENT if the fresh-register pass rate < 0.25; GENOME_SUFFICIENT if
>= 0.75; MIXED otherwise.
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
C9 = ROOT.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"


def main():
    import p11
    import world
    import z8
    res = json.loads((ROOT / "c_runaway_confirm" / "RESULTS.json").read_text())
    seed_idx = min(r["s"] for r in res if r["arm"] == "NO_RECOMB" and r["depth"] >= 20)
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    cell = dict(arm["cell"], atlas_axis="NONE")
    captured = []

    real_assay = p11.assay

    def capturing(z8m, **kw):
        out = real_assay(z8m, **kw)
        if out["pass"]:
            captured.append(dict(kw))
        return out
    p11.assay = capturing
    try:
        world.Runner(cell, 9_990_500 + seed_idx, tier=arm["tier"], max_epochs=200, implant="ACTUAL_GENOME",
                     implant_bytes=bytes.fromhex(arm["kwargs"]["implant_hex"])).run()
    finally:
        p11.assay = real_assay
    step = max(1, len(captured) // 300)
    sample = captured[::step][:300]
    obs_pass = fresh_pass = 0
    for kw in sample:
        o = real_assay(z8, **dict(kw, seed=("X-STATE", "obs") + tuple(kw["seed"])))
        f = real_assay(z8, **dict(kw, st_a=(None, 0, 0), st_b=(None, 0, 0),
                                  seed=("X-STATE", "fresh") + tuple(kw["seed"])))
        obs_pass += o["pass"]
        fresh_pass += f["pass"]
    n = len(sample)
    fr = fresh_pass / n if n else None
    cls = ("STATE_DEPENDENT" if fr is not None and fr < 0.25 else
           "GENOME_SUFFICIENT" if fr is not None and fr >= 0.75 else "MIXED")
    out = {"classification": cls, "runaway_seed": 9_990_500 + seed_idx, "p11_events_epochs_1_200": len(captured),
           "sampled": n, "pass_rate_observed_registers": round(obs_pass / n, 3) if n else None,
           "pass_rate_fresh_registers": round(fr, 3) if fr is not None else None}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
