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
    """quantum_mechanics x pysat_acids - liar_detection"""

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
        """Extract agents, statements, and truth-telling policies from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []
        policies = {}  # agent -> policy description
        question = lines[-1] if lines else ""
        
        # Extract capitalized names as potential agents
        agent_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b'
        all_names = re.findall(agent_pattern, prompt)
        
        # Look for policy descriptions
        policy_keywords = ['always tells the truth', 'always lies', 'alternates', 
                          'random', 'truth-teller', 'liar', 'knave', 'knight']
        
        for line in lines:
            # Find agents with policies
            for name in all_names:
                if name in line:
                    for keyword in policy_keywords:
                        if keyword in line.lower():
                            policies[name] = keyword
                            if name not in agents:
                                agents.append(name)
            
            # Extract statements (quoted or following "says")
            if '"' in line:
                quoted = re.findall(r'"([^"]*)"', line)
                statements.extend(quoted)
            elif 'says:' in line or 'says that' in line:
                parts = line.split('says:', 1) if 'says:' in line else line.split('says that', 1)
                if len(parts) > 1:
                    statement = parts[1].strip()
                    if statement:
                        statements.append(statement)
        
        # Extract logical relationships
        logical_ops = []
        for line in lines:
            if 'and' in line.lower() or 'or' in line.lower() or 'not' in line.lower():
                logical_ops.append(line)
        
        return {
            "agents": agents,
            "statements": statements,
            "policies": policies,
            "question": question,
            "logical_ops": logical_ops,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Quantum superposition of truth assignments with wavefunction collapse."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        question = structure["question"]
        
        if not agents or not statements:
            # Fallback: use entropy on statement patterns
            statement_entropy = self._compute_statement_entropy(statements)
            if statement_entropy > 0.5:
                computed_answer = "Inconsistent"
            else:
                computed_answer = "Consistent"
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Fallback: entropy analysis",
                "quantum_state": None
            }
        
        # Quantum mechanics scaffold: treat each possible truth assignment as a basis state
        # The wavefunction is a superposition of all consistent assignments
        # Measurement (answer extraction) collapses to the most probable consistent state
        
        # Step 1: Encode as SAT problem (quantum basis states)
        sat_clauses, var_map = self._encode_as_sat(agents, statements, policies)
        
        if not sat_clauses:
            # Use modus ponens as fallback
            computed_answer = self._fallback_modus_ponens(agents, statements, policies)
            return {
                "answer": computed_answer,
                "confidence": 0.6,
                "reasoning": "Fallback: modus ponens",
                "quantum_state": None
            }
        
        # Step 2: Check for paradox (quantum interference)
        paradox_result = detect_paradox(sat_clauses)
        
        # Step 3: Find consistent assignments (measurement outcomes)
        sat_solution = solve_sat(sat_clauses, len(var_map))
        
        # Step 4: Quantum collapse to most probable answer
        if paradox_result and paradox_result.get("is_paradox", False):
            # Quantum interference leads to contradiction
            computed_answer = "Paradox"
            confidence = 0.9
        elif sat_solution is None:
            # No consistent assignment (collapses to null state)
            computed_answer = "No consistent assignment"
            confidence = 0.8
        else:
            # Collapse to specific truth values
            truth_values = {var_map[i]: sat_solution.get(i, False) 
                          for i in range(1, len(var_map) + 1)}
            
            # Use entropy to measure uncertainty in the quantum state
            truth_probs = [0.5] * len(truth_values)  # Prior uncertainty
            if sat_solution:
                # Update based on solution
                truth_probs = [0.8 if truth_values.get(var, False) else 0.2 
                             for var in var_map.values()]
            
            state_entropy = entropy(truth_probs)
            
            # Bayesian update of confidence based on entropy
            prior_conf = 0.7
            likelihood = 1.0 - min(state_entropy, 1.0)
            confidence = bayesian_update(prior_conf, likelihood, false_positive=0.1)
            
            # Determine which agent's statement is key
            key_agent = self._identify_key_agent(agents, truth_values, var_map)
            computed_answer = key_agent if key_agent else "Ambiguous"
        
        # Step 5: Check entailment for specific questions
        if "who" in question.lower() and computed_answer not in ["Paradox", "No consistent assignment"]:
            # Use check_entailment amino acid
            question_clauses = self._encode_question(question, var_map)
            if question_clauses and sat_clauses:
                entailment = check_entailment(sat_clauses, question_clauses)
                if entailment and entailment.get("entails", False):
                    # Entailment gives higher confidence
                    confidence = bayesian_update(confidence, 0.9, false_positive=0.05)
        
        # Step 6: Final confidence aggregation (quantum decoherence)
        confidence_scores = [confidence, 0.8 if sat_solution else 0.3, 0.7]
        final_confidence = confidence_from_agreement(confidence_scores)
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Quantum superposition collapsed to {computed_answer}",
            "quantum_state": {
                "has_solution": sat_solution is not None,
                "is_paradox": paradox_result.get("is_paradox", False) if paradox_result else False,
                "entropy": state_entropy if 'state_entropy' in locals() else 0.0
            }
        }

    def _encode_as_sat(self, agents: List[str], statements: List[str], 
                      policies: Dict[str, str]) -> Tuple[List[List[int]], Dict[int, str]]:
        """Encode the liar puzzle as SAT clauses."""
        var_map = {}
        var_idx = 1
        clauses = []
        
        # Create variables for agent truth-telling states
        for agent in agents:
            var_map[var_idx] = f"{agent}_truthful"
            var_idx += 1
        
        # Create variables for statement truth values
        for i, stmt in enumerate(statements):
            var_map[var_idx] = f"stmt_{i}_true"
            var_idx += 1
        
        # Policy constraints (quantum constraints on the state space)
        for agent, policy in policies.items():
            agent_var = [k for k, v in var_map.items() if v == f"{agent}_truthful"][0]
            
            if 'always tells the truth' in policy.lower() or 'truth-teller' in policy.lower():
                # Agent is always truthful
                clauses.append([agent_var])
            elif 'always lies' in policy.lower() or 'liar' in policy.lower():
                # Agent always lies
                clauses.append([-agent_var])
            elif 'alternates' in policy.lower():
                # Quantum superposition: could be either
                # Encode as no constraint (free variable)
                pass
        
        # Statement constraints
        # For simplicity, assume statements refer to other agents' truthfulness
        for i, stmt in enumerate(statements):
            stmt_var = [k for k, v in var_map.items() if v == f"stmt_{i}_true"][0]
            
            # Try to parse statement
            for agent in agents:
                if agent in stmt:
                    agent_var = [k for k, v in var_map.items() if v == f"{agent}_truthful"][0]
                    
                    if 'is lying' in stmt.lower() or 'lies' in stmt.lower():
                        # Statement claims agent is lying
                        # If speaker is truthful, then agent_var is false
                        # If speaker is lying, then agent_var is true
                        speaker = self._find_speaker(stmt, agents)
                        if speaker:
                            speaker_var = [k for k, v in var_map.items() 
                                         if v == f"{speaker}_truthful"][0]
                            
                            # Clause: (speaker_truthful → ¬agent_truthful) ∧ (¬speaker_truthful → agent_truthful)
                            # CNF: (¬speaker_var ∨ ¬agent_var) ∧ (speaker_var ∨ agent_var)
                            clauses.append([-speaker_var, -agent_var])
                            clauses.append([speaker_var, agent_var])
                            
                            # Link statement variable
                            clauses.append([-stmt_var, -speaker_var, -agent_var])
                            clauses.append([-stmt_var, speaker_var, agent_var])
                            clauses.append([stmt_var, -speaker_var, agent_var])
                            clauses.append([stmt_var, speaker_var, -agent_var])
        
        return clauses, var_map

    def _find_speaker(self, statement: str, agents: List[str]) -> str:
        """Find which agent made a statement."""
        # Simple heuristic: look for agent name before "says" or similar
        words = statement.lower().split()
        for i, word in enumerate(words):
            if word in ['says', 'said', 'claims', 'states'] and i > 0:
                potential = ' '.join(words[:i]).title()
                for agent in agents:
                    if agent.lower() == potential.lower():
                        return agent
        return ""

    def _compute_statement_entropy(self, statements: List[str]) -> float:
        """Compute entropy of statement patterns."""
        if not statements:
            return 0.0
        
        # Count keyword frequencies
        keywords = ['not', 'and', 'or', 'true', 'false', 'lie', 'truth']
        counts = []
        for stmt in statements:
            stmt_lower = stmt.lower()
            count = sum(1 for kw in keywords if kw in stmt_lower)
            counts.append(count)
        
        if not counts:
            return 0.0
        
        # Normalize to probabilities
        total = sum(counts)
        if total == 0:
            return 0.0
        
        probs = [c/total for c in counts]
        return entropy(probs)

    def _fallback_modus_ponens(self, agents: List[str], statements: List[str], 
                              policies: Dict[str, str]) -> str:
        """Fallback reasoning using modus ponens."""
        # Create simple implication rules
        premises = []
        facts = set()
        
        for agent, policy in policies.items():
            if 'truth' in policy.lower():
                facts.add(f"{agent}_truthful")
            elif 'lie' in policy.lower():
                facts.add(f"not_{agent}_truthful")
        
        # Add implications based on statements
        for stmt in statements:
            for agent in agents:
                if agent in stmt:
                    if 'is lying' in stmt.lower():
                        speaker = self._find_speaker(stmt, agents)
                        if speaker:
                            premises.append((f"{speaker}_truthful", f"not_{agent}_truthful"))
        
        # Apply modus ponens
        inferred = modus_ponens(premises, facts)
        
        # Track beliefs
        observations = []
        for agent in agents:
            if f"{agent}_truthful" in inferred:
                observations.append((agent, f"{agent}_truthful", True))
            elif f"not_{agent}_truthful" in inferred:
                observations.append((agent, f"{agent}_truthful", False))
        
        belief_state = track_beliefs(agents, observations)
        
        # Determine answer
        for agent in agents:
            if agent in belief_state:
                if f"{agent}_truthful" in belief_state[agent]:
                    return f"{agent} is truthful"
                elif any("not" in fact for fact in belief_state[agent]):
                    return f"{agent} is lying"
        
        return "Inconclusive"

    def _identify_key_agent(self, agents: List[str], truth_values: Dict[str, bool],
                           var_map: Dict[int, str]) -> str:
        """Identify the key agent from truth values."""
        # Find agent with most informative truth value
        agent_truths = {}
        for var_name, is_true in truth_values.items():
            for agent in agents:
                if var_name.startswith(f"{agent}_"):
                    agent_truths[agent] = is_true
        
        if not agent_truths:
            return ""
        
        # Return first agent with definitive truth value
        for agent, is_true in agent_truths.items():
            return agent
        
        return ""

    def _encode_question(self, question: str, var_map: Dict[int, str]) -> List[List[int]]:
        """Encode the question as a SAT clause."""
        clauses = []
        
        # Simple encoding for "who" questions
        if "who" in question.lower():
            # Look for agent names in question
            for var_idx, var_name in var_map.items():
                if "_truthful" in var_name and "who" in question.lower():
                    agent = var_name.replace("_truthful", "")
                    if agent.lower() in question.lower():
                        # Question asks about this agent
                        clauses.append([var_idx])
        
        return clauses

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # NCD similarity fallback
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
        """Calibrate scores using quantum-inspired normalization."""
        if not scored:
            return scored
        
        # Extract scores
        scores = [item["score"] for item in scored]
        
        # Quantum normalization: softmax with temperature
        max_score = max(scores) if scores else 1.0
        temperature = 0.5  # Quantum temperature parameter
        
        for item in scored:
            # Apply softmax-like normalization
            exp_score = 2.71828 ** (item["score"] / temperature)
            item["score"] = exp_score / (sum(2.71828 ** (s / temperature) for s in scores))
        
        return scored

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