import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_linear_system,
    topological_sort,
    expected_value
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    compare_conditional_marginal,
    detect_confounders
)


class ReasoningTool:
    """Climate Modeling x Bayesian Networks - Simpson Paradox Detection"""

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

    # ========== PHASE 1: EXTRACT ==========
    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt to find entities, subgroups, rates, and the question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""

        # Find entity names (capitalized multi-word phrases that appear before rates)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        entities = {}
        subgroups = {}
        aggregated_rates = {}
        subgroup_rates = {}

        current_entity = None
        current_subgroup = None

        for line in lines:
            # Look for percentages
            percentages = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            if not percentages:
                continue

            # Check if line mentions an entity (hospital, drug, etc.)
            found_entities = re.findall(entity_pattern, line)
            for ent in found_entities:
                if ent.lower() not in ['the', 'and', 'for', 'with', 'that', 'which']:
                    if ent not in entities:
                        entities[ent] = {"mentions": 0, "rates": []}
                    entities[ent]["mentions"] += 1
                    current_entity = ent

            # Check for subgroup indicators (e.g., "men", "women", "severe", "mild")
            subgroup_keywords = ['men', 'women', 'male', 'female', 'severe', 'mild',
                                 'young', 'old', 'group', 'category', 'type']
            for word in subgroup_keywords:
                if word in line.lower():
                    current_subgroup = word
                    if current_subgroup not in subgroups:
                        subgroups[current_subgroup] = {"entities": set()}
                    if current_entity:
                        subgroups[current_subgroup]["entities"].add(current_entity)

            # Store rates
            rates = [float(p) / 100.0 for p in percentages]
            if current_entity:
                entities[current_entity]["rates"].extend(rates)
                if len(rates) == 1:
                    # Likely aggregated rate
                    if current_entity not in aggregated_rates:
                        aggregated_rates[current_entity] = []
                    aggregated_rates[current_entity].append(rates[0])
                elif len(rates) > 1:
                    # Likely subgroup rates
                    if current_entity not in subgroup_rates:
                        subgroup_rates[current_entity] = {}
                    if current_subgroup:
                        subgroup_rates[current_entity][current_subgroup] = rates
                    else:
                        # Store as generic subgroups
                        for i, rate in enumerate(rates):
                            subgroup_key = f"subgroup_{i}"
                            if subgroup_key not in subgroup_rates[current_entity]:
                                subgroup_rates[current_entity][subgroup_key] = []
                            subgroup_rates[current_entity][subgroup_key].append(rate)

        # Clean up entities with too few mentions
        final_entities = {k: v for k, v in entities.items() if v["mentions"] >= 2}

        return {
            "entities": final_entities,
            "subgroups": subgroups,
            "aggregated_rates": aggregated_rates,
            "subgroup_rates": subgroup_rates,
            "question": question,
            "raw": prompt
        }

    # ========== PHASE 2: REASON ==========
    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply climate modeling concepts to detect Simpson's paradox."""
        entities = structure["entities"]
        aggregated_rates = structure["aggregated_rates"]
        subgroup_rates = structure["subgroup_rates"]
        question = structure["question"]

        # Climate modeling scaffold: treat entities as climate models,
        # subgroups as different forcing scenarios, rates as temperature predictions.
        # Simpson's paradox is like model disagreement across scenarios.

        # Step 1: Build a simple Bayesian network for causal analysis
        # Use T1 primitive: topological_sort to order variables
        edges = []
        if len(entities) >= 2:
            entity_list = list(entities.keys())
            # Create a simple chain: Subgroup -> Entity -> Outcome
            for i in range(len(entity_list) - 1):
                edges.append((f"Subgroup_{i}", entity_list[i]))
                edges.append((entity_list[i], "Outcome"))
        
        topological_order = []
        if edges:
            topo_result = topological_sort(edges)
            if topo_result is not None:
                topological_order = topo_result

        # Step 2: Use amino acid to detect confounders (climate forcing variables)
        confounders_detected = []
        if len(entities) >= 2:
            entity_names = list(entities.keys())
            try:
                # Build a minimal BN for detection
                test_edges = [(entity_names[0], "Outcome"), (entity_names[1], "Outcome")]
                if subgroup_rates:
                    # Add subgroup as common cause
                    subgroup_key = list(subgroup_rates.get(entity_names[0], {}).keys())[0] if entity_names[0] in subgroup_rates else "Subgroup"
                    test_edges.append((subgroup_key, entity_names[0]))
                    test_edges.append((subgroup_key, entity_names[1]))
                
                model = build_bn(test_edges)
                if model is not None:
                    conf_result = detect_confounders(model, entity_names[0], entity_names[1])
                    if conf_result is not None:
                        confounders_detected = list(conf_result)
            except Exception:
                confounders_detected = []

        # Step 3: Compare aggregated vs subgroup trends (climate model ensemble analysis)
        paradox_detected = False
        best_entity = None
        confidence = 0.5

        if len(aggregated_rates) >= 2 and subgroup_rates:
            # Use T1 primitive: expected_value to compute weighted averages
            entity_scores = {}
            for entity, rates in aggregated_rates.items():
                if rates:
                    # Climate modeling: treat each rate as a model prediction
                    # Compute ensemble mean as aggregated score
                    predictions = [(1.0/len(rates), r) for r in rates]
                    agg_score = expected_value(predictions)
                    if agg_score is not None:
                        entity_scores[entity] = {"aggregated": agg_score, "subgroup_avg": 0.0}

            # Compute subgroup-adjusted scores
            for entity, subgroups_dict in subgroup_rates.items():
                if entity in entity_scores:
                    subgroup_values = []
                    for subgroup, rates in subgroups_dict.items():
                        if rates:
                            # Climate modeling: different forcing scenarios
                            predictions = [(1.0/len(rates), r) for r in rates]
                            scenario_mean = expected_value(predictions)
                            if scenario_mean is not None:
                                subgroup_values.append(scenario_mean)
                    
                    if subgroup_values:
                        # Use T1 primitive: entropy to measure uncertainty across scenarios
                        probs = [v/sum(subgroup_values) for v in subgroup_values] if sum(subgroup_values) > 0 else [1.0/len(subgroup_values)]*len(subgroup_values)
                        scenario_entropy = entropy(probs)
                        if scenario_entropy is not None:
                            # High entropy = high disagreement across scenarios (paradox indicator)
                            subgroup_avg = sum(subgroup_values) / len(subgroup_values)
                            entity_scores[entity]["subgroup_avg"] = subgroup_avg
                            entity_scores[entity]["entropy"] = scenario_entropy

            # Check for reversal (Simpson's paradox)
            if len(entity_scores) >= 2:
                entities_sorted_agg = sorted(entity_scores.items(), key=lambda x: x[1]["aggregated"], reverse=True)
                entities_sorted_sub = sorted(entity_scores.items(), key=lambda x: x[1]["subgroup_avg"], reverse=True)
                
                if entities_sorted_agg and entities_sorted_sub:
                    top_agg = entities_sorted_agg[0][0]
                    top_sub = entities_sorted_sub[0][0]
                    
                    if top_agg != top_sub:
                        paradox_detected = True
                        # Climate modeling: when scenario-adjusted ranking differs from ensemble mean,
                        # trust the scenario-adjusted result (like downscaling climate models)
                        best_entity = top_sub
                    else:
                        best_entity = top_agg

                    # Use T1 primitive: confidence_from_agreement
                    scores_list = []
                    for entity, data in entity_scores.items():
                        if "aggregated" in data and "subgroup_avg" in data:
                            # Agreement between aggregated and subgroup-adjusted
                            agreement = 1.0 - abs(data["aggregated"] - data["subgroup_avg"])
                            scores_list.append(agreement)
                    
                    if scores_list:
                        conf_result = confidence_from_agreement(scores_list)
                        if conf_result is not None:
                            confidence = conf_result

        # Step 4: Bayesian update of confidence based on paradox detection
        # Climate modeling: treat paradox detection as new evidence
        prior = confidence
        likelihood = 0.8 if paradox_detected else 0.5
        updated_confidence = bayesian_update(prior, likelihood, false_positive=0.2)
        if updated_confidence is not None:
            confidence = updated_confidence

        # Step 5: Determine final answer
        computed_answer = None
        if best_entity:
            computed_answer = best_entity
        elif entities:
            # Fallback: entity with most mentions
            computed_answer = max(entities.items(), key=lambda x: x[1]["mentions"])[0]
        else:
            # Last resort: extract from question
            entity_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', question)
            if entity_match:
                computed_answer = entity_match.group(1)
            else:
                computed_answer = "Unknown"

        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "paradox_detected": paradox_detected,
            "confounders": confounders_detected,
            "topological_order": topological_order,
            "reasoning": f"Climate modeling analysis: {'Paradox detected' if paradox_detected else 'No paradox'}, confounders={confounders_detected}"
        }

    # ========== PHASE 3: SCORE ==========
    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]

        results = []
        for candidate in candidates:
            # Primary: exact or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    # ========== PHASE 4: CALIBRATE ==========
    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple calibration: normalize scores to [0,1] range."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            normalized = [s / max(scores) for s in scores]
        else:
            normalized = [0.0] * len(scores)
        
        for i, item in enumerate(scored):
            item["score"] = normalized[i]
        
        return scored

    # ========== UTILITY ==========
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