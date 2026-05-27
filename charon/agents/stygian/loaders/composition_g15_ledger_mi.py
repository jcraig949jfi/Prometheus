"""Composition loader: EREBOS-G15-* (Cross-Generator MI) on live
kill_ledger meta-analysis.

Per the G15 plugin spec: tests whether cross-generator convergence
patterns reflect a Latent Confound L. The loader's empirical proxy:
compute Shannon mutual information between (plugin_id, kill_pattern)
over the union of Stygian + Pollux + Erebos kill_ledgers. High MI
means certain plugin-pattern pairings dominate; low MI means the
plugins explore approximately orthogonal failure modes.

Decision rule:
- MI >= MI_THRESHOLD_NATS: cross-gen structure exists, plugin and
  kill_pattern are coupled -> PROMOTED (G15's latent-confound
  hypothesis is empirically supported).
- MI < MI_THRESHOLD_NATS: failures are approximately uncorrelated
  with originating plugin -> REJECTED with kill_pattern =
  uncorrelated_residual_failures (matches plugin's expected pattern).

MI is computed from observed joint counts; we report both raw MI
and a normalized variant (MI / log(min(|X|, |Y|))) so the threshold
generalizes across catalog sizes.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

from charon.agents.stygian.loaders._composition import register

try:
    from harmonia.agents._base import REPO_ROOT
except Exception:
    REPO_ROOT = Path(__file__).resolve().parents[4]


LEDGER_PATHS = [
    REPO_ROOT / "charon" / "agents" / "stygian" / "state" / "kill_ledger.jsonl",
    REPO_ROOT / "charon" / "agents" / "pollux" / "state" / "kill_ledger.jsonl",
    REPO_ROOT / "charon" / "agents" / "erebos" / "state" / "kill_ledger.jsonl",
]

# MI threshold in nats. 0.1 nats ≈ 0.14 bits — small but non-trivial.
# Adjust if smoke tests show wrong-side biases.
MI_THRESHOLD_NATS = 0.10
MIN_PAIRED_ROWS = 20  # need at least this many (plugin, kp) observations


def _read_ledger_rows() -> list[dict]:
    """Read all kill_ledger rows across Stygian/Pollux/Erebos.
    Tolerates missing files and corrupt lines."""
    rows: list[dict] = []
    for path in LEDGER_PATHS:
        if not path.exists():
            continue
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
            continue
    return rows


def _extract_plugin_id(row: dict) -> Optional[str]:
    """Plugin/generator id field across the three ledger families."""
    # Erebos rows carry plugin_id in claim_payload
    cp = row.get("claim_payload") or {}
    pid = cp.get("plugin_id")
    if pid:
        return str(pid)
    # Generic fallback: generator_id field
    gid = row.get("generator_id")
    if gid:
        return str(gid)
    return None


def _extract_kill_pattern(row: dict) -> Optional[str]:
    kp = row.get("kill_pattern")
    if kp:
        return str(kp)
    return None


def _shannon_mi(joint: dict[tuple, int]) -> dict:
    """Compute MI(X; Y) in nats from observed joint counts.
    Returns dict with mi_nats, mi_bits, mi_normalized (Iyer 1995)."""
    if not joint:
        return {"mi_nats": 0.0, "mi_bits": 0.0, "mi_normalized": 0.0,
                "n_x": 0, "n_y": 0, "n_total": 0}
    total = sum(joint.values())
    if total <= 0:
        return {"mi_nats": 0.0, "mi_bits": 0.0, "mi_normalized": 0.0,
                "n_x": 0, "n_y": 0, "n_total": 0}
    # Marginals
    px: dict = {}
    py: dict = {}
    for (x, y), c in joint.items():
        px[x] = px.get(x, 0) + c
        py[y] = py.get(y, 0) + c
    mi = 0.0
    for (x, y), c in joint.items():
        if c == 0:
            continue
        p_xy = c / total
        p_x = px[x] / total
        p_y = py[y] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log(p_xy / (p_x * p_y))
    # Normalize by max possible (log of min cardinality)
    nx, ny = len(px), len(py)
    max_mi = math.log(max(min(nx, ny), 1)) if min(nx, ny) > 1 else 1.0
    return {
        "mi_nats": mi,
        "mi_bits": mi / math.log(2),
        "mi_normalized": mi / max_mi if max_mi > 0 else 0.0,
        "n_x": nx,
        "n_y": ny,
        "n_total": total,
    }


def run_g15_ledger_mi() -> dict:
    """Compute MI between plugin_id and kill_pattern across all
    kill_ledgers. Returns the result dict."""
    rows = _read_ledger_rows()
    if not rows:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "no rows found in Stygian/Pollux/Erebos ledgers",
        }

    # Build the joint count over (plugin_id, kill_pattern) for rows
    # where BOTH fields are present (only REJECTED-ish rows tend to
    # carry kill_patterns).
    joint: dict[tuple, int] = {}
    for r in rows:
        pid = _extract_plugin_id(r)
        kp = _extract_kill_pattern(r)
        if not pid or not kp:
            continue
        joint[(pid, kp)] = joint.get((pid, kp), 0) + 1

    n_observations = sum(joint.values())
    if n_observations < MIN_PAIRED_ROWS:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_paired_observations": n_observations,
            "min_paired_needed": MIN_PAIRED_ROWS,
            "notes": (
                f"only {n_observations} (plugin, kill_pattern) "
                f"observations in ledgers; need >= {MIN_PAIRED_ROWS}"
            ),
        }

    mi_block = _shannon_mi(joint)

    if mi_block["mi_nats"] >= MI_THRESHOLD_NATS:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"MI({mi_block['mi_nats']:.4f} nats / "
            f"{mi_block['mi_bits']:.4f} bits) >= threshold "
            f"{MI_THRESHOLD_NATS} nats. Cross-generator failure "
            f"patterns are coupled; G15's latent-confound "
            f"hypothesis is empirically supported. Normalized "
            f"MI = {mi_block['mi_normalized']:.4f}."
        )
    else:
        verdict = "REJECTED"
        kp = "uncorrelated_residual_failures"
        notes = (
            f"MI({mi_block['mi_nats']:.4f} nats) < threshold "
            f"{MI_THRESHOLD_NATS} nats. Plugin and kill_pattern "
            f"are approximately independent in the live ledger; "
            f"G15's latent-confound hypothesis is falsified -- "
            f"the failures look uncorrelated. Matches plugin's "
            f"expected_kill_pattern."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "mi_nats": round(mi_block["mi_nats"], 4),
        "mi_bits": round(mi_block["mi_bits"], 4),
        "mi_normalized": round(mi_block["mi_normalized"], 4),
        "mi_threshold_nats": MI_THRESHOLD_NATS,
        "n_distinct_plugins": mi_block["n_x"],
        "n_distinct_kill_patterns": mi_block["n_y"],
        "n_paired_observations": n_observations,
        "notes": notes,
    }


class G15LedgerMILoader:
    plugin_id = "g15_cross_gen_mi"
    composition_id = "g15_ledger_mi"
    description = (
        "Composition loader for EREBOS-G15-* claims. Meta-analysis "
        "of the live Stygian/Pollux/Erebos kill_ledgers; computes "
        "Shannon MI(plugin_id; kill_pattern); PROMOTED if MI >= "
        "0.10 nats, REJECTED uncorrelated_residual_failures if "
        "below. Domain-agnostic."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g15_cross_gen_mi":
            return False
        # Domain-agnostic: every G15 emission qualifies.
        return True

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g15_ledger_mi()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G15 ledger-MI composition: Shannon "
                "MI(plugin_id; kill_pattern) across union of "
                "Stygian/Pollux/Erebos kill_ledgers."
            ),
            "data_source": (
                "Live read of charon/agents/{stygian,pollux,erebos}/"
                "state/kill_ledger.jsonl; joint count over "
                "(plugin_id, kill_pattern)."
            ),
            "result": result,
            "notes": (
                "G15 graduates to empirical instrument via ledger MI. "
                "Domain-agnostic: works for any swarm meta-analysis "
                "context."
            ),
        }


register(G15LedgerMILoader())
