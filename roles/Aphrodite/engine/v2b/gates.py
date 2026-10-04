"""Evidence-computed gates, the reachability lint, and the static constant-gate lint.

Historical defect (TH-021; Artemis #871 R-08/R-11; verified 2026-09-29): several frozen gate conditions were
hard-coded True:
- run_s3s4.py S4 condition 4 and condition 8;
- a16.py donor_adjudication_valid.
The S4 POSITIVE_CONTROL was the treatment schema itself. A gate that cannot be False certifies nothing. v2b
therefore enforces three rules:

1. A Gate is a predicate over EVIDENCE. Its value is computed, never asserted, and its result carries a digest of
   the evidence it saw.
2. Before an experiment seals, every gate must be QUALIFIED. It must evaluate True on a declared pass fixture and
   False on a declared fail fixture. A gate that cannot reach both values raises GateUnreachable, and the
   experiment cannot freeze.
3. A positive control must be DISTINCT from the treatment (Control.check_distinct). It must also be able to fail:
   it is qualified like a gate, with a planted case on which it must report failure.

lint_constant_gates(path) is a static AST check. It flags assignments of a literal bool to gate-like names, dict
entries with gate-like keys whose value is a literal bool, `if True` / `if False`, and comparisons of a
literal with itself. It runs over every v2b experiment file in CI (tests/test_gates.py).
"""
import ast
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

GATE_NAME = re.compile(r"(cond|condition|gate|valid|qualif|passed|pass_|_ok$|^ok$|admissible|eligible|control|"
                       r"^[RCE]\d+_|^\d+_|transplant|hostile|no_donor|clean|novel)", re.I)


class GateUnreachable(Exception):
    pass


class ControlNotDistinct(Exception):
    pass


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


@dataclass
class GateResult:
    name: str
    value: bool
    evidence_digest: str
    detail: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self):
        return {"gate": self.name, "value": self.value, "evidence_digest": self.evidence_digest,
                "detail": self.detail}


@dataclass
class Gate:
    name: str
    predicate: Callable[[Any], bool]
    doc: str = ""
    qualified: bool = False
    qualification: Optional[Dict[str, Any]] = None

    def evaluate(self, evidence, detail=None) -> GateResult:
        v = self.predicate(evidence)
        if not isinstance(v, bool):
            raise TypeError("gate %s must return bool, got %r" % (self.name, type(v)))
        return GateResult(self.name, v, _digest(evidence), detail or {})

    def qualify(self, pass_fixture, fail_fixture) -> Dict[str, Any]:
        """The gate must be TRUE on pass_fixture and FALSE on fail_fixture."""
        a, b = self.predicate(pass_fixture), self.predicate(fail_fixture)
        self.qualification = {"gate": self.name, "on_pass_fixture": a, "on_fail_fixture": b,
                              "pass_digest": _digest(pass_fixture), "fail_digest": _digest(fail_fixture)}
        if a is not True or b is not False:
            raise GateUnreachable("gate %s: pass fixture -> %r, fail fixture -> %r (need True, False)"
                                  % (self.name, a, b))
        self.qualified = True
        return self.qualification


def require_qualified(gates: List[Gate]):
    bad = [g.name for g in gates if not g.qualified]
    if bad:
        raise GateUnreachable("unqualified gates at seal: %s" % bad)
    return [g.qualification for g in gates]


@dataclass
class Control:
    """A positive or negative control. `subject` is the object the control plants, e.g. a schema string.
    `treatment` is what the experiment's treatment arm carries."""
    name: str
    subject: Any
    kind: str                     # "POSITIVE" | "NEGATIVE" | "SHAM"

    def check_distinct(self, treatment, equal: Callable[[Any, Any], bool] = None):
        """A positive control equal to the treatment cannot discriminate (the S4 defect). `equal` should be the
        EXTENSIONAL equality of the ruler in force, not string equality."""
        eq = equal(self.subject, treatment) if equal else (self.subject == treatment)
        if eq:
            raise ControlNotDistinct("%s control %s is equal to the treatment %s" % (self.kind, self.subject,
                                                                                    treatment))
        return True


# ---------------------------------------------------------------- static lint
def _is_bool_const(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, bool)


def lint_constant_gates(path) -> List[Dict[str, Any]]:
    """Flags:
    - SUBSCRIPT_CONST: x["key"] = True/False with a string key. This is the dict-of-conditions pattern, as in
      c["4_hostile_evaluation"] = True and out["donor_adjudication_valid"] = True. Every such write is reported,
      because a result field set to a literal is an asserted outcome unless it is overwritten by a
      computation.
    - ASSIGN_CONST: name = True/False for a gate-like name that is NEVER recomputed in the same function. An
      initialise-then-update flag is classified INIT_FLAG and is not an error.
    - DICT_CONST: {"gate-like key": True/False} in a literal.
    - CONST_TEST: `if True` / `if False` (`while True` loop idioms are not flagged).
    - CONST_COMPARE: a literal compared with a literal.
    Each hit carries severity ERROR or INFO."""
    src = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.splitlines()
    hits = []

    def add(node, kind, name, sev="ERROR"):
        hits.append({"path": str(path), "line": node.lineno, "kind": kind, "name": name, "severity": sev,
                     "source": lines[node.lineno - 1].strip()})

    def scope_nodes(fn):
        return list(ast.walk(fn))

    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))] + [tree]
    owner = {}
    for fn in funcs:
        for n in ast.walk(fn):
            owner.setdefault(id(n), fn) if fn is tree else owner.__setitem__(id(n), fn)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _is_bool_const(node.value):
            for t in node.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) and                         isinstance(t.slice.value, str):
                    key = t.slice.value
                    # recomputed later in the same scope with a non-literal?
                    fn = owner.get(id(node), tree)
                    later = [n for n in ast.walk(fn) if isinstance(n, ast.Assign) and n is not node
                             and any(isinstance(tt, ast.Subscript) and isinstance(tt.slice, ast.Constant)
                                     and tt.slice.value == key for tt in n.targets)
                             and not _is_bool_const(n.value)]
                    add(node, "SUBSCRIPT_CONST", key, "INFO" if later else "ERROR")
                elif isinstance(t, ast.Name) and GATE_NAME.search(t.id):
                    fn = owner.get(id(node), tree)
                    recomputed = any(
                        (isinstance(n, ast.Assign) and n is not node and not _is_bool_const(n.value)
                         and any(isinstance(tt, ast.Name) and tt.id == t.id for tt in n.targets))
                        or (isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and n.target.id == t.id)
                        or (isinstance(n, ast.Assign) and n is not node and _is_bool_const(n.value)
                            and n.value.value != node.value.value
                            and any(isinstance(tt, ast.Name) and tt.id == t.id for tt in n.targets))
                        for n in ast.walk(fn))
                    add(node, "INIT_FLAG" if recomputed else "ASSIGN_CONST", t.id, "INFO" if recomputed else "ERROR")
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str) and GATE_NAME.search(k.value)                         and _is_bool_const(v):
                    add(v, "DICT_CONST", k.value)
        elif isinstance(node, (ast.If, ast.IfExp)) and _is_bool_const(node.test):
            add(node, "CONST_TEST", str(node.test.value))
        elif isinstance(node, ast.Compare) and len(node.comparators) == 1 and                 isinstance(node.left, ast.Constant) and isinstance(node.comparators[0], ast.Constant):
            add(node, "CONST_COMPARE", ast.unparse(node))
    return hits


def lint_errors(path):
    return [h for h in lint_constant_gates(path) if h["severity"] == "ERROR"]
