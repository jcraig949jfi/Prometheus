"""Provenance-carrying derivation of radius-3 rule tables (pure library).

Added 2026-09-16 on THEO-REQ-005 (table-level intervention: ablate or
substitute entries) and THEO-REQ-003 (composition of two same-kind
mechanisms), both routed to this seat as the owner of the evca semantics
(roles/Archaeon/INBOX_THEOPHRASTUS_REQ003_NO_READER_2026-09-14.md
recommends Herakles; no ruling has been posted at the time of writing, and
this module is the LIBRARY half either way: it mints nothing).

WHAT THIS IS. A derivation takes one or two parent rule tables and an
operator with explicit parameters, and returns a RECORD: the child table in
the library's canonical encoding, the parents by content-derived id, the
operator and its parameters in canonical form, and a digest over all of
that. The record is what a lineage row (PEW `fossil_players`:
`parent_player`, `mutation_ref`) needs and does not have today, when the only
way to run a modified rule is to submit a new `rule_hex` with no recorded
relation to anything.

WHAT THIS IS NOT. It does not write a player, a row or a file, and it does
not decide who does. Two facts are deliberately separated:

    child_player_id   CONTENT-derived: `evca:r3:<32 hex>`. Two routes to the
                      same table are one mechanism and one player. This is the
                      convention answered to Theophrastus's question of
                      2026-09-13 (comms #242) and it holds for RECOVERED
                      specimens too: "GKL" is a label, the table is the player.
    derivation_id     ROUTE-derived: a digest over (operator, parameters,
                      parents, child). Two routes to the same child are two
                      derivations. A lineage row keys on this.

A child that equals one of its parents is returned with `identity` True and
is never silently presented as a new mechanism.

PURITY. No I/O, no global RNG, no top-level execution. Every function
returns new objects. Same contract as `core`.
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

from .core import (EvcaError, RADIUS, TABLE_BITS, decode_table,
                   encode_table, reflect_table, complement_table,
                   require_table)

#: Prefix of a content-derived player id for a radius-3 table.
PLAYER_ID_PREFIX = "evca:r%d:" % RADIUS
#: Record kind, so a reader can refuse anything else.
RECORD_KIND = "evca_derived_rule_v1"
#: The operators this module implements. A name outside this set is refused.
OPERATORS = ("edit_entries", "crossover_mask", "reflect", "complement",
             "reflect_complement")


def canonical_hex(rule_hex: str) -> str:
    """The one spelling of a table: lowercase, no separators, 32 digits."""
    return encode_table(decode_table(rule_hex))


def player_id(rule_hex: str) -> str:
    """`evca:r3:<canonical hex>`. Derived from content; nobody mints it."""
    return PLAYER_ID_PREFIX + canonical_hex(rule_hex)


def rule_hex_of_player(pid: str) -> str:
    """Inverse of `player_id`; refuses any other id form."""
    if not isinstance(pid, str) or not pid.startswith(PLAYER_ID_PREFIX):
        raise EvcaError("not a %s<hex> player id: %r" % (PLAYER_ID_PREFIX, pid))
    return canonical_hex(pid[len(PLAYER_ID_PREFIX):])


def derivation_digest(operator: str, params: Dict[str, object],
                      parents: Sequence[str], child_hex: str) -> str:
    """sha256 over the canonical JSON of the route. Key order is fixed."""
    doc = {"kind": RECORD_KIND, "operator": operator, "params": params,
           "parents": list(parents), "child_rule_hex": child_hex}
    blob = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("ascii")
    return "sha256:" + hashlib.sha256(blob).hexdigest()[:32]


def _record(operator: str, params: Dict[str, object], parent_hexes: List[str],
            child: np.ndarray, extra: Dict[str, object]) -> Dict[str, object]:
    child_hex = encode_table(child)
    parents = [player_id(h) for h in parent_hexes]
    out = {
        "kind": RECORD_KIND,
        "operator": operator,
        "operator_params": params,
        "parents": parents,
        "parent_rule_hexes": [canonical_hex(h) for h in parent_hexes],
        "child_rule_hex": child_hex,
        "child_player_id": player_id(child_hex),
        "derivation_id": derivation_digest(operator, params, parents,
                                           child_hex),
        "identity": child_hex in [canonical_hex(h) for h in parent_hexes],
    }
    out.update(extra)
    return out


# ---------------------------------------------------------------------------
# edit_entries: ablate or substitute table entries (THEO-REQ-005)
# ---------------------------------------------------------------------------

def normalise_edits(edits: Iterable[Tuple[int, int]]) -> List[List[int]]:
    """Sorted, validated [[index, bit], ...]. Duplicates and ranges refused."""
    seen = set()
    out = []
    for item in edits:
        try:
            idx, bit = item
        except (TypeError, ValueError):
            raise EvcaError("each edit is (entry index, new bit), got %r"
                            % (item,))
        if isinstance(idx, bool) or not isinstance(idx, (int, np.integer)):
            raise EvcaError("entry index must be an integer, got %r" % (idx,))
        if not (0 <= idx < TABLE_BITS):
            raise EvcaError("entry index %d is outside [0, %d]"
                            % (idx, TABLE_BITS - 1))
        if isinstance(bit, bool) or bit not in (0, 1):
            raise EvcaError("new bit must be 0 or 1, got %r" % (bit,))
        if idx in seen:
            raise EvcaError("entry %d is edited twice; one edit per entry"
                            % idx)
        seen.add(int(idx))
        out.append([int(idx), int(bit)])
    out.sort()
    return out


def derive_edit(parent_hex: str, edits: Iterable[Tuple[int, int]]
                ) -> Dict[str, object]:
    """Child = parent with the listed entries set to the listed bits.

    An edit that sets an entry to the value it already has is kept in the
    record (it is what was asked) and counted in `n_no_op_edits`, so a
    child that equals its parent is explained rather than surprising.
    """
    parent = decode_table(parent_hex)
    norm = normalise_edits(edits)
    child = parent.copy()
    no_op = 0
    for idx, bit in norm:
        if child[idx] == bit:
            no_op += 1
        child[idx] = bit
    params = {"edits": norm}
    return _record("edit_entries", params, [parent_hex], child, {
        "n_edits": len(norm),
        "n_no_op_edits": no_op,
        "n_entries_changed": int((child != parent).sum()),
    })


def derive_flip(parent_hex: str, indices: Iterable[int]) -> Dict[str, object]:
    """Convenience: invert the listed entries. Recorded as `edit_entries`."""
    parent = decode_table(parent_hex)
    idxs = list(indices)
    for idx in idxs:
        if isinstance(idx, bool) or not isinstance(idx, (int, np.integer)) \
                or not (0 <= idx < TABLE_BITS):
            raise EvcaError("entry index must be in [0, %d], got %r"
                            % (TABLE_BITS - 1, idx))
    return derive_edit(parent_hex, [(int(i), int(1 - parent[int(i)]))
                                    for i in idxs])


# ---------------------------------------------------------------------------
# crossover_mask: composition of two same-kind mechanisms (THEO-REQ-003)
# ---------------------------------------------------------------------------

def require_mask(mask) -> np.ndarray:
    """A (128,) 0/1 selector: 0 takes parent A's entry, 1 takes parent B's.

    Accepts a 32-digit hex string in the table encoding or a 0/1 sequence.
    """
    if isinstance(mask, str):
        return decode_table(mask)
    m = np.asarray(mask)
    if m.shape != (TABLE_BITS,):
        raise EvcaError("mask must have %d entries, got shape %r"
                        % (TABLE_BITS, m.shape))
    if not np.isin(m, (0, 1)).all():
        raise EvcaError("mask must contain only 0 and 1")
    return m.astype(np.uint8)


def derive_crossover(parent_a_hex: str, parent_b_hex: str, mask
                     ) -> Dict[str, object]:
    """Child[j] = B[j] where mask[j] == 1 else A[j]. Uniform or blocked.

    The mask is the whole operator: a one-point crossover at k is the mask
    with ones from k on; a uniform crossover is a seeded random mask made
    by the caller (`crossover_mask_uniform`) and recorded here by content,
    so the record never depends on a seed being re-run.
    """
    a = decode_table(parent_a_hex)
    b = decode_table(parent_b_hex)
    m = require_mask(mask)
    child = np.where(m == 1, b, a).astype(np.uint8)
    params = {"mask_hex": encode_table(m)}
    return _record("crossover_mask", params, [parent_a_hex, parent_b_hex],
                   child, {
        "n_entries_from_b": int(m.sum()),
        "n_entries_where_parents_differ": int((a != b).sum()),
        "n_entries_changed_from_a": int((child != a).sum()),
        "n_entries_changed_from_b": int((child != b).sum()),
    })


def crossover_mask_one_point(k: int) -> np.ndarray:
    """Zeros below entry k, ones from k on: A's entries below the cut, B's
    from it. k in [0, 128]; k = 0 is all-from-B and k = 128 all-from-A, and
    both are allowed so a sweep over k includes its own identity controls."""
    if isinstance(k, bool) or not isinstance(k, (int, np.integer)) \
            or not (0 <= k <= TABLE_BITS):
        raise EvcaError("cut point must be in [0, %d], got %r"
                        % (TABLE_BITS, k))
    m = np.zeros(TABLE_BITS, dtype=np.uint8)
    m[int(k):] = 1
    return m


def crossover_mask_uniform(seed: int, p_from_b: float = 0.5) -> np.ndarray:
    """A seeded iid Bernoulli(p_from_b) mask. The seed is the caller's to
    record; the derivation record carries the mask by content."""
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise EvcaError("seed must be an integer, got %r" % (seed,))
    if not (0.0 <= float(p_from_b) <= 1.0):
        raise EvcaError("p_from_b must be in [0, 1]")
    rng = np.random.default_rng(int(seed))
    return (rng.random(TABLE_BITS) < float(p_from_b)).astype(np.uint8)


# ---------------------------------------------------------------------------
# The exact symmetries, as derivations with provenance.
# ---------------------------------------------------------------------------

def derive_transform(parent_hex: str, transform: str) -> Dict[str, object]:
    """reflect / complement / reflect_complement of a parent, recorded.

    The child tables are `core.reflect_table` / `core.complement_table`;
    this adds only the record. A transformed rule is a DIFFERENT table and
    therefore a different content-derived player, related to its parent by
    this derivation and by nothing else.
    """
    if transform not in ("reflect", "complement", "reflect_complement"):
        raise EvcaError("transform must be reflect, complement or "
                        "reflect_complement, got %r" % (transform,))
    parent = decode_table(parent_hex)
    child = parent
    if transform in ("reflect", "reflect_complement"):
        child = reflect_table(child)
    if transform in ("complement", "reflect_complement"):
        child = complement_table(child)
    return _record(transform, {}, [parent_hex], require_table(child), {
        "n_entries_changed": int((child != parent).sum()),
    })


def verify_record(rec: Dict[str, object]) -> Dict[str, object]:
    """Re-derive a record from its parents and parameters; refuse on any
    mismatch. The check a lineage reader runs before trusting a row."""
    if not isinstance(rec, dict) or rec.get("kind") != RECORD_KIND:
        raise EvcaError("not a %s record" % RECORD_KIND)
    op = rec.get("operator")
    if op not in OPERATORS:
        raise EvcaError("unknown operator %r" % (op,))
    parents = [rule_hex_of_player(p) for p in rec.get("parents", [])]
    params = rec.get("operator_params", {})
    if op == "edit_entries":
        again = derive_edit(parents[0], [tuple(e) for e in params["edits"]])
    elif op == "crossover_mask":
        again = derive_crossover(parents[0], parents[1], params["mask_hex"])
    else:
        again = derive_transform(parents[0], op)
    for key in ("child_rule_hex", "child_player_id", "derivation_id",
                "parents", "operator_params"):
        if again[key] != rec.get(key):
            raise EvcaError("record does not re-derive: %s differs" % key)
    return again
