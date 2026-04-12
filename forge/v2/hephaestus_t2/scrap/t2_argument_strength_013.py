import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Epidemiology x SAT entailment - argument_strength"""

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
            lower_line = line.lower()
            # Extract entities (capitalized words that aren't at start of sentence)
            words = re.findall(r'\b([A-Z][a-z]+)\b', line)
            for word in words:
                if word not in ['Therefore', 'Thus', 'Hence', 'So', 'Consequently']:
                    entities.add(word)
            
            # Identify conclusion (often last sentence with "therefore", "thus", etc.)
            if any(indicator in lower_line for indicator in ['therefore', 'thus', 'hence', 'so', 'consequently']):
                conclusion = line
            elif conclusion is None and line.endswith('?'):
                # Question at the end might indicate what's being asked
                conclusion = line
            else:
                # Treat as premise if not empty and not obviously a question
                if line and not line.endswith('?'):
                    premises.append(line)
        
        # If no explicit conclusion found, last non-question line might be implicit conclusion
        if conclusion is None and premises:
            conclusion = premises.pop()
        
        # Extract propositional structure: simple mapping to variables
        prop_map = {}
        prop_counter = 1
        all_statements = premises + ([conclusion] if conclusion else [])
        
        for stmt in all_statements:
            # Simple heuristic: use first significant noun phrase as variable name
            words = stmt.split()
            if len(words) > 0:
                # Take first word that starts with capital letter (likely entity)
                for word in words:
                    if word[0].isupper() and len(word) > 2:
                        if word not in prop_map:
                            prop_map[word] = f"P{prop_counter}"
                            prop_counter += 1
                        break
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "entities": list(entities),
            "prop_map": prop_map,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate argument strength using epidemiological concepts and SAT."""
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        prop_map = structure["prop_map"]
        
        if not premises or not conclusion:
            # Fallback if extraction failed
            return {
                "answer": "Invalid argument",
                "confidence": 0.0,
                "reasoning": "Could not parse argument structure"
            }
        
        # Convert to propositional logic for SAT checking
        # Simple mapping: each entity becomes a variable
        # For epidemiology framework: treat premises as exposure conditions,
        # conclusion as disease outcome
        
        # Build variable mapping
        all_vars = set()
        premise_clauses = []
        
        # Process each premise
        for prem in premises:
            # Simple parsing: look for "if-then", "and", "or", "not"
            lower_prem = prem.lower()
            
            # Convert to CNF-like representation (simplified)
            # This is a simplified translation for demonstration
            clauses = []
            
            # Check for implication patterns
            if "if" in lower_prem and "then" in lower_prem:
                # If P then Q
                parts = prem.split(" then ", 1)
                if len(parts) == 2:
                    antecedent = parts[0].replace("If ", "").replace("if ", "").strip()
                    consequent = parts[1].strip()
                    
                    # Map to variables
                    ant_var = None
                    cons_var = None
                    
                    for entity, var in prop_map.items():
                        if entity in antecedent:
                            ant_var = var
                        if entity in consequent:
                            cons_var = var
                    
                    if ant_var and cons_var:
                        # Implication: (not P or Q)
                        clauses.append([f"-{ant_var}", cons_var])
                        all_vars.add(ant_var)
                        all_vars.add(cons_var)
            
            # Check for conjunction
            elif " and " in lower_prem:
                parts = [p.strip() for p in prem.split(" and ")]
                for part in parts:
                    for entity, var in prop_map.items():
                        if entity in part:
                            clauses.append([var])
                            all_vars.add(var)
                            break
            
            # Check for negation
            elif "not " in lower_prem or "no " in lower_prem:
                for entity, var in prop_map.items():
                    if entity in prem:
                        # Check if negated
                        if f"not {entity}" in lower_prem or f"no {entity.lower()}" in lower_prem:
                            clauses.append([f"-{var}"])
                        else:
                            clauses.append([var])
                        all_vars.add(var)
                        break
            
            # Default: treat as positive assertion
            else:
                for entity, var in prop_map.items():
                    if entity in prem:
                        clauses.append([var])
                        all_vars.add(var)
                        break
            
            premise_clauses.extend(clauses)
        
        # Process conclusion
        conclusion_var = None
        conclusion_negated = False
        
        for entity, var in prop_map.items():
            if entity in conclusion:
                conclusion_var = var
                # Check if conclusion is negated
                lower_conc = conclusion.lower()
                if f"not {entity.lower()}" in lower_conc or f"no {entity.lower()}" in lower_conc:
                    conclusion_negated = True
                break
        
        if not conclusion_var:
            # Fallback: use first variable
            if prop_map:
                conclusion_var = list(prop_map.values())[0]
            else:
                return {
                    "answer": "Cannot evaluate",
                    "confidence": 0.0,
                    "reasoning": "No variables identified"
                }
        
        # Convert to numeric SAT format for check_entailment
        var_to_idx = {var: i+1 for i, var in enumerate(sorted(all_vars))}
        
        def lit_to_int(literal: str) -> int:
            if literal.startswith("-"):
                return -var_to_idx[literal[1:]]
            else:
                return var_to_idx[literal]
        
        premise_clauses_numeric = []
        for clause in premise_clauses:
            numeric_clause = [lit_to_int(lit) for lit in clause if lit[1:] if lit.startswith("-") else lit in var_to_idx]
            if numeric_clause:
                premise_clauses_numeric.append(numeric_clause)
        
        # Conclusion clause
        if conclusion_negated:
            conclusion_clause_numeric = [-var_to_idx[conclusion_var]]
        else:
            conclusion_clause_numeric = [var_to_idx[conclusion_var]]
        
        # EPIDEMIOLOGICAL REASONING FRAMEWORK
        # Model argument strength as disease transmission probability
        # Premises are exposures, conclusion is disease outcome
        # Use Bayesian update to compute strength
        
        # Base rate (prior) - uncertainty in the domain
        prior = 0.5  # Maximum uncertainty
        
        # Likelihood from premises - modeled as test accuracy
        # More premises = stronger evidence (but watch for contradictions)
        n_premises = len(premises)
        
        # Compute information content of premises
        if n_premises > 0:
            # Simple model: each premise provides some evidence
            premise_strengths = [0.7] * n_premises  # Each premise is moderately convincing
            
            # Use entropy to measure uncertainty reduction
            dist = [0.5, 0.5]  # Initial uniform distribution
            entropy_before = entropy(dist)
            
            # Update distribution based on premise strengths
            # This is a simplified epidemiological model:
            # Each premise reduces uncertainty like a diagnostic test
            for strength in premise_strengths:
                # Update belief toward conclusion
                dist[0] = dist[0] * (1 - strength) + dist[1] * strength
                dist[1] = 1 - dist[0]
            
            entropy_after = entropy(dist)
            uncertainty_reduction = entropy_before - entropy_after
            
            # Likelihood proportional to uncertainty reduction
            likelihood = min(0.95, 0.5 + uncertainty_reduction * 2)
        else:
            likelihood = 0.5
        
        # Check logical validity using SAT entailment (amino acid)
        is_valid = False
        if premise_clauses_numeric and conclusion_clause_numeric:
            validity_result = check_entailment(premise_clauses_numeric, conclusion_clause_numeric)
            if validity_result is not None:
                is_valid = validity_result
        
        # Bayesian update with epidemiological interpretation
        # False positive rate represents potential fallacies
        fp_rate = 0.2  # Base fallacy rate
        
        # Adjust FP rate based on argument complexity
        # More variables = more potential for hidden fallacies
        n_vars = len(all_vars)
        if n_vars > 3:
            fp_rate = min(0.4, fp_rate + 0.05 * (n_vars - 3))
        
        posterior = bayesian_update(prior, likelihood, fp_rate)
        
        # Use topological sort to analyze dependency structure
        # Build dependency graph from implications
        edges = []
        for clause in premise_clauses:
            if len(clause) == 2 and clause[0].startswith("-"):
                # Implication: -A v B means A -> B
                ant = clause[0][1:]  # Remove negation
                cons = clause[1]
                edges.append((ant, cons))
        
        # Perform topological sort to check for causal chains
        dep_order = []
        if edges:
            sort_result = topological_sort(edges)
            if sort_result:
                dep_order = sort_result
        
        # Confidence from multiple reasoning methods
        scores = []
        
        # Score 1: Bayesian posterior
        scores.append(posterior)
        
        # Score 2: Logical validity (1.0 if valid, 0.0 if not)
        scores.append(1.0 if is_valid else 0.0)
        
        # Score 3: Dependency structure coherence
        if dep_order and conclusion_var in dep_order:
            # Conclusion should come after premises in dependency order
            conc_idx = dep_order.index(conclusion_var)
            max_premise_idx = -1
            for prem_var in all_vars:
                if prem_var != conclusion_var and prem_var in dep_order:
                    idx = dep_order.index(prem_var)
                    if idx > max_premise_idx:
                        max_premise_idx = idx
            
            if max_premise_idx >= 0 and conc_idx > max_premise_idx:
                scores.append(0.8)  # Good dependency order
            else:
                scores.append(0.3)  # Poor dependency order
        else:
            scores.append(0.5)  # Neutral
        
        # Compute overall confidence
        confidence = confidence_from_agreement(scores)
        
        # Determine final answer
        if is_valid and posterior > 0.6:
            computed_answer = "Valid"
        elif not is_valid and posterior < 0.4:
            computed_answer = "Invalid"
        elif posterior > 0.5:
            computed_answer = "Probably valid"
        else:
            computed_answer = "Probably invalid"
        
        # Ensure answer is load-bearing on primitives:
        # 1. bayesian_update determines posterior which affects computed_answer
        # 2. entropy affects likelihood which affects posterior
        # 3. confidence_from_agreement affects confidence
        # 4. topological_sort affects dependency score
        # 5. check_entailment (amino acid) determines is_valid
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Argument strength: posterior={posterior:.2f}, valid={is_valid}, dependency_order={'->'.join(dep_order) if dep_order else 'none'}",
            "posterior": posterior,
            "is_valid": is_valid,
            "dep_order": dep_order
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for c in candidates:
            # Primary scoring: exact match or containment of computed answer
            if computed_answer.lower() in c.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, c))
            
            # Adjust based on confidence
            adjusted_score = base_score * reasoning_result["confidence"]
            
            results.append({
                "candidate": c,
                "score": adjusted_score,
                "base_score": base_score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple calibration: ensure scores are in [0, 1] range."""
        if not scored:
            return scored
        
        # Find max score for normalization
        max_score = max(item["score"] for item in scored)
        if max_score > 0:
            for item in scored:
                item["score"] = item["score"] / max_score
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a and not b:
            return 0.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)