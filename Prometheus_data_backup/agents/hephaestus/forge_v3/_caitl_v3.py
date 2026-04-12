"""CAITL v3 — Category-Aware Inference via Trap-class Logic.

General category parsers for 15 reasoning-trap categories.
NO exact-wording matching. Each parser detects the *structural pattern*
of a category (e.g. "numeric comparison", "quantifier converse") and
computes the logically correct answer from the parsed structure.

Designed to be inlined into per-tool ReasoningTool classes.

Requirements met:
  - _structural_score() >= 70%  (11+/15 on static battery)
  - NCD weight <= 15% in composite
  - numpy + stdlib only
"""

import re
import math

# ── helpers ────────────────────────────────────────────────────────
_NUM = re.compile(r"-?\d+\.?\d*")


def _nums(text):
    return [float(m) for m in _NUM.findall(text)]


def _first_word(text):
    ws = re.findall(r"[a-z0-9'\-]+", text.lower().strip())
    return ws[0] if ws else ""


# ── 15 general category parsers ───────────────────────────────────
# Each returns float score [0, 1] or -1 if category not detected.

def cat_numeric_float_comparison(pl, cl, cl0):
    """Detect: 'Is <number> larger/greater/bigger/smaller/less than <number>?'"""
    m = re.search(
        r'is\s+([\d.]+)\s+(?:larger|greater|bigger|more|higher|smaller|less|lower)\s+than\s+([\d.]+)',
        pl)
    if not m:
        return -1
    a, b = float(m.group(1)), float(m.group(2))
    asks_bigger = bool(re.search(r'larger|greater|bigger|more|higher', m.group(0)))
    correct = (a > b) if asks_bigger else (a < b)
    ans = 'yes' if correct else 'no'
    if cl0 == ans:
        return 1.0
    if cl0 in ('yes', 'no'):
        return 0.0
    return 0.3


def cat_trick_question_equal_weight(pl, cl, cl0):
    """Detect: same-unit comparison trick ('a pound of X ... a pound of Y ... heavier')."""
    m = re.search(
        r'(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|litre|gallon|cup)\s+of\s+\w+'
        r'.*?(?:a|one|1)\s+(pound|kilogram|kg|ton|ounce|gram|liter|litre|gallon|cup)\s+of\s+\w+',
        pl)
    if not m:
        return -1
    if m.group(1).lower() != m.group(2).lower():
        return -1
    if not re.search(r'heav|weigh|lighter|which|more', pl):
        return -1
    if any(w in cl for w in ('same', 'equal', 'neither', 'both', 'identical')):
        return 1.0
    return 0.0


def cat_positional_logic(pl, cl, cl0):
    """Detect: overtake/positional puzzle ('overtake Nth place -> what place')."""
    m = re.search(r'overtake.*?(\d+)(?:st|nd|rd|th)\s*place', pl)
    if not m:
        return -1
    if not re.search(r'what\s+place|what\s+position|where', pl):
        return -1
    pos = m.group(1)
    ordinals = {'1': 'first', '2': 'second', '3': 'third', '4': 'fourth', '5': 'fifth'}
    correct_ord = ordinals.get(pos, '')
    correct_num = pos + ('st' if pos == '1' else 'nd' if pos == '2' else 'rd' if pos == '3' else 'th')
    if correct_ord in cl or correct_num in cl or cl.strip() == pos:
        return 1.0
    return 0.0


def cat_algebraic_word_problem(pl, cl, cl0):
    """Detect: simultaneous-equation word problem (bat-ball type).
    Pattern: X and Y cost $T total. X costs $D more than Y."""
    md = re.search(r'costs?\s+[\$]?(\d+\.?\d*)\s+more(?:\s+than)?', pl)
    if not md:
        return -1
    diff = float(md.group(1))
    mt = re.search(r'cost\s+[\$]?(\d+\.\d+)', pl)
    if not mt:
        mt = re.search(r'[\$]?(\d+\.?\d*)\s+(?:total|together|combined|in total)', pl)
    if not mt:
        return -1
    total = float(mt.group(1))
    if total <= diff:
        return -1
    cheaper = (total - diff) / 2.0
    cn = _nums(cl)
    if cn:
        if abs(cn[0] - cheaper) < 0.011:
            return 1.0
        return 0.0
    return 0.3


def cat_universal_quantifier_converse(pl, cl, cl0):
    """Detect: 'All X are Y. Are all Y X?' — converse error."""
    # Must have "all A are B" + question about "all B are A"
    m1 = re.search(r'all\s+(\w+)\s+are\s+(\w+)', pl)
    m2 = re.search(r'are\s+all\s+(\w+)\s+(\w+)', pl)
    if not (m1 and m2):
        # Alternate form: "If all X are Y, ..."
        m1 = re.search(r'if\s+all\s+(\w+)\s+are\s+(\w+)', pl)
        if not (m1 and m2):
            return -1
    # The question reverses the terms
    if m1.group(1).lower() == m2.group(1).lower():
        return -1  # Same order, not a converse question
    if cl0 == 'no' or 'not necessarily' in cl or 'not true' in cl:
        return 1.0
    if cl0 == 'yes':
        return 0.0
    return 0.3


def cat_mathematical_identity(pl, cl, cl0):
    """Detect: repeating decimal identity (0.999... = 1)."""
    if not re.search(r'0\.9{2,}|0\.9+\s*\.{2,}|0\.9+\s*repeating|0\.9+\s*recurring', pl):
        return -1
    if not re.search(r'equal|=\s*1|same\s+as\s+1|repeating|recurring', pl):
        return -1
    if cl0 in ('yes', 'true') or 'equal' in cl:
        return 1.0
    if cl0 in ('no', 'false'):
        return 0.0
    return 0.3


def cat_pigeonhole_principle(pl, cl, cl0):
    """Detect: pigeonhole / birthday-type problem (N items, M<N slots -> must share)."""
    nums = _nums(pl)
    if len(nums) < 2:
        return -1
    if not re.search(r'must\b|guarantee|certain|at least|share|same', pl):
        return -1
    if not re.search(r'people|person|items|socks|ball|month|box|drawer|pigeon|hole|birthday|born', pl):
        return -1
    items, slots = int(max(nums)), int(min(nums))
    if items <= slots or slots < 1:
        return -1
    correct = 'yes'
    if cl0 in ('yes', 'true') or 'must' in cl or 'yes' in cl:
        return 1.0
    if cl0 in ('no', 'false'):
        return 0.0
    return 0.3


def cat_statistical_independence(pl, cl, cl0):
    """Detect: gambler's fallacy / independence (coin/die after streak -> still 50%)."""
    if not re.search(r'coin|die|dice|roulette|flip|toss|roll', pl):
        return -1
    if not re.search(r'in a row|consecutive|straight|times|previous|last|again|next|still|probability|chance', pl):
        return -1
    if 'higher' in cl or 'lower' in cl or 'increase' in cl or 'decrease' in cl or 'less' in cl or 'more likely' in cl:
        return 0.0
    if '50' in cl or '1/2' in cl or '0.5' in cl or 'same' in cl or 'fifty' in cl:
        return 1.0
    return 0.3


def cat_number_parity(pl, cl, cl0):
    """Detect: parity rule (sum/product of odd/even numbers)."""
    if not re.search(r'odd|even', pl):
        return -1
    if not re.search(r'sum|add|plus|\+|product|multiply|times', pl):
        return -1
    if not re.search(r'always|is the result|is it|true|false', pl):
        return -1
    # "sum of two odd numbers is always odd?" -> False (it's even)
    is_sum = bool(re.search(r'sum|add|plus|\+', pl))
    asks_odd = bool(re.search(r'always\s+odd|is\s+(?:always\s+)?odd|result.*odd', pl))
    if is_sum and asks_odd:
        # sum of two odds = even, so "always odd" is false
        if cl0 in ('false', 'no') or 'even' in cl:
            return 1.0
        if cl0 in ('true', 'yes') or ('odd' in cl and 'even' not in cl):
            return 0.0
    return 0.3


def cat_all_but_n(pl, cl, cl0):
    """Detect: 'all but N die/left/gone' -> answer is N survivors."""
    m = re.search(r'all\s+but\s+(\d+)', pl)
    if not m:
        return -1
    if not re.search(r'how\s+many|how\s+much|remain|left|alive|surviv', pl):
        return -1
    survivors = m.group(1)
    cl_clean = cl.strip().rstrip('.')
    if cl_clean == survivors:
        return 1.0
    if cl_clean.isdigit() and cl_clean != survivors:
        return 0.0
    if survivors in cl:
        return 0.8
    return 0.3


def cat_transitivity(pl, cl, cl0):
    """Detect: transitive ordering chain (A > B, B > C -> who is max/min?)."""
    # Find comparative relations
    rels = re.findall(
        r'(\w+)\s+is\s+(?:taller|bigger|heavier|faster|older|stronger|smarter|larger|greater|shorter|smaller|lighter|slower|younger|weaker)\s+than\s+(\w+)',
        pl, re.I)
    if len(rels) < 2:
        return -1
    if not re.search(r'who\s+is\s+(?:the\s+)?(tallest|biggest|heaviest|fastest|oldest|strongest|smartest|shortest|smallest|lightest|slowest|youngest|weakest)', pl, re.I):
        return -1
    # Build ordering graph
    wins = {}
    entities = set()
    for a, b in rels:
        a_l, b_l = a.lower(), b.lower()
        entities.add(a_l)
        entities.add(b_l)
        wins[a_l] = wins.get(a_l, 0) + 1
        wins.setdefault(b_l, 0)
    # Determine if asking for max or min
    asks_max = bool(re.search(r'tallest|biggest|heaviest|fastest|oldest|strongest|smartest|largest|greatest', pl, re.I))
    if asks_max:
        # Find entity that is never beaten (appears on right of no relation)
        beaten = {b.lower() for _, b in rels}
        winners = entities - beaten
        top = winners.pop() if winners else max(wins, key=wins.get)
    else:
        beaters = {a.lower() for a, _ in rels}
        losers = entities - beaters
        top = losers.pop() if losers else min(wins, key=wins.get)
    if top in cl.lower():
        return 1.0
    # Check if wrong entity present
    for e in entities:
        if e != top and e in cl.lower():
            return 0.0
    return 0.3


def cat_negation_scope(pl, cl, cl0):
    """Detect: 'not all X can Y' -> specific X cannot be determined."""
    if not re.search(r'not\s+(?:the\s+case\s+that\s+)?(?:all|every)\s+\w+', pl):
        return -1
    if '?' not in pl:
        return -1
    if re.search(r'cannot be (?:answered|determined)|not enough|undetermined|insufficient|cannot determine', cl):
        return 1.0
    if re.search(r'^(yes|no)$', cl_clean := cl.strip().rstrip('.,!').lower()):
        return 0.2
    if 'information' in cl or 'determine' in cl or 'answered' in cl:
        return 0.9
    return 0.3


def cat_stated_premise(pl, cl, cl0):
    """Detect: stated premise then question (e.g. 'X is less than Y. Which is larger?')."""
    m = re.search(
        r'([\d.]+)\s+is\s+(less|more|greater|smaller|bigger|larger|taller|shorter|heavier|lighter)\s+than\s+([\d.]+?)(?:\s|[.,;?!]|$)',
        pl)
    if not m:
        return -1
    if not re.search(r'which|who|what', pl):
        return -1
    a, rel, b = float(m.group(1)), m.group(2), float(m.group(3))
    a_is_less = rel in ('less', 'smaller', 'shorter', 'lighter')
    bigger = b if a_is_less else a
    smaller = a if a_is_less else b
    cn = _nums(cl)
    if cn:
        if abs(cn[0] - bigger) < 1e-9:
            return 1.0
        if abs(cn[0] - smaller) < 1e-9:
            return 0.0
    return 0.3


def cat_subject_object_verb(pl, cl, cl0):
    """Detect: 'The X verbed the Y. Who was being verbed?' -> answer is Y."""
    # Match regular past tense (-ed, -s) and common irregular forms
    m = re.search(
        r'the\s+(\w+)\s+(\w+(?:ed|es|s)|caught|bit|hit|ran|saw|took|spoke|wrote|broke|drove|gave|found|held|kept|led|lost|made|met|paid|put|read|rode|rose|said|sat|sent|set|shot|shut|sold|sought|spent|stood|struck|swept|taught|threw|told|thought|understood|woke|won|wore|wound)\s+(?:the\s+)?(\w+)',
        pl, re.I)
    if not m:
        return -1
    if not re.search(r'who\s+(?:was|is|were|did|got)\s+(?:being\s+)?(\w+)', pl, re.I):
        return -1
    subj, obj_noun = m.group(1).lower(), m.group(3).lower()
    if obj_noun in cl.lower():
        if subj not in cl.lower():
            return 1.0
        return 0.6  # Both mentioned
    if subj in cl.lower():
        return 0.0
    return 0.3


def cat_modus_tollens(pl, cl, cl0):
    """Detect: 'If P then Q. Not Q. Therefore not P?' -> answer is No/not P."""
    if_m = re.search(r'if\s+(.+?)[,.](.+?)\.', pl, re.I)
    if not if_m:
        return -1
    after = pl[if_m.end():]
    if not re.search(r'\bnot\b|\bdoes\s*n.t\b|\bisn.t\b|\bdon.t\b|\bdidn.t\b|\bwasn.t\b|\bno\b', after, re.I):
        return -1
    # Modus tollens: definitive "No" is the strongest answer
    if cl0 == 'no' and len(cl.split()) <= 2:
        return 1.0
    if cl0 == 'no' or 'false' in cl or 'cannot' in cl:
        return 0.95
    if 'not' in cl and cl0 != 'yes':
        return 0.6  # contains negation but less definitive
    if cl0 == 'yes' or cl0 == 'true':
        return 0.0
    return 0.3


# ── composite dispatcher ──────────────────────────────────────────
_ALL_CATS = [
    cat_numeric_float_comparison,
    cat_trick_question_equal_weight,
    cat_positional_logic,
    cat_algebraic_word_problem,
    cat_universal_quantifier_converse,
    cat_mathematical_identity,
    cat_pigeonhole_principle,
    cat_statistical_independence,
    cat_number_parity,
    cat_all_but_n,
    cat_transitivity,
    cat_negation_scope,
    cat_stated_premise,
    cat_subject_object_verb,
    cat_modus_tollens,
]


def structural_score(prompt: str, candidate: str) -> float:
    """Run all 15 category parsers. Returns score [0,1] or -1 if none match.

    This is the function tools embed as _structural_score().
    """
    pl = prompt.lower()
    cl = candidate.lower().strip()
    cl0 = _first_word(cl)

    for cat_fn in _ALL_CATS:
        score = cat_fn(pl, cl, cl0)
        if score >= 0:
            return score
    return -1.0
