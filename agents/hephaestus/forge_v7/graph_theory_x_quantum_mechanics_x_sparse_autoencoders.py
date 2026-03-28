import re
import math
import zlib
import numpy as np
from collections import namedtuple, defaultdict
from typing import List, Dict, Tuple, Set

Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])

class ReasoningTool:
    """
    Graph Theory x Quantum Mechanics x Sparse Autoencoders.

    Mechanism:
    1. Graph Construction: Builds a premise-relation graph from parsed features.
       Nodes = entities/concepts, edges = relations (causal, conditional, ordering).
    2. Shortest Path Scoring: Measures how tightly connected candidate concepts
       are to prompt concepts via shortest path in the relation graph.
    3. Superposition Evaluation: Scores each candidate simultaneously across
       multiple interpretive contexts (feature subsets), then collapses to the
       context that maximizes coherence (quantum measurement analogy).
    4. Sparse Feature Extraction: L1 projection keeps only the top-k features,
       filtering noise from the scoring pipeline.
    5. Epistemic Honesty: _meta_confidence caps ambiguous prompts.

    Score Decomposition: Graph (35%), Superposition (30%), Sparse (20%), NCD (15%).
    """

    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|without|neither|nor|none)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater|lower|higher|before|after|between)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided|assuming)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|due to|since|therefore|hence)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|units|km|cm|g|lb)?', re.I),
            'ordering': re.compile(r'\b(first|second|third|last|rank|order|next|previous)\b', re.I),
            'quantifier': re.compile(r'\b(all|every|some|any|most|few|none|each)\b', re.I),
            'modal': re.compile(r'\b(must|should|could|might|possibly|certainly|definitely|probably)\b', re.I),
            'relational': re.compile(r'\b(is a|has a|belongs to|part of|contains|related to)\b', re.I),
        }
        self.n_features = len(self.patterns)
        self.word_re = re.compile(r'\b[a-z]{3,}\b')
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased|failed)\b.*\b(have you|did you)\b', re.I),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
        ]
        self.subjectivity_re = re.compile(r'\b(best|worst|favorite|opinion|beautiful|ugly)\b', re.I)
        self.pronoun_re = re.compile(r'\b(he|she|him|her|they|them)\b', re.I)
        # Stop words for graph construction
        self._stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been', 'some', 'than',
            'its', 'over', 'such', 'that', 'this', 'with', 'will', 'each', 'from',
            'they', 'what', 'which', 'their', 'said', 'there', 'them', 'then',
            'would', 'about', 'could', 'other', 'into', 'more', 'very', 'when',
        }

    # ── Parsing ──────────────────────────────────────────────────────────

    def _extract_features(self, text: str) -> np.ndarray:
        vec = np.zeros(self.n_features, dtype=np.float64)
        for i, (name, pat) in enumerate(self.patterns.items()):
            vec[i] = len(pat.findall(text))
        return vec

    def _extract_statements(self, text: str) -> List[Statement]:
        stmts = []
        lt = text.lower()
        weight = 1.0
        if re.search(r'\b(certainly|definitely|must)\b', lt): weight = 1.0
        elif re.search(r'\b(possibly|maybe|might)\b', lt): weight = 0.5
        for name, pat in self.patterns.items():
            if name == 'numeric':
                for m in pat.finditer(text):
                    stmts.append(Statement('numeric', [float(m.group(1))], True, float(m.group(1)), weight))
            elif pat.search(lt):
                stmts.append(Statement(name, [], name != 'negation', None, weight))
        if not stmts:
            stmts.append(Statement('generic', [], True, None, weight))
        return stmts

    def _extract_content_words(self, text: str) -> List[str]:
        words = self.word_re.findall(text.lower())
        return [w for w in words if w not in self._stopwords]

    # ── Graph Construction ───────────────────────────────────────────────

    def _build_graph(self, text: str) -> Dict[str, Dict[str, float]]:
        """Build adjacency dict from co-occurring content words in windows."""
        words = self._extract_content_words(text)
        graph = defaultdict(lambda: defaultdict(float))
        window = 4
        for i, w in enumerate(words):
            for j in range(i + 1, min(i + window, len(words))):
                dist = 1.0 / (j - i)  # closer words = stronger edge
                graph[w][words[j]] += dist
                graph[words[j]][w] += dist
        return dict(graph)

    def _shortest_path_score(self, graph: Dict, source_words: Set[str],
                              target_words: Set[str]) -> float:
        """BFS shortest path from any source word to any target word."""
        if not source_words or not target_words or not graph:
            return 0.0
        # If direct overlap, return high score
        overlap = source_words & target_words
        if overlap:
            return 1.0

        best_dist = float('inf')
        for src in source_words:
            if src not in graph:
                continue
            # BFS
            visited = {src: 0}
            queue = [src]
            head = 0
            while head < len(queue):
                node = queue[head]
                head += 1
                if node in target_words:
                    best_dist = min(best_dist, visited[node])
                    break
                if visited[node] >= 6:  # max depth
                    continue
                for neighbor in graph.get(node, {}):
                    if neighbor not in visited:
                        visited[neighbor] = visited[node] + 1
                        queue.append(neighbor)

        if best_dist == float('inf'):
            return 0.0
        # Convert distance to score: 1/(1+d)
        return 1.0 / (1.0 + best_dist)

    # ── Superposition Evaluation ─────────────────────────────────────────

    def _superposition_score(self, prompt_features: np.ndarray,
                              cand_features: np.ndarray) -> float:
        """
        Evaluate candidate in multiple contexts simultaneously, collapse to best.
        Each context = a subset of feature channels (like a measurement basis).
        """
        n = self.n_features
        if n < 2:
            return 0.0

        # Generate contexts: sliding windows of feature subsets
        context_scores = []
        for start in range(n):
            size = max(2, n // 3)
            indices = [(start + i) % n for i in range(size)]
            p_sub = prompt_features[indices]
            c_sub = cand_features[indices]
            # Cosine similarity in this context
            dot = np.dot(p_sub, c_sub)
            norms = np.linalg.norm(p_sub) * np.linalg.norm(c_sub)
            sim = dot / norms if norms > 1e-12 else 0.0
            context_scores.append(sim)

        # Also add random projection contexts
        rng = np.random.RandomState(42)  # deterministic
        for _ in range(3):
            proj = rng.randn(n)
            p_proj = np.dot(prompt_features, proj)
            c_proj = np.dot(cand_features, proj)
            denom = abs(p_proj) + abs(c_proj)
            sim = 1.0 - abs(p_proj - c_proj) / denom if denom > 1e-12 else 0.0
            context_scores.append(max(0.0, sim))

        # Collapse: take the best context (measurement that maximizes coherence)
        if not context_scores:
            return 0.0
        # Weighted: best context gets 60%, mean of rest gets 40%
        sorted_scores = sorted(context_scores, reverse=True)
        best = sorted_scores[0]
        rest_mean = np.mean(sorted_scores[1:]) if len(sorted_scores) > 1 else 0.0
        return 0.6 * best + 0.4 * rest_mean

    # ── Sparse Feature Extraction ────────────────────────────────────────

    def _sparse_encode(self, vec: np.ndarray, k: int = 4) -> np.ndarray:
        """L1 sparse projection: keep top-k, zero the rest."""
        sparse = np.zeros_like(vec)
        if k >= len(vec):
            return vec.copy()
        topk = np.argsort(np.abs(vec))[-k:]
        sparse[topk] = vec[topk]
        return sparse

    def _sparse_similarity(self, pf: np.ndarray, cf: np.ndarray, k: int = 4) -> float:
        """Similarity of sparse-encoded feature vectors."""
        sp = self._sparse_encode(pf, k)
        sc = self._sparse_encode(cf, k)
        dot = np.dot(sp, sc)
        norms = np.linalg.norm(sp) * np.linalg.norm(sc)
        return dot / norms if norms > 1e-12 else 0.0

    # ── NCD ───────────────────────────────────────────────────────────────

    def _compute_ncd(self, s1: str, s2: str) -> float:
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except Exception:
            return 1.0

    # ── Meta Confidence (Tier B) ──────────────────────────────────────────

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        pl = prompt.lower()
        for pat in self.presupposition_triggers:
            if pat.search(pl):
                return 0.25
        if self.subjectivity_re.search(pl):
            return 0.30
        if 'who' in pl and self.pronoun_re.search(pl):
            if ' told ' in pl or ' said ' in pl:
                return 0.30
        stmts = self._extract_statements(prompt)
        if len(stmts) == 1 and stmts[0].pred == 'generic' and len(prompt.split()) < 10:
            return 0.20
        return 1.0

    # ── Core Scoring ──────────────────────────────────────────────────────

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        pf = self._extract_features(prompt)
        cf = self._extract_features(candidate)

        # 1. Graph-based shortest path
        combined_text = f"{prompt} {candidate}"
        graph = self._build_graph(combined_text)
        p_words = set(self._extract_content_words(prompt))
        c_words = set(self._extract_content_words(candidate))
        path_score = self._shortest_path_score(graph, p_words, c_words)

        # 2. Superposition evaluation
        sup_score = self._superposition_score(pf, cf)

        # 3. Sparse similarity
        sparse_sim = self._sparse_similarity(pf, cf, k=4)

        # 4. Numeric match bonus
        pnums = [float(x[0]) for x in self.patterns['numeric'].findall(prompt)]
        cnums = [float(x[0]) for x in self.patterns['numeric'].findall(candidate)]
        num_bonus = 0.0
        if pnums and cnums:
            for cn in cnums:
                for pn in pnums:
                    if pn != 0:
                        ratio = cn / pn
                        if abs(ratio - round(ratio)) < 0.01 and round(ratio) != 0:
                            num_bonus = max(num_bonus, 0.35)
                    if abs(cn - pn) < 1e-6:
                        num_bonus = max(num_bonus, 0.25)
            if num_bonus == 0:
                num_bonus = 0.1

        # 5. NCD tiebreaker
        ncd = self._compute_ncd(prompt, candidate)
        ncd_score = (1.0 - ncd) * 0.15

        # Assembly: Graph (35%), Superposition (30%), Sparse (20%), NCD (15%)
        final = (path_score * 0.35) + (sup_score * 0.30) + (sparse_sim * 0.20) + ncd_score
        final += num_bonus * 0.10  # small numeric channel

        reason = (f"graph={path_score:.3f} superposition={sup_score:.3f} "
                  f"sparse={sparse_sim:.3f} ncd={ncd:.3f} num={num_bonus:.2f}")
        return float(np.clip(final, 0, 1)), reason

    # ── Public API ────────────────────────────────────────────────────────

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        meta_cap = self._meta_confidence(prompt, "")
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            if meta_cap < 1.0:
                score = min(score, meta_cap)
                reason += f" [meta_cap={meta_cap:.2f}]"
            results.append({"candidate": cand, "score": score, "reasoning": reason})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.3:
            return meta_cap
        score, _ = self._score_candidate(prompt, answer)
        final = min(score, 0.95)
        final = min(final, meta_cap)
        return float(max(0.0, min(1.0, final)))
