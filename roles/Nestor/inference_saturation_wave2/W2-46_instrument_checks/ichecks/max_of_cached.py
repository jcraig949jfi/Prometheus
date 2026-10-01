"""Class (d): a maximum over cached noisy readouts is a selection amplifier.

Incident (W2-19): C9-H1R's readout ``held_max_final`` is the maximum, over organisms alive at the end, of a held-out
competence that the world validates ONCE per genome on a single 6-episode draw and then caches
(world.py: ``val_cache``; draws shared per validation epoch). An answer-before-read guesser (true held 0.495) was
recorded at 1.0 in 12/12 crossings; P(held = 1.0) on one draw is 1/64, but P(any of 100 validation epochs reaches
1.0) = 0.79. On true scores C9-H1R's I falls below its own 0.15 threshold.

Two checks.

``scan_max_of_cached`` (STATIC). Flags a script that reads a max-type readout of a noisy cached score
(``held_max_final``, ``held_max``, ``held_max_ever``, ``comp_max_*``, ``best_held``, ...) when the world caches that
score (``val_cache`` present in world.py).
    MAX_OF_CACHED   such a readout is read and the world caches the score
    OK              no such readout
    NOT_VERIFIED    a max readout is read but the world source is unreadable

``check_max_amplification`` (MODEL). For a readout value v that is the max over N cached single draws of a score
that is the mean of k Bernoulli(p0) episodes (p0 = the null guesser's per-episode success), compare the single-draw
tail P1 = P(score >= v) with the max tail PN = 1 - (1 - P1)^N.
    MAX_AMPLIFIED   P1 < alpha <= PN: the readout looks extreme only because it is a maximum
    OK              PN < alpha (extreme even as a maximum) or P1 >= alpha (not extreme at all)
    NOT_VERIFIED    N or k unknown / invalid
"""
from __future__ import annotations

import ast
import math
import pathlib
import re
from typing import Optional

from . import CheckResult, NOT_VERIFIED, OK
from ._static import parse, reachable_code, resolve_modules

NAME_SCAN = "max_of_cached"
NAME_AMP = "max_amplification"
MAX_KEY = re.compile(r"^(held|comp|competence|score|fitness)_?max(_\w+)?$|^(max|best)_?(held|comp|competence|score)(_\w+)?$"
                     r"|^d_held_max$")


def world_caches_scores(world_py: pathlib.Path) -> Optional[bool]:
    tree = parse(world_py)
    if tree is None:
        return None
    return any(isinstance(n, ast.Attribute) and n.attr == "val_cache" for n in ast.walk(tree))


def scan_max_of_cached(script: pathlib.Path, roots, world_dir, _index=None) -> CheckResult:
    res = resolve_modules(script, roots, world_dir, _index=_index)
    hits = []
    for path, node in reachable_code(res, script):
        for n in ast.walk(node):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and MAX_KEY.match(n.value):
                hits.append({"file": str(path), "line": n.lineno, "key": n.value})
    cached = world_caches_scores(pathlib.Path(world_dir) / "world.py") if world_dir else None
    details = {"max_readouts": hits, "world_caches_scores": cached}
    if not hits:
        return CheckResult(NAME_SCAN, OK, "no max-of-score readout", details)
    if cached is None:
        return CheckResult(NAME_SCAN, NOT_VERIFIED, "max readout found but the world's caching rule is unreadable", details)
    if not cached:
        return CheckResult(NAME_SCAN, OK, "max readout found but the world re-scores (no cache)", details)
    return CheckResult(NAME_SCAN, "MAX_OF_CACHED",
                       "reads %s: a maximum over cached single-draw scores is a selection amplifier; report a "
                       "cache-bypassed multi-draw score (W2-19)" % sorted({h["key"] for h in hits}), details, hits)


def single_draw_tail(v: float, k: int, p0: float) -> float:
    """P(mean of k Bernoulli(p0) >= v)."""
    j0 = math.ceil(v * k - 1e-9)
    return sum(math.comb(k, j) * p0 ** j * (1 - p0) ** (k - j) for j in range(max(j0, 0), k + 1))


def check_max_amplification(value: float, k: int, n_draws: int, p0: float = 0.5, alpha: float = 0.05) -> CheckResult:
    if not k or k < 1 or not n_draws or n_draws < 1:
        return CheckResult(NAME_AMP, NOT_VERIFIED, "need episodes per draw k >= 1 and number of cached draws N >= 1")
    p1 = single_draw_tail(value, k, p0)
    pn = 1 - (1 - p1) ** n_draws
    details = {"value": value, "k": k, "N": n_draws, "p0": p0, "P_single_draw": p1, "P_max_of_N": pn}
    if p1 < alpha <= pn:
        return CheckResult(NAME_AMP, "MAX_AMPLIFIED",
                           "a null guesser reaches %.3f on one draw with P=%.4f but as a max over %d cached draws with "
                           "P=%.3f: the value is produced by the maximum" % (value, p1, n_draws, pn), details)
    if pn < alpha:
        return CheckResult(NAME_AMP, OK, "extreme even as a max over %d draws (P=%.2g)" % (n_draws, pn), details)
    return CheckResult(NAME_AMP, OK, "not extreme on a single draw (P=%.3f): nothing for the max to amplify" % p1, details)
