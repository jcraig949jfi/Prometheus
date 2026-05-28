"""Loader-debt budget enforcement + plugin quarantine.

Per Erebos v3 §4.8 + DR amendment. Plugins without composition
loaders cannot accumulate unbounded *_pending emissions in the
ledger — they pollute substrate value metrics (per ITER-13 G15
finding: 73.8% of v1 MI signal was control-flow rows). This
module enforces:

- A plugin may emit at most MAX_PENDING_EMISSIONS short-circuit
  rows OR run for MAX_QUARANTINE_DAYS days without a composition
  loader, whichever comes first.
- After that cap, the plugin is QUARANTINED — its applicable()
  returns False on production runs; explicit test fixtures can
  still invoke it.
- Quarantined plugins are listed in pivot/erebos_quarantine.md
  with their unblock_criterion.
- Revival path: ship the composition loader. There is no other
  path.

Reading: pivot/erebos_v3_synthesis_2026-05-27.md §4.8
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


MAX_PENDING_EMISSIONS = 200
MAX_QUARANTINE_DAYS = 30


@dataclass(frozen=True)
class QuarantineRule:
    """Per-plugin quarantine entry."""
    plugin_id: str
    quarantined_since: str        # ISO date
    unblock_criterion: str        # specific path to revival
    quarantine_class: str         # "loader_missing" | "infrastructure_blocked"
                                  # | "vacuous_by_design"
    pending_emission_count: int = 0  # tracked at runtime; 0 for static decl

    def __post_init__(self) -> None:
        valid_classes = {
            "loader_missing", "infrastructure_blocked", "vacuous_by_design"
        }
        if self.quarantine_class not in valid_classes:
            raise ValueError(
                f"QuarantineRule {self.plugin_id!r}: invalid "
                f"quarantine_class {self.quarantine_class!r}; must be "
                f"one of {valid_classes}"
            )
        if not self.unblock_criterion:
            raise ValueError(
                f"QuarantineRule {self.plugin_id!r}: unblock_criterion "
                f"cannot be empty"
            )


class LoaderDebtCapExceededError(Exception):
    """Raised when a plugin exceeds MAX_PENDING_EMISSIONS while
    still loader-less."""


# Static quarantine rules. Updated by Phase 1+ as plugins gain
# loaders (entries removed) or new plugins are added (entries
# added). Reflects the 14/25 loader coverage state at v0.33.
QUARANTINE_RULES: dict[str, QuarantineRule] = {
    # ---------- 7 plain quarantine: could ship Mahler-context loader
    "g01_intersection": QuarantineRule(
        plugin_id="g01_intersection",
        quarantined_since="2026-05-27",
        unblock_criterion="ship composition_g01_mahler_intersection.py loader",
        quarantine_class="loader_missing",
    ),
    "g05_confound_swap": QuarantineRule(
        plugin_id="g05_confound_swap",
        quarantined_since="2026-05-27",
        unblock_criterion="ship composition_g05_mahler_stratified_resample.py loader",
        quarantine_class="loader_missing",
    ),
    "g06_null_space": QuarantineRule(
        plugin_id="g06_null_space",
        quarantined_since="2026-05-27",
        unblock_criterion="ship composition_g06_mahler_void_objects.py loader",
        quarantine_class="loader_missing",
    ),
    "g12_invariant_substitution": QuarantineRule(
        plugin_id="g12_invariant_substitution",
        quarantined_since="2026-05-27",
        unblock_criterion="ship composition_g12_mahler_substitution.py loader",
        quarantine_class="loader_missing",
    ),
    "g13_relation_weakening": QuarantineRule(
        plugin_id="g13_relation_weakening",
        quarantined_since="2026-05-27",
        unblock_criterion="ship composition_g13_mahler_predicate_weakening.py loader",
        quarantine_class="loader_missing",
    ),
    "g14_relation_strengthening": QuarantineRule(
        plugin_id="g14_relation_strengthening",
        quarantined_since="2026-05-27",
        unblock_criterion="ship composition_g14_mahler_predicate_strengthening.py loader",
        quarantine_class="loader_missing",
    ),
    "g22_subgraph_clique": QuarantineRule(
        plugin_id="g22_subgraph_clique",
        quarantined_since="2026-05-27",
        unblock_criterion="ship composition_g22_ledger_clique_master_property.py loader",
        quarantine_class="loader_missing",
    ),
    # ---------- 3 infrastructure-blocked per v3 whitepaper §6
    "g07_analogy": QuarantineRule(
        plugin_id="g07_analogy",
        quarantined_since="2026-05-27",
        unblock_criterion=(
            "BSD-context infrastructure: per-domain dataset accessor + "
            "cross-domain translation table + re-run primitive. "
            "Estimated 2-3 iterations of BSD infra work."
        ),
        quarantine_class="infrastructure_blocked",
    ),
    "g08_dimensional_lift": QuarantineRule(
        plugin_id="g08_dimensional_lift",
        quarantined_since="2026-05-27",
        unblock_criterion=(
            "Ergon ML pipeline: per-parent dataset accessor + Ridge/GBT "
            "k-fold held-out + OOD validation. Timeline depends on "
            "Ergon's roadmap; not Erebos-blocked."
        ),
        quarantine_class="infrastructure_blocked",
    ),
    "g21_isomorphism_functor": QuarantineRule(
        plugin_id="g21_isomorphism_functor",
        quarantined_since="2026-05-27",
        unblock_criterion=(
            "Per-domain morphism enumerators + SageMath integration. "
            "Estimated 3-5 iterations + SageMath wiring. Likely "
            "deferred to v1.0+."
        ),
        quarantine_class="infrastructure_blocked",
    ),
    # ---------- 1 vacuous-by-design
    "g20_instrument_disagreement": QuarantineRule(
        plugin_id="g20_instrument_disagreement",
        quarantined_since="2026-05-27",
        unblock_criterion=(
            "Lethe v2 ships false-form-fired emissions on modern LLM "
            "cascades. May never need to ship if modern cascade stays "
            "accurate; architectural slot reserved."
        ),
        quarantine_class="vacuous_by_design",
    ),
}


def is_quarantined(plugin_id: str) -> bool:
    """True if plugin is in the quarantine registry."""
    return plugin_id in QUARANTINE_RULES


def quarantine_rule_for(plugin_id: str) -> Optional[QuarantineRule]:
    """Return the QuarantineRule for plugin_id, or None if active."""
    return QUARANTINE_RULES.get(plugin_id)


def check_emission_cap(
    plugin_id: str, current_pending_count: int
) -> None:
    """Raises LoaderDebtCapExceededError if the plugin has emitted
    MORE than MAX_PENDING_EMISSIONS short-circuit rows AND is still
    loader-less.

    Called by the daemon's emission path so the cap is enforced
    incrementally rather than via a periodic sweep.
    """
    if current_pending_count <= MAX_PENDING_EMISSIONS:
        return
    if is_quarantined(plugin_id):
        # Already quarantined; should not have emitted at all.
        raise LoaderDebtCapExceededError(
            f"Plugin {plugin_id!r} is QUARANTINED but emitted "
            f"{current_pending_count} pending rows (cap "
            f"{MAX_PENDING_EMISSIONS}). The applicable() filter should "
            f"have prevented this — investigate the production path."
        )
    raise LoaderDebtCapExceededError(
        f"Plugin {plugin_id!r} emitted {current_pending_count} pending "
        f"rows without a composition loader (cap "
        f"{MAX_PENDING_EMISSIONS}). Either ship the loader or add a "
        f"QuarantineRule to charon/agents/erebos/_quarantine.py."
    )


def quarantine_class_counts() -> dict[str, int]:
    """Aggregate count of plugins by quarantine class."""
    counts: dict[str, int] = {}
    for rule in QUARANTINE_RULES.values():
        counts[rule.quarantine_class] = counts.get(rule.quarantine_class, 0) + 1
    return counts


def all_quarantined_plugins() -> list[str]:
    """Return sorted list of currently-quarantined plugin IDs."""
    return sorted(QUARANTINE_RULES.keys())


def unquarantine(plugin_id: str) -> None:
    """Test/admin helper — remove plugin from quarantine registry.
    Production path: ship the loader, then remove the entry."""
    QUARANTINE_RULES.pop(plugin_id, None)


def restore_quarantine_state(rules: dict[str, QuarantineRule]) -> None:
    """Test helper — restore the registry to a snapshot state."""
    QUARANTINE_RULES.clear()
    QUARANTINE_RULES.update(rules)
