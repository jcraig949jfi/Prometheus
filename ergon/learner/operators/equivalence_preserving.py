"""equivalence_preserving operator class — math-grounded mutations.

Per pivot/ergon_learner_v0.5_design_2026-05-05.md §3.4 W2.7 (Aporia artifact):

    "the most undervalued of the three [missing operator classes] —
     grounds mutation in real math instead of syntactic perturbation."

This operator class mutates by applying mathematically-defined moves that
preserve known invariants of the underlying object (isogeny on elliptic
curves, Reidemeister on knots, Hecke on modular forms, quadratic twists,
etc.). Each instance is keyed to an arsenal `equivalence_class` tag —
the canonicalizer subclass that defines what's invariant.

v0.5 ships ONE instance: **isogeny-on-elliptic-curve**. An isogeny
phi: E -> E' is a non-constant morphism of EC's; isogenous curves share
conductor, L-function, and (per LMFDB convention) live in the same
isogeny class label (e.g. "11.a1" and "11.a3" both have class "11.a").
The j-invariant is NOT preserved across non-trivial isogenies; the
arsenal-level invariant is the *isogeny class*, which is precisely what
the LMFDB canonical labeling encodes.

Full operator class (Reidemeister, Hecke, twists) deferred to v1.0.

Strategy for the spike:
  1. Find a node in the parent genome whose arg_bindings include an
     EC label literal (sampler `ec_label`).
  2. Look up the LMFDB isogeny class for that label.
  3. Pick a different sibling label from the same isogeny class.
  4. Substitute. Result: same isogeny class -> arsenal equivalence class
     `variety_fingerprint` invariants preserved at the LMFDB level.

If the cremona local mirror is absent OR no sibling exists, the operator
falls back to a hand-curated isogeny-class table covering the canonical
small-conductor classes (11.a, 14.a, 15.a, 17.a, 19.a, 21.a, 26.a, 26.b,
33.a, 37.a, 37.b, 38.a, 38.b, 50.a). Lineage tag is set regardless.

Lineage tag: "equivalence_preserving"
"""
from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional, Tuple

from ergon.learner.genome import Genome, NodeRef, validate_dag_invariants
from ergon.learner.operators.base import fresh_genome


# Hand-curated fallback isogeny-class table — covers the EC labels in
# `sample_arg("ec_label")` plus a few low-conductor neighborhoods. Keyed
# by LMFDB-style label "<cond>.<class><idx>"; values are siblings sharing
# the same "<cond>.<class>" isogeny class. Source: LMFDB ec_curvedata
# (cross-checked against Cremona ecdata 2026-05-05).
_FALLBACK_ISOGENY_CLASSES: Dict[str, Tuple[str, ...]] = {
    "11.a":   ("11.a1", "11.a2", "11.a3"),
    "14.a":   ("14.a1", "14.a2", "14.a3", "14.a4", "14.a5", "14.a6"),
    "15.a":   ("15.a1", "15.a2", "15.a3", "15.a4", "15.a5", "15.a6", "15.a7", "15.a8"),
    "17.a":   ("17.a1", "17.a2", "17.a3", "17.a4"),
    "19.a":   ("19.a1", "19.a2", "19.a3"),
    "21.a":   ("21.a1", "21.a2", "21.a3", "21.a4", "21.a5", "21.a6"),
    "26.a":   ("26.a1", "26.a2", "26.a3"),
    "26.b":   ("26.b1", "26.b2"),
    "33.a":   ("33.a1", "33.a2", "33.a3", "33.a4"),
    "37.a":   ("37.a1",),  # rank-1 singleton class
    "37.b":   ("37.b1", "37.b2", "37.b3"),
    "38.a":   ("38.a1", "38.a2", "38.a3"),
    "38.b":   ("38.b1", "38.b2", "38.b3", "38.b4"),
    "50.a":   ("50.a1", "50.a2", "50.a3", "50.a4"),
    "389.a":  ("389.a1",),  # rank-2 singleton
    "5077.a": ("5077.a1",),  # rank-3 singleton
}

# Pattern for LMFDB-style EC label: <conductor>.<class_letters><idx>
_EC_LABEL_RE = re.compile(r"^(\d+)\.([a-z]+)(\d+)$")
# Cremona-style label: <conductor><class_letters><idx>
_CREMONA_LABEL_RE = re.compile(r"^(\d+)([a-z]+)(\d+)$")


def _isogeny_class_of(label: str) -> Optional[str]:
    """Return the isogeny-class portion (e.g. '11.a' from '11.a1')."""
    m = _EC_LABEL_RE.match(label)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    m = _CREMONA_LABEL_RE.match(label)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    return None


def _siblings_in_class(label: str) -> Tuple[str, ...]:
    """Return all known siblings of `label` in its isogeny class.

    Tries the cremona local mirror first; falls back to the
    hand-curated table if the mirror is absent or the class is unknown.
    """
    cls = _isogeny_class_of(label)
    if cls is None:
        return ()

    # Try local cremona mirror first.
    try:
        from prometheus_math.databases import cremona as _cremona
        if _cremona.has_local_mirror():
            m = _EC_LABEL_RE.match(label) or _CREMONA_LABEL_RE.match(label)
            if m:
                cond = int(m.group(1))
                cls_letter = m.group(2)
                rows = _cremona.elliptic_curves(
                    conductor=cond,
                    fall_back_to_lmfdb=False,
                )
                siblings = tuple(
                    sorted({
                        r.get("lmfdb_label")
                        for r in rows
                        if r.get("isogeny_class") == cls_letter
                        and r.get("lmfdb_label")
                    })
                )
                if siblings:
                    return siblings
    except Exception:
        pass

    return _FALLBACK_ISOGENY_CLASSES.get(cls, ())


def _is_ec_label_literal(value: Any) -> bool:
    """Heuristic: looks like an EC label string."""
    if not isinstance(value, str):
        return False
    return bool(_EC_LABEL_RE.match(value) or _CREMONA_LABEL_RE.match(value))


class EquivalencePreservingOperator:
    """Mutate by applying invariant-preserving math moves.

    v0.5 single instance: isogeny-on-EC. The mutation finds an EC-label
    literal in the parent genome and replaces it with a sibling in the
    same isogeny class. The isogeny class label (and therefore the
    conductor, L-function, and arsenal `variety_fingerprint` equivalence
    class per LMFDB) is preserved across the mutation.

    If the parent contains no EC-label literal, the operator falls back
    to fresh_genome (tagged with this operator's lineage class).
    """

    operator_class = "equivalence_preserving"
    instance = "isogeny_on_ec"

    def __init__(self, allow_self_swap: bool = False):
        # If True, sibling-pick may yield the original label (no-op) when
        # the class is a singleton. Default: prefer non-trivial siblings;
        # singletons fall back to fresh.
        self.allow_self_swap = allow_self_swap

    def mutate(
        self,
        parent: Optional[Genome],
        rng: random.Random,
        atom_pool: Dict[str, Any],
    ) -> Genome:
        """Apply an isogeny-class-preserving mutation to the parent."""
        if parent is None or not parent.nodes:
            return fresh_genome(atom_pool, rng, "equivalence_preserving")

        # Find every (node_idx, binding_idx, label) triple where the
        # parent has an EC-label literal binding.
        candidates: List[Tuple[int, int, str]] = []
        for n_idx, node in enumerate(parent.nodes):
            for b_idx, (kind, value) in enumerate(node.arg_bindings):
                if kind == "literal" and _is_ec_label_literal(value):
                    candidates.append((n_idx, b_idx, value))

        if not candidates:
            return fresh_genome(atom_pool, rng, "equivalence_preserving")

        # Pick one EC-label binding to mutate.
        n_idx, b_idx, old_label = rng.choice(candidates)
        siblings = _siblings_in_class(old_label)
        non_self = [s for s in siblings if s != old_label]

        if not non_self:
            if self.allow_self_swap and siblings:
                new_label = old_label  # singleton; explicit no-op
            else:
                # Singleton class with no siblings — fall back to fresh
                # rather than emit a no-op child. The lineage tag still
                # marks intent.
                return fresh_genome(atom_pool, rng, "equivalence_preserving")
        else:
            new_label = rng.choice(non_self)

        # Substitute the binding.
        old_node = parent.nodes[n_idx]
        new_bindings = list(old_node.arg_bindings)
        new_bindings[b_idx] = ("literal", new_label)
        new_node = NodeRef(
            callable_ref=old_node.callable_ref,
            arg_bindings=tuple(new_bindings),
        )
        new_nodes = list(parent.nodes)
        new_nodes[n_idx] = new_node

        # Carry the math-grounded mutation provenance in metadata so
        # downstream tooling can audit which equivalence move fired.
        metadata = dict(parent.metadata)
        metadata["equivalence_move"] = {
            "instance": self.instance,
            "from_label": old_label,
            "to_label": new_label,
            "isogeny_class": _isogeny_class_of(old_label),
        }

        child = Genome(
            nodes=tuple(new_nodes),
            target_predicate=parent.target_predicate,
            mutation_operator_class="equivalence_preserving",
            parent_hash=parent.content_hash(),
            metadata=metadata,
        )
        validate_dag_invariants(child)
        return child
