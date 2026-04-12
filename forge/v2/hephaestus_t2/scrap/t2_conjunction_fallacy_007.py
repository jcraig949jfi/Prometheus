import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query


class ReasoningTool:
    """Immunology x Bayesian networks - Conjunction fallacy"""

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
        """Parse prompt to extract entities, probabilities, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all percentages and associate with nearby entities
        entities = {}
        current_entity = None
        
        # Look for patterns like "Entity A has a 30% chance of X"
        for line in lines:
            # Extract percentages
            percentages = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            if not percentages:
                continue
                
            # Extract entity names (capitalized words or phrases)
            # Look for patterns before "has", "of", or "with"
            entity_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
            if entity_match:
                current_entity = entity_match.group(1)
                if current_entity not in entities:
                    entities[current_entity] = {"probabilities": []}
                
                # Convert percentages to probabilities
                for pct in percentages:
                    entities[current_entity]["probabilities"].append(float(pct) / 100.0)
        
        # If no entities found with percentages, look for generic options
        if not entities:
            # Look for options like "Option A", "Choice B", etc.
            option_pattern = r'(Option|Choice|Alternative)\s+([A-Z])'
            for line in lines:
                matches = re.findall(option_pattern, line, re.IGNORECASE)
                for _, opt in matches:
                    entity_name = f"Option {opt}"
                    if entity_name not in entities:
                        entities[entity_name] = {"probabilities": []}
                    # Extract any numbers in the same line
                    numbers = re.findall(r'([0-9]+\.?[0-9]*)%?', line)
                    for num in numbers:
                        if '.' in num or len(num) > 2:  # Likely a probability
                            val = float(num)
                            if val > 1.0:  # Probably a percentage
                                val = val / 100.0
                            entities[entity_name]["probabilities"].append(val)
        
        # Extract conjunction phrases (e.g., "A and B", "both X and Y")
        conjunctions = []
        for line in lines:
            # Look for patterns like "A and B", "both X and Y"
            conj_match = re.search(r'both\s+([A-Za-z\s]+)\s+and\s+([A-Za-z\s]+)', line, re.IGNORECASE)
            if conj_match:
                conjunctions.append((conj_match.group(1).strip(), conj_match.group(2).strip()))
            else:
                # Simple "and" between capitalized words
                simple_conj = re.findall(r'([A-Z][a-z]+)\s+and\s+([A-Z][a-z]+)', line)
                conjunctions.extend(simple_conj)
        
        return {
            "entities": entities,
            "conjunctions": conjunctions,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use immunology framework: probabilities as antigen binding affinities,
        conjunction as co-stimulation requiring both signals."""
        entities = structure["entities"]
        conjunctions = structure["conjunctions"]
        
        if not entities:
            return {"answer": "Cannot determine", "confidence": 0.0, "reasoning": "No entities found"}
        
        # Immunology concept: Antigen binding affinity = probability
        # Co-stimulation requires both signals (conjunction) -> probability must be lower than individual
        # Immune response threshold determines which option is "activated" (correct)
        
        # Build Bayesian network for conjunction reasoning
        # Variables: individual events as antigens, conjunction as co-stimulation
        edges = []
        cpd_specs = {}
        
        # Create nodes for each entity
        entity_nodes = list(entities.keys())
        
        # If we have conjunctions, model them
        if conjunctions:
            # Use first conjunction found
            conj = conjunctions[0]
            conj_name = f"{conj[0]}_and_{conj[1]}"
            
            # Create edges: individual events -> conjunction
            edges = [(conj[0], conj_name), (conj[1], conj_name)]
            
            # Get probabilities from extracted data
            p1 = entities.get(conj[0], {}).get("probabilities", [0.5])[0] if conj[0] in entities else 0.5
            p2 = entities.get(conj[1], {}).get("probabilities", [0.5])[0] if conj[1] in entities else 0.5
            
            # CRITICAL: Use bayesian_update to compute conjunction probability
            # P(A∧B) = P(A) * P(B|A) ≈ P(A) * P(B) if independent
            # Use bayesian_update with false_positive=0 to get P(B|A) assuming dependence
            # For independence: P(B|A) = P(B)
            p_b_given_a = bayesian_update(p2, 1.0, 0.0)  # P(B|A) assuming perfect evidence
            
            # Immunology: Co-stimulation probability is product of individual binding affinities
            # (if independent) or lower if dependent
            conj_prob = p1 * p_b_given_a
            
            # Build CPD for conjunction node
            # P(conjunction=1 | A=1, B=1) = 1, else 0
            cpd_specs = {
                conj[0]: [[p1], [1-p1]],
                conj[1]: [[p2], [1-p2]],
                conj_name: {
                    'variable': conj_name,
                    'variable_card': 2,
                    'evidence': [conj[0], conj[1]],
                    'evidence_card': [2, 2],
                    'values': [[0, 0, 0, 1], [1, 1, 1, 0]]  # Only true when both parents are 1
                }
            }
            
            try:
                # CRITICAL: Use amino acid to build Bayesian network
                model = build_bn(edges, cpd_specs)
                if model:
                    # Query probability of conjunction
                    query_result = conditional_query(model, [conj_name], {})
                    if query_result and conj_name in query_result:
                        conj_prob_from_bn = query_result[conj_name].get(1, 0.0)
                        
                        # Immunology: Compare with individual probabilities
                        # Entropy measures uncertainty in immune recognition
                        individual_probs = [p1, p2]
                        entropy_val = entropy(individual_probs)
                        
                        # Expected value of immune response
                        outcomes = [(p1, 1.0), (1-p1, 0.0), (p2, 1.0), (1-p2, 0.0)]
                        exp_val = expected_value(outcomes)
                        
                        # Determine which is more probable: individual or conjunction
                        # Immunology principle: Co-stimulation (conjunction) should have
                        # lower probability than individual signals
                        max_individual = max(p1, p2)
                        
                        if conj_prob_from_bn < max_individual:
                            # Conjunction fallacy avoided - individual is more probable
                            answer_entity = conj[0] if p1 >= p2 else conj[1]
                            reasoning = f"Individual event ({answer_entity} with P={max_individual:.3f}) more probable than conjunction (P={conj_prob_from_bn:.3f}). Immunology: co-stimulation requires both antigens."
                        else:
                            # This would be a fallacy - conjunction shouldn't be more probable
                            answer_entity = conj_name
                            reasoning = f"Conjunction probability {conj_prob_from_bn:.3f}. Immunology: unusual binding affinity pattern."
                        
                        # Confidence based on agreement between different probability estimates
                        prob_estimates = [p1, p2, conj_prob_from_bn]
                        confidence = confidence_from_agreement(prob_estimates)
                        
                        return {
                            "answer": answer_entity,
                            "confidence": confidence,
                            "reasoning": f"{reasoning} Entropy={entropy_val:.3f}, Expected value={exp_val:.3f}"
                        }
            except Exception:
                # Fallback to T1 primitive-based reasoning
                pass
        
        # Fallback: Use T1 primitives directly
        # Find entity with highest probability
        best_entity = None
        best_prob = -1.0
        for entity, data in entities.items():
            probs = data.get("probabilities", [])
            if probs:
                avg_prob = sum(probs) / len(probs)
                # Use bayesian_update to refine probability
                refined = bayesian_update(avg_prob, 0.8, 0.1)  # Assume some evidence
                if refined > best_prob:
                    best_prob = refined
                    best_entity = entity
        
        if best_entity:
            # Compute entropy of all probabilities
            all_probs = []
            for data in entities.values():
                all_probs.extend(data.get("probabilities", []))
            if all_probs:
                entropy_val = entropy(all_probs)
            else:
                entropy_val = 0.0
            
            # Expected value
            outcomes = [(p, 1.0) for p in all_probs] + [(1-p, 0.0) for p in all_probs]
            exp_val = expected_value(outcomes) if outcomes else 0.0
            
            # Confidence from agreement
            confidence = confidence_from_agreement(all_probs) if all_probs else 0.5
            
            return {
                "answer": best_entity,
                "confidence": confidence,
                "reasoning": f"Highest probability {best_prob:.3f}. Entropy={entropy_val:.3f}, Expected value={exp_val:.3f}"
            }
        
        return {"answer": "Cannot determine", "confidence": 0.0, "reasoning": "No valid probabilities found"}

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored:
            return scored
        
        # Normalize scores to [0, 1] range
        scores = [item["raw_score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
            else:
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
        
        if max(ca, cb) == 0:
            return 1.0
        return (cab - min(ca, cb)) / max(ca, cb)