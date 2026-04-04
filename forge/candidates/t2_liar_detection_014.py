import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    solve_constraints,
    track_beliefs,
    modus_ponens,
    negate
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Decision theory x SAT/Constraint solving - liar_detection"""

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
        """Extract agents, statements, and truth-telling policies from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []
        policies = {}  # agent -> "truth-teller", "liar", or "random"
        question = lines[-1] if lines else ""
        
        # Extract agents (capitalized names)
        agent_pattern = r'\b([A-Z][a-z]+)\b'
        potential_agents = re.findall(agent_pattern, prompt)
        
        # Filter out common non-agent words
        non_agents = {'The', 'A', 'An', 'Which', 'What', 'Who', 'How', 'Many', 
                     'Some', 'All', 'One', 'Two', 'Three', 'Four', 'Five'}
        agents = [a for a in potential_agents if a not in non_agents]
        
        # Extract truth-telling policies
        for line in lines:
            line_lower = line.lower()
            for agent in agents:
                if agent.lower() in line_lower:
                    if 'always tells the truth' in line_lower or 'truth-teller' in line_lower:
                        policies[agent] = 'truth-teller'
                    elif 'always lies' in line_lower or 'liar' in line_lower:
                        policies[agent] = 'liar'
                    elif 'random' in line_lower or 'sometimes lies' in line_lower:
                        policies[agent] = 'random'
        
        # Extract statements (quoted text or sentences containing "says")
        statement_pattern = r'["\'“]([^"\'”]+)["\'”]'
        quoted = re.findall(statement_pattern, prompt)
        
        for line in lines:
            if 'says' in line.lower():
                # Extract the statement part after "says"
                parts = line.split('says', 1)
                if len(parts) > 1:
                    statement = parts[1].strip().strip('"\'')
                    if statement and not statement.endswith('?'):
                        statements.append(statement)
        
        statements.extend(quoted)
        statements = list(set(statements))  # Remove duplicates
        
        return {
            "agents": agents,
            "statements": statements,
            "policies": policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use decision theory framework to resolve liar puzzles."""
        agents = structure["agents"]
        policies = structure["policies"]
        statements = structure["statements"]
        question = structure["question"]
        
        # Decision theory: Model as strategic game where agents choose truth values
        # based on their type (truth-teller, liar, random)
        
        # Phase 1: Encode logical constraints using SAT
        clauses = []
        var_map = {}
        var_counter = 1
        
        # Create variables for each statement's truth value
        for stmt in statements:
            var_map[stmt] = var_counter
            var_counter += 1
        
        # Create variables for each agent's type consistency
        for agent in agents:
            var_map[f"{agent}_consistent"] = var_counter
            var_counter += 1
        
        # Encode truth-teller constraints: if agent is truth-teller, their statements are true
        for agent in agents:
            if policies.get(agent) == 'truth-teller':
                # Find statements made by this agent
                agent_stmts = []
                for stmt in statements:
                    # Check if this statement is attributed to agent
                    if agent.lower() in structure["raw"].lower():
                        # Find the sentence containing both agent and statement
                        sentences = structure["raw"].split('.')
                        for sent in sentences:
                            if agent.lower() in sent.lower() and stmt.lower() in sent.lower():
                                agent_stmts.append(stmt)
                                break
                
                # Encode: all agent's statements must be true
                for stmt in agent_stmts:
                    clauses.append([var_map[stmt]])  # Statement is true
        
        # Encode liar constraints: if agent is liar, their statements are false
        for agent in agents:
            if policies.get(agent) == 'liar':
                # Find statements made by this agent
                agent_stmts = []
                for stmt in statements:
                    sentences = structure["raw"].split('.')
                    for sent in sentences:
                        if agent.lower() in sent.lower() and stmt.lower() in sent.lower():
                            agent_stmts.append(stmt)
                            break
                
                # Encode: all agent's statements must be false
                for stmt in agent_stmts:
                    clauses.append([-var_map[stmt]])  # Statement is false
        
        # Encode logical relationships between statements
        # Look for statements about other statements or agents
        for stmt in statements:
            stmt_lower = stmt.lower()
            
            # Check for negation patterns
            if "not" in stmt_lower or "false" in stmt_lower or "lie" in stmt_lower:
                # Try to find what is being negated
                for other_stmt in statements:
                    if other_stmt != stmt and other_stmt.lower() in stmt_lower:
                        # This statement negates another statement
                        clauses.append([-var_map[stmt], -var_map[other_stmt]])  # Not both true
                        clauses.append([var_map[stmt], var_map[other_stmt]])    # Not both false
            
            # Check for equivalence patterns
            if "same as" in stmt_lower or "equivalent to" in stmt_lower:
                for other_stmt in statements:
                    if other_stmt != stmt and other_stmt.lower() in stmt_lower:
                        # This statement is equivalent to another
                        clauses.append([-var_map[stmt], var_map[other_stmt]])   # If stmt true, other true
                        clauses.append([var_map[stmt], -var_map[other_stmt]])   # If stmt false, other false
        
        # CRITICAL: Use amino acid to check for paradox
        paradox_result = detect_paradox(clauses)
        
        # CRITICAL: Use amino acid to check entailment for key statements
        # Find the most important statement (usually mentioned in question)
        key_statement = None
        for stmt in statements:
            if any(word in structure["question"].lower() for word in stmt.lower().split()[:3]):
                key_statement = stmt
                break
        
        entailment_result = None
        if key_statement and clauses:
            # Check if constraints entail the key statement
            entailment_result = check_entailment(clauses, [var_map[key_statement]])
        
        # CRITICAL: Use constraint solving to find consistent assignments
        # Convert SAT problem to CSP for solve_first
        csp_vars = {}
        csp_constraints = []
        
        for stmt in statements:
            csp_vars[stmt] = [True, False]  # Boolean domain
        
        # Convert clauses to CSP constraints
        for clause in clauses:
            if len(clause) == 1:
                var_idx = abs(clause[0])
                var_name = [k for k, v in var_map.items() if v == var_idx][0]
                if clause[0] > 0:
                    csp_constraints.append(([var_name], lambda x: x[0] == True))
                else:
                    csp_constraints.append(([var_name], lambda x: x[0] == False))
            elif len(clause) == 2:
                var1_idx = abs(clause[0])
                var2_idx = abs(clause[1])
                var1_name = [k for k, v in var_map.items() if v == var1_idx][0]
                var2_name = [k for k, v in var_map.items() if v == var2_idx][0]
                
                if clause[0] > 0 and clause[1] > 0:
                    csp_constraints.append(([var1_name, var2_name], lambda x: x[0] or x[1]))
                elif clause[0] > 0 and clause[1] < 0:
                    csp_constraints.append(([var1_name, var2_name], lambda x: x[0] or not x[1]))
                elif clause[0] < 0 and clause[1] > 0:
                    csp_constraints.append(([var1_name, var2_name], lambda x: not x[0] or x[1]))
                else:
                    csp_constraints.append(([var1_name, var2_name], lambda x: not x[0] or not x[1]))
        
        # CRITICAL: Use solve_first to find a solution
        solution = None
        if csp_vars and csp_constraints:
            solution = solve_first(csp_vars, csp_constraints)
        
        # CRITICAL: Use is_uniquely_solvable to check if solution is unique
        unique_solution = False
        if csp_vars and csp_constraints:
            unique_solution = is_uniquely_solvable(csp_vars, csp_constraints)
        
        # Decision theory: Compute expected truth values using Bayesian reasoning
        # Model each statement's probability of being true given agent types
        
        base_prior = 0.5  # Base rate for random statements
        
        statement_probs = {}
        for stmt in statements:
            # Find which agent made this statement
            making_agent = None
            for agent in agents:
                sentences = structure["raw"].split('.')
                for sent in sentences:
                    if agent.lower() in sent.lower() and stmt.lower() in sent.lower():
                        making_agent = agent
                        break
                if making_agent:
                    break
            
            if making_agent:
                agent_type = policies.get(making_agent, 'unknown')
                
                if agent_type == 'truth-teller':
                    likelihood = 1.0  # Truth-tellers always tell truth
                    false_positive = 0.0
                elif agent_type == 'liar':
                    likelihood = 0.0  # Liars always lie
                    false_positive = 1.0
                else:  # random or unknown
                    likelihood = 0.5
                    false_positive = 0.5
                
                # CRITICAL: Use bayesian_update
                posterior = bayesian_update(base_prior, likelihood, false_positive)
                statement_probs[stmt] = posterior
            else:
                statement_probs[stmt] = base_prior
        
        # CRITICAL: Use confidence_from_agreement on statement probabilities
        confidence = 0.5
        if statement_probs:
            prob_values = list(statement_probs.values())
            confidence = confidence_from_agreement(prob_values)
        
        # CRITICAL: Use track_beliefs to model agent knowledge states
        agent_beliefs = {}
        if agents:
            # Create simple observations based on solution
            observations = []
            if solution:
                for stmt, truth_val in solution.items():
                    if isinstance(stmt, str) and truth_val in [True, False]:
                        # Each agent observes the actual truth value
                        for agent in agents:
                            observations.append((agent, stmt, truth_val))
            
            if observations:
                agent_beliefs = track_beliefs(agents, observations)
        
        # Determine the answer based on decision theory analysis
        computed_answer = ""
        
        # Strategy 1: If paradox detected, answer indicates inconsistency
        if paradox_result and paradox_result.get("is_paradox", False):
            computed_answer = "paradox"
        # Strategy 2: If unique solution exists, extract key fact
        elif unique_solution and solution:
            # Find the statement most relevant to the question
            if key_statement and key_statement in solution:
                truth_val = solution[key_statement]
                computed_answer = f"{key_statement} is {truth_val}"
            else:
                # Use the first true statement as answer
                true_stmts = [stmt for stmt, val in solution.items() if val == True]
                if true_stmts:
                    computed_answer = f"{true_stmts[0]} is true"
                else:
                    computed_answer = "no statement is true"
        # Strategy 3: Use Bayesian posterior to determine most likely true statement
        elif statement_probs:
            # CRITICAL: Decision theory - choose statement with highest expected utility
            # Utility = probability of being true * relevance to question
            best_stmt = max(statement_probs.items(), key=lambda x: x[1])
            computed_answer = f"{best_stmt[0]} (probability: {best_stmt[1]:.2f})"
        # Strategy 4: Fallback to agent analysis
        elif agents:
            # Use modus_ponens on extracted implications
            premises = []
            for stmt in statements:
                # Create simple implications from statement patterns
                if "if" in stmt.lower() and "then" in stmt.lower():
                    parts = stmt.lower().split("then")
                    if len(parts) == 2:
                        antecedent = parts[0].replace("if", "").strip()
                        consequent = parts[1].strip()
                        premises.append((antecedent, consequent))
            
            facts = set()
            for agent, policy in policies.items():
                if policy == 'truth-teller':
                    facts.add(f"{agent} tells truth")
                elif policy == 'liar':
                    facts.add(f"{agent} lies")
            
            if premises:
                derived = modus_ponens(premises, facts)
                if derived:
                    computed_answer = list(derived)[0]
                else:
                    computed_answer = agents[0]  # Default to first agent
            else:
                computed_answer = agents[0]
        else:
            computed_answer = "cannot determine"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Paradox: {paradox_result}, Entailment: {entailment_result}, Unique: {unique_solution}",
            "statement_probs": statement_probs,
            "solution": solution
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: direct match with computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust score based on confidence
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