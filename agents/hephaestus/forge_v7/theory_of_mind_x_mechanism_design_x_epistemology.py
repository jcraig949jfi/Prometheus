import re
import math
import zlib
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Set

Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])


class ReasoningTool:
    """
    Theory of Mind x Mechanism Design x Epistemology.

    Gap target: Complex ToM (epistemic logic + strategic reasoning).

    Solvers:
      1. Perspective shift (facing each other = left/right swap)
      2. Intention reading (brought umbrella on sunny day -- what do they believe?)
      3. Argument strength evaluator (compare valid vs fallacious arguments)
      4. False belief (Sally-Anne variant)
      5. Knowledge attribution (informed vs uninformed agents)
      6. Mechanism design (incentive alignment, dominant strategy)

    Score: Structural (60%) + Computation (25%) + NCD (15%).
    """

    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|without|neither|doesn\'t|don\'t)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater|lower|higher|better|worse|stronger|weaker)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|would|could)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|due to|since|therefore|thus)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)\s*(kg|m|s|%|units)?', re.I),
            'belief': re.compile(r'\b(thinks?|believes?|expects?|assumes?|knows?)\b', re.I),
            'epistemic': re.compile(r'\b(justified|warranted|evidence|proof|valid|sound|fallac)', re.I),
            'argument': re.compile(r'\b(argument|premise|conclusion|therefore|hence|implies)\b', re.I),
        }
        self.fallacy_db = {
            'ad_hominem': re.compile(r'\b(?:stupid|idiot|fool|incompetent|unqualified)\b.*\b(?:therefore|so|thus|hence)\b', re.I),
            'appeal_authority': re.compile(r'\b(?:expert|professor|doctor|scientist)\s+(?:says?|said|claims?)\b.*\b(?:therefore|so|must be)\b', re.I),
            'straw_man': re.compile(r'\b(?:you\'re saying|so you think|you believe)\b.*\b(?:extreme|absurd|ridiculous)\b', re.I),
            'circular': re.compile(r'\b(\w{4,})\b.*\bbecause\b.*\b\1\b', re.I),
            'false_cause': re.compile(r'\b(?:after|followed by)\b.*\b(?:therefore|so|caused|because of)\b', re.I),
            'bandwagon': re.compile(r'\b(?:everyone|most people|majority|popular)\b.*\b(?:therefore|so|must be|right)\b', re.I),
            'slippery_slope': re.compile(r'\b(?:next thing|eventually|end up|lead to)\b.*\b(?:disaster|chaos|ruin|worst)\b', re.I),
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
        for key in ('negation', 'comparative', 'conditional', 'causal', 'belief', 'epistemic', 'argument'):
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

    # ── Perspective shift solver ────────────────────────────────────

    def _perspective_shift_solve(self, prompt: str, candidates: List[str]):
        """Facing each other: left/right swap, mirror image."""
        pl = prompt.lower()
        facing = re.search(r'(?:fac(?:e|es|ing)\s+(?:each other|you|opposite|across))', pl)
        if not facing:
            facing = re.search(r'(?:across\s+(?:from|the table)|opposite\s+(?:side|you))', pl)
        if not facing:
            return None, 0
        # Determine what is asked about
        lr_q = re.search(r'(?:which|what)\s+(?:side|hand|direction).*(?:your|from your)', pl)
        raise_m = re.search(r'(?:raises?|lifts?|holds?|waves?)\s+(?:his|her|their)?\s*(?:the\s+)?(left|right)', pl)
        if raise_m:
            orig = raise_m.group(1)
            answer = 'right' if orig == 'left' else 'left'
            for c in candidates:
                if answer in c.lower():
                    return c, 0.88
        # Generic left/right swap question
        if re.search(r'\b(left|right)\b', pl) and lr_q:
            if 'left' in pl:
                for c in candidates:
                    if 'right' in c.lower():
                        return c, 0.85
            elif 'right' in pl:
                for c in candidates:
                    if 'left' in c.lower():
                        return c, 0.85
        return None, 0

    # ── Intention reading solver ────────────────────────────────────

    def _intention_reading_solve(self, prompt: str, candidates: List[str]):
        """Infer beliefs/intentions from actions that seem incongruent."""
        pl = prompt.lower()
        if not re.search(r'what\s+(?:can|does?|do|would|might)\s+(?:we|this|that|it)\s+(?:infer|suggest|tell|indicate|mean|imply|reveal)', pl):
            return None, 0
        # Action-belief pairs
        incongruent = {
            'umbrella': {'sunny': 'expects rain', 'rain': 'prepared'},
            'coat': {'warm': 'expects cold', 'summer': 'expects cold'},
            'sunscreen': {'cloudy': 'expects sun', 'indoor': 'going outside'},
            'studying': {'holiday': 'expects exam', 'vacation': 'expects exam'},
            'saving': {'rich': 'expects downturn', 'wealthy': 'cautious'},
        }
        for obj, contexts in incongruent.items():
            if obj in pl:
                for ctx, belief in contexts.items():
                    if ctx in pl:
                        for c in candidates:
                            cl = c.lower()
                            if any(w in cl for w in belief.split()):
                                return c, 0.78
                        # Fallback: candidate mentioning belief/expect/think
                        for c in candidates:
                            if re.search(r'(?:believe|expect|think|anticipat|prepar)', c.lower()):
                                return c, 0.72
        return None, 0

    # ── Argument strength evaluator ─────────────────────────────────

    def _argument_strength_solve(self, prompt: str, candidates: List[str]):
        """Compare two arguments: identify which is valid vs fallacious."""
        pl = prompt.lower()
        if not re.search(r'(?:which|what)\s+(?:argument|reasoning|logic)\s+is\s+(?:stronger|better|valid|sound|more\s+convincing)', pl):
            if not re.search(r'(?:stronger|better|more valid|more sound)\s+(?:argument|reasoning)', pl):
                return None, 0
        # Check each candidate for fallacy patterns
        scores = []
        for c in candidates:
            cl = c.lower()
            fallacy_count = 0
            for fname, fpat in self.fallacy_db.items():
                if fpat.search(cl):
                    fallacy_count += 1
            # Also check for valid structure markers
            valid_markers = len(re.findall(r'\b(?:therefore|if.*then|all.*are|follows that|evidence shows)\b', cl))
            scores.append((c, valid_markers - fallacy_count * 2))
        if scores:
            scores.sort(key=lambda x: x[1], reverse=True)
            if scores[0][1] > scores[-1][1]:
                return scores[0][0], 0.75
        return None, 0

    # ── False belief (ToM) ──────────────────────────────────────────

    def _false_belief_solve(self, prompt: str, candidates: List[str]):
        """Sally-Anne: person leaves, object moved."""
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

    # ── Knowledge attribution ───────────────────────────────────────

    def _knowledge_attribution_solve(self, prompt: str, candidates: List[str]):
        """Informed vs uninformed agent."""
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
        return None, 0

    # ── Mechanism design solver ─────────────────────────────────────

    def _mechanism_design_solve(self, prompt: str, candidates: List[str]):
        """Incentive compatibility, truthful mechanism, dominant strategy."""
        pl = prompt.lower()
        if not re.search(r'(?:incentiv|mechanism|auction|vote|truthful|strategyproof|dominant\s+strategy)', pl):
            return None, 0
        # Vickrey / second-price auction
        if re.search(r'(?:second.price|vickrey|sealed.bid)', pl):
            if re.search(r'(?:what|how|should)\s+.*\s+(?:bid|strategy)', pl):
                for c in candidates:
                    cl = c.lower()
                    if any(w in cl for w in ('true value', 'truthful', 'actual value', 'honest')):
                        return c, 0.85
        # Dominant strategy
        if re.search(r'dominant\s+strategy', pl):
            nums = [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)', pl)]
            if len(nums) >= 4:
                # 2x2 payoff check
                if nums[0] > nums[2] and nums[1] > nums[3]:
                    for c in candidates:
                        if any(w in c.lower() for w in ('first', 'top', 'row 1', 'strategy a', 'cooperate')):
                            return c, 0.78
                elif nums[2] > nums[0] and nums[3] > nums[1]:
                    for c in candidates:
                        if any(w in c.lower() for w in ('second', 'bottom', 'row 2', 'strategy b', 'defect')):
                            return c, 0.78
        # Incentive alignment
        if re.search(r'incentive\s+(?:compatible|aligned)', pl):
            for c in candidates:
                if re.search(r'(?:truthful|honest|reveal|report accurately)', c.lower()):
                    return c, 0.75
        return None, 0

    # ── Strategic deception ─────────────────────────────────────────

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
        comp = 0.5 if (self.patterns['numeric'].search(prompt) and self.patterns['numeric'].search(candidate)) else 0.0
        ncd_s = (1.0 - self._ncd(prompt, candidate)) * 0.15
        score = base * 0.60 + comp * 0.25 + ncd_s
        return score, f"hyp={len(hyp)} mi={mi:.2f}"

    # ── Public API ──────────────────────────────────────────────────

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        solvers = [
            self._perspective_shift_solve, self._intention_reading_solve,
            self._argument_strength_solve, self._false_belief_solve,
            self._knowledge_attribution_solve, self._mechanism_design_solve,
            self._strategic_deception_solve,
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
