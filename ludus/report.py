"""Cycle 001 reporting — read the ledger, print the verdict table, rescore R1 two ways.

Nothing here calls a model. Every row already carries its own ground truth
(`ceiling1._one` stores `truth` and `position`), so rescoring is exact and needs
no rebuild of the item set.

R1 is reported under TWO normalisations, deliberately, and never merged:

  strict   punctuation-preserving; a hyphen dropped from "P-Q" scores wrong
  loose    punctuation-insensitive; only the field content has to match

Reporting both keeps format compliance and transition correctness separable. A
single normalisation chosen after seeing the answers would be exactly the
post-hoc fitting the charter forbids in §33.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ludus" / "ledgers"


def n_strict(x: str) -> str:
    return re.sub(r"[^A-Z0-9=>-]", "", (x or "").upper())


def n_loose(x: str) -> str:
    return re.sub(r"[^A-Z0-9=>]", "", (x or "").upper())



def greedy_over_all_items(cell: str):
    """Rebuild a cell's item set and score the one-ply heuristic over ALL of it."""
    world_name, rung = cell.split(":")
    if rung != "R2":
        return None
    import random, zlib
    from ludus.worlds import WORLDS
    from ludus.ceiling1 import build_items, SEED
    w = WORLDS[world_name]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    rng = random.Random(SEED + zlib.crc32(f"{world_name}:{rung}".encode()))
    items = build_items(w, rung, n, rng)
    hits = sum(1 for it in items if it["greedy"] in it["truth"])
    return hits / len(items)


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar on the discordant pairs only.

    Comparing a Wilson interval against the greedy POINT estimate is the wrong
    test: greedy's rate is itself estimated on the same 20 items. Only the pairs
    where model and heuristic disagree carry information.
    """
    from math import comb
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson interval — the normal interval degenerates to [p, p] at p = 0 or 1,
    and several cells here sit at exactly 1.000."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


def main() -> None:
    tag = sys.argv[1] if len(sys.argv) > 1 else "screening"
    js = LEDGER / f"cycle001_ceiling_{tag}.json"
    jl = LEDGER / f"cycle001_ceiling_{tag}.jsonl"
    rows = [json.loads(l) for l in jl.read_text(encoding="utf-8").splitlines() if l.strip()]
    summary = json.loads(js.read_text(encoding="utf-8")) if js.exists() else None

    if summary:
        print(f"solver_pin: {summary['solver_pin']}   max_tokens: {summary['max_tokens']}")
        print(f"resolution: {summary['resolution']}\n")

    cells: dict[str, list] = {}
    for r in rows:
        cells.setdefault(f"{r['world']}:{r['rung']}", []).append(r)

    print(f"{'cell':14s} {'n_ok':>4s} {'acc':>6s} {'wilson95':>16s} "
          f"{'rand':>6s} {'greedy':>7s} {'maj':>6s} {'pfail':>6s} {'trunc':>6s} {'tfail':>6s}")
    print("-" * 96)
    verdicts = {}
    for cell, rs in cells.items():
        live = [r for r in rs if r.get("transport_status") == "ok"]
        n = len(live)
        if n == 0:
            print(f"{cell:14s} {'0':>4s}   NO DATA")
            continue
        k = sum(1 for r in live if r.get("correct"))
        lo, hi = wilson(k, n)
        rand = sum(r.get("chance_random", 0.0) for r in live) / n
        # The greedy baseline is recomputed over EVERY item in the cell, not over
        # the rows where the model happened to parse. `score_row` only stamps
        # greedy_correct when the model produced an answer, so reading it off the
        # rows conditions the BASELINE on a post-treatment variable -- the
        # baseline would be measured on an easier subset exactly when the model
        # struggled. Items are reproducible (crc32 seeds), so they are rebuilt.
        greedy = greedy_over_all_items(cell)
        truths = [json.dumps(r.get("truth")) for r in live]
        maj = max(truths.count(t) for t in set(truths)) / n
        pf = sum(1 for r in live if r.get("parse_failure")) / n
        tr = sum(1 for r in live if r.get("truncated")) / n
        tf = 1 - n / len(rs)
        readable = "" if tr <= 0.10 else "  <-- NOT READABLE (truncation)"
        if greedy is not None:
            gc = [(bool(r.get("correct")), r.get("greedy_correct"))
                  for r in live if "greedy_correct" in r]
            b = sum(1 for m, g in gc if m and not g)
            c = sum(1 for m, g in gc if g and not m)
            readable += (f"  | vs greedy: discordant {b}/{c}, "
                         f"McNemar p={mcnemar_exact(b, c):.3f}")
        print(f"{cell:14s} {n:4d} {k/n:6.3f} [{lo:.3f},{hi:.3f}] "
              f"{rand:6.3f} {('%.3f' % greedy) if greedy is not None else '    - ':>7s} "
              f"{maj:6.3f} {pf:6.2f} {tr:6.2f} {tf:6.2f}{readable}")
        verdicts[cell] = {"n_transport_ok": n, "correct": k, "accuracy": round(k / n, 4),
                          "wilson95": [lo, hi], "baseline_random": round(rand, 4),
                          "baseline_greedy_1ply": None if greedy is None else round(greedy, 4),
                          "baseline_majority": round(maj, 4),
                          "parse_failure_rate": round(pf, 4),
                          "truncation_rate": round(tr, 4),
                          "transport_failure_rate": round(tf, 4)}

    print("\nR1 rescored under both normalisations (format compliance vs transition correctness):")
    for cell, rs in cells.items():
        if not cell.endswith("R1"):
            continue
        live = [r for r in rs if r.get("transport_status") == "ok" and r.get("truth")]
        if not live:
            continue
        s = sum(1 for r in live if n_strict(r.get("raw_answer") or "") == n_strict(r["truth"][0]))
        lo = sum(1 for r in live if n_loose(r.get("raw_answer") or "") == n_loose(r["truth"][0]))
        # How often did the model simply echo the position it was given, without
        # applying the action? That is a distinct failure from getting it wrong.
        echo = sum(1 for r in live
                   if n_loose(r.get("raw_answer") or "") == n_loose(r.get("position", "")))
        print(f"  {cell:14s} n={len(live):3d} strict={s/len(live):.3f} "
              f"loose={lo/len(live):.3f} echoed_input={echo/len(live):.3f}")
        verdicts.setdefault(cell, {}).update(
            r1_strict=round(s / len(live), 4), r1_loose=round(lo / len(live), 4),
            r1_echoed_input=round(echo / len(live), 4))

    out = LEDGER / f"cycle001_report_{tag}.json"
    out.write_text(json.dumps(verdicts, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
