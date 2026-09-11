"""The minimum primitive: record a failure and get back what is already known.

Hermes, 2026-09-11. Stdlib only, no service, no schema, no judge, no model.

THE ONE FUNCTION THAT MATTERS

    prior = record(observation, observer=..., signature=...)

It looks the signature up, appends this observation to the existing record if
there is one, creates the record if there is not, and RETURNS the observations
that were already there. The lookup is not something the seat has to remember
to do; it is the same call as the write. That is the whole mechanism, and it
is the answer to "what is the minimum primitive needed so the second observer
discovers the first observer's evidence before creating another record".

THREE PROPERTIES IT MUST HAVE, each earned by the probe

  1. INDEPENDENCE. Convergence must not turn five observations into one
     observation. Every observer's record is appended verbatim as its own
     block and is never rewritten, merged, summarised or averaged. The file
     holds 1 incident and N observations. observations() returns them
     separately and byte-equal to what was written.

  2. SPLITTABILITY. probe.py CTL-2 shows a symptom key can name a symptom
     with more than one cause. An incident is therefore a HYPOTHESIS that
     these observations share a cause, not an assertion of it. split() moves
     a named subset into a new record and leaves a pointer in both
     directions. Without this, symptom-level convergence would be a way of
     burying a second failure inside the first.

  3. INTENT IS NOT IDENTITY. An observation may carry `intent` (what the
     caller meant to be doing: which environment it asked for, whether this
     target was permitted). The signature NEVER reads it. Identity answers
     WHERE you were; intent answers WHETHER being there was allowed. The
     same physical target is a sandbox for one caller and a catastrophe for
     another, and collapsing the two questions would make the sandbox
     unusable or the catastrophe invisible.

WHAT THIS IS NOT: an incident system. There is no status field, no assignee,
no severity, no workflow, no lifecycle beyond the file existing. Those are
the bureaucracy the brief forbids, and none of them is needed to make the
N+1th discovery cheaper than the first.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DIR = Path(os.environ.get("PROMETHEUS_INCIDENTS", "roles/Hermes/incidents"))
_BLOCK = re.compile(r"^<!--obs (\{.*?\})-->$", re.M)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def path_for(signature: str, root: Optional[Path] = None) -> Path:
    if not re.fullmatch(r"[0-9a-f]{8,64}", signature):
        raise ValueError("signature must be lowercase hex, 8-64 chars: {!r}".format(signature))
    return (root or DEFAULT_DIR) / "{}.md".format(signature)


def observations(signature: str, root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Every observation on this incident, in the order recorded, each exactly
    as its observer wrote it. Never a summary."""
    p = path_for(signature, root)
    if not p.exists():
        return []
    return [json.loads(m.group(1)) for m in _BLOCK.finditer(p.read_text(encoding="utf-8"))]


def _fingerprint(observer: str, observed: Dict[str, Any]) -> str:
    return hashlib.sha256((observer + "|" + json.dumps(observed, sort_keys=True))
                          .encode("utf-8")).hexdigest()[:12]


def record(observed: Dict[str, Any], *, observer: str, signature: str,
           title: str = "", intent: Optional[Dict[str, Any]] = None,
           source: str = "", root: Optional[Path] = None) -> Dict[str, Any]:
    """Append this observation to the incident for `signature`, creating it if
    needed. Returns {"new": bool, "path": str, "prior": [...], "count": int}.

    `prior` is what the caller most needs and is the reason this is one call
    and not two: the second observer is handed the first observer's evidence
    as the return value of recording its own.
    """
    p = path_for(signature, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    prior = observations(signature, root)
    fp = _fingerprint(observer, observed)
    if any(o.get("fingerprint") == fp for o in prior):
        return {"new": False, "path": str(p), "prior": prior, "count": len(prior),
                "duplicate": True}
    entry = {"observer": observer, "at": _now(), "observed": observed,
             "fingerprint": fp, "source": source}
    if intent is not None:
        entry["intent"] = intent            # recorded, never signed over
    is_new = not p.exists()
    if is_new:
        p.write_text(
            "# INCIDENT {sig}{t}\n\n"
            "One file per failure SIGNATURE. Each block below is one observer's\n"
            "own record, appended verbatim and never rewritten: this file holds\n"
            "1 incident and N independent observations.\n\n"
            "A signature names a SYMPTOM. That these observations share a cause\n"
            "is a hypothesis; if it turns out they do not, split the incident\n"
            "(record.split) rather than deleting anyone's evidence.\n\n"
            "## OBSERVATIONS\n\n".format(sig=signature, t=(" -- " + title) if title else ""),
            encoding="utf-8")
    with p.open("a", encoding="utf-8") as fh:
        fh.write("<!--obs {}-->\n".format(json.dumps(entry, sort_keys=True)))
        fh.write("- {at}  {observer}  {summary}{src}\n".format(
            at=entry["at"], observer=observer,
            summary=str(observed.get("message", ""))[:100],
            src=("  [{}]".format(source) if source else "")))
    return {"new": is_new, "path": str(p), "prior": prior, "count": len(prior) + 1,
            "duplicate": False}


def split(signature: str, *, observers: List[str], new_signature: str, reason: str,
          root: Optional[Path] = None) -> Dict[str, Any]:
    """Move the named observers' observations to `new_signature`, leaving a
    pointer in both files. Evidence is moved, never dropped."""
    src, dst = path_for(signature, root), path_for(new_signature, root)
    if not src.exists():
        raise FileNotFoundError(str(src))
    keep, moved = [], []
    for o in observations(signature, root):
        (moved if o["observer"] in observers else keep).append(o)
    if not moved:
        raise ValueError("no observations to move for {}".format(observers))
    text = src.read_text(encoding="utf-8")
    head = text.split("## OBSERVATIONS", 1)[0] + "## OBSERVATIONS\n\n"
    src.write_text(head, encoding="utf-8")
    with src.open("a", encoding="utf-8") as fh:
        for o in keep:
            fh.write("<!--obs {}-->\n".format(json.dumps(o, sort_keys=True)))
            fh.write("- {}  {}  {}\n".format(o["at"], o["observer"],
                                             str(o["observed"].get("message", ""))[:100]))
        fh.write("\n## SPLIT {}\n\n{}\nMoved to {}: {}\n".format(
            _now(), reason, new_signature, ", ".join(observers)))
    for o in moved:
        record(o["observed"], observer=o["observer"], signature=new_signature,
               title="split from {}".format(signature), source=o.get("source", ""), root=root)
    with dst.open("a", encoding="utf-8") as fh:
        fh.write("\n## ORIGIN\n\nSplit from incident {} on {}: {}\n".format(
            signature, _now(), reason))
    return {"moved": [o["observer"] for o in moved], "kept": [o["observer"] for o in keep],
            "from": str(src), "to": str(dst)}
