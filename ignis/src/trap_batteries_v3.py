"""
trap_batteries_v3.py — Harder traps for 7B+ models.

Design goals:
  - Target baseline ~15-20/30 at 7B (vs ~25/30 on v2)
  - Multi-step reasoning required (2-3 hops minimum)
  - Same cognitive failure families as v2, harder instances
  - All answer pairs have distinct first BPE tokens
  - Draws on Forge category test patterns (temporal, causal, ToM, compositional)

Token collision rules:
  - Never use two numbers starting with the same digit ("11" vs "10")
  - Prefer word tokens (Yes/No, True/False, name tokens) over numerics
  - When using numbers, ensure different first digits or use words

Categories covered:
  1. Multi-step temporal (4 traps)
  2. Causal/counterfactual reasoning (3 traps)
  3. Theory of mind (3 traps)
  4. Constraint satisfaction (3 traps)
  5. Compositional arithmetic (3 traps)
  6. Probabilistic reasoning (3 traps)
  7. Combinatorial/counting (3 traps)
  8. Cognitive bias resistance (3 traps)
  9. Set theory / logic (3 traps)
  10. Modular / cyclic reasoning (2 traps)
"""

# ── Multi-step temporal (4 traps) ─────────────────────────────

TEMPORAL_TRAPS = [
    {
        "name": "Nested Relative Day",
        "prompt": "Today is Wednesday. What day is the day after the day after tomorrow? Answer: Saturday or Friday?",
        "target_token": "Saturday",
        "anti_token": "Friday",
        # Wed → tomorrow=Thu → day after=Fri → day after=Sat
        # Heuristic: "day after tomorrow" = Fri, then stop
    },
    {
        "name": "Age Constraint",
        "prompt": "Alice is 4 years older than Bob. Bob is twice as old as Carol. Carol is 5. How old is Alice? Answer: Fourteen or Nine?",
        "target_token": "Fourteen",
        "anti_token": "Nine",
        # Carol=5, Bob=10, Alice=14. Heuristic: 5+4=9 (skipping the doubling step).
    },
    {
        "name": "Duration Across Midnight",
        "prompt": "A process starts at 10:30 PM and runs for 5 hours 45 minutes. Does it end before or after 4 AM? Answer: Before or After?",
        "target_token": "Before",
        "anti_token": "After",
        # 10:30 PM + 5:45 = 4:15 AM. Wait: 10:30+5:45 = 3:15+1:00 = 4:15 AM. After 4 AM.
        # Actually: 10:30 PM + 5h = 3:30 AM + 45m = 4:15 AM. That's AFTER 4 AM.
        # Hmm, let me recalculate. 22:30 + 5:45 = 28:15 = 04:15. After.
        # I need target to be correct. Let me fix: "ends before or after 5 AM?"
        # 4:15 AM is before 5 AM. Target = Before. Good.
    },
    {
        "name": "Concurrent Finish",
        "prompt": "Task A takes 3 hours starting at 9 AM. Task B takes 5 hours starting at 8 AM. Which finishes first? Answer: Both or A?",
        "target_token": "Both",
        "anti_token": "A",
        # A: 9+3=12 PM. B: 8+5=1 PM. A finishes first. Wait — "Both" means same time.
        # Let me fix: A=3h from 9AM=12PM. B=5h from 8AM=1PM. A finishes first.
        # Need: which finishes first, A or B? Answer A or B.
    },
]

# Fix the traps that had logical issues during design:
TEMPORAL_TRAPS[2] = {
    "name": "Duration Across Midnight",
    "prompt": "A process starts at 10:30 PM and runs for 5 hours 45 minutes. Does it end before or after 5 AM? Answer: Before or After?",
    "target_token": "Before",
    "anti_token": "After",
    # 22:30 + 5:45 = 04:15 next day. Before 5 AM. Correct.
}

TEMPORAL_TRAPS[3] = {
    "name": "Concurrent Finish",
    "prompt": "Task A takes 3 hours starting at 9 AM. Task B takes 4 hours starting at 8 AM. Do they finish at the same time? Answer: Yes or No?",
    "target_token": "Yes",
    "anti_token": "No",
    # A: 9+3=12 PM. B: 8+4=12 PM. Same time. Heuristic: different starts = different ends.
}

# ── Causal / counterfactual (3 traps) ─────────────────────────

CAUSAL_TRAPS = [
    {
        "name": "Blocked Mediator",
        "prompt": "Smoking causes tar buildup. Tar buildup causes lung cancer. If we could prevent tar buildup, would smoking still cause lung cancer through this pathway? Answer: No or Yes?",
        "target_token": "No",
        "anti_token": "Yes",
        # Blocking the mediator breaks the causal chain. Heuristic: smoking=cancer always.
    },
    {
        "name": "Confounded Correlation",
        "prompt": "Cities with more firefighters have more fires. Does hiring more firefighters cause more fires? Answer: No or Yes?",
        "target_token": "No",
        "anti_token": "Yes",
        # Common cause: larger cities have both. Heuristic: correlation = causation.
    },
    {
        "name": "Counterfactual Universal",
        "prompt": "All students who studied passed the exam. Tom did not study. If Tom had studied, would he have passed? Answer: Yes or No?",
        "target_token": "Yes",
        "anti_token": "No",
        # Universal quantifier: all who studied passed → studying is sufficient.
        # Heuristic: Tom didn't study, so we can't know. But the universal gives us the answer.
    },
]

# ── Theory of mind (3 traps) ──────────────────────────────────

TOM_TRAPS = [
    {
        "name": "Second Order Belief",
        "prompt": "Alice put chocolate in the blue box. Alice left. Bob moved the chocolate to the red box. Alice did not see this. Where does Alice think the chocolate is? Answer: Blue or Red?",
        "target_token": "Blue",
        "anti_token": "Red",
        # Sally-Anne test. Alice's belief is stale. Heuristic: chocolate IS in red.
    },
    {
        "name": "Strategic Deception",
        "prompt": "Alice wants Bob to go left. Bob always does the opposite of what Alice suggests. What should Alice say? Answer: Right or Left?",
        "target_token": "Right",
        "anti_token": "Left",
        # Say opposite of desired outcome. Heuristic: say what you want.
    },
    {
        "name": "Information Asymmetry",
        "prompt": "You know a six-sided die is loaded to always roll 6. Your friend doesn't know it's loaded. What does your friend expect the average roll to be? Answer: Three or Six?",
        "target_token": "Three",
        "anti_token": "Six",
        # Friend expects fair die: E=3.5, closest = three. Heuristic: it always rolls 6.
    },
]

# ── Constraint satisfaction (3 traps) ─────────────────────────

CONSTRAINT_TRAPS = [
    {
        "name": "Liar Puzzle Simple",
        "prompt": "Alice says 'Bob is a liar.' Bob says 'Alice is a liar.' If exactly one of them always tells the truth, can you determine who the truth-teller is? Answer: No or Yes?",
        "target_token": "No",
        "anti_token": "Yes",
        # Both assignments are consistent. Symmetric. Heuristic: there must be an answer.
    },
    {
        "name": "Pigeonhole",
        "prompt": "A drawer has red, blue, and green socks. How many socks must you pull out in the dark to guarantee a matching pair? Answer: Four or Three?",
        "target_token": "Four",
        "anti_token": "Three",
        # 3 colors → need 4 to guarantee a match (pigeonhole). Heuristic: 3 colors = 3 socks.
    },
    {
        "name": "Vacuous Truth",
        "prompt": "There are no unicorns. Is the statement 'All unicorns can fly' true or false? Answer: True or False?",
        "target_token": "True",
        "anti_token": "False",
        # Vacuously true (empty domain). Heuristic: unicorns don't exist so it's false.
    },
]

# ── Compositional arithmetic (3 traps) ────────────────────────

COMPOSITIONAL_TRAPS = [
    {
        "name": "Order of Operations",
        "prompt": "What is 2 + 3 × 4? Answer: Fourteen or Twenty?",
        "target_token": "Fourteen",
        "anti_token": "Twenty",
        # 2+(3×4)=14. Heuristic: (2+3)×4=20 (left-to-right).
    },
    {
        "name": "Direction Composition",
        "prompt": "You face North. You turn right, then right again, then left. Which direction do you face? Answer: East or West?",
        "target_token": "East",
        "anti_token": "West",
        # N→E→S→E. Wait: N+right=E, E+right=S, S+left=E. Answer: East.
    },
    {
        "name": "Multi-Step State",
        "prompt": "Start with 10. Add 5, then double it, then subtract 8. What is the result? Answer: Twenty-two or Forty-two?",
        "target_token": "Twenty",
        "anti_token": "Forty",
        # 10+5=15, 15*2=30, 30-8=22. "Twenty-two" starts with "Twenty".
        # Heuristic trap: 10+5=15, *2=30... wait that's 22. Anti "Forty-two" for (10+5)*2+8=38... no.
        # Let me make cleaner numbers.
    },
]

# Fix multi-step state for cleaner numbers and token collision avoidance
COMPOSITIONAL_TRAPS[2] = {
    "name": "Multi-Step State",
    "prompt": "Start with 8. Double it, then add 6, then halve it. What is the result? Answer: Eleven or Twenty-two?",
    "target_token": "Eleven",
    "anti_token": "Twenty",
    # 8*2=16, 16+6=22, 22/2=11. Heuristic: just double and add: 8*2+6=22.
}

# ── Probabilistic reasoning (3 traps) ─────────────────────────

PROBABILITY_TRAPS = [
    {
        "name": "Base Rate Neglect",
        "prompt": "A disease affects 1 in 1000 people. A test is 99% accurate. You test positive. Is the probability you actually have the disease above or below 50%? Answer: Below or Above?",
        "target_token": "Below",
        "anti_token": "Above",
        # P(disease|positive) ≈ 1/11 ≈ 9%. Well below 50%. Heuristic: 99% accurate = 99% chance.
    },
    {
        "name": "Gambler's Fallacy",
        "prompt": "A fair coin has landed heads 9 times in a row. Is the probability of tails on the next flip exactly 50%? Answer: Yes or No?",
        "target_token": "Yes",
        "anti_token": "No",
        # Independent events. P(tails)=0.5 always. Heuristic: "due" for tails.
    },
    {
        "name": "Conjunction Fallacy",
        "prompt": "Linda is a 31-year-old activist concerned about social justice. Which is more probable: Linda is a bank teller, or Linda is a bank teller AND active in the feminist movement? Answer: Teller or Both?",
        "target_token": "Teller",
        "anti_token": "Both",
        # P(A) >= P(A and B) always. Heuristic: the description makes "Both" feel more likely.
    },
]

# ── Combinatorial / counting (3 traps) ────────────────────────

COUNTING_TRAPS = [
    {
        "name": "Diagonal Count",
        "prompt": "How many diagonals does a hexagon (6-sided polygon) have? Answer: Nine or Twelve?",
        "target_token": "Nine",
        "anti_token": "Twelve",
        # n(n-3)/2 = 6*3/2 = 9. Heuristic: 6 vertices × 2 diagonals each = 12 (double-counts).
    },
    {
        "name": "Handshake Scaling",
        "prompt": "At a party, everyone shakes hands with everyone else exactly once. With 6 people, is the number of handshakes above or below 18? Answer: Below or Above?",
        "target_token": "Below",
        "anti_token": "Above",
        # C(6,2) = 15. Below 18. Heuristic: 6×5=30/2=15... but "6 people × 3" feels like 18.
    },
    {
        "name": "Circular Arrangement",
        "prompt": "How many ways can 4 people sit around a circular table? Answer: Six or Twenty-four?",
        "target_token": "Six",
        "anti_token": "Twenty",
        # (n-1)! = 3! = 6. Heuristic: 4! = 24. Circular removes one degree of freedom.
    },
]

# ── Cognitive bias resistance (3 traps) ───────────────────────

BIAS_TRAPS = [
    {
        "name": "Sunk Cost",
        "prompt": "You paid $100 for a concert ticket. On the night, you feel sick and won't enjoy it. A friend offers a free movie you'd love. Should the $100 you already spent influence your decision? Answer: No or Yes?",
        "target_token": "No",
        "anti_token": "Yes",
        # Sunk cost should not affect forward-looking decisions. Heuristic: "I paid $100, I should go."
    },
    {
        "name": "Survivorship Bias",
        "prompt": "Every successful startup founder you've studied dropped out of college. Does this prove dropping out helps you succeed? Answer: No or Yes?",
        "target_token": "No",
        "anti_token": "Yes",
        # Selection bias — you're only seeing survivors. Heuristic: pattern = proof.
    },
    {
        "name": "Anchoring Resistance",
        "prompt": "A store marks a jacket from $300 down to $150. Another store sells the same jacket for $140, never discounted. Which is the better deal? Answer: Second or First?",
        "target_token": "Second",
        "anti_token": "First",
        # $140 < $150 regardless of anchor. Heuristic: 50% off feels like a better deal.
    },
]

# ── Set theory / logic (3 traps) ──────────────────────────────

LOGIC_TRAPS = [
    {
        "name": "Converse Error",
        "prompt": "If it rains, the ground is wet. The ground is wet. Can you conclude it rained? Answer: No or Yes?",
        "target_token": "No",
        "anti_token": "Yes",
        # Affirming the consequent fallacy. Ground could be wet from sprinklers. Heuristic: wet=rain.
    },
    {
        "name": "Necessary vs Sufficient",
        "prompt": "All dogs are mammals. Is being a mammal sufficient to be a dog? Answer: No or Yes?",
        "target_token": "No",
        "anti_token": "Yes",
        # Necessary but not sufficient. Cats are mammals too. Heuristic: dogs=mammals so mammals=dogs.
    },
    {
        "name": "Inclusion Exclusion",
        "prompt": "In a class of 30, 20 play soccer, 15 play basketball, and 10 play both. How many play neither? Answer: Five or Zero?",
        "target_token": "Five",
        "anti_token": "Zero",
        # |S∪B| = 20+15-10 = 25. Neither = 30-25 = 5. Heuristic: 20+15>30 so everyone plays something.
    },
]

# ── Modular / cyclic reasoning (2 traps) ──────────────────────

MODULAR_TRAPS = [
    {
        "name": "Clock Arithmetic",
        "prompt": "It is 10 AM. What time will it be in 25 hours? Answer: Eleven or Nine?",
        "target_token": "Eleven",
        "anti_token": "Nine",
        # 10 + 25 = 35 → 35 mod 24 = 11 AM. Heuristic: 25 hours ≈ 1 day, so ~10 AM (close to 9).
    },
    {
        "name": "Remainder Reasoning",
        "prompt": "You have 23 cookies to divide equally among 5 children. How many are left over? Answer: Three or Four?",
        "target_token": "Three",
        "anti_token": "Four",
        # 23 mod 5 = 3. Heuristic: 23/5=4.6, so 4? No — 4 is the quotient per child, remainder is 3.
    },
]

# ── Combined battery ──────────────────────────────────────────

V3_TRAPS = (
    TEMPORAL_TRAPS
    + CAUSAL_TRAPS
    + TOM_TRAPS
    + CONSTRAINT_TRAPS
    + COMPOSITIONAL_TRAPS
    + PROBABILITY_TRAPS
    + COUNTING_TRAPS
    + BIAS_TRAPS
    + LOGIC_TRAPS
    + MODULAR_TRAPS
)

# Verify no token collisions at import time
def _verify_no_collisions():
    """Check that no trap has target/anti tokens sharing a first character."""
    collisions = []
    for trap in V3_TRAPS:
        t = trap["target_token"]
        a = trap["anti_token"]
        if t[0].lower() == a[0].lower():
            collisions.append(f"  {trap['name']}: {t!r} vs {a!r} (both start with '{t[0]}')")
    if collisions:
        import warnings
        warnings.warn(
            f"v3 battery has {len(collisions)} potential token collisions:\n"
            + "\n".join(collisions)
        )

_verify_no_collisions()
