import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query


class ReasoningTool:
    """Mechanism Design x Bayesian Networks - Conjunction Fallacy"""

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
        """Extract entities, probabilities, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all percentage values
        percentages = []
        for line in lines:
            matches = re.findall(r'(\d+(?:\.\d+)?)%', line)
            percentages.extend([float(m) / 100.0 for m in matches])
        
        # Find entity names (capitalized phrases that appear before percentages)
        entities = {}
        for line in lines:
            # Look for patterns like "Entity has X% probability"
            match = re.search(r'([A-Z][a-zA-Z\s]+?)\s+(?:has|with|probability)', line)
            if match:
                entity = match.group(1).strip()
                if entity not in entities:
                    entities[entity] = {"probabilities": []}
                # Find percentages in the same line
                line_percentages = re.findall(r'(\d+(?:\.\d+)?)%', line)
                for pct in line_percentages:
                    entities[entity]["probabilities"].append(float(pct) / 100.0)
        
        # If no entities found via pattern, use generic ones
        if not entities:
            entities = {
                "Event_A": {"probabilities": percentages[:1] if percentages else [0.5]},
                "Event_B": {"probabilities": percentages[1:2] if len(percentages) > 1 else [0.5]},
                "Both": {"probabilities": percentages[2:3] if len(percentages) > 2 else [0.3]}
            }
        
        # Extract base rates if mentioned
        base_rate = 0.5
        for line in lines:
            if "base rate" in line.lower() or "prior" in line.lower():
                matches = re.findall(r'(\d+(?:\.\d+)?)%', line)
                if matches:
                    base_rate = float(matches[0]) / 100.0
        
        return {
            "entities": entities,
            "percentages": percentages,
            "question": question,
            "base_rate": base_rate,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mechanism design principles to analyze joint vs marginal probabilities."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        base_rate = structure["base_rate"]
        
        # Mechanism Design: Treat probabilities as agents with incentives
        # The conjunction fallacy occurs when P(A & B) > P(A) or P(B)
        # We'll design a mechanism that penalizes such inconsistencies
        
        # Extract key probabilities from the prompt
        if len(percentages) >= 3:
            p_a = percentages[0] if percentages else 0.5
            p_b = percentages[1] if len(percentages) > 1 else 0.5
            p_both = percentages[2] if len(percentages) > 2 else 0.3
        else:
            # Use entity probabilities if available
            entity_probs = []
            for entity, data in entities.items():
                if data["probabilities"]:
                    entity_probs.append(data["probabilities"][0])
            
            if len(entity_probs) >= 3:
                p_a, p_b, p_both = entity_probs[:3]
            else:
                # Default values for testing
                p_a, p_b, p_both = 0.5, 0.5, 0.3
        
        # CRITICAL PRIMITIVE 1: Bayesian update to compute posterior
        # Using base_rate as prior, p_both as likelihood
        posterior = bayesian_update(base_rate, p_both)
        if posterior is None:
            posterior = base_rate
        
        # CRITICAL PRIMITIVE 2: Entropy of the probability distribution
        # Measure uncertainty in the probability assignments
        prob_dist = [p_a, p_b, p_both]
        # Normalize to sum to 1 for entropy calculation
        total = sum(prob_dist)
        if total > 0:
            normalized = [p/total for p in prob_dist]
        else:
            normalized = [0.33, 0.33, 0.34]
        
        uncertainty = entropy(normalized)
        if uncertainty is None:
            uncertainty = 0.5
        
        # CRITICAL AMINO ACID: Build Bayesian network to check consistency
        # Create a simple BN: A -> Both <- B
        edges = [("A", "Both"), ("B", "Both")]
        
        # Define CPDs based on extracted probabilities
        cpd_specs = {
            "A": {"variable": "A", "variable_card": 2, "values": [[1-p_a], [p_a]]},
            "B": {"variable": "B", "variable_card": 2, "values": [[1-p_b], [p_b]]},
            "Both": {
                "variable": "Both", 
                "variable_card": 2,
                "values": [
                    [1-p_both, 1-p_both, 1-p_both, 1-p_both],  # P(Both=0 | A,B)
                    [p_both, p_both, p_both, p_both]           # P(Both=1 | A,B)
                ],
                "evidence": ["A", "B"],
                "evidence_card": [2, 2]
            }
        }
        
        model = build_bn(edges, cpd_specs)
        
        # CRITICAL: Query the BN for P(Both=1)
        bn_result = None
        if model is not None:
            bn_result = conditional_query(model, ["Both"], {})
        
        # Mechanism Design: Compute expected value of different choices
        # Options: choose marginal (A or B) vs conjunction (Both)
        outcomes_marginal = [(p_a, 1.0), (1-p_a, 0.0)]  # (prob, value)
        outcomes_conjunction = [(p_both, 1.0), (1-p_both, 0.0)]
        
        ev_marginal = expected_value(outcomes_marginal)
        ev_conjunction = expected_value(outcomes_conjunction)
        
        if ev_marginal is None:
            ev_marginal = p_a
        if ev_conjunction is None:
            ev_conjunction = p_both
        
        # CRITICAL PRIMITIVE 3: Confidence from agreement between different methods
        # Compare BN result with direct probability
        bn_prob = bn_result[("Both", 1)] if bn_result and ("Both", 1) in bn_result else p_both
        confidence_scores = [p_both, bn_prob, posterior]
        confidence = confidence_from_agreement(confidence_scores)
        if confidence is None:
            confidence = 0.5
        
        # Mechanism Design decision: Which is the rational choice?
        # If P(Both) > min(P(A), P(B)), flag as potential fallacy
        is_fallacy = p_both > min(p_a, p_b)
        
        # Determine correct answer based on probability theory
        if is_fallacy:
            # Conjunction fallacy detected - marginal probability should be higher
            correct_entity = "marginal probability"
            if p_a >= p_b:
                correct_value = f"{p_a*100:.1f}%"
            else:
                correct_value = f"{p_b*100:.1f}%"
        else:
            # No fallacy - conjunction might be correct if properly computed
            correct_entity = "conjunction probability"
            correct_value = f"{p_both*100:.1f}%"
        
        # Use BN result if available and different from direct computation
        if bn_result and abs(bn_prob - p_both) > 0.01:
            correct_entity = "Bayesian network result"
            correct_value = f"{bn_prob*100:.1f}%"
        
        return {
            "answer": correct_entity,
            "correct_value": correct_value,
            "p_a": p_a,
            "p_b": p_b,
            "p_both": p_both,
            "posterior": posterior,
            "uncertainty": uncertainty,
            "ev_marginal": ev_marginal,
            "ev_conjunction": ev_conjunction,
            "confidence": confidence,
            "is_fallacy": is_fallacy,
            "bn_prob": bn_prob if bn_result else None
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        correct_value = reasoning_result["correct_value"]
        
        # Create a full answer string for NCD comparison
        full_answer = f"{computed_answer} ({correct_value})"
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            score = 0.0
            
            # Check for computed answer in candidate
            if computed_answer.lower() in candidate.lower():
                score += 0.7
            
            # Check for correct value in candidate
            if correct_value in candidate:
                score += 0.3
            
            # If no direct match, use NCD as fallback
            if score == 0.0:
                ncd_score = self._ncd(full_answer, candidate)
                score = 1.0 / (1.0 + ncd_score)
            
            # Adjust score based on confidence from reasoning
            confidence = reasoning_result.get("confidence", 0.5)
            score *= confidence
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Normalize scores to 0-1 range
        scores = [item["raw_score"] for item in scored]
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 1
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
        else:
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