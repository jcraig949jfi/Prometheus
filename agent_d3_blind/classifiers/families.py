"""OFFLINE mutation-bias auditor.

Never imported by the mutation process, the census walkers, or any M0 baseline
(statically enforced in anti_cheat/checks.py).  Human-recognisable transformation
families are recovered here retrospectively, for auditing only.

Primary track: substrate-generic syntactic shape of the (parent -> child) token
string.  The decomposition is total, so the residual bucket is structurally near
empty; adversarial charging of the residual is therefore a no-op rather than a
benefit, and is reported as such.
"""
from collections import Counter

PRIMARY = ["identity", "append", "prepend", "wrap", "delete", "relabel",
           "permutation", "duplication", "splice", "lengthen-other",
           "shorten-other", "residual"]

SECONDARY = ["control-like", "memory-like", "representation-like", "route-like",
             "none"]


def _contiguous_block_of(sub_seq, seq):
    m = len(sub_seq)
    if m == 0:
        return False
    for i in range(len(seq) - m + 1):
        if seq[i:i + m] == sub_seq:
            return True
    return False


def classify(P, C):
    if C == P:
        return "identity"
    lp, lc = len(P), len(C)
    # wrap: both ends grew around an intact copy of the parent
    if lc > lp + 1:
        for i in range(1, lc - lp):
            if C[i:i + lp] == P:
                return "wrap"
    p = 0
    while p < min(lp, lc) and P[p] == C[p]:
        p += 1
    s = 0
    while s < min(lp, lc) - p and P[lp - 1 - s] == C[lc - 1 - s]:
        s += 1
    midP = P[p:lp - s]
    midC = C[p:lc - s]
    if not midP:
        if _contiguous_block_of(midC, P):
            return "duplication"
        if lc > lp and C[:lp] == P:
            return "append"
        if lc > lp and C[lc - lp:] == P:
            return "prepend"
        return "lengthen-other"
    if not midC:
        return "delete"
    if len(midP) == 1 and len(midC) == 1:
        return "relabel"
    if lp == lc and Counter(P) == Counter(C):
        return "permutation"
    if midP and midC:
        return "splice"
    return "residual"


# ---- secondary descriptive track (operation-level deltas) ----
_S1_CTRL = {11, 12}
_S1_MEM = {10}
_S1_REP = {2, 3, 9, 14, 15, 13}
_S1_ROUTE = {1, 27, 28}
_S2_CTRL = {21, 22}
_S2_MEM = {10, 11, 7, 8, 1, 2}
_S2_REP = {16, 17, 18, 19, 20, 23}
_S2_ROUTE = {12, 13, 14, 15, 9}
_S4_CTRL = {4}
_S4_ROUTE = {2}
_S4_REP = {0, 1, 3}


def _ops_of(basis, sub, prog):
    try:
        if basis == "S1":
            tr = sub.decode(prog)
            if tr is None:
                return Counter()
            out = Counter()
            st = [tr]
            while st:
                nd = st.pop()
                out[nd[0]] += 1
                st.extend(nd[2])
            return out
        if basis in ("S2", "S4"):
            return Counter(op for (op, *_r) in sub.decode(prog))
        if basis == "S3":
            rules = sub.parse(prog)
            if rules is None:
                return Counter()
            c = Counter()
            c["nrules"] = len(rules)
            for lhs, rhs, nv in rules:
                c["nvars"] += nv
                c["rhslen"] += len(rhs)
                c["lhslen"] += len(lhs)
            return c
    except Exception:
        return Counter()
    return Counter()


def op_family(basis, sub, P, C):
    a, b = _ops_of(basis, sub, P), _ops_of(basis, sub, C)
    intro = {k for k in b if b[k] > a.get(k, 0)}
    if basis == "S1":
        table = [(_S1_CTRL, "control-like"), (_S1_MEM, "memory-like"),
                 (_S1_REP, "representation-like"), (_S1_ROUTE, "route-like")]
    elif basis == "S2":
        table = [(_S2_CTRL, "control-like"), (_S2_MEM, "memory-like"),
                 (_S2_REP, "representation-like"), (_S2_ROUTE, "route-like")]
    elif basis == "S4":
        table = [(_S4_CTRL, "control-like"), (_S4_ROUTE, "route-like"),
                 (_S4_REP, "representation-like")]
    else:
        if b.get("nrules", 0) != a.get("nrules", 0):
            return "route-like"
        if b.get("nvars", 0) != a.get("nvars", 0):
            return "memory-like"
        if b.get("rhslen", 0) != a.get("rhslen", 0):
            return "representation-like"
        return "none"
    for s, name in table:
        if intro & s:
            return name
    return "none"


def charged_shares(family_counts):
    """Adversarial residual charging: residual mass is added to the largest
    non-residual family before the max-share statistic is computed."""
    c = dict(family_counts)
    total = sum(c.values())
    if total == 0:
        return {}, 0.0, 0
    res = c.pop("residual", 0)
    if c:
        big = max(c, key=lambda k: c[k])
        c[big] = c[big] + res
    else:
        c["residual"] = res
    shares = {k: v / total for k, v in c.items()}
    mx = max(shares.values())
    n5 = sum(1 for v in shares.values() if v >= 0.05)
    return shares, mx, n5
