import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    modus_ponens,
    track_beliefs,
    confidence_from_agreement,
    solve_sat,
    check_transitivity
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Feedback Systems x SAT/Constraint Solving - Liar Detection"""

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
        
        agents = set()
        statements = []
        truth_policies = {}  # agent -> policy: "always_truthful", "always_lying", "alternating", etc.
        question = lines[-1] if lines else ""
        
        # Look for agent declarations and their policies
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:always\s+(tells the truth|lies)|alternates|is (truthful|lying))'
        statement_pattern = r'\"([^\"]+)\"'
        
        for line in lines:
            # Extract agents and policies
            agent_matches = re.findall(agent_pattern, line, re.IGNORECASE)
            for match in agent_matches:
                agent_name = match[0]
                policy_text = match[1] if match[1] else match[2] if len(match) > 2 else ""
                agents.add(agent_name)
                
                if 'truth' in policy_text.lower() or 'truthful' in policy_text.lower():
                    truth_policies[agent_name] = "always_truthful"
                elif 'lie' in policy_text.lower() or 'lying' in policy_text.lower():
                    truth_policies[agent_name] = "always_lying"
                elif 'alternat' in policy_text.lower():
                    truth_policies[agent_name] = "alternating"
                else:
                    truth_policies[agent_name] = "unknown"
            
            # Extract quoted statements
            statement_matches = re.findall(statement_pattern, line)
            for stmt in statement_matches:
                # Try to associate statement with agent
                for agent in agents:
                    if agent.lower() in line.lower() and stmt not in statements:
                        statements.append((agent, stmt))
                        break
        
        # Extract numerical constraints if present (e.g., "exactly one statement is true")
        constraints = []
        for line in lines:
            if re.search(r'exactly\s+(\d+)\s+(?:statement|claim)', line, re.IGNORECASE):
                match = re.search(r'exactly\s+(\d+)', line, re.IGNORECASE)
                if match:
                    constraints.append(('exactly', int(match.group(1))))
            elif re.search(r'at least\s+(\d+)\s+(?:statement|claim)', line, re.IGNORECASE):
                match = re.search(r'at least\s+(\d+)', line, re.IGNORECASE)
                if match:
                    constraints.append(('at_least', int(match.group(1))))
            elif re.search(r'at most\s+(\d+)\s+(?:statement|claim)', line, re.IGNORECASE):
                match = re.search(r'at most\s+(\d+)', line, re.IGNORECASE)
                if match:
                    constraints.append(('at_most', int(match.group(1))))
        
        return {
            "agents": list(agents),
            "statements": statements,  # list of (agent, statement)
            "truth_policies": truth_policies,
            "constraints": constraints,
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use feedback systems reasoning with SAT/constraint solving to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        constraints = structure["constraints"]
        
        # FEEDBACK SYSTEMS APPROACH: Model truth values as a dynamic system
        # where each agent's statement creates feedback loops through logical dependencies
        # Stability = consistent assignment of truth values
        
        # Step 1: Encode as SAT problem
        # Variables: truth value of each statement (S1, S2, ...) and each agent's type (T_A, T_B, ...)
        # Constraints come from:
        # 1. Agent truth policies
        # 2. Logical content of statements (e.g., "A says: B is lying")
        # 3. Global constraints from prompt
        
        # Create variable mapping
        stmt_vars = {}
        agent_type_vars = {}
        var_counter = 1
        
        for i, (agent, stmt) in enumerate(statements):
            stmt_vars[(agent, stmt)] = var_counter
            var_counter += 1
        
        for agent in agents:
            agent_type_vars[agent] = var_counter
            var_counter += 1
        
        clauses = []
        
        # Constraint 1: Agent truth policies
        for agent, policy in truth_policies.items():
            agent_var = agent_type_vars[agent]
            
            # Find all statements by this agent
            agent_statements = [(a, s) for (a, s) in statements if a == agent]
            
            for (stmt_agent, stmt_text) in agent_statements:
                stmt_var = stmt_vars[(stmt_agent, stmt_text)]
                
                if policy == "always_truthful":
                    # If agent is truthful, statement must be true
                    clauses.append([agent_var, -stmt_var])  # ¬T_A ∨ S (T_A → S)
                    clauses.append([-agent_var, stmt_var])  # T_A ∨ ¬S (¬T_A → ¬S) - Actually simpler: T_A ↔ S
                    # Actually, for always truthful: T_A → S and ¬T_A → ¬S, so T_A ↔ S
                    clauses.append([agent_var, -stmt_var])
                    clauses.append([-agent_var, stmt_var])
                elif policy == "always_lying":
                    # If agent is lying, statement must be false
                    clauses.append([agent_var, stmt_var])   # ¬T_A ∨ ¬S (T_A → ¬S)
                    clauses.append([-agent_var, -stmt_var]) # T_A ∨ S (¬T_A → S)
                # For alternating or unknown, we need more complex encoding
        
        # Constraint 2: Analyze statement content for logical dependencies
        # Parse statements that refer to other agents or statements
        for (agent, stmt_text) in statements:
            stmt_var = stmt_vars[(agent, stmt_text)]
            
            # Check if statement claims another agent is lying/truthful
            for other_agent in agents:
                if other_agent.lower() in stmt_text.lower() and other_agent != agent:
                    if 'lying' in stmt_text.lower() or 'lie' in stmt_text.lower():
                        # "A says: B is lying" means: S_A ↔ ¬T_B
                        other_var = agent_type_vars[other_agent]
                        clauses.append([-stmt_var, -other_var])  # ¬S_A ∨ ¬T_B
                        clauses.append([stmt_var, other_var])    # S_A ∨ T_B
                    elif 'truth' in stmt_text.lower():
                        # "A says: B is truthful" means: S_A ↔ T_B
                        other_var = agent_type_vars[other_agent]
                        clauses.append([-stmt_var, other_var])   # ¬S_A ∨ T_B
                        clauses.append([stmt_var, -other_var])   # S_A ∨ ¬T_B
            
            # Check if statement claims another statement is true/false
            for (other_agent, other_stmt) in statements:
                if other_stmt.lower() in stmt_text.lower() and (agent, stmt_text) != (other_agent, other_stmt):
                    other_var = stmt_vars[(other_agent, other_stmt)]
                    if 'true' in stmt_text.lower():
                        # "A says: 'B's statement is true'"
                        clauses.append([-stmt_var, other_var])   # ¬S_A ∨ S_other
                        clauses.append([stmt_var, -other_var])   # S_A ∨ ¬S_other
                    elif 'false' in stmt_text.lower():
                        # "A says: 'B's statement is false'"
                        clauses.append([-stmt_var, -other_var])  # ¬S_A ∨ ¬S_other
                        clauses.append([stmt_var, other_var])    # S_A ∨ S_other
        
        # Constraint 3: Global constraints from prompt
        if constraints:
            stmt_indices = list(stmt_vars.values())
            for const_type, const_val in constraints:
                if const_type == 'exactly' and stmt_indices:
                    # Encode exactly K statements are true
                    # Use SAT encoding for cardinality constraint
                    k = const_val
                    n = len(stmt_indices)
                    
                    # At least k
                    for combo in self._combinations(stmt_indices, n - k + 1):
                        clauses.append(combo)  # At least k true: ¬(n-k+1 false)
                    
                    # At most k
                    for combo in self._combinations([-v for v in stmt_indices], k + 1):
                        clauses.append(combo)  # At most k true: ¬(k+1 true)
        
        # Use T1 primitive: solve_sat
        sat_solution = solve_sat(clauses, var_counter - 1)
        
        # Use amino acid: detect_paradox
        paradox_result = detect_paradox(clauses)
        
        # Use amino acid: check_entailment for specific conclusions
        # Check if we can deduce specific agent types from the constraints
        deduced_agents = set()
        if sat_solution:
            for agent in agents:
                agent_var = agent_type_vars[agent]
                # Check if agent_var must be true in all models
                # Create clause for ¬agent_var and check if premises entail agent_var
                conclusion_clause = [agent_var]
                entailment = check_entailment(clauses, conclusion_clause)
                if entailment:
                    deduced_agents.add(agent)
        
        # Use T1 primitive: modus_ponens to derive logical consequences
        # Convert to implication form for modus_ponens
        premises = []
        facts = set()
        
        # Simple encoding: if we have T_A ↔ S, add T_A → S and S → T_A
        for agent in agents:
            agent_statements = [(a, s) for (a, s) in statements if a == agent]
            for (stmt_agent, stmt_text) in agent_statements:
                if truth_policies.get(agent) == "always_truthful":
                    premises.append((f"T_{agent}", f"S_{stmt_agent}_{hash(stmt_text)}"))
                    premises.append((f"S_{stmt_agent}_{hash(stmt_text)}", f"T_{agent}"))
                elif truth_policies.get(agent) == "always_lying":
                    premises.append((f"T_{agent}", f"not_S_{stmt_agent}_{hash(stmt_text)}"))
                    premises.append((f"not_S_{stmt_agent}_{hash(stmt_text)}", f"T_{agent}"))
        
        # Use T1 primitive: track_beliefs
        # Model agents as believing their own statements if they're truthful
        observations = []
        for agent in agents:
            agent_statements = [(a, s) for (a, s) in statements if a == agent]
            for (stmt_agent, stmt_text) in agent_statements:
                if truth_policies.get(agent) == "always_truthful":
                    observations.append((agent, f"S_{stmt_agent}_{hash(stmt_text)}", True))
                elif truth_policies.get(agent) == "always_lying":
                    observations.append((agent, f"S_{stmt_agent}_{hash(stmt_text)}", False))
        
        beliefs = track_beliefs(agents, observations)
        
        # Use T1 primitive: confidence_from_agreement
        # Generate confidence from multiple reasoning approaches
        confidence_scores = []
        
        # Score 1: SAT solution existence
        confidence_scores.append(1.0 if sat_solution else 0.0)
        
        # Score 2: Paradox detection (no paradox is good)
        confidence_scores.append(0.0 if paradox_result else 1.0)
        
        # Score 3: Unique solution check using constraint amino acid
        # Convert to CSP for uniqueness check
        variables = {}
        domains = {}
        csp_constraints = []
        
        for agent in agents:
            variables[agent] = f"T_{agent}"
            domains[f"T_{agent}"] = ["truthful", "lying"]
        
        for (agent, stmt_text) in statements:
            variables[f"S_{agent}_{hash(stmt_text)}"] = f"S_{agent}_{hash(stmt_text)}"
            domains[f"S_{agent}_{hash(stmt_text)}"] = [True, False]
        
        # Add policy constraints
        for agent, policy in truth_policies.items():
            if policy == "always_truthful":
                agent_statements = [(a, s) for (a, s) in statements if a == agent]
                for (stmt_agent, stmt_text) in agent_statements:
                    def make_truthful_constraint(agt, stmt):
                        def constraint(values):
                            t_val = values[f"T_{agt}"]
                            s_val = values[f"S_{stmt_agent}_{hash(stmt)}"]
                            return (t_val == "truthful") == s_val
                        return constraint
                    csp_constraints.append(([f"T_{agent}", f"S_{stmt_agent}_{hash(stmt_text)}"], 
                                           make_truthful_constraint(agent, stmt_text)))
            elif policy == "always_lying":
                agent_statements = [(a, s) for (a, s) in statements if a == agent]
                for (stmt_agent, stmt_text) in agent_statements:
                    def make_lying_constraint(agt, stmt):
                        def constraint(values):
                            t_val = values[f"T_{agt}"]
                            s_val = values[f"S_{stmt_agent}_{hash(stmt)}"]
                            return (t_val == "lying") == (not s_val)
                        return constraint
                    csp_constraints.append(([f"T_{agent}", f"S_{stmt_agent}_{hash(stmt_text)}"], 
                                           make_lying_constraint(agent, stmt_text)))
        
        unique_check = is_uniquely_solvable(domains, csp_constraints)
        confidence_scores.append(1.0 if unique_check else 0.5)
        
        confidence = confidence_from_agreement(confidence_scores)
        
        # Determine the answer based on question type
        computed_answer = ""
        question = structure["question"].lower()
        
        if sat_solution:
            # Extract specific answer based on question
            if "who" in question:
                # Find agents with specific properties
                if "truth" in question or "honest" in question:
                    truthful_agents = []
                    for agent in agents:
                        agent_var = agent_type_vars[agent]
                        if agent_var in sat_solution and sat_solution[agent_var]:
                            truthful_agents.append(agent)
                    if truthful_agents:
                        computed_answer = truthful_agents[0]
                elif "lie" in question or "liar" in question:
                    lying_agents = []
                    for agent in agents:
                        agent_var = agent_type_vars[agent]
                        if agent_var in sat_solution and not sat_solution[agent_var]:
                            lying_agents.append(agent)
                    if lying_agents:
                        computed_answer = lying_agents[0]
            elif "what" in question and "statement" in question:
                # Find which statement is true/false
                true_statements = []
                for (agent, stmt), var in stmt_vars.items():
                    if var in sat_solution and sat_solution[var]:
                        true_statements.append(stmt)
                if true_statements:
                    computed_answer = true_statements[0]
        
        # Fallback if no specific answer found
        if not computed_answer:
            if sat_solution:
                # Summarize the solution
                summary_parts = []
                for agent in agents:
                    agent_var = agent_type_vars[agent]
                    if agent_var in sat_solution:
                        status = "truthful" if sat_solution[agent_var] else "lying"
                        summary_parts.append(f"{agent} is {status}")
                computed_answer = "; ".join(summary_parts)
            else:
                computed_answer = "Inconsistent puzzle"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"SAT solution: {sat_solution is not None}, Paradox: {paradox_result}, Unique: {unique_check}",
            "sat_solution": sat_solution,
            "deduced_agents": list(deduced_agents),
            "beliefs": beliefs
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(com