"""Class (c): label integrity in BASE.

Incidents:
  * W2-34: on the closed 256-site pair tape, ``L_share = 1.0`` is ABSORBING -- once every live organism carries the
    label there is no non-L writer left, so the share cannot fall (0/11 C-A3 runs that reached 1.0 ever dropped).
    "The label persists" is then no evidence of heredity (N13; C-A3 narratives).
  * W2-26: the oid/anc label survives wholesale in-place content replacement (6 control switch edges keep a 7ae3
    label with 61-63 of 64 bytes replaced).
  * W2-35: under BASE write-back rotated (frame-shifted) founder copies escape the label; under ATOMIC a rotated
    copy is never promoted and the member is restored, so ATOMIC label-share verdicts are immune.
  Lesson (W2-35): in BASE the label is neither necessary nor sufficient for descent.

Two checks.

``check_label_readout_write_back`` (STATIC). Flags a script that computes a LABEL-share / label-membership readout
(``o.anc == 0``, ``oid in <lineage set>``, ``L_share``) in a run whose write-back is BASE. Write-back is read from the
code: ``run_ds.runner_cls(world)`` and any ``world.Runner`` subclass whose ``_pair_interact`` restores un-converted
halves with ``_mutate`` are ATOMIC; a plain ``world.Runner`` / subclass without that restore, or an arm literally
named "BASE", is BASE.
    LABEL_READOUT_IN_BASE   a label readout exists and at least one runner is BASE
    OK                      no label readout, or every runner is ATOMIC
    NOT_VERIFIED            a label readout exists but no runner construction is found (write-back rule unknown)

``check_label_absorbing`` (RECORDS). Given per-run label-share series in a closed population, reports the runs whose
"label persists" reading is uninformative because the share reached 1.0 (absorbing), and cross-checks the absorbing
premise empirically (any drop after 1.0 refutes it).
    ABSORBED_LABEL   at least one run's persistence reading rests on an absorbed label (share hit 1.0, never fell)
    OK               no run reached 1.0, or the series show drops after 1.0 (the label can fall: not absorbing)
    NOT_VERIFIED     population closure unknown, or no series
"""
from __future__ import annotations

import ast
import pathlib
import re
from typing import Dict, List, Optional, Sequence

from . import CheckResult, NOT_VERIFIED, OK
from ._static import attr_chain, parse, reachable_code, resolve_modules

NAME_WB = "label_readout_write_back"
NAME_ABS = "label_absorbing"


def _label_readouts(tree: ast.AST) -> List[Dict]:
    out = []
    # `next(o for o in self.orgs if o.anc == 0)` picks the implanted founder at placement, where label == content:
    # an identification, not a label readout. Excluded.
    picks = {id(m) for c in ast.walk(tree) if isinstance(c, ast.Call) and attr_chain(c.func) == "next"
             for m in ast.walk(c)}
    for n in ast.walk(tree):
        if id(n) in picks:
            continue
        if isinstance(n, ast.Compare) and isinstance(n.left, ast.Attribute) and n.left.attr == "anc":
            out.append({"line": n.lineno, "kind": "anc_compare", "code": ast.unparse(n)[:80]})
        elif isinstance(n, ast.Compare) and isinstance(n.left, ast.Attribute) and n.left.attr == "oid" and \
                any(isinstance(op, (ast.In, ast.NotIn)) for op in n.ops):
            out.append({"line": n.lineno, "kind": "oid_in_label_set", "code": ast.unparse(n)[:80]})
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and re.fullmatch(r"(L_share|anc0_share|\w*(descendant|founder|lineage)_share)", n.value):
            out.append({"line": n.lineno, "kind": "label_share_key", "code": n.value})
    return out


def _restores(cls: ast.ClassDef) -> bool:
    for f in cls.body:
        if isinstance(f, ast.FunctionDef) and f.name == "_pair_interact":
            src = ast.unparse(f)
            if "_mutate(" in src and "super()._pair_interact" in src:
                return True
    return False


def write_back_modes(trees: Dict[pathlib.Path, ast.AST], script: pathlib.Path) -> Dict[str, List[str]]:
    """Return {"ATOMIC": [...evidence], "BASE": [...evidence]} from the script (helpers only for runner_cls)."""
    modes: Dict[str, List[str]] = {"ATOMIC": [], "BASE": []}
    tree = trees.get(pathlib.Path(script).resolve())
    if tree is None:
        return modes
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and attr_chain(n.func).endswith("runner_cls"):
            modes["ATOMIC"].append("line %d: runner_cls(world) (X-DONOR-SWAP ATOMIC runner)" % n.lineno)
        if isinstance(n, ast.ClassDef):
            bases = [attr_chain(b) for b in n.bases]
            if "world.Runner" in bases:
                (modes["ATOMIC"] if _restores(n) else modes["BASE"]).append(
                    "line %d: class %s(world.Runner)%s" % (n.lineno, n.name, " restores halves" if _restores(n) else ""))
        if isinstance(n, ast.Call) and attr_chain(n.func) == "world.Runner":
            modes["BASE"].append("line %d: world.Runner(...) instantiated directly" % n.lineno)
    # an arm switch: a class that restores only when the arm is ATOMIC still runs BASE arms
    lits = {c.value for c in ast.walk(tree) if isinstance(c, ast.Constant) and isinstance(c.value, str)}
    if "BASE" in lits and modes["ATOMIC"] and not modes["BASE"]:
        modes["BASE"].append("arm literal 'BASE' beside an ATOMIC runner")
    return modes


def check_label_readout_write_back(script: pathlib.Path, roots, world_dir, _index=None) -> CheckResult:
    res = resolve_modules(script, roots, world_dir, _index=_index)
    readouts = []
    for path, node in reachable_code(res, script):
        for r in _label_readouts(node):
            readouts.append(dict(r, file=str(path)))
    modes = write_back_modes(res["trees"], script)
    details = {"label_readouts": readouts, "write_back": modes}
    if not readouts:
        return CheckResult(NAME_WB, OK, "no label-share / label-membership readout", details)
    if not modes["ATOMIC"] and not modes["BASE"]:
        return CheckResult(NAME_WB, NOT_VERIFIED, "label readout found but no world runner construction: write-back "
                           "rule unknown", details)
    if modes["BASE"]:
        return CheckResult(NAME_WB, "LABEL_READOUT_IN_BASE",
                           "a label readout (%d sites) is computed in a BASE write-back run: in BASE the label is "
                           "neither necessary nor sufficient for descent (absorbing L, labels surviving content "
                           "replacement, unlabelled rotated frames); use content-keyed / frame-aware membership"
                           % len(readouts), details, readouts)
    return CheckResult(NAME_WB, OK, "label readouts only under ATOMIC write-back (immune to the W2-35 leak)", details)


def check_label_absorbing(series: Dict[str, Sequence[float]], closed_population: Optional[bool],
                          full: float = 1.0, eps: float = 1e-9) -> CheckResult:
    if closed_population is None:
        return CheckResult(NAME_ABS, NOT_VERIFIED, "population closure unknown: absorption cannot be assessed")
    if not series:
        return CheckResult(NAME_ABS, NOT_VERIFIED, "no label-share series supplied")
    reached, dropped = [], []
    for run, s in series.items():
        s = [x for x in s if x is not None]
        i = next((j for j, x in enumerate(s) if x >= full - eps), None)
        if i is None:
            continue
        reached.append(run)
        if any(x < full - eps for x in s[i + 1:]):
            dropped.append(run)
    details = {"n_runs": len(series), "reached_full": reached, "dropped_after_full": dropped,
               "closed_population": closed_population}
    if not reached:
        return CheckResult(NAME_ABS, OK, "no run's label share reached %.2f: non-label writers remain, so persistence "
                           "of the label is informative" % full, details)
    if dropped or not closed_population:
        return CheckResult(NAME_ABS, OK, "the label share falls after reaching %.2f in %d/%d runs (or the population is "
                           "open): the label is not absorbing here" % (full, len(dropped), len(reached)), details)
    return CheckResult(NAME_ABS, "ABSORBED_LABEL",
                       "%d/%d runs reached label share %.2f and 0 ever fell, in a closed population: from that epoch "
                       "on 'the label persists' carries no information about heredity" % (len(reached), len(series), full),
                       details, [{"run": r} for r in reached])
