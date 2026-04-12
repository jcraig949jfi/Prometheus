"""Feature-Discovery Bandit v2 — Structural + N-gram UCB.

Features include both linguistic n-grams AND structural indicators:
  - Word unigrams and bigrams
  - Character trigrams
  - Structural signals: negation presence, comparative direction,
    conditional structure, subject-object roles

UCB learns which features are informative. State persists across
evaluate() calls within the same instance.

Concepts: Information Theory x Sparse Autoencoders x Multi-Armed Bandits
"""

import re
import zlib
import numpy as np
from collections import Counter


class ReasoningTool:
    def __init__(self):
        self._counts = Counter()
        self._rewards = Counter()
        self._total_pulls = 0
        self._level = 6

    # -- NCD ---------------------------------------------------------------

    def _c(self, text: str) -> int:
        return len(zlib.compress(text.encode("utf-8"), self._level))

    def _ncd(self, x: str, y: str) -> float:
        cx, cy = self._c(x), self._c(y)
        cxy = self._c(x + " \n " + y)
        d = max(cx, cy)
        return (cxy - min(cx, cy)) / d if d > 0 else 1.0

    # -- Feature extraction ------------------------------------------------

    def _tokenize(self, text: str) -> list:
        return re.findall(r"[a-z0-9]+", text.lower())

    def _extract_features(self, text: str) -> set:
        """Multi-scale features: linguistic + structural."""
        text_lower = text.lower()
        words = self._tokenize(text)
        feats = set()

        # Word unigrams
        for w in words:
            feats.add(("w1", w))

        # Word bigrams
        for i in range(len(words) - 1):
            feats.add(("w2", words[i], words[i + 1]))

        # Character trigrams
        for i in range(len(text_lower) - 2):
            chunk = text_lower[i:i + 3]
            if chunk.strip():
                feats.add(("c3", chunk))

        # Skip-grams (order-invariant)
        for i in range(len(words)):
            for j in range(i + 1, min(i + 4, len(words))):
                pair = tuple(sorted([words[i], words[j]]))
                feats.add(("skip", pair[0], pair[1]))

        # -- Structural features --
        # Negation
        if re.search(r"\b(?:not|never|no|cannot|can't|won't|doesn't|don't|isn't|aren't)\b",
                      text_lower):
            feats.add(("struct", "has_negation"))
        else:
            feats.add(("struct", "no_negation"))

        # Affirmation
        if text_lower.strip().startswith("yes") or "true" in text_lower:
            feats.add(("struct", "affirms"))
        if text_lower.strip().startswith("no") or "false" in text_lower:
            feats.add(("struct", "denies"))

        # Comparative direction
        for m in re.finditer(
            r"(\S+)\s+(?:is\s+)?(?:larger|greater|bigger|taller|heavier|more)\s+than\s+(\S+)",
            text_lower
        ):
            feats.add(("comp", "greater", m.group(1).strip(".,;:?"), m.group(2).strip(".,;:?")))
        for m in re.finditer(
            r"(\S+)\s+(?:is\s+)?(?:less|smaller|shorter|lighter)\s+than\s+(\S+)",
            text_lower
        ):
            feats.add(("comp", "lesser", m.group(1).strip(".,;:?"), m.group(2).strip(".,;:?")))

        # Conditional
        if re.search(r"\bif\b", text_lower):
            feats.add(("struct", "has_conditional"))

        # Question type
        if re.search(r"\bwho\b", text_lower):
            feats.add(("struct", "asks_who"))
        if re.search(r"\bwhich\b", text_lower):
            feats.add(("struct", "asks_which"))
        if re.search(r"\bhow many\b", text_lower):
            feats.add(("struct", "asks_howmany"))

        # Numbers present
        nums = re.findall(r"\b\d+\.?\d*\b", text)
        for n in nums:
            feats.add(("num", n))

        # Subject-object
        for m in re.finditer(r"[Tt]he\s+(\w+)\s+(\w+(?:ed|s))\s+the\s+(\w+)", text):
            feats.add(("svo", "agent", m.group(1).lower()))
            feats.add(("svo", "patient", m.group(3).lower()))

        return feats

    # -- UCB ---------------------------------------------------------------

    def _ucb(self, feat) -> float:
        n = self._counts[feat]
        if n == 0:
            return 2.0
        mu = self._rewards[feat] / n
        exploration = np.sqrt(2.0 * np.log(self._total_pulls + 2) / n)
        return mu + exploration

    def _compute_structural_reward(self, prompt: str, candidate: str) -> float:
        """Structural consistency reward for bandit updates."""
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)

        reward = 0.5  # neutral baseline

        # Reward structural consistency
        p_has_neg = ("struct", "has_negation") in p_feats
        c_affirms = ("struct", "affirms") in c_feats
        c_denies = ("struct", "denies") in c_feats

        if p_has_neg and c_denies:
            reward += 0.3
        if p_has_neg and c_affirms:
            reward -= 0.3

        # Reward matching SVO roles
        p_agents = {f for f in p_feats if len(f) == 3 and f[0] == "svo" and f[1] == "agent"}
        p_patients = {f for f in p_feats if len(f) == 3 and f[0] == "svo" and f[1] == "patient"}
        if p_patients and any(f in c_feats for f in p_patients):
            reward += 0.2

        return float(np.clip(reward, 0.0, 1.0))

    def _update_bandit(self, prompt: str, prompt_feats: set,
                       candidates: list, cand_feats_list: list):
        """Update with structural + NCD reward."""
        for i, cand in enumerate(candidates):
            ncd_reward = 1.0 / (1.0 + self._ncd(prompt, cand))
            struct_reward = self._compute_structural_reward(prompt, cand)
            reward = 0.5 * struct_reward + 0.5 * ncd_reward

            shared = prompt_feats & cand_feats_list[i]
            for feat in shared:
                self._counts[feat] += 1
                self._rewards[feat] += reward
                self._total_pulls += 1

    # -- Public interface --------------------------------------------------

    def evaluate(self, prompt: str, candidates: list) -> list:
        if not candidates:
            return []

        prompt_feats = self._extract_features(prompt)
        cand_feats_list = [self._extract_features(c) for c in candidates]

        scores = []
        for i, cand in enumerate(candidates):
            shared = prompt_feats & cand_feats_list[i]
            if not shared:
                scores.append(0.0)
                continue

            ucb_total = sum(self._ucb(f) for f in shared)
            norm = len(cand_feats_list[i]) + 1
            bandit_score = ucb_total / norm

            # NCD component
            ncd_val = self._ncd(prompt, cand)
            ncd_component = 1.0 / (1.0 + ncd_val)

            # Structural consistency
            struct_reward = self._compute_structural_reward(prompt, cand)

            # Blend: 40% bandit, 30% structural, 30% NCD
            final = 0.4 * bandit_score + 0.3 * struct_reward + 0.3 * ncd_component
            scores.append(final)

        # Update after scoring
        self._update_bandit(prompt, prompt_feats, candidates, cand_feats_list)

        results = []
        for i, cand in enumerate(candidates):
            shared_count = len(prompt_feats & cand_feats_list[i])
            results.append({
                "candidate": cand,
                "score": float(scores[i]),
                "reasoning": (
                    f"shared={shared_count}, pulls={self._total_pulls}"
                ),
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        struct = self._compute_structural_reward(prompt, answer)
        # Structural signal dominates when present
        if struct > 0.7:
            return float(np.clip(0.8 + (struct - 0.5) * 0.4, 0.0, 1.0))
        elif struct < 0.3:
            return float(np.clip(struct * 0.3, 0.0, 0.15))

        # Mixed signal — blend bandit + structural + NCD
        prompt_feats = self._extract_features(prompt)
        answer_feats = self._extract_features(answer)
        shared = prompt_feats & answer_feats

        if not shared:
            return float(struct * 0.5)

        ucb_total = sum(self._ucb(f) for f in shared)
        norm = len(answer_feats) + 1
        bandit_conf = min(ucb_total / norm, 1.0)

        ncd_val = self._ncd(prompt, answer)
        ncd_conf = (1.0 - float(np.clip(ncd_val, 0.0, 1.0))) ** 2

        conf = 0.4 * struct + 0.35 * bandit_conf + 0.25 * ncd_conf
        return float(np.clip(conf, 0.0, 1.0))
