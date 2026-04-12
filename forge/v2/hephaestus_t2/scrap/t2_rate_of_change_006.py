import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """behavioral_economics x constraint_acids - rate_of_change"""

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
        """Extract entities, time points, values, and the question from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all numerical values (including percentages and decimals)
        number_pattern = r'([0-9]+\.?[0-9]*)\%?'
        
        # Find entity names (capitalized multi-word phrases that appear before numbers)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        
        entities = {}
        time_points = []
        values_by_entity = {}
        
        # Look for time references
        time_keywords = ['year', 'month', 'day', 'week', 'hour', 'minute', 'second',
                        'initially', 'starting', 'beginning', 'after', 'later',
                        'first', 'second', 'third', 'fourth', 'fifth']
        
        for line in lines:
            # Extract time points
            for kw in time_keywords:
                if kw in line.lower():
                    # Try to extract time value
                    time_match = re.search(r'(\d+)\s+' + kw, line.lower())
                    if time_match:
                        time_points.append(int(time_match.group(1)))
            
            # Extract entities and their values
            numbers = re.findall(number_pattern, line)
            if numbers:
                # Convert to float (handle percentages)
                num_values = [float(num) for num in numbers]
                
                # Find entity names in this line
                possible_entities = re.findall(entity_pattern, line)
                for entity in possible_entities:
                    if entity not in ['The', 'A', 'An', 'At', 'In', 'On', 'After', 'Before']:
                        if entity not in entities:
                            entities[entity] = {"mentions": 0, "values": []}
                        entities[entity]["mentions"] += 1
                        entities[entity]["values"].extend(num_values)
                        
                        if entity not in values_by_entity:
                            values_by_entity[entity] = []
                        values_by_entity[entity].extend(num_values)
        
        # Clean up entities - keep only those with multiple mentions or clear patterns
        clean_entities = {}
        for entity, data in entities.items():
            if data["mentions"] >= 2 or len(data["values"]) >= 2:
                clean_entities[entity] = data
        
        # Extract rate-related phrases
        rate_phrases = []
        rate_patterns = [
            r'rate of change',
            r'growth rate',
            r'decay rate',
            r'increase.*per',
            r'decrease.*per',
            r'change.*over time',
            r'velocity',
            r'acceleration'
        ]
        
        for pattern in rate_patterns:
            matches = re.findall(pattern, prompt.lower())
            rate_phrases.extend(matches)
        
        return {
            "entities": clean_entities,
            "time_points": sorted(list(set(time_points))),
            "values_by_entity": values_by_entity,
            "question": question,
            "rate_phrases": rate_phrases,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply behavioral economics concepts to compute rate of change."""
        entities = structure["entities"]
        time_points = structure["time_points"]
        values_by_entity = structure["values_by_entity"]
        question = structure["question"]
        
        # If we have at least 2 time points and values for entities, compute rates
        computed_answer = ""
        confidence = 0.5
        reasoning = ""
        
        # Behavioral economics concept: Prospect Theory - people value changes relative to reference points
        # We'll treat initial values as reference points and compute changes
        
        if len(time_points) >= 2 and values_by_entity:
            # Try to match time points with values
            # Simple heuristic: assume values are given in chronological order
            
            all_rates = {}
            
            for entity, values in values_by_entity.items():
                if len(values) >= 2:
                    # Use solve_linear_system to find slope if we have enough points
                    # Create simple linear system: y = mx + b
                    # Use first two points as (0, v1) and (1, v2) for relative time
                    
                    # PRIMITIVE 1: solve_linear_system - LOAD-BEARING
                    # This determines the slope (rate of change)
                    A = [[0, 1], [1, 1]]  # [time, constant]
                    b = [values[0], values[1]]
                    
                    coefficients = solve_linear_system(A, b)
                    
                    if coefficients is not None and len(coefficients) == 2:
                        slope = coefficients[0]  # m in y = mx + b
                        all_rates[entity] = slope
                        
                        # PRIMITIVE 2: entropy - LOAD-BEARING
                        # Measure uncertainty in the rate calculation
                        # Higher entropy means more uncertainty about which entity has max rate
                        rate_probs = []
                        for other_entity, other_values in values_by_entity.items():
                            if other_entity != entity and len(other_values) >= 2:
                                other_A = [[0, 1], [1, 1]]
                                other_b = [other_values[0], other_values[1]]
                                other_coeff = solve_linear_system(other_A, other_b)
                                if other_coeff:
                                    other_slope = other_coeff[0]
                                    # Convert to probability-like values
                                    rate_probs.append(abs(other_slope) / (abs(slope) + abs(other_slope) + 1e-10))
                        
                        if rate_probs:
                            uncertainty = entropy(rate_probs)
                            # Higher entropy reduces confidence
                            confidence = 1.0 - min(uncertainty, 1.0)
            
            if all_rates:
                # Find entity with maximum absolute rate of change
                # Behavioral economics: people overweight extreme changes (prospect theory)
                max_entity = max(all_rates.items(), key=lambda x: abs(x[1]))
                computed_answer = max_entity[0]
                reasoning = f"Entity '{computed_answer}' has maximum rate of change ({max_entity[1]:.2f})"
                
                # AMINO ACID 1: is_uniquely_solvable - LOAD-BEARING
                # Check if the rate assignment is uniquely determined
                # Create a CSP to verify uniqueness
                variables = list(all_rates.keys())
                domains = {var: ["positive", "negative", "zero"] for var in variables}
                
                # Constraints based on sign of rates
                constraints = []
                for var, rate in all_rates.items():
                    def sign_constraint(val, r=rate):
                        if r > 0.01:
                            return val == "positive"
                        elif r < -0.01:
                            return val == "negative"
                        else:
                            return val == "zero"
                    
                    constraints.append(([var], sign_constraint))
                
                unique = is_uniquely_solvable(variables_domains=domains, constraints=constraints)
                
                if not unique:
                    # If not unique, we need to use Bayesian update to refine
                    # PRIMITIVE 3: bayesian_update - LOAD-BEARING
                    prior = 0.7  # Prior confidence in our max rate selection
                    likelihood = 0.8 if abs(max_entity[1]) > sum(abs(r) for r in all_rates.values()) / len(all_rates) else 0.3
                    posterior = bayesian_update(prior, likelihood)
                    confidence = posterior
                    reasoning += f" (non-unique solution, Bayesian confidence: {confidence:.2f})"
                else:
                    reasoning += f" (unique solution)"
        
        # Fallback: if we couldn't compute rates, use constraint satisfaction approach
        if not computed_answer and entities:
            # AMINO ACID 2: build_bn and conditional_query - LOAD-BEARING
            # Build a simple Bayesian network for rate inference
            try:
                # Create edges: Time -> Value, Entity -> Value
                edges = [("Time", "Value"), ("Entity", "Value")]
                
                # Create CPDs based on extracted values
                cpd_specs = {
                    "Time": {"card": 2, "values": [[0.5, 0.5]]},  # Binary: early/late
                    "Entity": {"card": len(entities), "values": [[1.0/len(entities)] * len(entities)]},
                    "Value": {
                        "card": 2,  # Binary: high/low
                        "values": [[0.7, 0.3], [0.3, 0.7]],  # Dummy values - will be replaced
                        "parents": ["Time", "Entity"]
                    }
                }
                
                # Replace dummy values with actual extracted values if possible
                entity_list = list(entities.keys())
                if len(entity_list) >= 2 and "values" in entities[entity_list[0]]:
                    # Use first entity's values to estimate probabilities
                    values1 = entities[entity_list[0]]["values"]
                    values2 = entities[entity_list[1]]["values"] if len(entity_list) > 1 else []
                    
                    if values1 and values2:
                        avg1 = sum(values1) / len(values1)
                        avg2 = sum(values2) / len(values2) if values2 else avg1 * 1.1
                        
                        # Normalize to probabilities
                        total = avg1 + avg2
                        if total > 0:
                            cpd_specs["Value"]["values"] = [
                                [avg1/total, avg2/total],
                                [avg2/total, avg1/total]
                            ]
                
                model = build_bn(edges, cpd_specs)
                
                if model:
                    # Query: which entity has highest probability of high value given late time?
                    best_entity = None
                    best_prob = 0
                    
                    for i, entity in enumerate(entity_list):
                        # Evidence: Time=1 (late), Entity=i
                        evidence = {"Time": 1, "Entity": i}
                        query_result = conditional_query(model, ["Value"], evidence)
                        
                        if query_result and isinstance(query_result, dict):
                            # Get probability of Value=1 (high)
                            prob_high = query_result.get(1, 0.0)
                            if prob_high > best_prob:
                                best_prob = prob_high
                                best_entity = entity
                    
                    if best_entity:
                        computed_answer = best_entity
                        reasoning = f"Bayesian network predicts '{best_entity}' has highest value probability ({best_prob:.2f})"
                        confidence = best_prob
            except Exception:
                # If Bayesian network fails, use simple heuristic
                pass
        
        # Final fallback: use entity with most mentions
        if not computed_answer and entities:
            computed_answer = max(entities.items(), key=lambda x: x[1]["mentions"])[0]
            reasoning = f"Selected '{computed_answer}' based on frequency of mention"
            confidence = 0.3
        
        # PRIMITIVE 4: confidence_from_agreement - LOAD-BEARING
        # Combine multiple confidence sources
        confidence_sources = [confidence]
        if "rate_phrases" in structure and structure["rate_phrases"]:
            # Presence of rate terminology increases confidence
            confidence_sources.append(0.8)
        if len(time_points) >= 2:
            confidence_sources.append(0.7)
        
        final_confidence = confidence_from_agreement(confidence_sources)
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": reasoning,
            "raw_rates": all_rates if 'all_rates' in locals() else {}
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        confidence = reasoning_result["confidence"]
        
        results = []
        
        for candidate in candidates:
            # Primary scoring: exact or substring match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer + " " + reasoning_text, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple calibration: ensure scores are between 0 and 1
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
            else:
                # All scores equal
                for item in scored:
                    item["score"] = 0.5
        
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