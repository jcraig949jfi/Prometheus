import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Chemical kinetics x SAT solving - liar_detection"""

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
        """Extract agents, statements, and truth policies from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = ""
        
        current_agent = None
        for line in lines:
            # Look for agent introductions (capitalized names followed by colon or "says")
            agent_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s*[:]|\s+says)', line)
            if agent_match:
                current_agent = agent_match.group(1)
                if current_agent not in agents:
                    agents.append(current_agent)
                
                # Extract truth policy
                if "always tells the truth" in line.lower():
                    truth_policies[current_agent] = "truth"
                elif "always lies" in line.lower():
                    truth_policies[current_agent] = "lie"
                elif "alternates" in line.lower():
                    truth_policies[current_agent] = "alternate"
                elif "random" in line.lower():
                    truth_policies[current_agent] = "random"
            
            # Extract statements
            if current_agent and ('"' in line or "'" in line):
                quote_match = re.search(r'["\']([^"\']+)["\']', line)
                if quote_match:
                    statement = quote_match.group(1).strip()
                    statements.append({
                        "agent": current_agent,
                        "statement": statement,
                        "raw_line": line
                    })
            
            # Extract question (usually last line)
            if "?" in line and not question:
                question = line
        
        # Extract propositional variables (capitalized words that appear in statements)
        variables = set()
        for stmt in statements:
            words = re.findall(r'\b[A-Z][a-z]*\b', stmt["statement"])
            variables.update(words)
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "variables": list(variables),
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use chemical kinetics as scaffold: agents as chemical species, 
        truth values as concentrations, logical constraints as reaction rates."""
        
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        question = structure["question"]
        variables = structure["variables"]
        
        # Map variables to SAT literals
        var_to_lit = {var: i+1 for i, var in enumerate(variables)}
        lit_to_var = {i+1: var for i, var in enumerate(variables)}
        
        # Build CNF clauses from statements and truth policies
        clauses = []
        
        # Chemical kinetics analogy: each agent's truthfulness is a "concentration"
        # that evolves according to reaction rules (logical constraints)
        
        # 1. Track belief states using track_beliefs primitive
        # This represents the "kinetic network" of who believes what
        belief_observations = []
        for stmt in statements:
            agent = stmt["agent"]
            statement = stmt["statement"]
            # Convert statement to proposition if possible
            # Simple extraction: "X is true" -> X
            if " is true" in statement.lower():
                prop = statement.lower().replace(" is true", "").strip().title()
                if prop in variables:
                    belief_observations.append((agent, prop, True))
            elif " is false" in statement.lower():
                prop = statement.lower().replace(" is false", "").strip().title()
                if prop in variables:
                    belief_observations.append((agent, prop, False))
        
        # Use track_beliefs primitive - critical for determining what each agent believes
        belief_states = track_beliefs(agents, belief_observations)
        if belief_states is None:
            belief_states = {}
        
        # 2. Encode truth policies as constraints
        # Chemical kinetics: truth policies are "rate constants" that determine
        # how quickly falsehoods propagate through the system
        policy_clauses = []
        for agent, policy in truth_policies.items():
            if policy == "truth":
                # Agent always tells truth: if they say P, then P is true
                for stmt in statements:
                    if stmt["agent"] == agent:
                        # Extract proposition from statement
                        statement = stmt["statement"]
                        if " is true" in statement.lower():
                            prop = statement.lower().replace(" is true", "").strip().title()
                            if prop in var_to_lit:
                                # Agent says P -> P is true
                                policy_clauses.append([var_to_lit[prop]])
                        elif " is false" in statement.lower():
                            prop = statement.lower().replace(" is false", "").strip().title()
                            if prop in var_to_lit:
                                # Agent says not P -> P is false
                                policy_clauses.append([-var_to_lit[prop]])
            elif policy == "lie":
                # Agent always lies: if they say P, then P is false
                for stmt in statements:
                    if stmt["agent"] == agent:
                        statement = stmt["statement"]
                        if " is true" in statement.lower():
                            prop = statement.lower().replace(" is true", "").strip().title()
                            if prop in var_to_lit:
                                # Agent says P -> P is false
                                policy_clauses.append([-var_to_lit[prop]])
                        elif " is false" in statement.lower():
                            prop = statement.lower().replace(" is false", "").strip().title()
                            if prop in var_to_lit:
                                # Agent says not P -> P is true
                                policy_clauses.append([var_to_lit[prop]])
        
        clauses.extend(policy_clauses)
        
        # 3. Use detect_paradox amino acid to check for contradictions
        # Chemical kinetics: paradox detection is like finding equilibrium states
        # where concentrations cannot stabilize
        paradox_info = detect_paradox(clauses) if clauses else None
        
        # 4. Use solve_sat primitive to find satisfying assignments
        # This represents the "steady-state concentrations" of truth values
        sat_solution = None
        if clauses:
            sat_solution = solve_sat(clauses, len(var_to_lit))
        
        # 5. Chemical kinetics: compute "entropy" of the solution space
        # High entropy = many possible truth assignments (uncertainty)
        # Low entropy = few possibilities (certainty)
        solution_entropy = 0.0
        if sat_solution:
            # For a single solution, entropy is low
            solution_entropy = 0.1
        else:
            # If no solution, entropy is high (contradiction)
            solution_entropy = 1.0
        
        # 6. Use bayesian_update to refine confidence based on paradox detection
        # Chemical kinetics: Bayesian update is like adjusting reaction rates
        # based on observed equilibrium states
        prior_confidence = 0.5
        paradox_likelihood = 0.8 if paradox_info and paradox_info.get("is_paradox", False) else 0.2
        updated_confidence = bayesian_update(prior_confidence, paradox_likelihood, false_positive=0.1)
        
        # 7. Determine the answer based on SAT solution and question
        computed_answer = ""
        reasoning_text = ""
        
        if sat_solution:
            # Extract what the question is asking for
            if "who" in question.lower():
                # Find which agent's statement reveals the truth
                for agent in agents:
                    if agent.lower() in question.lower():
                        computed_answer = agent
                        break
                if not computed_answer:
                    # Default: agent with most consistent beliefs
                    agent_consistency = {}
                    for agent in agents:
                        consistent = 0
                        for prop, value in sat_solution.items():
                            var_name = lit_to_var.get(abs(prop))
                            if var_name and prop > 0:
                                # Check if agent's beliefs match SAT solution
                                if agent in belief_states:
                                    if var_name in belief_states[agent]:
                                        if (value and var_name in belief_states[agent]) or \
                                           (not value and var_name not in belief_states[agent]):
                                            consistent += 1
                        agent_consistency[agent] = consistent
                    
                    if agent_consistency:
                        computed_answer = max(agent_consistency.items(), key=lambda x: x[1])[0]
            elif "what" in question.lower() and "true" in question.lower():
                # Find which proposition is true
                true_props = [lit_to_var[lit] for lit, val in sat_solution.items() 
                             if lit > 0 and val and lit in lit_to_var]
                if true_props:
                    computed_answer = true_props[0]
                else:
                    false_props = [lit_to_var[abs(lit)] for lit, val in sat_solution.items() 
                                  if lit < 0 and val and abs(lit) in lit_to_var]
                    if false_props:
                        computed_answer = f"not {false_props[0]}"
        else:
            # No SAT solution - contradiction detected
            computed_answer = "contradiction"
        
        # 8. Use confidence_from_agreement primitive
        # Chemical kinetics: agreement between different reasoning paths
        # is like multiple reactions converging to same equilibrium
        confidence_scores = []
        if sat_solution:
            confidence_scores.append(0.8)
        if paradox_info and not paradox_info.get("is_paradox", False):
            confidence_scores.append(0.7)
        if computed_answer:
            confidence_scores.append(0.6)
        
        final_confidence = confidence_from_agreement(confidence_scores) if confidence_scores else 0.5
        
        # 9. Use modus_ponens to derive additional conclusions
        # Chemical kinetics: logical inference as reaction propagation
        premises = []
        for stmt in statements:
            # Convert simple implications
            if " if " in stmt["statement"].lower():
                parts = stmt["statement"].lower().split(" if ")
                if len(parts) == 2:
                    consequent = parts[0].strip().title()
                    antecedent = parts[1].strip().title()
                    if consequent in variables and antecedent in variables:
                        premises.append((antecedent, consequent))
        
        facts = set()
        if sat_solution:
            for lit, val in sat_solution.items():
                if val and abs(lit) in lit_to_var:
                    facts.add(lit_to_var[abs(lit)])
        
        derived_facts = modus_ponens(premises, facts) if premises else set()
        
        # If we still don't have an answer, use derived facts
        if not computed_answer and derived_facts:
            computed_answer = next(iter(derived_facts))
        
        # Final fallback if no answer computed
        if not computed_answer:
            computed_answer = agents[0] if agents else "unknown"
        
        reasoning_text = f"SAT solution: {sat_solution}, Paradox: {paradox_info}, Entropy: {solution_entropy:.2f}, Confidence: {final_confidence:.2f}"
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": reasoning_text,
            "sat_solution": sat_solution,
            "paradox_detected": paradox_info.get("is_paradox", False) if paradox_info else False,
            "entropy": solution_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
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
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
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
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0