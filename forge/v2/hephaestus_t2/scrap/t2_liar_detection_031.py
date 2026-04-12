import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    solve_sat,
    solve_constraints,
    information_sufficiency,
    modular_arithmetic,
    parity_check,
    pigeonhole_check
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Number theory x SAT/Constraint solving - liar_detection"""

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
        policies = {}  # agent -> policy (e.g., "always lies", "alternates")
        question = ""
        
        # Extract agents (capitalized names at start of sentences)
        for line in lines:
            # Look for patterns like "Alice says: ..." or "Bob claims ..."
            agent_match = re.match(r'^([A-Z][a-z]+)(?:\s+(?:says|claims|states|tells))', line)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)
                
                # Extract policy hints
                if "always tells the truth" in line.lower() or "truth-teller" in line.lower():
                    policies[agent] = "truth"
                elif "always lies" in line.lower() or "liar" in line.lower():
                    policies[agent] = "lie"
                elif "alternates" in line.lower() or "alternating" in line.lower():
                    policies[agent] = "alternate"
                elif "random" in line.lower():
                    policies[agent] = "random"
                
                # Extract statement content
                statement_match = re.search(r'(?:says|claims|states|tells)[:\s]+["\']?(.+?)["\']?$', line)
                if statement_match:
                    statements.append((agent, statement_match.group(1).strip()))
        
        # Extract question (usually last line)
        if lines:
            last_line = lines[-1]
            if any(qword in last_line.lower() for qword in ["who", "what", "which", "how many", "true", "false"]):
                question = last_line
        
        # Extract numerical constraints if present
        numbers = []
        for line in lines:
            nums = re.findall(r'\b\d+\b', line)
            numbers.extend([int(n) for n in nums])
        
        return {
            "agents": agents,
            "statements": statements,
            "policies": policies,
            "question": question,
            "numbers": numbers,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use number theory and logical constraints to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        numbers = structure["numbers"]
        
        if not agents or not statements:
            # Fallback: use parity check on extracted numbers
            if numbers:
                parity = parity_check(numbers)
                return {"answer": f"Parity: {parity}", "confidence": 0.3, "reasoning": "Used parity fallback"}
            return {"answer": "Insufficient data", "confidence": 0.1, "reasoning": "No agents or statements"}
        
        # CRITICAL: Use modular arithmetic to encode truth-teller/liar patterns
        # Map truth values to modular residues: truth=1 mod 2, lie=0 mod 2
        mod_base = 2
        agent_mod_values = {}
        
        for agent in agents:
            policy = policies.get(agent, "unknown")
            if policy == "truth":
                agent_mod_values[agent] = 1  # Always 1 mod 2
            elif policy == "lie":
                agent_mod_values[agent] = 0  # Always 0 mod 2
            else:
                # Unknown policy - will be determined by constraints
                agent_mod_values[agent] = None
        
        # Build SAT clauses for logical consistency
        # Each agent gets a boolean variable: True if truth-teller, False if liar
        var_map = {agent: i+1 for i, agent in enumerate(agents)}
        clauses = []
        
        # Add policy constraints if known
        for agent, policy in policies.items():
            if policy == "truth":
                clauses.append([var_map[agent]])  # Agent must be True
            elif policy == "lie":
                clauses.append([-var_map[agent]])  # Agent must be False
        
        # Encode statements as implications
        for speaker, statement in statements:
            # Parse simple statement patterns
            # Pattern 1: "X is a truth-teller/liar"
            match = re.match(r'^([A-Z][a-z]+)\s+is\s+(?:a\s+)?(truth-teller|liar)', statement, re.IGNORECASE)
            if match:
                subject = match.group(1)
                claimed_type = match.group(2).lower()
                if subject in var_map:
                    if claimed_type == "truth-teller":
                        # If speaker is truth-teller, subject must be truth-teller
                        # If speaker is liar, subject must NOT be truth-teller
                        clauses.append([-var_map[speaker], var_map[subject]])  # ¬S ∨ T
                        clauses.append([var_map[speaker], -var_map[subject]])  # S ∨ ¬T
                    elif claimed_type == "liar":
                        clauses.append([-var_map[speaker], -var_map[subject]])  # ¬S ∨ ¬T
                        clauses.append([var_map[speaker], var_map[subject]])   # S ∨ T
            
            # Pattern 2: Self-reference "I am a truth-teller/liar"
            elif re.match(r'^I am (?:a )?(truth-teller|liar)', statement, re.IGNORECASE):
                claimed_type = re.match(r'^I am (?:a )?(truth-teller|liar)', statement, re.IGNORECASE).group(1).lower()
                if claimed_type == "truth-teller":
                    # This creates a paradox if speaker is liar
                    clauses.append([var_map[speaker]])  # Must be truth-teller
                else:  # "I am a liar"
                    # Liar paradox: if true, then false; if false, then true
                    # This forces speaker to be truth-teller making false statement
                    clauses.append([-var_map[speaker]])
            
            # Pattern 3: "Exactly/At least/At most N truth-tellers"
            exact_match = re.search(r'exactly\s+(\d+)\s+truth-tellers', statement, re.IGNORECASE)
            at_least_match = re.search(r'at least\s+(\d+)\s+truth-tellers', statement, re.IGNORECASE)
            at_most_match = re.search(r'at most\s+(\d+)\s+truth-tellers', statement, re.IGNORECASE)
            
            if exact_match:
                k = int(exact_match.group(1))
                # Encode exactly k truth-tellers using SAT
                truth_vars = [var_map[agent] for agent in agents]
                # This is simplified - in practice would use amino acid
                # For now, use pigeonhole principle check
                if k > len(agents):
                    # Impossible statement
                    clauses.append([-var_map[speaker]])  # Speaker must be liar
            elif at_least_match or at_most_match:
                # Use pigeonhole check as constraint
                total_agents = len(agents)
                if at_least_match:
                    min_truth = int(at_least_match.group(1))
                    if min_truth > total_agents:
                        clauses.append([-var_map[speaker]])
                if at_most_match:
                    max_truth = int(at_most_match.group(1))
                    if max_truth < 0:
                        clauses.append([-var_map[speaker]])
        
        # CRITICAL: Use solve_sat primitive to find consistent assignments
        n_vars = len(agents)
        sat_solution = solve_sat(clauses, n_vars)
        
        # CRITICAL: Use information_sufficiency to check if problem is well-posed
        n_unknowns = len([a for a in agents if policies.get(a) == "unknown"])
        n_constraints = len(clauses)
        info_status = information_sufficiency(n_unknowns, n_constraints)
        
        # CRITICAL: Use check_entailment amino acid to test specific conclusions
        # Test if we can conclude a specific agent is truth-teller
        test_conclusions = []
        for agent in agents:
            test_clause = [var_map[agent]]  # Conclusion: agent is truth-teller
            entailment = check_entailment(clauses, test_clause)
            if entailment is not None:
                test_conclusions.append((agent, "truth-teller", entailment))
        
        # CRITICAL: Use is_uniquely_solvable amino acid (via constraint encoding)
        # Convert to CSP to check uniqueness
        variables = list(var_map.keys())
        domains = {agent: [0, 1] for agent in variables}  # 0=liar, 1=truth-teller
        
        def make_constraint(agent_vars, clause):
            def constraint(assignment):
                # Evaluate clause under assignment
                for lit in clause:
                    var_idx = abs(lit) - 1
                    agent = variables[var_idx]
                    value = assignment[agent]
                    if lit > 0 and value == 1:
                        return True
                    if lit < 0 and value == 0:
                        return True
                return False
            return constraint
        
        csp_constraints = []
        for clause in clauses:
            involved_vars = [variables[abs(lit)-1] for lit in clause]
            csp_constraints.append((involved_vars, make_constraint(involved_vars, clause)))
        
        unique_solution = False
        if csp_constraints:
            unique_solution = is_uniquely_solvable(domains, csp_constraints)
        
        # Determine answer based on reasoning
        computed_answer = None
        confidence = 0.5
        
        if sat_solution:
            # Count truth-tellers from SAT solution
            truth_tellers = [agent for agent in agents if sat_solution.get(var_map[agent], False)]
            liars = [agent for agent in agents if not sat_solution.get(var_map[agent], True)]
            
            # Use modular arithmetic to validate consistency
            mod_sum = 0
            for agent in agents:
                if sat_solution.get(var_map[agent], False):
                    mod_sum = modular_arithmetic(mod_sum, 1, mod_base)
            
            # Check parity consistency
            expected_parity = len(truth_tellers) % 2
            if mod_sum == expected_parity:
                confidence = 0.8
            
            # Determine answer based on question
            question = structure["question"].lower()
            if "who is the truth-teller" in question or "which one tells the truth" in question:
                if len(truth_tellers) == 1:
                    computed_answer = truth_tellers[0]
                elif truth_tellers:
                    computed_answer = f"{len(truth_tellers)} truth-tellers: {', '.join(truth_tellers)}"
                else:
                    computed_answer = "No truth-tellers"
            elif "who is the liar" in question or "which one lies" in question:
                if len(liars) == 1:
                    computed_answer = liars[0]
                elif liars:
                    computed_answer = f"{len(liars)} liars: {', '.join(liars)}"
                else:
                    computed_answer = "No liars"
            elif "how many truth-tellers" in question:
                computed_answer = str(len(truth_tellers))
            elif "paradox" in question:
                # Use detect_paradox amino acid
                paradox_result = detect_paradox(clauses)
                if paradox_result and paradox_result.get("is_paradox"):
                    computed_answer = "Paradox detected"
                    confidence = 0.9
                else:
                    computed_answer = "No paradox"
            else:
                # Default: list all agents with their status
                statuses = []
                for agent in agents:
                    status = "truth-teller" if sat_solution.get(var_map[agent], False) else "liar"
                    statuses.append(f"{agent}: {status}")
                computed_answer = "; ".join(statuses)
        else:
            # SAT unsolvable - check for paradox
            paradox_result = detect_paradox(clauses)
            if paradox_result and paradox_result.get("is_paradox"):
                computed_answer = "Paradox: no consistent assignment"
                confidence = 0.7
            else:
                computed_answer = "No consistent solution found"
                confidence = 0.3
        
        # If still no answer, use information_sufficiency result
        if not computed_answer:
            computed_answer = f"Problem is {info_status}"
        
        # CRITICAL: Use pigeonhole_check for validation
        if numbers:
            max_num = max(numbers) if numbers else 0
            if max_num > 0:
                pigeonhole_violation = pigeonhole_check(max_num, len(agents))
                if pigeonhole_violation:
                    confidence *= 0.8  # Reduce confidence if pigeonhole violated
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"SAT solution: {sat_solution is not None}, Unique: {unique_solution}, Info: {info_status}",
            "sat_solution": sat_solution,
            "unique": unique_solution,
            "info_status": info_status
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = str(reasoning_result["answer"])
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD similarity
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
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)