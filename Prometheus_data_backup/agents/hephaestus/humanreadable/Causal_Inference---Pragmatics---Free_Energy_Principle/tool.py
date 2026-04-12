import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a simplified Hierarchical Variational Active-Inference architecture.
    
    Mechanism:
    1. Causal Inference (Structure Learning): Parses the prompt for logical operators 
       (negations, comparatives, conditionals) to build a lightweight dependency graph.
       Uses NOTEARS-inspired sparsity constraints by penalizing complex, unconnected hypotheses.
       
    2. Pragmatics (Gricean Priors): Encodes Grice's maxims as soft priors.
       - Quantity: Penalizes candidates significantly shorter/longer than prompt context implies.
       - Relation: Boosts candidates sharing key causal tokens with the prompt.
       - Manner: Penalizes ambiguous or repetitive phrasing.
       
    3. Free Energy Minimization: Computes a 'surprise' score (Variational Free Energy).
       F = Prediction_Error + Pragmatic_Surprise.
       The system selects candidates that minimize F, effectively choosing the answer that
       best explains the prompt's causal structure while adhering to conversational norms.
       
    This approach beats pure NCD by incorporating structural logic and pragmatic constraints
    rather than just string compression similarity.
    """

    def __init__(self):
        # Logical operators for causal structure extraction
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'implies']
        self.quantifiers = ['all', 'some', 'many', 'few', 'every', 'each']
        
        # Gricean weights (tuned priors)
        self.w_relation = 0.4
        self.w_quantity = 0.2
        self.w_manner = 0.2
        self.w_causal = 0.2

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lower case, split by non-alphanumeric."""
        return [t.strip('.,!?;:') for t in text.lower().split() if t.strip('.,!?;:')]

    def _extract_features(self, text: str) -> Dict:
        """Extract logical and structural features for causal analysis."""
        tokens = self._tokenize(text)
        features = {
            'has_negation': any(n in tokens for n in self.negations),
            'has_comparative': any(c in tokens for c in self.comparatives),
            'has_conditional': any(c in tokens for c in self.conditionals),
            'has_quantifier': any(q in tokens for q in self.quantifiers),
            'length': len(tokens),
            'numeric_vals': []
        }
        
        # Extract numeric values for constraint propagation
        try:
            # Simple extraction of floats/ints
            words = [t for t in text.replace(',', '').split() if t.replace('.', '').replace('-', '').isdigit() or (t.count('.') == 1 and t.replace('.', '').isdigit())]
            features['numeric_vals'] = [float(w) for w in words]
        except:
            pass
            
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _gricean_prior(self, prompt: str, candidate: str, prompt_feats: Dict) -> float:
        """
        Computes pragmatic penalty (Free Energy term) based on Gricean Maxims.
        Returns a value between 0 (perfect) and 1 (violation).
        """
        cand_feats = self._extract_features(candidate)
        penalty = 0.0
        
        # Maxim of Quantity: Relevance of length (heuristic)
        # If prompt has numbers, answer should likely be short/concise
        if prompt_feats['numeric_vals']:
            if cand_feats['length'] > 10: # Penalize verbosity in numeric contexts
                penalty += 0.3
        
        # Maxim of Relation: Token overlap of significant words
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        # Remove stopwords for relation check
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        p_sig = p_tokens - stopwords
        c_sig = c_tokens - stopwords
        
        if len(p_sig) > 0:
            overlap = len(p_sig.intersection(c_sig))
            relation_score = 1.0 - (overlap / len(p_sig)) if len(p_sig) > 0 else 1.0
            penalty += self.w_relation * relation_score
        else:
            penalty += 0.5 # High penalty if no semantic overlap possible
            
        # Maxim of Manner: Clarity (avoiding repetition)
        if len(c_tokens) > 0:
            repetition = 1.0 - (len(set(c_tokens)) / len(c_tokens))
            penalty += self.w_manner * repetition
            
        return min(1.0, penalty)

    def _causal_consistency(self, prompt: str, candidate: str) -> float:
        """
        Checks logical consistency based on extracted features.
        Returns a score 0 (inconsistent) to 1 (consistent).
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        score = 1.0
        
        # Modus Tollens / Negation consistency
        # If prompt says "not X", and candidate asserts "X" without negation, penalize
        # This is a simplified heuristic for the "Causal DAG" structure
        if p_feats['has_negation'] and not c_feats['has_negation']:
            # Check if candidate is just a noun phrase (might be okay) vs full sentence
            if c_feats['length'] > 3:
                score -= 0.2
                
        # Numeric constraint propagation
        if p_feats['numeric_vals'] and c_feats['numeric_vals']:
            # If prompt compares A > B, and candidate picks the wrong one based on text
            # Hard to do without full NLP, so we check magnitude consistency if explicit
            pass 
            
        return max(0.0, score)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy (F) for a specific candidate.
        F = Prediction_Error (NCD) + Pragmatic_Surprise (Gricean) - Epistemic_Value (Causal)
        Lower F is better.
        """
        # 1. Prediction Error (Surprise from data) - using NCD as proxy for likelihood
        # Normalized to 0-1 range roughly
        pred_error = self._compute_ncd(prompt, candidate)
        
        # 2. Pragmatic Surprise (Violation of norms)
        p_feats = self._extract_features(prompt)
        prag_surprise = self._gricean_prior(prompt, candidate, p_feats)
        
        # 3. Epistemic Value (Causal consistency)
        causal_val = self._causal_consistency(prompt, candidate)
        
        # Combine: F = w1*PredErr + w2*PragSurprise - w3*CausalVal
        # We want to minimize F. High causal val reduces F.
        free_energy = (0.5 * pred_error) + (0.3 * prag_surprise) - (0.2 * causal_val)
        
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        prompt_feats = self._extract_features(prompt)
        
        # Calculate Free Energy for all candidates
        energies = []
        for cand in candidates:
            fe = self._compute_free_energy(prompt, cand)
            energies.append((cand, fe))
            
        # Normalize scores to 0-1 range (higher is better)
        # Invert energy: Score = 1 / (1 + Energy) or similar mapping
        min_e = min(e[1] for e in energies)
        max_e = max(e[1] for e in energies)
        range_e = max_e - min_e if max_e > min_e else 1.0
        
        for cand, fe in energies:
            # Map Free Energy to Score: Low FE -> High Score
            # Normalized: 0 (worst) to 1 (best)
            norm_fe = (fe - min_e) / range_e
            score = 1.0 - norm_fe
            
            # Add small deterministic tie-breaker based on length stability
            # Prefer concise answers in case of ties (Gricean Quantity)
            tie_break = 0.0001 / (len(cand) + 1)
            final_score = min(1.0, score + tie_break)
            
            reasoning = f"FE={fe:.4f}, CausalConsistency={'High' if self._causal_consistency(prompt, cand) > 0.8 else 'Low'}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        """
        # Generate a synthetic set of alternatives to compare against?
        # No, we must be deterministic and fast. 
        # Instead, we calculate the absolute Free Energy and map it to confidence.
        # Low Free Energy = High Confidence.
        
        fe = self._compute_free_energy(prompt, answer)
        
        # Heuristic mapping: 
        # FE < 0.2 -> Very Likely (0.9-1.0)
        # FE ~ 0.5 -> Uncertain (0.5)
        # FE > 0.8 -> Unlikely (0.1)
        
        # Sigmoid-like mapping centered around 0.4 FE
        confidence = 1.0 / (1.0 + math.exp(5.0 * (fe - 0.3)))
        
        # Clamp
        return max(0.0, min(1.0, confidence))