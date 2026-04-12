import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, solve_linear_system
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Social choice theory x Constraint satisfaction - Rate of change"""

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
        """Extract entities, values, time points, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all entities (capitalized multi-word phrases that appear with values)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        entities = {}
        
        # Find numerical values with potential time indicators
        time_points = []
        value_pattern = r'([0-9]+\.?[0-9]*)\s*(?:%|units?|points?)?'
        
        for line in lines:
            # Extract time references
            if re.search(r'(?:year|month|day|time|period|t\d*|point)', line.lower()):
                time_match = re.search(r'(?:year|month|day|time|period|t\d*|point)\s*(\d+)', line.lower())
                if time_match:
                    time_points.append(int(time_match.group(1)))
            
            # Extract entities and their values
            entity_matches = re.findall(entity_pattern, line)
            value_matches = re.findall(value_pattern, line)
            
            for entity in entity_matches:
                if entity not in entities:
                    entities[entity] = {"values": [], "times": [], "raw_line": line}
                
                # Convert values to float (handle percentages)
                for val_str in value_matches:
                    try:
                        val = float(val_str)
                        # If line contains "%", treat as percentage
                        if '%' in line:
                            val = val / 100.0
                        entities[entity]["values"].append(val)
                        # Associate with time if available
                        if time_points:
                            entities[entity]["times"].append(time_points[-1] if entities[entity]["times"] else 0)
                    except ValueError:
                        continue
        
        # Clean up entities with insufficient data
        entities = {k: v for k, v in entities.items() if len(v["values"]) >= 2}
        
        # Extract rate of change question type
        question_type = "unknown"
        if "rate" in question.lower() or "change" in question.lower():
            question_type = "rate"
        elif "increase" in question.lower() or "decrease" in question.lower():
            question_type = "direction"
        elif "value" in question.lower() or "amount" in question.lower():
            question_type = "value"
        
        return {
            "entities": entities,
            "question": question,
            "question_type": question_type,
            "time_points": sorted(set(time_points)) if time_points else [0, 1],
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply social choice theory to compute rate of change rankings."""
        entities = structure["entities"]
        question_type = structure["question_type"]
        
        if not entities:
            return {"answer": "No data", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Social choice theory: treat each time point as a voter, each entity's value as a preference
        # Compute Borda count across time points
        borda_scores = {}
        
        for entity, data in entities.items():
            values = data["values"]
            times = data.get("times", list(range(len(values))))
            
            if len(values) < 2:
                borda_scores[entity] = 0
                continue
            
            # CRITICAL PRIMITIVE 1: Solve linear system to find rate of change
            # Build system: value = a*time + b
            try:
                A = [[t, 1] for t in times[:len(values)]]
                b = values[:len(times)]
                coeffs = solve_linear_system(A, b)
                if coeffs is None:
                    # Fallback: simple difference
                    rate = (values[-1] - values[0]) / (times[-1] - times[0]) if len(times) > 1 else 0
                else:
                    rate = coeffs[0]  # slope = rate of change
            except Exception:
                rate = (values[-1] - values[0]) / max(1, (len(values) - 1))
            
            # CRITICAL PRIMITIVE 2: Compute entropy of value changes
            changes = [values[i] - values[i-1] for i in range(1, len(values))]
            if changes:
                # Normalize changes to probabilities
                abs_changes = [abs(c) for c in changes]
                total = sum(abs_changes)
                if total > 0:
                    probs = [c/total for c in abs_changes]
                    change_entropy = entropy(probs)
                else:
                    change_entropy = 0
            else:
                change_entropy = 0
            
            # CRITICAL AMINO ACID: Constraint satisfaction to check consistency
            # Build CSP: values should follow monotonic pattern if rate is consistent
            variables = [f"v{i}" for i in range(len(values))]
            domains = {v: ["inc", "dec", "equal"] for v in variables}
            
            constraints = []
            for i in range(1, len(values)):
                def monotonic_constraint(val1, val2, expected_dir):
                    if expected_dir == "inc":
                        return val1 == "inc" and val2 == "inc"
                    elif expected_dir == "dec":
                        return val1 == "dec" and val2 == "dec"
                    else:
                        return True
                
                expected_dir = "inc" if rate > 0 else "dec" if rate < 0 else "equal"
                constraints.append(([variables[i-1], variables[i]], 
                                  lambda x,y,d=expected_dir: monotonic_constraint(x,y,d)))
            
            # Check if pattern is uniquely solvable (consistent monotonic behavior)
            consistency_check = is_uniquely_solvable(domains, constraints)
            
            # Find first consistent assignment
            solution = solve_first(domains, constraints)
            
            # Score based on rate, entropy, and consistency
            base_score = abs(rate) * 100  # Magnitude of change
            
            # Adjust for consistency
            consistency_bonus = 1.0 if solution is not None else 0.5
            if consistency_check:
                consistency_bonus *= 1.2
            
            # Entropy penalty: more random changes = less predictable
            entropy_penalty = 1.0 - min(change_entropy, 0.8)
            
            borda_scores[entity] = base_score * consistency_bonus * entropy_penalty
        
        # CRITICAL PRIMITIVE 3: Bayesian update for confidence
        # Treat each entity's score as evidence for being the answer
        if borda_scores:
            max_score = max(borda_scores.values())
            min_score = min(borda_scores.values()) if len(borda_scores) > 1 else 0
            
            # Normalize scores to probabilities
            total = sum(borda_scores.values())
            if total > 0:
                probs = {e: s/total for e, s in borda_scores.items()}
                
                # Bayesian update: prior is uniform, likelihood is normalized score
                prior = 1.0 / len(borda_scores)
                best_entity = max(borda_scores.items(), key=lambda x: x[1])[0]
                likelihood = probs[best_entity]
                
                posterior = bayesian_update(prior, likelihood, false_positive=0.1)
                
                # CRITICAL PRIMITIVE 4: Confidence from agreement
                # Multiple scoring methods agreement
                scores_list = list(borda_scores.values())
                confidence = confidence_from_agreement(scores_list)
                
                # Final confidence combines Bayesian posterior and agreement
                final_confidence = (posterior + confidence) / 2
            else:
                best_entity = list(borda_scores.keys())[0]
                final_confidence = 0.5
        else:
            best_entity = "Unknown"
            final_confidence = 0.0
        
        # Determine answer based on question type
        if question_type == "rate":
            if borda_scores:
                best_data = entities[best_entity]
                if len(best_data["values"]) >= 2:
                    rate_val = (best_data["values"][-1] - best_data["values"][0]) / max(1, len(best_data["values"]) - 1)
                    if abs(rate_val) < 0.01:  # Less than 1%
                        computed_answer = f"{best_entity}: {rate_val*100:.1f}% per period"
                    else:
                        computed_answer = f"{best_entity}: {rate_val:.3f} units per period"
                else:
                    computed_answer = best_entity
            else:
                computed_answer = "No calculable rate"
        elif question_type == "direction":
            if borda_scores:
                best_data = entities[best_entity]
                if best_data["values"][-1] > best_data["values"][0]:
                    computed_answer = f"{best_entity}: increasing"
                elif best_data["values"][-1] < best_data["values"][0]:
                    computed_answer = f"{best_entity}: decreasing"
                else:
                    computed_answer = f"{best_entity}: constant"
            else:
                computed_answer = "Unknown direction"
        else:  # value or unknown
            computed_answer = best_entity
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Social choice Borda count with constraint consistency check. Best: {best_entity}",
            "raw_scores": borda_scores
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Check for entity match
                entity_match = False
                for entity in reasoning_result.get("raw_scores", {}).keys():
                    if entity.lower() in candidate.lower():
                        entity_match = True
                        break
                
                if entity_match:
                    base_score = 0.7
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

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            for item in scored:
                item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        return (cab - min(ca, cb)) / max(ca, cb) if max(ca, cb) > 0 else 1.0