import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Neuroscience x SAT solving - liar_detection"""

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
        
        # Look for agent declarations and their policies
        for line in lines:
            line_lower = line.lower()
            
            # Extract agent names (capitalized words that appear as subjects)
            # Simple pattern: "Alice says", "Bob claims", etc.
            agent_match = re.search(r'([A-Z][a-z]+)\s+(?:says|claims|states|asserts)', line)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)
            
            # Extract truth-telling policies
            if "always tells the truth" in line_lower or "truth-teller" in line_lower:
                for agent in agents:
                    if agent in line:
                        policies[agent] = "truth-teller"
            elif "always lies" in line_lower or "liar" in line_lower:
                for agent in agents:
                    if agent in line:
                        policies[agent] = "liar"
            elif "random" in line_lower or "sometimes lies" in line_lower:
                for agent in agents:
                    if agent in line:
                        policies[agent] = "random"
            
            # Extract statements (quoted or following "says")
            if '"' in line:
                statement_match = re.search(r'"([^"]+)"', line)
                if statement_match:
                    statements.append({
                        "text": statement_match.group(1),
                        "speaker": agent if 'agent' in locals() else None
                    })
            elif "says:" in line or "claims:" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    statements.append({
                        "text": parts[1].strip(),
                        "speaker": agent if 'agent' in locals() else None
                    })
        
        # If no explicit policies found, infer from context
        for agent in agents:
            if agent not in policies:
                policies[agent] = "unknown"
        
        return {
            "agents": agents,
            "statements": statements,
            "policies": policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use neuroscience-inspired reasoning to resolve liar puzzles.
        
        Neuroscience framework: Model agents as neural populations with 
        fixed firing patterns (truth-telling policies). The puzzle is a 
        constraint satisfaction problem where we must find the consistent 
        global state that minimizes prediction error (entropy).
        """
        agents = structure["agents"]
        policies = structure["policies"]
        statements = structure["statements"]
        
        # If no agents extracted, fallback to simple analysis
        if not agents:
            return {"answer": "Cannot determine", "confidence": 0.0, "reasoning": "No agents found"}
        
        # PHASE 1: Encode as SAT problem (amino acid)
        # Convert statements to propositional logic
        clauses = []
        var_map = {}  # Map propositions to SAT variables
        
        # Create variables for each agent's truth value
        for i, agent in enumerate(agents):
            var_map[f"{agent}_truthful"] = i + 1
        
        # Add constraints based on policies
        for agent, policy in policies.items():
            if agent in [a for a in agents]:
                idx = agents.index(agent)
                var = idx + 1
                if policy == "truth-teller":
                    # Truth-teller: all their statements are true
                    clauses.append([var])  # Agent is truthful
                elif policy == "liar":
                    # Liar: all their statements are false
                    clauses.append([-var])  # Agent is not truthful
                # Random: no constraint (can be either)
        
        # Add constraints from statements
        # Simple encoding: if agent says "X is Y", then (agent_truthful → X_is_Y)
        statement_idx = len(agents) + 1
        for stmt in statements:
            if stmt["speaker"] and stmt["speaker"] in agents:
                speaker_idx = agents.index(stmt["speaker"]) + 1
                # Create variable for statement truth
                stmt_var = statement_idx
                var_map[stmt["text"]] = stmt_var
                statement_idx += 1
                
                # Implication: speaker_truthful → statement_true
                # ¬speaker_truthful ∨ statement_true
                clauses.append([-speaker_idx, stmt_var])
                
                # If speaker is liar, statement must be false
                # But this is already covered by ¬speaker_truthful
        
        # Use SAT solving to check consistency (amino acid)
        paradox_result = detect_paradox(clauses)
        
        # Use constraint solving to find solutions (amino acid)
        # Convert to CSP format for solve_first
        variables = list(var_map.keys())
        domains = {}
        constraints = []
        
        for var in variables:
            domains[var] = [True, False]
        
        # Add policy constraints
        for agent, policy in policies.items():
            if agent in [a for a in agents] and policy in ["truth-teller", "liar"]:
                agent_var = f"{agent}_truthful"
                if agent_var in variables:
                    if policy == "truth-teller":
                        constraints.append(([agent_var], lambda vals: vals[0] == True))
                    else:  # liar
                        constraints.append(([agent_var], lambda vals: vals[0] == False))
        
        # Try to find a solution
        solution = solve_first(variables, domains, constraints)
        
        # Check if solution is unique (amino acid)
        unique = is_uniquely_solvable(variables, domains, constraints) if solution else False
        
        # PHASE 2: Bayesian belief update (T1 primitive)
        # Model uncertainty about agent types
        prior_truthful = 0.5  # Base rate assumption
        
        # Update based on statement consistency
        if paradox_result and paradox_result.get("is_paradox", False):
            # Paradox detected - policies may be inconsistent
            posterior = bayesian_update(prior_truthful, 0.1, 0.1)  # Low likelihood
        elif solution:
            # Consistent solution found
            if unique:
                posterior = bayesian_update(prior_truthful, 0.9, 0.1)  # High confidence
            else:
                posterior = bayesian_update(prior_truthful, 0.6, 0.2)  # Moderate confidence
        else:
            # No solution found
            posterior = bayesian_update(prior_truthful, 0.3, 0.3)  # Low confidence
        
        # PHASE 3: Compute entropy of possible states (T1 primitive)
        # Create probability distribution over possible agent types
        probs = []
        if solution:
            # If unique solution, low entropy
            probs = [0.9, 0.1]
        elif paradox_result and paradox_result.get("is_paradox", False):
            # Paradox - high uncertainty
            probs = [0.5, 0.5]
        else:
            # Multiple solutions possible
            probs = [0.7, 0.3]
        
        uncertainty = entropy(probs)
        
        # PHASE 4: Determine which agent's policy is most informative
        # Use modus ponens to derive conclusions (T1 primitive)
        facts = set()
        derived = set()
        
        if solution:
            # Add facts from solution
            for var, val in solution.items():
                if val:
                    facts.add(var)
            
            # Apply modus ponens
            premises = []
            for stmt in statements:
                if stmt["speaker"]:
                    speaker_var = f"{stmt['speaker']}_truthful"
                    stmt_var = stmt["text"]
                    if stmt_var in var_map:
                        premises.append((speaker_var, stmt_var))
            
            if premises:
                derived = modus_ponens(premises, facts)
        
        # PHASE 5: Track beliefs across agents (T1 primitive)
        # Model what each agent believes based on their statements
        observations = []
        for stmt in statements:
            if stmt["speaker"]:
                stmt_text = stmt["text"]
                # Try to extract proposition from statement
                prop = None
                if " is " in stmt_text or " are " in stmt_text:
                    prop = stmt_text
                if prop:
                    # Assume speaker believes what they say if truthful
                    speaker_idx = agents.index(stmt["speaker"])
                    observations.append((stmt["speaker"], prop, True))
        
        belief_state = track_beliefs(agents, observations) if observations else {}
        
        # PHASE 6: Compute final confidence (T1 primitive)
        confidence_scores = []
        if posterior > 0.5:
            confidence_scores.append(posterior)
        if uncertainty < 0.5:  # Low entropy = high confidence
            confidence_scores.append(1.0 - uncertainty)
        if solution:
            confidence_scores.append(0.8 if unique else 0.6)
        
        final_confidence = confidence_from_agreement(confidence_scores) if confidence_scores else 0.5
        
        # Determine the answer based on reasoning
        computed_answer = ""
        
        # Strategy 1: If paradox detected, answer indicates inconsistency
        if paradox_result and paradox_result.get("is_paradox", False):
            computed_answer = "The statements are contradictory"
        
        # Strategy 2: If unique solution, identify key agent
        elif solution and unique:
            # Find the agent whose truth value is most constrained
            agent_truth_values = []
            for agent in agents:
                agent_var = f"{agent}_truthful"
                if agent_var in solution:
                    agent_truth_values.append((agent, solution[agent_var]))
            
            if agent_truth_values:
                # Sort by truth value (truth-tellers first)
                agent_truth_values.sort(key=lambda x: x[1], reverse=True)
                computed_answer = agent_truth_values[0][0]
        
        # Strategy 3: Use Bayesian posterior to choose most likely truth-teller
        else:
            # Assign probability to each agent being truthful
            agent_probs = []
            for agent in agents:
                agent_policy = policies.get(agent, "unknown")
                if agent_policy == "truth-teller":
                    agent_probs.append((agent, posterior))
                elif agent_policy == "liar":
                    agent_probs.append((agent, 1.0 - posterior))
                else:
                    agent_probs.append((agent, 0.5))
            
            if agent_probs:
                best_agent = max(agent_probs, key=lambda x: x[1])[0]
                computed_answer = best_agent
        
        # Fallback if no answer determined
        if not computed_answer and agents:
            computed_answer = agents[0]
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"SAT consistency: {bool(solution)}, Paradox: {paradox_result.get('is_paradox', False) if paradox_result else False}, Unique: {unique}, Posterior: {posterior:.2f}, Entropy: {uncertainty:.2f}",
            "raw_answer": computed_answer
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        raw_answer = reasoning_result.get("raw_answer", computed_answer)
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 0.9 + (confidence * 0.1)
            elif raw_answer and raw_answer.lower() in candidate.lower():
                score = 0.8 + (confidence * 0.1)
            else:
                # Fallback: NCD similarity
                ncd_score = self._ncd(computed_answer, candidate)
                score = 0.5 * (1.0 - ncd_score) + 0.5 * confidence
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Extract raw scores
        raw_scores = [item["raw_score"] for item in scored]
        
        # Simple normalization: scale to [0, 1] range
        min_score = min(raw_scores)
        max_score = max(raw_scores)
        
        if max_score > min_score:
            for item in scored:
                normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                item["score"] = normalized
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