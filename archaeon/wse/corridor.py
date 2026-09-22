"""CORRIDOR TABLE (campaign 3, Phase A group C; campaign-2 L2-032, L2-035).

An INSTRUMENT beside the reachability table: for a (source cell -> target cell) pair, what
capability does a MATURE solution of the source already contain on the target (direct
reuse), and what does a search on the target reach when initialized with that material at
a declared dose (initialization reach: level and transition generations)? Mature sources
only (the source population's maturity block says solved=true, or the row says why not).
No row is a transfer claim; the table shows traversable task geometry.

Row fields:
  source_cell, source_foundry, source_budget, source_competence, source_maturity (block)
  target_cell, target_foundry, target_budget (N/G/E), regime
  direct_reuse: {"best": held-out best of the source organisms on the target, "n_sources"}
  init: {"dose": k, "N": N, "level": FLOOR|SHELF|SUMMIT, "first_shelf_gen", "first_summit_gen",
         "first_foothold_gen", "seed", "baseline_level"?}  (absent for direct-only probes)
  kind: "direct" | "init" | "ladder" (a route of pressures, source = the rung sequence)
  source: {campaign, experiment, arm, attempt}
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

REPO = Path(__file__).resolve().parents[2]
TABLE = REPO / "archaeon" / "campaign3" / "CORRIDOR.jsonl"


def row(*, source_cell: str, target_cell: str, kind: str, source: dict, source_maturity: Optional[dict] = None,
        source_competence: Optional[float] = None, source_foundry: Optional[str] = None, target_foundry: Optional[str] = None,
        source_budget: Optional[dict] = None, target_budget: Optional[dict] = None, regime: str = "E0",
        direct_reuse: Optional[dict] = None, init: Optional[dict] = None, note: str = "") -> dict:
    return {"source_cell": source_cell, "target_cell": target_cell, "kind": kind, "source": source,
            "source_maturity": source_maturity, "source_competence": source_competence, "source_foundry": source_foundry,
            "target_foundry": target_foundry, "source_budget": source_budget, "target_budget": target_budget, "regime": regime,
            "direct_reuse": direct_reuse, "init": init, "note": note,
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def _identity(r: dict) -> tuple:
    s = r.get("source", {})
    i = r.get("init") or {}
    return (r["source_cell"], r["target_cell"], r["kind"], s.get("campaign"), s.get("experiment"), s.get("arm"), s.get("attempt"),
            i.get("seed"), i.get("dose"))


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
            f.write(json.dumps(r, sort_keys=True) + "\n"); have.add(_identity(r)); n += 1
    return n


def edges(rows: Optional[List[dict]] = None, path: Path = TABLE) -> Dict[tuple, dict]:
    """Pooled view per (source_cell, target_cell): best direct reuse, init outcomes by level."""
    rs = rows if rows is not None else load(path)
    out: Dict[tuple, dict] = {}
    for r in rs:
        k = (r["source_cell"], r["target_cell"])
        e = out.setdefault(k, {"source_cell": k[0], "target_cell": k[1], "direct_best": None, "direct_n": 0,
                               "init_n": 0, "init_levels": {"FLOOR": 0, "SHELF": 0, "SUMMIT": 0}, "first_shelf_gens": [], "first_summit_gens": [],
                               "ladder_n": 0, "sources": set()})
        e["sources"].add("%s/%s" % (r["source"].get("campaign"), r["source"].get("experiment")))
        d = r.get("direct_reuse") or {}
        if d.get("best") is not None:
            e["direct_n"] += 1
            e["direct_best"] = max(e["direct_best"] or 0.0, d["best"])
        i = r.get("init") or {}
        if r["kind"] == "init" and i:
            e["init_n"] += 1
            e["init_levels"][i.get("level", "FLOOR")] = e["init_levels"].get(i.get("level", "FLOOR"), 0) + 1
            if i.get("first_shelf_gen") is not None:
                e["first_shelf_gens"].append(i["first_shelf_gen"])
            if i.get("first_summit_gen") is not None:
                e["first_summit_gens"].append(i["first_summit_gen"])
        if r["kind"] == "ladder":
            e["ladder_n"] += 1
            if i and i.get("level"):
                e["init_levels"][i["level"]] = e["init_levels"].get(i["level"], 0) + 1
    for e in out.values():
        e["sources"] = sorted(e["sources"]); e["first_shelf_gens"].sort(); e["first_summit_gens"].sort()
    return out


def table_text(rows: Optional[List[dict]] = None, path: Path = TABLE) -> str:
    es = edges(rows, path)
    lines = ["%-12s -> %-12s %7s %4s | init n=%-3s FLOOR/SHELF/SUMMIT %-12s shelf@%s summit@%s" % ("source", "target", "direct", "n", "", "", "", "")]
    for k in sorted(es):
        e = es[k]
        lv = e["init_levels"]
        lines.append("%-12s -> %-12s %7s %4d | init n=%-3d %-18s shelf@%s summit@%s %s" % (
            e["source_cell"], e["target_cell"], "-" if e["direct_best"] is None else "%.2f" % e["direct_best"], e["direct_n"],
            e["init_n"] + e["ladder_n"], "%d/%d/%d" % (lv.get("FLOOR", 0), lv.get("SHELF", 0), lv.get("SUMMIT", 0)),
            ",".join(str(x) for x in e["first_shelf_gens"][:6]) or "-", ",".join(str(x) for x in e["first_summit_gens"][:6]) or "-",
            "(ladder)" if e["ladder_n"] else ""))
    return "\n".join(lines)
