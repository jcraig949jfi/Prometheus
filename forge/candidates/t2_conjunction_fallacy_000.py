import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, expected_value
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, compare_conditional_marginal


class ReasoningTool:
    """Ecology x Bayesian networks - Conjunction fallacy"""

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
        """Extract entities, probabilities, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find all percentage values
        percentages = []
        for line in lines:
            matches = re.findall(r'([0-9]+\.?[0-9]*)%', line)
            percentages.extend([float(m)/100 for m in matches])
        
        # Find entity names (capitalized phrases that appear before percentages)
        entities = {}
        for line in lines:
            # Look for patterns like "Entity has X% probability"
            name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
            if name_match:
                name = name_match.group(1)
                if name not in entities and name not in ["What", "Which", "How", "Why"]:
                    # Find associated percentages in the same line
                    local_pcts = re.findall(r'([0-9]+\.?[0-9]*)%', line)
                    if local_pcts:
                        entities[name] = {"probabilities": [float(p)/100 for p in local_pcts]}
                    else:
                        entities[name] = {"probabilities": []}
        
        # If no entities found by capitalization, look for generic descriptions
        if not entities:
            # Look for patterns like "probability of X is Y%"
            prob_pattern = r'probability of ([^,.]+) is ([0-9]+\.?[0-9]*)%'
            for line in lines:
                matches = re.findall(prob_pattern, line.lower())
                for entity_desc, pct in matches:
                    entity_desc = entity_desc.strip()
                    if entity_desc and entity_desc not in entities:
                        entities[entity_desc] = {"probabilities": [float(pct)/100]}
        
        return {
            "entities": entities,
            "percentages": percentages,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ecological niche competition reasoning to conjunction fallacy."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        question = structure["question"]
        
        # ECOLOGICAL FRAMEWORK: Treat probabilities as resource availability
        # Joint probability = niche overlap, marginal = total resource
        # Conjunction fallacy occurs when niche overlap is overestimated
        
        # Phase 1: Build ecological competition model using Bayesian network
        # Nodes: Base event (A), Additional event (B), Joint (A∩B)
        # Ecological interpretation: A and B compete for probability resources
        
        computed_answer = ""
        confidence = 0.5
        reasoning = ""
        
        # Extract base probabilities from prompt data
        if len(percentages) >= 2:
            # Use extracted percentages for ecological modeling
            # Sort to get highest probabilities (most abundant resources)
            sorted_pcts = sorted(percentages, reverse=True)
            
            # ECOLOGICAL PRINCIPLE 1: Resource partitioning
            # Higher entropy in probability distribution indicates more competition
            entropy_val = entropy(sorted_pcts[:3] if len(sorted_pcts) >= 3 else sorted_pcts)
            
            # ECOLOGICAL PRINCIPLE 2: Niche overlap calculation
            # Build Bayesian network to model joint vs marginal probabilities
            edges = [("A", "Joint"), ("B", "Joint")]
            
            # Use extracted percentages for CPDs
            if len(sorted_pcts) >= 2:
                p_A = sorted_pcts[0]  # Most abundant resource (base event)
                p_B = sorted_pcts[1]  # Second most abundant (additional event)
                
                # Assume independence for ecological niche separation
                p_joint_independent = p_A * p_B
                
                # Build Bayesian network with ecological interpretation
                cpd_specs = {
                    "A": [[1 - p_A], [p_A]],
                    "B": [[1 - p_B], [p_B]],
                    "Joint": [
                        [1, 1, 1, 0],  # P(Joint=0|A,B)
                        [0, 0, 0, 1]   # P(Joint=1|A,B) = 1 only if both A=1 and B=1
                    ]
                }
                
                try:
                    model = build_bn(edges, cpd_specs)
                    
                    # Query joint probability P(Joint=1)
                    joint_query = conditional_query(model, ["Joint"], {})
                    if joint_query is not None and "Joint" in joint_query:
                        p_joint_bn = joint_query["Joint"].get(1, 0.0)
                        
                        # Compare with marginal P(A=1) using ecological competition
                        marginal_query = conditional_query(model, ["A"], {})
                        p_marginal = marginal_query["A"].get(1, 0.0) if marginal_query else p_A
                        
                        # ECOLOGICAL PRINCIPLE 3: Competitive exclusion
                        # Joint probability cannot exceed marginal (Gause's law)
                        if p_joint_bn > p_marginal:
                            # Conjunction fallacy detected - niche overlap overestimated
                            computed_answer = "joint" if "joint" in question.lower() else "marginal"
                            reasoning = f"Ecological competition: joint probability ({p_joint_bn:.3f}) exceeds marginal ({p_marginal:.3f}) violating Gause's law"
                        else:
                            # Ecologically valid: joint ≤ marginal
                            computed_answer = "marginal" if "marginal" in question.lower() else "joint"
                            reasoning = f"Ecologically consistent: joint ({p_joint_bn:.3f}) ≤ marginal ({p_marginal:.3f})"
                        
                        # Use Bayesian update to refine confidence based on ecological consistency
                        prior = 0.7
                        likelihood = 1.0 if p_joint_bn <= p_marginal else 0.3
                        confidence = bayesian_update(prior, likelihood)
                        
                except Exception:
                    # Fallback to ecological resource calculation
                    pass
        
        # If Bayesian network failed, use ecological resource competition directly
        if not computed_answer:
            # Use expected value of ecological resources
            if len(sorted_pcts) >= 2:
                p_A = sorted_pcts[0]
                p_B = sorted_pcts[1]
                
                # Ecological resource outcomes: (probability, resource value)
                outcomes = [
                    (p_A * p_B, 1.0),      # Both niches occupied
                    (p_A * (1-p_B), 0.5),   # Only base niche
                    ((1-p_A) * p_B, 0.5),   # Only additional niche
                    ((1-p_A)*(1-p_B), 0.0)  # No niche
                ]
                
                ev = expected_value(outcomes)
                
                # Compare with marginal resource (base niche alone)
                marginal_resource = p_A
                
                # Ecological decision: which has higher expected resource value?
                if ev > marginal_resource:
                    computed_answer = "joint"
                    reasoning = f"Joint ecological resource ({ev:.3f}) > marginal ({marginal_resource:.3f})"
                else:
                    computed_answer = "marginal"
                    reasoning = f"Marginal ecological resource ({marginal_resource:.3f}) ≥ joint ({ev:.3f})"
                
                # Calculate confidence from agreement between ecological metrics
                metrics = [ev, marginal_resource, p_A * p_B]
                confidence = confidence_from_agreement(metrics)
        
        # Final fallback: use entity names from prompt
        if not computed_answer and entities:
            # Find entity with highest probability (ecological dominance)
            dominant_entity = max(entities.items(), 
                                key=lambda x: max(x[1]["probabilities"]) if x[1]["probabilities"] else 0)
            computed_answer = dominant_entity[0]
            reasoning = f"Ecologically dominant entity: {computed_answer}"
            confidence = 0.6
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: direct match with computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Secondary: NCD similarity with reasoning
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence from ecological reasoning
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
        if max(scores) > min(scores):
            for item in scored:
                item["score"] = (item["score"] - min(scores)) / (max(scores) - min(scores))
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
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0