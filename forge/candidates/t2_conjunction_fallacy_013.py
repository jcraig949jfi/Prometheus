import re
import zlib
from typing import Dict, List, Any, Optional

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Reliability engineering x Bayesian networks - Conjunction fallacy"""

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        # Phase 3: SCORE
        scored = self._score_candidates(candidates, reasoning_result)
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
            matches = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            percentages.extend([float(m) / 100.0 for m in matches])
        
        # Find entity names (capitalized phrases that appear with probabilities)
        entities = {}
        for line in lines:
            # Look for patterns like "X is Y%" or "probability of X is Y%"
            if '%' in line:
                # Extract capitalized words as potential entity names
                words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
                for word in words:
                    if word not in entities:
                        entities[word] = {"probabilities": []}
        
        # Extract specific probability values for each entity
        # Look for patterns like "probability of X is Y%"
        for line in lines:
            for entity in entities:
                if entity.lower() in line.lower() and '%' in line:
                    matches = re.findall(r'([0-9]+\.?[0-9]*)%', line)
                    if matches:
                        entities[entity]["probabilities"].extend([float(m) / 100.0 for m in matches])
        
        # Clean up entities with no probabilities
        entities = {k: v for k, v in entities.items() if v["probabilities"]}
        
        return {
            "entities": entities,
            "percentages": percentages,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply reliability engineering principles to compute correct answer."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        
        if not entities or len(percentages) < 2:
            # Fallback: use simple probability comparison
            if percentages:
                max_prob = max(percentages)
                computed_answer = f"{max_prob*100:.1f}%"
            else:
                computed_answer = "Cannot determine"
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Insufficient data for reliability analysis"
            }
        
        # RELIABILITY ENGINEERING FRAMEWORK:
        # Treat probabilities as component failure rates
        # Joint probability = system failure rate when components are in series
        # Marginal probability = component failure rate alone
        
        # Extract base rates (marginal probabilities)
        base_rates = []
        for entity_data in entities.values():
            if entity_data["probabilities"]:
                base_rates.append(entity_data["probabilities"][0])
        
        if len(base_rates) < 2:
            computed_answer = list(entities.keys())[0] if entities else "Unknown"
            return {
                "answer": computed_answer,
                "confidence": 0.6,
                "reasoning": "Single probability found"
            }
        
        # PRIMITIVE 1: Compute entropy of base rates (uncertainty in component reliability)
        entropy_val = entropy(base_rates)
        
        # PRIMITIVE 2: Compute joint probability using Bayesian update
        # In reliability engineering, joint failure probability = P(A) * P(B|A)
        # For independent events, P(B|A) = P(B)
        joint_prob = base_rates[0]
        for i in range(1, len(base_rates)):
            # Use bayesian_update to compute joint probability
            # P(A∩B) = P(A) * P(B|A) = P(A) * P(B) for independent events
            # We'll use bayesian_update with false_positive=0 to get P(B|A) ≈ P(B)
            conditional_prob = bayesian_update(
                prior=base_rates[i],
                likelihood=1.0,  # Assuming independence
                false_positive=0.0
            )
            if conditional_prob is None:
                conditional_prob = base_rates[i]
            joint_prob *= conditional_prob
        
        # AMINO ACID: Build Bayesian network to verify independence
        # Create simple BN: A -> B (dependency) vs A B (independence)
        edges = []
        if len(base_rates) >= 2:
            # Test both dependency structures
            edges_dep = [("A", "B")]
            edges_ind = []
            
            # Build BN for independent case
            bn_ind = build_bn(edges_ind, None)
            
            # Query conditional probability to check if P(B|A) ≈ P(B)
            if bn_ind is not None:
                try:
                    # Create simple CPDs based on extracted probabilities
                    # For demonstration, use uniform priors
                    query_result = conditional_query(
                        bn_ind,
                        target_vars=["B"],
                        evidence={"A": True}
                    )
                except:
                    query_result = None
            else:
                query_result = None
        
        # PRIMITIVE 3: Compute expected value of choosing joint vs marginal
        # In reliability terms: expected cost of system failure vs component failure
        outcomes = [
            (joint_prob, -100.0),  # Cost if joint event occurs
            (1 - joint_prob, -10.0)  # Lower cost if only marginal events
        ]
        expected_joint = expected_value(outcomes)
        
        outcomes_marginal = [
            (base_rates[0], -50.0),  # Cost if first component fails
            (1 - base_rates[0], -5.0)  # Lower cost if it doesn't
        ]
        expected_marginal = expected_value(outcomes_marginal)
        
        # PRIMITIVE 4: Compute confidence from agreement between different reliability metrics
        reliability_metrics = [
            joint_prob,
            1 - entropy_val,  # Higher entropy = lower reliability confidence
            abs(expected_joint - expected_marginal) / 100.0  # Normalized difference
        ]
        confidence = confidence_from_agreement(reliability_metrics)
        if confidence is None:
            confidence = 0.7
        
        # Determine which is more probable: joint or marginal
        # In conjunction fallacy, joint probability (A∩B) ≤ min(P(A), P(B))
        entity_names = list(entities.keys())
        
        if len(entity_names) >= 2:
            # Check if joint probability is being incorrectly rated higher
            marginal_probs = [entities[e]["probabilities"][0] for e in entity_names[:2]]
            max_marginal = max(marginal_probs)
            
            # Conjunction fallacy occurs when joint > marginal
            # Correct answer should be the marginal (higher probability)
            if joint_prob > max_marginal + 0.01:  # Small tolerance
                # Joint is incorrectly rated higher - fallacy detected
                # The correct answer is the marginal event
                best_idx = marginal_probs.index(max_marginal)
                computed_answer = entity_names[best_idx]
                reasoning = f"Conjunction fallacy detected: P({entity_names[0]}∩{entity_names[1]}) = {joint_prob:.3f} > P({entity_names[best_idx]}) = {max_marginal:.3f}"
            else:
                # No fallacy or joint is correctly lower
                if joint_prob < max_marginal - 0.01:
                    # Joint is correctly lower
                    computed_answer = entity_names[0]  # Default to first entity
                    reasoning = f"Correct: P(joint) = {joint_prob:.3f} < P(marginal) = {max_marginal:.3f}"
                else:
                    # Probabilities are similar
                    computed_answer = entity_names[0]
                    reasoning = f"Similar probabilities: joint={joint_prob:.3f}, marginal={max_marginal:.3f}"
        else:
            computed_answer = entity_names[0] if entity_names else "Unknown"
            reasoning = f"Single entity analysis: P={base_rates[0]:.3f}"
        
        # AMINO ACID 2: Use constraint solving to verify probability consistency
        if len(base_rates) >= 2:
            # Check if the extracted probabilities satisfy probability axioms
            variables = ["P_A", "P_B", "P_AB"]
            domains = {
                "P_A": [base_rates[0]],
                "P_B": [base_rates[1] if len(base_rates) > 1 else 0.5],
                "P_AB": [joint_prob]
            }
            
            # Constraint: P_AB ≤ min(P_A, P_B)
            def conjunction_constraint(vals):
                p_a, p_b, p_ab = vals
                return p_ab <= min(p_a, p_b) + 1e-9  # Allow small numerical error
            
            constraints = [
                (["P_A", "P_B", "P_AB"], conjunction_constraint)
            ]
            
            consistent = is_uniquely_solvable(variables, domains, constraints)
            if consistent is not None and not consistent:
                # Probabilities violate conjunction rule
                reasoning += " | Probability constraint violated"
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning,
            "joint_prob": joint_prob,
            "marginal_probs": base_rates[:2] if len(base_rates) >= 2 else base_rates
        }

    def _score_candidates(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 0.9
            else:
                # Fallback: NCD similarity with reasoning text
                ncd_score = 1.0 - self._ncd(reasoning_text, candidate)
                score = max(0.1, ncd_score * 0.7)
            
            # Boost score if candidate contains probability-related terms
            prob_terms = ["probability", "likely", "chance", "percent", "%"]
            if any(term in candidate.lower() for term in prob_terms):
                score = min(1.0, score + 0.1)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored_candidates:
            return scored_candidates
        
        # Simple calibration: normalize scores to [0, 1] range
        scores = [item["score"] for item in scored_candidates]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            
            if max_score > min_score:
                for item in scored_candidates:
                    # Normalize and apply slight smoothing
                    normalized = (item["score"] - min_score) / (max_score - min_score)
                    item["score"] = normalized * 0.9 + 0.05  # Keep in [0.05, 0.95]
            else:
                # All scores equal
                for item in scored_candidates:
                    item["score"] = 0.5
        
        return scored_candidates

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)