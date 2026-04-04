import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_linear_system,
    expected_value
)
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """statistical_mechanics x pgmpy_acids - rate_of_change"""

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
        
        # Find all entities (capitalized multi-word phrases that appear with numbers)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_entities = re.findall(entity_pattern, prompt)
        
        # Find time points and associated values
        time_pattern = r'(?:time|year|day|month|week|hour)\s*(\d+)'
        time_points = re.findall(time_pattern, prompt.lower())
        
        # Find numerical values (percentages, rates, raw numbers)
        value_pattern = r'([0-9]+\.?[0-9]*)\s*%?'
        all_values = re.findall(value_pattern, prompt)
        numeric_values = [float(v) for v in all_values if float(v) > 0]
        
        # Associate values with entities based on proximity
        entities = {}
        sentences = prompt.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Find entities in this sentence
            sent_entities = re.findall(entity_pattern, sentence)
            # Find values in this sentence
            sent_values = re.findall(value_pattern, sentence)
            sent_numeric = [float(v) for v in sent_values if float(v) > 0]
            
            # Find time references in this sentence
            sent_times = re.findall(time_pattern, sentence.lower())
            
            for entity in sent_entities:
                if entity not in entities:
                    entities[entity] = {
                        "values": [],
                        "times": [],
                        "value_time_pairs": []
                    }
                
                if sent_numeric:
                    entities[entity]["values"].extend(sent_numeric[:3])  # Limit to first few
                
                if sent_times:
                    entities[entity]["times"].extend([int(t) for t in sent_times[:3]])
                
                # Create value-time pairs if both present
                if sent_numeric and sent_times:
                    min_len = min(len(sent_numeric), len(sent_times))
                    for i in range(min_len):
                        entities[entity]["value_time_pairs"].append(
                            (int(sent_times[i]), sent_numeric[i])
                        )
        
        # Clean up entities with no data
        entities = {k: v for k, v in entities.items() if v["values"] or v["value_time_pairs"]}
        
        return {
            "entities": entities,
            "question": question,
            "time_points": list(set([int(t) for t in time_points])),
            "numeric_values": numeric_values,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use statistical mechanics framework to compute rate of change.
        
        Conceptual mapping:
        - Entities = particles in a system
        - Values over time = energy states
        - Rate of change = derivative of energy with respect to time
        - Bayesian update = thermal equilibrium adjustment
        - Entropy = disorder in the rate estimates
        - Confidence = inverse temperature (certainty)
        """
        entities = structure["entities"]
        question = structure["question"]
        
        if not entities:
            # Fallback: extract any numbers and compute simple rate
            values = structure["numeric_values"]
            if len(values) >= 2:
                rate = (values[-1] - values[0]) / max(len(values) - 1, 1)
                return {
                    "answer": f"{rate:.2f}",
                    "confidence": 0.5,
                    "reasoning": "Simple difference using extracted values",
                    "computed_rate": rate
                }
            else:
                return {
                    "answer": "0",
                    "confidence": 0.1,
                    "reasoning": "No data extracted",
                    "computed_rate": 0
                }
        
        # Step 1: For each entity with time-value pairs, compute instantaneous rate
        entity_rates = {}
        entity_entropies = {}
        
        for entity, data in entities.items():
            pairs = data["value_time_pairs"]
            if len(pairs) >= 2:
                # Sort by time
                pairs.sort(key=lambda x: x[0])
                times = [t for t, _ in pairs]
                values = [v for _, v in pairs]
                
                # Compute rates between consecutive points
                rates = []
                for i in range(1, len(pairs)):
                    dt = times[i] - times[i-1]
                    if dt > 0:
                        rate = (values[i] - values[i-1]) / dt
                        rates.append(rate)
                
                if rates:
                    # Statistical mechanics: average rate = equilibrium value
                    avg_rate = sum(rates) / len(rates)
                    
                    # Compute entropy of rate distribution (disorder)
                    if len(rates) > 1:
                        # Normalize rates to probabilities
                        rate_min = min(rates)
                        rate_max = max(rates)
                        if rate_max > rate_min:
                            normalized = [(r - rate_min) / (rate_max - rate_min) for r in rates]
                            # Add small epsilon to avoid zeros
                            normalized = [max(v, 0.001) for v in normalized]
                            total = sum(normalized)
                            if total > 0:
                                probs = [v/total for v in normalized]
                                # T1 PRIMITIVE 1: entropy
                                rate_entropy = entropy(probs)
                                entity_entropies[entity] = rate_entropy
                    
                    entity_rates[entity] = avg_rate
        
        # Step 2: Use Bayesian update to refine rates based on prior information
        # In statistical mechanics, prior = equilibrium distribution
        refined_rates = {}
        if entity_rates:
            # Use first entity's rate as reference prior
            reference_rate = list(entity_rates.values())[0]
            
            for entity, rate in entity_rates.items():
                # T1 PRIMITIVE 2: bayesian_update
                # Prior belief about rate, likelihood from data, small false positive
                prior = 0.5  # Neutral prior
                likelihood = min(abs(rate) / (abs(reference_rate) + 0.1), 1.0)
                posterior = bayesian_update(prior, likelihood, false_positive=0.1)
                
                # Adjust rate by posterior confidence
                refined_rate = rate * posterior
                refined_rates[entity] = refined_rate
        
        # Step 3: Build a simple Bayesian network to model causal relationships
        # between time and value changes
        try:
            # Create edges: time -> value for each entity
            edges = []
            for entity in entities.keys():
                edges.append(("Time", f"{entity}_Value"))
            
            # Create CPDs based on extracted data
            cpd_specs = {}
            for entity, data in entities.items():
                pairs = data["value_time_pairs"]
                if len(pairs) >= 2:
                    # Simple linear relationship: value = slope * time + intercept
                    times = [t for t, _ in pairs]
                    values = [v for _, v in pairs]
                    
                    # T1 PRIMITIVE 3: solve_linear_system
                    # Solve for slope (rate) using least squares: A * [slope, intercept] = values
                    # where A = [[time1, 1], [time2, 1], ...]
                    A = [[t, 1] for t in times]
                    b = values
                    solution = solve_linear_system(A, b)
                    
                    if solution:
                        slope, intercept = solution[0], solution[1]
                        # AMINO ACID: build_bn
                        model = build_bn(edges, cpd_specs)
                        if model:
                            # Query the rate (slope) from the model
                            # AMINO ACID: conditional_query
                            query_result = conditional_query(
                                model, 
                                [f"{entity}_Value"], 
                                {"Time": times[-1] if times else 0}
                            )
                            
                            if query_result:
                                # Extract probability distribution
                                if isinstance(query_result, dict):
                                    # Use the query result to adjust rate
                                    rate_from_bn = list(query_result.values())[0] if query_result else 0
                                    # Blend with refined rate
                                    if entity in refined_rates:
                                        refined_rates[entity] = 0.7 * refined_rates[entity] + 0.3 * rate_from_bn
        except Exception:
            # If BN fails, continue with refined rates
            pass
        
        # Step 4: Determine which entity has maximum rate of change
        if refined_rates:
            # T1 PRIMITIVE 4: expected_value
            # Create expected value from rates and confidences
            outcomes = []
            for entity, rate in refined_rates.items():
                # Confidence based on entropy (low entropy = high confidence)
                conf = 1.0 - (entity_entropies.get(entity, 0.5) if entity_entropies else 0.5)
                outcomes.append((conf, rate))
            
            if outcomes:
                # Weighted expected rate
                exp_rate = expected_value(outcomes)
                
                # Find entity closest to expected rate
                best_entity = min(refined_rates.items(), 
                                 key=lambda x: abs(x[1] - exp_rate))[0]
                best_rate = refined_rates[best_entity]
                
                # T1 PRIMITIVE 5: confidence_from_agreement
                # Confidence from agreement among different rate estimates
                all_estimates = list(refined_rates.values())
                if len(all_estimates) > 1:
                    confidence = confidence_from_agreement(all_estimates)
                else:
                    confidence = 0.7
                
                # Check if question asks for numerical rate or entity
                if "rate" in question.lower() or "how much" in question.lower():
                    computed_answer = f"{best_rate:.2f}"
                else:
                    computed_answer = best_entity
                
                return {
                    "answer": computed_answer,
                    "confidence": min(confidence, 0.95),
                    "reasoning": f"Rate of change computed using statistical mechanics framework. Entity '{best_entity}' has rate {best_rate:.2f}.",
                    "computed_rate": best_rate,
                    "best_entity": best_entity
                }
        
        # Fallback: use entity with most data points
        if entities:
            best_entity = max(entities.items(), 
                             key=lambda x: len(x[1]["values"]))[0]
            return {
                "answer": best_entity,
                "confidence": 0.3,
                "reasoning": "Selected entity with most data points as fallback",
                "computed_rate": 0,
                "best_entity": best_entity
            }
        
        return {
            "answer": "0",
            "confidence": 0.1,
            "reasoning": "No computable rate found",
            "computed_rate": 0
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        computed_rate = reasoning_result.get("computed_rate", 0)
        best_entity = reasoning_result.get("best_entity", "")
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            candidate_lower = candidate.lower()
            answer_lower = computed_answer.lower()
            
            # Primary scoring: exact match or containment
            if answer_lower in candidate_lower or candidate_lower in answer_lower:
                base_score = 1.0
            else:
                # Check if candidate contains the best entity
                if best_entity and best_entity.lower() in candidate_lower:
                    base_score = 0.8
                else:
                    # Check for numerical rate match
                    rate_str = f"{computed_rate:.2f}"
                    if rate_str in candidate:
                        base_score = 0.9
                    else:
                        # Extract numbers from candidate
                        cand_numbers = re.findall(r'([0-9]+\.?[0-9]*)', candidate)
                        if cand_numbers:
                            cand_nums = [float(n) for n in cand_numbers]
                            # Check if any number is close to computed rate
                            if any(abs(num - computed_rate) < 0.1 for num in cand_nums):
                                base_score = 0.7
                            else:
                                # Fallback to NCD similarity
                                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                        else:
                            # Fallback to NCD similarity
                            base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score by confidence
            confidence = reasoning_result.get("confidence", 0.5)
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
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