"""sigma_kernel.caveats — preset caveat tokens + validation helper.

Operationalizes the C3 fix from
``stoa/discussions/2026-05-03-team-review-techne-bind-eval-and-pivot.md``:
caveats live as TYPED FIELDS on the CLAIM. Documents referencing the
result inherit them automatically rather than maintaining them at every
documentation layer.

This module defines a curated list of standardized caveat tokens
(``KNOWN_CAVEATS``) covering the common substrate failure modes named in
the team review and in ``feedback_ai_to_ai_inflation``. The list is
*open* — callers may pass arbitrary strings; this module's helper only
warns when a passed token looks like a misspelling of a known one.

Design rules (substrate-grade):
- Caveats are **immutable** once attached to a Claim — like provenance.
- The preset list **may grow** by stoa amendment.
- The preset list **may not rename or remove** existing tokens (that
  would mutate the semantics of historical claims).
- Validation **warns** but does not reject — the substrate is permissive
  at write, strict at hash.

See ``stoa/proposals/2026-05-04-techne-caveat-as-metadata-schema.md``
for the full schema rationale.
"""
from __future__ import annotations

import warnings


# ---------------------------------------------------------------------------
# The preset list
# ---------------------------------------------------------------------------
#
# Each entry maps a stable token to a short rationale. The token is what
# gets persisted in claims.caveats and propagated through TRACE. The
# rationale is for humans reading the substrate — it lives next to the
# token here, not in the persisted JSON, so the persisted form stays
# small and the rationale can be revised without touching old claims.
#
# Token format: snake_case, no whitespace, no leading digit. Validation
# warns on near-misses (e.g. "small-n" → "small_n").

KNOWN_CAVEATS: dict[str, str] = {
    # --- Sample-size / replication
    "small_n": (
        "sample size below substrate threshold of 5+ seeds; per "
        "feedback_replicate_seeds, replicate before citing"
    ),
    "single_seed": (
        "result from a single seed; replicate with 5+ before citing as a "
        "real lift"
    ),

    # --- Agent / learner pathology
    "mode_collapse": (
        "agent converged to a single basin; not exploring; lift number "
        "may be a fixed-point artifact"
    ),

    # --- Discovery vs rediscovery
    "rediscovery_not_discovery": (
        "result reproduces a known catalog entry (e.g. Salem cluster, "
        "Mossinghoff list); not new mathematics"
    ),

    # --- Battery / instrument
    "synthetic_battery_used": (
        "kill_path used a surrogate or smoke battery, not the real Charon "
        "F1-F20 battery; verdict is provisional"
    ),
    "ground_truth_absent": (
        "no published reference for the claimed structure; verification "
        "pending; cite with caution"
    ),

    # --- Environment shape (the +53.1% lift problem from C3)
    "bandit_structure": (
        "env is structurally a near-trivial bandit (>50% of actions are "
        "jackpots); RL lift number is suspect; see feedback_ai_to_ai_inflation"
    ),

    # --- Substrate-internal hygiene
    "unverified_callable_source": (
        "callable source was unavailable at BIND time (e.g. builtin or "
        "C extension); callable_hash is repr-based, not source-based"
    ),
    "cost_model_unenforced_dimension": (
        "declared cost dimension (e.g. memory_mb, oracle_calls) is not "
        "actually measured; RL agents will route around it"
    ),

    # --- Meta / instrument
    "instrument_drift_suspected": (
        "claim should be META_CLAIM against the battery, not the original "
        "hypothesis; OPERA-style pattern"
    ),
    "headline_number_pre_calibration": (
        "result reported before the calibration anchor sweep; numerical "
        "magnitude may shift after calibration"
    ),

    # --- FALSIFY-internal
    "falsify_warn": (
        "FALSIFY returned a WARN verdict; rationale appended at this "
        "caveat's prefix (truncated to 80 chars)"
    ),
}

# Maximum length for a single caveat string. Prevents accidental dump
# of a megabyte of rationale into the claims table. Truncation, not
# rejection: the substrate is permissive at write.
MAX_CAVEAT_LENGTH = 1000


# ---------------------------------------------------------------------------
# Validation / normalization helper
# ---------------------------------------------------------------------------


def _looks_like_misspelling(token: str, known: str) -> bool:
    """Cheap fuzzy: same alpha-only chars, just punctuation/case differ.

    Catches common variants like ``small-n``, ``Small_N``, ``small n``
    versus the canonical ``small_n``. Does NOT do real edit-distance —
    this is a check for "did the caller mean this token but typo the
    separator?" not a spell-checker.
    """
    norm_token = "".join(c.lower() for c in token if c.isalnum())
    norm_known = "".join(c.lower() for c in known if c.isalnum())
    return norm_token == norm_known and token != known


def validate_caveats(caveats: list[str] | None) -> list[str]:
    """Validate a caller-provided caveats list. Return the cleaned list.

    Behavior:
    - ``None`` becomes ``[]``.
    - Non-string items raise ``TypeError`` (we hash + persist these).
    - Items > ``MAX_CAVEAT_LENGTH`` chars are truncated with a suffix
      ``...[truncated]`` so the truncation is visible.
    - Duplicates are de-duplicated, preserving first-occurrence order.
    - Items that look like misspellings of preset tokens emit a
      ``UserWarning`` naming the suspected canonical form. The token
      is still accepted as-is (substrate is permissive at write).
    - Unknown tokens (not in ``KNOWN_CAVEATS`` and not similar to any
      preset) are accepted silently.

    Returns the cleaned, deduplicated list.
    """
    if caveats is None:
        return []
    if not isinstance(caveats, (list, tuple)):
        raise TypeError(
            f"caveats must be a list of strings; got {type(caveats).__name__}"
        )

    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in caveats:
        if not isinstance(raw, str):
            raise TypeError(
                f"each caveat must be a string; got {type(raw).__name__}"
            )

        # Truncate, not reject. The truncation is visible in the persisted
        # form so a human reading the substrate can see what happened.
        if len(raw) > MAX_CAVEAT_LENGTH:
            tok = raw[: MAX_CAVEAT_LENGTH - len("...[truncated]")] + "...[truncated]"
        else:
            tok = raw

        if tok in seen:
            continue

        # Misspelling check against the preset list. Only fires on
        # tokens NOT exactly in the preset list — exact matches are
        # canonical and skip this loop entirely.
        if tok not in KNOWN_CAVEATS:
            for known in KNOWN_CAVEATS:
                if _looks_like_misspelling(tok, known):
                    warnings.warn(
                        f"caveat {tok!r} looks like a misspelling of preset "
                        f"{known!r}; accepted as-is, but consider canonical form",
                        UserWarning,
                        stacklevel=3,
                    )
                    break
            # FALSIFY-warn caveats use the prefix form ``falsify_warn:...``
            # — handle them as canonical even though they don't exact-match.
            if tok.startswith("falsify_warn:"):
                pass  # canonical form; no warning

        seen.add(tok)
        cleaned.append(tok)

    return cleaned


def is_known(token: str) -> bool:
    """True iff ``token`` is in the canonical preset list (exact match).

    Note: ``"falsify_warn:<rationale>"`` returns False here — only the
    bare ``"falsify_warn"`` token matches exactly. The prefix form is
    handled separately by FALSIFY.
    """
    return token in KNOWN_CAVEATS


def describe(token: str) -> str | None:
    """Human-readable rationale for ``token`` if it's in the preset list,
    else ``None``. Useful for documentation generators that want to
    render a caveat list as a footnote."""
    return KNOWN_CAVEATS.get(token)


__all__ = [
    "KNOWN_CAVEATS",
    "MAX_CAVEAT_LENGTH",
    "validate_caveats",
    "is_known",
    "describe",
]
