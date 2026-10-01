"""Subject-facing prompts for the alien-lawful assay. Wording is neutral: no
class names, no mechanism names, no hint that some systems are generated
differently from others. Every prompt asks for one JSON object.
"""

from __future__ import annotations

SYSTEM = ("You are taking part in a study of reasoning about small discrete systems. "
          "You will see what a system did. Work carefully, give your honest best answer, "
          "and return exactly one JSON object in the requested shape and nothing else.")

CODE_NOTE = ("In code and expressions, a state is a Python list of integers `s`"
             "{sym}. Use only plain Python arithmetic, comparisons, loops and built-ins "
             "(range, len, sum, min, max, abs, sorted, list, tuple, zip, enumerate, all, any).")


def _code_note(pub):
    sym = (" (the symbols W, X, Y, Z are 0, 1, 2, 3 in that order)"
           if "symbols" in pub["header"] else "")
    return CODE_NOTE.format(sym=sym)


def _runs(obs):
    return "\n".join(f"Run {i + 1}: " + " -> ".join(t) for i, t in enumerate(obs))


def _interventions(ivs):
    out = []
    for i, iv in enumerate(ivs):
        if iv["type"] == "clamp":
            out.append(f"I{i + 1}: start from {iv['start']}; position {iv['position']} is forced to "
                       f"equal {iv['value']} (set to {iv['value']} at the start and reset to "
                       f"{iv['value']} after every step). Give the next 3 states.")
        else:
            out.append(f"I{i + 1}: start from {iv['start']}; the link {iv['link']} is removed (the "
                       "system behaves as if it did not exist). Give the next 3 states.")
    return "\n".join(out)


T4_SPEC = """"t4": {"claims": [ each claim is one of:
   {"kind": "conserved", "expr": "<Python expression in s whose value never changes from one state to the next>"},
   {"kind": "advances", "expr": "<expression>", "k": <int>, "note": "value goes up by 1 mod k every step"},
   {"kind": "one_predecessor", "note": "every state is produced by exactly one state"},
   {"kind": "settles", "note": "every run eventually stops changing"},
   {"kind": "symmetry", "expr": "<expression in s giving a transformed state (a list)>", "note": "applying the transformation before or after a step gives the same result"},
   {"kind": "other", "prose": "<anything else you believe is preserved or constrained>"} ]}"""


def blind(pub, obs=None, extra=""):
    obs = obs if obs is not None else pub["observations"]
    return f"""{pub['header']}
Below are observed runs of one system. Each state is followed by the state the system produced from it, one time step later.

{_runs(obs)}
{extra}
{_code_note(pub)}

Answer all five parts:
T1. Do these observations appear to arise from a stable underlying rule, or are they adequately explained as unstructured/random given the information here?
T2. For each of these states (not seen above), predict the state the system produces next:
{chr(10).join(f'Q{i + 1}: {q}' for i, q in enumerate(pub['t2_queries']))}
T3. Predict the result of these interventions:
{_interventions(pub['t3_interventions'])}
T4. Identify any quantity, relation, equivalence class or structure that appears preserved or constrained. Give executable claims where you can.
T5. Write the shortest Python function step(s) that you believe reproduces the system (returns the next state as a list).

Return one JSON object:
{{"t1": {{"verdict": "RULE" | "RANDOM" | "UNCERTAIN", "confidence": <0..1>, "evidence": "...", "uncertainty": "...", "discriminating_observation": "..."}},
 "t2": {{"predictions": ["<state>", ... one per query, in order]}},
 "t3": {{"predictions": [["<state>", "<state>", "<state>"], ... one list per intervention]}},
 {T4_SPEC},
 "t5": {{"code": "def step(s):\\n    ..."}}}}
Write states exactly in the notation used above."""


def familiarity(pub):
    return f"""{pub['header']}
Below are observed runs of one system. Each state is followed by the state the system produced from it, one time step later.

{_runs(pub['observations'])}

{_code_note(pub)}

Questions:
1. Is this system coherent (a lawful mechanism), incoherent/arbitrary, or unclear?
2. Does it resemble any known mechanism, theory, algorithm, or named family? If so, which, how confident are you, is it equivalent to it or only partly similar, and how does it differ?
3. If you named something in 2, write step(s) implementing that named mechanism as it would apply to this system.

Return one JSON object:
{{"coherence": "COHERENT" | "INCOHERENT" | "UNCLEAR", "coherence_reason": "...",
 "familiar": "YES" | "NO", "analogy": "<name or null>", "confidence": <0..1>,
 "claimed_equivalence": "EXACT" | "PARTIAL" | "SUPERFICIAL" | "NONE", "differences": "...",
 "analogy_code": "<def step(s): ... or null>"}}"""


def reveal(pub, rule_text):
    return f"""{pub['header']}
This is the exact update rule of a system:

{rule_text}

Some observed runs, for reference:
{_runs(pub['observations'][:3])}

{_code_note(pub)}

Answer:
A. Is this system coherent (a lawful mechanism), incoherent/arbitrary, or unclear?
B. What properties follow from the rule? Give executable claims (T4 format below).
C. For each of these states, give the state the system produces next:
{chr(10).join(f'Q{i + 1}: {q}' for i, q in enumerate(pub['t2_queries']))}
D. Predict the result of these interventions:
{_interventions(pub['t3_interventions'])}
E. Which kinds of intervention would change the system's long-run behaviour most, and why?

Return one JSON object:
{{"coherence": "COHERENT" | "INCOHERENT" | "UNCLEAR", "coherence_reason": "...",
 {T4_SPEC},
 "t2": {{"predictions": ["<state>", ...]}},
 "t3": {{"predictions": [["<state>", "<state>", "<state>"], ...]}},
 "interventions_that_matter": "..."}}"""


def pair(pub_a, pub_b):
    return f"""Two systems, A and B, of the same kind. For each you see observed runs (each state followed by the next state).

SYSTEM A. {pub_a['header']}
{_runs(pub_a['observations'])}

SYSTEM B. {pub_b['header']}
{_runs(pub_b['observations'])}

Which system shows stronger evidence of a compact lawful mechanism (a rule that could be stated briefly and would predict new states)?

Return one JSON object:
{{"choice": "A" | "B", "confidence": <0..1>, "reason": "..."}}"""


ACTIVE_INTRO = """{header}
You can experiment on one system. You have already seen these runs (each state followed by the next):

{runs}

You may make up to {budget} experiments, one per turn. Each experiment is one of:
  {{"query": "run", "start": "<state>", "steps": <1..6>}}
  {{"query": "clamp", "start": "<state>", "position": <int>, "value": <int>, "steps": <1..6>}}
     (position forced to value at the start and after every step)
  {{"query": "done"}}   when you have seen enough.
Reply with exactly one JSON object per turn: your next experiment."""


def active_turn(pub, runs, history, budget_left):
    head = ACTIVE_INTRO.format(header=pub["header"], runs=_runs(runs), budget=budget_left + len(history))
    hist = "\n".join(f"Experiment {i + 1}: {h['query']}\nResult: {h['result']}" for i, h in enumerate(history))
    tail = (f"\n\nExperiments so far:\n{hist}" if history else "") + \
           f"\n\nYou have {budget_left} experiment(s) left. Your next experiment (JSON only):"
    return head + tail


def active_final(pub, runs, history):
    nl = chr(10)
    hist = nl.join(f"Experiment {i + 1}: {h['query']}{nl}Result: {h['result']}"
                   for i, h in enumerate(history))
    extra = (nl + "You also ran these experiments:" + nl + hist + nl) if hist else ""
    return blind(pub, obs=runs, extra=extra)


_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
          "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
          "seventeen", "eighteen", "nineteen", "twenty", "twenty-one", "twenty-two",
          "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven",
          "twenty-eight", "twenty-nine", "thirty"]
_ORD = ["first", "second", "third", "fourth", "fifth", "sixth"]


def _prose_state(st):
    if " " not in st:                                   # symbol strings
        return "the symbols read " + ", then ".join(st)
    vals = st.split()
    return "; ".join(f"the {_ORD[i]} quantity is {_WORDS[int(v)]}" for i, v in enumerate(vals))


def prose_t2(pub):
    """Representation ablation: the same observations and T2 queries told in
    words instead of the tuple notation. Answers still in tuple notation."""
    runs = []
    for i, t in enumerate(pub["observations"]):
        steps = ". Next, ".join(_prose_state(s) for s in t)
        runs.append(f"In run {i + 1}: at first, {steps}.")
    qs = "\n".join(f"Q{i + 1}: {_prose_state(q)} (written {q})" for i, q in enumerate(pub["t2_queries"]))
    return f"""{pub['header']}
Here is what one system did, told in words. In each run, each description is followed by the state the system produced from it, one time step later.

{chr(10).join(runs)}

For each of these states, predict the state the system produces next:
{qs}

Return one JSON object: {{"t2": {{"predictions": ["<state in the written notation>", ... one per query]}}}}"""
