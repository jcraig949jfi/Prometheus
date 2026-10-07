"""B23 -- re-audit the Deep Frontier record with today's instruments (Phase 2-B: no old positive presumed valid).

Read-only on the off-repo evidence D:/Prometheus-worktrees/archaeon-wse-2026-09-16/archaeon/frontier/runs (2.3 GB,
2026-09-18..22). For every experiment directory with a segment checkpoint whose world is a wse.WorldSpec, take the
LAST chunk's checkpoint_out population and score each organism on that world's held-out episodes, plain vs the B08K
wide timing jitter (0-7 NOISE ticks before each ask). Per run: median plain, median jitter, share of competent
organisms (plain >= .9) that are TIMING EXPLOITS (jitter drop >= .15).
Worlds of another kind (C6 composed worlds etc.) are counted and listed, not scored here.

PREDICTION (before running): on single-stream fixed-timing worlds (W0-like), >= 50% of competent final organisms are
timing exploits; the frontier's competence numbers on those worlds overstate stored-state memory.
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter
from pathlib import Path

from archaeon.beta.b08k_wide_jitter_rescore import wide
from archaeon.wse.evolve import evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for

RUNS = Path("D:/Prometheus-worktrees/archaeon-wse-2026-09-16/archaeon/frontier/runs")
OUT = Path(__file__).resolve().parent / "results"
CAMPAIGN_SEED = 20260921


def last_chunk(exp_dir: Path):
    chunks = sorted(exp_dir.glob("chunk_*.json.gz"))
    return chunks[-1] if chunks else None


def main(argv):
    rows, kinds = [], Counter()
    for fam in sorted(p for p in RUNS.iterdir() if p.is_dir()):
        for exp in sorted(p for p in fam.iterdir() if p.is_dir()):
            ch = last_chunk(exp)
            if ch is None:
                kinds["no_chunk"] += 1
                continue
            try:
                c = json.load(gzip.open(ch))
            except Exception as e:                 # noqa: BLE001 -- recorded, not fatal
                rows.append({"exp": exp.name, "error": repr(e)[:200]}); continue
            world = c["spec"].get("world", {})
            kinds[world.get("kind", "?")] += 1
            if world.get("kind") != "wse.WorldSpec":
                rows.append({"exp": exp.name, "world_kind": world.get("kind"), "scored": False}); continue
            knobs = dict(world["knobs"])
            try:
                spec = WorldSpec(**knobs)
                eps = episodes_for(spec, CAMPAIGN_SEED, "heldout", 7, 48)
            except Exception as e:                 # noqa: BLE001
                rows.append({"exp": exp.name, "world": knobs.get("name"), "error": "world: " + repr(e)[:160]}); continue
            jit = wide(eps, ("b23", exp.name))
            pop = (c["out"].get("checkpoint_out") or {}).get("population", [])
            sc = []
            for org in pop:
                m = org["manifest"]
                try:
                    a = evaluate(m, eps, rng_seed=7)["reward"]; b = evaluate(m, jit, rng_seed=7)["reward"]
                except Exception as e:             # noqa: BLE001 -- e.g. graph manifests in a v0 evaluator
                    sc.append(None); continue
                sc.append((a, b))
            good = [x for x in sc if x and x[0] >= .9]
            med = lambda v: sorted(v)[len(v) // 2] if v else None   # noqa: E731
            rows.append({"exp": exp.name, "world": knobs.get("name"), "K": knobs.get("K"), "n": len(pop),
                         "unscorable": sum(1 for x in sc if x is None),
                         "median_plain": med([x[0] for x in sc if x]), "median_jitter": med([x[1] for x in sc if x]),
                         "competent": len(good), "competent_timing_exploit": sum(1 for x in good if x[0] - x[1] >= .15)})
            print(json.dumps(rows[-1]), flush=True)
    tot_c = sum(r.get("competent", 0) for r in rows)
    tot_t = sum(r.get("competent_timing_exploit", 0) for r in rows)
    summ = {"world_kinds": dict(kinds), "competent": tot_c, "competent_timing_exploit": tot_t,
            "share": round(tot_t / tot_c, 4) if tot_c else None}
    print(json.dumps(summ), flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "B23_result.json").write_text(json.dumps({"probe": "B23", "runs_root": str(RUNS), "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
