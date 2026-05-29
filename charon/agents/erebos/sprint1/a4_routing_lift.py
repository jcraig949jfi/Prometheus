"""Sprint-1 A4: routing-via-residue lift (Phase 2, ITER-48).

Hypothesis (from roadmap v2 line 86):
> "EIG of routing decisions when consulting kill_ledger vs
> round-robin"
> Pass: EIG ratio > 1.2 -> routing residue is actionable.

## EIG (Expected Information Gain) framing

For each routing decision the substrate makes, the choice is a
deterministic function of input signals:
  kp-routed:   plugin_choice = f(last_kill_pattern, state)
  round-robin: plugin_choice = g(last_plugin_id, state)

For deterministic routing functions, EIG ~ H(output) where H is
the entropy of the plugin distribution induced by walking the
input space.

  EIG_kp = H(plugin | kp drawn from KILL_PATTERN_REGISTRY)
  EIG_rr = H(plugin | round-robin walks _PLUGINS list)

A higher EIG_kp means kp routing's input signal (the 27-kp
registry) reaches MORE distinct plugin targets per decision than
round-robin's input signal (the 14-active-plugin cycle). The
ratio measures the information advantage.

## A4 protocol

1. Compute the plugin distribution induced by walking every kp
   in KILL_PATTERN_REGISTRY through
   _routing_action_to_plugin_id. Plugins that don't resolve
   (sentinel "none_claim_survives", etc.) contribute to a "no
   target" bucket.

2. Compute the plugin distribution that round-robin would walk
   in the same number of ticks (n_ticks = |REGISTRY|). Since
   round-robin cycles deterministically through _PLUGINS,
   plugin counts equal floor(n_ticks / n_active_plugins) or one
   more.

3. Compute Shannon entropy of each distribution in bits.

4. EIG ratio = H_kp / H_rr.

5. Pass if ratio > 1.20.

## Why this is the right structural measure

EIG-ratio is the substrate's "information per decision" given
its actual routing function. The test is independent of
verdict outcomes -- it asks whether the routing layer's input
signal (kp) carries strictly more information than round-
robin's input signal (last_plugin_id) in terms of plugin
diversity reachable.

If ratio <= 1.20, kp routing reaches fewer or comparably-few
plugins than round-robin given the registry size. The Layer-2
routing wire would not be providing a meaningful information
advantage; routing residue would not be actionable in the
EIG sense.
"""
from __future__ import annotations

import math
from collections import Counter

from charon.agents.erebos._kill_pattern_registry import (
    KILL_PATTERN_REGISTRY,
    routing_action_for,
)
from charon.agents.erebos._quarantine import is_quarantined
from charon.agents.erebos.generators import (
    REGISTRY,
    _PLUGINS,
    _routing_action_to_plugin_id,
)
from charon.agents.erebos.sprint1 import SprintResult


PASS_THRESHOLD_RATIO = 1.20


def _shannon_entropy_bits(counts: Counter) -> float:
    """Shannon entropy of a count distribution, in bits."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    H = 0.0
    for c in counts.values():
        if c == 0:
            continue
        p = c / total
        H -= p * math.log2(p)
    return H


def run_a4() -> SprintResult:
    """Execute A4 protocol; return verdict."""
    n_ticks = len(KILL_PATTERN_REGISTRY)

    # KP-routed distribution
    kp_picks: Counter = Counter()
    n_kp_unresolved = 0
    for kp_name in sorted(KILL_PATTERN_REGISTRY.keys()):
        action = routing_action_for(kp_name)
        target_id = (
            _routing_action_to_plugin_id(action) if action else None
        )
        if target_id is None or target_id not in REGISTRY:
            n_kp_unresolved += 1
            kp_picks["__unresolved__"] += 1
        else:
            kp_picks[target_id] += 1

    # Round-robin distribution: cycle through active plugins for
    # n_ticks ticks. Each active plugin gets either ceil or floor
    # (n_ticks / n_active).
    active_plugins = [
        p.id for p in _PLUGINS if not is_quarantined(p.id)
    ]
    n_active = len(active_plugins)
    rr_picks: Counter = Counter()
    for i in range(n_ticks):
        rr_picks[active_plugins[i % n_active]] += 1

    h_kp = _shannon_entropy_bits(kp_picks)
    h_rr = _shannon_entropy_bits(rr_picks)
    ratio = h_kp / h_rr if h_rr > 0 else float("inf")

    passed = ratio > PASS_THRESHOLD_RATIO

    distinct_kp_targets = sum(
        1 for k in kp_picks if k != "__unresolved__"
    )

    return SprintResult(
        experiment_id="A4",
        hypothesis=(
            "kp-routed selection's plugin-distribution entropy "
            "exceeds round-robin's by > 20% (kp signal is richer "
            "than last_plugin_id signal)"
        ),
        metric_name="eig_ratio_kp_over_rr",
        metric_value=ratio,
        pass_threshold=PASS_THRESHOLD_RATIO,
        comparator=">",
        passed=passed,
        protocol_summary=(
            f"For n_ticks={n_ticks} (= |KILL_PATTERN_REGISTRY|), "
            f"compute plugin-pick distribution under kp routing "
            f"vs round-robin (cycling {n_active} active plugins). "
            f"EIG ratio = H_kp / H_rr in bits."
        ),
        notes=(
            f"n_ticks={n_ticks}; n_active_plugins={n_active}; "
            f"H_kp={h_kp:.4f} bits; H_rr={h_rr:.4f} bits; "
            f"ratio={ratio:.4f}; "
            f"distinct_kp_targets={distinct_kp_targets}; "
            f"n_kp_unresolved={n_kp_unresolved}"
        ),
    )
