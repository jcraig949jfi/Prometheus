import re
import zlib
from typing import Dict, List, Any

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
        
        entities = {}
        subgroups = {}
        current_entity = None
        current_subgroup = None
        
        # Find entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        entities_found = re.findall(entity_pattern, prompt)
        
        # Find percentages and associate with context
        percent_pattern = r'(\d+(?:\.\d+)?)%'
        percentages = re.findall(percent_pattern, prompt)
        percent_floats = [float(p) / 100.0 for p in percentages]
        
        # Parse lines to build structure
        for line in lines:
            line_lower = line.lower()
            
            # Detect entity mentions
            for entity in entities_found:
                if entity in line and entity not in entities:
                    entities[entity] = {"rates": [], "subgroups": {}}
                    current_entity = entity
            
            # Detect subgroup indicators
            if any(word in line_lower for word in ["group", "subgroup", "category", "type", "class"]):
                # Extract subgroup name from the line
                subgroup_match = re.search(r'\b([a-z]+(?: [a-z]+)*)\b', line_lower)
                if subgroup_match:
                    subgroup = subgroup_match.group(1)
                    if subgroup not in ["group", "subgroup", "category", "type", "class"]:
                        subgroups[subgroup] = {"entities": {}}
                        current_subgroup = subgroup
            
            # Extract percentages and associate with current entity/subgroup
            line_percents = re.findall(percent_pattern, line)
            if line_percents and current_entity:
                rates = [float(p) / 100.0 for p in line_percents]
                if current_subgroup:
                    if current_subgroup not in entities[current_entity]["subgroups"]:
                        entities[current_entity]["subgroups"][current_subgroup] = []
                    entities[current_entity]["subgroups"][current_subgroup].extend(rates)
                else:
                    entities[current_entity]["rates"].extend(rates)
        
        # Collect all extracted percentages for information-theoretic analysis
        all_rates = []
        for entity_data in entities.values():
            all_rates.extend(entity_data["rates"])
            for subgroup_rates in entity_data["subgroups"].values():
                all_rates.extend(subgroup_rates)
        
        return {
            "entities": entities,
            "subgroups": subgroups,
            "question": question,
            "all_rates": all_rates,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information theory and Bayesian networks to detect Simpson's paradox."""
        entities = structure["entities"]
        question = structure["question"]
        all_rates = structure["all_rates"]
        
        # Compute information-theoretic measures using T1 primitives
        if all_rates:
            # Convert rates to probabilities for entropy calculation
            probs = [r for r in all_rates if 0 <= r <= 1]
            if len(probs) >= 2:
                # T1 primitive 1: Compute entropy of the rate distribution
                rate_entropy = entropy(probs)
            else:
                rate_entropy = 0.0
            
            # T1 primitive 2: Compute expected value of rates
            if probs:
                ev_pairs = [(1.0/len(probs), p) for p in probs]
                expected_rate = expected_value(ev_pairs)
            else:
                expected_rate = 0.5
        else:
            rate_entropy = 0.0
            expected_rate = 0.5
        
        # Build Bayesian network to analyze conditional vs marginal probabilities
        paradox_detected = False
        best_entity = None
        confidence = 0.5
        
        if len(entities) >= 2:
            entity_names = list(entities.keys())
            
            # Create a simple Bayesian network: Subgroup -> Entity -> Success
            edges = [("Subgroup", "Entity"), ("Entity", "Success")]
            
            # Build CPDs from extracted data
            cpd_specs = {}
            
            # Entity CPD: P(Entity | Subgroup)
            entity_probs = []
            for entity in entity_names:
                entity_data = entities[entity]
                if entity_data["subgroups"]:
                    # Use actual subgroup rates from extraction
                    subgroup_rates = []
                    for sg_rates in entity_data["subgroups"].values():
                        if sg_rates:
                            subgroup_rates.append(sum(sg_rates) / len(sg_rates))
                    if subgroup_rates:
                        entity_prob = sum(subgroup_rates) / len(subgroup_rates)
                    else:
                        entity_prob = 0.5
                else:
                    if entity_data["rates"]:
                        entity_prob = sum(entity_data["rates"]) / len(entity_data["rates"])
                    else:
                        entity_prob = 0.5
                entity_probs.append(entity_prob)
            
            # Normalize entity probabilities
            total_entity = sum(entity_probs) if sum(entity_probs) > 0 else 1.0
            entity_probs = [p/total_entity for p in entity_probs]
            
            # Success CPD: P(Success | Entity)
            success_probs = []
            for entity in entity_names:
                entity_data = entities[entity]
                if entity_data["rates"]:
                    # Use actual aggregated rates
                    success_prob = sum(entity_data["rates"]) / len(entity_data["rates"])
                elif entity_data["subgroups"]:
                    # Average subgroup rates
                    all_sg_rates = []
                    for sg_rates in entity_data["subgroups"].values():
                        all_sg_rates.extend(sg_rates)
                    if all_sg_rates:
                        success_prob = sum(all_sg_rates) / len(all_sg_rates)
                    else:
                        success_prob = 0.5
                else:
                    success_prob = 0.5
                success_probs.append(success_prob)
            
            # Amino acid 1: Build Bayesian network
            bn_model = build_bn(
                edges=edges,
                cpd_specs={
                    "Entity": {"values": entity_probs, "evidence": ["Subgroup"]},
                    "Success": {"values": success_probs, "evidence": ["Entity"]}
                }
            )
            
            if bn_model is not None:
                # Amino acid 2: Compare conditional vs marginal for each entity
                paradox_flags = []
                for i, entity in enumerate(entity_names):
                    # Query P(Success | Entity=entity)
                    cond_query = conditional_query(
                        bn_model,
                        target_vars=["Success"],
                        evidence={"Entity": entity}
                    )
                    
                    # Query P(Success) - marginal
                    marginal_query = conditional_query(
                        bn_model,
                        target_vars=["Success"],
                        evidence={}
                    )
                    
                    if cond_query is not None and marginal_query is not None:
                        # Amino acid 3: Formal Simpson's paradox detection
                        paradox_check = compare_conditional_marginal(
                            bn_model,
                            target="Success",
                            condition_var="Entity",
                            condition_val=entity
                        )
                        
                        if paradox_check is not None:
                            paradox_flags.append(paradox_check)
                
                # Determine if paradox exists
                if paradox_flags:
                    # T1 primitive 3: Compute confidence from agreement of paradox detectors
                    confidence = confidence_from_agreement([1.0 if flag else 0.0 for flag in paradox_flags])
                    paradox_detected = any(paradox_flags)
                
                # Amino acid 4: Detect confounders (subgroups as potential confounders)
                if len(entity_names) >= 2:
                    confounders = detect_confounders(bn_model, "Entity", "Success")
                    if confounders:
                        # If subgroups are confounders, paradox is more likely
                        confidence = min(1.0, confidence + 0.2)
                
                # Determine best entity based on success probability
                if success_probs:
                    best_idx = max(range(len(success_probs)), key=lambda i: success_probs[i])
                    best_entity = entity_names[best_idx]
                    # Adjust confidence based on entropy: low entropy = more certain
                    confidence = confidence * (1.0 - min(rate_entropy, 0.5))
        
        # If Bayesian network failed, fall back to simple rate comparison
        if best_entity is None and entities:
            # Simple comparison of aggregated rates
            entity_scores = {}
            for entity, data in entities.items():
                if data["rates"]:
                    entity_scores[entity] = sum(data["rates"]) / len(data["rates"])
                elif data["subgroups"]:
                    all_rates = []
                    for sg_rates in data["subgroups"].values():
                        all_rates.extend(sg_rates)
                    if all_rates:
                        entity_scores[entity] = sum(all_rates) / len(all_rates)
            
            if entity_scores:
                best_entity = max(entity_scores.items(), key=lambda x: x[1])[0]
                confidence = 0.7 * (1.0 - min(rate_entropy, 0.5))
        
        # Prepare reasoning result
        computed_answer = best_entity if best_entity else "Unknown"
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "paradox_detected": paradox_detected,
            "rate_entropy": rate_entropy,
            "reasoning": f"Analyzed {len(entities)} entities with entropy {rate_entropy:.3f}. "
                        f"Paradox detected: {paradox_detected}. Best entity: {computed_answer}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or partial match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            elif any(word.lower() in candidate.lower() 
                    for word in computed_answer.split() if len(word) > 3):
                base_score = 0.8
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust by confidence from reasoning phase
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
        
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            # Normalize to [0, 1] range
            max_score = max(scores)
            min_score = min(scores)
            
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