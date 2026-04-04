import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_sat,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import solve, check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Auction theory x SAT solving - liar_detection"""

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
        """Parse the prompt to identify agents, statements, and truth policies."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        statements = []  # (agent, statement_text, polarity?)
        truth_policies = {}  # agent -> policy description
        question = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear as subjects)
        # Simple pattern: "X says", "Y claims", "Z states"
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:says|claims|states|asserts|tells)'
        for line in lines:
            matches = re.findall(agent_pattern, line)
            for match in matches:
                agents.add(match)

        # Extract truth policies (e.g., "always lies", "always tells the truth", "alternates")
        policy_keywords = {
            'always lies': 'liar',
            'always tells the truth': 'truthful',
            'alternates': 'alternating',
            'random': 'random',
            'never lies': 'truthful',
            'never tells the truth': 'liar'
        }
        for line in lines:
            for key, policy in policy_keywords.items():
                if key in line.lower():
                    # Find which agent this policy applies to
                    for agent in agents:
                        if agent.lower() in line.lower():
                            truth_policies[agent] = policy
                            break

        # Extract statements: agent "says" followed by quoted or unquoted content
        statement_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:says|claims|states|asserts|tells)\s+["“]?([^"“.]+)["”]?'
        for line in lines:
            matches = re.findall(statement_pattern, line)
            for agent, stmt in matches:
                statements.append((agent, stmt.strip()))

        # If no explicit policies found, infer from context (e.g., "knights and knaves")
        if not truth_policies and 'knights' in prompt.lower() and 'knaves' in prompt.lower():
            # Assume knights always tell truth, knaves always lie
            for agent in agents:
                if 'knight' in prompt.lower():
                    truth_policies[agent] = 'truthful'
                elif 'knave' in prompt.lower():
                    truth_policies[agent] = 'liar'

        return {
            "agents": list(agents),
            "statements": statements,
            "policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    # ========== PHASE 2: REASON ==========
    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use auction theory as scaffold: agents bid truth values, SAT finds equilibrium."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        question = structure["question"]

        # Step 1: Encode as SAT using auction theory metaphor
        # Each agent's truthfulness is a "bid" in a sealed-bid auction
        # The "auctioneer" (logic constraints) determines which bids are consistent
        # Nash equilibrium = assignment where no agent wants to change truth value given others

        # Create boolean variables: T_A = True if agent A tells truth
        var_map = {agent: i+1 for i, agent in enumerate(agents)}
        n_vars = len(agents)

        # Clauses based on policies and statements
        clauses = []

        # Policy constraints (hard constraints = auction rules)
        for agent, policy in policies.items():
            idx = var_map[agent]
            if policy == 'truthful':
                clauses.append([idx])  # T_A must be true
            elif policy == 'liar':
                clauses.append([-idx])  # T_A must be false
            elif policy == 'alternating':
                # For alternating, we need temporal info - treat as unknown for now
                # Will handle via consistency check later
                pass

        # Statement constraints (what agents say must match their truthfulness)
        # If agent A says "P", then T_A -> P and ¬T_A -> ¬P
        # Convert statements to propositional logic
        statement_clauses = self._encode_statements(agents, statements, var_map)
        clauses.extend(statement_clauses)

        # Step 2: Solve SAT (find consistent truth assignments)
        # This is the "auction outcome" - which bids are accepted
        sat_result = solve(clauses, n_vars)
        
        # Use T1 primitive: solve_sat as backup
        if sat_result is None:
            sat_result = solve_sat(clauses, n_vars)

        # Step 3: Compute belief dynamics using auction theory
        # In auctions, bidders update beliefs about others' valuations
        # Here, we update confidence about truth values based on consistency
        if sat_result:
            # Extract truth values from SAT solution
            truth_values = {agent: (sat_result[var_map[agent]] if var_map[agent] in sat_result else None)
                           for agent in agents}
            
            # Compute confidence as auction clearing price stability
            # Multiple satisfying assignments = low confidence (price uncertainty)
            # Unique solution = high confidence (clear equilibrium)
            uniqueness_check = is_uniquely_solvable(
                variables_domains={agent: [True, False] for agent in agents},
                constraints=self._constraints_from_clauses(clauses, var_map)
            )
            
            # Use T1 primitive: confidence_from_agreement
            # Simulate multiple "auction rounds" with different initial beliefs
            simulated_scores = []
            for _ in range(3):
                # Perturb initial beliefs slightly
                perturbed_clauses = clauses[:]
                if len(agents) > 0:
                    # Add a random preference (like different auction formats)
                    import random
                    agent = random.choice(agents)
                    idx = var_map[agent]
                    if random.random() > 0.5:
                        perturbed_clauses.append([idx])
                    else:
                        perturbed_clauses.append([-idx])
                
                # Check if still solvable
                perturbed_sat = solve(perturbed_clauses, n_vars)
                if perturbed_sat:
                    # Score based on agreement with original solution
                    agreement = sum(1 for a in agents 
                                  if var_map[a] in perturbed_sat and var_map[a] in sat_result
                                  and perturbed_sat[var_map[a]] == sat_result[var_map[a]])
                    simulated_scores.append(agreement / len(agents))
            
            confidence = confidence_from_agreement(simulated_scores) if simulated_scores else 0.5
            
            # Use T1 primitive: entropy of truth value distribution
            truth_probs = []
            for agent in agents:
                if truth_values[agent] is True:
                    truth_probs.append(0.9)  # High probability of truth
                elif truth_values[agent] is False:
                    truth_probs.append(0.1)  # Low probability of truth
                else:
                    truth_probs.append(0.5)  # Unknown
            
            info_entropy = entropy(truth_probs) if truth_probs else 1.0
            
            # Use T1 primitive: bayesian_update on confidence
            # Prior confidence = 0.5, likelihood = 1 - normalized entropy
            likelihood = 1.0 - (info_entropy / len(agents)) if len(agents) > 0 else 0.5
            updated_confidence = bayesian_update(0.5, likelihood)
            
            # Determine answer from question
            computed_answer = self._extract_answer_from_question(question, truth_values, agents, statements)
            
            return {
                "answer": computed_answer,
                "confidence": updated_confidence,
                "truth_values": truth_values,
                "is_unique": uniqueness_check if uniqueness_check is not None else False,
                "reasoning": f"SAT solution found with confidence {updated_confidence:.2f}"
            }
        else:
            # No consistent assignment - paradox detected
            paradox_check = detect_paradox(clauses)
            
            # Use entailment to see what must be true despite inconsistency
            if len(agents) > 0:
                # Try to prove something about the first agent
                test_clause = [var_map[agents[0]]]
                entailment = check_entailment(clauses, test_clause)
                
                if entailment:
                    computed_answer = f"{agents[0]} must be truthful"
                else:
                    computed_answer = "Inconsistent statements detected"
            else:
                computed_answer = "No consistent interpretation"
            
            return {
                "answer": computed_answer,
                "confidence": 0.3,
                "truth_values": {},
                "is_unique": False,
                "reasoning": "Paradox detected" if paradox_check else "No consistent assignment"
            }

    def _encode_statements(self, agents: List[str], statements: List[Tuple[str, str]], 
                          var_map: Dict[str, int]) -> List[List[int]]:
        """Convert natural language statements to propositional clauses."""
        clauses = []
        
        # Simple statement patterns
        for agent, stmt in statements:
            agent_idx = var_map[agent]
            
            # Pattern 1: "X is truthful/lying"
            if 'truthful' in stmt.lower() or 'tells the truth' in stmt.lower():
                # Agent says "X is truthful"
                # Find which agent X is
                for other in agents:
                    if other.lower() in stmt.lower() and other != agent:
                        other_idx = var_map[other]
                        # T_agent -> T_other AND ¬T_agent -> ¬T_other
                        clauses.append([-agent_idx, other_idx])      # ¬T_agent ∨ T_other
                        clauses.append([agent_idx, -other_idx])      # T_agent ∨ ¬T_other
                        break
            
            # Pattern 2: "I am truthful/lying"
            elif 'i am' in stmt.lower() or 'i\'m' in stmt.lower():
                if 'truthful' in stmt.lower() or 'telling the truth' in stmt.lower():
                    # Agent says "I am truthful"
                    # This creates a paradox if agent is liar
                    clauses.append([agent_idx])  # Must be true for consistency
                elif 'lying' in stmt.lower() or 'liar' in stmt.lower():
                    # Agent says "I am lying"
                    # This is the liar paradox
                    clauses.append([agent_idx, -agent_idx])  # Always true, doesn't constrain
            
            # Pattern 3: "X said Y"
            elif 'said' in stmt.lower() or 'claims' in stmt.lower():
                # Extract nested statement
                # For simplicity, treat as referring to truth value
                for other in agents:
                    if other.lower() in stmt.lower() and other != agent:
                        other_idx = var_map[other]
                        # Agent says "Other is truthful"
                        clauses.append([-agent_idx, other_idx])
                        clauses.append([agent_idx, -other_idx])
                        break
            
            # Pattern 4: Simple factual statement (e.g., "the sky is blue")
            # Treat as a proposition P that must be consistent
            else:
                # Create a new variable for the fact
                fact_var = len(var_map) + len(clauses) + 1
                # T_agent -> fact_var AND ¬T_agent -> ¬fact_var
                clauses.append([-agent_idx, fact_var])
                clauses.append([agent_idx, -fact_var])
        
        return clauses

    def _constraints_from_clauses(self, clauses: List[List[int]], 
                                 var_map: Dict[str, int]) -> List[Tuple[List[str], callable]]:
        """Convert SAT clauses to CSP constraints for uniqueness check."""
        constraints = []
        reverse_map = {v: k for k, v in var_map.items()}
        
        for clause in clauses:
            if not clause:
                continue
                
            # Convert clause to constraint function
            vars_in_clause = [reverse_map[abs(lit)] for lit in clause if abs(lit) in reverse_map]
            
            if not vars_in_clause:
                continue
                
            def make_constraint(clause_vars, clause_lits):
                def constraint(assignment):
                    # A clause is satisfied if at least one literal is true
                    for var, lit in zip(clause_vars, clause_lits):
                        if var in assignment:
                            # Positive literal: variable must be True
                            # Negative literal: variable must be False
                            if lit > 0:
                                if assignment[var] == True:
                                    return True
                            else:
                                if assignment[var] == False:
                                    return True
                    return False
                return constraint
            
            # Extract literals for these specific variables
            clause_lits = []
            clause_vars = []
            for lit in clause:
                var_name = reverse_map.get(abs(lit))
                if var_name:
                    clause_vars.append(var_name)
                    clause_lits.append(lit)
            
            if clause_vars:
                constraints.append((clause_vars, make_constraint(clause_vars, clause_lits)))
        
        return constraints

    def _extract_answer_from_question(self, question: str, truth_values: Dict[str, bool],
                                     agents: List[str], statements: List[Tuple[str, str]]) -> str:
        """Determine what the answer should be based on the question."""
        question_lower = question.lower()
        
        # Common question patterns
        if 'who' in question_lower and 'truthful' in question_lower:
            # "Who is telling the truth?"
            truthful_agents = [agent for agent, val in truth_values.items() if val is True]
            if truthful_agents:
                return truthful_agents[0]  # Return first truthful agent
            else:
                return "No one is truthful"
        
        elif 'who' in question_lower and 'lying' in question_lower:
            # "Who is lying?"
            lying_agents = [agent for agent, val in truth_values.items() if val is False]
            if lying_agents:
                return lying_agents[0]
            else:
                return "No one is lying"
        
        elif 'what' in question_lower and 'statement' in question_lower:
            # "What statement is true?"
            # Find a statement made by a truthful agent
            for agent, stmt in statements:
                if truth_values.get(agent) is True:
                    return stmt
            return "No statement is verifiably true"
        
        elif 'paradox' in question_lower:
            # "Is there a paradox?"
            if any(val is None for val in truth_values.values()):
                return "Yes, paradoxical statements detected"
            else:
                return "No paradox"
        
        # Default: return the truth value of the first agent
        if agents:
            first_agent = agents[0]
            val = truth_values.get(first_agent)
            if val is True:
                return f"{first_agent} is truthful"
            elif val is False:
                return f"{first_agent} is lying"
            else:
                return f"{first_agent}'s truth value is indeterminate"
        
        return "Cannot determine answer from available information"

    # ========== PHASE 3: SCORE ==========
    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
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
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if len(scores) == 1:
            min_score = max_score = scores[0]
        else:
            min_score = min(scores)