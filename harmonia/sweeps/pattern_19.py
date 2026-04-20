"""
Pattern 19 — Stale / Irreproducible Prior Measurement Detection.

Triggered when a new SIGNATURE claims to re-measure an F-ID already in
the tensor. Compares the claimed new effect size / sample size against
the prior record. Flags:

  new_n > 3 * old_n AND |new_eff - old_eff| > 3 * old_eff  -> WARN (stale)
  sign flip regardless of magnitude                        -> BLOCK
  undocumented scorer / preprocessing change               -> WARN

The sweep does not silently overwrite — if drift is large, a conductor
annotation is required before the tensor update lands.

Anchor cases: F012 (claimed |z|=6.15, clean re-measure 0.39/0.52);
              F014 (4.4% gap -> 3.41% observed); F011 (14% -> 38%);
              F010 (pooled 0.40 at n=71 -> 0.11 at n=75).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PriorRecord:
    """Prior measurement recorded in the tensor / signals.specimens."""
    feature_id: str
    effect_size: Optional[float]
    z_score: Optional[float]
    n_samples: Optional[int]
    source: str = ""          # commit / scorer / method note
    claim_class: str = ""     # which null class the prior used


@dataclass
class NewMeasurement:
    feature_id: str
    effect_size: Optional[float]
    z_score: Optional[float]
    n_samples: Optional[int]
    source: str = ""
    claim_class: str = ""


@dataclass
class Pattern19Result:
    verdict: str
    rationale: str
    provenance_delta: dict


def sweep(new: NewMeasurement, prior: Optional[PriorRecord]) -> Pattern19Result:
    if prior is None:
        return Pattern19Result(
            verdict="CLEAR",
            rationale=(
                f"{new.feature_id}: no prior record; Pattern 19 not applicable"
            ),
            provenance_delta={},
        )

    delta = {
        "feature_id": new.feature_id,
        "old": {
            "effect_size": prior.effect_size,
            "z_score": prior.z_score,
            "n_samples": prior.n_samples,
            "source": prior.source,
            "claim_class": prior.claim_class,
        },
        "new": {
            "effect_size": new.effect_size,
            "z_score": new.z_score,
            "n_samples": new.n_samples,
            "source": new.source,
            "claim_class": new.claim_class,
        },
    }

    # Sign flip on z_score => BLOCK (the sharpest kind of drift)
    sign_flip = False
    if (prior.z_score is not None and new.z_score is not None
            and abs(prior.z_score) > 1.0 and abs(new.z_score) > 1.0):
        sign_flip = (prior.z_score * new.z_score) < 0

    # Sample-size growth
    n_ratio = None
    if prior.n_samples and new.n_samples:
        n_ratio = new.n_samples / prior.n_samples
    big_n_growth = (n_ratio is not None) and (n_ratio >= 3.0)

    # Effect-size drift: symmetric ratio. "differs by > 3x" means
    # max(old/new, new/old) >= 3 — a factor of 3 either direction.
    eff_ratio = None
    if (prior.effect_size is not None and new.effect_size is not None
            and prior.effect_size != 0 and new.effect_size != 0):
        a, b = abs(prior.effect_size), abs(new.effect_size)
        eff_ratio = max(a, b) / max(min(a, b), 1e-12)
    big_effect_drift = (eff_ratio is not None) and (eff_ratio >= 3.0)

    # Claim-class / scorer change is a provenance shift worth flagging
    class_changed = (prior.claim_class and new.claim_class
                     and prior.claim_class != new.claim_class)

    if sign_flip:
        return Pattern19Result(
            verdict="BLOCK",
            rationale=(
                f"{new.feature_id}: z-score sign flip prior={prior.z_score} "
                f"-> new={new.z_score}. Conductor review required — the "
                "new measurement contradicts the old at sign level"
            ),
            provenance_delta=delta,
        )

    if big_n_growth and big_effect_drift:
        return Pattern19Result(
            verdict="WARN",
            rationale=(
                f"{new.feature_id}: stale prior — n grew {n_ratio:.1f}x "
                f"({prior.n_samples} -> {new.n_samples}) AND effect drifted "
                f"{eff_ratio:.1f}x ({prior.effect_size} -> {new.effect_size}). "
                "Investigate why before silent overwrite"
            ),
            provenance_delta=delta,
        )

    if big_effect_drift:
        return Pattern19Result(
            verdict="WARN",
            rationale=(
                f"{new.feature_id}: effect size drifted {eff_ratio:.1f}x "
                f"({prior.effect_size} -> {new.effect_size}) without n-scale "
                "change. Possible scorer / preprocessing drift"
            ),
            provenance_delta=delta,
        )

    if class_changed:
        return Pattern19Result(
            verdict="WARN",
            rationale=(
                f"{new.feature_id}: claim-class changed {prior.claim_class} "
                f"-> {new.claim_class}. Annotate the reason in provenance"
            ),
            provenance_delta=delta,
        )

    return Pattern19Result(
        verdict="CLEAR",
        rationale=(
            f"{new.feature_id}: new measurement consistent with prior "
            f"(eff_ratio={eff_ratio!r}, n_ratio={n_ratio!r})"
        ),
        provenance_delta=delta,
    )
