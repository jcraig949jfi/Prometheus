"""AR-1 native unit extraction (rule X1) -- fixed before any pilot outcome (AR1_DESIGN.md s5). TARGET-BLIND: it reads
only the found tape, the R1 family's DEV examples and the mechanism KIND (f / p / s, part of the given decomposition,
exactly as E3-KP reads it). It never reads the sealed mechanism, test, tribunal or witness.

X1-a MINIMISE. T* = the found tape with contiguous windows deleted greedily while every dev output (value-or-FAIL) is
     unchanged: repeat { for w in 1, 2, 3: for i = 0 .. len-w: if deleting T[i:i+w] keeps all dev outputs, delete it
     and restart } until no deletion applies.
X1-b CANDIDATE SEGMENTS. Every contiguous segment S of T* such that
       - every token of S is PURE (0 1 2 3 a + - * / % n < = d s, or a macro token), i.e. no store / emit / skip /
         loop / re-list / len / drop token;
       - S contains at least one operator (+ - * / % n < =) and has >= 2 tokens;
       - S's static stack signature (k inputs taken from below its start, values left) and register use fit the kind:
           f : (k, out) = (1, 1), no 'a', last token not a comparison (< =)
           p : (k, out) = (1, 1), no 'a', last token is a comparison (< =)
           s : (k, out) = (2, 1) with no 'a'   OR   (1, 1) containing 'a'  (accumulator on the stack or in A).
X1-c CHOICE. The LONGEST candidate; ties -> the leftmost. None -> NO_EXTRACTABLE_UNIT.
The unit is promoted as macro token '@u<sha8 of its canonical text>' (identical segments collapse to one macro).
"""
import hashlib
from typing import Dict, List, Optional, Sequence, Tuple

from alien import machine as M

COMPARE = frozenset("<=")


def dev_outputs(tape, dev, out_type, macros=None) -> List:
    prog = M.compile_tape(tuple(tape), macros)
    return [M.run_compiled(prog, xs, out_type) for xs, _y in dev]


def minimise(tape: Sequence[str], dev, out_type, macros=None) -> Tuple[str, ...]:
    t = tuple(tape)
    ref = dev_outputs(t, dev, out_type, macros)
    changed = True
    while changed:
        changed = False
        for w in (1, 2, 3):
            for i in range(0, len(t) - w + 1):
                c = t[:i] + t[i + w:]
                outs = dev_outputs(c, dev, out_type, macros)
                if all(M.same_value(a, b) for a, b in zip(outs, ref)):
                    t = c
                    changed = True
                    break
            if changed:
                break
    return t


def fits_kind(seg: Sequence[str], kind: str, macros=None) -> bool:
    if len(seg) < 2:
        return False
    if not all(tok in M.PURE or M.is_macro(tok) for tok in seg):
        return False
    if not any(tok in M.OPERATORS or M.is_macro(tok) for tok in seg):
        return False
    sg = M.signature(seg, macros)
    if sg is None:
        return False
    has_a = "a" in seg
    if kind == "f":
        return sg == (1, 1) and not has_a and seg[-1] not in COMPARE
    if kind == "p":
        return sg == (1, 1) and not has_a and seg[-1] in COMPARE
    if kind == "s":
        return (sg == (2, 1) and not has_a) or (sg == (1, 1) and has_a)
    raise ValueError(kind)


def candidates(tape: Sequence[str], kind: str, macros=None) -> List[Tuple[int, int]]:
    t = tuple(tape)
    out = []
    for i in range(len(t)):
        for j in range(i + 2, len(t) + 1):
            if fits_kind(t[i:j], kind, macros):
                out.append((i, j))
    return out


def extract(tape: Sequence[str], dev, out_type, kind: str, macros=None) -> Dict:
    """Rule X1. Returns {minimised, segment (or None), span, n_candidates}."""
    tmin = minimise(tape, dev, out_type, macros)
    cands = candidates(tmin, kind, macros)
    if not cands:
        return {"minimised": M.to_str(tmin), "segment": None, "span": None, "n_candidates": 0}
    i, j = max(cands, key=lambda ij: (ij[1] - ij[0], -ij[0]))
    return {"minimised": M.to_str(tmin), "segment": M.to_str(tmin[i:j]), "span": [i, j],
            "n_candidates": len(cands)}


def macro_name(segment_text: str) -> str:
    return "@u" + hashlib.sha256(segment_text.encode()).hexdigest()[:8]


def probe_frame(kind: str, args: Tuple[int, ...]) -> Tuple[List[int], int]:
    """The fixed probe binding (diagnostic only): f/p: stack [v], A = 0; s: stack [a, b], A = a."""
    if kind in ("f", "p"):
        return [args[0]], 0
    return [args[0], args[1]], args[0]


def unit_value(segment: Sequence[str], kind: str, args: Tuple[int, ...], macros=None):
    st, reg = probe_frame(kind, args)
    v = M.run_frame(tuple(segment), st, reg, macros)
    if kind == "p" and v != M.FAIL:
        return v != 0
    return v
