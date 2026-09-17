"""Campaign-2 telemetry helpers (directive Phase A, groups E and H).

genome_summary   length / opcode-composition summary of one manifest (L-027)
maturity         source-maturity block for any artifact that can enter another population
                 (L-010; SFE-10's one paying exchange came from a producer that had SOLVED
                 its own cell -- that variable is first-class here)
origin_shares    share of a population carrying each origin tag (imported-lineage share)
rung_matrix      competence of one manifest on every rung of a ladder (rung x generation
                 matrices are built by calling this every k generations; L-022)
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence

from proteus.foundry.affordances import CATEGORY, MNEMONIC, N_OPCODES

CHANCE_4BIT = 1.0 / 16
SOLVE_THRESHOLD = 0.5


def genome_summary(manifest: dict) -> dict:
    g = manifest["genome"]
    ops = [w % N_OPCODES for w in g[0::4]]
    cats: Dict[str, int] = {}
    for o in ops:
        cats[CATEGORY[o]] = cats.get(CATEGORY[o], 0) + 1
    n = max(1, len(ops))
    return {
        "instr": len(ops),
        "words": len(g),
        "distinct_opcodes": len(set(ops)),
        "category_shares": {k: round(v / n, 4) for k, v in sorted(cats.items())},
        "opcode_hist": {MNEMONIC[o] if isinstance(MNEMONIC, (list, tuple, dict)) else str(o): ops.count(o) for o in sorted(set(ops))},
        "n_regs": manifest.get("n_regs"), "tape_words": manifest.get("tape_words"),
        "persist": manifest.get("persist"), "tick_budget": manifest.get("tick_budget"),
    }


def population_summary(manifests: Iterable[dict]) -> dict:
    ms = list(manifests)
    if not ms:
        return {"n": 0}
    lens = sorted(len(m["genome"]) // 4 for m in ms)
    cats: Dict[str, float] = {}
    for m in ms:
        for k, v in genome_summary(m)["category_shares"].items():
            cats[k] = cats.get(k, 0.0) + v
    return {"n": len(ms), "instr_min": lens[0], "instr_median": lens[len(lens) // 2], "instr_max": lens[-1],
            "instr_mean": round(sum(lens) / len(lens), 2),
            "category_shares_mean": {k: round(v / len(ms), 4) for k, v in sorted(cats.items())}}


def maturity(source_cell: str, elite_reward: float, final_rewards: Sequence[float], *, chance: float,
             budget: dict, competence: Optional[float] = None, generation: Optional[int] = None,
             lineage: Optional[dict] = None, solve_threshold: float = SOLVE_THRESHOLD) -> dict:
    """The first-class maturity block. `solved` is the variable SFE-10 said matters."""
    n = max(1, len(final_rewards))
    above = sum(1 for r in final_rewards if r > chance)
    return {
        "source_cell": source_cell,
        "source_elite_reward": round(float(elite_reward), 6),
        "source_competence": None if competence is None else round(float(competence), 6),
        "share_above_chance": round(above / n, 4),
        "chance": chance,
        "solved": bool(elite_reward >= solve_threshold),
        "solve_threshold": solve_threshold,
        "source_budget": dict(budget),
        "source_generation": generation,
        "lineage": lineage or {},
    }


def maturity_state(m: dict) -> Optional[str]:
    """RESIDUE_BELOW_FLOOR: nothing in the source population beat chance and the elite did not.
    IMMATURE_ARTIFACT: the source never solved its own cell. None: mature."""
    if m["share_above_chance"] == 0.0 and m["source_elite_reward"] <= m["chance"]:
        return "RESIDUE_BELOW_FLOOR"
    if not m["solved"]:
        return "IMMATURE_ARTIFACT"
    return None


def origin_shares(pop: Sequence[dict]) -> dict:
    n = max(1, len(pop))
    counts: Dict[str, int] = {}
    for org in pop:
        for tag in org.get("origins", ("gen0",)):
            counts[tag] = counts.get(tag, 0) + 1
    return {k: round(v / n, 4) for k, v in sorted(counts.items())}


def rung_matrix_row(evaluate_fn, manifest: dict, rungs: Sequence[tuple], gen: int) -> dict:
    """One row of the rung x generation matrix: rungs = [(label, episodes, rng_seed), ...]."""
    row = {"gen": gen}
    for label, episodes, rng_seed in rungs:
        row[str(label)] = round(evaluate_fn(manifest, episodes, rng_seed=rng_seed)["reward"], 6)
    return row


def probe_plan(G: int, transitions: Sequence[int], dense: int = 5, sparse: int = 5) -> List[int]:
    """Generations at which a curriculum probes every rung (campaign 3, Phase A group D):
    every generation within `dense` of a transition (before, at, after), every `sparse`
    generations elsewhere, plus 0 and G-1. Cheap where nothing changes, dense where it does."""
    gens = set(range(0, G, sparse)) | {0, G - 1}
    for t in transitions:
        gens |= set(range(max(0, t - dense), min(G, t + dense + 1)))
    return sorted(g for g in gens if 0 <= g < G)


def transition_events(matrix: List[dict], rung: str, *, appear: float = 0.5, collapse: float = 0.25) -> dict:
    """From a rung x generation matrix: the generation competence on `rung` first APPEARS
    (>= appear), first COLLAPSES (falls >= collapse below its running peak after appearing)
    and first RECOVERS (returns to >= appear after a collapse)."""
    peak = -1.0; appeared = collapsed = recovered = None
    for row in matrix:
        v = row.get(rung)
        if v is None:
            continue
        if appeared is None and v >= appear:
            appeared = row["gen"]
        if v > peak:
            peak = v
        if appeared is not None and collapsed is None and peak - v >= collapse:
            collapsed = row["gen"]
        if collapsed is not None and recovered is None and row["gen"] > collapsed and v >= appear:
            recovered = row["gen"]
    return {"appeared": appeared, "collapsed": collapsed, "recovered": recovered, "peak": peak if peak >= 0 else None}


def shelf_report(matrix: List[dict], rungs: Sequence[str], drop: float = 0.25) -> dict:
    """Where a rung's competence FELL by >= `drop` from its running maximum: the forgetting
    shelf SFE-05's battery mean hid. Reported per rung with the generation of the fall."""
    out = {}
    for r in rungs:
        best = -1.0; fell_at = None; low = None
        for row in matrix:
            v = row.get(r)
            if v is None:
                continue
            if v > best:
                best = v
            if best - v >= drop and fell_at is None:
                fell_at = row["gen"]; low = v
        out[r] = {"peak": best, "fell_at_gen": fell_at, "value_at_fall": low}
    return out
