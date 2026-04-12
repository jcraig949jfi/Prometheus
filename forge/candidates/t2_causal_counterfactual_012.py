import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    counterfactual_intervention,
    topological_sort,
    solve_constraints
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    do_calculus,
    detect_confounders
)


class ReasoningTool:
    """Relativity x Bayesian Networks - Causal Counterfactual"""

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
        """Extract causal structure, variables, and intervention details from prompt."""
        structure = {
            "entities": {},
            "variables": {},
            "edges": [],
            "interventions": [],
            "target": None,
            "question": "",
            "raw": prompt
        }
        
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        if lines:
            structure["question"] = lines[-1]
        
        # Extract entity names (capitalized multi-word phrases)
        entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities = re.findall(entity_pattern, prompt)
        for entity in entities:
            if entity not in structure["entities"] and len(entity.split()) <= 3:
                structure["entities"][entity] = {"mentions": 0, "values": []}
        
        # Extract causal relationships (X causes Y, X -> Y, X affects Y)
        causal_patterns = [
            r'(\w+)\s+(?:causes|affects|influences|leads to)\s+(\w+)',
            r'(\w+)\s*->\s*(\w+)',
            r'(\w+)\s+affects\s+(\w+)'
        ]
        
        for pattern in causal_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for src, dst in matches:
                if src and dst:
                    edge = (src.strip(), dst.strip())
                    if edge not in structure["edges"]:
                        structure["edges"].append(edge)
        
        # Extract numerical values and associate with variables
        value_pattern = r'(\d+(?:\.\d+)?)%?'
        value_matches = re.findall(value_pattern, prompt)
        for i, val in enumerate(value_matches):
            var_name = f"V{i+1}"
            structure["variables"][var_name] = float(val) / 100.0 if '%' in prompt else float(val)
        
        # Extract intervention language (if X were set to, suppose X was, counterfactually)
        intervention_keywords = ['if', 'were set to', 'suppose', 'counterfactually', 'intervene']
        sentences = prompt.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in intervention_keywords):
                # Look for variable-value pairs in intervention context
                val_match = re.search(r'(\d+(?:\.\d+)?)%?', sentence)
                var_match = re.search(r'\b([A-Za-z]+)\b', sentence)
                if val_match and var_match:
                    value = float(val_match.group(1)) / 100.0 if '%' in sentence else float(val_match.group(1))
                    variable = var_match.group(1)
                    structure["interventions"].append({
                        "variable": variable,
                        "value": value,
                        "context": sentence.strip()
                    })
        
        # Extract target variable (what we want to know about)
        target_keywords = ['what would', 'what is', 'calculate', 'determine', 'find']
        for sentence in sentences:
            for keyword in target_keywords:
                if keyword in sentence.lower():
                    # Find the variable mentioned after the keyword
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if word.lower() in ['be', 'happen', 'value', 'of'] and i+1 < len(words):
                            potential_target = words[i+1].strip('.,?!')
                            if potential_target in structure["variables"] or potential_target in [e for e in structure["entities"]]:
                                structure["target"] = potential_target
                                break
        
        return structure

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativistic framework: different reference frames (interventions)
        yield different observed outcomes. Use Bayesian networks for causal structure."""
        
        entities = structure["entities"]
        edges = structure["edges"]
        variables = structure["variables"]
        interventions = structure["interventions"]
        target = structure["target"]
        
        # If no explicit edges but we have variables, create a simple chain
        if not edges and len(variables) >= 2:
            var_names = list(variables.keys())
            for i in range(len(var_names)-1):
                edges.append((var_names[i], var_names[i+1]))
        
        # Build Bayesian network from extracted edges
        bn_model = None
        if edges:
            try:
                # Create CPDs based on extracted variable values
                cpd_specs = {}
                for node in set([src for src, _ in edges] + [dst for _, dst in edges]):
                    if node in variables:
                        # Use extracted value as probability
                        val = variables[node]
                        cpd_specs[node] = {
                            "values": [[val, 1-val]],  # P(node=1), P(node=0)
                            "states": [1, 0]
                        }
                
                bn_model = build_bn(edges, cpd_specs)
            except Exception:
                bn_model = None
        
        # LOAD-BEARING AMINO ACID 1: detect_confounders
        confounders = None
        if bn_model and len(edges) >= 2:
            try:
                # Pick two variables to check for confounders
                nodes = list(set([src for src, _ in edges] + [dst for _, dst in edges]))
                if len(nodes) >= 2:
                    confounders = detect_confounders(bn_model, nodes[0], nodes[1])
            except Exception:
                confounders = None
        
        # LOAD-BEARING PRIMITIVE 1: topological_sort on causal edges
        causal_order = None
        if edges:
            causal_order = topological_sort(edges)
        
        # LOAD-BEARING PRIMITIVE 2: entropy of variable values
        entropy_val = 0.0
        if variables:
            probs = list(variables.values())
            # Normalize to probability distribution
            total = sum(probs)
            if total > 0:
                norm_probs = [p/total for p in probs]
                entropy_val = entropy(norm_probs)
        
        # Determine answer based on interventions
        computed_answer = None
        confidence = 0.5
        reasoning = ""
        
        if interventions and target:
            # Apply relativistic reasoning: each intervention is a different reference frame
            frame_results = []
            
            for intervention in interventions:
                intervene_var = intervention["variable"]
                intervene_val = intervention["value"]
                
                # LOAD-BEARING PRIMITIVE 3: counterfactual_intervention
                cf_result = None
                if edges and variables:
                    # Convert variables dict to values for intervention
                    node_values = variables.copy()
                    cf_result = counterfactual_intervention(
                        edges, 
                        node_values, 
                        intervene_var, 
                        intervene_val
                    )
                
                if cf_result and target in cf_result:
                    frame_results.append({
                        "frame": intervene_var,
                        "value": cf_result[target],
                        "intervention": intervene_val
                    })
            
            if frame_results:
                # LOAD-BEARING AMINO ACID 2: conditional_query if BN exists
                conditional_prob = None
                if bn_model and target:
                    try:
                        # Query probability of target=1 given some evidence
                        evidence = {}
                        if interventions:
                            # Use first intervention as evidence
                            first_int = interventions[0]
                            if first_int["variable"] in [n for n in bn_model.nodes()]:
                                evidence = {first_int["variable"]: 1 if first_int["value"] > 0.5 else 0}
                        
                        conditional_prob = conditional_query(bn_model, [target], evidence)
                    except Exception:
                        conditional_prob = None
                
                # Determine answer based on relativistic frame comparison
                if len(frame_results) > 1:
                    # Different frames give different results - relativity in action
                    values = [r["value"] for r in frame_results]
                    avg_value = sum(values) / len(values)
                    
                    # Use entropy to measure uncertainty across frames
                    if entropy_val > 0.5:  # High entropy = high uncertainty
                        # Fall back to constraint solving
                        if variables:
                            # LOAD-BEARING PRIMITIVE 4: solve_constraints
                            constraints = []
                            domains = {var: [0, 1] for var in variables.keys()}
                            
                            # Add causal constraints
                            for src, dst in edges:
                                if src in variables and dst in variables:
                                    constraints.append(
                                        ([src, dst], lambda x, y: x <= y)  # Simple monotonic constraint
                                    )
                            
                            solution = solve_constraints(
                                list(variables.keys()),
                                domains,
                                constraints
                            )
                            
                            if solution and target in solution:
                                computed_answer = str(solution[target])
                                reasoning = f"Constraint solution across {len(frame_results)} frames"
                                confidence = 0.7
                            else:
                                # Use average of frame results
                                computed_answer = str(round(avg_value, 3))
                                reasoning = f"Relativistic average across {len(frame_results)} intervention frames"
                                confidence = 0.6
                        else:
                            computed_answer = str(round(avg_value, 3))
                            reasoning = f"Relativistic average across {len(frame_results)} intervention frames"
                            confidence = 0.6
                    else:
                        # Low entropy, more certain answer
                        best_frame = max(frame_results, key=lambda x: x["value"])
                        computed_answer = str(round(best_frame["value"], 3))
                        reasoning = f"Frame {best_frame['frame']}={best_frame['intervention']} yields maximal effect"
                        confidence = 0.8
                        
                        # Adjust confidence based on conditional query if available
                        if conditional_prob is not None:
                            try:
                                conf_adjust = float(conditional_prob.get(target, 0.5))
                                confidence = (confidence + conf_adjust) / 2
                            except:
                                pass
                else:
                    # Single intervention frame
                    computed_answer = str(round(frame_results[0]["value"], 3))
                    reasoning = f"Single intervention frame: {frame_results[0]['frame']}"
                    confidence = 0.7
        
        # Fallback if no interventions
        if not computed_answer and target:
            if target in variables:
                computed_answer = str(variables[target])
                reasoning = "Baseline value without intervention"
                confidence = 0.5
            elif entities:
                # Pick entity with most mentions
                for entity in entities:
                    entities[entity]["mentions"] = structure["raw"].count(entity)
                best_entity = max(entities.items(), key=lambda x: x[1]["mentions"])
                computed_answer = best_entity[0]
                reasoning = "Most frequently mentioned entity"
                confidence = 0.4
        
        # LOAD-BEARING PRIMITIVE 5: confidence_from_agreement
        if computed_answer and isinstance(computed_answer, str):
            try:
                # Create multiple scoring perspectives
                scores = []
                if entropy_val > 0:
                    scores.append(1.0 - min(entropy_val, 1.0))
                if causal_order:
                    scores.append(len(causal_order) / max(len(causal_order), 10))
                if confounders:
                    scores.append(0.8 if len(confounders) > 0 else 0.5)
                
                if scores:
                    agreement_confidence = confidence_from_agreement(scores)
                    confidence = (confidence + agreement_confidence) / 2
            except:
                pass
        
        # Final fallback
        if not computed_answer:
            computed_answer = "Unknown"
            reasoning = "Insufficient data for counterfactual reasoning"
            confidence = 0.1
        
        return {
            "answer": str(computed_answer),
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": reasoning,
            "metadata": {
                "entropy": entropy_val,
                "causal_order": causal_order,
                "confounders": list(confounders) if confounders else [],
                "frames": len(interventions)
            }
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            if computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Use NCD as fallback
                ncd_val = self._ncd(computed_answer, candidate)
                score = (1.0 - ncd_val) * confidence
            
            # Boost score if candidate contains reasoning keywords
            reasoning_text = reasoning_result["reasoning"]
            if any(keyword in candidate.lower() for keyword in ["frame", "intervention", "counterfactual", "relativ"]):
                score = min(score * 1.2, 1.0)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["raw_score"] for item in scored]
        
        # Simple min-max normalization
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)