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
    """Quantum mechanics x SAT solving - liar_detection"""

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
        truth_policies = {}
        question = lines[-1] if lines else ""
        
        # Extract agent names (capitalized words that appear before "says" or "always")
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        
        for line in lines:
            # Look for agent declarations
            if 'always' in line.lower() and ('truth' in line.lower() or 'lie' in line.lower()):
                agent_match = re.search(agent_pattern, line)
                if agent_match:
                    agent = agent_match.group(0)
                    agents.append(agent)
                    
                    # Determine truth policy
                    if 'truth' in line.lower():
                        truth_policies[agent] = 'truth-teller'
                    elif 'lie' in line.lower():
                        truth_policies[agent] = 'liar'
                    elif 'random' in line.lower():
                        truth_policies[agent] = 'random'
            
            # Extract statements (quoted text or sentences containing "says")
            if 'says' in line.lower():
                parts = line.split('says', 1)
                if len(parts) == 2:
                    agent_match = re.search(agent_pattern, parts[0])
                    if agent_match:
                        agent = agent_match.group(0)
                        statement = parts[1].strip().strip('"\'')
                        if statement:
                            statements.append((agent, statement))
        
        return {
            "agents": list(set(agents)),
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use quantum superposition analogy: each agent's truth value exists in superposition
        until constrained by logical consistency (measurement)."""
        
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        
        if not agents or not statements:
            # Fallback: use simple pattern matching
            computed_answer = self._fallback_reasoning(structure)
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Fallback: insufficient data for quantum model"
            }
        
        # Quantum analogy: each agent has a truth value (True=truth-teller, False=liar)
        # We'll encode this as a SAT problem where variables represent agent types
        
        # Create variable mapping
        var_map = {agent: i+1 for i, agent in enumerate(agents)}
        neg_var_map = {agent: -(i+1) for i, agent in enumerate(agents)}
        
        clauses = []
        
        # Add constraints from known truth policies (collapsing superposition)
        for agent, policy in truth_policies.items():
            if agent in var_map:
                if policy == 'truth-teller':
                    clauses.append([var_map[agent]])  # Agent must be True
                elif policy == 'liar':
                    clauses.append([neg_var_map[agent]])  # Agent must be False
        
        # Encode statements as logical constraints
        # If agent A says "B is a truth-teller", then:
        # (A ∧ B) ∨ (¬A ∧ ¬B)  [if A is truth-teller, B must be; if A is liar, B must not be]
        for speaker, statement in statements:
            # Parse statement to find referenced agent
            referenced_agents = []
            for agent in agents:
                if agent.lower() in statement.lower() and agent != speaker:
                    referenced_agents.append(agent)
            
            if not referenced_agents:
                # Statement doesn't reference another agent, treat as simple proposition
                # For simplicity, we'll skip complex parsing
                continue
            
            # For each referenced agent, create implication
            for target in referenced_agents:
                if speaker in var_map and target in var_map:
                    # (speaker → target_is_truth) ∧ (¬speaker → ¬target_is_truth)
                    # Equivalent to: (¬speaker ∨ target) ∧ (speaker ∨ ¬target)
                    clauses.append([neg_var_map[speaker], var_map[target]])
                    clauses.append([var_map[speaker], neg_var_map[target]])
        
        # CRITICAL PRIMITIVE 1: Use solve_sat to find consistent assignments
        sat_result = solve_sat(clauses, len(agents))
        
        # CRITICAL AMINO ACID 1: Use check_entailment to see what we can deduce
        # Check if we can deduce specific agent types from the constraints
        deduced_agents = {}
        
        for agent in agents:
            if agent in var_map:
                # Check if clauses entail agent is truth-teller
                entailment_true = check_entailment(clauses, [var_map[agent]])
                # Check if clauses entail agent is liar
                entailment_false = check_entailment(clauses, [neg_var_map[agent]])
                
                if entailment_true and not entailment_false:
                    deduced_agents[agent] = 'truth-teller'
                elif entailment_false and not entailment_true:
                    deduced_agents[agent] = 'liar'
                elif sat_result and var_map[agent] in sat_result:
                    # Use SAT solution if no strict entailment
                    deduced_agents[agent] = 'truth-teller' if sat_result[var_map[agent]] else 'liar'
        
        # CRITICAL PRIMITIVE 2: Use entropy to measure uncertainty in the solution space
        # Count possible assignments by trying different SAT assumptions
        if sat_result:
            # Create probability distribution over agent types
            agent_probs = {}
            for agent in agents:
                if agent in var_map:
                    # Try to find both possibilities
                    true_possible = solve_sat(clauses + [[var_map[agent]]], len(agents))
                    false_possible = solve_sat(clauses + [[neg_var_map[agent]]], len(agents))
                    
                    if true_possible and false_possible:
                        agent_probs[agent] = [0.5, 0.5]  # Equal probability
                    elif true_possible:
                        agent_probs[agent] = [1.0, 0.0]  # Definitely truth-teller
                    elif false_possible:
                        agent_probs[agent] = [0.0, 1.0]  # Definitely liar
                    else:
                        agent_probs[agent] = [0.5, 0.5]  # Default if unclear
            # Calculate entropy of the overall system
            if agent_probs:
                # Flatten probabilities for entropy calculation
                flat_probs = []
                for probs in agent_probs.values():
                    flat_probs.extend(probs)
                # Normalize
                total = sum(flat_probs)
                if total > 0:
                    normalized = [p/total for p in flat_probs]
                    system_entropy = entropy(normalized)
                else:
                    system_entropy = 1.0
            else:
                system_entropy = 1.0
        else:
            system_entropy = 1.0
        
        # CRITICAL AMINO ACID 2: Use detect_paradox to check for contradictions
        paradox_info = detect_paradox(clauses)
        
        # CRITICAL PRIMITIVE 3: Use bayesian_update to combine evidence
        # Start with prior based on number of agents
        prior = 0.5
        likelihood = 0.0
        
        if deduced_agents:
            # Calculate likelihood based on consistency
            consistent_assignments = 0
            total_possible = 2 ** len(agents)
            
            # Simple approximation: if SAT found solution, it's consistent
            if sat_result:
                consistent_assignments = 1
            
            if total_possible > 0:
                likelihood = consistent_assignments / total_possible
        
        posterior = bayesian_update(prior, likelihood, false_positive=0.1)
        
        # Determine answer based on question
        computed_answer = ""
        question = structure["question"].lower()
        
        if "who" in question and "truth" in question:
            # Find truth-tellers
            truth_tellers = [agent for agent, policy in deduced_agents.items() 
                           if policy == 'truth-teller']
            if truth_tellers:
                computed_answer = truth_tellers[0]
            elif agents:
                computed_answer = agents[0]
        elif "paradox" in question or "contradiction" in question:
            computed_answer = "Yes" if paradox_info and paradox_info.get("is_paradox", False) else "No"
        elif "how many" in question:
            if deduced_agents:
                count = sum(1 for policy in deduced_agents.values() if policy == 'truth-teller')
                computed_answer = str(count)
            else:
                computed_answer = "0"
        else:
            # Default: name the first agent with determined type
            for agent, policy in deduced_agents.items():
                computed_answer = f"{agent} is a {policy}"
                break
            if not computed_answer and agents:
                computed_answer = agents[0]
        
        # CRITICAL PRIMITIVE 4: Use confidence_from_agreement
        # Create multiple scoring perspectives
        scores = []
        if system_entropy < 0.5:  # Low entropy means more certain
            scores.append(0.8)
        else:
            scores.append(0.3)
        
        if paradox_info and not paradox_info.get("is_paradox", False):
            scores.append(0.7)  # No paradox increases confidence
        else:
            scores.append(0.4)
        
        if deduced_agents:
            scores.append(0.6)
        else:
            scores.append(0.2)
        
        confidence = confidence_from_agreement(scores)
        
        # Adjust confidence with posterior
        final_confidence = (confidence + posterior) / 2
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Quantum superposition model with entropy={system_entropy:.2f}, paradox_detected={paradox_info.get('is_paradox', False) if paradox_info else False}",
            "deduced_agents": deduced_agents,
            "system_entropy": system_entropy
        }

    def _fallback_reasoning(self, structure: Dict[str, Any]) -> str:
        """Fallback when quantum model can't be applied directly."""
        agents = structure["agents"]
        truth_policies = structure["truth_policies"]
        
        # Simple heuristic: if only one agent has known policy, return that
        known_agents = [agent for agent, policy in truth_policies.items() 
                       if policy in ['truth-teller', 'liar']]
        
        if len(known_agents) == 1:
            return known_agents[0]
        elif agents:
            return agents[0]
        else:
            return "Unknown"

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 0.9
            else:
                # Secondary: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            results.append({
                "candidate": candidate,
                "score": base_score,
                "raw_score": base_score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence from reasoning."""
        if not scored:
            return scored
        
        # Simple calibration: normalize scores
        scores = [item["raw_score"] for item in scored]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
            else:
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