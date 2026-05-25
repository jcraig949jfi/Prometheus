"""Hephaestus -- forger / composer agent (Charon swarm v0.7).

Per-tick algorithm (MVP):
  1. Scan Stygian's local kill_ledger for PROMOTED rows in the last
     7 days (Stygian PROMOTED means a v10 battery verdict that
     SURVIVED). Currently rare -- only Lehmer + BSD produce real
     verdicts -- but the count grows as loaders ship.
  2. Scan Pollux's local kill_ledger for PROMOTED rows in the last
     7 days (Pollux PROMOTED means a pair-correlation survived
     mean-spacing normalization).
  3. Read Hecate's most recent cross-generator canonical patterns
     (from her latest gradient_archaeology_*.md artifact).
  4. Compose ONE intersection-claim per tick by picking the highest-
     priority untried (Stygian, Pollux) pair and synthesizing the
     candidate-claim: "Stygian's claim X holds when restricted to
     the subset Y that Pollux's pair survived."
  5. Emit:
     a. A hephaestus/artifacts/composed_claim_*.md artifact with
        the structured claim + provenance.
     b. A kill_ledger row in Theseus shape with generator_id=
        "hephaestus", kill_pattern="hephaestus_composed_claim_pending",
        verdict="UNVERIFIED" (battery hasn't run on the composed
        claim yet).
     c. A stygian_priority queue row so Stygian picks it up next
        rotation cycle (will short-circuit with
        "stygian_hephaestus_composed_loader_pending" until a
        composed-claim loader ships in a later session).
  6. Mark the (Stygian, Pollux) pair as tried in state so we
     iterate through novel combinations.

Why this is substrate-grade and not another scanner:
- Inputs are TWO independent agents' PROMOTED verdicts (not raw
  source data the prior agents already see).
- Output is a NEW candidate-claim that didn't exist before this
  tick: "X restricted to Y." The composed claim is structurally
  more constrained than either parent claim.
- Stygian's downstream battery attack on the composed claim is the
  test of whether the composition is substantively meaningful or a
  product of pure coincidence.

Limitations of MVP:
- Only handles 2-way (Stygian + Pollux) compositions. 3-way
  (Stygian + Pollux + Hecate-canonical-pattern) deferred to v0.8.
- The "restriction" is currently a textual claim, not a loader-
  executable filter. Stygian will short-circuit until a per-
  composition loader exists. Future composer-aware Stygian loader
  could programmatically construct the restricted dataset.
- No HECATE-* or LETHE-* inputs yet (those agents don't currently
  emit PROMOTED-class rows; Lethe v2 may change this).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from charon.agents._base import CharonAgent
from charon.agents._shared_queues import stygian_priority_queue
from harmonia.agents._base import REPO_ROOT


# Input ledgers Hephaestus reads (only PROMOTED rows used for composition)
STYGIAN_LEDGER = (
    REPO_ROOT / "charon" / "agents" / "stygian" / "state" / "kill_ledger.jsonl"
)
POLLUX_LEDGER = (
    REPO_ROOT / "charon" / "agents" / "pollux" / "state" / "kill_ledger.jsonl"
)
HEPHAESTUS_LEDGER = (
    REPO_ROOT / "charon" / "agents" / "hephaestus" / "state" / "kill_ledger.jsonl"
)

# How far back to read promoted rows (avoids re-composing on ancient verdicts)
LOOKBACK_DAYS = 7

# Pythia inbox dir
HECATE_ARTIFACT_DIR = REPO_ROOT / "charon" / "agents" / "hecate" / "artifacts"


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return rows


def _filter_substantive_recent(rows: list[dict], lookback_days: int) -> list[dict]:
    """Substantive = PROMOTED (clean survival) OR UNVERIFIED-with-battery
    (battery ran and produced sub-test results without a clean REJECTED).
    Excludes REJECTED (claim killed) and stygian_*_pending short-circuits
    (no battery results to compose against)."""
    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=lookback_days)
    ).isoformat()
    out = []
    for r in rows:
        verdict = r.get("verdict")
        if verdict not in ("PROMOTED", "UNVERIFIED"):
            continue
        # Exclude short-circuit UNVERIFIED rows (no real battery output)
        kp = r.get("kill_pattern") or ""
        if kp.endswith("_pending") or kp.endswith("_skipped") or kp.endswith("_loader_pending"):
            continue
        if (r.get("emitted_at") or "") < cutoff:
            continue
        out.append(r)
    return out


def _read_latest_hecate_crossgen() -> list[str]:
    """Scan the most recent Hecate gradient_archaeology artifact for
    its 'crossgen_canonical_kp_top' list. Best-effort regex parse;
    returns [] if no recent artifact or pattern not found."""
    if not HECATE_ARTIFACT_DIR.exists():
        return []
    artifacts = sorted(
        HECATE_ARTIFACT_DIR.glob("gradient_archaeology_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not artifacts:
        return []
    try:
        text = artifacts[0].read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    # Find the "Top canonical ... cross-generator patterns" section and
    # extract the bullet lines below it.
    m = re.search(
        r"Top canonical[^\n]*cross-generator patterns.*?\n\n((?:- `[^`]+`\n)+)",
        text,
        re.DOTALL,
    )
    if not m:
        return []
    block = m.group(1)
    return re.findall(r"- `([^`]+)`", block)


def _content_hash(obj: dict) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _emit_to_ledger(row: dict) -> Path:
    HEPHAESTUS_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with HEPHAESTUS_LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return HEPHAESTUS_LEDGER


class HephaestusAgent(CharonAgent):
    """Composer/forger agent. Per-tick: read Stygian PROMOTED + Pollux
    PROMOTED + Hecate cross-gen patterns; synthesize one intersection-
    claim; emit ledger row + stygian_priority queue row."""

    name = "Hephaestus"
    role = "composer/forger (generates intersection-claims from Stygian + Pollux PROMOTED)"

    def self_generate_backlog(self) -> list[dict]:
        """Always one item: attempt one composition this tick."""
        return [{"action": "compose"}]

    # ---- composition logic ------------------------------------------

    def _pick_uncomposed_pair(
        self, stygian_rows: list[dict], pollux_rows: list[dict]
    ) -> Optional[tuple[dict, dict]]:
        """Find the highest-priority (Stygian-row, Pollux-row) pair we
        haven't composed yet. 'Tried' set persists in state."""
        if not stygian_rows or not pollux_rows:
            return None
        tried = set(self.load_state("tried_pairs", []) or [])
        # Iterate by (s_emitted_at DESC, p_emitted_at DESC) so newest
        # combinations get priority. Skip combinations we've already
        # composed.
        s_sorted = sorted(
            stygian_rows, key=lambda r: r.get("emitted_at", ""), reverse=True
        )
        p_sorted = sorted(
            pollux_rows, key=lambda r: r.get("emitted_at", ""), reverse=True
        )
        for s in s_sorted:
            for p in p_sorted:
                key = f"{s.get('record_id', '')}|{p.get('record_id', '')}"
                if key in tried:
                    continue
                return (s, p)
        return None

    def _mark_pair_tried(self, s_row: dict, p_row: dict) -> None:
        tried = set(self.load_state("tried_pairs", []) or [])
        key = f"{s_row.get('record_id', '')}|{p_row.get('record_id', '')}"
        tried.add(key)
        # Cap the set so it doesn't grow unbounded
        if len(tried) > 1000:
            tried = set(list(tried)[-1000:])
        self.save_state("tried_pairs", list(tried))

    def _synthesize_composed_claim(
        self, s_row: dict, p_row: dict, crossgen_patterns: list[str]
    ) -> dict:
        """Build the composed-claim payload: 'Stygian claim X restricted
        to Pollux survivor subset Y, with cross-gen context Z.'"""
        s_claim = s_row.get("canonical_claim_text", "")
        s_problem_id = (s_row.get("claim_payload") or {}).get("problem_id", "?")
        p_claim = p_row.get("canonical_claim_text", "")
        p_pair_name = (p_row.get("claim_payload") or {}).get("pair_name", "?")
        p_subset_a = (p_row.get("extras") or {}).get("subset_a_desc", "?")
        p_subset_b = (p_row.get("extras") or {}).get("subset_b_desc", "?")

        composed_id = f"HEPH-{s_problem_id}-x-{p_pair_name}"
        composition_text = (
            f"Composed intersection-claim {composed_id}: "
            f"The structural claim from Stygian's PROMOTED verdict on "
            f"`{s_problem_id}` (\"{s_claim[:200]}\") is hypothesized to "
            f"hold when restricted to the Pollux-PROMOTED subset pair "
            f"`{p_pair_name}` (subset A: {p_subset_a}; subset B: "
            f"{p_subset_b}). The substantive test is whether the "
            f"restricted-subset version of the Stygian claim survives "
            f"its own v10 battery -- if yes, the intersection is "
            f"non-trivial and the two parent observations have a "
            f"shared structural basis. If no, the intersection is "
            f"coincidental and the parent verdicts were independent."
        )
        if crossgen_patterns:
            composition_text += (
                f" Hecate cross-generator context (top canonical patterns "
                f"this tick): {crossgen_patterns[:5]}."
            )
        return {
            "composed_id": composed_id,
            "composition_text": composition_text,
            "stygian_record_id": s_row.get("record_id"),
            "stygian_problem_id": s_problem_id,
            "stygian_claim": s_claim,
            "pollux_record_id": p_row.get("record_id"),
            "pollux_pair_name": p_pair_name,
            "pollux_corr_raw": (p_row.get("kill_vector") or {}).get("corr_raw"),
            "pollux_corr_norm": (p_row.get("kill_vector") or {}).get("corr_norm"),
            "hecate_crossgen_patterns": crossgen_patterns[:5],
        }

    # ---- artifact + ledger + queue emission -------------------------

    def _emit_composed_claim_artifact(self, composed: dict) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        cid = composed["composed_id"]
        # Filename-safe slug
        slug = re.sub(r"[^A-Za-z0-9_.-]", "_", cid)[:60]
        fname = f"composed_claim_{slug}_{utc}.md"
        body_lines = [
            f"# Hephaestus composed claim -- {cid}",
            "",
            f"- emitted_at: {datetime.now(timezone.utc).isoformat()}",
            f"- emitted_by: Hephaestus (charon/agents/hephaestus/daemon.py)",
            "",
            "## Composition",
            "",
            composed["composition_text"],
            "",
            "## Parent verdicts",
            "",
            f"### Stygian PROMOTED ({composed['stygian_problem_id']})",
            "",
            f"- record_id: `{composed['stygian_record_id']}`",
            f"- claim: {composed['stygian_claim'][:500]}",
            "",
            f"### Pollux PROMOTED ({composed['pollux_pair_name']})",
            "",
            f"- record_id: `{composed['pollux_record_id']}`",
            f"- corr_raw: {composed['pollux_corr_raw']}",
            f"- corr_norm: {composed['pollux_corr_norm']}",
            "",
        ]
        if composed.get("hecate_crossgen_patterns"):
            body_lines += [
                "## Hecate cross-generator context",
                "",
            ]
            for p in composed["hecate_crossgen_patterns"]:
                body_lines.append(f"- `{p}`")
            body_lines.append("")
        body_lines += [
            "## Downstream action",
            "",
            "Enqueued to stygian_priority for v10 battery validation. "
            "Stygian will currently short-circuit with "
            "kill_pattern=stygian_hephaestus_composed_loader_pending "
            "until a per-composition loader ships. The composed-claim "
            "artifact alone is substrate-grade: it captures a new "
            "candidate intersection that didn't exist before this tick.",
            "",
        ]
        return self.write_artifact(fname, "\n".join(body_lines))

    def _emit_kill_ledger_row(self, composed: dict) -> str:
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "composed_id": composed["composed_id"],
            "stygian_record_id": composed["stygian_record_id"],
            "pollux_record_id": composed["pollux_record_id"],
            "emitted_at": now_iso,
        }
        rid = _content_hash(payload)
        row = {
            "batch_id": f"hephaestus-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "record_id": rid,
            "canonical_claim_text": composed["composition_text"][:500],
            "claim_kind": "hephaestus_composed_claim",
            "claim_payload": {
                "composed_id": composed["composed_id"],
                "stygian_problem_id": composed["stygian_problem_id"],
                "pollux_pair_name": composed["pollux_pair_name"],
            },
            "convergence_status": "composed",
            "diversity_score": None,
            "emitted_at": now_iso,
            "extras": {
                "stygian_record_id": composed["stygian_record_id"],
                "pollux_record_id": composed["pollux_record_id"],
                "hecate_crossgen_patterns": composed["hecate_crossgen_patterns"],
                "pollux_corr_raw": composed["pollux_corr_raw"],
                "pollux_corr_norm": composed["pollux_corr_norm"],
            },
            "generator_id": "hephaestus",  # 4th non-Theseus operator class
            "info_density": None,
            "kill_pattern": "hephaestus_composed_claim_pending",
            "kill_vector": None,
            "method": "intersection_composition",
            "novelty_estimate": None,
            "parent_record_id": composed["stygian_record_id"],
            "precision_dps": None,
            "sigma_claim_id": None,
            "sigma_symbol_ref": None,
            "step_trace": None,
            "training_weight": None,
            "verdict": "UNVERIFIED",  # battery hasn't run on composed claim yet
        }
        _emit_to_ledger(row)
        return rid

    def _enqueue_to_stygian(self, composed: dict, ledger_row_id: str) -> bool:
        try:
            queue = stygian_priority_queue()
            # Dedup: only enqueue once per composed_id within 24h
            recent_cutoff = (
                datetime.now(timezone.utc) - timedelta(hours=24)
            ).isoformat()
            recent_kps = queue.recent_keys("kill_pattern", recent_cutoff)
            key = f"hephaestus_composed_{composed['composed_id']}"
            if key in recent_kps:
                return False
            queue.append({
                "source": "hephaestus",
                "kill_pattern": key,
                "cluster_size": None,
                "top_generator": "hephaestus",
                "mi_z": None,
                "mi_observed": None,
                "hephaestus_composed_id": composed["composed_id"],
                "hephaestus_stygian_record_id": composed["stygian_record_id"],
                "hephaestus_pollux_record_id": composed["pollux_record_id"],
                "hephaestus_ledger_row_id": ledger_row_id,
                "rationale": composed["composition_text"][:300],
            })
            return True
        except Exception as e:
            self.log.warning(f"stygian_priority enqueue failed: {e}")
            return False

    def _emit_self_audit_null(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"self_audit_null_{utc}.md"
        body = (
            f"# Hephaestus SELF_AUDIT_NULL\n\n"
            f"- reason: {reason}\n"
            f"- at: {datetime.now(timezone.utc).isoformat()}\n\n"
            f"Hephaestus requires at least one PROMOTED row from each of "
            f"Stygian and Pollux in the last {LOOKBACK_DAYS} days to "
            f"compose an intersection-claim. When either source is empty, "
            f"the composer no-ops with this artifact. Pollux promotes "
            f"more frequently than Stygian (which is bottlenecked by "
            f"loader coverage); the typical null cause is Stygian-empty.\n"
        )
        return self.write_artifact(fname, body)

    # ---- run_tick --------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "stygian_substantive_recent": 0,
            "pollux_substantive_recent": 0,
            "crossgen_patterns_found": 0,
            "composed": False,
            "composed_id": None,
            "ledger_row_id": None,
            "enqueued_to_stygian": False,
            "skip_reason": None,
        }

        stygian_rows = _filter_substantive_recent(
            _read_jsonl(STYGIAN_LEDGER), LOOKBACK_DAYS
        )
        pollux_rows = _filter_substantive_recent(
            _read_jsonl(POLLUX_LEDGER), LOOKBACK_DAYS
        )
        crossgen = _read_latest_hecate_crossgen()
        stats["stygian_substantive_recent"] = len(stygian_rows)
        stats["pollux_substantive_recent"] = len(pollux_rows)
        stats["crossgen_patterns_found"] = len(crossgen)

        if dry_run:
            stats["items_processed"] += 1
            return stats

        if not stygian_rows:
            stats["skip_reason"] = "no_recent_stygian_substantive"
            try:
                self._emit_self_audit_null(stats["skip_reason"])
                stats["artifacts_written"] += 1
            except Exception as e:
                self.log.warning(f"self_audit_null emit failed: {e}")
                stats["errors"] += 1
            stats["items_processed"] += 1
            return stats
        if not pollux_rows:
            stats["skip_reason"] = "no_recent_pollux_substantive"
            try:
                self._emit_self_audit_null(stats["skip_reason"])
                stats["artifacts_written"] += 1
            except Exception as e:
                self.log.warning(f"self_audit_null emit failed: {e}")
                stats["errors"] += 1
            stats["items_processed"] += 1
            return stats

        pair = self._pick_uncomposed_pair(stygian_rows, pollux_rows)
        if not pair:
            stats["skip_reason"] = "all_pairs_already_composed"
            try:
                self._emit_self_audit_null(stats["skip_reason"])
                stats["artifacts_written"] += 1
            except Exception as e:
                self.log.warning(f"self_audit_null emit failed: {e}")
                stats["errors"] += 1
            stats["items_processed"] += 1
            return stats

        s_row, p_row = pair
        composed = self._synthesize_composed_claim(s_row, p_row, crossgen)
        try:
            self._emit_composed_claim_artifact(composed)
            stats["artifacts_written"] += 1
        except Exception as e:
            self.log.exception(f"composed-claim artifact emit failed: {e}")
            stats["errors"] += 1

        try:
            rid = self._emit_kill_ledger_row(composed)
            stats["ledger_row_id"] = rid
        except Exception as e:
            self.log.exception(f"kill_ledger emit failed: {e}")
            stats["errors"] += 1
            rid = None

        if rid is not None:
            stats["enqueued_to_stygian"] = self._enqueue_to_stygian(
                composed, rid
            )

        self._mark_pair_tried(s_row, p_row)
        stats["composed"] = True
        stats["composed_id"] = composed["composed_id"]
        stats["items_processed"] += 1

        self.log_work(
            "hephaestus_tick_complete",
            summary=(
                f"composed={stats['composed_id']} "
                f"stygian_recent={stats['stygian_substantive_recent']} "
                f"pollux_recent={stats['pollux_substantive_recent']} "
                f"crossgen={stats['crossgen_patterns_found']} "
                f"enqueued={stats['enqueued_to_stygian']}"
            ),
            success=stats["errors"] == 0,
        )
        return stats
