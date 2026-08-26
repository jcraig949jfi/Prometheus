#!/usr/bin/env python3
"""One renderer for every proof step, true or planted.

The fingerprint hazard measured in `epoch/SIMULATION_FINDINGS.md`: each mutation
operator used to append its own phrase to the step it rewrote — "CONVERSE:",
"Cancelling the factor", "the same estimate is taken to hold from n = 0 onward".
A falsifier could grep those and locate 84% of planted defects without doing any
mathematics, which is the mirror image of the rulebook's kill condition about
attacks exploiting fingerprints.

Patching the offending phrases would only remove the tells someone noticed. The
structural fix is this module: every step's prose is generated from its machine
check by the same function, so a mutated step and an untouched step of the same
kind are written by the same code path with different parameters. A lexical
signature is then impossible in principle rather than absent by inspection.

The rule this module exists to enforce: **no renderer may take the mutation as
an argument.** `render()` sees a check and nothing else. It cannot know whether
what it is describing is true.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------
# expression pretty-printing: Python source -> ordinary mathematical prose
# --------------------------------------------------------------------------

_SUBS = [
    (r"\*\*", "^"),
    (r"//", "/"),
    (r"\s*%\s*", " mod "),
    (r"\s*==\s*", " = "),
    (r"\s*!=\s*", " != "),
    (r"\s*>=\s*", " >= "),
    (r"\s*<=\s*", " <= "),
    (r"\s*\*\s*", "*"),
]


def expr(e: str) -> str:
    """Render a generator expression as readable mathematics."""
    s = e
    s = re.sub(r"sum_k\(([^,]+),\s*(\d+)\)", r"the sum of k^\2 for k = 1..\1", s)
    s = re.sub(r"pow\(([^,]+),\s*([^,]+),\s*([^)]+)\)", r"\1^(\2) mod \3", s)
    s = re.sub(r"lin_rec\(([^,]+),[^)]*\)", r"a_\1", s)
    s = re.sub(r"stop_time\(([^)]+)\)", r"the stopping time of \1", s)
    s = re.sub(r"shortcut_time\(([^)]+)\)", r"the stopping time of \1", s)
    s = re.sub(r"graph_degrees\(([^,]+),\s*\d+\)", r"the degree sequence of \1", s)
    s = re.sub(r"graph_is_connected\(([^,]+),\s*\d+\)\s*=+\s*1",
               r"\1 is connected", s)
    s = re.sub(r"graph_min_component_size\(([^,]+),\s*\d+\)",
               r"the smallest component of \1", s)
    s = re.sub(r"graph_edge_count\(([^,]+),\s*\d+\)", r"the edge count of \1", s)
    s = re.sub(r"\(1 if (.+?) else 0\)", r"[\1]", s)
    for pat, rep in _SUBS:
        s = re.sub(pat, rep, s)
    return s.strip()


def _subject(var: str) -> str:
    return "graph G" if var == "g" else "integer n"


def _range(check: dict) -> str:
    var, lo, hi = check.get("var", "n"), check.get("lo"), check.get("hi")
    if var == "g":
        return f"every graph G with index between {lo} and {hi}"
    return f"every integer {var} with {lo} <= {var} <= {hi}"


# --------------------------------------------------------------------------
# the renderers. None of them can see whether the claim is true.
# --------------------------------------------------------------------------

def render(check: dict) -> str:
    kind = check["kind"]
    var = check.get("var", "n")

    if kind == "forall_identity":
        return (f"For {_range(check)}, {expr(check['lhs'])} equals "
                f"{expr(check['rhs'])}.")

    if kind == "forall_inequality":
        word = {"<=": "is at most", "<": "is less than",
                ">=": "is at least", ">": "exceeds"}[check.get("op", "<=")]
        return (f"For {_range(check)}, {expr(check['lhs'])} {word} "
                f"{expr(check['rhs'])}.")

    if kind == "forall_implication":
        return (f"For {_range(check)}, if {expr(check['ante'])} then "
                f"{expr(check['cons'])}.")

    if kind == "forall_equivalence":
        return (f"For {_range(check)}, {expr(check['ante'])} holds exactly when "
                f"{expr(check['cons'])} holds.")

    if kind == "congruence":
        return (f"For {_range(check)}, {expr(check['lhs'])} is congruent to "
                f"{expr(check['rhs'])} modulo {check['modulus']}.")

    if kind == "forall_pred":
        return f"For {_range(check)}, {expr(check['pred'])}."

    if kind == "case_cover":
        cases = "; ".join(expr(c) for c in check["cases"])
        return (f"For {_range(check)}, at least one of the following holds: "
                f"{cases}.")

    if kind == "exists_pred":
        return (f"There is a {_subject(var)} with {check['lo']} <= {var} <= "
                f"{check['hi']} for which {expr(check['pred'])}.")

    if kind == "instantiation":
        return f"At {var} = {check['point']}, {expr(check['pred'])}."

    if kind == "generalization":
        return (f"The steps above establish the statement up to "
                f"{check['established_hi']}, and it is taken to hold for the "
                f"whole range up to {check['asserted_hi']}.")

    if kind == "subset":
        return (f"The range [{check['lo']}, {check['hi']}] lies inside "
                f"[{check['outer_lo']}, {check['outer_hi']}].")

    raise ValueError(f"no renderer for check kind {kind}")


def render_steps(steps: list[dict]) -> list[dict]:
    """Rewrite every step's text from its own check. Mutations included."""
    for s in steps:
        s["text"] = render(s["check"])
    return steps
