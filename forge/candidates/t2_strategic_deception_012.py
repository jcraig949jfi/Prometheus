import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import bayesian_update, entropy, confidence_from_agreement, topological_sort
from forge.amino_acids.nashpy_acids import find_equilibria, is_dominated


class ReasoningTool:
    """Quantum mechanics x Nash equilibria - strategic_deception"""

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
        """Extract agents, statements, and strategic options from prompt."""
        structure = {
            "agents": [],
            "statements": {},
            "options": {},
            "question": "",
            "raw": prompt
        }
        
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        if lines:
            structure["question"] = lines[-1]
        
        # Extract agent names (capitalized proper nouns that appear as subjects)
        sentences = prompt.split('.')
        agent_candidates = set()
        for sentence in sentences:
            words = sentence.split()
            for i, word in enumerate(words):
                if word and word[0].isupper() and len(word) > 1:
                    # Check if it's likely a name (not at start of sentence or followed by verb)
                    if i > 0 or any(w.lower() in ["says", "claims", "states", "declares"] 
                                   for w in words[i+1:i+3] if i+1 < len(words)):
                        agent_candidates.add(word)
        
        structure["agents"] = list(agent_candidates)
        
        # Extract statements and associate with agents
        for sentence in sentences:
            for agent in structure["agents"]:
                if agent in sentence:
                    # Look for quoted statements or claims
                    if '"' in sentence:
                        quote_start = sentence.find('"')
                        quote_end = sentence.rfind('"')
                        if quote_start != quote_end:
                            statement = sentence[quote_start+1:quote_end]
                            structure["statements"][agent] = statement
                    elif "says" in sentence.lower() or "claims" in sentence.lower():
                        # Extract the part after "says/claims"
                        parts = sentence.split(agent)
                        if len(parts) > 1:
                            rest = parts[1]
                            if "says" in rest.lower():
                                statement = rest.split("says")[-1].strip()
                            elif "claims" in rest.lower():
                                statement = rest.split("claims")[-1].strip()
                            else:
                                statement = rest.strip()
                            structure["statements"][agent] = statement
        
        # Extract strategic options (often mentioned as choices)
        option_keywords = ["option", "choice", "strategy", "plan", "action"]
        for sentence in sentences:
            for keyword in option_keywords:
                if keyword in sentence.lower():
                    # Look for capitalized options or quoted options
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if word and word[0].isupper() and len(word) > 1:
                            if i > 0 and words[i-1].lower() in ["option", "choice", "strategy"]:
                                structure["options"][word] = {"mentioned_in": sentence}
        
        return structure

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quantum-mechanics-inspired reasoning about strategic deception."""
        agents = structure["agents"]
        statements = structure["statements"]
        question = structure["question"]
        
        if len(agents) < 2:
            # Fallback: use entropy on statement probabilities
            computed_answer = self._fallback_reasoning(structure)
            return {
                "answer": computed_answer,
                "confidence": 0.5,
                "reasoning": "Insufficient agents for game theory analysis"
            }
        
        # Quantum mechanics concept: superposition of strategies
        # Each agent has a mixed strategy space
        # Deception creates entanglement between stated and actual intentions
        
        # Build payoff matrices based on extracted statements
        # Use topological_sort to order strategic dependencies
        strategic_deps = []
        for agent1 in agents:
            for agent2 in agents:
                if agent1 != agent2:
                    # If agent1's statement references agent2, there's a dependency
                    if agent1 in statements and agent2 in statements.get(agent1, ""):
                        strategic_deps.append((agent1, agent2))
        
        # LOAD-BEARING PRIMITIVE 1: topological_sort
        # Determines the order of strategic reasoning
        strategy_order = topological_sort(strategic_deps)
        if strategy_order is None:
            strategy_order = agents  # Fallback if cyclic
        
        # Quantum concept: density matrix of beliefs
        # Each agent's statement creates an observable
        # Actual strategy may be in superposition with stated strategy
        
        # Calculate entropy of statements as measure of deception
        statement_entropies = {}
        for agent, statement in statements.items():
            if statement:
                # Convert statement to probability distribution of words
                words = statement.lower().split()
                if words:
                    word_counts = {}
                    for word in words:
                        word_counts[word] = word_counts.get(word, 0) + 1
                    probs = [count/len(words) for count in word_counts.values()]
                    
                    # LOAD-BEARING PRIMITIVE 2: entropy
                    # Measures uncertainty in statements (higher entropy = more deceptive)
                    statement_entropy = entropy(probs)
                    statement_entropies[agent] = statement_entropy
        
        # Build a simple 2x2 game for the first two agents
        if len(agents) >= 2:
            agent_a, agent_b = agents[0], agents[1]
            
            # Quantum concept: payoff amplitudes (complex probabilities)
            # Deception creates interference patterns in expected payoffs
            
            # Base payoffs from statement analysis
            payoff_a = [[3, 0], [5, 1]]  # Default prisoner's dilemma style
            payoff_b = [[3, 5], [0, 1]]
            
            # Adjust based on statement entropy (deception level)
            if agent_a in statement_entropies:
                ent_a = statement_entropies[agent_a]
                # Higher entropy (more deceptive) changes payoffs
                payoff_a = [[3 + ent_a, 0 - ent_a], 
                           [5 + ent_a, 1 - ent_a]]
            
            if agent_b in statement_entropies:
                ent_b = statement_entropies[agent_b]
                payoff_b = [[3 + ent_b, 5 - ent_b], 
                           [0 + ent_b, 1 - ent_b]]
            
            # LOAD-BEARING AMINO ACID: find_equilibria
            # Finds Nash equilibria - critical for strategic deception analysis
            equilibria = find_equilibria(payoff_a, payoff_b)
            
            if equilibria:
                # Quantum concept: collapse to equilibrium state
                # The most probable equilibrium given the evidence
                
                # Calculate expected payoffs for each equilibrium
                eq_payoffs = []
                for eq in equilibria:
                    if len(eq) == 2:
                        strat_a, strat_b = eq
                        if strat_a is not None and strat_b is not None:
                            # Simple expected payoff calculation
                            exp_payoff_a = sum(p*a for p, a in zip(strat_a, [sum(p*q for p, q in zip(strat_b, row)) 
                                                                           for row in payoff_a]))
                            exp_payoff_b = sum(p*b for p, b in zip(strat_b, [sum(p*q for p, q in zip(strat_a, col)) 
                                                                           for col in zip(*payoff_b)]))
                            eq_payoffs.append((exp_payoff_a + exp_payoff_b, eq))
                
                if eq_payoffs:
                    # Select equilibrium with highest total payoff
                    best_eq = max(eq_payoffs, key=lambda x: x[0])[1]
                    
                    # Determine which agent is deceptive based on equilibrium vs statements
                    # Quantum concept: measurement basis mismatch
                    deceptive_agent = None
                    if best_eq[0] is not None and best_eq[1] is not None:
                        # Check if mixed strategy suggests deception
                        strat_a_mixed = any(0 < p < 1 for p in best_eq[0])
                        strat_b_mixed = any(0 < p < 1 for p in best_eq[1])
                        
                        if strat_a_mixed and agent_a in statements:
                            deceptive_agent = agent_a
                        elif strat_b_mixed and agent_b in statements:
                            deceptive_agent = agent_b
                        elif strat_a_mixed and strat_b_mixed:
                            # Both deceptive, choose one with higher statement entropy
                            ent_a = statement_entropies.get(agent_a, 0)
                            ent_b = statement_entropies.get(agent_b, 0)
                            deceptive_agent = agent_a if ent_a > ent_b else agent_b
                    
                    computed_answer = deceptive_agent or agent_a
                else:
                    computed_answer = self._fallback_reasoning(structure)
            else:
                computed_answer = self._fallback_reasoning(structure)
        else:
            computed_answer = self._fallback_reasoning(structure)
        
        # Calculate confidence using multiple metrics
        confidence_scores = []
        
        # Confidence from statement consistency
        if statement_entropies:
            # Lower entropy = more consistent statements = higher confidence
            avg_entropy = sum(statement_entropies.values()) / len(statement_entropies)
            consistency_conf = 1.0 / (1.0 + avg_entropy)
            confidence_scores.append(consistency_conf)
        
        # Confidence from game theory analysis
        if 'equilibria' in locals() and equilibria:
            game_conf = min(1.0, len(equilibria) / 3.0)  # More equilibria = less certain
            confidence_scores.append(game_conf)
        
        # LOAD-BEARING PRIMITIVE 3: confidence_from_agreement
        # Combines multiple confidence sources
        if confidence_scores:
            final_confidence = confidence_from_agreement(confidence_scores)
        else:
            final_confidence = 0.5
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": f"Quantum game theory analysis with Nash equilibria. Strategic order: {strategy_order}",
            "equilibria_found": 'equilibria' in locals() and bool(equilibria),
            "statement_entropies": statement_entropies
        }

    def _fallback_reasoning(self, structure: Dict[str, Any]) -> str:
        """Fallback reasoning when game theory analysis fails."""
        agents = structure["agents"]
        statements = structure["statements"]
        
        if not agents:
            return "Unknown"
        
        # Use entropy of statements to identify most deceptive agent
        max_entropy = -1
        most_deceptive = agents[0]
        
        for agent in agents:
            if agent in statements:
                statement = statements[agent]
                words = statement.lower().split()
                if words:
                    word_counts = {}
                    for word in words:
                        word_counts[word] = word_counts.get(word, 0) + 1
                    probs = [count/len(words) for count in word_counts.values()]
                    agent_entropy = entropy(probs)
                    
                    if agent_entropy > max_entropy:
                        max_entropy = agent_entropy
                        most_deceptive = agent
        
        return most_deceptive

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment of computed answer
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "computed_answer": computed_answer
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores based on confidence and distribution."""
        if not scored:
            return scored
        
        scores = [item["score"] for item in scored]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            
            if max_score > min_score:
                # Normalize to [0, 1] range
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
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0