import re
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    Hybrid Reasoning Tool: Structural Parsing + Embodied Ergodic Propagation.
    
    Mechanism:
    1. Parses prompt into (subject, predicate, object, modality) tuples using regex.
    2. Grounds content words to 3D embodied vectors (weight, size, motion).
    3. Builds a weighted adjacency matrix where edge weights reflect modality strength.
    4. Runs belief propagation (power iteration) to find steady-state entity importance.
    5. Uses FFT on the belief trajectory to measure ergodic consistency (stability).
    6. Scores candidates based on semantic alignment with stable entities and low spectral noise.
    7. Falls back to NCD only if structural signals are absent.
    """
    
    # Embodied lookup: (weight, size, motion)
    EMBODIED_LEXICON = {
        'heavy': (1.0, 0.0, 0.0), 'light': (0.2, 0.0, 0.0),
        'large': (0.0, 1.0, 0.0), 'big': (0.0, 1.0, 0.0), 'small': (0.0, 0.3, 0.0),
        'fast': (0.0, 0.0, 1.0), 'slow': (0.0, 0.0, 0.2), 'quick': (0.0, 0.0, 1.0),
        'strong': (1.0, 0.5, 0.0), 'weak': (0.1, 0.1, 0.0),
        'move': (0.0, 0.0, 1.0), 'push': (0.8, 0.0, 0.5), 'pull': (0.8, 0.0, 0.5),
        'lift': (0.8, 0.0, 0.5), 'drop': (0.5, 0.0, 0.8),
        'more': (0.5, 0.5, 0.0), 'less': (0.2, 0.2, 0.0),
        'before': (0.0, 0.0, 0.5), 'after': (0.0, 0.0, 0.5)
    }

    MODALITY_WEIGHTS = {
        'affirm': 1.0, 'negation': -1.0, 'comparative': 0.5,
        'conditional': 0.8, 'causal': 0.9, 'order': 1.2
    }

    def __init__(self):
        self.entities = []
        self.adj_matrix = None
        self.ergodic_score = 0.0
        self.has_structure = False

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def _get_embodied_vector(self, word):
        return np.array(self.EMBODIED_LEXICON.get(word, (0.0, 0.0, 0.0)))

    def _parse_sentence(self, sentence):
        """Extracts (subject, predicate, object, modality) using regex patterns."""
        sentence = sentence.strip().lower()
        if not sentence:
            return None
        
        # Patterns
        patterns = [
            # Causal: A leads to B / A because B
            (r'(\w+)\s+(leads?\s+to|causes|because)\s+(\w+)', 'causal'),
            # Conditional: If A then B
            (r'if\s+(\w+).*?then\s+(\w+)', 'conditional'),
            # Comparative: A is more/greater than B
            (r'(\w+)\s+(is\s+)?(more|less|greater|smaller)\s+(than)?\s+(\w+)', 'comparative'),
            # Order: A before/after B
            (r'(\w+)\s+(before|after)\s+(\w+)', 'order'),
            # Negation: A does not B / A is not B
            (r'(\w+)\s+(?:does\s+not|is\s+not|cannot)\s+(\w+)', 'negation'),
            # Simple Affirmation: A verbs B
            (r'(\w+)\s+(moves|pushes|pulls|lifts|hits|is)\s+(\w+)', 'affirm')
        ]
        
        for pattern, modality in patterns:
            match = re.search(pattern, sentence)
            if match:
                groups = match.groups()
                if modality == 'comparative':
                    # groups: (A, is, more/less, than, B) -> A, B
                    return (groups[0], groups[2], groups[4], modality)
                elif modality == 'order':
                    # groups: (A, before/after, B)
                    return (groups[0], groups[1], groups[2], modality)
                elif modality == 'conditional':
                    # groups: (A, B)
                    return (groups[0], 'implies', groups[1], modality)
                elif modality == 'causal':
                    # groups: (A, leads/causes, B)
                    return (groups[0], groups[1], groups[2], modality)
                elif modality == 'negation':
                    # groups: (A, verb) - treat as A -> NOT verb? Simplified to A->B with neg weight
                    return (groups[0], groups[1], groups[0], modality) # Self-loop negation or target
                else:
                    # Affirm: (A, verb, B)
                    return (groups[0], groups[1], groups[2], 'affirm')
        return None

    def _build_graph(self, prompt):
        sentences = re.split(r'[.\n]', prompt)
        triples = []
        all_entities = set()
        
        for sent in sentences:
            parsed = self._parse_sentence(sent)
            if parsed:
                triples.append(parsed)
                all_entities.add(parsed[0])
                all_entities.add(parsed[2])
        
        if not all_entities:
            return [], None, False
            
        self.entities = list(all_entities)
        n = len(self.entities)
        entity_idx = {e: i for i, e in enumerate(self.entities)}
        A = np.zeros((n, n))
        
        for sub, pred, obj, mod in triples:
            if sub not in entity_idx or obj not in entity_idx:
                continue
            i, j = entity_idx[sub], entity_idx[obj]
            
            # Base weight
            w = self.MODALITY_WEIGHTS.get(mod, 1.0)
            
            # Embodied grounding contribution
            e_sub = self._get_embodied_vector(sub)
            e_obj = self._get_embodied_vector(obj)
            
            # Add outer product scaled by weight to adjacency
            # We simplify: A[i,j] accumulates weight * (e_sub dot e_obj + 1)
            # This grounds the relation in physical properties
            embodiment_factor = np.dot(e_sub, e_obj) + 0.1 
            A[i, j] += w * embodiment_factor
            
        return self.entities, A, True

    def _run_belief_propagation(self, A, steps=20):
        if A is None or A.size == 0:
            return np.array([]), 0.0
            
        n = A.shape[0]
        if n == 0:
            return np.array([]), 0.0
            
        # Normalize rows for transition probability (row-stochastic)
        row_sums = A.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        P = A / row_sums
        
        # Uniform start
        b = np.ones(n) / n
        history = [b.copy()]
        
        for _ in range(steps):
            b_next = P.T @ b  # Column vector update
            # L1 Normalize
            total = np.sum(b_next)
            if total > 0:
                b_next = b_next / total
            history.append(b_next)
            b = b_next
            
        B = np.array(history) # Shape (T, n)
        
        # Spectral-Ergodic Scoring
        # FFT along time axis (axis=0)
        F = np.fft.fft(B, axis=0)
        
        # Zero freq (mean)
        F0 = F[0, :] 
        # Non-zero freq magnitude (instability/noise)
        F_noise = np.linalg.norm(F[1:, :], axis=0)
        
        # Ergodic score: High mean, low noise
        # Avoid division by zero
        denom = np.linalg.norm(F0) + 1e-9
        stability = 1.0 - (np.linalg.norm(F_noise) / denom)
        stability = max(0.0, min(1.0, stability))
        
        return F0, stability

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2:
            return 1.0
        c1 = len(compress(s1.encode()))
        c2 = len(compress(s2.encode()))
        c12 = len(compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # 1. Structural Parsing & Graph Build
        entities, A, has_struct = self._build_graph(prompt)
        self.has_structure = has_struct
        
        final_scores = []
        
        # 2. Belief Propagation & Spectral Analysis
        if has_struct and len(entities) > 0:
            F0, stability = self._run_belief_propagation(A)
            self.ergodic_score = stability
            
            # Map entities to belief values
            entity_beliefs = {e: float(F0[i]) for i, e in enumerate(entities)}
            
            for cand in candidates:
                cand_tokens = self._tokenize(cand)
                score = 0.0
                match_count = 0
                
                # Score based on embodied belief alignment
                for token in cand_tokens:
                    if token in entity_beliefs:
                        score += entity_beliefs[token]
                        match_count += 1
                    # Bonus for embodied words present in lexicon even if not explicit entities
                    elif token in self.EMBODIED_LEXICON:
                        score += 0.1 
                
                # Normalize by candidate length to avoid bias, but keep absolute score for matching
                if match_count > 0:
                    structural_score = 0.7 * (score / (match_count + 1)) + 0.3 * stability
                else:
                    structural_score = 0.0
                
                final_scores.append((cand, structural_score))
        else:
            # Fallback if no structure found
            final_scores = [(c, 0.0) for c in candidates]

        # 3. Ranking Logic
        # Sort by structural score descending
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Tie-breaking with NCD if scores are close or zero
        results = []
        for i, (cand, score) in enumerate(final_scores):
            reasoning = "Structural match" if score > 0.1 else "Fallback/NCD"
            
            # If scores are effectively tied (or all zero), use NCD against prompt
            if i > 0 and abs(score - final_scores[i-1][1]) < 0.01:
                # Higher NCD means less similar, we want similarity? 
                # Actually for reasoning, if structural fails, we might prefer concise answers or specific patterns.
                # But per instructions: NCD as tiebreaker.
                ncd_val = self._ncd_score(prompt, cand)
                # Adjust score slightly by NCD (lower NCD = more similar = slightly better tiebreaker)
                score -= ncd_val * 0.001 
                reasoning = "Tie-broken by NCD"

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural consistency and ergodic stability."""
        # Re-run lightweight evaluation for this specific pair
        temp_results = self.evaluate(prompt, [answer])
        if not temp_results:
            return 0.0
            
        base_score = temp_results[0]['score']
        
        # Boost if structural parsing was successful and ergodic stability is high
        if self.has_structure:
            # Combine base score with global stability metric
            conf = 0.5 * (base_score + self.ergodic_score)
            return min(1.0, max(0.0, conf))
        
        # If no structure, rely on NCD similarity as a weak proxy
        ncd = self._ncd_score(prompt, answer)
        return max(0.0, 1.0 - ncd) # Invert NCD so similar = high confidence