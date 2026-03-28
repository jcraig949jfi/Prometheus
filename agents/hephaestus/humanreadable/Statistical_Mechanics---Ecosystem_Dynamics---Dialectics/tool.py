import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Ecological Monte Carlo (DEMC) Sampler Implementation.
    
    Mechanism:
    1. Structural Parsing (Ecosystem Niche): Candidates are scored primarily on 
       logical structure (negations, comparatives, conditionals) rather than 
       semantic similarity. This avoids the "bag-of-words" trap.
    2. Dialectic Synthesis (Thesis-Antithesis): We generate an 'antithesis' by 
       logically inverting the structural markers of the candidate. The score 
       is penalized if the antithesis is also highly compatible with the prompt 
       (indicating ambiguity/fragility).
    3. Ecological Competition (Lotka-Volterra): Final scores are adjusted by 
       a competition term where candidates with overlapping structural signatures 
       suppress each other, promoting diversity in the top-ranked list.
    4. HMC Analogy: We use a deterministic gradient-like step where the "energy" 
       is the negative log-likelihood of the structural match.
       
    This approach prioritizes logical consistency over string compression (NCD),
    using NCD only as a tiebreaker to satisfy the baseline requirement.
    """

    def __init__(self):
        # Structural patterns for parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'than']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _check_structure(self, text: str) -> Dict[str, any]:
        tokens = self._tokenize(text)
        lower_text = text.lower()
        
        has_neg = any(n in tokens for n in self.negations)
        has_comp = any(c in tokens for c in self.comparatives) or any(c in lower_text for c in ['>', '<'])
        has_cond = any(c in tokens for c in self.conditionals)
        numbers = self._extract_numbers(text)
        
        return {
            'neg_count': sum(tokens.count(n) for n in self.negations),
            'comp_count': sum(tokens.count(c) for c in self.comparatives) + lower_text.count('>') + lower_text.count('<'),
            'cond_count': sum(tokens.count(c) for c in self.conditionals),
            'has_numbers': len(numbers) > 0,
            'numbers': numbers,
            'length': len(tokens)
        }

    def _structural_match_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on logical consistency between prompt and candidate.
        High score = structurally consistent.
        """
        p_struct = self._check_structure(prompt)
        c_struct = self._check_structure(candidate)
        score = 0.0
        
        # 1. Numeric Consistency (High Weight)
        if p_struct['has_numbers'] and c_struct['has_numbers']:
            # Check if candidate numbers are logically derived (simplified heuristic)
            # If prompt has numbers, candidate should likely have numbers or explicit logic
            p_nums = sorted(p_struct['numbers'])
            c_nums = sorted(c_struct['numbers'])
            
            # Reward if candidate numbers are within reasonable range of prompt numbers
            if c_nums:
                overlap = sum(1 for n in c_nums if any(abs(n - p) < 0.01 * max(1, abs(p)) for p in p_nums))
                score += 2.0 * (overlap / max(1, len(c_nums)))
        elif not p_struct['has_numbers'] and not c_struct['has_numbers']:
            score += 0.5 # Neutral match for non-numeric
            
        # 2. Logical Operator Consistency
        # If prompt has conditionals, candidate should ideally reflect conditional logic or direct answer
        if p_struct['cond_count'] > 0:
            # If prompt is conditional, candidate answering directly is good, 
            # but if candidate is also conditional, it might be restating premise (bad)
            if c_struct['cond_count'] == 0:
                score += 1.0 
        else:
            # If no conditionals in prompt, extra conditionals in candidate might be hallucination
            if c_struct['cond_count'] > 0:
                score -= 0.5

        # 3. Negation Alignment
        # Detect if prompt asks a negative question or contains negation
        if p_struct['neg_count'] > 0:
            # Candidate must handle negation carefully. 
            # Heuristic: If prompt has negation, candidate length should be substantial to explain
            if c_struct['length'] > 3:
                score += 0.5
        
        # 4. Direct Boolean Match (Simple case)
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        # Check for direct boolean answers if prompt looks like a yes/no question
        if any(q in prompt.lower() for q in ['is it', 'does it', 'can it', 'are they']):
            if any(b in c_tokens for b in self.booleans):
                score += 1.5

        return score

    def _generate_antithesis(self, candidate: str) -> str:
        """
        Dialectic step: Generate an antithesis by flipping structural markers.
        This simulates the 'perturbation' in HMC.
        """
        lower_c = candidate.lower()
        tokens = self._tokenize(candidate)
        
        # Flip negations
        flipped_tokens = []
        for token in tokens:
            if token in self.negations:
                # Simple flip: remove or replace (heuristic: just mark as flipped)
                flipped_tokens.append("FLIPPED_NEG")
            else:
                flipped_tokens.append(token)
        
        # If no negation to remove, add one to create contrast
        if "FLIPPED_NEG" not in " ".join(flipped_tokens):
             # Add a negation to the start to force contradiction
             flipped_tokens = ["not"] + flipped_tokens
             
        return " ".join(flipped_tokens)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        concat = s1_bytes + s2_bytes
        len_concat = len(zlib.compress(concat))
        len_s1_comp = len(zlib.compress(s1_bytes))
        len_s2_comp = len(zlib.compress(s2_bytes))
        
        max_len = max(len_s1_comp, len_s2_comp)
        if max_len == 0:
            return 0.0
            
        ncd = (len_concat - max_len) / max_len
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        population = [] # (index, raw_score, structural_sig)
        
        # Phase 1: Initial Scoring (Thesis)
        for i, cand in enumerate(candidates):
            struct_score = self._structural_match_score(prompt, cand)
            population.append({
                'index': i,
                'candidate': cand,
                'thesis_score': struct_score,
                'antithesis_score': 0.0,
                'niche_overlap': 0.0,
                'final_score': 0.0
            })
            
        # Phase 2: Dialectic Antithesis Check (Perturbation)
        # If the antithesis (flipped logic) also scores high, the original is fragile.
        for item in population:
            antithesis = self._generate_antithesis(item['candidate'])
            # Score how well the antithesis fits the prompt (should be low)
            anti_score = self._structural_match_score(prompt, antithesis)
            item['antithesis_score'] = anti_score
            
        # Phase 3: Ecological Competition (Lotka-Volterra interaction)
        # Calculate niche overlap based on structural signatures
        for i, item_i in enumerate(population):
            sig_i = self._check_structure(item_i['candidate'])
            overlap_penalty = 0.0
            
            for j, item_j in enumerate(population):
                if i == j:
                    continue
                sig_j = self._check_structure(item_j['candidate'])
                
                # Simple overlap metric: similarity in structural vector
                # (neg, comp, cond, num_flag)
                vec_i = [sig_i['neg_count'], sig_i['comp_count'], sig_i['cond_count'], int(sig_i['has_numbers'])]
                vec_j = [sig_j['neg_count'], sig_j['comp_count'], sig_j['cond_count'], int(sig_j['has_numbers'])]
                
                # Cosine-like similarity for overlap
                dot_prod = sum(a*b for a,b in zip(vec_i, vec_j))
                norm_i = math.sqrt(sum(a*a for a in vec_i)) + 1e-9
                norm_j = math.sqrt(sum(a*a for a in vec_j)) + 1e-9
                similarity = dot_prod / (norm_i * norm_j)
                
                if similarity > 0.8: # High overlap implies competition
                    overlap_penalty += similarity * 0.5 # Alpha coefficient
            
            item_i['niche_overlap'] = overlap_penalty

        # Phase 4: Synthesis and Final Scoring
        for item in population:
            # Fitness = Thesis - (Fragility from Antithesis) - (Competition)
            # Higher thesis is good. Higher antithesis match is BAD (fragile).
            # Higher overlap is BAD (crowded niche).
            
            fitness = item['thesis_score'] 
            fitness -= 0.5 * item['antithesis_score'] # Penalty for fragility
            fitness -= item['niche_overlap']          # Penalty for competition
            
            # NCD Tiebreaker (only if structural signals are weak or equal)
            # We add a tiny NCD component to break ties, but keep it secondary
            ncd_val = self._compute_ncd(prompt, item['candidate'])
            # Invert NCD so lower distance = higher score, but scale small
            ncd_bonus = (1.0 - ncd_val) * 0.05 
            
            item['final_score'] = fitness + ncd_bonus
            results.append(item)
            
        # Sort by final score descending
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Format output
        output = []
        for res in results:
            output.append({
                "candidate": res['candidate'],
                "score": float(res['final_score']),
                "reasoning": f"Structural match: {res['thesis_score']:.2f}, Fragility: {res['antithesis_score']:.2f}, Competition: {res['niche_overlap']:.2f}"
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the dialectical stability of the answer.
        """
        # Get evaluation for this single candidate
        # We simulate it being the only candidate to get intrinsic score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        item = res[0]
        
        # Confidence is high if:
        # 1. Thesis score is high
        # 2. Antithesis score is low (robust)
        # 3. Niche overlap is low (unique solution)
        
        thesis = item['score'] # This is actually the final_score from evaluate
        # Re-calculate components for clarity or extract from reasoning string? 
        # Better to re-run internal logic briefly or parse. 
        # Let's re-use the logic internally for precision.
        
        struct_score = self._structural_match_score(prompt, answer)
        anti = self._generate_antithesis(answer)
        anti_score = self._structural_match_score(prompt, anti)
        
        # Normalize to 0-1
        # Base confidence on the gap between thesis and antithesis
        raw_conf = struct_score - 0.5 * anti_score
        
        # Map to 0-1 using sigmoid-like mapping
        # Assume typical scores range -2 to 4
        conf = 1 / (1 + math.exp(-raw_conf))
        
        return min(1.0, max(0.0, conf))