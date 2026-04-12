import re
import numpy as np
import zlib

class ReasoningTool:
    """
    Soft-Structure-Match Abductive Scorer (SSMAS).
    Mechanism:
    1. Parses text into a soft logical graph (vertices=atoms, edges=relations).
    2. Uses differentiable constraint propagation (gradient descent on truth values)
       to find a logically consistent state for the prompt and candidates.
    3. Scores candidates based on structural similarity to the prompt's resolved state
       and an abductive penalty for missing explanatory links.
    4. Falls back to NCD only if structural signals are weak.
    """
    
    def __init__(self):
        self.alpha = 0.1
        self.steps = 20
        self.sigma = 0.5
        self.lam = 2.0

    def _tokenize(self, text):
        return re.findall(r"\b\w+\b|[^\s\w]", text.lower())

    def _extract_atoms_and_edges(self, text):
        tokens = self._tokenize(text)
        atoms = []
        edges = []
        seen = set()
        
        # Simple atom extraction (nouns/verbs as placeholders)
        for t in tokens:
            if t not in seen and len(t) > 2 and t not in self._stopwords():
                atoms.append(t)
                seen.add(t)
        
        if not atoms:
            return [], []

        # Build edges based on keywords
        text_l = text.lower()
        
        # Negation
        if any(w in text_l for w in ["not", "no", "never", "none"]):
            for i, a in enumerate(atoms):
                # Connect negation cue to nearby atoms (simplified to first/last for brevity)
                edges.append((0, i, 'negates')) 
                
        # Conditionals
        if any(w in text_l for w in ["if", "then", "unless", "implies"]):
            for i in range(len(atoms) - 1):
                edges.append((i, i + 1, 'implies'))
                
        # Causal
        if any(w in text_l for w in ["because", "causes", "leads"]):
            for i in range(len(atoms) - 1):
                edges.append((i, i + 1, 'causes'))

        # Comparatives (Numeric check)
        nums = re.findall(r"\d+\.?\d*", text)
        if len(nums) >= 2:
            # Link numeric values if present
            if nums[0] in text and nums[1] in text:
                 # Mock edge for numeric constraint
                 pass 

        # Default connectivity to ensure graph isn't empty
        if not edges and len(atoms) > 1:
            for i in range(len(atoms) - 1):
                edges.append((i, i+1, 'implies'))
                
        return atoms, edges

    def _stopwords(self):
        return {"the", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "into", "through", "during", "before", "after", "above", "below", "between", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "each", "few", "more", "most", "other", "some", "such", "only", "own", "same", "so", "than", "too", "very", "just", "and", "but", "if", "or", "because", "until", "while", "although", "though", "since", "lest"}

    def _propagate(self, atoms, edges, init_bias=0.5):
        if not atoms:
            return np.array([0.5]), 0.0
            
        n = len(atoms)
        s = np.full(n, init_bias, dtype=np.float32)
        
        # Adjust init based on explicit affirmations/negations in text (simplified)
        # Here we rely on the gradient descent to fix consistency
        
        for _ in range(self.steps):
            loss = 0.0
            grads = np.zeros_like(s)
            
            for i, j, rtype in edges:
                if i >= n or j >= n: continue
                
                si, sj = s[i], s[j]
                l_val = 0.0
                g_i, g_j = 0.0, 0.0
                
                if rtype == 'implies' or rtype == 'causes':
                    # Loss: max(0, si - sj)^2
                    diff = si - sj
                    if diff > 0:
                        l_val = diff * diff
                        g_i = 2 * diff
                        g_j = -2 * diff
                elif rtype == 'negates':
                    # Loss: (sj - (1-si))^2 -> sj + si - 1 = 0
                    val = si + sj - 1.0
                    l_val = val * val
                    g_i = 2 * val
                    g_j = 2 * val
                elif rtype == 'equals':
                    diff = si - sj
                    l_val = diff * diff
                    g_i = 2 * diff
                    g_j = -2 * diff
                    
                loss += l_val
                grads[i] += g_i
                grads[j] += g_j
            
            if np.linalg.norm(grads) < 1e-4:
                break
                
            s -= self.alpha * grads
            s = np.clip(s, 0.0, 1.0)
            
        return s, loss

    def _compute_ncd(self, s1, s2):
        if not s1 or not s2: return 1.0
        l1, l2 = len(s1), len(s2)
        if l1 == 0 or l2 == 0: return 1.0
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return max(c1, c2) / min(c1, c2) if min(c1, c2) > 0 else 1.0
        except:
            return 1.0

    def evaluate(self, prompt, candidates):
        p_atoms, p_edges = self._extract_atoms_and_edges(prompt)
        p_vec, p_loss = self._propagate(p_atoms, p_edges, init_bias=0.8) # Prompt assumed true-ish
        
        results = []
        max_score = -1.0
        
        # Pre-calculate structural signal strength
        has_structure = len(p_edges) > 0

        for cand in candidates:
            c_atoms, c_edges = self._extract_atoms_and_edges(cand)
            c_vec, c_loss = self._propagate(c_atoms, c_edges, init_bias=0.5)
            
            score = 0.0
            reasoning = ""
            
            if has_structure and len(p_atoms) > 0 and len(c_atoms) > 0:
                # Structural Matching
                min_len = min(len(p_vec), len(c_vec))
                p_trim = p_vec[:min_len]
                c_trim = c_vec[:min_len]
                
                # Pad if necessary (simple zero pad)
                if len(p_trim) < len(c_trim):
                    p_trim = np.pad(p_trim, (0, len(c_trim)-len(p_trim)), 'constant')
                elif len(c_trim) < len(p_trim):
                    c_trim = np.pad(c_trim, (0, len(p_trim)-len(c_trim)), 'constant')
                    
                dist = np.linalg.norm(p_trim - c_trim)
                s_struct = np.exp(-(dist**2) / (self.sigma**2))
                
                # Abductive Hypothesis Score
                # Flag vertices in candidate that are low truth but strongly implied by prompt structure
                h_count = 0
                for i, val in enumerate(c_trim):
                    if val < 0.3 and i < len(p_trim) and p_trim[i] > 0.7:
                        h_count += 1
                s_hyp = np.exp(-self.lam * h_count)
                
                score = float(s_struct * s_hyp)
                reasoning = f"Structural similarity: {s_struct:.2f}, Abductive penalty: {h_count} gaps."
            else:
                # Fallback to NCD if no structure detected
                ncd = self._compute_ncd(prompt, cand)
                score = 1.0 - ncd # Invert distance to similarity
                reasoning = "No logical structure detected; using compression similarity."

            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
            if score > max_score: max_score = score

        # Normalize scores relative to best found to ensure meaningful ranking
        if max_score > 0:
            for r in results:
                r['score'] = r['score'] / max_score if max_score != 0 else 0.0
        
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt, answer):
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']