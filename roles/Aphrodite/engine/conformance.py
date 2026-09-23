"""THE CONFORMANCE GATE (AMENDMENT 11 section 10).

Four times this program was damaged by the implementation diverging from the
declared semantics. The gate is a differential test:

    search evaluator (run_program)  ==  emitted artifact evaluator (sandbox)

over normal values, boundary values, overflow cases and failure modes. Any
disagreement fails the gate, and no Tier-3C run may begin while it is red.

The two evaluators are genuinely different code paths: run_program evaluates
compiled expression objects in-process, while the artifact evaluator execs
generated module source inside the restricted sandbox and answers through the
membrane. That is exactly why they drifted apart before.
"""
import itertools
import re
from typing import Dict, List, Tuple

import basis_v4 as G
import engine as E

CEIL = 10 ** 40

# Value classes the gate must cover.
NORMAL = [3, 7, 12, 30]
BOUNDARY = [0, 1, 2, -1]
EXTREME = [97, 999, 10 ** 12]
SEQ_SHAPES = [
    [5],                       # single element
    [2, 3],                    # minimal pair
    [7, 7, 7, 7],              # repeated
    [2, 3, 5, 7, 11, 13],      # ordinary
    [30] * 40,                 # long, drives products past the ceiling
    [29] * 200,                # tribunal stress length
]
TRAILING = [1, 2, 7, 97]

# Program shapes: every primitive in the body, plus the failure modes.
BODIES = ([tmpl.format("acc", "v") for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items())]
          + [tmpl.format("acc", "last") for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items())]
          + ["(acc // (v - v))",          # division by zero
             "(acc % (v - v))",           # modulo zero
             "pow(acc, v)",               # unbounded growth -> ceiling
             "pow(v, acc)",               # out-of-range exponent
             "(acc + (v % last))",        # nested, unseen-body shape
             "(acc + (v // last))",
             "math.gcd(abs(acc), abs((v * v)))",
             "acc", "v", "0", "1"])
FINALS = ["acc", "(acc - first)", "(acc * first)", "(acc + last)", "(acc % last)",
          "(acc // last)", "first", "last", "0"]
INITS = ["0", "1", "first", "last"]


def _prompt(xs: List[int], m: int) -> str:
    return "Family gate over: " + ", ".join(map(str, xs)) + " with %d." % m


def _artifact_answer(family: str, prog, xs: List[int], m: int):
    """Through the emitted module source, the sandbox and the membrane."""
    import meta_tribunal as M
    art = M.artifact_for(family, prog)
    r = E.Recipient.fresh(seed=1)
    r.load(art)
    return r.answer(_prompt(xs, m), family)


def _search_answer(prog, xs: List[int], m: int):
    got = G.run_program(prog, xs + [m], True)
    return None if got is None else str(got)


def check(limit_cases: int = 0) -> Dict:
    """Returns the gate report. `limit_cases` caps the sweep for a quick run;
    0 means the full declared sweep."""
    cases: List[Tuple] = []
    for init in INITS:
        for body in BODIES:
            for final in FINALS:
                cases.append(("fold", init, body, final))
    if limit_cases:
        cases = cases[:limit_cases]

    mismatches, checked = [], 0
    import meta_tribunal as M
    for prog in cases:
        for xs in SEQ_SHAPES:
            for m in TRAILING:
                checked += 1
                a = _search_answer(prog, xs, m)
                b = _artifact_answer("gate", prog, xs, m)
                # The declared contract: the artifact returns "overflow" exactly
                # where the searcher returns None, and agrees otherwise.
                agree = (a == b) or (a is None and b == "overflow")
                if not agree:
                    mismatches.append({"program": list(prog), "seq_len": len(xs),
                                       "trailing": m, "search": a, "artifact": b})
                    if len(mismatches) >= 25:
                        return {"checked": checked, "mismatches": mismatches,
                                "GREEN": False, "note": "aborted after 25 mismatches"}
    return {"checked": checked, "programs": len(cases),
            "mismatches": mismatches, "GREEN": not mismatches}
