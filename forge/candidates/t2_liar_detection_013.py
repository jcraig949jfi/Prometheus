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
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Electromagnetism x SAT/Constraint Solving - Liar Detection"""

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
        """Extract agents, statements, truth policies, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []
        truth_policies = {}  # agent -> "always_truthful", "always_lying", "random"
        question = ""
        
        current_agent = None
        
        for line in lines:
            # Detect agent introductions
            agent_match = re.search(r'(\w+)\s+(?:is|says|claims)', line, re.IGNORECASE)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)
                current_agent = agent
            
            # Extract truth policies
            if "always tells the truth" in line.lower() and current_agent:
                truth_policies[current_agent] = "always_truthful"
            elif "always lies" in line.lower() and current_agent:
                truth_policies[current_agent] = "always_lying"
            elif "random" in line.lower() and current_agent:
                truth_policies[current_agent] = "random"
            
            # Extract statements (quoted or following "says")
            if current_agent and ("says" in line.lower() or "claims" in line.lower()):
                # Find content after "says" or in quotes
                says_match = re.search(r'says\s+"([^"]+)"', line, re.IGNORECASE)
                if says_match:
                    statement = says_match.group(1)
                    statements.append((current_agent, statement))
                else:
                    # Try to extract statement after colon or "that"
                    parts = re.split(r'says|claims|that', line, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        statement = parts[1].strip(' ":')
                        if statement:
                            statements.append((current_agent, statement))
            
            # Extract question (usually last line)
            if "?" in line and not question:
                question = line
        
        # Parse question to find what's being asked
        question_target = None
        if "who" in question.lower():
            question_target = "agent"
        elif "what" in question.lower():
            question_target = "statement"
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "question_target": question_target,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use electromagnetic field theory: agents as charged particles, 
        statements as field lines, truth values as potentials.
        Consistency checking as field superposition."""
        
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        
        # Convert to SAT problem: each agent's statement has a truth value
        # Agent's truth policy imposes constraints
        
        # Phase 1: Build propositional variables
        # var_map: (agent, statement_index) -> SAT variable number
        var_map = {}
        clauses = []
        next_var = 1
        
        # Create variables for each statement
        statement_vars = {}
        for i, (agent, stmt) in enumerate(statements):
            var_map[(agent, i)] = next_var
            statement_vars[i] = next_var
            next_var += 1
        
        # Add constraints based on truth policies
        for agent in agents:
            policy = truth_policies.get(agent, "unknown")
            
            # Get all statements by this agent
            agent_stmts = [i for i, (a, _) in enumerate(statements) if a == agent]
            
            if policy == "always_truthful":
                # All statements by this agent must be true
                for stmt_idx in agent_stmts:
                    var = statement_vars[stmt_idx]
                    clauses.append([var])  # var must be true
                    
            elif policy == "always_lying":
                # All statements by this agent must be false
                for stmt_idx in agent_stmts:
                    var = statement_vars[stmt_idx]
                    clauses.append([-var])  # var must be false
                    
            elif policy == "random":
                # No constraints from policy alone
                pass
        
        # Add logical constraints between statements
        # Parse statements for logical relationships
        for i, (agent, stmt) in enumerate(statements):
            stmt_lower = stmt.lower()
            
            # Check for negations
            if "not" in stmt_lower or "false" in stmt_lower or "lie" in stmt_lower:
                # This statement might be about another statement's truth value
                # Look for references to other agents' statements
                for j, (other_agent, other_stmt) in enumerate(statements):
                    if i != j and other_agent in stmt:
                        # Statement i says something about statement j
                        if "not" in stmt_lower or "false" in stmt_lower:
                            # "A says B is lying" -> (A_truthful ∧ ¬B) ∨ (¬A_truthful ∧ B)
                            # Simplified: A's statement truth = (A_truthful == B_false)
                            a_var = statement_vars[i]
                            b_var = statement_vars[j]
                            
                            # (a → ¬b) ∧ (¬a → b)
                            clauses.append([-a_var, -b_var])  # a → ¬b
                            clauses.append([a_var, b_var])    # ¬a → b
        
        # CRITICAL: Use amino acid to check consistency
        paradox_result = detect_paradox(clauses)
        
        # Use T1 primitive: solve_sat to find satisfying assignment
        sat_assignment = solve_sat(clauses, next_var - 1)
        
        # Use T1 primitive: entropy to measure uncertainty in possible assignments
        if sat_assignment:
            # Count true/false assignments for each statement
            truth_counts = {}
            for stmt_idx in statement_vars:
                var = statement_vars[stmt_idx]
                if sat_assignment.get(var, False):
                    truth_counts[stmt_idx] = truth_counts.get(stmt_idx, 0) + 1
            
            # Calculate entropy of truth distribution
            if truth_counts:
                total = sum(truth_counts.values())
                probs = [count/total for count in truth_counts.values()]
                uncertainty = entropy(probs)
            else:
                uncertainty = 1.0
        else:
            uncertainty = 0.0
        
        # Use amino acid: check entailment for specific conclusions
        # Build conclusion based on question
        computed_answer = None
        confidence = 0.5
        
        if structure["question_target"] == "agent":
            # Question asks about a specific agent
            # Try to deduce which agent is being referred to
            for agent in agents:
                # Check if we can entail something about this agent
                test_clause = []
                # Simple test: can we determine if agent is truthful?
                agent_stmts = [i for i, (a, _) in enumerate(statements) if a == agent]
                if agent_stmts:
                    # Test if first statement must be true
                    test_var = statement_vars[agent_stmts[0]]
                    entailment = check_entailment(clauses, [test_var])
                    if entailment:
                        computed_answer = agent
                        break
        
        # Fallback reasoning using T1 primitives if SAT fails
        if not computed_answer and sat_assignment:
            # Use modus_ponens to derive conclusions
            premises = []
            facts = set()
            
            for i, (agent, stmt) in enumerate(statements):
                var = statement_vars[i]
                if sat_assignment.get(var, False):
                    # Statement is true
                    # Convert to logical form
                    for other_agent in agents:
                        if other_agent in stmt and "not" in stmt.lower():
                            # "A says B is not truthful"
                            premises.append((f"{agent}_truthful", f"not_{other_agent}_truthful"))
            
            # Use track_beliefs to model agent knowledge
            observations = []
            for agent in agents:
                policy = truth_policies.get(agent, "unknown")
                if policy == "always_truthful":
                    observations.append((agent, "truthful", True))
                elif policy == "always_lying":
                    observations.append((agent, "truthful", False))
            
            if observations:
                belief_state = track_beliefs(agents, observations)
                # Find agent with consistent beliefs
                for agent in agents:
                    if agent in belief_state and "truthful" in belief_state[agent]:
                        computed_answer = agent
                        break
        
        # Final fallback: use constraint solving
        if not computed_answer:
            # Build CSP
            variables = [f"stmt_{i}" for i in range(len(statements))]
            domains = {v: [True, False] for v in variables}
            
            constraints = []
            for i, (agent, stmt) in enumerate(statements):
                policy = truth_policies.get(agent, "unknown")
                if policy == "always_truthful":
                    constraints.append(([f"stmt_{i}"], lambda x: x[0] == True))
                elif policy == "always_lying":
                    constraints.append(([f"stmt_{i}"], lambda x: x[0] == False))
            
            solution = solve_first(variables, domains, constraints)
            if solution:
                # Find which agent's statements are all consistent
                for agent in agents:
                    agent_stmts = [i for i, (a, _) in enumerate(statements) if a == agent]
                    if all(solution.get(f"stmt_{i}", False) for i in agent_stmts):
                        computed_answer = agent
                        break
        
        # Use T1 primitive: confidence_from_agreement
        if computed_answer:
            # Simulate multiple reasoning paths
            scores = []
            if sat_assignment:
                scores.append(0.8 if computed_answer in agents else 0.2)
            if uncertainty < 0.5:
                scores.append(0.7)
            if len(agents) > 0:
                scores.append(1.0 / len(agents))
            
            if scores:
                confidence = confidence_from_agreement(scores)
            else:
                confidence = 0.5
        
        # Default answer if still none
        if not computed_answer and agents:
            computed_answer = agents[0]
        
        return {
            "answer": computed_answer or "Unknown",
            "confidence": confidence,
            "uncertainty": uncertainty,
            "paradox_detected": paradox_result.get("is_paradox", False) if paradox_result else False,
            "sat_solution_exists": sat_assignment is not None
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
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
        
        # Simple normalization
        scores = [item["score"] for item in scored]
        if max(scores) > 0:
            max_score = max(scores)
            for item in scored:
                item["score"] = item["score"] / max_score
        
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