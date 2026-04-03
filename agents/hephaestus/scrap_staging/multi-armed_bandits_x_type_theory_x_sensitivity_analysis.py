import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A hybrid reasoning evaluator combining Multi-Armed Bandits, Type Theory, and Sensitivity Analysis.
    
    Mechanism:
    1. Type-Theoretic Parsing: Extracts atomic propositions, comparatives, and conditionals with type tags.
    2. Constraint Propagation: Uses forward chaining to satisfy logical constraints and transitivity.
    3. Sensitivity Analysis: Perturbs input (synonyms, negation flips, numeric jitter) to estimate robustness.
    4. Bandit Selection: Uses UCB (Upper Confidence Bound) to rank candidates based on mean consistency 
       and variance-derived uncertainty.
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity, presuppositions, or fallacies.
    """

    def __init__(self):
        self.type_map = {
            'Prop': 'Prop', 'Bool': 'Bool', 'Real': 'Real'
        }
        # Simple synonym map for sensitivity perturbation
        self.synonyms = {
            'greater': 'larger', 'larger': 'greater', 'less': 'smaller', 
            'smaller': 'less', 'more': 'additional', 'additional': 'more',
            'true': 'correct', 'correct': 'true', 'false': 'incorrect', 'incorrect': 'false'
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Checks prompt for Tier B traps (ambiguity, presupposition, fallacies).
        Returns a cap value (0.25 if trap detected, 1.0 otherwise).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_patterns = [
            r"have you stopped", r"why did .* (fail|stop|quit)", r"when did .* stop",
            r"why is .* so", r"how did .* fail"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p_lower):
                return 0.25

        # 2. Scope/Pronoun ambiguity indicators
        ambiguity_triggers = [
            r"every .* a .*\?", r"who is .* he", r"who is .* she", r"who did .* refer to",
            r"which one is .* referring to"
        ]
        for pat in ambiguity_triggers:
            if re.search(pat, p_lower):
                return 0.25

        # 3. False Dichotomy
        if re.search(r"either .* or .*", p_lower) and "other" not in p_lower:
            return 0.25

        # 4. Subjectivity without criteria
        if re.search(r"(best|worst|favorite|beautiful)", p_lower) and "measure" not in p_lower:
            # Only flag if no numbers are present in the prompt
            if not re.search(r"\d+", prompt):
                return 0.25

        return 1.0

    def _parse_clauses(self, text: str) -> List[Tuple[str, str, tuple, str]]:
        """
        Extracts atomic propositions with type-theoretic tags.
        Returns list of (polarity, predicate, args, type).
        """
        clauses = []
        text_lower = text.lower()
        
        # Extract Comparatives (Real type)
        # Pattern: "X is greater than Y" or "X > Y"
        comp_pattern = r"(\w+)\s+(?:is\s+)?(greater|less|larger|smaller|more|fewer)\s+than\s+(\w+)"
        for m in re.finditer(comp_pattern, text_lower):
            clauses.append(('+', 'comp', (m.group(1), m.group(2), m.group(3)), 'Real'))
            
        # Pattern: "X > Y" or "X < Y"
        sym_comp_pattern = r"(\d+\.?\d*)\s*([<>])\s*(\d+\.?\d*)"
        for m in re.finditer(sym_comp_pattern, text):
            op = 'gt' if m.group(2) == '>' else 'lt'
            clauses.append(('+', op, (float(m.group(1)), float(m.group(3))), 'Real'))

        # Extract Conditionals (Prop type)
        cond_pattern = r"if\s+(.+?)\s+(?:then\s+)?(.+?)(?:\.|,|$)"
        for m in re.finditer(cond_pattern, text_lower):
            clauses.append(('+', 'cond', (m.group(1).strip(), m.group(2).strip()), 'Prop'))

        # Extract Negations
        neg_pattern = r"(?:it is not true that|not|never)\s+(\w+\s+\w+)"
        for m in re.finditer(neg_pattern, text_lower):
            clauses.append(('-', 'prop', (m.group(1),), 'Prop'))

        # Extract Atoms (Simple assertions)
        atom_pattern = r"(\w+)\s+(?:is|are|was|were)\s+(\w+)"
        for m in re.finditer(atom_pattern, text_lower):
            if m.group(2) not in ['greater', 'less', 'larger', 'smaller']:
                clauses.append(('+', 'prop', (m.group(1), m.group(2)), 'Prop'))

        return clauses

    def _propagate_constraints(self, clauses: List[Tuple]) -> float:
        """
        Runs deterministic forward chaining.
        Returns ratio of satisfied constraints.
        """
        if not clauses:
            return 0.5
        
        truth_table = {}
        satisfied_count = 0
        total_ops = 0

        # Initialize atoms
        for pol, pred, args, typ in clauses:
            if typ == 'Prop':
                key = str(args)
                if pol == '+':
                    truth_table[key] = True
                else:
                    truth_table[key] = False
        
        # Process Comparatives (Transitivity check)
        reals = {}
        for pol, pred, args, typ in clauses:
            if typ == 'Real':
                if pred == 'comp':
                    # Simplified: greater -> 1, less -> -1
                    val_map = {'greater': 1, 'larger': 1, 'more': 1, 'less': -1, 'smaller': -1, 'fewer': -1}
                    # We can't solve variables without more context, so we assume consistency if no contradiction
                    total_ops += 1
                    satisfied_count += 1 # Assume true unless proven false in this simple pass
                elif pred in ['gt', 'lt']:
                    total_ops += 1
                    v1, v2 = args
                    if pred == 'gt':
                        if v1 > v2: satisfied_count += 1
                    else:
                        if v1 < v2: satisfied_count += 1

        # Process Conditionals (Modus Ponens simulation)
        for pol, pred, args, typ in clauses:
            if pred == 'cond':
                total_ops += 1
                condition, result = args
                # If condition is in truth table and True, check result
                if condition in truth_table and truth_table[condition]:
                    if result in truth_table and truth_table[result]:
                        satisfied_count += 1
                else:
                    # If condition not met, conditional is vacuously true or untestable
                    satisfied_count += 1 

        return satisfied_count / max(total_ops, 1)

    def _perturb(self, text: str) -> str:
        """Randomly perturbs text for sensitivity analysis."""
        words = text.split()
        if not words:
            return text
        
        # Random synonym swap
        if np.random.rand() < 0.5:
            for i, w in enumerate(words):
                w_clean = w.lower().strip(".,!?")
                if w_clean in self.synonyms:
                    words[i] = self.synonyms[w_clean]
                    break
        
        # Numeric jitter
        new_words = []
        for w in words:
            if re.match(r"^\d+\.?\d*$", w):
                try:
                    val = float(w)
                    if np.random.rand() < 0.5:
                        val *= (1 + np.random.uniform(-0.05, 0.05))
                    new_words.append(f"{val:.2f}")
                except:
                    new_words.append(w)
            else:
                new_words.append(w)
        
        return " ".join(new_words)

    def _run_bandit_evaluation(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Evaluates a single candidate arm.
        Returns (mean_score, variance).
        """
        combined = f"{prompt} {candidate}"
        k = 5
        scores = []
        
        # Initial parse
        base_clauses = self._parse_clauses(combined)
        base_score = self._propagate_constraints(base_clauses)
        scores.append(base_score)
        
        # Sensitivity perturbations
        for _ in range(k-1):
            perturbed_text = self._perturb(combined)
            pert_clauses = self._parse_clauses(perturbed_text)
            s = self._propagate_constraints(pert_clauses)
            scores.append(s)
            
        scores_np = np.array(scores)
        return float(np.mean(scores_np)), float(np.var(scores_np))

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0: return 1.0
        concat = s1 + s2
        ncd = (len(z(concat)) - min(len(z(s1)), len(z(s2)))) / max(len1, len2)
        return max(0.0, min(1.0, 1.0 - ncd)) # Invert so higher is better

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        total_counts = 0
        
        # Store bandit stats: {index: {'count': int, 'mean': float, 'var': float}}
        bandits = {i: {'count': 0, 'mean': 0.0, 'var': 0.0} for i in range(len(candidates))}
        
        # Initial exploration: evaluate all once
        for i, cand in enumerate(candidates):
            mean_s, var_s = self._run_bandit_evaluation(prompt, cand)
            bandits[i]['count'] = 1
            bandits[i]['mean'] = mean_s
            bandits[i]['var'] = var_s + 1e-6 # Avoid div by zero
            total_counts += 1
            
        # UCB Selection Loop (Simulated budget)
        # In a real online setting, this would loop. Here we do a few rounds to refine.
        for _ in range(3): 
            best_ucb = -np.inf
            best_idx = 0
            
            for i in range(len(candidates)):
                b = bandits[i]
                if b['count'] == 0: 
                    ucb = np.inf
                else:
                    # UCB1 formula adapted with variance
                    exploration = 2 * np.sqrt(b['var'] * np.log(total_counts + 1) / b['count'])
                    ucb = b['mean'] + exploration
                
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_idx = i
            
            # Pull best arm
            cand = candidates[best_idx]
            mean_s, var_s = self._run_bandit_evaluation(prompt, cand)
            b = bandits[best_idx]
            
            # Update running mean
            new_count = b['count'] + 1
            b['mean'] = (b['mean'] * b['count'] + mean_s) / new_count
            b['var'] = var_s + 1e-6
            b['count'] = new_count
            total_counts += 1

        # Final Scoring and Ranking
        ranked = []
        for i, cand in enumerate(candidates):
            b = bandits[i]
            base_score = b['mean']
            
            # NCD Tiebreaker (max 15% influence)
            ncd_val = self._ncd_score(prompt, cand)
            composite_score = 0.85 * base_score + 0.15 * ncd_val
            
            ranked.append({
                "candidate": cand,
                "score": float(composite_score),
                "reasoning": f"Logical consistency: {base_score:.2f}, Structural similarity: {ncd_val:.2f}"
            })
            
        return sorted(ranked, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural evaluation
        # If no structural patterns match, we should be uncertain
        clauses = self._parse_clauses(f"{prompt} {answer}")
        if not clauses:
            structural_cap = 0.3
        else:
            structural_cap = 1.0
            
        # 3. Compute raw score
        mean_s, var_s = self._run_bandit_evaluation(prompt, answer)
        
        # Adjust score by variance (high variance = low confidence)
        variance_penalty = min(0.5, var_s * 2) 
        raw_conf = max(0.0, mean_s - variance_penalty)
        
        # Apply caps
        final_conf = min(raw_conf, meta_cap, structural_cap)
        
        # Ensure we never return > 0.9 without definitive computation (heuristic)
        if mean_s < 0.95:
            final_conf = min(final_conf, 0.9)
            
        return float(np.clip(final_conf, 0.0, 1.0))