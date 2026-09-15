"""Universe A: directed bounded rewriting over the alphabet {x, X, y, Y}.

OPERATIONAL SEMANTICS (this is the object under study; it is NOT group equality)
--------------------------------------------------------------------------------
A state is a word w over the alphabet {x, X, y, Y} with 0 <= len(w) <= L.
Letter codes: x=0, X=1, y=2, Y=3.  X is the formal inverse of x (code ^ 1), Y of y.

An action is a (rule, position) pair.  A rule is a directed rewrite  lhs -> rhs.
The rule is legal at position p in w iff  w[p:p+len(lhs)] == lhs  and  len(w) - len(lhs) + len(rhs) <= L.
Applying it yields  w[:p] + rhs + w[p+len(lhs):].

Rule families
  cancel   : aA -> ''  for a in {x, X, y, Y}, A = inverse(a).   Irreversible: there is NO introduce rule.
  relator  : each direction of each presentation relation is a separate named rule (see presentations.py).
Every word is its own canonical form; there is no free reduction performed implicitly.

Consequences of the semantics that are facts about THIS graph, not about the group:
  * length never increases, so a target t is reachable from s only if len(t) <= len(s) and len(s)-len(t) is even;
  * cancel is irreversible, so the graph is directed and reachability can be destroyed (target-conditioned traps);
  * relator rules come in inverse pairs, so relator-only moves are reversible and the graph contains cycles.
Bounded operational reachability under these rules is a strict sub-relation of group equality.

State indexing: index(w) = OFF[len(w)] + value(w) where value is the big-endian base-4 number of the letter codes
and OFF[l] = (4**l - 1) // 3.  The map is a bijection from words of length <= L onto range(NS), NS = OFF[L+1].
"""
from __future__ import annotations
import hashlib
import numpy as np

ALPHABET = "xXyY"
CODE = {c: i for i, c in enumerate(ALPHABET)}
PAD = 4  # sentinel for positions beyond the word length


def inverse_code(c: int) -> int:
    return c ^ 1


def offsets(L: int) -> np.ndarray:
    return np.array([(4 ** l - 1) // 3 for l in range(L + 2)], dtype=np.int64)


def encode(word: str) -> list[int]:
    return [CODE[c] for c in word]


def decode(codes) -> str:
    return "".join(ALPHABET[int(c)] for c in codes)


def word_index(word: str, L: int) -> int:
    l = len(word)
    if l > L:
        raise ValueError("word longer than cap")
    v = 0
    for c in word:
        v = v * 4 + CODE[c]
    return int(offsets(L)[l] + v)


def index_word(i: int, L: int) -> str:
    off = offsets(L)
    l = int(np.searchsorted(off, i, side="right") - 1)
    v = i - off[l]
    out = []
    for _ in range(l):
        out.append(ALPHABET[v % 4]); v //= 4
    return "".join(reversed(out))


def all_words(L: int):
    """Arrays W (NS, L) int8 padded with PAD, LEN (NS,) int8, in index order."""
    off = offsets(L)
    NS = int(off[L + 1])
    W = np.full((NS, max(L, 1)), PAD, dtype=np.int8)
    LEN = np.zeros(NS, dtype=np.int8)
    for l in range(1, L + 1):
        n = 4 ** l
        v = np.arange(n, dtype=np.int64)
        rows = slice(int(off[l]), int(off[l]) + n)
        LEN[rows] = l
        for i in range(l):
            W[rows, i] = (v // (4 ** (l - 1 - i))) % 4
    return W, LEN


class Rule:
    __slots__ = ("name", "family", "lhs", "rhs")

    def __init__(self, name: str, family: str, lhs: str, rhs: str):
        self.name, self.family, self.lhs, self.rhs = name, family, lhs, rhs

    def __repr__(self):
        return f"Rule({self.name}: {self.lhs!r}->{self.rhs!r})"


def cancel_rules() -> list[Rule]:
    return [Rule(f"cancel[{a}{ALPHABET[inverse_code(CODE[a])]}]", "cancel", a + ALPHABET[inverse_code(CODE[a])], "") for a in ALPHABET]


def transitions(L: int, rules: list[Rule]):
    """Vectorised generation of every legal (state, rule, position) -> successor.

    Returns dict with:
      src, dst : int64 arrays (nominal edges, one per legal action)
      rule, pos: int8 arrays
      W, LEN   : the word table
    Nominal edges are NOT deduplicated: two different actions may produce the same successor.
    """
    W, LEN = all_words(L)
    NS = W.shape[0]
    off = offsets(L)
    Lw = W.shape[1]
    # prefix values PREF[:, p] = value of W[:, :p]; SUFV[:, q] = value of W[:, q:LEN]
    PREF = np.zeros((NS, Lw + 1), dtype=np.int64)
    for p in range(Lw):
        PREF[:, p + 1] = PREF[:, p] * 4 + np.where(W[:, p] == PAD, 0, W[:, p]).astype(np.int64)
    LEN64 = LEN.astype(np.int64)
    VAL = PREF[np.arange(NS), LEN64]
    pow4 = 4 ** np.arange(Lw + 2, dtype=np.int64)
    SUFV = np.zeros((NS, Lw + 1), dtype=np.int64)
    for q in range(Lw + 1):
        tail = np.clip(LEN64 - q, 0, None)
        SUFV[:, q] = VAL - PREF[:, q] * pow4[tail]
    srcs, dsts, rids, poss = [], [], [], []
    for rid, r in enumerate(rules):
        lhs = np.array(encode(r.lhs), dtype=np.int8)
        k, m = len(lhs), len(r.rhs)
        rhs_val = 0
        for c in r.rhs:
            rhs_val = rhs_val * 4 + CODE[c]
        for p in range(0, L - k + 1):
            mask = (LEN64 >= p + k) & (LEN64 - k + m <= L)
            for i in range(k):
                mask &= W[:, p + i] == lhs[i]
            rows = np.nonzero(mask)[0]
            if rows.size == 0:
                continue
            l = LEN64[rows]
            suf = l - p - k
            newlen = l - k + m
            newval = PREF[rows, p] * pow4[m + suf] + rhs_val * pow4[suf] + SUFV[rows, p + k]
            dst = off[newlen] + newval
            srcs.append(rows); dsts.append(dst)
            rids.append(np.full(rows.size, rid, dtype=np.int8)); poss.append(np.full(rows.size, p, dtype=np.int8))
    src = np.concatenate(srcs) if srcs else np.zeros(0, np.int64)
    dst = np.concatenate(dsts) if dsts else np.zeros(0, np.int64)
    rid = np.concatenate(rids) if rids else np.zeros(0, np.int8)
    pos = np.concatenate(poss) if poss else np.zeros(0, np.int8)
    order = np.lexsort((pos, rid, dst, src))
    return {"src": src[order], "dst": dst[order], "rule": rid[order], "pos": pos[order], "W": W, "LEN": LEN, "NS": NS}


def apply_rule_str(word: str, rule: Rule, p: int, L: int) -> str | None:
    """Reference (scalar) semantics used by tests to check the vectorised generator."""
    k = len(rule.lhs)
    if word[p:p + k] != rule.lhs or len(word) - k + len(rule.rhs) > L:
        return None
    return word[:p] + rule.rhs + word[p + k:]


def csr(src: np.ndarray, dst: np.ndarray, n: int):
    """CSR adjacency from an edge list (assumed sorted by src not required)."""
    order = np.argsort(src, kind="stable")
    s, d = src[order], dst[order]
    counts = np.bincount(s, minlength=n)
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(counts, out=indptr[1:])
    return indptr, d.astype(np.int64)


def distinct_edges(src, dst):
    pairs = np.unique(np.stack([src, dst], axis=1), axis=0)
    return pairs[:, 0], pairs[:, 1]


def layered_bfs(indptr, indices, start: int, n: int, dist: np.ndarray | None = None) -> np.ndarray:
    """Vectorised BFS distances from start over the CSR graph; -1 = unreached."""
    if dist is None:
        dist = np.full(n, -1, dtype=np.int16)
    frontier = np.array([start], dtype=np.int64)
    d = 0
    while frontier.size:
        dist[frontier] = d
        counts = indptr[frontier + 1] - indptr[frontier]
        total = int(counts.sum())
        if total == 0:
            break
        starts = np.repeat(indptr[frontier], counts)
        within = np.arange(total) - np.repeat(np.cumsum(counts) - counts, counts)
        nb = indices[starts + within]
        nb = np.unique(nb)
        frontier = nb[dist[nb] < 0]
        d += 1
    return dist


def sha256_arrays(*arrays) -> str:
    h = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(a)
        h.update(str(a.dtype).encode()); h.update(str(a.shape).encode()); h.update(a.tobytes())
    return h.hexdigest()
