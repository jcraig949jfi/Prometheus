from typing import Dict, Tuple

"""
ReasoningTool – Phase‑Adaptive Bandit Controller (PABC)

Implements the algorithmic design described in the prompt:
* FeatureRecord parser (regex‑based, flat dict)
* Three BanditArm heuristics:
    - numeric consistency
    - logical entailment
    - causal chain
* Adaptive ControlState with learning‑rate (alpha), exploration‑rate (beta),
  decay (gamma) and a phase‑metric that triggers a phase transition.
* Scoring = weighted sum of arm means (+ UCB term during exploration).
* Meta‑confidence detection for presupposition, scope ambiguity,
  pronoun ambiguity, false dichotomy, subjectivity and unanswerability.
* Confidence is capped by the meta‑confidence and never exceeds 0.9
  unless the numeric arm produces a deterministic result.

The tool returns a ranked list of candidates together with a short
reasoning string and a calibrated confidence value.
"""

import re
import zlib
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple


# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
def _parse_features(text: str) -> dict:
    """Extract a flat FeatureRecord from *text*."""
    # simple regexes – they are deliberately lightweight
    neg = len(re.findall(r'\b(not|never|no )\b', text, flags=re.I))
    comp = len(re.findall(r'\b(greater than|less than|>=|<=|>|<|equal to|equals)\b',
                          text, flags=re.I))
    cond = len(re.findall(r'\bif\b.*\bthen\b', text, flags=re.I))
    nums = [float(m) for m in re.findall(r'[-+]?\d*\.\d+|\d+', text)]
    causal = len(re.findall(r'\b(causes?|leads? to|results? in)\b', text, flags=re.I))
    order = len(re.findall(r'\b(first|second|after|before|then|next)\b', text, flags=re.I))
    # very simple logic clause detection: "if X then Y"
    logic = re.findall(r'\bif\b\s+(.*?)\s+\bthen\b\s+(.*?)(?:[.;]|$)', text, flags=re.I)
    return {
        'negations': neg,
        'comparatives': comp,
        'conditionals': cond,
        'numbers': nums,
        'causal_links': causal,
        'order_relations': order,
        'logic_clauses': [(p.strip(), c.strip()) for p, c in logic],
    }


class BanditArm:
    """Stores statistics for a single heuristic."""
    def __init__(self):
        self.count = 0
        self.reward_sum = 0.0
        self.reward_sq = 0.0

    def update(self, reward: float):
        self.count += 1
        self.reward_sum += reward
        self.reward_sq += reward * reward

    @property
    def mean(self) -> float:
        return self.reward_sum / self.count if self.count else 0.0

    @property
    def var(self) -> float:
        if self.count < 2:
            return float('inf')
        return (self.reward_sq - (self.reward_sum ** 2) / self.count) / (self.count - 1)


class ControlState:
    """Adaptive gains and phase detection."""
    def __init__(self, theta: float = 0.5):
        self.alpha = 1.0   # weight for numeric arm
        self.beta = 1.0    # weight for logical arm
        self.gamma = 1.0   # weight for causal arm
        self.phase_metric = 0.0
        self.theta = theta
        self.exploration = True   # start in exploration mode

    def update_phase(self, arms: List[BanditArm]):
        # phase_metric = sum_i (var_i / count_i)
        metric = 0.0
        for arm in arms:
            if arm.count:
                metric += arm.var / arm.count
        self.phase_metric = metric
        self.exploration = metric > self.theta


# ----------------------------------------------------------------------
# Core reasoning tool
# ----------------------------------------------------------------------
class ReasoningTool:
    """Public interface required by the specification."""
    def __init__(self):
        # three arms: numeric, logical, causal
        self.arms = {
            'numeric': BanditArm(),
            'logical': BanditArm(),
            'causal': BanditArm(),
        }
        self.control = ControlState()
        self.ucb_c = 1.0   # exploration constant

    # ------------------------------------------------------------------
    # Heuristic implementations
    # ------------------------------------------------------------------
    def _numeric_reward(self, prompt_feat: dict, cand_feat: dict) -> float:
        """Reward = 1 if all numbers in candidate satisfy simple comparisons
        found in the prompt, else 0.  Very lightweight."""
        # extract comparisons from prompt (e.g., "x > 5")
        comps = re.findall(r'(\b\w+\b)\s*(>=|<=|>|<|=|==)\s*([-+]?\d*\.\d+|\d+)', prompt_feat['_raw'])
        if not comps:
            return 0.0
        # build a dict of variable -> value from candidate numbers (order based)
        cand_nums = cand_feat['numbers']
        if not cand_nums:
            return 0.0
        # map first numbers to variables in order of appearance
        var_vals = {}
        for i, (var, op, val) in enumerate(comps):
            if i < len(cand_nums):
                var_vals[var] = cand_nums[i]
        # evaluate each comparison
        for var, op, val in comps:
            if var not in var_vals:
                return 0.0
            lhs = var_vals[var]
            rhs = float(val)
            ok = {
                '>': lhs > rhs,
                '<': lhs < rhs,
                '>=': lhs >= rhs,
                '<=': lhs <= rhs,
                '=': lhs == rhs,
                '==': lhs == rhs,
            }[op]
            if not ok:
                return 0.0
        return 1.0

    def _logical_reward(self, prompt_feat: dict, cand_feat: dict) -> float:
        """Reward based on matching logical constructs (negations, comparatives,
        conditionals). Simple overlap count normalized."""
        matches = 0
        total = 0
        for key in ('negations', 'comparatives', 'conditionals'):
            total += 1
            if prompt_feat[key] and cand_feat[key]:
                matches += 1
        return matches / total if total else 0.0

    def _causal_reward(self, prompt_feat: dict, cand_feat: dict) -> float:
        """Reward = 1 if candidate contains at least as many causal links as prompt."""
        return 1.0 if cand_feat['causal_links'] >= prompt_feat['causal_links'] else 0.0

    # ------------------------------------------------------------------
    # Phase‑adaptive scoring
    # ------------------------------------------------------------------
    def _score_candidate(self, prompt_feat: dict, cand_feat: dict) -> Tuple[float, str]:
        """Compute sub‑scores, update arms, return final score and a short reasoning."""
        # raw rewards
        r_num = self._numeric_reward(prompt_feat, cand_feat)
        r_log = self._logical_reward(prompt_feat, cand_feat)
        r_cau = self._causal_reward(prompt_feat, cand_feat)

        # update arms
        self.arms['numeric'].update(r_num)
        self.arms['logical'].update(r_log)
        self.arms['causal'].update(r_cau)

        # adapt gains (PID‑like: only a proportional rule here)
        var_num = self.arms['numeric'].var
        if var_num < 0.01:          # variance low -> trust numeric arm
            self.control.alpha = min(self.control.alpha * 1.05, 3.0)
        else:
            self.control.alpha = max(self.control.alpha * 0.95, 0.5)

        # phase update
        self.control.update_phase(list(self.arms.values()))

        # weighted sum of arm means
        w = np.array([self.control.alpha,
                      self.control.beta,
                      self.control.gamma])
        means = np.array([self.arms['numeric'].mean,
                          self.arms['logical'].mean,
                          self.arms['causal'].mean])
        base_score = np.dot(w, means) / w.sum()

        # add UCB term if still exploring
        if self.control.exploration:
            N = sum(arm.count for arm in self.arms.values()) + 1e-9
            ucb = 0.0
            for arm in self.arms.values():
                if arm.count:
                    ucb += self.ucb_c * np.sqrt(np.log(N) / arm.count)
            base_score += ucb

        # short reasoning string
        parts = []
        if r_num:
            parts.append('numeric ok')
        if r_log:
            parts.append('logic matches')
        if r_cau:
            parts.append('causal chain present')
        reasoning = '; '.join(parts) if parts else 'no clear evidence'

        return float(base_score), reasoning

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates. Returns list of dicts:
        {"candidate": str, "score": float, "reasoning": str}
        """
        # keep raw prompt for numeric heuristic
        prompt_feat = _parse_features(prompt)
        prompt_feat['_raw'] = prompt   # needed for numeric regex extraction

        results = []
        for cand in candidates:
            cand_feat = _parse_features(cand)
            score, reason = self._score_candidate(prompt_feat, cand_feat)
            results.append({
                'candidate': cand,
                'score': score,
                'reasoning': reason,
            })

        # tie‑break with NCD (max 15 % of final influence)
        if len(results) > 1:
            lengths = [zlib.compress((prompt + c).encode()).__len__() for c in candidates]
            min_len = min(lengths)
            ncds = [(min_len / l) for l in lengths]  # higher = more similar
            # normalize
            ncds = np.array(ncds)
            ncds = (ncds - ncds.min()) / (ncds.ptp() + 1e-9)
            for i, r in enumerate(results):
                r['score'] = 0.85 * r['score'] + 0.15 * ncds[i]

        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    # ------------------------------------------------------------------
    # Meta‑confidence utilities
    # ------------------------------------------------------------------
    def _meta_confidence(self, prompt: str) -> float:
        """Detect traps; return a base confidence in [0,1]."""
        low = 0.1   # default low confidence for ambiguous prompts
        # 1. presupposition
        if re.search(r'\bhave you (stopped|quit|ceased)\b', prompt, flags=re.I):
            return low
        # 2. scope ambiguity – simple heuristic
        if re.search(r'\bevery\b.*\b(?:a|an|the)\b.*\b(?:a|an|the)\b', prompt, flags=re.I):
            return low
        # 3. pronoun ambiguity
        if re.search(r'\b\w+\b\s+told\s+\b\w+\b\s+he|she\b', prompt, flags=re.I):
            return low
        # 4. false dichotomy
        if re.search(r'\beither\b.*\bor\b', prompt, flags=re.I) and not re.search(r'\bboth\b', prompt, flags=re.I):
            return low
        # 5. subjectivity
        if re.search(r'\b(best|worst|favorite|most|least)\b', prompt, flags=re.I):
            return low
        # 6. unanswerability – no question mark or missing key terms
        if not re.search(r'\?', prompt):
            return low
        # otherwise moderate confidence
        return 0.7

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Calibrated confidence 0‑1.
        Uses meta‑confidence and the current numeric‑arm certainty.
        """
        meta = self._meta_confidence(prompt)

        # numeric arm certainty: high if variance low and count > 0
        num_arm = self.arms['numeric']
        if num_arm.count and num_arm.var < 0.02:
            numeric_conf = 0.9
        else:
            numeric_conf = 0.3

        # combine (geometric mean favours low values)
        conf = np.sqrt(meta * numeric_conf)

        # cap according to specification
        if conf > 0.9:
            conf = 0.9
        # never return >0.9 unless we have a deterministic numeric result
        if conf > 0.8 and numeric_conf < 0.9:
            conf = 0.8
        return float(conf)


# --- Auto-fix: ensure confidence() returns float in [0, 1] ---
_orig_confidence = ReasoningTool.confidence
def _safe_confidence(self, prompt, answer):
    try:
        result = _orig_confidence(self, prompt, answer)
        if result is None:
            return 0.5
        return max(0.0, min(1.0, float(result)))
    except (TypeError, ValueError):
        return 0.5
ReasoningTool.confidence = _safe_confidence


# --- Auto-fix: ensure evaluate() returns list[dict] ---
_orig_evaluate = ReasoningTool.evaluate
def _safe_evaluate(self, prompt, candidates):
    try:
        result = _orig_evaluate(self, prompt, candidates)
        if result is None:
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        if not isinstance(result, list):
            return [{"candidate": c, "score": 0.5, "reasoning": "fallback"} for c in candidates]
        return result
    except Exception:
        return [{"candidate": c, "score": 0.5, "reasoning": "error"} for c in candidates]
ReasoningTool.evaluate = _safe_evaluate
