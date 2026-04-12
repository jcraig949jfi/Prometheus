import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    solve_linear_system,
    expected_value,
    information_sufficiency,
    entropy,
    confidence_from_agreement
)
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Complexity theory x constraint satisfaction - rate_of_change"""

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
        """Extract time points, values, and question from prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        # Find time points and values
        time_points = []
        values = []
        entities = {}
        
        # Look for patterns like "t=0: 100", "at time 1: 150", "Year 2: 200"
        time_patterns = [
            r'(?:t|time|Time|T)\s*[=:]?\s*(\d+)[^\d]*([\d\.]+)',
            r'(?:Year|year|Y)\s*(\d+)[^\d]*([\d\.]+)',
            r'(\d+)\s*(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?)[^\d]*([\d\.]+)',
            r'([\d\.]+)\s*at\s*(?:t|time|T)\s*(\d+)'
        ]
        
        for line in lines:
            # Try each pattern
            for pattern in time_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if len(match) == 2:
                        try:
                            time = float(match[0])
                            value = float(match[1])
                            time_points.append(time)
                            values.append(value)
                        except ValueError:
                            continue
            
            # Also look for standalone numbers that might be values
            numbers = re.findall(r'\b(\d+\.?\d*)\b', line)
            if len(numbers) >= 2:
                # If line has multiple numbers, they might be time-value pairs
                for i in range(0, len(numbers)-1, 2):
                    try:
                        time = float(numbers[i])
                        value = float(numbers[i+1])
                        time_points.append(time)
                        values.append(value)
                    except (ValueError, IndexError):
                        continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_pairs = []
        for t, v in zip(time_points, values):
            if (t, v) not in seen:
                seen.add((t, v))
                unique_pairs.append((t, v))
        
        if unique_pairs:
            time_points, values = zip(*unique_pairs)
        else:
            time_points, values = [], []
        
        # Find question (usually last sentence)
        sentences = re.split(r'[.!?]+', prompt)
        question = sentences[-1].strip() if sentences else ""
        
        # Extract entity names (capitalized words that might be variables)
        words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', prompt)
        entity_names = [w for w in words if len(w.split()) <= 3 and w not in ['The', 'A', 'An', 'At', 'In', 'On']]
        
        for name in entity_names[:3]:  # Take up to 3 entities
            entities[name] = {"values": values[:2] if values else [0, 0]}
        
        return {
            "time_points": list(time_points),
            "values": list(values),
            "question": question,
            "entities": entities,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Compute rate of change using complexity theory concepts."""
        time_points = structure["time_points"]
        values = structure["values"]
        question = structure["question"]
        
        # Default answer if we can't compute
        computed_answer = "0"
        confidence = 0.5
        reasoning = "Insufficient data"
        
        if len(time_points) >= 2 and len(values) >= 2:
            # CRITICAL PATH 1: Solve linear system for rate (slope)
            # Build matrix A for linear regression: values = a*time + b
            A = []
            b = []
            for t, v in zip(time_points, values):
                A.append([t, 1])
                b.append(v)
            
            solution = solve_linear_system(A, b)
            
            if solution and len(solution) >= 1:
                slope = solution[0]  # Rate of change (a in y = ax + b)
                
                # CRITICAL PATH 2: Check if system is uniquely solvable using constraint satisfaction
                # Represent as constraint problem: find slope m such that values follow linear trend
                variables = ["m", "b"]
                domains = {
                    "m": [slope * 0.9, slope, slope * 1.1],  # Domain around computed slope
                    "b": [solution[1] if len(solution) > 1 else 0]
                }
                
                # Constraint: for each point, m*time + b ≈ value
                constraints = []
                for i, (t, v) in enumerate(zip(time_points, values)):
                    def make_constraint(idx, time, target):
                        def constraint(assignment):
                            m_val = assignment["m"]
                            b_val = assignment["b"]
                            predicted = m_val * time + b_val
                            return abs(predicted - target) < 0.1 * abs(target)
                        return constraint
                    
                    constraints.append((["m", "b"], make_constraint(i, t, v)))
                
                # Use amino acid to check uniqueness
                unique = is_uniquely_solvable(variables, domains, constraints)
                
                # CRITICAL PATH 3: Compute expected value of rate over time points
                if len(time_points) > 1:
                    time_diffs = [time_points[i+1] - time_points[i] for i in range(len(time_points)-1)]
                    value_diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
                    
                    if time_diffs:
                        # Calculate instantaneous rates
                        rates = [vd/td if td != 0 else 0 for vd, td in zip(value_diffs, time_diffs)]
                        
                        # Use expected_value primitive
                        if rates:
                            # Create probability distribution (uniform)
                            prob = 1.0 / len(rates)
                            outcomes = [(prob, rate) for rate in rates]
                            expected_rate = expected_value(outcomes)
                            
                            # CRITICAL PATH 4: Compute entropy of rates (complexity measure)
                            # Normalize rates to create probability distribution
                            abs_rates = [abs(r) for r in rates]
                            total = sum(abs_rates)
                            if total > 0:
                                probs = [r/total for r in abs_rates]
                                rate_entropy = entropy(probs)
                                
                                # CRITICAL PATH 5: Check information sufficiency
                                n_unknowns = 2  # slope and intercept
                                n_constraints = len(time_points)
                                sufficiency = information_sufficiency(n_unknowns, n_constraints)
                                
                                # Determine answer based on complexity theory concepts
                                # High entropy = complex, unpredictable rate changes
                                # Low entropy = simple, predictable rate
                                
                                if unique is True:
                                    # System is uniquely determined
                                    if rate_entropy < 0.5:  # Low complexity
                                        computed_answer = f"{slope:.2f}"
                                        reasoning = f"Linear rate: {slope:.2f}, low entropy ({rate_entropy:.2f}), uniquely determined"
                                    else:  # High complexity
                                        computed_answer = f"{expected_rate:.2f}"
                                        reasoning = f"Expected rate: {expected_rate:.2f}, high entropy ({rate_entropy:.2f})"
                                else:
                                    # Not uniquely determined
                                    computed_answer = f"{expected_rate:.2f}"
                                    reasoning = f"Expected rate: {expected_rate:.2f}, system not unique"
                                
                                # Set confidence based on agreement between different rate measures
                                rate_measures = [slope, expected_rate]
                                if len(rate_measures) >= 2:
                                    confidence = confidence_from_agreement(rate_measures)
                                else:
                                    confidence = 0.7
                            else:
                                computed_answer = f"{slope:.2f}"
                                reasoning = f"Linear rate: {slope:.2f}"
                                confidence = 0.6
                        else:
                            computed_answer = f"{slope:.2f}"
                            reasoning = f"Linear rate: {slope:.2f}"
                            confidence = 0.6
                    else:
                        computed_answer = f"{slope:.2f}"
                        reasoning = f"Linear rate: {slope:.2f}"
                        confidence = 0.6
                else:
                    computed_answer = f"{slope:.2f}"
                    reasoning = f"Linear rate: {slope:.2f}"
                    confidence = 0.6
            else:
                # Fallback: simple average rate
                if len(time_points) >= 2:
                    total_time = max(time_points) - min(time_points)
                    total_change = max(values) - min(values)
                    if total_time != 0:
                        avg_rate = total_change / total_time
                        computed_answer = f"{avg_rate:.2f}"
                        reasoning = f"Average rate: {avg_rate:.2f}"
                        confidence = 0.4
        elif len(values) >= 2:
            # Only values, no explicit times - assume unit time intervals
            rates = [values[i+1] - values[i] for i in range(len(values)-1)]
            if rates:
                avg_rate = sum(rates) / len(rates)
                computed_answer = f"{avg_rate:.2f}"
                reasoning = f"Average change per step: {avg_rate:.2f}"
                confidence = 0.3
        
        # Extract what's being asked for from question
        if "percentage" in question.lower() or "%" in question:
            # Convert to percentage if needed
            try:
                rate_num = float(computed_answer)
                computed_answer = f"{rate_num*100:.1f}%"
            except ValueError:
                pass
        elif "per" in question.lower() and ("hour" in question.lower() or "minute" in question.lower() or "second" in question.lower()):
            # Add units if appropriate
            if "hour" in question.lower():
                computed_answer = f"{computed_answer} per hour"
            elif "minute" in question.lower():
                computed_answer = f"{computed_answer} per minute"
            elif "second" in question.lower():
                computed_answer = f"{computed_answer} per second"
        
        return {
            "answer": computed_answer,
            "confidence": max(0.1, min(1.0, confidence)),
            "reasoning": reasoning
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Check for numerical equivalence
                candidate_nums = re.findall(r'[-+]?\d*\.\d+|\d+', candidate)
                computed_nums = re.findall(r'[-+]?\d*\.\d+|\d+', computed_answer)
                
                if candidate_nums and computed_nums:
                    try:
                        cand_num = float(candidate_nums[0])
                        comp_num = float(computed_nums[0])
                        # Score based on relative error
                        if comp_num != 0:
                            error = abs(cand_num - comp_num) / abs(comp_num)
                            score = 1.0 / (1.0 + error)
                        else:
                            score = 0.5 if cand_num == 0 else 0.1
                    except (ValueError, IndexError):
                        # Fallback to NCD
                        score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                else:
                    # Fallback to NCD with reasoning text for better compression
                    combined = f"{computed_answer} {reasoning_text}"
                    score = 1.0 / (1.0 + self._ncd(combined, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to better distribution."""
        if not scored:
            return scored
        
        scores = [item["raw_score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            
            if max_score > min_score:
                # Normalize to [0, 1] range
                for item in scored:
                    normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                    item["score"] = normalized
            else:
                # All scores equal
                for item in scored:
                    item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a and not b:
            return 0.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)