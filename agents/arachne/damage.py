"""Damage-algebra empirical coverage test.

Noesis named 9 "damage operators" (resolution moves) narratively, from 236
impossibility theorems. This asks the computational question: can each operator
be EXHIBITED empirically as a sequence transform that turns a no-match into a
real OEIS match? The OEIS table (394K sequences) is the exact oracle.

A transform that repairs a broken sequence into a catalogued one is an empirical
instance of that damage operator. Operators that resist realization in
sequence-space are findings: either narrative-only, or they need a different
landscape (permutations, polynomials, group actions, ...).

CLI:  PGPASSWORD=... python -m agents.arachne.damage coverage
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from agents.arachne.landscapes import _pg


# ---- sequence helpers -------------------------------------------------------
def _diffs(s):
    return [s[i + 1] - s[i] for i in range(len(s) - 1)]


def _psums(s):
    out, a = [], 0
    for x in s:
        a += x
        out.append(a)
    return out


def _running_avg(s):
    out, a = [], 0
    for i, x in enumerate(s):
        a += x
        out.append(round(a / (i + 1)))
    return out


# ---- damage operators realized as sequence transforms -----------------------
# Each returns a list of candidate repaired sequences to try matching.
def _truncate(s):
    return [s[1:], s[2:], s[:-1]]


def _partition(s):
    return [s[::2], s[1::2]]


def _quantize(s):
    # for rational/float input: coerce to integers several ways
    out = []
    try:
        out.append([round(float(x)) for x in s])
    except Exception:
        pass
    # numerators / denominators if Rational-like
    try:
        out.append([int(getattr(x, "p", x)) for x in s])   # numerators
        out.append([int(getattr(x, "q", 1)) for x in s])   # denominators
    except Exception:
        pass
    return [c for c in out if c]


def _invert(s):
    return [s[::-1], [-x for x in s]]


def _hierarchize(s):
    return [_diffs(s), _psums(s), _diffs(_diffs(s))]


def _distribute(s):
    return [_running_avg(s)]


def _concentrate(s):
    # localize damage to a region: the longest clean prefix before the defect
    return [s[:k] for k in range(len(s), 6, -1)]


REPAIRS = {
    "TRUNCATE": _truncate, "PARTITION": _partition, "QUANTIZE": _quantize,
    "INVERT": _invert, "HIERARCHIZE": _hierarchize, "DISTRIBUTE": _distribute,
    "CONCENTRATE": _concentrate,
    # EXTEND and RANDOMIZE are handled specially (not pure seq->seq transforms)
}


# ---- OEIS oracle ------------------------------------------------------------
class Oracle:
    def __init__(self):
        self.conn = _pg.connect("prometheus_sci")
        if self.conn:
            try:
                cur = self.conn.cursor(); cur.execute("SET statement_timeout=5000;"); cur.close()
            except Exception:
                pass

    def ok(self):
        return self.conn is not None

    def match(self, seq, min_len=9):
        """STRICT exact prefix match — applies NO hidden repair (no offset
        fallback = no implicit TRUNCATE; integers required = no implicit
        QUANTIZE), so each damage operator is measured cleanly."""
        try:
            if any(int(x) != x for x in seq):   # non-integer => needs QUANTIZE, no match
                return []
            seq = [int(x) for x in seq]
        except Exception:
            return []
        if len(seq) < min_len:
            return []
        seq = seq[:14]
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT oeis_id FROM analysis.oeis WHERE first_terms[1:%s]=%s::bigint[] "
                        "AND oeis_id IS NOT NULL ORDER BY oeis_id ASC LIMIT 6;", (len(seq), seq))
            hits = [r[0] for r in cur.fetchall()]
        except Exception:
            hits = []
        cur.close()
        return list(dict.fromkeys(hits))

    def canonical(self, seq, min_len=8, max_off=3):
        """Identify a sequence robustly: offset-tolerant (storage conventions
        vary — a leading 0 is not a damage operation), returns A-numbers sorted
        canonical-first (lowest A-number). Used to recover the INTENDED target,
        so 'exhibited' means canonical recovery, not a coincidental prefix hit."""
        try:
            if any(int(x) != x for x in seq):
                return []
            seq = [int(x) for x in seq]
        except Exception:
            return []
        if len(seq) < min_len:
            return []
        seq = seq[:14]
        hits = []
        cur = self.conn.cursor()
        for off in range(0, max_off + 1):
            try:
                cur.execute("SELECT oeis_id FROM analysis.oeis WHERE first_terms[%s:%s]=%s::bigint[] "
                            "AND oeis_id IS NOT NULL LIMIT 8;", (1 + off, off + len(seq), seq))
                hits += [r[0] for r in cur.fetchall()]
            except Exception:
                pass
        cur.close()
        uniq = list(dict.fromkeys(hits))
        uniq.sort(key=lambda a: int(a[1:]) if a[1:].isdigit() else 10 ** 9)
        return uniq

    def match_growth(self, seq):
        """RANDOMIZE: relax exact match to growth-rate class (statistical)."""
        try:
            seq = [float(x) for x in seq]
        except Exception:
            return []
        if len(seq) < 4 or seq[-2] == 0:
            return []
        g = seq[-1] / seq[-2] if seq[-2] else 0
        cur = self.conn.cursor()
        try:
            cur.execute("SELECT oeis_id, growth_rate FROM analysis.oeis WHERE growth_rate "
                        "BETWEEN %s AND %s AND oeis_id IS NOT NULL LIMIT 5;", (g - 0.02, g + 0.02))
            hits = [r[0] for r in cur.fetchall()]
        except Exception:
            hits = []
        cur.close()
        return hits


# ---- coverage experiment ----------------------------------------------------
def coverage():
    import sympy
    o, K = Oracle(), 16
    if not o.ok():
        return {"error": "OEIS oracle unavailable (PGPASSWORD?)"}

    catalan = [int(sympy.catalan(n)) for n in range(K)]
    factorial = [int(sympy.factorial(n)) for n in range(K)]
    fibonacci = [int(sympy.fibonacci(n)) for n in range(1, K + 1)]
    harmonic = [sympy.harmonic(n) for n in range(1, K + 1)]   # Rational

    harm_num = [int(h.p) for h in harmonic]                           # numerators
    results = {}

    def recover(op, clean, broken, note):
        """Canonical-grade: target = canonical id of the CLEAN sequence; the
        operator is exhibited iff (a) the broken seq does NOT already yield the
        target under the strict oracle, and (b) a repair candidate recovers the
        target under the canonical (offset-tolerant) oracle."""
        target = (o.canonical(clean) or [None])[0]
        strict_pre = set(o.match(broken))
        recovered = None
        for cand in REPAIRS[op](broken):
            if target and target in o.canonical(cand):
                recovered = target
                break
        results[op] = {"exhibited": bool(recovered) and target not in strict_pre,
                       "canonical_grade": bool(recovered) and recovered == target,
                       "target": target, "recovered": recovered, "note": note}

    recover("TRUNCATE", catalan, [99] + catalan, "junk leading term -> drop -> Catalan")
    recover("PARTITION", catalan, [v for p in zip(catalan, factorial) for v in p],
            "interleave Catalan+factorial -> bisect -> Catalan")
    recover("QUANTIZE", harm_num, harmonic, "rational harmonic -> numerators (A001008)")
    recover("INVERT", catalan, catalan[::-1], "reversed -> invert -> Catalan")
    recover("HIERARCHIZE", fibonacci, _psums(fibonacci), "partial sums -> difference -> Fibonacci")
    corrupt = list(catalan); corrupt[12] += 7
    recover("CONCENTRATE", catalan, corrupt, "one corrupted term -> longest clean prefix")

    # EXTEND: short prefix ambiguous, full length specific
    short_n = len(o.canonical(catalan[:6], min_len=4))
    full_hit = o.canonical(catalan, min_len=9)
    results["EXTEND"] = {"exhibited": short_n > max(1, len(full_hit)) and bool(full_hit),
                         "canonical_grade": "A000108" in full_hit,
                         "short_matches": short_n, "full": full_hit[:3],
                         "note": "more terms disambiguate -> A000108"}

    # RANDOMIZE: no exact match, statistical (growth-class) match
    pert = [int(sympy.prime(n)) + (n % 3) for n in range(1, K + 1)]
    results["RANDOMIZE"] = {"exhibited": not o.match(pert) and bool(o.match_growth(pert)),
                            "canonical_grade": False, "growth_class": o.match_growth(pert)[:3],
                            "note": "perturbed primes -> relax to growth-rate class (statistical)"}

    # DISTRIBUTE (new landscape): a constant's irrationality can't be an exact
    # integer sequence; spread it UNIFORMLY via equidistribution (Beatty
    # sequence floor(n*alpha)) -> a catalogued sequence. phi -> A000201.
    import math
    phi = (1 + 5 ** 0.5) / 2
    beatty = [int(math.floor(n * phi)) for n in range(1, K + 1)]
    beatty_hit = o.canonical(beatty)
    results["DISTRIBUTE"] = {"exhibited": bool(beatty_hit),
                             "canonical_grade": "A000201" in beatty_hit,
                             "recovered": beatty_hit[:3],
                             "note": "irrational phi spread uniformly via Beatty floor(n*phi) -> A000201"}

    order = ["TRUNCATE", "EXTEND", "RANDOMIZE", "HIERARCHIZE", "PARTITION",
             "DISTRIBUTE", "CONCENTRATE", "QUANTIZE", "INVERT"]
    exhibited = [k for k in order if results[k].get("exhibited")]
    canon = [k for k in order if results[k].get("canonical_grade")]
    return {"exhibited_count": f"{len(exhibited)}/9", "exhibited": exhibited,
            "canonical_grade_count": f"{len(canon)}/9", "canonical_grade": canon,
            "not_exhibited": [k for k in order if k not in exhibited],
            "detail": {k: results[k] for k in order}}


def oracle_ok(o):
    return o.ok()


def main():
    import json
    if len(sys.argv) > 1 and sys.argv[1] == "coverage":
        print(json.dumps(coverage(), indent=2, default=str))
    else:
        print("usage: python -m agents.arachne.damage coverage")


if __name__ == "__main__":
    main()
