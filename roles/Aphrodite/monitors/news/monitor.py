"""Deterministic core of Aphrodite's bounded RSI news monitor.

The operator's limits (2026-09-18, APHRODITE-12), preserved exactly:
weekly; inspect at most 8 candidates; admit at most 3; primary source
required; dedupe against the library; admit only if the item changes a
named theory, open question, experimental precedent, benchmark or active
design; non-admitted candidates expire after 30 days; after 4 consecutive
empty runs pause and report the pause once; owner Aphrodite.

The model only PROPOSES (pass_output.json). Everything here is
deterministic and is what actually decides.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

MAX_INSPECT = 8
MAX_ADMIT = 3
EXPIRY_DAYS = 30
BOUND_EMPTY = 4
TARGET_TYPES = ("theory", "question", "precedent", "design", "benchmark")

ARXIV = re.compile(r"\b(\d{4}\.\d{4,5})(?:v\d+)?\b")
URL = re.compile(r"https?://[^\s)\]>\"',]+")


def norm_key(k: str) -> str:
    k = (k or "").strip()
    m = ARXIV.search(k)
    if m:
        return m.group(1)
    return k.lower().rstrip("/").replace("http://", "https://")


def library_keys(library: Path) -> set:
    keys = set()
    for p in library.rglob("*.md"):
        t = p.read_text(encoding="utf-8", errors="replace")
        keys.update(m.group(1) for m in ARXIV.finditer(t))
        keys.update(norm_key(u) for u in URL.findall(t))
    return keys


def library_targets(library: Path) -> Dict[str, set]:
    th = (library / "THEORIES.md").read_text(encoding="utf-8", errors="replace")
    qs = (library / "QUESTIONS.md").read_text(encoding="utf-8", errors="replace")
    designs = {p.name for p in (library / "designs").glob("*.md")}
    return {
        "theory": set(re.findall(r"^## (T\d+)\.", th, re.M)),
        "question": set(re.findall(r"^([A-Z]\d+)\.", qs, re.M)),
        "design": designs,
        "precedent": designs,
        "text": {"_": " ".join(p.read_text(encoding="utf-8", errors="replace").lower()
                               for p in library.rglob("*.md"))},
    }


def validate(output: Dict, keys: set, targets: Dict[str, set]) -> Dict:
    """Apply the operator's limits. Returns admitted, candidates, violations."""
    violations: List[str] = []
    cands = list(output.get("candidates") or [])
    if len(cands) > MAX_INSPECT:
        violations.append(f"inspected {len(cands)} > {MAX_INSPECT}; truncated to the first {MAX_INSPECT}")
        cands = cands[:MAX_INSPECT]
    admitted, rest = [], []
    for c in cands:
        c = dict(c)
        key = norm_key(c.get("dedupe_key") or c.get("url") or "")
        c["dedupe_key"] = key
        reasons = []
        if not key:
            reasons.append("no dedupe key or url")
        if key in keys:
            reasons.append("duplicate of an item already in the library")
        if c.get("admit"):
            if c.get("primary_source_read") is not True:
                reasons.append("primary source not read")
            tt, tid = c.get("target_type"), str(c.get("target_id") or "").strip()
            if tt not in TARGET_TYPES:
                reasons.append(f"target_type {tt!r} not one of {TARGET_TYPES}")
            elif tt == "benchmark":
                if not tid or tid.lower() not in targets["text"]["_"]:
                    reasons.append(f"benchmark {tid!r} not named in the library")
            else:
                pool = targets[tt]
                if tt in ("design", "precedent"):
                    tid = tid.split()[0] if tid else tid
                if tid not in pool:
                    reasons.append(f"{tt} {tid!r} does not exist in the library")
            if not (c.get("change") or "").strip():
                reasons.append("no stated change")
        if c.get("admit") and not reasons and len(admitted) < MAX_ADMIT:
            admitted.append(c)
        else:
            if c.get("admit") and not reasons:
                reasons.append(f"admission cap {MAX_ADMIT} reached")
            if c.get("admit"):
                violations.append(f"demoted {key or '?'}: " + "; ".join(reasons))
            c["admit"] = False
            c["not_admitted_because"] = "; ".join(reasons) or "not proposed for admission"
            rest.append(c)
    return {"admitted": admitted, "candidates": rest, "violations": violations}


def expire(candidates: List[Dict], today: dt.date) -> Tuple[List[Dict], int]:
    keep = []
    for c in candidates:
        seen = dt.date.fromisoformat(c["first_seen"])
        if (today - seen).days < EXPIRY_DAYS:
            keep.append(c)
    return keep, len(candidates) - len(keep)


def step_state(state: Dict, admitted_n: int, now_iso: str, ok: bool) -> Dict:
    """Advance the circuit breaker. Productive means >= 1 admitted item and nothing else."""
    s = dict(state)
    s["passes"] = s.get("passes", 0) + 1
    s["last_pass_at"] = now_iso
    if ok:
        s["last_input_at"] = now_iso
    if admitted_n > 0:
        s["consecutive_empty"] = 0
        s["last_success_at"] = now_iso
    else:
        s["consecutive_empty"] = s.get("consecutive_empty", 0) + 1
    if s["consecutive_empty"] >= BOUND_EMPTY and not s.get("paused"):
        s["paused"] = True
        s["paused_at"] = now_iso
        s["pause_reported"] = False
    return s


def news_block(items: List[Dict], pass_date: str) -> str:
    lines = [f"\n## Monitor admissions {pass_date} (MONITOR-ADMITTED; unreviewed by the seat until annotated)\n"]
    for c in items:
        lines.append(f"- {c.get('date', 'unknown')} | {c.get('title', 'unknown')} | {c.get('url', '')}\n"
                     f"  dedupe {c['dedupe_key']} | primary source read | changes {c['target_type']} "
                     f"{c['target_id']}: {c.get('change', '').strip()}\n"
                     f"  summary: {c.get('summary', '').strip()}\n")
    return "".join(lines)


def load_json(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
