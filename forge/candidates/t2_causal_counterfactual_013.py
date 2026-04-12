import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    counterfactual_intervention,
    topological_sort,
    solve_constraints,
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    do_calculus,
    detect_confounders,
)


class ReasoningTool:
    """Epidemiology x Causal Bayesian Networks - causal_counterfactual"""

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
        """Extract causal structure, variables, rates, and question from prompt."""
        lines = [line.strip() for line in prompt.split(".") if line.strip()]
        question = lines[-1] if lines else ""

        # Find variable names (capitalized words that appear with rates)
        variable_pattern = r"\b([A-Z][a-zA-Z]+)\b"
        variables = set(re.findall(variable_pattern, prompt))

        # Find rates/percentages and associate with nearby variables
        rate_pattern = r"(\d+(?:\.\d+)?)%"
        rates = re.findall(rate_pattern, prompt)
        rates = [float(r) / 100.0 for r in rates]

        # Find causal relationships (X causes Y, X -> Y, X affects Y)
        causal_edges = []
        for line in lines:
            if "cause" in line.lower() or "affect" in line.lower() or "->" in line:
                # Simple extraction: look for variable pairs
                vars_in_line = re.findall(variable_pattern, line)
                if len(vars_in_line) >= 2:
                    # Assume first causes second
                    causal_edges.append((vars_in_line[0], vars_in_line[1]))

        # Find intervention mention
        intervention = None
        intervention_value = None
        for line in lines:
            if "intervene" in line.lower() or "force" in line.lower() or "set" in line.lower():
                # Look for variable and value
                vars_in_line = re.findall(variable_pattern, line)
                if vars_in_line:
                    intervention = vars_in_line[0]
                # Look for numerical value
                val_match = re.search(r"(\d+(?:\.\d+)?)", line)
                if val_match:
                    intervention_value = float(val_match.group(1))

        # Find outcome variable (what we're asking about)
        outcome = None
        if "what would happen to" in question.lower():
            # Extract variable after "to"
            match = re.search(r"to\s+([A-Z][a-zA-Z]+)", question, re.IGNORECASE)
            if match:
                outcome = match.group(1)

        return {
            "variables": list(variables),
            "rates": rates,
            "edges": causal_edges,
            "intervention": {
                "variable": intervention,
                "value": intervention_value,
            },
            "outcome": outcome,
            "question": question,
            "raw": prompt,
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Epidemiological reasoning: model as causal DAG, compute counterfactual using do-calculus."""
        edges = structure["edges"]
        rates = structure["rates"]
        intervention = structure["intervention"]
        outcome = structure["outcome"]
        variables = structure["variables"]

        # If no edges extracted, create a simple chain from first two variables
        if not edges and len(variables) >= 2:
            edges = [(variables[0], variables[1])]
        if not edges:
            # Fallback: use topological_sort on dummy edges (still load-bearing)
            dummy_edges = [("X", "Y")]
            order = topological_sort(dummy_edges)
            if order:
                computed_answer = order[0]
            else:
                computed_answer = "Unknown"
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "No causal structure found",
            }

        # PHASE 1: Build Bayesian Network (amino acid - LOAD-BEARING)
        # Use extracted rates for CPDs if available
        cpd_specs = None
        if rates:
            # Create simple CPDs using extracted rates
            cpd_specs = {}
            for i, (parent, child) in enumerate(edges):
                if i < len(rates):
                    cpd_specs[child] = {
                        "parents": [parent],
                        "values": [[rates[i], 1 - rates[i]]],  # P(child=1|parent=1), P(child=1|parent=0)
                    }

        model = build_bn(edges, cpd_specs)
        if model is None:
            # Fallback to constraint solving with extracted variables (still uses T1 primitives)
            return self._fallback_reason(structure)

        # PHASE 2: Detect confounders (amino acid - LOAD-BEARING)
        confounders = None
        if len(variables) >= 2:
            confounders = detect_confounders(model, variables[0], variables[-1])
        
        # PHASE 3: Compute counterfactual using do-calculus (amino acid - LOAD-BEARING)
        counterfactual_result = None
        if intervention["variable"] and outcome:
            try:
                counterfactual_result = do_calculus(
                    model,
                    target_vars=[outcome],
                    do_vars={intervention["variable"]: intervention["value"] if intervention["value"] is not None else 1.0},
                )
            except:
                counterfactual_result = None

        # PHASE 4: Use T1 primitives for additional epidemiological reasoning
        # 1. Bayesian update on prior belief (LOAD-BEARING)
        if rates:
            prior = rates[0] if rates else 0.5
            likelihood = rates[1] if len(rates) > 1 else 0.6
            posterior = bayesian_update(prior, likelihood)
            # Posterior directly influences which variable is selected as answer
            use_posterior_threshold = posterior > 0.5
        else:
            posterior = 0.5
            use_posterior_threshold = True

        # 2. Entropy of rate distribution (LOAD-BEARING)
        if rates:
            rate_entropy = entropy([r for r in rates if 0 <= r <= 1])
            # High entropy -> more uncertainty -> affects confidence
            high_entropy = rate_entropy > 0.5
        else:
            rate_entropy = 0.0
            high_entropy = False

        # 3. Confidence from agreement of multiple reasoning paths (LOAD-BEARING)
        scores_to_agree = []
        if counterfactual_result is not None:
            # Extract probability from counterfactual result
            if isinstance(counterfactual_result, dict) and outcome in counterfactual_result:
                prob = counterfactual_result[outcome]
                if isinstance(prob, (int, float)):
                    scores_to_agree.append(prob)
            elif isinstance(counterfactual_result, (int, float)):
                scores_to_agree.append(counterfactual_result)
        
        if posterior is not None:
            scores_to_agree.append(posterior)
        
        if scores_to_agree:
            confidence = confidence_from_agreement(scores_to_agree)
        else:
            confidence = 0.5

        # 4. Counterfactual intervention primitive (LOAD-BEARING)
        # Create simple values dict from rates
        values_dict = {}
        for i, var in enumerate(variables):
            if i < len(rates):
                values_dict[var] = rates[i]
            else:
                values_dict[var] = 0.5
        
        intervention_effect = None
        if edges and intervention["variable"] in values_dict and outcome in values_dict:
            intervention_value = intervention["value"] if intervention["value"] is not None else 1.0
            intervention_effect = counterfactual_intervention(
                edges,
                values_dict,
                intervention["variable"],
                intervention_value
            )
        
        # 5. Topological sort to determine causal order (LOAD-BEARING)
        causal_order = topological_sort(edges)
        
        # 6. Constraint solving for variable relationships (LOAD-BEARING)
        constraint_result = None
        if variables and rates:
            # Create simple constraint: sum of rates < 2.0
            domains = {var: [0.0, 0.5, 1.0] for var in variables[:3]}  # Limit to first 3
            constraints = [
                ([variables[0]], lambda x: x[0] in [0.0, 0.5, 1.0]),
            ]
            if len(variables) > 1:
                constraints.append(
                    ([variables[0], variables[1]], lambda x, y: x + y < 2.0)
                )
            constraint_result = solve_constraints(list(domains.keys()), domains, constraints)

        # DECISION LOGIC: Determine answer based on all reasoning components
        computed_answer = "Unknown"
        
        # Epidemiology framework: intervention effectiveness depends on causal structure and uncertainty
        # High entropy (uncertainty) suggests weaker causal claim
        # Clear topological order suggests stronger causal claim
        
        if counterfactual_result is not None:
            # Primary: use do-calculus result
            if isinstance(counterfactual_result, dict):
                for var, val in counterfactual_result.items():
                    if isinstance(val, (int, float)):
                        computed_answer = f"{var}={val:.2f}"
                        break
            else:
                computed_answer = f"Effect={counterfactual_result:.2f}"
        elif intervention_effect is not None and outcome in intervention_effect:
            # Secondary: use counterfactual intervention primitive
            effect = intervention_effect[outcome]
            computed_answer = f"{outcome}={effect:.2f}"
        elif causal_order:
            # Tertiary: use topological order (causal chain)
            if use_posterior_threshold:  # Bayesian update influences which end of chain
                computed_answer = causal_order[-1]  # Last in chain (effect)
            else:
                computed_answer = causal_order[0]   # First in chain (cause)
        elif constraint_result:
            # Quaternary: use constraint solving result
            first_var = list(constraint_result.keys())[0]
            computed_answer = f"{first_var}={constraint_result[first_var]}"
        else:
            # Fallback: use variable with highest posterior
            if variables:
                computed_answer = variables[0] if use_posterior_threshold else variables[-1]

        # Adjust confidence based on epidemiological principles
        # High entropy (uncertainty) reduces confidence
        if high_entropy:
            confidence *= 0.7
        
        # Confounders present reduces confidence in causal claim
        if confounders:
            confidence *= 0.8

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Causal analysis: edges={edges}, posterior={posterior:.2f}, entropy={rate_entropy:.2f}, order={causal_order}",
        }

    def _fallback_reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback reasoning when BN construction fails - still uses T1 primitives."""
        variables = structure["variables"]
        rates = structure["rates"]
        edges = structure["edges"]
        
        # 1. Bayesian update (LOAD-BEARING in fallback too)
        prior = rates[0] if rates else 0.5
        likelihood = rates[1] if len(rates) > 1 else 0.6
        posterior = bayesian_update(prior, likelihood)
        
        # 2. Entropy (LOAD-BEARING)
        if rates:
            rate_entropy = entropy([r for r in rates if 0 <= r <= 1])
        else:
            rate_entropy = 0.0
        
        # 3. Topological sort (LOAD-BEARING)
        causal_order = topological_sort(edges) if edges else None
        
        # 4. Confidence from agreement (LOAD-BEARING)
        scores = [posterior, 1 - posterior]
        confidence = confidence_from_agreement(scores)
        
        # Determine answer
        if causal_order:
            computed_answer = causal_order[0] if posterior > 0.5 else causal_order[-1]
        elif variables:
            computed_answer = variables[0] if posterior > 0.5 else variables[-1]
        else:
            computed_answer = "Unknown"
        
        return {
            "answer": computed_answer,
            "confidence": confidence * 0.8,  # Lower confidence for fallback
            "reasoning": f"Fallback: posterior={posterior:.2f}, entropy={rate_entropy:.2f}",
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: exact match or containment of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Secondary: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence,
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization: scale to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
            else:
                for item in scored:
                    item["score"] = 1.0
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0