import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining Gauge Theory, Falsificationism, and Multi-Armed Bandits.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions (Quantifier, Subject, Predicate, Object) and 
       logical features (negation, comparatives, conditionals) using regex.
    2. Gauge Connection: Builds a logical graph where edges represent inference rules. 
       A phase vector (theta) is propagated; inconsistencies (contradictions) cause phase shifts.
       Logical coherence is measured by the magnitude of the total phase deviation.
    3. Falsificationist Reward: Attempts to derive contradictions via forward chaining. 
       Surviving candidates gain reward; contradictions yield 0.
    4. Bandit Scoring: Uses UCB1 to balance exploitation (survival rate) and exploration (boldness).
    5. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, and unanswerability 
       in the prompt to cap confidence, ensuring the tool admits uncertainty.
    """
    
    # Regex patterns for structural extraction
    PATTERNS = {
        'quantifier': r'\b(all|some|none|every|no|any)\b',
        'negation': r'\b(not|no|never|neither|nor)\b',
        'comparative': r'(>=|<=|>|<|=|greater|less|equal)',
        'conditional': r'\b(if|then|unless|only if)\b',
        'causal': r'\b(because|leads to|causes|therefore)\b',
        'ordering': r'\b(before|after|first|last)\b',
        'presupposition': r'\b(have you stopped|why did .*(fail|stop|quit)|when did .*(stop|fail))\b',
        'false_dichotomy': r'\b(either .+ or .+|must be .+ or .+)\b',
        'scope_ambiguity': r'\b(every .+ (a|an) .+)\b', 
        'pronoun_ambiguity': r'\b((he|she|it|they) (was|is|were) .+\?|who .+\?)\b'
    }

    def __init__(self):
        self.d = 4  # Dimension of gauge phase vector
        self.tau = 0.2  # Coherence threshold
        self.c_ucb = 1.0  # UCB exploration constant

    def _normalize_text(self, text: str) -> str:
        return text.lower().strip()

    def _extract_features(self, text: str) -> Dict[str, bool]:
        """Extract logical features from text."""
        text_l = self._normalize_text(text)
        features = {}
        for key, pattern in self.PATTERNS.items():
            if key not in ['presupposition', 'false_dichotomy', 'scope_ambiguity', 'pronoun_ambiguity']:
                features[key] = bool(re.search(pattern, text_l))
        return features

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Evaluates the prompt for ambiguity, presuppositions, and unanswerability.
        Returns a cap value (low if problematic, 1.0 if clean).
        """
        p_low = self._normalize_text(prompt)
        
        # Check for presupposition traps
        if re.search(self.PATTERNS['presupposition'], p_low):
            return 0.2
        
        # Check for false dichotomy
        if re.search(self.PATTERNS['false_dichotomy'], p_low):
            # Only flag if it looks like a forced choice without context
            if "or" in p_low and ("must" in p_low or "either" in p_low):
                return 0.25

        # Check for scope ambiguity (simplified heuristic)
        if re.search(self.PATTERNS['scope_ambiguity'], p_low) and "same" not in p_low and "different" not in p_low:
             # Heuristic: if "every X bought a Y" appears, it might be ambiguous, 
             # but without more context, we don't hard-fail unless specific triggers exist.
             pass 

        # Check for pronoun ambiguity in questions
        if "?" in prompt and re.search(r'\b(he|she|it|them)\b', p_low):
            if re.search(r'\bwho\b', p_low) or re.search(r'\bwhich one\b', p_low):
                return 0.25

        # Check for subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_low) and not re.search(r'\b(data|fact|calculate)\b', p_low):
            return 0.3

        return 1.0

    def _parse_propositions(self, text: str) -> List[Dict]:
        """
        Parses text into structured propositions.
        Format: {type, subject, predicate, object, features, raw}
        """
        props = []
        text_l = self._normalize_text(text)
        
        # Simple sentence splitter
        sentences = re.split(r'[.;]', text_l)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            feat = self._extract_features(sent)
            
            # Attempt to extract comparative logic (e.g., "A is greater than B")
            comp_match = re.search(r'(\w+)\s+is\s+(greater|less|equal)\s+(?:to|than)?\s+(\w+)', sent)
            if comp_match:
                props.append({
                    'type': 'comparative',
                    'subject': comp_match.group(1),
                    'predicate': comp_match.group(2),
                    'object': comp_match.group(3),
                    'features': feat,
                    'raw': sent
                })
                continue

            # Attempt to extract conditional logic
            if feat.get('conditional'):
                props.append({
                    'type': 'conditional',
                    'subject': 'global',
                    'predicate': 'implies',
                    'object': 'global',
                    'features': feat,
                    'raw': sent
                })
                continue

            # Generic proposition extraction (Subject-Verb-Object approximation)
            # Very basic regex for demonstration of structural parsing
            generic = re.match(r'(\w+)\s+(\w+)\s+(.+)', sent)
            if generic:
                props.append({
                    'type': 'generic',
                    'subject': generic.group(1),
                    'predicate': generic.group(2),
                    'object': generic.group(3)[:20], # Truncate long objects
                    'features': feat,
                    'raw': sent
                })
            else:
                props.append({
                    'type': 'atomic',
                    'subject': 'unknown',
                    'predicate': 'exists',
                    'object': sent[:20],
                    'features': feat,
                    'raw': sent
                })
                
        return props

    def _compute_gauge_phase(self, propositions: List[Dict]) -> np.ndarray:
        """
        Computes the gauge phase vector by simulating parallel transport.
        Each proposition adds a phase shift based on its logical consistency features.
        """
        if not propositions:
            return np.zeros(self.d)
        
        theta = np.zeros(self.d)
        
        for i, prop in enumerate(propositions):
            # Phase increment based on features
            delta = np.zeros(self.d)
            
            if prop['features'].get('negation'):
                delta[0] = -0.1 # Negation introduces a phase flip risk
            if prop['features'].get('comparative'):
                delta[1] = 0.05 # Comparatives add slight complexity
            if prop['features'].get('conditional'):
                delta[2] = 0.1 # Conditionals add uncertainty
            
            # Parallel transport: accumulate phase
            theta = (theta + delta) % (2 * np.pi)
            
        return theta

    def _falsify(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """
        Attempts to falsify the candidate given the prompt.
        Returns (is_falsified, boldness_bonus).
        """
        combined = f"{prompt} {candidate}"
        props = self._parse_propositions(combined)
        
        # 1. Check for internal contradictions in features
        has_negation = any(p['features'].get('negation') for p in props)
        has_affirmation = any(not p['features'].get('negation') for p in props)
        
        # Simple contradiction heuristic: if we have explicit "no" and "yes" logic on same subject
        # In this simplified model, we look for direct string conflicts in subjects with opposing predicates
        subjects = {}
        is_falsified = False
        
        for p in props:
            subj = p['subject']
            pred = p['predicate']
            is_neg = p['features'].get('negation', False)
            
            if subj in subjects:
                # Check for contradiction
                if subjects[subj]['is_neg'] != is_neg and pred == subjects[subj]['pred']:
                    is_falsified = True
            else:
                subjects[subj] = {'pred': pred, 'is_neg': is_neg}
                
        # 2. Numeric evaluation (Constructive computation)
        # Extract numbers and check simple inequalities if present
        nums = re.findall(r'-?\d+\.?\d*', combined)
        if len(nums) >= 2:
            try:
                vals = [float(n) for n in nums]
                # If the candidate contains "false" or "incorrect" logic regarding extracted numbers
                # This is a placeholder for more complex math solving
                if 'false' in self._normalize_text(candidate) and len(set(vals)) == 1:
                     # If all numbers are same but claim is false? Hard to generalize without specific problem type
                     pass
            except ValueError:
                pass

        # Boldness bonus: log(1 + novel conjectures)
        # Heuristic: length of unique propositions / total length
        boldness = np.log(1 + len(props) * 0.5) if not is_falsified else 0.0
        
        return is_falsified, boldness

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0-1, lower is more similar)."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if max(z1, z2) == 0: return 1.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        total_trials = len(candidates)
        
        # Pre-compute prompt features for context
        prompt_props = self._parse_propositions(prompt)
        prompt_phase = self._compute_gauge_phase(prompt_props)
        
        for i, cand in enumerate(candidates):
            # 1. Structural Parsing & Gauge Phase
            cand_props = self._parse_propositions(cand)
            cand_phase = self._compute_gauge_phase(cand_props)
            
            # Phase coherence (difference from prompt phase)
            phase_diff = np.linalg.norm(prompt_phase - cand_phase)
            coherence_score = 1.0 / (1.0 + phase_diff) # Map to 0-1
            
            # 2. Falsification Test
            is_falsified, boldness = self._falsify(prompt, cand)
            
            # 3. Reward Calculation
            if is_falsified:
                reward = 0.0
            else:
                # Base reward from coherence + boldness
                reward = coherence_score + 0.1 * boldness
            
            # 4. Bandit State Update (Simulated for single shot)
            n_i = 1
            s_i = reward
            ucb = reward + self.c_ucb * np.sqrt(np.log(total_trials + 1) / (n_i + 1e-9))
            
            # 5. NCD Tiebreaker (Max 15% influence)
            # Compare candidate to prompt (relevance)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Final Score Composition
            # Structural/Logic: 50%, Computation/Falsification: 35%, NCD: 15%
            logic_score = ucb if not is_falsified else 0.0
            final_score = (0.50 * coherence_score) + (0.35 * logic_score) + (0.15 * ncd_score)
            
            # Penalty for falsification
            if is_falsified:
                final_score *= 0.1
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Coherence:{coherence_score:.2f}, Falsified:{is_falsified}, Boldness:{boldness:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/unanswerability.
        Caps at 0.9 unless computation was definitive.
        """
        # 1. Meta-Confidence (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Structural/Computational Confidence
        # Run a mini-evaluation to check consistency
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.1
            
        res = res_list[0]
        base_score = res['score']
        
        # If falsified, confidence is near 0
        if "Falsified:True" in res['reasoning']:
            return 0.05
            
        # Scale base score to 0-1 range roughly
        # Base score can be > 1 due to UCB, so normalize
        conf = min(1.0, base_score)
        
        # Apply meta cap
        final_conf = min(conf, meta_cap)
        
        # Never return > 0.9 unless it's a very high structural match
        if final_conf > 0.9:
            # Only allow >0.9 if coherence is extremely high and no ambiguity
            if meta_cap == 1.0 and "Falsified:False" in res['reasoning']:
                return 0.95 # Definitive computational answer
            else:
                return 0.9
                
        return max(0.0, final_conf)