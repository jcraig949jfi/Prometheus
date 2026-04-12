import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    counterfactual_intervention,
    topological_sort,
    solve_linear_system
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    do_calculus,
    detect_confounders
)
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Neuroscience x Causal Bayesian Networks - Causal Counterfactual"""

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
        """Extract entities, values, causal relationships, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases that appear multiple times)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_names = re.findall(entity_pattern, prompt)
        from collections import Counter
        name_counts = Counter(all_names)
        entities = [name for name, count in name_counts.items() if count > 1 and len(name) > 2]
        
        # Extract numerical values (percentages, rates, probabilities)
        numbers = re.findall(r'([0-9]+\.?[0-9]*)%', prompt)
        values = [float(n) / 100.0 for n in numbers]  # Convert to probabilities
        
        # Extract causal language: "causes", "affects", "influences", "leads to"
        causal_verbs = []
        for verb in ["causes", "affects", "influences", "leads to", "determines"]:
            if verb in prompt.lower():
                causal_verbs.append(verb)
        
        # Try to extract causal edges from sentences
        edges = []
        sentences = re.split(r'[.!?]', prompt)
        for sent in sentences:
            sent_lower = sent.lower()
            if "causes" in sent_lower or "affects" in sent_lower:
                # Simple pattern: "X causes Y"
                words = sent.split()
                for i, word in enumerate(words):
                    if word.lower() in ["causes", "affects", "influences"] and i > 0 and i < len(words) - 1:
                        cause = words[i-1]
                        effect = words[i+1]
                        if cause in entities and effect in entities:
                            edges.append((cause, effect))
        
        # If no edges found, create default based on entities
        if not edges and len(entities) >= 2:
            edges = [(entities[0], entities[1])]
        
        return {
            "entities": entities,
            "values": values,
            "edges": edges,
            "question": question,
            "causal_verbs": causal_verbs,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply neuroscience-inspired causal reasoning to compute counterfactual answer."""
        entities = structure["entities"]
        values = structure["values"]
        edges = structure["edges"]
        question = structure["question"]
        
        # NEUROSCIENCE SCAFFOLD: Model causal reasoning as neural network dynamics
        # Causal strength = synaptic weight, counterfactual = perturbing neural activity
        # Use entropy to measure uncertainty in causal pathways
        
        # If we have enough values, create a simple causal model
        computed_answer = None
        confidence = 0.5
        reasoning = ""
        
        # T1 PRIMITIVE 1: topological_sort to establish causal ordering
        causal_order = []
        if edges:
            causal_order = topological_sort(edges)
            if causal_order is None:
                # Graph has cycles, use first entity
                causal_order = entities[:1]
        
        # T1 PRIMITIVE 2: entropy to measure uncertainty in values
        value_entropy = 0.0
        if values:
            # Normalize values to create probability distribution
            total = sum(values)
            if total > 0:
                probs = [v/total for v in values]
                value_entropy = entropy(probs)
        
        # AMINO ACID 1: build_bn to create Bayesian network
        model = None
        if edges and len(values) >= len(edges):
            try:
                # Create simple CPDs from extracted values
                cpd_specs = {}
                for i, (parent, child) in enumerate(edges):
                    if i < len(values):
                        prob = values[i]
                        cpd_specs[child] = {
                            "variable": child,
                            "variable_card": 2,
                            "evidence": [parent],
                            "evidence_card": [2],
                            "values": [[prob, 1-prob], [1-prob, prob]]
                        }
                
                model = build_bn(edges, cpd_specs)
            except Exception:
                model = None
        
        # T1 PRIMITIVE 3: counterfactual_intervention for do-calculus
        intervention_result = None
        if edges and values and causal_order:
            # Create initial values dict
            init_values = {}
            for i, entity in enumerate(entities):
                if i < len(values):
                    init_values[entity] = values[i]
                else:
                    init_values[entity] = 0.5  # Default
            
            # Intervene on first cause
            intervene_node = causal_order[0] if causal_order else entities[0]
            intervention_result = counterfactual_intervention(
                edges, init_values, intervene_node, 0.0
            )
        
        # AMINO ACID 2: conditional_query for probabilistic reasoning
        conditional_prob = None
        if model and len(entities) >= 2:
            try:
                target = entities[-1] if len(entities) > 1 else entities[0]
                evidence = {entities[0]: 1} if len(entities) > 0 else {}
                conditional_prob = conditional_query(model, [target], evidence)
            except Exception:
                conditional_prob = None
        
        # Determine answer based on reasoning
        if intervention_result:
            # NEUROSCIENCE: Counterfactual as neural perturbation effect
            # Find entity with largest change from intervention
            if len(entities) >= 2:
                # Compute effect sizes
                effects = []
                for entity in entities[1:]:  # Skip intervened node
                    if entity in intervention_result:
                        # Simple effect measure
                        effect = abs(intervention_result.get(entity, 0.5) - 0.5)
                        effects.append((entity, effect))
                
                if effects:
                    # Entity with largest effect is the answer
                    best_entity = max(effects, key=lambda x: x[1])[0]
                    computed_answer = best_entity
                    confidence = 0.7 + (value_entropy * 0.3)  # Higher entropy reduces confidence
                    reasoning = f"Counterfactual intervention on {causal_order[0]} showed largest effect on {best_entity}"
        
        # Fallback 1: Use conditional probability
        if not computed_answer and conditional_prob is not None:
            # NEUROSCIENCE: Probabilistic inference as Bayesian belief updating
            if isinstance(conditional_prob, dict) and len(conditional_prob) > 0:
                # Find entity with highest conditional probability
                best_entity = max(conditional_prob.items(), key=lambda x: x[1])[0]
                computed_answer = best_entity
                confidence = 0.6
                reasoning = f"Highest conditional probability: {best_entity}"
        
        # Fallback 2: Use topological order
        if not computed_answer and causal_order:
            # NEUROSCIENCE: Causal hierarchy as neural processing stream
            computed_answer = causal_order[-1] if causal_order else entities[0]
            confidence = 0.5
            reasoning = f"Final node in causal chain: {computed_answer}"
        
        # Fallback 3: Use first entity
        if not computed_answer and entities:
            computed_answer = entities[0]
            confidence = 0.4
            reasoning = f"Primary entity: {computed_answer}"
        
        # T1 PRIMITIVE 4: bayesian_update to refine confidence
        if computed_answer and "what would" in question.lower() or "counterfactual" in question.lower():
            # Prior belief in counterfactual reasoning
            prior = 0.5
            likelihood = 0.8 if intervention_result else 0.3
            updated_confidence = bayesian_update(prior, likelihood, false_positive=0.1)
            confidence = (confidence + updated_confidence) / 2
        
        # T1 PRIMITIVE 5: confidence_from_agreement for multiple evidence sources
        confidence_sources = []
        if intervention_result:
            confidence_sources.append(0.7)
        if conditional_prob is not None:
            confidence_sources.append(0.6)
        if value_entropy > 0:
            confidence_sources.append(1.0 - min(value_entropy, 1.0))
        
        if confidence_sources:
            aggregated_confidence = confidence_from_agreement(confidence_sources)
            confidence = (confidence + aggregated_confidence) / 2
        
        # Final fallback
        if not computed_answer:
            computed_answer = "Unknown"
            confidence = 0.1
            reasoning = "Insufficient data for counterfactual reasoning"
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning,
            "intervention_result": intervention_result,
            "conditional_prob": conditional_prob,
            "causal_order": causal_order
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 0.9 + (confidence * 0.1)
            else:
                # Secondary scoring: NCD similarity to reasoning text
                ncd_score = self._ncd_similarity(reasoning_text, candidate)
                score = ncd_score * confidence
            
            # Penalize candidates that contradict the reasoning
            if "not" in candidate.lower() and "not" not in reasoning_text.lower():
                score *= 0.7
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _ncd_similarity(self, a: str, b: str) -> float:
        """Normalized Compression Distance similarity between two strings."""
        if not a or not b:
            return 0.0
        
        def compressed_length(s: str) -> int:
            return len(zlib.compress(s.encode('utf-8')))
        
        ca = compressed_length(a)
        cb = compressed_length(b)
        cab = compressed_length(a + " " + b)
        
        if max(ca, cb) == 0:
            return 0.0
        
        ncd = (cab - min(ca, cb)) / max(ca, cb)
        return 1.0 - min(ncd, 1.0)

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Normalize to 0-1 range
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score - min_score > 0:
            for item in scored:
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                item["score"] = normalized
        else:
            # All scores equal
            for item in scored:
                item["score"] = 0.5
        
        # Apply softmax for probability-like distribution
        exp_scores = [2.71828 ** item["score"] for item in scored]
        sum_exp = sum(exp_scores)
        
        if sum_exp > 0:
            for i, item in enumerate(scored):
                item["score"] = exp_scores[i] / sum_exp
        
        return scored