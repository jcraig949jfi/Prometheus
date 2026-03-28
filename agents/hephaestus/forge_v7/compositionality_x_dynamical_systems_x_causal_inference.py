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
    Compositionality x Dynamical Systems x Causal Inference.

    Gap target: Compositional (chaining temporal + causal reasoning).
    Core solvers: heterogeneous chain composition (logic THEN arithmetic THEN
    causal), train catch-up (d=r*t), temporal-causal counterfactuals,
    multi-hop with distractor pruning, depth-scaling 2-8 steps.
    Also: all standard parsers.

    Score: Structural (70%) + Computation (20%) + NCD tiebreaker (10%).
    """

    def __init__(self):
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no\b|without|neither|doesn\'t|don\'t|isn\'t|aren\'t)\b', re.I),
            'comparative': re.compile(r'\b(more than|less than|greater|fewer|taller|shorter|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|whenever)\b', re.I),
            'causal': re.compile(r'\b(because|causes?d?|leads?\s+to|due to|since|therefore|thus|hence|result)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)', re.I),
            'temporal': re.compile(r'\b(before|after|then|first|next|later|earlier|while|during|until|since)\b', re.I),
            'counterfactual': re.compile(r'\b(if\s+.+\s+hadn\'t|had\s+not|without|would\s+have|wouldn\'t)\b', re.I),
        }
        self.presupposition_triggers = [
            re.compile(r'\b(stopped|quit|ceased)\b.*\b(have you|did you)\b', re.I),
            re.compile(r'\bwhy\s+(did|does|is)\b', re.I),
        ]
        self.subjectivity_triggers = re.compile(r'\b(best|worst|favorite|opinion|beautiful)\b', re.I)

    # ── Train catch-up (d = r * t) ───────────────────────────────
    def _rate_time_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "Train A leaves at Xkm/h. Train B leaves T hours later at Ykm/h. When does B catch A?"
        speeds = re.findall(r'(\d+(?:\.\d+)?)\s*(?:km/h|mph|m/s|km per hour|miles per hour)', pl)
        if len(speeds) < 2:
            # Also try "travels at X" pattern
            speeds = re.findall(r'(?:speed|rate|travels?|goes?|moving)\s+(?:at\s+)?(\d+(?:\.\d+)?)', pl)
        if len(speeds) < 2:
            return None, 0.0
        s1, s2 = float(speeds[0]), float(speeds[1])
        # Head start: time or distance
        head_start_t = re.search(r'(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|minutes?|mins?)\s*(?:later|head start|ahead|before)', pl)
        head_start_d = re.search(r'(\d+(?:\.\d+)?)\s*(?:km|miles?|meters?|m)\s*(?:ahead|head start|lead)', pl)
        if head_start_t and s2 > s1:
            t_head = float(head_start_t.group(1))
            d_head = s1 * t_head
            t_catch = d_head / (s2 - s1)
            for c in candidates:
                for cn in re.findall(r'(\d+(?:\.\d+)?)', c):
                    if abs(float(cn) - t_catch) < 0.1:
                        return c, 0.90
        elif head_start_d and s2 > s1:
            d_head = float(head_start_d.group(1))
            t_catch = d_head / (s2 - s1)
            for c in candidates:
                for cn in re.findall(r'(\d+(?:\.\d+)?)', c):
                    if abs(float(cn) - t_catch) < 0.1:
                        return c, 0.90
        # Generic d=r*t
        if re.search(r'how\s+(?:long|far|much\s+time|many\s+hours)', pl):
            rate_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:km/h|mph|m/s|per\s+hour)', pl)
            dist_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:km|miles?|meters?)\b', pl)
            time_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|minutes?)', pl)
            if rate_m and dist_m and not time_m:
                t = float(dist_m.group(1)) / float(rate_m.group(1))
                for c in candidates:
                    for cn in re.findall(r'(\d+(?:\.\d+)?)', c):
                        if abs(float(cn) - t) < 0.1:
                            return c, 0.85
            elif rate_m and time_m and not dist_m:
                d = float(rate_m.group(1)) * float(time_m.group(1))
                for c in candidates:
                    for cn in re.findall(r'(\d+(?:\.\d+)?)', c):
                        if abs(float(cn) - d) < 0.1:
                            return c, 0.85
        return None, 0.0

    # ── Temporal-causal counterfactual ────────────────────────────
    def _temporal_causal_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # "A caused B. B happened before C. C caused D. If A hadn't happened?"
        causal_pairs = re.findall(r'(\w+)\s+(?:caused|led to|triggered|produced|resulted in)\s+(\w+)', pl)
        temporal_pairs = re.findall(r'(\w+)\s+(?:happened|occurred|came)\s+(?:before|prior to)\s+(\w+)', pl)
        if not causal_pairs:
            return None, 0.0
        # Build causal graph
        caused_by = {}  # effect -> cause
        for cause, effect in causal_pairs:
            caused_by[effect] = cause
        # If A hadn't happened, what wouldn't happen?
        cf_m = re.search(r"if\s+(\w+)\s+(?:hadn't|had not|didn't|did not)\s+(?:happen|occur)", pl)
        if not cf_m:
            # Also try "without A"
            cf_m = re.search(r'without\s+(\w+)', pl)
        if cf_m:
            removed = cf_m.group(1)
            # Find all downstream effects
            blocked = {removed}
            changed = True
            while changed:
                changed = False
                for effect, cause in caused_by.items():
                    if cause in blocked and effect not in blocked:
                        blocked.add(effect)
                        changed = True
            # "Would D happen?" or "What wouldn't happen?"
            target_m = re.search(r'(?:would|will|does)\s+(\w+)\s+(?:still\s+)?(?:happen|occur)', pl)
            if target_m:
                target = target_m.group(1)
                would_happen = target not in blocked
                for c in candidates:
                    cl = c.lower()
                    if not would_happen and ('no' in cl or 'not' in cl or "wouldn't" in cl or "would not" in cl):
                        return c, 0.85
                    if would_happen and ('yes' in cl or 'still' in cl or 'would' in cl):
                        return c, 0.85
            # "What wouldn't happen?"
            what_m = re.search(r'what\s+(?:would|wouldn\'t)\s+(?:not\s+)?happen', pl)
            if what_m:
                for c in candidates:
                    cl = c.lower()
                    for b in blocked:
                        if b != removed and b in cl:
                            return c, 0.80
        return None, 0.0

    # ── Multi-hop with distractor pruning ─────────────────────────
    def _multihop_distractor_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # Chain: "A implies B. B implies C. D implies E. A is true. Is C true?"
        implies = re.findall(r'(\w+)\s+(?:implies|means|leads to|entails|causes)\s+(\w+)', pl)
        if len(implies) < 2:
            return None, 0.0
        fwd = {}
        for a, b in implies:
            fwd.setdefault(a.strip(), []).append(b.strip())
        givens = set()
        for m in re.finditer(r'(\w+)\s+is\s+(?:true|given|known|the case)', pl):
            givens.add(m.group(1).strip())
        reachable = set(givens)
        frontier = list(givens)
        while frontier:
            node = frontier.pop(0)
            for nxt in fwd.get(node, []):
                if nxt not in reachable:
                    reachable.add(nxt)
                    frontier.append(nxt)
        target_m = re.search(r'(?:is|does|will|can)\s+(\w+)\s+(?:true|hold|follow|happen)', pl)
        if target_m:
            t = target_m.group(1).strip()
            answer = t in reachable
            for c in candidates:
                cl = c.lower()
                if answer and ('yes' in cl or 'true' in cl or t in cl):
                    return c, 0.85
                if not answer and ('no' in cl or 'false' in cl):
                    return c, 0.85
        return None, 0.0

    # ── Chained conditional solver ────────────────────────────────
    def _chained_conditional_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        chains = re.findall(r'if\s+(\w+(?:\s+\w+)?)\s*(?:,\s*)?then\s+(\w+(?:\s+\w+)?)', pl)
        if len(chains) < 2:
            return None, 0.0
        fwd = {}
        for ante, cons in chains:
            fwd[ante.strip()] = cons.strip()
        givens = set()
        for m in re.finditer(r'(\w+(?:\s+\w+)?)\s+is\s+true', pl):
            givens.add(m.group(1).strip())
        derived = set(givens)
        changed = True
        while changed:
            changed = False
            for ante, cons in fwd.items():
                if ante in derived and cons not in derived:
                    derived.add(cons)
                    changed = True
        for c in candidates:
            cl = c.lower()
            for d in derived - givens:
                if d in cl or 'true' in cl or 'yes' in cl:
                    return c, 0.80
        return None, 0.0

    # ── Compositional chain: logic + arithmetic + causal ──────────
    def _composite_chain_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        # Detect heterogeneous chain: conditional + numeric + causal
        has_cond = bool(re.search(r'\bif\b.*\bthen\b', pl))
        has_nums = len(re.findall(r'\d+', pl)) >= 2
        has_causal = bool(self.patterns['causal'].search(pl))
        if not (has_cond and has_nums) and not (has_nums and has_causal):
            return None, 0.0
        # Step 1: resolve conditionals
        cond_results = {}
        conds = re.findall(r'if\s+(.+?)\s*(?:,\s*)?then\s+(.+?)(?:\.|$)', pl)
        for ante, cons in conds:
            # Check if antecedent is stated as true
            ante_clean = ante.strip()
            if re.search(re.escape(ante_clean) + r'\s+is\s+true', pl) or \
               re.search(re.escape(ante_clean) + r'\b', pl):
                cond_results[cons.strip()] = True
        # Step 2: extract and compute arithmetic
        nums = [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)', pl)]
        computed = set()
        if len(nums) >= 2:
            for i in range(len(nums)):
                for j in range(len(nums)):
                    if i == j:
                        continue
                    computed.update([nums[i] + nums[j], nums[i] - nums[j],
                                    nums[i] * nums[j]])
                    if nums[j] != 0:
                        computed.add(nums[i] / nums[j])
        # Step 3: match candidates
        best, best_score = None, 0.0
        for c in candidates:
            cl = c.lower()
            score = 0.0
            # Check numeric match
            for cn in re.findall(r'(-?\d+(?:\.\d+)?)', c):
                cv = float(cn)
                if any(abs(cv - r) < 0.01 for r in computed):
                    score += 0.5
            # Check conditional conclusion match
            for concl, val in cond_results.items():
                if concl in cl:
                    score += 0.3
            if score > best_score:
                best, best_score = c, score
        if best and best_score >= 0.5:
            return best, min(best_score, 0.85)
        return None, 0.0

    # ── Bat-and-ball / algebraic word problem ─────────────────────
    def _bat_ball_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        m = re.search(r'(\w+)\s+and\s+(?:a\s+)?(\w+)\s+(?:cost|total)\s+\$?([\d.]+)', pl)
        m2 = re.search(r'(\w+)\s+costs?\s+\$?([\d.]+)\s+more\s+than\s+(?:the\s+)?(\w+)', pl)
        if m and m2:
            total = float(m.group(3))
            diff = float(m2.group(2))
            y_val = (total - diff) / 2.0
            x_val = total - y_val
            for c in candidates:
                if f"{y_val:g}" in c or f"{x_val:g}" in c:
                    return c, 0.90
        return None, 0.0

    # ── Transitivity ──────────────────────────────────────────────
    def _transitivity_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        relations = re.findall(r'(\w+)\s+is\s+(taller|shorter|heavier|lighter|older|younger|faster|slower|bigger|smaller)\s+than\s+(\w+)', pl)
        if len(relations) < 2:
            return None, 0.0
        greater_rels = ('taller', 'heavier', 'older', 'faster', 'bigger')
        greater = []
        for a, rel, b in relations:
            if rel in greater_rels:
                greater.append((a, b))
            else:
                greater.append((b, a))
        entities = set()
        for a, b in greater:
            entities.update([a, b])
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
        sup_m = re.search(r'who\s+is\s+(?:the\s+)?(tallest|shortest|heaviest|lightest|oldest|youngest|fastest|slowest|biggest|smallest)', pl)
        if sup_m:
            find_max = sup_m.group(1) in ('tallest', 'heaviest', 'oldest', 'fastest', 'biggest')
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

    # ── Modus tollens ─────────────────────────────────────────────
    def _modus_tollens_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        cond = re.findall(r'if\s+(.+?)\s*(?:,\s*)?then\s+(.+?)\.', pl)
        if not cond:
            return None, 0.0
        for ante, cons in cond:
            cons_c = cons.strip()
            if re.search(re.escape(cons_c) + r'\s+is\s+(?:false|not true)', pl) or \
               re.search(r'not\s+' + re.escape(cons_c), pl):
                for c in candidates:
                    cl = c.lower()
                    if 'false' in cl or 'not' in cl or 'no' in cl:
                        return c, 0.80
        return None, 0.0

    # ── Negation scope ────────────────────────────────────────────
    def _negation_scope_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        pl = prompt.lower()
        if re.search(r'not all\s+\w+\s+are\s+\w+', pl):
            for c in candidates:
                cl = c.lower()
                if 'some' in cl or 'at least one' in cl or 'not necessarily' in cl:
                    return c, 0.80
        return None, 0.0

    # ── Numeric arithmetic fallback ───────────────────────────────
    def _numeric_solve(self, prompt: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        nums = [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)', prompt)]
        if len(nums) < 2:
            return None, 0.0
        results = set()
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j:
                    continue
                results.update([nums[i] + nums[j], nums[i] - nums[j], nums[i] * nums[j]])
                if nums[j] != 0:
                    results.add(nums[i] / nums[j])
        for c in candidates:
            for cn in re.findall(r'(-?\d+(?:\.\d+)?)', c):
                cv = float(cn)
                if any(abs(cv - r) < 0.01 for r in results):
                    return c, 0.60
        return None, 0.0

    # ── NCD tiebreaker ────────────────────────────────────────────
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
            self._rate_time_solve, self._temporal_causal_solve,
            self._multihop_distractor_solve, self._chained_conditional_solve,
            self._composite_chain_solve, self._bat_ball_solve,
            self._transitivity_solve, self._modus_tollens_solve,
            self._negation_scope_solve, self._numeric_solve,
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
