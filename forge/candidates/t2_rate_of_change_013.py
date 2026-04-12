import re
import zlib
from typing import Dict, List, Any, Optional

from forge_primitives import (
    bayesian_update,
    expected_value,
    entropy,
    confidence_from_agreement,
    solve_linear_system
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Decision theory x Constraint satisfaction - Rate of change"""

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
        numbers = re.findall(r'([0-9]+\.?[0-9]*)%?', prompt)
        numeric_values = []
        for num in numbers:
            try:
                if '%' in prompt[prompt.find(num):prompt.find(num)+len(num)+3]:
                    numeric_values.append(float(num) / 100.0)
                else:
                    numeric_values.append(float(num))
            except ValueError:
                continue
        
        # Find time references
        time_patterns = [
            r'(?:year|month|day|week|hour|minute|second)s?\s+(\d+)',
            r'time\s+(\d+)',
            r'at\s+t=(\d+)',
            r'from\s+t(\d+)\s+to\s+t(\d+)'
        ]
        time_points = []
        for pattern in time_patterns:
            matches = re.findall(pattern, prompt.lower())
            for match in matches:
                if isinstance(match, tuple):
                    for m in match:
                        if m.isdigit():
                            time_points.append(int(m))
                elif match.isdigit():
                    time_points.append(int(match))
        
        # Find entity names (capitalized phrases that appear with values)
        entity_candidates = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', prompt)
        entities = {}
        
        # Look for value assignments to entities
        for entity in entity_candidates:
            if len(entity.split()) > 3:  # Probably not an entity name
                continue
                
            # Find numbers near this entity
            entity_pos = prompt.find(entity)
            if entity_pos == -1:
                continue
                
            # Look in a window around the entity
            window_start = max(0, entity_pos - 50)
            window_end = min(len(prompt), entity_pos + 50)
            window = prompt[window_start:window_end]
            
            # Extract numbers from this window
            window_numbers = re.findall(r'([0-9]+\.?[0-9]*)%?', window)
            entity_values = []
            for num in window_numbers:
                try:
                    if '%' in window[window.find(num):window.find(num)+len(num)+3]:
                        entity_values.append(float(num) / 100.0)
                    else:
                        entity_values.append(float(num))
                except ValueError:
                    continue
            
            if entity_values:
                entities[entity] = {
                    "values": entity_values,
                    "position": entity_pos
                }
        
        # If no entities found, create generic ones
        if not entities and numeric_values:
            entities = {
                "Variable_A": {"values": numeric_values[:len(numeric_values)//2] if len(numeric_values) > 1 else numeric_values, "position": 0},
                "Variable_B": {"values": numeric_values[len(numeric_values)//2:] if len(numeric_values) > 1 else numeric_values, "position": 1}
            }
        
        # Extract rate of change indicators
        rate_indicators = []
        rate_words = ["rate", "speed", "velocity", "acceleration", "change", "increase", "decrease", "growth", "decay"]
        for word in rate_words:
            if word in prompt.lower():
                rate_indicators.append(word)
        
        return {
            "entities": entities,
            "numeric_values": numeric_values,
            "time_points": sorted(list(set(time_points))),
            "question": question,
            "rate_indicators": rate_indicators,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply decision theory framework to compute rate of change."""
        entities = structure["entities"]
        numeric_values = structure["numeric_values"]
        time_points = structure["time_points"]
        question = structure["question"]
        
        # If we have at least 2 time points and corresponding values, compute rate
        computed_answer = None
        confidence = 0.5
        reasoning = ""
        
        # Decision theory approach: treat rate computation as an optimal decision under uncertainty
        # We'll use expected value of different rate estimation methods
        
        # METHOD 1: Linear regression using solve_linear_system (T1 primitive)
        if len(time_points) >= 2 and len(numeric_values) >= 2:
            # Try to fit a line: y = mx + b
            # Create system: Σy = mΣx + nb, Σxy = mΣx² + bΣx
            x_vals = time_points[:min(len(time_points), len(numeric_values))]
            y_vals = numeric_values[:min(len(time_points), len(numeric_values))]
            
            if len(x_vals) >= 2:
                n = len(x_vals)
                sum_x = sum(x_vals)
                sum_y = sum(y_vals)
                sum_xy = sum(x*y for x, y in zip(x_vals, y_vals))
                sum_x2 = sum(x*x for x in x_vals)
                
                A = [[sum_x2, sum_x], [sum_x, n]]
                b = [sum_xy, sum_y]
                
                solution = solve_linear_system(A, b)
                if solution:
                    m, b_val = solution
                    rate_linear = m
                    
                    # Compute entropy of the residuals as uncertainty measure
                    residuals = [y - (m*x + b_val) for x, y in zip(x_vals, y_vals)]
                    if residuals:
                        # Normalize residuals to probabilities
                        abs_res = [abs(r) for r in residuals]
                        if sum(abs_res) > 0:
                            probs = [r/sum(abs_res) for r in abs_res]
                            uncertainty = entropy(probs)  # T1 primitive
                        else:
                            uncertainty = 0.0
                    else:
                        uncertainty = 1.0
                    
                    # Bayesian update of confidence based on fit quality
                    prior_confidence = 0.5
                    likelihood = 1.0 - min(uncertainty, 1.0)
                    confidence = bayesian_update(prior_confidence, likelihood)  # T1 primitive
                    
                    # Expected value of rate considering uncertainty
                    outcomes = [(1.0 - uncertainty, rate_linear), (uncertainty, 0.0)]
                    expected_rate = expected_value(outcomes)  # T1 primitive
                    
                    # Use constraint satisfaction to check if solution is unique
                    # Create a simple CSP: rate must satisfy all data points within tolerance
                    variables = ["rate", "intercept"]
                    domains = {
                        "rate": [rate_linear, rate_linear * 0.9, rate_linear * 1.1],
                        "intercept": [b_val, b_val * 0.9, b_val * 1.1]
                    }
                    
                    def constraint_fn(vars_dict):
                        rate, intercept = vars_dict["rate"], vars_dict["intercept"]
                        # Check if all points are reasonably fit
                        errors = [abs(y - (rate*x + intercept)) for x, y in zip(x_vals, y_vals)]
                        return all(e < 0.1 * abs(y) for e, y in zip(errors, y_vals))
                    
                    constraints = [(["rate", "intercept"], constraint_fn)]
                    
                    # Check uniqueness using amino acid
                    unique = is_uniquely_solvable(variables, domains, constraints)  # Amino acid
                    
                    if unique:
                        confidence = confidence * 1.2  # Boost confidence for unique solution
                    
                    # Find first solution using amino acid
                    solution_csp = solve_first(variables, domains, constraints)  # Amino acid
                    
                    if solution_csp:
                        final_rate = solution_csp["rate"]
                    else:
                        final_rate = expected_rate
                    
                    computed_answer = f"{final_rate:.3f}"
                    reasoning = f"Linear rate: {rate_linear:.3f}, Expected: {expected_rate:.3f}, Uncertainty: {uncertainty:.3f}"
        
        # METHOD 2: If linear approach failed, use simple difference
        if not computed_answer and len(numeric_values) >= 2:
            if len(time_points) >= 2:
                # Use last two points
                rate_simple = (numeric_values[-1] - numeric_values[-2]) / (time_points[-1] - time_points[-2])
            else:
                # Assume unit time intervals
                rate_simple = numeric_values[-1] - numeric_values[0]
            
            # Compute confidence from agreement of different rate estimates
            rate_estimates = []
            
            # Estimate 1: Simple difference
            rate_estimates.append(rate_simple)
            
            # Estimate 2: Average of pairwise differences
            if len(numeric_values) > 2:
                pairwise_rates = []
                for i in range(1, len(numeric_values)):
                    if i < len(time_points):
                        dt = time_points[i] - time_points[i-1] if i < len(time_points) else 1
                    else:
                        dt = 1
                    pairwise_rates.append((numeric_values[i] - numeric_values[i-1]) / dt)
                if pairwise_rates:
                    rate_estimates.append(sum(pairwise_rates) / len(pairwise_rates))
            
            # Final confidence from agreement of estimates
            if len(rate_estimates) > 1:
                confidence = confidence_from_agreement(rate_estimates)  # T1 primitive
            else:
                confidence = 0.7
            
            computed_answer = f"{rate_simple:.3f}"
            reasoning = f"Simple rate: {rate_simple:.3f} from {len(rate_estimates)} estimates"
        
        # METHOD 3: Fallback to entity-based reasoning
        if not computed_answer and entities:
            # Find entity with maximum change
            max_change = -float('inf')
            best_entity = None
            
            for entity, data in entities.items():
                values = data["values"]
                if len(values) >= 2:
                    change = values[-1] - values[0]
                    if change > max_change:
                        max_change = change
                        best_entity = entity
            
            if best_entity:
                computed_answer = best_entity
                confidence = 0.6
                reasoning = f"Entity with maximum change: {best_entity} ({max_change:.3f})"
        
        # Final fallback
        if not computed_answer:
            computed_answer = "0.000"
            confidence = 0.3
            reasoning = "No rate computable from given data"
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning,
            "raw_values": numeric_values,
            "time_points": time_points
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        scored = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD similarity between reasoning text and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
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
        if max(scores) - min(scores) < 0.001:  # All scores nearly equal
            # Add small differentiation based on candidate length
            for item in scored:
                item["score"] = item["score"] + (len(item["candidate"]) * 0.0001)
        
        # Normalize to [0, 1] range
        min_score = min(scores)
        max_score = max(scores)
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a and not b:
            return 0.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)