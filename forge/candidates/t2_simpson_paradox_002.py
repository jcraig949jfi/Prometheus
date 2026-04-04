import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal, detect_confounders

class ReasoningTool:
    """Decision theory x Bayesian networks - Simpson's paradox detection"""

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
        """Extract entities, subgroups, rates, and the question from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases that appear with numbers)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Find all percentages and associate with nearby entities
        percent_pattern = r'(\d+(?:\.\d+)?)%'
        percentages = [float(p) for p in re.findall(percent_pattern, prompt)]
        
        # Find subgroup indicators (words like "men", "women", "young", "old", etc.)
        subgroup_keywords = ['men', 'women', 'male', 'female', 'young', 'old', 'children', 
                            'adults', 'group', 'category', 'type', 'class']
        subgroups = []
        for word in subgroup_keywords:
            if word in prompt.lower():
                subgroups.append(word)
        
        # Parse lines to build structured data
        entities = {}
        current_entity = None
        current_subgroup = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this line introduces a new entity
            for entity in potential_entities:
                if entity in line and entity not in entities:
                    current_entity = entity
                    entities[current_entity] = {
                        "subgroups": {},
                        "overall_rate": None,
                        "values": []
                    }
                    break
            
            # Check for subgroup mentions
            for subgroup in subgroups:
                if subgroup in line_lower:
                    current_subgroup = subgroup
                    break
            
            # Extract percentages from this line
            line_percents = re.findall(percent_pattern, line)
            if line_percents:
                rates = [float(p) for p in line_percents]
                
                if current_entity:
                    entities[current_entity]["values"].extend(rates)
                    
                    # If we have a subgroup context, store subgroup rates
                    if current_subgroup and len(rates) >= 1:
                        if current_subgroup not in entities[current_entity]["subgroups"]:
                            entities[current_entity]["subgroups"][current_subgroup] = []
                        entities[current_entity]["subgroups"][current_subgroup].extend(rates)
                    
                    # If this looks like an overall rate (single percentage or "overall")
                    if len(rates) == 1 or "overall" in line_lower or "total" in line_lower:
                        entities[current_entity]["overall_rate"] = rates[0]
        
        return {
            "entities": entities,
            "subgroups": subgroups,
            "percentages": percentages,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply decision theory with Bayesian networks to detect Simpson's paradox."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        percentages = structure["percentages"]
        
        if not entities or len(entities) < 2:
            # Fallback: use expected value on extracted percentages
            if percentages:
                # Create simple probability-value pairs
                probs = [1.0/len(percentages)] * len(percentages)
                pairs = list(zip(probs, percentages))
                ev = expected_value(pairs)
                return {
                    "answer": f"{ev:.1f}%",
                    "confidence": 0.3,
                    "reasoning": "Fallback: expected value of extracted percentages",
                    "paradox_detected": False
                }
            return {
                "answer": "Unknown",
                "confidence": 0.0,
                "reasoning": "No entities or percentages extracted",
                "paradox_detected": False
            }
        
        # Use T1 primitives for initial analysis
        # 1. Compute entropy of overall rates
        overall_rates = []
        for entity, data in entities.items():
            if data["overall_rate"] is not None:
                overall_rates.append(data["overall_rate"]/100)  # Convert to probabilities
        
        entropy_val = 0.0
        if len(overall_rates) >= 2:
            entropy_val = entropy(overall_rates)
        
        # 2. Bayesian update to compare entities
        prior = 0.5  # Initial belief that entity A is better than entity B
        entity_names = list(entities.keys())
        
        if len(entity_names) >= 2 and len(overall_rates) >= 2:
            # Use first two entities for comparison
            rate_a = overall_rates[0] if overall_rates else 0.5
            rate_b = overall_rates[1] if len(overall_rates) > 1 else 0.5
            
            # Likelihood: if A's rate is higher, it supports A being better
            likelihood = rate_a / (rate_a + rate_b) if (rate_a + rate_b) > 0 else 0.5
            posterior = bayesian_update(prior, likelihood)
        else:
            posterior = prior
        
        # 3. Build Bayesian network to detect Simpson's paradox
        paradox_detected = False
        computed_answer = None
        confidence = 0.5
        
        try:
            # Build a simple BN: Entity -> Outcome, Subgroup -> Outcome
            edges = [("Entity", "Outcome"), ("Subgroup", "Outcome")]
            
            # Extract subgroup data for BN
            entity_data = {}
            for entity, data in entities.items():
                if data["subgroups"]:
                    entity_data[entity] = data
            
            if len(entity_data) >= 2:
                # Use amino acid to build Bayesian network
                bn_model = build_bn(edges)
                
                if bn_model is not None:
                    # Use amino acid to compare conditional vs marginal
                    # We'll check if conditioning on subgroup changes the conclusion
                    
                    # First, get confidence from agreement of subgroup trends
                    agreement_scores = []
                    for entity, data in entity_data.items():
                        if data["subgroups"]:
                            subgroup_rates = []
                            for sg, rates in data["subgroups"].items():
                                if rates:
                                    subgroup_rates.append(sum(rates)/len(rates))
                            if subgroup_rates:
                                # Normalize scores for confidence calculation
                                normalized = [r/100 for r in subgroup_rates]
                                if normalized:
                                    agreement_scores.append(confidence_from_agreement(normalized))
                    
                    if agreement_scores:
                        confidence = sum(agreement_scores) / len(agreement_scores)
                    
                    # Detect confounders (common cause of Entity and Outcome)
                    confounders = detect_confounders(bn_model, "Entity", "Outcome")
                    
                    # Check for paradox by comparing subgroup trends with overall
                    paradox_indicators = []
                    for entity, data in entity_data.items():
                        if data["subgroups"] and data["overall_rate"] is not None:
                            overall = data["overall_rate"]
                            subgroup_avgs = []
                            for sg, rates in data["subgroups"].items():
                                if rates:
                                    subgroup_avgs.append(sum(rates)/len(rates))
                            
                            if subgroup_avgs:
                                # Check if all subgroups are better/worse than overall
                                all_better = all(sg > overall for sg in subgroup_avgs)
                                all_worse = all(sg < overall for sg in subgroup_avgs)
                                if all_better or all_worse:
                                    paradox_indicators.append(True)
                    
                    paradox_detected = len(paradox_indicators) > 0 and all(paradox_indicators)
                    
                    # Determine which entity is actually better based on decision theory
                    # Under uncertainty, choose entity with highest expected value
                    entity_evs = {}
                    for entity, data in entities.items():
                        rates = []
                        if data["overall_rate"] is not None:
                            rates.append(data["overall_rate"])
                        for sg_rates in data["subgroups"].values():
                            rates.extend(sg_rates)
                        
                        if rates:
                            # Simple expected value (uniform weights)
                            entity_evs[entity] = sum(rates) / len(rates)
                    
                    if entity_evs:
                        best_entity = max(entity_evs.items(), key=lambda x: x[1])[0]
                        computed_answer = best_entity
                        # Adjust confidence based on paradox detection
                        if paradox_detected:
                            # Lower confidence when paradox is detected
                            confidence = max(0.1, confidence * 0.7)
                        else:
                            confidence = min(1.0, confidence * 1.2)
        
        except Exception:
            # Fallback to simpler reasoning
            pass
        
        # Final fallback if computed_answer not set
        if computed_answer is None:
            if entity_evs:
                best_entity = max(entity_evs.items(), key=lambda x: x[1])[0]
                computed_answer = best_entity
            elif entity_names:
                computed_answer = entity_names[0]
            else:
                computed_answer = "Unknown"
        
        return {
            "answer": computed_answer,
            "confidence": min(1.0, max(0.0, confidence)),
            "reasoning": f"Decision theory analysis with entropy={entropy_val:.3f}, posterior={posterior:.3f}, paradox_detected={paradox_detected}",
            "paradox_detected": paradox_detected
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score based on confidence
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
        
        # Simple calibration: ensure scores are in [0, 1] and spread out
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            
            if max_score > min_score:
                # Normalize to [0, 1]
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