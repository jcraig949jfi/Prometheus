"""Triage: Serendipity/Apollo failures -> Mint Packets. First implementation (charter §25).

Sources read (all committed, all cited in PROVENANCE):
  apollo/data/clean_canary_v01.json                      Apollo's canary (50 tasks, 4 unsolved cats)
  apollo/cycles/campaign_20260825/E9_RESULT.json         Charon's blind battery result (0.0667)
  aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md taxonomy of the four unsolved categories
  aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md   forge library == Apollo v1 catalog (25=25)
  aporia/iq/FINDINGS_IQ_PORT_1_2026-08-25.md             all_but_n PORTED, dE=5/120, frozen

Output: four packets. Three are routed/closed on existing evidence (consume before duplicate);
one -- vacuous_truth -- is EXPRESSIVITY-SUSPECTED and enters APPRENTICE-TESTING with every
packet field populated from executed evidence (wall module), not prose.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hephaestus.src import packet as P  # noqa: E402
from hephaestus.src import wall_vacuous_truth as W  # noqa: E402

FP = ROOT / "agents" / "hephaestus" / "src" / "forge_primitives.py"
REG = ROOT / "apollo" / "src" / "blackboard_evolve.py"


def _e9_per_category() -> dict:
    try:
        d = json.loads((ROOT / "apollo/cycles/campaign_20260825/E9_RESULT.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    for k in ("per_category", "by_category", "categories"):
        if isinstance(d, dict) and k in d:
            return d[k]
    return {k: v for k, v in d.items() if isinstance(v, dict) and "vacuous_truth" in k} if isinstance(d, dict) else {}


def make_vacuous_truth() -> dict:
    ex = W.build_examples()
    train, hold = W.split(ex)
    pos = [e for e in ex if e["gold"] == "yes"]
    neg = [e for e in ex if e["gold"] == "no"]
    bnd = [e for e in ex if e["gold"] == "und"]
    cf = W.counterfeit_battery(ex)
    closure = W.closure_evidence(ex)
    p = P.new_packet("MINT-0001")
    p.update({
        "SOURCE_WORLD": "Apollo typed-blackboard canary (apollo/data/clean_canary_v01.json, category vacuous_truth) "
                        "and Charon's blind E9 battery (roles/Charon/apollo_e9/charon_battery_E9.json, 6 items).",
        "SOURCE_AGENT": "Apollo (E9 abstained 40/42; vacuous_truth 0/6). Diagnosis by Aporia 155-S/156-S.",
        "FAILURE_FAMILY": "vacuous_truth — truth value of a quantified claim (universal / negative-universal / "
                          "conditional / existential) over a domain the premises state is EMPTY, versus the same "
                          "claim over a non-empty domain with or without a counterexample.",
        "WHAT_FAILED": "Apollo emits selected_answer=None on every vacuous_truth task: no registered transformer "
                       "produces a truth value for a quantified claim; parse_comparison is gated on 'Is X larger than Y'.",
        "WHAT_SHOULD_HAVE_HAPPENED": "state.comparison = True for a universal/negative-universal/conditional claim whose "
                                     "domain is stated empty (vacuous truth); False for an existential over an empty "
                                     "domain or a universal with a stated counterexample; None (abstain) when the "
                                     "premises give no information. The frozen tail score_by_comparison__g then selects.",
        "MINIMAL_REPRODUCER": "PYTHONPATH=. python -m hephaestus.src.wall_vacuous_truth  (builds the 88-example dev "
                              "set; prints the counterfeit battery). Candidate execution: python -m "
                              "hephaestus.src.run_candidate vacuous_truth <candidate.py> <out.json>.",
        "POSITIVE_EXAMPLES": [{"id": e["id"], "kind": e["kind"], "prompt": e["prompt"], "correct": e["correct"]} for e in pos],
        "NEGATIVE_EXAMPLES": [{"id": e["id"], "kind": e["kind"], "prompt": e["prompt"], "correct": e["correct"]} for e in neg],
        "BOUNDARY_EXAMPLES": [{"id": e["id"], "kind": e["kind"], "prompt": e["prompt"], "correct": "abstain (cannot be determined)"} for e in bnd],
        "CURRENT_PRIMITIVES": sorted(closure.get("forge_primitives", {}).keys()) + ["apollo REGISTRY: 27 ops (15 transformers, 10 scorers, 2 quarantine)"],
        "PRIMITIVE_SET_HASH": {"forge_primitives.py": P.sha256_file(FP) if FP.exists() else None,
                               "apollo/src/blackboard_evolve.py": P.sha256_file(REG) if REG.exists() else None,
                               "IQ-PORT-1 frozen evaluator (aporia/iq)": "10fa10db9989eb3a79c2039d18b748a83e93f751578ec6d0a0e12717eb0fa5ae"},
        "WHY_COMPOSITION_APPEARS_INSUFFICIENT": closure.get("reading", "") + " " + closure.get("forge_primitives_reading", ""),
        "CLOSURE_EVIDENCE": [closure],
        "SEARCH_ALREADY_ATTEMPTED": [
            "Apollo O1 exhaustive enumeration over 1.74M type-correct pipelines: vacuous_truth 0/5 (ceiling 0.833; number later retracted by E9, but the abstention on this category is structural).",
            "Aporia SELECTOR pre-flight over the frozen 27-candidate pool: zero capability-related dE movers.",
            "Apollo E9 blind battery: 0/6, all abstained.",
        ],
        "COUNTERFEIT_TESTS": cf,
        "KNOWN_SHORTCUTS": [
            {"name": "constant_yes", "why_it_works_on_the_canary": "Apollo's canary has 5/5 'Yes'; scores 5/5 there. On the dev set: see COUNTERFEIT_TESTS."},
            {"name": "kw_no_and_every_to_yes", "why": "the obvious regex; fails NEARMISS_NO_KEYWORD and NONEMPTY_UNIV_ALL kinds."},
            {"name": "kw_vacuous_to_yes", "why": "the forge_v4 pathology: 98/375 files answer by matching the word 'vacuous' (counterfeit museum #001)."},
        ],
        "FORBIDDEN_SHORTCUTS": [
            "Any read of state.candidates to decide the truth value (the answer must come from problem_text).",
            "Matching the word 'vacuous' or the category name.",
            "Committing a truth value when the premises carry no information about the predicate (boundary kind must abstain).",
            "Hard-coding the three sentences of Apollo's canary generator.",
        ],
        "REPRESENTATION_PERTURBATIONS": [
            "emptiness stated as: 'there are no X', 'contains no X', 'not a single X', 'number of X is zero', 'exactly zero X'",
            "claim forms: every/all/each/any X is P; no X is P; if an X is Q then P; whenever; some/there is/at least one X is P",
            "claim stated before vs after the emptiness fact",
            "distractor 'no' on a different noun phrase than the claim's domain (NEARMISS_NO_KEYWORD)",
            "candidate order shuffled; candidate wording varied (yes / yes, it is true / yes, the claim holds)",
        ],
        "DESIRED_TYPED_INTERFACE": {
            "signature": "op_vacuous_truth(state: BlackboardState) -> BlackboardState",
            "reads": ["problem_text"], "writes": ["comparison"],
            "semantics": "comparison=True claim true; False claim false; None abstain. Do not touch candidates.",
            "tail": "apollo/src/blackboard_ops_compare.py score_by_comparison__g (frozen; selects candidate starting 'yes'/'no')",
            "allowed_imports": ["re", "math", "itertools", "collections", "functools", "string", "forge_primitives", "blackboard"],
            "delta_class": "dE_synth (no implementation exists anywhere accessible; a retrieval would be dE_port and is not available)",
        },
        "RESOURCE_CONSTRAINTS": "Pure Python, CPU, deterministic, < 1 s per task, no network, no model calls at inference time.",
        "INDEPENDENT_EVALUATOR": {
            "status": "MISSING — this is the gate on any deep mint being READ, not on it being ATTEMPTED.",
            "required": "Aporia's frozen G-heldout generator for vacuous_truth (TRANSFER-1 prerequisite per roles/Aporia/resume_aporia.md PART 2.5) and a post-E9 Apollo evaluator of record.",
            "available_now_but_reserved": "Charon's E9 battery (6 items) — independent, blind, NOT to be used for development; results on it are reported only by Charon/Aporia.",
            "independence_chain": "supplier (Hephaestus) != prereg author (Aporia/Charon) != prompt author != grader (frozen evaluator) != adjudicator (Charon).",
        },
        "SUCCESS_CRITERION": "Candidate passes dev (holdout accuracy_decidable >= 0.95, boundary_false_commit_rate == 0, all four input-mutant falsifiers pass), AND, under an independently authored prereg, moves the ceiling on the held-out generator with the op load-bearing under knockout and absent from the v1 catalog, forge library and every prior Apollo registry (mechanically checked).",
        "KILL_CRITERION": "Three consecutive deep mints that pass dev but do not move the independent held-out => coupling dead; route to compression under Lexis/Ergon. OR a reclassification by the Master Smith (existing primitive overlooked / composition / representation / evaluator defect).",
        "PROVENANCE": [
            {"ts": P.now_iso(), "by": "hephaestus.src.triage", "note": "packet created from executed wall module; dev examples Hephaestus-authored; no Charon E9 item read by any code in hephaestus/"},
            {"ref": "aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md:49-53"},
            {"ref": "aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md:72-75"},
            {"ref": "apollo/scripts/gen_clean_canary_v01.py:191-208 (degenerate generator)"},
            {"ref": "aporia/iq/probe_synth1_target_degeneracy.py"},
            {"ref": "apollo/cycles/campaign_20260825/E9_FINDINGS.md"},
        ],
        "_dev_split": {"train_ids": [e["id"] for e in train], "holdout_ids": [e["id"] for e in hold], "n_examples": len(ex)},
    })
    return p


def make_routed() -> list[dict]:
    out = []
    p = P.new_packet("MINT-0002", SOURCE_WORLD="Apollo canary, category all_but_n", SOURCE_AGENT="Apollo / Aporia",
                     FAILURE_FAMILY="all_but_n (arithmetic difference)")
    p["WHAT_FAILED"] = "Apollo v2 registry had no subtraction; forge_primitives.all_but_n existed since v1."
    p["SEARCH_ALREADY_ATTEMPTED"] = ["Aporia IQ-PORT-1 (2026-08-25): ported; dE_port = +5/120 exactly; pipeline frozen."]
    p["PROVENANCE"] = [{"ref": "aporia/iq/FINDINGS_IQ_PORT_1_2026-08-25.md"}]
    p["STATUS"] = "SCRAPPED"; p["PRIORITY"]["rationale"] = "Closed: retrieval, not synthesis. Consume before duplicate."
    out.append(p)
    p = P.new_packet("MINT-0003", SOURCE_WORLD="Apollo canary, category temporal_ordering", SOURCE_AGENT="Apollo / Aporia",
                     FAILURE_FAMILY="temporal_ordering (PARSER gap)")
    p["WHAT_FAILED"] = "Ordering machinery exists and works (op_build_ordering, forge temporal_order); the temporal predicate is unrecognised by any parser."
    p["PROVENANCE"] = [{"ref": "aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md:72-75"}]
    p["STATUS"] = "DORMANT"; p["PRIORITY"]["rationale"] = "Routed to Apollo: a parser, not a primitive. Doubly contaminated as a mint demonstration (156-S). Positive control only."
    out.append(p)
    p = P.new_packet("MINT-0004", SOURCE_WORLD="Apollo canary, category consistency_check", SOURCE_AGENT="Apollo / Aporia",
                     FAILURE_FAMILY="consistency_check (PARSER gap + missing consistency predicate over an existing structure)")
    p["WHAT_FAILED"] = "check_transitivity / solve_constraints exist; no parser feeds them a cycle-detection question; no predicate 'is this relation set consistent' is exposed as an op."
    p["PROVENANCE"] = [{"ref": "aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md:72-75"}, {"ref": "aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md"}]
    p["STATUS"] = "COMPOSITION-SUSPECTED"; p["PRIORITY"]["rationale"] = "Likely Level 0/1 (composition of existing primitives + a parser). Not a Level-2 candidate until closure evidence says otherwise. Held until MINT-0001 completes one cycle (charter §25)."
    out.append(p)
    return out


def main() -> None:
    P.QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    existing = {p["MINT_ID"] for p in P.iter_packets()}
    if "MINT-0001" not in existing:
        p = make_vacuous_truth()
        P.save(p)
        P.log_event("MINT-0001", "created", by="triage")
        P.set_status(p, "EXPRESSIVITY-SUSPECTED", "no forge primitive; no registry producer of `comparison` for quantified claims; closure evidence attached")
        P.set_status(p, "APPRENTICE-TESTING", "dev set + counterfeit battery + interface ready; cheap models may attempt")
        P.save(p)
        print("MINT-0001 created ->", p["STATUS"])
    for p in make_routed():
        if p["MINT_ID"] not in existing:
            P.save(p)
            P.log_event(p["MINT_ID"], "created", by="triage", status=p["STATUS"])
            print(p["MINT_ID"], "created ->", p["STATUS"])
    print("queue:", [(q["MINT_ID"], q["STATUS"]) for q in P.iter_packets()])


if __name__ == "__main__":
    main()
