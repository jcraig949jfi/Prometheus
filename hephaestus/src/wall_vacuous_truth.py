"""Wall: vacuous_truth. Reproducer, development examples, counterfeit battery, input-mutant
falsifiers, and closure evidence for MINT-0001.

Why this wall: Aporia 156-S named vacuous_truth as the ONLY unsolved Apollo category with no
corresponding forge primitive (aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md:49-53).
Apollo's own canary for it is degenerate (apollo/scripts/gen_clean_canary_v01.py:191-208:
three sentences, correct answer always "Yes"), so a text-blind constant-Yes scorer scores 5/5
(aporia/iq/probe_synth1_target_degeneracy.py). The examples below are Hephaestus-authored
DEVELOPMENT material only. Charon's blind E9 battery (roles/Charon/apollo_e9/
charon_battery_E9.json, 6 vacuous_truth items) is the INDEPENDENT held-out and is never read
by anything in this module.

Interface a candidate must satisfy (DESIRED_TYPED_INTERFACE): a function
    op_vacuous_truth(state: BlackboardState) -> BlackboardState
that reads state.problem_text and writes state.comparison = True (claim true) / False (claim
false), or leaves it None to abstain. Apollo's existing frozen tail score_by_comparison__g then
selects the candidate beginning with "yes"/"no". The candidate never touches state.candidates.
"""
from __future__ import annotations

import dataclasses
import inspect
import random
import re
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "apollo" / "src", ROOT / "agents" / "hephaestus" / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from blackboard import BlackboardState  # noqa: E402

WALL_ID = "vacuous_truth"
SEED = 20260901

# ── example construction ─────────────────────────────────────────────────────────────────

DOMAINS = [
    # (container phrase, plural noun, singular noun, property P, property Q)
    ("the jar", "red marbles", "red marble", "chipped", "heavier than ten grams"),
    ("this shelf", "books with more than 500 pages", "book with more than 500 pages", "overdue", "signed"),
    ("the department", "employees who hold a pilot licence", "employee who holds a pilot licence", "on the weekend rota", "over forty"),
    ("the box", "items weighing more than two kilograms", "item weighing more than two kilograms", "fragile", "insured"),
    ("the room", "people taller than two metres", "person taller than two metres", "asleep", "wearing a hat"),
    ("the garage", "electric cars", "electric car", "blue", "registered abroad"),
    ("the orchard", "trees older than a century", "tree older than a century", "diseased", "fenced"),
    ("the archive", "letters written in Latin", "letter written in Latin", "damaged", "catalogued"),
]

EMPTY_FORMS = [
    "There are no {pl} in {c}.",
    "{C} contains no {pl}.",
    "Not a single {sg} is in {c}.",
    "The number of {pl} in {c} is zero.",
    "Nobody has ever found a {sg} in {c}, and there are none now.",
]

UNIV_CLAIMS = [
    "every {sg} in {c} is {P}",
    "all {pl} in {c} are {P}",
    "each {sg} in {c} is {P}",
    "any {sg} in {c} is {P}",
]
NEG_UNIV_CLAIMS = ["no {sg} in {c} is {P}", "none of the {pl} in {c} are {P}"]
COND_CLAIMS = ["if a {sg} in {c} is {Q}, then it is {P}", "whenever a {sg} in {c} is {Q}, it is {P}"]
EXIST_CLAIMS = ["some {sg} in {c} is {P}", "there is a {sg} in {c} that is {P}", "at least one {sg} in {c} is {P}"]

YES = ["yes, it is true", "yes", "yes, the claim holds"]
NO = ["no, it is false", "no", "no, the claim fails"]
UND = ["cannot be determined", "undetermined", "it cannot be determined from this"]
FILL = ["only if {c} is empty", "the claim is not well formed", "only sometimes", "depends on context"]


def _cap(s: str) -> str:
    return s[0].upper() + s[1:]


def _fill(t: str, d: tuple) -> str:
    c, pl, sg, P, Q = d
    return t.format(c=c, C=_cap(c), pl=pl, sg=sg, P=P, Q=Q)


def _mk(rng: random.Random, kind: str, prompt: str, gold: str, d: tuple, note: str = "") -> dict:
    correct_pool = {"yes": YES, "no": NO, "und": UND}[gold]
    correct = rng.choice(correct_pool)
    others = []
    for pool in (YES, NO, UND):
        if pool is not correct_pool:
            others.append(rng.choice(pool))
    others.append(_fill(rng.choice(FILL), d))
    cands = [correct] + others
    rng.shuffle(cands)
    return {"kind": kind, "prompt": prompt, "candidates": cands, "correct": correct, "gold": gold, "note": note}


def build_examples(seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    ex: list[dict] = []
    for i, d in enumerate(DOMAINS):
        c, pl, sg, P, Q = d
        emp = _fill(rng.choice(EMPTY_FORMS), d)
        # vacuous universal over empty domain -> yes
        ex.append(_mk(rng, "VAC_UNIV_EMPTY", f"{emp} Consider the claim: {_fill(rng.choice(UNIV_CLAIMS), d)}. Is the claim true?", "yes", d))
        # vacuous negative universal over empty domain -> yes
        ex.append(_mk(rng, "VAC_NEGUNIV_EMPTY", f"{emp} Consider the claim: {_fill(rng.choice(NEG_UNIV_CLAIMS), d)}. Is the claim true?", "yes", d))
        # conditional with false antecedent -> yes
        emp_q = _fill(rng.choice(EMPTY_FORMS), (c, f"{pl} that are {Q}", f"{sg} that is {Q}", P, Q)) if i % 2 == 0 else f"No {sg} in {c} is {Q}."
        ex.append(_mk(rng, "VAC_COND_EMPTY", f"{emp_q} Consider the claim: {_fill(rng.choice(COND_CLAIMS), d)}. Is the claim true?", "yes", d))
        # existential over empty domain -> no
        ex.append(_mk(rng, "EXIST_EMPTY", f"{emp} Consider the claim: {_fill(rng.choice(EXIST_CLAIMS), d)}. Is the claim true?", "no", d))
        # claim stated BEFORE the emptiness fact -> yes (order perturbation)
        ex.append(_mk(rng, "VAC_UNIV_EMPTY_ORDER", f"Consider the claim: {_fill(rng.choice(UNIV_CLAIMS), d)}. {emp} Is the claim true?", "yes", d))
        # non-empty, counterexample present -> no
        k = rng.randint(3, 7); j = rng.randint(1, k - 1)
        ex.append(_mk(rng, "NONEMPTY_UNIV_COUNTEREX", f"There are exactly {k} {pl} in {c}, and exactly {j} of them are {P}. Consider the claim: {_fill(rng.choice(UNIV_CLAIMS), d)}. Is the claim true?", "no", d))
        # non-empty, all satisfy -> yes
        ex.append(_mk(rng, "NONEMPTY_UNIV_ALL", f"There are exactly {k} {pl} in {c}, and all {k} of them are {P}. Consider the claim: {_fill(rng.choice(UNIV_CLAIMS), d)}. Is the claim true?", "yes", d))
        # non-empty existential with witnesses -> yes
        ex.append(_mk(rng, "NONEMPTY_EXIST_TRUE", f"There are exactly {k} {pl} in {c}, and {j} of them are {P}. Consider the claim: {_fill(rng.choice(EXIST_CLAIMS), d)}. Is the claim true?", "yes", d))
        # boundary: non-empty, no information about P -> cannot be determined (correct op abstains)
        ex.append(_mk(rng, "NONEMPTY_UNKNOWN", f"There are exactly {k} {pl} in {c}. Consider the claim: {_fill(rng.choice(UNIV_CLAIMS), d)}. Is the claim true?", "und", d))
        # near-miss: the word 'no' appears but the claim's domain is non-empty with a counterexample -> no
        ex.append(_mk(rng, "NEARMISS_NO_KEYWORD", f"There are no {Q} {pl} in {c}, but there are exactly {k} {pl} in {c} and only {j} of them are {P}. Consider the claim: {_fill(rng.choice(UNIV_CLAIMS), d)}. Is the claim true?", "no", d,
                      note="kills the 'no' -> yes shortcut"))
        # near-miss: the word 'vacuous' appears, domain non-empty, claim false -> no
        ex.append(_mk(rng, "NEARMISS_VACUOUS_WORD", f"The label 'vacuous' is printed on {c}. It holds exactly {k} {pl}, and {j} of them are {P}. Consider the claim: {_fill(rng.choice(UNIV_CLAIMS), d)}. Is the claim true?", "no", d,
                      note="kills the 'vacuous' keyword shortcut (forge_v4, 98 files)"))
    for n, e in enumerate(ex):
        e["id"] = f"vt-{n:03d}"
    return ex


def split(examples: list[dict], n_train: int = 8, seed: int = SEED) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed + 1)
    idx = list(range(len(examples)))
    rng.shuffle(idx)
    train = [examples[i] for i in idx[:n_train]]
    hold = [examples[i] for i in idx[n_train:]]
    return train, hold


# ── harness ───────────────────────────────────────────────────────────────────────────────

def _tail_select(state: BlackboardState) -> str:
    """Apollo's frozen yes/no tail, re-implemented byte-for-byte in behaviour so the harness does
    not import the evolve module. Source: apollo/src/blackboard_ops_compare.py:45-52."""
    if state.comparison is None:
        return ""
    want = "yes" if state.comparison else "no"
    for c in state.candidates:
        if c.strip().lower().startswith(want):
            return c
    return ""


def run_op(op: Callable[[BlackboardState], BlackboardState], ex: dict) -> dict:
    st = BlackboardState(problem_text=ex["prompt"], candidates=list(ex["candidates"]))
    err = None
    try:
        out = op(st)
        if isinstance(out, BlackboardState):
            st = out
        elif out is not None:
            # interface violation: the op returned a value instead of the state (seen: phi3 `return True`)
            err = f"InterfaceViolation: op returned {type(out).__name__!s} instead of BlackboardState"
    except Exception as e:  # noqa: BLE001 — candidate code is untrusted
        err = f"{type(e).__name__}: {str(e)[:200]}"
    sel = _tail_select(st) if err is None else ""
    committed = st.comparison is not None and err is None
    if ex["gold"] == "und":
        ok = not committed
    else:
        ok = committed and sel == ex["correct"]
    return {"id": ex["id"], "kind": ex["kind"], "gold": ex["gold"], "comparison": st.comparison,
            "selected": sel, "ok": ok, "error": err}


def metrics(records: list[dict]) -> dict:
    dec = [r for r in records if r["gold"] != "und"]
    und = [r for r in records if r["gold"] == "und"]
    n_dec = len(dec) or 1
    return {
        "n": len(records),
        "accuracy_decidable": round(sum(r["ok"] for r in dec) / n_dec, 4),
        "abstain_rate_decidable": round(sum(r["comparison"] is None and not r["error"] for r in dec) / n_dec, 4),
        "boundary_false_commit_rate": round(sum(not r["ok"] for r in und) / (len(und) or 1), 4),
        "errors": sum(1 for r in records if r["error"]),
        "by_kind": {k: round(sum(r["ok"] for r in records if r["kind"] == k) /
                             max(1, sum(1 for r in records if r["kind"] == k)), 3)
                    for k in sorted({r["kind"] for r in records})},
    }


def evaluate(op: Callable, examples: list[dict]) -> dict:
    recs = [run_op(op, e) for e in examples]
    return {"metrics": metrics(recs), "records": recs}


# ── counterfeit battery: scorers that ignore semantics (KNOWN_SHORTCUTS, measured) ───────

def _kw(pattern: str, val_if_match: bool, val_else: bool | None):
    rx = re.compile(pattern, re.I)
    def op(st: BlackboardState) -> BlackboardState:
        st.comparison = val_if_match if rx.search(st.problem_text) else val_else
        return st
    return op


def _const(v: bool):
    def op(st: BlackboardState) -> BlackboardState:
        st.comparison = v
        return st
    return op


COUNTERFEITS: dict[str, Callable] = {
    "constant_yes": _const(True),
    "constant_no": _const(False),
    "kw_no_to_yes": _kw(r"\b(no|none|zero|not a single|nobody)\b", True, False),
    "kw_every_to_yes": _kw(r"\b(every|all|each|any)\b", True, False),
    "kw_no_and_every_to_yes": (lambda st: (setattr(st, "comparison",
        bool(re.search(r"\b(no|none|zero|not a single)\b", st.problem_text, re.I)) and
        bool(re.search(r"\b(every|all|each|any|if|whenever|no [a-z]+ in)\b", st.problem_text, re.I))) or st)),
    "kw_vacuous_to_yes": _kw(r"vacuous", True, None),
    "kw_some_to_no": _kw(r"\b(some|there is|at least one)\b", False, True),
}


def counterfeit_battery(examples: list[dict]) -> list[dict]:
    out = []
    for name, op in COUNTERFEITS.items():
        m = metrics([run_op(op, e) for e in examples])
        out.append({"shortcut": name, "accuracy_decidable": m["accuracy_decidable"],
                    "boundary_false_commit_rate": m["boundary_false_commit_rate"]})
    return out


# ── input-mutant falsifiers for a candidate (semantic perturbations of the PROMPT) ───────

def input_mutants(op: Callable, examples: list[dict]) -> dict:
    """Four falsifiers a genuine mechanism passes and a keyword mechanism fails."""
    res = {"emptiness_removed_should_not_commit_yes": [0, 0],
           "every_to_some_should_flip_to_no": [0, 0],
           "candidate_order_invariance": [0, 0],
           "no_to_exactly_zero_same_answer": [0, 0]}
    rng = random.Random(SEED + 2)
    for e in examples:
        if e["kind"] == "VAC_UNIV_EMPTY":
            # M1: delete the emptiness sentence -> claim becomes undetermined
            sents = e["prompt"].split(". ")
            p1 = ". ".join(s for s in sents if not re.search(r"\b(no|none|zero|not a single|nobody)\b", s, re.I))
            r = run_op(op, {**e, "prompt": p1, "gold": "und"})
            res["emptiness_removed_should_not_commit_yes"][1] += 1
            res["emptiness_removed_should_not_commit_yes"][0] += int(r["comparison"] is not True)
            # M2: every -> some over the same empty domain -> answer must flip to no
            p2 = re.sub(r"\b(every|each|any)\b", "some", e["prompt"], count=1, flags=re.I)
            p2 = re.sub(r"\ball ([a-z ]+?) are\b", r"some \1 are", p2, count=1, flags=re.I)
            r = run_op(op, {**e, "prompt": p2, "gold": "no", "correct": next(c for c in e["candidates"] if c.lower().startswith("no"))})
            res["every_to_some_should_flip_to_no"][1] += 1
            res["every_to_some_should_flip_to_no"][0] += int(r["ok"])
            # M4: 'no X' -> 'exactly zero X' -> same answer (yes)
            p4 = re.sub(r"\bThere are no\b", "There are exactly zero", e["prompt"])
            p4 = re.sub(r"\bcontains no\b", "contains exactly zero", p4)
            r = run_op(op, {**e, "prompt": p4})
            res["no_to_exactly_zero_same_answer"][1] += 1
            res["no_to_exactly_zero_same_answer"][0] += int(r["ok"])
        if e["gold"] != "und":
            # M3: shuffle candidate order -> same semantic selection
            cands = list(e["candidates"]); rng.shuffle(cands)
            r = run_op(op, {**e, "candidates": cands})
            res["candidate_order_invariance"][1] += 1
            res["candidate_order_invariance"][0] += int(r["ok"])
    return {k: {"passed": v[0], "of": v[1]} for k, v in res.items()}


# ── closure evidence: can the frozen substrate express this at all? ──────────────────────

def closure_evidence(examples: list[dict]) -> dict:
    out: dict[str, Any] = {}
    # (a) run every registered Apollo transformer on every example; record slots written
    try:
        import blackboard_evolve as be  # noqa: E402
        written: dict[str, set[str]] = {}
        commit = 0
        for name, (fn, role) in be.REGISTRY.items():
            if role != "transformer":
                continue
            for e in examples:
                st = BlackboardState(problem_text=e["prompt"], candidates=list(e["candidates"]))
                before = {f.name: repr(getattr(st, f.name)) for f in dataclasses.fields(st)}
                try:
                    st2 = fn(st) or st
                except Exception:  # noqa: BLE001
                    continue
                after = {f.name: repr(getattr(st2, f.name)) for f in dataclasses.fields(st2)}
                for k in after:
                    if after[k] != before[k] and k not in ("history", "provenance", "trace",
                                                           "op_log", "write_log", "skipped_ops"):
                        written.setdefault(name, set()).add(k)
                if st2.comparison is not None:
                    commit += 1
        out["apollo_registry_transformers_run"] = sum(1 for _, (f, r) in be.REGISTRY.items() if r == "transformer")
        out["slots_written_by_registry_on_this_wall"] = {k: sorted(v) for k, v in written.items()}
        out["registry_ops_that_commit_comparison"] = commit
        out["reading"] = ("No registered transformer writes `comparison` on any vacuous_truth prompt; "
                          "the only producer of that slot (parse_comparison) is gated on 'Is X larger than Y'. "
                          "The reachable set G(C) contains no path from problem_text to a truth value for a "
                          "quantified claim over a possibly-empty domain.")
    except Exception as e:  # noqa: BLE001
        out["apollo_registry_error"] = f"{type(e).__name__}: {e}"
    # (b) forge primitive signature scan: does any primitive take a domain + predicate?
    try:
        import forge_primitives as fp  # noqa: E402
        sigs = {}
        for n, f in inspect.getmembers(fp, inspect.isfunction):
            if f.__module__ == fp.__name__ and not n.startswith("_"):
                sigs[n] = str(inspect.signature(f))
        out["forge_primitives"] = sigs
        out["forge_primitives_accepting_callable_predicate"] = [
            n for n, s in sigs.items() if "pred" in s or "callable" in s.lower() or "fn" in s]
        out["forge_primitives_reading"] = (
            "The only primitive touching predicates is solve_constraints(variables, domains, constraints), "
            "a finite-domain CSP over explicit variables: nothing parses a domain or a predicate from text, "
            "and a CSP with no variables does not encode 'every X is P' over an empty X-set as a truth value. "
            "No primitive computes a universally/existentially quantified truth value or models an empty "
            "domain; `negate` is surface-form only.")
    except Exception as e:  # noqa: BLE001
        out["forge_primitives_error"] = f"{type(e).__name__}: {e}"
    # (c) prior independent evidence
    out["prior_evidence"] = [
        "aporia/iq/FINDINGS_SELECTOR_PREFLIGHT_2026-08-25.md: frozen pool = 25 forge primitives + 2 port ops; "
        "18 expressible; zero candidates move dE for a capability-related reason; vacuous_truth untouched.",
        "aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md:72-75: vacuous_truth = GENUINE capability gap, "
        "'no vacuous-implication semantics'.",
        "apollo/cycles/campaign_20260825/E9_RESULT.json: Apollo scored 0/6 on Charon's blind vacuous_truth items "
        "(abstained).",
    ]
    return out


if __name__ == "__main__":
    import json
    ex = build_examples()
    tr, ho = split(ex)
    print(len(ex), "examples;", len(tr), "train /", len(ho), "holdout")
    print(json.dumps(counterfeit_battery(ex), indent=1))
