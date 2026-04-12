import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    expected_value,
    topological_sort,
    solve_constraints
)
from forge.amino_acids.nashpy_acids import find_equilibria, is_dominated
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """equilibrium_chemistry x nashpy_acids - strategic_deception"""

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
        """Extract agents, actions, payoffs, and question from prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        # Find agents (typically named entities)
        agents = []
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        for line in lines:
            matches = re.findall(agent_pattern, line)
            for match in matches:
                if len(match.split()) <= 3 and match not in agents:
                    agents.append(match)
        
        # Extract numerical payoffs
        payoffs = []
        payoff_pattern = r'(-?\d+(?:\.\d+)?)'
        for line in lines:
            numbers = re.findall(payoff_pattern, line)
            if len(numbers) >= 2:
                payoffs.extend([float(num) for num in numbers])
        
        # Extract actions/strategies
        actions = {}
        action_keywords = ['cooperate', 'defect', 'attack', 'defend', 'lie', 'tell truth']
        for line in lines:
            for keyword in action_keywords:
                if keyword in line.lower():
                    # Find which agent this action belongs to
                    for agent in agents:
                        if agent in line:
                            if agent not in actions:
                                actions[agent] = []
                            if keyword not in actions[agent]:
                                actions[agent].append(keyword)
        
        # Extract question
        question = ""
        question_indicators = ['?', 'which', 'what', 'how', 'should', 'would']
        for line in lines[-3:]:  # Check last few lines
            if any(indicator in line.lower() for indicator in question_indicators):
                question = line
                break
        
        # Try to extract payoff matrix structure
        matrix_data = []
        for line in lines:
            if re.search(r'[\[\]\(\)]', line) and any(str(num) in line for num in payoffs[:4]):
                # Likely a payoff matrix line
                nums = re.findall(payoff_pattern, line)
                if len(nums) >= 2:
                    matrix_data.append([float(num) for num in nums])
        
        return {
            "agents": agents[:2] if len(agents) >= 2 else ["Player1", "Player2"],
            "payoffs": payoffs,
            "actions": actions,
            "question": question,
            "matrix_data": matrix_data,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use equilibrium chemistry framework to analyze strategic deception.
        
        Equilibrium chemistry concept: Reactions reach equilibrium when forward and 
        reverse rates balance. Here, strategic interactions reach Nash equilibrium 
        when no player can unilaterally improve payoff. Deception shifts the 
        apparent equilibrium by altering perceived payoffs.
        """
        agents = structure["agents"]
        payoffs = structure["payoffs"]
        actions = structure["actions"]
        question = structure["question"]
        
        # Default computed answer
        computed_answer = agents[0] if agents else "Unknown"
        confidence = 0.5
        reasoning = "Fallback: no strategic analysis possible"
        
        # Build payoff matrices using extracted data
        if len(payoffs) >= 4:
            # Try to construct 2x2 game matrices
            payoff_a = []
            payoff_b = []
            
            if len(payoffs) == 4:
                # Simple 2x2 game
                payoff_a = [[payoffs[0], payoffs[1]], [payoffs[2], payoffs[3]]]
                payoff_b = [[payoffs[1], payoffs[0]], [payoffs[3], payoffs[2]]]  # Symmetric assumption
            elif len(payoffs) >= 8:
                # Larger game, take first 4 for each player
                payoff_a = [[payoffs[0], payoffs[1]], [payoffs[2], payoffs[3]]]
                payoff_b = [[payoffs[4], payoffs[5]], [payoffs[6], payoffs[7]]]
            
            if payoff_a and payoff_b:
                # CRITICAL PATH 1: Find Nash equilibria using amino acid
                equilibria = find_equilibria(payoff_a, payoff_b)
                
                if equilibria:
                    # CRITICAL PATH 2: Check for dominated strategies
                    dominated_a = False
                    dominated_b = False
                    for i in range(len(payoff_a)):
                        if is_dominated(payoff_a, i, player_is_row=True):
                            dominated_a = True
                    for i in range(len(payoff_b[0])):
                        if is_dominated(payoff_b, i, player_is_row=False):
                            dominated_b = True
                    
                    # CRITICAL PATH 3: Use entropy to measure uncertainty in equilibrium selection
                    if len(equilibria) > 1:
                        # Multiple equilibria - compute entropy of equilibrium distribution
                        eq_probs = [1.0/len(equilibria)] * len(equilibria)
                        strategy_entropy = entropy(eq_probs)
                        
                        # CRITICAL PATH 4: Bayesian update based on deception cues
                        prior_deception = 0.3  # Base rate of deception
                        deception_likelihood = 0.7 if dominated_a or dominated_b else 0.3
                        deception_posterior = bayesian_update(prior_deception, deception_likelihood)
                        
                        # CRITICAL PATH 5: Expected value of different strategies
                        # Convert equilibria to expected payoffs
                        expected_payoffs = []
                        for eq in equilibria:
                            if isinstance(eq[0], (list, tuple)) and isinstance(eq[1], (list, tuple)):
                                # Mixed strategy equilibrium
                                row_probs, col_probs = eq[0], eq[1]
                                # Calculate expected payoff for player 1
                                exp_val = 0.0
                                for i in range(len(row_probs)):
                                    for j in range(len(col_probs)):
                                        exp_val += row_probs[i] * col_probs[j] * payoff_a[i][j]
                                expected_payoffs.append(exp_val)
                        
                        if expected_payoffs:
                            # CRITICAL PATH 6: Confidence from agreement among expected values
                            if len(expected_payoffs) > 1:
                                confidence_val = confidence_from_agreement(expected_payoffs)
                            else:
                                confidence_val = 0.8
                            
                            # Determine which agent benefits from deception
                            # Look for cues in the question
                            if "deceive" in question.lower() or "lie" in question.lower():
                                # Agent with dominated strategy might be deceptive
                                if dominated_a and not dominated_b:
                                    computed_answer = agents[0] if len(agents) > 0 else "Player1"
                                elif dominated_b and not dominated_a:
                                    computed_answer = agents[1] if len(agents) > 1 else "Player2"
                                else:
                                    # Use expected payoff to determine
                                    max_idx = expected_payoffs.index(max(expected_payoffs))
                                    computed_answer = agents[max_idx % len(agents)] if agents else "Player1"
                            else:
                                # Standard equilibrium analysis
                                # Use topological sort of strategy dependencies if we can extract them
                                strategy_edges = []
                                if actions:
                                    for agent in actions:
                                        for action in actions[agent]:
                                            strategy_edges.append((agent, action))
                                
                                if strategy_edges:
                                    # CRITICAL PATH 7: Topological sort of strategic dependencies
                                    sorted_strategies = topological_sort(strategy_edges)
                                    if sorted_strategies:
                                        computed_answer = sorted_strategies[0] if sorted_strategies else agents[0]
                                
                                # Fallback to highest expected payoff
                                if computed_answer == agents[0] and expected_payoffs:
                                    max_idx = expected_payoffs.index(max(expected_payoffs))
                                    computed_answer = agents[max_idx % len(agents)] if agents else "Player1"
                            
                            confidence = min(0.95, confidence_val * (1.0 - strategy_entropy))
                            reasoning = f"Game theory analysis: {len(equilibria)} Nash equilibrium(s) found. "
                            reasoning += f"Dominated strategies: Player1={dominated_a}, Player2={dominated_b}. "
                            reasoning += f"Deception posterior probability: {deception_posterior:.2f}"
        
        # Fallback if game analysis failed but we have constraint information
        if computed_answer == agents[0] and "?" in question:
            # Try constraint satisfaction approach
            variables = agents if agents else ["A", "B"]
            domains = {var: ["cooperate", "defect", "deceive"] for var in variables}
            
            # Constraints based on extracted actions
            constraints = []
            if actions:
                for agent in actions:
                    if actions[agent]:
                        # Constraint: agent must choose from available actions
                        def make_action_constraint(agt, acts):
                            def constraint(assignment):
                                return assignment[agt] in acts
                            return constraint
                        constraints.append(([agent], make_action_constraint(agent, actions[agent])))
            
            if constraints:
                # CRITICAL PATH 8: Solve constraint satisfaction problem
                solution = solve_constraints(variables, domains, constraints)
                if solution:
                    computed_answer = list(solution.keys())[0]
                    confidence = 0.7
                    reasoning = f"Constraint satisfaction solution: {solution}"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning,
            "raw_structure": structure
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        reasoning_text = reasoning_result["reasoning"]
        
        def ncd(a: str, b: str) -> float:
            """Normalized Compression Distance."""
            if not a or not b:
                return 1.0
            ca = len(zlib.compress(a.encode()))
            cb = len(zlib.compress(b.encode()))
            cab = len(zlib.compress((a + " " + b).encode()))
            if max(ca, cb) == 0:
                return 1.0
            return (cab - min(ca, cb)) / max(ca, cb)
        
        scored = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback 1: NCD with computed answer
                ncd1 = ncd(computed_answer, candidate)
                # Fallback 2: NCD with reasoning text (longer, more semantic)
                ncd2 = ncd(reasoning_text, candidate)
                base_score = 1.0 - min(ncd1, ncd2)
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            scored.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            normalized = [(s - min(scores)) / (max(scores) - min(scores)) for s in scores]
        else:
            normalized = [0.5] * len(scores)
        
        # Apply softmax for probabilistic interpretation
        exp_scores = [2.71828 ** s for s in normalized]
        total = sum(exp_scores)
        if total > 0:
            calibrated_scores = [e / total for e in exp_scores]
        else:
            calibrated_scores = normalized
        
        # Update scores
        for i, item in enumerate(scored):
            item["score"] = calibrated_scores[i]
        
        return scored