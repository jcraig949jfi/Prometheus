"""Class (b): the readout's ruler is not the world's own ruler.

Incidents:
  * W2-40 / W2-30: the world counts a birth by FID (``predecessor_accepts``: fid_other >= 0.90, fid_self < 0.90,
    donor wrote >= 0.25 n; ``_fidelity`` = positional share of identical bytes, world.py:1373) and BASE has NO keep
    test, so members that drift stay in the lineage. An EXACT-identity keep ruler counts them as losses (C3 side-0
    exact keep 0.519 vs class keep 0.955) and makes the C3 arm uninformative.
  * W2-26: W2-17's S0/S1 "types" were an event-side tag, not genotypes.

``world_member_rule(world_dir)`` builds the world's own membership predicate by extracting ``_fidelity`` from
world.py and ``PAIR_FID_OTHER_MIN`` from constants.py with ``ast`` (only that pure function is compiled; the world
module is never imported or run).

``check_ruler_agreement(world_member, readout_member, pairs)``: both predicates take (reference, genome) bytes and
return True when the readout counts the genome as the reference's lineage member / keep. ``pairs`` should be REAL
in-world (parent, member) genome pairs.
    RULER_MISMATCH   the readout disagrees with the world's ruler on more than `max_disagree` of pairs
                     (details: how many the readout drops that the world keeps, and vice versa)
    OK               agreement within tolerance
    NOT_VERIFIED     no pairs, or a predicate raised
"""
from __future__ import annotations

import ast
import pathlib
from typing import Callable, Optional, Sequence, Tuple

from . import CheckResult, NOT_VERIFIED, OK
from ._static import parse

NAME = "ruler_agreement"


def load_function(path: pathlib.Path, name: str) -> Optional[Callable]:
    tree = parse(path)
    if tree is None:
        return None
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name), None)
    if fn is None:
        return None
    mod = ast.Module(body=[fn], type_ignores=[])
    ns: dict = {}
    exec(compile(mod, str(path), "exec"), {"__builtins__": {"len": len, "min": min, "max": max, "sum": sum,
                                                          "range": range}}, ns)
    return ns[name]


def load_constant(path: pathlib.Path, dict_name: str, key: str):
    tree = parse(path)
    if tree is None:
        return None
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == dict_name for t in n.targets) \
                and isinstance(n.value, (ast.Dict, ast.Call)):
            d = n.value
            if isinstance(d, ast.Call):        # C = MappingProxyType({...}) / dict({...})
                d = next((a for a in d.args if isinstance(a, ast.Dict)), None)
                if d is None:
                    continue
            for k, v in zip(d.keys, d.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    return None


def world_member_rule(world_dir: pathlib.Path) -> Optional[Callable[[bytes, bytes], bool]]:
    world_dir = pathlib.Path(world_dir)
    fid = load_function(world_dir / "world.py", "_fidelity")
    thr = load_constant(world_dir / "constants.py", "C", "PAIR_FID_OTHER_MIN")
    if fid is None or thr is None:
        return None
    rule = lambda ref, g: fid(ref, g) >= thr  # noqa: E731
    rule.threshold = thr  # type: ignore[attr-defined]
    rule.fidelity = fid  # type: ignore[attr-defined]
    return rule


def check_ruler_agreement(world_member: Callable, readout_member: Callable, pairs: Sequence[Tuple[bytes, bytes]],
                          max_disagree: float = 0.05) -> CheckResult:
    if not pairs:
        return CheckResult(NAME, NOT_VERIFIED, "no (reference, genome) pairs supplied")
    if world_member is None or readout_member is None:
        return CheckResult(NAME, NOT_VERIFIED, "a ruler is missing")
    try:
        w = [bool(world_member(a, b)) for a, b in pairs]
        r = [bool(readout_member(a, b)) for a, b in pairs]
    except Exception as e:  # noqa: BLE001
        return CheckResult(NAME, NOT_VERIFIED, "a ruler raised %s: %s" % (type(e).__name__, e))
    drop = sum(1 for x, y in zip(w, r) if x and not y)
    add = sum(1 for x, y in zip(w, r) if y and not x)
    rate = (drop + add) / len(pairs)
    details = {"n": len(pairs), "world_members": sum(w), "readout_members": sum(r),
               "readout_drops_world_member": drop, "readout_adds_non_member": add, "disagreement": rate}
    if rate > max_disagree:
        return CheckResult(NAME, "RULER_MISMATCH",
                           "the readout disagrees with the world's own ruler on %.1f%% of real pairs (drops %d world "
                           "members, adds %d): predictions from this ruler describe a different world"
                           % (100 * rate, drop, add), details)
    return CheckResult(NAME, OK, "readout agrees with the world's ruler (%.1f%% disagreement)" % (100 * rate), details)
