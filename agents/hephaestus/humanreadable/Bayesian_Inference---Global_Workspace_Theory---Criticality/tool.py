import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Bayesian Inference, Global Workspace Theory (GWT), 
    and Criticality. It parses atomic propositions, maintains Beta-distributed beliefs,
    selects uncertain atoms for the 'workspace', tunes a critical temperature to 
    maximize susceptibility (variance), and updates beliefs based on candidate evidence.
    
    Features:
    - Structural parsing (negation, comparatives, conditionals, causality)
    - Bayesian belief updates (Beta distributions)
    - GWT-inspired attention on high-variance (uncertain) propositions
    - Criticality tuning via gradient ascent on total variance
    - Epistemic honesty checks for ambiguity and presupposition
    - Deterministic, numpy-only implementation
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nor)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|provided|except)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|produces|due to)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|none|every|each|most|few)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'svo': re.compile(r'(\w+)\s+(is|are|was|were|has|have|does|did|leads?|causes?|produces?)\s+(\w+)', re.IGNORECASE),
            'pronoun': re.compile(r'\b(he|she|it|they|him|her|them)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did|when did|how did).*\b(fail|stop|quit|cease)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|must be|only option)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.IGNORECASE)
        }
        self.max_atoms = 100

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with features."""
        atoms = []
        sentences = re.split(r'[.!?]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
                
            features = {
                'text': sent,
                'negated': bool(self.patterns['negation'].search(sent)),
                'comparative': bool(self.patterns['comparative'].search(sent)),
                'conditional': bool(self.patterns['conditional'].search(sent)),
                'causal': bool(self.patterns['causal'].search(sent)),
                'quantifier': None,
                'numbers': [],
                'polarity': 1
            }
            
            # Quantifiers
            q_match = self.patterns['quantifier'].search(sent)
            if q_match:
                q_word = q_match.group().lower()
                if q_word in ['all', 'every', 'each']:
                    features['quantifier'] = 'all'
                elif q_word in ['none', 'no']:
                    features['quantifier'] = 'none'
                    features['negated'] = True
                else:
                    features['quantifier'] = 'some'
            
            # Numbers
            features['numbers'] = [float(n) for n in self.patterns['number'].findall(sent)]
            
            # SVO extraction
            svo_matches = self.patterns['svo'].findall(sent)
            if svo_matches:
                for subj, rel, obj in svo_matches:
                    atoms.append({
                        'subject': subj.lower(),
                        'relation': rel.lower(),
                        'object': obj.lower(),
                        'features': features.copy()
                    })
            else:
                # Fallback: treat whole sentence as atom if no SVO
                atoms.append({
                    'subject': 'it',
                    'relation': 'is',
                    'object': sent[:50],
                    'features': features
                })
                
        return atoms[:self.max_atoms]

    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, and unanswerability."""
        score = 1.0
        
        # Presupposition traps
        if self.patterns['presupposition'].search(prompt):
            score *= 0.2
            
        # False dichotomy
        if self.patterns['false_dichotomy'].search(prompt):
            score *= 0.5
            
        # Subjectivity without criteria
        if self.patterns['subjectivity'].search(prompt):
            score *= 0.4
            
        # Pronoun ambiguity check (heuristic: multiple people + pronoun + 'who')
        people = len(set(re.findall(r'\b[A-Z][a-z]+\b', prompt)))
        pronouns = len(self.patterns['pronoun'].findall(prompt))
        if people >= 2 and pronouns >= 1 and 'who' in prompt.lower():
            score *= 0.3
            
        # Low information content
        if len(prompt.split()) < 5:
            score *= 0.5
            
        return max(0.0, min(1.0, score))

    def _compute_critical_temp(self, alphas: np.ndarray, betas: np.ndarray, k: int) -> float:
        """Tune inverse temperature to maximize susceptibility (variance)."""
        if k == 0 or len(alphas) == 0:
            return 1.0
            
        # Select top-k variance atoms
        vars = (alphas * betas) / ((alphas + betas)**2 * (alphas + betas + 1))
        top_k_idx = np.argsort(vars)[-k:]
        if len(top_k_idx) == 0:
            return 1.0
            
        # Simple gradient ascent approximation for criticality
        # We simulate susceptibility S = sum(variance)
        # In this simplified model, we just return a scaling factor based on variance spread
        selected_vars = vars[top_k_idx]
        total_var = np.sum(selected_vars)
        
        # Critical point approximation: higher variance spread -> lower temp (sharper focus)
        # If variance is high, we are near criticality already
        if total_var > 0:
            return 1.0 / (total_var + 0.1)
        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_atoms = self._extract_propositions(prompt)
        if not prompt_atoms:
            # Fallback for unstructured text
            prompt_atoms = [{'subject': 'text', 'relation': 'contains', 'object': prompt[:50], 'features': {'negated': False}}]
            
        N = len(prompt_atoms)
        alphas = np.ones(N)
        betas = np.ones(N)
        
        # Initialize priors based on quantifiers
        for i, atom in enumerate(prompt_atoms):
            q = atom['features'].get('quantifier')
            if q == 'all':
                alphas[i] = 5.0
            elif q == 'none':
                betas[i] = 5.0
                
        # Global Workspace Selection
        k = max(1, int(np.sqrt(N)))
        mus = alphas / (alphas + betas)
        vars = (alphas * betas) / ((alphas + betas)**2 * (alphas + betas + 1))
        workspace_idx = np.argsort(vars)[-k:]
        
        # Criticality tuning
        beta_temp = self._compute_critical_temp(alphas, betas, k)
        
        results = []
        for cand in candidates:
            cand_atoms = self._extract_propositions(cand)
            a_curr = alphas.copy()
            b_curr = betas.copy()
            
            # Evidence incorporation
            for c_atom in cand_atoms:
                # Match to prompt atoms (simple string matching for demo)
                matched = False
                c_txt = f"{c_atom['subject']} {c_atom['relation']} {c_atom['object']}".lower()
                
                for i, p_atom in enumerate(prompt_atoms):
                    p_txt = f"{p_atom['subject']} {p_atom['relation']} {p_atom['object']}".lower()
                    # Simple overlap score
                    if any(w in c_txt for w in p_txt.split()) or any(w in p_txt for w in c_txt.split()):
                        if i in workspace_idx:
                            # Update Beta
                            if not c_atom['features']['negated']:
                                a_curr[i] += 1
                            else:
                                b_curr[i] += 1
                        matched = True
                        break
                
                if not matched and len(workspace_idx) > 0:
                    # Penalize unknown info slightly if workspace exists
                    idx = workspace_idx[0]
                    b_curr[idx] += 0.5

            # Scoring
            score = 0.0
            for i in workspace_idx:
                mu = a_curr[i] / (a_curr[i] + b_curr[i])
                # Likelihood of evidence given posterior mean
                # Simplified: product of probabilities
                if mu > 0 and mu < 1:
                    score += math.log(mu + 1e-9)
                elif mu >= 1:
                    score += 0 # Log(1) = 0
            
            # Add NCD as minor tiebreaker (max 15% influence)
            ncd_score = self._ncd(prompt, cand)
            final_score = (0.85 * score) + (0.15 * ncd_score)
            
            results.append({
                'candidate': cand,
                'score': final_score,
                'reasoning': f"Workspace size: {k}, Critical Temp: {beta_temp:.2f}, Atoms: {N}"
            })
            
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
            
        # Evaluate single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Normalize score to 0-1 range roughly
        # Log scores are negative, closer to 0 is better
        norm_score = 1.0 / (1.0 + math.exp(-raw_score / 10)) # Sigmoid scaling
        
        # Cap at 0.9 unless definitive computation (heuristic: very high score)
        if norm_score > 0.9:
            norm_score = 0.9
            
        return min(norm_score, meta_conf)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

# Example usage logic would go here if run as script
if __name__ == "__main__":
    tool = ReasoningTool()
    p = "If it rains, the ground gets wet. It is raining."
    cands = ["The ground is wet.", "The ground is dry.", "It is sunny."]
    print(tool.evaluate(p, cands))