"""
Harmonia taint-sweep watchdog.

Phase 0 deliverable (spec §6.4) for the Harmonia auto-promotion pipeline.
Spec: D:\\Prometheus\\harmonia\\agents\\AUTOPROMOTION_TARGETS.md

When an auto-promotion's outcome is recorded as one of the NEGATIVE_OUTCOMES
(`auto_retracted`, `dismissed_human`, `contradicted`), file-state restoration
is not enough. Downstream actors may have already consumed the bad state -
their state dirs, recency caches, substrate slots, and cross-swarm consumers
all need to be checked for orphaned references.

This watchdog scans the declared taint_scope on the retracted yield row and
produces a Markdown sweep report at
    D:\\Prometheus\\harmonia\\agents\\_logs\\taint_sweeps\\<yield_id>_<utc>.md
listing every hit found. Each hit is informational; remediation is the
conductor's call (not auto-executed).

CLI:
    python D:\\Prometheus\\scripts\\harmonia_taint_sweep.py --auto
    python D:\\Prometheus\\scripts\\harmonia_taint_sweep.py --yield-id y-abc123
    python D:\\Prometheus\\scripts\\harmonia_taint_sweep.py --auto --dry-run
    python D:\\Prometheus\\scripts\\harmonia_taint_sweep.py --status
    python D:\\Prometheus\\scripts\\harmonia_taint_sweep.py --smoke-test
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Make harmonia.agents._scorer importable when launched from any cwd.
_THIS_FILE = Path(__file__).resolve()
REPO_ROOT = _THIS_FILE.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harmonia.agents._scorer import (  # noqa: E402
    AGENTS_DIR,
    EVENT_TAINT_SWEEP_COMPLETE,
    EVENT_TAINT_SWEEP_STARTED,
    LOGS_DIR,
    NEGATIVE_OUTCOMES,
    YIELDS_JSONL,
    consolidate_yields,
    emit_event,
    read_yields,
)

SWEEP_DIR = LOGS_DIR / "taint_sweeps"
STATE_FILE = AGENTS_DIR / "_logs" / "taint_sweeps_completed.json"
CHARON_AGENTS_DIR = REPO_ROOT / "charon" / "agents"

# Best-effort upper bound on how many lines we'll quote in a single finding
# snippet, so a wildly large state file can't blow up the report.
MAX_SNIPPET_CHARS = 240


# ---------------------------------------------------------------------------
# Finding dataclass
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """One orphaned-reference hit produced by the sweep."""
    category: str            # readable_by_agents | downstream_slot | recency_key | cross_swarm | missing_file
    file_path: str           # absolute path under D:\Prometheus\...
    line_number: Optional[int]
    matched_token: str       # the substring we actually matched
    snippet: str             # excerpt from the file
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Sweep-state file (which yield_ids have already been swept)
# ---------------------------------------------------------------------------

def _load_swept_state() -> dict:
    if not STATE_FILE.exists():
        return {"swept": {}, "schema_version": "taint_sweeps.v1"}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[taint_sweep] state load failed: {e}", file=sys.stderr)
        return {"swept": {}, "schema_version": "taint_sweeps.v1"}


def _save_swept_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, indent=2, default=str),
        encoding="utf-8",
    )


def _mark_swept(state: dict, yield_id: str, report_path: Path, findings: int) -> None:
    state.setdefault("swept", {})[yield_id] = {
        "swept_at": datetime.now(timezone.utc).isoformat(),
        "report_path": str(report_path),
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# Building the unswept queue
# ---------------------------------------------------------------------------

def _unswept_retractions(swept_state: dict) -> list[dict]:
    """Return consolidated yield rows whose outcome is a retraction and
    which have not been swept yet."""
    all_rows = read_yields()
    if not all_rows:
        return []
    consolidated = consolidate_yields(all_rows)
    already = set(swept_state.get("swept", {}).keys())
    out = []
    for yid, row in consolidated.items():
        if row.get("outcome") not in NEGATIVE_OUTCOMES:
            continue
        if yid in already:
            continue
        out.append(row)
    return out


# ---------------------------------------------------------------------------
# Sweep primitives
# ---------------------------------------------------------------------------

def _scan_file_for_tokens(
    path: Path,
    tokens: list[str],
    category: str,
    deep_for_dir: bool = False,
) -> list[Finding]:
    """Scan a single file for any of the tokens. Returns a Finding per
    matching line. Tokens are matched as plain substrings (case-sensitive
    -- artifact paths are case-significant on POSIX and we want to flag
    near-misses as findings too)."""
    findings: list[Finding] = []
    if not path.exists():
        return findings
    if path.is_dir():
        # Caller should pass files; if a dir slipped through, recurse only
        # if deep mode was requested.
        glob_pat = "**/*.json" if deep_for_dir else "*.json"
        for sub in path.glob(glob_pat):
            findings.extend(_scan_file_for_tokens(sub, tokens, category))
        return findings
    try:
        # Read line-by-line so we can attach line numbers.
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, start=1):
                for tok in tokens:
                    if not tok:
                        continue
                    if tok in line:
                        snippet = line.rstrip("\n")
                        if len(snippet) > MAX_SNIPPET_CHARS:
                            snippet = snippet[: MAX_SNIPPET_CHARS] + "..."
                        findings.append(Finding(
                            category=category,
                            file_path=str(path),
                            line_number=lineno,
                            matched_token=tok,
                            snippet=snippet,
                        ))
                        # One Finding per (line, token) is enough; break the
                        # token loop so a line with multiple tokens still
                        # only logs once per token.
    except (OSError, UnicodeError) as e:
        findings.append(Finding(
            category=category,
            file_path=str(path),
            line_number=None,
            matched_token="<scan_error>",
            snippet=f"file scan raised {type(e).__name__}: {e}",
            note="scan_error",
        ))
    return findings


def _scan_agent_state(
    agent_name: str,
    tokens: list[str],
    deep: bool,
) -> list[Finding]:
    """Scan an agent's state dir for the tokens."""
    findings: list[Finding] = []
    state_dir = AGENTS_DIR / agent_name / "state"
    if not state_dir.exists():
        # Not an error -- the agent may not have produced state yet.
        return findings
    glob_pat = "**/*.json" if deep else "*.json"
    for f in state_dir.glob(glob_pat):
        findings.extend(_scan_file_for_tokens(f, tokens, category=f"readable_by_agents:{agent_name}"))
    return findings


def _scan_downstream_slot(slot: str, tokens: list[str]) -> list[Finding]:
    """A downstream_slot may be a relative path or absolute. Normalize to
    an absolute path under REPO_ROOT and scan."""
    path = Path(slot)
    if not path.is_absolute():
        path = REPO_ROOT / slot
    if not path.exists():
        return [Finding(
            category="downstream_slot",
            file_path=str(path),
            line_number=None,
            matched_token="<missing>",
            snippet=f"declared downstream_slot does not exist: {path}",
            note="missing_file",
        )]
    return _scan_file_for_tokens(path, tokens, category="downstream_slot")


def _scan_cross_swarm(consumer: str, tokens: list[str], deep: bool) -> list[Finding]:
    """Best-effort cross-swarm scan. Free-form consumer name like
    'Charon swarm (Stygian primary-lit surveys)'. We try to extract a
    swarm name and an optional agent name."""
    findings: list[Finding] = []
    name_lower = consumer.lower()
    if "charon" in name_lower:
        if not CHARON_AGENTS_DIR.exists():
            return [Finding(
                category="cross_swarm",
                file_path=str(CHARON_AGENTS_DIR),
                line_number=None,
                matched_token="<charon_not_present>",
                snippet=f"cross_swarm_consumer '{consumer}' declared but {CHARON_AGENTS_DIR} not present locally",
                note="cross_swarm_skipped",
            )]
        # Try to pull a parenthesized agent name out of the consumer string
        m = re.search(r"\(([^)]+)\)", consumer)
        candidates: list[Path] = []
        if m:
            inner = m.group(1).strip().lower()
            # Crude token-match against subdirs
            for sub in CHARON_AGENTS_DIR.iterdir():
                if sub.is_dir() and any(tok in sub.name.lower() for tok in inner.split()):
                    art = sub / "artifacts"
                    if art.exists():
                        candidates.append(art)
        if not candidates:
            # Scan all Charon agents as best-effort
            for sub in CHARON_AGENTS_DIR.iterdir():
                if sub.is_dir():
                    art = sub / "artifacts"
                    if art.exists():
                        candidates.append(art)
        for art_dir in candidates:
            glob_pat = "**/*" if deep else "*"
            for f in art_dir.glob(glob_pat):
                if f.is_file():
                    findings.extend(_scan_file_for_tokens(
                        f, tokens, category=f"cross_swarm:charon:{art_dir.parent.name}"
                    ))
        return findings
    # Unknown swarm
    return [Finding(
        category="cross_swarm",
        file_path="<unknown>",
        line_number=None,
        matched_token="<unrecognized_swarm>",
        snippet=f"cross_swarm_consumer '{consumer}' does not match a known swarm; skipped",
        note="cross_swarm_skipped",
    )]


# ---------------------------------------------------------------------------
# Top-level sweep for one yield
# ---------------------------------------------------------------------------

def sweep_yield(row: dict, deep: bool = False) -> tuple[list[Finding], Path]:
    """Run the full sweep for one consolidated yield row. Returns
    (findings, report_path). Caller is responsible for emitting events
    and persisting state."""
    yield_id = row.get("yield_id", "y-unknown")
    artifact_path = row.get("artifact_path") or ""
    taint_scope = row.get("taint_scope") or {}

    # Tokens we'll grep for: full artifact path, basename, yield_id.
    tokens = []
    if artifact_path:
        tokens.append(artifact_path)
        tokens.append(Path(artifact_path).name)
    tokens.append(yield_id)
    # Dedup while preserving order
    seen = set()
    tokens = [t for t in tokens if not (t in seen or seen.add(t))]

    findings: list[Finding] = []

    # (a) readable_by_agents
    for ag in taint_scope.get("readable_by_agents") or []:
        findings.extend(_scan_agent_state(ag, tokens, deep))

    # (b) downstream_slots
    for slot in taint_scope.get("downstream_slots") or []:
        findings.extend(_scan_downstream_slot(slot, tokens))

    # (c) recency_keys_written -- scan ALL harmonia agent state dirs for the key
    rec_keys = taint_scope.get("recency_keys_written") or []
    if rec_keys:
        for agent_dir in AGENTS_DIR.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith("_"):
                continue
            state_dir = agent_dir / "state"
            if not state_dir.exists():
                continue
            glob_pat = "**/*.json" if deep else "*.json"
            for f in state_dir.glob(glob_pat):
                findings.extend(_scan_file_for_tokens(
                    f, list(rec_keys),
                    category=f"recency_key:{agent_dir.name}",
                ))

    # (d) cross_swarm_consumers
    for consumer in taint_scope.get("cross_swarm_consumers") or []:
        findings.extend(_scan_cross_swarm(consumer, tokens, deep))

    # Write report
    report_path = _write_report(yield_id, row, findings)
    return findings, report_path


def _write_report(yield_id: str, row: dict, findings: list[Finding]) -> Path:
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = SWEEP_DIR / f"{yield_id}_{utc}.md"
    artifact_path = row.get("artifact_path") or "<unknown>"
    outcome = row.get("outcome") or "<unknown>"
    observed_at = row.get("outcome_observed_at") or "<unknown>"
    taint_scope = row.get("taint_scope") or {}

    lines: list[str] = []
    lines.append(f"# Taint-sweep report: {yield_id}")
    lines.append("")
    lines.append(f"- Original artifact path: `{artifact_path}`")
    lines.append(f"- Retraction outcome: `{outcome}`")
    lines.append(f"- Outcome observed at: `{observed_at}`")
    lines.append(f"- Sweep generated at: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"- Report path: `{report_path}`")
    lines.append("")
    lines.append("## Declared taint_scope")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(taint_scope, indent=2, default=str))
    lines.append("```")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    if not findings:
        lines.append("_No orphaned references found in the declared taint scope._")
    else:
        for i, f in enumerate(findings, start=1):
            lineref = f":{f.line_number}" if f.line_number is not None else ""
            lines.append(f"### Finding {i} [{f.category}]")
            lines.append(f"- File: `{f.file_path}{lineref}`")
            lines.append(f"- Matched token: `{f.matched_token}`")
            if f.note:
                lines.append(f"- Note: `{f.note}`")
            lines.append(f"- Snippet:")
            lines.append("")
            lines.append("  ```")
            lines.append(f"  {f.snippet}")
            lines.append("  ```")
            lines.append("")
    lines.append("## Verdict")
    lines.append("")
    if not findings:
        lines.append("**Clean** -- retraction is fully complete; no downstream consumers detected.")
    else:
        lines.append(f"**{len(findings)} findings require manual remediation.** "
                     "File state restoration alone does not address the consumers listed above.")
    lines.append("")
    lines.append("## Suggested remediation")
    lines.append("")
    if not findings:
        lines.append("_No remediation required._")
    else:
        lines.append("Per-finding suggestions (informational; conductor decides):")
        lines.append("")
        for i, f in enumerate(findings, start=1):
            lines.append(f"### Finding {i}")
            if f.note == "missing_file":
                lines.append(f"- Declared `{f.file_path}` does not exist. "
                             "Either fix the original taint_scope declaration or "
                             "confirm the slot was never written.")
            elif f.note == "cross_swarm_skipped":
                lines.append(f"- Cross-swarm consumer was not scanned locally. "
                             "If the consumer swarm has its own taint-sweep tool, "
                             "trigger it manually with yield_id `{0}`.".format(yield_id))
            elif f.note == "scan_error":
                lines.append(f"- Scanner raised an error reading `{f.file_path}`. "
                             "Inspect the file manually for references to "
                             f"`{Path(row.get('artifact_path') or '').name}` or `{yield_id}`.")
            elif f.category.startswith("recency_key"):
                lines.append(f"- Recency-key `{f.matched_token}` is still claimed in "
                             f"`{f.file_path}`. Manually evict that key entry so "
                             "re-fires of the same fingerprint aren't suppressed.")
            elif f.category.startswith("readable_by_agents"):
                lines.append(f"- Agent state at `{f.file_path}` still references the "
                             "retracted artifact. Re-run that agent's state-rebuild "
                             "or manually purge the stale entry.")
            elif f.category.startswith("downstream_slot"):
                lines.append(f"- Downstream slot `{f.file_path}` cites the retracted "
                             "artifact at line "
                             f"{f.line_number}. Edit the slot to remove the citation "
                             "and add a retraction note pointing to this report.")
            elif f.category.startswith("cross_swarm"):
                lines.append(f"- Cross-swarm artifact `{f.file_path}` references the "
                             "retracted yield. Cross-swarm taint-sweep is out of "
                             "v0.2 scope (spec §6.4); manual coordination required.")
            else:
                lines.append(f"- Manual inspection of `{f.file_path}` required.")
            lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def run_sweep(row: dict, deep: bool = False) -> tuple[list[Finding], Path]:
    """Run sweep + emit started/complete events. Caller persists state."""
    yield_id = row.get("yield_id", "y-unknown")
    taint_scope = row.get("taint_scope") or {}
    scope_summary = {
        "readable_by_agents": list(taint_scope.get("readable_by_agents") or []),
        "downstream_slots": list(taint_scope.get("downstream_slots") or []),
        "recency_keys_written": list(taint_scope.get("recency_keys_written") or []),
        "cross_swarm_consumers": list(taint_scope.get("cross_swarm_consumers") or []),
    }
    emit_event(
        EVENT_TAINT_SWEEP_STARTED,
        {"yield_id": yield_id, "taint_scope_summary": scope_summary, "deep_scan": deep},
        agent="taint_sweep_watchdog",
        yield_id=yield_id,
    )
    findings, report_path = sweep_yield(row, deep=deep)
    emit_event(
        EVENT_TAINT_SWEEP_COMPLETE,
        {
            "yield_id": yield_id,
            "findings_count": len(findings),
            "clean": len(findings) == 0,
            "sweep_report_path": str(report_path),
        },
        agent="taint_sweep_watchdog",
        yield_id=yield_id,
    )
    return findings, report_path


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

def _run_smoke_test() -> int:
    """Synthesize a fake retraction with a real-looking taint scope, sweep
    it, verify the report + events, then clean up. Does NOT touch the real
    yields.jsonl (uses a temp synthetic row directly)."""
    print("[smoke] starting smoke test for taint-sweep watchdog")
    syn_yield_id = f"y-smoke-{uuid.uuid4().hex[:8]}"
    syn_agent = f"smoketest_taint_agent_{uuid.uuid4().hex[:6]}"
    syn_state_dir = AGENTS_DIR / syn_agent / "state"
    syn_state_dir.mkdir(parents=True, exist_ok=True)

    # Synthetic artifact path - we won't write to it, just declare it.
    syn_artifact_rel = f"harmonia/memory/symbols/SMOKETEST_{syn_yield_id}.md"
    syn_artifact_abs = REPO_ROOT / syn_artifact_rel
    artifact_basename = syn_artifact_abs.name

    # Plant a synthetic reference inside the synthetic agent's state, so the
    # sweep is guaranteed to find SOMETHING (proves the scanner works).
    syn_state_file = syn_state_dir / "consumed_artifacts.json"
    syn_state_file.write_text(json.dumps({
        "last_consumed": str(syn_artifact_abs),
        "yield_seen": syn_yield_id,
        "recency_key": f"smoketest:{syn_agent}",
    }, indent=2), encoding="utf-8")

    # Plant a downstream-slot file with a citation too.
    syn_slot = LOGS_DIR / "smoketest_downstream_slot.md"
    syn_slot.write_text(
        f"# Smoketest downstream slot\n\nCitation: {artifact_basename}\n"
        f"(yield_id {syn_yield_id})\n",
        encoding="utf-8",
    )

    synthetic_row = {
        "yield_id": syn_yield_id,
        "agent": syn_agent,
        "artifact_path": str(syn_artifact_abs),
        "action": "auto_promoted_to_smoketest",
        "outcome": "auto_retracted",
        "outcome_observed_at": datetime.now(timezone.utc).isoformat(),
        "taint_scope": {
            "readable_by_agents": [syn_agent],
            "downstream_slots": [str(syn_slot)],
            "used_for_training": False,
            "recency_keys_written": [f"smoketest:{syn_agent}"],
            "requires_taint_sweep_on_retract": True,
            "cross_swarm_consumers": [
                "Charon swarm (Stygian primary-lit surveys)",
                "Unknown-swarm (smoke probe)",
            ],
        },
    }

    # Snapshot event count
    events_path = LOGS_DIR / "events.jsonl"
    pre_count = sum(1 for _ in open(events_path, "r", encoding="utf-8")) if events_path.exists() else 0

    try:
        findings, report_path = run_sweep(synthetic_row, deep=False)
    except Exception as e:
        print(f"[smoke] FAIL: sweep raised: {e}", file=sys.stderr)
        return 2

    post_count = sum(1 for _ in open(events_path, "r", encoding="utf-8")) if events_path.exists() else 0
    new_events = post_count - pre_count

    print(f"[smoke] report written: {report_path}")
    print(f"[smoke] findings count: {len(findings)}")
    print(f"[smoke] new events appended to events.jsonl: {new_events}")

    ok = True
    if not report_path.exists():
        print("[smoke] FAIL: report file does not exist", file=sys.stderr)
        ok = False
    if new_events < 2:
        print(f"[smoke] FAIL: expected >=2 new events, saw {new_events}", file=sys.stderr)
        ok = False
    if len(findings) < 2:
        print(f"[smoke] FAIL: expected >=2 findings (planted refs), saw {len(findings)}", file=sys.stderr)
        ok = False

    # Cleanup synthetic state and slot. Leave the report in place as evidence.
    try:
        syn_state_file.unlink()
        syn_state_dir.rmdir()
        (AGENTS_DIR / syn_agent).rmdir()
        syn_slot.unlink()
    except Exception as e:
        print(f"[smoke] cleanup warning: {e}", file=sys.stderr)

    if ok:
        print("[smoke] PASS")
        return 0
    return 1


# ---------------------------------------------------------------------------
# CLI driver
# ---------------------------------------------------------------------------

def _cmd_status() -> int:
    state = _load_swept_state()
    unswept = _unswept_retractions(state)
    print(f"Unswept retraction yields: {len(unswept)}")
    for r in unswept:
        print(f"  - {r.get('yield_id')} outcome={r.get('outcome')} agent={r.get('agent')} artifact={r.get('artifact_path')}")
    swept = state.get("swept", {})
    print(f"Previously-swept yields: {len(swept)}")
    return 0


def _cmd_auto(dry_run: bool, deep: bool) -> int:
    state = _load_swept_state()
    unswept = _unswept_retractions(state)
    if not unswept:
        print("[taint_sweep] no work: zero unswept retractions")
        return 0
    print(f"[taint_sweep] {len(unswept)} unswept retraction(s) to process (dry_run={dry_run})")
    for row in unswept:
        yid = row.get("yield_id")
        if dry_run:
            print(f"[taint_sweep] DRY: would sweep {yid} (outcome={row.get('outcome')})")
            continue
        findings, report = run_sweep(row, deep=deep)
        _mark_swept(state, yid, report, len(findings))
        _save_swept_state(state)
        print(f"[taint_sweep] swept {yid}: {len(findings)} findings -> {report}")
    return 0


def _cmd_yield(yield_id: str, dry_run: bool, deep: bool) -> int:
    all_rows = read_yields()
    consolidated = consolidate_yields(all_rows)
    row = consolidated.get(yield_id)
    if row is None:
        print(f"[taint_sweep] yield_id {yield_id} not found in {YIELDS_JSONL}", file=sys.stderr)
        return 2
    if row.get("outcome") not in NEGATIVE_OUTCOMES:
        print(f"[taint_sweep] WARNING: yield_id {yield_id} outcome is "
              f"'{row.get('outcome')}' which is not in NEGATIVE_OUTCOMES; "
              "proceeding anyway because --yield-id is manual mode")
    if dry_run:
        print(f"[taint_sweep] DRY: would sweep {yield_id}")
        return 0
    state = _load_swept_state()
    findings, report = run_sweep(row, deep=deep)
    _mark_swept(state, yield_id, report, len(findings))
    _save_swept_state(state)
    print(f"[taint_sweep] swept {yield_id}: {len(findings)} findings -> {report}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Harmonia taint-sweep watchdog (spec §6.4). "
                    "Scans declared taint_scope after a retraction for "
                    "orphaned downstream references."
    )
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--auto", action="store_true",
                     help="Scan yields.jsonl and sweep every unswept retraction.")
    grp.add_argument("--yield-id", type=str,
                     help="Sweep one specific yield_id (manual mode).")
    grp.add_argument("--status", action="store_true",
                     help="Report how many unswept retractions exist.")
    grp.add_argument("--smoke-test", action="store_true",
                     help="Synthesize a fake retraction, sweep it end-to-end, verify events fire.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would be swept; no events or files written.")
    ap.add_argument("--deep-scan", action="store_true",
                    help="Recurse into state dirs (default: depth-1 *.json only).")
    args = ap.parse_args(argv)

    if args.status:
        return _cmd_status()
    if args.smoke_test:
        return _run_smoke_test()
    if args.auto:
        return _cmd_auto(dry_run=args.dry_run, deep=args.deep_scan)
    if args.yield_id:
        return _cmd_yield(args.yield_id, dry_run=args.dry_run, deep=args.deep_scan)
    return 2


if __name__ == "__main__":
    sys.exit(main())
