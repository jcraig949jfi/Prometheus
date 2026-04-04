import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders, compare_conditional_marginal

class ReasoningTool:
    """Electromagnetism x Bayesian networks - Simpson's paradox detection"""

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
        
        # Find entity names (capitalized multi-word phrases that appear with numbers)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_entities = re.findall(entity_pattern, prompt)
        
        # Find all percentage rates
        rate_pattern = r'(\d+(?:\.\d+)?)%'
        all_rates = [float(match) for match in re.findall(rate_pattern, prompt)]
        
        # Find subgroup indicators (words like "men", "women", "severe", "mild")
        subgroup_keywords = ['men', 'women', 'male', 'female', 'severe', 'mild', 
                            'young', 'old', 'group a', 'group b', 'type i', 'type ii']
        subgroups = []
        for word in subgroup_keywords:
            if word in prompt.lower():
                subgroups.append(word)
        
        # Build entity-rate mapping by proximity
        entities = {}
        sentences = prompt.split('.')
        for sentence in sentences:
            sentence_entities = re.findall(entity_pattern, sentence)
            sentence_rates = [float(match) for match in re.findall(rate_pattern, sentence)]
            
            for entity in sentence_entities:
                if entity not in entities:
                    entities[entity] = {"rates": [], "subgroups": {}}
                if sentence_rates:
                    entities[entity]["rates"].extend(sentence_rates)
        
        # Try to associate rates with subgroups
        for i, sentence in enumerate(sentences):
            lower_sentence = sentence.lower()
            for subgroup in subgroups:
                if subgroup in lower_sentence:
                    # Find rates in this sentence
                    sentence_rates = [float(match) for match in re.findall(rate_pattern, sentence)]
                    if sentence_rates:
                        # Find the nearest entity in this sentence
                        sentence_entities = re.findall(entity_pattern, sentence)
                        if sentence_entities:
                            entity = sentence_entities[0]
                            if entity in entities:
                                if subgroup not in entities[entity]["subgroups"]:
                                    entities[entity]["subgroups"][subgroup] = []
                                entities[entity]["subgroups"][subgroup].extend(sentence_rates)
        
        return {
            "entities": entities,
            "subgroups": subgroups,
            "all_rates": all_rates,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use electromagnetic field analogy: rates as charges, subgroups as field regions."""
        entities = structure["entities"]
        subgroups = structure["subgroups"]
        all_rates = structure["all_rates"]
        
        # Use T1 primitives
        # 1. Compute entropy of rates as measure of disorder (like thermal noise)
        if all_rates:
            rate_probs = [r/100 for r in all_rates]
            rate_entropy = entropy(rate_probs) if all(p >= 0 and p <= 1 for p in rate_probs) else 0.5
        else:
            rate_entropy = 0.5
        
        # 2. Bayesian update to adjust confidence based on subgroup consistency
        # Prior: equal belief in each entity being best
        prior = 0.5
        # Likelihood: how consistent are subgroup rates?
        consistency_scores = []
        for entity, data in entities.items():
            if data.get("subgroups"):
                subgroup_rates = []
                for sub_rates in data["subgroups"].values():
                    if sub_rates:
                        subgroup_rates.append(sum(sub_rates)/len(sub_rates)/100)
                if subgroup_rates:
                    # Compute variance as inverse consistency
                    mean_rate = sum(subgroup_rates)/len(subgroup_rates)
                    variance = sum((r - mean_rate)**2 for r in subgroup_rates)/len(subgroup_rates) if len(subgroup_rates) > 1 else 0
                    consistency = 1.0 - min(variance, 1.0)
                    consistency_scores.append(consistency)
        
        avg_consistency = sum(consistency_scores)/len(consistency_scores) if consistency_scores else 0.5
        updated_belief = bayesian_update(prior, avg_consistency, false_positive=0.1)
        
        # 3. Expected value of choosing each entity
        entity_evs = {}
        for entity, data in entities.items():
            if data.get("rates"):
                # Convert rates to probabilities
                probs = [r/100 for r in data["rates"]]
                # Value is the rate itself (higher is better)
                outcomes = [(1.0/len(probs), p) for p in probs] if probs else [(1.0, 0.5)]
                ev = expected_value(outcomes)
                entity_evs[entity] = ev
        
        # Use amino acid: build Bayesian network to detect Simpson's paradox
        # Model: Entity -> Subgroup -> Rate (confounding structure)
        best_entity = None
        paradox_detected = False
        
        if len(entities) >= 2 and subgroups:
            try:
                # Build simple BN: Entity influences Rate, Subgroup influences both
                edges = [("Entity", "Rate"), ("Subgroup", "Entity"), ("Subgroup", "Rate")]
                
                # Create CPDs from extracted data
                entity_names = list(entities.keys())
                subgroup_names = subgroups if subgroups else ["default"]
                
                # Entity CPD: P(Entity | Subgroup) - uniform for now
                entity_cpd = []
                for sub in subgroup_names:
                    for ent in entity_names:
                        entity_cpd.append([sub, ent, 1.0/len(entity_names)])
                
                # Rate CPD: P(Rate | Entity, Subgroup) - use extracted rates
                rate_cpd = []
                for ent in entity_names:
                    for sub in subgroup_names:
                        # Get rates for this entity-subgroup combination
                        ent_data = entities[ent]
                        sub_rates = ent_data.get("subgroups", {}).get(sub, [])
                        if sub_rates:
                            avg_rate = sum(sub_rates)/len(sub_rates)/100
                        else:
                            # Fallback to overall entity rate
                            overall_rates = ent_data.get("rates", [50.0])
                            avg_rate = sum(overall_rates)/len(overall_rates)/100
                        
                        # Simplified: Rate is binary (high/low)
                        rate_high = avg_rate
                        rate_low = 1.0 - avg_rate
                        rate_cpd.append([ent, sub, "high", rate_high])
                        rate_cpd.append([ent, sub, "low", rate_low])
                
                cpd_specs = {
                    "Entity": {"variables": ["Subgroup"], "values": entity_cpd},
                    "Rate": {"variables": ["Entity", "Subgroup"], "values": rate_cpd}
                }
                
                model = build_bn(edges, cpd_specs)
                
                if model:
                    # Check for Simpson's paradox using compare_conditional_marginal
                    for ent in entity_names:
                        result = compare_conditional_marginal(model, "Rate", "Entity", ent)
                        if result and "difference" in result:
                            # Large difference indicates conditioning matters
                            if abs(result["difference"]) > 0.2:
                                paradox_detected = True
                    
                    # Query: which entity has highest P(Rate=high)
                    best_prob = -1
                    for ent in entity_names:
                        query_result = conditional_query(model, ["Rate"], {"Entity": ent})
                        if query_result and "high" in query_result:
                            prob = query_result["high"]
                            if prob > best_prob:
                                best_prob = prob
                                best_entity = ent
            except Exception:
                # Fallback to simpler reasoning
                pass
        
        # If BN failed, use expected values
        if not best_entity and entity_evs:
            best_entity = max(entity_evs.items(), key=lambda x: x[1])[0]
        
        # 4. Confidence from agreement between different methods
        scores_to_agree = []
        if updated_belief:
            scores_to_agree.append(updated_belief)
        if entity_evs and best_entity in entity_evs:
            scores_to_agree.append(entity_evs[best_entity])
        if rate_entropy:
            scores_to_agree.append(1.0 - rate_entropy)  # Low entropy = high confidence
        
        confidence = confidence_from_agreement(scores_to_agree) if scores_to_agree else 0.5
        
        # Final answer: the entity name
        computed_answer = best_entity if best_entity else list(entities.keys())[0] if entities else "Unknown"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "paradox_detected": paradox_detected,
            "reasoning": f"Analyzed {len(entities)} entities across {len(subgroups)} subgroups. "
                        f"Electromagnetic analogy: rates as charges, subgroup consistency as field uniformity. "
                        f"Paradox detection: {paradox_detected}",
            "entity_evs": entity_evs
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
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