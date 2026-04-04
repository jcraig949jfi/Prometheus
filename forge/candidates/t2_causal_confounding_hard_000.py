import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    topological_sort,
    solve_linear_system,
    expected_value
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    detect_confounders,
    get_adjustment_set,
    conditional_query
)


class ReasoningTool:
    """Cell biology x Bayesian networks - causal_confounding_hard"""

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
        """Parse prompt to extract entities, relationships, and values."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        entities = {}
        relationships = []
        values = {}
        
        # Extract percentages and associate with nearest entity
        percent_pattern = r'([0-9]+\.?[0-9]*)%'
        
        for line in lines:
            # Find all entities in this line
            line_entities = re.findall(entity_pattern, line)
            percents = re.findall(percent_pattern, line)
            
            # Convert percentages to probabilities
            probs = [float(p) / 100.0 for p in percents]
            
            # Look for causal language
            if any(word in line.lower() for word in ['causes', 'affects', 'influences', 'leads to']):
                # Try to extract causal relationship
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in ['causes', 'affects', 'influences', 'leads']:
                        if i > 0 and i < len(words) - 1:
                            cause = words[i-1]
                            effect = words[i+1]
                            if cause in line_entities and effect in line_entities:
                                relationships.append((cause, effect))
            
            # Associate probabilities with entities
            for entity in line_entities:
                if entity not in entities:
                    entities[entity] = {"mentions": 0, "values": []}
                entities[entity]["mentions"] += 1
                if probs:
                    entities[entity]["values"].extend(probs)
        
        # Extract numerical values (not percentages)
        number_pattern = r'\b([0-9]+\.?[0-9]*)\b(?!%)'
        for line in lines:
            numbers = re.findall(number_pattern, line)
            for num in numbers:
                float_num = float(num)
                # Find nearest entity to this number
                words = line.split()
                for i, word in enumerate(words):
                    if word == num:
                        # Look left and right for entity names
                        for j in range(max(0, i-3), min(len(words), i+4)):
                            if words[j] in entities:
                                if words[j] not in values:
                                    values[words[j]] = []
                                values[words[j]].append(float_num)
                                break
        
        return {
            "entities": entities,
            "relationships": relationships,
            "values": values,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply cell biology framework to identify and adjust for confounders."""
        entities = structure["entities"]
        relationships = structure["relationships"]
        question = structure["question"]
        
        # Cell biology framework: treat variables as cellular components,
        # confounders as membrane-bound organelles that mediate signaling,
        # and causal effects as signal transduction pathways
        
        # Phase 1: Build causal graph (signaling network)
        edges = []
        for cause, effect in relationships:
            edges.append((cause, effect))
        
        # Use topological sort to identify signaling hierarchy
        # (like protein phosphorylation cascades)
        try:
            signaling_hierarchy = topological_sort(edges)
            if signaling_hierarchy is None:
                signaling_hierarchy = []
        except Exception:
            signaling_hierarchy = []
        
        # Phase 2: Detect confounders (organelles mediating cross-talk)
        confounders = set()
        if edges:
            try:
                # Build minimal Bayesian network for detection
                model = build_bn(edges)
                if model:
                    # Find all pairs of variables that might have confounders
                    entity_names = list(entities.keys())
                    for i in range(len(entity_names)):
                        for j in range(i+1, len(entity_names)):
                            var_a, var_b = entity_names[i], entity_names[j]
                            detected = detect_confounders(model, var_a, var_b)
                            if detected:
                                confounders.update(detected)
            except Exception:
                pass
        
        # Phase 3: Compute adjusted effects using backdoor adjustment
        # (like pharmacological inhibition of confounding pathways)
        adjusted_effects = {}
        
        # Look for treatment and outcome in question
        treatment = None
        outcome = None
        question_lower = question.lower()
        
        for entity in entities:
            if "affect" in question_lower or "effect" in question_lower:
                # Try to find what affects what
                if entity in question:
                    if not treatment and "on" in question_lower:
                        # Entity before "on" might be treatment
                        idx = question_lower.find(entity.lower())
                        if idx > 0 and "on" in question_lower[:idx]:
                            treatment = entity
                    elif not outcome:
                        outcome = entity
        
        # If we found treatment and outcome, compute adjusted effect
        if treatment and outcome and edges:
            try:
                model = build_bn(edges)
                if model:
                    # Get adjustment set (like finding which pathways to block)
                    adj_set = get_adjustment_set(model, treatment, outcome)
                    
                    if adj_set:
                        # Compute conditional probabilities using extracted values
                        # Use entropy to measure uncertainty in the adjustment
                        adj_probs = []
                        for adj_var in adj_set:
                            if adj_var in entities and entities[adj_var]["values"]:
                                # Convert values to probabilities if needed
                                vals = entities[adj_var]["values"]
                                if all(0 <= v <= 1 for v in vals):
                                    adj_probs.extend(vals)
                                else:
                                    # Normalize if values are not probabilities
                                    max_val = max(vals) if vals else 1
                                    adj_probs.extend([v/max_val for v in vals])
                        
                        if adj_probs:
                            # Higher entropy means more uncertainty in confounding
                            conf_entropy = entropy(adj_probs)
                            
                            # Use Bayesian update to adjust for confounding
                            # Prior: base rate from overall data
                            # Likelihood: subgroup-specific rates
                            base_rates = []
                            for entity in [treatment, outcome]:
                                if entity in entities and entities[entity]["values"]:
                                    vals = entities[entity]["values"]
                                    if vals:
                                        base_rates.append(sum(vals)/len(vals))
                            
                            if len(base_rates) >= 2:
                                prior = base_rates[0]
                                likelihood = base_rates[1]
                                
                                # False positive rate increases with confounding entropy
                                fp_rate = min(0.3, conf_entropy * 0.5)
                                
                                adjusted_prob = bayesian_update(prior, likelihood, fp_rate)
                                adjusted_effects[(treatment, outcome)] = adjusted_prob
            except Exception:
                pass
        
        # Phase 4: Determine answer using cell biology principles
        # In cell signaling, the true causal effect is the one that persists
        # after blocking confounding pathways (like using specific inhibitors)
        
        computed_answer = ""
        confidence = 0.5
        
        if adjusted_effects:
            # Use the adjusted effect to determine answer
            for (treat, out), effect in adjusted_effects.items():
                if "better" in question_lower or "worse" in question_lower:
                    # Compare treatments
                    if effect > 0.5:
                        computed_answer = treat
                    else:
                        # Look for alternative treatment
                        for entity in entities:
                            if entity != treat and entity in question:
                                computed_answer = entity
                                break
                        if not computed_answer:
                            computed_answer = out
                else:
                    # Just report the strongest effect
                    computed_answer = f"{treat} affects {out}"
            
            # Confidence from agreement of multiple adjustment methods
            scores = []
            if entities:
                for entity in entities:
                    if entity in computed_answer:
                        scores.append(0.8)
                    else:
                        scores.append(0.2)
            
            if scores:
                confidence = confidence_from_agreement(scores)
        
        # Fallback: if no adjusted effects, use topological hierarchy
        if not computed_answer and signaling_hierarchy:
            # In cell biology, upstream regulators control downstream effects
            computed_answer = signaling_hierarchy[0]  # Most upstream regulator
            confidence = 0.6
        
        # Final fallback: use entity with most mentions
        if not computed_answer and entities:
            computed_answer = max(entities.items(), 
                                key=lambda x: x[1]["mentions"])[0]
            confidence = 0.4
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "confounders": list(confounders),
            "adjusted_effects": adjusted_effects,
            "signaling_hierarchy": signaling_hierarchy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring of computed answer
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