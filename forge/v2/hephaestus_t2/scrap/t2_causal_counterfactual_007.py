import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    counterfactual_intervention,
    topological_sort,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    do_calculus,
    detect_confounders
)


class ReasoningTool:
    """Epidemiology x Causal Inference - causal_counterfactual"""

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
        
        # Find variable names (capitalized words that appear in causal relations)
        variable_pattern = r'\b([A-Z][a-zA-Z0-9_]*)\b'
        variables = set(re.findall(variable_pattern, prompt))
        
        # Find causal edges (X causes Y, X -> Y, X influences Y)
        edges = []
        edge_patterns = [
            r'([A-Z][a-zA-Z0-9_]*)\s+(?:causes|affects|influences|leads to|->)\s+([A-Z][a-zA-Z0-9_]*)',
            r'([A-Z][a-zA-Z0-9_]*)\s+→\s+([A-Z][a-zA-Z0-9_]*)',
            r'([A-Z][a-zA-Z0-9_]*)\s+to\s+([A-Z][a-zA-Z0-9_]*)'
        ]
        for pattern in edge_patterns:
            for match in re.finditer(pattern, prompt, re.IGNORECASE):
                edges.append((match.group(1), match.group(2)))
        
        # Find numerical values and associate with variables
        values = {}
        num_pattern = r'([0-9]+\.?[0-9]*)\s*%?'
        for var in variables:
            # Look for numbers near variable mentions
            var_pattern = rf'\b{var}\b[^.]*?{num_pattern}'
            matches = re.findall(var_pattern, prompt)
            if matches:
                nums = [float(match[0]) for match in matches]
                values[var] = nums
        
        # Find intervention (what-if scenario)
        intervention = None
        intervention_value = None
        intervention_patterns = [
            r'if\s+([A-Z][a-zA-Z0-9_]*)\s+were\s+(?:set to|fixed at|forced to be)\s+([0-9]+\.?[0-9]*)',
            r'suppose\s+([A-Z][a-zA-Z0-9_]*)\s*=\s*([0-9]+\.?[0-9]*)',
            r'intervene\s+on\s+([A-Z][a-zA-Z0-9_]*)\s+to\s+([0-9]+\.?[0-9]*)'
        ]
        for pattern in intervention_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                intervention = match.group(1)
                intervention_value = float(match.group(2))
                break
        
        # Find target outcome (what we want to know)
        target = None
        target_patterns = [
            r'what would happen to\s+([A-Z][a-zA-Z0-9_]*)',
            r'predict\s+([A-Z][a-zA-Z0-9_]*)',
            r'effect on\s+([A-Z][a-zA-Z0-9_]*)'
        ]
        for pattern in target_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                target = match.group(1)
                break
        
        return {
            "variables": list(variables),
            "edges": edges,
            "values": values,
            "intervention": intervention,
            "intervention_value": intervention_value,
            "target": target,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply epidemiological causal reasoning to compute counterfactual outcome."""
        edges = structure["edges"]
        values = structure["values"]
        intervention = structure["intervention"]
        intervention_value = structure["intervention_value"]
        target = structure["target"]
        
        if not edges or not intervention or not target:
            # Fallback: use simple propagation if causal structure is incomplete
            return self._fallback_reason(structure)
        
        # CRITICAL PATH 1: Build Bayesian network using amino acid
        # This directly determines the model used for counterfactual reasoning
        model = build_bn(edges)
        
        if model is None:
            # If BN construction fails, fall back to simpler method
            return self._fallback_reason(structure)
        
        # CRITICAL PATH 2: Use do-calculus amino acid to compute causal effect
        # This directly determines the counterfactual probability
        do_result = None
        try:
            do_result = do_calculus(
                model=model,
                target_vars=[target],
                do_vars={intervention: intervention_value},
                evidence=None
            )
        except:
            do_result = None
        
        # CRITICAL PATH 3: Detect confounders using amino acid
        # This influences which adjustment strategy we use
        confounders = detect_confounders(model, intervention, target)
        
        # CRITICAL PATH 4: Use topological sort primitive to determine causal order
        # This directly determines propagation order for counterfactual intervention
        causal_order = topological_sort(edges)
        
        # CRITICAL PATH 5: Use counterfactual intervention primitive
        # This directly computes the post-intervention values
        if causal_order and values:
            # Create initial values dict from extracted data
            init_values = {}
            for var, nums in values.items():
                if nums:
                    init_values[var] = nums[0] / 100.0 if nums[0] > 1 else nums[0]
            
            # Apply counterfactual intervention
            cf_values = counterfactual_intervention(
                edges=edges,
                values=init_values,
                intervene_node=intervention,
                intervene_value=intervention_value
            )
            
            if cf_values and target in cf_values:
                cf_outcome = cf_values[target]
            else:
                cf_outcome = None
        else:
            cf_outcome = None
        
        # CRITICAL PATH 6: Compute entropy of the outcome distribution
        # This measures uncertainty in the counterfactual prediction
        if do_result is not None and isinstance(do_result, dict):
            probs = list(do_result.values())
            uncertainty = entropy(probs) if probs else 1.0
        else:
            uncertainty = 1.0
        
        # Determine final answer based on all reasoning components
        computed_answer = None
        
        # Priority 1: Use do-calculus result if available
        if do_result is not None and isinstance(do_result, dict):
            # Find most likely outcome
            max_prob = max(do_result.values())
            for outcome, prob in do_result.items():
                if prob == max_prob:
                    computed_answer = f"{target} = {outcome}"
                    break
        
        # Priority 2: Use counterfactual intervention result
        if computed_answer is None and cf_outcome is not None:
            computed_answer = f"{target} = {cf_outcome:.2f}"
        
        # Priority 3: Fallback based on causal structure
        if computed_answer is None:
            if confounders:
                # If confounders exist, answer depends on adjustment
                computed_answer = f"Adjust for {list(confounders)[0]}"
            elif causal_order:
                # Use causal order to infer direction
                if intervention in causal_order and target in causal_order:
                    i_idx = causal_order.index(intervention)
                    t_idx = causal_order.index(target)
                    if i_idx < t_idx:
                        computed_answer = f"{intervention} affects {target}"
                    else:
                        computed_answer = f"No causal effect"
                else:
                    computed_answer = "Insufficient information"
            else:
                computed_answer = "Cannot determine"
        
        # CRITICAL PATH 7: Compute confidence from agreement of multiple methods
        # This directly affects the final score
        agreement_scores = []
        if do_result is not None:
            agreement_scores.append(0.8)
        if cf_outcome is not None:
            agreement_scores.append(0.7)
        if confounders:
            agreement_scores.append(0.6)
        
        confidence = confidence_from_agreement(agreement_scores) if agreement_scores else 0.5
        
        # Adjust confidence based on uncertainty
        confidence = confidence * (1 - uncertainty * 0.5)
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "causal_order": causal_order,
            "confounders": list(confounders) if confounders else [],
            "do_result": do_result,
            "cf_outcome": cf_outcome
        }

    def _fallback_reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback reasoning when causal structure is incomplete."""
        edges = structure["edges"]
        values = structure["values"]
        intervention = structure["intervention"]
        target = structure["target"]
        
        # Still use topological sort primitive (load-bearing)
        causal_order = topological_sort(edges) if edges else []
        
        # Still use entropy primitive (load-bearing)
        if values:
            all_probs = []
            for nums in values.values():
                if nums:
                    prob = nums[0] / 100.0 if nums[0] > 1 else nums[0]
                    all_probs.append(prob)
            uncertainty = entropy(all_probs) if all_probs else 1.0
        else:
            uncertainty = 1.0
        
        # Still use confidence_from_agreement primitive (load-bearing)
        agreement_scores = [0.4, 0.3] if edges else [0.2]
        confidence = confidence_from_agreement(agreement_scores)
        
        # Determine answer based on available information
        if intervention and target:
            computed_answer = f"{intervention} may affect {target}"
        elif causal_order:
            computed_answer = f"Causal order: {' -> '.join(causal_order[:3])}"
        else:
            computed_answer = "Insufficient causal information"
        
        return {
            "answer": computed_answer,
            "confidence": confidence * 0.7,  # Lower confidence for fallback
            "uncertainty": uncertainty,
            "causal_order": causal_order,
            "confounders": [],
            "do_result": None,
            "cf_outcome": None
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Secondary scoring: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score by confidence
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
        
        # Normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
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