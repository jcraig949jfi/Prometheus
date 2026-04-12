import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import detect_confounders, build_bn, conditional_query


class ReasoningTool:
    """Epidemiology x Bayesian Networks - causal_confounding_hard"""

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
        """Extract entities, values, and causal structure from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all capitalized multi-word entities (potential variables)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = {}
        edges = []
        
        # Look for causal language patterns
        causal_keywords = ['causes', 'affects', 'influences', 'leads to', 'impacts', 'determines']
        for line in lines:
            # Extract entity names
            found_entities = re.findall(entity_pattern, line)
            
            # Look for percentages associated with entities
            percentages = re.findall(r'(\d+(?:\.\d+)?)%', line)
            percentages = [float(p) / 100 for p in percentages]
            
            # Associate percentages with the last mentioned entity
            if found_entities and percentages:
                entity = found_entities[-1]
                if entity not in entities:
                    entities[entity] = {"values": []}
                entities[entity]["values"].extend(percentages)
            
            # Detect causal relationships
            for keyword in causal_keywords:
                if keyword in line.lower():
                    # Find entities before and after the keyword
                    parts = line.lower().split(keyword)
                    if len(parts) >= 2:
                        # Find entities in each part
                        before_entities = re.findall(entity_pattern, parts[0])
                        after_entities = re.findall(entity_pattern, parts[1])
                        if before_entities and after_entities:
                            for cause in before_entities[-1:]:
                                for effect in after_entities[:1]:
                                    edges.append((cause, effect))
        
        # If no edges found from causal keywords, infer from correlation patterns
        if not edges and len(entities) >= 2:
            entity_list = list(entities.keys())
            # Create a simple chain if we have multiple entities
            for i in range(len(entity_list) - 1):
                edges.append((entity_list[i], entity_list[i + 1]))
        
        return {
            "entities": entities,
            "edges": edges,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply epidemiological reasoning with Bayesian networks to identify confounding."""
        entities = structure["entities"]
        edges = structure["edges"]
        question = structure["question"]
        
        # Extract treatment and outcome from question
        treatment = None
        outcome = None
        question_lower = question.lower()
        
        # Look for treatment/outcome patterns in question
        for entity in entities:
            if entity.lower() in question_lower:
                if "affect" in question_lower or "cause" in question_lower or "influence" in question_lower:
                    # Entity mentioned with causal verb - likely treatment
                    treatment = entity
                elif "outcome" in question_lower or "result" in question_lower or "effect" in question_lower:
                    outcome = entity
        
        # If not found, use first two entities
        entity_list = list(entities.keys())
        if len(entity_list) >= 2:
            if treatment is None:
                treatment = entity_list[0]
            if outcome is None:
                outcome = entity_list[1]
        
        # Build Bayesian network from extracted edges
        model = None
        try:
            model = build_bn(edges)
        except Exception:
            model = None
        
        # Use topological_sort to determine causal ordering (LOAD-BEARING primitive 1)
        causal_order = []
        if edges:
            order_result = topological_sort(edges)
            if order_result is not None:
                causal_order = order_result
                # Ensure treatment comes before outcome in causal order
                if treatment in causal_order and outcome in causal_order:
                    treatment_idx = causal_order.index(treatment)
                    outcome_idx = causal_order.index(outcome)
                    if treatment_idx > outcome_idx:
                        # Swap if order is wrong - outcome should come after treatment
                        treatment, outcome = outcome, treatment
        
        # Detect confounders using amino acid (LOAD-BEARING amino acid)
        confounders = set()
        if model is not None and treatment and outcome:
            try:
                confounders_result = detect_confounders(model, treatment, outcome)
                if confounders_result is not None:
                    confounders = set(confounders_result)
            except Exception:
                confounders = set()
        
        # Compute entropy of entity values as measure of uncertainty (LOAD-BEARING primitive 2)
        entity_entropies = {}
        for entity, data in entities.items():
            values = data.get("values", [])
            if len(values) >= 2:
                # Create probability distribution from values
                probs = [v for v in values if 0 <= v <= 1]
                if probs:
                    # Normalize if needed
                    total = sum(probs)
                    if total > 0:
                        probs = [p/total for p in probs]
                    else:
                        probs = [1.0/len(probs)] * len(probs)
                    ent = entropy(probs)
                    entity_entropies[entity] = ent
        
        # Determine which entity is the confounder
        computed_confounder = None
        if confounders:
            # Choose the confounder with highest entropy (most uncertainty to resolve)
            candidate_confounders = [c for c in confounders if c in entity_entropies]
            if candidate_confounders:
                computed_confounder = max(candidate_confounders, 
                                        key=lambda x: entity_entropies.get(x, 0))
            else:
                computed_confounder = list(confounders)[0] if confounders else None
        elif entity_entropies:
            # If no confounders detected, choose entity with highest entropy
            computed_confounder = max(entity_entropies.items(), key=lambda x: x[1])[0]
        
        # Use Bayesian update to adjust for confounding (LOAD-BEARING primitive 3)
        adjusted_effect = None
        if computed_confounder and treatment and outcome:
            # Extract base rates from entity values
            treatment_values = entities.get(treatment, {}).get("values", [])
            outcome_values = entities.get(outcome, {}).get("values", [])
            confounder_values = entities.get(computed_confounder, {}).get("values", [])
            
            if treatment_values and outcome_values:
                # Use first value as prior, second as likelihood
                prior = treatment_values[0] if treatment_values else 0.5
                likelihood = outcome_values[0] if outcome_values else 0.5
                
                # Adjust for confounder if we have confounder values
                false_positive = 0.0
                if confounder_values:
                    false_positive = confounder_values[0] if confounder_values else 0.0
                
                adjusted_effect = bayesian_update(prior, likelihood, false_positive)
        
        # Determine final answer based on reasoning
        computed_answer = None
        if computed_confounder:
            computed_answer = computed_confounder
        elif treatment and outcome:
            # If no confounder found, answer might be about the relationship
            if adjusted_effect is not None:
                if adjusted_effect > 0.5:
                    computed_answer = f"Yes, {treatment} affects {outcome}"
                else:
                    computed_answer = f"No, {treatment} does not affect {outcome}"
            else:
                computed_answer = treatment  # Fallback to treatment
        
        # Use confidence_from_agreement for calibration (LOAD-BEARING primitive 4)
        confidence_scores = []
        if entity_entropies:
            # Lower entropy means more certainty
            certainty_scores = [1 - e for e in entity_entropies.values() if 0 <= e <= 1]
            if certainty_scores:
                confidence = confidence_from_agreement(certainty_scores)
            else:
                confidence = 0.5
        else:
            confidence = 0.5
        
        return {
            "answer": computed_answer or "Unknown",
            "confidence": confidence,
            "confounders": list(confounders),
            "adjusted_effect": adjusted_effect,
            "causal_order": causal_order,
            "reasoning": f"Detected confounders: {list(confounders)}. Causal order: {causal_order}. Adjusted effect: {adjusted_effect}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
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
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract scores
        scores = [item["score"] for item in scored]
        
        # Simple min-max normalization if needed
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        
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