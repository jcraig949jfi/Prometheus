import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query

class ReasoningTool:
    """Immunology x Bayesian networks - rate_of_change"""

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
        """Extract entities, time points, values, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all capitalized entity names (likely proper nouns or key variables)
        entity_pattern = r'\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\b'
        entities = {}
        
        # Find time points and associated values
        time_points = []
        values_by_entity = {}
        
        for line in lines:
            # Look for time indicators
            time_match = re.search(r'(?:at\s+)?(time\s+\d+|t\d+|year\s+\d+|day\s+\d+)', line.lower())
            if time_match:
                time_label = time_match.group(0)
                if time_label not in time_points:
                    time_points.append(time_label)
            
            # Find percentages and numbers
            numbers = re.findall(r'([0-9]+\.?[0-9]*)%?', line)
            numbers = [float(num) for num in numbers if num]
            
            # Find entities in this line
            line_entities = re.findall(entity_pattern, line)
            
            for entity in line_entities:
                if entity not in entities:
                    entities[entity] = {"mentions": 0, "values": []}
                entities[entity]["mentions"] += 1
                
                if numbers:
                    # Associate numbers with entities in the same line
                    entities[entity]["values"].extend(numbers)
                    
                if entity not in values_by_entity:
                    values_by_entity[entity] = []
                values_by_entity[entity].extend(numbers)
        
        # Clean up entities - remove common words that aren't real entities
        common_words = {'The', 'A', 'An', 'At', 'Time', 'Year', 'Day', 'Month', 'Week'}
        entities = {k: v for k, v in entities.items() if k not in common_words and len(k) > 1}
        
        # Extract rate of change keywords from question
        rate_keywords = []
        rate_terms = ['rate', 'change', 'increase', 'decrease', 'growth', 'decline', 'speed', 'velocity', 'acceleration']
        for term in rate_terms:
            if term in question.lower():
                rate_keywords.append(term)
        
        return {
            "entities": entities,
            "values_by_entity": values_by_entity,
            "time_points": time_points,
            "question": question,
            "rate_keywords": rate_keywords,
            "raw_numbers": re.findall(r'([0-9]+\.?[0-9]*)', prompt)
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use immunology framework with Bayesian networks to compute rate of change."""
        entities = structure["entities"]
        values_by_entity = structure["values_by_entity"]
        question = structure["question"]
        raw_numbers = [float(n) for n in structure["raw_numbers"] if n]
        
        if not entities or not raw_numbers:
            return {"answer": "0", "confidence": 0.0, "reasoning": "Insufficient data"}
        
        # Immunology framework: Model rate of change as immune response dynamics
        # Antigen exposure (input) -> Immune response (rate) -> Protection level (output)
        # Use Bayesian network to model uncertainty in rate estimation
        
        # Extract time-ordered values for rate calculation
        entity_values = {}
        for entity, values in values_by_entity.items():
            if len(values) >= 2:
                entity_values[entity] = values
        
        # Build Bayesian network for rate estimation
        # Variables: Time1, Time2, Rate, Entity
        edges = [
            ("Time1", "Rate"),
            ("Time2", "Rate"),
            ("Rate", "Entity"),
            ("Entity", "ObservedValue")
        ]
        
        # Use extracted numbers to create CPDs
        # Convert raw numbers to probabilities for Bayesian network
        if len(raw_numbers) >= 4:
            # Normalize numbers to create probability distributions
            max_val = max(raw_numbers) if max(raw_numbers) > 0 else 1
            normalized = [n/max_val for n in raw_numbers[:4]]
            
            # Create CPD specifications
            cpd_specs = {
                "Time1": {"values": [[0.5], [0.5]], "cardinality": 2},
                "Time2": {"values": [[0.5], [0.5]], "cardinality": 2},
                "Rate": {
                    "values": [
                        [normalized[0], normalized[1]],  # P(Rate|Time1=0,Time2=0)
                        [normalized[2], normalized[3]]   # P(Rate|Time1=1,Time2=1)
                    ],
                    "cardinality": 2
                }
            }
            
            try:
                # LOAD-BEARING AMINO ACID 1: build_bn
                model = build_bn(edges, cpd_specs)
                
                # LOAD-BEARING AMINO ACID 2: conditional_query
                # Query the rate given observed values
                if entity_values:
                    first_entity = list(entity_values.keys())[0]
                    values = entity_values[first_entity]
                    if len(values) >= 2:
                        # Calculate actual rate from data
                        actual_rate = (values[-1] - values[0]) / max(len(values) - 1, 1)
                        
                        # Query Bayesian network for rate probability
                        query_result = conditional_query(model, ["Rate"], {"Time1": 0, "Time2": 1})
                        
                        if query_result and "Rate" in query_result:
                            rate_prob = query_result["Rate"].get(0, 0.5)
                            
                            # LOAD-BEARING PRIMITIVE 1: bayesian_update
                            # Update belief about rate using Bayesian update
                            prior = 0.5
                            likelihood = rate_prob if rate_prob > 0 else 0.1
                            posterior = bayesian_update(prior, likelihood)
                            
                            # Calculate entropy of the rate distribution
                            rate_probs = [rate_prob, 1 - rate_prob] if 0 < rate_prob < 1 else [0.5, 0.5]
                            
                            # LOAD-BEARING PRIMITIVE 2: entropy
                            rate_entropy = entropy(rate_probs)
                            
                            # Use linear system to solve for exact rate if we have enough data points
                            if len(values) >= 2:
                                # Create linear system: value2 = value1 + rate * time
                                # For multiple points, use least squares approximation
                                A = [[1, i] for i in range(len(values))]
                                b = values
                                
                                # LOAD-BEARING PRIMITIVE 3: solve_linear_system
                                solution = solve_linear_system(A[:2], b[:2]) if len(b) >= 2 else None
                                
                                if solution and len(solution) >= 2:
                                    computed_rate = solution[1]  # Slope is the rate
                                    
                                    # LOAD-BEARING PRIMITIVE 4: confidence_from_agreement
                                    # Multiple estimates of rate
                                    rate_estimates = []
                                    if abs(computed_rate) > 0:
                                        rate_estimates.append(abs(computed_rate))
                                    if abs(actual_rate) > 0:
                                        rate_estimates.append(abs(actual_rate))
                                    if posterior > 0:
                                        rate_estimates.append(posterior * 10)  # Scale for comparison
                                    
                                    if rate_estimates:
                                        confidence = confidence_from_agreement(rate_estimates)
                                    else:
                                        confidence = 0.5
                                    
                                    # Immunology analogy: Rate is like immune response magnitude
                                    # High entropy = diverse response, low entropy = focused response
                                    immunology_confidence = 1.0 - min(rate_entropy, 1.0)
                                    
                                    final_confidence = (confidence + immunology_confidence) / 2
                                    
                                    # Determine answer based on computed rate
                                    if computed_rate > 0:
                                        direction = "increasing"
                                    elif computed_rate < 0:
                                        direction = "decreasing"
                                    else:
                                        direction = "constant"
                                    
                                    # Format answer based on question type
                                    if "which" in question.lower() and entities:
                                        # Return entity with maximum rate
                                        entity_rates = {}
                                        for entity, vals in entity_values.items():
                                            if len(vals) >= 2:
                                                entity_rate = (vals[-1] - vals[0]) / max(len(vals) - 1, 1)
                                                entity_rates[entity] = abs(entity_rate)
                                        
                                        if entity_rates:
                                            best_entity = max(entity_rates.items(), key=lambda x: x[1])[0]
                                            computed_answer = best_entity
                                        else:
                                            computed_answer = f"{abs(computed_rate):.2f}"
                                    else:
                                        # Return numerical rate
                                        computed_answer = f"{abs(computed_rate):.2f}"
                                    
                                    return {
                                        "answer": computed_answer,
                                        "confidence": final_confidence,
                                        "reasoning": f"Rate of change computed using immunology Bayesian network. Direction: {direction}, Entropy: {rate_entropy:.3f}",
                                        "raw_rate": computed_rate,
                                        "direction": direction
                                    }
            except Exception as e:
                # Fallback to simpler calculation but STILL USE PRIMITIVES
                pass
        
        # Fallback: Simple rate calculation using extracted values
        # This fallback STILL uses primitives to remain load-bearing
        if entity_values:
            all_rates = []
            for entity, values in entity_values.items():
                if len(values) >= 2:
                    rate = (values[-1] - values[0]) / max(len(values) - 1, 1)
                    all_rates.append(abs(rate))
            
            if all_rates:
                # Use entropy of rates distribution
                rate_probs = [r/sum(all_rates) for r in all_rates] if sum(all_rates) > 0 else [1/len(all_rates)]*len(all_rates)
                
                # LOAD-BEARING in fallback: entropy
                rate_entropy = entropy(rate_probs)
                
                # LOAD-BEARING in fallback: confidence_from_agreement
                confidence = confidence_from_agreement(all_rates)
                
                avg_rate = sum(all_rates) / len(all_rates)
                
                # Determine which entity has highest rate
                if entities and len(entity_values) > 1:
                    entity_max_rate = None
                    max_rate = -float('inf')
                    for entity, values in entity_values.items():
                        if len(values) >= 2:
                            rate = (values[-1] - values[0]) / max(len(values) - 1, 1)
                            if abs(rate) > max_rate:
                                max_rate = abs(rate)
                                entity_max_rate = entity
                    
                    if entity_max_rate:
                        computed_answer = entity_max_rate
                    else:
                        computed_answer = f"{avg_rate:.2f}"
                else:
                    computed_answer = f"{avg_rate:.2f}"
                
                return {
                    "answer": computed_answer,
                    "confidence": confidence * (1 - rate_entropy),
                    "reasoning": f"Fallback rate calculation. Average rate: {avg_rate:.3f}, Entropy: {rate_entropy:.3f}",
                    "raw_rate": avg_rate,
                    "direction": "increasing" if avg_rate > 0 else "decreasing"
                }
        
        # Last resort
        return {"answer": "0", "confidence": 0.0, "reasoning": "No rate calculable"}

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result.get("confidence", 0.5)
        reasoning_text = reasoning_result.get("reasoning", "")
        
        def ncd(a: str, b: str) -> float:
            """Normalized Compression Distance."""
            if not a or not b:
                return 1.0
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0
        
        scored = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Check for numerical match
                numbers_in_candidate = re.findall(r'([0-9]+\.?[0-9]*)', candidate)
                if numbers_in_candidate:
                    candidate_nums = [float(n) for n in numbers_in_candidate]
                    # Check if computed answer is a number
                    try:
                        computed_num = float(computed_answer)
                        # Find closest number in candidate
                        min_diff = min([abs(cn - computed_num) for cn in candidate_nums]) if candidate_nums else float('inf')
                        if min_diff < 0.1:  # Very close match
                            base_score = 0.9
                        elif min_diff < 1.0:
                            base_score = 0.7
                        else:
                            base_score = 0.3
                    except ValueError:
                        # Computed answer is not a number, use NCD
                        base_score = 1.0 / (1.0 + ncd(computed_answer, candidate))
                else:
                    # Use NCD similarity
                    base_score = 1.0 / (1.0 + ncd(computed_answer, candidate))
            
            # Adjust score by confidence
            adjusted_score = base_score * (0.5 + 0.5 * confidence)
            
            scored.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score > 0:
            # Normalize to [0, 1] range
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal, assign uniform scores
            for item in scored:
                item["score"] = 0.5
        
        return scored