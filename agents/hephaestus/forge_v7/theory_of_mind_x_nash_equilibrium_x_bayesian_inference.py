import re
import math
import zlib
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Optional, Set

Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])


class ReasoningTool:
    """
    Theory of Mind x Nash Equilibrium x Bayesian Inference.

    Gap target: Complex ToM (recursive Bayesian agent modeling).

    Solvers:
      1. False belief (Sally-Anne: person leaves, object moved, where do they look?)
      2. Knowledge attribution (You know X is rigged, Tom doesn't — what does Tom think?)
      3. Second-order belief (Alice thinks Bob thinks...)
      4. Strategic deception (X knows Y does opposite — what should X say?)
      5. Information asymmetry detector
      6. Mistaken belief chain (misinformation propagation)

    Score: Structural (60%) + Computation (25%) + NCD (15%).
    """

    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|without|neither|doesn\'t|don\'t|didn\'t)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater|lower|higher|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|would|could)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|due to|since|therefore)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|units)?', re.I),
            'ordering': re.compile(r'\b(first|second|third|last|rank|order)\b', re.I),
            'belief': re.compile(r'\b(thinks?|believes?|expects?|assumes?|knows?)\b', re.I),
            'tom': re.compile(r'\b(perspective|viewpoint|see|look|search|find)\b', re.I),
        }
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased|failed)\b.*\b(have you|did you)\b', re.I),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
            re.compile(r'\b(?:either)\b.*\b(?:or)\b', re.I),
        ]
        self.fallacy_triggers = {
            'presupposition': re.compile(r'(?:stopped|quit|when did you stop)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(?:every|all|each)\b.*\b(?:some|a|one)\b.*\b(?:not|doesn\'t)\b', re.I),
            'false_dichotomy': re.compile(r'\b(?:either|only two|must be one)\b.*\bor\b', re.I),
            'survivorship': re.compile(r'\b(?:successful|survivors?|winners?)\b.*\b(?:all|every|always)\b', re.I),
            'sunk_cost': re.compile(r'\b(?:already invested|already spent|too far|come this far)\b', re.I),
        }

    # ── Structural parsing ──────────────────────────────────────────

    def _extract_statements(self, text: str) -> List[Statement]:
        stmts: List[Statement] = []
        lt = text.lower()
        w = 1.0
        if re.search(r'\b(certainly|definitely|must)\b', lt): w = 1.0
        elif re.search(r'\b(possibly|maybe|might)\b', lt): w = 0.5
        elif re.search(r'\b(rarely|unlikely)\b', lt): w = 0.3
        for key in ('negation', 'comparative', 'conditional', 'causal', 'ordering', 'belief', 'tom'):
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

    # ── ToM solvers ─────────────────────────────────────────────────

    def _false_belief_solve(self, prompt: str, candidates: List[str]):
        """Sally-Anne: person leaves, object moved. Where do they look?"""
        pl = prompt.lower()
        # Detect: X puts/places object in location_A, X leaves, Y moves object to location_B
        put_m = re.search(r'(\w+)\s+(?:puts?|places?|leaves?)\s+(?:the\s+)?(\w+)\s+(?:in|on|under|behind)\s+(?:the\s+)?(\w+)', pl)
        move_m = re.search(r'(?:moves?|transfers?|takes?)\s+(?:the\s+)?(\w+)\s+(?:to|into|in|under|behind)\s+(?:the\s+)?(\w+)', pl)
        leaves_m = re.search(r'(\w+)\s+(?:leaves?|goes?\s+(?:out|away)|exits?|walks?\s+away)', pl)
        look_m = re.search(r'where\s+(?:will|does|would)\s+(\w+)\s+(?:look|search|expect|think)', pl)

        if put_m and move_m and leaves_m and look_m:
            original_loc = put_m.group(3)
            # The person who left still believes object is in original location
            for c in candidates:
                if original_loc in c.lower():
                    return c, 0.88
        return None, 0

    def _knowledge_attribution_solve(self, prompt: str, candidates: List[str]):
        """You know X is rigged, Tom doesn't. What does Tom think?"""
        pl = prompt.lower()
        if not re.search(r"(?:doesn't|does not|don't|do not)\s+know", pl):
            return None, 0
        if not re.search(r'what\s+(?:does|would|will)\s+\w+\s+(?:think|believe|expect|guess|predict)', pl):
            return None, 0
        # Rigged / biased / loaded => uninformed thinks fair
        if re.search(r'(?:rigged|loaded|biased|unfair|weighted|trick)', pl):
            for c in candidates:
                cl = c.lower()
                if any(w in cl for w in ('fair', 'equal', '50', 'even', 'normal', 'unbiased')):
                    return c, 0.85
        # Hidden / secret => uninformed uses default/visible information
        if re.search(r'(?:hidden|secret|concealed|unknown)', pl):
            for c in candidates:
                cl = c.lower()
                if any(w in cl for w in ('visible', 'apparent', 'surface', 'default', 'obvious')):
                    return c, 0.80
        return None, 0

    def _second_order_belief_solve(self, prompt: str, candidates: List[str]):
        """Alice thinks Bob thinks..."""
        pl = prompt.lower()
        # Match: X thinks/believes Y thinks/believes Z
        m = re.search(r'(\w+)\s+(?:thinks?|believes?)\s+(?:that\s+)?(\w+)\s+(?:thinks?|believes?)\s+(?:that\s+)?(.*?)(?:\.|$)', pl)
        if not m:
            return None, 0
        person_a, person_b, belief_content = m.group(1), m.group(2), m.group(3).strip()
        # Check if there's information about what person_b actually believes vs what A thinks
        actual_b = re.search(r'(?:but|however|actually|in reality)\s+' + person_b + r'\s+(?:thinks?|believes?)\s+(?:that\s+)?(.*?)(?:\.|$)', pl)
        if actual_b:
            # A's belief about B is wrong => answer about "what does A think B thinks" uses A's model
            for c in candidates:
                if belief_content and any(w in c.lower() for w in belief_content.split()[:3]):
                    return c, 0.80
        else:
            # No contradiction => A's model of B is presumed correct
            for c in candidates:
                if belief_content and any(w in c.lower() for w in belief_content.split()[:3]):
                    return c, 0.75
        return None, 0

    def _strategic_deception_solve(self, prompt: str, candidates: List[str]):
        """X knows Y does opposite of what told. What should X say?"""
        pl = prompt.lower()
        if not re.search(r'(?:opposite|contrary|reverse|contrarian)', pl):
            return None, 0
        if not re.search(r'(?:should|would|will)\s+\w+\s+(?:say|tell|recommend|advise)', pl):
            return None, 0
        want_m = re.search(r'wants?\s+(?:\w+\s+)?to\s+(?:go\s+)?(left|right|stay|leave|yes|no|north|south|east|west|buy|sell|accept|reject)', pl)
        if want_m:
            want = want_m.group(1)
            opp = {'left': 'right', 'right': 'left', 'stay': 'leave', 'leave': 'stay',
                    'yes': 'no', 'no': 'yes', 'north': 'south', 'south': 'north',
                    'east': 'west', 'west': 'east', 'buy': 'sell', 'sell': 'buy',
                    'accept': 'reject', 'reject': 'accept'}
            answer = opp.get(want, want)
            for c in candidates:
                if answer in c.lower():
                    return c, 0.85
        return None, 0

    def _information_asymmetry_solve(self, prompt: str, candidates: List[str]):
        """Detect who knows what and answer from the uninformed perspective."""
        pl = prompt.lower()
        # Pattern: X sees/witnesses something, Y does not
        see_m = re.search(r'(\w+)\s+(?:sees?|witnesses?|observes?|watches?|notices?)\s+(.*?)(?:\.|,)', pl)
        not_see = re.search(r'(\w+)\s+(?:does not|doesn\'t)\s+(?:see|witness|observe|watch|notice|know)', pl)
        if see_m and not_see:
            informed = see_m.group(1)
            uninformed = not_see.group(1)
            ask_m = re.search(r'what\s+(?:does|would|will)\s+(\w+)\s+(?:think|believe|expect)', pl)
            if ask_m:
                asked_about = ask_m.group(1)
                if asked_about == uninformed:
                    # Uninformed uses prior/default
                    for c in candidates:
                        cl = c.lower()
                        if any(w in cl for w in ('original', 'initial', 'default', 'first', 'still', 'same')):
                            return c, 0.82
        return None, 0

    def _mistaken_belief_chain_solve(self, prompt: str, candidates: List[str]):
        """Misinformation propagation: A tells B who tells C..."""
        pl = prompt.lower()
        # Pattern: A tells B that X, B tells C that Y (possibly distorted)
        tells = re.findall(r'(\w+)\s+(?:tells?|says?\s+to|informs?)\s+(\w+)\s+(?:that\s+)?(.*?)(?:\.|,|$)', pl)
        if len(tells) < 2:
            return None, 0
        # Track belief propagation
        beliefs = {}
        for teller, receiver, content in tells:
            beliefs[receiver.lower()] = content.strip()
        ask_m = re.search(r'what\s+(?:does|would|will)\s+(\w+)\s+(?:think|believe|expect)', pl)
        if ask_m:
            target = ask_m.group(1).lower()
            if target in beliefs:
                belief = beliefs[target]
                for c in candidates:
                    # Match candidate that aligns with what target was told
                    if any(w in c.lower() for w in belief.split()[:4] if len(w) > 2):
                        return c, 0.78
        return None, 0

    # ── Nash equilibrium solver ─────────────────────────────────────

    def _nash_solve(self, prompt: str, candidates: List[str]):
        """Simple 2-player game theory: dominant strategy / Nash equilibrium."""
        pl = prompt.lower()
        if not re.search(r'(?:strateg|game|payoff|player|nash|dominant|equilibrium)', pl):
            return None, 0
        # Parse payoff matrix hints
        nums = [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)', pl)]
        if len(nums) >= 4:
            # Try 2x2 game
            if len(nums) >= 8:
                # Row player payoffs: (a,b), (c,d); Col payoffs: (e,f), (g,h)
                rp = np.array([[nums[0], nums[2]], [nums[4], nums[6]]])
                cp = np.array([[nums[1], nums[3]], [nums[5], nums[7]]])
                # Find pure Nash: cell where row is best response AND col is best response
                for i in range(2):
                    for j in range(2):
                        row_br = rp[i, j] >= rp[1 - i, j]
                        col_br = cp[i, j] >= cp[i, 1 - j]
                        if row_br and col_br:
                            label = f"({i+1},{j+1})"
                            for c in candidates:
                                if label in c or (str(int(rp[i, j])) in c and str(int(cp[i, j])) in c):
                                    return c, 0.80
            # Dominant strategy
            if re.search(r'dominant', pl) and len(nums) >= 4:
                if nums[0] > nums[2] and nums[1] > nums[3]:
                    for c in candidates:
                        if 'first' in c.lower() or '1' in c or 'a' in c.lower():
                            return c, 0.75
        return None, 0

    # ── Bayesian update solver ──────────────────────────────────────

    def _bayesian_update_solve(self, prompt: str, candidates: List[str]):
        """Apply Bayes' theorem: P(H|E) = P(E|H)*P(H)/P(E)."""
        pl = prompt.lower()
        if not re.search(r'(?:probability|bayes|prior|posterior|likelihood|given that|P\()', pl):
            return None, 0
        # Extract probabilities
        probs = re.findall(r'(\d+(?:\.\d+)?)\s*%', pl)
        if not probs:
            probs = re.findall(r'(?:probability|chance|likelihood)\s+(?:of\s+)?(?:is\s+)?(\d+(?:\.\d+)?)', pl)
        if not probs:
            probs = re.findall(r'(\d\.\d+)', pl)
        if len(probs) >= 2:
            vals = [float(p) for p in probs]
            # Normalize if percentages
            vals = [v / 100.0 if v > 1.0 else v for v in vals]
            if len(vals) >= 3:
                # P(H), P(E|H), P(E|~H) => posterior
                ph, peh, penh = vals[0], vals[1], vals[2]
                pe = peh * ph + penh * (1 - ph)
                if pe > 0:
                    posterior = (peh * ph) / pe
                    post_pct = round(posterior * 100, 1)
                    for c in candidates:
                        cnums = re.findall(r'(\d+(?:\.\d+)?)', c)
                        for cn in cnums:
                            if abs(float(cn) - post_pct) < 2.0 or abs(float(cn) - posterior) < 0.02:
                                return c, 0.88
            elif len(vals) == 2:
                product = vals[0] * vals[1]
                for c in candidates:
                    cnums = re.findall(r'(\d+(?:\.\d+)?)', c)
                    for cn in cnums:
                        cv = float(cn)
                        if cv > 1: cv /= 100.0
                        if abs(cv - product) < 0.02:
                            return c, 0.75
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
        # "best explanation" / "best describes" are epistemic, not subjective
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
        # Greedy hypothesis
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
        # Computation bonus
        comp = 0.5 if (self.patterns['numeric'].search(prompt) and self.patterns['numeric'].search(candidate)) else 0.0
        ncd_s = (1.0 - self._ncd(prompt, candidate)) * 0.15
        score = base * 0.60 + comp * 0.25 + ncd_s
        return score, f"hyp={len(hyp)} mi={mi:.2f}"

    # ── Public API ──────────────────────────────────────────────────

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        solvers = [
            self._false_belief_solve, self._knowledge_attribution_solve,
            self._second_order_belief_solve, self._strategic_deception_solve,
            self._information_asymmetry_solve, self._mistaken_belief_chain_solve,
            self._nash_solve, self._bayesian_update_solve,
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
        # Fallback: structural scoring
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
