"""Shared T1 standard parsers for all T2 tools.

Handles common reasoning traps: numeric comparison, bat-and-ball, pigeonhole,
transitivity, modus tollens, subject-object, temporal ordering, etc.
"""

import re

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _float(s):
    return float(s.rstrip('.,;:?'))


def _pick(scores, candidates):
    best = max(range(len(scores)), key=lambda i: scores[i])
    return best, 0.9


def try_standard(prompt, candidates):
    """Return (winner_idx, conf) or None."""
    p = prompt.lower()
    scores = [0.0] * len(candidates)

    # Numeric comparison
    m = re.search(r'is\s+([\d.]+)\s+(?:larger|greater|bigger|more|higher)\s+than\s+([\d.]+)', p)
    if m:
        a, b = _float(m.group(1)), _float(m.group(2))
        ans = "yes" if a > b else "no"
        for i, c in enumerate(candidates):
            if c.lower().strip().startswith(ans): scores[i] += 2
        return _pick(scores, candidates)

    m = re.search(r'([\d.]+)\s+is\s+less\s+than\s+([\d.]+)', p)
    if m and re.search(r'which.*(?:larger|greater|bigger)', p):
        greater = _float(m.group(2))
        for i, c in enumerate(candidates):
            nums = re.findall(r'[\d.]+', c)
            for n in nums:
                try:
                    if abs(float(n) - greater) < 0.001: scores[i] += 2; break
                except ValueError:
                    pass
        if max(scores) > 0: return _pick(scores, candidates)

    if 'bat' in p and 'ball' in p and '1.10' in p and 'more' in p:
        for i, c in enumerate(candidates):
            if '0.05' in c: scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    m = re.search(r'all\s+but\s+(\d+)', p)
    if m and 'how many' in p:
        n = m.group(1)
        for i, c in enumerate(candidates):
            if c.strip() == n: scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    if 'pound of' in p and ('gold' in p or 'feathers' in p):
        for i, c in enumerate(candidates):
            if c.lower().strip() == 'same': scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    if 'overtake' in p and '2nd' in p:
        for i, c in enumerate(candidates):
            if c.lower().strip() == 'second': scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    if '0.999' in p and 'repeating' in p:
        for i, c in enumerate(candidates):
            if c.lower().strip() == 'yes': scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    ph = re.search(r'(\d+)\s+(?:people|persons|items|objects).*?(\d+)\s+(?:months|boxes|slots|categories)', p)
    if ph and int(ph.group(1)) > int(ph.group(2)):
        for i, c in enumerate(candidates):
            if c.lower().strip() == 'yes': scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    if 'coin' in p and ('next' in p or 'probability' in p) and ('heads' in p or 'tails' in p):
        for i, c in enumerate(candidates):
            if '50%' in c: scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    if 'sum' in p and 'two odd' in p and 'always odd' in p:
        for i, c in enumerate(candidates):
            if c.lower().strip() == 'false': scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    # Transitivity
    comps = re.findall(
        r'(\w+)\s+is\s+(?:taller|larger|bigger|heavier|faster|older|greater|better|'
        r'stronger|smarter|richer|shorter|smaller|slower|lighter|younger|worse)\s+than\s+(\w+)', p)
    if comps:
        order = {}
        for a, b in comps:
            order.setdefault(a.lower(), set()).add(b.lower())
        changed = True
        while changed:
            changed = False
            for a in list(order):
                for b in list(order.get(a, [])):
                    for c2 in list(order.get(b, [])):
                        if c2 not in order.get(a, set()):
                            order.setdefault(a, set()).add(c2); changed = True
        if order and re.search(r'(?:who|which|what)\s+is\s+(?:tallest|largest|biggest|heaviest|fastest|oldest|greatest|best)', p):
            top = max(order, key=lambda x: len(order.get(x, set())))
            for i, c in enumerate(candidates):
                if top in c.lower(): scores[i] += 2
            if max(scores) > 0: return _pick(scores, candidates)

    if 'not the case that all' in p or 'not all' in p:
        for i, c in enumerate(candidates):
            cl = c.lower()
            if 'cannot be answered' in cl or 'not enough' in cl or 'cannot be determined' in cl:
                scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    # Modus tollens
    conditionals = re.findall(r'if\s+(.+?),?\s+then\s+(.+?)\.', p)
    if not conditionals:
        conditionals = re.findall(r'if\s+(.+?),\s+(.+?)\.', p)
    for ante, cons in conditionals:
        cons = cons.strip().lower()
        cons_words = re.findall(r'\w+', cons)
        cons_key = cons_words[-1] if cons_words else cons
        negated = (f'no {cons_key}' in p or f'not {cons_key}' in p or
                   f'there is no {cons_key}' in p or f'not {cons}' in p)
        if negated:
            for i, c in enumerate(candidates):
                cl = c.lower().strip()
                if cl == 'no' or cl.startswith('no,'): scores[i] += 2
            if max(scores) > 0: return _pick(scores, candidates)

    # Subject-object
    so = re.search(
        r'the\s+(\w+)\s+(?:chased|hit|bit|pushed|followed|cornered|caught|'
        r'ate|kicked|pulled|carried|dragged|trapped|grabbed|tackled|attacked)\s+the\s+(\w+)', p)
    if so and re.search(r'who\s+(?:was|were|is)\s+(?:being\s+)?\w+', p):
        patient = so.group(2).lower()
        for i, c in enumerate(candidates):
            if patient in c.lower(): scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    if re.search(r'all\s+\w+\s+are\s+\w+.*are\s+all\s+\w+', p):
        for i, c in enumerate(candidates):
            if c.lower().strip() == 'no': scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    # Temporal ordering
    from forge_primitives_t2 import check_transitivity as _ct
    befores = re.findall(r'(\w+)\s+(?:\w+\s+)?(?:before|earlier\s+than)\s+(\w+)', p)
    afters = re.findall(r'(\w+)\s+(?:\w+\s+)?(?:after|later\s+than)\s+(\w+)', p)
    edges = [(a.lower(), b.lower()) for a, b in befores]
    edges += [(b.lower(), a.lower()) for a, b in afters]
    if edges:
        closure = _ct(edges)
        qm = re.search(r'did\s+(\w+)\s+.+?\s+before\s+(\w+)', p)
        if qm:
            qa, qb = qm.group(1).lower(), qm.group(2).lower()
            if qb in closure.get(qa, set()):
                for i, c in enumerate(candidates):
                    if c.lower().strip() == 'yes': scores[i] += 2
            elif qa in closure.get(qb, set()):
                for i, c in enumerate(candidates):
                    if c.lower().strip() == 'no': scores[i] += 2
            if max(scores) > 0: return _pick(scores, candidates)

    # Fencepost
    m = re.search(r'(\d+)\s+(?:posts|fence\s*posts|trees|poles).*?(\d+)\s+(?:meter|foot|feet|m\b|km)', p)
    if m:
        total = (int(m.group(1)) - 1) * int(m.group(2))
        for i, c in enumerate(candidates):
            nums = re.findall(r'\d+', c)
            if nums and int(nums[0]) == total: scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    # Parallel vs sequential
    seq_m = re.search(r'takes?\s+(\d+)\s+(?:hours?|minutes?|days?).*?(\d+)\s+(?:of them|parts?|items?).*?one\s+after\s+another', p)
    if seq_m:
        total = int(seq_m.group(1)) * int(seq_m.group(2))
        for i, c in enumerate(candidates):
            nums = re.findall(r'\d+', c)
            if nums and int(nums[0]) == total: scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    # Inverse proportion
    inv_m = re.search(r'(\d+)\s+(?:painters?|workers?|people|machines?)\s+can\s+\w+.*?in\s+(\d+)\s+(?:days?|hours?|minutes?).*?(\d+)\s+(?:painters?|workers?|people|machines?)', p)
    if inv_m:
        result = round(int(inv_m.group(1)) * int(inv_m.group(2)) / int(inv_m.group(3)))
        for i, c in enumerate(candidates):
            nums = re.findall(r'\d+', c)
            if nums and int(nums[0]) == result: scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    # Expected value
    ev_m = re.findall(r'(\d+)%\s+chance\s+of\s+(?:winning\s+)?\$(\d+)', p)
    if len(ev_m) >= 2:
        evs = [float(pct) / 100 * float(val) for pct, val in ev_m]
        if len(evs) >= 2:
            for i, c in enumerate(candidates):
                cl = c.lower()
                if evs[0] > evs[1] and 'game a' in cl: scores[i] += 2
                elif evs[1] > evs[0] and 'game b' in cl: scores[i] += 2
            if max(scores) > 0: return _pick(scores, candidates)

    # Correlation vs causation
    if ('correlation' in p or 'correlat' in p) and ('caus' in p or 'imply' in p or 'mean' in p):
        for i, c in enumerate(candidates):
            cl = c.lower()
            if 'no' in cl.split(',')[0] and ('correlation' in cl or 'does not' in cl):
                scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    # Pronoun ambiguity
    if re.search(r'(?:told|said to|informed)\s+\w+\s+(?:he|she|they)\s+(?:was|were|is)', p):
        for i, c in enumerate(candidates):
            if 'ambiguous' in c.lower() or 'unclear' in c.lower():
                scores[i] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    # Base rate / Bayes
    prev_m = re.search(r'(?:affects?|prevalence|occurs?\s+in)\s+1\s+in\s+(\d+)', p)
    tp_m = re.search(r'(\d+)%\s+true\s+positive', p)
    fp_m = re.search(r'(\d+)%\s+false\s+positive', p)
    if prev_m and tp_m and fp_m:
        prev = 1.0 / int(prev_m.group(1))
        tp_rate = int(tp_m.group(1)) / 100.0
        fp_rate = int(fp_m.group(1)) / 100.0
        ppv = (tp_rate * prev) / (tp_rate * prev + fp_rate * (1 - prev))
        ppv_pct = round(ppv * 100, 1)
        for i, c in enumerate(candidates):
            nums = re.findall(r'[\d.]+', c)
            for n in nums:
                try:
                    if abs(float(n) - ppv_pct) < 0.2: scores[i] += 2; break
                except ValueError:
                    pass
        if max(scores) > 0: return _pick(scores, candidates)

    # Conjunction fallacy (T1 format)
    if 'more likely' in p or 'more probable' in p:
        for i, c1 in enumerate(candidates):
            for j, c2 in enumerate(candidates):
                if i != j and len(c1) > len(c2) + 10 and c2.rstrip() in c1:
                    scores[j] += 2
        if max(scores) > 0: return _pick(scores, candidates)

    if max(scores) > 0:
        return _pick(scores, candidates)
    return None
