"""Cognitive-metabolism assay. RESTORED 2026-08-22 (see RECOVERY.md).

Build 1 asked "did epistemic gain occur" and answered yes/no. That collapses two
systems with completely different failure geometry:

  100 drivers -> 40 distinctions -> 30 behaviour changes -> 10 gains
  100 drivers ->  2 distinctions ->  2 behaviour changes ->  2 gains

So gain is measured as a funnel with conversion rates instead of a scalar. The
strongest category is unchanged and is still the conjunction of every link; the
intermediate stages exist to show WHERE the pipeline breaks, not to lower the bar.

  I  incompleteness   the store met something it could not predict at all
  D  distinction      a rule was proposed, environmentally tested, and persisted
  R  representation   that rule actually fires when normalising held-out queries
  B  behaviour        removing it changes the prediction on >= 1 held-out query
  G  gain             removing it loses >= 1 CORRECT held-out answer

The driver is INCOMPLETENESS, not surprise. Demanding surprise -> distinction
demanded that the safety mechanism FAIL before learning could begin, which is
wrong for a verification-gated architecture: it commits only when justified and
abstains otherwise, so it is never wrong, only ignorant. Measured across 20
universes: ~2,040 commitments, zero errors, 56% ignorance.

The contradiction rate survives as a separate axis, renamed away from "surprise"
because surprise is broader than error. A healthy run is I down, G up,
contradiction ~ 0. If it RISES that is an epistemic-integrity alarm, not
automatically "the verifier admitted a false rule" — memo corruption,
normalisation defects and too-few verification contexts all present the same way.
Alarm first, attribute cause second.

CAUSAL LINKAGE IS NOT ESTABLISHED. Ignorance falling while distinctions rise shows
only that I coexists with D. Proving I -> D needs the proposer to record which
deficit motivated each candidate. Until that exists I is a measure of OPPORTUNITY,
not mechanism, and is labelled so.

G is causal by construction: the counterfactual removes the rule AND purges every
memo entry that depended on it.

Also computed: GENERALISATION DISTANCE. A rule that only fixes near-duplicates of
its own evidence is weak evidence of representation; one that fixes structurally
remote held-out cases is strong. Measured without interpreting any semantics.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from substrate import ArtifactStore, SubstratePredictor, normalize


@dataclass
class Funnel:
    I: int = 0
    committed: int = 0
    contradictions: int = 0
    S: int = 0            # retained alias: contradiction events
    D: int = 0
    R: int = 0
    B: int = 0
    G: int = 0
    proposed: int = 0
    rejected: int = 0
    gain_queries: int = 0
    gen_len_ratio: float = 0.0
    gen_l1_count: float = 0.0
    gen_suffix_overlap: float = 0.0
    per_rule: List[Dict] = field(default_factory=list)

    def rates(self) -> Dict[str, float]:
        def r(num, den):
            return round(num / den, 4) if den else None
        return {
            "accept_rate_of_proposals": r(self.D, self.proposed),
            "ignorance_rate": r(self.I, self.I + self.committed),
            "contradiction_rate": r(self.contradictions, self.committed),
            "I_to_D_coexists": r(self.D, self.I),
            "D_to_R": r(self.R, self.D),
            "R_to_B": r(self.B, self.R),
            "B_to_G": r(self.G, self.B),
            "D_to_G": r(self.G, self.D),
        }

    def as_dict(self) -> Dict:
        d = {k: v for k, v in self.__dict__.items() if k != "per_rule"}
        d["rates"] = self.rates()
        return d


# ------------------------- generalisation distance, purely structural


def l1_count_distance(a: Sequence[str], b: Sequence[str]) -> int:
    ca, cb = Counter(a), Counter(b)
    return sum(abs(ca[k] - cb[k]) for k in set(ca) | set(cb))


def suffix_overlap(a: Sequence[str], b: Sequence[str]) -> int:
    n = 0
    for x, y in zip(reversed(list(a)), reversed(list(b))):
        if x != y:
            break
        n += 1
    return n


def assay(store: ArtifactStore, evalset) -> Funnel:
    """Walk every surviving rule through I->D->R->B->G against the held-out set."""
    f = Funnel()
    f.I = store.counters.get("probes_ignorant", 0)
    f.committed = store.counters.get("probes_committed", 0)
    f.contradictions = store.counters.get("probes_wrong", 0)
    f.S = f.contradictions
    f.proposed = store.counters.get("proposed", 0)
    f.rejected = store.counters.get("rejected", 0)

    active = [r for r in store.rules.values() if r.status == "active"]
    f.D = len(active)
    if not active:
        return f

    base = SubstratePredictor(store)
    base_preds = [base.predict(q.tag, q.word)[0] for q in evalset.queries]
    answers = evalset.answers

    all_rules = list(store.rules.values())
    fired_ids = set()
    for q in evalset.queries:
        _, fired = normalize(q.word, all_rules)
        fired_ids.update(fired)

    ratios, l1s, sufs = [], [], []
    helped = set()

    for r in active:
        rec = {"rid": r.rid, "lhs": " ".join(r.lhs), "rhs": " ".join(r.rhs),
               "proposer": r.proposer, "fires": r.rid in fired_ids,
               "changes": 0, "gains": 0, "losses": 0}
        if r.rid not in fired_ids:
            f.per_rule.append(rec)
            continue
        f.R += 1

        ghost = store.clone()
        ghost.demote(r.rid)
        gp = SubstratePredictor(ghost)
        changed = gains = losses = 0
        for i, q in enumerate(evalset.queries):
            alt = gp.predict(q.tag, q.word)[0]
            if alt == base_preds[i]:
                continue
            changed += 1
            if base_preds[i] == answers[i] and alt != answers[i]:
                gains += 1
                helped.add(q.qid)
                ratios.append(len(q.word) / max(1, len(r.lhs)))
                l1s.append(l1_count_distance(q.word, r.lhs))
                sufs.append(suffix_overlap(q.word, r.lhs))
            elif alt == answers[i] and base_preds[i] != answers[i]:
                losses += 1
        rec.update(changes=changed, gains=gains, losses=losses)
        f.per_rule.append(rec)
        if changed:
            f.B += 1
        if gains:
            f.G += 1

    f.gain_queries = len(helped)
    if ratios:
        f.gen_len_ratio = round(sum(ratios) / len(ratios), 3)
        f.gen_l1_count = round(sum(l1s) / len(l1s), 3)
        f.gen_suffix_overlap = round(sum(sufs) / len(sufs), 3)
    return f
