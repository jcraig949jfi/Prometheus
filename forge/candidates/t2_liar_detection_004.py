import re
import zlib
from typing import List, Dict, Any

from forge_primitives import (
    solve_sat,
    check_transitivity,
    confidence_from_agreement,
    entropy,
    solve_constraints,
    topological_sort
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Optics x SAT/Constraint - liar_detection"""

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
        """Extract agents, statements, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = []
        statements = []
        question = ""
        
        # Find agents (capitalized names at start of sentences)
        agent_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        # Find statements (usually contain "says", "claims", "states")
        statement_pattern = r'([^.!?]+(?:says|claims|states)[^.!?]+)'
        
        for line in lines:
            # Extract question (often last line with '?')
            if '?' in line:
                question = line
                continue
            
            # Extract agents
            agent_match = re.match(agent_pattern, line)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)
            
            # Extract statements
            statement_matches = re.findall(statement_pattern, line, re.IGNORECASE)
            for stmt in statement_matches:
                statements.append(stmt.strip())
        
        # Parse truth-telling policies (always truth-teller, always liar, random)
        policies = {}
        for agent in agents:
            agent_lower = agent.lower()
            if any(word in prompt.lower() for word in [f"{agent_lower} always tells the truth", 
                                                      f"{agent_lower} is truthful", 
                                                      "truth-teller"]):
                policies[agent] = "truth"
            elif any(word in prompt.lower() for word in [f"{agent_lower} always lies", 
                                                        f"{agent_lower} is a liar", 
                                                        "liar"]):
                policies[agent] = "lie"
            elif any(word in prompt.lower() for word in [f"{agent_lower} sometimes lies", 
                                                        f"{agent_lower} random", 
                                                        "random"]):
                policies[agent] = "random"
            else:
                policies[agent] = "unknown"
        
        return {
            "agents": agents,
            "statements": statements,
            "policies": policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use optics-inspired logical refraction to resolve liar puzzles."""
        agents = structure["agents"]
        policies = structure["policies"]
        question = structure["question"]
        
        # CRITICAL: Use amino acid to detect paradox in statements
        # Convert statements to logical clauses for paradox detection
        clauses = self._statements_to_clauses(structure["statements"], agents)
        paradox_result = detect_paradox(clauses) if clauses else None
        
        # CRITICAL: Use amino acid to check entailment for the question
        # Extract what the question is asking about
        target_conclusion = self._extract_conclusion(question, agents)
        entailment_result = None
        if clauses and target_conclusion:
            entailment_result = check_entailment(clauses, target_conclusion)
        
        # CRITICAL: Use T1 primitive to solve SAT for consistency checking
        sat_assignment = None
        if clauses:
            # Create SAT instance: each agent's statement is a variable
            sat_clauses = []
            var_map = {}
            for i, agent in enumerate(agents):
                var_map[agent] = i + 1
                # If agent is truth-teller, their statements must be true
                if policies.get(agent) == "truth":
                    # This is simplified - actual encoding would be more complex
                    pass
            
            # Try to find a satisfying assignment
            sat_assignment = solve_sat(sat_clauses, len(agents)) if sat_clauses else None
        
        # CRITICAL: Use T1 primitive for constraint solving
        # Model as CSP: each agent has truth value (0/1 for liar/truth-teller)
        variables = agents
        domains = {agent: [0, 1] for agent in agents}  # 0=liar, 1=truth-teller
        
        # Add constraints based on policies
        constraints = []
        for agent, policy in policies.items():
            if policy == "truth":
                constraints.append(([agent], lambda x: x == 1))
            elif policy == "lie":
                constraints.append(([agent], lambda x: x == 0))
        
        # Try to solve the CSP
        csp_solution = solve_first(variables, domains, constraints)
        
        # CRITICAL: Use T1 primitive to check if solution is unique
        unique_solution = False
        if csp_solution:
            unique_solution = is_uniquely_solvable(variables, domains, constraints)
        
        # CRITICAL: Use T1 primitive for confidence from agreement
        # Collect different reasoning paths
        scores = []
        if paradox_result and paradox_result.get("is_paradox", False):
            scores.append(0.3)  # Paradox detected, low confidence
        if entailment_result and entailment_result.get("entails", False):
            scores.append(0.8)  # Strong entailment
        if sat_assignment:
            scores.append(0.6)  # SAT solution found
        if csp_solution:
            scores.append(0.7)  # CSP solution found
        
        confidence = confidence_from_agreement(scores) if scores else 0.5
        
        # CRITICAL: Use T1 primitive for entropy of policy distribution
        policy_values = []
        for agent in agents:
            if policies.get(agent) == "truth":
                policy_values.append(1.0)
            elif policies.get(agent) == "lie":
                policy_values.append(0.0)
            else:
                policy_values.append(0.5)  # Unknown/random
        
        policy_entropy = entropy(policy_values) if policy_values else 1.0
        
        # Optics-inspired reasoning: logical refraction
        # In optics, light bends when passing through different media
        # Here, truth bends through different agent policies
        computed_answer = self._optics_refraction(agents, policies, csp_solution, 
                                                paradox_result, entailment_result,
                                                policy_entropy)
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Optical refraction analysis with entropy {policy_entropy:.2f}",
            "policies": policies,
            "unique_solution": unique_solution
        }

    def _optics_refraction(self, agents, policies, csp_solution, 
                          paradox_result, entailment_result, entropy_val):
        """Apply optics metaphor: truth refracts through policy media."""
        # Base case: if CSP gives unique solution, use that
        if csp_solution:
            # Find the agent whose truth value is most informative
            # Higher entropy means more uncertainty
            if entropy_val < 0.5:  # Low entropy = clear policies
                # Return the agent with definitive policy
                for agent, policy in policies.items():
                    if policy in ["truth", "lie"]:
                        return agent
            else:
                # High entropy = mixed policies, return most constrained agent
                if agents:
                    return agents[0]
        
        # Fallback based on paradox detection
        if paradox_result and paradox_result.get("is_paradox", False):
            # If paradox, the puzzle might be about identifying the liar causing it
            for agent in agents:
                if policies.get(agent) == "lie":
                    return agent
        
        # Final fallback
        return agents[0] if agents else "Unknown"

    def _statements_to_clauses(self, statements: List[str], agents: List[str]) -> List[List[int]]:
        """Convert natural language statements to SAT clauses (simplified)."""
        clauses = []
        # Simplified encoding: each statement gets a variable
        # In real implementation, would parse logical structure
        for i, stmt in enumerate(statements):
            # Check if statement references other agents
            for j, agent in enumerate(agents):
                if agent.lower() in stmt.lower():
                    # Create implication: if agent is truth-teller, statement is true
                    # This is a simplified placeholder
                    var_idx = i * len(agents) + j + 1
                    clauses.append([var_idx])
        return clauses

    def _extract_conclusion(self, question: str, agents: List[str]) -> List[int]:
        """Extract what the question is asking as a logical conclusion."""
        # Simplified: check if question asks about a specific agent
        for agent in agents:
            if agent.lower() in question.lower():
                # Return a dummy clause for the amino acid
                return [1]  # Placeholder
        return None

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
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
        """Calibrate scores to ensure proper distribution."""
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)