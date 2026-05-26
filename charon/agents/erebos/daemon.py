"""Erebos -- composer/forger agent (Charon swarm v0.8).

Plugin-host pattern per pivot/erebos_25_archetypes_spec_2026-05-26.md.

Per-tick:
  1. Build SwarmState snapshot from Stygian + Pollux + Erebos
     ledgers + Hecate's latest cross-gen patterns.
  2. Pick the next applicable plugin via round-robin (skipping
     non-applicable).
  3. Plugin.generate(state) -> ComposedClaim or None.
  4. If ComposedClaim emitted:
     a. Write a composed_claim_*.md artifact.
     b. Append a kill_ledger row in Theseus shape
        (generator_id='erebos', kill_pattern from plugin spec).
     c. Enqueue to stygian_priority for v10 battery attack (Stygian
        will short-circuit until composition-aware loader ships in
        v0.11+).
     d. Mark the (plugin_id, parent_ids) tuple as tried in state.

Generator plugins live under charon/agents/erebos/generators/.
Currently registered: G01 Intersection, G02 Contrast.

Renamed from Hephaestus 2026-05-26 (name collision with the existing
agents/hephaestus/ Forge -- 357+ forged tools, RLVF pipeline).
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import time
import uuid

from charon.agents._base import CharonAgent
from charon.agents._shared_queues import stygian_priority_queue
from charon.agents.erebos._logging import (
    GeneratorTickLog,
    emit_tick_log,
    hash_falsification_route,
)
from charon.agents.erebos.generators import (
    REGISTRY,
    next_plugin_round_robin,
)
from charon.agents.erebos.generators._base import ComposedClaim, SwarmState
from harmonia.agents._base import REPO_ROOT


# Input ledgers Erebos reads
STYGIAN_LEDGER = (
    REPO_ROOT / "charon" / "agents" / "stygian" / "state" / "kill_ledger.jsonl"
)
POLLUX_LEDGER = (
    REPO_ROOT / "charon" / "agents" / "pollux" / "state" / "kill_ledger.jsonl"
)
EREBOS_LEDGER = (
    REPO_ROOT / "charon" / "agents" / "erebos" / "state" / "kill_ledger.jsonl"
)
HECATE_ARTIFACT_DIR = REPO_ROOT / "charon" / "agents" / "hecate" / "artifacts"

LOOKBACK_DAYS = 7


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
    """Substantive = PROMOTED OR UNVERIFIED-with-real-battery-output OR
    REJECTED (G02 Contrast needs REJECTED rows). Excludes pure
    short-circuit rows (kill_pattern ending in _pending /
    _loader_pending / _skipped)."""
    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=lookback_days)
    ).isoformat()
    out = []
    for r in rows:
        verdict = r.get("verdict")
        if verdict not in ("PROMOTED", "UNVERIFIED", "REJECTED"):
            continue
        kp = r.get("kill_pattern") or ""
        if kp.endswith("_pending") or kp.endswith("_skipped") or kp.endswith("_loader_pending"):
            continue
        if (r.get("emitted_at") or "") < cutoff:
            continue
        out.append(r)
    return out


def _read_latest_hecate_crossgen() -> list[str]:
    if not HECATE_ARTIFACT_DIR.exists():
        return []
    artifacts = sorted(
        HECATE_ARTIFACT_DIR.glob("gradient_archaeology_*.md"),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    if not artifacts:
        return []
    try:
        text = artifacts[0].read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    m = re.search(
        r"Top canonical[^\n]*cross-generator patterns.*?\n\n((?:- `[^`]+`\n)+)",
        text, re.DOTALL,
    )
    if not m:
        return []
    return re.findall(r"- `([^`]+)`", m.group(1))


def _content_hash(obj: dict) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _emit_to_ledger(row: dict) -> Path:
    EREBOS_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with EREBOS_LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return EREBOS_LEDGER


class ErebosAgent(CharonAgent):
    """Composer/forger agent (plugin host)."""

    name = "Erebos"
    role = "composer/forger -- plugin host for 25 hypothesis-generator archetypes"

    def self_generate_backlog(self) -> list[dict]:
        return [{"action": "compose"}]

    def _build_swarm_state(self) -> SwarmState:
        stygian = _filter_substantive_recent(_read_jsonl(STYGIAN_LEDGER), LOOKBACK_DAYS)
        pollux = _filter_substantive_recent(_read_jsonl(POLLUX_LEDGER), LOOKBACK_DAYS)
        self_ledger = _read_jsonl(EREBOS_LEDGER)
        crossgen = _read_latest_hecate_crossgen()
        tried = set(self.load_state("tried_pairs", []) or [])
        tick_counter = int(self.load_state("tick_counter", 0) or 0) + 1
        self.save_state("tick_counter", tick_counter)
        return SwarmState(
            stygian_substantive=stygian,
            pollux_substantive=pollux,
            hecate_crossgen_canonical=crossgen,
            erebos_self_ledger=self_ledger,
            tried_pairs=tried,
            tick_counter=tick_counter,
        )

    def _mark_tried(self, plugin_id: str, claim: ComposedClaim) -> None:
        tried = set(self.load_state("tried_pairs", []) or [])
        parent_ids = "|".join(claim.parent_record_ids)
        key = f"{plugin_id}|{parent_ids}"
        tried.add(key)
        if len(tried) > 2000:
            tried = set(list(tried)[-2000:])
        self.save_state("tried_pairs", list(tried))

    # ---- artifact + ledger + queue emission -------------------------

    def _emit_composed_claim_artifact(self, claim: ComposedClaim, plugin) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        slug = re.sub(r"[^A-Za-z0-9_.-]", "_", claim.composed_id)[:60]
        fname = f"composed_claim_{slug}_{utc}.md"
        lines = [
            f"# Erebos composed claim -- {claim.composed_id}",
            "",
            f"- emitted_at: {datetime.now(timezone.utc).isoformat()}",
            f"- emitted_by: Erebos (charon/agents/erebos/daemon.py)",
            f"- plugin: `{plugin.id}` ({plugin.name})",
            f"- spec_phase: {plugin.spec_phase}",
            f"- feasibility_tier: {plugin.feasibility_tier}",
            "",
            "## Output claim",
            "",
            claim.output_claim_text,
            "",
            "## Six-field Erebos spec",
            "",
            "### Input / Provenance",
            "",
            "```json",
            json.dumps(claim.input_provenance, indent=2, ensure_ascii=False, default=str),
            "```",
            "",
            "### Transformation",
            "",
            claim.transformation_description,
            "",
            "### Falsification route",
            "",
            claim.falsification_route,
            "",
            "### Expected kill pattern",
            "",
            f"`{claim.expected_kill_pattern}`",
            "",
            "### Loader feasibility note",
            "",
            claim.loader_feasibility_note,
            "",
            "## Routing metadata",
            "",
            f"- parent_record_ids: {claim.parent_record_ids}",
            f"- composition_payload keys: {list(claim.composition_payload.keys())}",
            "",
        ]
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_kill_ledger_row(self, claim: ComposedClaim, plugin) -> str:
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "plugin_id": plugin.id,
            "composed_id": claim.composed_id,
            "parent_record_ids": claim.parent_record_ids,
            "emitted_at": now_iso,
        }
        rid = _content_hash(payload)
        kp = f"erebos_{plugin.id}_pending"
        row = {
            "batch_id": f"erebos-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "record_id": rid,
            "canonical_claim_text": claim.output_claim_text[:500],
            "claim_kind": f"erebos_{plugin.id}_claim",
            "claim_payload": {
                "plugin_id": plugin.id,
                "plugin_name": plugin.name,
                "spec_phase": plugin.spec_phase,
                "composed_id": claim.composed_id,
                "expected_kill_pattern": claim.expected_kill_pattern,
                "loader_feasibility_note": claim.loader_feasibility_note,
            },
            "convergence_status": "composed",
            "diversity_score": None,
            "emitted_at": now_iso,
            "extras": {
                "input_provenance": claim.input_provenance,
                "transformation_description": claim.transformation_description,
                "falsification_route": claim.falsification_route,
                "composition_payload": claim.composition_payload,
                "plugin_extras": claim.extras,
            },
            "generator_id": "erebos",
            "info_density": None,
            "kill_pattern": kp,
            "kill_vector": None,
            "method": f"erebos_{plugin.id}",
            "novelty_estimate": None,
            "parent_record_id": claim.parent_record_ids[0] if claim.parent_record_ids else None,
            "precision_dps": None,
            "sigma_claim_id": None,
            "sigma_symbol_ref": None,
            "step_trace": None,
            "training_weight": None,
            "verdict": "UNVERIFIED",
        }
        _emit_to_ledger(row)
        return rid

    def _enqueue_to_stygian(
        self, claim: ComposedClaim, plugin, ledger_row_id: str
    ) -> bool:
        try:
            queue = stygian_priority_queue()
            recent_cutoff = (
                datetime.now(timezone.utc) - timedelta(hours=24)
            ).isoformat()
            recent_kps = queue.recent_keys("kill_pattern", recent_cutoff)
            queue_kp = f"erebos_{plugin.id}_{claim.composed_id}"
            if queue_kp in recent_kps:
                return False
            queue.append({
                "source": "erebos",
                "kill_pattern": queue_kp,
                "cluster_size": None,
                "top_generator": "erebos",
                "mi_z": None,
                "mi_observed": None,
                "erebos_plugin_id": plugin.id,
                "erebos_composed_id": claim.composed_id,
                "erebos_expected_kill_pattern": claim.expected_kill_pattern,
                "erebos_falsification_route": claim.falsification_route,
                "erebos_ledger_row_id": ledger_row_id,
                "parent_record_ids": claim.parent_record_ids,
                "rationale": claim.output_claim_text[:300],
            })
            return True
        except Exception as e:
            self.log.warning(f"stygian_priority enqueue failed: {e}")
            return False

    def _emit_self_audit_null(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"self_audit_null_{utc}.md"
        body = (
            f"# Erebos SELF_AUDIT_NULL\n\n"
            f"- reason: {reason}\n"
            f"- at: {datetime.now(timezone.utc).isoformat()}\n\n"
            f"Erebos's plugin host found no applicable plugin this tick. "
            f"Causes: (a) Stygian + Pollux substantive-row pools empty in "
            f"last {LOOKBACK_DAYS} days; (b) all applicable plugin x "
            f"parent-row pairs already composed (tried_pairs set saturates "
            f"the available combinatorial space).\n"
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
            "plugin_id": None,
            "composed_id": None,
            "ledger_row_id": None,
            "enqueued_to_stygian": False,
            "skip_reason": None,
        }
        # Per-plugin structured log (DNA P4). Populated through the
        # tick + emitted at the end regardless of outcome.
        tick_t0 = time.time()
        tick_id = uuid.uuid4().hex[:16]
        tick_log = GeneratorTickLog(
            ts=datetime.now(timezone.utc).isoformat(),
            plugin_id="<unset>",
            tick_id=tick_id,
            applicable=False,
        )

        state = self._build_swarm_state()
        stats["stygian_substantive_recent"] = len(state.stygian_substantive)
        stats["pollux_substantive_recent"] = len(state.pollux_substantive)
        stats["crossgen_patterns_found"] = len(state.hecate_crossgen_canonical)
        tick_log.inputs_summary = {
            "stygian_substantive": len(state.stygian_substantive),
            "pollux_substantive": len(state.pollux_substantive),
            "crossgen_patterns": len(state.hecate_crossgen_canonical),
            "tried_pairs_size": len(state.tried_pairs),
        }

        if dry_run:
            stats["items_processed"] += 1
            tick_log.elapsed_ms = (time.time() - tick_t0) * 1000
            emit_tick_log(tick_log)
            return stats

        last_plugin_id = self.load_state("last_plugin_id", None)
        plugin = next_plugin_round_robin(state, last_plugin_id)
        if plugin is None:
            stats["skip_reason"] = "no_applicable_plugin"
            tick_log.plugin_id = "no_applicable_plugin"
            tick_log.applicable = False
            tick_log.transformation_path = "skip:no_applicable"
            tick_log.error = None
            try:
                self._emit_self_audit_null(stats["skip_reason"])
                stats["artifacts_written"] += 1
            except Exception as e:
                self.log.warning(f"self_audit_null emit failed: {e}")
                stats["errors"] += 1
                tick_log.error = f"self_audit_null_emit_failed: {e}"
            stats["items_processed"] += 1
            self.log_work(
                "erebos_tick_complete",
                summary=f"skip ({stats['skip_reason']})",
                success=stats["errors"] == 0,
            )
            tick_log.elapsed_ms = (time.time() - tick_t0) * 1000
            emit_tick_log(tick_log)
            return stats

        stats["plugin_id"] = plugin.id
        tick_log.plugin_id = plugin.id
        tick_log.applicable = True

        claim = plugin.generate(state)
        if claim is None:
            stats["skip_reason"] = f"{plugin.id}_returned_none"
            tick_log.transformation_path = "skip:plugin_returned_none"
            try:
                self._emit_self_audit_null(stats["skip_reason"])
                stats["artifacts_written"] += 1
            except Exception as e:
                stats["errors"] += 1
                tick_log.error = f"self_audit_null_emit_failed: {e}"
            stats["items_processed"] += 1
            tick_log.elapsed_ms = (time.time() - tick_t0) * 1000
            emit_tick_log(tick_log)
            return stats

        # Plugin generated a claim
        tick_log.generated = True
        tick_log.composed_id = claim.composed_id
        tick_log.parent_record_ids = list(claim.parent_record_ids)
        tick_log.transformation_path = claim.transformation_description[:200]
        tick_log.expected_kill_pattern = claim.expected_kill_pattern
        tick_log.falsification_route_hash = hash_falsification_route(
            claim.falsification_route
        )

        try:
            self._emit_composed_claim_artifact(claim, plugin)
            stats["artifacts_written"] += 1
        except Exception as e:
            self.log.exception(f"composed-claim artifact emit failed: {e}")
            stats["errors"] += 1
            tick_log.error = f"composed_claim_artifact_failed: {e}"

        try:
            rid = self._emit_kill_ledger_row(claim, plugin)
            stats["ledger_row_id"] = rid
        except Exception as e:
            self.log.exception(f"kill_ledger emit failed: {e}")
            stats["errors"] += 1
            tick_log.error = f"kill_ledger_emit_failed: {e}"
            rid = None

        if rid is not None:
            stats["enqueued_to_stygian"] = self._enqueue_to_stygian(
                claim, plugin, rid
            )

        self._mark_tried(plugin.id, claim)
        self.save_state("last_plugin_id", plugin.id)
        stats["composed"] = True
        stats["composed_id"] = claim.composed_id
        stats["items_processed"] += 1

        self.log_work(
            "erebos_tick_complete",
            summary=(
                f"plugin={plugin.id} composed={claim.composed_id} "
                f"stygian_recent={stats['stygian_substantive_recent']} "
                f"pollux_recent={stats['pollux_substantive_recent']} "
                f"enqueued={stats['enqueued_to_stygian']}"
            ),
            success=stats["errors"] == 0,
        )
        tick_log.elapsed_ms = (time.time() - tick_t0) * 1000
        emit_tick_log(tick_log)
        return stats
