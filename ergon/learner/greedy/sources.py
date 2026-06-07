"""Per-source adapters: substrate records -> normalized Examples.

Each adapter is a generator. Adapters are deliberately tolerant: a record
that cannot be serialized cleanly is skipped, not crashed on. Counts of
skips are returned via the SourceStats side-channel for the manifest.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .serializers import (
    Example,
    make_judgement,
    serialize_invariant_equality,
    strip_answer_leak,
    extract_holds,
)

PROM = Path("F:/Prometheus")


def _uid(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8", "replace")).hexdigest()[:24]


@dataclass
class SourceStats:
    name: str
    yielded: int = 0
    skipped: int = 0
    by_outcome: Dict[str, int] = field(default_factory=dict)

    def bump_out(self, o: str) -> None:
        self.by_outcome[o] = self.by_outcome.get(o, 0) + 1


def _verdict_outcome(verdict: str) -> tuple[str, bool]:
    v = (verdict or "").upper()
    if v == "REJECTED":
        return "rejected", True
    if v == "SHADOW_CATALOG":
        return "promoted", False
    if v == "PROMOTED":
        return "promoted", False
    if v == "UNVERIFIED":
        return "unverified", False
    return "other", False


# ---------------------------------------------------------------------------
# Tier 1 — Theseus corpus (the spine: ~270M records, ~40% kills, gold holds)
# ---------------------------------------------------------------------------

def theseus_examples(
    cap: int,
    stats: SourceStats,
    max_batches: int = 60,
    per_cell_cap: int = 900,
    seed: int = 13,
    values_shown: bool = False,
) -> Iterator[Example]:
    """Sample Theseus batches, stratified by (generator_id, verdict) so we
    get failure-mode AND domain variety, not one generator's flood.

    Every claim is rendered into a gold true/false judgement (answer
    computed from the payload, never read off the leaky canonical text)."""
    batches = sorted(glob.glob(str(PROM / "theseus/corpus/batch-*.jsonl")), reverse=True)
    if not batches:
        return
    # spread across the run, not just the newest N
    if len(batches) > max_batches:
        step = len(batches) / max_batches
        batches = [batches[int(i * step)] for i in range(max_batches)]
    cell_counts: Dict[str, int] = {}
    n = 0
    per_batch_line_cap = 60000  # sample a slice from each batch, don't scan whole 360MB files
    for bpath in batches:
        if n >= cap:
            break
        try:
            with open(bpath, "r", encoding="utf-8") as f:
                lines_read = 0
                for line in f:
                    if n >= cap:
                        break
                    lines_read += 1
                    if lines_read > per_batch_line_cap:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    gen = r.get("generator_id", "?")
                    verdict = r.get("verdict", "?")
                    cell = f"{gen}:{verdict}"
                    if cell_counts.get(cell, 0) >= per_cell_cap:
                        continue
                    payload = r.get("claim_payload") or {}
                    kind = r.get("claim_kind", "")
                    canonical = r.get("canonical_claim_text", "")

                    claim_text: Optional[str] = None
                    gold: Optional[bool] = None
                    justification = ""

                    if kind == "invariant_equality":
                        out = serialize_invariant_equality(payload, values_shown=values_shown)
                        if out is not None:
                            claim_text, gold, justification = out
                    if claim_text is None:
                        # fallback for other claim_kinds: clean canonical text
                        ct = strip_answer_leak(canonical)
                        h = extract_holds(canonical, payload)
                        if not ct or h is None or "holds=" in ct.lower():
                            stats.skipped += 1
                            continue
                        claim_text, gold = ct, h
                        justification = f"verified by the substrate engine ({r.get('method', 'computation')})."

                    outcome, is_fail = _verdict_outcome(verdict)
                    prompt, completion = make_judgement(claim_text, gold, justification)
                    cell_counts[cell] = cell_counts.get(cell, 0) + 1
                    n += 1
                    stats.yielded += 1
                    stats.bump_out(outcome)
                    cat_a = payload.get("catalog_a", "")
                    cat_b = payload.get("catalog_b", "")
                    domain = f"{cat_a}_x_{cat_b}" if cat_a or cat_b else (kind or "theseus")
                    ents = []
                    if payload.get("object_a"):
                        ents.append(f"{cat_a}:{payload.get('object_a')}")
                    if payload.get("object_b"):
                        ents.append(f"{cat_b}:{payload.get('object_b')}")
                    yield Example(
                        prompt=prompt, completion=completion, source="theseus", tier=1,
                        trust_weight=1.0 if verdict == "REJECTED" else 0.7,
                        domain=domain, outcome=outcome, is_failure=is_fail, gold_bool=gold,
                        uid=_uid("theseus", r.get("record_id", "") or canonical),
                        meta={"generator_id": gen, "kill_pattern": r.get("kill_pattern"),
                              "claim_kind": kind, "verdict": verdict},
                        entities=ents,
                    )
        except OSError:
            continue


# ---------------------------------------------------------------------------
# Tier 1 — Charon Pollux (numerical-coincidence kills, gold from kill_pattern)
# ---------------------------------------------------------------------------

def pollux_examples(cap: int, stats: SourceStats) -> Iterator[Example]:
    path = PROM / "charon/agents/pollux/state/kill_ledger.jsonl"
    if not path.exists():
        return
    n = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if n >= cap:
                break
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            p = r.get("claim_payload") or {}
            a_desc = (r.get("extras") or {}).get("subset_a_desc", p.get("pair_name", "subset A"))
            b_desc = (r.get("extras") or {}).get("subset_b_desc", "subset B")
            corr_raw = p.get("corr_raw")
            corr_norm = p.get("corr_norm")
            kp = r.get("kill_pattern", "")
            if corr_raw is None or corr_norm is None:
                stats.skipped += 1
                continue
            # Claim: the raw correlation reflects a real (scale-independent) relationship.
            claim = (f"The Spearman correlation of {corr_raw} between {a_desc} and {b_desc} "
                     f"reflects a real relationship that survives mean-spacing normalization.")
            gold = False  # kill_ledger entries are, by construction, the ones that did NOT survive
            just = (f"after normalization the correlation is {corr_norm}, "
                    f"so the raw correlation is a scale artifact ({kp}).")
            prompt, completion = make_judgement(claim, gold, just)
            n += 1
            stats.yielded += 1
            stats.bump_out("rejected")
            yield Example(
                prompt=prompt, completion=completion, source="pollux", tier=1,
                trust_weight=1.0, domain="mahler_measure_correlation", outcome="rejected",
                is_failure=True, gold_bool=gold,
                uid=_uid("pollux", r.get("record_id", "") or claim),
                meta={"kill_pattern": kp, "corr_raw": corr_raw, "corr_norm": corr_norm},
            )


# ---------------------------------------------------------------------------
# Tier 1 — Charon Erebos (composed falsification hypotheses; reasoning, no gold)
# ---------------------------------------------------------------------------

def erebos_examples(cap: int, stats: SourceStats) -> Iterator[Example]:
    path = PROM / "charon/agents/erebos/state/kill_ledger.jsonl"
    if not path.exists():
        return
    n = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if n >= cap:
                break
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            claim = r.get("canonical_claim_text") or ""
            kp = r.get("kill_pattern") or ""
            if not claim:
                stats.skipped += 1
                continue
            claim = strip_answer_leak(claim)
            prompt = (f"Hypothesis: {claim}\n"
                      f"What is the most likely way this fails under adversarial falsification?")
            completion = (f"Expected failure mode: {kp or 'composed-route falsification'}. "
                          f"The composition inherits its parents' kill conditions.")
            n += 1
            stats.yielded += 1
            stats.bump_out("rejected")
            yield Example(
                prompt=prompt, completion=completion, source="erebos", tier=1,
                trust_weight=0.8, domain="composed_falsification", outcome="rejected",
                is_failure=True, gold_bool=None,
                uid=_uid("erebos", r.get("record_id", "") or claim),
                meta={"kill_pattern": kp},
            )


# ---------------------------------------------------------------------------
# Tier 1 — Hephaestus forge ledger (will-it-forge judgement, gold from status)
# ---------------------------------------------------------------------------

def hephaestus_examples(cap: int, stats: SourceStats) -> Iterator[Example]:
    path = PROM / "agents/hephaestus/ledger.jsonl"
    if not path.exists():
        return
    n = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if n >= cap:
                break
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            names = r.get("concept_names") or []
            status = (r.get("status") or "").lower()
            reason = r.get("reason") or ""
            if not names or status not in ("forge", "scrap"):
                stats.skipped += 1
                continue
            combo = " + ".join(names)
            claim = (f"Combining the concepts [{combo}] yields a tool that passes the "
                     f"validation trap battery.")
            gold = (status == "forge")
            acc = r.get("accuracy")
            if gold:
                just = f"the forged tool passed the battery (accuracy {acc})."
                outcome = "forge"
            else:
                just = f"it was scrapped: {reason}."
                outcome = "scrap"
            prompt, completion = make_judgement(claim, gold, just)
            n += 1
            stats.yielded += 1
            stats.bump_out(outcome)
            yield Example(
                prompt=prompt, completion=completion, source="hephaestus", tier=1,
                trust_weight=1.0, domain="concept_forge", outcome=outcome,
                is_failure=(not gold), gold_bool=gold,
                uid=_uid("hephaestus", r.get("key", "") or combo, str(r.get("timestamp", ""))),
                meta={"status": status, "reason": reason[:120]},
            )


# ---------------------------------------------------------------------------
# Tier 2 — Charon prose artifacts (markdown), low trust, flagged
# ---------------------------------------------------------------------------

_AGENT_DIRS = ["lethe", "stygian", "acheron", "hecate", "moros"]
_VERDICT_LINE = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?(verdict|recommendation|finding|conclusion|kill_pattern|hypothesis)\b[:\*]*\s*(.+)$", re.IGNORECASE)
_H1 = re.compile(r"^#\s+(.+)$")


def charon_markdown_examples(cap: int, stats: SourceStats) -> Iterator[Example]:
    n = 0
    files: List[str] = []
    for agent in _AGENT_DIRS:
        files += glob.glob(str(PROM / f"charon/agents/{agent}/artifacts/*.md"))
    files.sort(reverse=True)
    for fp in files:
        if n >= cap:
            break
        try:
            text = Path(fp).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        title = ""
        findings: List[str] = []
        for ln in text.splitlines():
            m1 = _H1.match(ln)
            if m1 and not title:
                title = m1.group(1).strip()
            mv = _VERDICT_LINE.match(ln)
            if mv:
                findings.append(f"{mv.group(1).strip().lower()}: {mv.group(2).strip()[:200]}")
            if len(findings) >= 4:
                break
        if not title or not findings:
            stats.skipped += 1
            continue
        agent = Path(fp).parts[-3] if len(Path(fp).parts) >= 3 else "charon"
        prompt = f"A failure-hunt agent examined: {title}\nSummarize what it found and why it matters for falsification."
        completion = " ".join(findings)
        n += 1
        stats.yielded += 1
        stats.bump_out("prose_finding")
        yield Example(
            prompt=prompt, completion=completion, source=f"charon_md:{agent}", tier=2,
            trust_weight=0.4, domain=f"charon_{agent}", outcome="prose_finding",
            is_failure=True, gold_bool=None,
            uid=_uid("charonmd", fp),
            meta={"file": os.path.basename(fp)},
        )


# ---------------------------------------------------------------------------
# Tier 2 — Harmonia retraction registry (real retractions = strong failure data)
# ---------------------------------------------------------------------------

def harmonia_examples(cap: int, stats: SourceStats) -> Iterator[Example]:
    path = PROM / "harmonia/memory/retraction_registry.md"
    if not path.exists():
        return
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    n = 0
    # registry entries are typically "## F0xx ..." blocks; split on headings
    blocks = re.split(r"\n(?=#{1,3}\s)", text)
    for blk in blocks:
        if n >= cap:
            break
        head = blk.strip().splitlines()[0] if blk.strip() else ""
        head = re.sub(r"^#+\s*", "", head).strip()
        body = " ".join(l.strip() for l in blk.splitlines()[1:] if l.strip())[:300]
        if not head or len(head) < 6 or not body:
            stats.skipped += 1
            continue
        prompt = f"A previously-believed mathematical finding was retracted: {head}\nWhat went wrong?"
        completion = body
        n += 1
        stats.yielded += 1
        stats.bump_out("retraction")
        yield Example(
            prompt=prompt, completion=completion, source="harmonia_retraction", tier=2,
            trust_weight=0.5, domain="retraction", outcome="retraction",
            is_failure=True, gold_bool=None,
            uid=_uid("harmonia", head),
            meta={},
        )


ALL_SOURCES = {
    "theseus": theseus_examples,
    "pollux": pollux_examples,
    "erebos": erebos_examples,
    "hephaestus": hephaestus_examples,
    "charon_md": charon_markdown_examples,
    "harmonia": harmonia_examples,
}
