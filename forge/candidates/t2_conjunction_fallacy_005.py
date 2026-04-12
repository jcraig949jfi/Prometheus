import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query


class ReasoningTool:
    """Signal_processing x Bayesian networks - Conjunction_fallacy"""

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
        """Parse prompt to extract entities, probabilities, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all percentage values
        percentages = []
        for line in lines:
            matches = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            percentages.extend([float(m) / 100.0 for m in matches])
        
        # Find entity names (capitalized phrases that appear before percentages)
        entities = {}
        for line in lines:
            # Look for patterns like "Entity A has X%"
            words = line.split()
            for i, word in enumerate(words):
                if word.endswith('%') and i > 0:
                    # Look backward for entity name
                    entity_candidate = words[i-1]
                    if entity_candidate[0].isupper():
                        # Try to get the percentage value
                        pct_match = re.search(r'([0-9]+\.?[0-9]*)%', word)
                        if pct_match:
                            pct = float(pct_match.group(1)) / 100.0
                            if entity_candidate not in entities:
                                entities[entity_candidate] = []
                            entities[entity_candidate].append(pct)
        
        # Also look for conjunction phrases like "A and B"
        conjunction_phrases = []
        for line in lines:
            if ' and ' in line.lower():
                # Find capitalized words around 'and'
                parts = line.split()
                for i in range(len(parts) - 2):
                    if parts[i+1].lower() == 'and' and parts[i][0].isupper() and parts[i+2][0].isupper():
                        conj = f"{parts[i]} and {parts[i+2]}"
                        conjunction_phrases.append(conj)
        
        return {
            "percentages": percentages,
            "entities": entities,
            "conjunction_phrases": conjunction_phrases,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply signal processing concepts to analyze joint vs marginal probabilities."""
        percentages = structure["percentages"]
        entities = structure["entities"]
        question = structure["question"]
        
        # Signal processing framework: treat probabilities as signal amplitudes,
        # conjunction as signal mixing, and use Bayesian networks as filters
        
        # 1. Use entropy to measure uncertainty in extracted probabilities
        if percentages:
            prob_dist = [p for p in percentages if 0 <= p <= 1]
            if len(prob_dist) >= 2:
                # Normalize to create a distribution
                total = sum(prob_dist)
                if total > 0:
                    normalized = [p/total for p in prob_dist]
                    uncertainty = entropy(normalized)
                else:
                    uncertainty = 1.0
            else:
                uncertainty = 1.0
        else:
            uncertainty = 1.0
        
        # 2. Build Bayesian network to model conjunction relationship
        # Signal processing view: events are signals, conjunction is AND gate
        edges = [("A", "A_and_B"), ("B", "A_and_B")]
        
        # Extract base probabilities from entities
        base_probs = {}
        for entity, probs in entities.items():
            if probs:
                base_probs[entity] = probs[0]
        
        # Create CPDs using extracted probabilities
        cpd_specs = {}
        if "A" in base_probs and "B" in base_probs:
            p_a = base_probs["A"]
            p_b = base_probs["B"]
            
            # Assume independence for conjunction: P(A∧B) = P(A)*P(B)
            # This is the correct calculation that should be compared to fallacious intuition
            p_conjunction = p_a * p_b
            
            # Build CPD for A_and_B given parents A and B
            # P(A_and_B=1 | A=1, B=1) = 1, else 0 (logical AND)
            cpd_specs["A"] = {"variable": "A", "card": 2, "values": [[1-p_a], [p_a]]}
            cpd_specs["B"] = {"variable": "B", "card": 2, "values": [[1-p_b], [p_b]]}
            cpd_specs["A_and_B"] = {
                "variable": "A_and_B",
                "card": 2,
                "parents": ["A", "B"],
                "values": [[1.0, 1.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]  # AND gate truth table
            }
        
        # 3. Use amino acid to build Bayesian network
        model = None
        conj_prob_from_bn = None
        if cpd_specs:
            model = build_bn(edges, cpd_specs)
            
            # Query the conjunction probability
            if model:
                # Query P(A_and_B=1)
                query_result = conditional_query(model, ["A_and_B"], {})
                if query_result and "A_and_B" in query_result:
                    conj_prob_from_bn = query_result["A_and_B"].get(1, 0.0)
        
        # 4. Use expected_value primitive to compute weighted average if multiple probabilities
        outcomes = []
        for p in percentages:
            if 0 <= p <= 1:
                # Weight each probability equally
                outcomes.append((1.0/len(percentages), p))
        
        avg_prob = 0.0
        if outcomes:
            avg_prob = expected_value(outcomes)
        
        # 5. Determine which is larger: conjunction or one of the marginals
        computed_answer = ""
        confidence = 0.5
        
        if "A" in base_probs and "B" in base_probs and conj_prob_from_bn is not None:
            p_a = base_probs["A"]
            p_b = base_probs["B"]
            p_conj = conj_prob_from_bn
            
            # Signal processing decision: compare power (probability) levels
            # The conjunction fallacy occurs when people think P(A∧B) > P(A) or P(A∧B) > P(B)
            # But by probability theory, P(A∧B) ≤ min(P(A), P(B))
            
            # Use bayesian_update to incorporate uncertainty into decision
            # Prior: equal chance that conjunction is smaller or larger (should be smaller)
            prior = 0.5
            # Likelihood: based on actual comparison
            if p_conj < min(p_a, p_b):
                # Conjunction is correctly smaller
                likelihood = 0.9
            else:
                # This would be mathematically impossible under independence
                likelihood = 0.1
            
            posterior = bayesian_update(prior, likelihood)
            
            # Determine answer based on posterior
            if posterior > 0.5:
                # Conjunction is smaller (correct)
                if p_a <= p_b:
                    computed_answer = f"P(A and B) < P({list(base_probs.keys())[0]})"
                else:
                    computed_answer = f"P(A and B) < P({list(base_probs.keys())[1]})"
                confidence = posterior
            else:
                # Fallacious thinking (should rarely happen)
                computed_answer = "P(A and B) could be larger"
                confidence = 1 - posterior
        elif entities:
            # Fallback: use the entity with highest probability
            if entities:
                max_entity = max(entities.items(), key=lambda x: x[1][0] if x[1] else 0)
                computed_answer = f"{max_entity[0]} has highest probability"
                confidence = 0.7
        
        # 6. Use confidence_from_agreement to combine multiple confidence sources
        confidence_sources = []
        if uncertainty < 0.8:  # Lower uncertainty gives higher confidence
            confidence_sources.append(1.0 - uncertainty)
        if conj_prob_from_bn is not None:
            confidence_sources.append(0.8)
        if avg_prob > 0:
            confidence_sources.append(min(avg_prob, 0.9))
        
        if confidence_sources:
            combined_confidence = confidence_from_agreement(confidence_sources)
            # Blend with existing confidence
            confidence = (confidence + combined_confidence) / 2.0
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "conjunction_prob": conj_prob_from_bn,
            "marginal_probs": base_probs,
            "uncertainty": uncertainty,
            "reasoning": f"Signal processing analysis: probabilities as amplitudes, conjunction as mixing. Entropy={uncertainty:.3f}, BN conjunction prob={conj_prob_from_bn if conj_prob_from_bn else 'N/A'}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            score = 0.0
            
            # Convert both to lowercase for comparison
            comp_lower = computed_answer.lower()
            cand_lower = candidate.lower()
            
            # Check for direct containment
            if comp_lower in cand_lower:
                score = 0.9 + (confidence * 0.1)
            else:
                # Check for key concepts from reasoning
                key_terms = ["conjunction", "probability", "less than", "greater than", "P(A", "P(B"]
                matches = sum(1 for term in key_terms if term.lower() in cand_lower)
                if matches >= 2:
                    score = 0.6 + (confidence * 0.2)
                else:
                    # Fallback: NCD similarity to reasoning text
                    ncd_score = self._ncd(reasoning_text, candidate)
                    score = 0.3 + (ncd_score * 0.3)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores based on confidence."""
        calibrated = []
        for item in scored:
            score = item["score"]
            conf = item["confidence"]
            
            # Adjust score based on confidence
            # Higher confidence strengthens high scores, weakens low scores
            if score > 0.5:
                adjusted = score * (0.7 + 0.3 * conf)
            else:
                adjusted = score * (0.3 + 0.7 * conf)
            
            # Ensure score is in [0, 1]
            adjusted = max(0.0, min(1.0, adjusted))
            
            calibrated.append({
                "candidate": item["candidate"],
                "score": adjusted
            })
        
        return calibrated

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