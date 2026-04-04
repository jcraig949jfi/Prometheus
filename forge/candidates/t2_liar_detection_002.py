import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    solve_sat,
    modus_ponens,
    track_beliefs,
    confidence_from_agreement,
    topological_sort,
    check_transitivity
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """distributed_systems x constraint_acids - liar_detection"""

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
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        agents = []
        statements = []  # (agent, statement_text)
        truth_policies = {}  # agent -> policy ("always truth", "always lie", "random")
        question = ""
        
        current_agent = None
        
        for line in lines:
            # Look for agent introductions
            agent_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:says|states|claims|asserts)', line)
            if agent_match:
                agent_name = agent_match.group(1)
                if agent_name not in agents:
                    agents.append(agent_name)
                current_agent = agent_name
                
                # Extract the statement
                statement_match = re.search(r'says|states|claims|asserts[:\s]+["\']?([^"\'.]+)', line)
                if statement_match:
                    statement = statement_match.group(1).strip()
                    if statement:
                        statements.append((agent_name, statement))
            
            # Look for truth policies
            policy_patterns = [
                (r'always tells the truth', 'truth'),
                (r'always lies', 'lie'),
                (r'randomly tells truth or lies', 'random'),
                (r'alternates', 'alternate')
            ]
            
            for pattern, policy in policy_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if current_agent:
                        truth_policies[current_agent] = policy
                    elif agents:
                        # Apply to all mentioned agents if no specific agent
                        for agent in agents:
                            truth_policies[agent] = policy
            
            # Look for question
            if line.endswith('?'):
                question = line
        
        # Extract propositional variables (capitalized words that appear in statements)
        variables = set()
        for _, statement in statements:
            words = re.findall(r'\b[A-Z][a-z]*\b', statement)
            variables.update(words)
        
        # Map statements to propositional logic
        prop_statements = []
        for agent, statement in statements:
            # Simple mapping: "X is true" -> X, "not X" -> ¬X
            if 'not' in statement.lower() or "isn't" in statement or "is false" in statement:
                # Find the variable being negated
                var_match = re.search(r'\b([A-Z][a-z]*)\b', statement)
                if var_match:
                    var = var_match.group(1)
                    prop_statements.append((agent, f"¬{var}"))
            else:
                # Positive statement
                var_match = re.search(r'\b([A-Z][a-z]*)\b', statement)
                if var_match:
                    var = var_match.group(1)
                    prop_statements.append((agent, var))
        
        return {
            "agents": agents,
            "statements": statements,
            "prop_statements": prop_statements,
            "truth_policies": truth_policies,
            "variables": list(variables),
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use distributed systems consensus approach to resolve liar puzzles."""
        agents = structure["agents"]
        prop_statements = structure["prop_statements"]
        truth_policies = structure["truth_policies"]
        variables = structure["variables"]
        question = structure["question"]
        
        # PHASE 1: Build agent communication graph (who talks about whom)
        edges = []
        for agent1, stmt1 in prop_statements:
            # Extract variable from statement
            var_match = re.search(r'([A-Z][a-z]*|¬[A-Z][a-z]*)', stmt1)
            if var_match:
                var = var_match.group(1).replace('¬', '')
                # Find agents who mention this variable
                for agent2, stmt2 in prop_statements:
                    if agent1 != agent2 and var in stmt2:
                        edges.append((agent1, agent2))
        
        # Use topological_sort to find ordering of agent statements
        # (critical for distributed consensus)
        agent_order = topological_sort(edges)
        if agent_order is None:
            # Graph has cycles, use alphabetical as fallback
            agent_order = sorted(agents)
        
        # PHASE 2: Encode as SAT problem using solve_sat
        # Variables: each proposition P, and each agent's statement truth value
        n_vars = len(variables)
        var_to_idx = {var: i+1 for i, var in enumerate(variables)}
        
        clauses = []
        
        # Add constraints based on truth policies
        for agent, policy in truth_policies.items():
            # Find this agent's statements
            agent_stmts = [stmt for a, stmt in prop_statements if a == agent]
            
            for stmt in agent_stmts:
                # Extract variable and polarity
                if stmt.startswith('¬'):
                    var = stmt[1:]
                    polarity = -1
                else:
                    var = stmt
                    polarity = 1
                
                if var in var_to_idx:
                    var_idx = var_to_idx[var]
                    
                    if policy == 'truth':
                        # Statement is true -> variable has stated polarity
                        clauses.append([var_idx * polarity])
                    elif policy == 'lie':
                        # Statement is false -> variable has opposite polarity
                        clauses.append([-var_idx * polarity])
                    elif policy == 'random':
                        # No constraint (random can be either)
                        pass
        
        # PHASE 3: Check for consistency using detect_paradox (amino acid)
        paradox_info = detect_paradox(clauses)
        
        # PHASE 4: Use modus_ponens to derive conclusions
        # Build implication rules from statements
        premises = []
        facts = set()
        
        for agent, stmt in prop_statements:
            if agent in truth_policies and truth_policies[agent] == 'truth':
                # Truth-teller's statements are facts
                if '¬' in stmt:
                    var = stmt[1:]
                    facts.add(f"not_{var}")
                else:
                    facts.add(stmt)
            elif agent in truth_policies and truth_policies[agent] == 'lie':
                # Liar's statements imply the opposite
                if '¬' in stmt:
                    var = stmt[1:]
                    premises.append((f"{agent}_says_not_{var}", var))
                else:
                    premises.append((f"{agent}_says_{stmt}", f"not_{stmt}"))
        
        derived_facts = modus_ponens(premises, facts)
        
        # PHASE 5: Use track_beliefs to model agent knowledge
        observations = []
        for agent, stmt in prop_statements:
            # Each agent observes their own statement
            truth_value = agent in truth_policies and truth_policies[agent] == 'truth'
            observations.append((agent, stmt, truth_value))
        
        agent_beliefs = track_beliefs(agents, observations)
        
        # PHASE 6: Determine answer using constraint solving (amino acid)
        # Build CSP: variables with domains {True, False}
        variables_domains = {var: [True, False] for var in variables}
        
        constraints = []
        for clause in clauses:
            if len(clause) == 1:
                var_idx = abs(clause[0])
                var_name = [v for v, idx in var_to_idx.items() if idx == var_idx][0]
                if clause[0] > 0:
                    # var must be True
                    constraints.append(([var_name], lambda v: v[0] == True))
                else:
                    # var must be False
                    constraints.append(([var_name], lambda v: v[0] == False))
        
        # Use solve_first to find a solution
        solution = solve_first(variables_domains, constraints)
        
        # Use is_uniquely_solvable to check if solution is unique
        unique = is_uniquely_solvable(variables_domains, constraints)
        
        # PHASE 7: Determine which agent is telling truth based on question
        computed_answer = ""
        
        if "who" in question.lower() and "truth" in question.lower():
            # Find truth-tellers
            truth_tellers = [agent for agent, policy in truth_policies.items() 
                           if policy == 'truth']
            
            if truth_tellers:
                if len(truth_tellers) == 1:
                    computed_answer = truth_tellers[0]
                else:
                    # Multiple truth-tellers, use confidence_from_agreement
                    # Build confidence scores based on agreement with solution
                    scores = []
                    for agent in truth_tellers:
                        agent_stmts = [stmt for a, stmt in prop_statements if a == agent]
                        agreement = 0
                        for stmt in agent_stmts:
                            if stmt.startswith('¬'):
                                var = stmt[1:]
                                expected = False
                            else:
                                var = stmt
                                expected = True
                            
                            if solution and var in solution:
                                if solution[var] == expected:
                                    agreement += 1
                        
                        scores.append(agreement / max(len(agent_stmts), 1))
                    
                    confidence = confidence_from_agreement(scores)
                    if confidence > 0.5 and scores:
                        best_idx = scores.index(max(scores))
                        computed_answer = truth_tellers[best_idx]
                    else:
                        computed_answer = truth_tellers[0]
            else:
                # No explicit truth-tellers, find consistent agents
                consistent_agents = []
                for agent in agents:
                    agent_stmts = [stmt for a, stmt in prop_statements if a == agent]
                    consistent = True
                    for stmt in agent_stmts:
                        if stmt.startswith('¬'):
                            var = stmt[1:]
                            expected = False
                        else:
                            var = stmt
                            expected = True
                        
                        if solution and var in solution:
                            if solution[var] != expected:
                                consistent = False
                                break
                    
                    if consistent:
                        consistent_agents.append(agent)
                
                if consistent_agents:
                    computed_answer = consistent_agents[0]
        
        elif "what" in question.lower() and "true" in question.lower():
            # Question about what proposition is true
            if solution:
                true_vars = [var for var, val in solution.items() if val == True]
                if true_vars:
                    computed_answer = true_vars[0]
        
        # Fallback if no answer determined
        if not computed_answer:
            if solution:
                # Use first true variable
                for var, val in solution.items():
                    if val == True:
                        computed_answer = var
                        break
            
            if not computed_answer and agents:
                computed_answer = agents[0]
            else:
                computed_answer = "unknown"
        
        # Use check_entailment to verify answer (amino acid)
        # Build clause for answer
        answer_clause = []
        if computed_answer in variables:
            answer_clause = [var_to_idx[computed_answer]]
        elif computed_answer in agents:
            # Check if agent's statements are entailed
            agent_stmts = [stmt for a, stmt in prop_statements if a == computed_answer]
            if agent_stmts:
                stmt = agent_stmts[0]
                if stmt.startswith('¬'):
                    var = stmt[1:]
                    if var in var_to_idx:
                        answer_clause = [-var_to_idx[var]]
                else:
                    if stmt in var_to_idx:
                        answer_clause = [var_to_idx[stmt]]
        
        if answer_clause:
            entailment = check_entailment(clauses, answer_clause)
        else:
            entailment = False
        
        return {
            "answer": computed_answer,
            "confidence": unique,  # Higher confidence if solution is unique
            "reasoning": f"Consensus analysis with {len(agents)} agents, paradox_detected={paradox_info}, unique_solution={unique}, entailment={entailment}",
            "solution": solution,
            "unique": unique,
            "entailment": entailment
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD similarity between reasoning text and candidate
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * (0.5 + 0.5 * confidence)
            
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
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0