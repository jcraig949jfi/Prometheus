"""
Stern-Brocot — Stern-Brocot construction, Calkin-Wilf enumeration

Connects to: [number_theory, continued_fractions, binary_trees]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "stern_diatomic"
OPERATIONS = {}


def stern_brocot_sequence(x):
    """Generate first n terms of the Stern-Brocot sequence (as fractions p/q). x=[n]. Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 5000)
    # Stern's diatomic sequence: s(0)=0, s(1)=1, s(2n)=s(n), s(2n+1)=s(n)+s(n+1)
    s = np.zeros(n, dtype=np.int64)
    if n >= 1:
        s[0] = 0
    if n >= 2:
        s[1] = 1
    for i in range(2, n):
        if i % 2 == 0:
            s[i] = s[i // 2]
        else:
            s[i] = s[i // 2] + s[i // 2 + 1]
    return s


OPERATIONS["stern_brocot_sequence"] = {
    "fn": stern_brocot_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "Stern's diatomic sequence s(n)"
}


def calkin_wilf_enumerate(x):
    """Enumerate first n fractions in Calkin-Wilf tree as [p1,q1,p2,q2,...]. x=[n]. Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 2000)
    # Calkin-Wilf: start with 1/1, children of p/q are p/(p+q) and (p+q)/q
    # BFS traversal
    from collections import deque
    result = []
    queue = deque([(1, 1)])
    count = 0
    while count < n and queue:
        p, q = queue.popleft()
        result.extend([p, q])
        count += 1
        if count < n:
            queue.append((p, p + q))
            queue.append((p + q, q))
    return np.array(result, dtype=np.int64)


OPERATIONS["calkin_wilf_enumerate"] = {
    "fn": calkin_wilf_enumerate,
    "input_type": "array",
    "output_type": "array",
    "description": "First n fractions in Calkin-Wilf tree as [p1,q1,p2,q2,...]"
}


def stern_diatomic_s(x):
    """Compute Stern's diatomic s(n) for each n in x. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = []
    for n in vals.ravel():
        n = int(n)
        if n == 0:
            results.append(0)
        elif n == 1:
            results.append(1)
        else:
            # Use binary representation: efficient computation
            # s(n) can be computed from binary digits
            bits = bin(n)[2:]
            a, b = 1, 0
            for bit in bits[1:]:
                if bit == '0':
                    b = a + b
                else:
                    a = a + b
            results.append(a)
    return np.array(results, dtype=np.int64)


OPERATIONS["stern_diatomic_s"] = {
    "fn": stern_diatomic_s,
    "input_type": "array",
    "output_type": "array",
    "description": "Stern's diatomic function s(n) via binary expansion"
}


def mediant_fraction(x):
    """Compute mediant of two fractions a/b and c/d. x=[a,b,c,d]. Input: array. Output: array."""
    a, b, c, d = int(x[0]), int(x[1]), int(x[2]), int(x[3])
    # Mediant: (a+c)/(b+d)
    return np.array([a + c, b + d], dtype=np.int64)


OPERATIONS["mediant_fraction"] = {
    "fn": mediant_fraction,
    "input_type": "array",
    "output_type": "array",
    "description": "Mediant of fractions a/b and c/d = (a+c)/(b+d)"
}


def farey_sequence(x):
    """Generate Farey sequence F_n as [p1,q1,p2,q2,...]. n=int(x[0]). Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 200)
    # Farey sequence F_n: fractions p/q with 0 <= p/q <= 1, q <= n, in order
    fracs = []
    for q in range(1, n + 1):
        for p in range(0, q + 1):
            from math import gcd
            if gcd(p, q) == 1:
                fracs.append((p, q))
    fracs.sort(key=lambda f: f[0] / f[1])
    result = []
    for p, q in fracs:
        result.extend([p, q])
    return np.array(result, dtype=np.int64)


OPERATIONS["farey_sequence"] = {
    "fn": farey_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "Farey sequence F_n as [p1,q1,p2,q2,...]"
}


def stern_brocot_tree_path(x):
    """Find path in Stern-Brocot tree to fraction p/q. x=[p,q]. Returns L/R sequence as 0/1. Input: array. Output: array."""
    p, q = int(abs(x[0])), int(abs(x[1]))
    if q == 0:
        return np.array([])
    path = []
    # Navigate: start with 0/1 -- 1/1 -- 1/0
    lp, lq = 0, 1
    rp, rq = 1, 0
    for _ in range(100):
        mp, mq = lp + rp, lq + rq
        if mp == p and mq == q:
            break
        elif p * mq < mp * q:  # p/q < mp/mq -> go left
            path.append(0)
            rp, rq = mp, mq
        else:  # go right
            path.append(1)
            lp, lq = mp, mq
    return np.array(path, dtype=np.int64)


OPERATIONS["stern_brocot_tree_path"] = {
    "fn": stern_brocot_tree_path,
    "input_type": "array",
    "output_type": "array",
    "description": "Path in Stern-Brocot tree to p/q (0=left, 1=right)"
}


def hyperbinary_representations(x):
    """Count hyperbinary representations of n (binary with digits 0,1,2). x=[n]. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = []
    for n in vals.ravel():
        n = int(n)
        # Number of hyperbinary representations of n = s(n+1) (Stern's diatomic)
        if n == 0:
            results.append(1)
        else:
            # Compute s(n+1)
            m = n + 1
            bits = bin(m)[2:]
            a, b = 1, 0
            for bit in bits[1:]:
                if bit == '0':
                    b = a + b
                else:
                    a = a + b
            results.append(a)
    return np.array(results, dtype=np.int64)


OPERATIONS["hyperbinary_representations"] = {
    "fn": hyperbinary_representations,
    "input_type": "array",
    "output_type": "array",
    "description": "Count of hyperbinary representations (equals s(n+1))"
}


def minkowski_question_mark(x):
    """Minkowski's question mark function ?(x) for x in [0,1]. Input: array. Output: array."""
    vals = np.asarray(x, dtype=np.float64)
    results = []
    for v in vals.ravel():
        v = float(np.clip(v, 0, 1))
        if v == 0:
            results.append(0.0)
            continue
        if v == 1:
            results.append(1.0)
            continue
        # Compute via continued fraction expansion
        # ?(x) = 2 * sum_{k} (-1)^(k+1) / 2^(a_0+a_1+...+a_k)
        # where x = [a_0; a_1, a_2, ...] is the CF expansion
        cf = []
        rem = v
        for _ in range(50):
            if rem == 0:
                break
            a = int(1.0 / rem)
            cf.append(a)
            rem = 1.0 / rem - a
            if abs(rem) < 1e-12:
                break
        if not cf:
            results.append(0.0)
            continue
        qm = 0.0
        cumsum = 0
        for k, a in enumerate(cf):
            cumsum += a
            qm += ((-1) ** (k + 1)) / (2.0 ** cumsum)
        results.append(2.0 * qm)
    return np.array(results)


OPERATIONS["minkowski_question_mark"] = {
    "fn": minkowski_question_mark,
    "input_type": "array",
    "output_type": "array",
    "description": "Minkowski question mark function ?(x) on [0,1]"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
