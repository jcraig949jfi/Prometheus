"""Deterministic failure signatures, and the normalizations they need.

Hermes, 2026-09-11. Companion to observations.json and probe.py.

THE RULE THIS MODULE OBEYS. A signature is computed from what an observer
HAS AT THE POINT OF FAILURE and from nothing else. It may read the
exception type, the message, the exit state and the command. It may NOT
read a diagnosis, a root cause, an owner, a fix, or anything a seat only
learns afterwards. An agent must be able to record a symptom without
knowing why it happened; the moment a signature needs the cause, the
mechanism is useless, because the second observer would have to solve the
problem before discovering that the first observer already had.

Every normalization below is:
  * explicit      -- it is a named rule with a stated justification
  * deterministic -- same input, same output, on any machine, in any process
  * symptom-only  -- it never consults a diagnosis
  * reversible in evidence -- the raw observation is kept beside the key,
    so a wrong merge can be audited and split later

NORMALIZATIONS, each earned by a measured case (see probe.py output):

  N1 identifier-tail
     Schema-qualified identifiers keep the schema and lose the final
     segment: comms.messages -> comms.*, comms.agents -> comms.*
     EARNED BY case A, where five observers produced THREE different raw
     messages for one cause because `sync` touches comms.messages, `boot`
     and `who` touch comms.agents. Which table the code reached first is
     an irrelevant parameter of the observer, not of the failure.
     RISK, and it is real: two genuinely different failures inside one
     schema collapse. Bounded by keeping the schema and the exception
     type, and by the split affordance (see incident.py).

  N2 seat-name
     Any token equal to a seat name (roles/*) becomes <SEAT>.
     EARNED BY case B, where seven observers produced seven raw messages
     differing only in their own name. The observer's identity is never
     part of the failure's identity; it is the thing an incident collects,
     not the thing it is keyed by.

  N3 quantity
     Runs of digits become '#'.
     EARNED BY case D's tick counts (354, 160) and by paths that embed a
     date or an id. A count is a measure of how long a failure went
     unnoticed, never of which failure it is.

  N4 path-tail
     An absolute path becomes repository-relative where it can be done by
     string rule alone; a trailing filename after a mandated directory is
     dropped (roles/Vivarium/journal/2026-09-11.md -> roles/*/journal/).
     EARNED BY case C, where the same contract defect appears at two
     different .gitignore lines for two different directories.
     RISK: this is the weakest rule and probe.py shows it FAILING to
     converge case C anyway, for a reason worth reading.

WHAT IS DELIBERATELY NOT HERE: no fuzzy matching, no edit distance, no
embedding, no LLM. Every key is a sha256 over a tuple of strings. Two
observers compute the same key or they do not, and the probe reports which.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REPO = Path(__file__).resolve().parents[4]

_QUOTED_IDENT = re.compile(r'"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)"')
_BARE_IDENT = re.compile(r"\b([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\b")
_DIGITS = re.compile(r"\d+")
_SEAT_IN_QUOTES = re.compile(r"'([A-Za-z][A-Za-z0-9_-]*)'")


def seat_names() -> List[str]:
    d = REPO / "roles"
    if not d.is_dir():
        return []
    return sorted(p.name for p in d.iterdir() if p.is_dir() and p.name != "base-role")


# --------------------------------------------------------------- rules ---
def n1_identifier_tail(text: str) -> str:
    text = _QUOTED_IDENT.sub(lambda m: '"{}.*"'.format(m.group(1)), text)
    return _BARE_IDENT.sub(lambda m: "{}.*".format(m.group(1)), text)


def n2_seat_name(text: str, seats: Optional[Iterable[str]] = None) -> str:
    known = set(seats if seats is not None else seat_names())

    def sub(m):
        return "'<SEAT>'" if m.group(1) in known else m.group(0)

    return _SEAT_IN_QUOTES.sub(sub, text)


def n3_quantity(text: str) -> str:
    return _DIGITS.sub("#", text)


def n4_path_tail(text: str) -> str:
    text = text.replace("\\", "/")
    text = re.sub(r"roles/[A-Za-z][A-Za-z0-9_-]*/", "roles/*/", text)
    text = re.sub(r"roles/\*/(journal|archive|superseded|ops|ledgers|calibration|science|prompts)/[^\s]*",
                  r"roles/*/\1/", text)
    return text


RULES = {"N1": n1_identifier_tail, "N2": n2_seat_name, "N3": n3_quantity, "N4": n4_path_tail}


# ---------------------------------------------------------- strategies ---
def _key(parts: Iterable[str]) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def s0_raw(obs: Dict[str, Any]) -> str:
    """Everything, verbatim. The null strategy: what you get if you hash the
    observation as recorded."""
    return _key(["s0", obs.get("exception_type", ""), obs.get("message", ""),
                 obs.get("exit_state", "")])


def s1_type_only(obs: Dict[str, Any]) -> str:
    """The opposite extreme: exception type and exit state, no message.
    Included to show over-merge, not as a proposal."""
    return _key(["s1", obs.get("exception_type", ""), obs.get("exit_state", "")])


def s2_normalized(obs: Dict[str, Any], rules: Iterable[str] = ("N1", "N2", "N3", "N4"),
                  seats: Optional[Iterable[str]] = None) -> str:
    """The candidate. Exception type + exit state + the message put through
    the named rules, in a fixed order."""
    msg = obs.get("message", "")
    for r in rules:
        msg = RULES[r](msg, seats) if r == "N2" else RULES[r](msg)
    return _key(["s2", obs.get("exception_type", ""), obs.get("exit_state", ""), msg])


def s3_normalized_with_missing_input(obs: Dict[str, Any], seats: Optional[Iterable[str]] = None) -> str:
    """s2 plus the named missing input, when the observation carries one.
    This is what SPLITS case D back into four incidents, which is the
    correct answer for case D and the reason it is offered separately."""
    base = s2_normalized(obs, seats=seats)
    mi = obs.get("missing_input")
    return _key(["s3", base, str(mi)]) if mi is not None else _key(["s3", base])


def s4_whole_observation(obs: Dict[str, Any], seats: Optional[Iterable[str]] = None) -> str:
    """Hash the WHOLE observation: every key it carries, sorted, with the same
    named normalizations applied to every string value.

    Added 2026-09-11 for HERMES-32 and applied uniformly to before, after and
    ablation. It exists so that adding a field to an observation changes the
    key by the SAME rule for everyone, and so that no field can be hand-picked
    after seeing a result -- the objection s2 would otherwise invite, since s2
    reads three named keys and an instrument adds new ones.

    A field whose value is None is dropped, so removing a field and setting it
    to None are the same ablation."""
    parts = []
    for k in sorted(obs):
        v = obs[k]
        if v is None:
            continue
        if isinstance(v, str):
            for r in ("N1", "N2", "N3", "N4"):
                v = RULES[r](v, seats) if r == "N2" else RULES[r](v)
        parts.append("{}={}".format(k, v))
    return _key(["s4"] + parts)


STRATEGIES = {
    "s0_raw": s0_raw,
    "s1_type_only": s1_type_only,
    "s2_normalized": s2_normalized,
    "s3_normalized_plus_input": s3_normalized_with_missing_input,
    "s4_whole_observation": s4_whole_observation,
}


def load_cases(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    p = path or (Path(__file__).resolve().parent / "observations.json")
    return json.loads(p.read_text(encoding="utf-8"))["cases"]
