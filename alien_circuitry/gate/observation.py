"""FROZEN OBSERVATION LANGUAGE and EXACT BOUNDED LOOKAHEAD for the U-A3 gate.

Committed before any scoring (this file is hashed in the gate results).

Depth-0 observation of a state w (all O(len) to compute from the word itself and its legal action list):
  len(w)               word length
  terminal(w)          no legal action
  outdeg(w)            number of distinct successors
  n_actions(w)         number of legal (rule, position) actions
  n_cancel(w)          legal cancel actions
  n_relator(w)         legal relator actions
  cx, cX, cy, cY       symbol counts
  eq(w, t)             immediate target equality
Derived (still local, no global computation):
  len_bound(w, t) = (len(w) - len(t)) / 2      admissible lower bound on remaining steps (length never increases)
  parity/length/abelianisation-exponent mismatch => provably unreachable  (e = cx - cX + cy - cY is invariant
  under cancel and under xyx -> yxy, so e(w) != e(t) proves t unreachable; it never changes along an edge, so it
  cannot separate sibling actions, but it is part of the language for completeness)

NOT available: D, Reach, normal-form identity from global computation, trap labels, anything cached across problems.

Exact bounded lookahead of depth h from candidate successor s' toward target t:
  breadth-first exploration of the legal transition graph within h moves of s' (a visited set is kept: this is
  graph search, the cheaper and stronger form; the tree form is reported separately through heights).
  Verdict SAFE(d)   if t is found at depth d <= h                        (sound)
  Verdict TRAP      if the whole forward region is exhausted without t   (sound: no frontier node has an unseen successor)
  Verdict UNKNOWN   otherwise
  Cost: states expanded (successor lists generated) and transitions examined (edges scanned), counted twice:
  "uncached" per call, and "cached" against a per-problem memo of already-expanded states (a searcher remembers).
"""
from __future__ import annotations
import numpy as np

FEATURES = ["len", "terminal", "outdeg", "n_actions", "n_cancel", "n_relator", "cx", "cX", "cy", "cY", "eq_target"]
SIBLING_MATCH_FEATURES = ["rule_family", "succ_len", "succ_outdeg", "succ_eq_target", "succ_n_cancel", "succ_n_relator"]
LOOSE_MATCH_FEATURES = ["rule_family", "succ_len", "succ_outdeg"]


class Observer:
    def __init__(self, U: dict):
        W, NS = U["W"], U["NS"]
        self.NS = NS
        self.LEN = U["LEN"].astype(np.int64)
        self.outdeg = U["outdeg"].astype(np.int64)
        self.n_actions = U["outdeg_nominal"].astype(np.int64)
        fam = np.array([r.family for r in U["rules"]])
        self.rule_family = fam
        rid, src = U["rule"], U["src"]
        is_cancel = fam[rid] == "cancel"
        self.n_cancel = np.bincount(src[is_cancel], minlength=NS).astype(np.int64)
        self.n_relator = np.bincount(src[~is_cancel], minlength=NS).astype(np.int64)
        self.counts = np.stack([(W == c).sum(axis=1) for c in range(4)], axis=1).astype(np.int64)
        self.e = self.counts[:, 0] - self.counts[:, 1] + self.counts[:, 2] - self.counts[:, 3]
        fi, fx = U["fwd"]
        self.fi, self.fx = fi.tolist(), fx.tolist()

    def features(self, s: int, t: int) -> dict:
        c = self.counts[s]
        return {"len": int(self.LEN[s]), "terminal": bool(self.outdeg[s] == 0), "outdeg": int(self.outdeg[s]),
                "n_actions": int(self.n_actions[s]), "n_cancel": int(self.n_cancel[s]), "n_relator": int(self.n_relator[s]),
                "cx": int(c[0]), "cX": int(c[1]), "cy": int(c[2]), "cY": int(c[3]), "eq_target": bool(s == t)}

    def len_bound(self, s: int, t: int) -> int:
        return (int(self.LEN[s]) - int(self.LEN[t])) // 2

    def provably_dead(self, s: int, t: int) -> bool:
        if s == t:
            return False
        ls, lt = int(self.LEN[s]), int(self.LEN[t])
        return (self.outdeg[s] == 0) or ls < lt or ((ls - lt) & 1) or (self.e[s] != self.e[t])

    def lookahead(self, s: int, t: int, h: int, memo: set | None = None):
        """Returns (status, d, expanded_uncached, examined_uncached, expanded_new, examined_new)."""
        fi, fx = self.fi, self.fx
        if s == t:
            return "SAFE", 0, 0, 0, 0, 0
        visited = {s}; frontier = [s]; d = 0
        exp_u = exm_u = exp_n = exm_n = 0
        while True:
            if d == h:
                # openness check: does any frontier node have an unseen successor?
                for v in frontier:
                    deg = fi[v + 1] - fi[v]
                    exm_u += deg
                    if memo is not None and v not in memo:
                        memo.add(v); exp_n += 1; exm_n += deg
                    exp_u += 1
                    for u in fx[fi[v]:fi[v + 1]]:
                        if u not in visited:
                            return "UNKNOWN", -1, exp_u, exm_u, exp_n, exm_n
                return "TRAP", -1, exp_u, exm_u, exp_n, exm_n
            nxt = []
            for v in frontier:
                deg = fi[v + 1] - fi[v]
                exp_u += 1; exm_u += deg
                if memo is not None and v not in memo:
                    memo.add(v); exp_n += 1; exm_n += deg
                for u in fx[fi[v]:fi[v + 1]]:
                    if u not in visited:
                        visited.add(u); nxt.append(u)
            d += 1
            if not nxt:
                return "TRAP", -1, exp_u, exm_u, exp_n, exm_n
            if t in visited:
                return "SAFE", d, exp_u, exm_u, exp_n, exm_n
            frontier = nxt
