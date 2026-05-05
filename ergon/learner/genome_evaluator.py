"""ergon.learner.genome_evaluator — execute genome DAGs through real bindings.

Per pivot/ergon_learner_proposal_v8.md S4 + Iteration 2 of MVP build:

The Ergon engine produces typed-DAG genomes. Techne's BindEvalKernelV2
(commit b0355b1d) provides BIND/EVAL primitives that route through
CLAIM/FALSIFY/GATE/PROMOTE. To integrate the two, we BIND a single
"execute_genome" wrapper function once at engine startup; every episode
EVALs that binding with the genome's serialized form as args.

This keeps the substrate-discipline contract:
  - Each genome execution mints a CLAIM
  - bind_validation fires once at BIND time (validates the wrapper)
  - eval_validation fires per EVAL (validates the genome execution)
  - Successful EVAL produces an Evaluation symbol with provenance back
    to the binding

The genome execution itself is intentionally MVP-stub at this layer —
walks the DAG, calls each atom's callable_ref via importlib, threads
ref-bindings through. v0.5 swaps to actual prometheus_math.arsenal
calls; this MVP layer is where we validate the integration end-to-end
without actually running 2,800 callables.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from ergon.learner.genome import Genome, NodeRef


# ---------------------------------------------------------------------------
# Genome execution (MVP-stub)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GenomeEvaluationResult:
    """Output of one genome execution.

    Carries the load-bearing fields the engine needs:
    output_magnitude, output_canonicalizer_subclass, kill_verdicts,
    plus elapsed and provenance metadata.
    """
    output_magnitude: float
    output_canonicalizer_subclass: str
    output_canonical_form_distance: float
    kill_path_verdicts: Dict[str, str]
    output_repr: str
    elapsed_seconds: float
    success: bool
    error_repr: str = ""


def execute_genome_serialized(
    genome_json: str,
    promote_rate: float = 0.0001,
    seed: int = 0,
) -> Dict[str, Any]:
    """Execute a serialized genome and return evaluation outputs as a dict.

    This is the function BindEvalKernelV2 binds — the genome execution
    wrapper. Takes a JSON-serialized Genome dict (from Genome.to_dict)
    and returns a dict the engine can convert to GenomeEvaluationResult.

    At MVP scope: doesn't actually call arsenal callables (those need
    real backends). Instead computes deterministic-from-content outputs:
      magnitude: log-uniform across [10^0, 10^14] from sha256
      canonicalizer_subclass: deterministic from sha256
      canonical_form_distance: log-uniform across [1e-4, 1e2] from sha256
      kill_verdicts: BLOCK most often; rare CLEAR matching promote_rate

    v0.5 swaps this stub for a real DAG-walker that calls
    prometheus_math.arsenal_meta atoms via importlib + executes their
    arg-bindings + threads ref-outputs through the DAG.
    """
    t_start = time.time()

    try:
        data = json.loads(genome_json)
        content_hash = data.get("content_hash", "")
        nodes = data.get("nodes", [])
        operator_class = data.get("mutation_operator_class", "structural")
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        return {
            "output_magnitude": 0.0,
            "output_canonicalizer_subclass": "group_quotient",
            "output_canonical_form_distance": 1.0,
            "kill_path_verdicts": {"F1": "BLOCK", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"},
            "output_repr": f"genome_parse_error: {type(e).__name__}",
            "elapsed_seconds": time.time() - t_start,
            "success": False,
            "error_repr": f"{type(e).__name__}: {e}",
        }

    # Deterministic outputs from content_hash
    digest = hashlib.sha256(content_hash.encode()).hexdigest()
    h_mag = int(digest[:16], 16)
    h_sub = int(digest[16:24], 16)
    h_dist = int(digest[24:40], 16)
    h_verdict = int(digest[40:48], 16)

    frac_mag = h_mag / (16 ** 16)
    log_magnitude = frac_mag * 14.0
    magnitude = 10.0 ** log_magnitude

    subclass_idx = h_sub % 4
    subclass = ("group_quotient", "partition_refinement",
                "ideal_reduction", "variety_fingerprint")[subclass_idx]

    frac_dist = h_dist / (16 ** 16)
    log_dist = -4.0 + frac_dist * 6.0
    distance = 10.0 ** log_dist

    # Kill verdicts: per-operator-tuned promote rate
    per_op_multipliers = {
        "structural": 1.2, "symbolic": 1.0, "uniform": 0.3,
        "structured_null": 0.5, "anti_prior": 0.4,
        "neural": 1.5, "external_llm": 1.5,
    }
    rate = promote_rate * per_op_multipliers.get(operator_class, 1.0)
    # Use h_verdict as the random-uniform draw (deterministic)
    frac_verdict = h_verdict / (16 ** 8)
    if frac_verdict < rate:
        verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
    else:
        # Pick a kill-test by hash
        block_idx = (h_verdict // (16 ** 4)) % 4
        block_test = ("F1", "F6", "F9", "F11")[block_idx]
        verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
        verdicts[block_test] = "BLOCK"

    return {
        "output_magnitude": magnitude,
        "output_canonicalizer_subclass": subclass,
        "output_canonical_form_distance": distance,
        "kill_path_verdicts": verdicts,
        "output_repr": f"genome[{len(nodes)} atoms, op={operator_class}, mag~{magnitude:.2e}]",
        "elapsed_seconds": time.time() - t_start,
        "success": True,
        "error_repr": "",
    }


# ---------------------------------------------------------------------------
# BindEvalIntegration — wrapper around BindEvalKernelV2 for engine use
# ---------------------------------------------------------------------------


class BindEvalIntegration:
    """Adapter: routes genome evaluations through BindEvalKernelV2.

    Construction:
      - Spins up an in-memory SigmaKernel
      - Mints a bootstrap capability + a BIND capability
      - Pre-BINDs the execute_genome_serialized wrapper once

    Per-genome evaluation:
      - Mints an EVAL capability
      - Calls EVAL(binding, args=[genome_json])
      - Parses output_repr (which the kernel stores) to recover the
        evaluation dict
      - Returns GenomeEvaluationResult

    Note: at MVP scope this is the integration scaffolding. Each EVAL
    is a real CLAIM/FALSIFY/PROMOTE round-trip through the kernel.
    Cost: roughly 1-3ms per EVAL via in-process kernel; vs <0.1ms via
    the MVPSubstrateEvaluator stub. The substrate-discipline tradeoff
    is acceptable for substrate-grade pilots.
    """

    def __init__(self, promote_rate: float = 0.0001):
        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension, CostModel

        self.promote_rate = promote_rate
        self.kernel = SigmaKernel(":memory:")
        self.ext = BindEvalExtension(self.kernel)

        # Pre-BIND the genome executor
        bind_cap = self.kernel.mint_capability("ErgonGenomeBindCap")
        cost_model = CostModel(
            max_seconds=2.0,
            max_memory_mb=512,
            max_oracle_calls=0,
        )
        self.binding = self.ext.BIND(
            callable_ref="ergon.learner.genome_evaluator:execute_genome_serialized",
            cost_model=cost_model,
            postconditions=[
                "output_magnitude is float",
                "output_canonicalizer_subclass in {group_quotient, "
                "partition_refinement, ideal_reduction, variety_fingerprint}",
                "kill_path_verdicts contains F1, F6, F9, F11 keys",
            ],
            authority_refs=[
                "Techne BindEvalKernelV2 commit b0355b1d",
                "Ergon Trial 2 production pilot 1K x 5 seeds",
            ],
            cap=bind_cap,
            name="ergon_execute_genome",
        )

    def evaluate(self, genome: Genome) -> GenomeEvaluationResult:
        """Run one genome evaluation through BIND/EVAL pipeline.

        Each call mints an EVAL capability + runs the bound function +
        recovers the output. Output is serialized in the kernel's
        Evaluation symbol's def_blob; we re-read it from the binding
        on the way out.
        """
        eval_cap = self.kernel.mint_capability("ErgonGenomeEvalCap")
        genome_json = json.dumps(genome.to_dict())

        try:
            evaluation = self.ext.EVAL(
                binding_name=self.binding.symbol.name,
                binding_version=self.binding.symbol.version,
                args=[genome_json],
                kwargs={"promote_rate": self.promote_rate},
                cap=eval_cap,
            )
        except Exception as e:
            return GenomeEvaluationResult(
                output_magnitude=0.0,
                output_canonicalizer_subclass="group_quotient",
                output_canonical_form_distance=1.0,
                kill_path_verdicts={"F1": "BLOCK", "F6": "CLEAR",
                                    "F9": "CLEAR", "F11": "CLEAR"},
                output_repr=f"eval_error: {type(e).__name__}",
                elapsed_seconds=0.0,
                success=False,
                error_repr=f"{type(e).__name__}: {e}",
            )

        # Parse output dict from the evaluation's output_repr.
        # The kernel stores repr(output) which for our dict produces
        # something like "{'output_magnitude': 1.23e+05, ...}".
        # We use eval() with a guard since we control the output shape.
        output_dict = self._parse_evaluation_output(evaluation.output_repr)

        return GenomeEvaluationResult(
            output_magnitude=output_dict.get("output_magnitude", 0.0),
            output_canonicalizer_subclass=output_dict.get(
                "output_canonicalizer_subclass", "group_quotient"
            ),
            output_canonical_form_distance=output_dict.get(
                "output_canonical_form_distance", 1.0
            ),
            kill_path_verdicts=output_dict.get("kill_path_verdicts", {}),
            output_repr=evaluation.output_repr,
            elapsed_seconds=evaluation.actual_cost.get("elapsed_seconds", 0.0),
            success=evaluation.success,
            error_repr=evaluation.error_repr,
        )

    def _parse_evaluation_output(self, output_repr: str) -> Dict[str, Any]:
        """Recover the dict from the kernel-stored repr.

        execute_genome_serialized returns a dict; the kernel calls
        repr() on it which produces a Python-dict string. We use ast.
        literal_eval (safer than eval) to recover.
        """
        import ast
        try:
            return ast.literal_eval(output_repr)
        except (ValueError, SyntaxError):
            return {}


# ---------------------------------------------------------------------------
# BindEvalEvaluator — drop-in replacement for MVPSubstrateEvaluator
# ---------------------------------------------------------------------------


class BindEvalEvaluator:
    """Drop-in replacement for MVPSubstrateEvaluator that uses BindEvalIntegration.

    The engine accepts any object with the duck-typed interface:
      - evaluate(genome) -> dict (kill_path_verdicts)
      - evaluate_magnitude(genome) -> float
      - evaluate_canonicalizer_subclass(genome) -> str
      - evaluate_canonical_form_distance(genome) -> float

    BindEvalEvaluator caches the GenomeEvaluationResult per content_hash
    so the engine's separate evaluate_magnitude / evaluate_canonicalizer_
    subclass calls don't redundantly EVAL through the kernel.
    """

    def __init__(self, promote_rate: float = 0.0001):
        self._integration = BindEvalIntegration(promote_rate=promote_rate)
        self._cache: Dict[str, GenomeEvaluationResult] = {}

    def _get_or_evaluate(self, genome: Genome) -> GenomeEvaluationResult:
        ch = genome.content_hash()
        if ch not in self._cache:
            self._cache[ch] = self._integration.evaluate(genome)
        return self._cache[ch]

    def evaluate(self, genome: Genome) -> Dict[str, str]:
        return self._get_or_evaluate(genome).kill_path_verdicts

    def evaluate_magnitude(self, genome: Genome) -> float:
        return self._get_or_evaluate(genome).output_magnitude

    def evaluate_canonicalizer_subclass(self, genome: Genome) -> str:
        return self._get_or_evaluate(genome).output_canonicalizer_subclass

    def evaluate_canonical_form_distance(self, genome: Genome) -> float:
        return self._get_or_evaluate(genome).output_canonical_form_distance


# ---------------------------------------------------------------------------
# Obstruction-domain executor — Iter 14 / Task #64
# ---------------------------------------------------------------------------
#
# The execute_genome_serialized stub above produces deterministic-from-hash
# outputs (no actual predicate evaluation). For the predicate-discovery
# trial we need a real domain executor that:
#   1. Parses the genome,
#   2. Interprets it as a predicate (via genome_to_predicate),
#   3. Evaluates that predicate against OBSTRUCTION_CORPUS,
#   4. Reports lift / match-size / substrate-pass through the kernel.
#
# This routes ALL evaluations through BindEvalKernelV2's CLAIM/EVAL/GATE/
# PROMOTE — the substrate path Ergon was built to integrate with.


def execute_obstruction_genome_serialized(
    genome_json: str,
    promote_rate: float = 0.0001,  # unused; kept for BIND signature compat
    seed: int = 0,                 # unused; obstruction is deterministic
) -> Dict[str, Any]:
    """Obstruction-corpus aware genome executor.

    The genome's atoms are parsed as `predicate:<feature>=<value>`
    conjuncts (per ergon.learner.operators.predicate_symbolic). The
    resulting predicate is evaluated against OBSTRUCTION_CORPUS via
    prometheus_math.obstruction_env.evaluate_predicate.

    Substrate-pass criterion (matches HardenedObstructionEvaluator):
      - lift >= 1.5
      - match_group_size >= 3 (prevents single-record-overlap inflation)
    """
    t_start = time.time()

    try:
        from prometheus_math._obstruction_corpus import (
            OBSTRUCTION_CORPUS, OBSTRUCTION_SIGNATURE,
        )
        from prometheus_math.obstruction_env import evaluate_predicate
        from ergon.learner.trials.trial_3_obstruction_smoke import genome_to_predicate
    except ImportError as e:
        return {
            "output_magnitude": 0.0,
            "output_canonicalizer_subclass": "group_quotient",
            "output_canonical_form_distance": 1.0,
            "kill_path_verdicts": {"F1": "BLOCK", "F6": "CLEAR",
                                   "F9": "CLEAR", "F11": "CLEAR"},
            "output_repr": f"import_error: {type(e).__name__}",
            "elapsed_seconds": time.time() - t_start,
            "success": False,
            "error_repr": f"{type(e).__name__}: {e}",
        }

    try:
        data = json.loads(genome_json)
    except (json.JSONDecodeError, TypeError) as e:
        return {
            "output_magnitude": 0.0,
            "output_canonicalizer_subclass": "group_quotient",
            "output_canonical_form_distance": 1.0,
            "kill_path_verdicts": {"F1": "BLOCK", "F6": "CLEAR",
                                   "F9": "CLEAR", "F11": "CLEAR"},
            "output_repr": f"json_error: {type(e).__name__}",
            "elapsed_seconds": time.time() - t_start,
            "success": False,
            "error_repr": f"{type(e).__name__}: {e}",
        }

    genome = Genome.from_dict(data)
    pred = genome_to_predicate(genome)
    pred_eval = evaluate_predicate(pred, OBSTRUCTION_CORPUS)
    lift = pred_eval["lift"]
    match_size = pred_eval["match_group_size"]

    LIFT_PROMOTE = 1.5
    MIN_MATCH = 3
    passes = (lift >= LIFT_PROMOTE and match_size >= MIN_MATCH)

    feats = sorted(pred.keys())
    if not feats:
        subclass = "group_quotient"
    elif "has_diag_neg" in feats or "has_diag_pos" in feats:
        subclass = "variety_fingerprint"
    elif any(f.startswith("neg_") for f in feats):
        subclass = "ideal_reduction"
    else:
        subclass = "partition_refinement"

    sig_distance = 0.0
    for k, v in OBSTRUCTION_SIGNATURE.items():
        if pred.get(k) != v:
            sig_distance += 1
    for k in pred.keys():
        if k not in OBSTRUCTION_SIGNATURE:
            sig_distance += 0.5

    if passes:
        verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
    else:
        block_idx = (hash(genome_json) >> 4) % 4
        block_test = ("F1", "F6", "F9", "F11")[block_idx]
        verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
        verdicts[block_test] = "BLOCK"

    magnitude = 10.0 ** (math.log10(1 + lift) * 7)

    return {
        "output_magnitude": magnitude,
        "output_canonicalizer_subclass": subclass,
        "output_canonical_form_distance": sig_distance,
        "kill_path_verdicts": verdicts,
        "obstruction_lift": lift,
        "obstruction_match_size": match_size,
        "obstruction_predicate": dict(pred),
        "substrate_pass": passes,
        "output_repr": f"obs_pred[lift={lift:.2f},m={match_size}]",
        "elapsed_seconds": time.time() - t_start,
        "success": True,
        "error_repr": "",
    }


class ObstructionBindEvalIntegration(BindEvalIntegration):
    """BindEvalIntegration wired to the obstruction-domain executor.

    Same kernel/CLAIM/EVAL pipeline as the parent class, but BINDs
    `execute_obstruction_genome_serialized` instead of the content-hash
    stub. Used by ObstructionBindEvalEvaluator below.
    """

    def __init__(self, promote_rate: float = 0.0001):
        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension, CostModel

        self.promote_rate = promote_rate
        self.kernel = SigmaKernel(":memory:")
        self.ext = BindEvalExtension(self.kernel)

        bind_cap = self.kernel.mint_capability("ErgonObstructionBindCap")
        cost_model = CostModel(
            max_seconds=2.0,
            max_memory_mb=512,
            max_oracle_calls=0,
        )
        self.binding = self.ext.BIND(
            callable_ref=(
                "ergon.learner.genome_evaluator:"
                "execute_obstruction_genome_serialized"
            ),
            cost_model=cost_model,
            postconditions=[
                "output_magnitude is float",
                "obstruction_lift is float",
                "obstruction_match_size is int",
                "kill_path_verdicts contains F1, F6, F9, F11 keys",
            ],
            authority_refs=[
                "Ergon Iter 14 — domain-aware BindEval pilot for obstruction",
                "Ergon Iter 7-13 — predicate discovery on OBSTRUCTION_CORPUS",
            ],
            cap=bind_cap,
            name="ergon_execute_obstruction_genome",
        )


class ObstructionBindEvalEvaluator(BindEvalEvaluator):
    """Drop-in obstruction evaluator routed through BindEvalKernelV2.

    Adds obstruction-specific accessors so the predicate trial doesn't
    need to re-evaluate the predicate in-process; everything comes from
    the kernel-routed evaluation cache.
    """

    def __init__(self, promote_rate: float = 0.0001):
        self._integration = ObstructionBindEvalIntegration(promote_rate=promote_rate)
        self._cache: Dict[str, GenomeEvaluationResult] = {}
        self._aux_cache: Dict[str, Dict[str, Any]] = {}

    def _get_or_evaluate(self, genome: Genome) -> GenomeEvaluationResult:
        ch = genome.content_hash()
        if ch not in self._cache:
            result = self._integration.evaluate(genome)
            self._cache[ch] = result
            # Also pull through the obstruction-specific fields by
            # re-parsing output_repr directly (works because
            # execute_obstruction_genome_serialized returns a dict whose
            # repr is parsed back via ast.literal_eval upstream).
            try:
                import ast
                full = ast.literal_eval(result.output_repr) if result.output_repr.startswith("{") else {}
            except (ValueError, SyntaxError):
                full = {}
            self._aux_cache[ch] = full
        return self._cache[ch]

    def evaluate_obstruction(self, genome: Genome) -> Dict[str, Any]:
        """Return the obstruction-specific evaluation dict for this genome.

        Re-runs the bound function in-process to recover the full output
        dict (the kernel-stored output_repr is the truncated label, not
        the dict itself). This is fine because execute_obstruction_genome_
        serialized is deterministic in genome content.
        """
        ch = genome.content_hash()
        # Cache directly to avoid double-evaluation
        if ch in self._aux_cache and self._aux_cache[ch]:
            return self._aux_cache[ch]
        # The kernel evaluation is the substrate-grade path; the in-process
        # call recovers the full dict for trial-side analysis.
        out = execute_obstruction_genome_serialized(
            json.dumps(genome.to_dict()),
            promote_rate=self._integration.promote_rate,
        )
        self._aux_cache[ch] = out
        return out
