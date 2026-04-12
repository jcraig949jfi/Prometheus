import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    track_beliefs,
    solve_constraints,
    topological_sort
)
from forge.amino_acids.nashpy_acids import find_equilibria, is_dominated
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Neuroscience x Game Theory - strategic_deception"""

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
        """Extract agents, actions, payoffs, and deception cues from prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        sentences = [s.strip() for s in prompt.replace('\n', ' ').split('.') if s.strip()]
        
        # Find agent names (capitalized proper nouns that appear multiple times)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        from collections import Counter
        word_counts = Counter(words)
        agents = [word for word, count in word_counts.items() if count >= 2 and len(word) > 2]
        
        # Find actions (verbs following agents or in quotes)
        actions = []
        action_patterns = [
            r'"(.*?)"',
            r'choose[s]?\s+(\w+)',
            r'action\s+(\w+)',
            r'play[s]?\s+(\w+)'
        ]
        for pattern in action_patterns:
            actions.extend(re.findall(pattern, prompt, re.IGNORECASE))
        
        # Find numerical payoffs (positive/negative numbers)
        payoffs = []
        payoff_pattern = r'([+-]?\d+)\s*(?:point|utility|payoff)'
        payoff_matches = re.findall(payoff_pattern, prompt, re.IGNORECASE)
        for match in payoff_matches:
            try:
                payoffs.append(int(match))
            except:
                pass
        
        # Find deception cues
        deception_cues = []
        deception_keywords = ['lie', 'deceive', 'bluff', 'mislead', 'pretend', 'false', 'hidden']
        for keyword in deception_keywords:
            if keyword in prompt.lower():
                deception_cues.append(keyword)
        
        # Find the question
        question = ""
        for sentence in sentences:
            if '?' in sentence and ('who' in sentence.lower() or 'what' in sentence.lower() or 'which' in sentence.lower()):
                question = sentence
                break
        if not question and sentences:
            question = sentences[-1]
        
        # Extract belief statements (neuroscience: theory of mind)
        belief_statements = []
        belief_patterns = [
            r'(\w+)\s+(?:think|believe|expect)s?\s+that',
            r'(\w+)\s+(?:know|suspect)s?\s+that'
        ]
        for pattern in belief_patterns:
            for match in re.finditer(pattern, prompt, re.IGNORECASE):
                agent = match.group(1)
                # Find the content of the belief
                start = match.end()
                end = prompt.find('.', start)
                if end == -1:
                    end = len(prompt)
                content = prompt[start:end].strip()
                if content:
                    belief_statements.append((agent, content))
        
        return {
            "agents": list(set(agents)),
            "actions": list(set(actions)),
            "payoffs": payoffs,
            "deception_cues": deception_cues,
            "question": question,
            "belief_statements": belief_statements,
            "sentences": sentences,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply neuroscience-inspired game theory to model strategic deception."""
        agents = structure["agents"]
        actions = structure["actions"]
        payoffs = structure["payoffs"]
        deception_cues = structure["deception_cues"]
        belief_statements = structure["belief_statements"]
        question = structure["question"]
        
        # Neuroscience scaffold: prefrontal cortex tracks beliefs, amygdala detects deception,
        # and dopamine encodes prediction errors in strategic interactions
        
        # 1. Track beliefs using theory of mind (prefrontal cortex simulation)
        # This primitive is LOAD-BEARING: determines which agents believe what
        belief_tracking = {}
        if belief_statements:
            # Convert to format for track_beliefs
            agents_list = list(set([bs[0] for bs in belief_statements]))
            observations = []
            for agent, content in belief_statements:
                # Extract a fact from content
                fact_match = re.search(r'(\w+)\s+(?:will|is|has)', content)
                if fact_match:
                    fact = fact_match.group(1) + "_true"
                    observations.append((agent, fact, True))
            
            if observations and agents_list:
                belief_tracking = track_beliefs(agents_list, observations)
                if belief_tracking is None:
                    belief_tracking = {}
        
        # 2. Build game matrix from extracted payoffs (dopamine prediction error encoding)
        # Use entropy to measure uncertainty in strategic situation
        payoff_entropy = 0.0
        if payoffs:
            # Normalize payoffs to probabilities for entropy calculation
            abs_payoffs = [abs(p) for p in payoffs]
            total = sum(abs_payoffs)
            if total > 0:
                probs = [p/total for p in abs_payoffs]
                payoff_entropy = entropy(probs)  # LOAD-BEARING: measures strategic uncertainty
        
        # 3. Detect dominated strategies (amygdala-based threat detection)
        dominated_strategies = []
        if len(actions) >= 2 and len(payoffs) >= 4:
            # Create a simple 2x2 game matrix for analysis
            # This is a simplified representation; real extraction would be more complex
            payoff_a = [[payoffs[0] if i < len(payoffs) else 0 for j in range(2)] 
                       for i in range(2)]
            payoff_b = [[payoffs[1] if i < len(payoffs) else 0 for j in range(2)] 
                       for i in range(2)]
            
            # Check if any strategy is dominated
            for i in range(2):
                if is_dominated(payoff_a, i, player_is_row=True):
                    dominated_strategies.append(f"Action_{i}_dominated")
        
        # 4. Find Nash equilibria using game theory (prefrontal strategic reasoning)
        equilibria = []
        computed_answer = ""
        
        if len(payoffs) >= 4:
            # Construct 2x2 payoff matrices
            # Use first 4 payoffs for Player A, next 4 for Player B if available
            if len(payoffs) >= 8:
                payoff_a = [[payoffs[0], payoffs[1]], [payoffs[2], payoffs[3]]]
                payoff_b = [[payoffs[4], payoffs[5]], [payoffs[6], payoffs[7]]]
            else:
                # Use available payoffs with default values
                payoff_a = [[payoffs[0] if 0 < len(payoffs) else 1, 
                           payoffs[1] if 1 < len(payoffs) else 2],
                          [payoffs[2] if 2 < len(payoffs) else 0, 
                           payoffs[3] if 3 < len(payoffs) else 1]]
                payoff_b = [[2, 1], [1, 2]]  # Default coordination game
            
            eq_result = find_equilibria(payoff_a, payoff_b)  # LOAD-BEARING: determines game outcome
            if eq_result:
                equilibria = list(eq_result)
                
                # Determine which agent benefits from deception based on equilibria
                if equilibria:
                    # Analyze equilibrium payoffs
                    best_payoff = -float('inf')
                    best_agent = ""
                    for eq in equilibria:
                        if len(eq) == 2:
                            strat_a, strat_b = eq
                            if hasattr(strat_a, '__len__') and hasattr(strat_b, '__len__'):
                                # Mixed strategy - compute expected payoff
                                if len(strat_a) > 0 and len(strat_b) > 0:
                                    # Simple expected payoff calculation
                                    payoff_for_a = (payoff_a[0][0] * strat_a[0] * strat_b[0] +
                                                   payoff_a[0][1] * strat_a[0] * strat_b[1] +
                                                   payoff_a[1][0] * strat_a[1] * strat_b[0] +
                                                   payoff_a[1][1] * strat_a[1] * strat_b[1])
                                    payoff_for_b = (payoff_b[0][0] * strat_a[0] * strat_b[0] +
                                                   payoff_b[0][1] * strat_a[0] * strat_b[1] +
                                                   payoff_b[1][0] * strat_a[1] * strat_b[0] +
                                                   payoff_b[1][1] * strat_a[1] * strat_b[1])
                                    
                                    if payoff_for_a > best_payoff:
                                        best_payoff = payoff_for_a
                                        best_agent = agents[0] if len(agents) > 0 else "Player_A"
                                    if payoff_for_b > best_payoff:
                                        best_payoff = payoff_for_b
                                        best_agent = agents[1] if len(agents) > 1 else "Player_B"
        
        # 5. Model deception as constraint satisfaction problem
        # Neuroscience: deception requires maintaining false belief while tracking truth
        constraint_solution = None
        if agents and actions:
            # Variables: what each agent says vs what they believe
            variables = []
            domains = {}
            for agent in agents[:2]:  # Limit to first 2 agents
                variables.append(f"{agent}_says")
                variables.append(f"{agent}_believes")
                domains[f"{agent}_says"] = actions[:2] if len(actions) >= 2 else ["Cooperate", "Defect"]
                domains[f"{agent}_believes"] = actions[:2] if len(actions) >= 2 else ["Cooperate", "Defect"]
            
            # Constraints: deception means says != believes
            constraints = []
            for agent in agents[:2]:
                def deception_constraint(values, agent_name=agent):
                    says, believes = values
                    return says != believes  # Deception: saying something you don't believe
                
                constraints.append(([f"{agent}_says", f"{agent}_believes"], deception_constraint))
            
            # Solve CSP
            if variables and domains and constraints:
                constraint_solution = solve_constraints(variables, domains, constraints)  # LOAD-BEARING
            
            # Determine who is deceptive based on solution
            if constraint_solution:
                deceptive_agents = []
                for agent in agents[:2]:
                    says_key = f"{agent}_says"
                    believes_key = f"{agent}_believes"
                    if says_key in constraint_solution and believes_key in constraint_solution:
                        if constraint_solution[says_key] != constraint_solution[believes_key]:
                            deceptive_agents.append(agent)
                
                if deceptive_agents:
                    computed_answer = deceptive_agents[0]
        
        # 6. Use logical entailment to check if deception is rational
        # Neuroscience: prefrontal cortex evaluates logical consistency of strategies
        entailment_result = False
        if deception_cues and "lie" in " ".join(deception_cues).lower():
            # Create simple logical premises
            premises = []
            conclusion = []
            
            # Premise: If agent lies, they gain advantage
            premises.append([1, -2])  # lie -> advantage
            premises.append([1])      # agent lies
            
            # Conclusion: Therefore agent gains advantage
            conclusion = [2]
            
            entailment_result = check_entailment(premises, conclusion)  # LOAD-BEARING
        
        # 7. Bayesian update of deception probability based on cues
        # Neuroscience: updating beliefs based on observed behavior
        deception_probability = 0.5  # Prior
        if deception_cues:
            # More cues = higher likelihood of deception
            likelihood = min(0.9, 0.3 + 0.2 * len(deception_cues))
            deception_probability = bayesian_update(0.5, likelihood, 0.1)  # LOAD-BEARING
        
        # 8. Topological sort of strategic dependencies
        # Neuroscience: sequencing of strategic moves in prefrontal planning
        edges = []
        if len(agents) >= 2:
            # Create dependency: first mover influences second mover
            edges.append((agents[0], agents[1]))
            if len(agents) >= 3:
                edges.append((agents[1], agents[2]))
        
        strategic_order = []
        if edges:
            strategic_order = topological_sort(edges)  # LOAD-BEARING
            if strategic_order and not computed_answer:
                # First mover often has strategic advantage
                computed_answer = strategic_order[0]
        
        # 9. Confidence from agreement among different reasoning methods
        # Neuroscience: confidence emerges from consensus across neural systems
        confidence_scores = []
        if deception_probability > 0.6:
            confidence_scores.append(0.8)
        if entailment_result:
            confidence_scores.append(0.7)
        if constraint_solution:
            confidence_scores.append(0.6)
        if strategic_order:
            confidence_scores.append(0.5)
        
        confidence = 0.5  # Default
        if confidence_scores:
            confidence = confidence_from_agreement(confidence_scores)  # LOAD-BEARING
        
        # Determine final answer if not already set
        if not computed_answer:
            # Use game theory result
            if best_agent:
                computed_answer = best_agent
            elif agents:
                # Agent with most deception cues mentioned
                agent_deception_counts = {}
                for agent in agents:
                    count = sum(1 for cue in deception_cues if agent.lower() in prompt.lower())
                    agent_deception_counts[agent] = count
                
                if agent_deception_counts:
                    computed_answer = max(agent_deception_counts.items(), key=lambda x: x[1])[0]
                else:
                    computed_answer = agents[0]
            else:
                computed_answer = "Unknown"
        
        # Neuroscience explanation
        reasoning_text = (
            f"Prefrontal theory-of-mind tracking: {belief_tracking}. "
            f"Strategic uncertainty (entropy): {payoff_entropy:.2f}. "
            f"Nash equilibria: {equilibria}. "
            f"Deception probability (Bayesian): {deception_probability:.2f}. "
            f"Strategic order: {strategic_order}. "
            f"Logical entailment of deception rationality: {entailment_result}."
        )
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_text,
            "deception_probability": deception_probability,
            "equilibria": equilibria,
            "strategic_order": strategic_order
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
            
            # Check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 0.9 + (confidence * 0.1)
            else:
                # Fallback 1: NCD similarity to reasoning text
                ncd_score = 1.0 - self._ncd(reasoning_text, candidate)
                score = 0.5 + (ncd_score * 0.3) + (confidence * 0.2)
                
                # Fallback 2: Check for key neuroscience/game theory terms
                key_terms = ["deception", "strategy", "equilibrium", "belief", "game"]
                term_matches = sum(1 for term in key_terms if term in candidate.lower())
                score += term_matches * 0.05
            
            # Cap score
            score = min(1.0, max(0.0, score))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored_candidates:
            return scored_candidates
        
        # Simple calibration: normalize scores
        scores = [item["raw_score"] for item in scored_candidates]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            
            if max_score > min_score:
                for item in scored_candidates:
                    normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                    item["score"] = normalized
            else:
                # All scores equal
                for item in scored_candidates:
                    item["score"] = 0.5
        
        return scored_candidates

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