"""CAITL v3 Category Parsers -- structural pattern detection, no exact-wording matching.

Each parser returns (score, matched: bool) where score in [-1, 1].
+1 = candidate is structurally correct, -1 = structurally wrong, 0 = no signal.
matched=True means the parser fired (the prompt has this structure).

All parsers operate on STRUCTURAL PATTERNS extracted from text, not on specific
trap wordings. They should generalise to any rephrasing of the same logical
structure.
"""

import re
import math
from typing import Tuple, List, Optional, Dict

# ── helpers ──────────────────────────────────────────────────────────
_NUM = re.compile(r"[-+]?\d*\.?\d+")
_WORDS = re.compile(r"\b[a-z]+(?:'[a-z]+)?\b")


def _nums(text: str) -> List[float]:
    """Extract all numbers (int or float) from text."""
    return [float(m) for m in _NUM.findall(text)]


def _words(text: str) -> List[str]:
    return _WORDS.findall(text.lower())


def _has(text: str, *terms: str) -> bool:
    tl = text.lower()
    return any(t in tl for t in terms)


def _cword(text: str) -> str:
    """First meaningful word of candidate (for yes/no answers)."""
    w = _words(text)
    return w[0] if w else ""


def _affirm(text: str) -> bool:
    fw = _cword(text)
    return fw in ("yes", "true", "correct", "right")


def _deny(text: str) -> bool:
    fw = _cword(text)
    return fw in ("no", "false", "incorrect", "wrong", "not")


# ── 1. numeric_float_comparison ──────────────────────────────────────
def numeric_float_comparison(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect prompts that compare two numbers and check if the candidate
    picks the right answer.  Works with ANY comparison phrasing."""
    pl = prompt.lower()
    cl = candidate.lower().strip()
    # Pattern: two numbers + comparison question word
    nums = _nums(prompt)
    if len(nums) < 2:
        return 0.0, False
    # Need a comparison indicator in prompt
    gt_words = ("larger", "greater", "bigger", "more", "higher", "heavier")
    lt_words = ("smaller", "less", "fewer", "lower", "lighter", "shorter")
    is_gt_q = _has(pl, *gt_words)
    is_lt_q = _has(pl, *lt_words)
    if not (is_gt_q or is_lt_q):
        return 0.0, False
    # Determine the two compared values (first two numbers in prompt)
    a, b = nums[0], nums[1]
    cnums = _nums(candidate)
    # If prompt asks "is A greater than B"
    if is_gt_q and not is_lt_q:
        correct_bool = a > b
    elif is_lt_q and not is_gt_q:
        correct_bool = a < b
    else:
        # Both present -- look for "which is larger" style
        correct_val = max(a, b) if is_gt_q else min(a, b)
        if cnums and abs(cnums[0] - correct_val) < 1e-9:
            return 1.0, True
        if cnums and abs(cnums[0] - (a + b - correct_val)) < 1e-9:
            return -1.0, True
        return 0.0, True
    # yes/no style
    if _affirm(cl):
        return (1.0 if correct_bool else -1.0), True
    if _deny(cl):
        return (1.0 if not correct_bool else -1.0), True
    # candidate might state the number
    if cnums:
        correct_val = max(a, b) if is_gt_q else min(a, b)
        wrong_val = min(a, b) if is_gt_q else max(a, b)
        if abs(cnums[0] - correct_val) < 1e-9:
            return 1.0, True
        if abs(cnums[0] - wrong_val) < 1e-9:
            return -1.0, True
    return 0.0, True


# ── 2. trick_question_equal_weight ───────────────────────────────────
def trick_question_equal_weight(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect 'unit of X vs unit of Y weighs more' trick -- any unit, any
    substances.  Structure: same MEASURE of two different things, asks which
    is heavier/lighter."""
    pl = prompt.lower()
    # Pattern: <quantity> of <X> ... <same quantity> of <Y> ... weigh/heav/light
    m = re.search(
        r"(\d+\s+)?(pound|kilo|kg|ton|gram|ounce|lb|liter|gallon|cup)\s+of\s+(\w+)"
        r".*?\1?(pound|kilo|kg|ton|gram|ounce|lb|liter|gallon|cup)\s+of\s+(\w+)",
        pl)
    if not m:
        return 0.0, False
    # Must ask about weight comparison
    if not _has(pl, "heav", "weigh", "light", "more", "which"):
        return 0.0, False
    cl = candidate.lower()
    if _has(cl, "same", "equal", "neither", "both", "identical"):
        return 1.0, True
    # Wrong if they pick one substance
    return -0.5, True


# ── 3. positional_logic ──────────────────────────────────────────────
def positional_logic(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect 'overtake N-th place' puzzles.  Structure: you pass/overtake
    the person in position N -- what position are you in?  Answer = N."""
    pl = prompt.lower()
    # Pattern: overtake/pass + ordinal position
    m = re.search(r"(?:overtake|pass)\s+(?:the\s+)?(?:person|runner|racer|one)?\s*(?:in\s+)?(\w+)\s+place", pl)
    if not m:
        # Also match "overtake 2nd place"
        m = re.search(r"(?:overtake|pass)\s+(\w+)\s+place", pl)
    if not m:
        return 0.0, False
    if not _has(pl, "what place", "what position", "position are", "place are"):
        return 0.0, False
    pos_word = m.group(1).lower()
    # Map ordinal to cardinal
    ordinals = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3,
                "3rd": 3, "fourth": 4, "4th": 4, "fifth": 5, "5th": 5,
                "last": -1}
    target = ordinals.get(pos_word, None)
    if target is None:
        try:
            target = int(pos_word)
        except ValueError:
            return 0.0, False
    # Correct answer: you take their place (the position you overtook)
    cl = candidate.lower()
    target_words = {1: ("first", "1st", "1"), 2: ("second", "2nd", "2"),
                    3: ("third", "3rd", "3"), 4: ("fourth", "4th", "4"),
                    5: ("fifth", "5th", "5")}
    wrong_target = target - 1  # common mistake: think you go one ahead
    if target in target_words:
        if any(w in cl for w in target_words[target]):
            return 1.0, True
    if wrong_target in target_words:
        if any(w in cl for w in target_words[wrong_target]):
            return -1.0, True
    return 0.0, True


# ── 4. algebraic_word_problem ────────────────────────────────────────
def algebraic_word_problem(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect 'X and Y together cost T, X costs D more than Y' structure.
    Solve: y = (T - D) / 2.  Generalises beyond bat/ball."""
    pl = prompt.lower()
    # Pattern: total cost + difference
    m_total = re.search(r"(?:together|total|combined|in total)\s*(?:cost|is|are|was)?\s*\$?([\d.]+)", pl)
    if not m_total:
        m_total = re.search(r"\$?([\d.]+)\s*(?:total|together|combined|in all)", pl)
    if not m_total:
        # "A <thing> and a <thing> cost $T"
        m_total = re.search(r"(?:and\s+\w+\s+)?cost\s+\$?([\d.]+)", pl)
    m_diff = re.search(r"(?:costs?|is)\s+\$?([\d.]+)\s+more\s+than", pl)
    if not (m_total and m_diff):
        return 0.0, False
    total = float(m_total.group(1))
    diff = float(m_diff.group(1))
    correct = (total - diff) / 2.0
    cnums = _nums(candidate)
    if cnums:
        if abs(cnums[0] - correct) < 0.01:
            return 1.0, True
        # Common wrong answer: total - diff (the naive subtraction)
        if abs(cnums[0] - diff) < 0.01 or abs(cnums[0] - (total - diff)) < 0.01:
            # (total - diff) is 2*correct, could also be wrong
            if abs(cnums[0] - correct) > 0.01:
                return -1.0, True
    return 0.0, True


# ── 5. universal_quantifier_converse_error ───────────────────────────
def universal_quantifier_converse_error(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect 'All X are Y. Does that mean all Y are X?' structure.
    Answer: No (converse is not implied by universal)."""
    pl = prompt.lower()
    # Pattern: "all A are B" followed by question about converse
    m = re.search(r"\ball\s+(\w+)\s+are\s+(\w+)", pl)
    if not m:
        return 0.0, False
    a_class, b_class = m.group(1), m.group(2)
    # Check for converse question
    has_converse_q = bool(re.search(
        r"(?:does\s+(?:that|this|it)\s+mean|can\s+we\s+(?:say|conclude|infer)|"
        r"is\s+it\s+true|does\s+it\s+follow|are\s+all)\s+.*?" + re.escape(b_class),
        pl))
    if not has_converse_q:
        # Also match "all Y are X?" directly
        has_converse_q = bool(re.search(
            r"\ball\s+" + re.escape(b_class) + r"\s+are\s+" + re.escape(a_class), pl))
    if not has_converse_q:
        return 0.0, False
    cl = candidate.lower()
    if _deny(cl) or _has(cl, "not necessarily", "cannot", "does not follow", "no"):
        return 1.0, True
    if _affirm(cl):
        return -1.0, True
    return 0.0, True


# ── 6. mathematical_identity ─────────────────────────────────────────
def mathematical_identity(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect '0.999... = 1' or similar repeating decimal / mathematical
    identity questions.  Answer: Yes / equal / true."""
    pl = prompt.lower()
    # Pattern: repeating/recurring decimal and equals
    if re.search(r"0\.9{2,}|0\.9+\s*(?:repeating|recurring|\.{2,})", pl):
        if _has(pl, "equal", "same as", "="):
            cl = candidate.lower()
            if _affirm(cl) or _has(cl, "equal", "same", "yes", "true"):
                return 1.0, True
            if _deny(cl):
                return -1.0, True
            return 0.0, True
    return 0.0, False


# ── 7. pigeonhole_principle ──────────────────────────────────────────
def pigeonhole_principle(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect N items into M < N slots must-share problems.
    Structure: N entities, M categories, must at least two share?"""
    pl = prompt.lower()
    nums = _nums(prompt)
    if len(nums) < 2:
        return 0.0, False
    # Need indication of pigeonhole structure
    if not _has(pl, "must", "guarantee", "certain", "at least", "share",
                "same", "birthday", "month", "drawer", "sock", "color"):
        return 0.0, False
    items, slots = int(nums[0]), int(nums[1])
    # Ensure items > slots (pigeonhole)
    if items <= slots:
        items, slots = slots, items
    if items <= slots:
        return 0.0, False
    correct = items > slots  # must share
    cl = candidate.lower()
    if _affirm(cl) or _has(cl, "must", "yes", "true", "guaranteed"):
        return (1.0 if correct else -1.0), True
    if _deny(cl):
        return (-1.0 if correct else 1.0), True
    return 0.0, True


# ── 8. statistical_independence ──────────────────────────────────────
def statistical_independence(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect gambler's fallacy / independence questions.
    Structure: sequence of random outcomes, then asking about next probability.
    Answer: same as base rate (e.g. 50% for fair coin)."""
    pl = prompt.lower()
    # Pattern: random device + sequence of outcomes + probability question
    is_coin = _has(pl, "coin", "flip", "toss")
    is_dice = _has(pl, "dice", "die", "roll")
    is_roulette = _has(pl, "roulette", "spin")
    if not (is_coin or is_dice or is_roulette):
        return 0.0, False
    # Needs a sequence and a question
    has_sequence = bool(re.search(r"\d+\s*(?:times|flips|tosses|rolls|spins|in a row|consecutive|straight)", pl))
    has_question = _has(pl, "probability", "chance", "likely", "odds", "what is", "what are",
                        "next", "more likely", "less likely")
    if not (has_sequence and has_question):
        return 0.0, False
    cl = candidate.lower()
    # Correct: base rate (50% for coin, 1/6 for die)
    if is_coin:
        if _has(cl, "50", "1/2", "half", "fifty", "0.5", "same"):
            return 1.0, True
        if _has(cl, "higher", "lower", "more likely", "less likely", "increase", "decrease"):
            return -1.0, True
    if is_dice:
        if _has(cl, "1/6", "16.7", "same", "unchanged"):
            return 1.0, True
        if _has(cl, "higher", "lower", "more likely", "less likely"):
            return -1.0, True
    return 0.0, True


# ── 9. number_parity ─────────────────────────────────────────────────
def number_parity(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect parity questions: sum/product of odd/even numbers.
    Rules: odd+odd=even, even+even=even, odd+even=odd.
    odd*odd=odd, even*anything=even."""
    pl = prompt.lower()
    # Pattern: operation on parity-described numbers
    is_sum = _has(pl, "sum", "add", "plus", "+")
    is_prod = _has(pl, "product", "multiply", "times", "*")
    has_odd = "odd" in pl
    has_even = "even" in pl
    if not ((is_sum or is_prod) and (has_odd or has_even)):
        return 0.0, False
    # Determine structure
    # "sum of two odd numbers" → even
    # "sum of two even numbers" → even
    # "sum of an odd and an even" → odd
    # "product of two odd numbers" → odd
    # "product with any even" → even
    m_two_odd = bool(re.search(r"(?:two|2)\s+odd", pl))
    m_two_even = bool(re.search(r"(?:two|2)\s+even", pl))
    m_odd_even = has_odd and has_even
    if is_sum:
        if m_two_odd:
            correct_parity = "even"
        elif m_two_even:
            correct_parity = "even"
        elif m_odd_even:
            correct_parity = "odd"
        else:
            return 0.0, True
    elif is_prod:
        if m_two_odd:
            correct_parity = "odd"
        elif has_even:
            correct_parity = "even"
        else:
            return 0.0, True
    else:
        return 0.0, True

    cl = candidate.lower()
    # Check if prompt asserts wrong parity and asks true/false
    if _has(pl, "always odd") and correct_parity == "even":
        # Prompt claims wrong thing
        if _deny(cl) or _has(cl, "even", "false"):
            return 1.0, True
        if _affirm(cl) or _has(cl, "odd", "true"):
            return -1.0, True
    elif _has(pl, "always even") and correct_parity == "even":
        if _affirm(cl) or _has(cl, "even", "true"):
            return 1.0, True
        if _deny(cl):
            return -1.0, True
    # General: candidate states correct parity
    if correct_parity in cl:
        return 1.0, True
    wrong_parity = "odd" if correct_parity == "even" else "even"
    if wrong_parity in cl and correct_parity not in cl:
        return -1.0, True
    return 0.0, True


# ── 10. all_but_N_survivor_counting ──────────────────────────────────
def all_but_N_survivor_counting(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect 'all but N' survivor counting.
    Structure: group of M, all but N <die/leave/etc>.  How many left? Answer: N.
    Generalises: 'all except N', 'all save N', 'every one but N'."""
    pl = prompt.lower()
    m = re.search(r"all\s+(?:but|except|save)\s+(\d+)", pl)
    if not m:
        # "every ... but N"
        m = re.search(r"every\s+(?:\w+\s+)?(?:but|except)\s+(\d+)", pl)
    if not m:
        return 0.0, False
    if not _has(pl, "how many", "how much", "remain", "left", "alive", "survive"):
        return 0.0, False
    survivor_n = float(m.group(1))
    cnums = _nums(candidate)
    if cnums:
        if abs(cnums[0] - survivor_n) < 0.01:
            return 1.0, True
        return -0.8, True
    # String check
    if m.group(1) in candidate:
        return 1.0, True
    return -0.5, True


# ── 11. transitive_ordering ──────────────────────────────────────────
def transitive_ordering(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect transitive comparison chains: A > B, B > C, who is
    tallest/shortest/etc?  Generalises to any comparative adjective."""
    pl = prompt.lower()
    # Find all "X is <comp> than Y" pairs
    pairs = re.findall(
        r"(\w+)\s+is\s+(\w+(?:er|ier))\s+than\s+(\w+)", pl)
    if len(pairs) < 2:
        return 0.0, False
    # Build ordering graph
    greater = {}  # entity -> set of entities it is greater than
    for subj, _, obj in pairs:
        s, o = subj.lower(), obj.lower()
        greater.setdefault(s, set()).add(o)
    # Transitive closure
    changed = True
    while changed:
        changed = False
        for a in list(greater):
            for b in list(greater.get(a, set())):
                for c in greater.get(b, set()):
                    if c not in greater[a]:
                        greater[a].add(c)
                        changed = True
    # Find top (most wins) and bottom (no wins)
    all_ents = set()
    for a in greater:
        all_ents.add(a)
        all_ents.update(greater[a])
    top = [e for e in all_ents if len(greater.get(e, set())) == len(all_ents) - 1]
    bottom = [e for e in all_ents if len(greater.get(e, set())) == 0]
    # Determine if prompt asks for top or bottom
    asks_top = _has(pl, "tallest", "largest", "biggest", "heaviest", "fastest",
                     "oldest", "most", "highest", "best")
    asks_bottom = _has(pl, "shortest", "smallest", "lightest", "slowest",
                       "youngest", "least", "lowest", "worst")
    cl = candidate.lower()
    if asks_top and top:
        if any(t in cl for t in top):
            return 1.0, True
        if bottom and any(b in cl for b in bottom):
            return -1.0, True
    if asks_bottom and bottom:
        if any(b in cl for b in bottom):
            return 1.0, True
        if top and any(t in cl for t in top):
            return -1.0, True
    return 0.0, True


# ── 12. negation_scope_insufficiency ─────────────────────────────────
def negation_scope_insufficiency(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect 'not all X' / 'not every X' questions where the answer
    requires recognising that partial negation != full negation.
    'Not all X are Y' does NOT mean 'no X are Y'.
    Correct: cannot determine / not enough information / some might be."""
    pl = prompt.lower()
    # Pattern: "not all" or "not every" + question about conclusion
    if not re.search(r"not\s+(?:all|every|each)", pl):
        return 0.0, False
    if not _has(pl, "?", "can we", "does", "is it", "conclude", "mean", "infer",
                "true", "determine"):
        return 0.0, False
    cl = candidate.lower()
    # Correct: acknowledges insufficiency
    if _has(cl, "cannot", "not enough", "not necessarily", "insufficient",
            "can't determine", "does not follow", "some", "possible", "uncertain"):
        return 1.0, True
    # Wrong: definitive yes or definitive "none"
    if _affirm(cl) or _has(cl, "none", "all are", "every"):
        return -1.0, True
    if _deny(cl):
        # "No" could be correct ("no, we cannot conclude...") -- check context
        if _has(cl, "no,", "no.", "no we", "no you"):
            return 0.5, True
        return -0.3, True
    return 0.0, True


# ── 13. stated_premise_usage ─────────────────────────────────────────
def stated_premise_usage(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect prompts that explicitly state a comparison/fact and then ask
    a question whose answer is directly in the stated premise.
    E.g. 'X is less than Y. Which is larger?' Answer: Y (stated in premise)."""
    pl = prompt.lower()
    # Pattern: "A is less/greater than B" + "which is larger/smaller?"
    m = re.search(
        r"(\w+[\d.]*)\s+is\s+(less|more|greater|smaller|larger|bigger|shorter|taller|lighter|heavier)"
        r"\s+than\s+(\w+[\d.]*)", pl)
    if not m:
        # Also try with numbers: "3 is less than 5"
        m = re.search(
            r"([\d.]+)\s+is\s+(less|more|greater|smaller|larger|bigger)\s+than\s+([\d.]+)", pl)
    if not m:
        return 0.0, False
    entity_a = m.group(1).lower()
    relation = m.group(2).lower()
    entity_b = m.group(3).lower()
    # Determine which is "more" and which is "less"
    a_is_less = relation in ("less", "smaller", "shorter", "lighter")
    a_is_more = relation in ("more", "greater", "larger", "bigger", "taller", "heavier")
    # What does the question ask?
    asks_larger = _has(pl, "which is larger", "which is bigger", "which is greater",
                       "which is more", "which is taller", "which is heavier")
    asks_smaller = _has(pl, "which is smaller", "which is less", "which is shorter",
                        "which is lighter")
    if not (asks_larger or asks_smaller):
        return 0.0, False
    # Determine correct answer
    if asks_larger:
        correct = entity_b if a_is_less else entity_a
        wrong = entity_a if a_is_less else entity_b
    else:  # asks smaller
        correct = entity_a if a_is_less else entity_b
        wrong = entity_b if a_is_less else entity_a
    cl = candidate.lower()
    if correct in cl:
        return 1.0, True
    if wrong in cl and correct not in cl:
        return -1.0, True
    return 0.0, True


# ── 14. subject_object_verb_parsing ──────────────────────────────────
def subject_object_verb_parsing(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect SVO role confusion traps: 'The X verbed the Y. Who was verbed?'
    Correct: Y (the object), not X (the subject)."""
    pl = prompt.lower()
    # Find SVO pattern
    svo = re.search(
        r"(?:the\s+)?(\w+)\s+((?:\w+ed|\w+s|ate|hit|saw|bit|gave|told|chased|caught|pushed|pulled))"
        r"\s+(?:the\s+)?(\w+)", pl)
    if not svo:
        return 0.0, False
    subject = svo.group(1).lower()
    verb = svo.group(2).lower()
    obj = svo.group(3).lower()
    # Need a question about who did what
    # "Who was <verb>ed?" → object
    # "Who <verb>ed?" → subject
    asks_object = bool(re.search(
        r"who\s+(?:was|were|got|is)\s+\w+(?:ed|en)|"
        r"what\s+(?:was|were|got)\s+\w+(?:ed|en)|"
        r"who\s+did\s+\w+\s+\w+", pl))
    asks_subject = bool(re.search(
        r"who\s+(?:\w+ed|\w+s)\s+(?:the\s+)?\w+", pl))
    if not (asks_object or asks_subject):
        return 0.0, False
    cl = candidate.lower()
    if asks_object:
        if obj in cl and subject not in cl:
            return 1.0, True
        if subject in cl and obj not in cl:
            return -1.0, True
    elif asks_subject:
        if subject in cl and obj not in cl:
            return 1.0, True
        if obj in cl and subject not in cl:
            return -1.0, True
    return 0.0, True


# ── 15. modus_tollens_contrapositive ─────────────────────────────────
def modus_tollens_contrapositive(prompt: str, candidate: str) -> Tuple[float, bool]:
    """Detect modus tollens: If P then Q. Not Q. Therefore not P.
    Structure: conditional + denial of consequent + question about antecedent."""
    pl = prompt.lower()
    # Find conditional
    cond = re.search(r"if\s+(.+?)[,.]?\s*then\s+(.+?)(?:[,.]|$)", pl)
    if not cond:
        # Also "when X, Y"
        cond = re.search(r"when(?:ever)?\s+(.+?)[,.]?\s*(.+?)(?:[,.]|$)", pl)
    if not cond:
        return 0.0, False
    antecedent = cond.group(1).strip()
    consequent = cond.group(2).strip()
    # Check for denial of consequent in the rest of the prompt
    rest = pl[cond.end():]
    has_denial = _has(rest, "not " + consequent[:10], "no " + consequent[:10],
                      "didn't", "doesn't", "don't", "isn't", "aren't",
                      "not", "never", "absent", "lacks")
    if not has_denial:
        # Check for negation words near consequent keywords
        cons_words = set(_words(consequent))
        rest_words = _words(rest)
        neg_near_cons = False
        for i, w in enumerate(rest_words):
            if w in ("not", "no", "never", "doesn't", "didn't", "isn't", "don't"):
                # Check if next few words overlap with consequent
                window = set(rest_words[i:i+5])
                if window & cons_words:
                    neg_near_cons = True
                    break
        if not neg_near_cons:
            return 0.0, False
    cl = candidate.lower()
    # Correct: deny the antecedent (not P)
    if _deny(cl) or _has(cl, "not", "cannot", "doesn't", "didn't", "isn't"):
        return 1.0, True
    if _affirm(cl):
        return -1.0, True
    return 0.0, True


# ── Master dispatcher ────────────────────────────────────────────────
ALL_PARSERS = [
    ("numeric_float_comparison",          numeric_float_comparison),
    ("trick_question_equal_weight",       trick_question_equal_weight),
    ("positional_logic",                  positional_logic),
    ("algebraic_word_problem",            algebraic_word_problem),
    ("universal_quantifier_converse_error", universal_quantifier_converse_error),
    ("mathematical_identity",             mathematical_identity),
    ("pigeonhole_principle",              pigeonhole_principle),
    ("statistical_independence",          statistical_independence),
    ("number_parity",                     number_parity),
    ("all_but_N_survivor_counting",       all_but_N_survivor_counting),
    ("transitive_ordering",               transitive_ordering),
    ("negation_scope_insufficiency",      negation_scope_insufficiency),
    ("stated_premise_usage",              stated_premise_usage),
    ("subject_object_verb_parsing",       subject_object_verb_parsing),
    ("modus_tollens_contrapositive",      modus_tollens_contrapositive),
]


def run_all_parsers(prompt: str, candidate: str) -> Tuple[float, List[str]]:
    """Run all parsers.  Returns (aggregate_score, list_of_tags).

    aggregate_score is in [-1, 1].  Tags describe which parsers fired.
    If no parser fires, returns (0.0, []).
    """
    total = 0.0
    count = 0
    tags = []
    for name, fn in ALL_PARSERS:
        try:
            score, matched = fn(prompt, candidate)
            if matched:
                total += score
                count += 1
                tags.append(f"{name}={score:+.1f}")
        except Exception:
            pass
    if count == 0:
        return 0.0, []
    return total / count, tags
