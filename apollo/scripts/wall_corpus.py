"""wall_corpus.py — Tier A ablation-wall corpus generator (Apollo's probe contract).

Builds the metabolization probe's Tier A substrate: >=20 ablation-induced walls across
4 failure classes, each run on the deterministic Branch C substrate to plateau, each
carrying a ground-truth F-oracle diagnosis (CAUSE, no fix) and a quarantined F-answer.

Contract: `stations/M1_STATUS.md` §7b · spec `pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md`
§2/§4.2 · prereg `pivot/PREREG_METABOLIZATION_PROBE_v1.md`.
Also discharges W0/W1 of `pivot/STRATEGY_2026-08-12_resumption_and_roadmap.md` §10 —
one corpus, two consumers.

HEREDITY RULE (no new architecture): this harness NEVER edits the substrate. Every
ablation is applied by rebinding module globals on an imported `blackboard_evolve` at
runtime, inside a throwaway subprocess. `blackboard_evolve.py`, `blackboard.py`, and the
`blackboard_ops_*` modules are untouched on disk.

POSITIVE CONTROL (addendum-A §5.3): the corpus ships `CTRL-*` runs with no ablation.
A wall-type detector that cannot separate CTRL from the ablated runs is broken, not
insightful — a corpus of walls alone can only fail in the flattering direction.

Usage:
    python wall_corpus.py --list
    python wall_corpus.py --wall EX-01            # one wall, in-process
    python wall_corpus.py --all                   # every wall, subprocess each
    python wall_corpus.py --all --gens 150
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
OUT = Path(__file__).resolve().parent.parent / "wall_corpus"
sys.path.insert(0, str(SRC))

# Base configuration = the current PRODUCTION config (the one that reaches max_acc
# 0.833 / routable 1.000). Every wall is an ablation *of this*, so the control and the
# walls differ in exactly one factor.
BASE_RUN = dict(mode="deterministic", dispatch=True, crossover_frac=0.3,
                pop_size=24, seed=20260815, log_every=10)


# ══════════════════════════════════════════════════════════════════════
# Patch helpers — all operate on the imported module object `be`
# ══════════════════════════════════════════════════════════════════════

def _rebuild_role_lists(be):
    """Recompute the derived registry views after REGISTRY membership changes."""
    be.TRANSFORMERS = [n for n, (_, r) in be.REGISTRY.items() if r == be.ROLE_TRANSFORMER]
    be.SCORERS = [n for n, (_, r) in be.REGISTRY.items() if r == be.ROLE_SCORER]
    be.GUARDED_SCORERS = [n for n in be.GUARDED_SCORERS if n in be.REGISTRY]
    be.PLAIN_SCORERS = [n for n in be.SCORERS if n not in be.GUARDED_SCORERS]


def remove_ops(be, names):
    """EXPRESSIVENESS ablation: the capability is absent from the substrate entirely —
    removed from the registry AND purged from seed pipelines, so no search path and no
    seed can reach it."""
    names = set(names)
    for n in names:
        be.REGISTRY.pop(n, None)
    _rebuild_role_lists(be)

    orig_seed = be.seed_population

    def seeded(*a, **kw):
        pop = orig_seed(*a, **kw)
        kept = []
        for org in pop:
            org.pipeline = [n for n in org.pipeline if n not in names]
            if any(be.role_of(n) == be.ROLE_SCORER for n in org.pipeline):
                kept.append(org)
        # keep population size stable with random typed pipelines
        while len(kept) < len(pop):
            import random
            k = random.randint(1, 3)
            body = [random.choice(be.TRANSFORMERS) for _ in range(k)]
            sc = random.choice(be.GUARDED_SCORERS if be.GUARDED_SCORERS else be.SCORERS)
            o = be.BlackboardOrganism(body + [sc], genome_id=be._new_id())
            o.lineage = ["seed:random"]
            kept.append(o)
        return kept

    be.seed_population = seeded


def restrict_moves(be, allowed_prefixes):
    """SEARCH-OPERATOR ablation: the capability stays in the registry, but the mutation
    operator that could reach it is withheld. Implemented by rejection-sampling the
    ORIGINAL mutator on its own lineage tag — the substrate's mutation logic is reused
    verbatim, never reimplemented."""
    orig = be.mutate_deterministic

    def wrapped(org):
        for _ in range(32):
            child = orig(org)
            if len(child.lineage) == len(org.lineage):
                return child                      # move was a legitimate no-op
            if any(child.lineage[-1].startswith(p) for p in allowed_prefixes):
                return child
        return org.clone()

    be.mutate_deterministic = wrapped


def rebind_guard(be, guard_name, base_name, precond):
    """INTERFACE ablation: rebuild a guarded scorer with a broken precondition. The
    operator, its parser, and the search path all remain intact."""
    base = be.REGISTRY[base_name][0]
    be.REGISTRY[guard_name] = (
        be.BlackboardOp(base.fn, reads=base.reads, writes=base.writes,
                        precondition=precond, on_fail="skip", name=guard_name),
        be.ROLE_SCORER)


def wrap_fitness(be, mutate_f):
    """MEASUREMENT ablation: the organism is unchanged; the meter that reads it is bent."""
    orig = be.fitness

    def wrapped(org, tasks, single_baseline):
        f = orig(org, tasks, single_baseline)
        if not f["valid"]:
            return f
        return mutate_f(be, org, tasks, single_baseline, f)

    be.fitness = wrapped


def _canary_slice(tasks):
    """Battery layout is canary(50) + synth(30) + inference(20) + cross_tier(20)."""
    return tasks[:50] if len(tasks) == 120 else tasks[:len(tasks) * 5 // 12]


# ══════════════════════════════════════════════════════════════════════
# The walls
# ══════════════════════════════════════════════════════════════════════
# oracle_diagnosis  = CAUSE only. Names the mechanism and the missing capability CLASS.
#                     Never names the operator to add or the edit to make.
# answer_content    = the fix. QUARANTINED — never merged into the oracle field.
# separability      = "clean" | "tight" (cause phrasing crowds the fix; Ergon rules)

WALLS = []


def wall(wid, cls, ablation, oracle, answer, separability="clean", **run_over):
    def deco(fn):
        WALLS.append(dict(wall_id=wid, failure_class=cls, ablation_applied=ablation,
                          oracle_diagnosis=oracle, answer_content=answer,
                          separability=separability, run_overrides=run_over, apply=fn))
        return fn
    return deco


# ── Class 1: search-operator removed ──────────────────────────────────
# The capability is present and expressible. No mutation path reaches it.

@wall("SO-01", "search_operator_removed",
      {"kind": "disable_operator", "operator": "crossover", "detail": "crossover_frac 0.3 -> 0.0"},
      "Every capability the battery rewards is present in the substrate and each is "
      "individually reachable, but the assembled organism requires several coordinated "
      "edits whose intermediate forms score no better than their parents. The search "
      "only ever applies one edit at a time, so it cannot traverse a plateau wider than "
      "one edit. The missing capability class is a multi-edit recombination move.",
      "Restore crossover (recombine/dispatch_merge) at crossover_frac 0.3.",
      crossover_frac=0.0)
def _so01(be):
    pass


@wall("SO-02", "search_operator_removed",
      {"kind": "withhold_mutation_move", "move": "add_guard", "compound": True,
       "co_ablated": "crossover disabled (see corpus finding F1)"},
      "Recombination is unavailable, so every organism must be built by single edits from "
      "its parent — and the one edit that appends a routing branch is also unavailable. "
      "Branch count is therefore frozen at whatever seeding supplied: bodies diversify "
      "normally while the distribution of branches-per-organism never moves. The missing "
      "capability class is a move that adds a routing branch to an existing organism.",
      "Restore the add_guard mutation move.",
      crossover_frac=0.0)
def _so02(be):
    restrict_moves(be, ["insert_step@", "remove_step:", "swap_step@", "swap_scorer"])


@wall("SO-03", "search_operator_removed",
      {"kind": "withhold_mutation_move", "move": "insert", "compound": True,
       "co_ablated": "crossover disabled (see corpus finding F1)"},
      "Recombination is unavailable and no single edit can lengthen a body. Pipeline "
      "length never exceeds what seeding supplied and drifts downward as removals "
      "accumulate, so any capability needing a longer body than a seed already contains "
      "is unreachable even though every constituent operator is registered. The missing "
      "capability class is a move that lengthens an organism.",
      "Restore the insert mutation move.",
      crossover_frac=0.0)
def _so03(be):
    restrict_moves(be, ["remove_step:", "swap_step@", "swap_scorer", "add_guard:"])


@wall("SO-04", "search_operator_removed",
      {"kind": "substitute_operator", "operator": "dispatch_merge",
       "detail": "replaced by single-suffix recombine"},
      "Routers acquire branches but the acquired branches are inert: the guard fires on "
      "no task because the transformer that writes its keyed slot is absent from the same "
      "organism. Recombination transfers a contiguous tail, so a branch's producer and "
      "its consumer are never co-transferred. The missing capability class is a "
      "recombination move that carries a branch's producer and consumer together.",
      "Restore dispatch_merge (body+guard UNION crossover) in dispatch mode.")
def _so04(be):
    be.dispatch_merge = be.recombine


@wall("SO-05", "search_operator_removed",
      {"kind": "withhold_mutation_move", "move": "swap_scorer", "compound": True,
       "co_ablated": "crossover disabled (see corpus finding F1)"},
      "Recombination is unavailable and no edit exchanges a terminal, so each lineage is "
      "locked to the terminal it was seeded with. Bodies diversify normally while the "
      "distribution of terminals is frozen, so a body that would score well under a "
      "different terminal never meets one. The missing capability class is a move that "
      "exchanges an organism's terminal.",
      "Restore the swap_scorer mutation move.",
      crossover_frac=0.0)
def _so05(be):
    restrict_moves(be, ["insert_step@", "remove_step:", "swap_step@", "add_guard:"])


@wall("SO-06", "search_operator_removed",
      {"kind": "withhold_mutation_move", "move": "all_growth", "compound": True,
       "detail": "only remove/swap_t retained", "co_ablated": "crossover disabled (see corpus finding F1)"},
      "Nothing in the search can make an organism larger — neither recombination nor any "
      "single edit. The population monotonically simplifies: organisms lose operators and "
      "never regain them, and the archive converges on the shortest viable pipelines "
      "regardless of accuracy. Every capability class remains registered; none is ever "
      "assembled. The missing capability classes are all of the growth moves at once.",
      "Restore insert, swap_scorer and add_guard.",
      crossover_frac=0.0)
def _so06(be):
    restrict_moves(be, ["remove_step:", "swap_step@"])


# ── Class 2: expressiveness restricted ────────────────────────────────
# No operator in the substrate can produce the required state transition.

@wall("EX-01", "expressiveness_restricted",
      {"kind": "remove_registry_ops", "ops": ["forward_chain"]},
      "Rules are parsed into state and sit unconsumed: no operator reads the rule slot "
      "and writes derived conclusions, so the derived-fact slot is empty on every task. "
      "Subsets whose answers require applying a rule to an asserted fact are uniformly "
      "unsolved by every organism in the archive. The missing capability class is a "
      "rule-application operator.",
      "Restore forward_chain (reads rules+facts, writes derived_facts).")
def _ex01(be):
    remove_ops(be, ["forward_chain"])


@wall("EX-02", "expressiveness_restricted",
      {"kind": "remove_registry_ops", "ops": ["relations_from_facts"]},
      "Both tiers work in isolation — derived facts are produced, and orderings are built "
      "from relations — but nothing converts the output type of the first into the input "
      "type of the second. Tasks needing one tier's product as the other's input are "
      "unsolved while each tier's own subset is solved. The missing capability class is a "
      "type bridge between derived facts and relations.",
      "Restore relations_from_facts (reads derived_facts, writes relations).")
def _ex02(be):
    remove_ops(be, ["relations_from_facts"])


@wall("EX-03", "expressiveness_restricted",
      {"kind": "remove_registry_ops", "ops": ["op_build_ordering"]},
      "Relations are parsed and available but the ordered slot is never populated, so "
      "every consumer that keys on a ranked sequence abstains. Ranking tasks are "
      "uniformly unsolved. The missing capability class is an operator that reduces "
      "pairwise relations to a total order.",
      "Restore op_build_ordering (reads relations, writes ordered).")
def _ex03(be):
    remove_ops(be, ["op_build_ordering"])


@wall("EX-04", "expressiveness_restricted",
      {"kind": "remove_registry_ops",
       "ops": ["parse_comparison", "score_by_comparison__g"]},
      "One task form asks a yes/no question about a relation between two quantities. No "
      "operator writes a boolean slot and no terminal emits a yes/no answer, so these "
      "tasks are answered only by whichever unconditional terminal happens to fire. "
      "Accuracy on them does not exceed chance. The missing capability class is a "
      "boolean-valued producer and a matching yes/no terminal.",
      "Restore parse_comparison + score_by_comparison__g.")
def _ex04(be):
    remove_ops(be, ["parse_comparison", "score_by_comparison__g"])


@wall("EX-05", "expressiveness_restricted",
      {"kind": "remove_registry_ops", "ops": ["parse_box_items"]},
      "A registered terminal keys its guard on the counts slot, and a registered "
      "transformer aggregates that slot, but nothing populates it from the problem text. "
      "The whole downstream chain is therefore inert on every task and the branch is "
      "decorative wherever it appears. The missing capability class is a counts-writer.",
      "Restore parse_box_items (reads problem_text, writes counts).")
def _ex05(be):
    remove_ops(be, ["parse_box_items"])


@wall("EX-06", "expressiveness_restricted",
      {"kind": "remove_registry_ops", "ops": ["select_nth__g"]},
      "The ordered slot is populated correctly on ranking tasks and can be inspected, but "
      "no terminal converts a position in that sequence into a selected answer. Ranking "
      "tasks fail at the final step rather than the reasoning step. The missing capability "
      "class is a positional selector over an ordered sequence.",
      "Restore select_nth__g.")
def _ex06(be):
    remove_ops(be, ["select_nth__g"])


@wall("EX-07", "expressiveness_restricted",
      {"kind": "remove_registry_ops", "ops": ["op_aggregate_quantities"]},
      "Per-item counts are parsed into state but never reduced: the terminal that keys on "
      "an aggregate finds only the raw per-item mapping and abstains. Tasks requiring a "
      "total over parsed items are unsolved while single-item lookups succeed. The missing "
      "capability class is a reducer over a counts mapping.",
      "Restore op_aggregate_quantities.")
def _ex07(be):
    remove_ops(be, ["op_aggregate_quantities"])


@wall("EX-08", "expressiveness_restricted",
      {"kind": "remove_registry_ops", "ops": ["parse_rules"]},
      "The inference operator is present and correct but runs on an empty rule set on "
      "every task, so it derives nothing and its consumer abstains. The failure is at the "
      "ingest step, not the inference step: nothing converts problem text into rules and "
      "asserted facts. The missing capability class is a rule/fact ingester.",
      "Restore parse_rules (reads problem_text, writes rules+facts).")
def _ex08(be):
    remove_ops(be, ["parse_rules"])


# ── Class 3: measurement-artifact injected ────────────────────────────
# Capability present AND reachable AND assembled. The meter cannot see it.

@wall("MA-01", "measurement_artifact",
      {"kind": "bend_fitness", "detail": "selection accuracy computed on canary subset only"},
      "Portfolio coverage over the whole battery rises while the headline accuracy stays "
      "flat, and the archive keeps acquiring organisms that solve subsets the headline "
      "never credits. Selection pressure is being computed over a proper subset of the "
      "evaluation set, so improvements outside that subset are invisible to the search "
      "even though they are recorded elsewhere in the telemetry. The defect is in the "
      "scoring scope, not in any organism.",
      "Score fitness over the full 120-task battery, not the 50-task canary.")
def _ma01(be):
    def bend(be_, org, tasks, sb, f):
        sub = _canary_slice(tasks)
        acc = be_._evaluate_acc(org.ops(), sub)
        f["acc"] = acc
        f["comp_lift"] = acc - sb
        f["causal_composition_score"] = (max(0.0, f["comp_lift"])
                                         * max(0.0, f["dataflow_score"]))
        return f
    wrap_fitness(be, bend)


@wall("MA-02", "measurement_artifact",
      {"kind": "bend_descriptor", "detail": "archive keyed on full op-set, not load-bearing core"},
      "Archive cell count grows without bound while the number of behaviourally distinct "
      "organisms does not, and the best score is flat throughout. Cells are being "
      "distinguished by a property that includes causally inert operators, so one "
      "behaviour occupies many cells, and selection pressure is diluted across duplicates "
      "of the same organism. The defect is in the archive's identity function.",
      "Key the descriptor on the load-bearing core (lb_ops), not the full pipeline.")
def _ma02(be):
    def desc(org, f):
        scorers = frozenset(n for n in org.pipeline if be.role_of(n) == be.ROLE_SCORER)
        return (scorers, frozenset(org.pipeline))
    be.descriptor = desc


@wall("MA-03", "measurement_artifact",
      {"kind": "bend_descriptor", "detail": "descriptor drops the terminal-set component"},
      "A multi-branch router and a single-branch specialist that happen to share a body "
      "are treated as the same entry, so whichever was evaluated most recently displaces "
      "the other. Routing structure is never accumulated: the archive repeatedly discards "
      "an organism that answers several task types in favour of one that answers a single "
      "type. The defect is that the archive's identity function ignores terminal structure.",
      "Restore the scorer-set component of the descriptor.")
def _ma03(be):
    def desc(org, f):
        return (frozenset(), f["lb_ops"])
    be.descriptor = desc


@wall("MA-04", "measurement_artifact",
      {"kind": "bend_fitness", "detail": "accuracy estimated from a random 20-task resample per call"},
      "The best single organism is reported as solving a larger fraction of the battery "
      "than the union of every organism in the archive solves — an ordering that cannot "
      "occur if both numbers measure the same tasks, since one organism's solved set is a "
      "subset of the union. The same organism also receives different scores on repeated "
      "evaluation, and occupants are displaced by organisms that are not actually better. "
      "The headline is an estimate from a small sample redrawn on every call, so it "
      "carries sampling variance the coverage figure does not, and reports optimistically "
      "on lucky draws. The defect is the precision of the meter, not the population.",
      "Evaluate fitness on the full deterministic battery, not a random subsample.")
def _ma04(be):
    import random as _r

    def bend(be_, org, tasks, sb, f):
        sample = _r.sample(tasks, min(20, len(tasks)))
        acc = be_._evaluate_acc(org.ops(), sample)
        f["acc"] = acc
        f["comp_lift"] = acc - sb
        f["causal_composition_score"] = (max(0.0, f["comp_lift"])
                                         * max(0.0, f["dataflow_score"]))
        return f
    wrap_fitness(be, bend)


@wall("MA-05", "measurement_artifact",
      {"kind": "bend_fitness", "detail": "accuracy quantised to 1 decimal place"},
      "The score moves in discrete jumps and is flat between them, and organisms whose "
      "true accuracy differs are recorded as tied. Improvements smaller than the "
      "quantisation step are invisible, so gradual assembly gets no gradient and only "
      "changes large enough to clear a step size are ever selected. The defect is the "
      "resolution of the meter, not the capability of the population.",
      "Stop rounding acc; use full precision in fitness.")
def _ma05(be):
    def bend(be_, org, tasks, sb, f):
        acc = round(f["acc"], 1)
        f["acc"] = acc
        f["comp_lift"] = acc - sb
        f["causal_composition_score"] = (max(0.0, f["comp_lift"])
                                         * max(0.0, f["dataflow_score"]))
        return f
    wrap_fitness(be, bend)


@wall("MA-06", "measurement_artifact",
      {"kind": "bend_descriptor", "detail": "descriptor drops the body component"},
      "The archive saturates at a few dozen cells within the first generations and stops "
      "growing, while an unablated run of the same length accumulates hundreds. Organisms "
      "with completely different bodies displace one another from the same entry, so "
      "assembled bodies are discarded rather than retained alongside their neighbours. "
      "Headline accuracy and coverage are NOT degraded — a single organism already covers "
      "what the battery rewards — so the fault is visible only in the population "
      "structure. The defect is that the archive's identity function ignores the body "
      "entirely.",
      "Restore the (scorer-set, load-bearing-core) descriptor.")
def _ma06(be):
    def desc(org, f):
        scorers = frozenset(n for n in org.pipeline if be.role_of(n) == be.ROLE_SCORER)
        return (scorers, frozenset())
    be.descriptor = desc


# ── Class 4: interface-bug planted ────────────────────────────────────
# Everything present, reachable, assembled and measured. A wiring detail silently
# prevents the capability from firing.

@wall("IB-01", "interface_bug",
      {"kind": "rebind_guard", "guard": "score_by_aggregate__g",
       "detail": "precondition keyed on slot `quantities` (never written) instead of `counts`"},
      "One branch of the router never fires on any task. Its parser runs and populates a "
      "slot, and its terminal is present and correct, but the guard between them tests a "
      "different slot than the one the parser writes — and no operator in the substrate "
      "writes the slot being tested. Per-branch ablation shows the branch dropping nothing "
      "anywhere. The defect is a slot-name mismatch in the branch's precondition.",
      "Re-key the guard from `quantities` onto `counts`.")
def _ib01(be):
    rebind_guard(be, "score_by_aggregate__g", "score_by_aggregate",
                 lambda s: len(s.quantities) > 0 and len(s.ordered) == 0
                 and len(s.derived_facts) == 0 and len(s.facts) == 0)


@wall("IB-02", "interface_bug",
      {"kind": "rebind_guard", "guard": "select_nth__g",
       "detail": "precondition inverted (len(ordered) == 0)"},
      "A branch fires on exactly the tasks it cannot serve and abstains on exactly the "
      "tasks it was built for. Its subset accuracy is near zero while the slot it consumes "
      "is populated correctly on those same tasks. The guard's truth value is the negation "
      "of the condition under which the branch is applicable.",
      "Invert the guard back to len(ordered) > 0.")
def _ib02(be):
    rebind_guard(be, "select_nth__g", "select_nth", lambda s: len(s.ordered) == 0)


@wall("IB-03", "interface_bug",
      {"kind": "rebind_guard", "guard": "score_by_derivability__g",
       "detail": "precondition keyed on slot `probabilities` (never written)"},
      "The inference chain runs to completion and its output slot is correctly populated, "
      "but the terminal that consumes it never executes. The guard tests a slot that no "
      "registered operator writes, so the precondition is false on every task regardless "
      "of what the pipeline computed. Upstream telemetry looks healthy; the subset is "
      "unsolved.",
      "Re-key the guard onto derived_facts/facts.")
def _ib03(be):
    rebind_guard(be, "score_by_derivability__g", "score_by_derivability",
                 lambda s: len(s.probabilities) > 0)


@wall("IB-04", "interface_bug",
      {"kind": "shadow_op", "op": "relations_from_facts",
       "detail": "declares writes=[relations] but the write does not persist"},
      "An operator is present, executes without error, and declares that it writes a slot "
      "its downstream consumer reads — but after it runs the slot is still empty. The "
      "dataflow accounting credits the declared write, so the operator is scored as "
      "load-bearing while contributing nothing. Organisms that depend on the bridged value "
      "fail while their telemetry shows the bridge executing.",
      "Make relations_from_facts actually persist its write to `relations`.")
def _ib04(be):
    orig = be.REGISTRY["relations_from_facts"][0]

    def shadow(state):
        state = orig.fn(state)
        state.relations = []            # the declared write silently does not persist
        return state
    be.REGISTRY["relations_from_facts"] = (
        be.BlackboardOp(shadow, reads=orig.reads, writes=orig.writes,
                        precondition=orig.precondition, on_fail="skip",
                        name="relations_from_facts"), be.ROLE_TRANSFORMER)


@wall("IB-05", "interface_bug",
      {"kind": "rebind_on_fail", "detail": "guarded scorers use on_fail='error' instead of 'skip'"},
      "Multi-branch organisms score far below their own single-branch parents. A branch "
      "whose guard does not apply to the current task terminates the whole pipeline "
      "instead of standing aside, so adding any branch strictly harms the organism and "
      "routing is impossible to assemble. The defect is the declared behaviour of a branch "
      "on inapplicable input.",
      "Set on_fail='skip' for guarded scorers.")
def _ib05(be):
    for g in list(be.GUARDED_SCORERS):
        op, role = be.REGISTRY[g]
        be.REGISTRY[g] = (be.BlackboardOp(op.fn, reads=op.reads, writes=op.writes,
                                          precondition=op.precondition,
                                          on_fail="error", name=op.name), role)


@wall("IB-06", "interface_bug",
      {"kind": "shadow_op", "op": "parse_comparison",
       "detail": "writes its result into `evidence` instead of the slot its consumer reads"},
      "A parser executes on the right tasks and extracts the right value, but its consumer "
      "abstains on every one of them. The value is deposited in a different slot than the "
      "one the consumer keys on; both slots exist and neither operator errors. The two "
      "halves of the branch disagree about where the intermediate value lives.",
      "Write to `comparison`, the slot score_by_comparison__g reads.")
def _ib06(be):
    orig = be.REGISTRY["parse_comparison"][0]

    def shadow(state):
        state = orig.fn(state)
        if state.comparison is not None:
            state.evidence.append({"comparison": state.comparison})
            state.comparison = None
        return state
    be.REGISTRY["parse_comparison"] = (
        be.BlackboardOp(shadow, reads=orig.reads, writes=orig.writes,
                        precondition=orig.precondition, on_fail="skip",
                        name="parse_comparison"), be.ROLE_TRANSFORMER)


# ── Positive controls: no ablation ────────────────────────────────────

@wall("CTRL-01", "control_none", {"kind": "none"},
      "No ablation. Every capability class is present, reachable, assembled and correctly "
      "measured. A detector that reports a wall here is producing false positives.",
      "No fix required.")
def _ctrl01(be):
    pass


@wall("CTRL-02", "control_none", {"kind": "none", "detail": "different seed"},
      "No ablation, independent seed. Establishes the run-to-run variation of the wall "
      "signature under no fault, which bounds how much of any ablated run's signature is "
      "attributable to the ablation.",
      "No fix required.", seed=20260816)
def _ctrl02(be):
    pass


WALLS_BY_ID = {w["wall_id"]: w for w in WALLS}


# ══════════════════════════════════════════════════════════════════════
# Signature extraction
# ══════════════════════════════════════════════════════════════════════

def wall_signature(history):
    """Plateau telemetry. Contains NO solution content: only what an observer watching
    the run's own instrument panel could see."""
    if not history:
        return {}
    final = history[-1]
    accs = [h["max_acc"] for h in history]
    best_acc = max(accs)

    # gens_to_plateau: first gen achieving the final max_acc, never improved after
    gtp = next(i + 1 for i, a in enumerate(accs) if a >= best_acc)

    improvements = [{"gen": i + 1, "max_acc": accs[i]}
                    for i in range(len(accs)) if i == 0 or accs[i] > accs[i - 1]]

    viab = [h["mutation_viability"] for h in history]
    cells = [h["archive_cells"] for h in history]
    lens = [len(h["best_pipeline"]) for h in history]
    per = final.get("portfolio_per_subset", {})

    audits = [h["dispatch_audit"] for h in history if "dispatch_audit" in h]
    last_audit = audits[-1] if audits else None

    tail = max(1, len(history) // 4)
    return {
        "gens_run": len(history),
        "final_max_acc": final["max_acc"],
        "final_max_routable_acc": final.get("max_routable_acc"),
        "final_portfolio_coverage": final.get("portfolio_coverage"),
        "final_per_subset": per,
        "subsets_unsolved": sorted(k for k, v in per.items() if v <= 0.05),
        "subsets_solved": sorted(k for k, v in per.items() if v >= 0.95),
        "gens_to_plateau": gtp,
        "plateau_fraction": round((len(history) - gtp) / len(history), 3),
        "n_improvement_events": len(improvements),
        "improvement_curve": improvements,
        "final_archive_cells": final["archive_cells"],
        "final_distinct_real_shapes": final["distinct_real_shapes"],
        "cells_growth_after_plateau": cells[-1] - cells[min(gtp - 1, len(cells) - 1)],
        "cells_per_gen_tail": round((cells[-1] - cells[-tail]) / tail, 3),
        "shape_inflation_ratio": round(final["archive_cells"]
                                       / max(final["distinct_real_shapes"], 1), 3),
        "final_primitive_families": final["primitive_families"],
        "final_n_dispatchers": final.get("n_dispatchers"),
        "final_novel_multitier": final["novel_multitier"],
        "mutation_viability_mean": round(sum(viab) / len(viab), 3),
        "mutation_viability_min": round(min(viab), 3),
        "best_pipeline_len_first": lens[0],
        "best_pipeline_len_final": lens[-1],
        "best_pipeline_len_max": max(lens),
        "final_best_n_load_bearing": final["best_n_load_bearing"],
        "final_best_ccs": final["best_causal_composition_score"],
        "dispatch_audit_final": last_audit,
        "genuine_routing_final": (last_audit or {}).get("genuine_routing"),
        "branches_load_bearing_for_nothing": sorted(
            b for b, v in ((last_audit or {}).get("branches") or {}).items()
            if not v.get("load_bearing_for")),
    }


# ══════════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════════

def substrate_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True,
                              cwd=str(Path(__file__).resolve().parents[2])).stdout.strip()
    except Exception:
        return "unknown"


def run_wall(wid, gens):
    spec = WALLS_BY_ID[wid]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "walls").mkdir(exist_ok=True)
    (OUT / "runs").mkdir(exist_ok=True)

    import blackboard_evolve as be
    spec["apply"](be)

    cfg = dict(BASE_RUN)
    cfg.update(spec["run_overrides"])
    run_dir = OUT / "runs" / wid
    if run_dir.exists():
        for f in run_dir.glob("*.jsonl"):
            f.unlink()

    console = open(OUT / "runs" / f"{wid}_console.log", "w", encoding="utf-8")
    old = sys.stdout
    t0 = time.time()
    try:
        sys.stdout = console
        history = be.evolve(gens=gens, pop_size=cfg["pop_size"], mode=cfg["mode"],
                            seed=cfg["seed"], run_dir=str(run_dir),
                            log_every=cfg["log_every"], checkpoint_every=gens,
                            crossover_frac=cfg["crossover_frac"],
                            dispatch=cfg["dispatch"])
    finally:
        sys.stdout = old
        console.flush()
        console.close()

    rec = {
        "wall_id": wid,
        "failure_class": spec["failure_class"],
        "ablation_applied": spec["ablation_applied"],
        "wall_signature": wall_signature(history),
        "oracle_diagnosis": spec["oracle_diagnosis"],
        "answer_content": spec["answer_content"],
        "gens_to_plateau": wall_signature(history).get("gens_to_plateau"),
        "separability": spec["separability"],
        "provenance": {
            "substrate": "apollo/src/blackboard_evolve.py",
            "substrate_commit": substrate_commit(),
            "harness": "apollo/scripts/wall_corpus.py",
            "run_config": {k: v for k, v in cfg.items()},
            "gens": gens,
            "wall_clock_s": round(time.time() - t0, 1),
            "generated": "2026-08-15",
            "generator": "Apollo (M2)",
        },
    }
    with open(OUT / "walls" / f"{wid}.json", "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    return rec


def emit_corpus():
    """Collate the per-wall records into the single consumable JSONL + a manifest."""
    files = sorted((OUT / "walls").glob("*.json"))
    recs = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    recs.sort(key=lambda r: r["wall_id"])
    with open(OUT / "corpus.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())

    by_class = {}
    for r in recs:
        by_class.setdefault(r["failure_class"], []).append(r)
    summary = {
        "n_records": len(recs),
        "n_walls": sum(1 for r in recs if r["failure_class"] != "control_none"),
        "n_controls": sum(1 for r in recs if r["failure_class"] == "control_none"),
        "classes": {c: [r["wall_id"] for r in v] for c, v in sorted(by_class.items())},
        "field_disposition": {
            "f_oracle_shippable": ["wall_id", "wall_signature", "oracle_diagnosis"],
            "quarantined_answer_side": ["answer_content", "ablation_applied", "failure_class"],
            "never_shipped": ["provenance", "separability"],
        },
        "tight_separability": [r["wall_id"] for r in recs if r["separability"] == "tight"],
        "substrate_commit": recs[0]["provenance"]["substrate_commit"] if recs else None,
    }
    with open(OUT / "corpus_manifest.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--gens", type=int, default=150)
    args = ap.parse_args()

    if args.manifest:
        s = emit_corpus()
        print(json.dumps(s, indent=2))
        return

    if args.list:
        for w in WALLS:
            print(f"{w['wall_id']:8s} {w['failure_class']:28s} {w['ablation_applied']['kind']}")
        print(f"\n{len(WALLS)} runs; "
              f"{len([w for w in WALLS if w['failure_class'] != 'control_none'])} walls across "
              f"{len({w['failure_class'] for w in WALLS if w['failure_class'] != 'control_none'})} classes")
        return

    if args.wall:
        rec = run_wall(args.wall, args.gens)
        s = rec["wall_signature"]
        print(f"{args.wall}: max_acc={s['final_max_acc']} routable={s['final_max_routable_acc']} "
              f"cov={s['final_portfolio_coverage']} plateau@{s['gens_to_plateau']} "
              f"cells={s['final_archive_cells']} ({rec['provenance']['wall_clock_s']}s)")
        return

    if args.all:
        OUT.mkdir(parents=True, exist_ok=True)
        done, failed = [], []
        for w in WALLS:
            wid = w["wall_id"]
            t0 = time.time()
            r = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                "--wall", wid, "--gens", str(args.gens)],
                               capture_output=True, text=True)
            if r.returncode == 0:
                print(f"  {r.stdout.strip()}", flush=True)
                done.append(wid)
            else:
                print(f"  {wid}: FAILED rc={r.returncode}\n{r.stderr[-1500:]}", flush=True)
                failed.append(wid)
        print(f"\n{len(done)} ok, {len(failed)} failed  {failed if failed else ''}")
        if not failed:
            s = emit_corpus()
            print(f"corpus.jsonl: {s['n_records']} records "
                  f"({s['n_walls']} walls / {s['n_controls']} controls)")


if __name__ == "__main__":
    main()
