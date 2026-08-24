"""Flag selection steps that silently bias a population. AST-based, no inference.

The single largest error class in cycles 049-059 was WRONG-POPULATION: a measurement taken
over one set of rows and quoted as a property of another. Eight instances. A positive control
CANNOT detect this -- calibrating the scale does not tell you that you weighed the wrong pile.

But the CAUSE is usually a specific, syntactically visible operation:

    head -N / [:N] / list(...)[:n]      an ORDERED slice used as if it were a sample
    .rglob(...) with a cap             traversal order becomes selection
    sorted(...)[:n]                    rank-order selection presented as representative

Two real instances from this record:
    cycle 055  `grep ... | head -40` returned 40 hits ALL FROM ONE ROLE, because the traversal
               reached ergon first. The population was described as "cross-role" and was 87.5%
               one role.
    cycle 052  timed the FIRST 40 rows of an ordered catalog (median degree 8) and quoted the
               result for a table whose real median degree is 115.

This is decidable by AST: the slice either appears in a population-producing path or it does
not. It cannot tell you the sample is UNREPRESENTATIVE -- only that it was taken by position.
That distinction is the honest limit and is stated rather than glossed.
"""
from __future__ import annotations

import argparse
import ast
import pathlib

SELECTORS = {"glob", "rglob", "iterdir", "listdir", "walk", "findall", "finditer"}


class SliceAfterSelect(ast.NodeVisitor):
    def __init__(self, path: str):
        self.path = path
        self.hits: list[tuple[int, str]] = []

    def _is_positional_slice(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice)
                and node.slice.step is None)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if self._is_positional_slice(node):
            src = ast.unparse(node)[:70]
            inner = ast.unparse(node.value)[:70]
            # a positional slice of a traversal / sort / match result is order-as-selection
            if any(f"{s}(" in inner for s in SELECTORS):
                self.hits.append((node.lineno, f"ordered-slice of a traversal: {src}"))
            elif inner.startswith(("sorted(", "list(")):
                self.hits.append((node.lineno, f"ordered-slice of a sequence: {src}"))
        self.generic_visit(node)


def lint(path: pathlib.Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as e:
        return [f"{path}: unparseable ({e.msg})"]
    v = SliceAfterSelect(str(path))
    v.visit(tree)
    return [f"{path}:{ln}  {msg}" for ln, msg in v.hits]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    a = ap.parse_args()
    out: list[str] = []
    for p in a.paths:
        pp = pathlib.Path(p)
        files = sorted(pp.rglob("*.py")) if pp.is_dir() else [pp]
        for f in files:
            if "__pycache__" in str(f):
                continue
            out.extend(lint(f))
    for line in out:
        print("  " + line)
    print(f"\n{len(out)} positional-selection sites "
          f"(each is order-as-selection; representativeness is NOT decidable here)")
    return 1 if out else 0


if __name__ == "__main__":
    raise SystemExit(main())
