import re
import zlib
from typing import Dict, List, Any, Tuple
from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    modular_arithmetic,
    temporal_order,
    solve_linear_system
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Behavioral economics x Constraint satisfaction - temporal_complex"""

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
        """Extract temporal entities, values, and relationships from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        entities = {}
        temporal_relations = []
        values = {}
        question = lines[-1] if lines else ""
        
        # Extract time units and conversions
        time_pattern = r'(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?|years?)'
        # Extract arithmetic operations
        arithmetic_pattern = r'(\d+)\s*([+\-*/])\s*(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?|years?)'
        # Extract temporal order cues
        order_pattern = r'(before|after|earlier than|later than|from|to|until)'
        
        for line in lines:
            # Find time values with units
            time_matches = re.findall(time_pattern, line.lower())
            for amount, unit in time_matches:
                key = f"{amount}_{unit}"
                if key not in values:
                    values[key] = {"amount": int(amount), "unit": unit}
            
            # Find arithmetic expressions
            arith_matches = re.findall(arithmetic_pattern, line.lower())
            for num1, op, num2, unit in arith_matches:
                key = f"{num1}{op}{num2}_{unit}"
                if key not in values:
                    values[key] = {"num1": int(num1), "op": op, "num2": int(num2), "unit": unit}
            
            # Find temporal relationships
            if any(word in line.lower() for word in ['before', 'after', 'earlier', 'later']):
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in ['before', 'after', 'earlier', 'later']:
                        if i > 0 and i < len(words) - 1:
                            entity1 = words[i-1]
                            entity2 = words[i+1]
                            if word.lower() in ['before', 'earlier']:
                                temporal_relations.append((entity1, entity2))
                            else:
                                temporal_relations.append((entity2, entity1))
        
        # Extract named entities (capitalized phrases)
        named_entities = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', prompt)
        for entity in named_entities:
            if entity not in entities and len(entity.split()) <= 3:
                entities[entity] = {"type": "temporal_entity", "mentions": 1}
        
        return {
            "entities": entities,
            "values": values,
            "temporal_relations": temporal_relations,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply behavioral economics principles to temporal reasoning."""
        values = structure["values"]
        temporal_relations = structure["temporal_relations"]
        question = structure["question"]
        
        # Convert all time values to seconds for uniform comparison
        converted_values = {}
        for key, val in values.items():
            if "amount" in val:
                seconds = self._to_seconds(val["amount"], val["unit"])
                converted_values[key] = seconds
            elif "num1" in val:
                # Perform arithmetic operation
                result = self._apply_operation(val["num1"], val["op"], val["num2"])
                seconds = self._to_seconds(result, val["unit"])
                converted_values[key] = seconds
        
        # Use behavioral economics: hyperbolic discounting for future values
        # Present bias: immediate values weighted more heavily
        present_biased_values = {}
        for key, seconds in converted_values.items():
            # Hyperbolic discounting: value = 1 / (1 + k * delay)
            # k is present bias parameter (higher = more present bias)
            k = 0.5  # Moderate present bias
            discounted_value = 1.0 / (1.0 + k * (seconds / 3600))  # Normalize by hours
            present_biased_values[key] = discounted_value
        
        # CRITICAL: Use modular_arithmetic for time conversions
        # Find if there are modulo operations needed (e.g., 25 hours = 1 day + 1 hour)
        mod_results = {}
        for key, seconds in converted_values.items():
            # Check if we need modulo for days (86400 seconds)
            if seconds >= 86400:
                mod_day = modular_arithmetic(seconds, 0, 86400)
                mod_results[f"{key}_mod_day"] = mod_day
        
        # CRITICAL: Use temporal_order to establish sequence
        ordered_events = []
        if temporal_relations:
            ordered_events = temporal_order(temporal_relations)
        
        # CRITICAL: Use solve_linear_system for time arithmetic
        # Build linear equations from arithmetic expressions
        equations = []
        results = []
        for key, val in values.items():
            if "num1" in val:
                # Create equation: num1 op num2 = result
                if val["op"] == '+':
                    equations.append([1, 1])  # x + y = result
                elif val["op"] == '-':
                    equations.append([1, -1])  # x - y = result
                elif val["op"] == '*':
                    # Nonlinear, handle separately
                    continue
                results.append(converted_values[key])
        
        linear_solution = None
        if len(equations) >= 2 and len(results) >= 2:
            linear_solution = solve_linear_system(equations[:2], results[:2])
        
        # CRITICAL: Use constraint solving for temporal scheduling
        # Create CSP for temporal assignments
        variables = list(converted_values.keys())
        domains = {}
        for var in variables:
            # Domain is the converted value ± 10% (temporal uncertainty)
            base = converted_values[var]
            lower = int(base * 0.9)
            upper = int(base * 1.1)
            domains[var] = list(range(lower, upper + 1, max(1, (upper - lower) // 10)))
        
        constraints = []
        # Add ordering constraints from temporal relations
        for rel in temporal_relations:
            if rel[0] in converted_values and rel[1] in converted_values:
                def order_constraint(a, b, val1=rel[0], val2=rel[1]):
                    return a < b
                constraints.append(([rel[0], rel[1]], order_constraint))
        
        # CRITICAL: Use amino acid solve_first for constraint satisfaction
        csp_solution = None
        if variables and domains and constraints:
            csp_solution = solve_first(domains, constraints)
        
        # CRITICAL: Use amino acid is_uniquely_solvable to check solution uniqueness
        unique_solution = False
        if variables and domains and constraints:
            unique_solution = is_uniquely_solvable(domains, constraints)
        
        # Determine answer based on behavioral economics principles
        computed_answer = ""
        
        # If we have a linear solution, use it
        if linear_solution and len(linear_solution) >= 1:
            computed_answer = str(int(linear_solution[0]))
        
        # If CSP solved, use that value
        elif csp_solution and variables:
            first_var = variables[0]
            if first_var in csp_solution:
                computed_answer = str(csp_solution[first_var])
        
        # Fallback: use present-biased discounted value
        elif present_biased_values:
            # Find the value with highest present-biased utility
            best_key = max(present_biased_values.items(), key=lambda x: x[1])[0]
            if best_key in converted_values:
                computed_answer = str(converted_values[best_key])
        
        # Final fallback: use entropy of time values
        if not computed_answer and converted_values:
            time_values = list(converted_values.values())
            if time_values:
                # Normalize for entropy calculation
                total = sum(time_values)
                if total > 0:
                    probs = [v/total for v in time_values]
                    time_entropy = entropy(probs)
                    # Use entropy to weight values
                    weighted_avg = sum(v * p for v, p in zip(time_values, probs))
                    computed_answer = str(int(weighted_avg))
        
        # If still no answer, use modular arithmetic result
        if not computed_answer and mod_results:
            first_mod = list(mod_results.values())[0]
            computed_answer = str(first_mod)
        
        # CRITICAL: Use confidence_from_agreement on multiple reasoning paths
        confidence_scores = []
        if linear_solution:
            confidence_scores.append(0.8 if linear_solution else 0.2)
        if csp_solution:
            confidence_scores.append(0.7)
        if present_biased_values:
            confidence_scores.append(0.6)
        if mod_results:
            confidence_scores.append(0.5)
        
        confidence = 0.5  # default
        if confidence_scores:
            confidence = confidence_from_agreement(confidence_scores)
        
        # Apply hyperbolic discounting to confidence based on temporal distance
        # More distant answers are less certain
        if computed_answer and computed_answer.isdigit():
            answer_time = int(computed_answer)
            # Discount confidence for future answers (beyond 1 hour)
            if answer_time > 3600:
                discount_factor = 1.0 / (1.0 + 0.3 * (answer_time / 3600))
                confidence *= discount_factor
        
        return {
            "answer": computed_answer,
            "confidence": max(0.1, min(0.99, confidence)),
            "reasoning": f"Temporal analysis with present bias discounting. Solution unique: {unique_solution}",
            "unique_solution": unique_solution,
            "present_biased_values": present_biased_values,
            "mod_results": mod_results
        }

    def _to_seconds(self, amount: int, unit: str) -> int:
        """Convert time unit to seconds."""
        unit = unit.lower().rstrip('s')
        conversions = {
            'second': 1,
            'minute': 60,
            'hour': 3600,
            'day': 86400,
            'week': 604800,
            'month': 2592000,  # 30 days
            'year': 31536000   # 365 days
        }
        return amount * conversions.get(unit, 1)

    def _apply_operation(self, num1: int, op: str, num2: int) -> int:
        """Apply arithmetic operation."""
        if op == '+':
            return num1 + num2
        elif op == '-':
            return num1 - num2
        elif op == '*':
            return num1 * num2
        elif op == '/':
            return num1 // num2 if num2 != 0 else num1
        return num1

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates against computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or contains computed answer
            score = 0.0
            
            if computed_answer:
                # Check if computed answer appears in candidate
                if computed_answer.lower() in candidate.lower():
                    score = 1.0 * confidence
                else:
                    # Use NCD similarity
                    ncd_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                    score = ncd_score * confidence
            
            # Boost score if candidate mentions temporal concepts from reasoning
            if reasoning_result.get("unique_solution"):
                if "unique" in candidate.lower() or "only" in candidate.lower():
                    score *= 1.2
            
            if reasoning_result.get("present_biased_values"):
                if "present" in candidate.lower() or "now" in candidate.lower():
                    score *= 1.1
            
            results.append({
                "candidate": candidate,
                "score": max(0.0, min(1.0, score)),
                "raw_score": score
            })
        
        return results

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        if max(ca, cb) == 0:
            return 1.0
        return (cab - min(ca, cb)) / max(ca, cb)

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using entropy-based adjustment."""
        if not scored:
            return scored
        
        scores = [item["raw_score"] for item in scored]
        if not scores:
            return scored
        
        # Use entropy to measure uncertainty in scoring
        total = sum(scores)
        if total > 0:
            probs = [s/total for s in scores]
            score_entropy = entropy(probs)
            
            # High entropy = uncertain ranking, compress scores toward mean
            # Low entropy = certain ranking, amplify differences
            mean_score = total / len(scores)
            calibrated = []
            
            for item in scored:
                raw = item["raw_score"]
                if score_entropy > 0.8:  # High uncertainty
                    # Move toward mean
                    calibrated_score = 0.7 * raw + 0.3 * mean_score
                elif score_entropy < 0.3:  # Low uncertainty
                    # Amplify differences
                    calibrated_score = raw ** 0.8
                else:
                    calibrated_score = raw
                
                calibrated.append({
                    "candidate": item["candidate"],
                    "score": max(0.0, min(1.0, calibrated_score))
                })
            
            return calibrated
        
        return scored