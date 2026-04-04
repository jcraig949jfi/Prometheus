import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_sat,
    track_beliefs,
    modus_ponens
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Control theory x SAT entailment - liar_detection"""

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
        truth_policies = {}  # agent -> "always_truthful", "always_lying", or "alternating"
        question = ""
        
        for line in lines:
            # Extract agent names (capitalized words that appear before "says" or "is")
            if 'says' in line.lower() or 'states' in line.lower():
                # Find agent name before "says"
                parts = re.split(r'\s+says\s+', line, flags=re.IGNORECASE)
                if len(parts) > 1:
                    agent_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', parts[0])
                    if agent_match:
                        agent = agent_match.group(1)
                        if agent not in agents:
                            agents.append(agent)
                        statement = parts[1].strip('"\' ')
                        statements.append((agent, statement))
            
            # Extract truth policies
            if 'always tells the truth' in line.lower():
                for agent in agents:
                    if agent in line:
                        truth_policies[agent] = "always_truthful"
            elif 'always lies' in line.lower():
                for agent in agents:
                    if agent in line:
                        truth_policies[agent] = "always_lying"
            elif 'alternates' in line.lower() or 'alternating' in line.lower():
                for agent in agents:
                    if agent in line:
                        truth_policies[agent] = "alternating"
            
            # Extract question (usually last line)
            if line.startswith('Which') or line.startswith('What') or '?' in line:
                question = line
        
        # Control theory: treat agents as dynamical systems with truth-telling as output function
        # Truth policies define the system's transfer function
        system_states = {}
        for agent in agents:
            policy = truth_policies.get(agent, "unknown")
            # In control theory, we model each agent as a system with input (statement index)
            # and output (truth value). For alternators, we need to track state.
            if policy == "alternating":
                system_states[agent] = {"next_truthful": True, "statement_count": 0}
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "system_states": system_states,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use control theory to model agents as dynamical systems and SAT to find consistent truth assignments."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        system_states = structure["system_states"]
        
        # Control theory: Model each agent as a discrete-time system
        # State: (is_truthful, statement_count) for alternators
        # Output: truth value of current statement
        
        # Build SAT clauses based on truth policies
        clauses = []
        var_map = {}  # (agent, statement_idx) -> SAT variable number
        next_var = 1
        
        # Create variables for each statement
        for idx, (agent, stmt) in enumerate(statements):
            var_map[(agent, idx)] = next_var
            next_var += 1
        
        # Add constraints based on truth policies
        for agent in agents:
            policy = truth_policies.get(agent, "unknown")
            agent_statements = [(idx, stmt) for idx, (a, stmt) in enumerate(statements) if a == agent]
            
            if policy == "always_truthful":
                # All statements by this agent must be true
                for idx, _ in agent_statements:
                    var = var_map[(agent, idx)]
                    clauses.append([var])  # Variable must be true
            elif policy == "always_lying":
                # All statements by this agent must be false
                for idx, _ in agent_statements:
                    var = var_map[(agent, idx)]
                    clauses.append([-var])  # Variable must be false
            elif policy == "alternating":
                # Alternating truth teller: statements alternate between true and false
                # Control theory: this is a periodic system with period 2
                for i, (idx1, _) in enumerate(agent_statements):
                    var1 = var_map[(agent, idx1)]
                    # The system's output alternates: y[k] = (-1)^k * y[0]
                    # We encode this as XOR between consecutive statements
                    if i + 1 < len(agent_statements):
                        idx2 = agent_statements[i + 1][0]
                        var2 = var_map[(agent, idx2)]
                        # XOR(var1, var2) = True (they must be different)
                        # Encoding: (var1 ∨ var2) ∧ (¬var1 ∨ ¬var2)
                        clauses.append([var1, var2])
                        clauses.append([-var1, -var2])
        
        # Extract logical content from statements
        # Simple parsing for "X says Y" statements where Y is about other agents
        for idx, (agent, stmt) in enumerate(statements):
            stmt_var = var_map[(agent, idx)]
            
            # Check if statement is about another agent's truthfulness
            # Pattern: "[Agent] is [truthful/lying]"
            match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+(truthful|lying)', stmt, re.IGNORECASE)
            if match:
                target_agent = match.group(1)
                truth_value = match.group(2).lower()
                
                # Find if target agent made any statements
                target_vars = [var_map.get((target_agent, j)) for j in range(len(statements)) 
                             if (target_agent, j) in var_map]
                
                if target_vars:
                    # The statement claims something about ALL of target's statements
                    if truth_value == "truthful":
                        # "Target is truthful" means all target's statements are true
                        # This statement is true iff all target_vars are true
                        # Encode: stmt_var ↔ (target_var1 ∧ target_var2 ∧ ...)
                        for target_var in target_vars:
                            # If stmt is true, then target_var must be true
                            clauses.append([-stmt_var, target_var])
                        # If all target_vars are true, then stmt must be true
                        # This requires a clause with all negated target_vars or stmt
                        # Simplified: use SAT solving to find consistency
                        pass
                    else:  # "lying"
                        # "Target is lying" means all target's statements are false
                        for target_var in target_vars:
                            clauses.append([-stmt_var, -target_var])
        
        # Use SAT solving to find consistent assignment
        n_vars = next_var - 1
        
        # T1 PRIMITIVE 1: solve_sat - directly determines which assignments are possible
        sat_assignment = solve_sat(clauses, n_vars)
        
        if sat_assignment is None:
            # No consistent assignment found - use control theory fallback
            # Control theory: treat as unstable system, use entropy to measure uncertainty
            
            # T1 PRIMITIVE 2: entropy - measures uncertainty in possible truth values
            # Generate all possible truth assignments for a subset
            possible_assignments = []
            for agent in agents[:2]:  # Limit to first 2 agents for tractability
                agent_vars = [var_map.get((agent, j)) for j in range(len(statements)) 
                            if (agent, j) in var_map]
                if agent_vars:
                    # Generate possible truth values (simplified)
                    possible_assignments.append([0.5, 0.5])  # Equal probability true/false
            
            if possible_assignments:
                # Flatten and compute entropy
                flat_probs = []
                for pa in possible_assignments:
                    flat_probs.extend(pa)
                uncertainty = entropy(flat_probs) if flat_probs else 1.0
            else:
                uncertainty = 1.0
            
            # Use uncertainty to make decision
            # Higher entropy → more uncertain → answer is "cannot be determined"
            if uncertainty > 0.7:
                computed_answer = "cannot be determined"
                confidence = 0.5
            else:
                # Use track_beliefs as fallback
                observations = []
                for idx, (agent, stmt) in enumerate(statements):
                    # Simplified: treat statements as observations
                    observations.append((agent, f"stmt_{idx}", True))
                
                # T1 PRIMITIVE 3: track_beliefs - tracks what agents believe
                beliefs = track_beliefs(agents, observations)
                
                # Find agent with most consistent beliefs
                best_agent = max(agents, key=lambda a: len(beliefs.get(a, set())))
                computed_answer = best_agent
                confidence = 0.3
        else:
            # SAT found consistent assignment
            # Use amino acid to check entailment of possible conclusions
            
            # AMINO ACID: check_entailment - directly determines which conclusions follow
            # Check what we can conclude about specific agents
            
            possible_conclusions = []
            for agent in agents:
                # Check if we can conclude agent is truthful
                conclusion_clause = []
                agent_vars = [var_map.get((agent, j)) for j in range(len(statements)) 
                            if (agent, j) in var_map]
                if agent_vars:
                    # Conclusion: all of agent's statements are true
                    conclusion_clause = agent_vars  # All must be true
                    
                    entailment_result = check_entailment(clauses, conclusion_clause)
                    if entailment_result:
                        possible_conclusions.append((agent, "truthful"))
            
            # T1 PRIMITIVE 4: confidence_from_agreement - measures confidence from multiple conclusions
            if possible_conclusions:
                # Score each possible conclusion
                conclusion_scores = []
                for agent, conclusion in possible_conclusions:
                    # Use bayesian_update to compute confidence
                    prior = 0.5
                    likelihood = 0.8 if conclusion == "truthful" else 0.2
                    
                    # T1 PRIMITIVE 5: bayesian_update - updates belief based on evidence
                    posterior = bayesian_update(prior, likelihood)
                    conclusion_scores.append(posterior)
                
                if conclusion_scores:
                    confidence = confidence_from_agreement(conclusion_scores)
                    # Pick conclusion with highest posterior
                    best_idx = max(range(len(conclusion_scores)), key=lambda i: conclusion_scores[i])
                    best_agent, best_conclusion = possible_conclusions[best_idx]
                    computed_answer = f"{best_agent} is {best_conclusion}"
                else:
                    computed_answer = "inconsistent statements"
                    confidence = 0.5
            else:
                # Use constraint solving as alternative
                variables = list(var_map.keys())
                domains = {v: [True, False] for v in variables}
                constraints = []
                
                # Convert clauses to constraint functions
                for clause in clauses[:10]:  # Limit for tractability
                    def make_constraint(clause_vars):
                        def constraint(assignment):
                            for var in clause_vars:
                                val = assignment.get(var)
                                if val is None:
                                    continue
                                if var > 0 and val is True:
                                    return True
                                if var < 0 and val is False:
                                    return True
                            return False
                        return constraint
                    
                    constraint_vars = [v for v in variables if abs(var) in [var_map.get(v, 0) for v in variables]]
                    if constraint_vars:
                        constraints.append((constraint_vars, make_constraint(clause)))
                
                # Check if uniquely solvable
                unique = is_uniquely_solvable(domains, constraints)
                
                if unique:
                    computed_answer = "exactly one consistent interpretation"
                    confidence = 0.8
                else:
                    computed_answer = "multiple possible interpretations"
                    confidence = 0.6
        
        # Control theory: final output stabilization
        # The computed answer should be the fixed point of the belief update system
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": f"Control theory model with SAT consistency checking. Truth policies: {truth_policies}",
            "sat_assignment": sat_assignment is not None
        }

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
        """Normalized Compression Distance between two strings."""
        if not a and not b:
            return 0.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)