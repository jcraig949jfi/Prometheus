"""The answer-relevant backward slice of Apollo's blackboard, and the normalization
theorem that makes the reachability closure finite.

WHY THIS EXISTS
---------------
A first attempt at BFS over reachable blackboard states did not terminate. The cause is
exact and worth stating: `op_fencepost` (blackboard_ops.py:161) and `distribution_reducer`
(blackboard_ops_v2.py:181) both do `state.evidence.append(...)` and never clear. Applying
either one k times yields k distinct states. The substrate is therefore NOT finite-state,
and option (b) of the STEP 1 instruction -- "prove a normalization theorem showing longer
or repeating programs reduce to <=10 distinct operators" -- is FALSE as literally stated:
`A A A ...` produces unboundedly many distinct states.

But unbounded state is not unbounded BEHAVIOUR. `_evaluate_acc` reads exactly one slot,
`selected_answer`. So define the ANSWER-RELEVANT SLICE:

    D = least set of slots such that
          selected_answer in D,  and
          for every operator op, if writes(op) & D != {} then reads(op) subset-of D.

This is the standard backward program slice on the declared dataflow. Its property:

    THEOREM. If two states agree on every slot in D, then for every operator sequence,
    the resulting states agree on selected_answer.
    PROOF. Induction on sequence length. An operator whose write set misses D cannot
    change any D-slot. An operator whose write set meets D computes its writes from
    reads(op), and reads(op) subset-of D by construction, so it computes the same values
    from two D-agreeing states. Slots outside D never flow into D. QED.

So the BFS may be keyed on D alone. If `evidence` is outside D, the accumulation that
broke termination is invisible to the answer, and the closure over D is finite.

SOUNDNESS OF THE DECLARATIONS
-----------------------------
The theorem depends on `reads` being complete. A read that happens but is not declared
would let a slot outside D flow into D and the slice would be wrong. So the slice is
computed over  declared_reads UNION ast_detected_reads,  where ast_detected_reads are every
`state.X` / `s.X` attribute LOAD in the operator's own source. Over-approximating the read
set can only make D larger, i.e. the slice more conservative. Undeclared reads are reported
rather than silently absorbed.

Read-only with respect to apollo/.
"""
from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APOLLO = ROOT / "apollo"
sys.path.insert(0, str(APOLLO / "src"))
sys.path.insert(0, str(APOLLO / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

import blackboard_evolve as be                # noqa: E402
from blackboard import BlackboardState        # noqa: E402

PROVENANCE = {"write_log", "op_log", "skipped_ops"}
ALL_SLOTS = set(BlackboardState.__dataclass_fields__)


def ast_reads(op):
    """Every `state.X` / `s.X` attribute LOAD in the operator body, plus attributes
    touched by mutation (`state.X.append(...)` is a Load of X followed by a call)."""
    try:
        src = inspect.getsource(op.fn)
        tree = ast.parse(src.strip())
    except (OSError, TypeError, IndentationError, SyntaxError):
        return None                      # cannot verify -> caller treats as unknown
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id in ("state", "s"):
            if node.attr in ALL_SLOTS:
                found.add(node.attr)
    return found


def effective_io():
    """-> {op_name: (reads, writes)} with reads over-approximated, plus an audit list."""
    io, undeclared, unverifiable = {}, [], []
    for name, (op, _role) in be.REGISTRY.items():
        decl_r = set(op.reads)
        decl_w = set(op.writes)
        seen = ast_reads(op)
        if seen is None:
            unverifiable.append(name)
            eff_r = decl_r
        else:
            # a `state.X` that is only ever written still shows up as an Attribute node;
            # subtract the declared writes so pure outputs are not counted as inputs.
            extra = (seen - decl_r) - decl_w - PROVENANCE
            if extra:
                undeclared.append((name, sorted(extra)))
            eff_r = decl_r | extra
        io[name] = (eff_r, decl_w)
    return io, undeclared, unverifiable


def answer_slice(io, target="selected_answer"):
    """Least fixed point of the backward slice."""
    D = {target}
    changed = True
    while changed:
        changed = False
        for _name, (r, w) in io.items():
            if w & D:
                new = r - D
                if new:
                    D |= new
                    changed = True
    return D


def main():
    io, undeclared, unverifiable = effective_io()

    print("operators in registry: %d" % len(io))
    print("declared-read audit (over-approximation used, so this can only ENLARGE D):")
    if undeclared:
        for n, extra in sorted(undeclared):
            print("   UNDECLARED READ  %-28s touches %s" % (n, extra))
    else:
        print("   none")
    if unverifiable:
        print("   source unavailable (declared reads used as-is): %s" % unverifiable)
    print()

    D = answer_slice(io)
    outside = sorted(ALL_SLOTS - D - PROVENANCE)
    print("ANSWER-RELEVANT SLICE  D  (|D| = %d):" % len(D))
    for s in sorted(D):
        print("    %s" % s)
    print()
    print("slots OUTSIDE D (provably cannot influence selected_answer) (%d):" % len(outside))
    for s in outside:
        print("    %s" % s)
    print()

    # The specific question that broke termination.
    accum = ["evidence"]
    for a in accum:
        print("  '%s' in D ? %s" % (a, a in D))
    if "evidence" not in D:
        print()
        print("  => The two accumulating operators, op_fencepost and distribution_reducer,")
        print("     append ONLY to `evidence`, and `evidence` is outside D. Their unbounded")
        print("     growth is invisible to the answer. Keying the BFS on D restores")
        print("     finiteness without weakening the bound.")
    else:
        print()
        print("  => `evidence` IS answer-relevant. The closure is genuinely infinite and")
        print("     the reachability method cannot be used as stated. Report that, do not")
        print("     work around it.")

    # emit for reachable_answers.py to import
    (HERE / "_answer_slice.py").write_text(
        "# generated by answer_slice.py -- do not edit\nD = %r\n" % (sorted(D),),
        encoding="utf-8")
    print("\nwrote %s" % (HERE / "_answer_slice.py"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
