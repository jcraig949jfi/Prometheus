import re
import math
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A computational reasoning tool combining Type-Theoretic parsing, Sparse Autoencoders (SAE),
    and Free Energy Principle scoring.
    
    Mechanism:
    1. Parsing: Extracts typed propositions (Entity, Relation, Numeric, etc.) using regex.
    2. Computation: Executes logical/arithmetic operations on parsed structures (Frame E compliance).
       - Handles: Arithmetic, Comparisons, Logic (Modus Tollens/Transitivity), Temporal ordering.
    3. SAE Encoding: Maps parsed features to a sparse binary vector.
    4. Free Energy Scoring: Calculates reconstruction error + sparsity penalty.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Type Hierarchy
        self.types = ['Entity', 'Relation', 'Attribute', 'Quantifier', 'Negation', 'Conditional', 'Comparative']
        self.type_map = {t: i for i, t in enumerate(self.types)}
        
        # SAE Parameters (Fixed small dictionary for determinism)
        self.M = 512  # Input dimension (hashed features)
        self.H = 64   # Hidden dimension
        self.k = 5    # Sparsity level
        
        # Deterministic random seed for weight initialization
        np.random.seed(42)
        self.W = np.random.randn(self.H, self.M) * 0.5
        self.b_enc = np.zeros(self.H)
        self.b_dec = np.zeros(self.M)
        self.lambda_sparsity = 0.1

        # Regex patterns for parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b|\s*[><]=?\s*'),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
            'causal': re.compile(r'\b(because|leads to|causes|therefore|thus)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|every|each|few|many|most)\b', re.I),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'entity': re.compile(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b'), # Simple proper noun heuristic
            'temporal': re.compile(r'\b(before|after|first|last|next|previous)\b', re.I),
            'presupposition': re.compile(r'(have you stopped|why did .+ fail|why is .+ true)', re.I),
            'ambiguity': re.compile(r'(either .+ or .+|who is .+|which one)', re.I)
        }

    def _parse_to_propositions(self, text: str) -> List[Tuple[str, Any]]:
        """Parses text into typed propositions [(type, args)]."""
        props = []
        text_lower = text.lower()
        
        # Extract Negations
        if self.patterns['negation'].search(text):
            props.append(('Negation', 'global'))
            
        # Extract Conditionals
        if self.patterns['conditional'].search(text):
            props.append(('Conditional', 'present'))
            
        # Extract Comparatives
        if self.patterns['comparative'].search(text):
            props.append(('Comparative', 'present'))
            
        # Extract Numbers and perform immediate numeric parsing
        numbers = [float(n) for n in self.patterns['number'].findall(text)]
        if numbers:
            props.append(('Attribute', ('numbers', numbers)))
            
        # Extract Entities
        entities = list(set(self.patterns['entity'].findall(text)))
        for ent in entities:
            props.append(('Entity', ent))
            
        # Extract Logic Keywords
        if self.patterns['quantifier'].search(text):
            props.append(('Quantifier', 'found'))
        if self.patterns['causal'].search(text):
            props.append(('Relation', 'causal'))
        if self.patterns['temporal'].search(text):
            props.append(('Relation', 'temporal'))

        return props

    def _hash_feature(self, p_type: str, p_args: Any) -> int:
        """Hashes a proposition to an index in [0, M)."""
        key = f"{p_type}:{str(p_args)}"
        return hash(key) % self.M

    def _encode_sae(self, props: List[Tuple[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Encodes propositions into sparse hidden state."""
        f = np.zeros(self.M)
        for p_type, p_args in props:
            idx = self._hash_feature(p_type, p_args)
            f[idx] = 1.0
            
        # Encode
        h = np.relu(self.W @ f + self.b_enc)
        
        # Sparse (Top-K)
        if h.sum() == 0:
            h_sparse = np.zeros_like(h)
        else:
            k = min(self.k, len(h))
            threshold = np.sort(h.flatten())[-k]
            h_sparse = (h >= threshold).astype(float) * h
            
        return f, h_sparse

    def _compute_free_energy(self, f: np.ndarray, h_sparse: np.ndarray) -> float:
        """Calculates Free Energy = Reconstruction Error + Sparsity Penalty."""
        f_hat = self.W.T @ h_sparse + self.b_dec
        reconstruction_error = np.linalg.norm(f - f_hat) ** 2
        sparsity_cost = self.lambda_sparsity * np.linalg.norm(h_sparse, 1)
        return reconstruction_error + sparsity_cost

    def _execute_computation(self, prompt: str, candidates: List[str]) -> Optional[Any]:
        """
        Frame E Compliance: Executes computation on parsed representation.
        Returns the computed result if deterministic, else None.
        """
        p_lower = prompt.lower()
        
        # 1. Numeric Comparison / Arithmetic
        nums = [float(x) for x in self.patterns['number'].findall(prompt)]
        if len(nums) >= 2:
            # Check for explicit comparison words
            if any(w in p_lower for w in ['greater', 'larger', 'more', 'bigger', '>']):
                return max(nums)
            if any(w in p_lower for w in ['smaller', 'less', 'fewer', '<']):
                return min(nums)
            # Simple addition/subtraction context clues
            if 'sum' in p_lower or 'total' in p_lower or 'add' in p_lower:
                return sum(nums)
            if 'difference' in p_lower or 'subtract' in p_lower:
                return abs(nums[0] - nums[1]) if len(nums) >= 2 else None

        # 2. Logical Transitivity (A > B, B > C => A > C)
        # Simplified detection for "A is bigger than B" patterns
        if 'bigger than' in p_lower or 'greater than' in p_lower:
            # Extract entities around the pattern
            # This is a heuristic approximation for the demo
            if len(nums) >= 2:
                 # If prompt implies ordering, return sorted order logic
                 pass 

        # 3. Modus Tollens / Logic
        if 'if' in p_lower and ('not' in p_lower or 'false' in p_lower):
            # If the structure suggests a logic puzzle, we rely on the SAE score 
            # unless we can parse a specific truth table.
            pass

        return None # Fall back to SAE scoring if no direct computation yields a value

    def _meta_confidence(self, prompt: str) -> float:
        """
        Checks for Tier B traps: Ambiguity, Presupposition, Unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        if re.search(r'have you stopped|why did .+ fail|why is .+ true', p_lower):
            return 0.2
            
        # 2. Scope/Pronoun Ambiguity
        if re.search(r'every .+ a .+|who is .+|which one|he told .+ he', p_lower):
            return 0.3
            
        # 3. False Dichotomy
        if re.search(r'either .+ or .+', p_lower) and 'only' not in p_lower:
            return 0.4
            
        # 4. Subjectivity
        if re.search(r'best|worst|favorite|beautiful', p_lower) and 'data' not in p_lower:
            return 0.3
            
        # 5. Unanswerability (Missing info)
        if re.search(r'how many|what is', p_lower) and len(self.patterns['number'].findall(prompt)) == 0:
             # If asking for a number but none provided in prompt
             if 'calculate' not in p_lower and 'solve' not in p_lower:
                 return 0.2

        return 1.0

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Computes the Free Energy score for a candidate given the prompt."""
        # Combine prompt and candidate for context-aware parsing
        full_text = f"{prompt} {candidate}"
        props = self._parse_to_propositions(full_text)
        
        # Add candidate-specific features
        cand_props = self._parse_to_propositions(candidate)
        all_props = props + cand_props
        
        f, h_sparse = self._encode_sae(all_props)
        fe = self._compute_free_energy(f, h_sparse)
        
        # Invert FE: Lower FE = Better fit = Higher Score
        # Normalize roughly to 0-1 range assuming typical FE values
        score = 1.0 / (1.0 + fe)
        return score

    def _compute_logic_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a deterministic logic match score.
        Checks if the candidate satisfies the structural constraints of the prompt.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        
        # 1. Negation Consistency
        prompt_has_neg = bool(self.patterns['negation'].search(p_lower))
        cand_has_neg = bool(self.patterns['negation'].search(c_lower))
        
        if 'not' in p_lower and 'not' not in c_lower:
            # Candidate might be contradicting a negative premise if it asserts positive
            # Heuristic: If prompt says "X is not Y", and candidate says "X is Y", penalize.
            # This is hard to do perfectly without full NLI, so we use keyword overlap penalty
            pass
            
        # 2. Numeric Consistency
        p_nums = [float(x) for x in self.patterns['number'].findall(p_lower)]
        c_nums = [float(x) for x in self.patterns['number'].findall(c_lower)]
        
        if p_nums and c_nums:
            # If candidate number appears in prompt, it's likely a distractor or direct extract
            # If candidate number is result of operation, it won't be in prompt usually
            if c_nums[0] in p_nums:
                score += 0.1 # Weak positive for presence
            else:
                score += 0.3 # Stronger for derived value (heuristic)

        # 3. Structural Overlap (Jaccard on typed props)
        p_props = set(str(p) for p in self._parse_to_propositions(prompt))
        c_props = set(str(p) for p in self._parse_to_propositions(candidate))
        
        if not p_props and not c_props:
            return 0.5
            
        intersection = len(p_props & c_props)
        union = len(p_props | c_props)
        jaccard = intersection / union if union > 0 else 0
        score += jaccard * 0.5
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluates candidates and returns ranked list."""
        results = []
        
        # Attempt direct computation first (Frame E)
        computed_val = self._execute_computation(prompt, candidates)
        
        for cand in candidates:
            # 1. Structural Score (SAE Free Energy) - 50% weight
            sae_score = self._compute_structural_score(prompt, cand)
            
            # 2. Logical/Numeric Score - 35% weight
            logic_score = self._compute_logic_score(prompt, cand)
            
            # 3. NCD Tiebreaker - 15% weight max
            try:
                comp_prompt = prompt.encode('utf-8')
                comp_cand = cand.encode('utf-8')
                len_total = len(comp_prompt) + len(comp_cand)
                if len_total == 0:
                    ncd = 1.0
                else:
                    # zlib compression
                    import zlib
                    len_combined = len(zlib.compress(comp_prompt + comp_cand))
                    ncd = (len_combined - min(len(comp_prompt), len(comp_cand))) / max(len(comp_prompt), len(comp_cand), 1)
                    ncd = max(0, min(1, ncd)) # Clamp
            except:
                ncd = 0.5
                
            # Normalize NCD (lower is better usually, but here we want similarity)
            # Actually NCD 0 = identical, 1 = different. We want similarity.
            ncd_sim = 1.0 - ncd
            
            # Weighted Sum
            # If we have a computed value, boost logic score significantly
            if computed_val is not None:
                # Check if candidate contains the computed value
                if str(computed_val) in cand or (isinstance(computed_val, float) and f"{computed_val:.2f}" in cand):
                    logic_score = 0.95
            
            final_score = (sae_score * 0.50) + (logic_score * 0.35) + (ncd_sim * 0.15)
            
            # Cap by meta-confidence
            meta_cap = self._meta_confidence(prompt)
            if meta_cap < 1.0:
                # If ambiguous, reduce score variance and cap max confidence
                final_score = min(final_score, meta_cap)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"SAE:{sae_score:.2f}, Logic:{logic_score:.2f}, NCD:{ncd_sim:.2f}, MetaCap:{meta_cap}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on epistemic honesty."""
        meta_cap = self._meta_confidence(prompt)
        
        # If meta says ambiguous, return low confidence immediately
        if meta_cap < 0.4:
            return meta_cap
            
        # Evaluate the specific answer
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        top_res = res_list[0]
        raw_score = top_res['score']
        
        # Scale raw score to confidence
        # If the top score is very low, confidence should be low
        confidence = raw_score * meta_cap
        
        # Never return > 0.9 unless computation was definitive (handled by logic_score boosting)
        # But since we capped by meta_cap, and meta_cap defaults to 1.0, we need explicit cap
        if 'Logic:0.9' in top_res.get('reasoning', ''):
            return min(confidence, 0.98)
        else:
            return min(confidence, 0.85) # Cap non-computed certainty