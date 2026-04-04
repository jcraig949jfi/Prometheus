import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    track_beliefs,
    modus_ponens
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Information theory x SAT solving - liar_detection"""

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

    # ========== PHASE 1: EXTRACT ==========
    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt to extract agents, statements, truth policies, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        statements = []
        truth_policies = {}
        question = lines[-1] if lines else ""

        # Find agent names (capitalized words, often followed by 'says' or 'is')
        for line in lines:
            # Look for patterns like "Alice says", "Bob is a liar"
            agent_matches = re.findall(r'\b([A-Z][a-z]+)\b', line)
            for agent in agent_matches:
                if agent.lower() in ['the', 'what', 'who', 'which', 'how']:
                    continue
                agents.add(agent)

            # Extract truth policies
            if 'always tells the truth' in line.lower() or 'truth-teller' in line.lower():
                for agent in agent_matches:
                    if agent in agents:
                        truth_policies[agent] = 'truth'
            elif 'always lies' in line.lower() or 'liar' in line.lower():
                for agent in agent_matches:
                    if agent in agents:
                        truth_policies[agent] = 'lie'
            elif 'random' in line.lower() or 'sometimes' in line.lower():
                for agent in agent_matches:
                    if agent in agents:
                        truth_policies[agent] = 'random'

            # Extract statements (quoted or after 'says')
            if 'says' in line.lower():
                parts = line.split('says', 1)
                if len(parts) > 1:
                    speaker = parts[0].strip()
                    if speaker in agents:
                        statement = parts[1].strip().strip('"\'')
                        if statement:
                            statements.append((speaker, statement))

        # If no explicit policies, infer from statements about truthfulness
        for agent in agents:
            if agent not in truth_policies:
                # Check if any statement mentions this agent's truthfulness
                for speaker, stmt in statements:
                    if agent in stmt and ('truth' in stmt.lower() or 'lie' in stmt.lower()):
                        if 'truth' in stmt.lower():
                            truth_policies[agent] = 'truth'
                        elif 'lie' in stmt.lower():
                            truth_policies[agent] = 'lie'

        return {
            "agents": list(agents),
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    # ========== PHASE 2: REASON ==========
    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use information-theoretic SAT solving to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        question = structure["question"]

        # Step 1: Encode as SAT using information-theoretic constraints
        # Each agent has a truth variable T_i (True if truth-teller, False if liar)
        # Random agents are modeled as unknown variables with maximum entropy
        var_map = {agent: i+1 for i, agent in enumerate(agents)}
        n_vars = len(agents)
        clauses = []

        # Add constraints from truth policies
        for agent, policy in truth_policies.items():
            idx = var_map[agent]
            if policy == 'truth':
                clauses.append([idx])  # T_i must be true
            elif policy == 'lie':
                clauses.append([-idx])  # T_i must be false
            # 'random' adds no constraint (max entropy)

        # Add constraints from statements
        # For each statement "A says S", encode: T_A → S and ¬T_A → ¬S
        for speaker, stmt in statements:
            speaker_idx = var_map[speaker]
            
            # Parse statement for references to other agents' truth values
            # Simple pattern: "X is a truth-teller" or "X lies"
            mentioned_agents = []
            for agent in agents:
                if agent in stmt and agent != speaker:
                    mentioned_agents.append(agent)
            
            if mentioned_agents:
                # Handle statements about other agents' truthfulness
                for mentioned in mentioned_agents:
                    mentioned_idx = var_map[mentioned]
                    if 'truth' in stmt.lower() or 'truth-teller' in stmt.lower():
                        # "X is a truth-teller" means T_X
                        clauses.append([-speaker_idx, mentioned_idx])      # T_speaker → T_mentioned
                        clauses.append([speaker_idx, -mentioned_idx])      # ¬T_speaker → ¬T_mentioned
                    elif 'lie' in stmt.lower() or 'liar' in stmt.lower():
                        # "X is a liar" means ¬T_X
                        clauses.append([-speaker_idx, -mentioned_idx])     # T_speaker → ¬T_mentioned
                        clauses.append([speaker_idx, mentioned_idx])       # ¬T_speaker → T_mentioned
            else:
                # Self-referential or factual statements
                # For simplicity, treat as tautology if no agent mentioned
                pass

        # Step 2: Use SAT solving to find consistent assignments
        sat_result = solve_sat(clauses, n_vars)
        
        # Step 3: Use amino acid to detect paradox
        paradox_info = detect_paradox(clauses)
        
        # Step 4: Compute information-theoretic measures
        if sat_result:
            # Extract probabilities from SAT solutions (enumerate if small)
            all_solutions = self._enumerate_solutions(clauses, n_vars, limit=100)
            if all_solutions:
                # Compute probability each agent is truth-teller
                probs = []
                for agent in agents:
                    idx = var_map[agent]
                    count_true = sum(1 for sol in all_solutions if sol.get(idx, False))
                    prob = count_true / len(all_solutions)
                    probs.append(prob)
                
                # Compute entropy of the solution space
                sol_entropy = entropy(probs) if probs else 1.0
                
                # Use confidence_from_agreement on multiple scoring methods
                scores = []
                # Method 1: Probability-based
                scores.append(max(probs) if probs else 0.5)
                # Method 2: Entropy-based (lower entropy = higher confidence)
                scores.append(1.0 - min(sol_entropy, 1.0))
                # Method 3: Paradox detection confidence
                scores.append(0.9 if paradox_info is None else 0.1)
                
                confidence = confidence_from_agreement(scores)
                
                # Determine answer based on question
                computed_answer = self._determine_answer(question, agents, all_solutions, truth_policies)
            else:
                computed_answer = "paradox"
                confidence = 0.8
        else:
            computed_answer = "paradox"
            confidence = 0.9

        # Step 5: Use track_beliefs to model agent knowledge (if applicable)
        if statements:
            agent_list = list(agents)
            observations = []
            for speaker, stmt in statements:
                # Convert statement to boolean fact if possible
                fact = f"{speaker}_says_{hash(stmt) % 1000}"
                observations.append((speaker, fact, True))
            
            belief_state = track_beliefs(agent_list, observations)
            # Use belief state to refine answer if needed
            if computed_answer == "paradox" and belief_state:
                # Check if any agent believes contradictory facts
                for agent, facts in belief_state.items():
                    if len(facts) > 1:
                        # Try to resolve using modus_ponens
                        premises = []
                        for fact in facts:
                            # Create simple implication for demonstration
                            premises.append((f"{agent}_knows", fact))
                        
                        derived = modus_ponens(premises, {f"{agent}_knows"})
                        if derived:
                            computed_answer = f"{agent}_contradiction"
                            break

        # Step 6: Use constraint solving as alternative approach
        if computed_answer == "paradox" or confidence < 0.6:
            # Try CSP formulation
            variables = {agent: [True, False] for agent in agents}
            constraints = []
            
            for clause in clauses:
                def make_constraint(clause_vars, clause_lits):
                    def constraint(assignment):
                        for var, lit in zip(clause_vars, clause_lits):
                            if lit > 0 and not assignment[var]:
                                return False
                            if lit < 0 and assignment[var]:
                                return False
                        return True
                    return constraint
                
                clause_vars = [agents[abs(lit)-1] for lit in clause]
                constraints.append((clause_vars, make_constraint(clause_vars, clause)))
            
            csp_result = solve_first(variables, constraints)
            if csp_result:
                # Check uniqueness
                unique = is_uniquely_solvable(variables, constraints)
                if unique:
                    confidence = bayesian_update(confidence, 0.8)
                    # Extract answer from CSP solution
                    computed_answer = self._answer_from_csp(question, csp_result, truth_policies)

        return {
            "answer": str(computed_answer),
            "confidence": float(confidence),
            "reasoning": f"SAT solutions: {sat_result is not None}, Paradox: {paradox_info}, Confidence: {confidence:.2f}",
            "agents": agents,
            "policies": truth_policies
        }

    def _enumerate_solutions(self, clauses: List[List[int]], n_vars: int, limit: int = 100) -> List[Dict[int, bool]]:
        """Brute-force enumerate SAT solutions up to limit."""
        solutions = []
        # Try all 2^n assignments (for small n)
        if n_vars <= 8:
            for i in range(2**n_vars):
                assignment = {}
                for j in range(n_vars):
                    var = j + 1
                    assignment[var] = bool((i >> j) & 1)
                
                # Check if assignment satisfies all clauses
                satisfied = True
                for clause in clauses:
                    clause_ok = False
                    for lit in clause:
                        var = abs(lit)
                        val = assignment.get(var, False)
                        if (lit > 0 and val) or (lit < 0 and not val):
                            clause_ok = True
                            break
                    if not clause_ok:
                        satisfied = False
                        break
                
                if satisfied:
                    solutions.append(assignment)
                    if len(solutions) >= limit:
                        break
        return solutions

    def _determine_answer(self, question: str, agents: List[str], 
                         solutions: List[Dict[int, bool]], 
                         policies: Dict[str, str]) -> str:
        """Extract answer from question and solution space."""
        question_lower = question.lower()
        
        # Check for questions about specific agents
        for agent in agents:
            if agent.lower() in question_lower:
                # Count how many solutions have this agent as truth-teller
                agent_solutions = [s for s in solutions if s.get(agents.index(agent)+1, False)]
                if len(agent_solutions) > len(solutions) / 2:
                    return f"{agent} is truth-teller"
                else:
                    return f"{agent} is liar"
        
        # Check for "who" questions
        if 'who' in question_lower:
            # Find agent with most consistent truth value across solutions
            agent_consistency = {}
            for agent in agents:
                idx = agents.index(agent) + 1
                true_count = sum(1 for s in solutions if s.get(idx, False))
                consistency = max(true_count, len(solutions) - true_count) / len(solutions)
                agent_consistency[agent] = consistency
            
            if agent_consistency:
                most_consistent = max(agent_consistency.items(), key=lambda x: x[1])
                return most_consistent[0]
        
        # Default: return the first agent with known policy
        for agent, policy in policies.items():
            if policy in ['truth', 'lie']:
                return f"{agent} is {policy}"
        
        return "unknown"

    def _answer_from_csp(self, question: str, csp_solution: Dict[str, bool],
                        policies: Dict[str, str]) -> str:
        """Extract answer from CSP solution."""
        # Find agents with determined truth values
        determined = []
        for agent, value in csp_solution.items():
            if value:
                determined.append(f"{agent} is truth-teller")
            else:
                determined.append(f"{agent} is liar")
        
        if determined:
            return determined[0]
        
        return "consistent assignment found"

    # ========== PHASE 3: SCORE ==========
    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust based on confidence
            confidence = reasoning_result.get("confidence", 0.5)
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

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

    # ========== PHASE 4: CALIBRATE ==========
    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract scores
        scores = [item["score"] for item in scored]
        
        # Normalize to [0, 1] range
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal
            for item in scored:
                item["score"] = 0.5
        
        # Apply softmax to emphasize differences
        exp_scores = [2.71828 ** item["score"] for item in scored]
        total = sum(exp_scores)
        
        if total > 0:
            for i, item in enumerate(scored):
                item["score"] = exp_scores[i] / total
        
        return scored