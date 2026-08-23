"""Non-LLM arms. RESTORED 2026-08-22 (see RECOVERY.md).

P3a  random guess / majority class
P3b  signature-class automaton — a real, generic algorithm for this environment
P3c  substrate machinery + non-model proposer.  FROZEN at iteration 2.
P3d  substrate machinery + relevance-ranked proposer.  FROZEN at iteration 4.

P3c is the control that decides whether the frozen reasoner contributes anything
at all; P3d is the strong control. Both are frozen: a control should eliminate
alternative explanations, not asymptotically absorb every clever strategy
available to the experimenter, or the comparison degrades into "frozen LLM versus
more engineering hours".

Every arm here draws its probes from policy.probe_stream, the same generator the
LLM arms use for their unspent allowance.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

from config import ArmConfig
from policy import probe_stream
from substrate import (ArtifactStore, SubstratePredictor, classify,
                       detect_surprise, harvest, normalize, retest_active_rules,
                       submit_rule)
from universe import EvalSet, Interaction, Session, Universe


# ---------------------------------------------------------------------------
#  P3a
# ---------------------------------------------------------------------------


def random_arm(uni: Universe, evalset: EvalSet, seed: int) -> Dict:
    rng = random.Random(seed * 101 + 3)
    preds = [rng.choice(uni.symbols) for _ in evalset.queries]
    acc, _ = evalset.score(preds)
    maj_sym, maj_acc = evalset.majority_baseline()
    return {"arm": "P3a", "acc_random": acc, "acc_majority": maj_acc,
            "majority_symbol": maj_sym}


# ---------------------------------------------------------------------------
#  P3b — signature-class automaton
# ---------------------------------------------------------------------------


class SignatureAutomaton:
    """Assumes only that the system is deterministic and that a sequence's
    behaviour is summarised by what it yields from each tag."""

    def __init__(self, uni: Universe):
        self.uni = uni
        self.obs: Dict[Tuple[str, Tuple[str, ...]], str] = {}
        self.built = False

    def add(self, inter: Interaction) -> None:
        for i in range(len(inter.word) + 1):
            self.obs[(inter.tag, tuple(inter.word[:i]))] = inter.readout[i]
        self.built = False

    def _sig(self, w: Tuple[str, ...]) -> Optional[Tuple[str, ...]]:
        out = []
        for t in self.uni.tags:
            v = self.obs.get((t, w))
            if v is None:
                return None
            out.append(v)
        return tuple(out)

    def build(self) -> None:
        # DETERMINISM BUG, found 2026-08-22 and fixed here. This iterated a set of
        # string tuples. Python randomises string hashes per process, so set order
        # varied between runs, which changed insertion order into `sigs`, which
        # changed Counter.most_common tie-breaking in `votes`, which changed the
        # transition table and the final accuracy. P3b read 0.467 / 0.471 / 0.476 /
        # 0.483 / 0.470 across runs of IDENTICAL code, and that was misdiagnosed as
        # restoration drift. Sorting makes the arm reproducible; the whole-pipeline
        # determinism guarantee never actually covered this arm.
        words = sorted({w for (_, w) in self.obs})
        sigs: Dict[Tuple[str, ...], Tuple[str, ...]] = {}
        for w in words:
            s = self._sig(w)
            if s is not None:
                sigs[w] = s
        votes: Dict[Tuple[Tuple[str, ...], str], Counter] = defaultdict(Counter)
        for w, s in sigs.items():
            for a in self.uni.actions:
                s2 = sigs.get(w + (a,))
                if s2 is not None:
                    votes[(s, a)][s2] += 1
        # deterministic tie-break: highest count, then lexicographic
        self.delta = {k: max(sorted(c), key=lambda s2: (c[s2], s2))
                      for k, c in votes.items()}
        self.start = sigs.get(())
        self.n_classes = len(set(sigs.values()))
        self.built = True

    def predict(self, tag: str, word: Sequence[str], fallback: str
                ) -> Tuple[str, bool]:
        if not self.built:
            self.build()
        cur = self.start
        if cur is None:
            return fallback, False
        for a in word:
            nxt = self.delta.get((cur, a))
            if nxt is None:
                return fallback, False
            cur = nxt
        return cur[self.uni.tags.index(tag)], True


def state_merge_arm(uni: Universe, evalset: EvalSet, seed: int,
                    budget_per_round: int, rounds: int) -> List[Dict]:
    rng = random.Random(seed * 977 + 11)
    stream = probe_stream(uni, rng)
    auto = SignatureAutomaton(uni)
    seen: Counter = Counter()
    recs, total = [], 0
    for rnd in range(1, rounds + 1):
        session = Session(uni, budget_per_round)
        while session.remaining > 0:
            tag, word = next(stream)
            ok, _ = session.try_run(tag, word, source="baseline")
            if not ok:
                break
            auto.add(session.log[-1])
            seen.update(session.log[-1].readout)
        total += session.used
        maj_sym = seen.most_common(1)[0][0] if seen else uni.symbols[0]
        auto.build()
        preds, cov = [], 0
        for q in evalset.queries:
            p, hit = auto.predict(q.tag, q.word, maj_sym)
            preds.append(p)
            cov += hit
        acc, _ = evalset.score(preds)
        recs.append({"arm": "P3b", "round": rnd, "acc_post": acc,
                     "acc_pre": acc, "sub_post": acc, "sub_pre": acc,
                     "cov_post": cov / len(evalset.queries), "cov_pre": None,
                     "interactions": session.used, "cum_interactions": total,
                     "n_classes": auto.n_classes,
                     "true_classes": uni.true_class_count(),
                     "llm_calls": 0, "prompt_tokens": 0,
                     "completion_tokens": 0, "cost": 0.0})
    return recs


# ---------------------------------------------------------------------------
#  Proposers
# ---------------------------------------------------------------------------


class RandomProposer:
    mode = "random"

    def __init__(self, uni: Universe, rng: random.Random):
        self.uni, self.rng = uni, rng

    def observe(self, inter: Interaction) -> None:
        pass

    def propose(self, store: ArtifactStore, n: int):
        out = []
        for _ in range(n * 12):
            if len(out) >= n:
                break
            la = self.rng.choice([2, 2, 2, 3])
            lb = min(self.rng.choice([0, 1, 1, 2]), la - 1)
            lhs = [self.rng.choice(self.uni.actions) for _ in range(la)]
            rhs = [self.rng.choice(self.uni.actions) for _ in range(lb)]
            if classify(lhs, rhs) is None or store.has_rule(lhs, rhs):
                continue
            out.append((lhs, rhs))
        return out


class DataDrivenProposer:
    """Proposes pairs whose observed behaviour already agrees everywhere it has
    been seen. Reuses prefixes already paid for; costs no extra interactions."""

    mode = "datadriven"

    def __init__(self, uni: Universe, rng: random.Random, sig_tags: int = 0):
        self.uni, self.rng = uni, rng
        self.obs: Dict[Tuple[str, Tuple[str, ...]], str] = {}
        # CANDIDATE-BURDEN KNOB (iteration 27). A candidate is admitted when its
        # two words agree on `sig_tags` tags; 0 means all of them, the original
        # behaviour. Requiring FEWER tags is weaker evidence, so the pool floods
        # with plausible-but-often-false candidates. This manipulates proposal
        # burden DOWNSTREAM of the arena, leaving the hidden algebra untouched,
        # which is what makes it a causal test rather than another family sweep.
        self.sig_tags = sig_tags or len(uni.tags)

    def observe(self, inter: Interaction) -> None:
        for i in range(len(inter.word) + 1):
            self.obs[(inter.tag, tuple(inter.word[:i]))] = inter.readout[i]

    def _sig(self, w: Tuple[str, ...]) -> Optional[Tuple[str, ...]]:
        out = []
        for t in self.uni.tags[:self.sig_tags]:
            v = self.obs.get((t, w))
            if v is None:
                return None
            out.append(v)
        return tuple(out)

    def propose(self, store: ArtifactStore, n: int):
        buckets: Dict[Tuple[str, ...], List[Tuple[str, ...]]] = defaultdict(list)
        for w in {w for (_, w) in self.obs if len(w) <= 4}:
            s = self._sig(w)
            if s is not None:
                buckets[s].append(w)
        cands = []
        for group in buckets.values():
            group = sorted(group, key=lambda w: (len(w), w))
            for i, rhs_w in enumerate(group):
                for j, lhs_w in enumerate(group):
                    if i == j:
                        continue
                    lhs, rhs = list(lhs_w), list(rhs_w)
                    if classify(lhs, rhs) is None or store.has_rule(lhs, rhs):
                        continue
                    cands.append((len(lhs) - len(rhs), lhs, rhs))
        cands.sort(key=lambda c: (-c[0], c[1], c[2]))
        return [(l, r) for _, l, r in cands[:n]]


class RelevanceProposer(DataDrivenProposer):
    """P3d. The strongest proposer buildable from ARM-VISIBLE information only:
    its own observations, the action alphabet, the query length range disclosed
    in the task statement, and its own rule set. It never sees eval answers, eval
    queries, or hidden structure -- it scores against SYNTHETIC long words it
    generates itself.

    FROZEN at iteration 4. Do not optimise further.

    `ranking` exists only for the inductive-bias sensitivity test: 'compression'
    is P3d proper. That test found compression is the WORST firing-aware ranking
    (coverage 0.710, novelty 0.713, anticompression 0.703 all beat it at 0.647),
    so the operative variable is expected FIRING, not length reduction.
    """

    mode = "relevance"

    def __init__(self, uni: Universe, rng: random.Random,
                 len_lo: int = 8, len_hi: int = 12, n_probe_words: int = 120,
                 ranking: str = "compression", sig_tags: int = 0):
        super().__init__(uni, rng, sig_tags=sig_tags)
        self.ranking = ranking
        self.synthetic = [
            [rng.choice(uni.actions) for _ in range(rng.randint(len_lo, len_hi))]
            for _ in range(n_probe_words)
        ]

    def _support(self, w) -> int:
        return sum(1 for (_, ww) in self.obs if ww == tuple(w))

    def propose(self, store: ArtifactStore, n: int):
        cands = super().propose(store, n * 25)
        if not cands:
            return []
        rules = list(store.rules.values())
        reduced = [normalize(w, rules)[0] for w in self.synthetic]
        unresolved = {ArtifactStore.memo_key(t, w)
                      for t in self.uni.tags for w in reduced
                      if ArtifactStore.memo_key(t, w) not in store.memo}
        scored = []
        for lhs, rhs in cands:
            L = len(lhs)
            fires = sum(1 for w in reduced
                        if any(w[i:i + L] == lhs for i in range(len(w) - L + 1)))
            if fires == 0 and self.ranking != "support":
                continue
            cut = L - len(rhs)
            if self.ranking == "compression":
                score = fires * cut
            elif self.ranking == "coverage":
                score = fires
            elif self.ranking == "support":
                score = self._support(lhs) + self._support(rhs)
            elif self.ranking == "novelty":
                score = sum(1 for w in reduced
                            if any(w[i:i + L] == lhs
                                   for i in range(len(w) - L + 1))
                            and any(ArtifactStore.memo_key(t, w) in unresolved
                                    for t in self.uni.tags))
            elif self.ranking == "anticompression":
                score = fires / (1 + cut)
            else:
                raise ValueError(self.ranking)
            scored.append((-score, fires, lhs, rhs))
        scored.sort(key=lambda c: (c[0], -c[1], c[2], c[3]))
        return [(l, r) for _, _, l, r in scored[:n]]


# ---------------------------------------------------------------------------
#  P3c / P3d driver
# ---------------------------------------------------------------------------


def substrate_arm(uni: Universe, evalset: EvalSet, seed: int, cfg: ArmConfig,
                  rounds: int, proposer_mode: str = "random",
                  inject_wrong: int = 0,
                  sig_tags: int = 0) -> Tuple[List[Dict], ArtifactStore]:
    """The relevance proposer scores against synthetic words drawn from the query
    length range, which is arm-visible because the task statement discloses it.
    That range is read off the eval set rather than hardcoded, so the arm stays
    honest when the arena's probe cap changes."""
    rng = random.Random(seed * 613 + 29)
    stream = probe_stream(uni, rng)
    store = ArtifactStore()
    if proposer_mode.startswith("relevance"):
        rank = proposer_mode.split(":", 1)[1] if ":" in proposer_mode else "compression"
        prop = RelevanceProposer(uni, rng, ranking=rank,
                                 len_lo=getattr(evalset, "len_lo", 8),
                                 len_hi=getattr(evalset, "len_hi", 12),
                                 sig_tags=sig_tags)
    elif proposer_mode == "datadriven":
        prop = DataDrivenProposer(uni, rng, sig_tags=sig_tags)
    else:
        prop = RandomProposer(uni, rng)
    arm = f"P3c-{proposer_mode}"

    if inject_wrong:
        planted, guard = 0, 0
        while planted < inject_wrong and guard < 2000:
            guard += 1
            lhs = [rng.choice(uni.actions) for _ in range(2)]
            rhs = [rng.choice(uni.actions)]
            if classify(lhs, rhs) is None or store.has_rule(lhs, rhs):
                continue
            if uni.true_word_element(lhs) == uni.true_word_element(rhs):
                continue                  # accidentally true; not a wrong artifact
            r = store.add_rule(lhs, rhs, classify(lhs, rhs), "injected", 0)
            r.passes = 1                  # arrives looking credible
            planted += 1
        arm += f"+wrong{inject_wrong}"

    def spend(session: Session, k: int) -> None:
        for _ in range(k):
            if session.remaining <= 0:
                return
            tag, word = next(stream)
            # surprise must be read BEFORE the observation is absorbed
            detect_surprise(store, tag, word, uni.true_final_symbol(tag, word))
            ok, _ = session.try_run(tag, word, source="policy")
            if not ok:
                return
            harvest(store, session.log[-1])
            prop.observe(session.log[-1])

    recs = []
    for rnd in range(1, rounds + 1):
        session = Session(uni, cfg.budget_per_round)
        p, cov_pre = SubstratePredictor(store).predict_all(evalset.queries)
        acc_pre, _ = evalset.score(p)

        retest_active_rules(store, session, rng)
        for _ in range(cfg.turns):
            if session.remaining <= 0:
                break
            spend(session, cfg.runs_per_turn_p2)
            for lhs, rhs in prop.propose(store, cfg.claims_per_turn):
                if session.remaining < 2:
                    break
                submit_rule(store, session, lhs, rhs, proposer_mode, rnd, rng,
                            n_contexts=cfg.rule_contexts)
        spend(session, session.remaining)

        p, cov_post = SubstratePredictor(store).predict_all(
            evalset.queries, tally=True)
        acc_post, _ = evalset.score(p)
        recs.append({
            "arm": arm, "round": rnd,
            "acc_pre": acc_pre, "acc_post": acc_post,
            "sub_pre": acc_pre, "sub_post": acc_post,
            "cov_pre": cov_pre, "cov_post": cov_post,
            "interactions": session.used,
            "n_rules_active": len(store.active_rules()),
            "n_rules_rejected": len(store.rules) - len(store.active_rules()),
            "n_injected_alive": sum(1 for r in store.rules.values()
                                    if r.proposer == "injected"
                                    and r.status == "active"),
            "n_memo": len(store.memo), "store_bytes": store.size_bytes(),
            "n_ops": len(store.ops), "history_records": 0,
            "llm_calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
            "cost": 0.0, "epistemic_gains": 0,
        })
    return recs, store
