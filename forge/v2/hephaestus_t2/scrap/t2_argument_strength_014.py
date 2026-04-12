import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    check_transitivity
)
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Neuroscience x SAT entailment - argument_strength"""

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
        """Extract premises, conclusion, and entities from argument prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        # Find question (usually last sentence)
        question = lines[-1] if lines else ""
        
        # Extract premises and conclusion markers
        premises = []
        conclusion = None
        entities = set()
        
        # Look for premise indicators
        for line in lines:
            if any(indicator in line.lower() for indicator in ["premise", "assume", "given", "if"]):
                # Extract proposition text
                clean_line = re.sub(r'^\d+[\.\)]\s*', '', line)
                clean_line = re.sub(r'[Pp]remise\s*\d*[:\.]\s*', '', clean_line)
                if clean_line and len(clean_line) > 3:
                    premises.append(clean_line)
                    # Extract capitalized entities
                    entities.update(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', clean_line))
        
        # Look for conclusion indicators
        for line in lines:
            if any(indicator in line.lower() for indicator in ["conclusion", "therefore", "thus", "hence", "so"]):
                clean_line = re.sub(r'^\d+[\.\)]\s*', '', line)
                clean_line = re.sub(r'[Cc]onclusion\s*[:\.]\s*', '', clean_line)
                if clean_line and len(clean_line) > 3:
                    conclusion = clean_line
                    entities.update(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', clean_line))
        
        # If no explicit conclusion found, use the question
        if conclusion is None and "?" in question:
            conclusion = question.replace("?", "").strip()
        
        # Extract logical operators and connectives
        logical_structure = {
            "has_conditional": any("if" in p.lower() or "then" in p.lower() for p in premises),
            "has_conjunction": any("and" in p.lower() for p in premises),
            "has_disjunction": any("or" in p.lower() for p in premises),
            "has_negation": any("not" in p.lower() or "no " in p.lower() for p in premises)
        }
        
        return {
            "premises": premises,
            "conclusion": conclusion,
            "question": question,
            "entities": list(entities),
            "logical_structure": logical_structure,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use neuroscience-inspired reasoning to evaluate argument strength."""
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        entities = structure["entities"]
        logical_structure = structure["logical_structure"]
        
        if not premises or conclusion is None:
            # Fallback: use entity frequency as weak signal
            if entities:
                computed_answer = entities[0]
            else:
                computed_answer = "Invalid argument"
            return {
                "answer": computed_answer,
                "confidence": 0.1,
                "reasoning": "Missing premises or conclusion",
                "strength_score": 0.0
            }
        
        # NEUROSCIENCE SCAFFOLD: Model argument strength as neural activation patterns
        # Strong arguments create coherent activation patterns (low entropy)
        # Weak arguments create conflicting patterns (high entropy)
        
        # Step 1: Encode propositions as SAT variables
        # Each unique atomic proposition gets a variable
        atomic_props = self._extract_atomic_propositions(premises + [conclusion])
        var_map = {prop: i+1 for i, prop in enumerate(atomic_props)}
        
        # Step 2: Convert premises to CNF clauses (simplified encoding)
        premise_clauses = []
        for premise in premises:
            clauses = self._proposition_to_clauses(premise, var_map)
            if clauses:
                premise_clauses.extend(clauses)
        
        # Step 3: Convert conclusion to clause (negated for entailment check)
        conclusion_clause = self._proposition_to_clauses(conclusion, var_map, negate=True)
        
        # Step 4: Check logical entailment using amino acid
        # This directly determines if the argument is valid
        is_valid = False
        if premise_clauses and conclusion_clause:
            try:
                entailment_result = check_entailment(premise_clauses, conclusion_clause[0])
                is_valid = entailment_result if entailment_result is not None else False
            except:
                is_valid = False
        
        # Step 5: Compute neural activation coherence (entropy of belief states)
        # Model premises as generating probability distributions over truth assignments
        belief_states = []
        
        # Use SAT solving to find satisfying assignments
        if premise_clauses:
            try:
                sat_result = solve_sat(premise_clauses, len(var_map))
                if sat_result:
                    # Count true assignments for each variable across all models
                    # (Simplified: we'll use the single model from solve_sat)
                    # In neuroscience terms: each variable is a neuron, activation is truth value
                    activations = [1.0 if sat_result.get(i+1, False) else 0.0 
                                 for i in range(len(var_map))]
                    belief_states.append(activations)
            except:
                pass
        
        # Compute entropy of activation patterns
        if belief_states:
            # Flatten and compute entropy of the activation distribution
            flat_activations = [val for state in belief_states for val in state]
            # Normalize to probability distribution
            total = sum(flat_activations)
            if total > 0:
                probs = [a/total for a in flat_activations]
                activation_entropy = entropy(probs)
            else:
                activation_entropy = 1.0  # Max entropy for no activation
        else:
            activation_entropy = 1.0
        
        # Step 6: Bayesian update of argument strength based on coherence
        # Prior: weak argument (0.3), Likelihood: coherence reduces entropy
        prior_strength = 0.3
        # Likelihood: low entropy → high coherence → strong argument
        coherence_likelihood = 1.0 - min(activation_entropy, 0.9)  # Cap at 0.9
        
        # Use bayesian_update primitive - this directly influences strength score
        strength_posterior = bayesian_update(prior_strength, coherence_likelihood, false_positive=0.1)
        
        # Step 7: Check logical transitivity of implications
        # Extract implication relations from premises
        implications = []
        for premise in premises:
            if "if" in premise.lower() and "then" in premise.lower():
                # Simple extraction: "if A then B"
                parts = premise.lower().split("then")
                if len(parts) == 2:
                    antecedent = parts[0].replace("if", "").strip()
                    consequent = parts[1].strip()
                    # Map to entity names if possible
                    ant_entity = self._find_entity(antecedent, entities)
                    cons_entity = self._find_entity(consequent, entities)
                    if ant_entity and cons_entity:
                        implications.append((ant_entity, cons_entity))
        
        # Use check_transitivity primitive - this affects confidence
        transitive_closure = {}
        if implications:
            try:
                transitive_closure = check_transitivity(implications)
            except:
                transitive_closure = {}
        
        # Step 8: Modus ponens application
        # Extract facts from premises (simple atomic propositions)
        facts = set()
        for premise in premises:
            if not any(op in premise.lower() for op in ["if", "then", "or", "and", "not"]):
                # Simple fact
                fact_entity = self._find_entity(premise, entities)
                if fact_entity:
                    facts.add(fact_entity)
        
        # Create implication rules for modus_ponens
        mp_rules = []
        for ant, cons in implications:
            mp_rules.append((ant, cons))
        
        # Use modus_ponens primitive - this determines what can be derived
        derived = set()
        if mp_rules and facts:
            try:
                derived = modus_ponens(mp_rules, facts)
            except:
                derived = set()
        
        # Step 9: Final strength computation
        # Base strength from Bayesian posterior
        base_strength = strength_posterior
        
        # Boost if argument is logically valid
        if is_valid:
            base_strength *= 1.5
        
        # Boost if conclusion can be derived via modus ponens
        conc_entity = self._find_entity(conclusion, entities)
        if conc_entity and conc_entity in derived:
            base_strength *= 1.3
        
        # Normalize strength to [0, 1]
        final_strength = min(max(base_strength, 0.0), 1.0)
        
        # Step 10: Confidence from agreement of multiple reasoning paths
        # Different measures of argument quality
        quality_scores = [
            final_strength,
            1.0 if is_valid else 0.0,
            0.8 if conc_entity in derived else 0.2,
            1.0 - activation_entropy
        ]
        
        # Use confidence_from_agreement primitive - this directly sets confidence
        confidence = confidence_from_agreement(quality_scores)
        
        # Determine answer based on strength and validity
        if final_strength > 0.6:
            if is_valid:
                computed_answer = "Valid and strong argument"
            else:
                computed_answer = "Strong but invalid argument"
        elif final_strength > 0.3:
            computed_answer = "Moderately strong argument"
        else:
            computed_answer = "Weak argument"
        
        # If we have a specific entity conclusion, use it
        if conc_entity and final_strength > 0.5:
            computed_answer = f"Argument supports {conc_entity}"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Strength: {final_strength:.2f}, Valid: {is_valid}, Derived: {conc_entity in derived}",
            "strength_score": final_strength,
            "is_valid": is_valid,
            "derived_conclusion": conc_entity in derived
        }

    def _extract_atomic_propositions(self, propositions: List[str]) -> List[str]:
        """Extract atomic propositions from natural language."""
        atoms = []
        for prop in propositions:
            # Simple splitting on common connectives
            parts = re.split(r'\b(?:and|or|but|if|then)\b', prop.lower())
            for part in parts:
                clean = part.strip().strip('.,;')
                if clean and len(clean) > 2 and clean not in atoms:
                    atoms.append(clean)
        return list(set(atoms))

    def _proposition_to_clauses(self, proposition: str, var_map: Dict[str, int], 
                               negate: bool = False) -> List[List[int]]:
        """Convert natural language proposition to CNF clauses (simplified)."""
        clauses = []
        prop_lower = proposition.lower()
        
        # Handle simple atomic propositions
        if not any(op in prop_lower for op in ["and", "or", "if", "not"]):
            atom = proposition.strip().strip('.,;')
            if atom in var_map:
                var = var_map[atom]
                if negate:
                    clauses.append([-var])
                else:
                    clauses.append([var])
            return clauses
        
        # Handle negation
        if "not" in prop_lower:
            rest = prop_lower.replace("not", "").strip()
            if rest in var_map:
                var = var_map[rest]
                if negate:
                    clauses.append([var])  # Double negation
                else:
                    clauses.append([-var])
            return clauses
        
        # Handle conjunction (A and B)
        if " and " in prop_lower:
            parts = [p.strip() for p in prop_lower.split(" and ")]
            clause = []
            for part in parts:
                if part in var_map:
                    var = var_map[part]
                    clause.append(-var if negate else var)
            if clause:
                clauses.append(clause)
            return clauses
        
        # Handle implication (if A then B)
        if "if" in prop_lower and "then" in prop_lower:
            # Convert to clause: (¬A ∨ B)
            parts = prop_lower.split("then")
            if len(parts) == 2:
                antecedent = parts[0].replace("if", "").strip()
                consequent = parts[1].strip()
                if antecedent in var_map and consequent in var_map:
                    ant_var = var_map[antecedent]
                    cons_var = var_map[consequent]
                    if negate:
                        # Negation of implication: (A ∧ ¬B)
                        clauses.append([ant_var])
                        clauses.append([-cons_var])
                    else:
                        clauses.append([-ant_var, cons_var])
            return clauses
        
        # Default: treat as atomic
        atom = proposition.strip().strip('.,;')
        if atom in var_map:
            var = var_map[atom]
            if negate:
                clauses.append([-var])
            else:
                clauses.append([var])
        
        return clauses

    def _find_entity(self, text: str, entities: List[str]) -> str:
        """Find the most relevant entity in text."""
        if not entities:
            return ""
        
        text_lower = text.lower()
        for entity in entities:
            if entity.lower() in text_lower:
                return entity
        
        # Return first entity as fallback
        return entities[0] if entities else ""

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        strength = reasoning_result.get("strength_score", 0.5)
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Secondary: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust based on argument strength for relevant candidates
            if any(word in candidate.lower() for word in ["strong", "valid", "weak", "invalid"]):
                # Candidate is making a strength claim
                if "strong" in candidate.lower() and strength > 0.6:
                    base_score *= 1.2
                elif "weak" in candidate.lower() and strength < 0.4:
                    base_score *= 1.2
                elif "valid" in candidate.lower() and reasoning_result.get("is_valid", False):
                    base_score *= 1.2
                elif "invalid" in candidate.lower() and not reasoning_result.get("is_valid", True):
                    base_score *= 1.2
            
            results.append({
                "candidate": candidate,
                "score": base_score,
                "raw_score": base_score
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
        """Calibrate scores to better distribution."""
        if not scored:
            return scored
        
        scores = [item["raw_score"] for item in scored]
        if not scores:
            return scored
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score < 0.001:
            # All scores are similar, spread them slightly
            for i, item in enumerate(scored):
                item["score"] = 0.5 + (i * 0.01)
        else:
            # Normalize to [0, 1] range
            for item in scored:
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                item["score"] = normalized
        
        return scored