"""
Harmonia auto-promotion review tool (conductor's tag-and-move interface).

Surfaces unreviewed yields from
`D:\\Prometheus\\harmonia\\agents\\_logs\\yields.jsonl` (written by the
five Harmonia child-agents via `harmonia.agents._scorer.append_yield_row`)
as compact one-screen cards, accepts single-key actions, and records the
outcome via `update_yield_outcome` which appends an `outcome_update` row
plus emits `outcome_observed` and (optionally) `marginal_value_assigned`
events into
`D:\\Prometheus\\harmonia\\agents\\_logs\\events.jsonl` + the
`agora:harmonia_events` Redis stream.

Per spec section 7 (Phase 0.5):
  - This is the conductor's primary review interface.
  - Each interaction must be fast: <=5 sec per row.
  - Phase 1 success bar: <=60 min total human review across two weeks
    for 50 promotions.

CLI usage (all paths relative to repo root D:\\Prometheus):
    python scripts/harmonia_review.py
    python scripts/harmonia_review.py --agent iris
    python scripts/harmonia_review.py --since 2026-05-20
    python scripts/harmonia_review.py --limit 10
    python scripts/harmonia_review.py --auto-batch a3,a3,d0
    python scripts/harmonia_review.py --status

Keys accepted inside the interactive loop:
    a      accept (outcome = accepted_human)
    d      dismiss (outcome = dismissed_human)
    s      skip (no write; advance)
    0..5   set marginal_substrate_value; 0 implies dismiss, >=1 implies accept
    q      quit (record nothing more; exit cleanly)
    ?      print help legend

`a3` (an `a` letter followed by a 0-5 digit) is also accepted as a single
token in `--auto-batch` mode: it means "accept with marginal value 3".
Similarly `d0` is "dismiss with marginal value 0".
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Path bootstrap so the script runs from anywhere on D:\Prometheus
_THIS = Path(__file__).resolve()
REPO_ROOT = _THIS.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harmonia.agents._scorer import (  # noqa: E402
    OUTCOME_ACCEPTED_HUMAN,
    OUTCOME_DISMISSED_HUMAN,
    YIELDS_JSONL,
    consolidate_yields,
    read_yields,
    update_yield_outcome,
)


HELP_LEGEND = """\
keys:
  a       accept (outcome = accepted_human)
  d       dismiss (outcome = dismissed_human)
  s       skip (no write; advance to next yield)
  0..5    tag marginal_substrate_value; 0 = dismiss, >=1 = accept
  a<0-5>  accept + tag value in one token (e.g. 'a3')
  d<0-5>  dismiss + tag value in one token (e.g. 'd0')
  q       quit (writes nothing more; exits cleanly)
  ?       print this help"""


PREVIEW_LINES = 8
CARD_WIDTH = 72


# ---------------------------------------------------------------------------
# Card rendering
# ---------------------------------------------------------------------------

def _format_ts(iso: Optional[str]) -> str:
    if not iso:
        return "<unknown>"
    try:
        dt = datetime.fromisoformat(iso)
        # Normalize to UTC display (the canonical form in yields.jsonl)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return iso


def _format_taint(taint: Optional[dict]) -> str:
    if not taint:
        return "<missing>"
    readable = taint.get("readable_by_agents") or []
    slots = taint.get("downstream_slots") or []
    sweep = taint.get("requires_taint_sweep_on_retract")
    used_for_training = taint.get("used_for_training")
    cross = taint.get("cross_swarm_consumers") or []
    parts = [
        f"readable_by_agents: {list(readable)}",
        f"downstream_slots: {list(slots)}",
        f"sweep_on_retract: {bool(sweep)}",
    ]
    if used_for_training is not None:
        parts.append(f"used_for_training: {bool(used_for_training)}")
    if cross:
        parts.append(f"cross_swarm: {list(cross)}")
    return "{" + "; ".join(parts) + "}"


def _artifact_preview(path_str: Optional[str], n_lines: int = PREVIEW_LINES) -> str:
    if not path_str:
        return "<no artifact_path>"
    try:
        p = Path(path_str)
        if not p.exists():
            return "<artifact file not found>"
        lines: list[str] = []
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= n_lines:
                    lines.append("  ...")
                    break
                lines.append("  " + line.rstrip("\n"))
        if not lines:
            return "  <empty file>"
        return "\n".join(lines)
    except Exception as e:
        return f"<preview failed: {e}>"


def render_card(row: dict, idx: int, total: int) -> str:
    bar = "=" * CARD_WIDTH
    agent = row.get("agent") or "<unknown>"
    yid = row.get("yield_id") or "<no-yid>"
    action_at = _format_ts(row.get("action_at"))
    artifact = row.get("artifact_path") or "<missing>"
    score = row.get("auto_promote_score")
    score_str = f"{score:.2f}" if isinstance(score, (int, float)) else "<missing>"
    tier1 = row.get("tier1_method") or "<missing>"
    kill = row.get("kill_path") or "<missing>"
    taint = _format_taint(row.get("taint_scope"))
    action_name = row.get("action") or "<missing>"
    doctrine = row.get("doctrine_version")
    preview = _artifact_preview(row.get("artifact_path"))

    lines = [
        bar,
        f"[{idx} of {total}] {agent} / {yid}  (action_at {action_at})",
        f"action:   {action_name}",
        f"artifact: {artifact}",
        f"score:    {score_str}  ({tier1})",
        f"kill:     {kill}",
        f"taint:    {taint}",
    ]
    if doctrine:
        lines.append(f"doctrine: {doctrine}")
    lines.append("")
    lines.append(f"artifact preview (first {PREVIEW_LINES} lines):")
    lines.append(preview)
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------

class Action:
    ACCEPT = "accept"
    DISMISS = "dismiss"
    SKIP = "skip"
    QUIT = "quit"
    HELP = "help"
    INVALID = "invalid"


def parse_token(tok: str) -> tuple[str, Optional[int]]:
    """Parse a single user token into (action, optional marginal value).

    Returns (Action.*, value or None). Action.INVALID means the caller
    should redisplay the legend and re-prompt without advancing.
    """
    t = (tok or "").strip().lower()
    if not t:
        return Action.INVALID, None
    if t == "q":
        return Action.QUIT, None
    if t in ("?", "h", "help"):
        return Action.HELP, None
    if t == "s":
        return Action.SKIP, None
    if t == "a":
        return Action.ACCEPT, None
    if t == "d":
        return Action.DISMISS, None
    # Combined forms a3, d0
    if len(t) == 2 and t[0] in ("a", "d") and t[1].isdigit():
        v = int(t[1])
        if 0 <= v <= 5:
            return (Action.ACCEPT if t[0] == "a" else Action.DISMISS), v
        return Action.INVALID, None
    # Bare digit: 0 -> dismiss, 1-5 -> accept
    if len(t) == 1 and t.isdigit():
        v = int(t)
        if 0 <= v <= 5:
            return (Action.DISMISS if v == 0 else Action.ACCEPT), v
        return Action.INVALID, None
    return Action.INVALID, None


# ---------------------------------------------------------------------------
# Session state + summary
# ---------------------------------------------------------------------------

class Session:
    def __init__(self) -> None:
        self.t_start = time.monotonic()
        self.n_reviewed = 0
        self.n_accepted = 0
        self.n_dismissed = 0
        self.n_skipped = 0
        self.n_deferred = 0
        self.values: list[int] = []
        self.failures: list[str] = []

    def record(self, action: str, value: Optional[int], yid: str) -> None:
        ok = True
        if action == Action.ACCEPT:
            ok = update_yield_outcome(yid, OUTCOME_ACCEPTED_HUMAN, marginal_substrate_value=value)
            if ok:
                self.n_reviewed += 1
                self.n_accepted += 1
                if value is not None:
                    self.values.append(value)
        elif action == Action.DISMISS:
            ok = update_yield_outcome(yid, OUTCOME_DISMISSED_HUMAN, marginal_substrate_value=value)
            if ok:
                self.n_reviewed += 1
                self.n_dismissed += 1
                if value is not None:
                    self.values.append(value)
        elif action == Action.SKIP:
            self.n_skipped += 1
        if not ok:
            self.failures.append(yid)

    def record_deferred(self, n: int) -> None:
        self.n_deferred = n

    def summary(self) -> str:
        elapsed = time.monotonic() - self.t_start
        mins = int(elapsed // 60)
        secs = int(elapsed - mins * 60)
        mean_v = (sum(self.values) / len(self.values)) if self.values else 0.0
        lines = [
            "Session summary: "
            f"{self.n_reviewed} reviewed "
            f"({self.n_accepted} accepted / {self.n_dismissed} dismissed), "
            f"{self.n_skipped} skipped, {self.n_deferred} deferred.",
            f"Time elapsed: {mins} min {secs} sec",
            f"Yields tagged with marginal_value: {len(self.values)}"
            + (f" (mean {mean_v:.1f})" if self.values else ""),
        ]
        if self.failures:
            lines.append(
                f"WARNING: {len(self.failures)} update_yield_outcome call(s) failed "
                f"for yield_id(s): {self.failures}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Listing unreviewed yields
# ---------------------------------------------------------------------------

def list_unreviewed(
    agent: Optional[str] = None,
    since_iso: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[dict]:
    """Return unreviewed yields (outcome is None), oldest-first, after the
    consolidation of the append-only log into latest-state-per-yield-id.
    """
    rows = read_yields(since_iso=since_iso)
    if not rows:
        return []
    consolidated = consolidate_yields(rows)
    unreviewed: list[dict] = []
    for yid, row in consolidated.items():
        if row.get("action") == "outcome_update":
            # Orphan update with no canonical row; skip.
            continue
        if row.get("outcome") is not None:
            continue
        if agent is not None and row.get("agent") != agent:
            continue
        unreviewed.append(row)

    def _sort_key(r: dict):
        ts = r.get("action_at") or ""
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    unreviewed.sort(key=_sort_key)
    if limit is not None and limit > 0:
        unreviewed = unreviewed[:limit]
    return unreviewed


# ---------------------------------------------------------------------------
# Interactive + auto-batch loops
# ---------------------------------------------------------------------------

def _prompt() -> str:
    try:
        return input("Action? [a/d/s 0-5 q ?]: ")
    except EOFError:
        return "q"
    except KeyboardInterrupt:
        return "q"


def run_interactive(unreviewed: list[dict]) -> Session:
    sess = Session()
    total = len(unreviewed)
    for i, row in enumerate(unreviewed, start=1):
        yid = row.get("yield_id") or "<no-yid>"
        print(render_card(row, i, total))
        while True:
            raw = _prompt()
            action, value = parse_token(raw)
            if action == Action.INVALID:
                print(HELP_LEGEND)
                continue
            if action == Action.HELP:
                print(HELP_LEGEND)
                continue
            if action == Action.QUIT:
                # Everything from i onward (inclusive of current, which the
                # user did not action) counts as deferred.
                sess.record_deferred(total - (i - 1))
                return sess
            if action == Action.SKIP:
                sess.record(Action.SKIP, None, yid)
                break
            # accept or dismiss
            sess.record(action, value, yid)
            break
    # Loop ended naturally: anything left unreviewed (none, since we iterated
    # every row) is zero deferred. Skipped rows are also unreviewed but were
    # counted under n_skipped, not deferred.
    sess.record_deferred(0)
    return sess


def run_auto_batch(unreviewed: list[dict], batch_tokens: list[str]) -> Session:
    """Drive the loop non-interactively. Each token is consumed in order.

    Token semantics match interactive single-key input but combined forms
    (e.g. `a3`, `d0`) are first-class. Extra tokens beyond the unreviewed
    list are ignored; running out of tokens defers the remaining yields.
    """
    sess = Session()
    total = len(unreviewed)
    token_iter = iter(batch_tokens)
    for i, row in enumerate(unreviewed, start=1):
        yid = row.get("yield_id") or "<no-yid>"
        print(render_card(row, i, total))
        try:
            raw = next(token_iter)
        except StopIteration:
            # No more directives: defer the rest (including this one).
            sess.record_deferred(total - (i - 1))
            print(f"[auto-batch] out of tokens at yield {i}; deferring remainder.")
            return sess
        print(f"[auto-batch] action token = {raw!r}")
        action, value = parse_token(raw)
        if action == Action.INVALID:
            print(f"[auto-batch] invalid token {raw!r} for yield {yid}; treating as skip.")
            sess.record(Action.SKIP, None, yid)
            continue
        if action == Action.HELP:
            print(HELP_LEGEND)
            # Help doesn't advance; consume one extra token if available.
            try:
                raw = next(token_iter)
            except StopIteration:
                sess.record_deferred(total - (i - 1))
                return sess
            action, value = parse_token(raw)
        if action == Action.QUIT:
            sess.record_deferred(total - (i - 1))
            return sess
        if action == Action.SKIP:
            sess.record(Action.SKIP, None, yid)
            continue
        sess.record(action, value, yid)
    sess.record_deferred(0)
    return sess


# ---------------------------------------------------------------------------
# Top-level entry
# ---------------------------------------------------------------------------

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="harmonia_review",
        description=(
            "Conductor's tag-and-move review tool for the Harmonia "
            "auto-promotion pipeline. Reads "
            "D:\\Prometheus\\harmonia\\agents\\_logs\\yields.jsonl, "
            "surfaces unreviewed rows, accepts 5-second actions, and "
            "records outcomes via the shared _scorer interface."
        ),
    )
    p.add_argument("--agent", default=None, help="filter to a single agent's yields (phylax/sophia/iris/argos/telos/...)")
    p.add_argument("--since", default=None, help="ISO timestamp filter (action_at >= this)")
    p.add_argument("--limit", type=int, default=None, help="cap session size at this many yields")
    p.add_argument("--auto-batch", default=None, help="non-interactive token list, comma-separated (e.g. 'a3,a3,d0')")
    p.add_argument("--status", action="store_true", help="report pending review count and exit")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_argparser().parse_args(argv)

    unreviewed = list_unreviewed(
        agent=args.agent,
        since_iso=args.since,
        limit=args.limit,
    )

    if args.status:
        n = len(unreviewed)
        if n == 0:
            print("No pending reviews. [OK]")
        else:
            print(f"{n} pending review(s).")
            # Per-agent breakdown for triage
            by_agent: dict[str, int] = {}
            for r in unreviewed:
                k = r.get("agent") or "<unknown>"
                by_agent[k] = by_agent.get(k, 0) + 1
            for k in sorted(by_agent):
                print(f"  {k}: {by_agent[k]}")
            # Oldest pending hint
            oldest = unreviewed[0]
            print(f"  oldest: {oldest.get('yield_id')} at {_format_ts(oldest.get('action_at'))}")
        return 0

    if not unreviewed:
        print("No pending reviews. [OK]")
        return 0

    print(
        f"Loaded {len(unreviewed)} unreviewed yield(s) from "
        f"D:\\Prometheus\\harmonia\\agents\\_logs\\yields.jsonl"
    )
    if args.agent:
        print(f"  filter: agent = {args.agent}")
    if args.since:
        print(f"  filter: since = {args.since}")
    if args.limit:
        print(f"  filter: limit = {args.limit}")
    print()

    if args.auto_batch:
        tokens = [t for t in (tok.strip() for tok in args.auto_batch.split(",")) if t]
        sess = run_auto_batch(unreviewed, tokens)
    else:
        sess = run_interactive(unreviewed)

    print()
    print(sess.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
