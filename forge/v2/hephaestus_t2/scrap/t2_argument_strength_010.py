import re
import zlib
from typing import Dict, List, Any

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    topological_sort,
    check_transitivity
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox


class ReasoningTool:
    """Signal processing x SAT entailment - argument_strength"""

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
        """Extract premises, conclusion, and logical structure from prompt."""
        structure = {
            "premises": [],
            "conclusion": None,
            "variables": set(),
            "raw": prompt
        }
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', prompt)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Look for logical indicators
        for i, sent in enumerate(sentences):
            sent_lower = sent.lower()
            
            # Identify premises (often early sentences)
            if i < len(sentences) - 1:
                if any(indicator in sent_lower for indicator in 
                       ['if', 'since', 'because', 'given that', 'assuming']):
                    structure["premises"].append(sent)
                elif 'therefore' in sent_lower or 'thus' in sent_lower:
                    # Sometimes conclusion starts with therefore
                    if not structure["conclusion"]:
                        structure["conclusion"] = sent
                else:
                    # Default: treat as premise unless it's clearly a question
                    if not sent.endswith('?'):
                        structure["premises"].append(sent)
            
            # Last sentence is often the conclusion/question
            if i == len(sentences) - 1:
                if not structure["conclusion"]:
                    structure["conclusion"] = sent
        
        # Extract propositional variables (capitalized words that represent statements)
        for sent in structure["premises"] + ([structure["conclusion"]] if structure["conclusion"] else []):
            # Find simple statements (often single capitalized words or short phrases)
            words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', sent)
            for word in words:
                if len(word.split()) <= 3:  # Short phrases likely represent propositions
                    structure["variables"].add(word)
        
        # If no conclusion found, use last sentence
        if not structure["conclusion"] and sentences:
            structure["conclusion"] = sentences[-1]
        
        return structure

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use signal processing concepts to evaluate argument strength.
        
        Signal processing framework:
        - Premises are input signals with varying SNR (signal-to-noise ratio)
        - Logical operations are filters that process these signals
        - Argument strength is the output SNR after processing
        - Entropy measures uncertainty/noise in the reasoning chain
        """
        premises = structure["premises"]
        conclusion = structure["conclusion"]
        variables = list(structure["variables"])
        
        if not premises or not conclusion:
            return {
                "answer": "Invalid argument",
                "confidence": 0.0,
                "reasoning": "Missing premises or conclusion"
            }
        
        # Signal processing: Map variables to frequencies (unique identifiers)
        var_to_freq = {var: i+1 for i, var in enumerate(variables)}
        
        # Build SAT clauses from premises (signal encoding)
        clauses = []
        premise_signals = []  # SNR values for each premise
        
        for premise in premises:
            # Simple encoding: "A implies B" -> (-A ∨ B)
            # "A and B" -> (A ∧ B) encoded as two clauses: (A), (B)
            # "A or B" -> (A ∨ B)
            
            clause = []
            premise_lower = premise.lower()
            
            # Extract variables mentioned in this premise
            mentioned_vars = [v for v in variables if v in premise]
            
            if not mentioned_vars:
                continue
            
            # Signal strength: more variables = more complex signal
            snr = 1.0 / (len(mentioned_vars) + 0.1)  # Inverse relationship
            
            # Simple implication detection
            if 'implies' in premise_lower or 'if' in premise_lower or 'then' in premise_lower:
                # Try to parse "A implies B"
                parts = re.split(r'implies|if.*then', premise_lower, maxsplit=1)
                if len(parts) >= 2:
                    # Find variables in each part
                    antecedent_vars = [v for v in variables if v in parts[0]]
                    consequent_vars = [v for v in variables if v in parts[1]]
                    
                    if antecedent_vars and consequent_vars:
                        # Encode as (-antecedent ∨ consequent)
                        for ant in antecedent_vars:
                            for cons in consequent_vars:
                                clause = [-var_to_freq[ant], var_to_freq[cons]]
                                clauses.append(clause)
                                premise_signals.append(snr)
            
            # Conjunction detection
            elif 'and' in premise_lower:
                for var in mentioned_vars:
                    clauses.append([var_to_freq[var]])
                    premise_signals.append(snr)
            
            # Disjunction detection  
            elif 'or' in premise_lower:
                clause = [var_to_freq[var] for var in mentioned_vars]
                if clause:
                    clauses.append(clause)
                    premise_signals.append(snr)
            
            # Default: treat as simple assertion
            else:
                for var in mentioned_vars:
                    clauses.append([var_to_freq[var]])
                    premise_signals.append(snr)
        
        if not clauses:
            # Fallback: create simple clauses from variables
            for var in variables[:3]:  # Use first few variables
                clauses.append([var_to_freq[var]])
                premise_signals.append(0.5)
        
        # Encode conclusion as a clause to check entailment
        conclusion_vars = [v for v in variables if v in conclusion]
        if not conclusion_vars:
            conclusion_vars = variables[:1] if variables else []
        
        conclusion_clause = []
        conclusion_lower = conclusion.lower()
        
        if 'not' in conclusion_lower:
            # Negated conclusion
            for var in conclusion_vars:
                conclusion_clause = [-var_to_freq[var]]
        else:
            # Positive conclusion
            for var in conclusion_vars:
                conclusion_clause = [var_to_freq[var]]
        
        # CRITICAL: Use amino acid for logical entailment (LOAD-BEARING)
        entailment_result = check_entailment(clauses, conclusion_clause)
        
        # Signal processing: Compute entropy of premise signals
        if premise_signals:
            # Normalize signals to create probability distribution
            signal_sum = sum(premise_signals)
            if signal_sum > 0:
                signal_probs = [s/signal_sum for s in premise_signals]
                signal_entropy = entropy(signal_probs)  # T1 primitive (LOAD-BEARING)
            else:
                signal_entropy = 1.0
        else:
            signal_entropy = 1.0
        
        # CRITICAL: Use SAT solver to check consistency (LOAD-BEARING)
        sat_result = solve_sat(clauses, len(variables))
        
        # CRITICAL: Check for paradox in premises (LOAD-BEARING)
        paradox_info = detect_paradox(clauses)
        
        # CRITICAL: Use modus ponens to derive conclusions (LOAD-BEARING)
        # Convert clauses to implication rules for modus ponens
        mp_rules = []
        for clause in clauses:
            if len(clause) == 2 and clause[0] < 0 and clause[1] > 0:
                # (-A ∨ B) becomes (A → B)
                ant = variables[abs(clause[0])-1]
                cons = variables[clause[1]-1]
                mp_rules.append((ant, cons))
        
        mp_facts = set()
        # Add unit clauses as facts
        for clause in clauses:
            if len(clause) == 1 and clause[0] > 0:
                mp_facts.add(variables[clause[0]-1])
        
        mp_derived = modus_ponens(mp_rules, mp_facts)
        
        # CRITICAL: Build dependency graph and topological sort (LOAD-BEARING)
        edges = []
        for ant, cons in mp_rules:
            edges.append((ant, cons))
        
        if edges:
            try:
                topo_order = topological_sort(edges)  # T1 primitive (LOAD-BEARING)
            except:
                topo_order = []
        else:
            topo_order = []
        
        # CRITICAL: Check transitivity of implications (LOAD-BEARING)
        transitivity_result = check_transitivity(edges)
        
        # Determine argument validity based on multiple signals
        valid_signals = []
        
        # Signal 1: SAT entailment result
        if entailment_result is True:
            valid_signals.append(0.9)  # Strong signal for valid
        elif entailment_result is False:
            valid_signals.append(0.1)  # Weak signal for invalid
        else:
            valid_signals.append(0.5)  # Uncertain
        
        # Signal 2: Paradox detection
        if paradox_info and paradox_info.get("is_paradox", False):
            valid_signals.append(0.1)  # Paradox weakens argument
        else:
            valid_signals.append(0.7)  # No paradox strengthens
        
        # Signal 3: Modus ponens derivation
        conclusion_var = conclusion_vars[0] if conclusion_vars else None
        if conclusion_var and conclusion_var in mp_derived:
            valid_signals.append(0.8)
        else:
            valid_signals.append(0.3)
        
        # Signal 4: Topological structure
        if topo_order and conclusion_var and conclusion_var in topo_order:
            # Conclusion appears in dependency chain
            valid_signals.append(0.7)
        else:
            valid_signals.append(0.4)
        
        # Signal 5: Transitivity analysis
        if transitivity_result:
            reachable = set()
            for node in transitivity_result:
                reachable.update(transitivity_result[node])
            if conclusion_var and any(conclusion_var in transitivity_result.get(prem, set()) 
                                    for prem in mp_facts):
                valid_signals.append(0.8)
            else:
                valid_signals.append(0.3)
        
        # Compute final validity score using Bayesian update with entropy as noise
        prior = 0.5
        likelihood = sum(valid_signals) / len(valid_signals) if valid_signals else 0.5
        
        # Use entropy as measure of noise in the reasoning chain
        # Higher entropy = more uncertainty = lower confidence
        noise_level = min(signal_entropy, 0.9)  # Cap at 0.9
        
        # CRITICAL: Bayesian update with noise (LOAD-BEARING)
        posterior = bayesian_update(prior, likelihood, noise_level)
        
        # CRITICAL: Compute confidence from agreement of signals (LOAD-BEARING)
        confidence = confidence_from_agreement(valid_signals)
        
        # Determine final answer
        if posterior > 0.6:
            computed_answer = "Valid"
        elif posterior < 0.4:
            computed_answer = "Invalid"
        else:
            computed_answer = "Uncertain"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "posterior": posterior,
            "entropy": signal_entropy,
            "reasoning": f"Argument strength: {posterior:.2f}, Entropy: {signal_entropy:.2f}, Signals: {len(valid_signals)}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        
        for candidate in candidates:
            # Primary scoring: direct match with computed answer
            candidate_lower = candidate.lower()
            computed_lower = computed_answer.lower()
            
            if computed_lower in candidate_lower:
                base_score = 1.0
            elif any(word in candidate_lower for word in ["valid", "invalid", "uncertain"]):
                # Check for semantic match
                if ("valid" in computed_lower and "valid" in candidate_lower) or \
                   ("invalid" in computed_lower and "invalid" in candidate_lower) or \
                   ("uncertain" in computed_lower and "uncertain" in candidate_lower):
                    base_score = 0.8
                else:
                    base_score = 0.2
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * (0.5 + 0.5 * confidence)
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Extract scores
        scores = [item["score"] for item in scored]
        
        # Simple normalization: softmax-like transformation
        max_score = max(scores) if scores else 1.0
        min_score = min(scores) if scores else 0.0
        
        if max_score > min_score:
            for item in scored:
                # Rescale to [0, 1] range
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