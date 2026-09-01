"""LUDUS cycle 001 — CEILING-1. Where does the available solver fall off the ladder?

The charter's central quantity is C(G, theta): the cost of reaching competence
threshold theta in world G. Before any transfer claim can be read off that
quantity, theta has to be *attainable at all* by an agent this program can
actually run. This module measures that, and nothing else.

Four rungs, each with exact ground truth from `ludus.worlds.solve`:

  R0  LEGALITY     emit any legal action from the given state
  R1  TRANSITION   emit the exact state resulting from a named action
  R2  OPTIMAL      emit an action attaining the game value under optimal play
  R3  VALUE        emit the game value (final margin under optimal play)

Scoring is mechanical at every rung. No judge model is involved anywhere.

Three baselines accompany every cell, computed on THE SAME ITEMS, not on a
separate sample:

  random_legal   a state-blind draw from the world's action vocabulary (R0),
                 or a uniform draw from the legal set (R2)
  greedy_1ply    the one-ply own-score maximiser from `ludus.baselines`
  majority       the modal correct answer over the item set

`feedback_counter_baseline_discriminator`: a model reading above `random_legal`
but at or below `greedy_1ply` has demonstrated nothing that a four-line
heuristic does not already do.

Diagnostics logged per row and reported per cell, because each has previously
cost this program a result:
  parse_failure   the response carried no ANSWER line
  truncated       completion_tokens == max_tokens (`feedback_truncation_can_
                  flatter_a_gate` — truncation drags scores toward the floor
                  and the direction must be stated beside the number)
  illegal         at R2/R1 the answer named an action that is not legal here
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import statistics
import sys
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from ergon.probe import solver
from ludus.baselines import MIN_BRANCHING, greedy_action, world_vocabulary
from ludus.worlds import WORLDS, optimal_actions, reachable_states, solve

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ludus" / "ledgers"

SEED = 20260826
#: 4096, not 1024. The pinned solver is a reasoning model that spent 46 completion
#: tokens answering "reply with ANSWER: OK". A cap tight enough to truncate would
#: truncate MORE on the harder rungs, which is arm-correlated missing data pushing
#: scores toward the floor — `feedback_truncation_can_flatter_a_gate`.
MAX_TOKENS = 8192
#: Repinned 2026-08-26: nvidia:nemotron-super-49b-v1 and -v1.5 both now return
#: HTTP 410 Gone. A solver change is a solver-set change and is recorded, not
#: silently swapped.
SOLVER = "nvidia:gpt-oss-120b"

RUNGS = ("R0", "R1", "R2", "R3")

INSTRUCTION = {
    "R0": ("Name one action that is legal for the player to move in the "
           "position above.\n\nReason briefly if you wish. Your final line "
           "must be exactly:\nANSWER: <action>"),
    "R1": ("The player to move plays the action named below. Give the position "
           "that results.\n\nReason briefly if you wish. Your final line must "
           "be exactly:\nANSWER: <resulting position in the same field format, "
           "one line, fields separated by semicolons>"),
    "R2": ("Both players play perfectly for the rest of the game. Name an "
           "action for the player to move that is optimal under that "
           "assumption.\n\nReason as long as you need. Your final line must be "
           "exactly:\nANSWER: <action>"),
    "R3": ("Both players play perfectly for the rest of the game from the "
           "position above. Give the MARGIN at the end of the game.\n\nReason "
           "as long as you need. Your final line must be exactly:\n"
           "ANSWER: <integer>"),
}


def build_items(world, rung: str, n: int, rng: random.Random) -> list[dict]:
    states = [s for s in reachable_states(world)
              if len(world.legal_actions(s)) >= MIN_BRANCHING]
    pool = states if len(states) <= n else rng.sample(states, n)
    items = []
    for k, s in enumerate(pool):
        legal = world.legal_actions(s)
        item = {"item_id": f"{world.name}-{rung}-{k:03d}", "world": world.name,
                "rung": rung, "state": world.render_state(s),
                "legal": legal, "branching": len(legal)}
        if rung == "R0":
            item["truth"] = legal
            item["chance_random"] = len(legal) / len(world_vocabulary(world))
        elif rung == "R1":
            a = rng.choice(legal)
            item["given_action"] = a
            item["truth"] = [world.render_state(world.apply(s, a))]
            item["chance_random"] = 0.0
        elif rung == "R2":
            opt = optimal_actions(world, s)
            item["truth"] = opt
            item["chance_random"] = len(opt) / len(legal)
            item["greedy"] = greedy_action(world, s)
        else:
            item["truth"] = [str(solve(world, s))]
            item["chance_random"] = 0.0
            item["greedy"] = None
        items.append(item)
    return items


def render_prompt(world, item: dict) -> str:
    parts = [world.rules_text(), "", "POSITION:", item["state"], ""]
    if item["rung"] == "R1":
        parts += [f"ACTION PLAYED: {item['given_action']}", ""]
    parts.append(INSTRUCTION[item["rung"]])
    return "\n".join(parts)


ANSWER_RE = re.compile(r"ANSWER\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def parse_answer(text: str) -> str | None:
    m = ANSWER_RE.findall(text or "")
    if not m:
        return None
    return m[-1].strip().strip("`*").strip()


def normalise(world, rung: str, ans: str) -> str:
    a = ans.upper().strip().rstrip(".")
    if rung in ("R0", "R2"):
        a = re.sub(r"\s+", " ", a)
        if a.startswith("TAKE"):
            digits = re.findall(r"\d+", a)
            return f"TAKE {digits[0]}" if digits else a
        return a.split()[0] if a.split() else a
    if rung == "R3":
        m = re.search(r"-?\d+", a)
        return m.group(0) if m else a
    return re.sub(r"[^A-Z0-9=>-]", "", a)


def score_row(world, item: dict, text: str, completion_tokens) -> dict:
    ans = parse_answer(text)
    row = {"item_id": item["item_id"], "world": item["world"],
           "rung": item["rung"], "branching": item["branching"],
           "chance_random": round(item["chance_random"], 4),
           "raw_answer": ans, "parse_failure": ans is None,
           "truncated": completion_tokens == MAX_TOKENS}
    if ans is None:
        row.update(correct=False, illegal=None)
        return row
    norm = normalise(world, item["rung"], ans)
    row["normalised"] = norm
    truth = [normalise(world, item["rung"], t) for t in item["truth"]]
    row["correct"] = norm in truth
    if item["rung"] in ("R0", "R2"):
        row["illegal"] = norm not in [normalise(world, item["rung"], x)
                                      for x in item["legal"]]
    else:
        row["illegal"] = None
    if item["rung"] == "R2":
        row["greedy_correct"] = normalise(world, "R2", item["greedy"]) in truth
    return row


def summarise(rows: list[dict], items: list[dict]) -> dict:
    """Accuracy is computed over TRANSPORT-OK rows only.

    A transport failure is missing data, not a wrong answer. The pilot for this
    cycle counted four HTTP 410s as parse failures and reported accuracy 0.000
    with parse_failure_rate 1.00 — a hard ceiling that was entirely the harness.
    Transport failures are therefore their own class, excluded from the
    denominator and reported beside the number, never inside it.
    """
    n_all = len(rows)
    if n_all == 0:
        return {}
    live = [r for r in rows if r.get("transport_status") == "ok"]
    n = len(live)
    if n == 0:
        return {"n_attempted": n_all, "n_transport_ok": 0,
                "transport_failure_rate": 1.0,
                "verdict": "NO DATA — every call failed in transport",
                "transport_errors": sorted({r.get("error_type") for r in rows
                                            if r.get("error_type")})}
    scored = [r for r in live if not r["parse_failure"]]
    correct = sum(1 for r in live if r["correct"])
    p = correct / n
    se = (p * (1 - p) / n) ** 0.5
    out = {
        "n_attempted": n_all,
        "n_transport_ok": n,
        "transport_failure_rate": round(1 - n / n_all, 4),
        "n": n,
        "accuracy": round(p, 4),
        "se": round(se, 4),
        "ci95": [round(max(0.0, p - 1.96 * se), 4),
                 round(min(1.0, p + 1.96 * se), 4)],
        "accuracy_excluding_parse_failures":
            round(sum(1 for r in scored if r["correct"]) / len(scored), 4)
            if scored else None,
        "parse_failure_rate": round(sum(r["parse_failure"] for r in live) / n, 4),
        "truncation_rate": round(sum(bool(r["truncated"]) for r in live) / n, 4),
        "baseline_random": round(
            statistics.mean(i["chance_random"] for i in items), 4),
    }
    illegal = [r["illegal"] for r in live if r["illegal"] is not None]
    if illegal:
        out["illegal_action_rate"] = round(sum(illegal) / len(illegal), 4)
    g = [r["greedy_correct"] for r in live if "greedy_correct" in r]
    if g:
        out["baseline_greedy_1ply_same_items"] = round(sum(g) / len(g), 4)
    truth_first = [i["truth"][0] for i in items]
    mode_ct = max(truth_first.count(t) for t in set(truth_first))
    out["baseline_majority_same_items"] = round(mode_ct / len(items), 4)
    return out


def _one(world, rung, it, solver_id):
    res = solver.call(solver_id, render_prompt(world, it), max_tokens=MAX_TOKENS)
    if res.status != "ok":
        row = {"item_id": it["item_id"], "world": world.name, "rung": rung,
               "branching": it["branching"],
               "chance_random": round(it["chance_random"], 4),
               "transport_status": res.status, "error_type": res.error_type,
               "transport_failure": True,
               "parse_failure": None, "truncated": None,
               "correct": None, "illegal": None}
    else:
        row = score_row(world, it, res.text, res.completion_tokens)
        row["transport_status"] = "ok"
        row["truth"] = it["truth"]
        row["position"] = it["state"]
        row["raw_text_tail"] = (res.text or "")[-600:]
        row["latency_s"] = res.latency_s
        row["completion_tokens"] = res.completion_tokens
    row["solver"] = solver_id
    row["max_tokens"] = MAX_TOKENS
    row["ts_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return row


#: The free lane measures ~40 RPM and the pinned reasoning model runs ~45s per
#: call at this token budget. Six workers keeps well inside the rate limit while
#: making a 12-cell screening run finish in one sitting. Rows are written in
#: item order regardless of completion order, so the ledger stays deterministic.
WORKERS = 3


def run_cell(world, rung: str, n: int, solver_id: str, rng: random.Random,
             fh) -> dict:
    items = build_items(world, rung, n, rng)
    # Rows are written as each call returns, not after the whole cell. Batched
    # writes made a slow cell indistinguishable from a hung one, and a run was
    # killed on that ambiguity.
    done = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(_one, world, rung, it, solver_id): it["item_id"]
                for it in items}
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            done[r["item_id"]] = r
            print(f"    [{i}/{len(items)}] {r['item_id']} "
                  f"correct={r.get('correct')}", flush=True)
    rows = [done[it["item_id"]] for it in items]   # ledger stays in item order
    for row in rows:
        fh.write(json.dumps(row) + chr(10))
        line = (f"  {row['item_id']}  correct={row['correct']} "
                f"ans={str(row.get('normalised', row.get('raw_answer')))[:80]!r}")
        print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    fh.flush()
    return {"summary": summarise(rows, items), "rows": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--pilot", action="store_true",
                    help="n=4 per cell, transport and prompt check only")
    ap.add_argument("--solver", default=SOLVER)
    ap.add_argument("--worlds", default="WEIR,LOOM,TITHE")
    ap.add_argument("--rungs", default="R0,R1,R2,R3")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    n = 4 if args.pilot else args.n
    tag = args.tag or ("pilot" if args.pilot else "screening")

    LEDGER.mkdir(parents=True, exist_ok=True)
    jsonl = LEDGER / f"cycle001_ceiling_{tag}.jsonl"
    out = {"purpose": "CEILING-1: attainable rung map for the pinned solver",
           "solver_pin": args.solver, "seed": SEED, "max_tokens": MAX_TOKENS,
           "resolution": "pilot (transport check)" if args.pilot
                         else f"screening (n={n} per cell), not decision-n",
           "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "cells": {}}

    with jsonl.open("a", encoding="utf-8") as fh:
        for wname in args.worlds.split(","):
            world = WORLDS[wname.strip()]
            for rung in args.rungs.split(","):
                rung = rung.strip()
                rng = random.Random(SEED + zlib.crc32(f"{wname}:{rung}".encode()))
                print(f"\n=== {wname} {rung} (n={n}) ===", flush=True)
                cell = run_cell(world, rung, n, args.solver, rng, fh)
                out["cells"][f"{wname}:{rung}"] = cell["summary"]
                print(json.dumps(cell["summary"], indent=2), flush=True)

    path = LEDGER / f"cycle001_ceiling_{tag}.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {path}\nwrote {jsonl}")


if __name__ == "__main__":
    sys.exit(main())
