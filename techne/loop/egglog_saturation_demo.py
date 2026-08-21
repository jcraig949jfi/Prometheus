"""egglog spike (loop cycle 007): equality saturation proves (a*2)/2 == a with UNORDERED
rules -- the noncanonical-composition capability fixed pipelines lack.

Assessment for the circuit program (rung notes R5 / claims ledger):
- R2 proper: overkill (order is supplied; just execute).
- R2.5+: earns rent exactly when multiple equivalent intermediate forms must coexist and a
  later rewrite depends on which form exposes a match -- the e-graph holds ALL forms.
- R4 connection: extraction over a saturated e-graph is strategy selection with the search
  externalized; worth revisiting when the loop reaches R7/R8 (representation shift IS
  choosing the extraction).
- R5 connection (this cycle's rung): an e-graph is branch-holding at scale -- every
  equivalence class is a live "branch". The single-pass separation still applies: saturation
  needs the whole term; it is not a streaming mechanism.
"""
from __future__ import annotations
from egglog import EGraph, Expr, i64Like, StringLike, rewrite, eq, ruleset


class Math(Expr):
    def __init__(self, v: i64Like) -> None: ...
    @classmethod
    def var(cls, name: StringLike) -> "Math": ...
    def __add__(self, other: "Math") -> "Math": ...
    def __mul__(self, other: "Math") -> "Math": ...
    def __truediv__(self, other: "Math") -> "Math": ...


def main() -> None:
    egraph = EGraph()
    a = Math.var("a")
    e_id = egraph.let("e", (a * Math(2)) / Math(2))

    @ruleset
    def rules(x: Math, y: Math, z: Math):
        yield rewrite(x * y).to(y * x)
        yield rewrite((x * y) / z).to(x * (y / z))
        yield rewrite(x / x).to(Math(1))
        yield rewrite(x * Math(1)).to(x)

    egraph.run(rules * 10)
    egraph.check(eq(e_id).to(a))
    print("PASS: (a*2)/2 == a via unordered saturation")


if __name__ == "__main__":
    main()
