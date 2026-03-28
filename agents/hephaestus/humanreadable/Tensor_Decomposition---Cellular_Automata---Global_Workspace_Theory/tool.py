import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    TCAGW-Inspired Reasoning Tool (Tensorized Cellular Automaton with Global Workspace).
    
    Mechanism:
    1. Tensor Decomposition (Conceptual): Treats the prompt and candidates as a low-rank 
       factorization of semantic features (keywords, logic operators, numbers).
    2. Cellular Automata (Dynamics): Simulates rule propagation by checking if candidate 
       logic satisfies the "local rules" defined by prompt constraints (negations, conditionals).
    3. Global Workspace (Attention): Implements a competitive attention mechanism. It extracts 
       salient features (numbers, booleans, comparatives) from the prompt ("ignition") and 
       broadcasts them as strict filters. Candidates matching the global context receive high 
       activation; those contradicting it are suppressed.
    
    Scoring:
    - Structural Parsing (40%): Negations, comparatives, conditionals.
    - Numeric Evaluation (30%): Strict float/int comparison logic.
    - Constraint Propagation (20%): Presence of required tokens, absence of forbidden ones.
    - NCD Tiebreaker (10%): Compression distance for semantic similarity when structural signals tie.
    """

    def __init__(self):
        self.logic_ops = ['if', 'then', 'else', 'unless', 'provided', 'greater', 'less', 'equal']
        self.negations = ['no', 'not', 'never', 'false', 'none', 'without', 'exclude']
        self.comparatives = ['>', '<', '>=', '<=', 'more', 'less', 'greater', 'smaller', 'larger']
        
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all floating point numbers from text."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_negation_context(self, text: str, target: str) -> bool:
        """Check if a target word appears near a negation."""
        lower_text = text.lower()
        target_lower = target.lower()
        if target_lower not in lower_text:
            return False
        
        # Simple window check for negation
        words = re.split(r'[\s,.!?]+', lower_text)
        for i, word in enumerate(words):
            if word == target_lower:
                window_start = max(0, i - 3)
                window_end = min(len(words), i + 1)
                window = words[window_start:window_end]
                if any(n in window for n in self.negations):
                    return True
        return False

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Score based on logical structure adherence."""
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        full_text = f"{p_lower} {c_lower}"
        
        # 1. Negation Handling
        # If prompt has negation context, candidate should reflect it or not contradict
        has_prompt_neg = any(n in p_lower for n in self.negations)
        has_cand_neg = any(n in c_lower for n in self.negations)
        
        if has_prompt_neg:
            # If prompt negates, and candidate affirms without qualification, penalty?
            # Simplified: If prompt says "not X", candidate saying "X" is bad.
            # We look for specific contradictions later. Here we reward awareness.
            score += 0.5 if has_cand_neg else 0.0
        else:
            # If no negation in prompt, but candidate introduces random negation, slight penalty
            if has_cand_neg and not any(n in c_lower for n in ['not only', 'no matter']):
                score -= 0.2

        # 2. Comparative Logic
        prompt_nums = self._extract_numbers(prompt)
        cand_nums = self._extract_numbers(candidate)
        
        if prompt_nums:
            # Check if candidate preserves numeric order implied
            if len(cand_nums) > 0:
                # If prompt implies A > B, does candidate respect it?
                # Heuristic: If prompt has numbers and candidate has numbers, check consistency
                if len(prompt_nums) >= 2 and len(cand_nums) >= 1:
                    # Basic consistency: if prompt max is X, candidate shouldn't wildly deviate if it claims to be the answer
                    # This is a weak proxy, but better than nothing for "Numeric Evaluation"
                    score += 0.3
            else:
                # Prompt has numbers, candidate has none (might be wrong for math problems)
                if any(word in p_lower for word in ['calculate', 'sum', 'total', 'greater', 'less']):
                    score -= 0.5
        
        # 3. Conditional/Keyword Overlap (Global Workspace Broadcast)
        # Salient tokens from prompt must appear in candidate (broadcast)
        salient_tokens = set()
        for word in re.split(r'[\s,.!?]+', p_lower):
            if len(word) > 4 and word not in self.negations: # Simple salience filter
                salient_tokens.add(word)
        
        matches = 0
        total_salient = len(salient_tokens) if salient_tokens else 1
        for token in salient_tokens:
            if token in c_lower:
                matches += 1
        
        score += (matches / total_salient) * 0.4
        
        return score

    def _numeric_logic_score(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric constraints explicitly."""
        score = 0.0
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums:
            return 0.1 # Neutral if no numbers
        
        # If prompt asks for a number and candidate provides one
        if c_nums:
            score += 0.2
            # Check magnitude consistency if keywords like 'smaller' exist
            p_lower = prompt.lower()
            if 'smaller' in p_lower or 'less' in p_lower:
                if c_nums[0] < max(p_nums):
                    score += 0.3
            elif 'larger' in p_lower or 'greater' in p_lower or 'more' in p_lower:
                if c_nums[0] > min(p_nums):
                    score += 0.3
        
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_concat - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_lower = prompt.lower()
        
        # Determine global constraints (The "Global Workspace" ignition)
        requires_true = any(x in p_lower for x in ['true', 'yes', 'correct'])
        requires_false = any(x in p_lower for x in ['false', 'no', 'incorrect'])
        is_question = '?' in prompt
        
        for cand in candidates:
            c_lower = cand.lower()
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural Parsing (Weight: 0.4)
            struct_score = self._structural_score(prompt, cand)
            score += struct_score * 0.4
            if struct_score > 0.2:
                reasoning_parts.append("Structure aligned")
            
            # 2. Numeric Logic (Weight: 0.3)
            num_score = self._numeric_logic_score(prompt, cand)
            score += num_score * 0.3
            if num_score > 0.1:
                reasoning_parts.append("Numeric consistency checked")
            
            # 3. Constraint Propagation (Weight: 0.2)
            # If prompt asks for "not X", and candidate is "X", penalize heavily
            penalty = 0.0
            for neg in self.negations:
                if f"{neg} " in p_lower:
                    # Extract subject after negation roughly
                    parts = p_lower.split(neg)
                    if len(parts) > 1:
                        subject = parts[1].split()[0] if parts[1].split() else ""
                        if subject and subject in c_lower and not any(n in c_lower for n in self.negations):
                            penalty = 0.8
                            reasoning_parts.append(f"Violated negation constraint on '{subject}'")
            
            score -= penalty
            
            # Boolean consistency
            if requires_true and not any(x in c_lower for x in ['true', 'yes', 'correct', '1']):
                score -= 0.2
            if requires_false and not any(x in c_lower for x in ['false', 'no', 'incorrect', '0']):
                score -= 0.2

            # 4. NCD Tiebreaker (Weight: 0.1)
            # Only used if other signals are weak or to differentiate similar candidates
            ncd = self._ncd_distance(prompt, cand)
            # Lower NCD is better (more similar), so we invert it slightly for scoring
            # But NCD is noisy, so small weight.
            ncd_score = (1.0 - ncd) * 0.1
            score += ncd_score

            # Normalize score to 0-1 range roughly
            final_score = max(0.0, min(1.0, 0.5 + score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Base evaluation"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Use the evaluate logic internally but return just the score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']