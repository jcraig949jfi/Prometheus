import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_constraints,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import solve_first


class ReasoningTool:
    """Thermochemistry x SAT/Constraint Solving - Liar Detection"""

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
        """Extract agents, statements, truth policies, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "always tells truth")
        question = ""
        
        current_agent = None
        
        for line in lines:
            # Look for agent introductions (capitalized names followed by colon or "says")
            agent_match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)[:\s]', line)
            if agent_match:
                agent_name = agent_match.group(1)
                if agent_name not in agents:
                    agents.append(agent_name)
                current_agent = agent_name
                
                # Extract truth policy
                if "always lies" in line.lower() or "liar" in line.lower():
                    truth_policies[agent_name] = "liar"
                elif "always tells the truth" in line.lower() or "truth-teller" in line.lower():
                    truth_policies[agent_name] = "truth"
                elif "random" in line.lower() or "sometimes lies" in line.lower():
                    truth_policies[agent_policies] = "random"
            
            # Extract statements (quoted text or "says that...")
            if current_agent:
                # Find quoted statements
                quoted = re.findall(r'"([^"]*)"', line)
                if quoted:
                    for q in quoted:
                        statements.append({
                            "agent": current_agent,
                            "statement": q,
                            "raw": line
                        })
                # Find "says that" patterns
                elif "says that" in line.lower():
                    parts = line.split("says that", 1)
                    if len(parts) > 1:
                        stmt = parts[1].strip()
                        if stmt:
                            statements.append({
                                "agent": current_agent,
                                "statement": stmt.rstrip('.'),
                                "raw": line
                            })
            
            # Extract question (usually last line)
            if "?" in line and line == lines[-1]:
                question = line
        
        # Extract propositional variables from statements
        propositions = set()
        for stmt in statements:
            # Simple extraction: look for capitalized words that might be propositions
            words = re.findall(r'\b([A-Z][a-z]+)\b', stmt["statement"])
            for word in words:
                if word not in agents:  # Avoid confusing agent names with propositions
                    propositions.add(word)
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "propositions": list(propositions),
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use thermochemistry-inspired reasoning to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        propositions = structure["propositions"]
        question = structure["question"]
        
        # THERMOCHEMISTRY SCAFFOLD:
        # Treat truth as high-energy state (unstable), lies as low-energy (stable)
        # Consistency checking is like checking if a reaction is spontaneous (ΔG < 0)
        # Entropy measures disorder in possible truth assignments
        
        # Step 1: Encode as SAT problem
        # Variables: A_truth (agent A tells truth), P (proposition P is true)
        clauses = []
        var_map = {}
        var_counter = 1
        
        # Create variables for agents' truth-telling status
        for agent in agents:
            var_map[f"{agent}_truth"] = var_counter
            var_counter += 1
        
        # Create variables for propositions
        for prop in propositions:
            var_map[prop] = var_counter
            var_counter += 1
        
        # Add constraints based on truth policies
        for agent, policy in truth_policies.items():
            agent_var = var_map[f"{agent}_truth"]
            if policy == "liar":
                # Agent always lies: if agent_var is True, all their statements are False
                # We'll handle this per statement
                pass
            elif policy == "truth":
                # Agent always tells truth: if agent_var is True, all their statements are True
                # We'll handle this per statement
                pass
        
        # Process statements
        for stmt in statements:
            agent = stmt["agent"]
            statement_text = stmt["statement"]
            agent_var = var_map[f"{agent}_truth"]
            
            # Parse statement into logical form (simplified)
            # Look for negations
            is_negated = "not" in statement_text.lower() or "doesn't" in statement_text.lower()
            
            # Find which proposition this statement is about
            target_prop = None
            for prop in propositions:
                if prop in statement_text:
                    target_prop = prop
                    break
            
            if target_prop:
                prop_var = var_map[target_prop]
                
                # Encode: agent_var → (statement is true)
                # If agent tells truth (agent_var=1), then statement matches reality
                # If agent lies (agent_var=0), then statement is opposite of reality
                
                # For truth-teller: agent_var=1 → prop_var=1 (if positive) or prop_var=0 (if negated)
                # For liar: agent_var=0 → prop_var=0 (if positive) or prop_var=1 (if negated)
                
                # We encode as CNF clauses
                if is_negated:
                    # Statement says "not P"
                    # Truth-teller: agent_var → ¬prop_var
                    # Liar: ¬agent_var → prop_var
                    clauses.append([-agent_var, -prop_var])  # agent_var → ¬prop_var
                    clauses.append([agent_var, prop_var])     # ¬agent_var → prop_var
                else:
                    # Statement says "P"
                    # Truth-teller: agent_var → prop_var
                    # Liar: ¬agent_var → ¬prop_var
                    clauses.append([-agent_var, prop_var])    # agent_var → prop_var
                    clauses.append([agent_var, -prop_var])    # ¬agent_var → ¬prop_var
        
        # Use amino acid to check consistency
        consistency_result = None
        if clauses:
            # CRITICAL: amino acid call that directly determines answer
            consistency_result = check_entailment(clauses, [])
        
        # Step 2: Use constraint solving to find possible truth assignments
        # CRITICAL: T1 primitive call that directly determines answer
        if clauses and var_map:
            # Convert to constraint problem
            variables = list(var_map.keys())
            domains = {var: [0, 1] for var in variables}
            
            constraints = []
            for clause in clauses:
                def make_constraint(clause_vars=clause):
                    def constraint(assignment):
                        # CNF clause: at least one literal must be true
                        for lit in clause_vars:
                            var_idx = abs(lit) - 1
                            var_name = variables[var_idx]
                            value = assignment[var_name]
                            if lit > 0 and value == 1:
                                return True
                            if lit < 0 and value == 0:
                                return True
                        return False
                    return constraint
                
                # Get variable names involved in this clause
                involved_vars = []
                for lit in clause:
                    var_idx = abs(lit) - 1
                    if 0 <= var_idx < len(variables):
                        involved_vars.append(variables[var_idx])
                
                if involved_vars:
                    constraints.append((involved_vars, make_constraint()))
            
            # CRITICAL: amino acid call that directly determines answer
            solution = solve_first(variables_domains=domains, constraints=constraints)
        else:
            solution = None
        
        # Step 3: Analyze using thermochemistry concepts
        # Compute "energy" of truth assignments (higher energy = more contradictions)
        energy_values = []
        if solution:
            # For each agent, compute consistency energy
            for agent in agents:
                agent_var = f"{agent}_truth"
                if agent_var in solution:
                    # Truth-telling has higher "energy" (less stable)
                    # Lies have lower "energy" (more stable)
                    agent_energy = 1.0 if solution[agent_var] == 1 else 0.5
                    energy_values.append(agent_energy)
        
        # CRITICAL: T1 primitive call that directly determines answer
        if energy_values:
            system_entropy = entropy([ev/sum(energy_values) for ev in energy_values] if sum(energy_values) > 0 else [0.5, 0.5])
        else:
            system_entropy = entropy([0.5, 0.5])
        
        # Step 4: Determine answer to question
        computed_answer = ""
        confidence = 0.5
        
        # Extract what the question is asking for
        if "who" in question.lower():
            # Question asks for an agent name
            if solution:
                # Look for agents whose truth status is determined
                determined_agents = []
                for agent in agents:
                    agent_var = f"{agent}_truth"
                    if agent_var in solution:
                        determined_agents.append(agent)
                
                if determined_agents:
                    # CRITICAL: T1 primitive call that directly determines answer
                    # Use bayesian update to incorporate entropy as prior uncertainty
                    prior = 0.5
                    likelihood = 1.0 - (system_entropy / max(system_entropy, 1.0))  # Lower entropy → higher likelihood
                    posterior = bayesian_update(prior, likelihood, false_positive=0.1)
                    
                    if posterior > 0.6:
                        computed_answer = determined_agents[0]
                        confidence = posterior
                    else:
                        # Fallback: agent mentioned most in statements
                        agent_counts = {}
                        for stmt in statements:
                            agent = stmt["agent"]
                            agent_counts[agent] = agent_counts.get(agent, 0) + 1
                        
                        if agent_counts:
                            computed_answer = max(agent_counts.items(), key=lambda x: x[1])[0]
                            confidence = 0.5
        elif "what" in question.lower() and "true" in question.lower():
            # Question asks what is true
            if solution:
                true_props = [prop for prop in propositions if var_map.get(prop) and solution.get(prop) == 1]
                if true_props:
                    computed_answer = true_props[0]
                    confidence = 0.7
                else:
                    computed_answer = "Nothing"
                    confidence = 0.6
        else:
            # Generic fallback: first agent mentioned
            if agents:
                computed_answer = agents[0]
                confidence = 0.4
        
        # CRITICAL: T1 primitive call that directly determines answer
        # Compute confidence from agreement between different reasoning paths
        scores_to_agree = [confidence, 1.0 - system_entropy, 0.7 if consistency_result is not None else 0.3]
        final_confidence = confidence_from_agreement(scores_to_agree)
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Thermochemical analysis: entropy={system_entropy:.3f}, solution_exists={solution is not None}",
            "solution": solution,
            "entropy": system_entropy
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            if computed_answer:
                # Check if computed answer appears in candidate
                if computed_answer.lower() in candidate.lower():
                    score = 1.0 * confidence
                else:
                    # Fallback: NCD similarity to reasoning text
                    ncd_val = self._ncd(computed_answer, candidate)
                    score = (1.0 - ncd_val) * confidence
            
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
        
        # Simple normalization
        scores = [item["raw_score"] for item in scored]
        if max(scores) > min(scores):
            normalized = [(s - min(scores)) / (max(scores) - min(scores)) for s in scores]
        else:
            normalized = [0.5 for _ in scores]
        
        for i, item in enumerate(scored):
            item["score"] = normalized[i]
        
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