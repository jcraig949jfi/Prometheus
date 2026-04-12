import re
import math
import zlib
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple

Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])

class ReasoningTool:
    """
    Information Theory x Morphogenesis x Free Energy Principle.

    Mechanism:
    1. Feature Extraction: Structural parsing into 9 feature channels.
    2. Mutual Information: Measures shared information between prompt and
       candidate feature distributions (how much knowing one tells about other).
    3. Morphogenetic Growth: Active features "activate" neighboring features
       via a diffusion kernel, modeling how premises grow into conclusions.
    4. Variational Free Energy: F = Complexity - Accuracy. Complexity penalizes
       candidates with too many unexplained features; Accuracy rewards feature
       overlap with prompt.
    5. Epistemic Honesty: _meta_confidence caps ambiguous/subjective prompts.

    Score Decomposition: Free Energy (50%), Mutual Info (20%), Growth (15%), NCD (15%).
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
        # Morphogenetic diffusion kernel (adjacency between feature channels)
        # Nearby conceptual channels diffuse into each other
        self._build_diffusion_kernel()
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased|failed)\b.*\b(have you|did you)\b', re.I),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
        ]
        self.subjectivity_re = re.compile(r'\b(best|worst|favorite|opinion|beautiful|ugly)\b', re.I)
        self.pronoun_re = re.compile(r'\b(he|she|him|her|they|them)\b', re.I)

    def _build_diffusion_kernel(self):
        """Build a diffusion kernel: features that co-occur reinforce neighbors."""
        n = self.n_features
        # Start with identity + nearest-neighbor coupling
        K = np.eye(n, dtype=np.float64) * 0.6
        for i in range(n):
            if i > 0:
                K[i, i - 1] = 0.2
            if i < n - 1:
                K[i, i + 1] = 0.2
        # Semantic links: causal(3) <-> conditional(2), numeric(4) <-> comparative(1)
        K[3, 2] = 0.3; K[2, 3] = 0.3
        K[4, 1] = 0.25; K[1, 4] = 0.25
        # Normalize rows
        row_sums = K.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        self.diffusion_kernel = K / row_sums

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

    # ── Mutual Information ───────────────────────────────────────────────

    def _mutual_information(self, pf: np.ndarray, cf: np.ndarray) -> float:
        """Discrete MI between prompt and candidate feature distributions."""
        # Joint distribution from co-occurrence
        joint = np.outer(pf, cf)
        total = joint.sum()
        if total == 0:
            return 0.0
        joint_p = joint / total
        marginal_p = pf / (pf.sum() + 1e-12)
        marginal_c = cf / (cf.sum() + 1e-12)

        mi = 0.0
        for i in range(len(pf)):
            for j in range(len(cf)):
                if joint_p[i, j] > 1e-12:
                    denom = marginal_p[i] * marginal_c[j]
                    if denom > 1e-12:
                        mi += joint_p[i, j] * math.log2(joint_p[i, j] / denom)
        return max(0.0, mi)

    # ── Morphogenetic Growth ─────────────────────────────────────────────

    def _morphogenetic_grow(self, features: np.ndarray, steps: int = 3) -> np.ndarray:
        """Diffuse active features through the kernel, simulating pattern growth."""
        state = features.copy()
        for _ in range(steps):
            state = self.diffusion_kernel @ state
            # Threshold: only keep activations above a minimum
            state = np.where(state > 0.05, state, 0.0)
        return state

    # ── Variational Free Energy ──────────────────────────────────────────

    def _free_energy(self, prompt_features: np.ndarray, cand_features: np.ndarray) -> float:
        """
        F = Complexity - Accuracy.
        Complexity: KL divergence of candidate from uniform (penalize overspecialized).
        Accuracy: Negative reconstruction error (how well candidate explains prompt).
        Lower free energy = better candidate.
        """
        # Accuracy: negative L2 distance between grown candidate and prompt
        grown_cand = self._morphogenetic_grow(cand_features)
        accuracy = -np.sqrt(np.sum((prompt_features - grown_cand) ** 2) + 1e-12)

        # Complexity: KL(candidate || uniform)
        cf_norm = cand_features / (cand_features.sum() + 1e-12)
        uniform = np.ones(self.n_features) / self.n_features
        kl = 0.0
        for i in range(self.n_features):
            if cf_norm[i] > 1e-12:
                kl += cf_norm[i] * math.log2(cf_norm[i] / uniform[i])

        complexity = max(0.0, kl)
        return complexity + accuracy  # F = complexity - (-accuracy)

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

        # 1. Mutual Information (normalized)
        mi = self._mutual_information(pf, cf)
        max_mi = math.log2(self.n_features) if self.n_features > 1 else 1.0
        mi_score = min(mi / max_mi, 1.0)

        # 2. Morphogenetic growth similarity
        grown_p = self._morphogenetic_grow(pf)
        grown_c = self._morphogenetic_grow(cf)
        # Cosine similarity of grown states
        dot = np.dot(grown_p, grown_c)
        norms = (np.linalg.norm(grown_p) * np.linalg.norm(grown_c))
        growth_sim = dot / norms if norms > 1e-12 else 0.0

        # 3. Free energy (lower is better, convert to score)
        fe = self._free_energy(pf, cf)
        # Sigmoid transform: map free energy to [0, 1], lower FE -> higher score
        fe_score = 1.0 / (1.0 + math.exp(fe))

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
                            num_bonus = max(num_bonus, 0.3)
                    if abs(cn - pn) < 1e-6:
                        num_bonus = max(num_bonus, 0.2)
            if num_bonus == 0:
                num_bonus = 0.1

        # 5. NCD tiebreaker
        ncd = self._compute_ncd(prompt, candidate)
        ncd_score = (1.0 - ncd) * 0.15

        # Assembly: FE (50%), MI (20%), Growth (15%), NCD (15%)
        final = (fe_score * 0.50) + (mi_score * 0.20) + (growth_sim * 0.15) + ncd_score
        final += num_bonus * 0.15  # small numeric bonus channel

        reason = (f"free_energy={fe:.3f} mi={mi:.3f} growth_sim={growth_sim:.3f} "
                  f"ncd={ncd:.3f} num_bonus={num_bonus:.2f}")
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
