"""Persistent REACHABILITY TABLE (campaign 2, Phase A group A; L-017, L-028; L2-016).

One row per run (append-only JSONL), keyed by cell, value_bits, N, G, E, regime AND the
generation-0 FOUNDRY (the sampling distribution of generation 0 is part of the regime: the v01
survey sampled genomes of 1-32 instructions, campaigns 1 and 2 sample 1-16, and W1_d1 8-bit
reads 2/3 under the first and 1/6 under the second -- C2-SFE-02 attempt 1 found the gap).
Pooled summaries carry a Wilson band; five classes:

  COMMON                              pooled lower band >= 0.5
  REACHABLE                           reached at least once, pooled frequency >= 0.25
  RARE                                reached at least once, pooled frequency < 0.25
  UNESTABLISHED                       fewer than 3 baseline runs and none reached
  OBSERVED_UNREACHABLE_AT_BUDGET      >= 3 baseline runs, none reached (the band's upper
                                      edge is reported: 0/3 is < 0.71 at 95%, not "impossible")

A "baseline" run is a plain search from the cell's own generation 0 with no intervention
and no substituted organisms under the standard grammar; only baseline runs pool into the
classes. Treated runs are recorded too (kind='treated').

This is an instrument for knowing what question a budget buys, not a rule that forbids
exploration: candidates() returns cells in a requested band; lookup() never refuses.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from .worlds import WorldSpec

REPO = Path(__file__).resolve().parents[2]
TABLE = REPO / "archaeon" / "campaign2" / "REACHABILITY.jsonl"
KEY = ("cell", "value_bits", "N", "G", "E", "regime", "foundry")
CLASSES = ("COMMON", "REACHABLE", "RARE", "UNESTABLISHED", "OBSERVED_UNREACHABLE_AT_BUDGET")


def foundry_id(foundry: Optional[dict]) -> str:
    """'instr<lo>-<hi>:<8 hex>' over the foundry dict minus seed/n: the generation-0 regime."""
    from .evolve import FOUNDRY
    f = dict(foundry or FOUNDRY)
    f.pop("seed", None); f.pop("n", None)
    lo, hi = f.get("genome_instr_range", [0, 0])
    return "instr%d-%d:%s" % (lo, hi, hashlib.sha256(json.dumps(f, sort_keys=True).encode()).hexdigest()[:8])


def default_foundry_id() -> str:
    from .evolve import FOUNDRY
    return foundry_id(dict(FOUNDRY, genome_instr_range=[1, 16], tape_words_choices=[16, 32, 64, 128, 256], tick_budget_choices=[16, 64, 256]))


def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4))


def classify(n: int, k: int) -> str:
    if n == 0:
        return "UNESTABLISHED"
    lo, _hi = wilson(k, n)
    if k == 0:
        return "OBSERVED_UNREACHABLE_AT_BUDGET" if n >= 3 else "UNESTABLISHED"
    if lo >= 0.5:
        return "COMMON"
    if k / n >= 0.25:
        return "REACHABLE"
    return "RARE"


def spec_of(knobs: dict) -> WorldSpec:
    kw = {k: (tuple(v) if isinstance(v, list) else v) for k, v in knobs.items()}
    return WorldSpec(**kw)


def row(spec: WorldSpec, *, N: int, G: int, E: int, regime: str, seed: int, source: dict,
        first_solved_gen: Optional[int], best_train_max: float, heldout: Optional[float] = None,
        kind: str = "baseline", solve_threshold: float = 0.5, trace_best: Optional[Sequence[float]] = None,
        foundry: Optional[str] = None, campaign_seed: Optional[int] = None, rng_label: Optional[str] = None) -> dict:
    """campaign_seed + rng_label + seed identify the RUN: under common random numbers two
    experiments that search the same cell at the same budget with the same seeds produce the
    same run, and pooled() counts it once (C2-SFE-02's control arm reproduced C2-SFE-01's
    fresh arm row for row)."""
    return {
        "cell": spec.name, "world_id": spec.world_id(), "knobs": spec.knobs(), "value_bits": spec.value_bits,
        "N": N, "G": G, "E": E, "regime": regime, "foundry": foundry or default_foundry_id(), "seed": seed, "kind": kind, "source": source,
        "campaign_seed": campaign_seed, "rng_label": rng_label,
        "solve_threshold": solve_threshold, "first_solved_gen": first_solved_gen,
        "reached": first_solved_gen is not None, "best_train_max": round(float(best_train_max), 6),
        "heldout": None if heldout is None else round(float(heldout), 6),
        "eval_resolution": round(1.0 / max(1, E), 6),
        "trace_best": None if trace_best is None else [round(float(x), 4) for x in trace_best],
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def row_from_result(spec: WorldSpec, res: dict, *, N: int, G: int, E: int, regime: str, seed: int,
                    source: dict, heldout: Optional[float] = None, kind: Optional[str] = None,
                    foundry: Optional[dict] = None, campaign_seed: Optional[int] = None) -> dict:
    """A table row straight from run_cell()/Evolution.result(): kind is baseline iff the loop
    reports a verified common generation 0 with nothing substituted (pass kind='treated' for a
    non-standard operator set); foundry is the generation-0 dict the run used."""
    prov = res.get("gen0_provenance") or {}
    if kind is None:
        kind = "baseline" if prov.get("verified_common") and prov.get("n_substituted", 0) == 0 else "treated"
    tb = [t["best_reward"] for t in res["trace"]]
    return row(spec, N=N, G=G, E=E, regime=regime, seed=seed, source=source, first_solved_gen=res.get("first_solved_gen"),
               best_train_max=max(tb) if tb else 0.0, heldout=heldout, kind=kind,
               solve_threshold=res.get("solve_threshold", 0.5), trace_best=tb, foundry=foundry_id(foundry) if foundry else None,
               campaign_seed=prov.get("campaign_seed", campaign_seed), rng_label=res.get("rng_label"))


def _identity(r: dict) -> tuple:
    s = r.get("source", {})
    return (r["cell"], r["value_bits"], r["N"], r["G"], r["E"], r["regime"], r.get("foundry"), r["seed"], r["kind"],
            s.get("campaign"), s.get("experiment"), s.get("arm"), s.get("attempt"))


def run_identity(r: dict) -> tuple:
    """The RUN a baseline row measured: same cell, budget, foundry, campaign seed, rng label
    and seed = the same deterministic search, whichever experiment ran it."""
    return (r["cell"], r["value_bits"], r["N"], r["G"], r["E"], r["regime"], r.get("foundry"),
            r.get("campaign_seed"), r.get("rng_label"), r["seed"])


def dedupe_runs(rows: Iterable[dict]) -> List[dict]:
    seen = set(); out = []
    for r in rows:
        if r.get("kind") == "baseline" and r.get("campaign_seed") is not None:
            k = run_identity(r)
            if k in seen:
                continue
            seen.add(k)
        out.append(r)
    return out


def load(path: Path = TABLE) -> List[dict]:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def record(rows: Iterable[dict], path: Path = TABLE) -> int:
    """Append rows not already present (identity = key + seed + kind + source). Returns the
    number appended."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    have = {_identity(r) for r in load(p)}
    n = 0
    with p.open("a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            if _identity(r) in have:
                continue
            f.write(json.dumps(r, sort_keys=True) + "\n")
            have.add(_identity(r)); n += 1
    return n


def pooled(rows: Iterable[dict], kinds: Sequence[str] = ("baseline",), key: Sequence[str] = KEY) -> Dict[tuple, dict]:
    out: Dict[tuple, dict] = {}
    for r in dedupe_runs(rows):
        if r.get("kind") not in kinds:
            continue
        k = tuple(r.get(x) for x in key)
        s = out.setdefault(k, {kk: r.get(kk) for kk in key} | {"n": 0, "k": 0, "first_solved_gens": [], "best_train_max": 0.0,
                                                              "heldout_max": None, "eval_resolution": r.get("eval_resolution"),
                                                              "sources": set(), "seeds": []})
        s["n"] += 1
        s["seeds"].append(r.get("seed"))
        if r.get("reached"):
            s["k"] += 1
            s["first_solved_gens"].append(r.get("first_solved_gen"))
        s["best_train_max"] = max(s["best_train_max"], r.get("best_train_max") or 0.0)
        if r.get("heldout") is not None:
            s["heldout_max"] = max(s["heldout_max"] or 0.0, r["heldout"])
        src = r.get("source", {})
        s["sources"].add("%s/%s/%s" % (src.get("campaign"), src.get("experiment"), src.get("arm")))
    for s in out.values():
        s["freq"] = round(s["k"] / s["n"], 4) if s["n"] else None
        s["band95"] = wilson(s["k"], s["n"])
        s["class"] = classify(s["n"], s["k"])
        s["first_solved_gens"] = sorted(x for x in s["first_solved_gens"] if x is not None)
        s["median_first_solved_gen"] = (s["first_solved_gens"][len(s["first_solved_gens"]) // 2] if s["first_solved_gens"] else None)
        s["sources"] = sorted(s["sources"])
    return out


def lookup(cell: str, *, value_bits: int, N: Optional[int] = None, G: Optional[int] = None, E: Optional[int] = None,
           regime: str = "E0", foundry: Optional[str] = "default", G_min: Optional[int] = None, G_max: Optional[int] = None,
           rows: Optional[List[dict]] = None, path: Path = TABLE) -> dict:
    """The pooled estimate for a cell at a budget (exact N/G/E when given) or across budgets
    with G in [G_min, G_max], under one generation-0 foundry ('default' = the campaign
    foundry; None = pool across foundries, reported as such). Never refuses: an empty pool
    comes back UNESTABLISHED."""
    fid = default_foundry_id() if foundry == "default" else foundry
    rs = rows if rows is not None else load(path)
    sel = [r for r in rs if r["cell"] == cell and r["value_bits"] == value_bits and r["regime"] == regime and r["kind"] == "baseline"]
    if fid is not None:
        sel = [r for r in sel if r.get("foundry") == fid]
    if N is not None:
        sel = [r for r in sel if r["N"] == N]
    if E is not None:
        sel = [r for r in sel if r["E"] == E]
    if G is not None:
        sel = [r for r in sel if r["G"] == G]
    if G_min is not None:
        sel = [r for r in sel if r["G"] >= G_min]
    if G_max is not None:
        sel = [r for r in sel if r["G"] <= G_max]
    p = pooled(sel, key=("cell", "value_bits", "regime"))
    if not p:
        return {"cell": cell, "value_bits": value_bits, "regime": regime, "foundry": fid, "n": 0, "k": 0, "freq": None,
                "band95": (0.0, 1.0), "class": "UNESTABLISHED", "budgets": [], "first_solved_gens": [],
                "median_first_solved_gen": None, "best_train_max": None, "heldout_max": None}
    s = list(p.values())[0]
    s["foundry"] = fid
    s["budgets"] = sorted({(r["N"], r["G"], r["E"]) for r in sel})
    s["foundries_pooled"] = sorted({r.get("foundry") for r in sel})
    return s


def candidates(lo: float, hi: float, *, value_bits: Optional[int] = None, regime: str = "E0", foundry: Optional[str] = "default",
               min_n: int = 3, rows: Optional[List[dict]] = None, path: Path = TABLE, key: Sequence[str] = KEY) -> List[dict]:
    """Cells (at their recorded budgets) whose pooled baseline frequency lies in [lo, hi] with
    at least min_n runs, nearest to the band's centre first."""
    fid = default_foundry_id() if foundry == "default" else foundry
    rs = rows if rows is not None else load(path)
    if value_bits is not None:
        rs = [r for r in rs if r["value_bits"] == value_bits]
    rs = [r for r in rs if r["regime"] == regime]
    if fid is not None:
        rs = [r for r in rs if r.get("foundry") == fid]
    out = [s for s in pooled(rs, key=key).values() if s["n"] >= min_n and s["freq"] is not None and lo <= s["freq"] <= hi]
    mid = (lo + hi) / 2
    return sorted(out, key=lambda s: (abs(s["freq"] - mid), -s["n"]))


def table_text(summaries: Iterable[dict]) -> str:
    lines = ["%-14s %4s %5s %5s %3s %-5s %-11s %3s %3s %-6s %-13s %-32s %s" % ("cell", "bits", "N", "G", "E", "reg", "foundry", "n", "k", "freq", "band95", "class", "first_solved")]
    for s in sorted(summaries, key=lambda s: (s["cell"], s["value_bits"], s["N"], s["G"], s["E"], s["regime"], str(s.get("foundry")))):
        lines.append("%-14s %4d %5d %5d %3d %-5s %-11s %3d %3d %-6s %-13s %-32s %s" % (
            s["cell"], s["value_bits"], s["N"], s["G"], s["E"], s["regime"], str(s.get("foundry"))[:11], s["n"], s["k"],
            "-" if s["freq"] is None else "%.2f" % s["freq"], "%.2f-%.2f" % tuple(s["band95"]), s["class"],
            ",".join(str(x) for x in s["first_solved_gens"]) or "-"))
    return "\n".join(lines)


# ------------------------------------------------------------------ campaign-1 import
def _sfe_spec(name: str) -> WorldSpec:
    table = {
        "W0": WorldSpec("W0", value_bits=4), "W1_d1": WorldSpec("W1_d1", delay=1, value_bits=4),
        "W1_d4": WorldSpec("W1_d4", delay=4, value_bits=4), "W2_K2": WorldSpec("W2_K2", K=2, value_bits=4),
        "W3_K2": WorldSpec("W3_K2", K=2, ask_mode="one", value_bits=4),
    }
    return table[name]


def _first_solved(trace_best: Sequence[float], thr: float = 0.5) -> Optional[int]:
    for i, v in enumerate(trace_best):
        if v >= thr:
            return i
    return None


def import_campaign1(repo: Path = REPO, path: Path = TABLE) -> dict:
    """Every campaign-1 search whose generation 0 was the cell's own random population and
    whose loop ran without an intervention (kind=baseline), plus the treated arms, plus the
    v01 survey (foundry instr1-32) and the SSF cycles (instr1-16). Idempotent."""
    from .evolve import FOUNDRY
    c1 = repo / "archaeon" / "campaign1"
    F16 = default_foundry_id()
    F32 = foundry_id(FOUNDRY)
    rows: List[dict] = []

    def add(spec, rec, *, N, G, E, regime, seed, exp, arm, attempt, kind, heldout):
        tb = rec.get("trace_best") or []
        # campaign-1 loops keyed their RNG on the branch label: every experiment/arm/attempt was its own run
        rows.append(row(spec, N=N, G=G, E=E, regime=regime, seed=seed, source={"campaign": "cmp1", "experiment": exp, "arm": arm, "attempt": attempt},
                        first_solved_gen=rec.get("first_solved_gen", _first_solved(tb)), best_train_max=max(tb) if tb else 0.0,
                        heldout=heldout, kind=kind, trace_best=tb, foundry=F16, campaign_seed=20260917,
                        rng_label="cmp1/%s/%s/a%s" % (exp, arm, attempt)))

    def rows_of(exp, fname):
        p = c1 / exp / fname
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

    for attempt, fname in ((2, "rows.json"), (1, "rows_attempt1.json")):
        for r in rows_of("SFE-01", fname):
            add(_sfe_spec("W2_K2"), r, N=200, G=60, E=16, regime="E0", seed=r["seed"], exp="SFE-01", arm=r["cell"], attempt=attempt,
                kind="baseline" if r["cell"] == "00" else "treated", heldout=r.get("competence_heldout"))
    for r in rows_of("SFE-03", "rows.json"):
        add(_sfe_spec("W1_d4"), r, N=200, G=60, E=16, regime="E0", seed=r["seed"], exp="SFE-03", arm=r["arm"], attempt=1,
            kind="baseline" if r["arm"] == "fresh" else "treated", heldout=r.get("competence_heldout"))
    for r in rows_of("SFE-07", "rows.json"):
        add(_sfe_spec("W3_K2"), r, N=100, G=40, E=16, regime="E0", seed=r["seed"], exp="SFE-07", arm=r["set"], attempt=2,
            kind="baseline" if r["set"] == "random" else "treated", heldout=r.get("evolved_heldout"))
    for r in rows_of("SFE-09", "rows.json"):
        spec = _sfe_spec("W1_d4" if r["cell"] == "stuck" else "W1_d1")
        add(spec, r, N=200, G=60, E=16, regime="E0", seed=r["seed"], exp="SFE-09", arm=r["arm"], attempt=1,
            kind="baseline" if r["arm"] == "A_words" else "treated", heldout=r.get("competence_heldout"))
    for r in rows_of("SFE-10", "rows.json"):
        kind = "baseline" if (r["arm"] == "mono" or r["arm"].endswith("_noex")) else "treated"
        add(_sfe_spec("W2_K2"), r, N=200, G=int(r["consumer_G"]), E=16, regime="E0", seed=r["seed"], exp="SFE-10", arm=r["arm"], attempt=2,
            kind=kind, heldout=r.get("competence_heldout"))
    for camp in ("wse-survey-v01", "ssf-c1", "ssf-c2", "ssf-c3"):
        d = repo / "archaeon" / "wse" / "ledgers" / camp / "rows"
        if not d.exists():
            continue
        fid = F32 if camp == "wse-survey-v01" else F16
        for p in sorted(d.glob("*.json")):
            r = json.loads(p.read_text(encoding="utf-8"))
            try:
                spec = spec_of(r["world"]["knobs"])
            except TypeError:
                continue
            tb = [t["best_reward"] for t in r["trace"]]
            ex = r["experiment"]
            branch = r.get("organism", {}).get("branch", "B1_naive")
            kind = "baseline" if branch == "B1_naive" else "treated"
            rows.append(row(spec, N=ex["N"], G=ex["G"], E=ex["E"], regime=r["economics"]["name"], seed=r["world"]["seed"],
                            source={"campaign": camp, "experiment": camp, "arm": branch, "attempt": 1},
                            first_solved_gen=_first_solved(tb), best_train_max=max(tb) if tb else 0.0,
                            heldout=r["result"].get("reward_heldout"), kind=kind, trace_best=tb, foundry=fid,
                            campaign_seed=r["world"].get("campaign_seed"), rng_label=branch))
    n = record(rows, path)
    return {"candidate_rows": len(rows), "appended": n, "table": str(path)}


def migrate_runs(path: Path = TABLE, campaign2_seed: int = 20260918) -> dict:
    """Rows written before run identity existed get campaign_seed + rng_label from their source
    (cmp2 rows: the campaign-2 seed and the CRN label; cmp1/survey/ssf: as import_campaign1)."""
    rows = load(path)
    n = 0
    for r in rows:
        if r.get("campaign_seed") is not None:
            continue
        s = r.get("source", {})
        if s.get("campaign") == "cmp2":
            r["campaign_seed"], r["rng_label"] = campaign2_seed, "crn"
        elif s.get("campaign") == "cmp1":
            r["campaign_seed"], r["rng_label"] = 20260917, "cmp1/%s/%s/a%s" % (s.get("experiment"), s.get("arm"), s.get("attempt"))
        elif s.get("campaign") == "wse-survey-v01":
            r["campaign_seed"], r["rng_label"] = 20260916, s.get("arm")
        else:
            r["campaign_seed"], r["rng_label"] = 20260919, s.get("arm")
        n += 1
    Path(path).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8", newline="\n")
    return {"rows": len(rows), "migrated": n}


def migrate_foundry(path: Path = TABLE) -> dict:
    """L2-016: rows written before the foundry key get it from their source campaign."""
    from .evolve import FOUNDRY
    F16 = default_foundry_id(); F32 = foundry_id(FOUNDRY)
    rows = load(path)
    n = 0
    for r in rows:
        if not r.get("foundry"):
            r["foundry"] = F32 if r.get("source", {}).get("campaign") == "wse-survey-v01" else F16
            n += 1
    Path(path).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8", newline="\n")
    return {"rows": len(rows), "migrated": n, "F16": F16, "F32": F32}
