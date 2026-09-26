"""Chance floors of the honest ruler used by the replay (trap_generator_extended,
n_per_category=2, seed=42: 186 traps / 89 categories). Published BEFORE any model
call so every replay number can be read against them (measurement carries its
answer). Deterministic, no LLM.

Decoys: NCD baseline (the 1.0 pass gate's comparator), random-ranking tool (200
seeds), constant-first-candidate tool, constant-last-candidate tool, and the
position-majority tool (always picks the index that is most often correct in
this battery -- the cheapest counterfeit). Writes floors.json beside this file.

Run from the worktree root:
  PYTHONPATH=agents/hephaestus/src python hephaestus/xpol_2026/floors.py
"""
from __future__ import annotations
import collections, json, random, statistics, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "agents/hephaestus/src"))
from trap_generator_extended import generate_full_battery  # noqa: E402
from test_harness import _run_battery, _NCDBaseline, CATEGORY_TIER  # noqa: E402

SEED, NPC = 42, 2


class RandomTool:
    def __init__(self, seed): self.r = random.Random(seed)
    def evaluate(self, prompt, candidates):
        c = list(candidates); self.r.shuffle(c)
        return [{"candidate": x, "score": 1.0 - i * 0.01, "reasoning": ""} for i, x in enumerate(c)]
    def confidence(self, prompt, cand): return self.r.random()


class ConstantIndex:
    def __init__(self, idx): self.idx = idx
    def evaluate(self, prompt, candidates):
        c = list(candidates); i = self.idx if self.idx >= 0 else len(c) + self.idx
        i = max(0, min(len(c) - 1, i)); top = c.pop(i)
        return [{"candidate": top, "score": 1.0, "reasoning": ""}] + [{"candidate": x, "score": 0.5, "reasoning": ""} for x in c]
    def confidence(self, prompt, cand): return 0.5


def by_tier(res, battery):
    t = collections.defaultdict(lambda: [0, 0])
    for r, trap in zip(res["trap_results"], battery):
        k = CATEGORY_TIER.get(trap["category"], "?"); t[k][1] += 1; t[k][0] += int(r["is_correct"])
    return {k: {"correct": v[0], "n": v[1], "acc": round(v[0] / v[1], 4)} for k, v in sorted(t.items())}


def main():
    b = generate_full_battery(n_per_category=NPC, seed=SEED)
    idx_hist = collections.Counter(t["candidates"].index(t["correct"]) for t in b)
    majority_idx = idx_hist.most_common(1)[0][0]
    out = {"ruler": {"generator": "agents/hephaestus/src/trap_generator_extended.generate_full_battery", "n_per_category": NPC, "seed": SEED,
                     "n_traps": len(b), "n_categories": len({t["category"] for t in b}),
                     "tiers": dict(collections.Counter(CATEGORY_TIER.get(t["category"], "?") for t in b)),
                     "candidate_count_hist": dict(sorted(collections.Counter(len(t["candidates"]) for t in b).items())),
                     "correct_index_hist": dict(sorted(idx_hist.items()))},
           "chance_floor_accuracy": round(statistics.mean(1 / len(t["candidates"]) for t in b), 4),
           "computed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    ncd = _run_battery(_NCDBaseline(), b)
    out["ncd_baseline"] = {"accuracy": round(ncd["accuracy"], 4), "calibration": round(ncd["calibration"], 4), "by_tier": by_tier(ncd, b)}
    for name, tool in [("constant_first", ConstantIndex(0)), ("constant_last", ConstantIndex(-1)), (f"position_majority(idx={majority_idx})", ConstantIndex(majority_idx))]:
        r = _run_battery(tool, b)
        out[name] = {"accuracy": round(r["accuracy"], 4), "calibration": round(r["calibration"], 4), "by_tier": by_tier(r, b)}
    accs, cals, passes = [], [], 0
    for s in range(200):
        r = _run_battery(RandomTool(s), b); accs.append(r["accuracy"]); cals.append(r["calibration"])
        passes += int((r["accuracy"] > ncd["accuracy"] or r["calibration"] > ncd["calibration"]) and r["accuracy"] >= ncd["accuracy"] and r["calibration"] >= ncd["calibration"])
    out["random_tool_200"] = {"acc_mean": round(statistics.mean(accs), 4), "acc_max": round(max(accs), 4), "acc_p95": round(sorted(accs)[int(0.95 * 199)], 4),
                              "cal_mean": round(statistics.mean(cals), 4), "P_pass_1p0_gate": round(passes / 200, 4)}
    (HERE / "floors.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "ruler"}, indent=1)[:1500])


if __name__ == "__main__":
    main()
