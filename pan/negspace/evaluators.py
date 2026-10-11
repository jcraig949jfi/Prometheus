"""Distinctness evaluators: verdict(a_src, b_src) -> {'verdict': EQUIVALENT | DISTINCT | UNKNOWN, ...}.

Cheap baselines (frozen thresholds; they never answer UNKNOWN):
  text      difflib similarity ratio of the sources >= 0.80 -> EQUIVALENT
  ast       identical AST after renaming every identifier canonically (rename-invariant hash) -> EQUIVALENT
  embed     bge-small cosine of the sources >= 0.95 -> EQUIVALENT (Pan's own encoder, CPU)
  always_distinct / always_equivalent

Candidate:
  behavioral  run both on the frozen intervention suite in a sandbox; any output difference -> DISTINCT with the
              witness (stream, step, outputs); otherwise EQUIVALENT only if the suite executed every statement of
              BOTH mechanisms, else UNKNOWN with the unexecuted lines and the experiment that would decide
              (inputs that reach them). A crash on one side only is a behavioral difference (DISTINCT).
"""
import ast
import difflib

from . import domain

TEXT_T = 0.80
EMBED_T = 0.95


def text(a, b, **_):
    r = difflib.SequenceMatcher(None, a, b).ratio()
    return dict(verdict="EQUIVALENT" if r >= TEXT_T else "DISTINCT", score=round(r, 3))


class _Canon(ast.NodeTransformer):
    def __init__(self):
        self.names = {}

    def _n(self, s):
        return self.names.setdefault(s, "v{}".format(len(self.names)))

    def visit_Name(self, node):
        return ast.copy_location(ast.Name(id=self._n(node.id), ctx=node.ctx), node)

    def visit_arg(self, node):
        node.arg = self._n(node.arg)
        return node

    def visit_Attribute(self, node):
        self.generic_visit(node)
        node.attr = self._n(node.attr)
        return node

    def visit_FunctionDef(self, node):
        node.name = self._n(node.name)
        self.generic_visit(node)
        return node


def canonical(src):
    tree = _Canon().visit(ast.parse(src))
    return ast.dump(tree, annotate_fields=False)


def ast_hash(a, b, **_):
    return dict(verdict="EQUIVALENT" if canonical(a) == canonical(b) else "DISTINCT")


_EMB = {}


def embed(a, b, **_):
    import numpy as np
    from .. import embed as pembed
    model = pembed.default_model()
    for s in (a, b):
        if s not in _EMB:
            _EMB[s] = pembed.encode_docs([s], model)[0]
    va, vb = np.asarray(_EMB[a], np.float32), np.asarray(_EMB[b], np.float32)
    c = float(va @ vb / ((np.linalg.norm(va) * np.linalg.norm(vb)) or 1.0))
    return dict(verdict="EQUIVALENT" if c >= EMBED_T else "DISTINCT", score=round(c, 4))


def always_distinct(a, b, **_):
    return dict(verdict="DISTINCT")


def always_equivalent(a, b, **_):
    return dict(verdict="EQUIVALENT")


_RUNS = {}


def _run(src):
    if src not in _RUNS:
        why = domain.static_guard(src)
        _RUNS[src] = {"error": "guard: " + why} if why else domain.run(src)
    return _RUNS[src]


def behavioral(a, b, **_):
    ra, rb = _run(a), _run(b)
    if "error" in ra or "error" in rb:
        if ("error" in ra) != ("error" in rb):
            return dict(verdict="DISTINCT", witness="one side fails: {}".format(ra.get("error") or rb.get("error")))
        return dict(verdict="UNKNOWN", reason="both fail to run", errors=[ra["error"], rb["error"]],
                    next_experiment="repair or replace the mechanisms; no behavior to compare")
    for sid, _s, _w in domain.suite():
        ya, yb = ra["outputs"].get(sid), rb["outputs"].get(sid)
        if ya != yb:
            t = next((i for i, (p, q) in enumerate(zip(ya or [], yb or [])) if p != q), None)
            return dict(verdict="DISTINCT", witness=dict(stream=sid, step=t, a=None if t is None else ya[t],
                                                         b=None if t is None else yb[t]))
    miss_a = sorted(domain.executable_lines(a) - set(ra["lines"]))
    miss_b = sorted(domain.executable_lines(b) - set(rb["lines"]))
    if miss_a or miss_b:
        return dict(verdict="UNKNOWN", reason="identical on the suite, but the suite never executed some code",
                    unexecuted=dict(a=miss_a, b=miss_b),
                    next_experiment="construct inputs or interventions that execute the listed lines and compare again")
    return dict(verdict="EQUIVALENT", basis="identical on every suite stream with full statement coverage of both")


EVALUATORS = {"text": text, "ast": ast_hash, "embed": embed, "always_distinct": always_distinct,
              "always_equivalent": always_equivalent, "behavioral": behavioral}
