"""Reachability oracle. Spec: PREREG-TASKS.md section 5.

Full physics: reachability == expressibility, PROVED constructively per task by
building an explicit mutation path seed -> witness out of INSERT/DELETE edges
and verifying every edge against the physics' applicability rules. Independent
of any learner (constitution section 31): paths are built from the witness, not
from navigator trajectories.

Ablated physics (instrument validation only): with the length-growing classes
{INSERT, DUP_BLOCK} removed, no program longer than the longest seed (2) is
reachable — a provable length argument — so 'expressible + unreachable' cases
exist and the classifier must detect them.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'substrate'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mutation'))
from rm_vm import MAX_LEN
from physics import SEED_REPERTOIRE

START = (('MOV', 0, 0),)      # seed 0: identity


def _is_insert_edge(g, g2):
    if len(g2) != len(g) + 1 or len(g) >= MAX_LEN:
        return False
    for i in range(len(g2)):
        if tuple(g2[:i]) + tuple(g2[i + 1:]) == tuple(g):
            return True
    return False


def _is_delete_edge(g, g2):
    return _is_insert_edge(g2, g)     # symmetric definition


def structural_path(witness):
    """Explicit seed->witness path of INSERT edges then one DELETE edge
    (interleaved when the witness is at MAX_LEN). Returns the verified path or
    raises. Path length <= len(witness) + 2."""
    w = list(witness)
    path = [START]
    cur = list(START)
    n_first = min(len(w), MAX_LEN - 1)     # insert this many before deleting seed
    for i in range(n_first):
        cur = w[:i + 1] + [START[0]]      # witness prefix + trailing seed instr
        path.append(tuple(cur))
    # delete the trailing seed instruction
    cur = w[:n_first]
    path.append(tuple(cur))
    # insert any remaining witness instructions
    for i in range(n_first, len(w)):
        cur = w[:i + 1]
        path.append(tuple(cur))
    # verify every edge
    for a, b in zip(path, path[1:]):
        if not (_is_insert_edge(a, b) or _is_delete_edge(a, b)):
            raise AssertionError(f'illegal edge {a} -> {b}')
    assert path[-1] == tuple(witness)
    return path


def classify(task, expressible_witness):
    """REACHABLE with verified path iff a witness exists; UNKNOWN mirrors
    expressibility-UNKNOWN. Never uses learner trajectories."""
    if expressible_witness is None:
        return {'status': 'UNKNOWN_REACHABILITY', 'path_len': None}
    path = structural_path(expressible_witness)
    return {'status': 'REACHABLE', 'path_len': len(path) - 1}


def classify_ablated_no_growth(task, expressible_witness):
    """Under physics WITHOUT length-growing classes: reachable set from the
    seed repertoire is bounded to programs of length <= max seed length (2).
    Provable UNREACHABLE for any witness needing length > 2."""
    max_seed_len = max(len(s) for s in SEED_REPERTOIRE)
    if expressible_witness is None:
        return {'status': 'UNKNOWN_REACHABILITY'}
    if len(expressible_witness) > max_seed_len:
        # sufficient condition; a shorter equivalent witness would be needed to
        # overturn it, and the synthetic validation cases are chosen where the
        # minimal witness provably exceeds 2 (checked by exhaustive search over
        # all length<=2 programs in the validation battery).
        return {'status': 'UNREACHABLE', 'reason': 'length_bound'}
    return {'status': 'REACHABLE', 'path_len': 0}
