"""Frozen-reasoner arm and output parsing. RESTORED 2026-08-23.

Scope note: this restoration covers what the EMISSION probe needs — the parsers
and an LLMArm that can hold a store, a probe stream and a rendered context. The
full P0/P1/P2 accuracy round-loop is deliberately NOT restored, because the power
analysis (iteration 7) showed a 2-seed accuracy run gives a +/-29 point confidence
interval and is uninterpretable, while the outstanding measurement that a lane
window CAN settle is emission and claim truth-rate.
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence, Tuple

import prompts
from policy import probe_stream
from substrate import ArtifactStore, classify, harvest
from universe import EvalSet, Interaction, Session, Universe


def parse_seq(raw, store: Optional[ArtifactStore], actions: Sequence[str],
              maxlen: int) -> Optional[List[str]]:
    if raw is None:
        return None
    toks = ([str(t).strip() for t in raw] if isinstance(raw, list)
            else [t for t in str(raw).replace(",", " ").split() if t])
    if any(t not in actions for t in toks) or len(toks) > maxlen:
        return None
    return toks


def parse_runs(obj: dict, uni: Universe, store, cap: int
               ) -> List[Tuple[str, List[str]]]:
    out: List[Tuple[str, List[str]]] = []
    raw = obj.get("runs") or obj.get("_list") or []
    if not isinstance(raw, list):
        return out
    for item in raw[:cap * 3]:
        if isinstance(item, dict):
            tag, seq = item.get("tag"), item.get("seq", item.get("items"))
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            tag, seq = item
        else:
            continue
        tag = str(tag).strip()
        if tag not in uni.tags:
            continue
        word = parse_seq(seq, store, uni.actions, uni.spec.max_word_len)
        if not word:
            continue
        out.append((tag, word))
        if len(out) >= cap:
            break
    return out


def parse_claims(obj: dict, uni: Universe, store: ArtifactStore, cap: int
                 ) -> List[Tuple[List[str], List[str], List[str]]]:
    out = []
    raw = obj.get("claims") or []
    if not isinstance(raw, list):
        return out
    for item in raw[:cap * 3]:
        if not isinstance(item, dict):
            continue
        lhs = parse_seq(item.get("lhs"), store, uni.actions, uni.spec.max_word_len)
        rhs_raw = item.get("rhs", "")
        rhs = ([] if str(rhs_raw).strip() in ("", "()", "-", "nothing")
               else parse_seq(rhs_raw, store, uni.actions, uni.spec.max_word_len))
        if lhs is None or rhs is None or not lhs:
            continue
        if classify(lhs, rhs) is None:
            continue
        out.append((lhs, rhs, []))
        if len(out) >= cap:
            break
    return out


def parse_answers(obj: dict, symbols: Sequence[str], qids: Sequence[int],
                  fallback: str) -> List[str]:
    ans = obj.get("answers", obj)
    got: Dict[int, str] = {}
    if isinstance(ans, dict):
        for k, v in ans.items():
            try:
                i = int(str(k).strip())
            except ValueError:
                continue
            if str(v).strip() in symbols:
                got[i] = str(v).strip()
    elif isinstance(ans, list):
        for j, v in enumerate(ans):
            if str(v).strip() in symbols and j < len(qids):
                got[qids[j]] = str(v).strip()
    return [got.get(q, fallback) for q in qids]


class LLMArm:
    """Holds the persistent state one frozen-reasoner arm carries across a
    context wipe, plus the shared probe stream every arm uses for allowance it
    does not spend itself."""

    def __init__(self, arm: str, uni: Universe, evalset: EvalSet, model,
                 cfg, seed: int, condition: str = "C0"):
        assert arm in ("P0", "P1", "P2")
        assert condition in ("C0", "C1", "C1N", "C3", "C4")
        self.arm, self.condition = arm, condition
        self.uni, self.eval, self.model, self.cfg = uni, evalset, model, cfg
        self.rng = random.Random(seed * 31 + 5)
        self.stream = probe_stream(uni, self.rng)
        self.history: List[Interaction] = []
        self.store = ArtifactStore() if arm == "P2" else None
        self.sym_counts: Dict[str, int] = {}
        self.candidate_src = None
        self.system = prompts.system_prompt(
            uni, getattr(evalset, "len_lo", 8), getattr(evalset, "len_hi", 12),
            hint=(condition != "C4"))

    @property
    def fallback(self) -> str:
        """Filler for unanswered queries, from this arm's own observations —
        never from the evaluator."""
        if not self.sym_counts:
            return self.uni.symbols[0]
        return max(sorted(self.sym_counts), key=lambda s: self.sym_counts[s])

    def persistent_block(self) -> str:
        if self.arm == "P1":
            return prompts.render_history(self.history) if self.history else ""
        if self.arm == "P2":
            return prompts.render_store(self.store)
        return ""

    def round_block(self, session: Session) -> str:
        if not session.log:
            return ""
        return prompts.render_history(
            [i for i in session.log if i.source != "ruletest"], 8000)

    def candidates(self):
        """C3: candidates drawn ONLY from this arm's own observations."""
        from baselines import DataDrivenProposer
        if self.store is None:
            return ()
        if self.candidate_src is None:
            self.candidate_src = DataDrivenProposer(self.uni, self.rng)
            for i in self.history:
                self.candidate_src.observe(i)
        return self.candidate_src.propose(self.store, 20)

    def absorb(self, inter: Interaction) -> None:
        for sym in inter.readout:
            self.sym_counts[sym] = self.sym_counts.get(sym, 0) + 1
        if self.candidate_src is not None:
            self.candidate_src.observe(inter)
        if self.arm == "P1":
            self.history.append(inter)
        elif self.arm == "P2":
            harvest(self.store, inter)
