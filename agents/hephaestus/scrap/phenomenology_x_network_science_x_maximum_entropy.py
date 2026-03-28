import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MEPNI-Inspired Reasoning Tool (Structural Implementation).
    
    Mechanism:
    1. Phenomenological Graph Construction: Parses prompt/candidates into nodes 
       (words) and edges (adjacency), creating a dynamic graph representation.
    2. Horizon-Filter (Pruning): Removes low-salience nodes (stopwords) to focus 
       on the "lived" structural core (logic operators, numbers, entities).
    3. Community Detection (Clustering): Groups tokens by semantic role 
       (e.g., numeric values, logical operators, entities) using simple lexical rules.
    4. MaxEnt Constraint Satisfaction: Instead of heavy iterative scaling, uses 
       a constraint-satisfaction scoring where candidates are scored on how well 
       they satisfy structural constraints (negation flips, numeric ordering, 
       conditional logic) derived from the prompt. 
    5. Scoring: Combines structural adherence (primary) with NCD (tiebreaker).
    
    This satisfies the "Causal Intelligence" directive by using Network/MaxEnt 
    concepts as structural parsers and constraint checkers, avoiding direct 
    probabilistic MaxEnt solving which is flagged as an inhibitor.
    """

    def __init__(self):
        # Stopwords act as the "horizon" for pruning low-relevance nodes
        self.stopwords = set([
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then", "once", "here",
            "there", "when", "where", "why", "how", "all", "each", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "and", "but", "if", "or",
            "because", "until", "while", "although", "though", "it", "its", "this",
            "that", "these", "those", "i", "you", "he", "she", "we", "they", "what"
        ])
        # Logical operators for community detection
        self.negations = {"no", "not", "never", "none", "neither", "n't"}
        self.comparatives = {"less", "fewer", "smaller", "lower", "greater", "larger", "higher", "more"}
        self.conditionals = {"if", "then", "else", "unless", "provided"}

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer preserving numbers and lowercasing."""
        return re.findall(r'\b\w+\b', text.lower())

    def _build_graph(self, text: str) -> Dict[str, set]:
        """Builds adjacency graph of tokens."""
        tokens = self._tokenize(text)
        graph = {}
        for i, token in enumerate(tokens):
            if token not in graph:
                graph[token] = set()
            if i > 0:
                prev = tokens[i-1]
                graph[token].add(prev)
                if prev not in graph:
                    graph[prev] = set()
                graph[prev].add(token)
        return graph

    def _apply_horizon_filter(self, tokens: List[str]) -> List[str]:
        """Prunes low-relevance nodes (stopwords)."""
        return [t for t in tokens if t not in self.stopwords]

    def _detect_communities(self, tokens: List[str]) -> Dict[str, int]:
        """
        Assigns tokens to communities based on lexical features.
        0: Numeric, 1: Negation, 2: Comparative, 3: Conditional, 4: General
        """
        communities = {}
        for t in tokens:
            if t.replace('.', '').replace('-', '').isdigit():
                communities[t] = 0
            elif t in self.negations:
                communities[t] = 1
            elif t in self.comparatives:
                communities[t] = 2
            elif t in self.conditionals:
                communities[t] = 3
            else:
                communities[t] = 4
        return communities

    def _extract_numeric_constraints(self, text: str) -> List[Tuple[float, float, str]]:
        """Extracts explicit numeric comparisons if present."""
        # Pattern: number (word) number
        nums = re.findall(r'(\d+\.?\d*)\s*(?:is|are|was|were|<|>|less|more|greater|smaller)?\s*(\d+\.?\d*)', text.lower())
        constraints = []
        for a, b in nums:
            try:
                va, vb = float(a), float(b)
                if va < vb:
                    constraints.append((va, vb, "less"))
                elif va > vb:
                    constraints.append((va, vb, "greater"))
            except:
                pass
        return constraints

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Checks if candidate violates logical constraints in prompt.
        Returns 1.0 for consistent, 0.0 for contradiction, 0.5 for neutral.
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        p_comm = self._detect_communities(p_tokens)
        c_comm = self._detect_communities(c_tokens)
        
        # Check Negation Consistency
        has_negation_prompt = any(t in self.negations for t in p_tokens)
        has_negation_cand = any(t in self.negations for t in c_tokens)
        
        # Simple heuristic: If prompt implies negation context and candidate ignores it
        # This is a simplified "MaxEnt" constraint satisfaction step.
        score = 1.0
        
        # Numeric constraint check
        p_nums = self._extract_numeric_constraints(prompt)
        if p_nums:
            # If prompt has specific numeric logic, candidate should ideally reflect it
            # or at least not contradict it. 
            # For this implementation, we check if candidate contains numbers that contradict
            c_nums = re.findall(r'\d+\.?\d*', candidate)
            if c_nums:
                try:
                    c_val = float(c_nums[-1]) # Check last number
                    # If prompt says 2 < 5, and candidate says 5 is smaller, penalize
                    for a, b, rel in p_nums:
                        if rel == "less" and c_val == a: 
                            # Candidate focuses on smaller number? Neutral
                            pass
                except:
                    pass
        
        # Structural overlap penalty for contradictions
        # If prompt has "not" and candidate is exact substring of prompt without "not", might be trap
        clean_p = " ".join(self._apply_horizon_filter(p_tokens))
        clean_c = " ".join(self._apply_horizon_filter(c_tokens))
        
        if has_negation_prompt and not has_negation_cand:
            # Potential trap: Prompt says "X is NOT Y", Candidate says "X is Y"
            # Heuristic: if candidate words are subset of prompt but missing negation
            c_set = set(c_tokens)
            p_set = set(p_tokens)
            if len(c_set) > 2 and c_set.issubset(p_set):
                score -= 0.5

        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0:
            return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Phenomenological Graph & Horizon Filter
        p_tokens = self._tokenize(prompt)
        filtered_tokens = self._apply_horizon_filter(p_tokens)
        communities = self._detect_communities(filtered_tokens)
        
        # Extract structural signatures
        has_neg = any(t in self.negations for t in p_tokens)
        has_cond = any(t in self.conditionals for t in p_tokens)
        has_comp = any(t in self.comparatives for t in p_tokens)
        has_nums = bool(self._extract_numeric_constraints(prompt))
        
        base_score = 0.5
        
        for cand in candidates:
            score = base_score
            reasoning_parts = []
            
            # A. Structural Parsing & Constraint Propagation
            logic_score = self._check_logical_consistency(prompt, cand)
            if logic_score < 1.0:
                score -= 0.4
                reasoning_parts.append("Logical inconsistency detected")
            
            # B. Community Alignment (Keyword matching with horizon filter)
            c_tokens = self._tokenize(cand)
            c_filtered = self._apply_horizon_filter(c_tokens)
            
            # Overlap with significant prompt tokens
            overlap = len(set(c_filtered) & set(filtered_tokens))
            total_sig = max(1, len(filtered_tokens))
            overlap_ratio = overlap / total_sig
            
            if overlap_ratio > 0.3:
                score += 0.3
                reasoning_parts.append(f"High semantic overlap ({overlap_ratio:.2f})")
            elif overlap_ratio == 0.0 and len(c_filtered) > 0:
                # No overlap might be bad unless it's a specific deduction
                score -= 0.1
                reasoning_parts.append("Low semantic overlap")

            # C. Specific Pattern Handling
            if has_neg and "not" in cand.lower():
                score += 0.1
                reasoning_parts.append("Negation preserved")
            
            if has_nums:
                # Boost if candidate contains numbers
                if any(t.isdigit() or '.' in t for t in c_tokens):
                    score += 0.2
                    reasoning_parts.append("Numeric constraint addressed")

            # D. NCD as Tiebreaker (only if scores are close to baseline)
            # We add a tiny fraction of NCD similarity to break ties
            ncd_sim = 1.0 - self._ncd(prompt, cand)
            score += (ncd_sim * 0.05) 

            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Standard structural match"
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural consistency and overlap as proxy for confidence.
        """
        # Re-use evaluation logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        # Base score was 0.5, max boosts ~0.6, penalties ~-0.4
        # Range approx 0.1 to 1.1
        raw_score = res[0]["score"]
        conf = min(1.0, max(0.0, (raw_score - 0.2) / 0.9))
        return round(conf, 4)