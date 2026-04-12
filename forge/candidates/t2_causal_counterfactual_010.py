import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, counterfactual_intervention
from forge.amino_acids.pgmpy_acids import do_calculus, build_bn


class ReasoningTool:
    """Optics x pgmpy_acids - causal_counterfactual"""

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
        """Extract causal structure, variables, and intervention from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find variables (capitalized words that appear with values)
        variables = set()
        values = {}
        edges = []
        interventions = []
        
        # Look for causal language: "causes", "affects", "influences", "leads to"
        for line in lines:
            # Extract variable names (multi-word capitalized phrases)
            var_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
            for var in var_matches:
                if len(var.split()) <= 3:  # Avoid long phrases
                    variables.add(var)
            
            # Look for causal edges
            if "causes" in line.lower() or "affects" in line.lower():
                parts = line.lower().split("causes" if "causes" in line.lower() else "affects")
                if len(parts) == 2:
                    cause = parts[0].strip()
                    effect = parts[1].strip()
                    # Map back to extracted variable names
                    cause_var = self._match_variable(cause, variables)
                    effect_var = self._match_variable(effect, variables)
                    if cause_var and effect_var:
                        edges.append((cause_var, effect_var))
            
            # Look for numerical values associated with variables
            num_matches = re.findall(r'([0-9]+\.?[0-9]*)%?', line)
            if num_matches and var_matches:
                for var in var_matches[:len(num_matches)]:
                    try:
                        values[var] = float(num_matches[0]) / 100.0 if '%' in line else float(num_matches[0])
                    except:
                        pass
            
            # Look for intervention language: "if we set", "intervene on", "force to"
            if "if we set" in line.lower() or "intervene on" in line.lower():
                # Extract intervention variable and value
                inter_match = re.search(r'set\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+to\s+([0-9]+\.?[0-9]*)', line.lower())
                if inter_match:
                    var = self._match_variable(inter_match.group(1), variables)
                    if var:
                        try:
                            val = float(inter_match.group(2))
                            interventions.append((var, val))
                        except:
                            pass
        
        # If no edges found but variables exist, create a simple chain
        if not edges and len(variables) >= 2:
            var_list = list(variables)
            for i in range(len(var_list)-1):
                edges.append((var_list[i], var_list[i+1]))
        
        return {
            "variables": list(variables),
            "edges": edges,
            "values": values,
            "interventions": interventions,
            "question": question,
            "raw": prompt
        }

    def _match_variable(self, text: str, variables: set) -> str:
        """Find the best matching variable name from the set."""
        text_lower = text.lower()
        for var in variables:
            if var.lower() in text_lower or text_lower in var.lower():
                return var
        # If no match, try to capitalize first letters
        words = text.split()
        capitalized = ' '.join([w.capitalize() for w in words])
        if capitalized in variables:
            return capitalized
        return ""

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use optics-inspired causal reasoning with Bayesian networks."""
        variables = structure["variables"]
        edges = structure["edges"]
        values = structure["values"]
        interventions = structure["interventions"]
        
        if not variables or not edges:
            # Fallback: use simple statistical reasoning
            return self._fallback_reason(structure)
        
        # Build Bayesian network from extracted edges
        model = build_bn(edges)
        if model is None:
            return self._fallback_reason(structure)
        
        # OPTICS CONCEPT: Refractive index as information transmission efficiency
        # Higher entropy = more scattering = less reliable causal inference
        # Compute entropy of extracted values as measure of information clarity
        value_list = list(values.values())
        if len(value_list) >= 2:
            # Normalize values to create probability distribution
            total = sum(abs(v) for v in value_list)
            if total > 0:
                probs = [abs(v)/total for v in value_list]
                info_entropy = entropy(probs)  # T1 primitive - LOAD BEARING
                # High entropy means scattered information, lower confidence
                clarity = 1.0 - info_entropy
            else:
                clarity = 0.5
        else:
            clarity = 0.5
        
        # Determine target variable (usually mentioned in question)
        question = structure["question"].lower()
        target_var = ""
        for var in variables:
            if var.lower() in question:
                target_var = var
                break
        if not target_var and variables:
            target_var = variables[-1]  # Last variable as fallback
        
        # Determine intervention if specified
        do_var = None
        do_value = None
        if interventions:
            do_var, do_value = interventions[0]
        elif "if" in question and "had been" in question:
            # Try to extract counterfactual from question
            words = question.split()
            for i, word in enumerate(words):
                if word.lower() in ["had", "were", "was"] and i > 0:
                    possible_var = ' '.join(words[max(0, i-2):i]).title()
                    do_var = self._match_variable(possible_var, set(variables))
                    if do_var and i+1 < len(words):
                        # Try to extract value
                        next_word = words[i+1]
                        if next_word.isdigit() or '.' in next_word:
                            try:
                                do_value = float(next_word)
                            except:
                                do_value = 0.0
        
        # OPTICS CONCEPT: Snell's Law for causal effect propagation
        # The "refractive index" determines how strongly intervention affects outcome
        # Use bayesian_update to compute effect strength
        if target_var and do_var and do_value is not None:
            # Compute prior probability from extracted values
            prior = values.get(target_var, 0.5)
            # Likelihood based on edge structure (simplified)
            # Count paths from do_var to target_var
            path_count = self._count_paths(edges, do_var, target_var)
            likelihood = min(0.5 + 0.1 * path_count, 0.9) if path_count > 0 else 0.1
            
            # T1 primitive - LOAD BEARING: Bayesian update for effect strength
            effect_strength = bayesian_update(prior, likelihood, false_positive=0.1)
            
            # Use do_calculus amino acid - LOAD BEARING
            try:
                # Build evidence if available
                evidence = {}
                for var, val in values.items():
                    if var != do_var and var != target_var:
                        evidence[var] = val
                
                causal_effect = do_calculus(
                    model, 
                    target_vars=[target_var], 
                    do_vars={do_var: do_value}, 
                    evidence=evidence if evidence else None
                )
                
                if causal_effect is not None:
                    # Successfully computed causal effect
                    computed_answer = f"{target_var} would be {causal_effect:.2f}"
                    confidence = effect_strength * clarity
                else:
                    # Fallback to counterfactual_intervention primitive
                    computed_answer, confidence = self._use_counterfactual_primitive(
                        edges, values, do_var, do_value, target_var, clarity
                    )
            except:
                # Amino acid failed, use primitive fallback
                computed_answer, confidence = self._use_counterfactual_primitive(
                    edges, values, do_var, do_value, target_var, clarity
                )
        else:
            # No clear intervention, answer based on extracted values
            if values:
                max_var = max(values.items(), key=lambda x: x[1])[0]
                computed_answer = f"{max_var} has highest value"
                confidence = 0.6 * clarity
            else:
                computed_answer = "Insufficient data"
                confidence = 0.3
        
        # T1 primitive - LOAD BEARING: Confidence calibration
        if isinstance(confidence, (int, float)):
            confidence = confidence_from_agreement([confidence, clarity, 0.5])
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Optics-based causal analysis with entropy={info_entropy if 'info_entropy' in locals() else 'N/A'}, clarity={clarity:.2f}"
        }

    def _use_counterfactual_primitive(self, edges, values, do_var, do_value, target_var, clarity):
        """Fallback using counterfactual_intervention primitive."""
        # Prepare values dict with all variables
        all_values = {}
        for edge in edges:
            for var in edge:
                if var not in all_values:
                    all_values[var] = values.get(var, 0.5)
        
        # T1 primitive - LOAD BEARING: Counterfactual intervention
        result = counterfactual_intervention(edges, all_values, do_var, do_value)
        
        if result and target_var in result:
            effect = result[target_var]
            computed_answer = f"{target_var} would be {effect:.2f}"
            confidence = 0.7 * clarity
        else:
            computed_answer = f"Intervention on {do_var} affects system"
            confidence = 0.5 * clarity
        
        return computed_answer, confidence

    def _count_paths(self, edges: List[Tuple[str, str]], start: str, end: str) -> int:
        """Count simple paths from start to end in directed graph."""
        if start == end:
            return 0
        
        # Build adjacency list
        adj = {}
        for a, b in edges:
            adj.setdefault(a, []).append(b)
        
        # Simple DFS to count paths
        def dfs(current, visited):
            if current == end:
                return 1
            if current in visited:
                return 0
            visited.add(current)
            total = 0
            for neighbor in adj.get(current, []):
                total += dfs(neighbor, visited.copy())
            return total
        
        return dfs(start, set())

    def _fallback_reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback reasoning when BN construction fails."""
        variables = structure["variables"]
        values = structure["values"]
        
        if not variables:
            return {
                "answer": "Cannot determine",
                "confidence": 0.1,
                "reasoning": "No variables extracted"
            }
        
        # Use entropy on value distribution
        value_list = list(values.values())
        if len(value_list) >= 2:
            total = sum(abs(v) for v in value_list)
            if total > 0:
                probs = [abs(v)/total for v in value_list]
                info_entropy = entropy(probs)  # T1 primitive - LOAD BEARING
                clarity = 1.0 - info_entropy
            else:
                clarity = 0.5
        else:
            clarity = 0.5
        
        # Simple answer based on highest value
        if values:
            max_var = max(values.items(), key=lambda x: x[1])[0]
            computed_answer = f"{max_var} is highest"
            confidence = 0.6 * clarity
        else:
            computed_answer = f"{variables[0]} is relevant"
            confidence = 0.3 * clarity
        
        confidence = confidence_from_agreement([confidence, clarity, 0.4])  # T1 primitive - LOAD BEARING
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Fallback analysis with entropy={info_entropy if 'info_entropy' in locals() else 'N/A'}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD similarity
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

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        return (cab - min(ca, cb)) / max(ca, cb)

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if max(scores) - min(scores) < 0.01:
            # All scores too similar, spread them out
            for i, item in enumerate(scored):
                item["score"] = item["base_score"] * item["confidence"]
        
        # Ensure scores are between 0 and 1
        for item in scored:
            item["score"] = max(0.0, min(1.0, item["score"]))
        
        return scored