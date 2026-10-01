"""PROPOSAL ONLY -- not wired into any runner. scrub.py (v1) stays the frozen
instrument for meta v1; this file is the candidate replacement for v2 and must
be adopted by a preregistration, not by import.

Why: v1's ACRONYM rule ([A-Z][A-Z0-9]+) masks every all-caps token, so
rewrite rules, state names, indexed variables and logic operators are erased
("YZ -> XW" -> "[X] -> [X]", "L1 penalty" -> "[X] penalty", "AND-gated" ->
"[X]-gated"); field names are matched case-insensitively with an automatic
singular, so "avalanche statistics" / "sufficient statistic" / "logic gate"
lose words that name no discipline; the novelty list deletes "new", "novel",
"unique" wherever they occur, changing claims ("transfers to novel tasks" ->
"transfers to tasks", "a unique attractor" -> "a attractor").
See roles/Hecate/harvest_w2/INV_G_scrubber_damage.md.

What v2 masks (the intended targets of v1, kept):
  * every dictionary concept name, hyphen/space/plural variants, any case;
  * the v1 eponym/stem list;
  * field names: multi-word fields in any case; single-word fields only when
    Capitalised (proper-noun use: "Physics", not "physics of avalanches");
    no automatic singular for -ics words ("Statistics" -/-> "statistic");
  * acronyms ONLY if they abbreviate a dictionary concept / listed eponym
    (CONCEPT_ACRONYMS) or are coined in the same text as
    "Capitalised Invented Name (ACRO)"; the coined ACRO is then masked
    everywhere in that text;
  * hype words only (novel/new as an adjective of the proposal itself).
What v2 never touches: single letters, indexed symbols (X1, N0, L2),
two-letter state/rule names (AB, YZ -> XW), logic operators (AND, XOR),
technical acronyms that name no concept (DAG, KL, PCA, SVD, STDP...).

Idempotent: scrub_v2(scrub_v2(t)) == scrub_v2(t) (v1 would turn "[NAME]"
into "[[X]]" on a second pass; harmless in v1 only because COINAGE never fired).

    python -m hecate.meta.scrub_v2_proposal test       # unit tests
    python -m hecate.meta.scrub_v2_proposal compare    # v1 vs v2 on arms_v1.jsonl
"""

from __future__ import annotations

import functools
import json
import os
import re
import sys

from hecate.meta.scrub import EPONYMS_AND_STEMS, MASK, vocab

NAME_MASK = "[NAME]"
HYPE = re.compile(
    r"(?<![A-Za-z])(?:unprecedented|groundbreaking|innovative|revolutionary|first-ever"
    r"|(?:novel|new)(?=\s+(?:mechanisms?|approach(?:es)?|methods?|frameworks?|paradigms?"
    r"|architectures?|ideas?|principles?|insights?|theor(?:y|ies)|class(?:es)? of)\b))"
    r"(?![A-Za-z])", re.I)

# Abbreviations of dictionary concepts / listed eponyms. >=3-letter initialisms
# are generated; 2-letter ones collide with symbols and are curated by hand.
CURATED_ACRONYMS = ("RL", "KC", "GA", "QM", "CA", "ToM", "TOM", "RG", "SAT", "UNSAT",
                    "MaxSAT", "BTW", "HJB", "SAE", "FFT", "DWT", "CWT", "MaxEnt")
_STOP = {"of", "the", "and"}


def _initials(name):
    return "".join(w[0].upper() for w in re.split(r"[\s-]+", name) if w.lower() not in _STOP)


@functools.lru_cache(maxsize=1)
def concept_acronyms():
    names, fields = vocab()
    gen = {_initials(n) for n in list(names) + list(fields)}
    return tuple(sorted({a for a in gen if len(a) >= 3} | set(CURATED_ACRONYMS)))


def _variants(term, singularise=True):
    out = {term, term.replace("-", " "), term.replace(" ", "-")}
    for t in list(out):
        if t.endswith("ics"):
            continue  # Statistics/Physics/Economics: no fake singular
        if t.endswith("s") and not t.endswith("ss"):
            if singularise:
                out.add(t[:-1])
        else:
            out.add(t + "s")
    return out


def _alt(terms):
    return "|".join(sorted((re.escape(t) for t in terms), key=len, reverse=True))


@functools.lru_cache(maxsize=1)
def _patterns():
    names, fields = vocab()
    ci = set()
    for t in list(names) + list(EPONYMS_AND_STEMS):
        ci |= _variants(t)
    cs = set()
    for f in fields:
        (ci if " " in f else cs).update(_variants(f))
    p_ci = re.compile(r"(?<![A-Za-z])(?:" + _alt(ci) + r")(?![A-Za-z])", re.I)
    # single-word fields: Capitalised only (Physics, PHYSICS), never lower-case
    p_cs = re.compile(r"(?<![A-Za-z])(?:" + _alt(cs | {c.upper() for c in cs}) + r")(?![A-Za-z])")
    acr = concept_acronyms()
    p_acr = re.compile(r"(?<![A-Za-z0-9_])(?:" + _alt(acr) + r")s?(?![A-Za-z0-9_])")
    return p_ci, p_cs, p_acr


COINAGE = re.compile(r"((?:[A-Z][\w-]*\s+){1,7})\(\s*([A-Z][A-Za-z0-9-]{1,})\s*\)")


def _coinage(text):
    """Mask "Capitalised Invented Name (ACRO)" only when ACRO is built from the
    initials of the preceding capitalised words (an actual coinage), then
    mask the coined ACRO wherever else it occurs. Returns (text, acros)."""
    acros = []

    def rep(m):
        words = [w for w in re.split(r"[\s-]+", m.group(1).strip()) if w]
        acro = m.group(2)
        letters = "".join(c for c in acro if c.isupper())
        for k in range(len(words), 1, -1):  # longest tail whose initials match
            tail = words[-k:]
            if "".join(w[0].upper() for w in tail if w.lower() not in _STOP) == letters:
                head = m.group(1)[: len(m.group(1).rstrip())]
                idx = head.rfind(tail[0])
                acros.append(acro)
                return m.group(1)[:idx] + NAME_MASK
        return m.group(0)

    t = COINAGE.sub(rep, text)
    for a in acros:
        t = re.sub(r"(?<![A-Za-z0-9_\[])" + re.escape(a) + r"s?(?![A-Za-z0-9_\]])", NAME_MASK, t)
    return t, acros


def scrub_v2(text: str, indexed: bool = False) -> str:
    """indexed=True (optional, for the PREREG to choose): each distinct masked
    term gets its own stable tag [X1], [X2], ... within one text, so relations
    between masked terms survive ("SAT/UNSAT threshold" -> "[X1]/[X2] threshold"
    instead of "[X]/[X] threshold") without revealing which terms they were."""
    p_ci, p_cs, p_acr = _patterns()
    t, _ = _coinage(text)
    tags = {}

    def rep(m):
        if not indexed:
            return MASK
        key = m.group(0).lower().replace("-", " ").rstrip("s")
        tags.setdefault(key, f"[X{len(tags) + 1}]")
        return tags[key]

    t = p_ci.sub(rep, t)
    t = p_cs.sub(rep, t)
    t = p_acr.sub(rep, t)
    t = HYPE.sub("", t)
    return re.sub(r"[ \t]{2,}", " ", t)


def check_v2(text: str) -> list[str]:
    """Fail-closed leak check matching v2's policy: every concept name and
    multi-word field in any case; single-word fields when Capitalised;
    concept acronyms. (v1 check() would also flag lower-case 'statistics',
    'logic', 'physics' -- that is the deliberate policy change.)"""
    names, fields = vocab()
    low = text.lower()
    leaks = [n for n in list(names) + [f for f in fields if " " in f]
             if re.search(r"(?<![a-z])" + re.escape(n.lower()) + r"(?![a-z])", low)]
    leaks += [f for f in fields if " " not in f
              and re.search(r"(?<![A-Za-z])(?:" + re.escape(f) + "|" + re.escape(f.upper()) + r")(?![A-Za-z])", text)]
    leaks += [a for a in concept_acronyms()
              if re.search(r"(?<![A-Za-z0-9_])" + re.escape(a) + r"s?(?![A-Za-z0-9_])", text)]
    return leaks


# ---------------------------------------------------------------- tests ----

def _tests():
    s = scrub_v2
    cases_preserve = [
        "rule YZ -> XW applied to every adjacent pair",
        "A -> AB, B -> A (a rewrite system on states A and B)",
        "pulses in either order AB or BA across trials",
        "minimise reconstruction error plus an L1 penalty; compare to L2",
        "variables X1..Xn on a DAG; truncate to size N1 < N0",
        "parity checks over GF(q) with HG^T = 0",
        "solve NOT and AND, then XOR, then NAND sub-functions",
        "KL divergence, PCA and SVD baselines, STDP and LTP/LTD windows",
        "avalanche statistics; a sufficient statistic; a logic gate",
        "the physics of avalanches",
        "transfers to novel tasks; a new cell is born; a unique attractor",
        "states S1, S2 and the WAIT state; the ORDER of closure",
    ]
    for c in cases_preserve:
        assert s(c) == c, (c, s(c))
    cases_mask = [
        ("a Self-Organized Criticality lattice (SOC) near threshold", "SOC"),
        ("Hebbian learning with a Kalman filter", "Hebbian"),
        ("we used Reinforcement Learning (RL) and MCTS rollouts", "MCTS"),
        ("a SAT instance; UNSAT cores; the BTW sandpile", "SAT"),
        ("As a researcher in Statistical Physics I propose", "Statistical Physics"),
        ("From Physics and Biology we borrow", "Physics"),
        ("statistical physics of spin glasses", "statistical physics"),
        ("Gene Regulatory Networks (GRNs) and GRN motifs", "GRN"),
        ("this novel mechanism is groundbreaking", "novel"),
        ("Error Correcting Codes and error-correcting code words", "rror"),
    ]
    for c, gone in cases_mask:
        out = s(c)
        assert gone not in out, (c, out)
        assert not check_v2(out), (c, out, check_v2(out))
    # coinage: invented name + its acronym, later re-use masked; non-coinage parens kept
    out = s("We call it Stochastic Cascade Network (SCN). The SCN fires. Data (N) stays.")
    assert "Stochastic" not in out and "SCN" not in out and "Data (N)" in out, out
    out = s("Each Step (S1) is logged; Null Twin (NT) differs.")
    assert "(S1)" in out, out  # S1 is not the initials of 'Each Step'
    # idempotence
    for c in cases_preserve + [x for x, _ in cases_mask]:
        assert s(s(c)) == s(c), c
    # indexed placeholders keep relations between masked terms
    out = s("sweep across the SAT/UNSAT threshold; SAT instances", indexed=True)
    assert out == "sweep across the [X1]/[X2] threshold; [X1] instances", out
    assert s(out, indexed=True) == out
    # the v1 defect itself, for the record
    from hecate.meta.scrub import scrub
    assert scrub("YZ -> XW") == "[X] -> [X]"
    assert scrub_v2("YZ -> XW") == "YZ -> XW"
    print("scrub_v2_proposal: all tests passed")


# -------------------------------------------------------------- compare ----

def _compare():
    from hecate.meta.scrub import check, mechanism_text, scrub
    here = os.path.dirname(os.path.abspath(__file__))
    keys = ("statement", "what_exists", "what_changes", "what_persists",
            "what_is_selected", "what_can_reproduce", "what_can_learn",
            "what_can_transfer", "distinguishing_observable", "minimal_world")
    word = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")
    stats = {}
    v2_leaks, v1check_on_v2 = [], {}
    with open(os.path.join(here, "arms", "arms_v1.jsonl"), encoding="utf-8") as fh:
        arms = [json.loads(l) for l in fh if l.strip()]
    for a in arms:
        for j, m in enumerate(a["mechanisms"]):
            parts = []
            for k in keys:
                v = m.get(k)
                if isinstance(v, list):
                    v = "; ".join(str(x) for x in v)
                if v:
                    parts.append(f"{k.replace('_', ' ')}: {v}")
            raw = "\n".join(parts)
            v1, v2 = scrub(raw), scrub_v2(raw)
            assert v1 == mechanism_text(m)
            nraw = len(word.findall(raw))
            st = stats.setdefault(a["arm"], {"n": 0, "v1_X": 0, "v2_X": 0, "v1_words_lost": 0,
                                             "v2_words_lost": 0, "raw_words": 0, "v2_identical_raw": 0})
            st["n"] += 1
            st["raw_words"] += nraw
            for tag, t in (("v1", v1), ("v2", v2)):
                st[f"{tag}_X"] += t.count(MASK) + t.count(NAME_MASK)
                kept = len(word.findall(t.replace(MASK, " ").replace(NAME_MASK, " ")))
                st[f"{tag}_words_lost"] += nraw - kept
            st["v2_identical_raw"] += v2 == raw
            item = f"u{a['unit']}-{a['arm']}-m{j}"
            if check_v2(v2):
                v2_leaks.append((item, check_v2(v2)))
            c1 = check(v2)
            if c1:
                v1check_on_v2[item] = c1
    print("arm  n  v1_masks v2_masks  v1_words_lost% v2_words_lost%  v2_untouched")
    for arm in "TPSOG":
        st = stats[arm]
        print(arm, st["n"], st["v1_X"], st["v2_X"],
              round(100 * st["v1_words_lost"] / st["raw_words"], 2),
              round(100 * st["v2_words_lost"] / st["raw_words"], 2), st["v2_identical_raw"])
    print("check_v2 leaks:", len(v2_leaks), v2_leaks[:5])
    from collections import Counter
    print("v1 check() hits on v2 output (deliberate policy change):", len(v1check_on_v2),
          Counter(x for v in v1check_on_v2.values() for x in v))


if __name__ == "__main__":
    {"test": _tests, "compare": _compare}[sys.argv[1] if len(sys.argv) > 1 else "test"]()
