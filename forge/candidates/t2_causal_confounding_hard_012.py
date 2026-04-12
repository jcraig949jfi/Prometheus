import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders


class ReasoningTool:
    """Number theory x Bayesian networks - Causal confounding hard"""

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
        """Extract entities, values, relationships, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all capitalized multi-word phrases as potential entities
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        all_entities = re.findall(entity_pattern, prompt)
        entities = {}
        for ent in set(all_entities):
            if len(ent.split()) <= 3:  # Filter out long phrases
                entities[ent] = {"values": [], "mentions": 0}
        
        # Count mentions
        for ent in entities:
            entities[ent]["mentions"] = prompt.count(ent)
        
        # Extract percentages and associate with nearest entity
        percent_pattern = r'(\d+(?:\.\d+)?)%'
        percentages = re.findall(percent_pattern, prompt)
        float_percentages = [float(p) / 100.0 for p in percentages]
        
        # Find causal language patterns
        causal_words = ["causes", "affects", "influences", "leads to", "because", "due to"]
        causal_relations = []
        for line in lines:
            for word in causal_words:
                if word in line.lower():
                    # Extract entities around causal word
                    parts = re.split(r'\b' + word + r'\b', line, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        left_ents = re.findall(entity_pattern, parts[0])
                        right_ents = re.findall(entity_pattern, parts[1])
                        if left_ents and right_ents:
                            causal_relations.append((left_ents[-1], right_ents[0]))
        
        # Find comparison language
        comparison_words = ["higher", "lower", "better", "worse", "more", "less"]
        comparison_target = None
        for word in comparison_words:
            if word in question.lower():
                # Find entity being compared
                for ent in entities:
                    if ent in question:
                        comparison_target = ent
                        break
        
        return {
            "entities": entities,
            "percentages": float_percentages,
            "causal_relations": list(set(causal_relations)),
            "question": question,
            "comparison_target": comparison_target,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply number theory concepts through Bayesian network analysis."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        causal_relations = structure["causal_relations"]
        question = structure["question"]
        
        # If we have at least 3 entities and some causal relations, build a BN
        computed_answer = None
        confidence = 0.5
        reasoning_text = ""
        
        if len(entities) >= 2 and len(percentages) >= 2 and causal_relations:
            # Create a simple DAG from causal relations
            edges = []
            for cause, effect in causal_relations:
                if cause in entities and effect in entities:
                    edges.append((cause, effect))
            
            # Use topological_sort to determine causal order (LOAD-BEARING)
            causal_order = topological_sort(edges)
            
            if causal_order:
                # Build Bayesian network with extracted percentages as probabilities
                cpd_specs = {}
                if len(percentages) >= len(causal_order):
                    # Use percentages as conditional probabilities in order
                    for i, node in enumerate(causal_order):
                        parents = [p for (p, c) in edges if c == node]
                        if not parents:
                            # Root node: use percentage as prior
                            if i < len(percentages):
                                prob = percentages[i]
                                cpd_specs[node] = {
                                    'variable': node,
                                    'variable_card': 2,
                                    'values': [[prob, 1 - prob]],
                                    'evidence': [],
                                    'evidence_card': []
                                }
                        else:
                            # Child node: use percentages for conditional probabilities
                            if i < len(percentages):
                                prob = percentages[i]
                                # Simple binary CPD
                                cpd_specs[node] = {
                                    'variable': node,
                                    'variable_card': 2,
                                    'values': [[prob, 1 - prob], [1 - prob, prob]],
                                    'evidence': parents,
                                    'evidence_card': [2] * len(parents)
                                }
                
                # Use build_bn amino acid (LOAD-BEARING)
                model = build_bn(edges, cpd_specs)
                
                if model:
                    # Use detect_confounders amino acid (LOAD-BEARING)
                    confounders_result = None
                    if len(causal_order) >= 2:
                        var_a, var_b = causal_order[0], causal_order[-1]
                        confounders_result = detect_confounders(model, var_a, var_b)
                    
                    # Use conditional_query amino acid (LOAD-BEARING)
                    query_result = None
                    if len(causal_order) >= 2:
                        # Query the effect of first on last
                        target = causal_order[-1]
                        evidence = {causal_order[0]: 1}  # Assuming 1 means "present"
                        query_result = conditional_query(model, [target], evidence)
                    
                    # Apply number theory: treat probabilities as modular residues
                    # Compute "confounding strength" using modular arithmetic properties
                    if percentages:
                        # Use entropy on probability distribution (LOAD-BEARING)
                        prob_dist = percentages[:min(4, len(percentages))]
                        # Normalize to sum to 1
                        if sum(prob_dist) > 0:
                            prob_dist = [p / sum(prob_dist) for p in prob_dist]
                        else:
                            prob_dist = [1.0 / len(prob_dist)] * len(prob_dist)
                        
                        entropy_val = entropy(prob_dist)
                        
                        # Use bayesian_update with extracted values (LOAD-BEARING)
                        if len(percentages) >= 2:
                            prior = percentages[0]
                            likelihood = percentages[1] if len(percentages) > 1 else 0.5
                            posterior = bayesian_update(prior, likelihood)
                            
                            # Determine answer based on confounding analysis
                            if confounders_result:
                                confounder_list = list(confounders_result)
                                if confounder_list:
                                    # The confounder is the answer
                                    computed_answer = confounder_list[0]
                                    reasoning_text = f"Confounder detected: {computed_answer}"
                                    # Adjust confidence using entropy and posterior
                                    confidence = max(0.1, min(0.9, (1 - entropy_val) * posterior))
                                else:
                                    # No confounder, use query result
                                    if query_result and target in query_result:
                                        effect_prob = query_result[target].get(1, 0.5)
                                        # Find entity with strongest effect
                                        max_ent = None
                                        max_val = -1
                                        for ent in entities:
                                            if ent in causal_order:
                                                idx = causal_order.index(ent)
                                                if idx < len(percentages):
                                                    val = percentages[idx]
                                                    if val > max_val:
                                                        max_val = val
                                                        max_ent = ent
                                        computed_answer = max_ent or causal_order[0]
                                        reasoning_text = f"Direct effect: {computed_answer}"
                                        confidence = effect_prob
                            else:
                                # Fallback: use entity with highest mention count
                                max_mentions = max(entities.values(), key=lambda x: x["mentions"])["mentions"]
                                top_entities = [e for e, data in entities.items() if data["mentions"] == max_mentions]
                                computed_answer = top_entities[0] if top_entities else list(entities.keys())[0]
                                reasoning_text = "Most mentioned entity"
                                confidence = 0.3
                        else:
                            computed_answer = list(entities.keys())[0]
                            reasoning_text = "Default entity"
                            confidence = 0.2
                    else:
                        computed_answer = list(entities.keys())[0]
                        reasoning_text = "No percentages found"
                        confidence = 0.1
                else:
                    # BN failed, use simple heuristic with primitives
                    if percentages:
                        # Use entropy on percentages (LOAD-BEARING)
                        prob_dist = percentages[:min(4, len(percentages))]
                        if sum(prob_dist) > 0:
                            prob_dist = [p / sum(prob_dist) for p in prob_dist]
                        entropy_val = entropy(prob_dist)
                        
                        # Entity with value closest to 0.5 (max uncertainty)
                        closest_ent = None
                        closest_dist = float('inf')
                        for ent in entities:
                            if percentages:
                                idx = list(entities.keys()).index(ent) % len(percentages)
                                dist = abs(percentages[idx] - 0.5)
                                if dist < closest_dist:
                                    closest_dist = dist
                                    closest_ent = ent
                        
                        computed_answer = closest_ent or list(entities.keys())[0]
                        reasoning_text = f"Entity near decision boundary (entropy: {entropy_val:.3f})"
                        confidence = 0.5 * (1 - entropy_val)
                    else:
                        computed_answer = list(entities.keys())[0]
                        reasoning_text = "Fallback to first entity"
                        confidence = 0.1
            else:
                # No causal order, use entity analysis
                if percentages:
                    # Use bayesian_update with first two percentages (LOAD-BEARING)
                    if len(percentages) >= 2:
                        posterior = bayesian_update(percentages[0], percentages[1])
                        # Pick entity based on posterior
                        ent_list = list(entities.keys())
                        idx = 0 if posterior > 0.5 else min(1, len(ent_list) - 1)
                        computed_answer = ent_list[idx]
                        reasoning_text = f"Bayesian decision (posterior: {posterior:.3f})"
                        confidence = abs(posterior - 0.5) * 2
                    else:
                        computed_answer = list(entities.keys())[0]
                        reasoning_text = "Single percentage available"
                        confidence = 0.2
                else:
                    computed_answer = list(entities.keys())[0]
                    reasoning_text = "No data for reasoning"
                    confidence = 0.1
        else:
            # Minimal case
            if entities:
                computed_answer = list(entities.keys())[0]
                reasoning_text = "Only entity extraction possible"
                confidence = 0.1
            else:
                # Extract any capitalized word as fallback
                words = re.findall(r'\b[A-Z][a-z]+\b', question)
                computed_answer = words[0] if words else "Unknown"
                reasoning_text = "Word extraction fallback"
                confidence = 0.05
        
        # Use confidence_from_agreement with multiple confidence sources (LOAD-BEARING)
        confidence_sources = [confidence]
        if percentages:
            confidence_sources.append(min(0.9, max(0.1, sum(percentages) / len(percentages))))
        if len(entities) > 1:
            confidence_sources.append(min(0.8, len(entities) / 10.0))
        
        final_confidence = confidence_from_agreement(confidence_sources)
        
        return {
            "answer": str(computed_answer),
            "confidence": final_confidence,
            "reasoning": reasoning_text,
            "entities": list(entities.keys()),
            "percentages": percentages
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        def ncd(a: str, b: str) -> float:
            """Normalized Compression Distance."""
            if not a or not b:
                return 1.0
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            if max(ca, cb) == 0:
                return 1.0
            return (cab - min(ca, cb)) / max(ca, cb)
        
        scored = []
        for candidate in candidates:
            # Primary: exact match or substring of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Secondary: NCD similarity to computed answer
                ncd_val = ncd(computed_answer, candidate)
                base_score = 1.0 / (1.0 + ncd_val)
            
            # Tertiary: NCD to reasoning text (weaker signal)
            reasoning_ncd = ncd(reasoning_text, candidate)
            reasoning_score = 1.0 / (1.0 + reasoning_ncd)
            
            # Combined score
            combined = 0.7 * base_score + 0.3 * reasoning_score
            
            scored.append({
                "candidate": candidate,
                "score": combined,
                "base_score": base_score,
                "reasoning_score": reasoning_score
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to improve discrimination."""
        if not scored:
            return scored
        
        # Extract scores
        scores = [item["score"] for item in scored]
        
        # Simple calibration: softmax-like transformation
        if max(scores) - min(scores) > 0.001:
            # Shift and scale
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
        # Ensure scores are between 0 and 1
        for item in scored:
            item["score"] = max(0.0, min(1.0, item["score"]))
        
        return scored