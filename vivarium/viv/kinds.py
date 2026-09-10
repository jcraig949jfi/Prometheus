"""The execution-kind registry: what each kind of experiment REQUIRES.

One entry per executor kind. An entry declares the EXACT set of parameters the
kind consumes -- not a minimum, an exact set. Validation requires all of them
and rejects any extra, and no executor is permitted a default for any of them.

WHY EXACT AND WHY NO DEFAULTS. `evaluate_bitstring` derived its hidden target
from sha256("target:{seed_root}:{length}"), and `length` defaulted to 24. A
spec that omitted it was accepted and then silently run against a
Vivarium-chosen landscape -- Vivarium supplying a scientific parameter, which
is the one thing this seat exists not to do. A missing parameter is now a
REJECTED SPECIFICATION. An absent value that means something (no controls, no
prediction) must be written explicitly, because "absent" and "empty" are
different experiments and only one of them was requested.

IMPLEMENTED vs EXTERNAL. `implemented=False` declares a kind whose contract is
known but whose executor does not live here. Such a row is admissible -- the
queue is a REGISTER, and a candidate registered before selection need not be
runnable today -- but executing it fails terminally with
EXECUTOR_NOT_IMPLEMENTED rather than silently doing something else.

OWNERSHIP. `owner` names the seat that owns an entry's content. Vivarium owns
the shape of this file and the two kinds it can execute; it does not own the
scientific meaning of another seat's parameters. An entry marked PROVISIONAL
was transcribed by Vivarium from what that seat's code actually emits, and is
theirs to confirm or correct.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet

from .result_schema import Field as R
from .result_schema import (describe as describe_result,
                             reduction_supported, validate_result)


#: Lifecycle of a kind. RETIRED is not deletion: rows and fossils that named a
#: retired kind stay readable and keep their meaning, and the entry stays here
#: so an archaeologist reading a 2026-09 fossil can still learn what
#: `archaeon.probe.v0` meant. What RETIRED forbids is a NEW admission.
ACTIVE = "ACTIVE"
RETIRED = "RETIRED"


@dataclass(frozen=True)
class Kind:
    kind: str
    #: The EXACT parameter names work.payload must carry. Not a minimum.
    params: FrozenSet[str]
    #: False = contract known, executor absent. Admissible, not runnable.
    implemented: bool
    owner: str
    note: str = ""
    provisional: bool = False
    #: ACTIVE | RETIRED. A retired kind is refused at ADMISSION and keeps its
    #: historical meaning for everything already recorded.
    status: str = ACTIVE
    #: Does the executor carry state between repeats? A spec may only declare
    #: repeat.state="persist" for a stateful kind -- otherwise "persist" would
    #: be a silent no-op: a declared scientific choice quietly not happening.
    stateful: bool = False
    #: Why it was retired, and what replaced it. Never blank when RETIRED.
    retired_note: str = ""
    retired_at: str = ""
    #: WP-0f. What the executor RETURNS: field -> result_schema.Field. Empty
    #: for a kind whose executor does not live here -- an external owner
    #: declares its own result, and guessing one would be a contract Vivarium
    #: is not entitled to write.
    result_schema: Dict[str, R] = field(default_factory=dict)
    #: C1. Which of `params` are ARTIFACT SLOTS -- payload keys whose value is
    #: {digest, artifact_type, schema_version, codec, expected_bytes,
    #: interface_id} and which preflight resolves to bytes before execution.
    #: Empty for every kind that existed before the loader, so their contracts
    #: and their identities are untouched: this ADDS an inner exact-key check
    #: to the new consuming kinds and relaxes nothing anywhere.
    artifact_slots: FrozenSet[str] = frozenset()
    #: Which of `artifact_slots` may be the JSON value `null`, meaning THIS
    #: EXPERIMENT DECLARES IT CONSUMES NOTHING HERE. The key is still present
    #: and the payload contract is still exact, so `null` is a value inside
    #: spec_hash and not an omission -- H0's "off" cell is a declared input
    #: rather than a hidden alternative library. A slot NOT listed here may
    #: never be null: `artifact_probe_v1` without its artifact is not a
    #: control, it is a broken request.
    optional_artifact_slots: FrozenSet[str] = frozenset()

    @property
    def retired(self) -> bool:
        return self.status == RETIRED

    @property
    def declares_result(self) -> bool:
        return bool(self.result_schema)

    def check_result(self, result, *, truncation=None) -> dict:
        """Validate an executor's OUTPUT. Raises ResultSchemaError."""
        return validate_result(self.kind, self.result_schema, result,
                               truncation=truncation)

    def supports_reduction(self, field_name: str, reduction: str):
        """May an outcome rule reduce this output field this way?"""
        return reduction_supported(self.result_schema, field_name, reduction)

    def result_lines(self) -> list:
        return describe_result(self.result_schema)

    def check(self, payload: dict) -> list:
        """Reasons this payload does not satisfy the contract. Empty = ok."""
        if not isinstance(payload, dict):
            return ["work.payload must be an object"]
        got = set(payload)
        reasons = []
        missing = sorted(self.params - got)
        if missing:
            reasons.append(
                "work.payload for kind %r is missing %s; every parameter that "
                "can change the result must be explicit (no executor default "
                "exists or is permitted)" % (self.kind, missing))
        extra = sorted(got - self.params)
        if extra:
            reasons.append(
                "work.payload for kind %r carries unknown parameter(s) %s; "
                "the contract is exact, and an unread parameter in a hashed "
                "spec is a channel, not a comment" % (self.kind, extra))
        # C1: the same exactness, one level down. A slot whose keys are wrong,
        # or whose digest/type/interface cannot be resolved by this build, is
        # refused at ADMISSION -- "placeholders never enter a queue".
        for name in sorted(self.artifact_slots):
            if name not in payload:
                continue
            from . import artifacts as _artifacts            # noqa: PLC0415
            if payload[name] is None:
                if name not in self.optional_artifact_slots:
                    reasons.append(
                        "artifact slot %r of kind %r may not be null; this "
                        "kind has no meaning without it, so an absent value "
                        "here is a broken request and not a control"
                        % (name, self.kind))
                continue
            reasons.extend(_artifacts.check_slot(name, payload[name]))
        return reasons


REGISTRY: Dict[str, Kind] = {}


def register(k: Kind) -> Kind:
    REGISTRY[k.kind] = k
    return k


# --------------------------------------------------------------- Vivarium's
register(Kind(
    kind="noop_v0",
    params=frozenset(),
    implemented=True,
    owner="vivarium",
    note="Exercises the whole queue -> SFE -> PEW loop with no science in it. "
         "Takes no parameters at all, so there is nothing it could default.",
    result_schema={
        "executed": R("boolean", note="always true; the loop ran"),
    }))

register(Kind(
    kind="evaluate_bitstring",
    params=frozenset({"bits", "length"}),
    implemented=True,
    owner="vivarium",
    note="Delegates to the engine's own reference executor. `length` is a "
         "scientific parameter: the hidden target is derived from "
         "sha256('target:<seed_root>:<length>'), so two lengths are two "
         "landscapes. It used to default to 24.",
    result_schema={
        "bits": R("string", note="the candidate as scored"),
        "score": R("number", finite=True,
                   note="fraction of positions matching the hidden target"),
        "solved": R("boolean", note="score >= 1.0"),
        "length": R("integer", note="the landscape length actually used"),
    }))


# --------------------------------------------------------------- Archaeon's
register(Kind(
    kind="archaeon.probe.v0",
    params=frozenset({"procedure", "probe_kind", "replicates", "worlds",
                      "players", "target", "hold_fixed", "controls"}),
    implemented=False,
    owner="archaeon",
    provisional=True,
    status=RETIRED,
    retired_at="2026-09-06",
    note="HISTORICAL MEANING, PRESERVED. A region-targeted re-interrogation of "
         "the sfe.candidate_score.v0 chart. `probe_kind` named the operation "
         "from Archaeon's fixed detector->probe table (RESAMPLE_REGION, "
         "REPLICATE_AT_COORDINATE, INTERPOLATE_BETWEEN, CROSS_REPLICATE, "
         "REPEAT_OUTLIER_CELL, BISECT_BOUNDARY); `target` gave the coordinate "
         "in both normalized and raw form; `worlds`/`players` the region; "
         "`hold_fixed` what the probe held constant; `replicates` how many "
         "times; `controls` the nearby conditions, [] meaning explicitly none. "
         "Any queue row or fossil naming this kind still means exactly that, "
         "and this entry exists so it stays readable.",
    retired_note="RETIRED 2026-09-06 by operator direction. No executor was "
         "ever written for it and none can be written faithfully: the "
         "sfe.candidate_score.v0 worlds it targets were scored by a harness "
         "Vivarium does not have -- candidate 6926509 scores 0.42289 in the "
         "corpus and 0.33333 under the engine's 24-bit reference executor, and "
         "0.42289 is not a multiple of 1/24 -- so any substitution would "
         "fabricate an execution that was not the one requested. Archaeon's "
         "producer already routes around it with a declared random.v0 draw "
         "over evaluate_bitstring. Its re-execution half is now served by "
         "`repeat` (spec v3); its region-targeting half is an SFE substrate "
         "request, not an executor kind. RETIRED refuses NEW admissions only."))


# ------------------------------------------------- primitives for `repeat`
register(Kind(
    kind="random_walk_v0",
    params=frozenset({"steps", "step_scale"}),
    implemented=True,
    owner="vivarium",
    stateful=True,
    note="A bench primitive, not a scientific claim. A deterministic 1-D walk: "
         "`steps` increments drawn from the repeat's derived seed, each scaled "
         "by `step_scale`. It exists because repeat.state has no observable "
         "meaning without a kind that HAS state -- under `reset` the repeats "
         "are independent draws, under `persist` they are one trajectory, and "
         "that difference is exactly what within-world serial autocorrelation "
         "reads. Available to templates; ADMITTING a template that uses it is "
         "the operator's act, never mine.",
    result_schema={
        "position": R("number", finite=True, note="position after this repeat"),
        "start_position": R("number", finite=True,
                            note="position this repeat began from; equals the "
                                 "previous position under state=persist"),
        "displacement": R("number", finite=True,
                          note="position - start_position"),
        "steps": R("integer", note="steps taken, echoing the declared param"),
        "step_scale": R("number", finite=True),
        "seed": R("integer", note="the REPEAT's derived seed, not the world's"),
    }))


# ------------------------------------------------- Herakles's, wrapped (C1)
register(Kind(
    kind="ca_density_v0",
    params=frozenset({"rule_hex", "radius", "n_cells", "steps", "n_ic",
                      "ic_density_set", "success_criterion", "transform"}),
    implemented=True,
    owner="herakles (library) / vivarium (wrapper)",
    stateful=False,
    note="A thin wrapper around herakles/evca (WP-C1). Vivarium owns the kind "
         "contract; Herakles owns the semantics -- the rule encoding, the "
         "neighbourhood bit order, the periodic boundary and the r=3-only "
         "refusal all come from core.py and none is decided here. The lattice "
         "state lives inside ONE execution, so nothing carries between "
         "repeats and stateful is False. `success_criterion` (at_T | stable) "
         "chooses which mask `accuracy` is scored under; BOTH are always "
         "reported, along with the two per-rule fixed-point facts that decide "
         "whether they can differ at all. `ic_density_set` is ordered, null "
         "meaning the unbiased ensemble; n_ic is ICs PER density.",
    result_schema={
        "accuracy": R("number", finite=True,
                      note="scored under the declared success_criterion"),
        "misclassified_ic": R("vector", element="integer",
                              bounds=(0, 64), reductions=("any", "count"),
                              note="IC indices, global across density blocks, "
                                   "ascending, bounded"),
        "spacetime_digest": R("string",
                              note="one declared space-time diagram: ic_index "
                                   "0 of the first block"),
        "success_criterion": R("string", note="echoed, so a reader cannot "
                                             "mistake which question was "
                                             "answered"),
        "accuracy_at_T": R("number", finite=True),
        "accuracy_stable": R("number", finite=True),
        "n_incorrect_at_T": R("integer"),
        "n_incorrect_stable": R("integer"),
        "mask_digest": R("string",
                         note="F-20: the mask under the DECLARED criterion -- "
                              "the same rule `accuracy` follows. The two "
                              "per-criterion digests below are unchanged and "
                              "still reported; this is the one a symmetry "
                              "check compares without having to work out "
                              "which reading the row used"),
        "witness": R("vector", element="integer", bounds=(0, 64),
                     reductions=("any", "count"),
                     note="F-20: the same list as misclassified_ic, under the "
                          "name Herakles's c3_null_check reads"),
        "mask_digest_at_T": R("string"),
        "mask_digest_stable": R("string"),
        "all_zeros_fixed": R("boolean", note="table entry 0"),
        "all_ones_fixed": R("boolean", note="table entry 127"),
        "criteria_agree": R("boolean",
                            note="whether at_T and stable selected the same "
                                 "ICs on this run"),
        "n_ic_total": R("integer", note="n_ic * len(ic_density_set)"),
        "n_cells": R("integer"),
        "steps": R("integer"),
        "witness_truncated": R("boolean"),
        "transform": R("string",
                      note="none | reflect | complement | reflect_complement; "
                           "the four EXACT symmetries, so a transformed arm is "
                           "a NULL arm and accuracy that moves under one is a "
                           "defect rather than a result"),
        "accuracy_is_per_cell_mean": R("boolean",
            note="ALWAYS present. `accuracy` is a per-cell MEAN under "
                 "cellwise_majority_match and a fraction of ICs under the two "
                 "mask criteria; a reader must not have to infer which shape "
                 "it has from the criterion string"),
        # Present only under cellwise_majority_match: Herakles's own fields,
        # under his names. The dispersion is not optional information -- he
        # states that the two CONSTANT rules land on the same mean as a random
        # table and are separated only by it, so a row carrying the mean alone
        # would hide what makes the mean usable.
        "cellwise_sd_across_ics": R("number", finite=True, required=False,
            note="IC-to-IC spread WITHIN this table: ~0.50 for a constant "
                 "rule, ~0.10 for a random one. NOT the spread of the mean "
                 "across tables, which is far smaller"),
        "cellwise_min_cell_match": R("number", finite=True, required=False),
        "cellwise_max_cell_match": R("number", finite=True, required=False),
        "cellwise_fraction_all_cells_match": R("number", finite=True,
                                               required=False),
        "cellwise_fraction_no_cells_match": R("number", finite=True,
                                              required=False),
        "cellwise_comparable_to_published_P": R("boolean", required=False,
            note="false: this is a different measure from the published "
                 "density-classification P and is not to be compared with it"),
        "ic_transformed": R("boolean",
                            note="F-20: whether the REALISED IC sample "
                                 "actually changed. Measured by comparing the "
                                 "arrays, never declared from the transform "
                                 "name -- transforming the rule alone is not "
                                 "the symmetry, and this is how a reader "
                                 "establishes which happened"),
        "majority_target_flipped": R("boolean",
                                     note="F-20: whether the majority target "
                                          "is the complement of the "
                                          "untransformed sample's. Measured. "
                                          "Complement must flip it; if it did "
                                          "not, the target was computed from "
                                          "the wrong sample"),
        "transformed_rule_hex": R("string",
                                  note="the rule actually run; equal to "
                                       "rule_hex under transform=none"),
        "spacetime_is_image_of_untransformed": R("boolean",
            note="false under a transform: the library re-draws its own IC for "
                 "the diagram and does not see the transform, so the diagram "
                 "is faithful to the rule that ran and is NOT the image of the "
                 "untransformed run's diagram"),
    }))


# ------------------------------------------------- the loader's own fixture
register(Kind(
    kind="artifact_probe_v1",
    params=frozenset({"failure_inputs", "reduction"}),
    artifact_slots=frozenset({"failure_inputs"}),
    implemented=True,
    owner="vivarium",
    stateful=False,
    note="AN INSTRUMENT, NOT AN EXPERIMENT. The first kind that consumes an "
         "immutable artifact input, and it exists to make the loader path "
         "observable end to end -- not to measure anything about Boolean "
         "functions. Its arithmetic is a deterministic fold over the ORDERED "
         "input rows the artifact carries, chosen because it changes when any "
         "byte of the input changes and for no other reason; reading a "
         "scientific meaning into `folded` would be reading one into a "
         "checksum. H0's design says the same of its hand-built library "
         "fixtures: they exercise the plumbing and are explicitly instrument "
         "controls.\n"
         "The `failure_inputs` slot is an artifact SLOT: the digest is sealed "
         "in spec_hash, and the locator that finds a copy of those bytes is "
         "not. `reduction` names which fold, so nothing here has a default.",
    result_schema={
        "folded": R("integer",
                    note="deterministic fold over the ordered rows; an "
                         "instrument reading, not a measurement of anything"),
        "reduction": R("string", note="which fold, echoed"),
        "items_consumed": R("integer",
                            note="root items plus the whole closure's"),
        "root_items": R("integer"),
        "n_bits": R("integer"),
        "items_digest": R("string",
                          note="sha256 of the ordered rows AS CONSUMED, so a "
                               "reordering is visible"),
        "input_digest": R("string", note="the sealed slot digest, echoed"),
        "consumed_closure_hash": R("string",
                                   note="the closure in the order the KIND "
                                        "consumed it; preflight resolves "
                                        "depth-first, so this is not the "
                                        "receipt's manifest hash"),
        "closure_size": R("integer"),
        "interface_id": R("string"),
        "inputs_immutable": R("boolean",
                              note="the kind tried to mutate its input and "
                                   "was refused; measured, not asserted"),
    }))


# ----------------------------------------- H1/H0: the search inside the kind
register(Kind(
    kind="cegis_boolean_v1",
    params=frozenset({
        "target_truth_table", "grammar_version", "candidate_policy",
        "candidate_seed", "max_expr_size", "max_candidates",
        "oracle_call_cap", "vm_op_cap", "trace_bound", "vm_ticks",
        "case_ordering", "termination", "seed_probe_count", "shortfall_rule",
        "source_pack", "component_library"}),
    artifact_slots=frozenset({"source_pack", "component_library"}),
    optional_artifact_slots=frozenset({"source_pack", "component_library"}),
    implemented=True,
    owner="vivarium (kind contract) / proteus (Boolean semantics)",
    stateful=False,
    note="A bounded within-task CEGIS loop, SEALED INSIDE THE KIND. Every "
         "input that governs an adaptive choice is a hashed parameter: the "
         "candidate policy and its seed, the case ordering, the caps, the "
         "trace bound, the termination rule, and the two artifact slots. The "
         "generic runner sees a kind name and a result and never learns that "
         "a search happened (design C3).\n"
         "Proteus owns the semantics -- grammar, compiler, VM, independent "
         "truth-table oracle, ordered first witness. NOT is compiled as "
         "XOR x, ONE by their compiler; nothing here emits an opcode.\n"
         "BOTH SLOTS MAY BE null, and null is a DECLARED INPUT inside "
         "spec_hash rather than an omission. H0's four cells are four "
         "payloads differing in exactly those two positions, run by one "
         "solver runtime -- which is what makes them four cells of one "
         "experiment. A hand-built component library is an INSTRUMENT "
         "control and must be labelled as one by whoever issues it; this "
         "kind cannot tell an instrument library from a derived one and does "
         "not pretend to.\n"
         "solved requires FULL COVERAGE of all 8 assignments; no-witness is "
         "never solved; and budget exhaustion has three distinct statuses "
         "kept apart from EXHAUSTED_CANDIDATES, which means the declared "
         "space actually ran out.",
    result_schema={
        "status": R("string",
                    note="SOLVED | EXHAUSTED_CANDIDATES | BUDGET_CANDIDATES | "
                         "BUDGET_VM_OPS | BUDGET_ORACLE_CALLS"),
        "solved": R("boolean",
                    note="true only after all 8 assignments were expected AND "
                         "passed; never inferred from an absent witness"),
        "solution": R("string", required=False,
                      note="the solving expression as canonical JSON, or "
                           "absent"),
        "solution_size": R("integer", required=False),
        "candidates_tried": R("integer"),
        "candidates_invalid": R("integer",
                                note="compiled-refused; counted, never "
                                     "silently skipped"),
        "verifications": R("integer", note="exhaustive checks actually run"),
        "oracle_calls": R("integer"),
        "oracle_call_cap": R("integer"),
        "vm_ops": R("integer",
                    note="the resource the caps bind on, and the channel "
                         "through which a better constraint set pays"),
        "vm_op_cap": R("integer"),
        "constraints_seeded": R("integer", note="probes actually spent"),
        "constraints_final": R("integer"),
        "seed_probe_count": R("integer", note="the ALLOWANCE, echoed"),
        "seed_probe_shortfall": R("integer",
                                  note="allowance minus spend; a short pool "
                                       "is reported, never topped up from "
                                       "another source"),
        "seeded_from": R("string", note="source_pack | fresh_probe_allowance"),
        "source_pack_digest": R("string", required=False),
        "source_pack_items": R("integer"),
        "component_library_digest": R("string", required=False),
        "component_library_size": R("integer"),
        "coverage_required": R("integer"),
        "witnesses": R("vector", element="record", bounds=(0, 4096),
                       reductions=("count",),
                       note="ordered counterexamples, bounded by trace_bound"),
        "witness_truncated": R("boolean"),
        "target_truth_table": R("string"),
        "grammar_version": R("string"),
        "interface_version": R("string"),
        "library_version": R("string"),
    }))


# --------------------------------------------- Herakles's radius-1, wrapped
register(Kind(
    kind="eca_rule_eval_v1",
    params=frozenset({"rule_number", "n_cells", "steps"}),
    implemented=True,
    owner="herakles (library) / vivarium (wrapper)",
    stateful=False,
    note="A thin wrapper around herakles/eca (radius 1). The library owns the "
         "rule numbering, the neighbourhood order, the periodic ring and the "
         "definition of TERMINAL BEHAVIOUR -- the lattice after exactly "
         "`steps` updates over every one of the 2^n_cells initial "
         "configurations, not the trajectory.\n"
         "IT REPORTS THE OBSERVABLE, NOT A SCORE. Two rules with identical "
         "terminal behaviour are behaviourally indistinguishable and, in the "
         "library's own words, must not be counted as two tasks -- so the "
         "result is the behaviour digest and the equivalence class, which is "
         "what class_map_fixture.json is keyed to. Scoring a rule against a "
         "target would need a target and a metric, and neither exists in the "
         "library or in any handed-over spec; inventing them here would be "
         "Vivarium deciding what H5 measures. A scored variant is a NEW kind "
         "name, never a flag on this one.\n"
         "The seed is accepted and unused: the scope is exhaustive, so there "
         "is nothing to sample.",
    result_schema={
        "rule_number": R("integer"),
        "behaviour_digest": R("string",
                              note="the library's own observable digest; two "
                                   "rules agreeing here are one task"),
        "equivalence_class_members": R("vector", element="integer",
                                       bounds=(1, 256),
                                       reductions=("count",),
                                       note="every rule sharing this "
                                            "behaviour on THIS scope"),
        "equivalence_class_size": R("integer"),
        "is_class_representative": R("boolean",
                                     note="lowest-numbered member; a stable "
                                          "choice, not a claim of primacy"),
        "n_cells": R("integer"),
        "steps": R("integer"),
        "n_initial_configurations": R("integer"),
        "on_fixture_scope": R("boolean",
                              note="whether this payload's scope is the one "
                                   "class_map_fixture.json was computed over"),
        "fixture_class_agrees": R("boolean", required=False,
                                  note="absent off the fixture scope, where "
                                       "there is nothing to agree with"),
        "fixture_class_members": R("vector", element="integer",
                                   bounds=(1, 256), required=False,
                                   reductions=("count",)),
        "radius": R("integer", note="1, from the library"),
        "scored_against_a_target": R("boolean",
                                     note="always false; see the note above"),
    }))


def get(kind: str):
    return REGISTRY.get(kind)


def known() -> list:
    return sorted(REGISTRY)


def implemented() -> list:
    return sorted(k for k, v in REGISTRY.items() if v.implemented)


def admissible() -> list:
    """Kinds a NEW row may name. Excludes retired ones."""
    return sorted(k for k, v in REGISTRY.items() if not v.retired)


def retired() -> list:
    return sorted(k for k, v in REGISTRY.items() if v.retired)
