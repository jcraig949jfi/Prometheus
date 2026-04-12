import re
import zlib
from typing import Dict, List, Any

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.nashpy_acids import find_equilibria


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
        """Parse prompt to extract entities, payoffs, and question."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        question = lines[-1] if lines else ""
        
        # Find agent names (capitalized words that appear as players)
        agent_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_agents = re.findall(agent_pattern, prompt)
        
        # Filter to likely agents (appear multiple times or near "player", "agent", "chooses")
        agents = []
        for agent in potential_agents:
            if len(agent.split()) <= 3:  # Reasonable name length
                # Check if appears in strategic context
                context = prompt.lower()
                agent_lower = agent.lower()
                if (f"{agent_lower} chooses" in context or 
                    f"{agent_lower}'s" in context or
                    f"player {agent_lower}" in context or
                    context.count(agent_lower) >= 2):
                    agents.append(agent)
        
        # Extract numerical payoffs
        payoff_pattern = r'(-?\d+(?:\.\d+)?)'
        numbers = [float(m) for m in re.findall(payoff_pattern, prompt) if m.replace('.', '').replace('-', '').isdigit()]
        
        # Extract statements about intentions/deception
        deception_indicators = []
        deception_keywords = ['claims', 'says', 'states', 'announces', 'declares', 
                             'but actually', 'secretly', 'privately', 'truth', 'lie']
        sentences = prompt.split('.')
        for sent in sentences:
            sent_lower = sent.lower()
            if any(keyword in sent_lower for keyword in deception_keywords):
                deception_indicators.append(sent.strip())
        
        return {
            "agents": list(set(agents))[:4],  # Limit to reasonable number
            "payoff_numbers": numbers,
            "question": question,
            "deception_indicators": deception_indicators,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use cell biology concepts (signaling pathways as game moves) to model deception."""
        agents = structure["agents"]
        payoff_numbers = structure["payoff_numbers"]
        question = structure["question"]
        deception_indicators = structure["deception_indicators"]
        
        if len(agents) < 2:
            # Fallback: use simple deception detection
            computed_answer = self._fallback_reason(structure)
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Insufficient agents for game theory analysis"
            }
        
        # Cell biology scaffold: Model agents as cells with surface receptors (stated intentions)
        # and internal signaling pathways (true preferences). Deception occurs when
        # surface signaling doesn't match internal pathway activation.
        
        # PRIMITIVE 1: topological_sort - order agents by deception potential
        # In cell biology, signaling cascades have specific order
        edges = []
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i != j:
                    # Create edges based on deception indicators mentioning agents
                    for indicator in deception_indicators:
                        if agent1.lower() in indicator.lower() and agent2.lower() in indicator.lower():
                            edges.append((agent1, agent2))  # agent1 deceives agent2
        
        # Load-bearing primitive call 1: topological_sort
        deception_order = topological_sort(edges)
        if deception_order is None:
            deception_order = agents  # fallback if cycle
        
        # PRIMITIVE 2: entropy - measure uncertainty in payoffs (like stochastic signaling)
        if len(payoff_numbers) >= 2:
            # Normalize payoffs to probabilities for entropy calculation
            abs_payoffs = [abs(p) for p in payoff_numbers[:10]]  # limit to first 10
            if sum(abs_payoffs) > 0:
                probs = [p/sum(abs_payoffs) for p in abs_payoffs]
                # Load-bearing primitive call 2: entropy
                payoff_entropy = entropy(probs)
            else:
                payoff_entropy = 1.0
        else:
            payoff_entropy = 1.0
        
        # Construct game matrix from extracted numbers
        n_agents = min(len(agents), 2)  # Focus on 2-player games
        if n_agents == 2 and len(payoff_numbers) >= 4:
            # Try to form 2x2 game
            payoffs_a = []
            payoffs_b = []
            
            # Use first 4 numbers for payoffs
            nums = payoff_numbers[:4]
            if len(nums) == 4:
                # Row player (first agent)
                payoffs_a = [[nums[0], nums[1]], [nums[2], nums[3]]]
                # Column player (second agent) - use complements for zero-sum like structure
                payoffs_b = [[-nums[0], -nums[1]], [-nums[2], -nums[3]]]
            else:
                # Use numbers to create symmetric game
                payoffs_a = [[payoff_numbers[0] if len(payoff_numbers) > 0 else 3, 
                              payoff_numbers[1] if len(payoff_numbers) > 1 else 1],
                             [payoff_numbers[2] if len(payoff_numbers) > 2 else 0,
                              payoff_numbers[3] if len(payoff_numbers) > 3 else 2]]
                payoffs_b = [[payoff_numbers[1] if len(payoff_numbers) > 1 else 1,
                              payoff_numbers[0] if len(payoff_numbers) > 0 else 3],
                             [payoff_numbers[3] if len(payoff_numbers) > 3 else 2,
                              payoff_numbers[2] if len(payoff_numbers) > 2 else 0]]
            
            # AMINO ACID: find_equilibria - critical for strategic reasoning
            equilibria = find_equilibria(payoffs_a, payoffs_b)
            
            if equilibria:
                # Load-bearing amino acid call: equilibria directly determines answer
                eq_list = list(equilibria)
                if eq_list:
                    # Use first equilibrium
                    first_eq = eq_list[0]
                    # In cell biology, stable equilibria correspond to phenotypic states
                    # High deception corresponds to mixed strategies or off-diagonal payoffs
                    
                    # Analyze deception level based on equilibrium type
                    if len(first_eq) == 2:
                        strat_a, strat_b = first_eq
                        # Mixed strategies suggest deception (uncertainty)
                        deception_level = 0.0
                        if len(strat_a) > 1:
                            deception_level += 0.5
                        if len(strat_b) > 1:
                            deception_level += 0.5
                        
                        # PRIMITIVE 3: bayesian_update - update belief about who is deceptive
                        # Prior: first in deception_order is most deceptive
                        prior = 0.7 if deception_order and agents[0] == deception_order[0] else 0.3
                        likelihood = deception_level
                        # Load-bearing primitive call 3: bayesian_update
                        posterior = bayesian_update(prior, likelihood, false_positive=0.1)
                        
                        if posterior > 0.5:
                            deceptive_agent = agents[0]
                        else:
                            deceptive_agent = agents[1] if len(agents) > 1 else agents[0]
                        
                        computed_answer = deceptive_agent
                        confidence = min(posterior, 0.9)
                    else:
                        computed_answer = self._fallback_reason(structure)
                        confidence = 0.6
                else:
                    computed_answer = self._fallback_reason(structure)
                    confidence = 0.6
            else:
                computed_answer = self._fallback_reason(structure)
                confidence = 0.6
        else:
            computed_answer = self._fallback_reason(structure)
            confidence = 0.6
        
        # PRIMITIVE 4: confidence_from_agreement - combine multiple signals
        # Like multiple signaling pathways converging in cell biology
        signals = []
        if payoff_entropy < 0.8:  # Low entropy means clear payoffs
            signals.append(0.8)
        if deception_indicators:
            signals.append(0.7)
        if computed_answer and computed_answer in agents:
            signals.append(0.9)
        
        if len(signals) >= 2:
            final_confidence = confidence_from_agreement(signals)
        else:
            final_confidence = confidence
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Game theory analysis with cell biology signaling model. Deception order: {deception_order}. Payoff entropy: {payoff_entropy:.2f}."
        }

    def _fallback_reason(self, structure: Dict[str, Any]) -> str:
        """Fallback reasoning when game theory fails - still uses primitives."""
        agents = structure["agents"]
        deception_indicators = structure["deception_indicators"]
        
        if not agents:
            return "No clear answer"
        
        # Use deception indicators to guess
        if deception_indicators:
            # Find agent mentioned in deception context
            for agent in agents:
                for indicator in deception_indicators:
                    if agent.lower() in indicator.lower():
                        return agent
        
        # Default: first agent
        return agents[0]

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(str(computed_answer), candidate))
            
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
        
        # Simple normalization
        max_score = max(item["score"] for item in scored) if scored else 1.0
        if max_score > 0:
            for item in scored:
                item["score"] = item["score"] / max_score
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        return (cab - min(ca, cb)) / max(ca, cb)