import re
import zlib
from typing import Dict, List, Any, Tuple
from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders, compare_conditional_marginal

class ReasoningTool:
    """Immunology x Bayesian Networks - Simpson's Paradox"""

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
        """Parse prompt to find entities, subgroups, rates, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all percentage values
        percent_pattern = r'([0-9]+\.?[0-9]*)%'
        all_percents = re.findall(percent_pattern, prompt)
        rates = [float(p) / 100.0 for p in all_percents]
        
        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter: exclude common words, focus on likely hospital/drug/group names
        common_words = {'The', 'A', 'An', 'And', 'But', 'Or', 'For', 'With', 'Which', 
                       'What', 'When', 'Where', 'Why', 'How', 'Total', 'Overall'}
        entities = [e for e in potential_entities if e not in common_words and len(e.split()) <= 3]
        
        # Find subgroup indicators (like "men", "women", "severe", "mild")
        subgroup_indicators = []
        subgroup_keywords = ['men', 'women', 'male', 'female', 'severe', 'mild', 
                            'young', 'old', 'group', 'category', 'type']
        words = prompt.lower().split()
        for word in words:
            if word in subgroup_keywords:
                subgroup_indicators.append(word)
        
        # Build structure
        return {
            "entities": entities,
            "rates": rates,
            "question": question,
            "subgroup_indicators": subgroup_indicators,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Immunological reasoning: treat subgroups as immune cell populations,
        aggregated data as systemic response, paradox as immune dysregulation."""
        
        entities = structure["entities"]
        rates = structure["rates"]
        question = structure["question"]
        
        # Immunological concept: Different immune cell populations (subgroups) 
        # can show opposite responses to treatment, while systemic (aggregated) 
        # response appears reversed due to population composition.
        # We model this as a Bayesian network where treatment efficacy depends
        # on subgroup (like cytokine profiles).
        
        # Use T1 primitives
        if rates:
            # Compute entropy of rates as measure of heterogeneity (immunological diversity)
            rate_entropy = entropy(rates) if len(rates) > 1 else 0.0
            
            # Bayesian update: prior belief in paradox based on rate heterogeneity
            # High entropy suggests subgroup differences (like diverse immune responses)
            prior_paradox = 0.3  # Base rate assumption
            likelihood = min(rate_entropy * 2.0, 1.0)  # Scale entropy to [0,1]
            paradox_posterior = bayesian_update(prior_paradox, likelihood)
            
            # Expected value of aggregated vs subgroup rates
            if len(rates) >= 2:
                # Pairwise comparisons: (probability of reversal, magnitude)
                comparisons = []
                for i in range(0, len(rates)-1, 2):
                    if i+1 < len(rates):
                        diff = abs(rates[i] - rates[i+1])
                        prob_reversal = min(diff * 3.0, 1.0)  # Larger differences more likely to reverse
                        comparisons.append((prob_reversal, diff))
                
                if comparisons:
                    expected_reversal = expected_value(comparisons)
                else:
                    expected_reversal = 0.0
            else:
                expected_reversal = 0.0
        else:
            rate_entropy = 0.0
            paradox_posterior = 0.0
            expected_reversal = 0.0
        
        # Build Bayesian network to detect Simpson's paradox
        # Immunological analogy: Treatment (T) -> Outcome (O), with Subgroup (S) as confounder
        edges = [("Subgroup", "Treatment"), ("Subgroup", "Outcome"), ("Treatment", "Outcome")]
        
        # Use extracted rates for CPDs if we have enough data
        if len(rates) >= 4:
            # Assume first two rates are for subgroup A, next two for subgroup B
            # Format: P(Outcome|Treatment, Subgroup)
            cpd_specs = {
                "Subgroup": {"card": 2, "values": [[0.5], [0.5]]},  # Equal subgroups
                "Treatment": {
                    "card": 2,
                    "parents": ["Subgroup"],
                    "values": [[0.5, 0.5], [0.5, 0.5]]  # Treatment independent of subgroup
                },
                "Outcome": {
                    "card": 2,
                    "parents": ["Treatment", "Subgroup"],
                    "values": [
                        [rates[0] if 0 < len(rates) else 0.5, rates[1] if 1 < len(rates) else 0.5],  # T=0
                        [rates[2] if 2 < len(rates) else 0.5, rates[3] if 3 < len(rates) else 0.5]   # T=1
                    ]
                }
            }
        else:
            # Fallback: use uniform probabilities
            cpd_specs = {
                "Subgroup": {"card": 2, "values": [[0.5], [0.5]]},
                "Treatment": {
                    "card": 2,
                    "parents": ["Subgroup"],
                    "values": [[0.5, 0.5], [0.5, 0.5]]
                },
                "Outcome": {
                    "card": 2,
                    "parents": ["Treatment", "Subgroup"],
                    "values": [[0.6, 0.4], [0.4, 0.6]]  # Setup for potential reversal
                }
            }
        
        # Use amino acid: build Bayesian network
        bn_model = build_bn(edges, cpd_specs)
        
        paradox_detected = False
        confounders = []
        
        if bn_model is not None:
            # Use amino acid: detect confounders (immunological: check for hidden variables)
            confounders = detect_confounders(bn_model, "Treatment", "Outcome")
            
            # Use amino acid: compare conditional vs marginal (Simpson's paradox test)
            # Immunological: compare systemic response (marginal) vs cell-specific (conditional)
            if len(rates) >= 4:
                try:
                    # P(Outcome=1 | Treatment=1) vs P(Outcome=1)
                    cond_result = conditional_query(bn_model, ["Outcome"], {"Treatment": 1})
                    marginal_result = conditional_query(bn_model, ["Outcome"], {})
                    
                    if cond_result is not None and marginal_result is not None:
                        cond_prob = cond_result.get(1, 0.0)
                        marginal_prob = marginal_result.get(1, 0.0)
                        
                        # Paradox if conditioning flips the direction
                        paradox_detected = abs(cond_prob - marginal_prob) > 0.2
                except:
                    paradox_detected = False
        
        # Determine which entity is "better" based on reasoning
        # Immunological: The "better" treatment is the one with higher efficacy 
        # in the dominant subgroup (like targeting the responsive immune population)
        computed_answer = ""
        if entities:
            if paradox_detected:
                # When paradox detected, the aggregated winner is often wrong
                # Look for entity mentioned in context of subgroups
                for entity in entities:
                    if any(word in structure["raw_prompt"].lower() for word in ["subgroup", "separately", "individually"]):
                        if entity.lower() in structure["raw_prompt"].lower():
                            computed_answer = entity
                            break
                
                if not computed_answer and len(entities) >= 2:
                    # Default to second entity if paradox detected
                    computed_answer = entities[1]
            else:
                # No paradox: aggregated data is reliable
                if len(entities) >= 1:
                    computed_answer = entities[0]
        
        # Use T1 primitive: confidence from agreement of multiple signals
        signals = []
        if paradox_posterior > 0.5:
            signals.append(0.8)
        if paradox_detected:
            signals.append(0.9)
        if expected_reversal > 0.3:
            signals.append(0.7)
        
        confidence = confidence_from_agreement(signals) if signals else 0.5
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "paradox_detected": paradox_detected,
            "confounders": confounders,
            "reasoning": f"Immunological analysis: rate_entropy={rate_entropy:.3f}, paradox_posterior={paradox_posterior:.3f}, expected_reversal={expected_reversal:.3f}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: exact or partial match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
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
        
        # Simple normalization: scale to [0, 1] range
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            scale = 1.0 / max(scores)
        else:
            scale = 1.0
        
        for item in scored:
            item["score"] = item["score"] * scale
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0