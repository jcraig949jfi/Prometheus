import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query


class ReasoningTool:
    """Complexity theory x Bayesian networks - Conjunction fallacy"""

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
            entity_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:has|probability|is)', line)
            if entity_match:
                entity = entity_match.group(1)
                # Find associated percentage
                perc_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                if perc_match:
                    if entity not in entities:
                        entities[entity] = []
                    entities[entity].append(float(perc_match.group(1)) / 100.0)
        
        # If no entities found by pattern, look for capitalized words
        if not entities:
            words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
            for word in words:
                if word not in ['The', 'A', 'An', 'And', 'Or', 'But']:
                    entities[word] = percentages[:1] if percentages else [0.5]
        
        # Extract conjunction phrases (A and B)
        conjunctions = []
        for line in lines:
            conj_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
            if conj_match:
                conjunctions.append(f"{conj_match.group(1)} and {conj_match.group(2)}")
        
        return {
            "entities": entities,
            "percentages": percentages,
            "question": question,
            "conjunctions": conjunctions,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply complexity theory framework: treat probabilities as computational resources,
        conjunction as composition requiring more resources than individual components."""
        
        entities = structure["entities"]
        percentages = structure["percentages"]
        conjunctions = structure["conjunctions"]
        
        # Complexity theory: joint probability requires more computational resources
        # than marginal probabilities. The fallacy occurs when composition is treated
        # as requiring fewer resources than its components.
        
        # Build Bayesian network to model dependencies
        edges = []
        cpd_specs = {}
        
        # Create nodes for each entity
        entity_nodes = list(entities.keys())
        
        # If we have conjunction phrases, create nodes for them
        if conjunctions:
            for conj in conjunctions:
                # Extract component entities
                parts = conj.split(' and ')
                if len(parts) == 2:
                    a, b = parts[0].strip(), parts[1].strip()
                    if a in entity_nodes and b in entity_nodes:
                        edges.append((a, conj))
                        edges.append((b, conj))
        
        # Use extracted percentages for CPDs
        if percentages:
            # Create simple CPDs using extracted data
            for i, entity in enumerate(entity_nodes):
                if i < len(percentages):
                    prob = percentages[i]
                    cpd_specs[entity] = [[prob], [1 - prob]]
        
        # Build Bayesian network (amino acid 1)
        model = None
        joint_prob = None
        marginal_probs = {}
        
        try:
            if edges:
                model = build_bn(edges, cpd_specs if cpd_specs else None)
                
                # Query joint probability if we have conjunction
                if conjunctions and model:
                    for conj in conjunctions:
                        parts = conj.split(' and ')
                        if len(parts) == 2:
                            a, b = parts[0].strip(), parts[1].strip()
                            # Query P(A and B) - assuming independence for simplicity
                            query_result = conditional_query(model, [a, b], {})
                            if query_result:
                                # Extract joint probability
                                joint_prob = query_result.get((1, 1), 0.0)
                                
                            # Get marginal probabilities
                            marg_a = conditional_query(model, [a], {})
                            marg_b = conditional_query(model, [b], {})
                            if marg_a:
                                marginal_probs[a] = marg_a.get(1, 0.0)
                            if marg_b:
                                marginal_probs[b] = marg_b.get(1, 0.0)
        except Exception:
            model = None
        
        # Complexity measure: entropy of probability distribution (T1 primitive 1)
        probs_for_entropy = percentages if percentages else [0.5, 0.5]
        complexity_entropy = entropy(probs_for_entropy)
        
        # Bayesian update to adjust probabilities based on conjunction (T1 primitive 2)
        prior = probs_for_entropy[0] if probs_for_entropy else 0.5
        likelihood = joint_prob if joint_prob is not None else (prior * 0.8)
        posterior = bayesian_update(prior, likelihood)
        
        # Expected value calculation for decision (T1 primitive 3)
        outcomes = []
        for entity, probs in entities.items():
            if probs:
                prob = probs[0]
                # Value is inverse of probability (higher probability = lower surprise)
                value = 1.0 - prob
                outcomes.append((prob, value))
        
        if not outcomes:
            outcomes = [(0.5, 0.5), (0.5, 0.5)]
        
        expected_val = expected_value(outcomes)
        
        # Determine which is more probable: conjunction or individual event
        computed_answer = ""
        confidence = 0.5
        
        if joint_prob is not None and marginal_probs:
            # Check for conjunction fallacy: P(A and B) should be <= min(P(A), P(B))
            min_marginal = min(marginal_probs.values())
            
            # Use complexity theory: if joint probability requires more resources,
            # it should be lower than individual probabilities
            resource_ratio = joint_prob / (min_marginal + 1e-10)
            
            # Bayesian update influences decision
            if posterior < 0.5 and resource_ratio > 1.0:
                # Detected conjunction fallacy
                computed_answer = "individual event"
                confidence = 0.8
            else:
                # No fallacy or conjunction is actually more probable
                computed_answer = "conjunction"
                confidence = 0.6
        else:
            # Fallback using extracted entities and entropy
            if entities:
                # Find entity with highest probability
                max_entity = max(entities.items(), 
                               key=lambda x: x[1][0] if x[1] else 0.0)
                computed_answer = max_entity[0]
            else:
                computed_answer = "individual event"
            
            # Adjust confidence based on entropy (higher entropy = lower confidence)
            confidence = max(0.3, 1.0 - complexity_entropy)
        
        # Final confidence adjustment using T1 primitive
        confidence_scores = [confidence, posterior, expected_val]
        final_confidence = confidence_from_agreement(confidence_scores)
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "joint_prob": joint_prob if joint_prob is not None else 0.0,
            "marginal_probs": marginal_probs,
            "entropy": complexity_entropy,
            "posterior": posterior,
            "expected_value": expected_val
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD similarity
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
        
        # Normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
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
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)