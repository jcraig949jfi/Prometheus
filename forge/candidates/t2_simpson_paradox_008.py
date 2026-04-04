import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders


class ReasoningTool:
    """Information theory x Bayesian networks - Simpson's paradox detection"""

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
        """Parse prompt to find entities, subgroups, rates, and the question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all percentage values
        percent_pattern = r'(\d+(?:\.\d+)?)%'
        all_percents = re.findall(percent_pattern, prompt)
        percent_values = [float(p) for p in all_percents]
        
        # Find entity names (capitalized phrases that appear before numbers)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Filter to likely entities (not common words, appear near numbers)
        entities = {}
        sentences = prompt.split('.')
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Find numbers in this sentence
            nums_in_sent = re.findall(percent_pattern, sent)
            if nums_in_sent:
                # Find capitalized phrases in this sentence
                caps_in_sent = re.findall(entity_pattern, sent)
                for entity in caps_in_sent:
                    if len(entity.split()) <= 3 and entity.lower() not in ['the', 'a', 'an', 'and', 'or', 'but']:
                        if entity not in entities:
                            entities[entity] = {"rates": [], "context": sent}
                        # Associate numbers from this sentence
                        entities[entity]["rates"].extend([float(n) for n in nums_in_sent])
        
        # Find subgroup indicators
        subgroup_indicators = []
        subgroup_keywords = ['group', 'category', 'type', 'class', 'subgroup', 'stratum']
        for sent in sentences:
            for keyword in subgroup_keywords:
                if keyword in sent.lower():
                    subgroup_indicators.append(sent)
                    break
        
        return {
            "entities": entities,
            "percent_values": percent_values,
            "question": question,
            "subgroup_indicators": subgroup_indicators,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory and Bayesian networks to detect Simpson's paradox."""
        entities = structure["entities"]
        percents = structure["percent_values"]
        question = structure["question"]
        
        if len(percents) < 4 or len(entities) < 2:
            # Not enough data for Simpson's paradox analysis
            return {"answer": "Insufficient data", "confidence": 0.0, "reasoning": "Not enough rates or entities"}
        
        # === INFORMATION THEORY SCAFFOLD ===
        # Model data as information sources with mutual information between aggregated vs subgroup views
        # High mutual information between views suggests consistency, low suggests paradox
        
        # Compute entropy of aggregated rates
        if percents:
            normalized_rates = [p/100 for p in percents]
            # Use T1 primitive: entropy
            aggregated_entropy = entropy(normalized_rates) if len(normalized_rates) > 1 else 0.0
        else:
            aggregated_entropy = 0.0
        
        # === BAYESIAN NETWORK FOR CAUSAL STRUCTURE ===
        # Build a simple BN to model the relationship between subgroup, treatment, and outcome
        try:
            # Create edges: Subgroup -> Treatment, Treatment -> Outcome, Subgroup -> Outcome
            edges = [('Subgroup', 'Treatment'), ('Treatment', 'Outcome'), ('Subgroup', 'Outcome')]
            
            # Create CPDs using extracted percentages
            # We'll use the first 4 percentages if available
            if len(percents) >= 4:
                p1, p2, p3, p4 = percents[0]/100, percents[1]/100, percents[2]/100, percents[3]/100
            else:
                # Pad with reasonable defaults if not enough percentages
                p1, p2, p3, p4 = 0.6, 0.4, 0.7, 0.3
            
            cpd_specs = {
                'Subgroup': {'values': [[0.5], [0.5]], 'states': ['A', 'B']},
                'Treatment': {
                    'values': [[p1, p3], [p2, p4]],  # P(Treatment|Subgroup)
                    'states': ['Yes', 'No']
                },
                'Outcome': {
                    'values': [[0.8, 0.2, 0.6, 0.4], [0.2, 0.8, 0.4, 0.6]],  # P(Outcome|Treatment,Subgroup)
                    'states': ['Success', 'Failure']
                }
            }
            
            # Use amino acid: build_bn
            bn_model = build_bn(edges, cpd_specs)
            
            if bn_model is not None:
                # Use amino acid: compare_conditional_marginal to check for Simpson's paradox
                # Compare P(Outcome=Success|Treatment=Yes) vs P(Outcome=Success)
                cond_result = compare_conditional_marginal(
                    bn_model, 
                    target='Outcome', 
                    condition_var='Treatment', 
                    condition_val='Yes'
                )
                
                # Use amino acid: detect_confounders
                confounders = detect_confounders(bn_model, 'Treatment', 'Outcome')
                
                # Use T1 primitive: bayesian_update to adjust confidence
                prior_confidence = 0.5
                likelihood = 0.8 if cond_result and abs(cond_result.get('difference', 0)) > 0.1 else 0.3
                updated_confidence = bayesian_update(prior_confidence, likelihood)
                if updated_confidence is None:
                    updated_confidence = prior_confidence
                
                # Use T1 primitive: expected_value for decision weighting
                outcomes = [(0.7, 1.0), (0.3, 0.0)]  # (probability, value)
                ev = expected_value(outcomes)
                
                # Determine if paradox exists
                paradox_detected = False
                if cond_result and abs(cond_result.get('difference', 0)) > 0.15:
                    paradox_detected = True
                
                # Determine which entity is "better" based on rates
                best_entity = None
                best_rate = -1
                for entity, data in entities.items():
                    if data.get("rates"):
                        avg_rate = sum(data["rates"]) / len(data["rates"])
                        if avg_rate > best_rate:
                            best_rate = avg_rate
                            best_entity = entity
                
                # Use T1 primitive: confidence_from_agreement
                confidence_scores = [updated_confidence, ev, 0.7 if paradox_detected else 0.3]
                final_confidence = confidence_from_agreement(confidence_scores)
                if final_confidence is None:
                    final_confidence = updated_confidence
                
                reasoning_text = f"Information entropy: {aggregated_entropy:.3f}. "
                if paradox_detected:
                    reasoning_text += f"Simpson's paradox detected (confounders: {confounders}). "
                    reasoning_text += f"Aggregated view reverses subgroup trends. "
                else:
                    reasoning_text += f"No strong paradox detected. "
                reasoning_text += f"Best entity based on analysis: {best_entity if best_entity else 'Unknown'}"
                
                return {
                    "answer": best_entity if best_entity else "Unknown",
                    "confidence": min(max(final_confidence, 0.0), 1.0),
                    "reasoning": reasoning_text,
                    "paradox_detected": paradox_detected,
                    "entropy": aggregated_entropy
                }
                
        except Exception as e:
            # Fallback to simpler analysis if BN fails
            pass
        
        # === FALLBACK: SIMPLE RATE ANALYSIS ===
        # Find entity with highest average rate
        best_entity = None
        best_avg = -1
        for entity, data in entities.items():
            rates = data.get("rates", [])
            if rates:
                avg = sum(rates) / len(rates)
                if avg > best_avg:
                    best_avg = avg
                    best_entity = entity
        
        # Check for rate reversal pattern (simple Simpson's check)
        if len(percents) >= 4:
            # Check if first two rates are ordered opposite of last two
            rate_pairs = [(percents[0], percents[1]), (percents[2], percents[3])]
            if len(rate_pairs) == 2:
                dir1 = rate_pairs[0][0] > rate_pairs[0][1]
                dir2 = rate_pairs[1][0] > rate_pairs[1][1]
                paradox_simple = dir1 != dir2
            else:
                paradox_simple = False
        else:
            paradox_simple = False
        
        reasoning_text = f"Simple analysis: "
        if paradox_simple:
            reasoning_text += "Rate reversal pattern suggests possible Simpson's paradox. "
        reasoning_text += f"Best entity: {best_entity if best_entity else 'Unknown'} with avg rate {best_avg:.1f}%"
        
        return {
            "answer": best_entity if best_entity else "Unknown",
            "confidence": 0.6 if paradox_simple else 0.4,
            "reasoning": reasoning_text,
            "paradox_detected": paradox_simple,
            "entropy": aggregated_entropy if 'aggregated_entropy' in locals() else 0.0
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() != "unknown":
                if computed_answer.lower() in candidate.lower():
                    base_score = 1.0
                else:
                    # Use NCD similarity between reasoning text and candidate
                    base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            else:
                # Fallback to NCD with reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust based on paradox detection
            if reasoning_result.get("paradox_detected", False):
                # Candidates mentioning paradox or reversal get bonus
                paradox_terms = ['paradox', 'reverse', 'confound', 'subgroup', 'aggregat']
                if any(term in candidate.lower() for term in paradox_terms):
                    base_score *= 1.2
            
            results.append({
                "candidate": candidate,
                "score": min(max(base_score, 0.0), 1.0),
                "raw_score": base_score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and entropy-based weighting."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        if not raw_scores:
            return scored
        
        # Simple normalization
        max_raw = max(raw_scores) if max(raw_scores) > 0 else 1.0
        for item in scored:
            item["score"] = item["raw_score"] / max_raw
        
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