"""Every string the frozen reasoner is ever shown. RESTORED 2026-08-23.

Isolated in one module so the guard suite can scan the *rendered* text of every
condition for ontology leakage. Nothing here may name the hidden family.

Deliberate shared prior: the "look for interchangeable sequences" hint is given
IDENTICALLY in C0-C3. Otherwise a substrate arm would win merely by being told
what kind of thing to look for. Those conditions test EXPLOITATION of a hypothesis
class, not INVENTION of one. C4 is the exception and withholds the hint.
"""
from __future__ import annotations

from typing import List, Sequence

CONTEXT_CHAR_BUDGET = 24_000
MAX_NOTE_CHARS = 800
C4_BUDGET_BYTES = 200

_HINT = (
    "A useful thing to hunt for: two different item sequences that behave "
    "interchangeably, meaning you can swap one for the other at any point "
    "without changing anything the system shows afterwards. Short stand-ins "
    "for longer sequences are the most valuable find."
)


def system_prompt(uni, len_lo: int = 8, len_hi: int = 12,
                  hint: bool = True) -> str:
    """The query length range MUST match EvalSet's. It said 8-14 while EvalSet
    generated 8-12 for several iterations, so every arm was told a wrong range;
    it is passed in now and a guard asserts the two agree."""
    return (
        "You are probing an unfamiliar system. Nothing about how it works has "
        "been disclosed to you and nobody will explain it. What the system "
        "returns is your only source of information.\n\n"
        "THE ONLY COMMAND\n"
        "  RUN <tag> <items>\n"
        f"  tag is one of: {' '.join(uni.tags)}\n"
        f"  items is a sequence of 1 to {uni.spec.max_word_len} entries drawn "
        f"from: {' '.join(uni.actions)} (repeats allowed)\n"
        f"  the system replies with len(items)+1 readouts, each one of: "
        f"{' '.join(uni.symbols)}\n"
        "  the first readout is what the system shows for the tag by itself; "
        "readout number i+1 is what it shows once the first i entries have "
        "been fed in.\n\n"
        "YOUR OBJECTIVE\n"
        "Later you will be asked to name the FINAL readout for entry sequences "
        f"of length {len_lo} to {len_hi} that you will NOT be permitted to run. "
        "Guessing is 1 in 4. Find whatever regularity lets you beat that.\n\n"
        + (_HINT + "\n\n" if hint else "")
        + "Answer with JSON only. No prose outside the JSON."
    )


# C1 supplies a MOTIVE to speculate, not merely permission. C1N is the same
# demand with the incentive stripped, so the pair brackets that confound.
# Measured: C1 emitted 1.00 claims/turn, C1N 1.57 — the incentive adds nothing,
# so C1N is the cleaner instrument.
C1_DEMAND = (
    "\nREQUIRED THIS TURN: you must include at least one claim. It must be one "
    "that would be USEFUL IF TRUE and that is not already established by the "
    "confirmed list above. Guessing is explicitly permitted and expected: a "
    "claim you are unsure of is worth more than no claim, because the system "
    "itself will settle it and a wrong claim costs you only the check. Do not "
    "repeat something you have already run. Assert something you have not.\n"
)

C1_NEUTRAL = (
    "\nREQUIRED THIS TURN: include at least one claim that is not already "
    "established by the confirmed list above. The system will check it.\n"
)

C3_OFFER = (
    "\nCANDIDATES DRAWN FROM YOUR OWN RECORDS. Each pair below has behaved the "
    "same way everywhere you have seen it so far. You did not have to find "
    "these. Put the ones you judge worth checking into `claims` and the system "
    "will settle them. Leave out the ones you think are coincidence.\n{cands}\n"
)


def render_candidates(cands: Sequence, limit: int = 20) -> str:
    if not cands:
        return "  (none available yet)"
    return "\n".join(f"  {i}: {' '.join(l)}  ==  {' '.join(r) or '(nothing)'}"
                     for i, (l, r) in enumerate(cands[:limit]))


def explore_user(arm: str, uni, budget_left: int, turn: int, turns: int,
                 runs_this_turn: int, context_block: str,
                 condition: str = "C0", candidates: Sequence = ()) -> str:
    head = (f"Probing turn {turn} of {turns}. You may issue up to "
            f"{runs_this_turn} RUN commands now (remaining overall allowance: "
            f"{budget_left}).\n")
    if context_block:
        head += "\n" + context_block + "\n"

    if arm == "P2":
        fmt = (
            "\nReply with JSON of exactly this shape:\n"
            '{"runs": [{"tag": "K0", "seq": "A1 A2 A3"}],\n'
            ' "claims": [{"lhs": "A1 A2", "rhs": "A3"}],\n'
            ' "note": "at most 700 characters, carried forward for you"}\n\n'
            "About claims: each claim asserts that lhs and rhs are "
            "interchangeable. Every claim is checked against the system itself. "
            "Checking costs part of your allowance, and a claim that fails is "
            "destroyed. Claims that survive are kept and reused later, so they "
            "are the only thing that compounds. Make rhs strictly shorter than "
            "lhs, or the same length but earlier alphabetically. rhs may be "
            "the empty string \"\" to assert that lhs does nothing."
        )
        if condition == "C1":
            fmt += C1_DEMAND
        elif condition == "C1N":
            fmt += C1_NEUTRAL
        elif condition == "C3":
            fmt += C3_OFFER.format(cands=render_candidates(candidates))
    else:
        fmt = ("\nReply with JSON of exactly this shape:\n"
               '{"runs": [{"tag": "K0", "seq": "A1 A2 A3"}], "note": "..."}\n')
    return head + fmt


def render_history(log, budget_chars: int = CONTEXT_CHAR_BUDGET) -> str:
    lines = [f"{i.tag} {' '.join(i.word)} -> {' '.join(i.readout)}" for i in log]
    out, total = [], 0
    for ln in reversed(lines):
        if total + len(ln) + 1 > budget_chars:
            break
        out.append(ln)
        total += len(ln) + 1
    out.reverse()
    dropped = len(lines) - len(out)
    head = f"EVERYTHING YOU HAVE RUN SO FAR ({len(out)} records"
    head += f", {dropped} older ones dropped for space):" if dropped else "):"
    return head + "\n" + "\n".join(out)


def render_store(store, budget_chars: int = CONTEXT_CHAR_BUDGET) -> str:
    parts: List[str] = []
    live = [r for r in store.rules.values() if r.status == "active"]
    dead = [r for r in store.rules.values() if r.status != "active"]
    live.sort(key=lambda r: (-r.passes, r.rid))
    parts.append(f"CONFIRMED INTERCHANGEABLE PAIRS ({len(live)}), each already "
                 "checked against the system:")
    for r in live:
        parts.append(f'  {r.rid}: {" ".join(r.lhs)} == '
                     f'{" ".join(r.rhs) or "(nothing)"} [confirmed x{r.passes}]')
    if not live:
        parts.append("  (none yet)")
    if dead:
        parts.append(f"\nDISPROVED BY THE SYSTEM ({len(dead)}) — do not propose again:")
        for r in dead[:40]:
            parts.append(f'  {" ".join(r.lhs)} != {" ".join(r.rhs) or "(nothing)"}')
    if store.note:
        parts.append("\nNOTE YOU LEFT YOURSELF EARLIER:\n" + store.note)
    body = "\n".join(parts)
    room = budget_chars - len(body)
    if room > 400 and store.memo:
        sample, used = [], 0
        for k in sorted(store.memo):
            tag, _, w = k.partition("|")
            ln = f'  {tag} {w or "(nothing)"} -> {store.memo[k]["sym"]}'
            if used + len(ln) + 1 > room - 200:
                break
            sample.append(ln)
            used += len(ln) + 1
        body += (f"\n\nRECORDED OUTCOMES for reduced sequences "
                 f"({len(sample)} of {len(store.memo)} shown):\n"
                 + "\n".join(sample))
    return body[:budget_chars]


def eval_user(uni, queries: Sequence, context_block: str, offset: int) -> str:
    lines = [f"  {offset + i}: {q.tag} {' '.join(q.word)}"
             for i, q in enumerate(queries)]
    head = (context_block + "\n\n") if context_block else ""
    return (head +
            "You may NOT run anything now. Name the FINAL readout for each of "
            "the following sequences.\n\n" + "\n".join(lines) +
            "\n\nReply with JSON only:\n"
            '{"answers": {"' + str(offset) + '": "q0", ...}}\n'
            f"one entry per line above, each value one of: {' '.join(uni.symbols)}.")
