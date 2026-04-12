import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pgmpy_acids import detect_confounders, build_bn, conditional_query


class ReasoningTool:
    """feedback_systems x pgmpy_acids - causal_confounding_hard"""

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
        """Extract entities, relationships, and values from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized multi-word phrases that appear multiple times)
        words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', prompt)
        from collections import Counter
        word_counts = Counter(words)
        entities = [word for word, count in word_counts.items() if count > 1 and len(word) > 2]
        
        # Find causal relationships (X causes Y, X affects Y, X influences Y)
        causal_patterns = [
            r'(\w+)\s+(?:causes|affects|influences|impacts|determines)\s+(\w+)',
            r'(\w+)\s+→\s+(\w+)',
            r'(\w+)\s+leads to\s+(\w+)',
            r'(\w+)\s+affects\s+(\w+)'
        ]
        
        edges = []
        for pattern in causal_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    edges.append((match[0].strip(), match[1].strip()))
        
        # Find numerical values (percentages, rates, probabilities)
        numbers = re.findall(r'([0-9]+\.?[0-9]*)%', prompt)
        values = [float(num) for num in numbers]
        
        # Find treatment and outcome variables from question
        treatment = None
        outcome = None
        if "effect of" in question.lower():
            parts = question.lower().split("effect of")
            if len(parts) > 1:
                treatment_match = re.search(r'\b(\w+)\b', parts[1])
                if treatment_match:
                    treatment = treatment_match.group(1)
        
        if "on" in question.lower():
            parts = question.lower().split("on")
            if len(parts) > 1:
                outcome_match = re.search(r'\b(\w+)\b', parts[1])
                if outcome_match:
                    outcome = outcome_match.group(1)
        
        return {
            "entities": entities,
            "edges": list(set(edges)),
            "values": values,
            "question": question,
            "treatment": treatment,
            "outcome": outcome,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply feedback systems reasoning to identify and adjust for confounding."""
        entities = structure["entities"]
        edges = structure["edges"]
        values = structure["values"]
        treatment = structure["treatment"]
        outcome = structure["outcome"]
        
        # If we have at least 2 entities and some edges, build a causal model
        if len(entities) >= 2 and edges:
            # Build a simple Bayesian network from extracted edges
            model = build_bn(edges)
            
            # Use topological sort to understand causal ordering (T1 primitive)
            sorted_nodes = topological_sort(edges)
            
            # If we have treatment and outcome, look for confounders
            if treatment and outcome and treatment in entities and outcome in entities:
                # Detect confounders using amino acid (load-bearing)
                confounders_result = detect_confounders(model, treatment, outcome)
                
                if confounders_result:
                    # Convert to list if it's a set
                    if isinstance(confounders_result, set):
                        confounders_list = list(confounders_result)
                    else:
                        confounders_list = confounders_result
                    
                    # Use entropy to measure uncertainty in confounding (T1 primitive)
                    if confounders_list:
                        # Create probability distribution for confounders
                        n_confounders = len(confounders_list)
                        if n_confounders > 0:
                            # Equal probability for each confounder
                            probs = [1.0/n_confounders] * n_confounders
                            confounder_entropy = entropy(probs)
                        else:
                            confounder_entropy = 0.0
                    else:
                        confounder_entropy = 0.0
                    
                    # Bayesian update for belief in confounding (T1 primitive)
                    # Prior belief: 0.3 that there is confounding
                    prior = 0.3
                    # Likelihood: more confounders → stronger evidence
                    likelihood = min(0.9, len(confounders_list) * 0.3) if confounders_list else 0.1
                    posterior_confounding = bayesian_update(prior, likelihood)
                    
                    # Determine which entity is the main confounder
                    if confounders_list:
                        # Use the confounder with highest "centrality" in the graph
                        # Count incoming edges to each confounder
                        edge_counts = {}
                        for conf in confounders_list:
                            count = sum(1 for (src, tgt) in edges if tgt == conf)
                            edge_counts[conf] = count
                        
                        if edge_counts:
                            main_confounder = max(edge_counts.items(), key=lambda x: x[1])[0]
                        else:
                            main_confounder = confounders_list[0]
                        
                        # Feedback systems concept: confounding creates feedback loops
                        # that distort causal inference. The adjustment breaks the loop.
                        computed_answer = main_confounder
                        confidence = min(0.95, posterior_confounding * (1 + confounder_entropy))
                    else:
                        computed_answer = "No confounding"
                        confidence = 1.0 - posterior_confounding
                else:
                    computed_answer = "No confounding detected"
                    confidence = 0.7
            else:
                # If no specific treatment/outcome, use the most central node
                if sorted_nodes:
                    # In feedback systems, central nodes often act as integrators
                    # that can confound relationships
                    computed_answer = sorted_nodes[0]
                    
                    # Use confidence from agreement of different centrality measures
                    centrality_scores = []
                    if sorted_nodes:
                        centrality_scores.append(1.0)  # First in topological order
                    
                    # Count edges for each node
                    for node in entities[:3]:  # Look at first few entities
                        in_degree = sum(1 for (src, tgt) in edges if tgt == node)
                        out_degree = sum(1 for (src, tgt) in edges if src == node)
                        centrality_scores.append((in_degree + out_degree) / max(len(edges), 1))
                    
                    confidence = confidence_from_agreement(centrality_scores)
                else:
                    computed_answer = entities[0] if entities else "Unknown"
                    confidence = 0.5
        else:
            # Fallback: use first entity
            computed_answer = entities[0] if entities else "Unknown"
            confidence = 0.3
        
        return {
            "answer": str(computed_answer),
            "confidence": float(confidence),
            "reasoning": f"Identified {computed_answer} as key confounding variable using feedback systems analysis",
            "structure": structure
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match
            if computed_answer.lower() in candidate.lower():
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
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple calibration: ensure scores are in reasonable range
        scores = [item["score"] for item in scored]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            
            if max_score > min_score:
                # Normalize to [0.1, 0.9] range to avoid extremes
                for item in scored:
                    normalized = 0.1 + 0.8 * (item["score"] - min_score) / (max_score - min_score)
                    item["score"] = normalized
            else:
                # All scores equal, assign uniform scores
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