"""Persistent REACHABILITY TABLE (campaigns 2-3; L-017, L-028, L2-016, L2-025, L2-026).

One row per run (append-only JSONL), keyed by cell, value_bits, N, G, E, regime and the
generation-0 FOUNDRY (the sampling distribution of generation 0 is part of the regime).
Rows carry run identity (campaign_seed, rng_label, seed): under common random numbers two
experiments that search the same cell at the same budget with the same seeds produce the
same run, and pooled() counts it once.

THREE LEVELS OF REACH (campaign 3, D3-002): every row records the best training reward and
  FLOOR   best <  SHELF_MIN (0.45)
  SHELF   SHELF_MIN <= best < SUMMIT_MIN (0.90)   (one stream of a K=2 cell; half credit)
  SUMMIT  best >= SUMMIT_MIN                     (the preregistered full-solve criterion)
with first_foothold_gen (>= 0.5, the campaign-1/2 criterion), first_shelf_gen and
first_summit_gen; a row whose run ended without a summit is censored at G for the summit.

RIGHT-CENSORING (campaign 3, D3-003): a run stopped k generations after its first solve
(stopped_on_solve=true) is a BASELINE row with G = generations run. lookup(G) pools every
row that informs budget G monotonically: rows run for >= G generations (reached iff the
event happened before G) and stopped rows whose event happened before G.

Classes (foothold criterion, unchanged from campaign 2): COMMON (Wilson lower >= 0.5),
REACHABLE (freq >= 0.25), RARE (reached, freq < 0.25), OBSERVED_UNREACHABLE_AT_BUDGET
(>= 3 runs, none), UNESTABLISHED. The same classes are computed for the SUMMIT event
(class_summit). A shelf histogram (best training reward, bins of 0.1) is pooled per key.
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
FOOTHOLD_MIN = 0.5
SHELF_MIN = 0.45
SUMMIT_MIN = 0.90
LEVELS = ("FLOOR", "SHELF", "SUMMIT")


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


def level_of(best: Optional[float], heldout: Optional[float] = None) -> str:
    """SUMMIT needs the HELD-OUT competence (>= SUMMIT_MIN) when one is known: a single
    generation's training best of 0.9375 with held-out 0.53 (C2-SFE-03 seed 9) is a lucky
    battery, not a full solution (D3-006). A training-only summit is a CANDIDATE (see
    summit_candidate_gen) and levels as SHELF until confirmed."""
    if best is None:
        return "FLOOR"
    if best >= SUMMIT_MIN and (heldout is None or heldout >= SUMMIT_MIN):
        return "SUMMIT" if heldout is not None else "SHELF"
    if best >= SHELF_MIN:
        return "SHELF"
    return "FLOOR"


def first_at(trace_best: Optional[Sequence[float]], thr: float) -> Optional[int]:
    if not trace_best:
        return None
    for i, v in enumerate(trace_best):
        if v >= thr:
            return i
    return None


def spec_of(knobs: dict) -> WorldSpec:
    kw = {k: (tuple(v) if isinstance(v, list) else v) for k, v in knobs.items()}
    return WorldSpec(**kw)


def row(spec: WorldSpec, *, N: int, G: int, E: int, regime: str, seed: int, source: dict,
        first_solved_gen: Optional[int], best_train_max: float, heldout: Optional[float] = None,
        kind: str = "baseline", solve_threshold: float = 0.5, trace_best: Optional[Sequence[float]] = None,
        foundry: Optional[str] = None, campaign_seed: Optional[int] = None, rng_label: Optional[str] = None,
        stopped_on_solve: bool = False, heldout_per_ask: Optional[Sequence[float]] = None) -> dict:
    tb = None if trace_best is None else [round(float(x), 4) for x in trace_best]
    return {
        "cell": spec.name, "world_id": spec.world_id(), "knobs": spec.knobs(), "value_bits": spec.value_bits,
        "N": N, "G": G, "E": E, "regime": regime, "foundry": foundry or default_foundry_id(), "seed": seed, "kind": kind, "source": source,
        "campaign_seed": campaign_seed, "rng_label": rng_label, "stopped_on_solve": bool(stopped_on_solve),
        "solve_threshold": solve_threshold, "first_solved_gen": first_solved_gen,
        "reached": first_solved_gen is not None, "best_train_max": round(float(best_train_max), 6),
        "level": level_of(best_train_max, heldout), "first_foothold_gen": first_solved_gen if first_solved_gen is not None else first_at(tb, FOOTHOLD_MIN),
        "first_shelf_gen": first_at(tb, SHELF_MIN),
        "summit_candidate_gen": first_at(tb, SUMMIT_MIN),                       # training best >= SUMMIT_MIN (one battery)
        "first_summit_gen": (first_at(tb, SUMMIT_MIN) if (heldout is not None and heldout >= SUMMIT_MIN) else None),   # confirmed held-out
        "summit_censored": not (heldout is not None and heldout >= SUMMIT_MIN and first_at(tb, SUMMIT_MIN) is not None),
        "heldout": None if heldout is None else round(float(heldout), 6),
        "heldout_per_ask": None if heldout_per_ask is None else [round(float(x), 4) for x in heldout_per_ask],
        "eval_resolution": round(1.0 / max(1, E), 6),
        "trace_best": tb,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def row_from_result(spec: WorldSpec, res: dict, *, N: int, G: int, E: int, regime: str, seed: int,
                    source: dict, heldout: Optional[float] = None, kind: Optional[str] = None,
                    foundry: Optional[dict] = None, campaign_seed: Optional[int] = None,
                    stopped_on_solve: bool = False, heldout_per_ask: Optional[Sequence[float]] = None) -> dict:
    """A table row straight from run_cell()/Evolution.result(): kind is baseline iff the loop
    reports a verified common generation 0 with nothing substituted (pass kind='treated' for a
    non-standard operator set or schedule); a stopped-on-solve run stays baseline (censored)."""
    prov = res.get("gen0_provenance") or {}
    if kind is None:
        kind = "baseline" if prov.get("verified_common") and prov.get("n_substituted", 0) == 0 else "treated"
    tb = [t["best_reward"] for t in res["trace"]]
    return row(spec, N=N, G=G, E=E, regime=regime, seed=seed, source=source, first_solved_gen=res.get("first_solved_gen"),
               best_train_max=max(tb) if tb else 0.0, heldout=heldout, kind=kind,
               solve_threshold=res.get("solve_threshold", 0.5), trace_best=tb, foundry=foundry_id(foundry) if foundry else None,
               campaign_seed=prov.get("campaign_seed", campaign_seed), rng_label=res.get("rng_label"),
               stopped_on_solve=stopped_on_solve, heldout_per_ask=heldout_per_ask)


def _identity(r: dict) -> tuple:
    s = r.get("source", {})
    return (r["cell"], r["value_bits"], r["N"], r["G"], r["E"], r["regime"], r.get("foundry"), r["seed"], r["kind"],
            s.get("campaign"), s.get("experiment"), s.get("arm"), s.get("attempt"))


def run_identity(r: dict) -> tuple:
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


def _event_gen(r: dict, event: str) -> Optional[int]:
    return {"foothold": r.get("first_foothold_gen", r.get("first_solved_gen")), "shelf": r.get("first_shelf_gen"),
            "summit": r.get("first_summit_gen")}[event]


def _summary(key_vals: dict, rows: List[dict], G: Optional[int] = None) -> dict:
    """Pool rows (already deduped and selected) at budget G (None = each row's own G)."""
    s = dict(key_vals)
    s.update({"n": 0, "k": 0, "k_shelf": 0, "k_summit": 0, "first_solved_gens": [], "first_shelf_gens": [], "first_summit_gens": [],
              "best_train_max": 0.0, "heldout_max": None, "levels": {"FLOOR": 0, "SHELF": 0, "SUMMIT": 0}, "shelf_hist": {},
              "sources": set(), "seeds": [], "eval_resolution": rows[0].get("eval_resolution") if rows else None})
    for r in rows:
        g_budget = G if G is not None else r["G"]
        s["n"] += 1; s["seeds"].append(r.get("seed"))
        fg = _event_gen(r, "foothold"); sg = _event_gen(r, "shelf"); mg = _event_gen(r, "summit")
        if fg is not None and fg < g_budget:
            s["k"] += 1; s["first_solved_gens"].append(fg)
        if sg is not None and sg < g_budget:
            s["k_shelf"] += 1; s["first_shelf_gens"].append(sg)
        if mg is not None and mg < g_budget:
            s["k_summit"] += 1; s["first_summit_gens"].append(mg)
        best = r.get("best_train_max") or 0.0
        if G is not None and r.get("trace_best") and r["G"] > G:
            best = max(r["trace_best"][:G]) if r["trace_best"][:G] else 0.0
        s["best_train_max"] = max(s["best_train_max"], best)
        lv = level_of(best, r.get("heldout")) if (G is None or r["G"] <= G) else level_of(best, None)
        if lv == "SUMMIT" and mg is not None and not (mg < g_budget):
            lv = "SHELF"
        s["levels"][lv] += 1
        cg = r.get("summit_candidate_gen")
        if cg is not None and cg < g_budget:
            s["k_summit_candidate"] = s.get("k_summit_candidate", 0) + 1
        b = "%.1f" % (math.floor(best * 10 + 1e-9) / 10); s["shelf_hist"][b] = s["shelf_hist"].get(b, 0) + 1
        if r.get("heldout") is not None:
            s["heldout_max"] = max(s["heldout_max"] or 0.0, r["heldout"])
        src = r.get("source", {}); s["sources"].add("%s/%s/%s" % (src.get("campaign"), src.get("experiment"), src.get("arm")))
    s["freq"] = round(s["k"] / s["n"], 4) if s["n"] else None
    s["band95"] = wilson(s["k"], s["n"]); s["class"] = classify(s["n"], s["k"])
    s["freq_shelf"] = round(s["k_shelf"] / s["n"], 4) if s["n"] else None
    s["freq_summit"] = round(s["k_summit"] / s["n"], 4) if s["n"] else None
    # confirmed summits (held-out >= SUMMIT_MIN) plus training-only candidates from rows WITHOUT a
    # held-out (stop-rule rows recorded before campaign 3): the class is computed over both and
    # the two counts are reported apart so a reader sees what is confirmed
    s["k_summit_candidate"] = s.get("k_summit_candidate", 0)
    s["k_summit_any"] = s["k_summit"] + sum(1 for r in rows if r.get("heldout") is None and r.get("summit_candidate_gen") is not None
                                            and r["summit_candidate_gen"] < (G if G is not None else r["G"]))
    s["band95_summit"] = wilson(s["k_summit_any"], s["n"]); s["class_summit"] = classify(s["n"], s["k_summit_any"])
    for kk in ("first_solved_gens", "first_shelf_gens", "first_summit_gens"):
        s[kk] = sorted(x for x in s[kk] if x is not None)
    s["median_first_solved_gen"] = s["first_solved_gens"][len(s["first_solved_gens"]) // 2] if s["first_solved_gens"] else None
    s["sources"] = sorted(s["sources"])
    s["shelf_hist"] = dict(sorted(s["shelf_hist"].items()))
    return s


def pooled(rows: Iterable[dict], kinds: Sequence[str] = ("baseline",), key: Sequence[str] = KEY) -> Dict[tuple, dict]:
    groups: Dict[tuple, List[dict]] = {}
    for r in dedupe_runs(rows):
        if r.get("kind") not in kinds:
            continue
        groups.setdefault(tuple(r.get(x) for x in key), []).append(r)
    return {k: _summary({kk: rs[0].get(kk) for kk in key}, rs) for k, rs in groups.items()}


def lookup(cell: str, *, value_bits: int, N: Optional[int] = None, G: Optional[int] = None, E: Optional[int] = None,
           regime: str = "E0", foundry: Optional[str] = "default", G_min: Optional[int] = None, G_max: Optional[int] = None,
           rows: Optional[List[dict]] = None, path: Path = TABLE, monotone: bool = True) -> dict:
    """The pooled estimate for a cell at a budget under one generation-0 foundry ('default' =
    the campaign foundry; None = pool across foundries). With G given and monotone=True (D3-003)
    every row that INFORMS budget G is pooled: rows run for >= G generations (event iff before
    G) and stopped-on-solve rows whose event happened before G. Never refuses."""
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
        if monotone:
            sel = [r for r in sel if r["G"] >= G or (r.get("stopped_on_solve") and r.get("reached") and (r.get("first_solved_gen") or 0) < G)]
        else:
            sel = [r for r in sel if r["G"] == G]
    if G_min is not None:
        sel = [r for r in sel if r["G"] >= G_min]
    if G_max is not None:
        sel = [r for r in sel if r["G"] <= G_max]
    sel = dedupe_runs(sel)
    if not sel:
        return {"cell": cell, "value_bits": value_bits, "regime": regime, "foundry": fid, "n": 0, "k": 0, "k_shelf": 0, "k_summit": 0, "freq": None,
                "freq_shelf": None, "freq_summit": None, "band95": (0.0, 1.0), "band95_summit": (0.0, 1.0), "class": "UNESTABLISHED",
                "class_summit": "UNESTABLISHED", "budgets": [], "first_solved_gens": [], "first_shelf_gens": [], "first_summit_gens": [],
                "median_first_solved_gen": None, "best_train_max": None, "heldout_max": None, "levels": {"FLOOR": 0, "SHELF": 0, "SUMMIT": 0}, "shelf_hist": {}}
    s = _summary({"cell": cell, "value_bits": value_bits, "regime": regime}, sel, G=G)
    s["foundry"] = fid; s["G_pooled"] = G
    s["budgets"] = sorted({(r["N"], r["G"], r["E"]) for r in sel})
    s["foundries_pooled"] = sorted({r.get("foundry") for r in sel})
    s["n_censored_runs"] = sum(1 for r in sel if r.get("stopped_on_solve"))
    return s


def candidates(lo: float, hi: float, *, value_bits: Optional[int] = None, regime: str = "E0", foundry: Optional[str] = "default",
               min_n: int = 3, rows: Optional[List[dict]] = None, path: Path = TABLE, key: Sequence[str] = KEY) -> List[dict]:
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
    lines = ["%-14s %4s %5s %5s %3s %-5s %-11s %3s %3s %-6s %-13s %-30s %-9s %s" % (
        "cell", "bits", "N", "G", "E", "reg", "foundry", "n", "k", "freq", "band95", "class", "F/S/Su", "first_solved")]
    for s in sorted(summaries, key=lambda s: (s["cell"], s["value_bits"], s.get("N") or 0, s.get("G") or 0, s.get("E") or 0, s["regime"], str(s.get("foundry")))):
        lv = s.get("levels", {})
        lines.append("%-14s %4d %5d %5d %3d %-5s %-11s %3d %3d %-6s %-13s %-30s %-9s %s" % (
            s["cell"], s["value_bits"], s.get("N") or 0, s.get("G") or 0, s.get("E") or 0, s["regime"], str(s.get("foundry"))[:11], s["n"], s["k"],
            "-" if s["freq"] is None else "%.2f" % s["freq"], "%.2f-%.2f" % tuple(s["band95"]), s["class"],
            "%d/%d/%d" % (lv.get("FLOOR", 0), lv.get("SHELF", 0), lv.get("SUMMIT", 0)),
            ",".join(str(x) for x in s["first_solved_gens"]) or "-"))
    return "\n".join(lines)


# ------------------------------------------------------------------ campaign-1 import (unchanged from campaign 2)
def _sfe_spec(name: str) -> WorldSpec:
    table = {
        "W0": WorldSpec("W0", value_bits=4), "W1_d1": WorldSpec("W1_d1", delay=1, value_bits=4),
        "W1_d4": WorldSpec("W1_d4", delay=4, value_bits=4), "W2_K2": WorldSpec("W2_K2", K=2, value_bits=4),
        "W3_K2": WorldSpec("W3_K2", K=2, ask_mode="one", value_bits=4),
    }
    return table[name]


def _first_solved(trace_best: Sequence[float], thr: float = 0.5) -> Optional[int]:
    return first_at(trace_best, thr)


def import_campaign1(repo: Path = REPO, path: Path = TABLE) -> dict:
    from .evolve import FOUNDRY
    c1 = repo / "archaeon" / "campaign1"
    F16 = default_foundry_id(); F32 = foundry_id(FOUNDRY)
    rows: List[dict] = []

    def add(spec, rec, *, N, G, E, regime, seed, exp, arm, attempt, kind, heldout):
        tb = rec.get("trace_best") or []
        rows.append(row(spec, N=N, G=G, E=E, regime=regime, seed=seed, source={"campaign": "cmp1", "experiment": exp, "arm": arm, "attempt": attempt},
                        first_solved_gen=rec.get("first_solved_gen", _first_solved(tb)), best_train_max=max(tb) if tb else 0.0,
                        heldout=heldout, kind=kind, trace_best=tb, foundry=F16, campaign_seed=20260917, rng_label="cmp1/%s/%s/a%s" % (exp, arm, attempt)))

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


# ------------------------------------------------------------------ migrations
def migrate_foundry(path: Path = TABLE) -> dict:
    from .evolve import FOUNDRY
    F16 = default_foundry_id(); F32 = foundry_id(FOUNDRY)
    rows = load(path); n = 0
    for r in rows:
        if not r.get("foundry"):
            r["foundry"] = F32 if r.get("source", {}).get("campaign") == "wse-survey-v01" else F16; n += 1
    Path(path).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8", newline="\n")
    return {"rows": len(rows), "migrated": n}


def migrate_runs(path: Path = TABLE, campaign2_seed: int = 20260918) -> dict:
    rows = load(path); n = 0
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


STOP_RULE_ARMS = {"source-mature", "source-solved", "producer", "stream"}     # campaign-2 arms run with a stop-on-solve rule


def migrate_levels(path: Path = TABLE) -> dict:
    """Campaign 3 (D3-002, D3-003): levels, first_shelf/first_summit, censoring flag on every
    row; campaign-2 stop-rule rows become baseline + stopped_on_solve."""
    rows = load(path); n = 0; recl = 0
    for r in rows:
        tb = r.get("trace_best")
        best = r.get("best_train_max") or 0.0
        ho = r.get("heldout")
        r["level"] = level_of(best, ho)
        r["first_foothold_gen"] = r.get("first_solved_gen") if r.get("first_solved_gen") is not None else first_at(tb, FOOTHOLD_MIN)
        r["first_shelf_gen"] = first_at(tb, SHELF_MIN)
        r["summit_candidate_gen"] = first_at(tb, SUMMIT_MIN)
        r["first_summit_gen"] = r["summit_candidate_gen"] if (ho is not None and ho >= SUMMIT_MIN) else None
        r["summit_censored"] = r["first_summit_gen"] is None
        r.setdefault("stopped_on_solve", False)
        src = r.get("source", {})
        if src.get("campaign") == "cmp2" and src.get("arm") in STOP_RULE_ARMS and r.get("kind") == "treated":
            r["kind"] = "baseline"; r["stopped_on_solve"] = True; recl += 1
        n += 1
    Path(path).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8", newline="\n")
    return {"rows": n, "reclassified_stop_rule_rows": recl}
