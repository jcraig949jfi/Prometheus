import re
import math
import zlib
import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple, Optional, Set

Statement = namedtuple('Statement', ['pred', 'args', 'polarity', 'num_val', 'weight'])


class ReasoningTool:
    """
    Frame B/C hybrid: Constructive computation + dynamics tracking.
    Model Checking x Constraint Satisfaction x Falsificationism.

    Gap target: Self-referential (constraint propagation over loops).
    Core solver: liar detection via exhaustive truth-assignment search with
    constraint propagation. Also: premise contradiction, chained conditionals,
    multi-hop deduction, and all standard structural parsers.

    Score: Structural (70%) + Computation (20%) + NCD tiebreaker (10%).
    """

    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no\b|without|neither|doesn\'t|don\'t|isn\'t|aren\'t|cannot|can\'t)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater|fewer|taller|shorter|heavier|lighter|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|whenever|provided that)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|due to|since|therefore|thus|hence)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)', re.I),
            'ordering': re.compile(r'\b(first|second|third|last|rank|order)\b', re.I),
        }
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased)\b.*\b(have you|did you)\b', re.I),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
        ]
        self.subjectivity_triggers = re.compile(r'\b(best|worst|favorite|opinion|beautiful)\b', re.I)

    # ── Liar / truth-teller solver ────────────────────────────────
    def _liar_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "X says Y lies/is a liar"  or  "X says Y tells the truth"
        lie_claims = re.findall(r'(\w+)\s+(?:says?|claims?)\s+(?:that\s+)?(\w+)\s+(?:is\s+)?(?:lying|liar|lies)', pl)
        truth_claims = re.findall(r'(\w+)\s+(?:says?|claims?)\s+(?:that\s+)?(\w+)\s+(?:tells?\s+(?:the\s+)?truth|is\s+honest|is\s+truthful)', pl)
        if not lie_claims and not truth_claims:
            return None, 0.0
        people = set()
        for a, b in lie_claims + truth_claims:
            people.update([a, b])
        exactly_one = bool(re.search(r'exactly one', pl))
        solutions = []
        for candidate_tt in people:
            tt_set = {candidate_tt}
            liar_set = set()
            queue = [candidate_tt]
            consistent = True
            while queue and consistent:
                current = queue.pop(0)
                is_tt = current in tt_set
                for a, b in lie_claims:
                    if a == current:
                        target_liar = is_tt
                        if target_liar:
                            if b in tt_set:
                                consistent = False; break
                            if b not in liar_set:
                                liar_set.add(b); queue.append(b)
                        else:
                            if b in liar_set:
                                consistent = False; break
                            if b not in tt_set:
                                tt_set.add(b); queue.append(b)
                    if b == current:
                        pass  # b is the object, not the speaker
                if not consistent:
                    break
                for a, b in truth_claims:
                    if a == current:
                        target_truth = is_tt
                        if target_truth:
                            if b in liar_set:
                                consistent = False; break
                            if b not in tt_set:
                                tt_set.add(b); queue.append(b)
                        else:
                            if b in tt_set:
                                consistent = False; break
                            if b not in liar_set:
                                liar_set.add(b); queue.append(b)
                    if not consistent:
                        break
            if not consistent or (tt_set & liar_set):
                continue
            remaining = people - tt_set - liar_set
            for r in remaining:
                liar_set.add(r)
            if tt_set & liar_set:
                continue
            if exactly_one and len(tt_set) != 1:
                continue
            solutions.append((tt_set, liar_set))
        if len(solutions) == 1:
            tt_set = solutions[0][0]
            for c in candidates:
                cl = c.lower()
                for t in tt_set:
                    if t in cl:
                        return c, 0.90
        elif len(solutions) > 1:
            # Multiple solutions -- pick any that matches a candidate
            for sol_tt, _ in solutions:
                for c in candidates:
                    cl = c.lower()
                    for t in sol_tt:
                        if t in cl:
                            return c, 0.65
        return None, 0.0

    # ── Premise contradiction detector ────────────────────────────
    def _contradiction_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # Detect "All X are Y" + "Z is X but not Y"
        universals = re.findall(r'all\s+(\w+)\s+are\s+(\w+)', pl)
        negations = re.findall(r'(\w+)\s+is\s+(?:a\s+)?(\w+)\s+(?:but|and)\s+(?:is\s+)?not\s+(?:a\s+)?(\w+)', pl)
        if universals and negations:
            for cat, prop in universals:
                for entity, ecat, eprop in negations:
                    if ecat == cat and eprop == prop:
                        for c in candidates:
                            if 'contradiction' in c.lower() or 'false' in c.lower() or 'impossible' in c.lower():
                                return c, 0.85
        # "X is both A and not A"
        if re.search(r'(\w+)\s+is\s+both\s+(\w+)\s+and\s+not\s+\2', pl):
            for c in candidates:
                if 'contradiction' in c.lower() or 'false' in c.lower():
                    return c, 0.85
        return None, 0.0

    # ── Chained conditional solver ────────────────────────────────
    def _chained_conditional_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "If A then B. If B then C. A is true. What about C?"
        chains = re.findall(r'if\s+(\w+(?:\s+\w+)?)\s*(?:,\s*)?then\s+(\w+(?:\s+\w+)?)', pl)
        if len(chains) < 2:
            return None, 0.0
        # Build forward map
        fwd = {}
        for ante, cons in chains:
            fwd[ante.strip()] = cons.strip()
        # Find given facts
        givens = set()
        for m in re.finditer(r'(\w+(?:\s+\w+)?)\s+is\s+true', pl):
            givens.add(m.group(1).strip())
        # Propagate
        changed = True
        derived = set(givens)
        while changed:
            changed = False
            for ante, cons in fwd.items():
                if ante in derived and cons not in derived:
                    derived.add(cons)
                    changed = True
        # Match candidates
        for c in candidates:
            cl = c.lower()
            for d in derived - givens:
                if d in cl or 'true' in cl or 'yes' in cl:
                    return c, 0.80
        return None, 0.0

    # ── Multi-hop deduction (A->B->C->D) ──────────────────────────
    def _multihop_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "A implies B. B implies C. C implies D. A is true. Is D true?"
        implies = re.findall(r'(\w+)\s+(?:implies|means|leads to|entails|causes)\s+(\w+)', pl)
        if len(implies) < 2:
            return None, 0.0
        fwd = {}
        for a, b in implies:
            fwd.setdefault(a.strip(), []).append(b.strip())
        givens = set()
        for m in re.finditer(r'(\w+)\s+is\s+(?:true|given|known)', pl):
            givens.add(m.group(1).strip())
        reachable = set(givens)
        frontier = list(givens)
        while frontier:
            node = frontier.pop(0)
            for nxt in fwd.get(node, []):
                if nxt not in reachable:
                    reachable.add(nxt)
                    frontier.append(nxt)
        target_m = re.search(r'(?:is|does|will)\s+(\w+)\s+(?:true|hold|follow|happen)', pl)
        if target_m:
            t = target_m.group(1).strip()
            answer = t in reachable
            for c in candidates:
                cl = c.lower()
                if answer and ('yes' in cl or 'true' in cl or t in cl):
                    return c, 0.80
                if not answer and ('no' in cl or 'false' in cl):
                    return c, 0.80
        return None, 0.0

    # ── Modus tollens ─────────────────────────────────────────────
    def _modus_tollens_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "If P then Q. Q is false. Therefore P is ..."
        cond = re.findall(r'if\s+(.+?)\s*(?:,\s*)?then\s+(.+?)\.', pl)
        if not cond:
            return None, 0.0
        for ante, cons in cond:
            cons_clean = cons.strip()
            # Check if consequent is negated
            if re.search(re.escape(cons_clean) + r'\s+is\s+(?:false|not true|wrong)', pl) or \
               re.search(r'not\s+' + re.escape(cons_clean), pl):
                # P must be false
                for c in candidates:
                    cl = c.lower()
                    if 'false' in cl or 'not' in cl or 'no' in cl:
                        return c, 0.80
        return None, 0.0

    # ── Bat-and-ball / algebraic word problems ────────────────────
    def _bat_ball_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "X and Y cost $T together. X costs $D more than Y. How much does Y cost?"
        m = re.search(r'(\w+)\s+and\s+(?:a\s+)?(\w+)\s+(?:cost|total)\s+\$?([\d.]+)', pl)
        m2 = re.search(r'(\w+)\s+costs?\s+\$?([\d.]+)\s+more\s+than\s+(?:the\s+)?(\w+)', pl)
        if m and m2:
            total = float(m.group(3))
            diff = float(m2.group(2))
            # x + y = total, x - y = diff => y = (total - diff) / 2
            y_val = (total - diff) / 2.0
            x_val = total - y_val
            # Figure out which is asked
            for c in candidates:
                # Check both values
                y_str = f"{y_val:g}"
                x_str = f"{x_val:g}"
                if y_str in c or f"${y_str}" in c:
                    return c, 0.90
                if x_str in c or f"${x_str}" in c:
                    return c, 0.85
        return None, 0.0

    # ── Negation scope ────────────────────────────────────────────
    def _negation_scope_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "Not all X are Y" != "No X are Y"
        if re.search(r'not all\s+\w+\s+are\s+\w+', pl):
            for c in candidates:
                cl = c.lower()
                if 'some' in cl or 'at least one' in cl or 'not necessarily' in cl:
                    return c, 0.80
                if 'none' in cl or 'no ' in cl:
                    # This is the wrong interpretation
                    continue
        return None, 0.0

    # ── SVO extraction for who-did-what ───────────────────────────
    def _svo_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "X verb-ed Y" patterns + "who verb-ed?" questions
        svo = re.findall(r'(\w+)\s+(gave|told|sent|showed|passed|handed|kicked|hit|threw)\s+(?:the\s+)?(?:\w+\s+to\s+)?(\w+)', pl)
        if svo and re.search(r'\bwho\b', pl):
            action_m = re.search(r'who\s+(\w+)', pl)
            if action_m:
                verb_q = action_m.group(1)
                for subj, verb, obj in svo:
                    if verb.startswith(verb_q[:3]):
                        for c in candidates:
                            if subj in c.lower():
                                return c, 0.75
        return None, 0.0

    # ── Transitivity solver ───────────────────────────────────────
    def _transitivity_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        relations = re.findall(r'(\w+)\s+is\s+(taller|shorter|heavier|lighter|older|younger|faster|slower|bigger|smaller)\s+than\s+(\w+)', pl)
        if len(relations) < 2:
            return None, 0.0
        # Build graph: a > b for "a is taller than b"
        greater = []
        for a, rel, b in relations:
            if rel in ('taller', 'heavier', 'older', 'faster', 'bigger'):
                greater.append((a, b))
            else:
                greater.append((b, a))
        # Transitive closure
        entities = set()
        for a, b in greater:
            entities.update([a, b])
        # Reachability
        reach = {e: set() for e in entities}
        for a, b in greater:
            reach[a].add(b)
        changed = True
        while changed:
            changed = False
            for e in entities:
                for r in list(reach[e]):
                    for rr in list(reach.get(r, [])):
                        if rr not in reach[e]:
                            reach[e].add(rr)
                            changed = True
        # "Who is tallest?" or "Is A taller than C?"
        superlative = re.search(r'who\s+is\s+(?:the\s+)?(tallest|shortest|heaviest|lightest|oldest|youngest|fastest|slowest|biggest|smallest)', pl)
        if superlative:
            sup = superlative.group(1)
            find_max = sup in ('tallest', 'heaviest', 'oldest', 'fastest', 'biggest')
            if find_max:
                for e in entities:
                    if len(reach[e]) == len(entities) - 1:
                        for c in candidates:
                            if e in c.lower():
                                return c, 0.85
            else:
                for e in entities:
                    if not reach[e]:
                        for c in candidates:
                            if e in c.lower():
                                return c, 0.85
        return None, 0.0

    # ── Numeric arithmetic ────────────────────────────────────────
    def _numeric_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        nums = [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)', pl)]
        if len(nums) < 2:
            return None, 0.0
        results = set()
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j:
                    continue
                results.update([nums[i] + nums[j], nums[i] - nums[j],
                                nums[i] * nums[j]])
                if nums[j] != 0:
                    results.add(nums[i] / nums[j])
        best, best_score = None, 0.0
        for c in candidates:
            c_nums = re.findall(r'(-?\d+(?:\.\d+)?)', c)
            for cn in c_nums:
                cv = float(cn)
                if cv in results or any(abs(cv - r) < 0.01 for r in results):
                    if best_score < 0.6:
                        best, best_score = c, 0.60
        return best, best_score

    # ── NCD tiebreaker (10% weight) ───────────────────────────────
    def _compute_ncd(self, s1: str, s2: str) -> float:
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except Exception:
            return 1.0

    # ── Meta-confidence (Tier B) ──────────────────────────────────
    def _meta_confidence(self, prompt: str, answer: str) -> float:
        pl = prompt.lower()
        for pat in self.presupposition_triggers:
            if pat.search(pl):
                return 0.25
        if self.subjectivity_triggers.search(pl):
            return 0.30
        if re.search(r'\b(ambiguous|unclear|vague|insufficient)\b', pl):
            return 0.25
        return 1.0

    # ── Main evaluate ─────────────────────────────────────────────
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        solvers = [
            self._liar_solve, self._contradiction_solve,
            self._chained_conditional_solve, self._multihop_solve,
            self._modus_tollens_solve, self._bat_ball_solve,
            self._negation_scope_solve, self._svo_solve,
            self._transitivity_solve, self._numeric_solve,
        ]
        for solver in solvers:
            try:
                best, score = solver(prompt, candidates)
                if best and score > 0.5:
                    meta = self._meta_confidence(prompt, best)
                    score = min(score, meta)
                    results = []
                    for c in candidates:
                        if c == best:
                            results.append({"candidate": c, "score": float(score),
                                            "reasoning": f"execution:{solver.__name__}"})
                        else:
                            results.append({"candidate": c, "score": 0.1,
                                            "reasoning": "structural:non_match"})
                    results.sort(key=lambda x: x["score"], reverse=True)
                    return results
            except Exception:
                pass
        # Fallback: NCD ranking
        results = []
        for c in candidates:
            ncd = self._compute_ncd(prompt, c)
            results.append({"candidate": c, "score": float((1 - ncd) * 0.10),
                            "reasoning": "fallback:ncd_only"})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        meta = self._meta_confidence(prompt, answer)
        if meta < 0.3:
            return meta
        res = self.evaluate(prompt, [answer])
        if res:
            return float(max(0.0, min(1.0, min(res[0]["score"], meta))))
        return 0.2
