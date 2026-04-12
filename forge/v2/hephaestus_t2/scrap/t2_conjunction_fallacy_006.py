import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query


class ReasoningTool:
    """Chemical kinetics x Bayesian networks - Conjunction fallacy"""

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
        
        # Find entity names (capitalized phrases)
        entities = []
        for line in lines:
            # Look for patterns like "Linda is a bank teller"
            name_matches = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
            for name in name_matches:
                if name.lower() not in ['the', 'and', 'but', 'however', 'therefore']:
                    if name not in entities and len(name.split()) <= 3:
                        entities.append(name)
        
        # Find conjunction phrases (A and B)
        conjunctions = []
        for line in lines:
            if ' and ' in line.lower():
                # Look for patterns like "bank teller and feminist"
                conj_matches = re.findall(r'(\w+(?:\s+\w+)*)\s+and\s+(\w+(?:\s+\w+)*)', line, re.IGNORECASE)
                for a, b in conj_matches:
                    conjunctions.append(f"{a} and {b}")
        
        return {
            "percentages": percentages,
            "entities": entities,
            "conjunctions": conjunctions,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply chemical kinetics framework to probability reasoning."""
        percentages = structure["percentages"]
        entities = structure["entities"]
        conjunctions = structure["conjunctions"]
        question = structure["question"]
        
        if len(percentages) < 2:
            # Fallback: use simple comparison if not enough data
            computed_answer = "marginal probability" if "marginal" in question.lower() else "joint probability"
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Insufficient data for detailed analysis"
            }
        
        # Chemical kinetics analogy: probabilities as reaction rates
        # P(A) and P(B) are like reactant concentrations
        # P(A∧B) is like product formation rate
        
        # Extract base probabilities (assuming first two are P(A) and P(B))
        if len(percentages) >= 2:
            p_a = percentages[0]
            p_b = percentages[1]
        else:
            p_a = p_b = 0.5
        
        # Extract joint probability if available (third percentage)
        if len(percentages) >= 3:
            p_joint = percentages[2]
        else:
            # Estimate joint as product if independent (worst-case for fallacy)
            p_joint = p_a * p_b
        
        # T1 PRIMITIVE 1: entropy of the probability distribution
        # Higher entropy = more uncertainty = less likely conjunction is higher
        prob_dist = [p_a, p_b, p_joint]
        if sum(prob_dist) > 0:
            normalized = [p / sum(prob_dist) for p in prob_dist]
        else:
            normalized = [0.33, 0.33, 0.34]
        
        entropy_val = entropy(normalized)
        
        # T1 PRIMITIVE 2: expected value of choosing conjunction vs marginal
        # Treat as decision problem: expected utility of each choice
        outcomes_conjunction = [(p_joint, 1.0), (1 - p_joint, 0.0)]
        outcomes_marginal = [(p_a, 1.0), (1 - p_a, 0.0)]
        
        ev_conjunction = expected_value(outcomes_conjunction)
        ev_marginal = expected_value(outcomes_marginal)
        
        # Amino acid: Build Bayesian network to check logical consistency
        # Variables: A, B, A_and_B
        edges = [("A", "A_and_B"), ("B", "A_and_B")]
        
        # CPD for A_and_B: deterministic AND gate
        cpd_specs = {
            "A": {"values": [[p_a], [1 - p_a]]},
            "B": {"values": [[p_b], [1 - p_b]]},
            "A_and_B": {
                "values": [
                    [1.0, 0.0, 0.0, 1.0],  # P(A_and_B=1 | A,B)
                    [0.0, 1.0, 1.0, 0.0]   # P(A_and_B=0 | A,B)
                ],
                "evidence": ["A", "B"],
                "evidence_card": [2, 2]
            }
        }
        
        try:
            model = build_bn(edges, cpd_specs)
            # Query P(A_and_B=1)
            query_result = conditional_query(model, ["A_and_B"], {})
            
            if query_result and "A_and_B" in query_result:
                bn_joint = query_result["A_and_B"].get(1, 0.0)
            else:
                bn_joint = p_a * p_b  # Fallback to independence assumption
        except Exception:
            bn_joint = p_a * p_b  # Fallback
        
        # T1 PRIMITIVE 3: bayesian update to adjust confidence
        # Prior: conjunction fallacy is common (0.7)
        # Likelihood: based on comparison of probabilities
        prior = 0.7  # Prior belief that people commit the fallacy
        likelihood = 1.0 if p_joint > min(p_a, p_b) else 0.3
        posterior = bayesian_update(prior, likelihood)
        
        # Determine which is actually larger
        correct_larger = p_joint <= min(p_a, p_b)  # Joint should be ≤ each marginal
        
        # T1 PRIMITIVE 4: confidence from agreement of multiple indicators
        indicators = []
        if correct_larger:
            indicators.append(1.0)
        else:
            indicators.append(0.0)
        
        if bn_joint <= min(p_a, p_b):
            indicators.append(1.0)
        else:
            indicators.append(0.0)
        
        if ev_marginal >= ev_conjunction:
            indicators.append(1.0)
        else:
            indicators.append(0.0)
        
        confidence = confidence_from_agreement(indicators) if indicators else 0.5
        
        # Chemical kinetics decision: reaction favorability
        # ΔG = -RT ln(K) where K = P_joint / (P_A * P_B)
        # If K < 1, reaction unfavorable (conjunction less likely)
        if p_a * p_b > 0:
            k_ratio = p_joint / (p_a * p_b)
        else:
            k_ratio = 1.0
        
        # Final decision based on multiple factors
        if k_ratio <= 1.0 and correct_larger and bn_joint <= min(p_a, p_b):
            computed_answer = "joint probability is less than or equal to marginal probability"
            final_confidence = max(confidence, posterior)
        else:
            # Check if this might be a fallacy case
            if p_joint > min(p_a, p_b):
                computed_answer = "conjunction fallacy may occur"
            else:
                computed_answer = "joint probability is less than or equal to marginal probability"
            final_confidence = confidence
        
        # Select appropriate entity name for answer
        answer_entity = "probability comparison"
        if entities:
            answer_entity = entities[0]
        elif conjunctions:
            answer_entity = conjunctions[0]
        
        return {
            "answer": f"{answer_entity}: {computed_answer}",
            "confidence": final_confidence,
            "reasoning": f"Chemical kinetics analysis: K={k_ratio:.3f}, entropy={entropy_val:.3f}, EV_marginal={ev_marginal:.3f}, EV_conjunction={ev_conjunction:.3f}",
            "key_value": computed_answer
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["key_value"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
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

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            normalized = [(s - min(scores)) / (max(scores) - min(scores)) for s in scores]
        else:
            normalized = [0.5 for _ in scores]
        
        for i, item in enumerate(scored):
            item["score"] = normalized[i]
        
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