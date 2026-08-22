"""MECHANISM AUDIT — how does this defect class get MADE? (Cycle 041.)

Cycle 040 counted TEN instances of the answering-outside-your-domain class among FORTY
measure-like functions and called 25% a "habit". Round-11 review corrected the word:
with no external corpus of comparable functions there is no baseline to be high against, so the
claim is LOCALLY RECURRENT DEFECT CLASS — 11/40 in this corpus, external prevalence unknown. The
migration is justified by local expected loss, not by beating an industry rate. Cycle 041's assignment was to check whether that
survives counting ROOTS rather than SITES, since instance 9 was a wrapper that inherited its
callee's conflation verbatim.

The call graph gives the narrow answer: exactly one inheritance edge among the ten, so nine roots
and the rate barely moves. But call-graph descent is not the only way two bugs can be the same
bug. Three of the ten have the same shape --

    for a, b in combinations(instances, 2):
        ...
        return witness
    return None                      # <- fewer than two instances: loop never ran, sentinel out

-- which is not three independent mistakes. It is one idiom, used three times, that produces the
bug every time it is used. **That is what a root should mean.**

**And the recount does not weaken the claim; it relocates it.** "I write bad measures" becomes
"a few idioms reliably produce this bug, and I reach for them." The second is the more useful
statement because an idiom is greppable and a habit is not -- which yields a prediction that can
fail:

    IF the idiom is the root, THEN idiom-presence should predict CONFLATES among the forty
    measure-like functions, including ones not yet audited.

`predicts_conflation()` runs exactly that and reports the confusion matrix, hits and misses both.
A root notion that does not predict is a relabelling, and would deserve to be thrown out.

**CORRECTION, external review round 11 — and it lands on the framing above, not the data.**

Two different quantities were being conflated by hunting for a single "root count":

    ROOTS               independent originating defects — propensity to CREATE the error
    EXPOSED SITES       measure-like interfaces affected — how much is semantically contaminated
    PROPAGATION FACTOR  sites / roots — how far one creation event travels through wrappers

Neither subsumes the other. One root inherited through fifteen wrappers is one creation event and
fifteen places a caller can receive a lie. `provenance()` reports all three instead of picking one.

And the correction bites: **only INHERITED reduces the root count causally.** Three functions
sharing an idiom are one MECHANISM but still three separate creation events — I wrote the idiom
three times. With 11 exposed sites and 1 inherited, the propagation factor is 1.1, which means
this is repeated CREATION rather than failure to CONTAIN. The idiom clustering therefore explains
*how* the error gets made, and rescues nothing about *how often*. Saying the recount "relocates
the claim" overstated it; the mechanism table is a description of the failure mode, not a smaller
number.
"""
from __future__ import annotations

import ast
import inspect
import textwrap
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

__all__ = ["MECHANISMS", "VACUOUS_QUANTIFIER", "EMPTY_ITERATION_SENTINEL", "ARITHMETIC_IDENTITY",
           "INHERITED", "NO_IDIOM", "classify_mechanism", "mechanism_of_source", "THE_TEN",
           "root_counts", "predicts_conflation", "Prediction", "provenance", "Provenance"]

VACUOUS_QUANTIFIER = "VACUOUS_QUANTIFIER"
EMPTY_ITERATION_SENTINEL = "EMPTY_ITERATION_SENTINEL"
ARITHMETIC_IDENTITY = "ARITHMETIC_IDENTITY"
INHERITED = "INHERITED"
NO_IDIOM = "NO_IDIOM"

MECHANISMS = (VACUOUS_QUANTIFIER, EMPTY_ITERATION_SENTINEL, ARITHMETIC_IDENTITY, INHERITED)

# The ten sites, with the module each lives in.
THE_TEN: Tuple[Tuple[str, str, int], ...] = (
    ("prometheus_math.battery", "structural_constancy", 29),
    ("techne.ladder_circuits.aliasing", "find_aliasing_witness", 37),
    ("techne.ladder_circuits.aliasing", "fiber_search", 37),
    ("prometheus_math.partition", "refinement_multiplicity", 38),
    ("prometheus_math.calibration", "skill", 39),
    ("techne.ladder_circuits.aliasing", "verify_factorization", 39),
    ("techne.ladder_circuits.sweep", "uniform_adversary", 39),
    ("prometheus_math.partition", "is_refinement_chain", 40),
    ("prometheus_math.partition", "chain_direction", 40),
    ("techne.ladder_circuits.sweep", "find_splitting_witness", 40),
)

_TEN_NAMES = frozenset(n for _m, n, _c in THE_TEN)
_EXPANDERS = frozenset(["combinations", "permutations", "product", "zip", "enumerate", "pairwise"])


def _returns_constant_after_loop(fn_node: ast.FunctionDef) -> bool:
    """A `for` at statement level with a constant `return` after it in the same body.

    That is the sentinel shape: zero iterations falls straight through to a return that was
    written to mean "searched and found nothing".
    """
    body = fn_node.body
    for i, stmt in enumerate(body):
        if isinstance(stmt, ast.For):
            for later in body[i + 1:]:
                if isinstance(later, ast.Return) and isinstance(later.value, ast.Constant):
                    return True
    return False


def _has_vacuous_quantifier(fn_node: ast.FunctionDef) -> bool:
    """`all(...)` / `any(...)` in a return position -- empty input yields the identity element."""
    for node in ast.walk(fn_node):
        if isinstance(node, ast.Return) and node.value is not None:
            for sub in ast.walk(node.value):
                if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                        and sub.func.id in ("all", "any")):
                    return True
    return False


def _has_arithmetic_identity(fn_node: ast.FunctionDef) -> bool:
    """A reduction whose empty-case identity is returned DIRECTLY -- `return sum(...)`,
    `return max(...)`, or `return 0`.

    **The returned expression itself is inspected, not its subtree.** The first version walked
    every node under the return, so `return xs[0]` matched on the subscript index and the
    classifier reported ARITHMETIC_IDENTITY for a function that explicitly raises on empty input.
    A planted anti-case caught it before any count from this classifier was used, which is the
    only reason the mechanism table below is worth reading.
    """
    for node in ast.walk(fn_node):
        if isinstance(node, ast.Return) and node.value is not None:
            v = node.value
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Name):
                if v.func.id in ("sum", "max", "min", "len"):
                    return True
            if isinstance(v, ast.Constant) and v.value in (0, 0.0):
                return True
    return False


def _calls_any_of_the_ten(fn_node: ast.FunctionDef) -> bool:
    for node in ast.walk(fn_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in _TEN_NAMES and node.func.id != fn_node.name:
                return True
    return False


def _iterates_over_an_expansion(fn_node: ast.FunctionDef) -> bool:
    for node in ast.walk(fn_node):
        if isinstance(node, ast.For):
            it = node.iter
            if (isinstance(it, ast.Call) and isinstance(it.func, ast.Name)
                    and it.func.id in _EXPANDERS):
                return True
            if isinstance(it, ast.Name):
                return True
    return False


def mechanism_of_source(src: str) -> str:
    """Classify the idiom from source text. Order matters and is stated rather than incidental:
    INHERITED first (a wrapper's mechanism is its callee's, not its own), then the three
    self-contained idioms."""
    try:
        tree = ast.parse(textwrap.dedent(src))
    except SyntaxError:
        return NO_IDIOM
    fn_node = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)), None)
    if fn_node is None:
        return NO_IDIOM
    if _calls_any_of_the_ten(fn_node):
        return INHERITED
    if _iterates_over_an_expansion(fn_node) and _returns_constant_after_loop(fn_node):
        return EMPTY_ITERATION_SENTINEL
    if _has_vacuous_quantifier(fn_node):
        return VACUOUS_QUANTIFIER
    if _has_arithmetic_identity(fn_node):
        return ARITHMETIC_IDENTITY
    return NO_IDIOM


def classify_mechanism(fn: Callable) -> str:
    try:
        return mechanism_of_source(inspect.getsource(fn))
    except (OSError, TypeError):
        return NO_IDIOM


def _resolve(mod_name: str, attr: str) -> Optional[Callable]:
    import importlib
    try:
        fn = getattr(importlib.import_module(mod_name), attr)
    except Exception:  # pragma: no cover
        return None
    return getattr(fn, "__wrapped__", fn)


def root_counts() -> Dict[str, List[str]]:
    """Group the ten sites by mechanism. The values are the sites; the KEYS are the roots."""
    groups: Dict[str, List[str]] = {}
    for mod_name, attr, _cycle in THE_TEN:
        fn = _resolve(mod_name, attr)
        mech = classify_mechanism(fn) if fn is not None else NO_IDIOM
        groups.setdefault(mech, []).append(attr)
    return groups


@dataclass(frozen=True)
class Prediction:
    """The confusion matrix for 'idiom presence predicts conflation'."""
    true_positive: List[str]
    false_positive: List[str]
    false_negative: List[str]
    true_negative: int

    @property
    def precision(self) -> float:
        d = len(self.true_positive) + len(self.false_positive)
        return len(self.true_positive) / d if d else 0.0

    @property
    def recall(self) -> float:
        d = len(self.true_positive) + len(self.false_negative)
        return len(self.true_positive) / d if d else 0.0


def predicts_conflation() -> Prediction:
    """**The test that can fail.** If the idiom is really the root, its presence should predict
    which measure-like functions conflate.

    Ground truth is the union of the ten known sites and anything the cycle-040 degenerate audit
    still reports as CONFLATES. The predictor is idiom-presence. Reported as a full confusion
    matrix with names, not as a score: a false positive here is a PREDICTION OF A NEW INSTANCE
    and is worth more than the accuracy figure.
    """
    from prometheus_math.degenerate_audit import CONFLATES, audit_modules, is_measure_like
    import importlib
    import inspect as _inspect

    verdicts = {r.name: r.verdict for r in audit_modules()}
    tp: List[str] = []
    fp: List[str] = []
    fn_: List[str] = []
    tn = 0
    seen = set()
    modules = {m for m, _n, _c in THE_TEN} | {
        "prometheus_math.partition", "techne.ladder_circuits.aliasing",
        "techne.ladder_circuits.sweep", "prometheus_math.calibration"}
    for mod_name in sorted(modules):
        mod = importlib.import_module(mod_name)
        for name in sorted(dir(mod)):
            if name.startswith("_"):
                continue
            obj = getattr(mod, name, None)
            obj = getattr(obj, "__wrapped__", obj)
            if not _inspect.isfunction(obj) or obj.__module__ != mod_name:
                continue
            if not is_measure_like(obj) or name in seen:
                continue
            seen.add(name)
            has_idiom = classify_mechanism(obj) in MECHANISMS
            conflates = verdicts.get(name) == CONFLATES or name in _TEN_NAMES
            if has_idiom and conflates:
                tp.append(name)
            elif has_idiom and not conflates:
                fp.append(name)
            elif conflates and not has_idiom:
                fn_.append(name)
            else:
                tn += 1
    return Prediction(sorted(tp), sorted(fp), sorted(fn_), tn)


@dataclass(frozen=True)
class Provenance:
    """Three numbers, because they measure three different risks (external review, round 11)."""
    roots: int
    exposed_sites: int
    inherited: List[str]

    @property
    def propagation_factor(self) -> float:
        return self.exposed_sites / self.roots if self.roots else 0.0


def provenance(sites: Optional[List[str]] = None) -> Provenance:
    """Split the class into creation events and exposure.

    A site is NOT a root iff its mechanism is `INHERITED` — it copied a callee's conflation rather
    than inventing one. Sharing an IDIOM does not make two sites one root: the idiom is how the
    error gets made, not a single event that made it twice.

    The interpretation that matters is the ratio. A propagation factor near 1 says the defects are
    independently created and containment is not the problem; a factor of five would say two roots
    leaked through ten interfaces and the diagnosis is failure to contain semantic defects across
    seams. Those call for different fixes, which is why one number could not carry both.
    """
    names = sites if sites is not None else [n for _m, n, _c in THE_TEN] + ["verify_family_incapacity"]
    inherited = [n for n in names if n in _INHERITED_SITES]
    roots = len(names) - len(inherited)
    return Provenance(roots=roots, exposed_sites=len(names), inherited=inherited)


# Established by call-graph analysis, not by grouping: `chain_direction` calls
# `is_refinement_chain` and copied its empty-case answer verbatim.
_INHERITED_SITES = frozenset(["chain_direction"])
