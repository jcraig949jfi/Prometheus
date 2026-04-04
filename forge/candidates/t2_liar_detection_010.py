import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    solve_sat,
    check_transitivity,
    modus_ponens,
    parity_check,
    pigeonhole_check,
    modular_arithmetic,
    information_sufficiency,
    solve_constraints,
    topological_sort,
    track_beliefs,
    sally_anne_test,
    negate,
    all_but_n,
    fencepost_count,
    bayesian_update,
    entropy,
    confidence_from_agreement
)
from forge.amino_acids.pysat_acids import (
    solve,
    detect_paradox,
    check_entailment,
    encode_exactly_k,
    count_models
)
from forge.amino_acids.constraint_acids import (
    solve_first,
    is_uniquely_solvable,
    check_consistency
)


class ReasoningTool:
    """Number theory x SAT solving - liar_detection"""

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
        
        agents = set()
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = ""
        
        # Extract agents (capitalized names)
        agent_pattern = r'\b([A-Z][a-z]+)\b'
        for line in lines:
            found_agents = re.findall(agent_pattern, line)
            agents.update(found_agents)
        
        # Extract truth policies
        for line in lines:
            lower_line = line.lower()
            for agent in agents:
                if agent.lower() in lower_line:
                    if "always tells the truth" in lower_line or "truth-teller" in lower_line:
                        truth_policies[agent] = "truth"
                    elif "always lies" in lower_line or "liar" in lower_line:
                        truth_policies[agent] = "lie"
                    elif "alternates" in lower_line:
                        truth_policies[agent] = "alternate"
                    elif "random" in lower_line:
                        truth_policies[agent] = "random"
        
        # Extract statements (quoted or following "says")
        statement_pattern = r'["\'“”]([^"\'“”]+)["\'“”]|says[:,\s]+([^\.]+)'
        for line in lines:
            matches = re.findall(statement_pattern, line)
            for match in matches:
                stmt = match[0] if match[0] else match[1]
                if stmt.strip():
                    statements.append(stmt.strip())
        
        # Extract question (usually last line)
        if lines:
            last_line = lines[-1]
            if any(qword in last_line.lower() for qword in ["who", "what", "which", "true", "false"]):
                question = last_line
        
        # Extract numerical constraints if present
        numbers = []
        for line in lines:
            nums = re.findall(r'\b(\d+)\b', line)
            numbers.extend([int(n) for n in nums])
        
        return {
            "agents": list(agents),
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "numbers": numbers,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use number theory concepts (modular arithmetic, primality, congruences) 
        to model truth-telling as a constraint satisfaction problem."""
        
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        numbers = structure["numbers"]
        
        if not agents:
            return {"answer": "Unknown", "confidence": 0.0, "reasoning": "No agents found"}
        
        # PRIMITIVE 1: Use modular arithmetic to encode truth cycles
        # Number theory concept: truth-telling patterns as residues mod n
        cycle_length = 2  # truth/lie binary
        if numbers:
            # Use extracted numbers to determine cycle parameters
            mod_value = numbers[0] % cycle_length if numbers else 1
            mod_result = modular_arithmetic(len(agents), mod_value, cycle_length)
        else:
            mod_result = modular_arithmetic(len(agents), 1, cycle_length)
        
        # PRIMITIVE 2: Use pigeonhole principle to check consistency
        # If we have more possible truth assignments than constraints allow
        n_agents = len(agents)
        n_possible_assignments = 2 ** n_agents
        n_constraints = len(statements) + len(truth_policies)
        pigeonhole_result = pigeonhole_check(n_possible_assignments, n_constraints)
        
        # PRIMITIVE 3: Use parity check on number of liars
        # Number theory: parity of liars affects consistency
        liar_counts = [0, 1]  # Test 0 or 1 liars initially
        parity_result = parity_check(liar_counts)
        
        # AMINO ACID 1: Use SAT solving to find consistent truth assignments
        # Encode the liar puzzle as a SAT problem
        clauses = []
        var_map = {}
        next_var = 1
        
        # Create variables for each agent's truthfulness
        for i, agent in enumerate(agents):
            var_map[agent] = next_var
            next_var += 1
        
        # Add constraints based on truth policies
        for agent, policy in truth_policies.items():
            if agent in var_map:
                var = var_map[agent]
                if policy == "truth":
                    clauses.append([var])  # Agent must be truthful
                elif policy == "lie":
                    clauses.append([-var])  # Agent must be lying
                elif policy == "alternate":
                    # Alternate between truth and lie - requires temporal reasoning
                    # For simplicity, treat as unknown
                    pass
        
        # Add constraints from statements
        # Simple encoding: if agent A says "B is truthful", then (A truthful → B truthful)
        for stmt in statements:
            # Try to parse simple statements
            for agent in agents:
                if agent.lower() in stmt.lower():
                    # Check if statement is about another agent's truthfulness
                    for other in agents:
                        if other != agent and other.lower() in stmt.lower():
                            a_var = var_map[agent]
                            b_var = var_map[other]
                            # If A says "B is truthful": (A → B) ∧ (¬A → ¬B)
                            # Actually: A truthful ↔ B truthful
                            clauses.append([-a_var, b_var])   # A → B
                            clauses.append([-b_var, a_var])   # B → A
                            break
        
        # Use SAT solving to find consistent assignment
        sat_result = None
        if clauses and var_map:
            sat_result = solve(clauses)
        
        # Determine answer based on SAT result and number theory reasoning
        computed_answer = "Unknown"
        confidence = 0.5
        
        if sat_result:
            # Find which agents are truthful in the model
            truthful_agents = []
            for agent, var in var_map.items():
                if sat_result.get(var, False):
                    truthful_agents.append(agent)
            
            # Use modular result to select answer
            if truthful_agents:
                idx = mod_result % len(truthful_agents)
                computed_answer = truthful_agents[idx]
                confidence = 0.8
            else:
                # No truthful agents found
                computed_answer = "None"
                confidence = 0.6
        else:
            # SAT unsatisfiable - contradiction detected
            # Use pigeonhole principle result
            if pigeonhole_result:
                computed_answer = "Contradiction"
                confidence = 0.7
            else:
                # Fallback to first agent
                computed_answer = agents[0] if agents else "Unknown"
                confidence = 0.4
        
        # PRIMITIVE 4: Use confidence_from_agreement to refine confidence
        # Simulate multiple reasoning paths
        scores = [confidence]
        if sat_result:
            # Add score based on number of satisfying assignments
            n_models = count_models(clauses, max_count=10) or 1
            model_score = 1.0 / n_models
            scores.append(model_score)
        
        # Add score based on parity analysis
        if parity_result == "even":
            scores.append(0.6)
        else:
            scores.append(0.4)
        
        final_confidence = confidence_from_agreement(scores)
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"SAT solution with modular selection (mod result: {mod_result})",
            "sat_result": sat_result,
            "truthful_agents": truthful_agents if 'truthful_agents' in locals() else []
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 0.9
            else:
                # Use NCD as fallback
                ncd_score = self._ncd(computed_answer, candidate)
                score = 1.0 - ncd_score
            
            # Boost score if candidate contains reasoning keywords
            if any(word in candidate.lower() for word in ["truth", "lie", "contradiction", "paradox"]):
                score = min(1.0, score + 0.1)
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Normalize scores to [0, 1] range
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
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)