import re
import zlib
from typing import List, Dict, Any

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_sat,
    modus_ponens
)
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Optics x SAT entailment - liar_detection"""

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
        policies = {}
        question = lines[-1] if lines else ""
        
        # Find agent names (capitalized words that appear before "says" or "always")
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        
        for line in lines:
            # Extract agents
            possible_agents = re.findall(agent_pattern, line)
            for agent in possible_agents:
                if agent not in agents and len(agent.split()) <= 2:
                    agents.append(agent)
            
            # Extract truth-telling policies
            if 'always tells the truth' in line.lower():
                for agent in possible_agents:
                    if agent in agents:
                        policies[agent] = 'truth'
            elif 'always lies' in line.lower():
                for agent in possible_agents:
                    if agent in agents:
                        policies[agent] = 'lie'
            
            # Extract statements (quoted or after "says")
            if 'says' in line.lower():
                parts = line.split('says', 1)
                if len(parts) > 1:
                    statement = parts[1].strip().strip('"').strip()
                    if statement and statement not in statements:
                        statements.append(statement)
        
        return {
            "agents": agents,
            "statements": statements,
            "policies": policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use optical coherence analogy: truth values as light waves that interfere."""
        agents = structure["agents"]
        policies = structure["policies"]
        statements = structure["statements"]
        
        # If we have enough structure, use SAT entailment to find consistent truth assignments
        computed_answer = None
        confidence = 0.5
        reasoning = ""
        
        # Build logical constraints based on truth-telling policies
        # In optics analogy: truth-tellers emit coherent waves (consistent statements),
        # liars emit anti-coherent waves (contradictions)
        
        # Phase 1: Use SAT to check consistency of statements with policies
        if len(agents) >= 2 and len(statements) >= 1:
            # Encode as propositional logic
            # For each agent A and statement S: if A says S and A is truth-teller, then S is true
            # If A says S and A is liar, then S is false
            
            clauses = []
            var_map = {}
            next_var = 1
            
            # Create variables for statements
            for i, stmt in enumerate(statements):
                var_map[stmt] = next_var
                next_var += 1
            
            # Create variables for agent truthfulness (True = truth-teller, False = liar)
            for agent in agents:
                var_map[f"{agent}_truthful"] = next_var
                next_var += 1
            
            # Add constraints based on policies
            for agent, policy in policies.items():
                if policy == 'truth':
                    # Agent is truthful: their statement variable equals statement truth
                    for stmt in statements:
                        if agent.lower() in structure["raw"].lower() and stmt.lower() in structure["raw"].lower():
                            # If agent says this statement
                            # Truth-teller: statement is true
                            clauses.append([var_map[f"{agent}_truthful"], -var_map[stmt]])  # agent_truthful → statement_true
                            clauses.append([-var_map[f"{agent}_truthful"], var_map[stmt]])  # ¬agent_truthful → ¬statement_true
                elif policy == 'lie':
                    # Agent lies: their statement variable is opposite of statement truth
                    for stmt in statements:
                        if agent.lower() in structure["raw"].lower() and stmt.lower() in structure["raw"].lower():
                            # Liar: statement is false
                            clauses.append([var_map[f"{agent}_truthful"], var_map[stmt]])   # agent_truthful → statement_false
                            clauses.append([-var_map[f"{agent}_truthful"], -var_map[stmt]]) # ¬agent_truthful → statement_true
            
            # Use SAT to find consistent assignments
            if clauses:
                sat_result = solve_sat(clauses, next_var - 1)
                
                if sat_result:
                    # Use entropy of truth values as measure of coherence (optical analogy)
                    truth_values = []
                    for stmt in statements:
                        if var_map[stmt] in sat_result and sat_result[var_map[stmt]]:
                            truth_values.append(1.0)
                        else:
                            truth_values.append(0.0)
                    
                    # Compute entropy of truth distribution (optical coherence measure)
                    if truth_values:
                        # Normalize to probability distribution
                        p_true = sum(truth_values) / len(truth_values)
                        p_false = 1 - p_true
                        dist_entropy = entropy([p_true, p_false]) if p_true > 0 and p_false > 0 else 0.0
                        
                        # Low entropy = high coherence (consistent truth values)
                        # High entropy = low coherence (mixed truth values)
                        coherence = 1.0 - (dist_entropy / 1.0)  # max entropy for binary is 1.0
                        
                        # Use amino acid to check entailment of possible conclusions
                        # Try to deduce which agent is being asked about
                        question = structure["question"].lower()
                        for agent in agents:
                            if agent.lower() in question:
                                # Check if we can deduce something about this agent
                                conclusion_var = var_map.get(f"{agent}_truthful")
                                if conclusion_var:
                                    # Create premise clauses (all our constraints)
                                    premise_clauses = clauses
                                    # Conclusion: agent is truthful
                                    conclusion_clause = [conclusion_var]
                                    
                                    # Use amino acid to check entailment
                                    entailment_result = check_entailment(premise_clauses, conclusion_clause)
                                    
                                    if entailment_result is True:
                                        computed_answer = f"{agent} tells the truth"
                                        confidence = 0.9
                                        reasoning = f"SAT entailment proves {agent} must be truthful"
                                        break
                                    elif entailment_result is False:
                                        # Check opposite conclusion
                                        conclusion_clause_neg = [-conclusion_var]
                                        entailment_result_neg = check_entailment(premise_clauses, conclusion_clause_neg)
                                        if entailment_result_neg is True:
                                            computed_answer = f"{agent} lies"
                                            confidence = 0.9
                                            reasoning = f"SAT entailment proves {agent} must be lying"
                                            break
                        
                        # If no specific entailment, use Bayesian update on coherence
                        if not computed_answer:
                            # Prior belief: random agent is truth-teller
                            prior = 0.5
                            # Likelihood: coherence supports consistency
                            likelihood = coherence
                            posterior = bayesian_update(prior, likelihood, false_positive=0.1)
                            
                            # Find agent with most mentions in question
                            question_agents = []
                            for agent in agents:
                                if agent.lower() in question:
                                    question_agents.append(agent)
                            
                            if question_agents:
                                target_agent = question_agents[0]
                                if posterior > 0.5:
                                    computed_answer = f"{target_agent} tells the truth"
                                else:
                                    computed_answer = f"{target_agent} lies"
                                confidence = abs(posterior - 0.5) * 2  # Convert to 0-1 scale
                                reasoning = f"Bayesian update with coherence {coherence:.2f} gives posterior {posterior:.2f}"
        
        # Fallback: Use modus ponens on extracted statements
        if not computed_answer and statements:
            # Create simple implication rules
            premises = []
            facts = set()
            
            for agent, policy in policies.items():
                for stmt in statements:
                    if agent.lower() in structure["raw"].lower() and stmt.lower() in structure["raw"].lower():
                        if policy == 'truth':
                            # If agent is truth-teller, then statement is true
                            premises.append((f"{agent}_truthful", stmt))
                            # We don't know if agent is truthful yet
                        elif policy == 'lie':
                            # If agent is liar, then statement is false
                            premises.append((f"{agent}_liar", f"not_{stmt}"))
            
            # Try to deduce something
            deduced = modus_ponens(premises, facts)
            
            # Use confidence from agreement of multiple deduction paths
            if deduced:
                confidence_scores = []
                for item in deduced:
                    # Simple heuristic: longer deductions are less confident
                    confidence_scores.append(1.0 / (len(item.split('_')) + 1))
                
                if confidence_scores:
                    agg_confidence = confidence_from_agreement(confidence_scores)
                    confidence = max(confidence, agg_confidence)
            
            # Default answer based on first agent in question
            question = structure["question"].lower()
            for agent in agents:
                if agent.lower() in question:
                    computed_answer = f"{agent} tells the truth"  # Default assumption
                    break
        
        # Final fallback
        if not computed_answer and agents:
            computed_answer = f"{agents[0]} tells the truth"
            confidence = 0.5
            reasoning = "Default fallback: first agent assumed truthful"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer or "", candidate))
            
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
        
        # Simple normalization to 0-1 range
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
        if not a and not b:
            return 0.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)