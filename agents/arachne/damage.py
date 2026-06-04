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

    results = {}

    def record(op, broken, note, special=None):
        pre = o.match(broken) if special is None else []
        repaired_hit, example = None, None
        if special == "EXTEND":
            pre_amb = o.match(broken[:6], min_len=4)   # short prefix: ambiguous
            full = o.match(broken, min_len=9)          # extended: specific
            exhibited = len(pre_amb) > max(1, len(full)) and len(full) >= 1
            results[op] = {"exhibited": exhibited, "note": note,
                           "short_matches": len(pre_amb), "full_matches": full[:3]}
            return
        if special == "RANDOMIZE":
            exact = o.match(broken)
            stat = o.match_growth(broken)
            results[op] = {"exhibited": len(exact) == 0 and len(stat) > 0, "note": note,
                           "exact": exact[:2], "growth_class": stat[:3]}
            return
        for cand in REPAIRS[op](broken):
            hit = o.match(cand)
            if hit:
                repaired_hit, example = hit, (cand[:6], hit[:3])
                break
        results[op] = {"exhibited": bool(repaired_hit) and not pre,
                       "note": note, "pre_match": pre[:2],
                       "repaired_to": example[1] if example else None,
                       "repaired_prefix": example[0] if example else None}

    # constructed broken cases, each needing one operator
    record("TRUNCATE", [99] + catalan, "junk leading term; drop it -> catalan")
    record("EXTEND", catalan, "5-term prefix ambiguous; full length disambiguates", special="EXTEND")
    record("PARTITION", [v for pair in zip(catalan, factorial) for v in pair],
           "interleave catalan+factorial; bisect -> each matches")
    record("QUANTIZE", harmonic, "harmonic numbers are rational; quantize -> integer seq")
    record("INVERT", catalan[::-1], "reversed catalan; invert -> catalan")
    record("HIERARCHIZE", _psums(fibonacci), "partial sums of fib; difference -> fib")
    record("DISTRIBUTE", catalan, "running-average smoothing -> matches a smoothed seq?")
    # CONCENTRATE: corrupt one middle term
    corrupt = list(catalan); corrupt[12] = corrupt[12] + 7
    record("CONCENTRATE", corrupt, "one corrupted term; isolate/drop it -> rest matches")
    record("RANDOMIZE", [int(sympy.prime(n)) + (n % 3) for n in range(1, K + 1)],
           "perturbed primes; no exact match, growth-class match", special="RANDOMIZE")

    exhibited = [k for k, v in results.items() if v.get("exhibited")]
    return {"exhibited_count": f"{len(exhibited)}/9", "exhibited": exhibited,
            "not_exhibited": [k for k in results if k not in exhibited],
            "detail": results}


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
