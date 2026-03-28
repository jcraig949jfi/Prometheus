import re
import math
import zlib
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Set

Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])


class ReasoningTool:
    """
    Theory of Mind x Metacognition x Abductive Reasoning.

    Gap target: Complex ToM (recursive belief attribution).

    Solvers:
      1. Abductive inference (inference to best explanation -- score by parsimony+coverage)
      2. Metacognitive reflection (re-examine top candidate for consistency)
      3. Confidence calibration ("probably X" -> moderate confidence)
      4. False belief (Sally-Anne)
      5. Knowledge attribution (informed vs uninformed)
      6. Second-order belief (A thinks B thinks...)
      7. Strategic deception (opposite behavior)

    Score: Structural (60%) + Computation (25%) + NCD (15%).
    """

    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|without|neither|doesn\'t|don\'t)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater|lower|higher|better|worse)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|would|could)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|due to|since|therefore|thus|explains?)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|units)?', re.I),
            'belief': re.compile(r'\b(thinks?|believes?|expects?|assumes?|knows?)\b', re.I),
            'hedging': re.compile(r'\b(probably|likely|possibly|perhaps|might|may|could|uncertain)\b', re.I),
            'abductive': re.compile(r'\b(explain|account for|best explanation|most likely|hypothesis|diagnos)', re.I),
        }
        self.confidence_hedges = {
            'certainly': 0.95, 'definitely': 0.95, 'must': 0.90,
            'very likely': 0.85, 'likely': 0.75, 'probably': 0.70,
            'possibly': 0.45, 'perhaps': 0.40, 'maybe': 0.40,
            'might': 0.35, 'unlikely': 0.20, 'rarely': 0.15,
            'impossible': 0.05, 'never': 0.05,
        }
        self.fallacy_triggers = {
            'presupposition': re.compile(r'(?:stopped|quit|when did you stop)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(?:every|all|each)\b.*\b(?:some|a|one)\b.*\b(?:not|doesn\'t)\b', re.I),
            'false_dichotomy': re.compile(r'\b(?:either|only two|must be one)\b.*\bor\b', re.I),
            'survivorship': re.compile(r'\b(?:successful|survivors?|winners?)\b.*\b(?:all|every|always)\b', re.I),
            'sunk_cost': re.compile(r'\b(?:already invested|already spent|too far|come this far)\b', re.I),
        }
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased|failed)\b.*\b(have you|did you)\b', re.I),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
        ]

    # ── Parsing ─────────────────────────────────────────────────────

    def _extract_statements(self, text: str) -> List[Statement]:
        stmts: List[Statement] = []
        lt = text.lower()
        w = 1.0
        if re.search(r'\b(certainly|definitely|must)\b', lt): w = 1.0
        elif re.search(r'\b(possibly|maybe|might)\b', lt): w = 0.5
        elif re.search(r'\b(rarely|unlikely)\b', lt): w = 0.3
        for key in ('negation', 'comparative', 'conditional', 'causal', 'belief', 'hedging', 'abductive'):
            if self.patterns[key].search(lt):
                stmts.append(Statement(key, [], key != 'negation', None, w))
        for m in self.patterns['numeric'].finditer(text):
            stmts.append(Statement('numeric', [float(m.group(1))], True, float(m.group(1)), w))
        if not stmts:
            stmts.append(Statement('generic', [], True, None, w))
        return stmts

    def _entropy(self, w: np.ndarray) -> float:
        if len(w) == 0 or w.sum() == 0: return 0.0
        p = w / w.sum(); p = p[p > 0]
        return float(-np.sum(p * np.log2(p + 1e-10)))

    def _ncd(self, a: str, b: str) -> float:
        try:
            ba, bb = a.encode(), b.encode()
            ca, cb, cab = len(zlib.compress(ba)), len(zlib.compress(bb)), len(zlib.compress(ba + bb))
            return (cab - min(ca, cb)) / max(ca, cb, 1)
        except Exception:
            return 1.0

    # ── Abductive inference solver ──────────────────────────────────

    def _abductive_solve(self, prompt: str, candidates: List[str]):
        """Inference to best explanation: score candidates by parsimony + coverage."""
        pl = prompt.lower()
        if not re.search(r'(?:explain|best explanation|most likely|account for|what caused|diagnos|why did)', pl):
            return None, 0
        # Extract observations (facts mentioned in prompt)
        observations = set()
        # Sentences as observation units
        sents = re.split(r'[.!?]+', pl)
        for s in sents:
            s = s.strip()
            if len(s) > 10 and not re.search(r'(?:which|what|why|how)\s', s):
                # This is a factual sentence (not a question)
                keywords = [w for w in re.findall(r'\b\w{4,}\b', s) if w not in
                           ('that', 'this', 'with', 'from', 'have', 'been', 'were', 'they', 'them', 'their')]
                observations.update(keywords[:5])
        if not observations:
            return None, 0
        # Score each candidate by coverage (how many observations it connects to) + parsimony
        best_c, best_s = None, -1.0
        for c in candidates:
            cl = c.lower()
            c_words = set(re.findall(r'\b\w{4,}\b', cl))
            # Coverage: fraction of observations mentioned or related in candidate
            coverage = len(observations & c_words) / max(len(observations), 1)
            # Parsimony: shorter explanations preferred (normalized)
            parsimony = 1.0 / (1.0 + len(c.split()) / 20.0)
            # Causal language bonus
            causal_bonus = 0.15 if self.patterns['causal'].search(cl) else 0.0
            score = coverage * 0.5 + parsimony * 0.2 + causal_bonus + 0.15
            if score > best_s:
                best_s, best_c = score, c
        if best_c and best_s > 0.3:
            return best_c, min(0.82, best_s)
        return None, 0

    # ── Metacognitive reflection ────────────────────────────────────

    def _metacognitive_reflect(self, prompt: str, candidate: str) -> float:
        """Re-examine a candidate for internal consistency. Returns penalty 0-0.3."""
        cl = candidate.lower()
        penalty = 0.0
        # Self-contradiction: contains both X and not-X
        if re.search(r'\b(is)\b', cl) and re.search(r'\b(is not|isn\'t)\b', cl):
            # Check if same subject
            penalty += 0.15
        # Vague hand-waving without substance
        vague_count = len(re.findall(r'\b(somehow|sort of|kind of|various|things|stuff)\b', cl))
        penalty += vague_count * 0.05
        # Overconfidence without evidence
        if re.search(r'\b(certainly|definitely|absolutely|always|never)\b', cl):
            if not re.search(r'\b(because|since|evidence|data|shows|proves)\b', cl):
                penalty += 0.10
        return min(0.3, penalty)

    # ── Confidence calibration ──────────────────────────────────────

    def _calibrate_confidence(self, text: str) -> float:
        """Extract hedging language and map to calibrated confidence."""
        tl = text.lower()
        best_match = None
        best_pos = len(tl) + 1
        for hedge, conf in self.confidence_hedges.items():
            idx = tl.find(hedge)
            if idx >= 0 and idx < best_pos:
                best_pos = idx
                best_match = conf
        return best_match if best_match is not None else 0.60

    # ── ToM solvers ─────────────────────────────────────────────────

    def _false_belief_solve(self, prompt: str, candidates: List[str]):
        """Sally-Anne variant."""
        pl = prompt.lower()
        put_m = re.search(r'(\w+)\s+(?:puts?|places?|leaves?)\s+(?:the\s+)?(\w+)\s+(?:in|on|under|behind)\s+(?:the\s+)?(\w+)', pl)
        move_m = re.search(r'(?:moves?|transfers?|takes?)\s+(?:the\s+)?(\w+)\s+(?:to|into|in|under|behind)\s+(?:the\s+)?(\w+)', pl)
        leaves_m = re.search(r'(\w+)\s+(?:leaves?|goes?\s+(?:out|away)|exits?|walks?\s+away)', pl)
        look_m = re.search(r'where\s+(?:will|does|would)\s+(\w+)\s+(?:look|search|expect|think)', pl)
        if put_m and move_m and leaves_m and look_m:
            original_loc = put_m.group(3)
            for c in candidates:
                if original_loc in c.lower():
                    return c, 0.88
        return None, 0

    def _knowledge_attribution_solve(self, prompt: str, candidates: List[str]):
        """Informed vs uninformed perspective."""
        pl = prompt.lower()
        if not re.search(r"(?:doesn't|does not|don't)\s+know", pl):
            return None, 0
        if not re.search(r'what\s+(?:does|would|will)\s+\w+\s+(?:think|believe|expect)', pl):
            return None, 0
        if re.search(r'(?:rigged|loaded|biased|unfair|weighted|trick)', pl):
            for c in candidates:
                cl = c.lower()
                if any(w in cl for w in ('fair', 'equal', '50', 'even', 'normal')):
                    return c, 0.85
        if re.search(r'(?:hidden|secret|concealed|moved)', pl):
            for c in candidates:
                cl = c.lower()
                if any(w in cl for w in ('original', 'initial', 'first', 'still', 'same')):
                    return c, 0.82
        return None, 0

    def _second_order_belief_solve(self, prompt: str, candidates: List[str]):
        """A thinks B thinks..."""
        pl = prompt.lower()
        m = re.search(r'(\w+)\s+(?:thinks?|believes?)\s+(?:that\s+)?(\w+)\s+(?:thinks?|believes?)\s+(?:that\s+)?(.*?)(?:\.|$)', pl)
        if not m:
            return None, 0
        belief_content = m.group(3).strip()
        actual_b = re.search(r'(?:but|however|actually|in reality)\s+' + m.group(2) + r'\s+(?:thinks?|believes?)\s+(?:that\s+)?(.*?)(?:\.|$)', pl)
        if actual_b:
            # A's model is outdated/wrong; answer uses A's model
            for c in candidates:
                if belief_content and any(w in c.lower() for w in belief_content.split()[:3] if len(w) > 2):
                    return c, 0.80
        else:
            for c in candidates:
                if belief_content and any(w in c.lower() for w in belief_content.split()[:3] if len(w) > 2):
                    return c, 0.75
        return None, 0

    def _strategic_deception_solve(self, prompt: str, candidates: List[str]):
        pl = prompt.lower()
        if not re.search(r'(?:opposite|contrary|reverse)', pl):
            return None, 0
        if not re.search(r'(?:should|would)\s+\w+\s+(?:say|tell)', pl):
            return None, 0
        want_m = re.search(r'wants?\s+(?:\w+\s+)?to\s+(?:go\s+)?(left|right|stay|leave|yes|no)', pl)
        if want_m:
            want = want_m.group(1)
            opp = {'left': 'right', 'right': 'left', 'stay': 'leave',
                    'leave': 'stay', 'yes': 'no', 'no': 'yes'}
            for c in candidates:
                if opp.get(want, want) in c.lower():
                    return c, 0.85
        return None, 0

    def _information_asymmetry_solve(self, prompt: str, candidates: List[str]):
        """Detect who knows what."""
        pl = prompt.lower()
        see_m = re.search(r'(\w+)\s+(?:sees?|witnesses?|observes?|watches?|notices?)\s+(.*?)(?:\.|,)', pl)
        not_see = re.search(r'(\w+)\s+(?:does not|doesn\'t)\s+(?:see|witness|observe|know)', pl)
        if see_m and not_see:
            uninformed = not_see.group(1)
            ask_m = re.search(r'what\s+(?:does|would|will)\s+(\w+)\s+(?:think|believe|expect)', pl)
            if ask_m and ask_m.group(1) == uninformed:
                for c in candidates:
                    cl = c.lower()
                    if any(w in cl for w in ('original', 'initial', 'default', 'first', 'still', 'same')):
                        return c, 0.82
        return None, 0

    # ── Meta-confidence (Tier B) ────────────────────────────────────

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        pl = prompt.lower()
        for name, pat in self.fallacy_triggers.items():
            if pat.search(pl):
                return 0.25
        for pat in self.presupposition_triggers:
            if pat.search(pl):
                return 0.25
        if re.search(r'\b(best|worst|favorite|opinion|beautiful|ugly)\b', pl):
            if not re.search(r'\bbest\s+(?:explain|describe|account|represent|fit)', pl):
                return 0.28
        stmts = self._extract_statements(prompt)
        if len(stmts) == 1 and stmts[0].pred == 'generic' and len(prompt.split()) < 8:
            return 0.20
        return 1.0

    # ── Core scoring ────────────────────────────────────────────────

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        stmts = self._extract_statements(f"{prompt} {candidate}")
        ws = np.array([s.weight for s in stmts])
        h_total = self._entropy(ws)
        hyp: Set[int] = set()
        rem = set(range(len(stmts)))
        cw = ws.copy()
        for _ in range(min(5, len(stmts))):
            best_i, best_g = -1, -1.0
            for i in rem:
                tw = cw.copy(); tw[i] = 0
                g = h_total - self._entropy(tw)
                if g > best_g: best_g, best_i = g, i
            if best_i >= 0 and best_g > 0.01:
                hyp.add(best_i); rem.discard(best_i); cw[best_i] = 0
            else:
                break
        rw = ws.copy()
        for i in hyp: rw[i] = 0
        mi = h_total - self._entropy(rw)
        base = 1 / (1 + math.exp(-mi))
        # Metacognitive reflection penalty
        mc_penalty = self._metacognitive_reflect(prompt, candidate)
        comp = 0.5 if (self.patterns['numeric'].search(prompt) and self.patterns['numeric'].search(candidate)) else 0.0
        ncd_s = (1.0 - self._ncd(prompt, candidate)) * 0.15
        score = base * 0.60 + comp * 0.25 + ncd_s - mc_penalty
        # Confidence calibration from hedging language in candidate
        cal = self._calibrate_confidence(candidate)
        score = score * (0.7 + 0.3 * cal)  # Slight modulation by hedging
        return max(0.0, score), f"hyp={len(hyp)} mi={mi:.2f} mc_pen={mc_penalty:.2f} cal={cal:.2f}"

    # ── Public API ──────────────────────────────────────────────────

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        solvers = [
            self._abductive_solve, self._false_belief_solve,
            self._knowledge_attribution_solve, self._second_order_belief_solve,
            self._strategic_deception_solve, self._information_asymmetry_solve,
        ]
        for solver in solvers:
            try:
                best, score = solver(prompt, candidates)
                if best and score > 0.5:
                    results = []
                    for c in candidates:
                        s = float(score) if c == best else float(max(0.05, 1.0 - score))
                        results.append({"candidate": c, "score": s,
                                        "reasoning": f"execution:solver={solver.__name__}"})
                    results.sort(key=lambda x: x["score"], reverse=True)
                    return results
            except Exception:
                pass
        meta_cap = self._meta_confidence(prompt, "")
        results = []
        for c in candidates:
            s, reason = self._score_candidate(prompt, c)
            if meta_cap < 1.0:
                s = min(s, meta_cap)
                reason += f" [meta_cap={meta_cap:.2f}]"
            results.append({"candidate": c, "score": float(s), "reasoning": reason})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta_cap = self._meta_confidence(prompt, answer)
        if meta_cap < 0.3:
            return meta_cap
        s, _ = self._score_candidate(prompt, answer)
        return float(max(0.0, min(0.95, min(s, meta_cap))))
