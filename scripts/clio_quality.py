"""
Clio v0.4 — Quality observability

Computes a rolling-window quality snapshot over Clio's substrate output:
volume (papers / extractions / submissions), yield (claims per paper,
zero-claim rate), specificity (claim_type / paradigm hints / falsifiable
/ confidence percentiles), diversity (paradigm coverage), and failure
modes (sigma submission errors, theorem→counterexample kill-path mismatch).

Snapshots persist to agora.clio_quality_snapshots (time-series) AND merge
into Clio's agent_heartbeats.status_json under a 'quality' key so the
dashboard and Metis brief pick them up automatically through the existing
intelligence-pipeline path.

Observability only — no claim filtering happens here. Per James 2026-05-18:
"observe for now, this is important to test to see if sigma engine is
behaving as expected. We also want to ensure that we're not killing claims
that the paper suggest should not be killed."

The theorem-kill-path mismatch tracker (theorem claims whose kill_path
template includes "counterexample") is the canary for the latter concern.
If the metric is non-trivial, kill_path generation needs refinement.

Usage:
    python scripts/clio_quality.py --snapshot              # compute, persist, heartbeat
    python scripts/clio_quality.py --show                  # render the latest snapshot
    python scripts/clio_quality.py --show-history 24       # render last N snapshots
"""
import argparse
import json
import logging
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CLIO-QUALITY] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("clio_quality")


# ---------------------------------------------------------------------------
# Helpers — pure functions for testability
# ---------------------------------------------------------------------------

def _pct(numer: int, denom: int) -> float:
    """Safe percentage. Returns 0.0 when denom == 0."""
    return round(100.0 * numer / denom, 2) if denom > 0 else 0.0


def _round_or_none(v: Any, ndigits: int = 3) -> Optional[float]:
    """Round a numeric value, or None for None."""
    if v is None:
        return None
    try:
        return round(float(v), ndigits)
    except (TypeError, ValueError):
        return None


def _percentiles(values: list, ps: tuple = (25, 50, 75)) -> dict:
    """Compute named percentiles. Returns {p25: ..., p50: ..., p75: ...}.
    Empty input returns Nones."""
    out = {f"p{p}": None for p in ps}
    if not values:
        return out
    vs = sorted(float(v) for v in values if v is not None)
    if not vs:
        return out
    n = len(vs)
    for p in ps:
        # Use the same definition as numpy default: linear interpolation
        k = (p / 100.0) * (n - 1)
        lo, hi = int(k), min(int(k) + 1, n - 1)
        frac = k - lo
        out[f"p{p}"] = round(vs[lo] + frac * (vs[hi] - vs[lo]), 3)
    return out


def _gini(values: list) -> Optional[float]:
    """Gini coefficient (concentration measure). 0=even, 1=fully concentrated.
    Returns None for empty or single-element input."""
    if not values:
        return None
    vs = sorted(float(v) for v in values if v is not None)
    if len(vs) < 2:
        return None
    n = len(vs)
    cumsum = 0.0
    total = 0.0
    for i, v in enumerate(vs):
        cumsum += (i + 1) * v
        total += v
    if total == 0:
        return None
    return round((2 * cumsum) / (n * total) - (n + 1) / n, 4)


# ---------------------------------------------------------------------------
# Metric collectors — each takes a cursor and returns a dict slice
# ---------------------------------------------------------------------------

def _collect_volume(cur, hours: int) -> dict:
    """Counts of papers / extractions / submissions in window."""
    cur.execute("""
        SELECT COUNT(*) FROM agora.clio_papers
        WHERE found_at > NOW() - (%s || ' hours')::INTERVAL
    """, (str(hours),))
    papers = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM agora.clio_claim_extractions
        WHERE extracted_at > NOW() - (%s || ' hours')::INTERVAL
    """, (str(hours),))
    extractions = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM agora.clio_claim_extractions
        WHERE sigma_submitted_at > NOW() - (%s || ' hours')::INTERVAL
          AND sigma_claim_id IS NOT NULL
    """, (str(hours),))
    submitted = cur.fetchone()[0]
    return {
        "papers_24h": papers,
        "claims_extracted_24h": extractions,
        "claims_submitted_24h": submitted,
    }


def _collect_yield(cur, hours: int) -> dict:
    """Distribution of claims-per-paper, papers-with-zero-claims rate."""
    cur.execute("""
        SELECT p.id, COUNT(e.id) AS n_claims
        FROM agora.clio_papers p
        LEFT JOIN agora.clio_claim_extractions e ON e.paper_id = p.id
        WHERE p.found_at > NOW() - (%s || ' hours')::INTERVAL
          AND EXISTS (
              SELECT 1 FROM agora.clio_claim_extractions e2
              WHERE e2.paper_id = p.id
          )
        GROUP BY p.id
    """, (str(hours),))
    rows = cur.fetchall()
    counts = [r[1] for r in rows]
    out = {
        "claims_per_paper_mean": round(statistics.fmean(counts), 3) if counts else None,
        "papers_attempted_24h": len(counts),
    }
    out.update({f"claims_per_paper_{k}": v for k, v in _percentiles(counts).items()})
    zero = sum(1 for c in counts if c == 0)
    out["papers_with_zero_claims_pct"] = _pct(zero, len(counts))
    return out


def _collect_specificity(cur, hours: int) -> dict:
    """Per-claim quality signals over claims extracted in window."""
    cur.execute("""
        SELECT claim_type, paradigm_hint, open_problem_hint, falsifiable,
               confidence, LENGTH(claim_text) AS text_len
        FROM agora.clio_claim_extractions
        WHERE extracted_at > NOW() - (%s || ' hours')::INTERVAL
    """, (str(hours),))
    rows = cur.fetchall()
    n = len(rows)
    if n == 0:
        return {
            "claim_type_known_pct": 0.0, "paradigm_hint_pct": 0.0,
            "open_problem_hint_pct": 0.0, "falsifiable_pct": 0.0,
            "confidence_mean": None, "confidence_p25": None,
            "confidence_p50": None, "confidence_p75": None,
            "claim_text_length_mean": None,
        }
    typed = sum(1 for r in rows if r[0])
    paradigmed = sum(1 for r in rows if r[1])
    open_p = sum(1 for r in rows if r[2])
    falsif = sum(1 for r in rows if r[3] is True)
    conf_vals = [r[4] for r in rows if r[4] is not None]
    text_lens = [r[5] for r in rows if r[5] is not None]
    out = {
        "claim_type_known_pct": _pct(typed, n),
        "paradigm_hint_pct": _pct(paradigmed, n),
        "open_problem_hint_pct": _pct(open_p, n),
        "falsifiable_pct": _pct(falsif, n),
        "confidence_mean": _round_or_none(statistics.fmean(conf_vals)) if conf_vals else None,
        "claim_text_length_mean": round(statistics.fmean(text_lens), 1) if text_lens else None,
    }
    out.update({f"confidence_{k}": v for k, v in _percentiles(conf_vals).items()})
    return out


def _collect_diversity(cur, hours: int) -> dict:
    """Paradigm coverage + per-query yield distribution."""
    cur.execute("""
        SELECT paradigm_hint, COUNT(*) AS n
        FROM agora.clio_claim_extractions
        WHERE extracted_at > NOW() - (%s || ' hours')::INTERVAL
          AND paradigm_hint IS NOT NULL
        GROUP BY paradigm_hint
        ORDER BY n DESC
    """, (str(hours),))
    paradigm_rows = cur.fetchall()
    paradigm_distribution = {r[0]: r[1] for r in paradigm_rows[:15]}  # cap on stored detail
    paradigm_counts = [r[1] for r in paradigm_rows]

    # COUNT(DISTINCT p.id) is critical here: the LEFT JOIN multiplies rows
    # by claim count, so naive COUNT(p.id) over-counts papers with >1 claim.
    cur.execute("""
        SELECT p.query_matched, COUNT(DISTINCT p.id) AS n_papers,
               COUNT(e.id) AS n_claims
        FROM agora.clio_papers p
        LEFT JOIN agora.clio_claim_extractions e ON e.paper_id = p.id
        WHERE p.found_at > NOW() - (%s || ' hours')::INTERVAL
        GROUP BY p.query_matched
        ORDER BY n_papers DESC
    """, (str(hours),))
    qrows = cur.fetchall()
    query_yield = []
    for q, npapers, nclaims in qrows:
        cpp = round(nclaims / npapers, 3) if npapers else 0.0
        query_yield.append({
            "query": (q or "")[:120],
            "papers": npapers,
            "claims": nclaims,
            "claims_per_paper": cpp,
        })

    return {
        "paradigm_coverage_count": len(paradigm_counts),
        "paradigm_distribution": paradigm_distribution,
        "paradigm_distribution_gini": _gini(paradigm_counts),
        "query_yield": query_yield,
    }


def _collect_failure_modes(cur, hours: int) -> dict:
    """Sigma submission errors + theorem-kill-path mismatch canary.

    The kill_path mismatch tracker is the v0.5 concern flagged by James
    2026-05-18: theorem-class claims with kill_paths containing
    'counterexample' are potentially inappropriately killable, since a
    theorem with a sound published proof can't be killed by counterexample —
    only by exposing a flaw in the proof or its hypotheses.
    """
    cur.execute("""
        SELECT COUNT(*) FROM agora.clio_claim_extractions
        WHERE extracted_at > NOW() - (%s || ' hours')::INTERVAL
          AND sigma_submission_error IS NOT NULL
    """, (str(hours),))
    sigma_errors = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM agora.clio_claim_extractions
        WHERE extracted_at > NOW() - (%s || ' hours')::INTERVAL
          AND sigma_claim_id IS NOT NULL
    """, (str(hours),))
    sigma_submitted = cur.fetchone()[0]

    # Theorem-kill-path canary: theorems whose Sigma kill_path mentions
    # 'counterexample'. Requires a join into sigma.claims.
    cur.execute("""
        SELECT COUNT(*) FROM agora.clio_claim_extractions e
        JOIN sigma.claims c ON c.id = e.sigma_claim_id
        WHERE e.extracted_at > NOW() - (%s || ' hours')::INTERVAL
          AND e.claim_type = 'theorem'
          AND lower(c.kill_path) LIKE '%%counterexample%%'
    """, (str(hours),))
    theorem_with_counterexample_kill = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM agora.clio_claim_extractions
        WHERE extracted_at > NOW() - (%s || ' hours')::INTERVAL
          AND claim_type = 'theorem'
          AND sigma_claim_id IS NOT NULL
    """, (str(hours),))
    theorem_submitted = cur.fetchone()[0]

    return {
        "sigma_submission_error_count": sigma_errors,
        "sigma_submission_error_pct": _pct(sigma_errors, sigma_submitted + sigma_errors),
        "theorem_claims_submitted_24h": theorem_submitted,
        "theorem_with_counterexample_kill_path_pct":
            _pct(theorem_with_counterexample_kill, theorem_submitted),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_quality_snapshot(window_hours: int = 24, connect_fn: Optional[Callable] = None) -> dict:
    """Compute a quality snapshot. connect_fn is injectable for tests."""
    connect_fn = connect_fn or (agora_persist._connect if HAS_PG else None)
    if connect_fn is None:
        raise RuntimeError("agora_persist unavailable")
    snapshot = {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "window_hours": window_hours,
    }
    with connect_fn() as conn:
        with conn.cursor() as cur:
            snapshot.update(_collect_volume(cur, window_hours))
            snapshot.update(_collect_yield(cur, window_hours))
            snapshot.update(_collect_specificity(cur, window_hours))
            snapshot.update(_collect_diversity(cur, window_hours))
            snapshot.update(_collect_failure_modes(cur, window_hours))
    return snapshot


def update_heartbeat_quality(snapshot: dict, agent_name: str = "Clio", machine: str = "M1") -> bool:
    """Merge the quality snapshot's headline numbers into Clio's heartbeat.

    Reads current status_json (if any), adds a 'quality' sub-object with the
    headline metrics, and writes back via write_heartbeat.
    """
    if not HAS_PG:
        return False
    existing = agora_persist.read_agent(agent_name) or {}
    sj = existing.get("status_json") or {}
    if isinstance(sj, str):
        try:
            sj = json.loads(sj)
        except json.JSONDecodeError:
            sj = {}
    headline = {
        "computed_at": snapshot.get("computed_at"),
        "window_hours": snapshot.get("window_hours"),
        "papers_24h": snapshot.get("papers_24h"),
        "claims_extracted_24h": snapshot.get("claims_extracted_24h"),
        "claims_submitted_24h": snapshot.get("claims_submitted_24h"),
        "papers_with_zero_claims_pct": snapshot.get("papers_with_zero_claims_pct"),
        "claims_per_paper_mean": snapshot.get("claims_per_paper_mean"),
        "paradigm_hint_pct": snapshot.get("paradigm_hint_pct"),
        "paradigm_coverage_count": snapshot.get("paradigm_coverage_count"),
        "confidence_mean": snapshot.get("confidence_mean"),
        "confidence_p50": snapshot.get("confidence_p50"),
        "falsifiable_pct": snapshot.get("falsifiable_pct"),
        "sigma_submission_error_pct": snapshot.get("sigma_submission_error_pct"),
        "theorem_with_counterexample_kill_path_pct":
            snapshot.get("theorem_with_counterexample_kill_path_pct"),
    }
    sj["quality"] = headline
    return agora_persist.write_heartbeat(
        agent_name=agent_name, machine=machine, status="online", status_json=sj,
    )


def render_snapshot(snapshot: dict) -> str:
    """Pretty-print a snapshot as multi-line markdown-ish text. Pure."""
    lines = [
        f"# Clio quality snapshot — {snapshot.get('computed_at', '?')}",
        f"window: last {snapshot.get('window_hours', '?')}h",
        "",
        "## Volume",
        f"  papers_24h:          {snapshot.get('papers_24h', 0)}",
        f"  claims_extracted_24h: {snapshot.get('claims_extracted_24h', 0)}",
        f"  claims_submitted_24h: {snapshot.get('claims_submitted_24h', 0)}",
        "",
        "## Yield",
        f"  claims_per_paper_mean: {snapshot.get('claims_per_paper_mean', 'n/a')}",
        f"  claims_per_paper_p25/p50/p75: {snapshot.get('claims_per_paper_p25', '-')} / {snapshot.get('claims_per_paper_p50', '-')} / {snapshot.get('claims_per_paper_p75', '-')}",
        f"  papers_with_zero_claims_pct: {snapshot.get('papers_with_zero_claims_pct', 0)}%",
        "",
        "## Specificity",
        f"  claim_type_known_pct: {snapshot.get('claim_type_known_pct', 0)}%",
        f"  paradigm_hint_pct: {snapshot.get('paradigm_hint_pct', 0)}%",
        f"  open_problem_hint_pct: {snapshot.get('open_problem_hint_pct', 0)}%",
        f"  falsifiable_pct: {snapshot.get('falsifiable_pct', 0)}%",
        f"  confidence_mean: {snapshot.get('confidence_mean', 'n/a')}",
        f"  confidence_p25/p50/p75: {snapshot.get('confidence_p25', '-')} / {snapshot.get('confidence_p50', '-')} / {snapshot.get('confidence_p75', '-')}",
        f"  claim_text_length_mean: {snapshot.get('claim_text_length_mean', 'n/a')}",
        "",
        "## Diversity",
        f"  paradigm_coverage_count: {snapshot.get('paradigm_coverage_count', 0)} / 30",
        f"  paradigm_distribution_gini: {snapshot.get('paradigm_distribution_gini', 'n/a')}",
        f"  paradigm_distribution (top): {dict(list((snapshot.get('paradigm_distribution') or {}).items())[:6])}",
        "",
        "## Failure modes",
        f"  sigma_submission_error_count: {snapshot.get('sigma_submission_error_count', 0)}",
        f"  sigma_submission_error_pct: {snapshot.get('sigma_submission_error_pct', 0)}%",
        f"  theorem_claims_submitted_24h: {snapshot.get('theorem_claims_submitted_24h', 0)}",
        f"  theorem_with_counterexample_kill_path_pct: {snapshot.get('theorem_with_counterexample_kill_path_pct', 0)}%  (canary for kill-path mismatch)",
    ]
    qy = snapshot.get("query_yield") or []
    if qy:
        lines.append("")
        lines.append("## Query yield (top 10)")
        for q in qy[:10]:
            lines.append(f"  papers={q['papers']:>3} claims={q['claims']:>3} cpp={q['claims_per_paper']:>5}  {q['query'][:90]}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Clio v0.4 — quality observability")
    parser.add_argument("--snapshot", action="store_true", help="Compute + persist + heartbeat")
    parser.add_argument("--show", action="store_true", help="Render latest snapshot")
    parser.add_argument("--show-history", type=int, default=0, help="Render last N snapshots (summary)")
    parser.add_argument("--window", type=int, default=24, help="Window in hours (default 24)")
    args = parser.parse_args()

    if not HAS_PG:
        log.error("agora_persist unavailable")
        return 1

    if args.snapshot:
        snap = compute_quality_snapshot(window_hours=args.window)
        sid = agora_persist.write_clio_quality_snapshot(args.window, snap)
        ok = update_heartbeat_quality(snap)
        log.info(f"snapshot id={sid} persisted; heartbeat updated={ok}")
        print(render_snapshot(snap))
        return 0

    if args.show:
        snaps = agora_persist.read_recent_clio_quality_snapshots(limit=1)
        if not snaps:
            print("(no snapshots yet — run --snapshot first)")
            return 0
        m = snaps[0]["metrics"]
        if isinstance(m, str):
            m = json.loads(m)
        print(render_snapshot(m))
        return 0

    if args.show_history:
        snaps = agora_persist.read_recent_clio_quality_snapshots(limit=args.show_history)
        for s in snaps:
            m = s["metrics"]
            if isinstance(m, str):
                m = json.loads(m)
            print(f"{s['snapshot_at']}  papers={m.get('papers_24h', 0):>3}  "
                  f"claims={m.get('claims_extracted_24h', 0):>3}  "
                  f"submitted={m.get('claims_submitted_24h', 0):>3}  "
                  f"paradigm_cov={m.get('paradigm_coverage_count', 0):>2}  "
                  f"conf_p50={m.get('confidence_p50', '---')}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
