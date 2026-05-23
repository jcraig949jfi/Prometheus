"""
harmonia_weekly_report.py - weekly maturation roll-up for the Harmonia
auto-promotion pipeline.

Reads `D:\\Prometheus\\harmonia\\agents\\_logs\\events.jsonl` and
`D:\\Prometheus\\harmonia\\agents\\_logs\\yields.jsonl` for the prior 7
days (configurable via --window or --since), assembles a markdown
roll-up, and writes it to
`D:\\Prometheus\\harmonia\\agents\\_logs\\weekly_<YYYYMMDD_HHMMSS>.md`.

The report is the conductor's primary surface for understanding "is the
system getting smarter or just busier" -- wins, losses, trends,
health-signals, and per-agent maturation cards (spec §6.7 in
`D:\\Prometheus\\harmonia\\agents\\AUTOPROMOTION_TARGETS.md`). The
conductor reviews it in <=5 minutes.

Phase 0 reality: events.jsonl + yields.jsonl currently contain only the
`_scorer.py` smoke-test rows. The report is built to degrade gracefully:
all five agent cards print with status `not_yet_wired` until real
promotions land. The trend tracker is in place so that as the swarm
produces real data, the time-series consumer is already wired.

Usage:
    python scripts/harmonia_weekly_report.py                   # default 7d
    python scripts/harmonia_weekly_report.py --window 14d      # custom window
    python scripts/harmonia_weekly_report.py --since 2026-05-15
    python scripts/harmonia_weekly_report.py --json            # machine output
    python scripts/harmonia_weekly_report.py --stdout          # print only
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

# Add repo root to sys.path so we can import the scorer interface
_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harmonia.agents._scorer import (  # noqa: E402
    emit_event,
    read_yields,
    consolidate_yields,
    EVENT_WEEKLY_REPORT_EMITTED,
    OUTCOME_CLASSES,
    POSITIVE_OUTCOMES,
    NEGATIVE_OUTCOMES,
    NEUTRAL_OUTCOMES,
    YIELDS_JSONL,
    EVENTS_JSONL,
    LOGS_DIR,
    AGENTS_DIR,
)

AGENT_NAMES = ("phylax", "sophia", "iris", "argos", "telos")
SWARM_KEY = "swarm"

# Thresholds for §6.7 health-signal alerts
THRESH_TAINT_SWEEP_WARN = 5
THRESH_QUIESCE_WARN = 1            # any -> WARN
THRESH_QUIESCE_ALERT = 1           # >1 -> ALERT
THRESH_ABORT_RATE_WARN = 0.20      # >20% of proposed
THRESH_CONSUMER_GROWTH_WARN = 5


# ---------------------------------------------------------------------------
# CLI parsing
# ---------------------------------------------------------------------------

def _parse_window(window: str) -> timedelta:
    m = re.fullmatch(r"(\d+)\s*([hdwm])", window.lower().strip())
    if not m:
        raise SystemExit(
            f"bad --window value '{window}'; expected like '7d', '24h', '2w'"
        )
    n = int(m.group(1))
    unit = m.group(2)
    return {
        "h": timedelta(hours=n),
        "d": timedelta(days=n),
        "w": timedelta(weeks=n),
        "m": timedelta(days=30 * n),
    }[unit]


def _parse_since(since: str) -> datetime:
    # Accept YYYY-MM-DD or full ISO
    try:
        if "T" in since:
            return datetime.fromisoformat(since).astimezone(timezone.utc)
        d = datetime.fromisoformat(since)
        return d.replace(tzinfo=timezone.utc)
    except Exception as e:
        raise SystemExit(f"bad --since value '{since}': {e}")


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Weekly maturation report for the Harmonia auto-promotion "
            "pipeline (spec §6.7). Reads events.jsonl + yields.jsonl from "
            "D:\\Prometheus\\harmonia\\agents\\_logs\\."
        )
    )
    p.add_argument("--window", default="7d",
                   help="window size; e.g. '7d', '24h', '2w' (default: 7d)")
    p.add_argument("--since", default=None,
                   help="explicit window start (YYYY-MM-DD or ISO); "
                        "overrides --window")
    p.add_argument("--json", action="store_true",
                   help="emit machine-readable JSON instead of markdown")
    p.add_argument("--stdout", action="store_true",
                   help="print to stdout only; do not write to a weekly_*.md")
    p.add_argument("--no-emit-event", action="store_true",
                   help="skip the weekly_report_emitted event "
                        "(use when previewing)")
    return p


# ---------------------------------------------------------------------------
# Event-log reader
# ---------------------------------------------------------------------------

def read_events(
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> list[dict]:
    """Read events.jsonl rows in [since, until). Graceful on missing file."""
    if not EVENTS_JSONL.exists():
        return []
    out: list[dict] = []
    try:
        with open(EVENTS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                ts_raw = r.get("ts")
                if not ts_raw:
                    continue
                try:
                    ts = datetime.fromisoformat(ts_raw)
                except Exception:
                    continue
                if since is not None and ts < since:
                    continue
                if until is not None and ts >= until:
                    continue
                out.append(r)
    except Exception as e:
        print(f"[read_events] read failed: {e}", file=sys.stderr)
    return out


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _empty_agent_stats() -> dict:
    return {
        "events_by_class": Counter(),
        "total_events": 0,
        "tick_complete": 0,
        "tier0_reject": 0,
        "tier1_scored": 0,
        "bandit_pulls": 0,
        "bandit_explore_pulls": 0,
        "autopromote_proposed": 0,
        "autopromote_committed": 0,
        "autopromote_aborted": 0,
        "taint_sweep_started": 0,
        "scorer_self_quiesce": 0,
        "doctrine_version_check_failures": 0,
        "errors": 0,
        "yields": [],
        # Outcome buckets (from consolidated yields)
        "accepted_human": 0,
        "accepted_downstream_use": 0,
        "dismissed_human": 0,
        "auto_retracted": 0,
        "contradicted": 0,
        "survived_ttl_unreviewed": 0,
        "stale_unconsumed": 0,
        "marginal_values": [],          # ints 0..5
        "time_to_outcome_seconds": [],  # float seconds
        "cross_swarm_consumers": set(),
    }


def aggregate_events_by_agent(events: list[dict]) -> dict[str, dict]:
    stats: dict[str, dict] = {a: _empty_agent_stats() for a in AGENT_NAMES}
    stats[SWARM_KEY] = _empty_agent_stats()

    for ev in events:
        agent = ev.get("agent") or "unknown"
        klass = ev.get("event_class") or "unknown"
        data = ev.get("event_data") or {}

        # Route to known agent bucket; unknown agents only count toward swarm
        buckets = [stats[SWARM_KEY]]
        if agent in stats:
            buckets.append(stats[agent])

        for b in buckets:
            b["events_by_class"][klass] += 1
            b["total_events"] += 1
            if klass == "tick_complete":
                b["tick_complete"] += 1
            elif klass == "tier0_reject":
                b["tier0_reject"] += 1
            elif klass == "tier1_scored":
                b["tier1_scored"] += 1
            elif klass == "bandit_arm_pulled":
                b["bandit_pulls"] += 1
                if data.get("mode") == "explore":
                    b["bandit_explore_pulls"] += 1
            elif klass == "autopromote_proposed":
                b["autopromote_proposed"] += 1
            elif klass == "autopromote_committed":
                b["autopromote_committed"] += 1
            elif klass == "autopromote_aborted":
                b["autopromote_aborted"] += 1
            elif klass == "taint_sweep_started":
                b["taint_sweep_started"] += 1
            elif klass == "scorer_self_quiesce":
                b["scorer_self_quiesce"] += 1
            elif klass == "doctrine_version_check":
                if not data.get("passed", True):
                    b["doctrine_version_check_failures"] += 1
            # Generic error count: any event whose data has errors > 0
            try:
                err_n = data.get("errors")
                if isinstance(err_n, (int, float)) and err_n > 0:
                    b["errors"] += 1
            except Exception:
                pass
    return stats


def aggregate_yields_by_agent(
    consolidated: dict[str, dict],
) -> dict[str, dict]:
    stats: dict[str, dict] = {a: _empty_agent_stats() for a in AGENT_NAMES}
    stats[SWARM_KEY] = _empty_agent_stats()

    for yid, row in consolidated.items():
        agent = row.get("agent")
        outcome = row.get("outcome")
        mv = row.get("marginal_substrate_value")
        taint = row.get("taint_scope") or {}
        action_at = row.get("action_at")
        outcome_at = row.get("outcome_observed_at")

        buckets = [stats[SWARM_KEY]]
        if agent in stats:
            buckets.append(stats[agent])

        for b in buckets:
            b["yields"].append(row)
            if outcome in OUTCOME_CLASSES:
                b[outcome] = b.get(outcome, 0) + 1
            if isinstance(mv, int):
                b["marginal_values"].append(mv)
            if action_at and outcome_at:
                try:
                    a_dt = datetime.fromisoformat(action_at)
                    o_dt = datetime.fromisoformat(outcome_at)
                    b["time_to_outcome_seconds"].append(
                        (o_dt - a_dt).total_seconds()
                    )
                except Exception:
                    pass
            cs = taint.get("cross_swarm_consumers") or []
            for c in cs:
                b["cross_swarm_consumers"].add(c)
    return stats


def merge_agent_stats(
    ev_stats: dict[str, dict],
    yield_stats: dict[str, dict],
) -> dict[str, dict]:
    """Both aggregators populate parallel agent buckets; combine them so each
    agent has both event and yield aggregates in one dict."""
    merged: dict[str, dict] = {}
    keys = set(ev_stats) | set(yield_stats)
    for k in keys:
        a = ev_stats.get(k) or _empty_agent_stats()
        b = yield_stats.get(k) or _empty_agent_stats()
        m = dict(a)  # shallow copy
        # Overlay yield-side fields
        for fld in (
            "yields", "marginal_values", "time_to_outcome_seconds",
            "cross_swarm_consumers",
            "accepted_human", "accepted_downstream_use",
            "dismissed_human", "auto_retracted", "contradicted",
            "survived_ttl_unreviewed", "stale_unconsumed",
        ):
            m[fld] = b[fld]
        merged[k] = m
    return merged


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------

def _mean(values: list[float]) -> Optional[float]:
    return statistics.fmean(values) if values else None


def _median(values: list[float]) -> Optional[float]:
    return statistics.median(values) if values else None


def _fp_rate(stats: dict) -> Optional[float]:
    promos = stats["autopromote_committed"]
    if promos == 0:
        return None
    fp = stats["dismissed_human"] + stats["auto_retracted"] + stats["contradicted"]
    return fp / promos


def _abort_rate(stats: dict) -> Optional[float]:
    proposed = stats["autopromote_proposed"]
    if proposed == 0:
        return None
    return stats["autopromote_aborted"] / proposed


def _explore_rate(stats: dict) -> Optional[float]:
    pulls = stats["bandit_pulls"]
    if pulls == 0:
        return None
    return stats["bandit_explore_pulls"] / pulls


def _tier0_reject_rate(stats: dict) -> Optional[float]:
    # Approximate "total candidates" as tier0_reject + tier1_scored events,
    # since every survivor of Tier 0 gets a Tier 1 score.
    denom = stats["tier0_reject"] + stats["tier1_scored"]
    if denom == 0:
        return None
    return stats["tier0_reject"] / denom


def _trend_arrow(curr: Optional[float], prior: Optional[float], eps: float = 1e-9) -> str:
    if curr is None or prior is None:
        return "->"
    if curr > prior + eps:
        return "up"
    if curr < prior - eps:
        return "down"
    return "->"


def _fmt(v: Optional[float], pct: bool = False, places: int = 2) -> str:
    if v is None:
        return "-"
    if pct:
        return f"{v * 100:.{places}f}%"
    return f"{v:.{places}f}"


def _fmt_delta(curr: Optional[float], prior: Optional[float],
               pct: bool = False, places: int = 2) -> str:
    if curr is None and prior is None:
        return "-"
    if prior is None:
        return f"{_fmt(curr, pct=pct, places=places)} (no prior)"
    if curr is None:
        return f"- (was {_fmt(prior, pct=pct, places=places)})"
    delta = curr - prior
    arrow = _trend_arrow(curr, prior)
    if pct:
        return f"{_fmt(curr, pct=True, places=places)} {arrow} (delta {delta * 100:+.{places}f}pp)"
    return f"{_fmt(curr, places=places)} {arrow} (delta {delta:+.{places}f})"


# ---------------------------------------------------------------------------
# Section assembly
# ---------------------------------------------------------------------------

def _header_section(
    since: datetime,
    until: datetime,
    stats: dict[str, dict],
    now: datetime,
) -> str:
    swarm = stats[SWARM_KEY]
    lines = [
        "# Harmonia weekly maturation report",
        "",
        f"- Window: `{since.isoformat()}` to `{until.isoformat()}`",
        f"- Generated_at: `{now.isoformat()}`",
        f"- Total ticks observed: **{swarm['tick_complete']}**",
        f"- Total promotions observed: **{swarm['autopromote_committed']}**",
        f"- Total errors: **{swarm['errors']}**",
        "",
        f"Source logs: `{EVENTS_JSONL}`, `{YIELDS_JSONL}`",
        "",
    ]
    return "\n".join(lines)


def _wins_section(stats: dict[str, dict]) -> str:
    lines = [
        "## 1. Wins (per-agent + swarm-wide)",
        "",
        "| Agent | accepted_human | accepted_downstream_use | mean(marginal_value) | promotions w/ mv >= 3 |",
        "|---|---|---|---|---|",
    ]
    for name in list(AGENT_NAMES) + [SWARM_KEY]:
        s = stats[name]
        mv = s["marginal_values"]
        mv_mean = _mean(mv)
        mv_ge3 = sum(1 for v in mv if v >= 3)
        lines.append(
            f"| {name} | {s['accepted_human']} | {s['accepted_downstream_use']} | "
            f"{_fmt(mv_mean)} | {mv_ge3} |"
        )
    lines.append("")
    return "\n".join(lines)


def _losses_section(stats: dict[str, dict]) -> str:
    lines = [
        "## 2. Losses (per-agent)",
        "",
        "| Agent | dismissed_human | auto_retracted | contradicted | survived_ttl_unreviewed | stale_unconsumed |",
        "|---|---|---|---|---|---|",
    ]
    for name in list(AGENT_NAMES) + [SWARM_KEY]:
        s = stats[name]
        lines.append(
            f"| {name} | {s['dismissed_human']} | {s['auto_retracted']} | "
            f"{s['contradicted']} | {s['survived_ttl_unreviewed']} | "
            f"{s['stale_unconsumed']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _trend_section(
    curr_stats: dict[str, dict],
    prior_stats: Optional[dict[str, dict]],
) -> str:
    lines = [
        "## 3. Maturation trends (week-over-week)",
        "",
    ]
    if prior_stats is None:
        lines.append(
            "_No prior-week data available; current-week values shown with `(no prior)`._"
        )
        lines.append("")

    lines += [
        "| Agent | FP rate | mean(mv) | median time-to-outcome (s) | Tier 0 reject rate | bandit explore rate |",
        "|---|---|---|---|---|---|",
    ]
    for name in list(AGENT_NAMES) + [SWARM_KEY]:
        s = curr_stats[name]
        p = prior_stats[name] if prior_stats else None

        fp_c = _fp_rate(s)
        fp_p = _fp_rate(p) if p else None

        mv_c = _mean(s["marginal_values"])
        mv_p = _mean(p["marginal_values"]) if p else None

        ttO_c = _median(s["time_to_outcome_seconds"])
        ttO_p = _median(p["time_to_outcome_seconds"]) if p else None

        t0_c = _tier0_reject_rate(s)
        t0_p = _tier0_reject_rate(p) if p else None

        ex_c = _explore_rate(s)
        ex_p = _explore_rate(p) if p else None

        lines.append(
            f"| {name} | {_fmt_delta(fp_c, fp_p, pct=True)} "
            f"| {_fmt_delta(mv_c, mv_p)} "
            f"| {_fmt_delta(ttO_c, ttO_p, places=0)} "
            f"| {_fmt_delta(t0_c, t0_p, pct=True)} "
            f"| {_fmt_delta(ex_c, ex_p, pct=True)} |"
        )
    lines.append("")
    return "\n".join(lines)


def _alert_str(count: int, warn_at: int, alert_at: Optional[int] = None) -> str:
    if alert_at is not None and count >= alert_at and alert_at > warn_at:
        return "ALERT"
    if count > warn_at:
        return "WARN"
    return "OK"


def _rate_alert_str(rate: Optional[float], warn_at: float) -> str:
    if rate is None:
        return "OK"
    return "WARN" if rate > warn_at else "OK"


def _health_section(
    curr_stats: dict[str, dict],
    prior_stats: Optional[dict[str, dict]],
) -> str:
    swarm = curr_stats[SWARM_KEY]
    prior_swarm = prior_stats[SWARM_KEY] if prior_stats else None

    taint = swarm["taint_sweep_started"]
    quiesce = swarm["scorer_self_quiesce"]
    doctrine_fail = swarm["doctrine_version_check_failures"]
    abort_rate = _abort_rate(swarm)

    consumers_curr = len(swarm["cross_swarm_consumers"])
    consumers_prior = (
        len(prior_swarm["cross_swarm_consumers"]) if prior_swarm else None
    )
    consumers_delta = (
        consumers_curr - consumers_prior if consumers_prior is not None else None
    )

    # Quiesce: any -> WARN; >1 -> ALERT
    if quiesce == 0:
        quiesce_alert = "OK"
    elif quiesce <= 1:
        quiesce_alert = "WARN"
    else:
        quiesce_alert = "ALERT"

    doctrine_alert = "WARN" if doctrine_fail > 0 else "OK"

    if consumers_delta is None:
        consumer_alert = "OK"
    else:
        consumer_alert = "WARN" if consumers_delta > THRESH_CONSUMER_GROWTH_WARN else "OK"

    lines = [
        "## 4. Health signals",
        "",
        "| Signal | Count this week | Notes | Alert |",
        "|---|---|---|---|",
        f"| Taint-sweep events fired | {taint} | warn threshold >{THRESH_TAINT_SWEEP_WARN} | "
        f"{_alert_str(taint, THRESH_TAINT_SWEEP_WARN)} |",
        f"| scorer_self_quiesce events | {quiesce} | any=WARN, >1=ALERT | {quiesce_alert} |",
        f"| doctrine_version_check failures | {doctrine_fail} | any failure=WARN | {doctrine_alert} |",
        f"| autopromote_aborted rate | {_fmt(abort_rate, pct=True) if abort_rate is not None else '-'}"
        f" | warn >{int(THRESH_ABORT_RATE_WARN * 100)}% of proposed | "
        f"{_rate_alert_str(abort_rate, THRESH_ABORT_RATE_WARN)} |",
        f"| Cross-swarm consumer count | {consumers_curr} "
        f"(delta {'+' + str(consumers_delta) if consumers_delta is not None and consumers_delta >= 0 else (str(consumers_delta) if consumers_delta is not None else 'no prior')}) "
        f"| warn delta >{THRESH_CONSUMER_GROWTH_WARN} | {consumer_alert} |",
        "",
    ]
    return "\n".join(lines)


def _agent_card(
    name: str,
    s: dict,
    four_wk_avg: Optional[dict],
) -> str:
    rows = [
        ("autopromote_committed", s["autopromote_committed"]),
        ("accepted_human", s["accepted_human"]),
        ("dismissed_human", s["dismissed_human"]),
        ("taint_sweep_started", s["taint_sweep_started"]),
    ]
    title = name.capitalize()
    lines = [f"## {title}", ""]
    lines.append("| Event class | Count this week | 4wk avg | Trend |")
    lines.append("|---|---|---|---|")
    for klass, count in rows:
        if four_wk_avg is not None:
            avg = four_wk_avg.get(klass, 0.0)
            arrow = _trend_arrow(float(count), avg)
            avg_str = f"{avg:.1f}"
        else:
            avg_str = "0.0"
            arrow = "->"
        lines.append(f"| {klass} | {count} | {avg_str} | {arrow} |")
    lines.append("")

    # Natural-language summary
    promos = s["autopromote_committed"]
    accepts = s["accepted_human"] + s["accepted_downstream_use"]
    losses = s["dismissed_human"] + s["auto_retracted"] + s["contradicted"]
    taint = s["taint_sweep_started"]
    pulls = s["bandit_pulls"]

    if (promos + accepts + losses + taint + pulls + s["total_events"]) == 0:
        summary = (
            f"{title} this week: 0 auto-promotions, 0 accepted, no taint events. "
            f"Status: not_yet_wired (Phase 0)."
        )
    else:
        accept_pct = (accepts / promos * 100) if promos else None
        loss_pct = (losses / promos * 100) if promos else None
        bits = [
            f"{promos} auto-promotions",
            f"{accepts} accepted",
            f"{losses} losses",
        ]
        if accept_pct is not None:
            bits.append(f"accept rate {accept_pct:.0f}%")
        if loss_pct is not None and loss_pct > 0:
            bits.append(f"loss rate {loss_pct:.0f}%")
        if taint > 0:
            bits.append(f"{taint} taint sweeps")
        if pulls > 0:
            ex = _explore_rate(s)
            if ex is not None:
                bits.append(f"bandit explore rate {ex * 100:.0f}%")
        summary = f"{title} this week: " + ", ".join(bits) + "."
    lines.append(f"**Summary**: {summary}")
    lines.append("")
    return "\n".join(lines)


def _agent_cards_section(
    curr_stats: dict[str, dict],
    four_wk_avgs: Optional[dict[str, dict]],
) -> str:
    lines = ["## 5. Per-agent maturation cards", ""]
    for name in AGENT_NAMES:
        s = curr_stats[name]
        avg = four_wk_avgs.get(name) if four_wk_avgs else None
        lines.append(_agent_card(name, s, avg))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4-week rolling average (for agent cards)
# ---------------------------------------------------------------------------

def four_week_averages(
    until: datetime,
    window: timedelta,
) -> dict[str, dict[str, float]]:
    """For each agent, compute the average count per event class over the
    four windows preceding `until`. Used by the per-agent card trend column.

    Returns: { agent_name: { event_class: avg_count_per_window } }
    """
    sums: dict[str, Counter] = {a: Counter() for a in AGENT_NAMES}
    n_windows = 4
    for i in range(n_windows):
        w_end = until - i * window
        w_start = w_end - window
        ev = read_events(since=w_start, until=w_end)
        for row in ev:
            agent = row.get("agent")
            klass = row.get("event_class")
            if agent in sums and klass:
                sums[agent][klass] += 1
    return {
        a: {klass: count / n_windows for klass, count in counter.items()}
        for a, counter in sums.items()
    }


# ---------------------------------------------------------------------------
# Build the report
# ---------------------------------------------------------------------------

def build_report(
    since: datetime,
    until: datetime,
    now: datetime,
) -> tuple[str, dict[str, dict], dict[str, dict]]:
    """Assemble the full markdown report. Returns
    (markdown, current_stats, prior_stats_or_None)."""
    # Current window
    events_curr = read_events(since=since, until=until)
    yields_curr_raw = read_yields(since_iso=since.isoformat())
    # Filter consolidated yields to only those whose canonical action_at is
    # in window. read_yields already filters on action_at >= since.
    yields_curr_raw = [
        r for r in yields_curr_raw
        if _action_at_in_window(r, since, until)
    ]
    consolidated_curr = consolidate_yields(yields_curr_raw)

    # Prior window (for trend / delta)
    window = until - since
    prior_until = since
    prior_since = since - window
    events_prior = read_events(since=prior_since, until=prior_until)
    yields_prior_raw = [
        r for r in read_yields(since_iso=prior_since.isoformat())
        if _action_at_in_window(r, prior_since, prior_until)
    ]
    consolidated_prior = consolidate_yields(yields_prior_raw)

    # Aggregate
    ev_stats_curr = aggregate_events_by_agent(events_curr)
    yl_stats_curr = aggregate_yields_by_agent(consolidated_curr)
    curr_stats = merge_agent_stats(ev_stats_curr, yl_stats_curr)

    prior_has_data = bool(events_prior) or bool(consolidated_prior)
    if prior_has_data:
        ev_stats_prior = aggregate_events_by_agent(events_prior)
        yl_stats_prior = aggregate_yields_by_agent(consolidated_prior)
        prior_stats = merge_agent_stats(ev_stats_prior, yl_stats_prior)
    else:
        prior_stats = None

    four_wk_avgs = four_week_averages(until=since, window=window)

    sections = [
        _header_section(since, until, curr_stats, now),
        _wins_section(curr_stats),
        _losses_section(curr_stats),
        _trend_section(curr_stats, prior_stats),
        _health_section(curr_stats, prior_stats),
        _agent_cards_section(curr_stats, four_wk_avgs),
        f"---\n\n"
        f"_Report file: `{LOGS_DIR}\\weekly_<utc>.md`._  "
        f"_Source: spec §6.7 in `D:\\Prometheus\\harmonia\\agents\\AUTOPROMOTION_TARGETS.md`._\n",
    ]
    return "\n".join(sections), curr_stats, prior_stats


def _action_at_in_window(
    row: dict, since: datetime, until: datetime,
) -> bool:
    ts_raw = row.get("action_at")
    if not ts_raw:
        return False
    try:
        ts = datetime.fromisoformat(ts_raw)
    except Exception:
        return False
    return since <= ts < until


# ---------------------------------------------------------------------------
# JSON view (for --json)
# ---------------------------------------------------------------------------

def _stats_to_jsonable(stats: dict[str, dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for k, v in stats.items():
        d = {}
        for fld, val in v.items():
            if fld == "events_by_class":
                d[fld] = dict(val)
            elif fld == "cross_swarm_consumers":
                d[fld] = sorted(val)
            elif fld == "yields":
                d["yield_count"] = len(val)
            else:
                d[fld] = val
        out[k] = d
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    args = _build_argparser().parse_args(argv)
    now = datetime.now(timezone.utc)
    if args.since:
        since = _parse_since(args.since)
        until = now
    else:
        window = _parse_window(args.window)
        until = now
        since = until - window

    md, curr_stats, prior_stats = build_report(since, until, now)

    if args.json:
        payload = {
            "since": since.isoformat(),
            "until": until.isoformat(),
            "generated_at": now.isoformat(),
            "current": _stats_to_jsonable(curr_stats),
            "prior": _stats_to_jsonable(prior_stats) if prior_stats else None,
        }
        out_text = json.dumps(payload, indent=2, default=str)
    else:
        out_text = md

    out_path: Optional[Path] = None
    if not args.stdout:
        out_path = LOGS_DIR / f"weekly_{now.strftime('%Y%m%d_%H%M%S')}.md"
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
        except Exception as e:
            print(f"[weekly_report] write failed: {e}", file=sys.stderr)
            out_path = None

    print(out_text)

    if not args.no_emit_event:
        emit_event(
            EVENT_WEEKLY_REPORT_EMITTED,
            {
                "since": since.isoformat(),
                "until": until.isoformat(),
                "report_path": str(out_path) if out_path else None,
                "total_ticks": curr_stats[SWARM_KEY]["tick_complete"],
                "total_promotions": curr_stats[SWARM_KEY]["autopromote_committed"],
                "total_errors": curr_stats[SWARM_KEY]["errors"],
            },
            agent="harmonia_weekly_report",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
