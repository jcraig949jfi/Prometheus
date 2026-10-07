"""B23b -- C6-native re-audit of the 102 composed-world frontier runs (constant twin + blind twin).

B23 scored the 28 wse.WorldSpec frontier runs (54% of competent organisms were timing exploits). The other 102 runs
used c6.composed.v1 worlds (archaeon/campaign6/worlds/runtime.py: feedback worlds, 24 ticks). Jitter is not the right
control there, so two controls per run, on the run's best final organism (best of the checkpointed population under
this evaluation):
  CONSTANT TWIN  the best fixed-output program: every tick, output constant c on every output channel, c over a
                 grid (0..15, 2^31, 2^32-1). Competence that does not beat it is not competence (feedback memory:
                 constant twin for competence).
  BLIND TWIN     the same elite with every observation word replaced by 0 (channel shapes kept): does it use its
                 inputs at all?
Readout per run: elite reward, best constant reward, blind reward; classes BEATS_CONSTANT (elite - constant >= .05),
INPUT_USING (elite - blind >= .05). Evaluation: archaeon.campaign6.worlds.runtime.evaluate_world, seed = the run's
spec seed, E = 8, rng_seed 7 (identical for elite and twins).
PREDICTION (before running): in >= 50% of runs the elite does NOT beat its constant twin by .05.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

from archaeon.campaign6.segment import resolve_world
from archaeon.campaign6.worlds.runtime import evaluate_world

RUNS = Path("D:/Prometheus-worktrees/archaeon-wse-2026-09-16/archaeon/frontier/runs")
OUT = Path(__file__).resolve().parent / "results"
CONSTS = list(range(16)) + [1 << 31, (1 << 32) - 1]


def constant_manifest(c, K):
    g = [3, 1, c & 0xFFFFFFFF, 0]                       # LDC r1, c
    for ch in range(K):
        g += [3, 2, ch, 0, 23, 1, 2, 0]                 # LDC r2, ch ; OUT r1 on ch r2
    g += [1, 0, 0, 0]                                   # HALT
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": 4, "tape_words": max(16, ((len(g) + 3) // 4) * 4 + 16),
            "genome": g, "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 1}


class Blind:
    """Wraps a ComposedWorld: observations keep their shape but every word is 0."""
    def __init__(self, w):
        self.w = w
        self.K = w.K
        self.features = getattr(w, "features", None)

    def __getattr__(self, k):
        return getattr(self.w, k)

    def observe(self, st):
        return [[0] * len(ch) for ch in self.w.observe(st)]


def score(m, world, seed):
    return evaluate_world(m, world, seed, 8, rng_seed=7)["reward"]


def main(argv):
    limit = int(argv[0]) if argv else 10 ** 9
    rows = []
    n = 0
    for fam in sorted(p for p in RUNS.iterdir() if p.is_dir()):
        for exp in sorted(p for p in fam.iterdir() if p.is_dir()):
            chunks = sorted(exp.glob("chunk_*.json.gz"))
            if not chunks:
                continue
            c = json.load(gzip.open(chunks[-1]))
            wd = c["spec"].get("world", {})
            if wd.get("kind") != "c6.composed.v1":
                continue
            n += 1
            if n > limit:
                break
            try:
                world = resolve_world(wd)
                seed = c["spec"].get("provenance", {}).get("seed", 0) or 0
                pop = (c["out"].get("checkpoint_out") or {}).get("population", [])
                scored = []
                for org in pop:
                    try:
                        scored.append((score(org["manifest"], world, seed), org["manifest"]))
                    except Exception:                                     # noqa: BLE001
                        pass
                if not scored:
                    rows.append({"exp": exp.name, "error": "no scorable organism"}); continue
                er, em = max(scored, key=lambda z: z[0])
                const = max(score(constant_manifest(v, world.K), world, seed) for v in CONSTS)
                blind = score(em, Blind(world), seed)
                rows.append({"exp": exp.name, "family": fam.name, "features": getattr(world, "features", None), "K": world.K,
                             "elite": round(er, 4), "constant": round(const, 4), "blind": round(blind, 4),
                             "beats_constant": er - const >= .05, "input_using": er - blind >= .05})
            except Exception as e:                                         # noqa: BLE001
                rows.append({"exp": exp.name, "error": repr(e)[:200]})
            print(json.dumps(rows[-1]), flush=True)
    ok = [r for r in rows if "elite" in r]
    summ = {"runs": len(rows), "scored": len(ok), "beats_constant": sum(r["beats_constant"] for r in ok),
            "input_using": sum(r["input_using"] for r in ok),
            "both": sum(r["beats_constant"] and r["input_using"] for r in ok)}
    print(json.dumps(summ), flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "B23b_result.json").write_text(json.dumps({"probe": "B23b", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
