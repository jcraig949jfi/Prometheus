import re
import math
import zlib
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Set

Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])

class ReasoningTool:
    """
    Information Theory x Sparse Autoencoders x Multi-Armed Bandits.

    Mechanism:
    1. Feature Extraction: Parses structural features (negation, causal, numeric,
       conditional, comparative, ordering, quantifier, modal) from text.
    2. Shannon Entropy Scoring: Measures candidate informativeness via entropy
       of activated feature distribution.
    3. L1-Sparse Feature Selection: Keeps only top-k discriminative features
       per candidate, zeroing the rest (sparse autoencoder analogy).
    4. UCB1 Bandit: Learns which features best discriminate across candidates;
       features that consistently separate winners get higher weight.
    5. Epistemic Honesty: _meta_confidence caps score on ambiguous prompts.

    Score Decomposition: Structural (55%), Bandit (30%), NCD (15%).
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
        }
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased|failed)\b.*\b(have you|did you)\b', re.I),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
        ]
        self.subjectivity_re = re.compile(r'\b(best|worst|favorite|opinion|beautiful|ugly)\b', re.I)
        self.pronoun_re = re.compile(r'\b(he|she|him|her|they|them)\b', re.I)
        # Bandit state: counts and rewards per feature type
        self._bandit_counts = {k: 1.0 for k in self.patterns}
        self._bandit_rewards = {k: 0.5 for k in self.patterns}
        self._total_pulls = len(self.patterns)

    # ── Parsing ──────────────────────────────────────────────────────────

    def _extract_features(self, text: str) -> np.ndarray:
        """Returns a feature vector of match counts for each pattern."""
        vec = np.zeros(len(self.patterns), dtype=np.float64)
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

    # ── Shannon Entropy ──────────────────────────────────────────────────

    def _shannon_entropy(self, vec: np.ndarray) -> float:
        total = vec.sum()
        if total == 0:
            return 0.0
        p = vec / total
        p = p[p > 0]
        return float(-np.sum(p * np.log2(p + 1e-12)))

    # ── L1 Sparse Selection ─────────────────────────────────────────────

    def _sparse_select(self, vec: np.ndarray, k: int = 4) -> np.ndarray:
        """Keep only top-k features by magnitude, zero the rest."""
        sparse = np.zeros_like(vec)
        if k >= len(vec):
            return vec.copy()
        topk = np.argsort(np.abs(vec))[-k:]
        sparse[topk] = vec[topk]
        return sparse

    # ── UCB1 Bandit ──────────────────────────────────────────────────────

    def _ucb1_weights(self) -> np.ndarray:
        """Compute UCB1 score for each feature arm."""
        weights = np.zeros(len(self.patterns))
        keys = list(self.patterns.keys())
        for i, k in enumerate(keys):
            mean_reward = self._bandit_rewards[k] / self._bandit_counts[k]
            exploration = math.sqrt(2.0 * math.log(self._total_pulls + 1) / self._bandit_counts[k])
            weights[i] = mean_reward + exploration
        # Normalize to [0, 1]
        wmax = weights.max()
        if wmax > 0:
            weights /= wmax
        return weights

    def _update_bandit(self, winning_features: np.ndarray, losing_features: np.ndarray):
        """Reward features present in winner, penalize those only in loser."""
        keys = list(self.patterns.keys())
        for i, k in enumerate(keys):
            self._total_pulls += 1
            self._bandit_counts[k] += 1
            if winning_features[i] > 0 and losing_features[i] == 0:
                self._bandit_rewards[k] += 1.0  # discriminative
            elif winning_features[i] > 0:
                self._bandit_rewards[k] += 0.3  # present but not discriminative
            # else: no reward

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

        # Combined feature vector
        combined = pf + cf
        sparse_combined = self._sparse_select(combined, k=4)

        # Entropy of sparse features: higher = more informative candidate
        ent = self._shannon_entropy(sparse_combined)
        max_ent = math.log2(len(self.patterns)) if len(self.patterns) > 0 else 1.0
        ent_score = ent / max_ent if max_ent > 0 else 0.0

        # Bandit-weighted overlap: how well do discriminative features align?
        ucb_w = self._ucb1_weights()
        overlap = np.sum(sparse_combined * ucb_w)
        max_overlap = np.sum(np.sort(ucb_w)[-4:] * np.sort(sparse_combined)[-4:])
        bandit_score = overlap / max_overlap if max_overlap > 0 else 0.0

        # Numeric match bonus
        pnums = [float(x[0]) for x in self.patterns['numeric'].findall(prompt)]
        cnums = [float(x[0]) for x in self.patterns['numeric'].findall(candidate)]
        num_bonus = 0.0
        if pnums and cnums:
            # Check if candidate number could be derived from prompt numbers
            for cn in cnums:
                for pn in pnums:
                    if pn != 0 and abs(cn - pn) < 1e-6:
                        num_bonus = 0.3
                    elif pn != 0:
                        ratio = cn / pn if pn != 0 else 0
                        if abs(ratio - round(ratio)) < 0.01 and round(ratio) != 0:
                            num_bonus = max(num_bonus, 0.4)
            if num_bonus == 0 and cnums:
                num_bonus = 0.15

        # NCD tiebreaker
        ncd = self._compute_ncd(prompt, candidate)
        ncd_score = (1.0 - ncd) * 0.15

        # Final assembly: Structural 55%, Bandit 30%, NCD 15%
        structural = (ent_score * 0.5 + num_bonus) * 0.55
        bandit = bandit_score * 0.30
        final = structural + bandit + ncd_score

        reason = (f"entropy={ent:.3f} sparse_feats={int(np.count_nonzero(sparse_combined))} "
                  f"bandit={bandit_score:.3f} ncd={ncd:.3f}")
        return float(np.clip(final, 0, 1)), reason

    # ── Public API ────────────────────────────────────────────────────────

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        meta_cap = self._meta_confidence(prompt, "")
        results = []
        features_per_cand = []

        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            if meta_cap < 1.0:
                score = min(score, meta_cap)
                reason += f" [meta_cap={meta_cap:.2f}]"
            results.append({"candidate": cand, "score": score, "reasoning": reason})
            features_per_cand.append(self._extract_features(f"{prompt} {cand}"))

        results.sort(key=lambda x: x['score'], reverse=True)

        # Update bandit with winner vs others
        if len(results) > 1 and len(features_per_cand) > 1:
            winner_idx = candidates.index(results[0]['candidate'])
            loser_idx = candidates.index(results[-1]['candidate'])
            self._update_bandit(features_per_cand[winner_idx], features_per_cand[loser_idx])

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.3:
            return meta_cap
        score, _ = self._score_candidate(prompt, answer)
        final = min(score, 0.95)
        final = min(final, meta_cap)
        return float(max(0.0, min(1.0, final)))
