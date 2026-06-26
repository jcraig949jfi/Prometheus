"""mutation_dryrun.py — LLM mutation-interface dry run (pre-Phase-1 gate 2).

Per the 2026-05-29 review: before Phase 1, confirm the LLM mutation
operator can reliably PROPOSE valid typed operator-step mutations using a
strict JSON/DSL interface (not free-form Python). The reviewer's bar:
>= 80% type-valid suggestions on 100 dry-run mutations.

Per Doctrine #2, we measure four metrics SEPARATELY (not one pass rate):
  - parse-valid:    response contains a parseable JSON object
  - type-valid:     op exists, position valid, reads/writes match the op's
                    declared signature
  - audit-valid:    inserting the step keeps the pipeline protocol-clean
                    (no recompute-bypass / undeclared reads introduced)
  - survives-eval:  the mutated pipeline compiles + runs on a canary task
                    without crashing

The four are reported as a gradient, with the failure signature of each
rejected mutation.

Usage:
    python mutation_dryrun.py [n=100]
"""
import sys
import json
import re
import time
import urllib.request
import urllib.error
import random
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src"))

from blackboard import BlackboardState, run_pipeline
from blackboard_ops import (parse_names_and_relations, parse_question_target, parse_numbers,
                            op_transitive_closure, op_numeric_argmax, score_by_max_entity, score_by_max_value)
from blackboard_ops_v2 import (parse_ordinal, op_build_ordering, select_nth, parse_box_items,
                               op_aggregate_quantities, score_by_aggregate, entity_counter,
                               evidence_updater, distribution_reducer)
from blackboard_ops_r2 import (parse_rules, forward_chain, relations_from_facts,
                               score_by_derivability)
from blackboard_ops_compare import (parse_comparison, parse_which_extreme,
                                    score_by_comparison, score_by_extreme_number)

RNG = random.Random(20260529)
URL = "http://localhost:8800"

# Operator catalog (name -> op object) for type-validation
CATALOG = {
    op.name: op for op in [
        parse_numbers, parse_names_and_relations, parse_question_target, parse_ordinal,
        parse_box_items, op_build_ordering, op_transitive_closure, op_numeric_argmax,
        op_aggregate_quantities, entity_counter, evidence_updater, distribution_reducer,
        parse_rules, forward_chain, relations_from_facts,
        select_nth, score_by_max_entity, score_by_max_value, score_by_aggregate,
        score_by_derivability,
        parse_comparison, parse_which_extreme, score_by_comparison, score_by_extreme_number,
    ]
}

ALL_SLOTS = ["problem_text", "candidates", "numbers", "names", "relations", "quantities",
             "question_target", "transitive_closure", "ordered", "counts", "evidence",
             "hypotheses", "probabilities", "confidence", "max_entity", "max_value",
             "rules", "facts", "derived_facts",
             "comparison", "extreme_number",
             "candidate_scores", "selected_answer"]


def _catalog_table() -> str:
    lines = []
    for name, op in CATALOG.items():
        lines.append(f"  {name}: reads={op.reads} writes={op.writes}")
    return "\n".join(lines)


# A few seed pipelines to mutate (varied contexts)
SEED_PIPELINES = [
    ["parse_names_and_relations"],
    ["parse_names_and_relations", "parse_ordinal"],
    ["parse_box_items"],
    ["parse_names_and_relations", "op_build_ordering"],
    ["parse_numbers", "parse_question_target"],
]


def _cat(name):
    """Resolve a pipeline op to its catalog entry. Guarded scorer variants ('*__g',
    added for dispatch 2026-06-24) share their base op's reads/writes signature, so
    fall back to the base name; unknown ops resolve to None (rendered as '?')."""
    return CATALOG.get(name) or CATALOG.get(name.replace("__g", ""))


def build_prompt(current_pipeline: list[str]) -> str:
    def _sig(name):
        op = _cat(name)
        return (op.reads, op.writes) if op is not None else ("?", "?")
    pipe_table = "\n".join(
        f"  step {i}: {name}  (reads={_sig(name)[0]}, writes={_sig(name)[1]})"
        for i, name in enumerate(current_pipeline)
    ) or "  (empty pipeline)"
    return f"""You are proposing ONE mutation to a reasoning pipeline. A pipeline is an
ordered list of typed operators. Each operator reads named state slots and
writes named state slots. You insert one operator.

CURRENT PIPELINE:
{pipe_table}

AVAILABLE SLOTS (state fields you can read/write):
{', '.join(ALL_SLOTS)}

AVAILABLE OPERATORS (you may only insert one of these, with its exact signature):
{_catalog_table()}

RULES:
- Choose an operator whose declared reads are slots that an earlier step writes
  (or are input slots problem_text/candidates).
- The "reads" and "writes" you specify MUST match the operator's declared
  signature exactly.
- "position" is the index to insert at (0 = front, {len(current_pipeline)} = end).

Return EXACTLY ONE JSON object, no other text, in this schema:
{{"mutation": "insert_step", "position": <int>, "step": {{"kind": "Atomic", "op": "<operator_name>", "reads": [...], "writes": [...]}}, "rationale": "<one sentence>"}}

THREE VALID EXAMPLES:
{{"mutation": "insert_step", "position": 1, "step": {{"kind": "Atomic", "op": "op_build_ordering", "reads": ["relations"], "writes": ["ordered"]}}, "rationale": "ordering is needed to select nth"}}
{{"mutation": "insert_step", "position": 2, "step": {{"kind": "Atomic", "op": "op_aggregate_quantities", "reads": ["counts"], "writes": ["max_value"]}}, "rationale": "sum the per-category counts"}}
{{"mutation": "insert_step", "position": 1, "step": {{"kind": "Atomic", "op": "entity_counter", "reads": ["names", "relations", "quantities"], "writes": ["counts", "evidence"]}}, "rationale": "count parsed entities"}}

ONE INVALID EXAMPLE (do not do this):
{{"mutation": "insert_step", "position": 0, "step": {{"kind": "Atomic", "op": "made_up_op", "reads": ["foo"], "writes": ["bar"]}}, "rationale": "invalid: made_up_op is not in the catalog and foo/bar are not real slots"}}

Return exactly one JSON object now:"""


def extract_json(text: str):
    """Find the first balanced JSON object in the text."""
    # Try fenced first
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    candidate = m.group(1) if m else None
    if candidate is None:
        # Find first {...} with brace matching
        start = text.find('{')
        if start < 0:
            return None
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    break
    if candidate is None:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def validate(obj, current_pipeline):
    """Return (parse_ok, type_ok, type_signature) for a parsed mutation object."""
    if obj is None:
        return False, False, "parse-fail"
    if not isinstance(obj, dict):
        return True, False, "not-a-dict"
    if obj.get("mutation") != "insert_step":
        return True, False, f"unknown-mutation:{obj.get('mutation')}"
    step = obj.get("step", {})
    if not isinstance(step, dict):
        return True, False, "step-not-dict"
    op_name = step.get("op")
    if op_name not in CATALOG:
        return True, False, f"unknown-op:{op_name}"
    op = CATALOG[op_name]
    # position validity
    pos = obj.get("position")
    if not isinstance(pos, int) or pos < 0 or pos > len(current_pipeline):
        return True, False, f"bad-position:{pos}"
    # reads/writes must match declared signature (as sets)
    declared_reads = set(op.reads)
    declared_writes = set(op.writes)
    proposed_reads = set(step.get("reads", []))
    proposed_writes = set(step.get("writes", []))
    if proposed_reads != declared_reads:
        return True, False, f"reads-mismatch:{op_name}"
    if proposed_writes != declared_writes:
        return True, False, f"writes-mismatch:{op_name}"
    return True, True, "type-valid"


def audit_and_eval(obj, current_pipeline):
    """For a type-valid mutation, check audit-validity + survives-eval."""
    from blackboard import audit_pipeline
    step = obj["step"]
    op = CATALOG[step["op"]]
    pos = obj["position"]
    new_pipeline_names = current_pipeline[:pos] + [step["op"]] + current_pipeline[pos:]
    new_pipeline = [_cat(n) for n in new_pipeline_names]  # _cat: guarded-scorer tolerant
    # audit: no NEW recompute-bypass introduced by the inserted op
    sigs = audit_pipeline(new_pipeline)
    inserted_recompute = any(w["op"] == op.name for w in sigs["recompute_bypass"])
    audit_ok = not inserted_recompute
    # survives-eval: run on a trivial task without crashing
    survives = True
    try:
        s = BlackboardState(problem_text="Alice is taller than Bob. Who is tallest?",
                            candidates=["Alice", "Bob"])
        run_pipeline(new_pipeline, s)
    except Exception:
        survives = False
    return audit_ok, survives


def call_granite(prompt, max_tokens=300, temperature=0.3, timeout=60):
    body = json.dumps({"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}).encode()
    req = urllib.request.Request(f"{URL}/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read()).get("text", "")
    except Exception as e:
        return f"__ERROR__:{e}"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"LLM mutation dry-run: {n} mutations against Granite at {URL}")
    print(f"Reviewer threshold: >=80% type-valid")
    print()

    parse_ok = type_ok = audit_ok = survives_ok = 0
    type_fail_signatures = Counter()
    t0 = time.time()

    for i in range(n):
        seed = RNG.choice(SEED_PIPELINES)
        prompt = build_prompt(seed)
        text = call_granite(prompt)
        if text.startswith("__ERROR__"):
            type_fail_signatures["server-error"] += 1
            continue
        obj = extract_json(text)
        p_ok, t_ok, sig = validate(obj, seed)
        if p_ok:
            parse_ok += 1
        if t_ok:
            type_ok += 1
            a_ok, s_ok = audit_and_eval(obj, seed)
            if a_ok:
                audit_ok += 1
            if s_ok:
                survives_ok += 1
        else:
            type_fail_signatures[sig] += 1
        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{n}] parse={parse_ok} type={type_ok} audit={audit_ok} survives={survives_ok} "
                  f"({time.time()-t0:.0f}s)")

    print()
    print("=" * 70)
    print("DRY-RUN READING (Doctrine #2 — four metrics separately + signatures)")
    print("=" * 70)
    print(f"  parse-valid:    {parse_ok}/{n}  ({parse_ok/n:.1%})")
    print(f"  type-valid:     {type_ok}/{n}  ({type_ok/n:.1%})   <- reviewer's >=80% gate")
    print(f"  audit-valid:    {audit_ok}/{n}  ({audit_ok/n:.1%})")
    print(f"  survives-eval:  {survives_ok}/{n}  ({survives_ok/n:.1%})")
    print()
    print("Type-fail signatures (the gradient of WHY mutations were rejected):")
    for sig, count in type_fail_signatures.most_common():
        print(f"    {count:3d}  {sig}")
    print()
    rate = type_ok / n
    if rate >= 0.80:
        print(f"GATE PASSED: type-valid {rate:.1%} >= 80%. The JSON-DSL mutation interface")
        print(f"             is viable for Phase 1. Granite can reliably propose valid")
        print(f"             typed operator-steps.")
    elif rate >= 0.50:
        print(f"GATE MARGINAL: type-valid {rate:.1%}. Interface works but needs tuning.")
        print(f"               Look at the top type-fail signatures above — each is a")
        print(f"               specific prompt or schema fix.")
    else:
        print(f"GATE FAILED: type-valid {rate:.1%} < 50%. The interface is not yet viable.")
        print(f"             The top type-fail signature tells you the dominant failure mode.")
        print(f"             Fix it before Phase 1 — don't run evolution on a broken mutation")
        print(f"             interface.")


if __name__ == "__main__":
    main()
