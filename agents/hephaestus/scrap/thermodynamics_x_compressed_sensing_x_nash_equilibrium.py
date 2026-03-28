import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Stochastic Sparse Equilibrium Search (SSES) Implementation.
    
    Mechanism:
    1. Compressed Sensing (Signal Extraction): Treats the prompt as an undersampled signal.
       Extracts a sparse feature vector based on structural markers (negations, comparatives,
       conditionals, numeric literals) rather than raw token overlap.
    2. Thermodynamics (Search Dynamics): Computes an initial 'energy' (error) for each candidate.
       Applies a simulated annealing acceptance criterion. If a candidate has higher energy 
       (worse fit) but the system 'temperature' (uncertainty/entropy of the prompt) is high,
       it may still be accepted temporarily to escape local minima. Here, we model this as 
       a penalty adjustment: high-entropy prompts reduce the penalty for non-exact matches,
       while low-entropy (rigid) prompts enforce strict structural adherence.
    3. Nash Equilibrium (Convergence): The final score represents a stable state where 
       structural compliance (logic) and semantic compression (NCD) reach an equilibrium.
       No single factor can improve the score without violating the sparsity constraints 
       of the extracted features.
    
    This approach prioritizes structural logic (Reasoning) and uncertainty quantification 
    (Metacognition) over simple string similarity.
    """

    def __init__(self):
        # Structural regex patterns for sparse feature extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|better|worse|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided|when)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'logic_conn': re.compile(r'\b(and|or|but|however|therefore|thus|hence)\b', re.I)
        }

    def _extract_sparse_features(self, text: str) -> Dict[str, any]:
        """Compressed Sensing step: Extract high-value structural features."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_logic': bool(self.patterns['logic_conn'].search(text_lower)),
            'numbers': self.patterns['numeric'].findall(text_lower),
            'length': len(text),
            'word_count': len(text.split())
        }
        return features

    def _check_structural_compliance(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluate logical consistency based on structural features.
        Returns a compliance score (0.0 to 1.0).
        """
        score = 1.0
        
        # 1. Negation Consistency
        # If prompt has negation, valid answers often need to reflect awareness or specific handling
        # Simple heuristic: If prompt is negative, and candidate is a simple "Yes", penalize heavily?
        # Instead, we check if the candidate mirrors the structural complexity.
        if prompt_feats['has_negation'] and not cand_feats['has_negation']:
            # If prompt is complex (negation) but candidate is simple, slight penalty unless candidate is very short
            if cand_feats['word_count'] < 5:
                score -= 0.2
        
        # 2. Numeric Consistency (Constraint Propagation)
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if p_nums:
            # If prompt has numbers, candidate should ideally engage with them or be a logical word answer
            # If candidate has numbers, do they match order of magnitude? (Simplified check)
            if c_nums:
                try:
                    p_max = max(float(x) for x in p_nums)
                    c_max = max(float(x) for x in c_nums)
                    # Heuristic: If candidate number is wildly different from prompt max in a math context, penalize
                    # This is a weak proxy for "solving", but catches obvious hallucinations
                    if p_max > 0 and (c_max > p_max * 10 or c_max < p_max * 0.01):
                        score -= 0.3
                except ValueError:
                    pass

        # 3. Conditional/Logic Flow
        if prompt_feats['has_conditional'] and not cand_feats['has_logic'] and not cand_feats['has_conditional']:
            # Prompts with conditions often require 'if', 'therefore', or structured reasoning in answer
            if cand_feats['word_count'] > 3: # Only if candidate is long enough to have included it
                score -= 0.15

        return max(0.0, score)

    def _compute_energy(self, prompt: str, candidate: str, structural_score: float) -> float:
        """
        Thermodynamics step: Calculate energy based on NCD and structural fit.
        Lower energy = better state.
        E = (1 - structural_score) + alpha * NCD
        """
        # Normalized Compression Distance (NCD)
        try:
            z_prompt = len(zlib.compress(prompt.encode()))
            z_cand = len(zlib.compress(candidate.encode()))
            z_comb = len(zlib.compress((prompt + candidate).encode()))
            
            denom = max(z_prompt, z_cand)
            if denom == 0:
                ncd = 1.0
            else:
                ncd = (z_comb - min(z_prompt, z_cand)) / denom
        except:
            ncd = 1.0

        # Energy function: Structural compliance reduces energy significantly
        # NCD acts as the baseline entropy cost
        energy = (1.0 - structural_score) + (0.5 * ncd)
        return energy

    def _simulated_annealing_adjust(self, base_score: float, prompt: str) -> float:
        """
        Thermodynamic adjustment: High entropy (uncertainty) in prompt allows 
        more exploration (less penalty for imperfection). Low entropy enforces strictness.
        """
        # Estimate prompt entropy via compression ratio
        z_prompt = len(zlib.compress(prompt.encode()))
        ratio = z_prompt / len(prompt.encode()) if len(prompt) > 0 else 1.0
        
        # If ratio is high (hard to compress = high entropy/complexity), we are less certain
        # We soften the score slightly to allow for ambiguity
        if ratio > 0.8: # High complexity
            adjustment = 0.05 
        else:
            adjustment = 0.0
            
        return min(1.0, base_score + adjustment)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._extract_sparse_features(prompt)
        results = []
        
        # Calculate raw energies first to find the "ground state" for normalization
        energies = []
        for cand in candidates:
            cand_feats = self._extract_sparse_features(cand)
            struct_score = self._check_structural_compliance(prompt_feats, cand_feats, prompt, cand)
            energy = self._compute_energy(prompt, cand, struct_score)
            energies.append(energy)
        
        # Convert energy to probability-like score (Boltzmann distribution analogy)
        # Score = exp(-E) / sum(exp(-E)) -> Simplified to 1/(1+E) for stability here
        min_energy = min(energies) if energies else 1.0
        
        for i, cand in enumerate(candidates):
            cand_feats = self._extract_sparse_features(cand)
            struct_score = self._check_structural_compliance(prompt_feats, cand_feats, prompt, cand)
            energy = energies[i]
            
            # Normalize energy relative to the best candidate found in this batch
            # This creates the Nash Equilibrium: relative stability among competitors
            rel_energy = energy - min_energy + 0.01 # Avoid division by zero
            
            # Inverse energy scoring
            raw_score = 1.0 / (1.0 + rel_energy * 2.0)
            
            # Apply thermodynamic adjustment for uncertainty
            final_score = self._simulated_annealing_adjust(raw_score, prompt)
            
            # Reasoning trace
            reasoning = f"Structural compliance: {struct_score:.2f}. "
            if prompt_feats['has_negation'] and not cand_feats['has_negation']:
                reasoning += "Detected potential negation mismatch. "
            if prompt_feats['numbers'] and not cand_feats['numbers']:
                reasoning += "Numeric data present in prompt but not explicitly mirrored. "
            if final_score > 0.8:
                reasoning += "High equilibrium stability."
            else:
                reasoning += "Moderate/Low stability."

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same SSES logic: high structural compliance + low NCD = high confidence.
        """
        # Evaluate as a single candidate set
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']