"""blackboard_ops_compare.py — boolean / comparison primitives (lever 2, 2026-06-26).

The 0.558 diagnosis found canary's 20 compare/bool tasks unsolvable: no primitive
produced a yes/no answer or a pick-the-larger-number answer. These two transformer
+ guarded-scorer pairs close that gap. Construct-validated 20/20 on the compare
canary with clean abstention (0 misfires on non-compare tasks) before wiring.

Two task forms in the compare canary:
  - "Is X larger than Y?"            -> yes/no   (parse_comparison + score_by_comparison)
  - "X is less than Y. Which is larger?" -> pick number (parse_which_extreme + score_by_extreme_number)

Typed-state discipline: the TRANSFORMER reads problem_text and writes a typed slot
(comparison / extreme_number); the guarded SCORER keys on that slot (never on
problem_text surface), so routing is semantic, not memorized.
"""
from __future__ import annotations
import re
from blackboard import blackboard_op

_NUM = re.compile(r"-?\d+\.?\d*")


@blackboard_op(
    reads=["problem_text"], writes=["comparison"],
    precondition=lambda s: s.problem_text.strip().lower().startswith("is ")
    and bool(re.search(r"larger|greater|less|smaller|bigger", s.problem_text.lower())),
)
def parse_comparison(state):
    """'Is X larger than Y?' -> comparison (bool). True iff the asserted relation holds."""
    nums = _NUM.findall(state.problem_text)
    t = state.problem_text.lower()
    if len(nums) >= 2:
        x, y = float(nums[0]), float(nums[1])
        if re.search(r"larger|greater|bigger", t):
            state.comparison = (x > y)
        elif re.search(r"less|smaller", t):
            state.comparison = (x < y)
    return state


@blackboard_op(
    reads=["comparison", "candidates"], writes=["selected_answer"],
    precondition=lambda s: s.comparison is not None,
)
def score_by_comparison(state):
    """Select the candidate that begins with 'Yes'/'No' per the parsed comparison."""
    want = "yes" if state.comparison else "no"
    for c in state.candidates:
        if c.strip().lower().startswith(want):
            state.selected_answer = c
            break
    return state


@blackboard_op(
    reads=["problem_text"], writes=["extreme_number"],
    precondition=lambda s: "which" in s.problem_text.lower()
    and bool(re.search(r"larger|smaller|greater|bigger", s.problem_text.lower())),
)
def parse_which_extreme(state):
    """'... Which number is larger?' -> extreme_number (the larger/smaller value, as
    its source-text string so it matches the candidate prefix)."""
    nums = _NUM.findall(state.problem_text)
    t = state.problem_text.lower()
    if len(nums) >= 2:
        pairs = sorted((float(n), n) for n in nums)
        state.extreme_number = pairs[-1][1] if re.search(r"larger|greater|bigger", t) else pairs[0][1]
    return state


@blackboard_op(
    reads=["extreme_number", "candidates"], writes=["selected_answer"],
    precondition=lambda s: bool(s.extreme_number)
    and any(c.strip().startswith(s.extreme_number) for c in s.candidates),
)
def score_by_extreme_number(state):
    """Select the candidate that begins with the extreme number's text."""
    for c in state.candidates:
        if c.strip().startswith(state.extreme_number):
            state.selected_answer = c
            break
    return state
