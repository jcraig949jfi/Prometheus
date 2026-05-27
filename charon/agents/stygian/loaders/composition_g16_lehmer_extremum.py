"""Composition loader: EREBOS-G16-* (Anti-Anchor) on Lehmer-context
parents.

Per the G16 plugin spec: takes a PROMOTED anchor, pushes ONE numeric
parameter to an adversarial extreme, and predicts catastrophic break
at that extreme. For Lehmer-context emissions, the parameter is
typically `degree` or `mahler_measure`. This loader tests the
adversarial-band hypothesis by restricting the Mossinghoff catalog
to a tight band around the adversarial value and rerunning the
parent's Lehmer-survival test there.

Concrete test (v0.14 MVP):
- Read `adversarial_value` from the queue payload's composition_payload
  (the value G16 wrote when emitting the claim). Fall back to a
  multiplicative push (10x) of a degree-like extracted value if no
  explicit adversarial_value is given.
- Restrict Mossinghoff entries to those whose `mahler_measure` is
  within +/-BAND_WIDTH of the adversarial value.
- Recompute survival fraction (entries with M >= M_Lehmer) in the
  restricted band.

Decision rule:
- If the adversarial band is empty (no entries): kill_pattern =
  stygian_composition_empty_adversarial_band (the extreme really is
  uninhabited; G16's break-here hypothesis is structural).
- If band survival is >= ANCHOR_SURVIVAL_THRESHOLD (e.g., 0.90):
  the anchor survives the adversarial regime -> kill_pattern =
  conjecture_survives_adversarial_attack (G16's break-here
  hypothesis falsified; the anchor extends past its center).
- If band survival is < ANCHOR_SURVIVAL_THRESHOLD: the anchor
  meaningfully degrades in the adversarial band -> PROMOTED
  (G16's hypothesis succeeds — the parent's PROMOTED status was
  centered on the typical regime and weakens in the extreme).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
    survival_fraction,
)

try:
    from harmonia.agents._base import REPO_ROOT
except Exception:
    REPO_ROOT = Path(__file__).resolve().parents[4]


BAND_WIDTH = 0.05  # half-width of the adversarial band around adversarial M value
ANCHOR_SURVIVAL_THRESHOLD = 0.90
MIN_BAND_SIZE = 5  # need at least this many entries in the band to evaluate

EREBOS_LEDGER = (
    REPO_ROOT / "charon" / "agents" / "erebos" / "state" / "kill_ledger.jsonl"
)


def _adversarial_value_from_ledger(composed_id: str) -> Optional[dict]:
    """Look up the Erebos ledger row matching composed_id; extract
    composition_payload.adversarial_value and param_key. Returns
    {adversarial_value, param_key} or None on miss."""
    if not EREBOS_LEDGER.exists():
        return None
    try:
        with EREBOS_LEDGER.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                cid = (row.get("claim_payload") or {}).get("composed_id")
                if cid != composed_id:
                    continue
                cp = (row.get("extras") or {}).get("composition_payload") or {}
                adv = cp.get("adversarial_value")
                key = cp.get("param_key")
                if adv is not None and key:
                    return {
                        "adversarial_value": float(adv),
                        "param_key": str(key),
                    }
    except Exception:
        return None
    return None


def run_g16_lehmer_extremum(adversarial_M: float, param_key: str) -> dict:
    """Test anchor survival in the adversarial M-band."""
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load failed",
        }
    lo = adversarial_M - BAND_WIDTH
    hi = adversarial_M + BAND_WIDTH
    band = [
        float(e["mahler_measure"]) for e in entries
        if lo <= float(e["mahler_measure"]) <= hi
    ]
    n_band = len(band)
    if n_band == 0:
        return {
            "verdict": "REJECTED",
            "kill_pattern": "stygian_composition_empty_adversarial_band",
            "adversarial_value": adversarial_M,
            "param_key": param_key,
            "band_lo": round(lo, 6),
            "band_hi": round(hi, 6),
            "n_band": 0,
            "notes": (
                f"Adversarial band [{lo:.4f}, {hi:.4f}] is empty in "
                f"Mossinghoff catalog. The 'break here' hypothesis is "
                f"structurally trivial (no objects exist at the "
                f"extreme to be tested). G16's emission for this "
                f"param/value cannot be evaluated."
            ),
        }
    if n_band < MIN_BAND_SIZE:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "adversarial_value": adversarial_M,
            "param_key": param_key,
            "band_lo": round(lo, 6),
            "band_hi": round(hi, 6),
            "n_band": n_band,
            "notes": (
                f"Adversarial band has {n_band} entries "
                f"(< {MIN_BAND_SIZE}); insufficient to evaluate."
            ),
        }

    band_survival = survival_fraction(band, M_LEHMER)

    # ITER-19 refinement: compute a permutation null over the band
    # for robustness. Compare band survival against survival under
    # random subsamples of the FULL catalog with the same N. If
    # band survival is significantly different from a same-size
    # subsample of the catalog, the band's behavior is genuinely
    # local; if not, the band looks like an arbitrary subsample.
    all_catalog_M = [float(e["mahler_measure"]) for e in entries]
    import random
    rng = random.Random(42)
    n_perm = 500
    null_survivals = []
    for _ in range(n_perm):
        sample = rng.sample(all_catalog_M, n_band)
        null_survivals.append(survival_fraction(sample, M_LEHMER))
    null_survivals_sorted = sorted(null_survivals)
    null_p05 = null_survivals_sorted[int(0.05 * (len(null_survivals_sorted) - 1))]
    null_p95 = null_survivals_sorted[int(0.95 * (len(null_survivals_sorted) - 1))]
    # Band is "structurally different" from catalog-bulk if its
    # survival falls OUTSIDE the null 90% central mass.
    band_is_structurally_different = (
        band_survival < null_p05 or band_survival > null_p95
    )

    if band_survival >= ANCHOR_SURVIVAL_THRESHOLD:
        verdict = "REJECTED"
        kp = "conjecture_survives_adversarial_attack"
        notes = (
            f"Anchor survival in adversarial band [{lo:.4f}, {hi:.4f}] "
            f"= {band_survival:.4f} >= {ANCHOR_SURVIVAL_THRESHOLD}; "
            f"the anchor extends past the typical regime. G16's "
            f"break-here hypothesis is falsified -- the anchor "
            f"validated."
        )
    else:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"Anchor survival in adversarial band [{lo:.4f}, {hi:.4f}] "
            f"= {band_survival:.4f} < {ANCHOR_SURVIVAL_THRESHOLD}; "
            f"the anchor meaningfully degrades in the extreme. G16's "
            f"break-here hypothesis succeeded -- substrate-grade "
            f"evidence the parent's PROMOTED status was regime-local."
        )

    # Append permutation-null context to notes so consumers know
    # whether the verdict is null-robust
    notes += (
        f" Permutation null over {n_perm} catalog subsamples of size "
        f"{n_band}: null central 90% mass = [{null_p05:.4f}, "
        f"{null_p95:.4f}]. Band survival is "
        f"{'STRUCTURALLY DIFFERENT' if band_is_structurally_different else 'within null mass'}."
    )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "adversarial_value": adversarial_M,
        "param_key": param_key,
        "band_lo": round(lo, 6),
        "band_hi": round(hi, 6),
        "band_width": BAND_WIDTH,
        "n_band": n_band,
        "band_survival": round(band_survival, 4),
        "null_p05": round(null_p05, 4),
        "null_p95": round(null_p95, 4),
        "band_is_structurally_different": band_is_structurally_different,
        "permutation_n": n_perm,
        "anchor_survival_threshold": ANCHOR_SURVIVAL_THRESHOLD,
        "notes": notes,
    }


class G16LehmerExtremumLoader:
    plugin_id = "g16_anti_anchor"
    composition_id = "g16_lehmer_extremum"
    description = (
        "Composition loader for EREBOS-G16-* claims whose parent is "
        "BL-C-001 Lehmer. Reads adversarial_value from Erebos ledger "
        "composition_payload; restricts Mossinghoff catalog to the "
        "adversarial M-band; measures anchor survival there."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g16_anti_anchor":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        return (
            "BL-C-001" in composed_id
            or "lehmer" in composed_id.lower()
            or "lehmer" in rationale
            or "mahler" in rationale
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        composed_id = queue_payload.get("erebos_composed_id", "?")
        looked_up = _adversarial_value_from_ledger(composed_id)
        if looked_up is None:
            result = {
                "verdict": "UNVERIFIED",
                "kill_pattern": "stygian_composition_payload_lookup_failed",
                "notes": (
                    f"Could not resolve composition_payload."
                    f"adversarial_value for {composed_id} in Erebos "
                    f"ledger. Composition cannot proceed."
                ),
            }
        else:
            result = run_g16_lehmer_extremum(
                adversarial_M=looked_up["adversarial_value"],
                param_key=looked_up["param_key"],
            )
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G16 extremum composition: restrict Mossinghoff "
                "catalog to a band around G16's adversarial_value; "
                "measure anchor survival there; PROMOTED if anchor "
                "degrades, REJECTED with conjecture_survives_"
                "adversarial_attack if anchor extends."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; band restriction around "
                "G16's adversarial_value."
            ),
            "result": result,
            "notes": (
                "G16 graduates to empirical instrument for Lehmer-"
                "context anti-anchor emissions. Reads adversarial_value "
                "from the Erebos ledger row's composition_payload."
            ),
        }


register(G16LehmerExtremumLoader())
