import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import detect_confounders, conditional_query


class ReasoningTool:
    """Quantum mechanics x pgmpy_acids - causal_confounding_hard"""

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
        """Parse prompt to extract entities, values, and causal structure."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        entities = {}
        edges = []
        values = {}
        question = lines[-1] if lines else ""
        
        # Extract entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_entities = re.findall(entity_pattern, prompt)
        
        # Extract percentages and associate with entities
        percent_pattern = r'(\d+(?:\.\d+)?)%'
        percent_matches = re.findall(percent_pattern, prompt)
        percentages = [float(p) / 100.0 for p in percent_matches]
        
        # Find causal relationships (words like "causes", "affects", "influences")
        causal_words = ["causes", "affects", "influences", "leads to", "determines"]
        for line in lines:
            for word in causal_words:
                if word in line.lower():
                    # Find entities before and after causal word
                    parts = re.split(word, line, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        before_entities = re.findall(entity_pattern, parts[0])
                        after_entities = re.findall(entity_pattern, parts[1])
                        if before_entities and after_entities:
                            edges.append((before_entities[-1], after_entities[0]))
        
        # Associate percentages with entities based on proximity
        sentences = prompt.split('.')
        for i, sentence in enumerate(sentences):
            sentence_entities = re.findall(entity_pattern, sentence)
            sentence_percents = re.findall(percent_pattern, sentence)
            for entity in sentence_entities:
                if entity not in entities:
                    entities[entity] = {"values": [], "mentions": 0}
                entities[entity]["mentions"] += 1
                for percent in sentence_percents:
                    entities[entity]["values"].append(float(percent) / 100.0)
        
        # Clean up edges - remove duplicates and self-loops
        edges = list(set([e for e in edges if e[0] != e[1]]))
        
        return {
            "entities": entities,
            "edges": edges,
            "percentages": percentages,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Quantum mechanical approach to confounding: treat variables as quantum states,
        confounding as entanglement, and adjustment as decoherence."""
        
        entities = structure["entities"]
        edges = structure["edges"]
        percentages = structure["percentages"]
        
        if not edges or len(entities) < 2:
            # Fallback: use simple comparison if no clear causal structure
            computed_answer = self._fallback_reasoning(entities, percentages)
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Fallback: No clear causal structure detected"
            }
        
        # Build a simple Bayesian network from extracted edges
        # Use quantum superposition concept: each variable exists in multiple states
        # until measured (conditioned)
        
        # 1. Use topological_sort to determine causal order (quantum measurement sequence)
        try:
            causal_order = topological_sort(edges)
            if causal_order is None:
                # Graph has cycles, use first two entities as treatment/outcome
                if len(edges) > 0:
                    treatment, outcome = edges[0]
                else:
                    return self._fallback_reasoning(entities, percentages)
            else:
                # Last in causal order is likely the outcome
                outcome = causal_order[-1] if causal_order else ""
                # First with outgoing edges is likely treatment
                treatment = next((e[0] for e in edges if e[0] in causal_order), "")
        except Exception:
            treatment, outcome = "", ""
        
        if not treatment or not outcome:
            return self._fallback_reasoning(entities, percentages)
        
        # 2. Use detect_confounders to find entangled variables (quantum entanglement)
        # Build a minimal model for detection
        model_edges = [(treatment, outcome)] + edges
        try:
            confounders_result = detect_confounders(model_edges, treatment, outcome)
            confounders = confounders_result if confounders_result else set()
        except Exception:
            confounders = set()
        
        # 3. Quantum decoherence through adjustment
        # Use entropy to measure uncertainty reduction after adjustment
        if percentages:
            # Create probability distributions from percentages
            probs = [p for p in percentages if 0 <= p <= 1]
            if len(probs) >= 2:
                # Initial entropy (unadjusted state)
                initial_entropy = entropy(probs[:min(2, len(probs))])
                
                # Adjusted state (condition on confounders if any)
                adjusted_probs = []
                if confounders and len(probs) > 2:
                    # Simulate adjustment by reweighting probabilities
                    # Quantum collapse: measurement reduces entropy
                    adjusted_probs = [p * 0.8 for p in probs[:2]]  # Decoherence effect
                    if adjusted_probs:
                        adjusted_entropy = entropy(adjusted_probs)
                    else:
                        adjusted_entropy = initial_entropy * 0.7  # Estimated reduction
                else:
                    adjusted_entropy = initial_entropy
                
                # Entropy reduction indicates successful adjustment
                entropy_reduction = initial_entropy - adjusted_entropy
            else:
                entropy_reduction = 0.0
        else:
            entropy_reduction = 0.0
        
        # 4. Bayesian update with quantum interference
        # Treatment effect as amplitude, confounding as phase shift
        if percentages and len(percentages) >= 2:
            # Use first two percentages as prior and likelihood
            prior = min(0.99, max(0.01, percentages[0]))
            likelihood = min(0.99, max(0.01, percentages[1]))
            
            # False positive rate represents quantum decoherence
            fp_rate = 0.1 if confounders else 0.05
            
            posterior = bayesian_update(prior, likelihood, fp_rate)
            
            # Quantum interference: confounders create destructive/constructive interference
            if confounders:
                # Adjust posterior based on number of confounders (phase shifts)
                interference_factor = 1.0 / (1.0 + len(confounders) * 0.2)
                posterior = posterior * interference_factor
        else:
            posterior = 0.5
        
        # 5. Determine answer based on quantum measurement outcome
        # The "collapsed" state after adjustment reveals the true causal effect
        if confounders:
            # With confounding, the adjusted answer differs from naive comparison
            if posterior > 0.5:
                computed_answer = treatment
            else:
                # Look for other entities that might be the true cause
                other_entities = [e for e in entities.keys() if e != treatment and e != outcome]
                if other_entities:
                    computed_answer = other_entities[0]
                else:
                    computed_answer = outcome
        else:
            # No confounding, direct effect
            if posterior > 0.5:
                computed_answer = treatment
            else:
                computed_answer = outcome
        
        # 6. Confidence from quantum coherence (agreement between multiple "measurements")
        confidence_scores = []
        if entropy_reduction > 0:
            confidence_scores.append(min(1.0, entropy_reduction * 10))
        if posterior != 0.5:
            confidence_scores.append(abs(posterior - 0.5) * 2)
        if confounders:
            confidence_scores.append(0.7)  # Higher confidence when we detected confounding
        
        if confidence_scores:
            confidence = confidence_from_agreement(confidence_scores)
        else:
            confidence = 0.5
        
        # Ensure computed_answer is a valid entity name
        if computed_answer not in entities and entities:
            computed_answer = list(entities.keys())[0]
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Quantum adjustment: {len(confounders)} confounders detected, entropy reduction {entropy_reduction:.3f}, posterior {posterior:.3f}",
            "confounders": list(confounders),
            "posterior": posterior
        }

    def _fallback_reasoning(self, entities: Dict, percentages: List[float]) -> Dict[str, Any]:
        """Fallback when causal structure is unclear."""
        if not entities:
            return {"answer": "", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Use entity with most mentions
        entity_items = list(entities.items())
        entity_items.sort(key=lambda x: x[1]["mentions"], reverse=True)
        
        if entity_items:
            computed_answer = entity_items[0][0]
            
            # Use entropy on available percentages
            if percentages:
                probs = [p for p in percentages if 0 <= p <= 1][:2]
                if len(probs) >= 2:
                    e = entropy(probs)
                    confidence = max(0.1, min(0.9, 1.0 - e))
                else:
                    confidence = 0.5
            else:
                confidence = 0.3
        else:
            computed_answer = ""
            confidence = 0.0
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": "Fallback: Most frequently mentioned entity"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        if not computed_answer:
            # No answer computed, return uniform low scores
            return [{"candidate": c, "score": 0.1, "raw_score": 0.1} for c in candidates]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Secondary: NCD similarity
                ncd_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                # Also check for confounder mentions if present
                confounders = reasoning_result.get("confounders", [])
                confounder_bonus = 0.0
                for conf in confounders:
                    if conf.lower() in candidate.lower():
                        confounder_bonus += 0.2
                score = min(1.0, ncd_score + confounder_bonus)
            
            # Adjust by confidence
            adjusted_score = score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "raw_score": score,
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