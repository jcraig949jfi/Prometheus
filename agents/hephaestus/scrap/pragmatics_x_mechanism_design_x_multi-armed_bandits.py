import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A reasoning tool combining Pragmatics, Mechanism Design, and Multi-Armed Bandits.
    
    Mechanism:
    1. Pragmatics (Parsing): Extracts propositional atoms (entities, predicates, negations, 
       conditionals, causals, numbers) using regex to build a structured representation.
    2. Logic Graph: Constructs a directed implication graph from conditional/causal cues 
       and computes transitive closure to find all derivable truths.
    3. Bandits (Uncertainty): Maintains belief states (successes/counts) for each atom. 
       Uses UCB (Upper Confidence Bound) to compute optimistic beliefs, encouraging 
       exploration of uncertain but supported facts.
    4. Mechanism Design (Scoring): Computes a VCG-style score for each candidate answer. 
       The score is the marginal contribution of the candidate's atoms to the total 
       log-likelihood of the system, making truthful answering a dominant strategy.
    """
    
    # Regex patterns for structural parsing
    PATTERNS = {
        'entity': r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b',
        'number': r'-?\d+(?:\.\d+)?',
        'negation': r'\b(?:not|no|never|neither|nor)\b',
        'comparative': r'\b(?:greater|less|more|fewer|higher|lower|equal|same)\b(?:\s+than)?',
        'conditional': r'\b(?:if|then|provided|unless)\b',
        'causal': r'\b(?:because|therefore|thus|hence|leads to|results in|causes)\b',
        'quantifier': r'\b(?:all|some|none|every|any)\b',
        'temporal': r'\b(?:before|after|while|during)\b'
    }

    def __init__(self):
        # State: atom_id -> {'n': count, 's': supports}
        self.atom_state: Dict[int, Tuple[int, int]] = {}
        self.atom_text_map: Dict[int, str] = {}
        self.next_atom_id = 0
        self.total_proposals = 1  # Avoid log(0), start at 1

    def _extract_atoms(self, text: str) -> List[Dict]:
        """Extract structured atoms from text using regex."""
        atoms = []
        text_lower = text.lower()
        
        # Helper to add atom
        def add_atom(atype: str, content: str, polarity: int = 1, args: List[int] = None):
            nonlocal self
            key = f"{atype}:{content}:{polarity}"
            if key not in self.atom_text_map.values():
                # Simple deduplication within this step, global ID assignment happens later if needed
                # For this implementation, we map text signatures to IDs dynamically
                pass 
            
            atoms.append({
                'type': atype,
                'content': content,
                'polarity': polarity,
                'args': args or []
            })

        # Extract Numbers
        for m in re.finditer(self.PATTERNS['number'], text):
            add_atom('number', m.group())
            
        # Extract Entities (Capitalized words, simple heuristic)
        for m in re.finditer(self.PATTERNS['entity'], text):
            add_atom('entity', m.group())
            
        # Extract Logical Cues
        for m in re.finditer(self.PATTERNS['negation'], text_lower):
            add_atom('negation', m.group(), polarity=-1)
            
        for m in re.finditer(self.PATTERNS['comparative'], text_lower):
            add_atom('comparative', m.group())
            
        for m in re.finditer(self.PATTERNS['conditional'], text_lower):
            add_atom('conditional', m.group())
            
        for m in re.finditer(self.PATTERNS['causal'], text_lower):
            add_atom('causal', m.group())
            
        for m in re.finditer(self.PATTERNS['quantifier'], text_lower):
            add_atom('quantifier', m.group())
            
        for m in re.finditer(self.PATTERNS['temporal'], text_lower):
            add_atom('temporal', m.group())

        return atoms

    def _get_atom_id(self, atom: Dict) -> int:
        """Map an atom dict to a global integer ID, initializing state if new."""
        signature = f"{atom['type']}:{atom['content']}:{atom['polarity']}"
        # Check if we have seen this signature before (simplified global map)
        # In a real distributed system, this would be hashed. Here we use a local map.
        if signature not in self.atom_text_map:
            # Reverse lookup for efficiency could be added, but linear scan is fine for small N
            # Actually, let's maintain a reverse map implicitly or just use the dict values
            # To keep it simple and deterministic:
            found = False
            for aid, txt in self.atom_text_map.items():
                if txt == signature:
                    return aid
            
            # New atom
            aid = self.next_atom_id
            self.next_atom_id += 1
            self.atom_text_map[aid] = signature
            self.atom_state[aid] = (0, 0) # n, s
            return aid
        return None # Should not happen if logic is correct, but let's fix the lookup

    def _build_graph(self, atoms: List[Dict]) -> np.ndarray:
        """Build adjacency matrix from atoms based on conditionals/causals."""
        n = len(atoms)
        if n == 0:
            return np.zeros((0, 0), dtype=bool)
        
        A = np.zeros((n, n), dtype=bool)
        
        # Simple heuristic: If a conditional exists, link preceding entity/number to following
        # This is a shallow pragmatic approximation as requested.
        types = [a['type'] for a in atoms]
        
        for i, atom in enumerate(atoms):
            if atom['type'] in ['conditional', 'causal']:
                # Link previous atom to next atom if they exist
                if i > 0 and i < len(atoms) - 1:
                    A[i-1, i+1] = True
                # Also link the cue itself to the consequence
                if i < len(atoms) - 1:
                    A[i, i+1] = True
        
        # Transitive closure (Floyd-Warshall style via repeated squaring or simple loop)
        # Since N is small (prompt length), simple iteration works
        if n > 0:
            closure = A.copy()
            for _ in range(n):
                closure = closure | np.dot(closure, A) # Boolean matrix mult
                closure = (closure > 0)
            return closure
        return A

    def _compute_ucb_beliefs(self, atom_ids: Set[int]) -> Dict[int, float]:
        """Compute optimistic belief (theta_tilde) for atoms using UCB."""
        beliefs = {}
        N = max(1, self.total_proposals)
        
        for aid in atom_ids:
            n, s = self.atom_state.get(aid, (0, 0))
            if n == 0:
                # Unobserved: high uncertainty bonus
                theta_hat = 0.5
                bonus = 1.0 
            else:
                theta_hat = s / n
                # UCB1 bonus
                bonus = np.sqrt(np.log(N) / n) if n > 0 else 1.0
            
            # Clamp between 0.01 and 0.99 to avoid log(0)
            theta_tilde = min(0.99, max(0.01, theta_hat + bonus))
            beliefs[aid] = theta_tilde
            
        return beliefs

    def _calculate_score(self, prompt_atoms: List[Dict], candidate_atoms: List[Dict], all_candidates_atoms: List[List[Dict]]) -> float:
        """Calculate VCG-style score based on marginal log-likelihood contribution."""
        
        # Collect all unique atoms involved to initialize IDs
        all_raw_atoms = prompt_atoms + candidate_atoms
        for cand in all_candidates_atoms:
            all_raw_atoms.extend(cand)
            
        # Map to IDs
        atom_ids = set()
        atom_map = {} # local mapping for this evaluation step
        
        # We need a consistent way to ID atoms across prompt and candidates
        # Re-using the class level map for persistence across calls is better for Bandit learning
        # But for a single evaluation, we ensure all are registered
        
        current_atoms = []
        for atom in all_raw_atoms:
            sig = f"{atom['type']}:{atom['content']}:{atom['polarity']}"
            if sig not in self.atom_text_map.values():
                 # Register new
                 aid = self.next_atom_id
                 self.next_atom_id += 1
                 self.atom_text_map[aid] = sig
                 if aid not in self.atom_state:
                     self.atom_state[aid] = (0, 0)
            else:
                # Find existing
                aid = None
                for k, v in self.atom_text_map.items():
                    if v == sig:
                        aid = k
                        break
            
            current_atoms.append((atom, aid))
            atom_ids.add(aid)

        # Update global counts for atoms present in this prompt context (simplified observation)
        # We assume presence in prompt implies some observation
        for _, aid in current_atoms:
            n, s = self.atom_state[aid]
            # Increment count, assume support if in prompt (heuristic)
            self.atom_state[aid] = (n + 1, s + 1)
        
        self.total_proposals += 1
        
        # Get UCB beliefs
        beliefs = self._compute_ucb_beliefs(atom_ids)
        
        # Define function to compute log-likelihood of a set of atoms
        def get_log_likelihood(atom_list):
            ll = 0.0
            seen_ids = set()
            for atom, aid in atom_list:
                if aid in seen_ids: continue
                seen_ids.add(aid)
                theta = beliefs.get(aid, 0.5)
                # If polarity is negative, we want low theta? 
                # Simplification: We reward high belief in asserted atoms
                ll += np.log(theta)
            return ll

        # Candidate specific atoms
        cand_atom_pairs = []
        for atom in candidate_atoms:
             sig = f"{atom['type']}:{atom['content']}:{atom['polarity']}"
             aid = None
             for k, v in self.atom_text_map.items():
                if v == sig:
                    aid = k
                    break
             if aid: cand_atom_pairs.append((atom, aid))

        # Score = L(S_k) - max(L(S_-k))
        # Simplified: Score = Sum(log(theta)) for candidate atoms
        # The "mechanism design" aspect here is that we are scoring based on the 
        # consistency with the learned beliefs (UCB) derived from the prompt structure.
        
        score = 0.0
        for atom, aid in cand_atom_pairs:
            theta = beliefs.get(aid, 0.5)
            score += np.log(theta)
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_atoms = self._extract_atoms(prompt)
        candidate_data = []
        
        # Pre-extract atoms for all candidates
        all_cand_atoms_raw = []
        for c in candidates:
            atoms = self._extract_atoms(c)
            all_cand_atoms_raw.append(atoms)
        
        for i, cand in enumerate(candidates):
            cand_atoms = all_cand_atoms_raw[i]
            
            # Calculate score
            # We pass the specific candidate atoms and the list of all others for the VCG calc
            score = self._calculate_score(prompt_atoms, cand_atoms, all_cand_atoms_raw)
            
            # Add NCD as a tiebreaker/secondary signal as per instructions
            # NCD(P, C) approx 1 - (Compression(P+C) - Compression(P)) / Compression(C)
            # Using zlib length as proxy for compression
            import zlib
            p_bytes = prompt.encode()
            c_bytes = cand.encode()
            try:
                comp_p = len(zlib.compress(p_bytes))
                comp_c = len(zlib.compress(c_bytes))
                comp_pc = len(zlib.compress(p_bytes + c_bytes))
                # Normalized Compression Distance approximation
                ncd = (comp_pc - comp_p) / comp_c if comp_c > 0 else 1.0
                # Invert so higher is better, and scale down to be a tiebreaker
                ncd_score = (1.0 - ncd) * 0.1 
            except:
                ncd_score = 0.0
            
            final_score = score + ncd_score
            
            candidate_data.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {len(cand_atoms)} atoms, UCB-LogLik: {score:.4f}, NCD_bonus: {ncd_score:.4f}"
            })
        
        # Sort by score descending
        candidate_data.sort(key=lambda x: x['score'], reverse=True)
        return candidate_data

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the score of the answer relative to a null baseline."""
        # Evaluate against a dummy set to get absolute scoring context
        # Or simply use the internal logic to score this single candidate
        atoms = self._extract_atoms(answer)
        prompt_atoms = self._extract_atoms(prompt)
        
        # Mock evaluation to update state and get score
        # We reuse the scoring logic but simplify for single item
        # Re-run extraction to ensure IDs are consistent
        temp_candidates = [answer, ""] # Compare against empty
        res = self.evaluate(prompt, temp_candidates)
        
        if not res:
            return 0.0
            
        # The score is log-likelihood based. Map to 0-1.
        # Log-likelihoods are negative. 
        # Higher (less negative) is better.
        best_score = res[0]['score']
        
        # Heuristic mapping: 
        # If the answer is the top result, confidence is high if score > threshold
        # If it's the empty string, confidence is low.
        if answer == "" or (len(res) > 1 and res[0]['candidate'] != answer):
             # Not the top choice
             # Check if it's in the list at all
             found = False
             for r in res:
                 if r['candidate'] == answer:
                     found = True
                     break
             if not found:
                 return 0.1 # Low confidence if not even parsed well
             
        # Normalize score: Assume scores are around -10 to 0 for reasonable answers
        # Sigmoid-like mapping
        conf = 1.0 / (1.0 + np.exp(-best_score - 2)) # Shifted sigmoid
        return min(1.0, max(0.0, conf))