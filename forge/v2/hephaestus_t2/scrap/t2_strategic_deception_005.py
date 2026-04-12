import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, track_beliefs
from forge.amino_acids.nashpy_acids import find_equilibria, is_dominated


class ReasoningTool:
    """Cell biology x Nash equilibria - strategic deception"""

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
        """Parse prompt to find agents, their stated intentions, possible actions, and payoffs."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = []
        actions = {}
        payoffs = {}
        question = lines[-1] if lines else ""
        
        # Find agent names (capitalized words that appear before "says" or "claims")
        for line in lines:
            if "says" in line.lower() or "claims" in line.lower():
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in ["says", "claims"] and i > 0:
                        agent = words[i-1]
                        if agent[0].isupper() and agent not in agents:
                            agents.append(agent)
        
        # Find actions and payoffs using patterns like "X gets Y if Z"
        for line in lines:
            # Look for payoff patterns
            payoff_match = re.search(r'(\w+)\s+gets\s+([-\d]+)\s+if\s+(\w+)', line, re.IGNORECASE)
            if payoff_match:
                agent, value, condition = payoff_match.groups()
                if agent not in payoffs:
                    payoffs[agent] = {}
                payoffs[agent][condition] = int(value)
            
            # Look for action options
            action_match = re.search(r'(\w+)\s+can\s+(cooperate|defect|attack|retreat|lie|tell truth)', line, re.IGNORECASE)
            if action_match:
                agent, action = action_match.groups()
                if agent not in actions:
                    actions[agent] = []
                if action not in actions[agent]:
                    actions[agent].append(action)
        
        # If no structured payoffs found, look for numerical values near agent names
        if not payoffs:
            for line in lines:
                numbers = re.findall(r'[-\d]+', line)
                for agent in agents:
                    if agent in line and numbers:
                        if agent not in payoffs:
                            payoffs[agent] = {}
                        for num in numbers[:2]:  # Take first few numbers
                            payoffs[agent][f"outcome_{len(payoffs[agent])}"] = int(num)
        
        # Default actions if none found
        if not actions:
            for agent in agents:
                actions[agent] = ["cooperate", "defect"]
        
        return {
            "agents": agents,
            "actions": actions,
            "payoffs": payoffs,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use cell biology concepts (signaling pathways as game strategies) 
        and Nash equilibria to find optimal deceptive strategy."""
        agents = structure["agents"]
        actions = structure["actions"]
        payoffs = structure["payoffs"]
        
        if len(agents) < 2:
            # Fallback: use entropy on belief tracking
            computed_answer = self._fallback_reasoning(structure)
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Only one agent found, using fallback"
            }
        
        # Build payoff matrices from extracted data
        payoff_a, payoff_b, computed_answer = self._build_game_matrices(agents, actions, payoffs)
        
        # CRITICAL: Use Nash equilibrium analysis (amino acid)
        equilibria = find_equilibria(payoff_a, payoff_b)
        
        if equilibria:
            # CRITICAL: Use entropy to measure uncertainty in equilibrium strategies
            eq_probs = []
            for eq in equilibria:
                if isinstance(eq[0], (list, tuple)) and len(eq[0]) > 0:
                    eq_probs.extend(eq[0])
            if eq_probs:
                strategy_entropy = entropy(eq_probs)
            else:
                strategy_entropy = 1.0
            
            # CRITICAL: Use track_beliefs to model deceptive signaling
            # In cell biology, signaling molecules can misrepresent internal state
            observations = []
            for agent in agents:
                # Simulate deceptive observation: agent claims one thing but may do another
                observations.append((agent, "claims_cooperate", True))
                observations.append((agent, "actually_defects", False))
            
            belief_state = track_beliefs(agents, observations)
            
            # Determine which agent benefits from deception
            deception_benefits = {}
            for agent in agents:
                if agent in belief_state:
                    # CRITICAL: Use bayesian_update to model belief revision
                    prior = 0.5  # Initial trust
                    likelihood = 0.8 if "actually_defects" in [obs[1] for obs in observations if obs[0] == agent] else 0.2
                    posterior = bayesian_update(prior, likelihood, false_positive=0.1)
                    deception_benefits[agent] = posterior
            
            # CRITICAL: The computed answer depends on Nash equilibrium AND deception analysis
            if strategy_entropy > 0.7 and deception_benefits:
                # High entropy + deception benefit suggests deceptive strategy is optimal
                best_deceiver = max(deception_benefits.items(), key=lambda x: x[1])[0]
                computed_answer = best_deceiver
            elif equilibria and len(equilibria) > 0:
                # Use first equilibrium to determine answer
                first_eq = equilibria[0]
                if isinstance(first_eq[0], (list, tuple)) and len(first_eq[0]) > 0:
                    # Mixed strategy: agent with highest probability in equilibrium
                    max_prob_idx = max(range(len(first_eq[0])), key=lambda i: first_eq[0][i])
                    if max_prob_idx < len(agents):
                        computed_answer = agents[max_prob_idx]
                else:
                    # Pure strategy
                    computed_answer = agents[0] if first_eq[0] == 1 else agents[1]
            else:
                computed_answer = self._fallback_reasoning(structure)
        else:
            # No equilibria found, use fallback
            computed_answer = self._fallback_reasoning(structure)
        
        # CRITICAL: Final confidence depends on agreement between different reasoning paths
        confidence_scores = []
        if 'strategy_entropy' in locals():
            confidence_scores.append(1.0 - strategy_entropy)
        if 'deception_benefits' in locals() and computed_answer in deception_benefits:
            confidence_scores.append(deception_benefits[computed_answer])
        
        if confidence_scores:
            confidence = confidence_from_agreement(confidence_scores)
        else:
            confidence = 0.5
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Nash equilibrium analysis with cell biology signaling deception model"
        }

    def _build_game_matrices(self, agents, actions, payoffs):
        """Construct payoff matrices from extracted data."""
        # Default prisoner's dilemma if no payoffs extracted
        default_payoffs = {
            "cooperate": {"cooperate": 3, "defect": 0},
            "defect": {"cooperate": 5, "defect": 1}
        }
        
        payoff_a = []
        payoff_b = []
        
        if len(agents) >= 2:
            agent1_actions = actions.get(agents[0], ["cooperate", "defect"])
            agent2_actions = actions.get(agents[1], ["cooperate", "defect"])
            
            for a1 in agent1_actions:
                row_a = []
                row_b = []
                for a2 in agent2_actions:
                    # Try to use extracted payoffs
                    if agents[0] in payoffs and a2 in payoffs[agents[0]]:
                        payoff1 = payoffs[agents[0]][a2]
                    else:
                        payoff1 = default_payoffs.get(a1, {}).get(a2, 0)
                    
                    if agents[1] in payoffs and a1 in payoffs[agents[1]]:
                        payoff2 = payoffs[agents[1]][a1]
                    else:
                        payoff2 = default_payoffs.get(a2, {}).get(a1, 0)
                    
                    row_a.append(payoff1)
                    row_b.append(payoff2)
                
                payoff_a.append(row_a)
                payoff_b.append(row_b)
            
            # CRITICAL: Check if any strategy is dominated (amino acid)
            dominated_info = []
            for i in range(len(payoff_a)):
                dominated = is_dominated(payoff_a, i, player_is_row=True)
                dominated_info.append(dominated)
            
            # Determine computed answer based on dominance
            if any(dominated_info):
                # Choose action that is not dominated
                non_dominated_idx = [i for i, d in enumerate(dominated_info) if not d]
                if non_dominated_idx:
                    chosen_action = agent1_actions[non_dominated_idx[0]]
                    computed_answer = f"{agents[0]} should {chosen_action}"
                else:
                    computed_answer = agents[0]
            else:
                computed_answer = agents[0]
        else:
            payoff_a = [[3, 0], [5, 1]]
            payoff_b = [[3, 5], [0, 1]]
            computed_answer = agents[0] if agents else "Agent1"
        
        return payoff_a, payoff_b, computed_answer

    def _fallback_reasoning(self, structure: Dict[str, Any]) -> str:
        """Fallback reasoning using primitives when game analysis fails."""
        agents = structure["agents"]
        payoffs = structure["payoffs"]
        
        if not agents:
            return "No agent"
        
        # CRITICAL: Use entropy on payoff distributions
        entropy_values = []
        for agent in agents:
            if agent in payoffs:
                values = list(payoffs[agent].values())
                if values:
                    # Normalize to probabilities
                    total = sum(abs(v) for v in values)
                    if total > 0:
                        probs = [abs(v)/total for v in values]
                        agent_entropy = entropy(probs)
                        entropy_values.append((agent, agent_entropy))
        
        if entropy_values:
            # Agent with most uncertain payoffs (highest entropy) may be deceptive
            most_uncertain = max(entropy_values, key=lambda x: x[1])[0]
            return most_uncertain
        
        return agents[0]

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item["raw_score"] for item in scored]
        if max(scores) - min(scores) < 0.001:
            # All scores similar, differentiate slightly
            for i, item in enumerate(scored):
                item["score"] = item["raw_score"] + (i * 0.0001)
        else:
            # Normalize to [0, 1] range
            min_val = min(scores)
            max_val = max(scores)
            if max_val > min_val:
                for item in scored:
                    item["score"] = (item["raw_score"] - min_val) / (max_val - min_val)
            else:
                for item in scored:
                    item["score"] = item["raw_score"]
        
        return scored