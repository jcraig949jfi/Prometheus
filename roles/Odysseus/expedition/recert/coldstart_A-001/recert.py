"""recert.py -- a functional LABEL RECERTIFICATION harness (stdlib only).

Operator directive 2026-09-28 s6 ("label != capability" as an instrument): for a label L
  (1) state the behavioural property L is supposed to imply;
  (2) build an intervention that directly tests it;
  (3) test it under several environments / inputs;
  (4) keep four columns apart:
        PROVENANCE  how the label was produced ("what we called it then", copied from the record, never rewritten)
        STRUCTURAL  what the object contains (static features, cheap, no execution needed)
        BEHAVIOURAL what the object does under the test, as a pass rate over an environment set
        CAUSAL      what, when intervened on, carries the behaviour (is it the mechanism the label presumes?)

A Label is a plain spec; the engine-specific parts are five callables supplied by a per-label script:

    provenance(obj)        -> dict   must hold "label_then" (str); anything else is copied verbatim
    structural(obj)        -> dict   must hold "ok" (bool): does the object carry the structure the label presumes
    environments(obj)      -> list   environment descriptors (JSON-able)
    behavioural(obj, env)  -> dict   must hold "pass" (bool)
    causal(obj, beh)       -> dict   must hold "ok" (True / False / None = not applicable); gets the behaviour block
                                     so it can intervene in an environment where the behaviour is present

VERDICTS (one per object; the first matching rule wins)
    LABEL_PROVENANCE_ONLY               behaviour in no environment and the presumed structure absent: only the history
                                        of how the object was made supports the label
    STRUCTURE_WITHOUT_BEHAVIOUR         the presumed structure is present, the behaviour is absent in every environment
    BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM the behaviour is present somewhere, but the causal intervention shows it is not
                                        carried by the mechanism the label presumes (e.g. painting passes a copy test)
    LABEL_CONTEXT_DEPENDENT             behaviour and mechanism present, but in fewer than `min_rate` of environments
    LABEL_OK                            behaviour in >= min_rate of environments and mechanism as presumed (or n/a)
For objects that do NOT carry the label (controls), the same logic is run and the verdict is prefixed UNLABELLED_
(e.g. UNLABELLED_LABEL_OK = a capable object the labelling process missed: a false negative).

The harness never edits a historical record: every row carries `then` (the provenance block, verbatim) beside `now`
(verdict + measured columns).
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

VERDICTS = ("LABEL_OK", "LABEL_CONTEXT_DEPENDENT", "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM",
            "STRUCTURE_WITHOUT_BEHAVIOUR", "LABEL_PROVENANCE_ONLY")


@dataclass
class Label:
    name: str
    claimed_property: str                     # the behavioural property the label is supposed to imply
    expected_mechanism: str                   # what the label presumes carries it
    provenance: Callable[[Any], Dict]
    structural: Callable[[Any], Dict]
    environments: Callable[[Any], List]
    behavioural: Callable[[Any, Any], Dict]
    causal: Callable[[Any, Dict], Dict]
    obj_id: Callable[[Any], str] = str
    labelled: Callable[[Any], bool] = lambda o: True
    min_rate: float = 0.5                     # behaviour must hold in at least this share of environments for LABEL_OK
    keep_env_rows: bool = False               # store every per-environment result (large) or only a digest
    notes: Dict = field(default_factory=dict)


def verdict(structural_ok: bool, rate: float, causal_ok: Optional[bool], min_rate: float = 0.5,
            labelled: bool = True) -> str:
    if rate <= 0.0:
        v = "STRUCTURE_WITHOUT_BEHAVIOUR" if structural_ok else "LABEL_PROVENANCE_ONLY"
    elif causal_ok is False:
        v = "BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM"
    elif rate < min_rate:
        v = "LABEL_CONTEXT_DEPENDENT"
    else:
        v = "LABEL_OK"
    return v if labelled else "UNLABELLED_" + v


def recertify_one(label: Label, obj) -> Dict:
    t0 = time.time()
    prov = label.provenance(obj)
    struct = label.structural(obj)
    envs = label.environments(obj)
    res = [label.behavioural(obj, e) for e in envs]
    n_pass = sum(1 for r in res if r.get("pass"))
    rate = n_pass / len(envs) if envs else 0.0
    beh = {"n_env": len(envs), "n_pass": n_pass, "pass_rate": round(rate, 4),
           "passing_envs": [e for e, r in zip(envs, res) if r.get("pass")][:8],
           "first_pass_detail": next((r for r in res if r.get("pass")), None)}
    if label.keep_env_rows:
        beh["env_rows"] = [{"env": e, **r} for e, r in zip(envs, res)]
    beh["_all"] = list(zip(envs, res))             # handed to causal(), stripped before output
    cau = label.causal(obj, beh)
    beh.pop("_all", None)
    lab = bool(label.labelled(obj))
    v = verdict(bool(struct.get("ok")), rate, cau.get("ok"), label.min_rate, lab)
    return {"id": label.obj_id(obj), "label": label.name, "labelled": lab,
            "then": prov, "structural": struct, "behavioural": beh, "causal": cau,
            "now": v, "wall_s": round(time.time() - t0, 3)}


_G: Dict[str, Any] = {}


def _work(i):
    return recertify_one(_G["label"], _G["objs"][i])


def run(label: Label, objs: List, workers: int = 4, progress: bool = True) -> List[Dict]:
    """Recertify every object. Parallel over objects with fork (the Label's callables need not be picklable)."""
    t0 = time.time()
    if workers <= 1 or len(objs) < 8:
        rows = [recertify_one(label, o) for o in objs]
    else:
        _G["label"], _G["objs"] = label, objs
        ctx = mp.get_context("fork")
        rows = []
        with ctx.Pool(workers) as pool:
            for k, r in enumerate(pool.imap(_work, range(len(objs)), chunksize=max(1, len(objs) // (workers * 16)))):
                rows.append(r)
                if progress and (k + 1) % max(1, len(objs) // 10) == 0:
                    print("  %s: %d/%d  %.0fs" % (label.name, k + 1, len(objs), time.time() - t0), flush=True)
    return rows


def summarise(rows: List[Dict], by: Optional[Callable[[Dict], str]] = None) -> Dict:
    out = {"n": len(rows), "verdicts": dict(Counter(r["now"] for r in rows).most_common())}
    if by is not None:
        tab: Dict[str, Counter] = {}
        for r in rows:
            tab.setdefault(by(r), Counter())[r["now"]] += 1
        out["by"] = {k: dict(v.most_common()) for k, v in sorted(tab.items())}
    return out


def write(path: str, label: Label, rows: List[Dict], extra: Optional[Dict] = None) -> None:
    doc = {"label": label.name, "claimed_property": label.claimed_property,
           "expected_mechanism": label.expected_mechanism, "min_rate": label.min_rate, "notes": label.notes,
           "summary": summarise(rows), **(extra or {}), "rows": rows}
    with open(path, "w", encoding="ascii") as fh:
        json.dump(doc, fh, indent=1, sort_keys=False, default=str)


# ---- small shared measures ----------------------------------------------------------------------------------------
def dominant_share(b: bytes) -> float:
    return max(Counter(b).values()) / len(b) if b else 0.0


def entropy_bits(b: bytes) -> float:
    """Empirical Shannon entropy of the byte distribution, bits per byte (0 for a homopolymer, <= log2(len))."""
    if not b:
        return 0.0
    n = len(b)
    return -sum(c / n * math.log2(c / n) for c in Counter(b).values())


def fidelity(a: bytes, b: bytes) -> float:
    n = min(len(a), len(b))
    return sum(1 for i in range(n) if a[i] == b[i]) / max(len(a), len(b)) if n else 0.0
