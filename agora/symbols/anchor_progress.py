"""ANCHOR_PROGRESS_LEDGER — mutable sidecar for per-symbol anchor state.

Stores post-promotion anchor evolution (cross-resolvers, tier upgrades,
forward-path applications) in Redis HASH `symbols:<NAME>:anchor_progress`
keyed by anchor_id. Parallels T2 lifecycle-status pattern: mutable
metadata adjacent to immutable `:v<N>:def`.

Rule 3 immutability is PRESERVED: the :def blob is never touched. This
sidecar is a separate key space.

Spec: see harmonia/memory/symbols/CANDIDATES.md §ANCHOR_PROGRESS_LEDGER.
First deployment: FRAME_INCOMPATIBILITY_TEST@v2 (2026-04-23).
"""
import json
import time
from typing import Any
from .resolve import _get_redis

_VALID_TIERS = {
    "shadow",
    "shadow_contested",
    "surviving_candidate",
    "coordinate_invariant",
}

_TIER_ORDER = {
    "shadow": 0,
    "shadow_contested": 0,
    "surviving_candidate": 1,
    "coordinate_invariant": 2,
}


def _progress_key(name: str) -> str:
    return f"symbols:{name}:anchor_progress"


def update_anchor_progress(
    name: str,
    anchor_id: str,
    *,
    resolver: str | None = None,
    cross_resolver_add: str | None = None,
    tier: str | None = None,
    forward_path_application_add: str | None = None,
    open_question_add: str | None = None,
    rationale: str = "",
    allow_tier_downgrade: bool = False,
) -> dict:
    """Append-only update of anchor progress state.

    - `cross_resolver_add` / `forward_path_application_add` / `open_question_add`
      append to the respective list if not already present (idempotent).
    - `tier` must be in {_VALID_TIERS}; downgrade requires `allow_tier_downgrade=True`
      AND a non-empty `rationale`.
    - `resolver` is set only if not already set (immutable primary resolver).

    Returns the updated record.
    """
    r = _get_redis()
    key = _progress_key(name)
    raw = r.hget(key, anchor_id)
    if raw:
        rec = json.loads(raw)
    else:
        rec = {
            "anchor_id": anchor_id,
            "resolver": None,
            "cross_resolvers": [],
            "tier": "shadow",
            "forward_path_applications": [],
            "open_questions": [],
            "tier_upgrade_history": [],
        }

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if resolver is not None:
        if rec["resolver"] is None:
            rec["resolver"] = resolver
        elif rec["resolver"] != resolver:
            raise ValueError(
                f"resolver already set to {rec['resolver']!r}; "
                f"cannot reassign to {resolver!r}. "
                "A different agent re-resolving the anchor should be "
                "recorded as cross_resolver_add."
            )

    if cross_resolver_add is not None:
        if cross_resolver_add != rec.get("resolver") and cross_resolver_add not in rec["cross_resolvers"]:
            rec["cross_resolvers"].append(cross_resolver_add)

    if forward_path_application_add is not None:
        if forward_path_application_add not in rec["forward_path_applications"]:
            rec["forward_path_applications"].append(forward_path_application_add)

    if open_question_add is not None:
        if open_question_add not in rec["open_questions"]:
            rec["open_questions"].append(open_question_add)

    if tier is not None:
        if tier not in _VALID_TIERS:
            raise ValueError(f"invalid tier {tier!r}; valid: {sorted(_VALID_TIERS)}")
        old_tier = rec["tier"]
        if tier != old_tier:
            new_rank = _TIER_ORDER[tier]
            old_rank = _TIER_ORDER[old_tier]
            if new_rank < old_rank and not allow_tier_downgrade:
                raise ValueError(
                    f"tier downgrade {old_tier} -> {tier} requires "
                    "allow_tier_downgrade=True and a non-empty rationale."
                )
            if new_rank < old_rank and not rationale:
                raise ValueError("tier downgrade requires non-empty rationale")
            rec["tier_upgrade_history"].append({
                "from": old_tier,
                "to": tier,
                "at": now,
                "rationale": rationale,
            })
            rec["tier"] = tier

    rec["updated_at"] = now
    r.hset(key, anchor_id, json.dumps(rec))
    return rec


def get_anchor_progress(name: str, anchor_id: str | None = None) -> dict:
    """Read anchor progress for a symbol.

    If anchor_id is None, returns all anchors as {anchor_id: record}.
    Otherwise returns the single record for that anchor.
    """
    r = _get_redis()
    key = _progress_key(name)
    if anchor_id is not None:
        raw = r.hget(key, anchor_id)
        return json.loads(raw) if raw else {}
    all_raw = r.hgetall(key)
    return {aid: json.loads(raw) for aid, raw in all_raw.items()}


def list_anchor_progress_symbols() -> list[str]:
    """Return all symbol names that have an anchor_progress sidecar."""
    r = _get_redis()
    prefix = "symbols:"
    suffix = ":anchor_progress"
    names = []
    for k in r.scan_iter(match=f"{prefix}*{suffix}"):
        inner = k[len(prefix):-len(suffix)]
        names.append(inner)
    return sorted(names)


def export_progress_md(name: str) -> str:
    """Export anchor progress as human-readable Markdown."""
    data = get_anchor_progress(name)
    if not data:
        return f"# {name} — anchor progress\n\n(no anchor progress recorded)\n"
    lines = [f"# {name} — anchor progress\n"]
    for anchor_id, rec in sorted(data.items()):
        lines.append(f"## {anchor_id}")
        lines.append(f"- **Tier:** {rec['tier']}")
        lines.append(f"- **Resolver:** {rec.get('resolver') or '(none)'}")
        xr = ", ".join(rec.get("cross_resolvers") or []) or "(none)"
        lines.append(f"- **Cross-resolvers:** {xr}")
        fp = ", ".join(rec.get("forward_path_applications") or []) or "(none)"
        lines.append(f"- **Forward-path applications:** {fp}")
        hist = rec.get("tier_upgrade_history") or []
        if hist:
            lines.append("- **Tier history:**")
            for h in hist:
                r2 = h.get("rationale") or ""
                lines.append(f"  - {h['at']} {h['from']} -> {h['to']}: {r2}")
        oq = rec.get("open_questions") or []
        if oq:
            lines.append("- **Open questions:**")
            for q in oq:
                lines.append(f"  - {q}")
        lines.append("")
    return "\n".join(lines)
