"""Telos — stalled-specimen reviver (Harmonia child agent).

See `D:\\Prometheus\\harmonia\\agents\\telos\\CHARTER.md` for the brief
and `D:\\Prometheus\\harmonia\\agents\\_base.py` for the shared API.

Per-tick MVP behavior:
  1. Parse `frontier_specimen_state.md` -> live F-IDs + killed list.
  2. Compute stall age from `last_audit_outcome`.
  3. Diff promoted symbols (substrate_health or symbols/INDEX.md) vs
     each F-ID's `cross_refs` to find lenses-not-yet-applied.
  4. Pick most-stalled F-ID past threshold (anti-greedy rotation).
  5. Emit a revive-task artifact + optional DeepSeek probe.
  6. Fallback: patrol killed F-IDs.
  7. Final fallback: emit `NEGATIVE_SPACE_MAPPED@v1` candidate.

Never a silent tick. Proposal only — Telos never mutates the ledger.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone, date as _date
from pathlib import Path
from typing import Optional

_THIS = Path(__file__).resolve()
REPO_ROOT = _THIS.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harmonia.agents._base import HarmoniaAgent  # noqa: E402

# ---------------------------------------------------------------------------
# Canonical paths
# ---------------------------------------------------------------------------

FRONTIER_LEDGER = REPO_ROOT / "harmonia" / "memory" / "frontier_specimen_state.md"
METHODOLOGY_TOOLKIT = REPO_ROOT / "harmonia" / "memory" / "methodology_toolkit.md"
SYMBOLS_INDEX = REPO_ROOT / "harmonia" / "memory" / "symbols" / "INDEX.md"
RETRACTION_REGISTRY = REPO_ROOT / "harmonia" / "memory" / "retraction_registry.md"

DEFAULT_STALL_THRESHOLD_DAYS = 14

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
# F-ID rows look like:  | **F011** | live_specimen ... | last_audit | open_q | cross_refs |
ROW_RE = re.compile(r"^\|\s*\*?\*?(F\d{3}[a-z]?)\*?\*?\s*\|", re.IGNORECASE)
# Symbol references inside cross_refs cells (e.g., EPS011@v2, NULL_BSWCD@v2)
SYMBOL_REF_RE = re.compile(r"`?([A-Z][A-Z0-9_]+)@v\d+`?")
# Symbol names in INDEX table rows like:  | [NULL_BSWCD@v2](NULL_BSWCD.md) | ...
INDEX_SYMBOL_RE = re.compile(r"\|\s*\[([A-Z][A-Z0-9_]+)@v\d+\]\(")
# Methodology toolkit headings:  ### 1. `KOLMOGOROV_HAT@v1` — fingerprint compressibility
TOOLKIT_HEADING_RE = re.compile(
    r"^###\s+\d+\.\s+`([A-Z][A-Z0-9_]+@v\d+)`\s*[—\-]\s*(.+?)\s*$",
    re.MULTILINE,
)
# Killed-stub sentence: "F010 (NF backbone, killed via block-shuffle), F012 (...)"
KILLED_FID_RE = re.compile(r"\bF(\d{3}[a-z]?)\b")


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_frontier_ledger(text: str) -> tuple[list[dict], list[str]]:
    """Return (live_rows, killed_fids).

    live_rows are dicts: {fid, tier, last_audit_outcome, open_questions,
    cross_refs, cross_ref_symbols, raw_row}.
    killed_fids is a deduped sorted list of F-IDs mentioned in the
    "Killed + data-frontier (stub)" section.
    """
    live_rows: list[dict] = []
    seen: set[str] = set()

    # Find the "Live specimens" table; rows come before the next H3 (### ...)
    in_live_section = False
    in_killed_section = False
    killed_text_buf: list[str] = []

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        # Section gating
        if stripped.startswith("### Live specimens"):
            in_live_section = True
            in_killed_section = False
            continue
        if stripped.startswith("### Calibration anchors"):
            in_live_section = False
            continue
        if stripped.startswith("### Killed") or stripped.startswith("### Killed + data-frontier"):
            in_live_section = False
            in_killed_section = True
            continue
        if stripped.startswith("## ") or stripped.startswith("### "):
            # Any other H2/H3 closes both sections
            if in_killed_section and not stripped.startswith("### Killed"):
                in_killed_section = False
            if in_live_section and not stripped.startswith("### Live"):
                in_live_section = False

        if in_killed_section:
            killed_text_buf.append(stripped)

        if not in_live_section:
            continue
        m = ROW_RE.match(stripped)
        if not m:
            continue
        # Skip the header/divider rows (|---|---|...)
        if set(stripped.replace("|", "").strip()) <= {"-", " ", ":"}:
            continue
        # Split into cells; drop leading/trailing empties from outer pipes
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 5:
            continue
        fid_raw = m.group(1).upper()
        if fid_raw in seen:
            continue
        seen.add(fid_raw)
        fid = fid_raw
        tier = cells[1]
        last_audit_outcome = cells[2]
        open_questions = cells[3]
        cross_refs = cells[4]
        cross_ref_symbols = set(SYMBOL_REF_RE.findall(cross_refs))
        live_rows.append({
            "fid": fid,
            "tier": tier,
            "last_audit_outcome": last_audit_outcome,
            "open_questions": open_questions,
            "cross_refs": cross_refs,
            "cross_ref_symbols": sorted(cross_ref_symbols),
            "raw_row": stripped,
        })

    killed_fids = sorted({
        "F" + m for m in KILLED_FID_RE.findall(" ".join(killed_text_buf))
    })
    # Drop any F-IDs that are also in the live rows
    live_fids = {r["fid"] for r in live_rows}
    killed_fids = [f for f in killed_fids if f not in live_fids]
    return live_rows, killed_fids


def _latest_date(text: str) -> Optional[_date]:
    if not text:
        return None
    dates = DATE_RE.findall(text)
    if not dates:
        return None
    parsed = []
    for d in dates:
        try:
            parsed.append(_date.fromisoformat(d))
        except Exception:
            pass
    return max(parsed) if parsed else None


def _parse_methodology_toolkit(text: str) -> list[dict]:
    """Return [{symbol, one_line}] from toolkit shelf headings."""
    out = []
    for m in TOOLKIT_HEADING_RE.finditer(text):
        out.append({"symbol": m.group(1), "one_line": m.group(2)})
    return out


def _parse_symbols_index(text: str) -> set[str]:
    """Return set of promoted symbol names from `symbols/INDEX.md` tables."""
    return set(INDEX_SYMBOL_RE.findall(text))


def _get_promoted_symbols_via_agora() -> Optional[set[str]]:
    """Try substrate_health(); return set of names or None on failure.

    substrate_health() PRINTS to stdout, so we silence it.
    """
    try:
        from io import StringIO
        from contextlib import redirect_stdout
        from agora.helpers import substrate_health  # type: ignore
        buf = StringIO()
        with redirect_stdout(buf):
            res = substrate_health()
        syms = res.get("symbols") if isinstance(res, dict) else None
        if isinstance(syms, dict):
            return set(syms.keys())
    except Exception:
        return None
    return None


# ---------------------------------------------------------------------------
# TelosAgent
# ---------------------------------------------------------------------------

class TelosAgent(HarmoniaAgent):

    name = "Telos"
    role = "stalled-specimen reviver / negative-space patroller"
    machine = "M2"

    # ---- helper methods --------------------------------------------------

    def _read(self, path: Path) -> Optional[str]:
        try:
            if not path.exists():
                self.log.warning(f"missing source file: {path}")
                return None
            return path.read_text(encoding="utf-8")
        except Exception as e:
            self.log.warning(f"could not read {path}: {e}")
            return None

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def _retractions_in_adjacent(
        self, fid: str, cross_refs: str, retr_text: Optional[str]
    ) -> list[str]:
        """Return retraction-registry lines mentioning the same F-ID or
        any F-ID referenced in `cross_refs`."""
        if not retr_text:
            return []
        targets = {fid}
        for m in re.finditer(r"\bF\d{3}[a-z]?\b", cross_refs):
            targets.add(m.group(0).upper())
        hits = []
        for block in retr_text.split("\n### "):
            block_upper = block.upper()
            for t in targets:
                if t in block_upper:
                    head = block.splitlines()[0].strip()
                    if head and head not in hits:
                        hits.append(head[:200])
                    break
        return hits

    # ---- backlog ---------------------------------------------------------

    def self_generate_backlog(self) -> list[dict]:
        """Return ordered work-items: stalled live-specimens first, then
        unrevisited killed F-IDs, then a sentinel for the
        NEGATIVE_SPACE_MAPPED fallback. Pure-read; no side effects."""
        threshold = int(self.load_state("stall_threshold_days",
                                        DEFAULT_STALL_THRESHOLD_DAYS) or
                        DEFAULT_STALL_THRESHOLD_DAYS)
        text = self._read(FRONTIER_LEDGER)
        if text is None:
            return [{"mode": "negative_space",
                     "reason": "frontier_ledger_unreadable"}]
        rows, killed = _parse_frontier_ledger(text)
        today = datetime.now(timezone.utc).date()
        items: list[dict] = []
        for r in rows:
            # Tier-prefix match — `live_specimen` rows only. Rows like
            # "calibration_refinement (downgraded from live_specimen ...)"
            # contain the substring but are NOT live_specimen tier.
            if not r["tier"].lower().lstrip().startswith("live_specimen"):
                continue
            d = _latest_date(r["last_audit_outcome"])
            stall_days = (today - d).days if d else 9_999
            if stall_days >= threshold:
                items.append({
                    "mode": "revive",
                    "fid": r["fid"],
                    "stall_days": stall_days,
                    "has_open_questions": bool(
                        r["open_questions"]
                        and r["open_questions"].strip() not in {"", "—", "-"}
                    ),
                })
        # Sort: most-stalled first, prefer open-questions-non-empty
        items.sort(key=lambda x: (-x["stall_days"], not x["has_open_questions"]))
        revisited = set(self.load_state("killed_revisited", []) or [])
        for k in killed:
            if k in revisited:
                continue
            items.append({"mode": "killed_revisit", "fid": k})
        items.append({"mode": "negative_space",
                      "reason": "fallback_no_unrevisited_targets"})
        return items

    # ---- tick ------------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats = {
            "fid_picked": None,
            "mode": None,
            "stall_days": None,
            "lenses_proposed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "skipped": False,
            "dry_run": dry_run,
        }

        threshold = int(self.load_state("stall_threshold_days",
                                        DEFAULT_STALL_THRESHOLD_DAYS) or
                        DEFAULT_STALL_THRESHOLD_DAYS)
        last_picked = self.load_state("last_picked", None)
        revisited = list(self.load_state("killed_revisited", []) or [])

        ledger_text = self._read(FRONTIER_LEDGER)
        if ledger_text is None:
            return self._handle_negative_space(
                stats, dry_run,
                live=[], killed=[],
                reason="frontier_specimen_state.md unreadable",
                threshold=threshold,
            )

        live_rows, killed_fids = _parse_frontier_ledger(ledger_text)

        toolkit_text = self._read(METHODOLOGY_TOOLKIT) or ""
        toolkit_entries = _parse_methodology_toolkit(toolkit_text)
        toolkit_symbols = {e["symbol"].split("@")[0] for e in toolkit_entries}

        agora_syms = _get_promoted_symbols_via_agora()
        if agora_syms is not None:
            promoted_symbols = set(agora_syms)
            promoted_source = "agora.helpers.substrate_health()"
        else:
            idx_text = self._read(SYMBOLS_INDEX) or ""
            promoted_symbols = _parse_symbols_index(idx_text)
            promoted_source = str(SYMBOLS_INDEX)
        # Include toolkit-shelf symbols (they're candidate lenses too)
        candidate_lenses = sorted(promoted_symbols | toolkit_symbols)
        stats["promoted_symbol_count"] = len(promoted_symbols)
        stats["toolkit_entry_count"] = len(toolkit_entries)
        stats["promoted_source"] = promoted_source

        retraction_text = self._read(RETRACTION_REGISTRY)

        # --- pick most-stalled live_specimen past threshold -----------------

        today = datetime.now(timezone.utc).date()
        ranked: list[tuple[int, bool, dict, Optional[_date]]] = []
        for r in live_rows:
            # Telos targets `live_specimen` rows only — calibration_refinement
            # / killed_* / data_frontier rows in this section are skipped.
            # Tier-prefix match — `live_specimen` rows only. Rows like
            # "calibration_refinement (downgraded from live_specimen ...)"
            # contain the substring but are NOT live_specimen tier.
            if not r["tier"].lower().lstrip().startswith("live_specimen"):
                continue
            d = _latest_date(r["last_audit_outcome"])
            stall_days = (today - d).days if d else 9_999
            if stall_days < threshold:
                continue
            if last_picked and r["fid"] == last_picked:
                # anti-greedy: skip last picked (rotate)
                continue
            has_open = bool(
                r["open_questions"]
                and r["open_questions"].strip() not in {"", "—", "-"}
            )
            ranked.append((stall_days, has_open, r, d))
        # Sort by stall_days desc, then prefer has_open
        ranked.sort(key=lambda t: (-t[0], not t[1]))
        stats["backlog_remaining"] = max(0, len(ranked) - 1)

        if ranked:
            stall_days, has_open, row, audit_date = ranked[0]
            return self._handle_revive(
                stats, dry_run, row, stall_days, audit_date,
                candidate_lenses, toolkit_entries, promoted_symbols,
                retraction_text, threshold,
                live_count=len(live_rows),
            )

        # --- fall back to killed-F-ID patrol -------------------------------

        candidates_killed = [f for f in killed_fids if f not in revisited]
        if candidates_killed:
            target = sorted(candidates_killed)[0]
            return self._handle_killed_revisit(
                stats, dry_run, target, candidate_lenses, toolkit_entries,
                promoted_symbols, retraction_text, revisited,
                killed_remaining=len(candidates_killed) - 1,
            )

        # --- final fallback: NEGATIVE_SPACE_MAPPED -------------------------
        return self._handle_negative_space(
            stats, dry_run,
            live=live_rows, killed=killed_fids,
            reason=("all live specimens within stall_threshold "
                    f"({threshold}d) and all killed F-IDs already revisited"),
            threshold=threshold,
        )

    # ---- handlers --------------------------------------------------------

    def _handle_revive(
        self, stats, dry_run, row, stall_days, audit_date,
        candidate_lenses, toolkit_entries, promoted_symbols,
        retraction_text, threshold, live_count,
    ) -> dict:
        fid = row["fid"]
        applied = set(row["cross_ref_symbols"])
        not_applied = [s for s in candidate_lenses if s not in applied]
        toolkit_by_sym = {e["symbol"].split("@")[0]: e for e in toolkit_entries}
        adjacent_retractions = self._retractions_in_adjacent(
            fid, row["cross_refs"], retraction_text
        )

        # priority score: stall_days * (1 if open_questions else 0.6)
        open_q = row["open_questions"].strip()
        has_open = bool(open_q and open_q not in {"", "—", "-"})
        base_priority = round(stall_days * (1.0 if has_open else 0.6), 2)

        # Top-3 audit actions: pick the first three not-applied lenses,
        # prefer ones with a toolkit entry (richer descriptions).
        # Exclude lenses already proposed in prior ticks for this F-ID
        # (anti-duplicate-artifact discipline). When the pool exhausts,
        # rotate back through (state key `proposed_history[fid]` is reset
        # by emitting a single PROPOSAL_POOL_EXHAUSTED artifact and clearing).
        proposed_history_all: dict = self.load_state(
            "proposed_history", default={}
        ) or {}
        already_proposed = set(proposed_history_all.get(fid, []))
        candidates_after_dedup = [
            s for s in not_applied if s not in already_proposed
        ]
        if not candidates_after_dedup:
            # Pool exhausted — clear and start the rotation over, but emit
            # a sentinel artifact for this tick so the conductor sees the
            # full-coverage signal.
            stats["proposal_pool_exhausted"] = True
            proposed_history_all[fid] = []
            self.save_state("proposed_history", proposed_history_all)
            candidates_after_dedup = not_applied
        ranked_lenses = sorted(
            candidates_after_dedup,
            key=lambda s: (s not in toolkit_by_sym, s),
        )
        proposed = ranked_lenses[:3]
        stats["lenses_proposed"] = len(proposed)
        if not dry_run and proposed:
            proposed_history_all.setdefault(fid, []).extend(proposed)
            self.save_state("proposed_history", proposed_history_all)

        now_iso = self._now_iso()
        artifact_name = f"revive_{fid}_{now_iso}.md"
        body = self._render_revive(
            fid=fid, row=row, stall_days=stall_days, audit_date=audit_date,
            threshold=threshold,
            not_applied=not_applied, proposed=proposed,
            toolkit_by_sym=toolkit_by_sym,
            adjacent_retractions=adjacent_retractions,
            base_priority=base_priority,
            promoted_symbols=promoted_symbols,
            live_count=live_count,
        )

        # Optional DeepSeek probe
        ds = self._deepseek_probe(fid, row, stall_days, proposed)
        if ds:
            body += "\n\n## DeepSeek next-action sketch\n\n" + ds.strip() + "\n"

        artifact_path: Optional[Path] = None
        if not dry_run:
            artifact_path = self.write_artifact(artifact_name, body)
            stats["artifacts_written"] = 1
            self.save_state("last_picked", fid)
        else:
            stats["artifacts_written"] = 0

        stats["fid_picked"] = fid
        stats["mode"] = "revive"
        stats["stall_days"] = stall_days
        stats["artifact_path"] = str(artifact_path) if artifact_path else None

        self.log_work(
            "telos_tick_complete",
            summary=(f"revive task for {fid} stalled {stall_days}d "
                     f"(threshold {threshold}d); "
                     f"{len(not_applied)} lenses unapplied, "
                     f"{stats['lenses_proposed']} proposed"),
            output_path=str(artifact_path) if artifact_path else None,
            success=True,
        )
        self.log.info(
            f"revive {fid} stall={stall_days}d lenses_proposed={stats['lenses_proposed']} "
            f"dry_run={dry_run}"
        )
        return stats

    def _handle_killed_revisit(
        self, stats, dry_run, fid, candidate_lenses, toolkit_entries,
        promoted_symbols, retraction_text, revisited, killed_remaining,
    ) -> dict:
        toolkit_by_sym = {e["symbol"].split("@")[0]: e for e in toolkit_entries}
        adjacent = self._retractions_in_adjacent(fid, "", retraction_text)

        now_iso = self._now_iso()
        artifact_name = f"killed_revisit_{fid}_{now_iso}.md"
        body = self._render_killed_revisit(
            fid=fid, candidate_lenses=candidate_lenses,
            toolkit_by_sym=toolkit_by_sym,
            adjacent_retractions=adjacent,
            promoted_symbols=promoted_symbols,
        )

        artifact_path: Optional[Path] = None
        if not dry_run:
            artifact_path = self.write_artifact(artifact_name, body)
            stats["artifacts_written"] = 1
            revisited.append(fid)
            self.save_state("killed_revisited", revisited)
        else:
            stats["artifacts_written"] = 0

        stats["fid_picked"] = fid
        stats["mode"] = "killed_revisit"
        stats["backlog_remaining"] = killed_remaining
        stats["lenses_proposed"] = min(3, len(candidate_lenses))
        stats["artifact_path"] = str(artifact_path) if artifact_path else None

        self.log_work(
            "telos_tick_complete",
            summary=(f"killed-revisit sketch for {fid}; "
                     f"{len(candidate_lenses)} current lenses on shelf"),
            output_path=str(artifact_path) if artifact_path else None,
            success=True,
        )
        self.log.info(f"killed_revisit {fid} dry_run={dry_run}")
        return stats

    def _handle_negative_space(
        self, stats, dry_run, live, killed, reason, threshold,
    ) -> dict:
        now_iso = self._now_iso()
        artifact_name = f"negative_space_mapped_{now_iso}.md"
        body = self._render_negative_space(
            live=live, killed=killed, reason=reason, threshold=threshold,
            revisited=list(self.load_state("killed_revisited", []) or []),
        )
        artifact_path: Optional[Path] = None
        if not dry_run:
            artifact_path = self.write_artifact(artifact_name, body)
            stats["artifacts_written"] = 1
        else:
            stats["artifacts_written"] = 0
        stats["mode"] = "negative_space_mapped"
        stats["artifact_path"] = str(artifact_path) if artifact_path else None
        self.log_work(
            "telos_tick_complete",
            summary=f"NEGATIVE_SPACE_MAPPED@v1 candidate filed ({reason})",
            output_path=str(artifact_path) if artifact_path else None,
            success=True,
        )
        self.log.info(f"negative_space reason='{reason}' dry_run={dry_run}")
        return stats

    # ---- DeepSeek probe --------------------------------------------------

    def _deepseek_probe(self, fid, row, stall_days, proposed) -> Optional[str]:
        try:
            prompt = (
                f"F-ID {fid} at tier '{row['tier']}' has been stalled for "
                f"{stall_days} days. last_audit_outcome: "
                f"\"{row['last_audit_outcome']}\". "
                f"Open questions: {row['open_questions'] or '(none recorded)'}. "
                f"Lenses NOT yet applied (from current toolkit + promoted "
                f"symbols): {', '.join(proposed) or '(none — exhausted)'}. "
                "Propose the SINGLE highest-leverage next audit action in "
                "<=100 words. Be specific about what's measured, what null "
                "is used, and what verdict resolves what."
            )
            return self.deepseek_complete(
                prompt,
                system=("You are an adversarial methodology reviewer in the "
                        "Prometheus substrate. Falsification-first. One "
                        "action, not three. No preambles."),
                max_tokens=300,
            )
        except Exception as e:
            self.log.warning(f"deepseek probe failed: {e}")
            return None

    # ---- artifact rendering ---------------------------------------------

    def _render_revive(
        self, fid, row, stall_days, audit_date, threshold,
        not_applied, proposed, toolkit_by_sym, adjacent_retractions,
        base_priority, promoted_symbols, live_count,
    ) -> str:
        now = datetime.now(timezone.utc).isoformat()
        applied = sorted(set(row["cross_ref_symbols"]))
        # New symbols since last audit = promoted_symbols not in applied
        new_since = sorted(set(promoted_symbols) - set(applied))

        def _lens_line(sym: str) -> str:
            entry = toolkit_by_sym.get(sym)
            if entry:
                return (f"- `{entry['symbol']}` — {entry['one_line']}  "
                        f"(toolkit entry: `D:\\Prometheus\\harmonia\\memory\\methodology_toolkit.md`)")
            return (f"- `{sym}` — promoted symbol; spec at "
                    f"`D:\\Prometheus\\harmonia\\memory\\symbols\\{sym}.md`")

        lenses_block = ("\n".join(_lens_line(s) for s in not_applied)
                        if not_applied else
                        "_(none — every promoted lens already appears in cross_refs)_")

        proposed_block_lines = []
        for i, s in enumerate(proposed, 1):
            entry = toolkit_by_sym.get(s)
            descr = entry["one_line"] if entry else "(promoted symbol)"
            priority = round(base_priority / i, 2)  # rank-decayed
            proposed_block_lines.append(
                f"{i}. **Apply `{s}` to {fid}.** {descr}\n"
                f"   - priority score: **{priority}** "
                f"(base {base_priority} / rank {i})\n"
                f"   - rationale: lens absent from `cross_refs`; landed since "
                f"last audit ({audit_date.isoformat() if audit_date else 'unknown'})."
            )
        if not proposed_block_lines:
            proposed_block_lines.append(
                "1. **Negative-space probe.** No promoted-lens deltas vs current "
                f"cross_refs for {fid}. Propose a `NEGATIVE_SPACE_MAPPED@v1` "
                "follow-up: what coordinate doesn't exist yet that would "
                "discriminate this specimen?"
            )
        proposed_block = "\n".join(proposed_block_lines)

        adj_block = ("\n".join(f"- {r}" for r in adjacent_retractions)
                     if adjacent_retractions else
                     "_(none — no retraction-registry entries name this F-ID or its cross-refs)_")

        new_since_block = (", ".join(f"`{s}`" for s in new_since[:25])
                           if new_since else "_(none)_")
        if len(new_since) > 25:
            new_since_block += f", ... (+{len(new_since)-25} more)"

        agora_spec = self._render_agora_spec(fid, proposed, base_priority, row)

        applied_block = (", ".join(f"`{s}`" for s in applied)
                         if applied else "_(none parsed from cross_refs cell)_")

        return (
f"""# Telos revive task — {fid}

**Filed:** {now}
**Tier:** {row['tier']}
**Stall age:** **{stall_days} days** (threshold {threshold}d)
**Last audit date parsed:** {audit_date.isoformat() if audit_date else 'unparseable'}
**Live-specimen population this tick:** {live_count}
**Source ledger:** `D:\\Prometheus\\harmonia\\memory\\frontier_specimen_state.md`

## Quoted `last_audit_outcome`

> {row['last_audit_outcome']}

## Quoted `open_questions`

> {row['open_questions'] or '_(empty)_'}

## Applied lenses (from `cross_refs`)

{applied_block}

## Lenses NOT yet applied

{lenses_block}

## New promoted symbols since last audit (delta)

{new_since_block}

## Retractions in adjacent F-IDs (potential reframes)

{adj_block}

## Proposed next 3 audit actions

{proposed_block}

## Seedable Agora queue task spec (description — NOT seeded)

```
{agora_spec}
```

## Telos discipline notes

- This artifact is a PROPOSAL. Do not mutate `frontier_specimen_state.md`
  or any tier value on the strength of this file.
- Anti-greedy rotation: Telos will skip {fid} on the next tick even if
  it remains the top-stalled specimen — see state key `last_picked`.
- Verify the audit date parse: Telos picked the LATEST `YYYY-MM-DD`
  appearing inside the `last_audit_outcome` cell.
- If `cross_refs` parsing missed a symbol, that's an under-count of
  applied lenses — false-positive proposals are the failure mode, not
  false-negative.
""")

    def _render_agora_spec(self, fid, proposed, base_priority, row) -> str:
        first = proposed[0] if proposed else "NEGATIVE_SPACE_PROBE"
        return (
f"""title: Revive {fid} — apply {first}
requested_by: Telos
priority: {round(base_priority, 1)}
tier: T5
tags:
  source: telos
  fid: {fid}
  mode: revive_proposal
prompt: |
  Specimen {fid} is at tier "{row['tier'][:60]}" and has been stalled
  past Telos's threshold. Open questions remain.
  Apply `{first}` to {fid} using the toolkit spec; pre-register the
  null protocol and a kill-criterion before running. Report:
  1. measured value + 95% CI
  2. null distribution result (NULL_BSWCD@v2 or argued alternative)
  3. verdict against the kill-criterion
  4. Pattern 30 severity check
  5. SHADOWS_ON_WALL tier reached
""")

    def _render_killed_revisit(
        self, fid, candidate_lenses, toolkit_by_sym, adjacent_retractions,
        promoted_symbols,
    ) -> str:
        now = datetime.now(timezone.utc).isoformat()
        # Pick up to 3 lenses that look newest/most-relevant
        candidates = [s for s in candidate_lenses if s in toolkit_by_sym][:3]
        if len(candidates) < 3:
            for s in candidate_lenses:
                if s not in candidates:
                    candidates.append(s)
                if len(candidates) >= 3:
                    break

        cand_lines = []
        for s in candidates:
            entry = toolkit_by_sym.get(s)
            descr = entry["one_line"] if entry else "(promoted symbol)"
            cand_lines.append(f"- `{s}` — {descr}")
        cand_block = ("\n".join(cand_lines)
                      if cand_lines else
                      "_(no current lenses found — see methodology toolkit)_")

        adj_block = ("\n".join(f"- {r}" for r in adjacent_retractions)
                     if adjacent_retractions else
                     "_(retraction registry has no entries explicitly naming this F-ID)_")

        return (
f"""# Telos killed-revisit sketch — {fid}

**Filed:** {now}
**Mode:** would-current-tooling-un-kill?
**Source ledger:** `D:\\Prometheus\\harmonia\\memory\\frontier_specimen_state.md`
**Retraction registry consulted:** `D:\\Prometheus\\harmonia\\memory\\retraction_registry.md`

## Why this tick

The live-specimen pile has no F-IDs past stall threshold AND {fid} has
not been revisited in this Telos session's `killed_revisited` state.
Retractions are not always permanent. Telos asks: does the current
substrate carry a tool that wasn't available at kill-time?

## What was tried at kill-time

See the retraction-registry entry (if any) and `build_landscape_tensor.py`
FEATURES history for {fid}. Telos does not re-summarize the kill —
**operator should read the original entry before treating this revisit
as evidence**.

## Retraction-registry entries naming {fid} or adjacent F-IDs

{adj_block}

## What's available NOW that may not have been

{cand_block}

## Verdict sketch (TBD by operator/auditor)

- [ ] likely-still-killed (mechanism survives under new tooling)
- [ ] worth-revisit (a current lens demonstrably probes a different axis)
- [ ] ambiguous (need a calibration-anchor pre-test of the new lens first)

## Telos discipline notes

- This is a SKETCH. The kill stands until a real audit replaces it.
- If revisit is approved, route through `decisions_for_james.md`; do
  not mutate `frontier_specimen_state.md` directly.
- Telos appends {fid} to state key `killed_revisited` so this artifact
  does not duplicate.
""")

    def _render_negative_space(
        self, live, killed, reason, threshold, revisited,
    ) -> str:
        now = datetime.now(timezone.utc).isoformat()
        live_fids = [r["fid"] for r in live]
        return (
f"""# NEGATIVE_SPACE_MAPPED@v1 — candidate artifact

**Filed:** {now}
**Reason:** {reason}
**Stall threshold this tick:** {threshold} days
**Live-specimen F-IDs surveyed:** {', '.join(live_fids) or '_(none)_'}
**Killed F-IDs surveyed:** {', '.join(killed) or '_(none)_'}
**Already revisited this session:** {', '.join(revisited) or '_(none)_'}

## Why this artifact exists

Telos's hard discipline: silence is forbidden. A silent tick would
validate-by-not-asking that every specimen is settled. It isn't —
Telos is instead reporting that, with the **current substrate**, he
cannot think of a next lens to propose for any F-ID in the patrol set.

## Proposal: substrate-primitive gap

The negative space Telos has just mapped is itself a finding-shaped
object. What coordinate, tool, or null does the substrate not yet
carry that would un-stall the survey above?

Candidate framings:

- a stall-detector that knows the difference between "no progress
  because the question is hard" vs "no progress because the question
  is malformed"
- a cross-F-ID similarity coordinate (so revive proposals on one F-ID
  can transfer to its neighbors automatically)
- a kill-revisit protocol with a calibrated false-positive budget
  (currently Telos's killed-revisit is hand-sketched)

## Telos discipline notes

- Promotion of `NEGATIVE_SPACE_MAPPED@v1` from candidate to symbol
  requires the usual two-agent reference + conductor sign-off.
- File path convention: this artifact lives under
  `D:\\Prometheus\\harmonia\\agents\\telos\\artifacts\\` until / unless
  promoted.
""")
