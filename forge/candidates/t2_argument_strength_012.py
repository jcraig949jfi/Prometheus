import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    topological_sort
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Game theory x SAT entailment - argument_strength"""

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
        """Extract premises, conclusion, and entities from the argument."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        premises = []
        conclusion = None
        entities = set()
        
        # Look for premise indicators and conclusion indicators
        for line in lines:
            line_lower = line.lower()
            # Extract entities (capitalized words that aren't at start of sentence)
            words = re.findall(r'\b([A-Z][a-z]+)\b', line)
            entities.update(words)
            
            # Check if this is a conclusion
            if any(indicator in line_lower for indicator in ['therefore', 'thus', 'hence', 'so', 'conclusion']):
                conclusion = line
            elif 'if' in line_lower or 'then' in line_lower or 'implies' in line_lower or 'and' in line_lower:
                premises.append(line)
        
        # If no conclusion marker found, last line is likely conclusion
        if conclusion is None and lines:
            conclusion = lines[-1]
            if len(lines) > 1:
                premises = lines[:-1]
        
        # Extract propositional variables (single letters or short words)
        variables = set()
        for text in premises + [conclusion] if conclusion else []:
            # Find single letters (A, B, C) or short capitalized words
            found = re.findall(r'\b([A-Z])\b', text)
            variables.update(found)
            # Also look for short capitalized words that might be variables
            short_words = re.findall(r'\b([A-Z][a-z]{1,3})\b', text)
            variables.update(short_words)
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "entities": list(entities),
            "variables": list(variables),
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use game theory and SAT to evaluate argument strength."""
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        variables = structure["variables"]
        
        if not premises or conclusion is None or not variables:
            # Fallback: use topological sort on extracted entities
            if structure["entities"]:
                # Create a simple dependency graph based on mention order
                edges = []
                entities = structure["entities"]
                for i in range(len(entities)-1):
                    edges.append((entities[i], entities[i+1]))
                
                try:
                    sorted_entities = topological_sort(edges)
                    if sorted_entities:
                        computed_answer = sorted_entities[0]
                        confidence = 0.3
                        return {
                            "answer": computed_answer,
                            "confidence": confidence,
                            "reasoning": "Fallback: topological sort on entities"
                        }
                except:
                    pass
            
            # Ultimate fallback
            computed_answer = "Invalid"
            confidence = 0.1
            return {
                "answer": computed_answer,
                "confidence": confidence,
                "reasoning": "Could not parse argument structure"
            }
        
        # Convert natural language to propositional logic
        # Simple mapping: each variable becomes a proposition
        var_map = {}
        for i, var in enumerate(variables, 1):
            var_map[var] = i  # Positive literal
        
        # Build SAT clauses from premises
        clauses = []
        
        for premise in premises:
            premise_clauses = self._parse_premise(premise, var_map)
            if premise_clauses:
                clauses.extend(premise_clauses)
        
        # Build conclusion clause (negated for entailment check)
        conclusion_clause = self._parse_conclusion(conclusion, var_map)
        
        # CRITICAL PATH 1: Use check_entailment amino acid
        # This directly determines if the argument is valid
        is_valid_result = check_entailment(clauses, conclusion_clause)
        
        # CRITICAL PATH 2: Use solve_sat primitive on premises
        # This determines if premises are consistent
        sat_result = solve_sat(clauses, len(var_map))
        
        # CRITICAL PATH 3: Use is_uniquely_solvable amino acid
        # Check if premises uniquely determine conclusion
        # Convert to CSP format
        if var_map:
            variables_domains = {var: [True, False] for var in var_map.keys()}
            csp_constraints = []
            
            # Convert SAT clauses to CSP constraints
            for clause in clauses:
                def make_constraint(clause_vars, clause_lits):
                    def constraint(assignment):
                        # At least one literal must be true
                        for var, lit in zip(clause_vars, clause_lits):
                            if lit > 0 and assignment[var]:
                                return True
                            elif lit < 0 and not assignment[var]:
                                return True
                        return False
                    return constraint
                
                clause_vars = []
                clause_lits = []
                for lit in clause:
                    var_name = None
                    for v, idx in var_map.items():
                        if abs(lit) == idx:
                            var_name = v
                            break
                    if var_name:
                        clause_vars.append(var_name)
                        clause_lits.append(lit)
                
                if clause_vars:
                    csp_constraints.append((clause_vars, make_constraint(clause_vars, clause_lits)))
            
            unique_solvable = is_uniquely_solvable(variables_domains, csp_constraints)
        else:
            unique_solvable = False
        
        # CRITICAL PATH 4: Use modus_ponens primitive
        # Extract simple implications for modus ponens
        mp_premises = []
        mp_facts = set()
        
        for premise in premises:
            # Look for "if A then B" patterns
            if_match = re.search(r'if\s+([^,]+)\s+then\s+([^.]+)', premise.lower())
            if if_match:
                antecedent = if_match.group(1).strip()
                consequent = if_match.group(2).strip()
                
                # Find which variables match
                ant_vars = []
                cons_vars = []
                
                for var in variables:
                    if var.lower() in antecedent.lower():
                        ant_vars.append(var)
                    if var.lower() in consequent.lower():
                        cons_vars.append(var)
                
                if ant_vars and cons_vars:
                    for ant in ant_vars:
                        for cons in cons_vars:
                            mp_premises.append((ant, cons))
            
            # Check for simple facts
            for var in variables:
                if var.lower() in premise.lower() and 'not' not in premise.lower():
                    # Simple positive assertion
                    mp_facts.add(var)
        
        mp_result = modus_ponens(mp_premises, mp_facts)
        
        # CRITICAL PATH 5: Use entropy primitive
        # Calculate entropy of truth value distribution
        if sat_result:
            # Count models to estimate distribution
            true_count = 0
            for var in var_map.values():
                if sat_result.get(var, False):
                    true_count += 1
            
            prob_true = true_count / len(var_map) if var_map else 0.5
            entropy_val = entropy([prob_true, 1 - prob_true])
        else:
            entropy_val = entropy([0.5, 0.5])
        
        # CRITICAL PATH 6: Use bayesian_update primitive
        # Update belief in conclusion based on premises
        prior = 0.5  # Initial belief
        likelihood = 0.8 if is_valid_result else 0.2
        posterior = bayesian_update(prior, likelihood)
        
        # CRITICAL PATH 7: Use confidence_from_agreement primitive
        # Multiple indicators of argument strength
        indicators = []
        if is_valid_result:
            indicators.append(0.9)
        if sat_result:
            indicators.append(0.7)
        if unique_solvable:
            indicators.append(0.8)
        if mp_result:
            indicators.append(0.6)
        
        if indicators:
            confidence = confidence_from_agreement(indicators)
        else:
            confidence = 0.5
        
        # Game theory perspective: argument as strategic game
        # Strong arguments have high posterior, low entropy, high confidence
        argument_strength = posterior * (1 - entropy_val) * confidence
        
        # Determine computed answer based on reasoning
        if is_valid_result and sat_result and argument_strength > 0.5:
            computed_answer = "Valid"
            strength_desc = "Strong"
        elif is_valid_result and sat_result:
            computed_answer = "Valid"
            strength_desc = "Moderate"
        elif sat_result and not is_valid_result:
            computed_answer = "Invalid"
            strength_desc = "Weak"
        else:
            computed_answer = "Invalid"
            strength_desc = "Very weak"
        
        # Incorporate modus_ponens result
        if mp_result and computed_answer == "Valid":
            computed_answer = "Deductively Valid"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Argument is {computed_answer} ({strength_desc}). "
                        f"SAT check: {'satisfiable' if sat_result else 'unsatisfiable'}. "
                        f"Entailment: {'holds' if is_valid_result else 'fails'}. "
                        f"Posterior belief: {posterior:.2f}, Entropy: {entropy_val:.2f}",
            "raw_strength": argument_strength
        }

    def _parse_premise(self, premise: str, var_map: Dict[str, int]) -> List[List[int]]:
        """Convert natural language premise to SAT clauses."""
        clauses = []
        premise_lower = premise.lower()
        
        # Handle conjunction (A and B)
        if ' and ' in premise_lower:
            parts = [p.strip() for p in premise_lower.split(' and ')]
            for part in parts:
                for var, idx in var_map.items():
                    if var.lower() in part:
                        if 'not' in part:
                            clauses.append([-idx])
                        else:
                            clauses.append([idx])
        
        # Handle disjunction (A or B)
        elif ' or ' in premise_lower:
            parts = [p.strip() for p in premise_lower.split(' or ')]
            clause = []
            for part in parts:
                for var, idx in var_map.items():
                    if var.lower() in part:
                        if 'not' in part:
                            clause.append(-idx)
                        else:
                            clause.append(idx)
            if clause:
                clauses.append(clause)
        
        # Handle implication (if A then B)
        elif 'if ' in premise_lower and ' then ' in premise_lower:
            # Extract parts
            match = re.search(r'if\s+([^,]+)\s+then\s+([^.]+)', premise_lower)
            if match:
                antecedent = match.group(1).strip()
                consequent = match.group(2).strip()
                
                ant_vars = []
                cons_vars = []
                
                for var, idx in var_map.items():
                    if var.lower() in antecedent.lower():
                        if 'not' in antecedent.lower():
                            ant_vars.append(-idx)
                        else:
                            ant_vars.append(idx)
                    if var.lower() in consequent.lower():
                        if 'not' in consequent.lower():
                            cons_vars.append(-idx)
                        else:
                            cons_vars.append(idx)
                
                # Implication: (not A) or B
                for ant in ant_vars:
                    for cons in cons_vars:
                        clauses.append([-ant, cons])
        
        # Simple statement
        else:
            for var, idx in var_map.items():
                if var.lower() in premise_lower:
                    if 'not' in premise_lower:
                        clauses.append([-idx])
                    else:
                        clauses.append([idx])
        
        return clauses

    def _parse_conclusion(self, conclusion: str, var_map: Dict[str, int]) -> List[int]:
        """Convert conclusion to a single clause (negated for entailment check)."""
        conclusion_lower = conclusion.lower()
        clause = []
        
        # Handle conjunction in conclusion (for entailment, we need all)
        if ' and ' in conclusion_lower:
            parts = [p.strip() for p in conclusion_lower.split(' and ')]
            for part in parts:
                for var, idx in var_map.items():
                    if var.lower() in part:
                        if 'not' in part:
                            clause.append(idx)  # Negated in conclusion becomes positive in clause
                        else:
                            clause.append(-idx)  # Positive in conclusion becomes negative in clause
        else:
            # Single statement
            for var, idx in var_map.items():
                if var.lower() in conclusion_lower:
                    if 'not' in conclusion_lower:
                        clause.append(idx)  # Negated in conclusion
                    else:
                        clause.append(-idx)  # Positive in conclusion
        
        return clause if clause else [1]  # Default clause if no variables found

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD similarity between reasoning text and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
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
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Normalize scores to [0, 1] range
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            normalized = [(s - min(scores)) / (max(scores) - min(scores)) for s in scores]
        else:
            normalized = [0.5 for _ in scores]
        
        # Apply softmax for final probabilities
        exp_scores = [2.71828 ** s for s in normalized]
        total = sum(exp_scores)
        if total > 0:
            final_scores = [s / total for s in exp_scores]
        else:
            final_scores = [1.0 / len(scored) for _ in scored]
        
        for i, item in enumerate(scored):
            item["score"] = final_scores[i]
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0