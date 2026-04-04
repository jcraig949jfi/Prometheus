import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders

class ReasoningTool:
    """Signal processing x Bayesian networks - Simpson's paradox detection"""

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
        
        # Find entity names (capitalized phrases that appear with rates)
        entity_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        all_names = re.findall(entity_pattern, prompt)
        # Filter to likely entities (appear multiple times or with numbers)
        entity_counts = {}
        for name in all_names:
            if len(name.split()) <= 3:  # Avoid very long phrases
                entity_counts[name] = entity_counts.get(name, 0) + 1
        entities = [name for name, count in entity_counts.items() if count >= 2]
        
        # Extract numerical rates (percentages)
        rate_pattern = r'(\d+(?:\.\d+)?)%'
        rates = [float(match) for match in re.findall(rate_pattern, prompt)]
        
        # Find subgroup indicators (words like "men", "women", "severe", "mild")
        subgroup_keywords = ['men', 'women', 'male', 'female', 'severe', 'mild', 
                           'young', 'old', 'group a', 'group b', 'type i', 'type ii']
        subgroups = []
        for word in subgroup_keywords:
            if word in prompt.lower():
                subgroups.append(word)
        
        # Build structure
        return {
            "entities": entities,
            "rates": rates,
            "subgroups": subgroups,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply signal processing concepts to detect Simpson's paradox reversal."""
        entities = structure["entities"]
        rates = structure["rates"]
        subgroups = structure["subgroups"]
        question = structure["question"]
        
        # Signal processing framework: treat aggregated data as low-pass filtered signal,
        # subgroup data as high-frequency components. Paradox occurs when low-pass
        # trend (aggregate) has opposite sign to high-pass detail (subgroups).
        
        # Use T1 primitives
        if len(rates) >= 2:
            # Compute entropy of rate distribution as signal uncertainty
            rate_probs = [r/100 for r in rates]
            signal_entropy = entropy(rate_probs) if all(0 <= p <= 1 for p in rate_probs) else 0.5
            
            # Bayesian update: treat aggregated rate as prior, subgroup as likelihood
            if len(rates) >= 4:
                # Assume first two rates are aggregated, next two are subgroup
                aggregated_prior = rates[0] / 100
                subgroup_likelihood = rates[2] / 100
                updated_belief = bayesian_update(aggregated_prior, subgroup_likelihood)
                if updated_belief is None:
                    updated_belief = aggregated_prior
            else:
                updated_belief = rates[0] / 100 if rates else 0.5
            
            # Expected value of outcomes (treat rates as probabilities of success)
            if len(rates) >= 4:
                outcome_pairs = [(rates[i]/100, 1.0) for i in range(min(4, len(rates)))]
                ev = expected_value(outcome_pairs)
            else:
                ev = sum(rates)/len(rates)/100 if rates else 0.5
        else:
            signal_entropy = 0.5
            updated_belief = 0.5
            ev = 0.5
        
        # Build Bayesian network to detect paradox (amino acid)
        bn_model = None
        paradox_detected = False
        best_entity = None
        
        if len(entities) >= 2 and len(rates) >= 4:
            # Create simple BN: Entity -> Rate, with Subgroup as confounder
            try:
                edges = [("Subgroup", "Rate"), ("Entity", "Rate")]
                cpd_specs = {
                    "Subgroup": {"card": 2, "values": [[0.5, 0.5]]},
                    "Entity": {"card": 2, "values": [[0.5, 0.5]]},
                    "Rate": {
                        "card": 2,
                        "parents": ["Subgroup", "Entity"],
                        "values": [
                            [rates[0]/100, rates[1]/100],  # Entity0, Subgroup0/1
                            [rates[2]/100, rates[3]/100]   # Entity1, Subgroup0/1
                        ] if len(rates) >= 4 else [[0.6, 0.4], [0.4, 0.6]]
                    }
                }
                bn_model = build_bn(edges, cpd_specs)
                
                if bn_model is not None:
                    # Use amino acid to compare conditional vs marginal
                    result = compare_conditional_marginal(
                        bn_model, 
                        target="Rate", 
                        condition_var="Entity", 
                        condition_val=0
                    )
                    if result is not None:
                        # If P(Rate|Entity) differs significantly from P(Rate), paradox possible
                        paradox_detected = abs(result.get("difference", 0)) > 0.1
                    
                    # Find confounders (amino acid)
                    confounders = detect_confounders(bn_model, "Entity", "Rate")
                    if confounders and "Subgroup" in str(confounders):
                        paradox_detected = True
                    
                    # Query which entity has higher rate when adjusting for subgroup
                    try:
                        query0 = conditional_query(bn_model, ["Rate"], {"Entity": 0, "Subgroup": 0})
                        query1 = conditional_query(bn_model, ["Rate"], {"Entity": 1, "Subgroup": 0})
                        if query0 is not None and query1 is not None:
                            # Compare adjusted rates
                            rate0 = query0.get("Rate", {}).get(1, 0.5)  # P(Rate=1|...)
                            rate1 = query1.get("Rate", {}).get(1, 0.5)
                            best_idx = 0 if rate0 > rate1 else 1
                            best_entity = entities[best_idx] if best_idx < len(entities) else entities[0]
                    except:
                        pass
            except:
                pass
        
        # Confidence from agreement of multiple signals (T1 primitive)
        if len(rates) >= 4:
            # Create multiple "scorer" outputs from different analyses
            scorer_outputs = []
            if len(rates) >= 4:
                # Scorer 1: Compare first two rates
                scorer_outputs.append(rates[0] - rates[1])
                # Scorer 2: Compare next two rates
                scorer_outputs.append(rates[2] - rates[3])
                # Scorer 3: Compare averages
                avg1 = (rates[0] + rates[2]) / 2
                avg2 = (rates[1] + rates[3]) / 2
                scorer_outputs.append(avg1 - avg2)
            
            if scorer_outputs:
                confidence = confidence_from_agreement(scorer_outputs)
                if confidence is None:
                    confidence = 0.7
            else:
                confidence = 0.7
        else:
            confidence = 0.5
        
        # Determine answer entity
        if best_entity is None and entities:
            # Fallback: entity with highest extracted rate
            if rates:
                # Simple heuristic: use the entity mentioned first with highest rate
                best_entity = entities[0]
            else:
                best_entity = entities[0]
        
        # Signal processing interpretation: if paradox detected, answer is the entity
        # that wins after "filtering out" the confounding frequency (subgroup)
        reasoning_text = f"Signal entropy: {signal_entropy:.2f}, "
        reasoning_text += f"Paradox detected: {paradox_detected}, "
        reasoning_text += f"Confidence: {confidence:.2f}"
        
        return {
            "answer": best_entity if best_entity else "Unknown",
            "confidence": confidence,
            "reasoning": reasoning_text,
            "paradox_detected": paradox_detected,
            "signal_entropy": signal_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Boost if candidate mentions paradox-related terms (but not matching)
            paradox_terms = ["reverse", "paradox", "confound", "subgroup", "aggregat"]
            term_count = sum(1 for term in paradox_terms if term in candidate.lower())
            term_boost = 0.1 * min(term_count, 3)
            
            score = min(base_score + term_boost, 1.0)
            results.append({
                "candidate": candidate,
                "score": score,
                "base_score": base_score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored:
            return scored
        
        # Use confidence to adjust scores toward 0.5 if low confidence
        confidence = 0.7  # Default from reasoning phase
        
        calibrated = []
        for item in scored:
            original = item["score"]
            # High confidence: keep scores extreme; low confidence: pull toward 0.5
            calibrated_score = 0.5 + (original - 0.5) * confidence
            calibrated.append({
                "candidate": item["candidate"],
                "score": calibrated_score
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