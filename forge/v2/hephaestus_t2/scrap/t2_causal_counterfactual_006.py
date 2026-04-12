import re
import zlib
from typing import Dict, List, Any, Optional, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    counterfactual_intervention,
    topological_sort,
    solve_constraints,
    expected_value,
    information_sufficiency,
    modus_ponens,
    temporal_order,
    modular_arithmetic,
    fencepost_count,
    parity_check,
    negate,
    pigeonhole_check,
    coin_flip_independence,
    bat_and_ball,
    all_but_n,
    direction_composition,
    check_transitivity,
    dag_traverse,
    track_beliefs,
    sally_anne_test,
    solve_sat,
    solve_linear_system,
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    detect_confounders,
    do_calculus,
    get_adjustment_set,
    compare_conditional_marginal,
    active_trails,
    map_query,
    find_dseparators,
    get_markov_blanket,
)
from forge.amino_acids.pysat_acids import (
    solve,
    detect_paradox,
    check_entailment,
    count_models,
    enumerate_models,
    extract_mus,
    is_valid,
    maxsat_solve,
    encode_exactly_k,
)
from forge.amino_acids.constraint_acids import (
    solve_first,
    solve_all,
    check_consistency,
    is_uniquely_solvable,
    count_solutions,
    find_conflicts,
)
from forge.amino_acids.nashpy_acids import (
    find_equilibria,
    is_dominated,
    best_response,
    find_dominant_strategy,
    compute_minimax,
    expected_payoff,
)


class ReasoningTool:
    """Evolutionary biology x pgmpy_acids - causal_counterfactual"""

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        # Phase 3: SCORE
        scored = self._score(candidates, reasoning_result)
        # Phase 4: CALIBRATE
        calibrated = self._calibrate(scored)
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract entities, values, causal relationships, and question from prompt."""
        lines = [line.strip() for line in prompt.split(".") if line.strip()]
        question = lines[-1] if lines else ""

        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
        entities = {}
        for line in lines:
            matches = re.findall(entity_pattern, line)
            for match in matches:
                if match not in entities and len(match.split()) <= 3:
                    entities[match] = {"values": [], "mentions": 0, "line": line}
                if match in entities:
                    entities[match]["mentions"] += 1

        # Find numerical values (percentages, rates, counts)
        value_pattern = r"(\d+(?:\.\d+)?)%?"
        for line in lines:
            numbers = re.findall(value_pattern, line)
            for num in numbers:
                # Associate with nearest entity
                for entity in entities:
                    if entity in line:
                        try:
                            val = float(num)
                            entities[entity]["values"].append(val)
                        except ValueError:
                            pass

        # Find causal language (causes, affects, leads to, influences)
        causal_edges = []
        causal_keywords = ["causes", "affects", "leads to", "influences", "determines", "impacts"]
        for line in lines:
            for keyword in causal_keywords:
                if keyword in line.lower():
                    # Try to extract subject and object
                    parts = line.lower().split(keyword)
                    if len(parts) >= 2:
                        # Find entities in each part
                        left_entities = [e for e in entities if e.lower() in parts[0]]
                        right_entities = [e for e in entities if e.lower() in parts[1]]
                        if left_entities and right_entities:
                            causal_edges.append((left_entities[0], right_entities[0]))

        # Find intervention language (if, would have, under, given)
        interventions = []
        intervention_keywords = ["if", "would have", "under", "given", "suppose", "intervene"]
        for line in lines:
            for keyword in intervention_keywords:
                if keyword in line.lower():
                    # Extract the intervention condition
                    for entity in entities:
                        if entity.lower() in line.lower():
                            interventions.append(entity)

        return {
            "entities": entities,
            "causal_edges": causal_edges,
            "interventions": interventions,
            "question": question,
            "raw_lines": lines,
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply evolutionary biology framework to compute counterfactual answer."""
        entities = structure["entities"]
        causal_edges = structure["causal_edges"]
        interventions = structure["interventions"]
        question = structure["question"]

        # === EVOLUTIONARY BIOLOGY FRAMEWORK ===
        # Model causal variables as "traits" that evolve under selection pressure.
        # Interventions are like environmental changes that alter trait fitness.
        # Counterfactuals are alternative evolutionary trajectories.

        # 1. Extract trait values (entity values) as fitness components
        trait_fitness = {}
        for entity, data in entities.items():
            values = data.get("values", [])
            if values:
                # Fitness = expected value of trait (higher is better)
                fitness_vals = [(1.0, v) for v in values]  # uniform weighting
                fitness = expected_value(fitness_vals)
                trait_fitness[entity] = fitness
            else:
                trait_fitness[entity] = 0.0

        # 2. Build causal DAG as evolutionary constraint network
        # Use topological_sort to find evolutionary ordering
        if causal_edges:
            try:
                evolutionary_order = topological_sort(causal_edges)
                if evolutionary_order is None:
                    evolutionary_order = list(entities.keys())
            except Exception:
                evolutionary_order = list(entities.keys())
        else:
            evolutionary_order = list(entities.keys())

        # 3. Apply amino acid: build Bayesian network for causal inference
        bn_model = None
        if causal_edges:
            try:
                # Build simple BN with binary nodes (0/1 based on fitness threshold)
                cpd_specs = {}
                for node in set([e[0] for e in causal_edges] + [e[1] for e in causal_edges]):
                    parents = [p for (p, c) in causal_edges if c == node]
                    if parents:
                        # Create simple CPD: if any parent is "high", child is likely high
                        cpd_specs[node] = {
                            "parents": parents,
                            "values": [[0.3, 0.7], [0.7, 0.3]],  # P(child|parents)
                        }
                bn_model = build_bn(causal_edges, cpd_specs)
            except Exception:
                bn_model = None

        # 4. Determine which entity is the target of the counterfactual question
        target_entity = None
        question_lower = question.lower()
        for entity in entities:
            if entity.lower() in question_lower:
                target_entity = entity
                break
        if not target_entity and entities:
            target_entity = list(entities.keys())[0]

        # 5. Compute counterfactual using evolutionary selection pressure
        # If there's an intervention mentioned, simulate its effect
        intervention_effect = None
        if interventions and target_entity:
            # Use counterfactual_intervention primitive
            try:
                # Create simple values dict from trait_fitness
                values_dict = {e: trait_fitness.get(e, 0.0) for e in entities}
                # Intervene on the first intervention entity
                intervene_node = interventions[0]
                # Set intervention value to alter fitness
                intervene_value = 0.0  # complete suppression
                cf_result = counterfactual_intervention(
                    causal_edges, values_dict, intervene_node, intervene_value
                )
                if cf_result and target_entity in cf_result:
                    intervention_effect = cf_result[target_entity]
            except Exception:
                pass

        # 6. Use amino acid: do_calculus to compute causal effect if BN exists
        causal_effect = None
        if bn_model and target_entity and interventions:
            try:
                # Compute P(target | do(intervention))
                effect = do_calculus(
                    bn_model,
                    target_vars=[target_entity],
                    do_vars={interventions[0]: 1},
                    evidence=None,
                )
                if effect:
                    causal_effect = effect.get(target_entity, 0.5)
            except Exception:
                pass

        # 7. Apply entropy to measure uncertainty in evolutionary outcome
        fitness_values = list(trait_fitness.values())
        if len(fitness_values) >= 2:
            # Normalize to probability distribution
            total = sum(fitness_values)
            if total > 0:
                probs = [v / total for v in fitness_values]
                evolutionary_uncertainty = entropy(probs)
            else:
                evolutionary_uncertainty = 1.0
        else:
            evolutionary_uncertainty = 0.0

        # 8. Determine answer based on evolutionary fitness and counterfactual
        computed_answer = None
        confidence = 0.5

        if intervention_effect is not None:
            # Compare original fitness vs counterfactual fitness
            original_fitness = trait_fitness.get(target_entity, 0.0)
            if intervention_effect < original_fitness:
                computed_answer = f"{target_entity} would be worse"
                confidence = 0.8
            elif intervention_effect > original_fitness:
                computed_answer = f"{target_entity} would be better"
                confidence = 0.8
            else:
                computed_answer = f"{target_entity} would be unchanged"
                confidence = 0.6
        elif causal_effect is not None:
            # Use do-calculus result
            if causal_effect > 0.5:
                computed_answer = f"{target_entity} would increase"
                confidence = 0.7
            else:
                computed_answer = f"{target_entity} would decrease"
                confidence = 0.7
        else:
            # Fallback: which entity has highest fitness?
            if trait_fitness:
                best_entity = max(trait_fitness.items(), key=lambda x: x[1])[0]
                computed_answer = best_entity
                confidence = 0.6
            else:
                computed_answer = "Unknown"
                confidence = 0.3

        # 9. Use confidence_from_agreement primitive
        # Create multiple scoring perspectives
        scores = []
        if trait_fitness:
            scores.append(max(trait_fitness.values()) / 100.0 if max(trait_fitness.values()) > 0 else 0.5)
        scores.append(1.0 - evolutionary_uncertainty)
        if intervention_effect is not None:
            scores.append(abs(intervention_effect) / 100.0 if abs(intervention_effect) > 0 else 0.5)
        if len(scores) >= 2:
            confidence = confidence_from_agreement(scores)
        else:
            confidence = max(confidence, 0.5)

        # 10. Use amino acid: detect_confounders to check for hidden variables
        confounders_detected = None
        if bn_model and len(causal_edges) >= 2:
            try:
                # Pick two connected variables
                if len(causal_edges) >= 1:
                    var_a, var_b = causal_edges[0]
                    confounders = detect_confounders(bn_model, var_a, var_b)
                    if confounders:
                        confounders_detected = list(confounders)
            except Exception:
                pass

        # If confounders detected, adjust answer
        if confounders_detected and computed_answer:
            computed_answer = f"{computed_answer} (confounded by {confounders_detected[0]})"
            confidence *= 0.9

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "target_entity": target_entity,
            "intervention_effect": intervention_effect,
            "causal_effect": causal_effect,
            "evolutionary_uncertainty": evolutionary_uncertainty,
            "confounders": confounders_detected,
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]

        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Fallback: NCD similarity
                ncd_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                score = ncd_score * confidence
            results.append({"candidate": candidate, "score": score, "confidence": confidence})
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored

        # Simple normalization
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            max_score = max(scores)
            for item in scored:
                item["score"] = item["score"] / max_score
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0