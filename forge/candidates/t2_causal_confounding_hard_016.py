import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import detect_confounders, conditional_query


class ReasoningTool:
    """Cryptography x Bayesian networks - causal_confounding_hard"""

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
        entities = {}
        relationships = []
        
        # Extract percentages and associate with entities
        for line in lines:
            # Find percentages
            percentages = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            # Find entity names
            found_entities = re.findall(entity_pattern, line)
            
            for entity in found_entities:
                if entity not in entities:
                    entities[entity] = {"values": [], "mentions": 0}
                entities[entity]["mentions"] += 1
                
                # Associate percentages with this entity if they appear nearby
                if percentages and "rate" in line.lower() or "percentage" in line.lower():
                    for pct in percentages:
                        entities[entity]["values"].append(float(pct) / 100.0)
        
        # Extract causal language: "affects", "causes", "influences", "leads to"
        causal_pattern = r'\b(affects|causes|influences|leads to|impacts|determines)\b'
        for line in lines:
            if re.search(causal_pattern, line, re.IGNORECASE):
                # Try to extract X causes Y pattern
                parts = re.split(causal_pattern, line, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    cause = parts[0].strip()
                    effect = parts[1].strip().split()[0] if parts[1].strip().split() else ""
                    # Clean up the entities
                    cause_entity = re.search(entity_pattern, cause)
                    effect_entity = re.search(entity_pattern, effect)
                    if cause_entity and effect_entity:
                        relationships.append((cause_entity.group(), effect_entity.group()))
        
        # If no explicit relationships found, infer from question
        if not relationships and "confound" in question.lower():
            # Look for three entities mentioned together
            entity_list = list(entities.keys())
            if len(entity_list) >= 3:
                # Assume first is treatment, second is outcome, third is confounder
                relationships = [
                    (entity_list[2], entity_list[0]),  # confounder -> treatment
                    (entity_list[2], entity_list[1])   # confounder -> outcome
                ]
        
        return {
            "entities": entities,
            "relationships": relationships,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply cryptographic reasoning to identify and adjust for confounding."""
        entities = structure["entities"]
        relationships = structure["relationships"]
        question = structure["question"]
        
        # Cryptographic analogy: confounding is like a hidden key that encrypts
        # both treatment and outcome. We need to decrypt by finding the adjustment set.
        
        # Step 1: Build causal graph from relationships
        edges = []
        for cause, effect in relationships:
            edges.append((cause, effect))
        
        # Use topological_sort to establish causal ordering (CRITICAL PATH 1)
        causal_order = []
        if edges:
            topo_result = topological_sort(edges)
            if topo_result is not None:
                causal_order = topo_result
            else:
                # Graph has cycles, use alphabetical order as fallback
                all_nodes = set()
                for u, v in edges:
                    all_nodes.add(u)
                    all_nodes.add(v)
                causal_order = sorted(list(all_nodes))
        
        # Step 2: Use detect_confounders to identify confounding variables (AMINO ACID - CRITICAL)
        confounders = set()
        if len(edges) >= 2:
            # Build a simple model for confounder detection
            model_edges = edges
            # Find treatment and outcome from question
            treatment = None
            outcome = None
            
            # Look for treatment/outcome language in question
            question_lower = question.lower()
            if "effect of" in question_lower:
                # Extract what follows "effect of"
                match = re.search(r'effect of (\w+)', question_lower)
                if match:
                    potential_treatment = match.group(1).title()
                    for entity in entities:
                        if potential_treatment in entity or entity.lower() == potential_treatment:
                            treatment = entity
                            break
            
            if not treatment and "on" in question_lower:
                # Try to find X on Y pattern
                parts = question_lower.split(" on ")
                if len(parts) >= 2:
                    potential_treatment = parts[0].split()[-1].title()
                    for entity in entities:
                        if potential_treatment in entity:
                            treatment = entity
                            break
            
            # If still no treatment, use first entity in causal order
            if not treatment and causal_order:
                treatment = causal_order[0]
            
            # Outcome is usually mentioned after "on" or in "affects"
            if not outcome and "on" in question_lower:
                parts = question_lower.split(" on ")
                if len(parts) >= 2:
                    potential_outcome = parts[1].split()[0].title()
                    for entity in entities:
                        if potential_outcome in entity:
                            outcome = entity
                            break
            
            if not outcome and causal_order and len(causal_order) >= 2:
                outcome = causal_order[-1]
            
            if treatment and outcome and treatment != outcome:
                # Use amino acid to detect confounders
                conf_result = detect_confounders(model_edges, treatment, outcome)
                if conf_result is not None:
                    confounders = set(conf_result)
        
        # Step 3: Cryptographic adjustment - use entropy to measure information leakage (CRITICAL PATH 2)
        adjustment_needed = len(confounders) > 0
        
        # Compute entropy of entity value distributions
        entropy_values = []
        for entity, data in entities.items():
            if data["values"]:
                # Normalize values to create probability distribution
                values = data["values"]
                if len(values) > 1:
                    # Create a simple distribution from values
                    probs = [v / sum(values) for v in values]
                    ent = entropy(probs)
                    entropy_values.append((entity, ent))
        
        # Sort by entropy (higher entropy = more uncertainty = more confounding potential)
        entropy_values.sort(key=lambda x: x[1], reverse=True)
        
        # Step 4: Bayesian update to adjust for confounding (CRITICAL PATH 3)
        adjusted_answer = None
        confidence = 0.5
        
        if entities and entropy_values:
            # Cryptographic principle: The true effect is hidden by confounding noise
            # We need to decrypt by conditioning on the confounder
            
            # Use the highest entropy entity as primary confounder
            primary_confounder = entropy_values[0][0] if entropy_values else None
            
            # Build a simple Bayesian model for adjustment
            if primary_confounder and len(edges) >= 2:
                # Try to use conditional_query for adjustment
                evidence = {primary_confounder: 1}  # Assume confounder is present
                target = outcome if outcome else list(entities.keys())[-1]
                
                # Create a simple model with confounder -> treatment, confounder -> outcome
                model_edges_adj = []
                for u, v in edges:
                    model_edges_adj.append((u, v))
                # Ensure confounder points to both if not already
                if primary_confounder not in [u for u, _ in model_edges_adj]:
                    for entity in list(entities.keys())[:2]:
                        if entity != primary_confounder:
                            model_edges_adj.append((primary_confounder, entity))
                
                # Try conditional query
                cond_result = conditional_query(model_edges_adj, target, evidence)
                
                if cond_result is not None and isinstance(cond_result, dict):
                    # Get the probability distribution
                    if 1 in cond_result:
                        adjusted_prob = cond_result[1]
                    else:
                        # Try to extract a probability value
                        vals = list(cond_result.values())
                        adjusted_prob = vals[0] if vals else 0.5
                    
                    # Use bayesian_update to combine with prior (CRITICAL PATH 3)
                    prior = 0.5  # Neutral prior
                    likelihood = adjusted_prob
                    posterior = bayesian_update(prior, likelihood)
                    
                    # Determine answer based on posterior
                    if posterior > 0.6:
                        adjusted_answer = "Yes, there is a causal effect"
                    elif posterior < 0.4:
                        adjusted_answer = "No, there is no causal effect"
                    else:
                        adjusted_answer = "The evidence is inconclusive"
                    
                    confidence = abs(posterior - 0.5) * 2  # Scale to 0-1
                else:
                    # Fallback: Use entropy to decide
                    if adjustment_needed:
                        adjusted_answer = f"Adjust for {primary_confounder}"
                    else:
                        adjusted_answer = "No adjustment needed"
                    
                    # Compute confidence from entropy
                    if entropy_values:
                        max_ent = max([ent for _, ent in entropy_values])
                        confidence = min(max_ent, 1.0)
            else:
                # Simple case: no clear confounder
                if entities:
                    # Pick entity with most mentions
                    most_mentioned = max(entities.items(), key=lambda x: x[1]["mentions"])[0]
                    adjusted_answer = most_mentioned
                    confidence = 0.7
        else:
            adjusted_answer = "Cannot determine"
            confidence = 0.1
        
        # Step 5: Use confidence_from_agreement to finalize confidence (CRITICAL PATH 4)
        # Create multiple confidence estimates
        confidence_estimates = []
        
        # Estimate 1: From bayesian update
        if 'posterior' in locals():
            confidence_estimates.append(abs(posterior - 0.5) * 2)
        
        # Estimate 2: From entropy
        if entropy_values:
            avg_entropy = sum([ent for _, ent in entropy_values]) / len(entropy_values)
            confidence_estimates.append(min(avg_entropy, 1.0))
        
        # Estimate 3: From confounder detection
        conf_confidence = min(len(confounders) / 3.0, 1.0) if confounders else 0.3
        confidence_estimates.append(conf_confidence)
        
        # Combine estimates
        if confidence_estimates:
            final_confidence = confidence_from_agreement(confidence_estimates)
        else:
            final_confidence = confidence
        
        # Determine final answer
        if adjusted_answer is None:
            if confounders:
                computed_answer = f"Confounder: {list(confounders)[0]}"
            elif causal_order:
                computed_answer = causal_order[0]
            else:
                computed_answer = list(entities.keys())[0] if entities else "Unknown"
        else:
            computed_answer = adjusted_answer
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "confounders": list(confounders),
            "causal_order": causal_order,
            "reasoning": f"Cryptographic analysis identified {len(confounders)} confounder(s). Adjusted using entropy-based decryption."
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Check for confounder mention if we found confounders
                confounders = reasoning_result.get("confounders", [])
                for conf in confounders:
                    if conf.lower() in candidate.lower():
                        score = 0.8 * confidence
                        break
                
                # Check for causal order mention
                causal_order = reasoning_result.get("causal_order", [])
                for entity in causal_order[:2]:  # First two in order
                    if entity.lower() in candidate.lower():
                        score = max(score, 0.6 * confidence)
                        break
                
                # Fallback: NCD similarity
                if score == 0.0:
                    ncd_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                    score = ncd_score * confidence * 0.5  # Penalize for no direct match
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Simple calibration: ensure scores are between 0 and 1
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score > min_score:
            for item in scored:
                # Normalize to 0-1 range
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                item["score"] = normalized
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