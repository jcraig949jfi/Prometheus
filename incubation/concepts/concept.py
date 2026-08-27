"""concept.py — solver-visible concept records and executable guards.

A concept is an arbitrary symbol (c0001, c0002, ...) bound to an executable word of
primitive IDs, optionally bounded by an executable guard. The SOLVER-VISIBLE record
contains nothing else: no world identity, no strata, no semantic names. Provenance and
evidence live in the ledger (omniscient side).

Guard semantics (sound-by-construction for prefix probes): a guard is an ordered list of
atoms (probe_word, slot, op, threshold). Evaluating an atom executes its probe through
the boundary (counted). If a probe FAILS at runtime the guard returns True (predict
failure): for probes that are prefixes of the concept's own word this is sound, because
the concept's execution would fail at the same step. Otherwise the atom compares the
probed state's slot against the threshold with '<' or '=='. Any true atom => skip.
"""
from __future__ import annotations


class Guard:
    def __init__(self, atoms):
        # atoms: list of (probe_word: tuple[pid], slot: int, op: str, c)
        # ordered cheapest-probe-first at construction time
        self.atoms = [(tuple(p), int(j), op, c) for (p, j, op, c) in atoms]

    def __call__(self, bnd, state):
        for probe, j, op, c in self.atoms:
            v = state
            failed = False
            for pid in probe:
                v = bnd.apply(pid, v)
                if v is None:
                    failed = True
                    break
            if failed:
                return True
            x = bnd.read(v)[j]
            if (op == "<" and x < c) or (op == "==" and x == c):
                return True
        return False

    def to_json(self):
        return [[list(p), j, op, c] for (p, j, op, c) in self.atoms]


class Concept:
    def __init__(self, cid, word, guard=None):
        self.cid = cid
        self.word = tuple(word)
        self.guard = guard

    def to_json(self):
        return {"cid": self.cid, "word": list(self.word),
                "guard": None if self.guard is None else self.guard.to_json(),
                "invoke_exec_cost": len(self.word)}

    def content_hash(self):
        import hashlib
        return hashlib.sha256(repr((self.word,
                                    None if self.guard is None
                                    else self.guard.atoms)).encode()).hexdigest()[:16]
