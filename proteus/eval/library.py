"""WP-B1 -- the foundry VM's evaluation exposed as a PURE LIBRARY.

    evaluate(program, spec, step_budget, seed) -> EvalResult

PURITY, which is the point of the package. This module reads no registry, reads no fossils,
opens no file, writes no file, and makes no network call. Everything it needs arrives as an
argument. `proteus/tests/test_wp_b1.py` asserts that mechanically over this module's own source,
so the property is enforced rather than promised.

D-9: the semantic owner ships the library and the wrapper stays blind. Vivarium wraps this as
`program_eval_v0` without needing to know what an opcode means.

----------------------------------------------------------------------------------------------
THE DECLARED ORDERING, without which "the FIRST failing input" is meaningless
----------------------------------------------------------------------------------------------
A specification is an ORDERED list of cases. The witness is the case of LOWEST INDEX whose
observed output differs from its expected output. If a caller has only an unordered set, the
library REFUSES rather than imposing an arbitrary order, because a silently-chosen order makes
the witness a property of this module's iteration and not of the program.

----------------------------------------------------------------------------------------------
BUDGET EXHAUSTION -- THE DECISION THIS PACKAGE WAS ASKED TO MAKE
----------------------------------------------------------------------------------------------
Budget exhaustion is a DISTINCT STATUS and, by default, NOT a counterexample.

"The program did not finish" is not "the program produced a wrong answer". If exhaustion counted
as a counterexample by default, then lowering the budget would MANUFACTURE witnesses, and the
witness is precisely the quantity Branch B exists to price. A cheap knob would silently move the
measured thing.

The default is therefore `BudgetPolicy.STATUS_ONLY`: an exhausted case yields status BUDGET and
is NOT eligible to be the witness. A caller whose specification genuinely says "answer within
this budget" may pass `BudgetPolicy.COUNTEREXAMPLE`, which makes exhaustion eligible. The policy
is recorded in the result, so no reader has to infer which convention produced a witness.

Both policies scan cases in the SAME declared order, so switching policy can only ever move the
witness EARLIER (to an exhausted case that STATUS_ONLY skipped), never to a different late case.

----------------------------------------------------------------------------------------------
TRACE
----------------------------------------------------------------------------------------------
The trace is bounded and PASSIVE. Execution never consults it, so truncation cannot change
outputs, status, steps or the witness -- asserted by a test that runs every case at trace limit 0
and at an unbounded limit and compares everything except the trace itself. Truncation is always
explicit: `trace_truncated` and `trace_events_dropped` are present whether or not it occurred.

----------------------------------------------------------------------------------------------
WHAT THIS MODULE DOES NOT CLAIM
----------------------------------------------------------------------------------------------
Nothing here calls a program correct, interesting, an agent, or a solution. `passed` means the
observed outputs equalled the declared expected outputs on the declared cases, and nothing more.
A program that fails every case is a normal result, not a defect.
"""
from __future__ import annotations

from proteus.foundry.identity import canonical_json, sha256_hex
from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import ManifestError, Meter, Player, validate_manifest

LIBRARY_VERSION = "proteus.program_eval.v0"
SPEC_SCHEMA = "proteus.evaluation_spec.v0"

#: Per-case execution outcomes. HALT/YIELD/BUDGET come from the VM; the rest are library-level.
STATUS_HALT = "halt"
STATUS_YIELD = "yield"
STATUS_BUDGET = "budget"
STATUS_NO_OUTPUT = "no_output"          # ran, produced no value on a case that expected one


class BudgetPolicy:
    STATUS_ONLY = "budget_status_only"          # default: exhaustion is NOT a counterexample
    COUNTEREXAMPLE = "budget_is_counterexample"  # opt in: exhaustion IS a counterexample
    ALL = (STATUS_ONLY, COUNTEREXAMPLE)


class EvaluationError(ValueError):
    """Any malformed input. The library fails closed; it never guesses."""


# --------------------------------------------------------------------------- specification

def make_spec(cases, n_out=1, ticks=6, label=None):
    """Build an ORDERED specification. `cases` is a list of {inputs, expected}.

    `inputs` is the ABI's list-of-channels. `expected` is the expected output channels, or None
    to declare "no expectation" (such a case can never be the witness).
    """
    if not isinstance(cases, list) or not cases:
        raise EvaluationError("a specification needs a non-empty ORDERED list of cases")
    out = []
    for i, c in enumerate(cases):
        if not isinstance(c, dict) or "inputs" not in c:
            raise EvaluationError(f"case {i} must be an object with an 'inputs' field")
        if not isinstance(c["inputs"], list):
            raise EvaluationError(f"case {i}: inputs must be a list of channels")
        for ch in c["inputs"]:
            if not isinstance(ch, list) or any(not isinstance(v, int) or isinstance(v, bool)
                                               or not 0 <= v < 2 ** 32 for v in ch):
                raise EvaluationError(f"case {i}: each channel must be a list of uint32")
        exp = c.get("expected")
        if exp is not None and not isinstance(exp, list):
            raise EvaluationError(f"case {i}: expected must be a list of channels or null")
        out.append({"index": i, "inputs": c["inputs"], "expected": exp})
    spec = {"schema_version": SPEC_SCHEMA, "ordering": "case index, ascending; ties impossible",
            "n_out": int(n_out), "ticks": int(ticks), "cases": out}
    if label is not None:
        spec["label"] = str(label)
    spec["spec_id"] = sha256_hex(canonical_json(
        {k: v for k, v in spec.items() if k != "label"}))
    return spec


def validate_spec(spec):
    if not isinstance(spec, dict) or spec.get("schema_version") != SPEC_SCHEMA:
        raise EvaluationError(f"specification must carry schema_version {SPEC_SCHEMA!r}")
    if not isinstance(spec.get("cases"), list) or not spec["cases"]:
        raise EvaluationError("specification has no cases")
    seen = [c["index"] for c in spec["cases"]]
    if seen != sorted(seen) or len(set(seen)) != len(seen):
        raise EvaluationError("case indices must be unique and ascending -- the ordering IS "
                              "the definition of 'first counterexample'")


# --------------------------------------------------------------------------- evaluation

def evaluate(program, spec, step_budget=None, seed=0, trace_limit=64,
             budget_policy=BudgetPolicy.STATUS_ONLY):
    """Evaluate `program` against the ORDERED `spec`. Pure: no IO of any kind.

    `program`      a player manifest (family "program")
    `step_budget`  max TICKS per case. None means the spec's own `ticks`. The manifest's
                   `tick_budget` caps OPS PER TICK and can be lowered by the VM but never raised.
    `trace_limit`  max recorded trace events per case; 0 records none. Passive either way.
    """
    if budget_policy not in BudgetPolicy.ALL:
        raise EvaluationError(f"unknown budget policy {budget_policy!r}")
    if not isinstance(program, dict):
        raise EvaluationError("program must be a player manifest object")
    try:
        validate_manifest(program)
    except ManifestError as e:
        raise EvaluationError(f"invalid program manifest: {e}") from e
    validate_spec(spec)
    ticks = int(spec["ticks"] if step_budget is None else step_budget)
    if ticks < 0:
        raise EvaluationError("step_budget must be >= 0")
    n_out = int(spec["n_out"])
    if n_out < 0:
        raise EvaluationError("n_out must be >= 0")

    cases, witness = [], None
    for case in spec["cases"]:
        rec = _run_case(program, case, n_out, ticks, seed, trace_limit)
        cases.append(rec)

    # ---- witness selection, strictly in declared order
    for rec in cases:
        if rec["expected"] is None:
            continue                       # no expectation -> cannot be a counterexample
        exhausted = rec["status"] == STATUS_BUDGET
        if exhausted and budget_policy == BudgetPolicy.STATUS_ONLY:
            continue                       # declared: exhaustion is a status, not a witness
        if not rec["passed"]:
            witness = {"case_index": rec["index"], "inputs": rec["inputs"],
                       "expected": rec["expected"], "observed": rec["outputs"],
                       "status": rec["status"],
                       "reason": ("budget_exhausted" if exhausted else "output_mismatch")}
            break

    n_eval = sum(1 for c in cases if c["expected"] is not None)
    n_pass = sum(1 for c in cases if c["expected"] is not None and c["passed"])
    return {
        "schema_version": "proteus.eval_result.v0",
        "library_version": LIBRARY_VERSION,
        "spec_id": spec.get("spec_id"),
        "seed": seed,
        "step_budget_ticks": ticks,
        "budget_policy": budget_policy,
        "budget_exhaustion_is_counterexample": budget_policy == BudgetPolicy.COUNTEREXAMPLE,
        "trace_limit": trace_limit,
        "cases": cases,
        "witness": witness,
        "has_witness": witness is not None,
        "cases_total": len(cases),
        "cases_with_expectation": n_eval,
        "cases_passed": n_pass,
        "all_passed": n_eval > 0 and n_pass == n_eval,
        "steps_total": sum(c["steps"] for c in cases),
        "ops_total": sum(c["ops"] for c in cases),
        "status_counts": _counts(c["status"] for c in cases),
        "note": ("'passed' means observed == expected on the declared cases. It is not a claim "
                 "that the program is correct, interesting, or an agent."),
    }


def _run_case(program, case, n_out, ticks, seed, trace_limit):
    """One case. Mirrors the arena's per-tick loop exactly, including break-on-halt."""
    p = Player(program)
    st = p.fresh_state()
    rng = SplitMix64(seed)
    m = Meter()
    outs_all, statuses, trace, dropped = [], [], [], 0
    for t in range(ticks):
        outs, status = p.run_tick(st, case["inputs"], n_out, rng, meter=m)
        outs_all.append([list(ch) for ch in outs])
        statuses.append(status)
        if len(trace) < trace_limit:
            trace.append({"tick": t, "status": status,
                          "out_lens": [len(ch) for ch in outs], "ops": m.ops})
        else:
            dropped += 1
        if status == STATUS_HALT:
            break

    flat = [v for tick in outs_all for ch in tick for v in ch]
    status = statuses[-1] if statuses else STATUS_BUDGET
    if status != STATUS_HALT and not flat and case["expected"] is not None:
        pass  # keep the VM's own status; NO_OUTPUT is reported separately below
    emitted = bool(flat)
    observed = outs_all[-1] if outs_all else []
    passed = None
    if case["expected"] is not None:
        passed = (observed == case["expected"])
    return {
        "index": case["index"], "inputs": case["inputs"], "expected": case["expected"],
        "outputs": observed, "outputs_all_ticks": outs_all,
        "statuses_all_ticks": statuses,
        "emitted_any_value": emitted,
        "status": status if statuses else STATUS_BUDGET,
        "no_output": not emitted,
        "steps": len(statuses), "ops": m.ops,
        "passed": bool(passed) if passed is not None else None,
        "trace": trace, "trace_truncated": dropped > 0, "trace_events_dropped": dropped,
    }


def _counts(it):
    d = {}
    for x in it:
        d[x] = d.get(x, 0) + 1
    return dict(sorted(d.items()))


# --------------------------------------------------------------------------- alias relabelling

def relabel_opcode_aliases(program, k):
    """Add k*N_OPCODES to the OPCODE SLOT of every instruction: instruction-identical, byte-distinct.

    `op = word mod N_OPCODES`, so adding a multiple of N_OPCODES to an opcode word is a semantic
    RELABELLING that must leave execution unchanged.

    ONLY SLOT 0 OF EACH INSTRUCTION IS TOUCHED, and that restriction is load-bearing. An earlier
    version of this function offset every word and silently corrupted the program: operand `a` is
    taken mod `n_regs`, so on a 4-register machine a `0` operand became `25 mod 4 == 1` -- a
    different register. Relabelling the whole genome is not a relabelling, it is an edit.

    Instructions are decoded at ip, ip+1, ip+2, ip+3 with ip advancing in steps of 4 from 0, so
    the opcode slots are exactly the word indices divisible by 4.

    CAVEAT THAT REMAINS TRUE: the genome is also copied into the tape, so a relabelled opcode word
    is a different DATUM. A program that reads its own code as data may still diverge, and that is
    a fact about the substrate, not a defect here. The caller compares and reports.
    """
    from proteus.foundry.affordances import N_OPCODES
    if not isinstance(k, int) or k < 0:
        raise EvaluationError("k must be a non-negative integer")
    g = []
    for i, w in enumerate(program["genome"]):
        if i % 4 == 0:
            v = w + k * N_OPCODES
            if v >= 2 ** 32:
                raise EvaluationError("relabelling would overflow uint32; choose a smaller k")
            g.append(v)
        else:
            g.append(w)
    out = dict(program)
    out["genome"] = g
    return out


# --------------------------------------------------------------------------- input sensitivity

def input_sensitivity(program, input_sets, n_out=1, ticks=6, seed=0):
    """Does this program's EXECUTION depend on its input at all? Pure; no IO.

    B1-b requires world-blindness to be REPORTED. This reports it and nothing more.

    A program is `world_blind` when its outputs and statuses are identical across every supplied
    input set. That is a statement about THIS channel and THESE inputs -- widening the channel is
    WP-B4 and may change the answer, which is exactly why the result carries `input_sets_tested`.

    WHAT THIS DOES NOT SAY. `world_blind = False` means execution varied with input. It does NOT
    make the program a responsive agent, an agent, or a solver. Harmonia measured that 75% of the
    64 specimens are world-blind under the current channel; the correct reading of the remaining
    25% is "execution is not invariant", not "these are agents".
    """
    if not isinstance(input_sets, list) or len(input_sets) < 2:
        raise EvaluationError("input sensitivity needs at least two input sets to compare")
    sigs = []
    for inputs in input_sets:
        spec = make_spec([{"inputs": inputs, "expected": None}], n_out=n_out, ticks=ticks)
        r = evaluate(program, spec, seed=seed, trace_limit=0)
        c = r["cases"][0]
        sigs.append(canonical_json({"outputs": c["outputs_all_ticks"], "status": c["status"],
                                    "steps": c["steps"], "ops": c["ops"]}))
    distinct = len(set(sigs))
    return {
        "world_blind": distinct == 1,
        "distinct_execution_signatures": distinct,
        "input_sets_tested": len(input_sets),
        "claim_boundary": ("world_blind=False means execution varied with input on THESE inputs "
                           "under THIS channel. It is not a claim that the program is an agent, "
                           "is responsive in any world, or solves anything."),
    }
