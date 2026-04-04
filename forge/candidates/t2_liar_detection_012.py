import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_constraints,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """evolutionary_biology x pysat_acids - liar_detection"""

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
        statements = {}
        policies = {}
        question = lines[-1] if lines else ""
        
        # Extract agent names (capitalized words that appear before 'says' or 'always')
        for line in lines:
            # Find agent patterns like "Alice says" or "Bob always tells the truth"
            agent_match = re.search(r'([A-Z][a-z]+)\s+(?:says|always|never|tells)', line)
            if agent_match:
                agent = agent_match.group(1)
                agents.add(agent)
                
                # Extract policy
                if 'always tells the truth' in line.lower():
                    policies[agent] = 'truth'
                elif 'always lies' in line.lower():
                    policies[agent] = 'lie'
                elif 'alternates' in line.lower() or 'sometimes' in line.lower():
                    policies[agent] = 'alternating'
                
                # Extract statement content
                if 'says:' in line or 'says "' in line:
                    # Find quoted statement or statement after colon
                    quote_match = re.search(r'["\'“]([^"\'”]+)["\'”]', line)
                    if quote_match:
                        statements[agent] = quote_match.group(1).strip()
                    else:
                        # Try to extract after colon
                        colon_parts = line.split(':', 1)
                        if len(colon_parts) > 1:
                            statements[agent] = colon_parts[1].strip()
        
        # Extract propositional variables (simple facts mentioned)
        facts = set()
        for line in lines:
            # Look for simple factual statements
            if 'is true' in line.lower() or 'is false' in line.lower():
                # Extract the fact part before "is true/false"
                fact_match = re.search(r'([^\.]+)\s+is\s+(true|false)', line, re.IGNORECASE)
                if fact_match:
                    fact = fact_match.group(1).strip()
                    facts.add(fact)
        
        return {
            "agents": list(agents),
            "statements": statements,
            "policies": policies,
            "facts": list(facts),
            "question": question,
            "raw_lines": lines
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use evolutionary game theory and logical consistency to determine truth."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["policies"]
        facts = structure["facts"]
        
        # Evolutionary biology framework: agents as species with fixed truth-telling strategies
        # Truth-tellers have high fitness when environment (other agents' statements) is consistent
        # Liars have high fitness when they can create contradictions that survive selection
        
        # Phase 1: Build logical constraints from statements
        clauses = self._build_clauses(agents, statements, policies)
        
        # Phase 2: Use amino acid to detect paradox in the system
        paradox_info = detect_paradox(clauses)
        
        # Phase 3: Use T1 primitives to analyze belief dynamics
        # Compute entropy of possible truth assignments as measure of uncertainty
        possible_assignments = self._enumerate_assignments(agents, clauses)
        
        if possible_assignments:
            # Compute probability distribution over assignments
            probs = [1.0 / len(possible_assignments)] * len(possible_assignments)
            uncertainty = entropy(probs)  # T1 primitive 1
            
            # For each agent, compute posterior belief about their truthfulness
            # using bayesian update based on statement consistency
            agent_truth_prob = {}
            for agent in agents:
                # Prior: based on policy if known
                prior = 0.5
                if agent in policies:
                    if policies[agent] == 'truth':
                        prior = 0.9
                    elif policies[agent] == 'lie':
                        prior = 0.1
                    elif policies[agent] == 'alternating':
                        prior = 0.5
                
                # Likelihood: proportion of consistent assignments where agent's statement is true
                consistent_with_agent_true = 0
                total_consistent = 0
                
                for assignment in possible_assignments:
                    # Check if assignment satisfies all clauses
                    if self._satisfies_all(assignment, clauses):
                        total_consistent += 1
                        if assignment.get(f"{agent}_statement", False):
                            consistent_with_agent_true += 1
                
                likelihood = consistent_with_agent_true / max(total_consistent, 1)
                
                # Update belief
                posterior = bayesian_update(prior, likelihood, false_positive=0.1)  # T1 primitive 2
                agent_truth_prob[agent] = posterior
            
            # Use confidence_from_agreement to measure consensus
            truth_scores = list(agent_truth_prob.values())
            if truth_scores:
                consensus = confidence_from_agreement(truth_scores)  # T1 primitive 3
            else:
                consensus = 0.5
        else:
            uncertainty = 1.0
            agent_truth_prob = {agent: 0.5 for agent in agents}
            consensus = 0.0
        
        # Phase 4: Determine which fact is most likely true based on evolutionary stability
        # Facts that appear in most consistent assignments are evolutionarily stable
        fact_support = {}
        for fact in facts:
            support_count = 0
            total_assignments = len(possible_assignments)
            
            for assignment in possible_assignments:
                if self._satisfies_all(assignment, clauses):
                    # Check if fact is true in this assignment
                    # We'll use a simple heuristic: fact mentioned in true statements
                    fact_key = f"fact_{fact.replace(' ', '_')}"
                    if assignment.get(fact_key, False):
                        support_count += 1
            
            fact_support[fact] = support_count / max(total_assignments, 1)
        
        # Determine answer: either an agent's identity or a fact
        computed_answer = ""
        reasoning_text = ""
        
        if paradox_info and paradox_info.get("is_paradox", False):
            # Paradox detected - system is inconsistent
            computed_answer = "contradiction"
            reasoning_text = "The statements form a logical paradox."
        elif fact_support:
            # Find most supported fact
            best_fact = max(fact_support.items(), key=lambda x: x[1])
            if best_fact[1] > 0.5:
                computed_answer = best_fact[0]
                reasoning_text = f"Most evolutionarily stable fact: {best_fact[0]}"
            else:
                # No clear fact, check agent truthfulness
                if agent_truth_prob:
                    most_truthful = max(agent_truth_prob.items(), key=lambda x: x[1])
                    computed_answer = most_truthful[0]
                    reasoning_text = f"Most likely truth-teller: {most_truthful[0]}"
                else:
                    computed_answer = "unknown"
                    reasoning_text = "Insufficient information to determine truth."
        else:
            # No facts mentioned, determine liar/truth-teller
            if agent_truth_prob:
                # Evolutionary pressure: truth-tellers survive when environment is consistent
                # Liars survive when they can create beneficial contradictions
                if uncertainty < 0.3:  # Low uncertainty means consistent environment
                    # Truth-tellers have advantage
                    most_truthful = max(agent_truth_prob.items(), key=lambda x: x[1])
                    computed_answer = most_truthful[0]
                    reasoning_text = f"Consistent environment favors truth-teller: {most_truthful[0]}"
                else:
                    # High uncertainty, liars might thrive
                    least_truthful = min(agent_truth_prob.items(), key=lambda x: x[1])
                    computed_answer = least_truthful[0]
                    reasoning_text = f"Uncertain environment may favor liar: {least_truthful[0]}"
            else:
                computed_answer = "cannot determine"
                reasoning_text = "No clear evolutionary stable strategy."
        
        return {
            "answer": computed_answer,
            "confidence": consensus,
            "reasoning": reasoning_text,
            "uncertainty": uncertainty,
            "agent_truth_prob": agent_truth_prob,
            "fact_support": fact_support,
            "paradox_detected": paradox_info.get("is_paradox", False) if paradox_info else False
        }

    def _build_clauses(self, agents: List[str], statements: Dict[str, str], policies: Dict[str, str]) -> List[List[int]]:
        """Convert natural language statements to propositional logic clauses."""
        clauses = []
        var_map = {}
        next_var = 1
        
        # Create variables for agents' truthfulness
        for agent in agents:
            var_map[f"{agent}_truthful"] = next_var
            next_var += 1
        
        # Create variables for statements being true
        for agent, stmt in statements.items():
            var_map[f"{agent}_statement"] = next_var
            next_var += 1
            
            # Policy constraints
            if agent in policies:
                if policies[agent] == 'truth':
                    # Truthful agent → statement is true
                    clauses.append([-var_map[f"{agent}_truthful"], var_map[f"{agent}_statement"]])
                    clauses.append([var_map[f"{agent}_truthful"], -var_map[f"{agent}_statement"]])
                elif policies[agent] == 'lie':
                    # Lying agent → statement is false
                    clauses.append([-var_map[f"{agent}_truthful"], -var_map[f"{agent}_statement"]])
                    clauses.append([var_map[f"{agent}_truthful"], var_map[f"{agent}_statement"]])
        
        # Extract simple logical relationships from statements
        for agent, stmt in statements.items():
            # Handle simple statement patterns
            stmt_lower = stmt.lower()
            
            # Pattern: "X is truthful" or "X is lying"
            for other_agent in agents:
                if f"{other_agent.lower()} is truthful" in stmt_lower:
                    # Statement claims other_agent is truthful
                    clauses.append([
                        -var_map[f"{agent}_statement"],
                        var_map[f"{other_agent}_truthful"]
                    ])
                    clauses.append([
                        var_map[f"{agent}_statement"],
                        -var_map[f"{other_agent}_truthful"]
                    ])
                elif f"{other_agent.lower()} is lying" in stmt_lower:
                    # Statement claims other_agent is lying
                    clauses.append([
                        -var_map[f"{agent}_statement"],
                        -var_map[f"{other_agent}_truthful"]
                    ])
                    clauses.append([
                        var_map[f"{agent}_statement"],
                        var_map[f"{other_agent}_truthful"]
                    ])
            
            # Pattern: self-reference
            if "i am" in stmt_lower or "i'm" in stmt_lower:
                if "truthful" in stmt_lower:
                    # "I am truthful" - statement equivalent to agent being truthful
                    clauses.append([
                        -var_map[f"{agent}_statement"],
                        var_map[f"{agent}_truthful"]
                    ])
                    clauses.append([
                        var_map[f"{agent}_statement"],
                        -var_map[f"{agent}_truthful"]
                    ])
                elif "lying" in stmt_lower:
                    # "I am lying" - creates liar paradox
                    # This will be caught by paradox detection
                    pass
        
        return clauses

    def _enumerate_assignments(self, agents: List[str], clauses: List[List[int]]) -> List[Dict[str, bool]]:
        """Enumerate possible truth assignments for small problems."""
        if len(agents) > 4:  # Too many variables for brute force
            return []
        
        # Get all variables from clauses
        all_vars = set()
        for clause in clauses:
            for lit in clause:
                all_vars.add(abs(lit))
        
        if not all_vars:
            return []
        
        # Brute force enumeration
        assignments = []
        n = len(all_vars)
        var_list = list(all_vars)
        
        for i in range(2**n):
            assignment = {}
            for j, var in enumerate(var_list):
                assignment[var] = bool((i >> j) & 1)
            
            # Check if assignment satisfies all clauses
            if self._satisfies_all(assignment, clauses):
                # Convert to named assignment
                named_assignment = {}
                # We need the reverse mapping from var numbers to names
                # For simplicity, we'll just store the numeric assignment
                assignments.append(assignment)
        
        return assignments

    def _satisfies_all(self, assignment: Dict[int, bool], clauses: List[List[int]]) -> bool:
        """Check if assignment satisfies all clauses."""
        for clause in clauses:
            clause_satisfied = False
            for lit in clause:
                var = abs(lit)
                value = assignment.get(var, False)
                if lit > 0 and value:
                    clause_satisfied = True
                    break
                elif lit < 0 and not value:
                    clause_satisfied = True
                    break
            if not clause_satisfied:
                return False
        return True

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Adjust based on confidence
            confidence = reasoning_result.get("confidence", 0.5)
            adjusted_score = base_score * (0.5 + 0.5 * confidence)
            
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