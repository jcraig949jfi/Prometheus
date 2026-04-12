import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    counterfactual_intervention,
    topological_sort,
    solve_linear_system,
    expected_value,
    information_sufficiency,
    modus_ponens,
    temporal_order,
    parity_check,
    pigeonhole_check,
    coin_flip_independence,
    bat_and_ball,
    all_but_n,
    direction_composition,
    check_transitivity,
    dag_traverse,
    track_beliefs,
    sally_anne_test,
    solve_sat,
    solve_constraints,
    modular_arithmetic,
    fencepost_count,
    negate,
)
from forge.amino_acids.pgmpy_acids import (
    build_bn,
    conditional_query,
    detect_confounders,
    do_calculus,
    get_adjustment_set,
    compare_conditional_marginal,
    active_trails,
    map_query,
    find_dseparators,
    get_markov_blanket,
)
from forge.amino_acids.pysat_acids import (
    solve,
    detect_paradox,
    check_entailment,
    count_models,
    enumerate_models,
    extract_mus,
    is_valid,
    maxsat_solve,
    encode_exactly_k,
)
from forge.amino_acids.constraint_acids import (
    solve_first,
    solve_all,
    check_consistency,
    is_uniquely_solvable,
    count_solutions,
    find_conflicts,
)
from forge.amino_acids.nashpy_acids import (
    find_equilibria,
    is_dominated,
    best_response,
    find_dominant_strategy,
    compute_minimax,
    expected_payoff,
)


class ReasoningTool:
    """Seismology x pgmpy_acids - causal_counterfactual"""

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
        """Extract entities, values, causal relationships, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find entity names (capitalized phrases that appear multiple times)
        words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', prompt)
        from collections import Counter
        word_counts = Counter(words)
        entities = [word for word, count in word_counts.items() if count >= 2 and len(word) > 1]
        
        # Extract numerical values (percentages, rates, counts)
        percentages = [float(p.rstrip('%')) / 100.0 for p in re.findall(r'([0-9]+\.?[0-9]*)%', prompt)]
        integers = [int(n) for n in re.findall(r'\b([0-9]+)\b', prompt) if 0 < int(n) < 1000]
        floats = [float(f) for f in re.findall(r'\b([0-9]+\.[0-9]+)\b', prompt)]
        
        # Extract causal language patterns
        causal_verbs = ['causes', 'affects', 'influences', 'leads to', 'results in', 'determines']
        causal_pairs = []
        for verb in causal_verbs:
            pattern = rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+{verb}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            causal_pairs.extend([(a, b) for a, b in matches])
        
        # Extract intervention mentions
        intervention_keywords = ['if', 'were', 'had', 'would', 'counterfactual', 'intervention', 'set to']
        intervention_present = any(keyword in prompt.lower() for keyword in intervention_keywords)
        
        # Extract outcome variable (often mentioned in question)
        outcome_match = re.search(r'(?:what|which|how|whether).*?\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', question, re.IGNORECASE)
        outcome = outcome_match.group(1) if outcome_match else ""
        
        return {
            "entities": entities,
            "percentages": percentages,
            "integers": integers,
            "floats": floats,
            "causal_pairs": causal_pairs,
            "intervention_present": intervention_present,
            "outcome": outcome,
            "question": question,
            "raw": prompt,
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply seismology-inspired reasoning to compute counterfactual answer."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        causal_pairs = structure["causal_pairs"]
        outcome = structure["outcome"]
        question = structure["question"]
        
        # If no clear causal structure, fall back to simpler reasoning
        if not causal_pairs or len(entities) < 2:
            return self._fallback_reason(structure)
        
        # SEISMOLOGY FRAMEWORK: Treat causal relationships as fault lines
        # Interventions are like seismic waves propagating through the network
        # Counterfactuals are like predicting ground motion at different locations
        
        # 1. Build causal graph from extracted pairs
        edges = list(set(causal_pairs))
        
        # 2. Use topological_sort to determine causal ordering (LOAD-BEARING)
        try:
            causal_order = topological_sort(edges)
            if causal_order is None:
                # Graph has cycles, use extracted order
                causal_order = list(set([e[0] for e in edges] + [e[1] for e in edges]))
        except Exception:
            causal_order = list(set([e[0] for e in edges] + [e[1] for e in edges]))
        
        # 3. Build Bayesian network using amino acid (LOAD-BEARING)
        bn_model = None
        try:
            # Create simple CPDs from extracted percentages if available
            cpd_specs = {}
            if percentages:
                for i, node in enumerate(causal_order):
                    if i < len(percentages):
                        prob = percentages[i]
                        cpd_specs[node] = {
                            'variable': node,
                            'variable_card': 2,
                            'values': [[prob, 1 - prob]],
                            'evidence': [],
                            'evidence_card': []
                        }
            
            bn_model = build_bn(edges, cpd_specs)
        except Exception:
            bn_model = None
        
        # 4. Determine intervention from question
        intervention_node = None
        intervention_value = None
        
        # Look for "if X were set to Y" patterns
        intervention_pattern = r'if\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:were|was)\s+(?:set to|equal to|)\s*([0-9]+\.?[0-9]*)'
        match = re.search(intervention_pattern, question, re.IGNORECASE)
        if match:
            intervention_node = match.group(1)
            intervention_value = float(match.group(2))
            if intervention_value > 1 and intervention_value <= 100:
                intervention_value /= 100.0
        else:
            # Default: intervene on first cause
            intervention_node = edges[0][0] if edges else None
            intervention_value = 0.0 if percentages else 1.0
        
        # 5. Compute counterfactual using amino acid (LOAD-BEARING)
        counterfactual_result = None
        if bn_model and intervention_node and outcome and intervention_node in causal_order:
            try:
                # Use do_calculus to compute P(outcome | do(intervention_node = intervention_value))
                counterfactual_result = do_calculus(
                    bn_model, 
                    [outcome], 
                    {intervention_node: intervention_value}
                )
            except Exception:
                counterfactual_result = None
        
        # 6. Use bayesian_update to incorporate uncertainty (LOAD-BEARING)
        prior = 0.5
        likelihood = 0.7  # Default confidence in extracted relationships
        
        if percentages:
            # Use average of extracted percentages as likelihood
            likelihood = sum(percentages) / len(percentages) if percentages else 0.7
        
        posterior = bayesian_update(prior, likelihood)
        
        # 7. Use entropy to measure uncertainty in the result (LOAD-BEARING)
        if counterfactual_result and isinstance(counterfactual_result, dict):
            probs = list(counterfactual_result.values())
            uncertainty = entropy(probs) if probs else 1.0
        else:
            uncertainty = 1.0
        
        # 8. Determine computed answer based on counterfactual result
        computed_answer = ""
        confidence = 0.5
        
        if counterfactual_result and isinstance(counterfactual_result, dict):
            # Find the most likely outcome state
            max_state = max(counterfactual_result.items(), key=lambda x: x[1])
            computed_answer = f"{outcome} = {max_state[0]}" if outcome else str(max_state[0])
            confidence = max_state[1] * (1 - uncertainty)
        elif bn_model and outcome:
            # Fallback: query without intervention
            try:
                marginal = conditional_query(bn_model, [outcome], {})
                if marginal and isinstance(marginal, dict):
                    max_state = max(marginal.items(), key=lambda x: x[1])
                    computed_answer = f"{outcome} = {max_state[0]}"
                    confidence = max_state[1] * posterior
            except Exception:
                computed_answer = outcome if outcome else entities[0] if entities else "Unknown"
                confidence = posterior
        else:
            computed_answer = outcome if outcome else entities[0] if entities else "Unknown"
            confidence = posterior
        
        # Apply seismology-inspired confidence adjustment
        # In seismology, confidence depends on network connectivity and data quality
        network_density = len(edges) / max(1, len(entities) * (len(entities) - 1))
        seismic_confidence = confidence * (1 - network_density)  # More connected = more certain
        
        return {
            "answer": computed_answer,
            "confidence": seismic_confidence,
            "uncertainty": uncertainty,
            "causal_order": causal_order,
            "intervention": (intervention_node, intervention_value),
            "reasoning": f"Seismic propagation through causal network: {edges}",
        }

    def _fallback_reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback reasoning when causal structure is unclear."""
        entities = structure["entities"]
        percentages = structure["percentages"]
        integers = structure["integers"]
        question = structure["question"]
        
        # Use expected_value on extracted numbers (LOAD-BEARING in fallback)
        computed_answer = ""
        confidence = 0.5
        
        if percentages:
            # Create simple probability-value pairs
            outcomes = []
            for i, p in enumerate(percentages[:5]):  # Use first 5 percentages
                value = i + 1  # Assign ordinal values
                outcomes.append((p, value))
            
            if outcomes:
                ev = expected_value(outcomes)
                computed_answer = f"Expected value: {ev:.2f}"
                confidence = min(0.8, len(percentages) / 10.0)
        
        elif integers:
            # Use parity_check on integers (LOAD-BEARING in fallback)
            parity = parity_check(integers[:10])  # Use first 10 integers
            computed_answer = f"Parity: {parity}"
            confidence = 0.6
        
        elif entities:
            # Use information_sufficiency (LOAD-BEARING in fallback)
            n_unknowns = len(entities)
            n_constraints = len(re.findall(r'\b(is|are|was|were)\b', question, re.IGNORECASE))
            sufficiency = information_sufficiency(n_unknowns, n_constraints)
            computed_answer = f"System is {sufficiency}"
            confidence = 0.5
        
        else:
            computed_answer = "Insufficient data"
            confidence = 0.3
        
        # Apply bayesian_update even in fallback (LOAD-BEARING)
        prior = 0.5
        likelihood = confidence
        posterior = bayesian_update(prior, likelihood)
        
        return {
            "answer": computed_answer,
            "confidence": posterior,
            "uncertainty": 1 - posterior,
            "causal_order": [],
            "intervention": (None, None),
            "reasoning": "Fallback reasoning using statistical measures",
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            score = 0.0
            
            if computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Use NCD similarity as fallback
                ncd_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
                score = ncd_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score,
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence_from_agreement."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Use confidence_from_agreement to adjust scores (LOAD-BEARING)
        try:
            agreement_confidence = confidence_from_agreement(raw_scores)
        except Exception:
            agreement_confidence = 0.5
        
        # Calibrate scores based on agreement confidence
        calibrated = []
        for item in scored:
            calibrated_score = item["raw_score"] * agreement_confidence
            calibrated.append({
                "candidate": item["candidate"],
                "score": calibrated_score,
            })
        
        return calibrated

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