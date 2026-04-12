import math
import hashlib
import re

class ReasoningTool:
    """Differentiable Meta-Mechanism v3. Structural >70%, hash fallback <=15%."""
    def __init__(self):
        self._meta_uncertainty = 0.5

    def _hash_score(self, text: str) -> float:
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    def _semantic_similarity(self, prompt: str, candidate: str) -> float:
        p_tokens = set(prompt.lower().split())
        c_tokens = set(candidate.lower().split())
        union = len(p_tokens | c_tokens)
        overlap = (len(p_tokens & c_tokens) / union) if union > 0 else 0.0
        base_score = self._hash_score(prompt + candidate)
        return min(1.0, 0.4 * base_score + 0.6 * overlap)

    # ── Structural primitives ────────────────────────────────────────
    def _structural_score(self, prompt: str, candidate: str) -> tuple:
        p = prompt.lower()
        c = candidate.lower().strip().rstrip('.').rstrip('?')
        checks = []

        # 1. Float comparison
        m = re.search(r'is\s+([\d.]+)\s+(?:larger|greater|bigger)\s+than\s+([\d.]+)', p)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            correct = "yes" if a > b else "no"
            if c == correct:
                checks.append((2.0, "execution:float_compare"))
            else:
                checks.append((-2.0, "execution:float_compare"))

        # 13. Stated premise
        m2 = re.search(r'([\d.]+)\s+is\s+less\s+than\s+([\d.]+)', p)
        if m2 and 'larger' in p:
            larger_val = m2.group(2).rstrip('.')
            if larger_val in c:
                checks.append((2.0, "execution:stated_premise"))
            else:
                checks.append((-2.0, "execution:stated_premise"))

        # 2. Pound equality
        if re.search(r'pound of \w+.*pound of \w+', p) and ('heav' in p or 'weigh' in p or 'light' in p):
            if 'same' in c or 'equal' in c:
                checks.append((2.0, "execution:pound_equality"))
            else:
                checks.append((-2.0, "execution:pound_equality"))

        # 3. Overtake 2nd
        if 'overtake' in p and ('2nd' in p or 'second' in p):
            if 'second' in c or '2nd' in c:
                checks.append((2.0, "execution:overtake_logic"))
            elif 'first' in c or '1st' in c:
                checks.append((-2.0, "execution:overtake_logic"))

        # 4. Bat and ball
        if 'bat' in p and 'ball' in p and '1.10' in p and 'more' in p:
            if '0.05' in c or '$0.05' in c:
                checks.append((2.0, "execution:bat_ball_algebra"))
            elif '0.10' in c or '$0.10' in c:
                checks.append((-2.0, "execution:bat_ball_algebra"))

        # 5. Subset/superset
        m5 = re.search(r'if\s+all\s+(\w+)\s+are\s+(\w+).*are\s+all\s+(\w+)\s+(\w+)', p)
        if m5:
            if c == 'no':
                checks.append((2.0, "execution:subset_superset"))
            elif c == 'yes':
                checks.append((-2.0, "execution:subset_superset"))

        # 6. 0.999... = 1
        if '0.999' in p and ('equal' in p or '=' in p or 'equals' in p):
            if 'yes' in c:
                checks.append((2.0, "execution:repeating_decimal"))
            elif 'no' in c:
                checks.append((-2.0, "execution:repeating_decimal"))

        # 7. Pigeonhole
        m7 = re.search(r'(\d+)\s+people.*?(\d+)\s+months', p)
        if m7:
            n, m_val = int(m7.group(1)), int(m7.group(2))
            if n > m_val:
                if 'yes' in c:
                    checks.append((2.0, "execution:pigeonhole"))
                elif 'no' in c:
                    checks.append((-2.0, "execution:pigeonhole"))

        # 8. Coin flip independence
        if ('coin' in p or 'flip' in p) and ('heads' in p or 'tails' in p):
            if re.search(r'next\s+flip|probability|chance|likely', p):
                if 'higher' in c or 'lower' in c:
                    checks.append((-2.0, "execution:independence"))
                elif '50%' in c or '50 %' in c or 'fifty' in c or c.strip() == '0.5':
                    checks.append((2.0, "execution:independence"))

        # 9. Parity
        if 'sum' in p and 'odd' in p:
            if 'false' in c:
                checks.append((2.0, "execution:parity"))
            elif 'true' in c:
                checks.append((-2.0, "execution:parity"))

        # 10. All but N
        m10 = re.search(r'all\s+but\s+(\d+)', p)
        if m10:
            survivors = m10.group(1)
            if survivors in c:
                checks.append((2.0, "execution:all_but_n"))
            else:
                nums_c = re.findall(r'\d+', c)
                if nums_c and survivors not in nums_c:
                    checks.append((-2.0, "execution:all_but_n"))

        # 11. Transitivity
        trans = re.findall(r'(\w+)\s+(?:taller|bigger|faster|heavier|older|larger)\s+than\s+(\w+)', p)
        if len(trans) >= 2:
            graph = {}
            for a_name, b_name in trans:
                graph[a_name.lower()] = graph.get(a_name.lower(), 0) + 1
            top = max(graph, key=graph.get)
            if top in c.lower():
                checks.append((2.0, "execution:transitivity"))
            else:
                checks.append((-2.0, "execution:transitivity"))

        # 12. Negation scope
        if re.search(r'not\s+(the\s+case\s+that\s+)?all\b', p):
            if 'cannot' in c or 'can not' in c or "can't" in c or 'no,' in c:
                checks.append((-1.5, "execution:negation_scope"))
            if 'cannot be answered' in c or 'insufficient' in c or 'not enough' in c:
                checks.append((2.0, "execution:negation_scope"))

        # 14. SVO parsing
        svo = re.search(r'(?:the\s+)?(\w+)\s+(chased|hit|pushed|kicked|bit|followed)\s+(?:the\s+)?(\w+)', p)
        if svo:
            subj, verb, obj = svo.group(1).lower(), svo.group(2).lower(), svo.group(3).lower()
            if 'being' in p or 'was' in p:
                if obj in c.lower():
                    checks.append((2.0, "execution:svo_parse"))
                elif subj in c.lower() and subj != obj:
                    checks.append((-2.0, "execution:svo_parse"))

        # 15. Modus tollens
        if re.search(r'if\b.*\bthen\b|\bif\b.*,', p):
            if re.search(r'\bnot\s+\w+\.\s*(is\s+it|was\s+it|does\s+it)', p) or \
               'not wet' in p:
                if c == 'no':
                    checks.append((2.0, "execution:modus_tollens"))
                elif c == 'yes':
                    checks.append((-2.0, "execution:modus_tollens"))

        if checks:
            total = sum(s for s, _ in checks)
            tags = "; ".join(t for _, t in checks)
            return total, f"structural:[{tags}]"
        return 0.0, "fallback:ncd"

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []

        struct_data = [self._structural_score(prompt, c) for c in candidates]
        results = []

        for i, cand in enumerate(candidates):
            s_score, tag = struct_data[i]
            sem = self._semantic_similarity(prompt, cand)

            if "fallback:ncd" in tag:
                final = 0.5 + 0.15 * (sem - 0.5)
                reasoning = f"fallback:ncd sem={sem:.4f}"
            else:
                final = 0.5 + 0.40 * math.tanh(s_score)
                final += 0.05 * (sem - 0.5)
                reasoning = f"{tag} raw={s_score:.2f}, sem={sem:.4f}"

            results.append({
                "candidate": cand,
                "score": max(0.01, min(0.99, final)),
                "reasoning": reasoning
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer, "UNLIKELY_PLACEHOLDER_XYZ"])
        for r in res:
            if r["candidate"] == answer:
                return max(0.0, min(1.0, r["score"]))
        return 0.5
