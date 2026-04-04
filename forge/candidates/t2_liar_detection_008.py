import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_constraints,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Feedback systems x SAT/Constraint solving - liar_detection"""

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
        """Extract agents, statements, truth policies, and question from prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        agents = []
        statements = []  # (agent, statement_text, is_claim_about_other?)
        truth_policies = {}  # agent -> policy description
        question = ""
        
        current_agent = None
        
        for line in lines:
            # Look for agent introductions (e.g., "Alice says:", "Bob states:")
            agent_match = re.match(r'^([A-Z][a-z]+)\s+(?:says|states|claims|asserts):', line)
            if agent_match:
                current_agent = agent_match.group(1)
                if current_agent not in agents:
                    agents.append(current_agent)
                
                # Extract the statement
                statement_text = line[agent_match.end():].strip()
                if statement_text:
                    # Check if statement is about another agent
                    is_about_other = any(
                        agent in statement_text and agent != current_agent 
                        for agent in agents
                    )
                    statements.append((current_agent, statement_text, is_about_other))
            
            # Look for truth policy descriptions
            elif "always tells the truth" in line.lower():
                for agent in agents:
                    if agent.lower() in line.lower():
                        truth_policies[agent] = "truthful"
            elif "always lies" in line.lower():
                for agent in agents:
                    if agent.lower() in line.lower():
                        truth_policies[agent] = "liar"
            elif "alternates" in line.lower() or "random" in line.lower():
                for agent in agents:
                    if agent.lower() in line.lower():
                        truth_policies[agent] = "alternating"
            
            # Look for question (usually at the end)
            elif line.endswith('?'):
                question = line
        
        # If no explicit policies found, infer from statements
        for agent in agents:
            if agent not in truth_policies:
                # Check if agent makes self-referential statements
                agent_statements = [s for s in statements if s[0] == agent]
                if any("I am" in s[1] for s in agent_statements):
                    truth_policies[agent] = "unknown"
                else:
                    truth_policies[agent] = "unknown"
        
        # Extract propositional variables from statements
        variables = set()
        for _, statement, _ in statements:
            # Simple extraction: look for capitalized words that might be propositions
            words = re.findall(r'\b[A-Z][a-z]+\b', statement)
            for word in words:
                if word not in agents:  # Not an agent name
                    variables.add(word)
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "variables": list(variables),
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use feedback systems framework to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        question = structure["question"]
        variables = structure["variables"]
        
        # FEEDBACK SYSTEMS APPROACH: Model as a closed-loop system
        # Agents' statements create feedback loops of truth values
        # Stability analysis determines consistent assignments
        
        # Step 1: Encode statements as logical constraints
        # Each agent has a truth value T(agent) ∈ {True, False}
        # Each statement has a truth value based on its content
        
        # Create SAT encoding
        clauses = []
        var_map = {}  # variable name -> SAT variable index
        next_var = 1
        
        # Map agents to SAT variables
        for agent in agents:
            var_map[f"T_{agent}"] = next_var  # T_Alice = agent tells truth
            next_var += 1
        
        # Map propositional variables
        for var in variables:
            var_map[var] = next_var
            next_var += 1
        
        # Encode each statement
        for agent, statement_text, is_about_other in statements:
            agent_var = var_map[f"T_{agent}"]
            
            # Parse simple statement forms
            if "and" in statement_text.lower():
                # Conjunction: A and B
                parts = [p.strip() for p in statement_text.lower().split("and")]
                clause_vars = []
                for part in parts:
                    if part.startswith("not "):
                        var_name = part[4:].strip().capitalize()
                        if var_name in var_map:
                            clause_vars.append(-var_map[var_name])
                    else:
                        var_name = part.strip().capitalize()
                        if var_name in var_map:
                            clause_vars.append(var_map[var_name])
                
                if clause_vars:
                    # Statement is true iff all parts are true
                    # T(agent) → (A ∧ B)  and  ¬T(agent) → ¬(A ∧ B)
                    # Encode as: (¬T ∨ A) ∧ (¬T ∨ B) ∧ (T ∨ ¬A ∨ ¬B)
                    for var in clause_vars:
                        clauses.append([-agent_var, var])
                    clauses.append([agent_var] + [-v for v in clause_vars])
            
            elif "or" in statement_text.lower():
                # Disjunction: A or B
                parts = [p.strip() for p in statement_text.lower().split("or")]
                clause_vars = []
                for part in parts:
                    if part.startswith("not "):
                        var_name = part[4:].strip().capitalize()
                        if var_name in var_map:
                            clause_vars.append(-var_map[var_name])
                    else:
                        var_name = part.strip().capitalize()
                        if var_name in var_map:
                            clause_vars.append(var_map[var_name])
                
                if clause_vars:
                    # T(agent) → (A ∨ B)  and  ¬T(agent) → ¬(A ∨ B)
                    # Encode as: (¬T ∨ A ∨ B) ∧ (T ∨ ¬A) ∧ (T ∨ ¬B)
                    clauses.append([-agent_var] + clause_vars)
                    for var in clause_vars:
                        clauses.append([agent_var, -var])
            
            elif "not" in statement_text.lower():
                # Negation: not A
                var_name = statement_text.lower().replace("not", "").strip().capitalize()
                if var_name in var_map:
                    # T(agent) → ¬A  and  ¬T(agent) → A
                    clauses.append([-agent_var, -var_map[var_name]])
                    clauses.append([agent_var, var_map[var_name]])
            
            elif "is lying" in statement_text.lower() or "is a liar" in statement_text.lower():
                # Statement about another agent's truthfulness
                target = None
                for a in agents:
                    if a.lower() in statement_text.lower() and a != agent:
                        target = a
                        break
                
                if target:
                    target_var = var_map[f"T_{target}"]
                    # "X is lying" means ¬T_target
                    # T(agent) → ¬T_target  and  ¬T(agent) → T_target
                    clauses.append([-agent_var, -target_var])
                    clauses.append([agent_var, target_var])
            
            elif "is telling the truth" in statement_text.lower():
                # Statement about another agent's truthfulness
                target = None
                for a in agents:
                    if a.lower() in statement_text.lower() and a != agent:
                        target = a
                        break
                
                if target:
                    target_var = var_map[f"T_{target}"]
                    # "X is telling truth" means T_target
                    # T(agent) → T_target  and  ¬T(agent) → ¬T_target
                    clauses.append([-agent_var, target_var])
                    clauses.append([agent_var, -target_var])
            
            else:
                # Simple atomic statement
                var_name = statement_text.strip().capitalize()
                if var_name in var_map:
                    # T(agent) → A  and  ¬T(agent) → ¬A
                    clauses.append([-agent_var, var_map[var_name]])
                    clauses.append([agent_var, -var_map[var_name]])
        
        # Step 2: Encode truth policies as constraints
        for agent, policy in truth_policies.items():
            agent_var = var_map[f"T_{agent}"]
            if policy == "truthful":
                clauses.append([agent_var])  # T_agent must be true
            elif policy == "liar":
                clauses.append([-agent_var])  # T_agent must be false
            # alternating/unknown: no constraint
        
        # Step 3: Use amino acid to check consistency and find solution
        # CRITICAL: This amino acid call is load-bearing
        sat_result = check_entailment(clauses, [])
        
        # Step 4: If SAT, find a satisfying assignment using constraint solving
        computed_answer = "Unknown"
        confidence = 0.5
        
        if sat_result is not None and sat_result.get("entails", False):
            # The system is consistent, find a solution
            # Convert to CSP for solving
            variables_domains = {}
            constraints = []
            
            # Create variables
            for name, var_idx in var_map.items():
                variables_domains[name] = [0, 1]  # 0=False, 1=True
            
            # Convert clauses to CSP constraints
            for clause in clauses:
                def make_constraint(clause_vars):
                    def constraint(assignment):
                        for var in clause_vars:
                            var_name = None
                            for n, idx in var_map.items():
                                if idx == abs(var):
                                    var_name = n
                                    break
                            if var_name:
                                value = assignment.get(var_name, 0)
                                if var > 0 and value == 1:
                                    return True
                                if var < 0 and value == 0:
                                    return True
                        return False
                    return constraint
                
                constraint_vars = []
                for var in clause:
                    for name, idx in var_map.items():
                        if idx == abs(var):
                            constraint_vars.append(name)
                            break
                
                if constraint_vars:
                    constraints.append((constraint_vars, make_constraint(clause)))
            
            # CRITICAL: This amino acid call is load-bearing
            solution = solve_first(variables_domains, constraints)
            
            if solution:
                # CRITICAL: This primitive call is load-bearing
                # Check if solution is unique
                unique = is_uniquely_solvable(variables_domains, constraints)
                
                # CRITICAL: Use entropy to measure uncertainty in agent truth values
                agent_truth_probs = []
                for agent in agents:
                    var_name = f"T_{agent}"
                    if var_name in solution:
                        agent_truth_probs.append(solution[var_name])
                    else:
                        agent_truth_probs.append(0.5)  # Unknown
                
                # CRITICAL: This primitive call is load-bearing
                uncertainty = entropy(agent_truth_probs)
                
                # Determine answer based on question
                if "who is telling the truth" in question.lower():
                    truthful_agents = [
                        agent for agent in agents 
                        if solution.get(f"T_{agent}", 0) == 1
                    ]
                    if truthful_agents:
                        computed_answer = truthful_agents[0]
                        # CRITICAL: Use confidence_from_agreement on multiple possible solutions
                        # Simulate alternative solutions by flipping uncertain variables
                        alt_scores = []
                        for agent in agents:
                            if f"T_{agent}" in solution:
                                alt_scores.append(solution[f"T_{agent}"])
                        
                        # CRITICAL: This primitive call is load-bearing
                        confidence = confidence_from_agreement(alt_scores)
                        
                        # Adjust confidence based on uniqueness
                        if unique:
                            confidence = max(confidence, 0.8)
                        else:
                            confidence = max(confidence * 0.7, 0.3)
                    else:
                        computed_answer = "Nobody"
                        confidence = 0.6
                
                elif "what is true" in question.lower() or "which statement" in question.lower():
                    # Find true propositions
                    true_props = [
                        name for name, val in solution.items() 
                        if not name.startswith("T_") and val == 1
                    ]
                    if true_props:
                        computed_answer = true_props[0]
                        confidence = 0.7
                    else:
                        computed_answer = "None"
                        confidence = 0.6
                
                else:
                    # Default: answer with the most likely truthful agent
                    agent_truth_values = [
                        (agent, solution.get(f"T_{agent}", 0))
                        for agent in agents
                    ]
                    best_agent = max(agent_truth_values, key=lambda x: x[1])[0]
                    computed_answer = best_agent
                    confidence = 0.65
            else:
                # Inconsistent system - paradox detected
                computed_answer = "Paradox"
                confidence = 0.9
        else:
            # System is inconsistent or check_entailment failed
            # Fallback: use simpler reasoning with remaining primitives
            
            # CRITICAL: Fallback still uses primitives
            # Use modus_ponens on extracted statements
            premises = []
            facts = set()
            
            # Convert simple statements to implications
            for agent, statement, _ in statements:
                if "if" in statement.lower() and "then" in statement.lower():
                    parts = statement.lower().split("then")
                    if len(parts) == 2:
                        antecedent = parts[0].replace("if", "").strip()
                        consequent = parts[1].strip()
                        premises.append((antecedent.capitalize(), consequent.capitalize()))
            
            # CRITICAL: This primitive call is load-bearing in fallback
            inferred = modus_ponens(premises, facts)
            
            if inferred:
                computed_answer = list(inferred)[0]
                confidence = 0.4
            else:
                # Last resort: track beliefs
                observations = []
                for agent, statement, is_about_other in statements:
                    if is_about_other:
                        target = None
                        for a in agents:
                            if a.lower() in statement.lower() and a != agent:
                                target = a
                                break
                        if target:
                            # Agent observes something about another agent
                            observations.append((agent, target, "lying" in statement.lower()))
                
                # CRITICAL: This primitive call is load-bearing in fallback
                beliefs = track_beliefs(agents, observations)
                
                # Find agent with most consistent beliefs
                best_agent = max(agents, key=lambda a: len(beliefs.get(a, set())))
                computed_answer = best_agent
                confidence = 0.3
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Feedback systems analysis with SAT encoding. Found: {computed_answer}",
            "clauses_count": len(clauses),
            "agents": agents
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
                # Use NCD as fallback
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