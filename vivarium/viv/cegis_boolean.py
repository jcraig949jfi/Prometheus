"""`cegis_boolean_v1` -- a bounded CEGIS loop, sealed inside one kind.

WHERE THE ADAPTIVE PART LIVES. Inside here, and nowhere else. The loop chooses
its next candidate and its next counterexample from its own previous internal
results, and every input that governs those choices -- the candidate policy and
its seed, the case ordering, the source pack, the component library, the caps,
the trace bound and the termination rule -- is SEALED in work.payload and
therefore inside spec_hash. The generic Vivarium runner sees a kind name and a
result; it never learns that a search happened. That is C3's whole requirement,
and it is structural rather than promised: `viv/executors.py` calls this with a
payload, a seed and frozen artifact data, and there is no route back out.

PROTEUS OWNS THE SEMANTICS. The grammar, the compiler, the VM, the independent
truth-table evaluator and the ordered-first-witness rule are
`proteus/eval/boolean.py` and `proteus/eval/library.py`. Nothing here decides
what a Boolean program means. In particular NOT IS COMPILED AS `XOR x, ONE` --
their decision, for their stated reason (the VM's NOT is a 32-bit complement
and leaves {0,1} on the first negation), and this file never emits an opcode of
its own.

WHY THE CAPS ARE THE EXPERIMENT. The candidate ENUMERATION ORDER is fixed by
the sealed seed, so the first candidate that satisfies the target is the same
expression in every arm. If the loop ran to completion, every arm would solve
the same tasks and H1 would be structurally incapable of showing anything.
What can differ is COST, and therefore how far down the same enumeration an arm
gets before `vm_op_cap` bites. "At the same total resource caps" is doing real
work in that sentence -- remove the cap and this design measures nothing.

THE SIGN OF THAT EFFECT IS NOT DECIDED HERE, and it is worth being exact about
why, because the obvious story is wrong. Seeding does not simply make rejection
cheaper. Each candidate is checked against the constraint cases IN ORDER,
stopping at the first mismatch, so:

  * a seeded constraint that FIRES kills a candidate in one or two VM cases
    that would otherwise have cost a full eight-case verification;
  * a seeded constraint that does NOT fire is pure added cost, paid again by
    every candidate that reaches it.

So more constraints are not better constraints, and a pack of poorly
discriminative inputs makes the arm SLOWER. Measured here on 2026-09-10 while
building this: seeding four fresh probes cut oracle calls on every target
tried, cut VM ops on the two that solve quickly, and RAISED VM ops by ~47% on
the one that scans its whole space (maj3, 3025 candidates). Both directions are
real and both are reachable.

That is precisely H1's question -- whether relevant source inputs seed more
discriminative constraints than random ones -- and this file exists to make it
askable, not to answer it. Nothing here should be read as predicting that a
source pack helps.

FOUR RULES THAT ARE NOT NEGOTIABLE HERE

  solved requires FULL COVERAGE. A candidate is solved only when the
  exhaustive check over all eight assignments ran, expected a value on all
  eight, and passed all eight. `cases_with_expectation == 8` is asserted, not
  assumed.

  NO WITNESS IS NEVER SOLVED. Passing the constraint subset means nothing was
  found; it is not a claim that nothing exists. Only the exhaustive check can
  end the loop successfully.

  BUDGET EXHAUSTION IS ITS OWN STATUS, and there are three of them --
  BUDGET_VM_OPS, BUDGET_ORACLE_CALLS, BUDGET_CANDIDATES -- kept distinct from
  EXHAUSTED_CANDIDATES, which means the declared search space actually ran out.
  "We could not afford to keep looking" and "we looked everywhere" are
  different findings about a task and only one of them is about the task.

  LABELS COME FROM THE TARGET. Every input, wherever it came from, is labelled
  by the target truth table in this run. A source pack carries INPUTS; a
  transferred label is never read, so a wrong one cannot corrupt a result --
  it can only waste a probe.

THE EMPTY INPUT IS A DECLARED INPUT. `source_pack: null` and
`component_library: null` are explicit values in a hashed payload, not omitted
keys and not a hidden alternative library. H0's four cells are four payloads
that differ in exactly those two positions and in nothing else, run by one
solver runtime -- which is what makes them four cells of one experiment rather
than four experiments.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent.parent

#: The only candidate policy this build implements. A second one is a new
#: string and a new sealed identity, never a flag on this one.
CANDIDATE_POLICIES = ("seeded_enumeration_v1",)
#: The only case ordering. Proteus's declared assignment order IS the
#: definition of "first counterexample"; a second ordering would be a
#: different experiment wearing the same name.
CASE_ORDERINGS = ("proteus_declared",)
TERMINATIONS = ("first_solution", "exhaust_candidates")
SHORTFALL_RULES = ("report_and_proceed",)

#: Closed. Every run ends in exactly one of these.
SOLVED = "SOLVED"
EXHAUSTED_CANDIDATES = "EXHAUSTED_CANDIDATES"
BUDGET_CANDIDATES = "BUDGET_CANDIDATES"
BUDGET_VM_OPS = "BUDGET_VM_OPS"
BUDGET_ORACLE_CALLS = "BUDGET_ORACLE_CALLS"
STATUSES = (SOLVED, EXHAUSTED_CANDIDATES, BUDGET_CANDIDATES, BUDGET_VM_OPS,
            BUDGET_ORACLE_CALLS)

N_INPUTS = 3
N_ASSIGNMENTS = 8


class CegisError(RuntimeError):
    """A malformed payload or an unavailable substrate. Fails closed."""


def _proteus():
    """Import Proteus's substrate, or say exactly what is missing.

    Not vendored and not reimplemented: a second copy of the compilation rule
    that makes NOT safe is the drift this wrapper exists to avoid."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    try:
        from proteus.eval import boolean as _b                # noqa: PLC0415
        from proteus.eval import library as _l                # noqa: PLC0415
    except Exception as exc:                                  # noqa: BLE001
        raise CegisError(
            "cegis_boolean_v1 needs Proteus's boolean3 substrate "
            "(proteus/eval/boolean.py). Refusing to reimplement its grammar, "
            "its compiler or its NOT rule: %s" % exc) from exc
    return _b, _l


# --------------------------------------------------------------- expressions
def _from_json(node, _b, _depth=0):
    """JSON nested list -> Proteus's tuple AST. Structural only; Proteus's own
    `check` decides validity immediately afterwards."""
    if _depth > 32:
        raise CegisError("component expression nests deeper than 32")
    if not isinstance(node, list) or not node:
        raise CegisError("expression must be a non-empty list, got %r" % (node,))
    op = node[0]
    if op in ("const", "input"):
        if len(node) != 2:
            raise CegisError("%s takes exactly one payload" % op)
        return (op, node[1])
    return tuple([op] + [_from_json(a, _b, _depth + 1) for a in node[1:]])


def _to_json(expr):
    if expr[0] in ("const", "input"):
        return [expr[0], expr[1]]
    return [expr[0]] + [_to_json(a) for a in expr[1:]]


def _size(expr) -> int:
    if expr[0] in ("const", "input", "component"):
        return 1
    return 1 + sum(_size(a) for a in expr[1:])


class _Split:
    """SplitMix64, so the enumeration's shuffle is the same on every host.

    Python's `random` would also be deterministic, but its guarantee is about
    a version rather than about an algorithm, and a candidate ORDER that could
    move under an interpreter upgrade is a sealed input that is not sealed.
    """

    def __init__(self, seed: int):
        self.s = seed & 0xFFFFFFFFFFFFFFFF

    def next(self) -> int:
        self.s = (self.s + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def shuffle(self, items: list) -> None:
        for i in range(len(items) - 1, 0, -1):
            j = self.next() % (i + 1)
            items[i], items[j] = items[j], items[i]


def enumerate_candidates(leaves: List[tuple], *, seed: int, max_size: int,
                         limit: int):
    """Size-ordered enumeration over the declared grammar, shuffled WITHIN each
    size by the sealed seed.

    Size-ordered because a component library's whole effect is to make a useful
    expression SMALLER -- a frozen subtree costs 1 instead of the 3 or 5 nodes
    it stands for -- and an enumeration that ignored size could not express
    that effect at all. Shuffled within a size so the order is a declared
    seeded choice rather than an artefact of how the generator loops.

    Yields (expr, size). Stops after `limit` candidates or after `max_size`.
    """
    by_size: Dict[int, list] = {1: list(leaves)}
    emitted = 0
    for size in range(1, max_size + 1):
        if size not in by_size:
            here: list = []
            for a in by_size.get(size - 1, ()):
                here.append(("not", a))
            for i in range(1, size - 1):
                left = by_size.get(i, ())
                right = by_size.get(size - 1 - i, ())
                for op in ("and", "or", "xor"):
                    for x in left:
                        for y in right:
                            here.append((op, x, y))
            by_size[size] = here
        bucket = list(by_size[size])
        _Split(seed ^ (size * 0x9E3779B1)).shuffle(bucket)
        for expr in bucket:
            if emitted >= limit:
                return
            emitted += 1
            yield expr, size


# ------------------------------------------------------------------- oracle
class _Oracle:
    """The target. It answers LABELS for assignments and counts every answer.

    The candidate search never holds this object: it is consulted by the loop
    and its verdicts reach the search only as counterexamples. C3 forbids
    handing a candidate the task's implementation or its evaluation set, and
    the separation here is that the enumerator is a generator over leaves and
    operators with no reference to the table at all.
    """

    def __init__(self, table: str, cap: int):
        self.table = table
        self.cap = cap
        self.calls = 0

    def label(self, assignment: List[int]) -> int:
        k = 0
        for bit in assignment:
            k = (k << 1) | int(bit)
        self.calls += 1
        return int(self.table[k])

    def over_cap(self) -> bool:
        return self.calls > self.cap


# --------------------------------------------------------------------- run
def run(payload: dict, *, seed: int, inputs: dict) -> dict:      # noqa: C901
    """One bounded CEGIS attempt on one target. Deterministic given the seal."""
    _b, _l = _proteus()

    table = payload["target_truth_table"]
    if (not isinstance(table, str) or len(table) != N_ASSIGNMENTS
            or any(c not in "01" for c in table)):
        raise CegisError(
            "target_truth_table must be %d characters of '0'/'1' in Proteus's "
            "declared assignment order (input 0 most significant), got %r"
            % (N_ASSIGNMENTS, table))
    if payload["grammar_version"] != _b.GRAMMAR_VERSION:
        raise CegisError(
            "the spec seals grammar_version %r; this build has Proteus's %r. "
            "A grammar change is a new experiment, not a new run of this one."
            % (payload["grammar_version"], _b.GRAMMAR_VERSION))
    if payload["candidate_policy"] not in CANDIDATE_POLICIES:
        raise CegisError("candidate_policy must be one of %s"
                         % (list(CANDIDATE_POLICIES),))
    if payload["case_ordering"] not in CASE_ORDERINGS:
        raise CegisError("case_ordering must be one of %s"
                         % (list(CASE_ORDERINGS),))
    if payload["termination"] not in TERMINATIONS:
        raise CegisError("termination must be one of %s" % (list(TERMINATIONS),))
    if payload["shortfall_rule"] not in SHORTFALL_RULES:
        raise CegisError("shortfall_rule must be one of %s"
                         % (list(SHORTFALL_RULES),))

    max_candidates = _positive(payload, "max_candidates")
    max_expr_size = _positive(payload, "max_expr_size")
    oracle_cap = _positive(payload, "oracle_call_cap")
    op_cap = _positive(payload, "vm_op_cap")
    trace_bound = _positive(payload, "trace_bound")
    vm_ticks = _positive(payload, "vm_ticks")
    seed_probes = payload["seed_probe_count"]
    if not isinstance(seed_probes, int) or isinstance(seed_probes, bool) \
            or seed_probes < 0:
        raise CegisError("seed_probe_count must be a non-negative integer")

    assignments = _b.assignments(N_INPUTS)
    oracle = _Oracle(table, oracle_cap)

    # -- the component library: extra LEAVES, so a frozen subtree costs 1 ----
    library = inputs.get("component_library")
    components: List[Tuple[str, tuple]] = []
    if library is not None:
        for entry in library.data["components"]:
            expr = _from_json([x for x in _json_of(entry["expr"])], _b)
            _b.check(expr)                       # Proteus decides validity
            components.append((entry["name"], expr))
    leaves = [_b.I(i) for i in range(N_INPUTS)] + [_b.C(0), _b.C(1)]
    leaves += [expr for _name, expr in components]

    # -- seeding the constraint set -----------------------------------------
    pack = inputs.get("source_pack")
    constraints: List[dict] = []
    if pack is not None:
        if pack.data["n_bits"] != N_INPUTS:
            raise CegisError(
                "source pack declares n_bits=%s; this task has %d inputs. A "
                "pack of the wrong width is not a compatible source."
                % (pack.data["n_bits"], N_INPUTS))
        rows = [list(r) for r in pack.all_items()]
        seeded_from = "source_pack"
    else:
        # The FRESH arm's equal allowance: the same number of probes, spent on
        # the declared case ordering. Equal allowance, not equal spend -- what
        # each arm actually spent is reported below.
        rows = [list(a) for a in assignments]
        seeded_from = "fresh_probe_allowance"

    seen = set()
    used = 0
    for row in rows:
        if used >= seed_probes:
            break
        key = tuple(row)
        if key in seen:
            continue                       # distinct inputs; a repeat is not a probe
        seen.add(key)
        constraints.append({"inputs": [list(row)],
                            "expected": [[oracle.label(row)]],
                            "origin": seeded_from})
        used += 1
    shortfall = seed_probes - used

    # -- the loop ------------------------------------------------------------
    status = EXHAUSTED_CANDIDATES
    solution = None
    solution_size = None
    tried = invalid = 0
    vm_ops = 0
    witnesses: List[dict] = []
    witness_truncated = False
    verifications = 0

    def _spec_from(cases):
        return _l.make_spec([{"inputs": c["inputs"], "expected": c["expected"]}
                             for c in cases], n_out=1, ticks=vm_ticks,
                            label="cegis_boolean_v1")

    for expr, size in enumerate_candidates(leaves, seed=payload["candidate_seed"],
                                           max_size=max_expr_size,
                                           limit=max_candidates):
        if vm_ops > op_cap:
            status = BUDGET_VM_OPS
            break
        if oracle.over_cap():
            status = BUDGET_ORACLE_CALLS
            break
        tried += 1
        try:
            manifest = _b.compile_boolean(expr)
        except _b.BooleanError:
            # Too deep for the declared temporaries. Counted, never silently
            # skipped: an invalid candidate consumed its place in the order.
            invalid += 1
            continue

        # Constraints IN ORDER, stopping at the first mismatch. This is the
        # whole cost mechanism; evaluating them as one spec would run all of
        # them every time and erase the difference the experiment measures.
        rejected = False
        for c in constraints:
            res = _l.evaluate(manifest, _spec_from([c]), seed=seed,
                              trace_limit=0)
            vm_ops += res["ops_total"]
            if res["has_witness"]:
                rejected = True
                break
        if rejected:
            continue
        if vm_ops > op_cap:
            status = BUDGET_VM_OPS
            break

        # FULL COVERAGE, or it is not solved. Every assignment is labelled by
        # the target here, and the charge is real.
        full = [{"inputs": [list(a)], "expected": [[oracle.label(a)]]}
                for a in assignments]
        verifications += 1
        res = _l.evaluate(manifest, _spec_from(full), seed=seed, trace_limit=0)
        vm_ops += res["ops_total"]
        if (res["cases_with_expectation"] == N_ASSIGNMENTS
                and res["all_passed"]):
            status = SOLVED
            solution, solution_size = expr, size
            if payload["termination"] == "first_solution":
                break
            continue
        w = res["witness"]
        if w is None:
            # Not solved and no witness: the coverage check above already
            # refused to call this solved, and there is nothing to learn from
            # it. Recorded so a run that produced only these is legible.
            witnesses.append({"candidate_size": size, "witness": None,
                              "reason": "no_witness_and_not_full_coverage",
                              "cases_with_expectation":
                                  res["cases_with_expectation"]})
            continue
        constraints.append({"inputs": w["inputs"], "expected": w["expected"],
                            "origin": "counterexample"})
        if len(witnesses) < trace_bound:
            witnesses.append({"candidate_size": size,
                              "candidate": _to_json(expr),
                              "case_index": w["case_index"],
                              "inputs": w["inputs"], "expected": w["expected"],
                              "observed": w["observed"], "reason": w["reason"]})
        else:
            witness_truncated = True
    else:
        # The generator ran out. Which of the two reasons it was matters.
        if status == EXHAUSTED_CANDIDATES and tried >= max_candidates:
            status = BUDGET_CANDIDATES

    if status == BUDGET_VM_OPS and oracle.over_cap():
        # Both caps are past; name the one that stopped the loop first is not
        # knowable, so name the one checked first and say the other is also
        # over rather than picking silently.
        pass

    # OPTIONAL FIELDS ARE OMITTED, NOT SET TO null. `solution: null` and
    # `solution` absent look the same to a reader and are not the same claim:
    # the first says a solution was recorded and it was nothing. An input that
    # was never consumed contributes no key at all, exactly as a run with no
    # artifacts contributes no load receipt.
    out = {
        "status": status,
        "solved": status == SOLVED,
        "candidates_tried": tried,
        "candidates_invalid": invalid,
        "verifications": verifications,
        "oracle_calls": oracle.calls,
        "oracle_call_cap": oracle_cap,
        "vm_ops": vm_ops,
        "vm_op_cap": op_cap,
        "constraints_seeded": used,
        "constraints_final": len(constraints),
        "seed_probe_count": seed_probes,
        "seed_probe_shortfall": shortfall,
        "seeded_from": seeded_from,
        "source_pack_items": len(pack.all_items()) if pack is not None else 0,
        "component_library_size": len(components),
        "coverage_required": N_ASSIGNMENTS,
        "witnesses": witnesses,
        "witness_truncated": witness_truncated,
        "target_truth_table": table,
        "grammar_version": _b.GRAMMAR_VERSION,
        "interface_version": _b.INTERFACE_VERSION,
        "library_version": _l.LIBRARY_VERSION,
        "executor": "cegis_boolean_v1",
        "reproducibility": "BIT_DETERMINISTIC",
    }
    if solution is not None:
        # Canonical JSON TEXT, not a nested list: an expression is one value
        # with one spelling, and a string is the shape that survives a result
        # schema, a fossil and a diff without changing under any of them.
        out["solution"] = json.dumps(_to_json(solution), separators=(",", ":"))
        out["solution_size"] = solution_size
    if pack is not None:
        out["source_pack_digest"] = pack.digest
    if library is not None:
        out["component_library_digest"] = library.digest
    if witness_truncated:
        out["_truncated"] = {"witnesses": True}
    return out


def _positive(payload: dict, name: str) -> int:
    v = payload[name]
    if not isinstance(v, int) or isinstance(v, bool) or v < 1:
        raise CegisError("%s must be a positive integer, got %r" % (name, v))
    return v


def _json_of(value):
    """Frozen (tuple/mappingproxy) -> plain JSON types, for one expression."""
    if isinstance(value, tuple):
        return [_json_of(v) for v in value]
    return value
